# The EXECUTION axis — does it provably run, here?

The Execution axis (B1–B5) grades *mechanism*, bottom-up: from "does this SQL even parse" to "does
the whole query behave safely under the real plan." It is the **mechanizable** axis — route it to the
real engine via `bin/query-harness.py` and **trust the engine, not the read-through**. An LLM cannot
reliably tell by reading whether a column exists, a query binds, or a plan fans out into a cartesian
product; running `EXPLAIN`/dry-run is the only evidence.

## The ladder

| Level | Gate | The tool that proves it | The signal |
|---|---|---|---|
| **B1 Parses** | `[gate]` | the dialect parser / `psql -c`, `sqlite3`, dry-run | valid SQL for *this* dialect — not a sibling dialect's grammar |
| **B2 Binds** | `[gate]` | `PREPARE` / dry-run / `EXPLAIN` (no execution) | every table, column, function **exists in the schema** (the #1 hallucination) |
| **B3 Plan/Run** | `[gate]` | `EXPLAIN` (+ `EXPLAIN ANALYZE` on a fixture) | the plan succeeds **and shows no cartesian/fan-out** — no nested-loop over an unconstrained join |
| **B4 Performance** | review | `EXPLAIN ANALYZE` / the cost estimate | uses indexes / partition pruning; bounded scan; cost ∝ answer size |
| **B5 Safety** | review | the SQL itself + the harness | stable `ORDER BY` under `LIMIT`; guarded `UPDATE`/`DELETE`; correct txn scope |

The gates cascade: don't grade performance (B4) for a query that won't bind (B2). A red gate stops
the axis — fix it before reviewing.

## The live-gate protocol (the harness)

`bin/query-harness.py` is a thin adapter, not a bundled database. You declare the project's commands
once; it runs each phase whose tool is on PATH and normalizes the verdicts. A missing tool is a
**SKIP** (evidence incomplete), never a pass — like the execution-harness in `code-decomposer`, the
static logic is self-tested with no deps; the live run fires where the engine exists.

```json
{
  "dialect": "postgres",
  "gates": {
    "parse":   { "cmd": "psql -d app -c \"PREPARE _q AS SELECT 1\"" },
    "bind":    { "cmd": "psql -d app -v ON_ERROR_STOP=1 -c \"EXPLAIN SELECT 1\"" },
    "explain": { "cmd": "psql -d app -c \"EXPLAIN SELECT * FROM orders LIMIT 1\"" },
    "run":     { "cmd": "psql -d app -c \"EXPLAIN ANALYZE SELECT 1\"", "gate": false }
  }
}
```

`gate` defaults: parse / bind / explain gate; run is advisory (it touches data). Run it:

```sh
python3 bin/query-harness.py template          # print a starter manifest
python3 bin/query-harness.py manifest.json     # run present gates; report card; nonzero on gate fail
```

Read the card honestly: a **skipped** gate means you have *no evidence* for that level, not a pass.
A SHIPPABLE verdict requires the gates to have actually **run green**, not merely "not failed."

## Reading each tool's signal

- **Parse** — the cheapest gate: a misplaced comma, a reserved word used as an identifier, a
  dialect-specific clause (`QUALIFY` on Postgres) caught before anything else. Run it first.
- **Bind** — confirms every identifier resolves against the *real schema*. This catches the #1
  hallucination: a confident `SELECT customer.lifetime_value` where the column doesn't exist. A
  `PREPARE` or dry-run binds without executing. Treat `SELECT *` as un-bound surface — it hides
  whether the columns you *think* exist do.
- **EXPLAIN (plan)** — the decisive gate. Read the plan, don't just check the exit code:
  - **Nested Loop with no join condition** / a `CROSS JOIN` node ⇒ a cartesian product — the silent
    fan-out's worst case. `sql-lint.py` flags the static "multiple tables, no predicate" smell; the
    plan confirms it on the real schema.
  - **Row-estimate blowup** — an intermediate row estimate orders of magnitude above the table sizes
    is a fan-out signature even when the final result looks small.
  - **Seq Scan on a large table** under a filter that should use an index ⇒ a B4 performance flag
    (often a non-sargable predicate — see `semantics-axis.md` A5).
- **EXPLAIN ANALYZE** — the proof for B4: actual vs estimated rows, actual time, buffers/bytes read.
  Advisory by cost (it runs the query), decisive in judgment.

## B4 Performance & B5 Safety (reviews)

- **B4** — beyond "it runs": does it use the indexes/partitions it should? Is the scan bounded? On a
  warehouse (BigQuery/Snowflake) the cost *is* bytes scanned — an unpartitioned scan is both slow and
  expensive, and partition pruning is correctness-adjacent.
- **B5** — determinism and blast radius:
  - **Stable `ORDER BY` under `LIMIT`** — `LIMIT` without a total `ORDER BY` (one whose key is unique)
    returns an arbitrary, nondeterministic page. Pagination silently skips/repeats rows.
  - **Guarded mutation** — an `UPDATE`/`DELETE` with no `WHERE` rewrites the whole table.
    `sql-lint.py` flags this statically; it is the single most catastrophic SQL defect.
  - **Transaction scope** — multi-statement writes are wrapped in a transaction; the query doesn't
    rely on implicit row order or isolation it doesn't have.

The output of this axis is the **plan report card** — which gates ran, their verdicts, and the plan's
fan-out/scan findings — handed alongside the query-spec card to a reviewer and to `code-decomposer`.
