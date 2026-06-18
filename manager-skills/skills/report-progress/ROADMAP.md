# Roadmap

Seeded from the 2026-05-31 `skills-critique` review (`reviews/2026-05-31-skills-critique-full-panel.md`, 2.4/5). §SelfAudit, the `stable → draft` demotion, the labeled checklist, the routing corpus, the enriched description, and this ROADMAP landed in v1.1.0; below is what `stable` will require.

## Planned
- [v1.2] **`scripts/check-report.py`** — mechanize the `[gate]` checklist vs the `report-authoring` rubric (skills-critique): every blocker has owner + date + deadline; every risk has likelihood/impact/mitigation/owner; every in-progress item has owner + target date; exec-RAG ≤ worst body RAG; next steps are owned + dated. Wire into `run-skill-gates.py`. Closes D4/D8 + the mechanizable half of D1.
- [v1.2] **Behavioral eval** — ≥3 cases asserting a produced report satisfies named gates (no orphaned blocker; exec-RAG consistent; ≥1 next step owned+dated). Routing corpus (D5) shipped v1.1.0.
- [v1.2] **Calibration anchors + labels for the RAG criteria** (D3) — one worked example per signal so two reporters converge; the "Optimistic Green" failure the skill warns about becomes a gated check.
- [v1.2] **No-prior-report recovery path** (D10 PA5) — define the first-ever-report branch; the skill currently leans on diffing against a prior report with no defined fallback.
- [v1.x] Re-earn `status: stable` once the behavioral eval + a mechanized gate exist and the routing F1 baseline holds.

## Deferred
- A shared `report-*` family `check-report.py` (one script over all four siblings) — deferred until the per-skill version proves its checks; revisit when ≥2 siblings have it.
- Multi-project / portfolio rollup — deferred because the skill's contract is a single bounded body of work; a rollup is `report-state`'s territory. Revisit only if a real multi-project progress need appears.

## Out of scope (by design)
- Executing the next steps or resolving the blockers it lists — the deliverable is a status document (stated in §SelfAudit, output scope).
- Visualizing the risk landscape — delegated to `viz-2x2`.
