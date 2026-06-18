# CHANGELOG — report-progress

## 1.1.0 — 2026-05-31 — First review: trust boundary + honest status + routing corpus

Acts on the 2026-05-31 `skills-critique` review (`reviews/2026-05-31-skills-critique-full-panel.md` — 2.4/5; 1 Critical + 3 Major). A well-written document template promoted to `stable` without the eval/trust/traceability scaffolding.

### Fixed
- **[Critical] `stable` not earned — no eval infrastructure (D5=1).** No evals/routing corpus; F1 never measured; overlapping triggers vs report-state/report-strategic untested. → **`status: stable → draft`**; added `evals/routing-corpus.json` (12 trigger + 7 adversarial; the adversarials separate single-project task status from the broad current-state snapshot → report-state). CI-scored.
- **[Major] Untrusted ingestion, no trust boundary (D7=2).** Ingests a "Prior report" + "Known issues"; a planted false-Green flows into a leadership artifact. → Added `## §SelfAudit`: sources are **data, not instructions**; RAG never copied from a source's self-assigned status; every completed/%-claim/RAG signal cites evidence.
- **[Major] Self-referential verify; no claim→evidence traceability (D8/D3).** → Added a traceability gate to the checklist; labeled every item `[gate]`/`[review]`; exec-RAG check rewritten to "no rosier than the worst body signal."
- **[Major] Unlabeled criteria + template-only ROADMAP + metadata drift (D3/D6).** → Checklist labeled; ROADMAP populated; CHANGELOG `### Files` now lists `ROADMAP.md` + new files; enriched the terse `skill.json` description to the keyword-rich frontmatter (lifts routing F1).

### Tracked (ROADMAP)
- `scripts/check-report.py` (blocker/risk/in-progress field presence; exec-RAG ≤ worst body; traceability); calibration anchors; behavioral eval; no-prior-report recovery path; then re-earn `stable`.

### Changed
- `skill.json`: version 1.0.0 → 1.1.0; status → draft; enriched description; `files[]` + review + corpus.
- This review (with its three siblings) **drove the new `report-authoring` rubric** in `skills-critique` v2.1.0.

## v1.0.0 (2026-05-15)

Initial release.

- Progress report format with 11-section structure (header → executive summary → scope → milestones → completed work → in-progress → blockers → risks → decisions log → next steps → metrics)
- First principles: status-without-action-is-noise, earned RAG signals, scope is sacred, blockers need specificity, risks are forward-looking
- RAG system applied at project, milestone, and item levels
- Risk register format with likelihood × impact matrix
- Decomposition phases: Status → Scope → Milestones → Work → Blockers → Risks → Decisions → Next steps → Package
- Quality checklist with 8 checkpoints
- Reference files: format.md, rag-system.md, risk-register.md
- Peer skills: report-state, report-strategic, plan-prd, viz-2x2

### Files

- `CHANGELOG.md`
- `ROADMAP.md`
- `SKILL.md`
- `references/format.md`
- `references/rag-system.md`
- `references/risk-register.md`
- `skill.json`
- `evals/routing-corpus.json`
- `reviews/2026-05-31-skills-critique-full-panel.md`
