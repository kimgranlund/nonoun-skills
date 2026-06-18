---
name: color-verifier
description: Generate, extend, and verify OKLCH color ramps and semantic mappings that satisfy contrast, hue-stability, and perceptual-evenness constraints. Use when the user needs to build a ramp from a brand anchor, extend an existing palette to a full scale, assign semantic roles, or verify that a proposed palette holds up under every (theme × scheme × contrast) combination — including contrast ratios, WCAG/APCA pass-fail, and color-blind (CVD) safety. NOT for focus order, keyboard nav, or focus-ring contrast (focus-verifier); NOT for RTL/bidi, locale Intl formatting, or text-expansion (i18n-verifier); NOT for loading skeleton/spinner, CLS, or perceived-latency budgets (perf-verifier); NOT for destructive-action undo/type-to-confirm or audit-trail UX (safety-verifier); NOT for color-space theory or palette/harmony math (color-science); NOT for building a color-picker or swatch component (component-decomposer).
---

# color-verifier

Content skill that owns the **how** of color in ui-dev. Upstream schemas say what color roles exist; this skill derives the actual numeric OKLCH steps and proves they behave.


## Invocation

This is a **constraint** decomposition skill. The user needs a ramp, a palette extension, or a verification. Decompose: (1) specify the contrast/hue/perceptual requirements, (2) compute OKLCH values, (3) assign semantic roles, (4) verify under every (theme × scheme × contrast) combination.

### Step 1 — Ingestion

Classify the ask surface:
- "Build a ramp from anchor" → needs brand anchor hue + target step count
- "Extend existing palette" → needs current palette + target coverage
- "Assign semantic roles" → needs UI surface list (button, surface, text, etc.)
- "Verify palette" → needs candidate palette + target themes/schemes to verify

### Step 2 — Decomposition

| Sub-ask | What it derives | Constraint |
|---|---|---|
| Lightness step spacing | Perceptual evenness across ramp | JND ≥ 2 between adjacent steps |
| Hue stability | Chroma → hue shift at low L | Anchor hue preserved within ±5° |
| Contrast pairs | Every foreground/background pair | APCA Lc + WCAG 2.2 AA floor |
| Gamut safety | P3 vs sRGB boundaries | Clamp to gamut; flag out-of-gamut |
| Semantic role assignment | UI role → ramp step | Role contrast must hold under all themes |
| Theme × scheme verification | Light/dark variant generation | All pairs must satisfy floor |

### Step 3 — Execution routing

If a brand anchor cannot produce a full ramp while holding perceptual evenness, flag a `DecompositionGap` for the user to pick a different anchor. APCA is the modern design standard; WCAG 2.2 is the legal floor. Every derived value must carry provenance (source schema, computation method).


## When to use

- A BrandSchema exists with anchor colors but no full ramp.
- A UISchema has `primitive.color` scales to fill.
- User wants to add an intent color (danger/warning/success/info) that is perceptually consistent with the existing palette.
- User wants a contrast-conformance proof for a candidate palette.
- Dark-scheme companion palette needs to be derived from a light one.

## When NOT to use

- User is picking a single color for a one-off element → they don't need a ramp, just pick.
- User wants to override a specific token → edit UISchema directly, no ramp logic needed.
- Pure art direction decisions (vibe, mood) → BrandSchema / `ui-schema-brand`.

## Rate-limiting factor

**Perceptual consistency under OKLCH is a constrained-optimization problem, not a free choice.** Given anchors + constraints (contrast floor, chroma ceiling, hue stability), only a narrow corridor of valid ramps exists. This skill's job is to find that corridor, not to invent freely.

## First principles

1. OKLCH separates lightness, chroma, and hue perceptually — so ramps that vary L while holding H (and optionally C) are perceptually coherent.
2. WCAG contrast depends on sRGB luminance, not OKLCH L. So hitting a contrast target requires measuring contrast in sRGB even when you author in OKLCH.
3. Gamut matters. Not every (L, C, H) triple maps to sRGB. Out-of-gamut triples must be chroma-reduced — by policy, **never lightness-reduced** — to preserve ramp spacing.
4. Perceptual evenness of a ramp is measured by ΔL between adjacent steps — not by visual judgment.
5. Intent colors (danger, warning, success, info) are semantic, not free — their hue ranges are culturally load-bearing.

## Procedure

### Step 1 — Establish the ramp skeleton

For each color family the UISchema declares (e.g. `neutral`, `accent`, `danger`):

