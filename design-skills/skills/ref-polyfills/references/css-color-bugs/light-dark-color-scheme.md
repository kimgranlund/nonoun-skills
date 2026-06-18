---
date: 2026-04-27
coverage: esoteric
peers:
  - ../meta/the-modern-baseline.md
  - ../feature-detection/at-supports-recipes.md
primary_sources:
  - https://www.w3.org/TR/css-color-5/#light-dark — CSS Color Module Level 5: light-dark() definition
  - https://drafts.csswg.org/css-color-5/#light-dark — Editor's Draft
  - https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/color_value/light-dark — MDN reference
  - https://web.dev/articles/light-dark — web.dev: CSS color-scheme-dependent colors with light-dark()
  - https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme — MDN: color-scheme property
  - https://css-tricks.com/almanac/functions/l/light-dark/ — CSS-Tricks almanac entry
  - https://www.edge-cases.com/css/css-light-dark-function — EdgeCases: gotchas writeup
---

# `light-dark()` silently no-ops without `color-scheme`

## TL;DR

`light-dark(white, black)` always returns `white` (the first argument) **unless** the relevant element — typically `:root` — has `color-scheme: light dark` declared. There is no warning, no console message, no `@supports` failure. It just silently uses the light value forever, even when the user prefers dark mode. This is **per spec** — it's not an engine bug — but it is the single most-asked "why isn't my dark mode working" question on the modern web. Document it here so anyone searching for the bug lands on the answer.

## The minimum-correct setup

```css
:root {
  color-scheme: light dark;          /* REQUIRED for light-dark() to work */
}

body {
  background: light-dark(white, black);
  color: light-dark(black, white);
}
```

Without the `color-scheme: light dark` declaration:

- Browser defaults to "light" used color scheme.
- `light-dark(white, black)` resolves to `white`.
- `light-dark(black, white)` resolves to `black`.
- Page is permanently in light mode regardless of OS preference.

## Why the spec works this way

