# The STRUCTURE axis — is it the right decomposition?

The Structure axis (A1–A5) grades *intent*, top-down: from the system's context and boundaries down
to the contracts between its modules. This is the axis the dependency checker **cannot see** — a
cycle/layering tool is silent on "this module owns the wrong concept." It is also the axis LLMs fail
silently on (a confident, plausible, beautifully-drawn box diagram over the wrong boundaries), so it
carries an **adversarial structural probe**, not just a checklist.

This reference folds the type-driven, ownership-first architecture method (the substance graduated
from the `arch-system` skill) into the STRUCTURE axis.

## Reason on two planes in parallel — OUTSIDE-IN × INSIDE-OUT

Architecture is planned and reviewed from **two perspectives held at once** (the repo-wide convention,
see `HOWTO.md`). Fill the whole table before you grade — a green INSIDE-OUT structure that serves the
wrong OUTSIDE-IN goals is the classic "elegant solution to the wrong problem":

- **OUTSIDE-IN — the goals.** *What is this system for, and how do we know it's good?* The drivers and
  the **architecture characteristics** (the *-ilities*: scalability, evolvability, operability,
  security, cost…), the principles, the KPIs/SLOs, the rubric. **Everything is a trade-off** — there is
  no "right" architecture, only one whose trade-offs fit the *ranked* characteristics. Naming and
  ranking those characteristics is the **first architectural act**; it lives in **A1 (context)** and is
  graded in **A5 (fitness)**.
- **INSIDE-OUT — the foundations.** *What structure honors the physics and the constraints?* The
  technical canon below (DDD, hexagonal, CLEAN, SOLID, connascence…). It runs through **A1–A4** and is
  what the **INTEGRITY axis** mechanically verifies.

|  | **intent** (judgment) | **mechanism** (the `bin/`) |
|---|---|---|
| **OUTSIDE-IN** (goals) | the ranked *-ilities*, principles, the rubric (A1/A5) | SLO / load / acceptance checks (out of band) |
| **INSIDE-OUT** (foundations) | boundaries, ownership, contracts (A1–A4) | acyclic · layered · coupling-bounded → `dependency-check.py` |

## The named canon — the conventions distinguished engineers cite

These are the well-known guides the INSIDE-OUT plane draws on. Each maps onto a level of the method —
the skill doesn't invent a new vocabulary, it *operationalizes* the standard one.

- **Coupling & cohesion** — the master variables. **High cohesion** (a module's parts change together)
  localizes change; **low coupling** stops change rippling. Nearly every rule below reduces to these.
  *(A3 cohesion; B coupling.)*
- **Connascence** (Page-Jones) — the sharpened coupling metric: the *stronger* the connascence between
  two elements (static: name → type → meaning → position → algorithm; dynamic: execution → timing →
  value → identity), the *closer* they must live. Refactor by **converting strong forms to weak** and
  **minimizing any connascence that crosses a boundary**. This is what `dependency-check.py`'s coupling
  count approximates. *(A4/B.)*
- **Separation of Concerns + Information Hiding** (Parnas, 1972) — split the system so each part owns
  one concern, and **hide each decision likely to change** behind a stable interface. SRP and ISP are
  direct corollaries. *(A1/A3/A4.)*
- **SOLID** — **S**RP (one reason to change → A3), **O**CP, **L**SP, **I**SP (narrow contracts → A4),
  **D**IP (depend on abstractions, not details → the dependency *direction*). DRY rides alongside.
- **Dependency Inversion & the dependency rule** — high-level policy depends on abstractions; source
  dependencies point **toward stability** (inward). The engine of every domain-centric architecture.
  *(A2 flow direction; B3 layering.)*
- **Domain-Driven Design** (Evans) — **bounded contexts**: a model is consistent only inside an explicit
  boundary, with a **ubiquitous language** and one owner. This *is* A1's "vocabulary boundaries / one
  owning context." *(A1.)*
- **Hexagonal / Ports & Adapters** (Cockburn) and **CLEAN / Onion** (Martin) — the **domain at the
  center**, infrastructure outside; the domain imports nothing outward; **ports** (interfaces) +
  **adapters** (implementations) are the seams. This is A4 (contracts) constrained by the dependency
  rule. *(A4 + B3.)*
- **Conway's Law & the inverse Conway maneuver** — a system mirrors the communication structure of the
  org that builds it; align module boundaries to **team boundaries**, or reshape the org to get the
  architecture you want. Architecture is socio-technical, not purely technical. *(A1/A2.)*
- **Evolutionary architecture & fitness functions** (Ford/Parsons/Kua) — architecture changes, so guard
  its characteristics with **fitness functions**: automated checks, wired into CI, that **block** any
  change violating an architectural rule — turning architecture into an *executable specification*.
  **`bin/dependency-check.py` is a fitness function** (acyclicity / layering / coupling); the INTEGRITY
  axis is the fitness-function layer. *(B = fitness functions.)*
- **Decision capture & leveled views** — **ADRs** (context → options → decision → consequences, append-
  only) record *why*; the **C4 model** (Context → Container → Component → Code) gives the spec a legible
  view at every altitude (it maps onto A1 → A2 → A3/A4). *(see `references/dependency-policy.md`.)*

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
