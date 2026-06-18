# Roadmap — architecture-decomposer

Ships its core in 0.1.0 (the two axes, the dependency checker, the contract-card protocol, the
graduated STRUCTURE knowledge, the stress catalogue). Everything below is additive.

## `bin/dependency-check.py`

- [ ] **Edge extractors** — derive a contract card from a real codebase instead of hand-authoring it:
      a Python import grapher (`ast`), a JS/TS import grapher (regex), a build-config reader
      (`package.json` workspaces, Cargo, go.mod). Each with its own fixtures. This closes the
      "grade the real graph, not the doc's arrows" gap mechanically.
- [ ] **Shortest-cycle report** — when CYCLE fires, report the *minimal* back-edge to break, not just
      the SCC, so the fix is one edge to invert.
- [ ] **Acyclic-but-fragile metrics** — instability (I = fanout / (fanin+fanout)) and a
      distance-from-main-sequence score per module, surfaced as advisories alongside HIGH_COUPLING.
- [ ] A `--json` report mode so GRADE can fold the INTEGRITY findings into a machine-readable card.
- [ ] **Layer inference** — when `layer_of` is omitted, infer candidate layers from the graph's
      topological levels and flag where the inferred layering and the declared one disagree.

## Method & corpus

- [ ] A worked **end-to-end transcript** (a service DESIGN → contract card → DECOMPOSE of the built
      repo → GRADE), with the card, the INTEGRITY report, and a cycle-break fix checked in and
      dogfooded — the maturity step the repo ROADMAP tracks.
- [ ] An **adversarial-probe template** (the fresh-context structural-skeptic prompt) as a reusable
      reference, shared in shape with `deep-research`'s verify step and `code-decomposer`'s spec probe.
- [ ] A **fitness-function** deepening — turning the stress catalogue into checked-in executable
      architecture fitness functions (ArchUnit-style) where the toolchain supports it.
- [ ] A `domain-*` deepening for the highest-risk of the seven domains (SSR hydration boundaries; MCP
      tool/resource ownership) if the single `architecture-knowledge.md` table proves too thin.

## Plugin

- [ ] Promote to **beta** once the routing corpus is exercised against the live sibling set and the
      worked transcript lands. The sharpest collisions to keep fenced: `code-decomposer` (a unit
      inside one module vs the graph between modules) and the graduated-from `arch-system` root skill.
