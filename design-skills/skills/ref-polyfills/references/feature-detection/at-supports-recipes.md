---
date: 2026-04-27
coverage: canonical
peers:
  - ../feature-detection/js-feature-detection.md
  - ../feature-detection/progressive-enhancement.md
  - ../feature-detection/ponyfill-pattern.md
  - ../meta/decision-tree.md
  - ../meta/the-modern-baseline.md
  - ../css-color-bugs/relative-color-syntax.md
  - ../anchor-positioning-quirks/inset-area-rename.md
  - ../css-polyfills-and-shims/anchor-positioning-polyfill.md
primary_sources:
  - https://developer.mozilla.org/en-US/docs/Web/CSS/@supports — `@supports` at-rule reference
  - https://drafts.csswg.org/css-conditional-5/ — CSS Conditional Rules Module Level 5 (selector(), font-tech(), font-format(), at-rule())
  - https://drafts.csswg.org/css-conditional-3/ — CSS Conditional Rules Module Level 3 (the @supports baseline)
  - https://www.bram.us/2023/01/04/css-has-feature-detection-with-supportsselector-you-want-has-not-has/ — `:has()` feature-query gotcha
  - https://www.bram.us/2026/03/15/at-rule/ — `@supports at-rule(@keyword)` shipping in Chromium 148
  - https://caniuse.com/mdn-css_at-rules_supports_font-tech — caniuse for `font-tech()`
  - https://groups.google.com/a/chromium.org/g/blink-dev/c/AzUM6sVsjBc — Intent to Ship: `font-tech()` / `font-format()`
---

# `@supports` recipes

The CSS feature-query at-rule is the **first tool to reach for** before any CSS polyfill. At our baseline, `@supports` plus a flat fallback solves most of the surface that pre-2024 codebases polyfilled. The browser tells you what it has — you don't guess via UA strings or ship a runtime shim.

## The four condition forms

```css
/* 1. property-value pair */
@supports (display: grid) { ... }

/* 2. selector — needs the selector() function form */
@supports selector(:has(*)) { ... }

/* 3. font tech / format */
@supports font-tech(color-COLRv1) { ... }
@supports font-format(woff2) { ... }

/* 4. at-rule (CSS Conditional 5; Chromium 148+ only at this baseline) */
@supports at-rule(@scope) { ... }
```

Forms 1 and 2 are universal at our baseline. Form 3 is widely available (Chrome 102+, Firefox 108+, Safari 17+). Form 4 is brand-new: `@supports at-rule(@keyword)` ships in Chromium 148 and is not yet in Safari or Firefox stable as of April 2026 — treat it as advisory.

## Combinators: `not`, `and`, `or`

```css
/* not — reverse detection for fallbacks */
@supports not (display: grid) {
  .layout { display: flex; flex-wrap: wrap; }
}

/* and — composite conditions */
@supports (display: grid) and (gap: 1rem) {
  .layout { display: grid; gap: 1rem; }
}

/* or — accept either spelling */
@supports (display: grid) or (display: -ms-grid) {
  .layout { display: grid; }
}

/* nested — same effect as `and`, sometimes clearer */
@supports (display: grid) {
  @supports (gap: 1rem) {
    .layout { display: grid; gap: 1rem; }
  }
}
```

Parenthesize aggressively. The CSS parser is permissive but mixed `and`/`or` without parens is unspecified in some readings — group explicitly:

```css
@supports ((display: grid) and (gap: 1rem)) or (display: -ms-grid) { ... }
```

## Common detection idioms at our baseline

### Modern color functions

```css
/* OKLCH support — universal at baseline */
@supports (color: oklch(50% 0.1 0)) {
  :root { --accent: oklch(70% 0.15 140); }
}

/* Relative color syntax — Chrome 119+, Safari 16.4+, Firefox 128+ — Baseline July 2024 */
@supports (color: rgb(from white r g b)) {
  .surface { background: oklch(from var(--brand) calc(l * 0.95) c h); }
}

/* light-dark() — Chrome 123+, Safari 17.5+, Firefox 120+ */
@supports (color: light-dark(white, black)) {
  :root { color-scheme: light dark; --bg: light-dark(#fff, #111); }
}

/* color-mix() — Chrome 111+, Safari 16.2+, Firefox 113+ */
@supports (color: color-mix(in oklab, white, black)) {
  .tint { background: color-mix(in oklab, var(--bg) 90%, var(--accent)); }
}
```

