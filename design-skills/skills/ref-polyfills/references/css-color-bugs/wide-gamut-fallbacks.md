---
date: 2026-04-27
coverage: extended
peers:
  - ./display-p3-firefox-lag.md
  - ./relative-color-syntax.md
  - ../meta/the-modern-baseline.md
  - ../feature-detection/at-supports-recipes.md
primary_sources:
  - https://webkit.org/blog/10042/wide-gamut-color-in-css-with-display-p3/ — WebKit blog: Wide Gamut Color in CSS with Display-P3
  - https://web.dev/articles/color-spaces-and-css — web.dev: Color spaces and CSS (Adam Argyle, Una Kravets)
  - https://developer.mozilla.org/en-US/docs/Web/CSS/@media/color-gamut — MDN: color-gamut media feature
  - https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/color_value/color — MDN: color() function
  - https://www.w3.org/TR/css-color-4/#predefined — CSS Color 4: predefined color spaces
  - https://www.w3.org/TR/css-color-4/#gamut-mapping — CSS Color 4: gamut mapping algorithm
  - https://drafts.csswg.org/css-color-4/#css-gamut-mapping — Editor's Draft: gamut mapping
  - https://bugzilla.mozilla.org/show_bug.cgi?id=1626624 — Mozilla bug: Firefox display-p3 rendering
---

# Wide-gamut color fallbacks — the progressive-enhancement pattern

## TL;DR

Layer P3 colors on top of an sRGB baseline using `@supports (color: color(display-p3 0 0 0))`. This works at our baseline (Chromium 125+, Safari 17.4+, Firefox 129+) — although Firefox renders the P3 declaration as gamut-mapped sRGB rather than wide gamut (see [`display-p3-firefox-lag.md`](./display-p3-firefox-lag.md)). Avoid `@media (color-gamut: p3)` as the gating mechanism because Firefox always returns false there. Prefer `color()` over `oklch()` when you specifically need explicit P3 — `oklch()` is perceptual but its rendering goes through gamut-mapping at the engine, whereas `color(display-p3 ...)` is the colorspace-explicit form.

## The canonical pattern

```css
.brand {
  background: #1a73e8;                                  /* sRGB fallback */
}

@supports (color: color(display-p3 0 0 0)) {
  .brand {
    background: color(display-p3 0.1 0.45 0.91);        /* P3 enhanced */
  }
}
```

Behavior at the baseline:

| Engine | Sees `@supports` | Sees `color(display-p3 ...)` | Renders as |
|---|---|---|---|
| Chrome 111+ on P3 display | true | parses, uses | wide gamut |
| Chrome 111+ on sRGB display | true | parses, uses | gamut-mapped to sRGB |
| Safari 15+ on P3 display | true | parses, uses | wide gamut |
| Safari 15+ on sRGB display | true | parses, uses | gamut-mapped to sRGB |
| Firefox 113+ on P3 display | true | parses, uses | gamut-mapped to sRGB *(see `display-p3-firefox-lag.md`)* |
| Firefox 113+ on sRGB display | true | parses, uses | sRGB |
| Older browsers | false | not used | sRGB fallback |

The key insight: in Firefox, the `@supports` query returns `true` even though the actual rendering doesn't honor wide gamut. **This is fine** — Firefox's gamut-mapping result is roughly equivalent to what your sRGB fallback would have been anyway (the rendering pipeline ends at sRGB regardless). What matters is that Chrome and Safari users on capable hardware get the wide-gamut result, and everyone else gets a usable sRGB result.

## Why not `@media (color-gamut: p3)`?

This was the originally-recommended pattern:

```css
/* AVOID — broken in Firefox */
.brand {
  background: #1a73e8;
}

@media (color-gamut: p3) {
  .brand {
    background: color(display-p3 0.1 0.45 0.91);
  }
}
```

Three problems:

1. **Firefox always reports false** for `(color-gamut: p3)`, even on P3 hardware ([`display-p3-firefox-lag.md`](./display-p3-firefox-lag.md), MDN BCD issue #21422). Firefox users on P3 displays never get the P3 branch.

2. **It gates on display capability, not engine capability.** A user on Chrome with an sRGB-only display gets the sRGB fallback. That's "correct" in one sense (the display can't show wide gamut), but it forecloses future improvements when the user upgrades hardware. With `@supports`-based gating, the same user gets the P3 declaration; the engine gamut-maps it to sRGB at render time, and if they later get a P3 display, the rendering improves automatically.

3. **`@supports` is more composable.** You can combine `@supports (color: color(display-p3 ...)) and (color: oklch(0 0 0))` to gate on multiple modern features in one block. `@media (color-gamut: p3)` doesn't compose with feature queries cleanly.

