---
name: code-decomposer
description: >
  Decompose, design, and grade a unit of code (function, module, change) on two crossing axes —
  SPEC (problem → contract → cases → approach → fit) and EXECUTION (compile → types/lint → test →
  robustness → observability) — scored separately so a plausible implementation can't hide a broken
  one, nor a green test suite the wrong behavior. EXECUTION routes to the real toolchain via a
  harness (bin/execution-harness.py); the "green but wrong" failure routes to a
  test-vacuity linter (bin/test-vacuity-check.py: no-assert, tautology, mock-only) plus mutation and
  an adversarial spec probe. Backed by a gated rubric, a spec-card + execution-
  report protocol, and unit-family playbooks. Use when deciding whether an implementation is right,
  grading a unit's contract, or hardening a test suite. NOT for diff-time bug hunting (/code-review),
  running the app (/verify), architecture
  blueprints (arch-system), quality cleanups (/simplify), or grading a proof / deductive argument on
  its logic and rigor (→ proof-decomposer).
---

# code-decomposer — grade a unit of code on two crossing axes

A unit of code is **correct on two independent axes that walk the same hierarchy in opposite
directions** — the decomposer seam the layout-, mermaid-, and component-decomposers apply to space,
diagrams, and components, here applied to a function / module / change:

- **Spec · whole → part** grades the **intent**: the problem → its contract → the cases it covers →
  its approach → its fit with the codebase. *"Is it the right code?"*
- **Execution · part → whole** grades the **mechanism**: it compiles → types & lints clean → tests
  pass and are *real* → it's robust → it's observable. *"Does it provably run, here?"*

They **cross at the contract** — the signature + behavior is *both* the claim (what the code should
do) and the mechanism (what the type-checker enforces and the tests pin). That crossing is the whole
technique: a unit can be **correct idea, won't run** (right contract and approach, but a hallucinated
API or a red test) or **green but wrong** (compiles, types check, CI is green, but it solves the
wrong problem or the tests are vacuous). Opposite defects, opposite fixes — so you **score and report
the two axes separately**, never averaged.

The reason this is outsized for an LLM author: EXECUTION is exactly where models hallucinate with the
most confidence *and* it is mechanizable — so the gate converts the worst failure into a caught
error. And the **green but wrong** quadrant — the one every other code tool misses — gets a dedicated
attack: a test-vacuity linter + mutation for "are the tests real?", and a fresh-context adversarial
probe for "is it the right problem?".

## Quick Start

**You bring:** a unit (a spec, a screenshot of a diff, existing code) and the question — "design
this", "is this right?", "are these tests real?", "is it production-ready?". **You get:** a spec card
(the contract + cases), an execution report card, and a two-axis grade with the defect quadrant named.

> *"Is this `parse_duration` implementation done?"* →
> 1. **Spec — problem → contract:** the requirement is "duration string → seconds" `[gate]`; the
>    contract is `(text:str) -> int`, `ValueError` on unparseable, `result ≥ 0` `[gate]`. Cases:
>    `""`, `-5s`, `1h30m`, overflow.
> 2. **Execution — run it, don't read it:** `bin/execution-harness.py` runs compile + typecheck +
>    test `[gate]`. Green? Now prove the tests are *real*: `bin/test-vacuity-check.py` (no
>    tautology/mock-only/no-assert) + a mutation pass `[gate]`.
> 3. **Adversarial spec probe:** in a fresh context, hunt one input that violates the contract
>    (`"90"` with no unit? negative? unicode digits?) — any counterexample is a missing case + test.
> 4. **Review + report:** approach/fit (A4/A5), robustness/observability (B4/B5), then the two axis
>    scores + the quadrant cell — gate failures first — handed to `/code-review` and `/verify`.