- Step count: read from UISchema.primitive.color.scale (default 11: `0, 50, 100..900, 1000`).
- Lightness anchors:
  - Step `0`:    L ≈ 0.99
  - Step `50`:   L ≈ 0.97
  - Step `100`:  L ≈ 0.94
  - Step `500`:  L ≈ 0.60–0.65 (the "brand step" when the family has an anchor)
  - Step `900`:  L ≈ 0.20
  - Step `1000`: L ≈ 0.12
- Interpolate remaining Ls linearly between anchors.

### Step 2 — Place the anchor

If the family has a stated brand anchor (e.g. `accent-500 = oklch(0.62 0.18 270)`), its actual L overrides step 500's ideal L. Re-interpolate the ramp so ΔL between adjacent steps varies ≤ 20%.

### Step 3 — Chroma curve

Chroma follows a bell curve across lightness:

```
C(L) = C_max × exp(−k × ((L − L_peak)²))
```

- `C_max` from the anchor's chroma (or brand ceiling).
- `L_peak` typically 0.60 for accents (mid lightness), 0.70+ for pastels, 0.50 for darker jewel tones.
- `k` tuned so extremes (L < 0.15, L > 0.95) have C < 0.02 (near-neutral at the ends).

Neutral family: C is 0..0.02 across all steps (optionally a tiny chroma tint toward the brand accent for warmth).

### Step 4 — Hue stability

Default: hue is constant across the ramp. Allow ±8° of hue drift only when necessary for gamut — and only toward the next-neighbor hue (e.g., a blue ramp may drift toward cyan at high L, never toward green).

### Step 5 — Gamut mapping

For each generated (L, C, H) triple:

- Check if in sRGB gamut. If yes, keep.
- If no, reduce C in steps of 0.005 until in gamut. **Do not touch L.**
- Record the reduction in the token's provenance (`gamut-reduced: ΔC = 0.015`).
- If reduction exceeds 0.05 to get into gamut, the anchor itself is out-of-gamut — flag and ask the user to adjust.

### Step 6 — Semantic mapping

Map ramp steps to semantic roles per UISchema:

- `--surface`:            neutral-50 (light) / neutral-950 (dark)
- `--surface-raised`:     neutral-0  (light) / neutral-900 (dark)
- `--surface-sunken`:     neutral-100 (light) / neutral-1000 (dark)
- `--on-surface`:         neutral-900 (light) / neutral-50 (dark)
- `--on-surface-muted`:   neutral-700 (light) / neutral-300 (dark)
- `--border`:             neutral-200 (light) / neutral-800 (dark)
- `--border-strong`:      neutral-400 (light) / neutral-600 (dark)
- `--accent`:             accent-500
- `--on-accent`:          neutral-0 or neutral-1000 (whichever clears contrast)
- `--focus-ring`:         accent-500 (or accent-600 in light, accent-400 in dark)

These defaults are starting points — UISchema can override. The skill NEVER invents new semantic roles.

### Step 7 — Contrast verification

For every semantic pair that carries text or focus indication:

- Convert each side to sRGB.
- Compute WCAG 2.2 relative luminance.
- Compute ratio.
- Verify against UISchema.accessibility.contrastFloor:
  - AA normal text: ≥ 4.5
  - AA large text: ≥ 3.0
  - AAA normal: ≥ 7.0
  - UI components / focus rings: ≥ 3.0

If any pair fails:

- First attempt: swap to the next-neighbor ramp step (e.g., `--on-surface-muted` from neutral-700 → neutral-800). Retain.
- Second attempt: widen the lightness anchor for that role.
- Third attempt: refuse and hand a DecompositionGap back to the forward workflow.

### Step 8 — Dark-scheme derivation

When UISchema requires a dark scheme:

- Mirror L: `L_dark = 1 − L_light` for neutrals.
- For accents: flip the L around 0.55 (so accent-500 at L=0.62 becomes accent-500-dark at L=0.48), preserve hue, slightly reduce chroma by 10–15% (dark surfaces hide chroma less — reducing C avoids glow).
- Verify every dark-scheme pair against the same contrast floor.

### Step 9 — Emit

Each token carries:

```ts
{
  name: "--color-accent-500",
  oklch: { L: 0.620, C: 0.180, H: 270.0 },
  srgb:  "#4A5CFF",
  gamutReduced: false,
  provenance: { source: "derived", from: "accent anchor" },
  contrastPairs: [
    { against: "--surface", ratio: 4.82, target: 4.5, pass: true }
  ]
}
```

## Mechanism gate — `bin/contrast-check.py`

WCAG contrast is **arithmetic**, not a matter of taste — so the contrast floor is **routed to code, never to inference**. An LLM judging "looks readable" fails silently exactly where a pair lands a few hundredths under 4.5:1. CVD safety and perceptual evenness, by contrast, are perceptual judgments and **stay a review** in this skill (Step 2 decomposition, the anti-patterns list).

