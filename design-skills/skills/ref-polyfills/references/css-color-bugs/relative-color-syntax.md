---
date: 2026-04-27
coverage: extended
peers:
  - ./oklch-oklab-safari.md
  - ./currentcolor-resolution.md
  - ../meta/the-modern-baseline.md
  - ../feature-detection/at-supports-recipes.md
primary_sources:
  - https://www.w3.org/TR/css-color-5/#relative-colors — CSS Color Module Level 5: relative colors
  - https://developer.chrome.com/blog/css-relative-color-syntax — Chrome blog (Adam Argyle), Nov 2023
  - https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_colors/Relative_colors — MDN guide
  - https://caniuse.com/css-relative-colors — caniuse browser-support matrix
  - https://caniuse.com/mdn-css_types_color_oklch_relative_syntax — caniuse: relative oklch specifically
  - https://ishadeed.com/article/css-relative-colors/ — Ahmad Shadeed: Relative Color Syntax (practical guide)
  - https://frontendmasters.com/blog/relative-color-syntax-basic-use-cases/ — Frontend Masters: practical use cases
  - https://bugs.webkit.org/show_bug.cgi?id=267647 — WebKit: relative color syntax should be unitless
---

# Relative color syntax — `oklch(from base ...)` at our baseline

## TL;DR

Relative color syntax — `oklch(from var(--brand) calc(l * 1.2) c h)` — derives a new color from an existing one by mathematical expressions on its components. **At our baseline (Chromium 125+, Safari 17.4+, Firefox 129+), it is universally supported and does not need a polyfill.** That said, there are three small interop edges to know about: (1) the canonical feature query is `@supports (color: rgb(from white r g b))` — don't reinvent it; (2) achromatic origin colors propagate `NaN` through hue calculations in some implementations; (3) calc() expressions inside relative color have had Chromium-specific bugs around unit handling that may still surface in older 125-series builds.

## What relative color syntax does

It lets you express a color as a transformation of another color, inside any CSS color function. The pattern:

```css
/* Pattern: <function>(from <origin-color> <expressions-using-component-letters>) */

/* OKLCH: l, c, h are made available */
:root {
  --brand: oklch(0.65 0.22 250);
  --brand-light: oklch(from var(--brand) calc(l + 0.15) c h);
  --brand-dark:  oklch(from var(--brand) calc(l - 0.15) c h);
  --brand-mute:  oklch(from var(--brand) l calc(c * 0.5) h);
  --brand-warm:  oklch(from var(--brand) l c calc(h - 30));
}

/* RGB: r, g, b, alpha are available */
.translucent { background: rgb(from var(--bg) r g b / 0.5); }

/* OKLAB: l, a, b */
.shifted { background: oklab(from var(--brand) l calc(a + 0.05) b); }

/* HSL: h, s, l */
.tweaked { background: hsl(from var(--accent) h calc(s - 10%) l); }
```

The component letters are bound to the origin color converted into the target color space. So `oklch(from #ff0000 ...)` first converts `#ff0000` to OKLCH (which is `oklch(0.628 0.258 29.23)`), then exposes `l = 0.628`, `c = 0.258`, `h = 29.23` for use in the expressions.

## Browser support at our baseline

| Engine | First version | Date | At baseline? |
|---|---|---|---|
| Chrome / Edge | 119 | November 2023 | Yes — our floor is 125 |
| Safari (Desktop & iOS) | 16.4 | March 2023 | Yes — our floor is 17.4 |
| Firefox | 128 | July 9, 2024 | Yes — our floor is 129 |

**Universally supported at our baseline.** caniuse-confirmed across all three engines as Baseline Newly Available since July 2024 (when Firefox 128 closed the gap).

No polyfill needed. There is also no production-quality polyfill *available*, because relative color syntax is not transformable at build time without losing its dynamic-recomputation behavior — `oklch(from currentColor ...)` and `oklch(from var(--theme-color) ...)` are core use cases, and a build-time pass would have to resolve those statically (defeating the purpose).

## Feature detection — the canonical query

```css
@supports (color: rgb(from white r g b)) {
  /* Relative color syntax is supported */
}
```

The reason this specific form is canonical:

- It uses the simplest origin color (`white`).
- It uses the most basic color function (`rgb`).
- It uses the simplest possible expression (just the bare component letters).
- All three engines parse and accept it correctly when relative color syntax is present, and reject it when not.

**Don't use `@supports (color: oklch(from white l c h))`** — engine support for the *function* (`oklch()`) and the *relative syntax* (`from`) advanced separately, and at the edges between, this query produced false positives or false negatives. The `rgb(from ...)` form is the recommended canonical detector per [the Chrome relative-colors blog post](https://developer.chrome.com/blog/css-relative-color-syntax) and most WebKit/Mozilla docs.

At our baseline, this query returns `true` everywhere; the feature gate is functionally a no-op. It is good practice to leave it in place anyway as documentation (so a reader knows the wrapped block is using relative color syntax).

## The achromatic NaN gotcha

When the origin color has zero chroma (white, black, gray), the **hue is powerless** — there is no meaningful angle for "the hue of pure white." The CSS Color spec says the hue value should be treated as `none` in this case, which propagates through `calc()` expressions as `NaN`.

```css
/* Origin is gray — h is powerless */
.bug {
  background: oklch(from gray l 0.2 calc(h + 30));
}
```

Different engines handle this differently:

