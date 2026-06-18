# report-strategic — skills-critique review (score 10-dim + critique 9-critic), 2026-05-31

**Method:** one **fresh-context, blind** reviewer that *used* `skills-critique` (score mode = holistic 10-dim scorecard; critique mode = 9-critic panel). Every claim grep-verified against the files. Reviewer did not know the author.

## Verdict — 2.4/5; **clears the bar (2 Critical + 3 Major).** The `stable` label is not earned.

Zero evals, zero routing corpus, no §SelfAudit, no trust boundary; "verify" is a 10-item checklist the same agent ticks against its own draft. Strong context engineering (D9=4) is the one real strength.

| Dim | Score | Type | Finding |
|---|---|---|---|
| D1 Harness | 3 | review | No §SelfAudit; no Quick Start in first 50 lines (CS2 fail); first screen is First-Principles prose |
| D2 Control mode | 3 | review | Load-bearing "Analyze — synthesize findings" is a one-line phase label delegating judgment with no criteria at point of use |
| D3 Rubric quality | 3 | gate+review | `quality-rubric.md` is well-formed (10 dims, 24/30 gate) but **no `[gate]`/`[review]`/`[hypothesis]` labels**; "24/30 = publication-grade" is an unlabeled `[hypothesis]` asserted as fact |
| D4 Mechanization | 1 | gate | No `scripts/`; mechanize-bait left as prose ("every term defined in glossary", "references complete", "no orphaned finding") |
| **D5 Evaluation** | **1** | gate | **No evals/, no routing corpus, no behavioral eval, F1 never measured.** Verify = self-scored checklist |
| D6 Extensibility | 2 | review | ROADMAP template-only (empty); no §Teach; no observed compounding |
| **D7 Security** | **1** | gate | **Zero trust/injection/provenance language** (grep: none). Ingests "available sources" + invokes `research-survey` (web fetch) → writes a document. No data/instruction boundary; the "reliability tier" field is editorial hygiene, not an injection guard |
| D8 Observability | 1 | review | Verify is self-assessment; no external signal, no audit trail |
| D9 Context eng | 4 | review | Genuinely good — references load on explicit conditions; progressive disclosure |
| D10 Plan anatomy | 3 | review | Sensible 6-phase decomposition (summary last) but vague subgoals, no checkpoint before the expensive write |

## Top findings
- **[Critical] C1 — `stable` is a false label; verify closes on the agent's own draft** *(Boris/Charity/Karpathy/Farley)* — no evals/scripts/reviews on disk; the only gate is "score against quality-rubric.md" self-scored. **Fix:** demote to `draft` + add a routing corpus (measured F1) + behavioral cases.
- **[Critical] C2 — Untrusted-content ingestion with no trust boundary** *(Simon/Wlaschin)* — `research-survey` web output + pasted sources flow into "findings"/"recommendations" with no data-vs-instruction separation; a planted source can launder an instruction into a "Primary" finding. **Fix:** §SelfAudit trust boundary + finding→citation traceability.
- **[Major] M1 — Rubric unlabeled + uncalibrated; 24/30 threshold asserted** *(Wlaschin/Huyen)*.
- **[Major] M2 — Mechanize-bait left as prose; no `scripts/check-report.py`** *(Elon/Farley)*.
- **[Major] M3 — Metadata drift: SKILL.md frontmatter has no `version`; CHANGELOG Files block omits ROADMAP.md** *(Farley/Steve)*.
- [Minor] No §SelfAudit / Quick Start; Recommendation format hard-requires "Owner" even for external/thought-leadership reports where none exists (control-mode over-prescription).

## Instrument probe — is a `report-authoring` rubric needed?
**Yes, sharply.** The holistic rubric scored the skill-as-machine but is blind to whether the skill produces a *good report*; the reviewer had to fall back on the skill's own (unlabeled, uncalibrated) `quality-rubric.md` — circular. Recommended dimensions: claim→evidence traceability `[gate]`, source/trust boundary, BLUF/pyramid, audience fit, recommendation actionability (owner conditional on audience), calibration `[hypothesis]`. **→ Acted on: `skills-critique` v2.1.0 added `references/rubrics/report-authoring.md` with exactly these dimensions.**

## Disposition
- **[done v1.1.0]** §SelfAudit trust boundary added; status `stable → draft`; Quality Checklist labeled `[gate]`/`[review]`; `evals/routing-corpus.json` added (triggers + sibling-disambiguating adversarials); ROADMAP populated; CHANGELOG Files drift fixed.
- **[tracked — ROADMAP]** `scripts/check-report.py` (mechanize D1/D5/D7 against the new report-authoring rubric); behavioral eval; calibrate the 24/30 threshold; add Quick Start; make Owner conditional on audience.
- First skill reviewed with `skills-critique` post-merge; drove the `report-authoring` instrument addition.
