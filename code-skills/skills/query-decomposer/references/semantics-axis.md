# The SEMANTICS axis — is it the right query?

The Semantics axis (A1–A5) grades *intent*, top-down: from the question the query must answer to the
detail of how it fits the schema. This is the axis the engine **cannot see** — a planner is silent on
"this answers the wrong question" and "this is at the wrong grain." It is also the axis LLMs fail
silently on (a confident, plausible, clean-looking result set on the wrong thing), so it carries an
**adversarial probe**, not just a checklist.

## A1 · Question `[gate]`

Name the question in one sentence, in the user's terms, before reading the SQL. Then ask: does this
query answer *that*, or an adjacent thing it's easy to drift to?

- Distinguish the **asked** question from the **assumed** one. "Revenue per customer" and "revenue per
  order" differ by one join and one grain; "active users" depends entirely on the definition of
  *active*. An LLM answers the most familiar neighbour of the real request.
- Surface the implicit acceptance criteria: what known number would prove it's right? (Last quarter's
  revenue total you can reconcile against; a customer count you already trust.)
- **Gate:** if the query answers the wrong question, stop — every level below is polishing the wrong
  result. Re-spec, don't refine.

## A2 · Grain `[gate]`

The grain is the crossing seam with EXECUTION and **the contract every downstream number trusts**:
*one row per WHAT* is the unit of analysis. State it explicitly even when the SQL doesn't:

- **One row per ___** — per customer? per customer-per-month? per order-line? The grain is the
  primary key of the result set, and it must be unique on that key or every aggregate is suspect.
- **The measure's grain must match.** `SUM(order.amount)` grouped by customer is only right if each
  order appears **once** in the joined rowset. A join that fans the orders out (e.g. customer →
  orders → order_items) multiplies every order's amount by its item count — silently.
- **Additivity** — is the measure additive across the grain (revenue), semi-additive (a balance,
  additive across entities but not time), or non-additive (a ratio, an average-of-averages)? A
  non-additive measure summed at the wrong grain is wrong even with no fan-out.
- **Gate:** a wrong grain double-counts silently and poisons cases, joins, and review. Lock it first,
  and **prove it with the row-count/uniqueness check** in `grain-and-joins.md` — don't certify it by
  reading.

## A3 · Joins & filters `[review]`

Enumerate the join graph and the filter semantics — this is where the silent fan-out lives:

- **Join keys** are correct and on the right cardinality (1:1, 1:N, N:M). An N:M join through a
  bridge table without aggregating first is the classic fan-out.
- **No accidental cartesian** — every table in the `FROM` has a join predicate connecting it; a
  comma-join or a missing `ON` is a cross product (`sql-lint.py` flags the static case).
- **`WHERE` is `NULL`-aware.** A predicate on an outer-joined table's column (`WHERE o.status =
  'paid'`) **rejects the `NULL`s the outer join produced**, silently turning a `LEFT JOIN` into an
  `INNER JOIN`. Move it to the `ON` clause or guard it `OR o.id IS NULL`.
- **Filter placement** — `WHERE` filters rows before grouping; the wrong predicate excludes rows you
  meant to count as zero. The forbidden rows the question rules out — are they actually excluded?

## A4 · Aggregation & windows `[review]`

The aggregate layer, where grain meets arithmetic:

- **`GROUP BY` completeness** — every non-aggregated column in the `SELECT` is in the `GROUP BY` (or
  the query is wrong; some dialects reject it, MySQL with `ONLY_FULL_GROUP_BY` off silently picks an
  arbitrary row — see `dialects.md`).
- **`HAVING` vs `WHERE`** — `WHERE` filters rows, `HAVING` filters groups. Filtering a pre-aggregate
  condition in `HAVING` (or vice versa) changes the answer.
- **`NULL`-in-aggregate** — `COUNT(col)` skips `NULL`s, `COUNT(*)` counts rows; `AVG`/`SUM` skip
  `NULL`s. "Average that treats missing as zero" needs `COALESCE`, not `AVG`. A `NULL` in a `GROUP
  BY` key forms its own group.
- **Window frames** — `PARTITION BY` sets the grain of the window, `ORDER BY` sets the running order,
  and the **frame** (`ROWS BETWEEN ... ` vs the default `RANGE`) changes running totals on ties. A
  ranking with a non-deterministic tie-break (`ROW_NUMBER` over a non-unique order) is unstable.

## A5 · Fit `[review]`

Coherence with the schema — the difference between *runs* and *belongs*:

- Matches schema conventions: naming, the canonical join paths, the agreed definition of derived
  metrics (one team's "active" is another's churn).
- **Sargable predicates** — no function wrapping an indexed column (`WHERE DATE(created) = ...`
  defeats the index; use a range on `created`). This is correctness-adjacent on a scanned warehouse
  where cost is the bytes read.
- Right dialect idioms; no needless nested subquery the planner can't flatten; no duplication of an
  existing view/CTE that already encodes the right grain.

## The adversarial SEMANTICS probe (route A1/A2 to a skeptic, not the author)

The dangerous defect — *returns rows, wrong question/grain* — lives here, and it is not
deterministically gateable from the SQL alone. So verify it the way `deep-research` verifies claims:
**in a fresh context, adversarially.**

- Prompt a separate reviewer (a fresh agent, not the one that wrote the query): *"Here is the stated
  question and the query. (1) What question does this query ACTUALLY answer — at what grain? (2) Find
  one scenario where a row is double-counted or a join silently dropped rows. Default to 'the grain
  is wrong' and search for the fan-out."*
- A verifier that shares the author's context inherits its blind spots and rubber-stamps the clean
  result set. Separation is the point.
- Feed any counterexample back as a missing **A3 join fix** or **A2 grain correction**, and add the
  row-count/uniqueness check that would have caught it.

The output of this axis is the **query-spec card** — the question + the named grain + the tables and
join paths — the artifact GRADE re-derives and SPECIFY emits, and the thing you hand to a reviewer
and to `code-decomposer` (see `policy.md`).
