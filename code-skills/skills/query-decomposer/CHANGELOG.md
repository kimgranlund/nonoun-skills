# Changelog — query-decomposer

Versioned independently of the `code-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.2.2 — beta

Deepened `bin/sql-lint.py` with the last ROADMAP-tracked smell, locked with must-flag **and**
must-not-flag selftest fixtures (`selftest` still exits 0; all prior smells + their FP guards intact):

- **NON_SARGABLE** (A5/B4) — a `WHERE` or `JOIN ... ON` predicate that wraps a likely-indexed column
  in a **function** (`DATE(created_at)='...'`, `UPPER(name)='X'`, `COALESCE(status,'')='x'`), in
  **arithmetic** (`price*1.2>100`, `col+0=5`), or uses a **leading-wildcard `LIKE`** (`name LIKE
  '%foo'`) defeats an index on the raw column. Advisory; the fix is to move the transform to the
  literal side or store a computed column.

False-positive guards (must NOT flag): a function/arithmetic on the **literal** side only
(`created_at = DATE('...')`, `ts >= NOW() - INTERVAL '7 days'` — the column stays bare); an anchored
`LIKE 'foo%'` (sargable — only a *leading* `%` flags); a bare `col = 'lit'`; and `HAVING` aggregates
(`COUNT(*) > 5`) — NON_SARGABLE is scoped to `WHERE`/`JOIN-ON` predicates, not `HAVING` or bare
`SELECT` items. It reuses the length-preserving `normalize()` (a function name inside a string literal
or comment can't trip it), and reads the original un-blanked text only to test the leading-`%` of a
`LIKE`. `references/grain-and-joins.md` gains it in the smell table; the ROADMAP item is marked done.

## 0.2.1 — beta

Deepened the SEMANTICS gate in `bin/sql-lint.py` with the two highest-value grain smells the
ROADMAP tracked, each locked with must-flag **and** must-not-flag selftest fixtures (`selftest`
still exits 0; all prior smells + their FP guards intact):

- **JOIN_FANOUT** — the #1 grain killer. A query that joins a parent to ≥2 distinct tables
  (explicit `JOIN`s + comma-`FROM` tables beyond the first) with **no** `GROUP BY`, **no**
  `SELECT DISTINCT`, and **no** aggregate in `SELECT` can silently *multiply* rows (1:N × 1:N
  fan-out — "returns rows, wrong grain"). Advisory; any collapsing construct suppresses it.
  Verify with `COUNT(*)` vs `COUNT(DISTINCT key)`.
- **OUTER_JOIN_DEMOTED** — a `LEFT`/`RIGHT [OUTER] JOIN`'d table/alias appearing in a plain
  `WHERE` predicate (`=,<,>,<=,>=,<>,LIKE,IN`) — anything but `IS [NOT] NULL` — silently demotes
  the outer join to an `INNER` join (the `NULL`-extended rows are filtered out, a real semantic
  change). The `IS NULL` anti-join and predicates on the driving (LEFT) table are excluded.

Both reuse the existing comment/string-stripping `normalize()` (comments can't fool them) and
count joins on the paren-stripped top-level statement (subquery joins don't inflate the count).
`references/grain-and-joins.md` (the centerpiece) gains both in its failure-mode tables; the two
ROADMAP items are marked done.

## 0.2.0 — beta

Promoted to beta as part of the marketplace **v0.2.0** milestone (see the root CHANGELOG). This cycle the skill gained a checked-in, sibling-collision-tested routing-eval corpus, an adversarial-review hardening pass (fixes locked as selftest fixtures), and a worked `examples/walkthrough.md` (a red→green bin proof).

## 0.1.0 — draft

Initial release. Decompose / design / grade a SQL query on the **SEMANTICS × EXECUTION** crossing
axes, scored separately with a gated rubric and the opposite-defect quadrant.

- **The two-axis method** (`references/decomposition-method.md`): Semantics (question → grain →
  joins/filters → aggregation/windows → fit) × Execution (parses → binds → plan/run → performance →
  safety), crossing at the query-against-the-schema; gates before reviews; the *right-logic-won't-bind*
  vs *returns-rows-wrong-grain* quadrant; and the **grain-is-the-contract, prove-it-don't-read-it**
  doctrine.
- **The EXECUTION harness** (`references/execution-axis.md` + `bin/query-harness.py`): a thin adapter
  that reads a per-project command manifest, runs each present gate (parse/bind/explain/run) against
  the real engine, and normalizes verdicts to a plan report card — a missing engine is a SKIP, not a
  pass. `selftest` proves the parse + normalize + run/skip logic with no external deps.
- **The SQL smell linter** (`references/grain-and-joins.md` + `bin/sql-lint.py`): the mechanized
  static pre-filter for the *returns rows, wrong grain* quadrant. Flags SELECT *, UPDATE/DELETE with
  no WHERE, implicit cross join (multi-table FROM with no predicate), LIMIT with no ORDER BY, and a
  GROUP-BY-incompleteness heuristic; a clean query passes, each smell is caught.
- **The SEMANTICS axis** (`references/semantics-axis.md`): framing the question, the grain contract,
  join/filter correctness, the NULL/aggregate traps, and the fresh-context **adversarial
  wrong-question probe**.
- **Grain & joins** (`references/grain-and-joins.md`): the centerpiece — the fan-out failure-mode
  table, and how a **uniqueness/row-count check (`COUNT(*)` vs `COUNT(DISTINCT key)`) proves the
  grain** where reading the SQL cannot.
- **Dialects** (`references/dialects.md`): Postgres · MySQL · SQLite · BigQuery · Snowflake, each
  with the GROUP BY / NULL / typing / window / cost differences that flip a query to won't-bind or
  wrong-answer.
- **Policy** (`references/policy.md`): the 10-point definition-of-done, the query-spec card
  `{question, grain, tables[], plan_verdict}` + plan-report shapes, the harness manifest, and the
  handoff seams to `code-decomposer`, `regex-decomposer`, `arch-system`, and a reviewer.

Second skill in the `code-skills` plugin (sibling to `code-decomposer`).
