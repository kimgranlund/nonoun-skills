# Worked example — silent fan-out on SEMANTICS × EXECUTION

A complete DECOMPOSE → fix → GRADE for a query that **returns rows** but at the wrong grain — the
signature failure `query-decomposer` exists to catch. The two `.sql` files here are checked in and
`bin/sql-lint.py` actually flags / clears them.

## The artifact

"List each active user with their role name." The query runs, returns rows, looks joined — it even
filters on status. Ship it?

```sql
SELECT u.id, r.name FROM users u, roles r WHERE u.status = 'active';
```

## DECOMPOSE

**A · Semantics** (whole → part)
- **A1 Question** `[gate]` — "one row per active user, with that user's role name." ✓
- **A2 Grain** `[gate]` — the contract is **one row per user**. *Claim:* this query holds it. The
  `WHERE u.status = 'active'` is a **filter on a literal**, not a join predicate — nothing relates
  `users` to `roles`. So the real grain is `users × roles` (every active user paired with *every*
  role). The grain claim is suspect; prove it before reading aggregation/fit.

**B · Execution** (part → whole)
- B1 Parses / B2 Binds `[gate]` — assume green (it runs).
- **B3 Plan/Run** `[gate, code]` — a returns-rows query is evidence of nothing if the grain is
  wrong. Run the SQL smell pre-filter on the artifact (`examples/active-roles.red.sql`):

```
$ python3 bin/sql-lint.py examples/active-roles.red.sql
  examples/active-roles.red.sql:4  IMPLICIT_CROSS_JOIN FROM lists 2 tables with no join predicate — cartesian product
sql-lint: 1 smell(s) across 1 file(s) — verify grain with COUNT(*) vs COUNT(DISTINCT key)
```

**A2 has actually failed, proven mechanically.** A comma-FROM with two tables and no
`col = col` predicate is a cartesian — the linter sees that the only `=` is a literal filter, not a
join. The row count is `active_users × roles`; the grain is blown. (Next rung: `COUNT(*)` vs
`COUNT(DISTINCT u.id)` confirms the fan-out live.)

## Fix — add the real join predicate

Relate the tables through a column=column join, not a filter (`examples/active-roles.green.sql`):

```sql
SELECT u.id, r.name FROM users u JOIN roles r ON r.id = u.role_id WHERE u.status = 'active';
```

```
$ python3 bin/sql-lint.py examples/active-roles.green.sql
sql-lint: OK — no smells in 1 file(s)
```

The `ON r.id = u.role_id` restores the one-row-per-user grain; `status` stays a filter, where it
belongs. The red→green transition is the proof that A2 now holds.

## GRADE — two scores, never averaged

- **Semantics: A2 gate-fail → (after fix) 5/5** — right question; grain now matches it (one row per
  user, not the cartesian); joins/filters/aggregation/fit clear.
- **Execution: 5/5** — parses, binds, and the smell gate is green (no cartesian).

**Quadrant:** the red query sat in **"returns rows, wrong grain"** (Execution looked fine — it runs —
but Semantics' grain was a hidden fan-out) — *runs right, answers wrong*. The fix is a join
predicate, not query tuning. After it: **SHIPPABLE**.

The lesson: "does it return rows?" is the wrong question; "is every FROM table tied by a real join
predicate, or is a literal filter masquerading as one?" is the right one — and that's mechanizable.