For why `oklab` is preferred over `oklch` for transparent / gray mixing, see `../css-color-bugs/color-mix-interpolation.md`.

### Container queries

```css
/* Container query support — Baseline February 2023 */
@supports (container-type: inline-size) {
  .card { container-type: inline-size; }
  @container (inline-size > 40rem) { .card { padding: 2rem; } }
}
```

### Anchor positioning

Detection is the *current* property name, not the historical one (`inset-area` was renamed to `position-area` in Chrome 129; see `../anchor-positioning-quirks/inset-area-rename.md`):

```css
@supports (anchor-name: --foo) {
  .tooltip {
    position: absolute;
    position-anchor: --tooltip-anchor;
    top: anchor(bottom);
    position-area: bottom span-x;
  }
}

@supports not (anchor-name: --foo) {
  .tooltip {
    /* JS-positioned fallback or static placement */
  }
}
```

### `@scope`

`@scope` is supported in Chrome 118+, Safari 17.4+, Firefox 146+. Below the Firefox floor at our baseline (129–145), the only reliable detection is to test the parsed at-rule via `at-rule()` — but that itself only ships in Chromium 148+. The portable detection is to test a property `@scope` enables in the rendered cascade and assume parsing follows. In practice: ship flat-cascade fallback CSS, then layer scoped CSS behind feature-query gating where possible. See `progressive-enhancement.md`.

When `at-rule()` is widely shipped:

```css
@supports at-rule(@scope) {
  @scope (.card) { ... }
}
```

Until then, treat `@scope` as feature-query-resistant and design the fallback to work flat.

### Selector queries

`selector()` is universal at our baseline. The `:has()` gotcha is the canonical trap:

```css
/* WRONG — always evaluates false because the empty :has() is invalid */
@supports selector(:has()) { ... }

/* RIGHT — pass a selector argument */
@supports selector(:has(*)) { ... }

/* BETTER — relative selector ensures it's not just shallow :has() support */
@supports selector(:has(+ *)) { ... }
```

See https://www.bram.us/2023/01/04/css-has-feature-detection-with-supportsselector-you-want-has-not-has/ for the full discussion.

Other useful selector queries at baseline:

```css
@supports selector(:user-valid) { ... }   /* form validation pseudo-classes */
@supports selector(:user-invalid) { ... }
@supports selector(:state(active)) { ... } /* CustomStateSet */
@supports selector(:nth-child(1 of .item)) { ... } /* "of" syntax */
```

### Font feature detection

`font-tech()` and `font-format()` are both supported at baseline (Chrome 102+, Firefox 108+, Safari 17+):

```css
/* Detect WOFF2 (universally true at baseline; useful only for legacy graceful) */
@supports font-format(woff2) { ... }

/* Color font formats */
@supports font-tech(color-COLRv1) { ... }
@supports font-tech(color-CBDT) { ... }
@supports font-tech(color-SVG) { ... }

/* Variable fonts */
@supports font-tech(variations) { ... }

/* Palettes */
@supports font-tech(palettes) { ... }
```

These pair with `@font-face src tech(...)` for selective font loading. See https://groups.google.com/a/chromium.org/g/blink-dev/c/AzUM6sVsjBc for the original Chromium intent-to-ship.

### Custom properties with `@property`

```css
@supports (background: paint(squircle)) { ... }      /* Houdini paint API */

/* @property registration — no direct @supports test; detect via JS */
/* if (typeof CSS !== 'undefined' && 'registerProperty' in CSS) { ... } */
```

For `@property` itself, feature-query detection is awkward — there's no dedicated property-value pair to test for. Use the JS path or test a property that requires registration semantics (e.g. animating a custom property; the un-registered fallback is no-animation, the registered version animates). See `../css-polyfills-and-shims/at-property-fallbacks.md`.

