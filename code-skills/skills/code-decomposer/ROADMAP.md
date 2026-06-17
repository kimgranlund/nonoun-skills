# Roadmap — code-decomposer

Ships its core in 0.1.0 (the two axes, the execution harness, the test-vacuity linter, the spec/
execution cards, the unit families). Everything below is additive.

## `bin/test-vacuity-check.py`

- [ ] More languages: Go (`go/ast` is out of reach from stdlib Python — regex pass), Rust, Java,
      Ruby. Each as a best-effort regex detector with its own fixtures.
- [ ] **Test-mirrors-implementation** detection — the highest-value judgment smell currently left to
      the reader: flag a test whose expected value is computed with the same expression the unit
      uses (needs the unit source alongside the test).
- [ ] **Assertion-free `expect`** in TS (`expect(x)` with no matcher) and **snapshot-only** files.
- [ ] Emit a machine-readable report (JSON) so GRADE can fold vacuity signals into the report card.

## `bin/execution-harness.py`

- [ ] **Mutation-score parsing** — read the score from `mutmut` / `stryker` / `cosmic-ray` output and
      gate on a threshold, instead of exit-code-only.
- [ ] **Changed-unit scoping** — run gates over only the files in a diff (pair with `git`), so
      mutation cost is bounded to the review surface.
- [ ] Per-phase **timeout** + output capture to the report card; a `--json` report mode.
- [ ] A small **manifest registry** of starter manifests per ecosystem (python/pytest, node/vitest,
      go, rust) the skill can drop in.

## Method & corpus

- [ ] A **routing-eval corpus** (the maturity step the repo ROADMAP tracks) — especially the
      boundaries with `/code-review` (diff-time), `/verify` (app-time), `arch-system` (boundaries),
      and `/simplify` (quality), which are the likely mis-routes.
- [ ] A worked **end-to-end transcript** (a `parse_duration` SPECIFY → implement → DECOMPOSE → GRADE),
      with the spec card, the execution report, and a surviving-mutant fix checked in and dogfooded.
- [ ] An **adversarial-probe template** (the fresh-context skeptic prompt) as a reusable reference,
      shared in shape with `deep-research`'s verify step.
- [ ] A `family-*` deepening for the highest-risk families (async/concurrent determinism;
      I/O error-path contracts) if the single `unit-families.md` table proves too thin.

## Plugin

- [ ] As `code-skills` grows, candidate siblings from the same COMPOSE/REALIZE lineage: a
      `query-decomposer` (SQL: semantics × execution) and a `regex-decomposer` (language × match) —
      both with deterministic example-set gates.
