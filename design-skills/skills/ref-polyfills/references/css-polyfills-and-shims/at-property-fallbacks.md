---
date: 2026-04-27
coverage: extended
peers:
  - ../meta/the-modern-baseline.md
  - ../meta/decision-tree.md
  - ../feature-detection/at-supports-recipes.md
  - ./view-transitions.md
  - ./lightningcss-css-lowering.md
  - ../build-tools/lightningcss-features.md
primary_sources:
  - https://web.dev/blog/at-property-baseline — "@property: Next-gen CSS variables now with universal browser support"; Baseline July 9, 2024
  - https://developer.mozilla.org/en-US/docs/Web/CSS/@property — MDN reference
  - https://web.dev/css-props-and-vals/ — Houdini CSS Properties and Values API origin (Chrome 78 JS, Chrome 85 CSS)
  - https://developer.chrome.com/blog/new-in-chrome-85 — Chrome 85 added the @property at-rule
  - https://developer.mozilla.org/en-US/docs/Web/CSS/@scope — `@scope` MDN reference
  - https://web-standards.dev/news/2026/01/scope-css-baseline/ — `@scope` reaches Baseline (Firefox 146)
  - https://caniuse.com/css-cascade-scope — caniuse `@scope` support data
  - https://caniuse.com/mdn-css_at-rules_property — caniuse `@property` support data
---

# `@property` is at baseline — `@scope` was the gap; the broader pattern is "feature-query + flat fallback"

> **Status at 2026-04-27.** `@property` is **Baseline Newly Available since July 9, 2024** — fully native at our floor (Chrome 85, Firefox 128, Safari 16.4). `@scope` reached Baseline only in **December 2025 / January 2026** (Firefox 146); at our skill's floor (Firefox 129+) there is a **17-version gap**, and **no real polyfill exists**. This file documents the gap and the pattern for un-polyfillable CSS features: feature-query + flat fallback + accept degraded experience.

## `@property` — fully Baseline at our floor

`@property` lets you register typed CSS custom properties — declaring syntax, inheritance, and initial value. This unlocks animation of custom properties, type-checked variables, and inheritance control.

### Browser support — green at our floor

| Engine | First version | Date |
|---|---|---|
| Chrome / Edge | **85** | August 25, 2020 |
| Firefox | **128** | July 9, 2024 |
| Safari | **16.4** | March 27, 2023 |

