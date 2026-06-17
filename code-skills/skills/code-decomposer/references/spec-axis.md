# The SPEC axis — is it the right code?

The Spec axis (A1–A5) grades *intent*, top-down: from the problem the code must solve to the detail
of how it fits the codebase. This is the axis the toolchain **cannot see** — a compiler is silent on
"this solves the wrong problem." It is also the axis LLMs fail silently on (confident, plausible,
wrong), so it carries an **adversarial probe**, not just a checklist.

## A1 · Problem `[gate]`

Name the requirement in one sentence, in the user's terms, before reading the implementation. Then
ask: does this code address *that*, or an adjacent thing it's easy to drift to?

- Distinguish the **asked** problem from the **assumed** one (an LLM often answers a more familiar
  neighbour of the real request).
- Surface the implicit acceptance criteria: what observable behavior would prove it's solved?
- **Gate:** if the unit solves the wrong problem, stop — every level below is polishing the wrong
  thing. Re-spec, don't refine.

## A2 · Contract `[gate]`

The contract is the crossing seam with EXECUTION — what the type-checker enforces and the tests pin.
Make it explicit even when the language won't:

- **Signature** — inputs, outputs, and their types; what's required vs optional; nullability.
- **Preconditions** — what must hold on entry (and whose job it is to guarantee it — caller or
  callee).
- **Postconditions** — what's true on return; invariants preserved.
- **Error modes** — what it does on bad input: throw / return error / sentinel; which errors are
  part of the contract vs bugs.
- **Effects** — what it reads/writes/mutates beyond its return value (the contract includes side
  effects).
- **Gate:** a wrong or missing contract poisons cases, tests, and review. Lock it first; it's the
  artifact you hand to a code author and to `/code-review`.

## A3 · Cases `[review]`

Enumerate the real input space — LLMs over-index on the happy path:

- Empty / null / zero / missing; single-element; very large; duplicate.
- Boundary values (off-by-one, inclusive/exclusive edges, overflow).
- Error paths and partial failure (the call that raises halfway through).
- Concurrency / ordering / re-entrancy where relevant.
- The **forbidden** inputs the contract rules out — are they actually rejected?

Score by coverage of the space, not count of cases. A test per case is the EXECUTION-side evidence.

## A4 · Approach `[review]`

Is the implementation strategy appropriate — not the cleverest, the *right-altitude*?

- **Complexity** fits the data scale (no accidental quadratic; no premature optimization).
- **Idiom** matches the language and codebase (uses the platform, doesn't reinvent it).
- **Reuse** over reinvention — does an existing helper/abstraction already do this?
- **Altitude** — not over-engineered (a framework for a one-off) nor under-engineered (a one-off
  where a small abstraction removes real duplication).

## A5 · Fit `[review]`

Coherence with the surrounding code — the difference between *works* and *belongs*:

- Matches local patterns, naming, error-handling style, and module boundaries.
- Doesn't duplicate an existing capability or add a redundant dependency.
- Lands in the right file/layer; its public surface is no larger than it needs to be.

## The adversarial SPEC probe (route A1/A3 to a skeptic, not the author)

The dangerous defect — *green but wrong* — lives here, and it is not deterministically gateable. So
verify it the way `deep-research` verifies claims: **in a fresh context, adversarially.**

- Prompt a separate reviewer (a fresh agent, not the one that wrote or read the code with approval):
  *"Here is the stated requirement and the code. Find one input or scenario where the code does NOT
  satisfy the requirement. Default to 'a counterexample exists' and search for it."*
- A verifier that shares the author's context inherits its blind spots and rubber-stamps. Separation
  is the point.
- Feed any counterexample back as a missing **A3 case** and a new test (which a mutation run should
  then show the suite previously missed).

The output of this axis is the **spec card** — the recovered/declared contract + the case list — the
artifact GRADE re-derives and DESIGN emits, and the thing you hand to a code author and to
`/code-review`.
