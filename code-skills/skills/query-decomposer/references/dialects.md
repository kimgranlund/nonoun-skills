# Dialects — the differences that flip a query to won't-bind or wrong-answer

The two-axis method is dialect-agnostic; the traps that turn a passing query into *won't bind* (B2)
or *wrong answer* (A4) are dialect-specific. Match the engine, then the method gets a hazard list —
it focuses the walk, it doesn't change it. One query can target more than one engine (a portable
report); take the union of the hazards.

## The hazard table

| Engine | `GROUP BY` | NULL & typing | Windows | Cost / scan | The trap that bites |
|---|---|---|---|---|---|
| **Postgres** | strict — bare non-aggregated columns rejected unless functionally dependent on the PK | strict typing; `IS DISTINCT FROM` for NULL-safe `=`; `NULL` sorts last by default | full window support; no `QUALIFY` (use a subquery) | row-based; index/seq-scan in the plan | a `WHERE` on a `LEFT JOIN`ed column demotes it to `INNER` (universal, but Postgres won't warn) |
| **MySQL** | `ONLY_FULL_GROUP_BY` **off** ⇒ a bad `GROUP BY` **silently picks an arbitrary row** for ungrouped columns — a wrong answer that binds and runs | loose coercion (`'5abc' = 5` is true); `NULL`-unsafe `=`, use `<=>` | window functions only 8.0+; no `QUALIFY` | row-based | the silent arbitrary-row pick is the single most dangerous default — *check `sql_mode`* |
| **SQLite** | lenient — allows bare columns in aggregates (picks a row) | **dynamic typing** — a column can hold any type; type bugs hide until data surprises you | windows 3.25+; older builds lack them | row-based; small-scale | no `RIGHT`/`FULL JOIN` before 3.39; date math is string/`julianday` gymnastics |
| **BigQuery** | standard SQL `GROUP BY`; `GROUP BY ALL` shorthand | `SAFE_CAST` to avoid cast failures aborting the query; `NULL` in `STRUCT`/`ARRAY` | **`QUALIFY`** filters window results inline | **cost = bytes scanned** — partition/cluster pruning is correctness-adjacent (an unpartitioned scan is a real bug) | a non-pruned `WHERE` on a partitioned table scans (and bills) the whole table |
| **Snowflake** | standard; `GROUP BY ALL` | `TRY_CAST`; `NULL`-aware; case-insensitive identifiers unless quoted | **`QUALIFY`**; rich window frames | **cost = credits ∝ data scanned**; micro-partition pruning | quoted vs unquoted identifier case mismatch ⇒ won't-bind; result caching can mask a slow query |

## The portability rules of thumb

- **`QUALIFY` is BigQuery/Snowflake only.** On Postgres/MySQL/SQLite, filter a window with a wrapping
  subquery (`SELECT ... FROM (SELECT ..., ROW_NUMBER() OVER (...) rn) WHERE rn = 1`).
- **String concatenation** — `||` (Postgres/SQLite/Snowflake/standard) vs `CONCAT()` (MySQL, where
  `||` is logical OR unless `PIPES_AS_CONCAT`).
- **`LIMIT` vs `TOP` vs `FETCH FIRST`** — `LIMIT n` (Postgres/MySQL/SQLite/BigQuery), `FETCH FIRST n
  ROWS ONLY` (standard/Snowflake also supports `LIMIT`).
- **Date math** — `INTERVAL '1 day'` (Postgres), `DATE_ADD`/`DATE_SUB` (MySQL/BigQuery),
  `DATEADD` (Snowflake), `julianday`/`date(...)` (SQLite). A date expression is a frequent
  won't-bind across engines.
- **Boolean** — real `BOOLEAN` (Postgres/Snowflake/BigQuery) vs `TINYINT(1)` (MySQL) vs `0/1`
  integers (SQLite). A `WHERE is_active` may not bind where the column is an integer.
- **Identifier quoting** — double-quotes (standard/Postgres), backticks (MySQL/BigQuery), and case
  rules differ (Snowflake folds unquoted to uppercase). A quoted-case mismatch is a silent
  won't-bind.

## How a dialect shifts the walk

- **Where B2 (bind) bites** — the dialect-specific clause (`QUALIFY`, `||`, a date function) is the
  most common won't-bind. Run `parse`/`bind` against the *target* engine, not a sibling.
- **Where A4 (aggregation) bites** — MySQL's `ONLY_FULL_GROUP_BY` off is the canonical *binds, runs,
  wrong answer*: confirm `sql_mode` before trusting any `GROUP BY` on MySQL.
- **Where B4 (performance) becomes correctness** — on BigQuery/Snowflake, an unpartitioned/unpruned
  scan isn't just slow, it bills the whole table; partition pruning belongs in the plan review.

Set the dialect in the harness manifest (`"dialect": "postgres"`) and in the query-spec card, so the
parse/bind gates run against the engine that will actually execute the query.
