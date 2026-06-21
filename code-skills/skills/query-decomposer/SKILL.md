---
name: query-decomposer
description: >
  Decompose, design, and grade a SQL query on two crossing axes — SEMANTICS (question → grain →
  joins/filters → aggregation → fit) and EXECUTION (parses → binds → plan/run → performance →
  safety) — scored separately so a query that returns rows can't hide that it answers the wrong
  question or at the wrong grain, nor a correct idea hide a column that won't bind. EXECUTION routes
  to the real EXPLAIN/dry-run via a self-tested harness (bin/query-harness.py); the wrong-grain /
  fan-out failure routes to a static SQL smell linter (bin/sql-lint.py: implicit cross join,
  missing-WHERE DML) plus a row-count/uniqueness grain check. Backed by a gated rubric, a query-spec
  card + plan-report protocol, and dialect playbooks. Use when deciding whether a query is right,
  recovering what it answers, or proving its grain. NOT for a unit of application code — a function
  or implementation graded on its spec (code-decomposer); a regular expression / regex pattern
  (regex-decomposer); or schema design (architecture-decomposer).
---

# query-decomposer — grade a SQL query on two crossing axes

A SQL query is **correct on two independent axes that walk the same hierarchy in opposite
directions** — the decomposer seam the layout-, mermaid-, component-, and code-decomposers apply to
space, diagrams, components, and functions, here applied to an analytics or transactional query:

- **Semantics · whole → part** grades the **intent**: the question it must answer → its result grain
  → its joins & filters → its aggregation & windows → its fit with the schema. *"Is it the right
  query?"*
- **Execution · part → whole** grades the **mechanism**: it parses → every table/column binds → the
  plan runs without a cartesian explosion → it performs → it's safe & deterministic. *"Does it
  provably run, here?"*

They **cross at the query measured against the schema** — the SELECT list + joins are *both* the
claim (what the result rows should mean) and the mechanism (what the planner binds and the optimizer
executes). That crossing is the whole technique: a query can be **right logic, won't bind/run**
(correct join keys and grouping, but a hallucinated column or a syntax error) or **returns rows,
answers wrong question / wrong grain** (parses, binds, runs, returns a clean result set — but a
silent join fan-out double-counts, or it answers an adjacent question). Opposite defects, opposite
fixes — so you **score and report the two axes separately**, never averaged.

The reason this is outsized for an LLM author: EXECUTION is exactly where models hallucinate column
names with the most confidence *and* it is mechanizable — `EXPLAIN`/dry-run converts the worst
binding failure into a caught error. And the **wrong-grain** quadrant — the one a returns-rows
sanity check misses entirely — gets a dedicated attack: a row-count/uniqueness check that *proves*
the grain instead of reading the SQL and hoping.

## Quick Start

**You bring:** a query (a spec, a screenshot of SQL, an existing report query) and the question —
"write this", "is this right?", "is the grain correct?", "why is this number doubled?". **You get:**
a query-spec card (question + grain + tables), a plan report card, and a two-axis grade with the
defect quadrant named.

> *"Does this `revenue per customer` query double-count?"* →
> 1. **Semantics — question → grain:** the question is "total paid revenue per customer last
>    quarter" `[gate]`; the grain contract is **one row per customer**, measure = `SUM(amount)`
>    `[gate]`. Name it before reading the joins.
> 2. **Execution — run it, don't read it:** `bin/query-harness.py` runs parse + bind + EXPLAIN
>    `[gate]`. Binds? Now read the plan for a nested-loop over an unfiltered join — the fan-out
>    signature.
> 3. **Prove the grain, don't eyeball it:** wrap the query and check
>    `COUNT(*) == COUNT(DISTINCT customer_id)`. If rows > distinct customers, a join fanned out and
>    every `SUM` is inflated — the result set looked fine. `bin/sql-lint.py` pre-flags the
>    implicit-cross-join and `SELECT *` smells statically.
> 4. **Review + report:** joins/filters/aggregation (A3/A4), performance/safety (B4/B5), then the
>    two axis scores + the quadrant cell — gate failures first — handed to `code-decomposer` for the
>    surrounding code or to a reviewer.

