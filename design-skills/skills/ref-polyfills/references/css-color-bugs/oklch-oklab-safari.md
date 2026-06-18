---
date: 2026-04-27
coverage: esoteric
peers:
  - ./color-mix-interpolation.md
  - ./currentcolor-resolution.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://github.com/tailwindlabs/tailwindcss/pull/15201 — Tailwind v4 PR switching color-mix from oklch to oklab (merged Nov 27, 2024)
  - https://github.com/tailwindlabs/tailwindcss/discussions/15184 — original Tailwind discussion that surfaced the bug
  - https://github.com/w3c/csswg-drafts/issues/10484 — CSSWG issue "Should color-mix() default to oklab interpolation?"
  - https://bugs.webkit.org/show_bug.cgi?id=255939 — WebKit Bugzilla: (OK)LCH implementation is not according to spec
  - https://webkit.org/blog/15865/webkit-features-in-safari-18-0/ — Safari 18.0 release notes (Sept 16, 2024)
  - https://developer.apple.com/documentation/safari-release-notes/safari-18-release-notes — Apple's Safari 18.0 release notes
---

# Safari < 18 OKLCH `color-mix` red-shift bug

## TL;DR

In Safari Desktop versions before 18.0 (released **September 16, 2024**), `color-mix(in oklch, ...)` interpolates as if the polar conversion were happening in CIE LCH space rather than OKLCH. The visible effect: mixing any color with `transparent` or with a gray tone produces a noticeably red/purple-shifted intermediate, instead of the perceptually-clean transition OKLCH is supposed to provide. Use `color-mix(in oklab, ...)` instead — it sidesteps the bug entirely because oklab uses Cartesian coordinates and doesn't go through hue interpolation at all.

## What's actually wrong

The OKLCH color space is the cylindrical (polar) form of OKLab — the same `L` axis but `(C, h)` polar coordinates instead of `(a, b)` Cartesian. To interpolate two OKLCH colors, an engine must:

1. Convert each color to `(L, C, h)` triples.
2. Interpolate `L` and `C` linearly.
3. Interpolate `h` along the shorter arc (default).
4. Convert the resulting triple back to OKLab → linear sRGB → display.

Safari's implementation prior to 18.0 used the same code path as `lch()` (CIE LCH) interpolation when it received an `oklch` interpolation method — different white point, different chroma normalization, and (most visibly) different powerless-component handling. The downstream effect when you fade toward `transparent`:

- Spec behavior: `transparent` is treated as `oklch(0 0 0 / 0)` and the hue is powerless, so the start color's hue is preserved through the fade.
- Safari < 18: hue normalization differs, and a missing/zero chroma component gets reinterpreted via the LCH path, which lands in a hue region that — once converted back to sRGB — sits in the red/purple corner of the gamut. So fading a blue to transparent passes through reddish purple.

