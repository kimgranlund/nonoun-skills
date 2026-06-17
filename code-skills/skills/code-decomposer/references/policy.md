# Policy — definition-of-done, the cards, and the handoff

The reusable artifacts and boundaries: what "done" means, the shape of the two cards the skill emits,
the harness manifest, and how this hands off to the rest of the code-tooling fleet without
overlapping it.

## Definition-of-done (a unit is shippable when…)

Gated items route to `bin/`; review items are 1–5 judgments. SHIPPABLE = the quadrant top-left.

1. **Right problem (A1)** — addresses the actual requirement, stated in one sentence.
2. **Sound contract (A2)** — signature, pre/postconditions, error modes, and effects are explicit.
3. **Cases covered (A3)** — boundaries, empty/null, error paths, and any concurrency are enumerated
   and tested (≥4).
4. **Appropriate approach (A4)** — right complexity/idiom/altitude; reuses rather than reinvents (≥4).
5. **Fits the codebase (A5)** — matches local patterns, no duplication, right module, minimal public
   surface (≥4).
6. **Compiles & types (B1/B2)** — `execution-harness.py` compile + typecheck gates ran green; no
   nonexistent APIs; no un-checked `any`/`ignore` on the contract surface.
7. **Green ∧ real tests (B3)** — the test gate ran green **and** `test-vacuity-check.py` is clean
   **and** a mutation run leaves no surviving mutant on contract behavior.
8. **Robust (B4)** — holds on edge/adversarial input; deterministic; bounded resources (≥4).
9. **Observable (B5)** — failures are diagnosable; effects contained; the unit is testable (≥4).
10. **Both axes ≥4, zero gate fails, SHIPPABLE quadrant** — reported as two scores, gate failures
    first, with the verified contract + execution report ready for handoff.

## The two cards

**Spec card** (`*.spec.json`) — emitted by DESIGN, re-derived by DECOMPOSE:
```json
{
  "unit": "parse_duration",
  "family": ["pure-function", "data-transform"],
  "problem": "convert a human duration string to seconds",
  "contract": {
    "inputs":  [{"name": "text", "type": "str"}],
    "output":  {"type": "int", "unit": "seconds"},
    "pre":     ["text is non-empty"],
    "post":    ["result >= 0"],
    "errors":  ["ValueError on unparseable input"],
    "effects": []
  },
  "cases": ["\"90s\" -> 90", "\"1h30m\" -> 5400", "\"\" -> ValueError",
            "\"-5s\" -> ValueError", "huge value -> no overflow"]
}
```

**Execution report card** — emitted by the harness + vacuity check + mutation:
```
phase       gate    ran   verdict
compile     gate    yes   pass
typecheck   gate    yes   pass
test        gate    yes   pass
mutation    advise  yes   2 mutants survived  <- B3 not really passing
vacuity:    NO_ASSERT x0 · TAUTOLOGY x0 · MOCK_ONLY x1
```

## The harness adapter manifest

The per-project command map `execution-harness.py` reads (`template` prints a starter). `gate`
defaults: compile/typecheck/test gate; lint/mutation advisory. Commit one manifest per project root;
keep it in sync with CI so the skill runs the *same* gates CI does.

## Handoff — what this skill does NOT do

The code-tooling fleet has clear seams; `code-decomposer` is the **implementation-time design + grade**
stage and feeds the others:

- **→ a code author** (e.g. `ui-build-components` for components, or plain implementation): receives
  the locked spec card and writes the unit. This skill grades, it does not emit the implementation.
- **→ `/code-review`**: receives the verified contract + execution report and audits the *finished
  diff* for bugs. `code-decomposer` is design-time and unit-scoped; `/code-review` is diff-time and
  change-scoped. Don't re-run its bug hunt.
- **→ `/verify`**: runs the whole app to confirm end-to-end behavior. `code-decomposer` proves the
  *unit* executes and its tests are real; `/verify` proves the *system* behaves. Different altitude.
- **← `arch-system` / `arch-pattern`**: hand *in* the contract/boundary. This skill grades a unit
  against its contract; it does not design system boundaries.
- **not `/simplify`**: that's reuse/efficiency cleanup (quality). This skill is correctness
  (right + runs). A unit can be SHIPPABLE here and still have cleanups for `/simplify`.

## Governance

- **Spec cards are checked in** next to the unit (or the test) as the contract of record; they
  version with the code and are the diff a reviewer reads first.
- **The manifest tracks CI** — if CI adds a gate (a new linter, mutation), add it to the manifest so
  the skill's verdict and CI's verdict can't diverge.
- **Mutation budget** — run mutation on changed units in review, not the whole tree every commit;
  the vacuity linter is the cheap everywhere-gate, mutation the targeted proof.