The legacy recommendation appears in older WebKit docs (the [Wide Gamut Color in CSS with Display-P3](https://webkit.org/blog/10042/wide-gamut-color-in-css-with-display-p3/) blog post from 2020), which predated wide `@supports` support for color-function detection. Treat that recommendation as obsolete.

## `color(display-p3 ...)` vs `oklch(...)` — when to pick which

These are different tools:

### `color(display-p3 r g b)` — colorspace-explicit

- Specifies a color in **the actual P3 gamut**, with `r`, `g`, `b` as P3 primaries.
- The color is *natively a P3 color*; the engine's job is to render it on whatever display is available.
- On P3 displays: rendered at full gamut.
- On sRGB displays: gamut-mapped to sRGB.
- Use when you have a specific P3 RGB triple you want to render as-is — typically a designer's pick from a P3-aware tool.

### `oklch(L C H)` — perceptual

- Specifies a color in OKLCH, a perceptual color space.
- The color is then *converted* into whatever color space the engine wants to render in.
- For colors inside sRGB: rendered as sRGB.
- For colors outside sRGB but inside P3: rendered as P3 *if the engine supports it* (Chrome and Safari yes; Firefox flattens to sRGB).
- For colors outside P3: gamut-mapped down.
- Use when you want perceptual uniformity (e.g., visually-even tonal scales). The wide-gamut benefit is a side effect.

### Comparison

```css
/* Both produce a saturated red */
.color-fn  { background: color(display-p3 1 0 0); }
.oklch-red { background: oklch(0.628 0.259 30); }
```

In practice these render very similarly on P3-capable hardware. The semantic difference matters for theme systems:

- `color(display-p3 ...)` is **stable** — the color value is exactly that P3 triple, always.
- `oklch(...)` is **derivable** — you can manipulate it via `oklch(from ... calc(l * 1.2) c h)` to produce tonal scales, hover states, etc.

So you'll often see both in the same system: `oklch()` for tokens you want to manipulate, `color(display-p3 ...)` for fixed brand-specific accents.

## Combined pattern — sRGB → P3 enhancement with feature query

The full production-ready stack:

```css
:root {
  /* Tier 1: sRGB fallback (universal) */
  --brand:    #1a73e8;
  --brand-fg: #ffffff;
}

@supports (color: color(display-p3 0 0 0)) {
  :root {
    /* Tier 2: P3 enhancement when engine supports color() function */
    --brand:    color(display-p3 0.1 0.45 0.91);
    --brand-fg: color(display-p3 1 1 1);
  }
}

@supports (color: oklch(0 0 0)) {
  :root {
    /* Tier 3: perceptual color when oklch() is supported (universal at our baseline,
       but useful for projects with floors below ours) */
    --brand-hover: oklch(from var(--brand) calc(l * 0.92) c h);
  }
}
```

At our baseline, all three tiers fire; the cascade produces the most-modern values. For projects with floors below ours, the tiers degrade gracefully.

## Verifying gamut at the dev side

To test that your P3 color is *actually* being rendered as wide gamut (and not gamut-mapped):

1. **Use a P3-capable display** — modern MacBook Pro / iMac / iPhone / iPad screens since ~2017 are P3.
2. **Open in Safari or Chrome** — Firefox flattens, so test elsewhere first.
3. **Compare side by side** — render `#ff0000` and `color(display-p3 1 0 0)` in adjacent swatches. On a P3 display, the latter should look noticeably more saturated. If they look identical, gamut-mapping is happening (either because the engine doesn't support P3 rendering for this surface, or the display is sRGB-only).
4. **Use Safari's Inspector → Color Picker** to examine. Safari shows the actual rendered color values, including whether the result is in P3 or sRGB.

## Token export from design tools

Modern design tools (Figma, Sketch, Adobe XD) increasingly support P3 color picking. When you export tokens:

- **Figma's `Display P3` mode** exports tokens as `color(display-p3 r g b)` (after Figma's June 2024 P3 export support).
- **CSS variables from Tailwind v4** include both sRGB and P3 forms in the generated `@theme` block.
- **Hand-authoring**: pick the sRGB equivalent first, then bump saturation to taste in the P3 form. The relationship is not linear — a "perceptually equivalent" P3 color is often slightly less saturated in P3 coordinates than you'd think.

## At our baseline

- `color()` function: universal at our baseline (Chrome 111+, Firefox 113+, Safari 15+).
- `@supports (color: color(display-p3 0 0 0))`: returns `true` at all three engines.
- Wide-gamut *rendering*: Chrome and Safari on capable displays. **Firefox renders gamut-mapped to sRGB regardless** — see [`display-p3-firefox-lag.md`](./display-p3-firefox-lag.md).
- `@media (color-gamut: p3)`: works in Chrome and Safari; broken in Firefox. **Don't use as a gate.**

The progressive-enhancement pattern with `@supports` is correct and bulletproof at our baseline.

## Cross-references

- The Firefox-specific gamut bug: [`display-p3-firefox-lag.md`](./display-p3-firefox-lag.md)
- Relative color syntax (often used with wide-gamut tokens): [`relative-color-syntax.md`](./relative-color-syntax.md)
- Baseline color-feature support: [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)
- Feature-query authoring patterns: [`../feature-detection/at-supports-recipes.md`](../feature-detection/at-supports-recipes.md)