`python3 bin/contrast-check.py <card.json | dir>` reads a **color surface card** — the foreground/background pairs that carry text or UI indication — and flags any pair below its AA floor:

```json
{ "pairs": [
  {"name": "body text",   "fg": "#1a1a1a", "bg": "#ffffff", "size": "normal", "role": "text"},
  {"name": "muted label", "fg": "#767676", "bg": "#ffffff", "size": "normal", "role": "text"},
  {"name": "card border", "fg": "#949494", "bg": "#ffffff",                    "role": "ui"}
]}
```

Per pair (only `fg` + `bg` required): `name` (report label), `fg`/`bg` (`#rgb`, `#rrggbb`, or `rgb()/rgba()` — rgba alpha is ignored; a malformed color is a clear per-pair error, not a crash), `size` (`normal` default | `large`), `role` (`text` default | `ui`/non-text). For each pair it computes the WCAG 2.x ratio (sRGB → linearized relative luminance → `(L1+0.05)/(L2+0.05)`) and emits:

- **`CONTRAST_FAIL_AA`** *(gate, exit 1)* — text below **4.5** (normal) / **3.0** (large); ui/non-text below **3.0**.
- **`CONTRAST_FAIL_AAA`** *(advisory WARN)* — text below **7.0** (normal) / **4.5** (large), only when the pair already clears AA. (No AAA tier for graphics — WCAG 1.4.11 keeps the ui floor at 3.0.)

`--json` emits a machine-readable report. The gate is a **lossy pre-filter, not an oracle**: a clean run proves the arithmetic floor holds — it does **not** prove the palette CVD-safe or perceptually even, which is why those remain reviews. `python3 bin/contrast-check.py selftest` exits 0, locked by good + bad fixtures (the `#777` ≈ 4.48 near-miss, a 3:1-as-normal-text fail, `#767676` ≈ 4.54 AA-pass, a 3:1 pair passing as `large`/`ui`, malformed colors, and the verified `#777777` on `#ffffff` ≈ 4.48:1 ratio math).

## Invariants

1. **L monotonic across the ramp.** Step N's L < Step N+1's L (dark-to-light convention).
2. **Hue stable or drifting ≤ 8° toward next neighbor.**
3. **Gamut reduction is C-only, never L.**
4. **Every contrast-bearing semantic pair is verified.** No unverified pairs emitted.
5. **Ramp steps are perceptually even** — no adjacent-ΔL ratio above 1.5 (excluding the 0↔50 and 950↔1000 end pairs).
6. **Neutral chroma never exceeds 0.02.** Or exactly zero if UISchema declares `neutral: true-grey`.
7. **Dark-scheme chroma is reduced by 10–15% vs light.**


- **INV-COL-001** — Every proof cites specific schema paths or CSS rules it evaluates (enforcement: convention)
- **INV-COL-002** — Remediation suggestions are scoped to the schema/artifact that can fix them (enforcement: convention)

## Typed Interface

**Domain:** `ui-design`

**Consumes:** Relevant schemas and artifacts.

**Produces:** `ColorProof` — constraint-satisfaction proof or violation report.

**Invariants:** Evaluations cite schema paths or CSS rules; remediation suggestions scoped to fixable artifact.

**Downstream:** `ui-audit-quality`.

## Anti-patterns this skill refuses

- Using HSL/HSV to generate the ramp (perceptually misleading).
- "Shade by multiplying RGB values by a scalar" (destroys hue and contrast).
- Hard-coding hex values without OKLCH provenance.
- Introducing new semantic roles (e.g., `--primary-alt-subtle-hover`) — semantics are owned by UISchema.
- Emitting a pair without a contrast number.
- Reducing lightness (instead of chroma) to solve gamut overflow.
- Using the same hue across all intent colors (danger + success + warning + info must each occupy a distinct hue region).

## Handoff

- `ui-build-tokens` consumes the emitted OKLCH tokens as primitives.
- `ui-build-theme` uses the ramp when emitting theme variants and prefers-contrast escalations.
- `ui-audit-quality` re-runs the contrast verification independently as a check.
- `ui-decomp-legacy` produces observed palette data this skill can extend into full ramps.

## Bundled reference files

- `ramps/neutral-curve.json` — default L-anchor grid and chroma ceilings for neutral families.
- `ramps/accent-curve.json` — L anchors and chroma-bell parameters for accent families.
- `ramps/intent-hues.json` — canonical hue ranges for danger/warning/success/info and the ±tolerance.
- `verification/contrast-pairs.json` — the authoritative list of semantic pairs that must be verified and their targets.