Per [web.dev/blog/at-property-baseline](https://web.dev/blog/at-property-baseline): *"@property is now available in all three major browser engines and became Baseline Newly available as of July 9, 2024."*

Our skill's baseline is Chrome 125+ (well past 85), Firefox 129+ (just past 128 — barely!), Safari 17.4+ (well past 16.4). **All three engines ship `@property` at our floor.** No polyfill needed. No fallback needed for the at-rule itself.

### Canonical example

```css
@property --gradient-angle {
  syntax: '<angle>';
  inherits: false;
  initial-value: 0deg;
}

.spinning-gradient {
  --gradient-angle: 0deg;
  background: linear-gradient(var(--gradient-angle), #f06, #06f);
  animation: spin 4s linear infinite;
}

@keyframes spin {
  to { --gradient-angle: 360deg; }
}
```

Without `@property`, the angle would be a string and would not animate (CSS variables of unspecified type interpolate as strings, which CSS animation cannot tween). `@property` makes the variable typed-as-`<angle>`, so the browser knows how to interpolate it.

### Things to know about authoring

- **`syntax` and `inherits` are required.** Omitting either makes the entire `@property` rule invalid.
- **`initial-value` is required unless `syntax: '*'`.** If you specify a typed syntax (`<color>`, `<length>`, `<angle>`, etc.) and omit `initial-value`, the rule is invalid.
- **Don't shadow normal custom properties incorrectly** — registering `--foo` as `<color>` and then setting it to a non-color value silently keeps the initial-value, which can be confusing during debugging.

## `@scope` — Baseline arrived 17 versions after our Firefox floor

`@scope` enables scoped CSS rules — selecting elements in DOM subtrees without coupling selectors tightly to structure or relying on Shadow DOM.

### Browser support — gap at our floor

| Engine | First version | Date |
|---|---|---|
| Chrome / Edge | **118** | October 10, 2023 |
| Safari | **17.4** | March 5, 2024 |
| Firefox | **146** | December 9, 2025 |

Per [web-standards.dev](https://web-standards.dev/news/2026/01/scope-css-baseline/): *"With Firefox 146 officially supporting the @scope at-rule, CSS @scope is now available across Chrome, Safari, and Firefox — earning the Baseline: Newly Available status."* The Baseline date is December 2025 / January 2026 (depending on calculation cutoff).

At our baseline:
- **Chrome 125+**: yes (since Chrome 118)
- **Safari 17.4+**: yes (since 17.4 itself)
- **Firefox 129–145**: **NO** (17 missing versions)
- **Firefox 146+**: yes

That's a substantial gap. Firefox 129 to 145 is 17 major releases — ~16 months of Firefox time.

### There is no real `@scope` polyfill

`@scope` cannot be polyfilled cleanly. To simulate it in JS would require:

1. Parsing `@scope` blocks from author stylesheets.
2. Resolving each `@scope (root) to (limit)` declaration into a list of matching DOM elements.
3. Generating equivalent flat CSS scoped via attribute selectors or class additions.
4. Running this on every DOM mutation (because `@scope`'s root/limit binding is dynamic).

The runtime cost of this approach approaches the cost of a CSS-in-JS framework — at which point you should just use a CSS-in-JS framework. **No production polyfill exists**, and none is likely to be built; the energy goes into Firefox shipping native instead.

### The pattern: feature-query + flat fallback

For Firefox 129–145 users, the answer is to author both versions and let the cascade pick:

```css
/* Flat fallback — works everywhere */
.article-card .title {
  color: var(--text-strong);
  font-size: 1.25rem;
}
.article-card .meta {
  color: var(--text-muted);
}

/* Scoped enhancement — Firefox 146+, Chrome 118+, Safari 17.4+ */
@supports (selector(:scope)) {
  @scope (.article-card) {
    .title { font-size: 1.5rem; } /* refines beyond the flat version */
    .meta  { font-size: 0.875rem; }
  }
}
```

The flat selectors degrade gracefully. The `@scope` block enhances on supporting browsers. Firefox 129–145 sees a slightly less polished card; Firefox 146+ sees the refinement.

### When the flat fallback is not enough

For some `@scope` use cases — particularly **donut-scoping** (`@scope (a) to (b)` to exclude a subtree) — a flat selector cannot replicate the behavior. There are two options:

1. **Avoid donut-scoping until your Firefox floor is 146+.** Use class additions or component boundaries instead.
2. **Use Shadow DOM.** If you genuinely need scoped styles with subtree exclusion, Shadow DOM provides the encapsulation natively across all browsers.

There is no third option that doesn't involve a major build-time framework.

## The bigger lesson — when there's no polyfill

`@scope` is one example of a pattern that recurs across modern CSS:

- **CSS Houdini Layout / Paint API**: Chrome only; no polyfill possible (requires worklet thread).
- **CSS Custom Highlight API**: Chromium + Safari; Firefox 140+; pre-baseline at 2026.
- **`@scope`**: gap on Firefox 129–145 as documented here.
- **`@starting-style`**: Baseline as of mid-2025; mostly OK but gap for Firefox 128 (just below our floor) — would have been ungated below baseline.
- **`field-sizing: content`**: Baseline Newly Available 2025; gap for Safari 17.4 → some 17.x versions.
- **Anchor positioning**: has a polyfill (`@oddbird/css-anchor-positioning`), but with significant limitations — see `./anchor-positioning-polyfill.md`.
- **Scroll-driven animations**: has a polyfill (`flackr/scroll-timeline`), but with perf trade-offs — see `./scroll-timeline-polyfill.md`.

The pattern: not every CSS feature has a polyfill. Sometimes the answer is **"use feature query and accept degraded experience for unsupported users."** This is the modern progressive-enhancement stance, applied to CSS:

1. **Author the flat fallback first.** Make the page work without the new feature.
2. **Layer the enhancement inside `@supports`.** Authors who scan the cascade can see exactly which feature is the enhancement.
3. **Don't try to fake the new feature with JS unless the polyfill is mature.** "JS rewriting CSS at runtime" is rarely a net win.

## Feature-detection recipes

For at-rules:

```css
/* @scope */
@supports (selector(:scope)) { ... }

/* @starting-style */
@supports (transition-behavior: allow-discrete) { ... }
/* (transition-behavior is the natural pair to @starting-style) */

/* @container */
@supports (container-type: inline-size) { ... }

/* @property — already baseline; you don't usually need to gate */
@supports at-rule(@property) { ... }
```

`@supports at-rule(...)` and `@supports selector(...)` are themselves widely supported; see `../feature-detection/at-supports-recipes.md`.

For JS-side detection:

```js
// @scope
const scopeOK = CSS.supports('selector(:scope)');

// @starting-style requires checking transition-behavior
const startingStyleOK = CSS.supports('transition-behavior: allow-discrete');
```

## When NOT to author both — drop the fallback

If your audience analytics show negligible Firefox 129–145 share (consumer-facing apps with auto-updating Firefox users by April 2026 are mostly on 147+), the flat fallback is dead weight you maintain forever. Track your audience and remove the fallback when the supporting-browser share crosses ~99%.

## Cross-references

- `../meta/the-modern-baseline.md` — what's at our floor; `@property` is, `@scope` is borderline.
- `../meta/decision-tree.md` — "Do I need a polyfill?" — points to this pattern when the answer is no-but-also-no-polyfill.
- `../feature-detection/at-supports-recipes.md` — full `@supports` recipe library.
- `./lightningcss-css-lowering.md` — what build-time tools can vs. can't lower.
- `./anchor-positioning-polyfill.md` — example of a feature where a polyfill DOES exist (with caveats).
- `./scroll-timeline-polyfill.md` — same as anchor-positioning; polyfill exists but constrained.
- `./view-transitions.md` — example where no real polyfill exists; same pattern as `@scope`.
