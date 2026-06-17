# Grain & joins — why a clean result set is evidence of nothing

This is the centerpiece. The whole skill exists because an LLM (and a hurrying analyst) produces the
**returns rows, wrong grain** quadrant — a query that parses, binds, runs, and returns a tidy result
set that is *silently double-counted*. SEMANTICS's A2 gate is "one row per WHAT, and it's actually
unique on that key." This file is how you *prove* the grain, and `bin/sql-lint.py` is its mechanized
static pre-filter.

## The one principle

> **The result grain is the contract; prove it, don't read it.** "One row per customer" is a claim
> every downstream `SUM`, `AVG`, and `COUNT` trusts. A query whose grain is wrong returns a clean
> result set and plausible numbers — and is wrong. The only proof is a **uniqueness/row-count check**
> on the live result, not a read of the join graph.

Two corollaries:
- **Returning rows is necessary, not sufficient.** The question is never "did it return rows?" but
  "is the result set unique on the grain key, and does a known total reconcile?"
- **The proof is a count, not an inspection.** A join fan-out is invisible in the SQL and invisible in
  a spot-check of the output; it surfaces only when you count.

## The grain check (the proof)

Wrap the query and ask the engine two questions:

```sql
-- 1. Is the result unique on its claimed grain key?
SELECT COUNT(*) AS rows, COUNT(DISTINCT customer_id) AS distinct_key
FROM ( <the query> ) q;
-- rows > distinct_key  =>  the result is NOT one-row-per-customer; a join fanned out.

-- 2. Does a measure reconcile against a known, independently-trusted total?
SELECT SUM(revenue) FROM ( <the query> ) q;       -- vs last quarter's known revenue
```

If `rows > distinct_key`, the grain is wrong: some customers appear on multiple rows, and any
`SUM`/`COUNT` over the un-deduplicated set is inflated. If the reconciled total is **higher** than
the known figure, you are double-counting (the fan-out signature); **lower**, you dropped rows (an
`INNER` where you meant `OUTER`, or a `NULL`-rejecting `WHERE`).

## The fan-out failure modes (where the silent wrong-answer hides)

| Mode | What it looks like in SQL | What it does to the answer |
|---|---|---|
| **1:N join, then SUM** | `customers JOIN orders` then `SUM(order.amount)` grouped by customer | each customer's row repeats per order — `SUM` is *correct* here (one amount per order row), but adding a *second* 1:N join multiplies it |
| **Two 1:N joins (the killer)** | `orders JOIN items JOIN payments` | each order's `items` × `payments` cross-multiply; `SUM(amount)` is inflated by the item count (`sql-lint.py` flags this as **JOIN_FANOUT** when there's no `GROUP BY`/`DISTINCT`/aggregate to collapse it) |
| **N:M through a bridge** | `users JOIN user_roles JOIN roles` then count users | each user repeats per role; `COUNT(*)` counts user-roles, not users |
| **Implicit cross join** | `FROM a, b` with no `WHERE a.id = b.a_id` | every row of `a` × every row of `b` — the cartesian product (`sql-lint.py` flags this) |
| **`NULL`-rejecting WHERE on an outer join** | `LEFT JOIN o ... WHERE o.status='paid'` | the `WHERE` drops the `NULL` rows the `LEFT JOIN` produced — silently an `INNER JOIN`, fewer rows than intended (`sql-lint.py` flags this as **OUTER_JOIN_DEMOTED**; `WHERE o.id IS NULL` is the legitimate anti-join and is excluded) |
| **Non-additive measure summed** | `SUM(rate)` or `AVG(AVG(...))` at a coarser grain | a ratio/average summed or re-averaged at the wrong grain is meaningless even with no fan-out |

## How to fix a fan-out (not the score)

A wrong grain is fixed by **changing the query**, never by accepting the number:

- **Aggregate before joining.** Collapse each 1:N to its grain in a CTE/subquery first
  (`SELECT order_id, SUM(amount) FROM items GROUP BY order_id`), then join the pre-aggregated result
  — so the join is 1:1 and can't fan out.
- **`COUNT(DISTINCT key)`** instead of `COUNT(*)` when the rowset is intentionally fanned but you want
  the entity count — a band-aid, not a substitute for the right grain.
- **Move the predicate to the `ON` clause** (or guard `OR o.id IS NULL`) to keep an outer join outer.
- **Re-derive the grain (A2)** when the measure is non-additive: a ratio is computed as
  `SUM(numerator) / SUM(denominator)` at the target grain, never as `AVG(ratio)`.

