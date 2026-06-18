# Roadmap

Seeded from the 2026-05-31 review (`reviews/2026-05-31-core-skills-evaluator-full-panel.md`, **4/5 CLEAN**). These are polish items, not blockers — the skill passed.

## Planned
- [v1.2] **`scripts/validate_2x2.py` (~30 lines).** Turn the artifact Quality checklist from self-assessment into a `[gate]`: grep the generated HTML for SVG-coordinate bounds (e.g. `y = 94 - (pct/100)*82` stays in-range), CSS-variables-only (no hardcoded hex), and OG-tags-present. Closes the lone Major (the diagram currently validates against nothing) + D4 (chart-coordinate math is mechanize-bait) + D8 (verify is self-assessed). Wire into `run-skill-gates.py`.
- [v1.2] **Label the Quality checklist** items `[gate]` (mechanical: coordinate bounds, CSS-vars, OG-tags) vs `[review]` (judgment: axis independence, archetype fit). *(D3)*
- [v1.2] **Reconcile eval-corpus version drift** — `routing-corpus.json` / `adversarial-corpus.json` self-version `0.1.0` while the skill is `1.1.x`.
- [v1.2] **Trim the ASCII wireframe** in SKILL.md (~25 lines) that duplicates the invariants table.

## Deferred
- A behavioral-corpus *runner* (the `adversarial-corpus.json` cases are currently eyeballed) — deferred because the routing corpus is already live + CI-gated (F1 0.72) and carries most of the regression value; revisit when `validate_2x2.py` lands and a behavioral harness can reuse its plumbing.

## Out of scope (by design)
- Chart types beyond the 2×2 quadrant (Venn, flowchart, ranking, gradient/heatmap) — excluded because the skill's whole discipline is the 4-archetype / 2-independent-axis form; other shapes route elsewhere. The routing corpus actively tests *against* these as adversarial negatives.
- JavaScript interactivity in the artifact — excluded by design; output is JS-free static HTML (also why the untrusted-input surface is near-N/A, D7=4).
