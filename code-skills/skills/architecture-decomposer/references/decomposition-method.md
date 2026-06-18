# The two-axis method — STRUCTURE × INTEGRITY

A software architecture is **sound on two independent axes that walk the same hierarchy in opposite
directions** — the decomposer seam the code-, layout-, mermaid-, and component-decomposers apply to
units, space, diagrams, and components, here applied to a system / service / module graph.

- **Structure · whole → part** grades the **intent**: the system's context → its containers/modules →
  the responsibilities of each → the interfaces between them → its fitness for the forces on it.
  *"Is it the right decomposition?"* This is where an LLM is strong (reads a design top-down).
- **Integrity · part → whole** grades the **mechanism**: the dependency graph is well-formed → it's
  acyclic → it respects the layering → coupling is bounded → it deploys. *"Does the structure
  actually hold, here?"* This is where an LLM fails silently — it cannot reliably tell by eye whether
  a graph is acyclic or every edge respects layering — so it is **routed to code**
  (`bin/dependency-check.py`).

They **cross at the component dependency graph** — the set of edges between modules is *both* the
expression of the structure (what depends on what, by design) and the mechanism (what the
cycle/layering checker walks). A structure that won't hold as a graph is a diagram, not an
architecture; a graph that's clean but built on the wrong boundaries is "compiles but wrong."

That crossing is the whole technique. An architecture can be:

- **elegant on paper, but cyclic / tangled** — the boxes-and-arrows read beautifully, the
  responsibilities are crisp, but the real dependency graph has a cycle, an edge that points up
  through the layers, or a god-module every other module reaches into. The classic
  design-doc-vs-reality gap: a clean picture over a knot.
- **compiles & deploys, but wrong boundaries** — the graph is a perfect DAG, every layer is
  respected, it builds and ships — but the decomposition is wrong: one module owns two
  vocabularies, a responsibility is split across three containers, the interface leaks internals.
  The classic LLM trap: a mechanically valid structure around the wrong concepts.

Opposite defects, opposite fixes — so you **score and report the two axes separately, never
averaged.** An averaged score hides which one you have, and they need opposite work (re-wire the
graph vs re-draw the boundaries).

## The leveled walk

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Structure** | whole → part | **A1** Context/boundaries `[gate]` → **A2** Containers/modules `[gate]` → **A3** Responsibilities → **A4** Interfaces/contracts → **A5** Fitness | "Is it the *right decomposition*?" |
| **B · Integrity** | part → whole | **B1** Graph well-formed `[gate, code]` → **B2** Acyclic `[gate, code]` → **B3** Layering respected `[gate, code]` → **B4** Coupling bounded → **B5** Deployability | "Does the structure *actually hold*, here?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** — a failure cascades and BLOCKS the reviews below it on
that axis. `A3–A5 · B4–B5` are **`[review]`s** (1–5). A sound architecture is **≥4 on every review
with zero gate failures**, reported as two separate axis scores plus the quadrant cell.

### A · Structure (whole → part)

- **A1 Context / boundaries `[gate]`** — is the system carved at the right joints? Are the external
  actors, the system boundary, and the bounded contexts named in the user's vocabulary, with each
  concept owned by exactly one place? A wrong top-level boundary makes everything below moot. (The
  ownership question — see `references/architecture-knowledge.md`.)
- **A2 Containers / modules `[gate]`** — the major deployable/buildable units (services, packages,
  layers) and their reason to exist. A unit with no clear reason, or two units that should be one,
  poisons every decision under it.
- **A3 Responsibilities `[review]`** — single-responsibility, cohesion, the right altitude per
  module. Does each module do one thing, with high internal cohesion?
- **A4 Interfaces / contracts `[review]`** — the public surface each module exposes: narrow,
  explicit, result-typed, immutable at the boundary. Leaky abstractions and god-interfaces live here.
- **A5 Fitness `[review]`** — the *-ilities under the real forces: scalability, evolvability,
  the cost of the most likely change, operability. Does the structure serve the forces on it?

### B · Integrity (part → whole)

- **B1 Graph well-formed `[gate, code]`** — every node and edge resolves: no edge to a nonexistent
  module, no dangling reference. (Routed to `bin/dependency-check.py` card parse.)
- **B2 Acyclic `[gate, code]`** — the module dependency graph has **no cycle**. A cycle means two
  modules can't be built, tested, reasoned about, or replaced independently. (Tarjan SCC in the bin.)
- **B3 Layering respected `[gate, code]`** — every edge points **down** the declared layer order; no
  module depends *up* on a layer above it. (The `LAYER_VIOLATION` check in the bin.)
- **B4 Coupling bounded `[review]`** — fan-in / fan-out per module is within reason; no hub every
  module reaches into, no module that reaches into everything. (The bin's `HIGH_COUPLING` advisory
  feeds this review.)
