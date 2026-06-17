# Roadmap — query-decomposer

Ships its core in 0.1.0 (the two axes, the query harness, the SQL smell linter, the query-spec/plan
cards, the dialect playbooks). Everything below is additive.

## `bin/sql-lint.py`

- [x] **Two-1:N-join fan-out heuristic** — the highest-value grain smell currently left to the live
      `COUNT` check: flag a query that joins two distinct 1:N tables to the same parent without an
      intervening aggregation. *Shipped 0.2.1 as `JOIN_FANOUT`: ≥2 joined tables (explicit `JOIN`s +
      comma-`FROM` beyond the first) with no `GROUP BY`/`DISTINCT`/aggregate ⇒ advisory flag.*
- [x] **NULL-rejecting WHERE on an outer join** — detect `LEFT JOIN t ... WHERE t.col <op> ...`
      (the silent `INNER` demotion), the dominant A3 defect. *Shipped 0.2.1 as `OUTER_JOIN_DEMOTED`:
      a plain `WHERE` predicate (`=,<,>,<=,>=,<>,LIKE,IN`, never `IS [NOT] NULL`) on a `LEFT`/`RIGHT`-
      joined table/alias ⇒ flag; the `IS NULL` anti-join is excluded.*
- [ ] **Non-sargable predicate** — flag a function wrapping a likely-indexed column in `WHERE`
      (`WHERE DATE(created) = ...`), the A5/B4 smell.
- [ ] Emit a machine-readable report (JSON) so GRADE can fold smell signals into the plan report card.

## `bin/query-harness.py`

- [ ] **A grain-check phase** — a first-class `grain` gate that wraps the query and runs the
      `COUNT(*)` vs `COUNT(DISTINCT key)` check, so the most dangerous defect is mechanized end-to-end
      rather than run by hand.
- [ ] **Plan parsing** — read the `EXPLAIN` output and flag a `Nested Loop` with no join condition /
      a row-estimate blowup automatically, instead of leaving the plan read to the human.
- [ ] Per-phase **timeout** + output capture to the report card; a `--json` report mode.
- [ ] A small **manifest registry** of starter manifests per engine (postgres/psql, mysql,
      sqlite3, bigquery/bq, snowflake/snowsql) the skill can drop in.

## Method & corpus

- [ ] A **routing-eval corpus** (the maturity step the repo ROADMAP tracks) — especially the
      boundaries with `code-decomposer` (surrounding code), `regex-decomposer` (text patterns),
      `arch-system` (schema design), and a reviewer, which are the likely mis-routes.
- [ ] A worked **end-to-end transcript** (a `revenue per customer` SPECIFY → write → DECOMPOSE →
      GRADE) with the query-spec card, the plan report, and a caught fan-out (`COUNT(*)` >
      `COUNT(DISTINCT customer)`) fix checked in and dogfooded.
- [ ] An **adversarial-probe template** (the fresh-context "what question does this actually answer,
      at what grain?" skeptic prompt) as a reusable reference, shared in shape with `deep-research`'s
      verify step.
- [ ] A `dialect-*` deepening for the highest-risk engines (BigQuery/Snowflake cost-as-correctness;
      MySQL `ONLY_FULL_GROUP_BY`) if the single `dialects.md` table proves too thin.

## Plugin

- [ ] As `code-skills` grows, the COMPOSE/REALIZE lineage continues: this skill pairs with
      `code-decomposer` (the function around the query) and `regex-decomposer` (a `LIKE`/regex
      predicate's match behavior) — all three with deterministic example-set gates that route
      computation to `bin/` rather than inference.
