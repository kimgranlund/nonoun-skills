# Roadmap

Seeded from the 2026-05-31 `skills-critique` review (`reviews/2026-05-31-skills-critique-full-panel.md`, 2.4/5). The §SelfAudit trust boundary, the `stable → draft` demotion, the labeled checklist, the routing corpus, and this ROADMAP landed in v1.1.0; the items below are what `stable` will require.

## Planned
- [v1.2] **`scripts/check-report.py`** — mechanize the `[gate]` checklist items against the `report-authoring` rubric (skills-critique): glossary-term coverage, no-orphaned-finding (finding→implication/recommendation cross-ref), references-completeness, and a §SelfAudit grep (claim→evidence traceability). Wire into `run-skill-gates.py`. Closes D4 + the mechanizable half of D1/D5.
- [v1.2] **Behavioral eval** — ≥3 cases asserting a produced report satisfies named gates (exec-summary stands alone; every finding cited; ≥1 scope limitation stated). The routing corpus (D5) shipped in v1.1.0; this is the output-quality half.
- [v1.2] **Calibrate the `quality-rubric.md` 24/30 publication threshold** — currently an unlabeled `[hypothesis]` asserted as fact; label every dimension `[gate]`/`[review]`/`[hypothesis]` and tie the threshold to a real reader-outcome signal.
- [v1.2] **Quick Start** within the first 50 lines (CS2 gate) with one worked mini-example.
- [v1.x] Re-earn `status: stable` once the behavioral eval + a mechanized gate exist and the routing F1 baseline holds.

## Deferred
- A shared `report-*` family `check-report.py` (one script over all four siblings) — deferred until the per-skill version proves its checks; revisit when ≥2 siblings have the script so the common core is clear.

## Out of scope (by design)
- Executing the report's recommendations or acting on the systems it describes — the deliverable is a document (stated in §SelfAudit, output scope).
- Visual rendering / diagram generation — delegated to `viz-2x2`.
