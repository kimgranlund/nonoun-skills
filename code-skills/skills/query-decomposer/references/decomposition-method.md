# The two-axis method — SEMANTICS × EXECUTION

A SQL query is **correct on two independent axes that walk the same hierarchy in opposite
directions** — the decomposer seam the layout-, mermaid-, component-, and code-decomposers apply to
space, diagrams, components, and functions, here applied to an analytics or transactional query.

- **Semantics · whole → part** grades the **intent**: the question it must answer → its result grain
  → its joins & filters → its aggregation & windows → its fit with the schema. *"Is it the right
  query?"*
- **Execution · part → whole** grades the **mechanism**: it parses → every table/column binds → the
  plan runs without a cartesian explosion → it performs → it's safe & deterministic. *"Does it
  provably run, here?"*

They **cross at the query measured against the schema** — the SELECT list + joins are *both* the
claim (what the result rows should mean) and the mechanism (what the planner binds and the optimizer
executes). A query that won't bind is fiction; a query that binds with no examined grain is "returns
rows, wrong answer" waiting to happen.

That crossing is the whole technique. A query can be:

- **right logic, won't bind/run** — correct join keys, grouping, and intent, but a hallucinated
  column, a misspelled table, a missing comma, or a syntax error the dialect rejects. The classic LLM
  failure: plausible SQL that references a column that isn't there.
- **returns rows, answers wrong question / wrong grain** — parses, binds, runs, returns a clean
  result set — but a silent join fan-out double-counts every measure, or it answers an adjacent
  question, or a `NULL`-rejecting `WHERE` quietly turned an `OUTER JOIN` into an `INNER`. The classic
  LLM trap: a clean result set on the wrong thing.

Opposite defects, opposite fixes — so you **score and report the two axes separately, never
averaged.** An averaged score hides which one you have, and they need opposite work (fix an
identifier vs re-derive the grain).

## The leveled walk

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Semantics** | whole → part | **A1** Question `[gate]` → **A2** Grain `[gate]` → **A3** Joins/filters → **A4** Aggregation/windows → **A5** Fit | "Is it the *right query*?" |
| **B · Execution** | part → whole | **B1** Parses `[gate, code]` → **B2** Binds `[gate, code]` → **B3** Plan/Run `[gate, code]` → **B4** Performance → **B5** Safety | "Does it *provably run*, here?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** — a failure cascades and BLOCKS the reviews below it on
that axis. `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable query is **≥4 on every review with
zero gate failures**, reported as two separate axis scores plus the quadrant cell.

### A · Semantics (whole → part)

- **A1 Question `[gate]`** — does the query answer the *actual* question, in one sentence, not an
  adjacent one? "Revenue per customer" and "revenue per order" are one join apart and look the same
  in SQL. Wrong question ⇒ everything below is moot.
- **A2 Grain `[gate]`** — the result contract: **one row per WHAT** is the unit of analysis. Name it
  before reading the joins. A wrong grain double-counts silently and poisons every measure under it.
- **A3 Joins/filters `[review]`** — correct join keys; no accidental fan-out or cartesian product;
  `WHERE` is correct and `NULL`-aware (a `WHERE` on an outer-joined column that rejects `NULL`
  silently demotes the join to inner).
- **A4 Aggregation/windows `[review]`** — `GROUP BY` is complete (every non-aggregated select column
  present); `HAVING` vs `WHERE` used correctly; window frames (`ROWS`/`RANGE`, `PARTITION BY`,
  `ORDER BY`) are right; `NULL`-in-aggregate handled (`COUNT(col)` ≠ `COUNT(*)`).
- **A5 Fit `[review]`** — matches schema conventions and naming; predicates are **sargable** (no
  function wrapping an indexed column); right dialect idioms; no needless subqueries the planner
  can't flatten.

### B · Execution (part → whole)

- **B1 Parses `[gate, code]`** — syntactically valid SQL for the target dialect. Routed to
  `bin/query-harness.py`.
- **B2 Binds `[gate, code]`** — every table, column, and function **exists in the schema** (the #1
  hallucination — a confident reference to a column that isn't there). A dry-run / prepare proves it.
- **B3 Plan/Run `[gate, code]`** — `EXPLAIN` (or dry-run) succeeds **and the plan shows no cartesian
  explosion** — no nested-loop over an unconstrained join, no row-estimate blowup. The plan is the
  evidence; the exit code alone is not.
- **B4 Performance `[review]`** — uses indexes / partition pruning; bounded scan; no surprise
  full-table scan; estimated cost is proportional to the answer size.
- **B5 Safety/determinism `[review]`** — stable `ORDER BY` under `LIMIT` (else the page is
  nondeterministic); no unguarded `UPDATE`/`DELETE` (a missing `WHERE` is catastrophic);
  transaction scope is correct; no reliance on implicit row order.

## The opposite-defect quadrant

```
                 B · EXECUTION passes      B · EXECUTION fails
