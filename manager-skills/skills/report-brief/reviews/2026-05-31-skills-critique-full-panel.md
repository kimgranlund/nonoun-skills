# report-brief — skills-critique review (score 10-dim + critique 9-critic), 2026-05-31

**Method:** one **fresh-context, blind** reviewer using `skills-critique` (score + critique modes). Every claim grep-verified against the files.

## Verdict — 2.4/5; **clears the bar (2 Critical + 3 Major).** `stable` not earned.

A well-written intelligence-brief template that borrows IC tradecraft (BLUF, confidence bands, source tiers, ACH) but ships every discipline as advisory prose — **present as form, absent as a gate, guard, or eval.** D9=4 (context engineering) is the strength.

| Dim | Score | Type | Finding |
|---|---|---|---|
| D1 Harness | 3 | review | No §SelfAudit; no Quick Start in first 50 lines (CS2 fail) |
| D2 Control mode | 4 | review | Good — judgment governed by checklist + confidence rubric, not a rigid procedure |
| D3 Rubric quality | 2 | gate+review | Quality Checklist entirely unlabeled; mechanical gates and judgment reviews indistinguishable |
| D4 Mechanization | 3 | gate | No `scripts/`; the confidence-lexicon banned-phrase list (`confidence-lexicon.md:108-124`) is a deterministic lint left as eyeballing |
| **D5 Evaluation** | **1** | gate | **No evals/, no routing corpus, F1 never measured.** Quality Checklist is a self-administered authoring aid |
| D6 Extensibility | 2 | review | ROADMAP template-only; no §Teach |
| **D7 Security** | **1** | gate | **Ingests untrusted sources** ("Available sources…" `SKILL.md:112`; `research-survey`) and emits "We assess with **high confidence**" with no injection guard / provenance / fabrication guard — AP-H3 trusted-content-reader |
| D8 Observability | 1 | review | Self-administered checklist is the only post-run signal; confident-but-wrong is the failure mode and self-grading is the weakest close |
| D9 Context eng | 4 | review | Strong progressive disclosure; minor eager duplication of the confidence table |
| D10 Plan anatomy | 3 | review | 7 phases ordered with one checkpoint, but narrative subgoals ("Judge", "Imply") |

## Top findings
- **[Critical] C1 — No trust boundary; the skill weaponizes confidence over unvetted input** *(Simon/Charity)* — calibrated confidence is the value prop, with no mechanism that the confidence tracks evidence vs a poisoned/hallucinated source. **Fix:** §SelfAudit + "no high-confidence judgment without ≥2 resolving sources" (the `tradecraft.md` rule, made a guard) + un-sourced→Gaps.
- **[Critical] C2 — Zero eval infrastructure under `stable`** *(Boris/Karpathy/Farley)* — routing collision with 3 near-synonymous siblings is unmeasured. **Fix:** routing corpus + demote to draft.
- **[Major] M1 — Unlabeled checklist** *(Wlaschin)* — mechanical vs judgment items indistinguishable. **Fix:** label + a 6-line `lint_brief.py`.
- **[Major] M2 — Self-referential verify** *(Charity/Farley)* — loop closes on the agent's own checklist; add an independent red-team pass.
- **[Major] M3 — Confidence lexicon manufactures authority with no calibration** *(Huyen/Karpathy)* — hard probability bands required, the honest escape ("67%") banned; tie bands to the source-count rule.
- [Minor] Description/structure duplication; CHANGELOG Files omits ROADMAP.md; narrative decomposition subgoals.

## Instrument probe — is a `report-authoring` rubric needed?
**Yes** — the holistic rubric carried ~85% (D5/D7/D3 landed cleanly via the AP-H3 pattern) but scores the skill-as-machine, not the report-document. The reviewer had to borrow the skill's own `tradecraft.md` standard (circular). Proposed dims: claim→evidence traceability `[gate]` (would have promoted C1 from a critic's catch to a gated line), source/trust posture `[gate]`, BLUF `[gate]`, calibration honesty `[hypothesis]`, audience fit, recommendation actionability, gap surfacing `[gate]`. **→ Acted on: `skills-critique` v2.1.0 added `report-authoring.md` with these dimensions.**

## Disposition
- **[done v1.1.0]** §SelfAudit (≥2-source confidence rule); status `stable → draft`; labeled checklist + banned-phrase/adopted-verdict gates; `evals/routing-corpus.json`; ROADMAP; enriched description (also lifts routing F1); CHANGELOG Files drift fixed.
- **[tracked — ROADMAP]** `scripts/lint_brief.py`; behavioral eval; independent verify pass; then re-earn `stable`.
