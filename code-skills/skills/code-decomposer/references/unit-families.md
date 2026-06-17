# Unit families — pick by what the code does

Code units aren't uniform: a pure function and an async I/O boundary fail in different ways and need
different evidence. This is the "archetype library" — match the family, then the two axes get a
**spec-risk profile** (where SPEC defects hide) and an **execution emphasis** (which gate is decisive
and what a real test looks like). One unit can be more than one family; take the union of the
emphases.

| Family | Spec-risk (where A-defects hide) | Execution emphasis (the decisive gate + real-test shape) |
|---|---|---|
| **Pure function** | missed cases (A3): boundaries, empty, overflow; wrong contract on edge inputs | B3 via **property tests** + table-driven cases; mutation should kill easily — surviving mutants mean missed cases |
| **Stateful / effectful** | hidden preconditions, order-dependence, the contract's *effects* left implicit (A2) | B5 observability + B4 determinism; test the **state transition** and the effect, not just the return; pin invariants across calls |
| **Async / concurrent** | races, re-entrancy, cancellation, partial completion (A3/A4) | B4 robustness is decisive: determinism under interleaving, timeout/cancel paths; beware tests that pass only because timing happened to line up |
| **I/O boundary** (network/fs/db) | error modes & partial failure (A2) — the unhappy path *is* the contract | B3 with the **error paths** tested (timeout, 500, malformed response), not just success; mock the external edge, assert across the real seam; over-mocking is the trap |
| **Data transform / parser** | the input space (A3): malformed, adversarial, encoding, huge; round-trip invariants | B1 (does it even handle the grammar) + B3 property tests (parse∘print == id where it should); fuzz for B4 |
| **API endpoint / handler** | contract = request/response schema + status codes + auth (A2); wrong-problem risk is high | B3 contract tests against the schema, auth/error responses; B5 observability of failures; adversarial probe on the auth/validation cases |
| **Glue / orchestration** | A4 approach (right altitude) + A5 fit; often *should not exist* (duplicates a pattern) | B3 that the steps compose and the failure of any step is handled; MOCK_ONLY is the dominant vacuity here — assert the orchestrated *result*, not that each step was called |

## How a family shifts the walk

- **Where the gate bites.** A pure function lives or dies on B3 case coverage; an async unit on B4
  determinism; an I/O boundary on B3 error-path tests. Spend the verification budget there.
- **Where the SPEC probe aims.** For an endpoint, the adversarial probe hunts the auth/validation
  bypass; for a parser, the malformed/adversarial input; for orchestration, the "wrong problem /
  shouldn't exist" question.
- **Which vacuity dominates.** Orchestration and I/O units attract **MOCK_ONLY** tests (everything
  mocked, nothing asserted); pure/transform units attract **happy-path monoculture** (missed A3
  cases that mutation exposes). Point `test-vacuity-check.py` and the mutation run accordingly.

## The cross-family rule

Whatever the family, the contract (A2) is the crossing seam and the tests pin *it*. The family only
tells you **where the defect is most likely to hide** and **which gate is the cheapest place to catch
it** — it doesn't change the method, it focuses it.
