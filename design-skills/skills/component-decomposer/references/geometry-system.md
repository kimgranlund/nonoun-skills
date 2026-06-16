# The geometry system — one law, a six-step ramp, everything derived

This is the deterministic foundation of the **Realize** axis (level B1). The button is the base
unit; input, select, menu-item, tab, badge, tag, and container insets all derive from it. The whole
system is governed by **one law** and a small ramp of **free values** — everything else is computed,
and `bin/geometry-check.py` is the source of truth (this file documents what the code computes; the
code's `selftest` proves it against the hand-authored table).

> Run it: `python3 bin/geometry-check.py ramp` · `… layout XL icon,label,caret` · `… validate card.json`

## The law

> **Edge padding for any glyph = (height − glyph) / 2.**
> Every glyph (icon or caret) is centered in a **square cell** of side = the button height.

Two consequences fall straight out of the law — they are the system, not conventions bolted on top:

1. **An icon-only (or caret-only) button is exactly square** — `width == height`. The glyph centers
   in its square cell; there is nothing else in the box.
2. **The asymmetric inline padding is forced, not chosen.** Because the icon and the caret are
   *intentionally different sizes*, the icon side gets `(h − icon)/2` and the caret side gets
   `(h − caret)/2`. The caret is smaller, so the caret side is more padded — the imbalance you see is
   the law, not a fudge factor.

This is why the only **free** per-size design decisions are five numbers: **height, icon, caret,
font, spacer**. Pick those; the paddings, the squareness, the pill radius, and the composed insets
are all computed.

## The canonical ramp (free values)

| size | height | icon | caret | font | spacer |
|------|-------:|-----:|------:|-----:|-------:|
| 2XL  | 64 | 28 | 18 | 20 | 8 |
| XL   | 48 | 24 | 16 | 18 | 8 |
| LG   | 36 | 20 | 14 | 16 | 8 |
| MD   | 28 | 18 | 14 | 14 | 4 |
| SM   | 24 | 16 | 12 | 13 | 4 |
| XS   | 20 | 14 | 12 | 12 | 4 |

Notes on the shape of the ramp (so you can extend or retune it coherently):
- **Icons shrink slower than height** — the icon/height ratio climbs from 0.44 (2XL) to 0.70 (XS):
  small controls keep a legible glyph. The caret is always smaller than the icon at the same size.
- **Spacer is a two-value split**: `8` for the large tiers (height ≥ 36 / font ≥ 16), `4` for the
  tight tiers. It is the gap flanking the label and between adjacent glyphs.

## The derived ramp (computed by the law)

| size | pad-icon `(h−icon)/2` | pad-caret `(h−caret)/2` | radius-pill `h/2` | inset `=pad-caret` | gap `=spacer` |
|------|-----:|-----:|-----:|-----:|-----:|
| 2XL  | 18 | 23 | 32 | 23 | 8 |
| XL   | 12 | 16 | 24 | 16 | 8 |
| LG   | 8  | 11 | 18 | 11 | 8 |
| MD   | 5  | 7  | 14 | 7  | 4 |
| SM   | 4  | 6  | 12 | 6  | 4 |
| XS   | 3  | 4  | 10 | 4  | 4 |

`pad-icon` and `pad-caret` are the icon-side and caret-side inline paddings. `pad-label` (text at an
edge) takes the generous caret-side value. All are integers at every canonical size because the
heights and glyph sizes share parity — a property worth preserving if you add a size.

## The box model & permutations

Layout is `display: flex` with `justify-content: space-between` and the `spacer` as the gap flanking
the label. Reading left → right, the full pattern is:

```
| pad-lead | glyph | spacer | label (fills) | spacer | glyph | pad-trail |
```

The lead/trail paddings come from whichever slot sits at that edge (icon → pad-icon, caret →
pad-caret, label → pad-label). The label takes the remaining space and **text-aligns by what flanks
it**:

| permutation | label text-align | why |
|---|---|---|
| `icon · label · caret` | **center** | flanked on both sides |
| `icon · label` | **end** (right) | neighbour only on the left |
| `label · caret` | **start** (left) | neighbour only on the right |
| `label` | **center** | alone |
| `icon` | center (square) | single glyph, no label |
| `caret` | center (square) | single glyph, no label |
| `caret · label` | **end** | neighbour only on the left |
| `caret · label · icon` | **center** | flanked on both sides |

Rule, stated once: **label flanked both sides → center; only-left → end; only-right → start;
alone/absent → center.** (`label_justify()` in the engine; verified against all eight above.)

Worked example — `2XL · icon · label · caret` (matches the hand-authored spec exactly):
```
| 18 pad | icon 28 | 8 spacer | label(fill) | 8 spacer | caret 18 | 23 pad |
```
Worked example — `MD · icon` (icon-only → square):
```
| 5 pad | icon 18 | 5 pad |   →  width == height == 28
```

## Radius

- **Pill (default for the chip/button family)** = `height / 2` — fully rounded; the geometric
  default the system computes (`radius-pill` column).
- **Soft / sharp** radii are a *brand* choice layered on top, not a geometric law. A defensible soft
  ramp (tunable): 2XL 20 · XL 16 · LG 12 · MD 10 · SM 8 · XS 6. Keep one radius scale per library and
  re-point it with a token; don't set radius per component instance.

## Badges & tags — a smaller scale of the same system

A badge or tag is **a button at a reduced scale**: the same box model and the same `(h − glyph)/2`
law, shifted down the ramp (a "MD" badge uses the geometry of an SM/XS button) and usually pill, with
no caret. Don't invent a parallel geometry — map the badge's size onto the button ramp and inherit
every derived value. An icon-only badge is still square.

## Composed padding — containers & lists

> **Containers and lists use the same inside padding for contained sections.** Nesting reuses the
> same `inset`, so boundaries visibly "compose" (stack) — that is the intended look, not a bug.

- A container/section at size *S* uses inner padding = **`inset[S]`** (= the caret-side pad at *S*).
- The gap between gridded/listed items = **`gap[S]`** (= the spacer at *S*).
- A contained control (e.g. an icon-button in a grid) keeps its own square geometry; the container's
  inset sits *around* it. Two nested sections at the same size therefore show `inset + inset` of
  breathing room at their shared edge — the "Composed Padding" effect.

This is what lets a button, the cell it sits in, the section that holds the cells, and the card that
holds the section all share one coherent rhythm with no magic numbers.

## How it lands in the signals/CSS idiom

The reference libraries (`fable-tests/reactive-components`, `adia/gen-ui-kit`) express this ramp as
**CSS custom properties keyed by a `size` / `scale` attribute**, with components reading the tokens —
never hard-coding pixels. The geometry stays declarative and themeable:

```css
/* size ramp as tokens (illustrative — values from the ramp above) */
:where([scale="xl"]) {
  --c-height: 48px; --c-icon: 24px; --c-caret: 16px; --c-font: 18px; --c-spacer: 8px;
}
/* the law, expressed once, reused by every control */
:where(x-button) {
  --c-pad-icon:  calc((var(--c-height) - var(--c-icon))  / 2);
  --c-pad-caret: calc((var(--c-height) - var(--c-caret)) / 2);
  block-size: var(--c-height);
  border-radius: calc(var(--c-height) / 2);            /* pill */
  padding-inline: var(--c-pad-icon) var(--c-pad-caret);
  display: flex; align-items: center; justify-content: space-between; gap: var(--c-spacer);
}
:where(x-button):is([icon-only], :not([label])) {     /* single glyph -> square */
  inline-size: var(--c-height); padding-inline: 0; justify-content: center;
}
```

Properties (`size`, `icon`, `label`, `caret`) are **signals** on the element; the geometry is pure
CSS driven by the reflected `scale`/`size` attribute, so a size change is one attribute write and
zero layout JS. See `platform-baseline.md` for the element/FACE side.

## Verifying geometry

- `python3 bin/geometry-check.py validate card.json` against a declared spec:
  ```json
  { "component": "x-button", "size": "XL", "slots": ["icon","label","caret"],
    "height": 48, "icon": 24, "caret": 16, "pad_lead": 12, "pad_trail": 16,
    "justify": "center", "radius": "pill", "radius_px": 24 }
  ```
  The checker fails any value that's off the ramp, any edge padding that breaks the law, a wrong
  label justification, or a glyph-only spec that isn't square.
- The most common geometry defects (all caught): a glyph-only button that isn't square; a symmetric
  inline padding (ignoring icon ≠ caret); a hard-coded radius instead of `height/2`; a container
  inset that doesn't match the size's `inset`; a label justification that doesn't follow the flank
  rule.