## What `sql-lint.py` catches (the static pre-filter)

Cheap, deterministic, before the live grain check — the smells that *correlate* with a wrong grain or
an unsafe query:

| Smell | Why it matters |
|---|---|
| **JOIN_FANOUT** | ≥2 joined tables (explicit `JOIN`s + comma-`FROM` tables beyond the first) with **no** `GROUP BY`, **no** `SELECT DISTINCT`, and **no** aggregate in `SELECT` ⇒ a 1:N × 1:N fan-out can silently *multiply* rows (the "two 1:N joins" killer above) — verify with `COUNT(*)` vs `COUNT(DISTINCT key)` (A2). Conservative: any collapsing construct suppresses it |
| **OUTER_JOIN_DEMOTED** | a `LEFT`/`RIGHT [OUTER] JOIN`'d table whose alias/column appears in a plain `WHERE` predicate (`=,<,>,<=,>=,<>,LIKE,IN`) — anything but `IS [NOT] NULL` ⇒ the `WHERE` drops the `NULL`-extended rows and the outer join is silently an `INNER` (the dominant A3 defect above); `WHERE o.id IS NULL` is the legitimate anti-join and does not flag |
| **IMPLICIT_CROSS_JOIN** | a `FROM` with multiple tables and no join predicate ⇒ a cartesian product (the worst fan-out) |
| **SELECT_STAR** | hides the result columns ⇒ you can't see the grain key, and a join adds columns silently |
| **MISSING_WHERE_DML** | `UPDATE`/`DELETE` with no `WHERE` ⇒ rewrites the whole table (the catastrophic B5 defect) |
| **LIMIT_NO_ORDER** | `LIMIT` with no `ORDER BY` ⇒ a nondeterministic page (B5) |
| **GROUP_BY_INCOMPLETE** | a heuristic flag: more distinct columns selected than grouped ⇒ likely a `GROUP BY` gap (A4) |
| **NON_SARGABLE** | a `WHERE`/`JOIN ... ON` predicate wraps a likely-indexed column in a **function** (`WHERE DATE(created_at)='...'`, `UPPER(name)='X'`, `COALESCE(status,'')='x'`), in **arithmetic** (`WHERE price*1.2>100`, `col+0=5`), or uses a **leading-wildcard `LIKE`** (`name LIKE '%foo'`) ⇒ the planner can't use an index on the raw column (a performance/perf-correctness smell, A5/B4). Move the transform to the literal side (`created_at = DATE('...')`) or store a computed/indexed column. A function on the **literal** side (`WHERE created_at = DATE('...')`, `ts >= NOW() - INTERVAL '7 days'`), an anchored `LIKE 'foo%'`, a bare `col = 'lit'`, and a `HAVING COUNT(*)>5` aggregate are all sargable / out-of-scope and do **not** flag |

Run it: `python3 bin/sql-lint.py <file|dir>`. Findings are *signals*, not proof — they point the live
grain check at the weak spots. A clean lint does **not** mean the grain is right; only the
row-count/uniqueness check proves that.

The same tool reads the *plan* the query produced, not just its source:
`python3 bin/sql-lint.py plan <explain.json>` parses a Postgres `EXPLAIN (FORMAT JSON)` document (a
file — **no live DB needed**) and flags the EXECUTION-axis (B3/B4) smells the SQL read can't see — a
`Nested Loop` driving a `Seq Scan` (O(n·m), `NESTED_LOOP_NO_INDEX`), a >100× `Actual` vs `Plan` row
blowup (`ROW_ESTIMATE_BLOWUP`, ANALYZE only), a filtered/wide `Seq Scan` (`SEQ_SCAN`), and a large
`Sort`/`Hash Aggregate` (`HIGH_COST_SORT`). See `references/execution-axis.md` for the full catalogue;
the fan-out it confirms is the plan-level twin of the static `JOIN_FANOUT`/`IMPLICIT_CROSS_JOIN` above.

## How this scores

A2 is **named ∧ proven**:
- named = the grain ("one row per ___") is stated explicitly before the joins are read;
- proven = `COUNT(*) == COUNT(DISTINCT key)` on the live result **and** a known total reconciles.

A query that returns rows but whose result set isn't unique on the grain key is **not** A2-passing —
it's the *returns rows, wrong grain* quadrant, and the corrective is on the query (aggregate before
joining / fix the join / re-derive the grain), not the score.