## The `@supports` browser floor

Universal `@supports (property: value)` and `@supports not (...)` support has been Baseline since 2017. At our floor:

| Form | Floor |
|---|---|
| `@supports (property: value)` | Universal since 2017 |
| `@supports not (...)`, `and`, `or` | Universal since 2017 |
| `@supports selector(...)` | Chrome 83+, Firefox 103+, Safari 16+ — universal at our baseline |
| `@supports font-tech(...)` / `font-format(...)` | Chrome 102+, Firefox 108+, Safari 17+ — universal at our baseline |
| `@supports at-rule(@keyword)` | **Chromium 148+ only** — not shipped in Safari / Firefox stable |

If your support floor is below Chrome 83 / Firefox 103 / Safari 16, you cannot rely on `selector()`. Above our baseline, every form except `at-rule()` is safe.

## Anti-patterns

### UA-string sniffing as a workaround for "missing feature queries"

```js
// DON'T — brittle, lies, and unnecessary at our baseline
if (/Safari/.test(navigator.userAgent) && !/Chrome/.test(navigator.userAgent)) {
  document.body.classList.add('safari-fallback');
}
```

`@supports` with a property test is correct in 99% of cases. The 1% — load-bearing engine bugs that `@supports` can't see — should route to `../css-color-bugs/`, `../popover-quirks/`, or `../anchor-positioning-quirks/`, not to UA sniffing.

### Empty selector queries

```css
/* WRONG — always false */
@supports selector(:has()) { ... }
@supports selector(::view-transition-group()) { ... }

/* RIGHT — provide a non-empty argument */
@supports selector(:has(*)) { ... }
@supports selector(::view-transition-group(*)) { ... }
```

### Detecting absence by omission

```css
/* DON'T — relies on cascade order; brittle */
.layout { display: flex; }
@supports (display: grid) {
  .layout { display: grid; }
}
/* What if a third rule re-applies display: flex via specificity? */

/* DO — explicit fallback via @supports not, or design the cascade so the
   modern rule wins by source order */
@supports not (display: grid) {
  .layout { display: flex; flex-wrap: wrap; }
}
@supports (display: grid) {
  .layout { display: grid; gap: 1rem; }
}
```

The cascade still applies inside `@supports` — feature queries don't change specificity, only conditional-inclusion.

### Polyfilling `@supports` itself

It's tempting to imagine a JS polyfill that emulates `@supports` for ancient browsers. **Don't.** `@supports` has been universally shipped since 2017 (IE never had it, but IE is below every modern baseline by years). Pre-2017 browsers are out of scope at every modern baseline.

## When `@supports` isn't enough

Some bugs are silent — the feature query says "yes, supported," but the implementation has a load-bearing bug. Examples at our baseline:

- Safari < 18 OKLCH `color-mix` interpolating in LCH instead of OKLCH (`../css-color-bugs/oklch-oklab-safari.md`)
- Firefox rendering `color(display-p3 ...)` mapped to sRGB despite passing the feature query (`../css-color-bugs/display-p3-firefox-lag.md`)
- iOS Safari 17.0–18.2 popover light-dismiss broken (`../popover-quirks/ios-safari-light-dismiss.md`)

For these, the workaround lives in the bug-axis files, not in a feature query. The pattern is to ship the safe form everywhere (e.g. `color-mix(in oklab, ...)` instead of `in oklch`) rather than gate behavior on the engine.

## Cross-references

- `progressive-enhancement.md` — the design pattern that `@supports` enables.
- `js-feature-detection.md` — the JS counterpart for runtime APIs.
- `../meta/decision-tree.md` — Step 4 of the do-I-need-a-polyfill flow.
- `../css-color-bugs/relative-color-syntax.md` — `oklch(from base ...)` detection.
- `../anchor-positioning-quirks/inset-area-rename.md` — what to detect (`anchor-name`, not `inset-area`).
- `../css-polyfills-and-shims/anchor-positioning-polyfill.md` — when `@supports` isn't enough and you need a runtime shim.
