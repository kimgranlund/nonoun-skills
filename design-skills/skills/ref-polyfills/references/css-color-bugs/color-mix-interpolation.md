---
date: 2026-04-27
coverage: esoteric
peers:
  - ./oklch-oklab-safari.md
  - ./currentcolor-resolution.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://github.com/w3c/csswg-drafts/issues/10484 — "Should color-mix() default to oklab interpolation?" (the canonical CSSWG thread)
  - https://github.com/w3c/csswg-drafts/issues/9436 — "Does interpolation with achromatic colors truly have a 'longer' arc?"
  - https://github.com/w3c/csswg-drafts/issues/8609 — Powerless components in `white` — the spec ambiguity that drove engine divergence
  - https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/color-interpolation-method — MDN <color-interpolation-method>
  - https://www.w3.org/TR/css-color-4/#interpolation — CSS Color 4 interpolation rules
  - https://en.wikipedia.org/wiki/Oklab_color_space — Oklab definition
---

# Chrome ↔ Safari OKLCH hue-value divergence in `color-mix`

## TL;DR

Even after the Safari < 18 red-shift bug is fixed (see [`oklch-oklab-safari.md`](./oklch-oklab-safari.md)), `color-mix(in oklch, ...)` can still return materially different hue values across engines for the same inputs — particularly when one endpoint is achromatic (`white`, `black`, `gray`) or near-achromatic. This is rooted in spec ambiguity around powerless hue components and shorter-vs-longer hue arc resolution. **For cross-engine stability, use `color-mix(in oklab, ...)`** — Cartesian `(L, a, b)` interpolation is engine-agnostic by construction.

## The reproducible case

The Web Platform Tests group and several CSSWG-thread participants have collected a canonical example: mixing `white` and `blue` in `oklch`. Below is one of the snapshots from the [csswg-drafts thread](https://github.com/w3c/csswg-drafts/issues/8609) and surrounding bug reports.

| Input | Engine | Computed value |
|---|---|---|
| `color-mix(in oklch, white, blue)` | Chrome (V8/Blink) | `oklch(0.725987 0.15663 323.92)` |
| `color-mix(in oklch, white, blue)` | Safari (WebKit) | `oklch(0.72600687 0.15660721 177.02602)` |
| `color-mix(in oklch, white, blue)` | Spec-intended (csswg-drafts thread) | `oklch(72.601% 0.15661 264.052)` |

Lightness and chroma agree (lightness ~0.726, chroma ~0.157). The hue values **disagree by ~150°** — Chrome lands in magenta-red (323.92°), Safari in green (177°), and the spec-intended value sits in blue (264°). All three lightness/chroma pairs are functionally identical; the visible color is dictated entirely by the hue, and the hue value is wildly engine-dependent.

The visible result: the same CSS produces different colors. There is no "browser bug" in the engine-implementation sense — both engines are valid interpretations of an under-specified part of CSS Color 4. They are just incompatibly under-specified.

## Why this happens

The disagreement is rooted in two related spec ambiguities.

### Powerless hue components

CSS Color 4 §12.2 says: "If a component is missing (`none`) or *powerless* (e.g. hue when chroma is 0), it does not contribute to interpolation and the corresponding component of the resulting interpolated color is taken from the other operand." That covers `white` (which has chroma 0 in OKLCH) and `black`.

But the spec doesn't precisely define what "*does not contribute*" means once you re-cylindricalize the result. Engines diverge on:

- Should the missing hue be replaced with the other operand's hue **before** the polar interpolation, or **after**?
- If both endpoints are powerless on the same component, what's the result? (See [csswg-drafts #8609](https://github.com/w3c/csswg-drafts/issues/8609).)
- For `white` mixed with `blue`, Chrome's pipeline arrives at one hue normalization; Safari's arrives at another. Both are arguably-correct readings of the spec.

### Shorter-vs-longer arc when one operand is hueless

CSS Color 4 says hue interpolation defaults to **shorter hue** — take the smaller arc between the two hue angles. But `white`'s hue is *powerless*, not *defined as some specific angle*. If you treat white's hue as "blue's hue" before interpolating, the shorter arc is degenerate (both endpoints at the same angle); if you treat it as "0°", the shorter arc to blue's ~265° is around the long way. Chrome and Safari's choices differ here. See [csswg-drafts #9436](https://github.com/w3c/csswg-drafts/issues/9436) for the CSSWG resolution attempt.

## The fix that the spec is converging on

The CSSWG is moving toward making **oklab the default interpolation space** for `color-mix` (and gradients), per [issue #10484](https://github.com/w3c/csswg-drafts/issues/10484). Reasoning:

1. OKLab uses **Cartesian** `(L, a, b)` coordinates. There is no hue, so there's no shorter-vs-longer arc question, no powerless-component ambiguity.
2. The interpolated path is a **straight line through OKLab space** — perceptually uniform, stable across engines, and produces the visually-cleanest gradient between two saturated colors that are not on the same hue ray.
3. Engine implementers agree: there is one correct answer to "interpolate `(L₁, a₁, b₁)` with `(L₂, a₂, b₂)` linearly," and they all compute the same one.

The CSSWG has not yet published a final resolution, but the trajectory is clear and several major frameworks (Tailwind v4, see [PR #15201](https://github.com/tailwindlabs/tailwindcss/pull/15201)) have already migrated.

## What to do today

### Use `oklab` for cross-browser stability

```css
/* Predictable across Chrome, Firefox, Safari 17.4+, all touched OS versions */
background: color-mix(in oklab, var(--brand) 50%, transparent);
border-color: color-mix(in oklab, currentColor, white 30%);
```

### Use `oklch` only when you actively want hue arc interpolation

```css
/* You want a hue rotation across the color wheel — oklch is correct here */
.hue-rotation {
  background: linear-gradient(in oklch, red, blue);
}
```

### Avoid implicit interpolation across achromatic operands

These are the cases where engines disagree most:

```css
/* AVOID — engine-dependent hue value */
color-mix(in oklch, white, blue)
color-mix(in oklch, blue, transparent 50%)
color-mix(in oklch, gray, red)

/* PREFER — engine-agnostic */
color-mix(in oklab, white, blue)
color-mix(in oklab, blue, transparent 50%)
color-mix(in oklab, gray, red)
```

### When `oklch` is unavoidable

If you genuinely need polar interpolation (e.g., a designed hue-shift across a brand ramp), nail down the hue arc explicitly:

```css
color-mix(in oklch shorter hue, oklch(0.7 0.2 30), oklch(0.7 0.2 290));
color-mix(in oklch longer hue, oklch(0.7 0.2 30), oklch(0.7 0.2 290));
```

This eliminates the shorter-vs-longer ambiguity and forces engines to take the same arc. It does not fix the powerless-component case — for that, only Cartesian (oklab/lab) interpolation is bulletproof.

## At our baseline

Chromium 125+, Safari 17.4+, and Firefox 129+ all support `color-mix` and all support both `oklab` and `oklch` interpolation methods. The hue-value divergence above persists at the baseline — it is not a polyfill candidate, it is a build-time recommendation:

> Default to `in oklab`. Reach for `in oklch` only when you know you want polar interpolation and your input pairs are not achromatic.

## Cross-references

- Safari < 18 red-shift (related, distinct bug — Safari-only): [`oklch-oklab-safari.md`](./oklch-oklab-safari.md)
- `currentColor` resolution timing in `color-mix`: [`currentcolor-resolution.md`](./currentcolor-resolution.md)
- Baseline color-function support: [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)
