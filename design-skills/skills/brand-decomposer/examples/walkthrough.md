# Walkthrough — grading two brand specs, then critiquing work against one

Two cards ship with the skill: `docusign.green.brand.json` (a complete, operable spec) and
`acme.red.brand.json` (a degraded one that lands in both defect quadrants). Both are the bin's own
fixtures, written to disk so you can run every command below.

## 1 · GRADE the green spec — DocuSign

### Outside-in (operability) — run the gate first

```sh
python3 bin/brand-spec-check.py lint examples/docusign.green.brand.json
# brand-spec-check: OK — operability gates clear (well-formed, traced, accessible, complete);
#                   the meaning axis is judged separately
```

B1–B3 gates green: every token/rule is typed with `severity ∈ {must,should,may}`, carries `evidence[]`
+ `confidence`, declares a `truth`; the one `color_pair` (`#130032` on `#ffffff`) clears AA at 19.56:1.
B4: all six domains covered, five surfaces enumerated. **Axis B = 5.**

### Inside-out (meaning) — the rubric, then refute the idea

- **A1 idea** — *"agreements are dynamic moments of connection, not static documents — make the moment
  of agreement feel like forward progress."* Not interchangeable adjectives (`GENERIC_IDEA` clean). It
  *forces* downstream choices. **Gate clear.**
- **A2 chain** — `idea→voice→mark→color→type→layout→imagery→apps` (8 links). Each link is forced: the
  idea → voice rule `voice.active` ("active progress, never document management") → color rule
  `color.activation` ("activation accent, not full-field"). **Gate clear.**
- **A3–A5 rubric** — voice/mark/color/type each carry a reason; one example shows the activation
  principle on product-UI; governance has a partner-approval `must`. Rubric ≈ 86/100 → **A = 4.**
- **Adversarial refutation** (fresh context): *could a competitor copy-paste "agreements are dynamic
  moments of connection"?* No — it is specific to an agreements product. *Does the chain force the
  primitives?* Yes — color/voice rules derive from the idea. **Survives → not hollow.**

**Verdict:** A = 4, B = 5, zero gate failures → **SHIPPABLE**. Two scores, never averaged.

## 2 · GRADE the red spec — Acme (both defects at once)

```sh
python3 bin/brand-spec-check.py lint examples/acme.red.brand.json
# brand-spec-check: FAIL (7)
#   - Acme: GENERIC_IDEA — brand_idea is only interchangeable adjectives/filler ('Modern, bold, and simple.') …
#   - Acme: UNTRACED — rule 'r1' has no evidence[] …
#   - Acme: LOW_CONFIDENCE — inferred rule 'r1' at 0.60 (< 0.75) not marked review (B2 gate …)
#   - Acme: COLLAPSED_TRUTH — rule 'r2' truth 'guess' not one of observed/inferred/proposed (B2 gate)
#   - Acme: rule 'r2' severity 'loud' not in ['may', 'must', 'should']
#   - Acme: UNTRACED — token 'color.brand' has no evidence[] …
#   - Acme: CONTRAST_FAIL — pair 'grey on white' 2.64:1 below AA 4.5 …
#   ⚠ meaning_chain has 2 links · BARE_TOKEN (color.brand value, no role+meaning)
#   ⚠ INCOMPLETE (mark/expression/governance; no surfaces)
```

Note `LOW_CONFIDENCE` and `COLLAPSED_TRUTH` are **B2 gate FAILS**, not advisories — an unflagged weak
inference or a collapsed truth reads as a settled rule, the exact trust defect the three-truths model
exists to stop. (`GENERIC_IDEA` is caught even with a filler noun — `"…simple solutions"` doesn't
escape; only a *concrete* subject does.)

- **Axis B fails outright** — `UNTRACED`, `LOW_CONFIDENCE`, `COLLAPSED_TRUTH`, malformed `severity`,
  `CONTRAST_FAIL` are B1–B3 gate failures. The spec is not operable: an agent cannot trust or cite it.
  **B = 1.**
- **Axis A also fails** — `brand_idea` is *"Modern, bold, and simple."* → `GENERIC_IDEA` (A1 gate). A
  competitor could copy-paste it; the two-link chain (`idea→color`) does not propagate. **A = 1.**