**Modes:** **SPECIFY** (question → grain → query, top-down) · **DECOMPOSE** (read a query → recover
its question + grain → run the execution ladder → grade) · **GRADE** (score both axes, gates before
reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Semantics** | whole → part | **A1** Question → **A2** Grain → **A3** Joins/filters → **A4** Aggregation/windows → **A5** Fit | "Is it the *right query*?" |
| **B · Execution** | part → whole | **B1** Parses → **B2** Binds → **B3** Plan/Run → **B4** Performance → **B5** Safety | "Does it *provably run*, here?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on
that axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable query is **≥4 on every review with
zero gate failures**, reported as two separate axis scores plus the defect quadrant. `B1/B2/B3` route
to the real engine via `bin/query-harness.py` — never certified by reading.

Reason on **two planes in parallel** (`HOWTO.md`): **OUTSIDE-IN** — the business question and the grain
that answers it (*what's good?*) — and **INSIDE-OUT** — the relational foundations (set semantics,
joins/keys, normalization, the planner's cost model). SEMANTICS grades the OUTSIDE-IN question;
EXECUTION verifies the INSIDE-OUT plan runs. The named canon lives in `architecture-decomposer`'s
`references/architecture-knowledge.md`.

## The doctrine — grain is the contract; prove it, don't read it

The non-obvious core, and the reason it earns a skill:

- **The result grain is the contract** — "one row per WHAT" is the claim every downstream number
  trusts. A query at the wrong grain **double-counts silently**: it returns a clean result set, every
  value is a plausible number, and the join fan-out is invisible until someone reconciles the total.
  Lock the grain (A2) before the joins, and **prove it with a uniqueness/row-count check**, not by
  reading the SQL.
- **EXECUTION is the cheap, deterministic axis** — route B1/B2/B3 to the real `EXPLAIN`/dry-run via
  `bin/query-harness.py` and **trust the engine, not the read-through**. It catches *right logic,
  won't bind* (the hallucinated column, the typo'd table) outright, and the plan exposes the
  cartesian product before it ever runs against data.

## The dialects (pick by what engine runs it)

The semantics are dialect-agnostic; the traps that flip a passing query to *won't bind* or *wrong
answer* are dialect-specific. Match the engine, then the method gets a hazard list — it focuses the
walk, doesn't change it. Full table in `references/dialects.md`.

| Engine | The trap that bites |
|---|---|
| **Postgres** | `GROUP BY` rejects bare non-aggregated columns; `NULL`-safe `IS DISTINCT FROM`; strict typing |
| **MySQL** | `ONLY_FULL_GROUP_BY` off ⇒ silent arbitrary-row pick in a bad GROUP BY; loose type coercion |
| **SQLite** | dynamic typing hides type bugs; limited window support on old versions; no `RIGHT JOIN` (older) |
| **BigQuery / Snowflake** | `QUALIFY` for window filters; cost = bytes scanned (partition pruning is correctness-adjacent); `SAFE_CAST` |

## §SelfAudit

- **Grain is the contract — prove it, don't read it.** Run the `COUNT(*)` vs `COUNT(DISTINCT key)`
  check (and reconcile a known total). A result set that "looks right" is *no evidence* the grain is
  right; a silent fan-out passes every eyeball test.
- **Execution is the gate the LLM fails silently.** Run parse + bind + `EXPLAIN` via
  `query-harness.py`; do not certify "the column exists / it runs" from reading. An unrun gate is *no
  evidence*, not a pass — a hallucinated column name reads perfectly.
- **Read the plan for the cartesian, not just the exit code.** A query can bind and "run" yet carry a
  nested-loop over an unconstrained join. `sql-lint.py` flags the implicit cross join statically; the
  plan confirms it — and `sql-lint.py plan <explain.json>` mechanizes that read, parsing a Postgres
  `EXPLAIN (FORMAT JSON)` file (no live DB) for a `Nested Loop` over a `Seq Scan` / a row-estimate
  blowup so the dangerous plan judgement routes to code, not to a human eyeballing the tree.
- **Gates before reviews, always.** Don't grade aggregation for a query that won't bind, or
  performance for one whose grain is wrong. Stop each axis at its first failed gate.
- **Two scores, never one.** *Right-logic-won't-bind* and *returns-rows-wrong-grain* need opposite
  fixes (fix the SQL identifier vs re-derive the grain). Report both axes and name the quadrant cell;
  never average.
- **Query, not surrounding code.** This skill locks the question + grain + plan verdict and emits the
  card — it does not write the application code around the query (`code-decomposer`), design the
  schema (`architecture-decomposer`), or grade text/regex patterns (`regex-decomposer`). Hand off; don't overlap.

## Verify Target

A query is **done** when: it answers the right question with an explicit, named grain (A1/A2);
joins/filters, aggregation/windows, and fit ≥4; the harness parse + bind + plan gates ran **green**;
the grain is **proven** (row-count == distinct-key, a known total reconciles); performance + safety
≥4 (uses indexes/partitions, stable `ORDER BY` under `LIMIT`, no unguarded `UPDATE`/`DELETE`); and
both axes score ≥4 with zero gate failures, landing in the **SHIPPABLE** quadrant — with the
query-spec card + plan report ready for handoff. **NOT done** when: it parses, binds, and returns
rows but answers an adjacent question or double-counts at the wrong grain (*returns rows, wrong
question/grain*); or the question and grain are right but a column won't bind or the syntax is
invalid (*right logic, won't run*); or a gate was skipped (no engine on PATH) and reported as a pass;
or one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Semantics × Execution), the leveled walk with gates, the quadrant, the grain-is-the-contract doctrine, and the SPECIFY / DECOMPOSE / GRADE workflows |
| `references/semantics-axis.md` | **the Semantics axis** — framing the question in one sentence, the **grain contract**, join/filter correctness, the NULL/aggregate traps (NULL-in-aggregate, HAVING vs WHERE, NULL-rejecting WHERE on an outer join), and the adversarial wrong-question probe |
| `references/execution-axis.md` | **the Execution axis** — the parse → bind → plan/run ladder, the **live-gate protocol** (the harness manifest), and how to read an `EXPLAIN` plan for the cartesian/fan-out signature; mechanized by `bin/query-harness.py` |
| `references/grain-and-joins.md` | **any "is the grain right / why is this doubled?" question** — the centerpiece: result grain, join fan-out, the silent-wrong-answer failure modes, and how a **uniqueness/row-count check proves the grain** where reading the SQL cannot |
| `references/dialects.md` | **picking the engine** — Postgres · MySQL · SQLite · BigQuery · Snowflake, each with the `GROUP BY`/NULL/typing/window/cost differences that flip a query to won't-bind or wrong-answer |
| `references/policy.md` | **definition-of-done / handoff** — the 10-point DoD, the query-spec card `{question, grain, tables[], plan_verdict}` + plan-report shapes, the harness adapter manifest, and the seams to `code-decomposer`, `regex-decomposer`, `architecture-decomposer`, and a reviewer |
| `bin/query-harness.py` | **mechanizes B1–B3** — reads a per-project command manifest, runs each present gate (parse/bind/explain/run), normalizes verdicts to a report card (a missing tool is a SKIP, not a pass). `template` · `<manifest.json>` · `selftest` |
| `bin/sql-lint.py` | **mechanizes the SQL smell pre-filter** — flags `SELECT *`, `UPDATE`/`DELETE` with no `WHERE`, multi-table `FROM` with no join predicate (implicit cross join), `LIMIT` with no `ORDER BY`, likely-incomplete `GROUP BY`, `JOIN_FANOUT`, `OUTER_JOIN_DEMOTED`, `NON_SARGABLE`; `<file\|dir>` · `selftest`. The `plan <explain.json>` subcommand reads a Postgres `EXPLAIN (FORMAT JSON)` file (no live DB) and flags plan smells — `NESTED_LOOP_NO_INDEX`, `ROW_ESTIMATE_BLOWUP` (blocking), `SEQ_SCAN`, `HIGH_COST_SORT` (advisory) — see `references/execution-axis.md` |
