# Roadmap

Seeded from the 2026-05-31 `skills-critique` review (`reviews/2026-05-31-skills-critique-full-panel.md`, 2.4/5). §SelfAudit, the `stable → draft` demotion, the labeled checklist, the routing corpus, the enriched description, and this ROADMAP landed in v1.1.0; below is what `stable` will require.

## Planned
- [v1.2] **`scripts/lint_brief.py`** — mechanize the `[gate]` checklist items against the `report-authoring` rubric (skills-critique): BLUF confidence-token in sentence 1; every key judgment carries a lexicon token; banned-phrase scan from `confidence-lexicon.md`; ≥2-source rule for any high-confidence judgment. Wire into `run-skill-gates.py`. Closes D4 + the mechanizable half of D1/D6.
- [v1.2] **Behavioral eval** — ≥3 cases asserting a produced brief satisfies named gates (BLUF present; every judgment confidence-annotated; ≥1 specific intelligence gap). Routing corpus (D5) shipped v1.1.0; this is the output-quality half.
- [v1.2] **Independent verify pass** — a red-team re-read distinct from authoring (D8), since the only current gate is the author's own checklist.
- [v1.x] Re-earn `status: stable` once the behavioral eval + a mechanized gate exist and the routing F1 baseline holds.

## Deferred
- A shared `report-*` family lint (one script over all four siblings) — deferred until the per-skill version proves its checks; revisit when ≥2 siblings have it.

## Out of scope (by design)
- Acting on the assessment (collection tasking, executing implications) — the deliverable is a briefing document (stated in §SelfAudit, output scope).
- Calibrating an LLM's confidence to ground-truth probability — out of reach for a prose skill; the skill enforces the *source-count discipline* behind a confidence band, not statistical calibration.