Tracking bug: [WebKit Bugzilla 255939](https://bugs.webkit.org/show_bug.cgi?id=255939) — "(OK)LCH implementation is not according to spec." Closed as fixed in Safari 18.0.

## Reproduction

Drop this into a test page and view in Safari 17.x vs Chrome/Firefox/Safari 18+:

```html
<style>
  .swatch { width: 200px; height: 60px; display: inline-block; }
  .a { background: oklch(0.5 0.2 250); }
  .b { background: color-mix(in oklch, oklch(0.5 0.2 250) 50%, transparent); }
  .c { background: color-mix(in oklab, oklch(0.5 0.2 250) 50%, transparent); }
</style>
<div class="swatch a">solid blue</div>
<div class="swatch b">in oklch → transparent (broken in Safari < 18)</div>
<div class="swatch c">in oklab → transparent (correct everywhere)</div>
```

In Safari 17.4–17.x, `.b` renders with a visibly purple/magenta cast. In Safari 18+, Chrome 111+, and Firefox 113+, `.b` and `.c` look near-identical (a half-opacity blue).

The same artefact appears with grays:

```css
/* Safari < 18: passes through reddish purple */
background: color-mix(in oklch, oklch(0.5 0.2 250), oklch(0.5 0 0));

/* Cross-engine consistent */
background: color-mix(in oklab, oklch(0.5 0.2 250), oklch(0.5 0 0));
```

## Cross-engine reference table

For input `color-mix(in oklch, oklch(0.5 0.2 250) 50%, transparent)`:

| Engine | Result | Visual |
|---|---|---|
| Chrome 111+ | `color-mix` resolves to ~`oklch(0.5 0.2 250 / 0.5)` | Half-opacity blue, hue preserved |
| Firefox 113+ | Same as Chrome | Half-opacity blue |
| Safari Desktop **< 18.0** | Hue rotates toward red/purple during interpolation | Purplish, visibly off |
| Safari Desktop **≥ 18.0** | Matches Chrome/Firefox | Half-opacity blue |
| iOS Safari | Tracks Safari version (locked to OS); iOS 17.x affected, iOS 18.x fixed | Same fix point as Desktop |

Note on iOS: the prompt's original brief flagged "NOT iOS Safari" — that is incorrect. WKWebView and Mobile Safari ship the same WebKit build as Desktop Safari for the matching OS version. iOS 17.x devices are **affected** by this bug exactly like Safari Desktop 17.x.

## The fix at the project level

This is exactly the situation `color-mix(in oklab, ...)` exists to handle. OKLab uses Cartesian `(L, a, b)` coordinates, so:

- There is no hue interpolation, no shorter-arc-vs-longer-arc ambiguity.
- A `transparent` argument resolves to `oklab(0 0 0 / 0)` and contributes zero to both `a` and `b`. The interpolated path stays on a straight line through the perceptual color space.
- The Safari < 18 code path that mishandles powerless hue components never runs.

The Tailwind v4 fix is [PR #15201](https://github.com/tailwindlabs/tailwindcss/pull/15201) (merged November 27, 2024 by Adam Wathan). It rewrites every internal `color-mix` call from `in oklch` to `in oklab`, including the gradient utilities. The trade-off Wathan documents: oklab gradients between two saturated, non-gray colors look slightly muddier than oklch gradients (because the path goes through the rectangular interior of the chroma plane rather than around the hue circle). Tailwind v4 exposes `bg-linear-to-r/oklch` modifier syntax for opt-in oklch when you specifically want the polar path.

## When to keep using oklch anyway

`color-mix(in oklch, ...)` is the right choice when:

- Both endpoints are saturated colors with similar lightness (no gray, no transparent).
- You actively want hue arc interpolation — e.g., a hue-rotation gradient through an entire color wheel.
- Your support floor is Safari 18.0+ and you're not seeing red-shift on transparent fades.

Use `oklab` when any of:

- Either endpoint is `transparent`, gray, or has near-zero chroma.
- You need cross-engine identical output and your floor includes Safari 17.x.
- You're computing semantic alpha overlays (the entire `color-mix(..., transparent)` family).

## At our baseline

Our floor is Safari **17.4+**. Safari 17.4–17.6 are **affected**; Safari 18.0+ is **clean**. Until Safari 17.x falls out of the support window (typically when iOS 17.x users have rolled forward to iOS 18+, currently ~6–9 months further out), prefer `oklab` for any `color-mix` that touches transparency or grays. This is a default-good substitution: `oklab` is also the CSSWG's proposed default for `color-mix` interpolation per [csswg-drafts issue #10484](https://github.com/w3c/csswg-drafts/issues/10484).

## Cross-references

- Cross-engine OKLCH hue divergence (a different but related bug): [`color-mix-interpolation.md`](./color-mix-interpolation.md)
- Why `currentColor` interacts oddly with these mixes: [`currentcolor-resolution.md`](./currentcolor-resolution.md)
- Baseline definitions: [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)