**Modes:** **SPECIFY** (Spec-down → declare the execution plan → emit a spec card) · **DECOMPOSE**
(read code → recover the contract → run the execution ladder → grade) · **GRADE** (score both axes,
gates before reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Spec** | whole → part | **A1** Problem → **A2** Contract → **A3** Cases → **A4** Approach → **A5** Fit | "Is it the *right code*?" |
| **B · Execution** | part → whole | **B1** Compile → **B2** Types/Lint → **B3** Test → **B4** Robustness → **B5** Observability | "Does it *provably run*, here?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on
that axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable unit is **≥4 on every review with
zero gate failures**, reported as two separate axis scores plus the defect quadrant.

## The doctrine — gate where you can, adversarially verify where you can't

The non-obvious core, and the reason it earns a skill:

- **EXECUTION is the cheap, deterministic axis** — route B1/B2/B3 to the real toolchain via
  `bin/execution-harness.py` and **trust the tool, not the read-through**. It catches *correct idea,
  won't run* outright.
- **"Green but wrong" is NOT deterministically gateable** — it lives on the SPEC side and hidden
  inside B3 ("are the tests real?"). Route it two ways: **mutation testing** + `test-vacuity-check.py`
  for test real-ness, and a **fresh-context adversarial probe** for "right problem?". A verifier that
  shares the author's context rubber-stamps it — separate the context (the `deep-research` move).

## The unit families (pick by what the code does)

Each family tells you **where the SPEC defect hides** and **which gate is the cheapest place to catch
it** — it focuses the method, doesn't change it. Full table in `references/unit-families.md`.

| Family | Decisive gate / real-test shape |
|---|---|
| pure function · data transform / parser | B3 property + table cases; mutation kills easily |
| stateful / effectful | B5 observability + B4 determinism; test the state transition |
| async / concurrent | B4 robustness: races, cancel, interleaving |
| I/O boundary · API endpoint | B3 **error paths** (timeout/500/malformed), not just success |
| glue / orchestration | MOCK_ONLY is the trap — assert the orchestrated result |

## §SelfAudit

- **Execution is the gate the LLM fails silently.** Run the toolchain (`execution-harness.py`); do
  not certify "it compiles / the test passes" from reading. An unrun gate is *no evidence*, not a
  pass.
- **A green suite is evidence of nothing until it's been mutated.** B3 is *green ∧ real*. Run
  `test-vacuity-check.py` then a mutation pass; a surviving mutant on contract behavior is untested
  behavior, regardless of line coverage.
- **The dangerous defect is invisible to the tools — probe the spec adversarially in a fresh
  context.** "Green but wrong" needs a skeptic hunting a counterexample, not the author's confidence.
- **Gates before reviews, always.** Don't grade approach for code that won't compile, or robustness
  for a unit whose contract is wrong. Stop each axis at its first failed gate.
- **Two scores, never one.** *Correct-idea-won't-run* and *green-but-wrong* need opposite fixes
  (toolchain vs spec). Report both axes and name the quadrant cell; never average.
- **Contract, not implementation.** This skill locks the contract + grade and emits the cards — it
  does not write the unit, hunt a diff for bugs (`/code-review`), run the app (`/verify`), or clean
  up quality (`/simplify`). Hand off; don't overlap.

## Verify Target

A unit is **done** when: it addresses the right problem with a sound, explicit contract (A1/A2);
cases/approach/fit ≥4; the harness compile + typecheck + test gates ran **green**; the tests are
**real** (vacuity-clean + no surviving mutant on contract behavior); robustness + observability ≥4;
and both axes score ≥4 with zero gate failures, landing in the **SHIPPABLE** quadrant — with the spec
card + execution report ready for `/code-review` and `/verify`. **NOT done** when: it compiles and CI
is green but solves the wrong problem or the tests are vacuous (*green but wrong*); or the contract
and approach are right but it won't run (*correct idea, won't run*); or a gate was skipped (tool
absent) and reported as a pass; or one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Spec × Execution), the leveled walk with gates, the quadrant, the gate-vs-adversarial-verify doctrine, and the SPECIFY / DECOMPOSE / GRADE workflows |
| `references/spec-axis.md` | **the Spec axis** — problem framing, contract design (signature, pre/post, errors, effects), case enumeration, approach/altitude, codebase fit, and the **adversarial spec probe** |
| `references/execution-axis.md` | **the Execution axis** — the toolchain ladder, the **live-gate protocol** (the harness manifest), and how to read each tool's signal; mechanized by `bin/execution-harness.py` |
| `references/test-integrity.md` | **any "are these tests real?" question** — the centerpiece: the vacuity taxonomy, the deeper smells (test-mirrors-impl, over-mocking, snapshot rot), mutation as proof, and *tests pin the contract, not the implementation*; mechanized by `bin/test-vacuity-check.py` |
| `references/unit-families.md` | **classifying a unit** — pure · stateful · async · I/O · parser · endpoint · glue, each with its spec-risk profile and execution emphasis |
| `references/policy.md` | **definition-of-done / handoff** — the 10-point DoD, the spec-card + execution-report shapes, the harness adapter manifest, and the seams to `/code-review`, `/verify`, `arch-system`, `/simplify` |
| `bin/execution-harness.py` | **mechanizes B1–B3** — reads a per-project command manifest, runs each present gate, normalizes verdicts to a report card (a missing tool is a SKIP, not a pass). `template` · `<manifest.json>` · `selftest` |
| `bin/test-vacuity-check.py` | **mechanizes B3 real-ness** — flags vacuous tests (no-assert · tautology · mock-only · focused · skipped) in Python (ast) + JS/TS; `<file\|dir> [--unit NAME]` · `selftest` |
