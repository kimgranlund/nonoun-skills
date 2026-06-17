# The two-axis method — SPEC × EXECUTION

A unit of code is **correct on two independent axes that walk the same hierarchy in opposite
directions** — the decomposer seam the layout-, mermaid-, and component-decomposers apply to space,
diagrams, and components, here applied to a function / module / change.

- **Spec · whole → part** grades the **intent**: the problem it addresses → its contract → the cases
  it covers → its approach → its fit with the codebase. *"Is it the right code?"*
- **Execution · part → whole** grades the **mechanism**: it parses/compiles → types & lints clean →
  tests pass and are real → it's robust → it's observable. *"Does it provably run, here?"*

They **cross at the contract** — the signature + behavior is *both* the claim (what the code should
do) and the mechanism (what the type-checker enforces and the tests pin). A contract that won't
execute is fiction; execution with no real contract is "green but wrong" waiting to happen.

That crossing is the whole technique. A unit can be:

- **correct idea, won't run** — right contract and approach, but a hallucinated API, a type error,
  or a red test. The classic LLM failure: plausible code that doesn't execute.
- **green but wrong** — compiles, types check, CI is green — but it solves the wrong problem, or the
  tests are *vacuous* and would pass against a broken implementation. The classic LLM trap: a green
  checkmark on the wrong thing.

Opposite defects, opposite fixes — so you **score and report the two axes separately, never
averaged.** An averaged score hides which one you have, and they need opposite work (toolchain vs
spec).

## The leveled walk

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Spec** | whole → part | **A1** Problem `[gate]` → **A2** Contract `[gate]` → **A3** Cases → **A4** Approach → **A5** Fit | "Is it the *right code*?" |
| **B · Execution** | part → whole | **B1** Compile `[gate, code]` → **B2** Types/Lint `[gate, code]` → **B3** Test `[gate, code]` → **B4** Robustness → **B5** Observability | "Does it *provably run*, here?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** — a failure cascades and BLOCKS the reviews below it on
that axis. `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable unit is **≥4 on every review with
zero gate failures**, reported as two separate axis scores plus the quadrant cell.

### A · Spec (whole → part)

- **A1 Problem `[gate]`** — does it address the *actual* requirement, not an adjacent one? Solving
  the wrong problem makes everything below moot.
- **A2 Contract `[gate]`** — signature, input/output types, pre/postconditions, error modes, the
  public surface. Wrong contract poisons every decision under it.
- **A3 Cases `[review]`** — covers the real input space: empty/null, boundaries, error paths,
  concurrency, the off-happy-path.
- **A4 Approach `[review]`** — appropriate algorithm/complexity/idiom; right altitude; reuse over
  reinvention; not over- or under-engineered.
- **A5 Fit `[review]`** — coheres with the codebase: surrounding patterns, naming, deps; doesn't
  duplicate; lives in the right module.

### B · Execution (part → whole)

- **B1 Compile `[gate, code]`** — syntactically valid, compiles/loads, **no reference to nonexistent
  symbols or APIs** (the #1 hallucination). Routed to `bin/execution-harness.py`.
- **B2 Types/Lint `[gate, code]`** — type-checks, lints clean, no static defects.
- **B3 Test `[gate, code]`** — the relevant tests pass **and are real**, and the unit executes on
  representative input. Real-ness is *not* free from a green run — see the doctrine below.
- **B4 Robustness `[review]`** — adversarial/edge input, determinism, idempotency where required,
  resource bounds.
- **B5 Observability `[review]`** — failures are diagnosable; the unit is testable/instrumented; side
  effects are contained.

## The opposite-defect quadrant

```
                 B · EXECUTION passes      B · EXECUTION fails
A · SPEC     ┌────────────────────────┬────────────────────────┐
  passes     │      SHIPPABLE         │  correct idea, won't    │
             │                        │  run — right contract & │
             │                        │  approach, but a        │
             │                        │  hallucinated API /     │
             │                        │  type error / red test  │
             ├────────────────────────┼────────────────────────┤
A · SPEC     │ green but wrong —      │       REBUILD           │
  fails      │ compiles, types check, │                         │
             │ CI green, but solves   │                         │
             │ the wrong problem or   │                         │
             │ the tests are vacuous  │                         │
             └────────────────────────┴────────────────────────┘
```

The quadrant **names the fix**: top-right needs toolchain work; bottom-left needs *spec* work the
toolchain **cannot see**.

## The doctrine — gate where you can, adversarially verify where you can't

This is why the skill earns its place (and why it's outsized for an LLM author):

- The EXECUTION gates (B1/B2/B3) are the **cheap** axis — run the real toolchain via
  `bin/execution-harness.py`. They catch *correct-idea-won't-run* deterministically. **Trust the
  tool, not the read-through** — an LLM cannot reliably tell by reading whether code compiles or a
  test passes.
- But the **dangerous** axis ("green but wrong") is partly on the SPEC side *and* hidden inside B3
  ("are the tests real?"), and it is **not deterministically gateable**. Route it two ways:
  - **Mutation testing** as the mechanized proxy for B3 real-ness: if a deliberately broken
    implementation still passes, the suite is vacuous. `bin/test-vacuity-check.py` is the cheap
    static pre-filter (no-assert / tautology / mock-only); a real mutation run is the proof.
  - **An adversarial SPEC probe** for A1/A3: a *fresh-context* skeptic asked to find one input where
    the code violates the stated requirement. A verifier sharing the author's context inherits its
    blind spots — separate the context (the `deep-research` adversarial-verify move).

## Modes

- **SPECIFY** (before writing) — walk Spec-down (problem → contract → cases → approach), declare the
  execution plan (which types/tests will pin it), emit a **spec card**.
- **DECOMPOSE** (existing code) — recover the contract (A1/A2), run the execution ladder (B1–B3 via
  the harness + vacuity check), score the reviews; emit the spec card + a gap list (e.g. *"green, but
  this mutation survives — the test is vacuous"*).
- **GRADE** — score both axes, gates first (run the harness + vacuity check + a mutation/adversarial
  pass), place in the quadrant, name one corrective per failure.

## Walk order (do not skip)

1. **A1 Problem / A2 Contract** — name the requirement and the contract. Wrong ⇒ stop, re-spec.
2. **B1/B2/B3 Execution** — run `execution-harness.py`. Red gate ⇒ fix before reviewing (you can't
   grade approach for code that won't compile).
3. **B3 real-ness** — run `test-vacuity-check.py`, then a mutation pass. Surviving mutants /
   vacuity signals ⇒ the suite doesn't pin the contract; fix the tests, not the score.
4. **A1/A3 adversarial probe** — in a fresh context, try to find an input that violates the spec.
5. **Reviews** — A3–A5 then B4–B5, 1–5 each. Below 4 ⇒ name the single corrective.
6. **Report** — two axis scores, the quadrant cell, gate failures first; hand the verified contract
   + execution report to `/code-review` and `/verify`.
