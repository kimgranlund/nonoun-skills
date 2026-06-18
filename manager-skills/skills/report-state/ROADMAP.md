# Roadmap

Seeded from the 2026-05-31 `skills-critique` review (`reviews/2026-05-31-skills-critique-full-panel.md`, 2.4/5). §SelfAudit, the `stable → draft` demotion, the labeled checklist, the routing corpus, the enriched description, and this ROADMAP landed in v1.1.0; below is what `stable` will require.

## Planned
- [v1.2] **`scripts/check-report.py`** — mechanize the `[gate]` checklist vs the `report-authoring` rubric (skills-critique): every matrix row has a non-empty evidence cell; exec-summary RAG ≤ worst body RAG; every 🔴 row has a Path-Forward action; every in-scope inventory item appears in the matrix. Wire into `run-skill-gates.py`. Closes D4/D8 + the mechanizable half of D1.
- [v1.2] **Per-RAG-level calibration anchors** — one worked example per signal ("Amber because metrics X,Y crossed thresholds T1,T2") so two assessors converge; label every RAG/checklist criterion `[gate]`/`[review]`. Closes the D3 AP-H1 confident-rubric-without-calibration gap.
- [v1.2] **Behavioral eval** — ≥3 cases asserting a produced report satisfies named gates. Routing corpus (D5) shipped v1.1.0.
- [v1.2] **Quick Start** + one fully-worked 3-component matrix example (CS2 + the missing worked example).
- [v1.x] Re-earn `status: stable` once the behavioral eval + a mechanized gate exist and the routing F1 baseline holds.

## Deferred
- A shared `report-*` family `check-report.py` (one script over all four siblings) — deferred until the per-skill version proves its checks; revisit when ≥2 siblings have it.

## Out of scope (by design)
- Acting on the assessment or executing the Path Forward — the deliverable is a current-state document (stated in §SelfAudit, output scope).
- Visual rendering — delegated to `viz-2x2`.
