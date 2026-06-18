# viz-2x2 — Holistic 10-dim + adversarial critic pass (2026-05-31)

**Method:** one **fresh-context** subagent (blind), which **ran the live gates** (score-routing,
metadata) to verify claims. **Target:** viz-2x2 v1.1.0 (`status: stable`, 209-line SKILL.md).

## Verdict — 4/5; **CLEAN — does NOT clear the "≥1 Critical or ≥2 Major" bar** (0 Critical, 1 Major).

The first genuinely clean skill of the campaign — a focused, disciplined 2×2-diagram generator with
**excellent context engineering (D9=5)**, correct control-mode design (D2=5), and — contrary to the
inert-corpus hypothesis — **a real, scored, regression-gated routing eval (D5=4)**: the agent executed
`score-routing.py viz-2x2` → F1 **0.72**, committed in `routing-baselines.json`, run by
`run-skill-gates.py`. Reported honestly as clean; no Critical manufactured.

| Dim | Score | Finding |
|---|---|---|
| D1 Harness | 4 | Pass — no §SelfAudit (low-cost here) |
| D2 Control mode | 5 | Pass — layout=procedure, axis-discovery=judgment w/ a falsifiable test |
| D3 Rubric quality | 3 | Minor — Quality checklist unlabeled (mechanical vs judgment items mixed) |
| D4 Mechanization | 3 | Minor — chart-coordinate math (`y=94-(pct/100)*82`) is mechanize-bait; a ~30-line `chart_path.py` would zero it |
| D5 Evaluation | 4 | Pass — **routing corpus is live + CI-gated** (F1 0.72); behavioral corpus has no runner (the −1) |
| D6 Extensibility | 2 | Minor — template-only ROADMAP |
| D7 Security | 4 | Pass — minimal untrusted surface (visualizes user prose; JS-free static HTML); near-N/A |
| D8 Observability | 2 | **Major** — verify = self-assessed checklist on the agent's own artifact |
| D9 Context eng | 5 | Pass — textbook minimum-effective-dose loading |
| D10 Plan anatomy | 4 | Pass |

**Single Major (Boris/Karpathy):** the generated 2×2 **validates against nothing** — the Quality checklist
is self-assessed, and the mechanizable items (SVG-coordinate bounds, CSS-vars-only, OG-tags-present) are
left as eyeball checks. The author mechanized + CI-gated *routing* but not the *artifact*. Severity Major,
not Critical — blast radius is one cosmetically-wrong diagram a human sees immediately.

**Minors:** CHANGELOG malformed (two "v1.1" headings + a stale File-Inventory footer); eval corpora
self-version `0.1.0` vs skill `1.1.0`; empty ROADMAP; the ASCII wireframe duplicates the invariants table (~25 trim-able lines).

## Fixes (light — it's a clean skill)
- **[done]** Populate `ROADMAP.md` (D6) with the tracked items.
- **[tracked]** A ~30-line `scripts/validate_2x2.py` (SVG-coordinate bounds + CSS-var/OG-tag grep) to turn
  the artifact checklist from belief into a `[gate]` (closes the lone Major + D4/D8); label the Quality
  checklist `[gate]`/`[review]`; reconcile the CHANGELOG/eval version drift.

## Disposition
ROADMAP populated this pass; the artifact-validator + label items tracked. **No Critical — the skill is
sound;** these are polish items, not blockers.
