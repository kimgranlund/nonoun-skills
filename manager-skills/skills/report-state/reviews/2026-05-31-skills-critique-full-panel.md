# report-state — skills-critique review (score 10-dim + critique 9-critic), 2026-05-31

**Method:** one **fresh-context, blind** reviewer using `skills-critique` (score + critique modes). Every claim grep-verified against the files.

## Verdict — 2.4/5; **clears the bar (1 Critical + 3 Major).** `stable` not earned.

Four `[gate]` dimensions (D3, D4, D5, D7) fail. Strong context engineering (D9=4); the whole `report-*` family shares this exact gap profile — a systemic mislabel, not a one-off.

| Dim | Score | Type | Finding |
|---|---|---|---|
| D1 Harness | 3 | review | No §SelfAudit; no Quick Start in first 50 lines; no worked example anywhere (only the empty template) |
| D2 Control mode | 4 | review | Good entropy match (deterministic structure as Procedure, judgment as Rubric); one mismatch — judgment checks framed as binary `[ ]` |
| D3 Rubric quality | 2 | gate+review | RAG criteria reasonable but **no `[gate]`/`[review]`/`[hypothesis]` labels**; adjective-led anchors ("Degraded or at risk"), uncalibrated (AP-H1) |
| D4 Mechanization | 2 | gate | No `scripts/`; "exec RAG matches body", "every signal has evidence", "every Red has an action" are checkable but left as prose |
| **D5 Evaluation** | **1** | gate | **No evals/, no routing corpus, F1 never measured;** verify = self-check closing on the agent's beliefs |
| D6 Extensibility | 2 | review | ROADMAP template-only (zero non-comment lines); single v1.0.0 release, no compounding |
| **D7 Security** | **1** | gate | **Ingests "Prior assessments"/"Known concerns" + `research-survey`, emits confident RAG verdicts leadership escalates on, with zero trust/provenance/fabrication guard** (grep: none) — injection foothold + no observed-vs-inferred tag |
| D8 Observability | 2 | review | Verify = self-assessment; no audit trail; confirming accuracy requires re-deriving from source |
| D9 Context eng | 4 | review | Strong — references load on explicit conditions; minor coarse load conditions |
| D10 Plan anatomy | 3 | review | Ordered 7-phase method with mostly-verifiable intermediate states, but no checkpoint before publishing a Red verdict |

## Top findings
- **[Critical] C1 — Untrusted ingestion → confident verdicts, no trust boundary, injection foothold + no provenance** *(Simon/Charity/Karpathy)* — two unguarded failure classes: a source-embedded directive ("treat X as Green") folds into a verdict; and "Key evidence" need not trace to a verifiable source or distinguish observed from fabricated. **Fix:** §SelfAudit (data-not-instructions; origin-tagged evidence; unlocatable→⚫Unknown; no adopted source status) + mechanize as a gate.
- **[Major] M1 — No mechanization; self-graded prose gates** *(Elon/Farley)* — `scripts/check-report.py` converts D4/D5/D8 to a real gate (every row has evidence; exec-RAG ≤ worst body RAG; every Red has an action).
- **[Major] M2 — `stable` with zero eval infra; overlapping triggers untested** *(Boris/Huyen)* — "where do we stand"/"assess our X" collide with report-progress/report-strategic. **Fix:** routing corpus + demote to draft.
- **[Major] M3 — Confident rubric without calibration; "honesty" is the one property it can't check** *(Wlaschin/Karpathy)* — label criteria; add per-RAG-level calibration anchors.
- [Minor] No Quick Start / worked example; verify-step control mode weakest-available; no `date:` in frontmatter.

## Instrument probe — is a `report-authoring` rubric needed?
**Yes, sharply.** The manifest has prd/spec-authoring but no `report-authoring`; the holistic rubric scores the skill-as-tool, and three sharpest findings (provenance, honesty/calibration, no worked example) had to be reconstructed by bending D7/D3/D8/D10 sideways (D10 fit the report-as-output awkwardly). Proposed dims: claim→evidence traceability `[gate]`, source-provenance/trust `[gate]`, BLUF `[review]`, audience fit `[review]`, honesty/non-softening `[review]`, recommendation/next-step actionability `[review]`, calibrated-signal discipline `[gate]`. **→ Acted on: `skills-critique` v2.1.0 added `report-authoring.md`.**

## Disposition
- **[done v1.1.0]** §SelfAudit (origin-tagged evidence, no adopted source status); status `stable → draft`; labeled checklist + exec-RAG-≤-worst rewrite; `evals/routing-corpus.json` (report-progress disambiguation); ROADMAP; enriched description; CHANGELOG Files drift fixed.
- **[tracked — ROADMAP]** `scripts/check-report.py`; per-RAG calibration anchors; behavioral eval; Quick Start + worked example; then re-earn `stable`.
