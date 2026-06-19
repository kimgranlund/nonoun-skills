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

---

# Worked example 2 — a toolbar+overflow on COMPOSE × REALIZE (the composition scale)

The same two-axis split applied one tier up — **how components nest + wire**. Here A4's **seam gate**
catches a fake overflow, the way B1's geometry gate caught the off-law padding above.

**Artifact.** A header toolbar — six action buttons in a row, and at the far right a `···` button that
opens a menu listing "Cut / Copy / Paste". At 1200px all six buttons show; at 600px the last two clip
off the edge. The `···` menu always lists the same three items regardless of width.

## Compose (whole → part)

- **A1 Layer / A4 Tier `[gate]` — component.** On the **primitive → component → module** ladder it's a
  **component**: it composes primitives (`x-button`s, an `x-menu`) and adds a seam. Not a primitive (it
  composes), not a module (no regions, no cross-component state). ✓
- **A2 Anatomy / A4 Boundary `[gate]` — one toolbar.** `toolbar → [ action-group(button×6) · spacer ·
  overflow-trigger → menu(item×3) ]`. One cohesive unit — not a god-component, not scatter. ✓
- **A4 Composition — the SEAM `[gate, code]` — FAIL.** The overflow is **not a seam**. The inline
  buttons (six, fixed) and the `···` menu (three, hardcoded) are **two hand-kept lists**, not one action
  list projected. The `···` is decorative — overflowing buttons *clip*, they don't *collapse into* the
  menu. → **BLOCKED.**
- **A5 Coherence `[review]` — 5.** No outer margin; it sits in the header region it's handed (the app
  shell hands up to layout-decomposer).

```
$ composition-check.py lint toolbar.composition.json
  ERROR a horizontal axis carries 6 actions but declares no overflow mechanism —
        it will clip or wrap; declare a priority-overflow seam (A4 / REALIZE B4)
```

## Realize (part → whole)

- **B1–B3 — cite the leaves.** `x-button` / `x-menu` have clean single-component contracts (geometry on
  the ramp, FACE, APG keyboard) — **cited, not re-graded**. ✓
- **B3 cross-component state — the defect.** The overflowed set must be *derived* from available width
  against a single priority-ordered action list, projected into both the inline group and the menu. Here
  it's **authored twice** — the cross-component state defect.

## Verdict

- **Quadrant: built right, designed wrong (at A4).** The boundaries are clean (Compose A1/A2 pass) but
  the A4 *seam* gate fails — the overflow is a static decoration, the actions are authored twice. It
  *looks* composed and *breaks* the moment width varies — **boxed but inert**.
- **The one fix (A4 seam + B3 state).** Derive the overflowed set from width against one priority-ordered
  action list; project the *same* list into the inline group and the overflow menu — the buttons that
  don't fit *become* the menu items, and every action stays reachable.

The lesson mirrors example 1: a beautifully-bounded toolbar with a fake overflow is caught by the
**composition card gate** the way an off-ramp padding is caught by the **geometry gate** — the
mechanizable joint routes to code, the two axes are scored separately, and the quadrant names exactly
which half to fix.