- **B5 Deployability `[review]`** — it actually builds, packages, and deploys as decomposed; the
  units have independent lifecycles where the design claims they do.

## The opposite-defect quadrant

```
                  B · INTEGRITY holds        B · INTEGRITY fails
A · STRUCTURE  ┌────────────────────────┬────────────────────────┐
  passes       │       SOUND            │  elegant on paper, but  │
               │                        │  cyclic / tangled —     │
               │  right boundaries AND  │  crisp boxes & arrows,  │
               │  a clean, layered,     │  but a real cycle, a    │
               │  bounded graph         │  depends-up edge, or a  │
               │                        │  god-module hub         │
               ├────────────────────────┼────────────────────────┤
A · STRUCTURE  │ compiles & deploys,    │       REBUILD           │
  fails        │ but wrong boundaries — │                         │
               │ a perfect DAG over the │                         │
               │ wrong decomposition    │                         │
               │ (split/merged concept, │                         │
               │ leaky interface)       │                         │
               └────────────────────────┴────────────────────────┘
```

The quadrant **names the fix**: top-right needs **graph work** the design eye misses (break the
cycle, reverse the up-edge, split the hub) — route it to `bin/dependency-check.py`. Bottom-left needs
**boundary work** the graph checker **cannot see** (re-draw the contexts, re-assign a
responsibility, narrow an interface) — route it to a fresh-context structural review.

## The doctrine — gate where you can, adversarially verify where you can't

This is why the skill earns its place (and why it's outsized for an LLM author):

- The INTEGRITY gates (B1/B2/B3) are the **cheap, deterministic** axis — feed the dependency graph as
  a contract card to `bin/dependency-check.py` and **trust the tool, not the read-through**. An LLM
  cannot reliably tell by eye whether a 30-node graph is acyclic or whether every one of 60 edges
  respects the layering — but Tarjan's SCC and a layer-index comparison can, every time. This catches
  *elegant-on-paper-but-cyclic* outright.
- But the **dangerous** axis ("compiles & deploys, but wrong boundaries") is entirely on the
  STRUCTURE side, and it is **not deterministically gateable** — a graph checker is silent on "this
  module owns the wrong concept." Route it two ways:
  - **An adversarial STRUCTURE probe** for A1/A3: a *fresh-context* skeptic asked to find one
    concept that two modules both claim to own, one responsibility split across containers, or one
    interface that leaks internals. A verifier sharing the author's context inherits its blind spots —
    separate the context (the `deep-research` adversarial-verify move).
  - **Stress scenarios** for A5 fitness — walk the most likely change, the 10× load, the swapped
    dependency, the partial failure (see `references/dependency-policy.md`); friction under a scenario
    the boxes-and-arrows hid is a structural finding.

**The clean run is necessary, not sufficient.** A green `dependency-check.py` proves the graph is
well-formed, acyclic, and layered — it does **not** prove the boundaries are right. A perfect DAG over
the wrong decomposition is the bottom-left quadrant; the tool is blind to it by construction. Confirm
the dangerous case adversarially.

## Modes

- **DESIGN** (before building) — walk Structure-down (context → containers → responsibilities →
  interfaces → fitness), declare the dependency graph as a contract card, run
  `dependency-check.py` on the *proposed* graph to prove it CAN be acyclic + layered, emit the card.
- **DECOMPOSE** (existing system) — recover the boundaries (A1/A2) and the real dependency graph
  (extract edges from imports / build config / call sites), run the INTEGRITY ladder (B1–B3 via the
  bin), score the reviews; emit the contract card + a gap list (e.g. *"acyclic, but `billing` and
  `orders` both own `Customer` — bottom-left"*).
- **GRADE** — score both axes, gates first (run the bin + a fresh-context structural probe + stress
  scenarios), place in the quadrant, name one corrective per failure.

## Walk order (do not skip)

1. **A1 Context / A2 Containers** — name the boundaries and the major units. Wrong ⇒ stop, re-carve.
2. **B1/B2/B3 Integrity** — build the contract card, run `dependency-check.py`. A gate flag (cycle,
   layer violation) ⇒ fix the graph before reviewing (you can't grade fitness for a tangled graph).
3. **B4 coupling** — read the `HIGH_COUPLING` advisories; a hub is a structural smell to confirm.
4. **A1/A3 adversarial structural probe** — in a fresh context, hunt one contested-ownership concept,
   one split responsibility, one leaky interface.
5. **A5 fitness stress** — walk the most likely change + a failure/scale scenario.
6. **Reviews** — A3–A5 then B4–B5, 1–5 each. Below 4 ⇒ name the single corrective.
7. **Report** — two axis scores, the quadrant cell, gate failures first; hand the verified contract
   card to a code author (`code-decomposer` per module) and `/code-review`.
