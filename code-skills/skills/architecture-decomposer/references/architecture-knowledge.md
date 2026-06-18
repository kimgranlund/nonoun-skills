# The STRUCTURE axis — is it the right decomposition?

The Structure axis (A1–A5) grades *intent*, top-down: from the system's context and boundaries down
to the contracts between its modules. This is the axis the dependency checker **cannot see** — a
cycle/layering tool is silent on "this module owns the wrong concept." It is also the axis LLMs fail
silently on (a confident, plausible, beautifully-drawn box diagram over the wrong boundaries), so it
carries an **adversarial structural probe**, not just a checklist.

This reference folds the type-driven, ownership-first architecture method (the substance graduated
from the `arch-system` skill) into the STRUCTURE axis.

## The core belief — types are the architecture

If you can't express a boundary as a clean type, the boundary is wrong. Types encode ownership, flow,
contracts, and constraints in a form that's both human-readable and machine-checkable. Interfaces
define boundaries. Generics encode flexibility. Union types encode valid states. If the types are
clean, the system is clean; if the types fight you, the boundaries are wrong. So every level of the
STRUCTURE axis has a *type test*: the hypothesis is confirmed when the types compose cleanly and
falsified when they need escape hatches (`any`, `as unknown`, untyped bags, `!important`).

## A1 · Context / boundaries `[gate]`

Carve the system at the right joints before anything else.

- **Vocabulary boundaries** — where do the same words mean different things? A "user" in auth vs. a
  "user" in billing are different concepts; each bounded context owns its own meaning.
- **Lifecycle boundaries** — what data has different creation / mutation / deletion timing?
- **Authority boundaries** — who (person, team, service) is the source of truth for what data?
- **Ownership is the fundamental question.** Before "how should this work," ask "who owns this?"
  State, data, lifecycle, mutation ownership. When ownership is clear, the architecture follows. Every
  concept has **exactly one** owning context — shared ownership means a missing context or a wrong
  boundary.
- **Gate:** a wrong top-level boundary makes every level below it a polish of the wrong shape.
  Re-carve, don't refine.

## A2 · Containers / modules `[gate]`

The major buildable / deployable units and their reason to exist.

- Name each unit (service, package, layer, module) and the *one* thing it owns.
- **Flows are directional.** State the direction of each dependency: one-way / request-response /
  event-driven. **Bidirectional flow between two modules is a code smell** — there's likely a missing
  third module, or the two are actually one. (This is also what shows up downstream as a B2 cycle.)
- **Gate:** a unit with no clear reason to exist, or two units that should be merged, poisons the
  responsibilities and interfaces below.

## A3 · Responsibilities `[review]`

Single-responsibility and cohesion per module.

- Does each module do one thing, with high internal cohesion (its parts change together)?
- A responsibility split across three containers, or two responsibilities crammed into one, is the
  finding. Make illegal states unrepresentable: a lifecycle is a discriminated union of states (a
  draft order can't have a tracking number), not a flat bag of optional fields with boolean flags.

## A4 · Interfaces / contracts `[review]`

The public surface each module exposes to the others — this is the crossing seam with INTEGRITY (the
edges of the dependency graph are the contracts in use). Contracts should be:

- **Narrow** — expose only what the consumer needs, not the full domain model. An interface with
  10+ methods or a token with 10+ consumers is a smell.
- **Result-typed** — make failure states explicit in the return value, not thrown-and-forgotten.
- **Immutable at the boundary** — data crossing a boundary is not mutated downstream.
- **Versioned** where consumers are external — the contract is the thing you can't break casually.

## A5 · Fitness `[review]`

The *-ilities under the real forces on the system (see `references/dependency-policy.md` for the
stress catalogue):

- **Scalability** — where's the first bottleneck under 10× load? Can the hot path scale independently?
- **Evolvability** — the most likely change: how many modules does it touch? A change localized to one
  module's internals is cheap; a cross-cutting one is expensive and signals a wrong boundary.
- **Operability / resilience** — component failure, partial failure, cascading failure: does the
  structure contain blast radius (circuit breakers, bulkheads, backpressure)?

## The seven domains (each is a STRUCTURE specialization)

The method is the same across domains; what changes is *where the boundary defect hides* and *what the
ownership question is*. Pick the lens that matches the system.

| Domain | The ownership question | The boundary expressed as |
|---|---|---|
| **System architecture** | which service is the source of truth? | service contracts + event schemas; failure isolation |
| **Data modeling** | who can write this field? | entities as discriminated lifecycle-state structures, not flat optional bags |
| **Frontend (CSS / tokens / web components)** | which domain owns this custom property / state? | `@layer` as the module system, tokens as typed primitives, attribute selectors as state discriminants, a custom element's attribute API as its contract |
| **Platform / OS** | what does the platform provide vs. what do extensions bring? | capability interfaces, resource handles (acquire/release), extension points (hooks/slots), typed workflow pipelines |
| **Server-side rendering** | who owns the render — server or client? | the hydration boundary as a contract (server emits HTML + serialized props; props must be serializable — a type constraint); streaming/suspense boundaries as independent render domains |
| **MCP (skills / plugins / servers)** | what does the host own vs. the server? | tool input/output as JSON Schema; resource URIs `{scheme}://{domain}/{path}` encoding ownership; a skill's `description` as the trigger contract, the SKILL.md body as the behavior contract |
| **A2UI (schema-driven generative UI)** | what does the agent decide vs. what does the component own? | a 6-stage pipeline (interpret→analyze→plan→generate→validate→render) where each stage's output type is the next stage's input type; the component schema as the agent↔renderer contract |

Friction signals that cut across all seven (these are the STRUCTURE-axis tells):

- Type escape hatches (`any`, `object`, untyped dicts, `!important`, `"use client"` on everything) —
  a boundary isn't designed, just escaped.
- Duplicate types / tokens / models across modules — ownership is contested (A1).
- Optional fields doing the work of a state machine — the lifecycle isn't modeled (A3).
- Bidirectional imports or callback hell at a boundary — the flow direction is wrong (A2; shows up as
  a B2 cycle).
- A contract with a huge surface (interface with 10+ methods) — A4 narrowness failure.

## The adversarial structural probe

After the gate walk, run a **fresh-context** skeptic against the boundaries — a verifier sharing the
author's context inherits its blind spots. Ask it to find, with one concrete example each:

- **Contested ownership (A1):** one concept that two modules both claim to own.
- **Split responsibility (A3):** one behavior that lives in three places, or one module doing two
  unrelated things.
- **Leaky interface (A4):** one contract that exposes a consumer to another module's internals.
- **Evolution friction (A5):** the most likely change — name how many modules it touches.

Any counterexample is a STRUCTURE finding the dependency checker is blind to — the bottom-left
quadrant ("compiles & deploys, but wrong boundaries").
