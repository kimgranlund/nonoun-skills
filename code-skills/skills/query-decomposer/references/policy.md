# Policy — definition-of-done, the cards, and the handoff

The reusable artifacts and boundaries: what "done" means, the shape of the two cards the skill emits,
the harness manifest, and how this hands off to the rest of the fleet without overlapping it.

## Definition-of-done (a query is shippable when…)

Gated items route to `bin/`; review items are 1–5 judgments. SHIPPABLE = the quadrant top-left.

1. **Right question (A1)** — answers the actual question, stated in one sentence.
2. **Named ∧ proven grain (A2)** — the grain ("one row per ___") is explicit **and** the live result
   is unique on the grain key (`COUNT(*) == COUNT(DISTINCT key)`) **and** a known total reconciles.
3. **Correct joins & filters (A3)** — right keys, no accidental fan-out/cartesian, `NULL`-aware
   `WHERE` that doesn't demote an outer join (≥4).
4. **Correct aggregation & windows (A4)** — complete `GROUP BY`, right `HAVING`/`WHERE`, correct
   window frames, `NULL`-in-aggregate handled (≥4).
5. **Fits the schema (A5)** — matches conventions, sargable predicates, right dialect idioms, no
   duplication of an existing view (≥4).
6. **Parses & binds (B1/B2)** — `query-harness.py` parse + bind gates ran green against the *target
   dialect*; no nonexistent table/column/function.
7. **Plan/Run green ∧ no cartesian (B3)** — the `EXPLAIN` gate ran green **and** the plan shows no
   cartesian/fan-out (no nested-loop over an unconstrained join, no row-estimate blowup).
8. **Performant (B4)** — uses indexes/partition pruning; bounded scan; cost ∝ answer size (≥4).
9. **Safe & deterministic (B5)** — stable `ORDER BY` under `LIMIT`; guarded `UPDATE`/`DELETE`;
   correct transaction scope; no reliance on implicit row order (≥4).
10. **Both axes ≥4, zero gate fails, SHIPPABLE quadrant** — reported as two scores, gate failures
    first, with the query-spec card + plan report ready for handoff.

## The two cards

**Query-spec card** (`*.query.json`) — emitted by SPECIFY, re-derived by DECOMPOSE:
```json
{
  "query": "revenue_per_customer_q3",
  "dialect": "postgres",
  "question": "total paid revenue per customer in Q3",
  "grain": "one row per customer_id",
  "measure": {"expr": "SUM(o.amount)", "additivity": "additive"},
  "tables": ["customers c", "orders o"],
  "join_paths": ["c.id = o.customer_id (1:N — aggregate orders first)"],
  "grain_check": "COUNT(*) == COUNT(DISTINCT customer_id)",
  "plan_verdict": "no cartesian; index scan on orders(customer_id, created_at)"
}
```

**Plan report card** — emitted by the harness + lint + grain check:
```
phase     gate    ran   verdict
parse     gate    yes   pass
bind      gate    yes   pass
explain   gate    yes   pass
run       advise  yes   pass
grain:    COUNT(*)=412  COUNT(DISTINCT customer_id)=412   <- unique on grain ✓
lint:     SELECT_STAR x0 · IMPLICIT_CROSS_JOIN x0 · MISSING_WHERE_DML x0 · LIMIT_NO_ORDER x0
```

A `grain:` line where `COUNT(*)` > the distinct key, or a non-reconciling total, is the *returns
rows, wrong grain* quadrant — B is green, A2 fails.

## The harness adapter manifest

The per-project command map `query-harness.py` reads (`template` prints a starter). `gate` defaults:
parse/bind/explain gate; run is advisory (it touches data). Commit one manifest per project root and
set `"dialect"` to the engine that executes the query, so the skill's gates run against the *same*
engine production does — a query that binds on SQLite may not bind on Postgres.

## Handoff — what this skill does NOT do

The fleet has clear seams; `query-decomposer` owns **query semantics + execution grading** and feeds
the others:

- **→ `code-decomposer`**: receives the verified query-spec card and grades the *surrounding
  application code* — the function that builds the query string, binds parameters, maps rows to
  objects, handles the empty result. This skill grades the *query*; `code-decomposer` grades the
  *code around it*. Don't re-grade the function's contract here.
- **← `regex-decomposer`**: owns *text/string patterns* (a `LIKE`/regex predicate's match behavior is
  its territory, not this skill's). Hand a gnarly pattern there; grade the query that uses it here.
- **← `arch-system` / a data architect**: owns *schema design* — table structure, keys, indexes,
  normalization. This skill grades a query *against* an existing schema; it does not design the
  schema. A missing index is a B4 flag here and a schema task there.
- **→ a reviewer / `/code-review`**: receives the query-spec card + plan report and audits the
  finished change. `query-decomposer` is design-time and query-scoped.

## Governance

- **Query-spec cards are checked in** next to the query (or the migration/report) as the contract of
  record — especially the **grain** and the **grain_check**, the two lines a reviewer reads first.
- **The manifest tracks the engine** — set the dialect; if production moves engines, update it so the
  bind gate can't pass against the wrong grammar.
- **The grain check is cheap — run it every time.** It is the everywhere-gate for the most dangerous
  defect; the `EXPLAIN` plan read is the targeted proof for the cartesian. Never ship a `SUM`/`COUNT`
  query without the row-count/uniqueness check having run green.