- **Chrome / Safari**: `calc(NaN + 30)` resolves to `NaN`, and the resulting `oklch(... NaN)` clamps to `0` (per the CSS Color 4 powerless-component rules), giving a reddish (hue 30°) color rather than the expected "shifted gray."
- **Firefox**: Earlier versions (128–130) treated the missing hue as `0` from the start, producing a similar red-shifted result but via a slightly different code path.
- **All three**: Result is *not* "gray with chroma 0.2 at some plausible hue." It's typically something near hue 30° — usually red, often surprising.

If your relative color formula reads from an origin that *might* be achromatic (currentColor, theme-driven, user-customizable), guard the chroma path:

```css
/* Defensive: only use the hue from the origin if chroma is non-zero */
.safe {
  background: oklch(from var(--maybe-gray) l 0.2 calc(h + 30));
  /* Better: pin the hue explicitly and only derive l, c */
  background: oklch(from var(--maybe-gray) l 0.2 250);
}
```

Or use OKLab (rectangular, no hue, no powerless component):

```css
.safe-oklab {
  background: oklab(from var(--maybe-gray) l calc(a + 0.05) b);
}
```

This avoids the achromatic propagation issue entirely.

## Calc inside relative color — Chromium edge cases

There were several Chromium issues around `calc()` expressions inside relative color syntax shipping bugs in 119–123. As of Chrome 125 (our baseline), most of these are closed:

- **Unit-mixing in calc**: early Chrome 119 implementations choked on `calc(l + 10%)` (mixing unitless and percentage) — fixed by 122. Not relevant at our baseline.
- **Variable substitution in `from`**: `oklch(from var(--brand) ...)` worked from 119; the bug was around `var(...)` *inside* the expressions (e.g., `oklch(from var(--brand) calc(l * var(--scale)) c h)`), where Chrome had partial support until 124. Fixed by Chrome 125, which is our floor — proceed with confidence.
- **Whitespace in expressions**: `calc(l*1.2)` (no spaces) was rejected in some early Chrome builds. Fixed everywhere by mid-2024.

If you see relative-color expressions misbehaving in production at our baseline, the issue is almost always one of: (a) origin color is achromatic and you're propagating powerless hue (covered above), (b) you used the wrong feature-detection query, or (c) you have a stale `@supports` fallback that's overriding the modern declaration.

## Common patterns at our baseline

### Tonal scales from a single brand color

```css
:root {
  --brand: oklch(0.65 0.22 250);
}
.tone-50  { background: oklch(from var(--brand) 0.97 calc(c * 0.1)  h); }
.tone-100 { background: oklch(from var(--brand) 0.92 calc(c * 0.2)  h); }
.tone-200 { background: oklch(from var(--brand) 0.85 calc(c * 0.4)  h); }
.tone-300 { background: oklch(from var(--brand) 0.78 calc(c * 0.6)  h); }
.tone-400 { background: oklch(from var(--brand) 0.71 calc(c * 0.8)  h); }
.tone-500 { background: var(--brand); }
.tone-600 { background: oklch(from var(--brand) 0.58 calc(c * 1.05) h); }
/* etc. */
```

This is the canonical use case. With OKLCH's perceptual uniformity, walking `l` linearly produces visually-even tonal steps. Without relative color syntax, you'd have to compute these at build time.

### Hover/active state derivation

```css
.button {
  --bg: var(--brand);
  background: var(--bg);
  
  &:hover {
    background: oklch(from var(--bg) calc(l * 0.92) c h);
  }
  &:active {
    background: oklch(from var(--bg) calc(l * 0.84) c h);
  }
  &:disabled {
    background: oklch(from var(--bg) l calc(c * 0.3) h);
  }
}
```

Hover/active darken by lightness; disabled desaturates by chroma. All derived from a single source of truth.

### Border/text from background

```css
.surface {
  --bg: oklch(0.97 0.02 250);
  background: var(--bg);
  border: 1px solid oklch(from var(--bg) calc(l - 0.1) c h);
  color: oklch(from var(--bg) calc(l - 0.7) c h);
}
```

Borders pick up a slightly-darker version of the background; text picks up a much-darker version. Theme-friendly, brand-coherent, no token explosion.

## When NOT to use relative color syntax

- **When the derivation should be precomputed**: if the math is the same for every theme/scheme, computing at build time and emitting static custom properties is cheaper at runtime and works in 100% of browsers. Use relative color syntax when the *origin* changes at runtime.
- **When you need cross-browser-identical output**: see [`color-mix-interpolation.md`](./color-mix-interpolation.md). Relative color syntax shares some of the powerless-component edge cases that hue-interpolation has — Cartesian (`oklab(from ...)`) is more deterministic than polar (`oklch(from ...)`) for derivations that touch achromatic origins.
- **When the formula is hard to read**: `oklch(from var(--brand) calc(l - 0.15 + var(--theme-shift) * 0.05) calc(c * 0.85) calc(h + 12))` is hard to verify at a glance. Sometimes a build-time pipeline that spits out named tokens is clearer.

## Cross-references

- Safari < 18 OKLCH bug (separate issue; relative color is fine in Safari 16.4+): [`oklch-oklab-safari.md`](./oklch-oklab-safari.md)
- `currentColor` resolution timing (same surface area; affects relative color too): [`currentcolor-resolution.md`](./currentcolor-resolution.md)
- Baseline color-feature support: [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)
- Feature-query authoring patterns: [`../feature-detection/at-supports-recipes.md`](../feature-detection/at-supports-recipes.md)