A · SEMANTICS┌────────────────────────┬────────────────────────┐
  passes     │      SHIPPABLE         │  right logic, won't     │
             │                        │  run — correct grain &  │
             │                        │  joins, but a           │
             │                        │  hallucinated column /  │
             │                        │  typo'd table / syntax  │
             ├────────────────────────┼────────────────────────┤
A · SEMANTICS│ returns rows, wrong    │       REBUILD           │
  fails      │ question/grain —       │                         │
             │ parses, binds, runs,   │                         │
             │ returns a clean result │                         │
             │ set, but a silent      │                         │
             │ fan-out double-counts  │                         │
             └────────────────────────┴────────────────────────┘
```

The quadrant **names the fix**: top-right needs an identifier/syntax fix the engine points at;
bottom-left needs *grain/question* work the engine **cannot see** — it ran fine.

## The doctrine — grain is the contract; prove it, don't read it

This is why the skill earns its place (and why it's outsized for an LLM author):

- **The result grain is the contract.** "One row per WHAT" is the claim every downstream number
  trusts. A wrong grain double-counts silently — a clean result set, plausible numbers, an invisible
  fan-out. Lock the grain (A2) before the joins, and **prove it with a uniqueness/row-count check**
  (`COUNT(*)` vs `COUNT(DISTINCT key)`, plus reconciling a known total), not by reading the SQL.
  See `grain-and-joins.md`.
- **The EXECUTION gates (B1/B2/B3) are the cheap axis** — run the real `EXPLAIN`/dry-run via
  `bin/query-harness.py`. They catch *right-logic-won't-bind* deterministically. **Trust the engine,
  not the read-through** — an LLM cannot reliably tell by reading whether a column exists or a plan
  fans out. A hallucinated column name reads perfectly; only the binder knows.

## Modes

- **SPECIFY** (before writing) — walk Semantics-down (question → grain → joins → aggregation),
  declare the execution plan (which dialect, which tables, what the grain check will be), emit a
  **query-spec card**.
- **DECOMPOSE** (existing query) — recover the question (A1) and grain (A2) from the SQL, run the
  execution ladder (B1–B3 via the harness + `sql-lint.py`), prove the grain, score the reviews; emit
  the card + a gap list (e.g. *"binds and runs, but `COUNT(*)` > `COUNT(DISTINCT customer)` — the
  order join fanned out; every `SUM` is inflated"*).
- **GRADE** — score both axes, gates first (run the harness + lint + grain check), place in the
  quadrant, name one corrective per failure.

## Walk order (do not skip)

1. **A1 Question / A2 Grain** — name the question in one sentence and the grain ("one row per ___").
   Wrong ⇒ stop, re-spec.
2. **B1/B2/B3 Execution** — run `query-harness.py` (parse + bind + `EXPLAIN`). Red gate ⇒ fix before
   reviewing (you can't grade aggregation for a query that won't bind).
3. **Prove the grain** — wrap the query, check `COUNT(*) == COUNT(DISTINCT key)` and reconcile a
   known total. Mismatch ⇒ a join fanned out; the result is wrong regardless of the green plan.
4. **A1/A3 adversarial probe** — in a fresh context, ask "what question does this *actually* answer?"
   and hunt one row the contract forbids (a duplicated key, a `NULL` group, an `INNER` masquerading
   as `OUTER`).
5. **Reviews** — A3–A5 then B4–B5, 1–5 each. Below 4 ⇒ name the single corrective.
6. **Report** — two axis scores, the quadrant cell, gate failures first; hand the verified
   query-spec card + plan report to `code-decomposer` (surrounding code) or a reviewer.
