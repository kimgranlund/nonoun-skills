---
name: architecture-decomposer
description: >
  Decompose, design, and grade a software architecture (system, service, or module graph) on two
  crossing axes — STRUCTURE (context/boundaries → modules → responsibilities → interfaces → fitness)
  and INTEGRITY (graph well-formed → acyclic → layered → coupling bounded → deployable) — scored
  separately so an elegant-on-paper design can't hide a cyclic/tangled graph, nor a clean DAG hide
  wrong boundaries. INTEGRITY routes to a self-tested dependency checker (bin/dependency-check.py:
  cycles via Tarjan, layer violations, coupling, orphans); the wrong-boundaries failure routes to a
  fresh-context structural probe. Use when designing system boundaries, modeling a domain, deciding
  what owns what, or grading whether a structure holds. Triggers on "design the system", "right
  boundaries", "where does this state live", "is this architecture sound", "find the dependency
  cycle". NOT for a unit of code (code-decomposer), a UI component (component-decomposer), a UI
  layout (layout-decomposer), or a proof (proof-decomposer).
---

# architecture-decomposer — grade a software architecture on two crossing axes

A software architecture is **sound on two independent axes that walk the same hierarchy in opposite
directions** — the decomposer seam the code-, layout-, mermaid-, and component-decomposers apply to
units, space, diagrams, and components, here applied to a system / service / module graph:

- **Structure · whole → part** grades the **intent**: the context & boundaries → the containers/
  modules → their responsibilities → the interfaces between them → its fitness for the forces on it.
  *"Is it the right decomposition?"* (an LLM is strong here — it reads a design top-down).
- **Integrity · part → whole** grades the **mechanism**: the dependency graph is well-formed → it's
  acyclic → it respects the layering → coupling is bounded → it deploys. *"Does the structure
  actually hold, here?"* (an LLM fails silently here — it cannot tell by eye if a graph is acyclic —
  so it routes to code).

They **cross at the component dependency graph** — the set of edges between modules is *both* the
expression of the structure (what depends on what, by design) and the mechanism (what the
cycle/layering checker walks). That crossing is the whole technique: an architecture can be **elegant
on paper but cyclic/tangled** (crisp boxes and arrows, but a real cycle, a depends-up edge, or a
god-module hub) or **compiles & deploys but wrong boundaries** (a perfect DAG over a split
responsibility, a contested-ownership concept, a leaky interface). Opposite defects, opposite fixes —
so you **score and report the two axes separately**, never averaged.

The reason this is outsized for an LLM author: INTEGRITY is exactly where models can't verify by eye
*and* it is mechanizable — so the gate converts the worst failure into a caught error (Tarjan finds
the cycle; a layer-index compare finds the up-edge). And the **wrong-boundaries** quadrant — the one a
graph checker is blind to by construction — gets a dedicated attack: a fresh-context structural probe
+ stress scenarios.

## Quick Start

**You bring:** an architecture (a design doc, a repo, a boxes-and-arrows sketch) and the question —
"design this", "are these the right boundaries?", "is there a cycle?", "will it hold under change?".
**You get:** a contract card (the dependency graph + layers), an INTEGRITY report, and a two-axis
grade with the defect quadrant named.

> *"Is this service architecture sound?"* →
> 1. **Structure — context → containers:** boundaries carved at the right joints, each concept owned
>    once `[gate]`; the modules and their reason to exist `[gate]`.
> 2. **Integrity — run it, don't read it:** build the contract card (nodes + ordered layers + edges),
>    run `bin/dependency-check.py` — it flags CYCLE (Tarjan), LAYER_VIOLATION (depends-up),
>    HIGH_COUPLING (hub), ORPHAN `[gate B1/B2/B3]`. A gate flag stops the axis — fix the graph first.
> 3. **Adversarial structural probe:** in a fresh context, hunt one concept two modules both own, one
>    split responsibility, one leaky interface — any counterexample is a wrong-boundaries finding the
>    checker can't see.
> 4. **Review + report:** responsibilities/interfaces/fitness (A3–A5), coupling/deployability
>    (B4/B5), then the two axis scores + the quadrant cell — gate failures first — handed per-module to
>    `code-decomposer` and to `/code-review`.

