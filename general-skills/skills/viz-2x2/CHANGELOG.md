# CHANGELOG — viz-2x2

## v1.1.1 — First review: clean pass; ROADMAP populated (2026-05-31)

Acts on the 2026-05-31 review (`reviews/2026-05-31-core-skills-evaluator-full-panel.md` — **4/5; CLEAN**, 0 Critical, 1 Major). The first skill of the review campaign to clear with no Critical: correct control-mode design, textbook context engineering, and — verified live by the subagent — a real, CI-gated routing eval (`score-routing.py viz-2x2` → F1 **0.72**, in `routing-baselines.json`, run by `run-skill-gates.py`).

### Changed
- Populated `ROADMAP.md` (was template-only — the D6 Minor).
- Fixed the stale CHANGELOG File-Inventory footer (listed only `SKILL.md` + `template.md`).
- `skill.json`: version 1.1.0 → 1.1.1; `files[]` + the review doc.

### Tracked (ROADMAP — polish, not blockers)
- A ~30-line `scripts/validate_2x2.py` (SVG-coordinate bounds + CSS-var/OG-tag grep) to turn the artifact Quality checklist from self-assessment into a `[gate]` — closes the lone Major (artifact validates against nothing) + D4/D8. Label the Quality checklist `[gate]`/`[review]`; reconcile the eval-corpus `0.1.0` vs skill `1.1.x` version drift.

## v1.1.0 — Eval corpus + skill.json polish (2026-05-23)

### Added

- **`evals/routing-corpus.json`** — 12 trigger phrases + 5 adversarial cases
  testing wrong-cardinality (3/6 instead of 4), wrong-shape (ranking, flowchart,
  Venn), and gradient-vs-quadrant ambiguity.
- **`evals/adversarial-corpus.json`** — 5 behavioral evals covering axis
  independence violations, cardinality mismatch (5 archetypes), all-anti-pattern
  matrices, vague trade-offs, and ranking-disguised-as-2×2.

### Changed

- `skill.json` description harmonized with SKILL.md frontmatter — was a different
  one-line summary; now carries the full WHAT+WHEN+NEG form.
- `skill.json` tags expanded from `["ui"]` to 10 entries: `ui`, `2x2`, `matrix`,
  `quadrant`, `framework`, `comparison`, `strategic-thinking`, `trade-offs`,
  `artifact`, `html`.
- `skill.json` files[] updated to include the two new evals corpora.

## v1.1 — Artifact mode + Claude Design theme support (2026-05-12)

### Added

- **`references/claude-artifacts.md`** — Deployment guide for Claude Chat (claude.ai)
  artifact mode and Claude Design theme integration. Covers artifact tag format,
  CSP sandbox constraints, font fallback strategy, theme override layer, and
  cross-environment checklist.
- **`references/visual-system.md`** — Comprehensive design system specification
  explaining the *why* behind every visual decision (colors, typography, layout,
  SVG chart spec, curve taxonomy, responsive behavior, accessibility).
- **Artifact layout ASCII wireframe** in `SKILL.md` — helps agents reason about
  DOM structure without reading the full template.
- **Two output modes** documented in `SKILL.md` — artifact mode (Claude Chat/
  Design) vs file mode (disk sharing).
- **System font fallback** explicitly documented — `system-ui, -apple-system`
  are declared before `DM Sans`; Google Fonts treated as progressive enhancement.
- **Theme override layer** in template CSS — commented `:root` block for Claude
  Design base themes, ready to uncomment when deploying in Design context.

### Changed

- `Step 7` renamed from "Save and present" to "Present" with artifact/file
  mode branching.
- `skill.json` files[] updated to include `visual-system.md` and
  `claude-artifacts.md`.
- Template `<head>` comments added explaining font loading strategy and
  design token override pattern.

## 0.2.0 — 2026-05-07 — Naming Convention Rename

- Renamed from `2x2-matrix` to `viz-2x2` per the `viz-` domain/phase convention.
- All cross-references in downstream/upstream skills updated.

## v1.0 — Initial release (2026-04-11)

Initial skill authored.

## File Inventory

```
viz-2x2/
├── SKILL.md
├── skill.json
├── CHANGELOG.md
├── ROADMAP.md
├── references/
│   ├── template.md
│   ├── visual-system.md
│   └── claude-artifacts.md
├── evals/
│   ├── routing-corpus.json
│   └── adversarial-corpus.json
└── reviews/
    └── 2026-05-31-core-skills-evaluator-full-panel.md
```
