# Worked example — "green but wrong" on SPEC × EXECUTION

A complete DECOMPOSE → fix → GRADE for a unit whose tests are **green but vacuous** — the signature
failure `code-decomposer` exists to catch. The two test files here are checked in and the
test-vacuity linter actually flags / clears them.

## The artifact

A `total(items)` function with a passing test suite. CI is green. Ship it?

## DECOMPOSE

**A · Spec** (whole → part)
- **A1 Problem** `[gate]` — "sum the prices of cart items; reject a negative price." ✓
- **A2 Contract** `[gate]` — `total(list[{price}]) -> int`, `ValueError` on a negative price, `0` for
  empty. ✓
- A3 Cases — empty, negative, multi-item. (the case set the tests must pin)

**B · Execution** (part → whole)
- B1 Compile / B2 Types `[gate]` — assume green.
- **B3 Test** `[gate, code]` — green is necessary, **not sufficient**. The gate is *green ∧ real*.
  Run the vacuity pre-filter on the suite (`examples/test_cart_red.py`):

```
$ python3 bin/test-vacuity-check.py examples/test_cart_red.py
  examples/test_cart_red.py:8   TAUTOLOGY  assertEqual(x, x)
  examples/test_cart_red.py:10  NO_ASSERT  test_runs asserts nothing
test-vacuity-check: 2 vacuity signal(s) across 1 file(s) — verify with a mutation run
```

**B3 fails.** `assertEqual(1, 1)` passes against *any* implementation of `total()`; `test_runs`
calls `total(...)` but asserts nothing, so it only fails by throwing. The suite is green and pins
**nothing** — a broken `total` (returns the count, ignores negatives) would stay green. This is the
*green but wrong* quadrant, proven mechanically.

## Fix

Rewrite the tests to pin the contract (`examples/test_cart_green.py`): an independently-known sum,
the empty case, and the negative-price error path.

```
$ python3 bin/test-vacuity-check.py examples/test_cart_green.py
test-vacuity-check: OK — no vacuity signals in 1 file(s)
```

Each test now references the unit, asserts a result the contract promises, and exercises a named A3
case. (The next rung is a mutation run — break `total` on purpose and confirm a test goes red.)

## GRADE — two scores, never averaged

- **Spec: 5/5** — right problem, sound contract, cases enumerated.
- **Execution: B3 gate-fail → (after fix) 5/5** — compile/types green, tests now green ∧ real.

**Quadrant:** the red suite sat in **"green but wrong"** (Execution's B3 looked green but was
vacuous) — *the CI checkmark on the wrong thing*. The fix is the tests pinning the contract, not the
code. After it: **SHIPPABLE**.

The lesson: "do the tests pass?" is the wrong question; "would they *fail* against a broken
implementation?" is the right one — and that's mechanizable.
