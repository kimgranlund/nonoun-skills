# Worked example — a 2XL button on COMPOSE × REALIZE

A complete DECOMPOSE → fix → GRADE for one button, showing the **B1 geometry gate** catching an
off-law padding and the red→green proof. The two example specs in this folder are checked in and the
geometry engine actually verifies them.

## The artifact

A 2XL button with `[ icon · label · caret ]`. The designer hand-set the inline paddings to **18px on
both sides** — symmetric, which *looks* tidy.

## DECOMPOSE

**A · Compose** (whole → part)
- **A1 Layer** `[gate]` — a **component** (a named, skinned widget). ✓
- **A2 Anatomy** `[gate]` — parts `icon · label · caret`, the eight-permutation box model. ✓
- A3–A5 — `variant`/`size` enums, composes as a select trigger / menu item, fits the library. (reviewed below)

**B · Realize** (part → whole)
- **B1 Geometry** `[gate, code]` — run the engine on the spec (`examples/button-2xl.red.json`):

```
$ python3 bin/geometry-check.py validate examples/button-2xl.red.json
geometry-check: FAIL (1)
  - x-button[2XL]: pad_trail=18, law gives 23
```

**Gate fails.** The law is *every glyph centers in a square cell of side = the button height*, so the
edge padding is `(height − glyph) / 2`. The caret side must be `(64 − 18)/2 = 23`, not 18. The
symmetric 18/18 ignores that the caret (18px) is smaller than the icon (28px) — the asymmetry isn't
a choice, it's arithmetic. A failed `[gate]` blocks the B-axis reviews (B2–B5): no point grading
SSR or theming on a box that's off the ramp.

## Fix

Set the caret-side padding to the derived value (`examples/button-2xl.green.json`: `pad_trail: 23`,
and the pill `radius_px: 32 = height/2`):

```
$ python3 bin/geometry-check.py validate examples/button-2xl.green.json
geometry-check: OK — 1 spec(s) match the ramp
```

The icon side stays 18 (= `(64 − 28)/2`), which is *also* exactly the symmetric padding an icon-only
2XL button would use — confirming the same law makes an icon-only button square.

## GRADE — two scores, never averaged

- **Compose: 5/5** — right layer, named anatomy, orthogonal enums, composes upward, coherent.
- **Realize: gate-fail → (after fix) 5/5** — B1 was the only blocker; with the padding on the law,
  B2 (autonomous element) / B3 (ElementInternals role) / B4 (APG keyboard + forced-colors) / B5
  (SSR/theming) all clear.

**Quadrant:** the red spec sat in **"clean API, dead/off control"** (Compose passed, Realize failed
on geometry) — *designed right, built wrong*. The fix is geometry, not API. After it: **SHIPPABLE**.

The lesson: the dimensional defect is invisible to a sympathetic read ("18/18 looks balanced") and
caught deterministically by the law in code — *computation routes to code, never inference.*
