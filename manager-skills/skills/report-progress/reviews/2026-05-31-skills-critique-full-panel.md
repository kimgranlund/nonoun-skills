# report-progress — skills-critique review (score 10-dim + critique 9-critic), 2026-05-31

**Method:** one **fresh-context, blind** reviewer using `skills-critique` (score + critique modes). Every claim grep-verified against the files.

## Verdict — 2.4/5; **clears the bar (1 Critical + 3 Major).** `stable` not earned.

A well-written PM document template promoted to `stable` without the eval, trust, and traceability scaffolding that turns a template into a capability contract. D9=4 (context engineering) the strength; the five `[gate]` dims average ~1.6.

| Dim | Score | Type | Finding |
|---|---|---|---|
| D1 Harness | 3 | review | No §SelfAudit; no Quick Start (CS2 fail); description 963 chars (over the ~950 guidance) |
| D2 Control mode | 4 | review | Correct: deterministic skeleton as Procedure, judgment as Rubric; the core "Green or Amber?" act is under-instrumented (no scored rubric/calibration) |
| D3 Rubric quality | 2 | gate+review | Zero `[gate]`/`[review]`/`[hypothesis]` labels anywhere; "RAG must be earned" has no calibration anchor |
| D4 Mechanization | 2 | gate | No `scripts/`; "exec RAG matches body", "every blocker has owner/date" are checkable but prose |
| **D5 Evaluation** | **1** | gate | **No evals/, no routing corpus, zero adversarial phrases to separate it from report-state/report-strategic;** F1 never measured |
| D6 Extensibility | 2 | review | ROADMAP 14 lines of empty template comments under a `stable` label |
| D7 Security | 2 | gate | Ingests "Prior report"/"Known issues" → leadership narrative, with no scope/injection/trust statement (grep: 0 hits) — AP-H3 trusted-content-reader; a planted false-Green flows in unchallenged |
| D8 Observability | 2 | review | Terminal gate checks document *shape*, never *truth*; no claim→evidence traceability |
| D9 Context eng | 4 | review | Strong progressive disclosure under Execution |
| D10 Plan anatomy | 3 | review | Clean 9-step sequence (summary derived from body) but no no-prior-report recovery branch |

## Top findings
- **[Critical] C1 — `stable` is asserted, not earned (D5=1)** *(Boris/Charity/Farley/Karpathy)* — no evals/scripts/reviews on disk; first eval date does not exist; RAG output has no automatic reward signal. **Fix:** demote to draft + routing corpus (adversarials must separate report-progress from report-state/report-strategic).
- **[Major] M1 — Untrusted ingestion, defenseless content-reader (D7=2)** *(Simon)* — a false-Green in a prior report is indistinguishable from legitimate content and reaches a leadership artifact. **Fix:** §SelfAudit (source = data; RAG never copied from a source) + a "RAG derived from evidence, never copied" checklist line.
- **[Major] M2 — Only verify is self-assessment; no claim→evidence traceability (D8/D3)** *(Charity/Wlaschin/Karpathy)* — the checklist verifies "well-formed", never "accurate"; false-Green lives in that gap. **Fix:** traceability gate (every completed/%-claim/RAG cites a source).
- **[Major] M3 — Unlabeled criteria + empty ROADMAP undercut the skill's own discipline (D3/D6)** *(Boris/Steve)* — plus a metadata sub-finding: CHANGELOG Files omits ROADMAP.md while skill.json files[] includes it.
- [Minor] No Quick Start; description over the ~950 guidance; no no-prior-report branch.

## Instrument probe — is a `report-authoring` rubric needed?
**Yes.** The holistic rubric scores the skill-as-machine, not the report it emits; the most consequential question ("will the report be accurate, well-targeted, actionable?") had to be smuggled into D8/D3/D10 — and D10 (execution plans) fit report-as-output awkwardly. Proposed dims (each `[gate]`/`[review]`): claim→evidence traceability, BLUF/pyramid, audience fit, recommendation/next-step actionability, source-trust boundary, calibrated-signal discipline. Without R1/R4/R5 as named gates a less rubric-fluent reviewer would miss the traceability and audience-fit gaps. **→ Acted on: `skills-critique` v2.1.0 added `report-authoring.md`.**

## Disposition
- **[done v1.1.0]** §SelfAudit (RAG never copied from a source); status `stable → draft`; labeled checklist + traceability + exec-RAG-≤-worst gates; `evals/routing-corpus.json` (report-state disambiguation); ROADMAP; enriched description; CHANGELOG Files drift fixed.
- **[tracked — ROADMAP]** `scripts/check-report.py`; behavioral eval; RAG calibration anchors; no-prior-report recovery; then re-earn `stable`.