**Verdict:** broken on both axes — the *start-over-from-the-idea* quadrant. Note the value of scoring
separately: a spec can fail B while A is fine (a sharp idea trapped in untyped prose = **beautiful but
unusable**) or pass B while A fails (a perfectly typed token system around a generic idea = **operable
but hollow**). Acme manages both.

### The contrast joint, directly

```sh
python3 bin/brand-spec-check.py contrast "#9aa0a6" "#ffffff"     #   2.64:1  (AA floor 4.5 — FAIL)
python3 bin/brand-spec-check.py contrast "#130032" "#ffffff"     #  19.56:1  (AA floor 4.5 — PASS)
```

The `--json` form (`lint … --json`) emits the shared `{tool, ok, summary, findings[]}` report for
piping into a harness.

## 3 · The operable-but-hollow quadrant — why the gate is *necessary, not sufficient*

Acme fails both axes loudly. The dangerous case is quieter: a brand that is **fully operable yet
hollow** (high B, low A). `empower.hollow.brand.json` is exactly typed, traced, accessible, complete,
and band-coherent — so it passes **every mechanizable gate clean**:

```sh
python3 bin/brand-spec-check.py lint examples/empower.hollow.brand.json
# brand-spec-check: OK — operability gates clear (well-formed, traced, accessible, complete);
#                   the meaning axis is judged separately       (--json: 0 findings, ok:true → B = 5)
```

But read the idea: *"Empowering people to do their best work."* Any SaaS company could copy-paste it.
The voice rule is only adjectives ("clear, friendly, human"); the meaning chain lists `idea→voice→mark→
color→type` but no link is *forced* by the idea. The gate cannot see any of this — `GENERIC_IDEA` only
catches *pure* adjective/filler salad, and "empowering / best / work" reads as substantive. **This is
the whole point of the skill.** Run the **adversarial idea-refutation** (a skeptic in a fresh context):

- *Could a competitor copy-paste this idea?* Yes → **fails A1.**
- *Does each chain link force its primitive?* No — "clean modern sans because it's readable" is
  decorative → **the chain is hollow.**
- *Is the voice a behavior or adjectives?* Adjectives → **fails A3.**

**Verdict:** B = 5, A = 1 → **operable but hollow** — the quadrant a green gate hides. A spec can reach
this state and *pass the bin completely*; only the axis-A refutation catches it. That is why the skill
**scores the two axes separately** and why a clean `brand-spec-check` run is **necessary, not
sufficient**: it proves the brand is *operable*, never that it is *good*.

## 4 · CRITIQUE work against the validated DocuSign spec

CRITIQUE requires a spec that **passes the gate** — DocuSign does, Acme does not (so critiquing against
Acme would be ungrounded). Suppose the work is a campaign hero that paints the whole viewport in the
primary indigo with the headline *"Manage your documents efficiently."*

**Ungrounded (never do this):** "This feels off-brand, make it bolder."

**Grounded — name the mechanism, cite the spec:**

| Field | Finding |
|---|---|
| **tension** | The hero uses the primary as a full-field background, but `color.activation` (should) documents it as an *activation accent*, not a base. *(color role)* |
| **tension** | "Manage your documents efficiently" is static document-management language; `voice.active` (should) calls for active agreement *progress*. *(voice behavior)* |
| **severity** | both `should` (flexible-but-documented) — not `must`; flag, don't block |
| **evidence** | spec rules `color.activation`, `voice.active` (both `truth: inferred`, confidence 0.80–0.85) · the observed hero |
| **recommended move** | reduce indigo to a highlight; let `color.surface` carry the base. Rewrite to a direct agreement-progress outcome ("Get to signed in minutes"). *(proposed)* |
| **review_flag** | the inferred rules sit at 0.80–0.85 — strong, not explicit; if the campaign is high-stakes, confirm against the source deck |

The critique separates **observed** (the hero), **the spec** (the cited rules), and **proposed** (the
moves) — and never says "off-brand" without naming the mechanism. For other directions, move along a
documented axis (*premium restraint ↔ campaign loudness*), not random variety. See
`references/critique-mode.md`.
