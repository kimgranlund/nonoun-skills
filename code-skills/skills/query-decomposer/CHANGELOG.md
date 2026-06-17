# Changelog — query-decomposer

Versioned independently of the `code-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

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
