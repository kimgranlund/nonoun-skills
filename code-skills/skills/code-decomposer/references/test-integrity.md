# Test integrity — why a green suite is evidence of nothing

This is the centerpiece. The whole skill exists because an LLM (and a hurrying human) produces the
**green but wrong** quadrant — code that compiles, types check, and passes a suite that *cannot
fail for the right reason*. EXECUTION's B3 gate is "tests pass **and are real**." This file is the
real-ness half, and `bin/test-vacuity-check.py` is its mechanized pre-filter.

## The one principle

> **A test pins the contract, not the implementation.** Its job is to *fail* when the behavior the
> contract promises is broken. A test that can't fail — or fails only when the code's incidental
> shape changes — is not a test, it's a comment that takes CPU.

Two corollaries:
- **Green is necessary, not sufficient.** The question is never "does it pass?" but "would it
  *fail* against a broken implementation?"
- **The proof is mutation, not inspection.** Break the implementation on purpose; a real suite
  notices. A surviving mutant is untested behavior.

## The vacuity taxonomy (what `test-vacuity-check.py` flags)

Static, cheap, deterministic — the pre-filter before a (costlier) mutation run:

| Kind | Smell | Why it's vacuous |
|---|---|---|
| **NO_ASSERT** | a test with no assertion | can only fail by throwing — it asserts nothing about behavior |
| **TAUTOLOGY** | `assert True` · `assertEqual(x, x)` · `expect(2).toBe(2)` | always passes; the comparison can't be false |
| **MOCK_ONLY** | asserts only `mock.assert_called()` / `toHaveBeenCalled()` | tests that a call happened, never that the *result* is right (mock-the-subject) |
| **FOCUSED** | `it.only(` / `fdescribe` | silently disables every sibling test in the file — the suite you think ran, didn't |
| **SKIPPED** | `@skip` / `xit` / `.skip` | counted toward "passing" while running nothing |

Run it: `python3 bin/test-vacuity-check.py <file|dir> [--unit NAME]`. With `--unit`, it also flags a
test that asserts something but **never references the unit it claims to cover** (a test bound to the
wrong subject). Findings are *signals*, not proof — they point a mutation run at the weak spots.

## The deeper smells (judgment, beyond the linter)

The linter catches the mechanical cases; these need a read:

- **Test mirrors the implementation.** The test re-computes the expected value with the same logic
  the code uses (`assert f(x) == x * 2 + 1` where `f` literally returns `x * 2 + 1`). It passes by
  construction and breaks only when the code changes — it pins the *implementation*, not the
  *contract*. Pin to an independently-known expected value.
- **Over-mocking.** So much is mocked that the test exercises the mocks, not the unit. If every
  collaborator is a mock, the test asserts your understanding of the collaborators, which may be
  wrong — and the real integration is untested.
- **Snapshot rot.** A snapshot test that's re-recorded whenever it fails asserts only "the output
  equals the last output," which is a tautology across time.
- **Assertion-free `expect`.** `expect(result)` with no matcher (`.toBe(...)`) — common in TS where
  it type-checks but asserts nothing at runtime.
- **Happy-path monoculture.** Every test feeds valid input; the error modes in the contract (A2) and
  the edge cases (A3) are untested. Coverage % looks high; the *space* coverage is low.

## Mutation testing — the proof

`test-vacuity-check.py` is the cheap filter; a mutation run is the verdict for B3:

- A mutation tool (`mutmut`, `cosmic-ray`, `stryker` for JS/TS) makes small semantic edits to the
  code (flip a comparison, drop a statement, change a constant) and re-runs the suite.
- A **killed** mutant = some test failed = that behavior is pinned. A **surviving** mutant = no test
  noticed = untested behavior, regardless of line coverage.
- Wire it as the `mutation` phase in the execution harness manifest (advisory by cost, decisive in
  judgment). The mutation *score* (killed / total) is the real B3 signal; line coverage is not.

## What a real test looks like

- Pins an **independently-known** expected value (not re-derived from the code).
- Exercises a **named case** from A3 (a boundary, an error mode, an empty input) — its name says
  which.
- Asserts the **result/effect** the contract promises, not that a mock was poked.
- **Fails** when you break the corresponding line of the implementation (verify once with a manual
  mutation if you don't run a mutation tool).
- Mocks only what it must (the slow / non-deterministic / external collaborators), and asserts across
  the real seam where it can.

## How this scores

B3 is **green ∧ real**:
- green = the execution harness's `test` gate ran and passed;
- real = no NO_ASSERT/TAUTOLOGY/MOCK_ONLY/FOCUSED signals on the tests that cover this unit, **and**
  the mutation score over this unit is adequate (no surviving mutants on contract behavior).

A unit that is green with vacuous tests is **not** B3-passing — it's the *green but wrong* quadrant,
and the corrective is on the tests (pin the contract), not the score.