`light-dark()` does not read `prefers-color-scheme` directly. It reads the **used color scheme** of the element where it appears, which is determined by the [`color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme) property. The chain:

1. The CSS `color-scheme` property declares which schemes the element is willing to use (`normal`, `light`, `dark`, `light dark`, `only light`, etc.).
2. The browser picks one as the **used color scheme** based on user preference *intersected* with the element's declared willingness.
3. `light-dark()` looks at that used color scheme and returns argument 1 (light) or argument 2 (dark).

If `color-scheme` is not set, the element defers to the page's UA default — which is `normal`, treated as light. The user's `prefers-color-scheme: dark` does not override `normal`; it can only steer the picker when both `light` and `dark` are in the willingness list.

This is intentional. The spec's authors wanted authors to opt in to dark scheme support explicitly — partly so that legacy pages with hardcoded white backgrounds and black text don't suddenly become unreadable when a user's OS theme is dark, and partly because dark mode often requires more than just color swaps (image filters, semi-transparent surfaces, focus styling). Forcing an explicit `color-scheme` declaration is the spec's way of making the author confirm they've thought about it.

Spec section: [CSS Color Module Level 5 §4.7 — light-dark()](https://www.w3.org/TR/css-color-5/#light-dark).

## Reproduction

The bug: this looks like it should work and doesn't.

```html
<!DOCTYPE html>
<html>
  <style>
    /* No color-scheme declared anywhere */
    body {
      background: light-dark(white, black);
      color: light-dark(black, white);
    }
  </style>
  <body>
    Hello — am I light or dark?
  </body>
</html>
```

Expected (incorrect intuition): "the browser uses my OS preference."
Actual: always white-on-black, regardless of `prefers-color-scheme`.

The fix:

```html
<style>
  :root {
    color-scheme: light dark;       /* THIS LINE */
  }
  body {
    background: light-dark(white, black);
    color: light-dark(black, white);
  }
</style>
```

Now the page tracks `prefers-color-scheme` correctly.

## Adjacent gotchas

### `color-scheme` cascades

`color-scheme` is inherited. If you set `color-scheme: light` on an element somewhere down the tree (intentionally or not), every `light-dark()` inside that subtree returns the light value, even when the rest of the page is in dark mode.

```css
:root { color-scheme: light dark; }      /* whole page tracks pref */
.legal-document { color-scheme: light; } /* this subtree forced light */
```

This is sometimes useful — print stylesheets, embedded payment iframes, and content that simply hasn't been audited for dark mode legibility benefit from being pinned. It's also a bug source when you do it accidentally.

### `<meta name="color-scheme">` is the HTML alternative

You can set it via HTML instead of CSS. Either is fine; pick one and stick with it.

```html
<meta name="color-scheme" content="light dark">
```

This sets the equivalent of `color-scheme: light dark` on `:root`. Some hand-coded sites prefer this because the browser knows about the scheme before any CSS loads (faster initial-paint correctness for scrollbar/form-control colors).

### Forced colors mode wins

When the user is in Windows High Contrast / forced-colors mode, `light-dark()` resolves are overridden by system colors (`Canvas`, `CanvasText`, etc.). This is correct — forced-colors users want platform colors, not your dark theme. Just be aware that `light-dark()`'s value is not load-bearing in forced-colors environments.

```css
@media (forced-colors: active) {
  /* light-dark() is being overridden — your colors are not honored here.
     Use system colors directly for any contrast-load-bearing styling. */
}
```

### `@supports (color: light-dark(...))` can return false-positives in older Chromium

A small implementation quirk: in Chrome 122–124 betas, `@supports (color: light-dark(red, blue))` returned `true` even when `light-dark()` was behind a runtime flag. Stable Chrome 123+ honors it correctly. Not load-bearing at our baseline (Chromium 125+, Safari 17.4+, Firefox 129+); flagged only because legacy build pipelines may have inherited a feature-query gate that no longer needs guarding.

### Both arguments must be `<color>` types

`light-dark()` takes exactly two `<color>` arguments. Custom properties resolve, but a missing or non-color value is a parse error and the whole declaration drops. There's no "missing" sentinel.

```css
/* OK */
color: light-dark(var(--text-light), var(--text-dark));

/* INVALID — you cannot use light-dark() with images, gradients, fonts, etc. */
background-image: light-dark(url(light.png), url(dark.png));   /* won't parse */
```

For non-color media-conditional values, use `prefers-color-scheme` directly:

```css
@media (prefers-color-scheme: dark) {
  body { background-image: url(dark.png); }
}
```

## Why this is in the bug catalog despite being spec-defined

It is a correctness-via-omission failure mode that no warning system surfaces:

- The CSS does not throw.
- DevTools shows `light-dark(...)` resolving to a `<color>`.
- The Computed pane shows the right value-type.
- It just always picks the light branch.

The path from observation ("dark mode not working") to root cause (`color-scheme: light dark` is not on `:root`) is unguided. Documenting it as a bug-catalog entry — even if the spec is correct — is the high-impact disambiguation.

## At our baseline

`light-dark()` is Baseline since Safari 17.5 / Firefox 120 / Chrome 123. Our baseline is Safari **17.4**, which is one minor version below — verify your iOS user mix. For the rest, `light-dark()` is universally usable. The `color-scheme` property has been universal since 2022 (Chrome 81, Firefox 96, Safari 13).

There is **no polyfill** for `light-dark()`. The fallback pattern is `prefers-color-scheme`-based:

```css
:root {
  /* Fallback */
  --bg: white;
  --fg: black;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: black;
    --fg: white;
  }
}

@supports (color: light-dark(white, black)) {
  :root {
    color-scheme: light dark;
    --bg: light-dark(white, black);
    --fg: light-dark(black, white);
  }
}
```

This double-layered approach is overkill at our baseline (Safari 17.4 supports `light-dark()` per BCD with one minor caveat); listed here for posterity for projects with floors below ours.

## Cross-references

- Baseline color-function support: [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)
- Feature-query patterns: [`../feature-detection/at-supports-recipes.md`](../feature-detection/at-supports-recipes.md)
