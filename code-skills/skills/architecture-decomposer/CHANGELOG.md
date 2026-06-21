# Changelog — architecture-decomposer

Versioned independently of the `code-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.2.0 — beta

Enriched `references/architecture-knowledge.md` with the **two-plane reasoning model** and the **named
canon** distinguished engineers cite — the template for the repo-wide OUTSIDE-IN/INSIDE-OUT alignment
(see `HOWTO.md`).

- **Two planes, reasoned in parallel.** **OUTSIDE-IN** — the goals and ranked **architecture
  characteristics** (*-ilities*) the system serves, with the *everything-is-a-trade-off* framing (lives
  in A1 context / A5 fitness) — × **INSIDE-OUT** — the technical foundations that hold it up (A1–A4),
  mechanically verified by INTEGRITY. The two compose into a 2×2 (plane × intent/mechanism) where the
  mechanizable cells route to `bin/` — `dependency-check.py` named as the **fitness function** it is.
- **The named canon, each mapped to a method level** — coupling/cohesion, **connascence** (the coupling
  metric `dependency-check.py` approximates), Separation of Concerns + **Information Hiding** (Parnas),
  **SOLID** (SRP→A3, ISP→A4, DIP→dependency direction), **Dependency Inversion** & the dependency rule,
  **DDD bounded contexts** (= A1 vocabulary boundaries), **Hexagonal / Ports & Adapters** and
  **CLEAN / Onion** (A4 + the inward dependency rule), **Conway's Law + inverse Conway**, **evolutionary
  architecture & fitness functions**, and **ADRs / C4** for decision capture and leveled views. The
  skill now *operationalizes* the standard vocabulary instead of paraphrasing it.
- SKILL.md surfaces the two-plane model in the method section and the references table.

## 0.1.0 — draft

Initial release. Decompose / design / grade a software architecture on the **STRUCTURE × INTEGRITY**
crossing axes, scored separately with a gated rubric and the opposite-defect quadrant. Graduates the
root `arch-system` skill (type-driven, ownership-first system design) into the nonoun "decomposer"
vintage — the same domain knowledge, now folded into a two-axis grader with a deterministic mechanism
gate.

- **The two-axis method** (`references/decomposition-method.md`): Structure (context/boundaries →
  containers/modules → responsibilities → interfaces → fitness) × Integrity (graph well-formed →
  acyclic → layering respected → coupling bounded → deployable), crossing at the **component
  dependency graph**; gates before reviews; the *elegant-on-paper-but-cyclic* vs
  *compiles-but-wrong-boundaries* quadrant; and the **gate-where-you-can, adversarially-verify-where-
  you-can't** doctrine.
- **The dependency checker** (`references/dependency-policy.md` + `bin/dependency-check.py`): the
  mechanized attack on the INTEGRITY axis — reads an architecture **contract card** (components +
  ordered layers + edges) and flags **CYCLE** (Tarjan SCC, a gate failure), **LAYER_VIOLATION**
  (a depends-up edge, a gate failure), **HIGH_COUPLING** (fan-in/out over threshold, advisory), and
  **ORPHAN** (no edges in or out, advisory). `selftest` proves every check with **must-flag AND
  must-not-flag** fixtures (a clean DAG passes with zero findings; a diamond does not false-positive
  as a cycle; a down-edge does not false-positive as a layer violation), with no external deps.
- **The STRUCTURE axis** (`references/architecture-knowledge.md`): the substance graduated from
  `arch-system` — context/boundaries, ownership-first decomposition, types-are-the-architecture, the
  seven domains (system · data · frontend/CSS-tokens-components · platform · SSR · MCP · A2UI), and
  the fresh-context **adversarial structural probe** for the wrong-boundaries quadrant.
- **The INTEGRITY axis & policy** (`references/dependency-policy.md`): the dependency ladder, the
  contract-card protocol, how to read each flag, the **stress catalogue** for fitness/deployability,
  and the handoff seams to `code-decomposer` (per module), `/code-review`, `/verify`, and `/simplify`.
- **A routing corpus** (`architecture-decomposer.corpus.json`): sibling-collision-tested positives +
  adversarial negatives, fencing the family neighbours (code-/component-/layout-/proof-decomposer).
