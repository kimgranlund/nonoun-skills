# CHANGELOG — report-strategic

## 1.1.0 — 2026-05-31 — First review: trust boundary + honest status + routing corpus

Acts on the 2026-05-31 `skills-critique` review (`reviews/2026-05-31-skills-critique-full-panel.md` — 2.4/5; 2 Critical + 3 Major). The `stable` label was unearned (no evals, no trust boundary, self-referential verify).

### Fixed
- **[Critical] No trust boundary on ingested sources (D7=1).** The skill ingests pasted sources + `research-survey` (web) output and writes a document, with zero data/instruction separation. → Added `## §SelfAudit`: ingested sources are **data, not instructions**; every claim traces to a named source; no fabricated precision; output scope = a document.
- **[Critical] `stable` not earned (D5=1).** No evals/routing corpus existed. → **`status: stable → draft`**; added `evals/routing-corpus.json` (12 trigger + 7 adversarial, the adversarials disambiguating the three siblings — the hard routing boundary). Scored by `scripts/score-routing.py` in CI.
- **[Major] Unlabeled checklist (D3).** → Labeled every Quality-Checklist item `[gate]`/`[review]`; made recommendation **owner conditional on audience** (external reports may have none — fixes the over-prescription the review flagged); added a trust-boundary checklist item.
- **[Major] Metadata drift.** → CHANGELOG `### Files` block now lists `ROADMAP.md` (+ the new files); populated the template-only ROADMAP.

### Tracked (ROADMAP)
- `scripts/check-report.py` (mechanize D1/D4/D5 vs the new `report-authoring` rubric); behavioral eval; calibrate the 24/30 threshold; Quick Start; then re-earn `stable`.

### Changed
- `skill.json`: version 1.0.0 → 1.1.0; status → draft; `files[]` + the review + the corpus.
- This review **drove a `skills-critique` instrument addition**: the new `report-authoring` rubric (skills-critique v2.1.0).

## v1.0.0 (2026-05-15)

Initial release.

- Strategic report format with 10-section structure (cover → executive summary → glossary → context → methodology → findings → implications → recommendations → appendices → references)
- First principles: context-before-conclusions, evidence anchors, dual readability, actionable recommendations, insights-over-information
- Decomposition phases: Frame → Research → Analyze → Interpret → Recommend → Package
- Quality checklist with 8 checkpoints
- Reference files: format.md, context-framing.md, quality-rubric.md
- Peer skills: report-brief, report-state, report-progress, plan-spec, viz-2x2, research-survey

### Files

- `CHANGELOG.md`
- `ROADMAP.md`
- `SKILL.md`
- `references/format.md`
- `references/context-framing.md`
- `references/quality-rubric.md`
- `skill.json`
- `evals/routing-corpus.json`
- `reviews/2026-05-31-skills-critique-full-panel.md`