**Modes:** **DESIGN** (Structure-down → declare the dependency graph → prove it can be acyclic+layered
→ emit a contract card) · **DECOMPOSE** (recover the boundaries + the real graph → run the INTEGRITY
ladder → grade) · **GRADE** (score both axes, gates before reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Structure** | whole → part | **A1** Context/boundaries → **A2** Containers/modules → **A3** Responsibilities → **A4** Interfaces → **A5** Fitness | "Is it the *right decomposition*?" |
| **B · Integrity** | part → whole | **B1** Graph well-formed → **B2** Acyclic → **B3** Layering → **B4** Coupling → **B5** Deployability | "Does the structure *actually hold*, here?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on
that axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A sound architecture is **≥4 on every review
with zero gate failures**, reported as two separate axis scores plus the defect quadrant.

## The doctrine — gate where you can, adversarially verify where you can't

The non-obvious core, and the reason it earns a skill:

- **INTEGRITY is the cheap, deterministic axis** — feed the dependency graph as a contract card to
  `bin/dependency-check.py` and **trust the tool, not the read-through**. It catches *elegant-on-paper
  but cyclic/tangled* outright (Tarjan's SCC for cycles, a layer-index compare for depends-up edges).
- **"Wrong boundaries" is NOT deterministically gateable** — it lives entirely on the STRUCTURE side,
  and a graph checker is silent on "this module owns the wrong concept." Route it two ways: a
  **fresh-context structural probe** (a skeptic hunting one contested-ownership concept / split
  responsibility / leaky interface) and **stress scenarios** (the most likely change, 10× load, a
  swapped dependency). A verifier sharing the author's context rubber-stamps it — separate the context
  (the `deep-research` move).
- **A clean run is necessary, not sufficient.** A green `dependency-check.py` proves the graph is
  acyclic + layered; it does **not** prove the boundaries are right. A perfect DAG over the wrong
  decomposition is the bottom-left quadrant — the tool is blind to it by construction.

## §SelfAudit

- **Integrity is the gate the LLM fails silently.** Run `dependency-check.py` over the real
  dependency graph; do not certify "it's acyclic / properly layered" from reading boxes-and-arrows. An
  unrun gate is *no evidence*, not a pass.
- **Grade the real graph, not the design doc's arrows.** For an existing system, recover edges from
  imports / build config / call sites — the doc's arrows are the STRUCTURE *claim*; the card is the
  INTEGRITY *reality*. A hidden edge found at B5 deployability is a missing edge — add it and re-run.
- **The dangerous defect is invisible to the tool — probe the structure adversarially in a fresh
  context.** "Wrong boundaries" needs a skeptic hunting a counterexample, not the author's confidence.
- **Gates before reviews, always.** Don't grade fitness for a graph with a cycle, or interfaces for a
  system carved at the wrong joints. Stop each axis at its first failed gate.
- **Two scores, never one.** *Elegant-but-cyclic* and *clean-but-wrong-boundaries* need opposite fixes
  (re-wire the graph vs re-draw the boundaries). Report both axes and name the quadrant; never average.
- **Boundaries + grade, not the build.** This skill locks the boundaries + dependency graph and emits
  the card — it does not write the modules (hand each to `code-decomposer`), hunt a diff
  (`/code-review`), run the app (`/verify`), or clean up quality (`/simplify`). Hand off; don't overlap.

## Verify Target

An architecture is **sound** when: it's carved at the right joints with each concept owned once
(A1/A2); responsibilities/interfaces/fitness ≥4; the contract card's graph ran **green** through
`dependency-check.py` (well-formed + acyclic + layered, B1/B2/B3); coupling is bounded and it deploys
as decomposed (B4/B5 ≥4); and both axes score ≥4 with zero gate failures, landing in the **SOUND**
quadrant — with the contract card ready to hand per-module to `code-decomposer` and to `/code-review`.
**NOT sound** when: the graph is a clean DAG but the decomposition is wrong — a split responsibility,
a contested-ownership concept, a leaky interface (*compiles & deploys, but wrong boundaries*); or the
boxes read beautifully but the real graph has a cycle or a depends-up edge (*elegant on paper, but
cyclic/tangled*); or a gate was skipped (graph not actually run) and reported as a pass; or one
blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Structure × Integrity), the leveled walk with gates, the quadrant, the gate-vs-adversarial-verify doctrine, and the DESIGN / DECOMPOSE / GRADE workflows |
| `references/architecture-knowledge.md` | **the Structure axis** — context/boundaries, ownership-first decomposition, types-are-the-architecture, responsibilities/interfaces/fitness, the seven domains (system · data · frontend · platform · SSR · MCP · A2UI), and the **adversarial structural probe** |
| `references/dependency-policy.md` | **the Integrity axis** — the dependency ladder, the **contract-card protocol** (nodes + ordered layers + edges), how to read each flag (CYCLE/LAYER_VIOLATION/HIGH_COUPLING/ORPHAN), the stress catalogue for fitness, and the handoff seams; mechanized by `bin/dependency-check.py` |
| `bin/dependency-check.py` | **mechanizes B1–B3 (+ B4 advisory)** — reads a contract card, flags CYCLE (Tarjan SCC), LAYER_VIOLATION (depends-up), HIGH_COUPLING (fan-in/out over threshold), ORPHAN; gate flags FAIL, advisory flags inform. `<card.json>` · `template` · `selftest` |
