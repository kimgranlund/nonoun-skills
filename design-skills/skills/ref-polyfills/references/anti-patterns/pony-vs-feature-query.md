---
date: 2026-04-27
coverage: advisory
peers:
  - ../feature-detection/at-supports-recipes.md
  - ../feature-detection/progressive-enhancement.md
  - ../feature-detection/ponyfill-pattern.md
  - ../feature-detection/js-feature-detection.md
  - ../feature-detection/prollyfill-pattern.md
  - ../meta/decision-tree.md
  - ../meta/the-modern-baseline.md
  - ../css-color-bugs/oklch-oklab-safari.md
  - ../css-color-bugs/relative-color-syntax.md
  - ../css-polyfills-and-shims/scroll-timeline-polyfill.md
  - ../css-polyfills-and-shims/anchor-positioning-polyfill.md
  - ../runtime-polyfills/iterator-helpers.md
primary_sources:
  - https://developer.mozilla.org/en-US/docs/Web/CSS/@supports — `@supports` reference
  - https://drafts.csswg.org/css-conditional-3/ — CSS Conditional Rules Module 3 (the `@supports` baseline)
  - https://web.dev/articles/baseline-and-polyfills — modern progressive-enhancement guidance
  - https://github.com/sindresorhus/ponyfill — Sindre Sorhus's canonical ponyfill README
  - https://ponyfoo.com/articles/polyfills-or-ponyfills — Nicolás Bevacqua's "Polyfills or Ponyfills?" essay
  - https://philipwalton.com/articles/the-dark-side-of-polyfilling-css/ — Philip Walton on the limits of CSS polyfilling
  - https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/animation-timeline — animation-timeline reference
---

# Anti-pattern: reaching for a ponyfill when a feature query would do

## The anti-pattern

A team needs a feature that's not supported in every engine of their support matrix. Their reflex is to install a ponyfill (or polyfill) that makes the feature work everywhere. The ponyfill ships in the bundle. Every user pays for it.

The mistake: a CSS `@supports` feature query (or, for JS, a single `'feature' in obj` check) would have handled the differentiation natively, with zero runtime code, and would have given each user the best UX their browser can deliver instead of a uniform ponyfilled approximation.

Three concrete examples:

```js
// ANTI-PATTERN — importing a CSS.supports() polyfill
import 'css-supports-polyfill'; // ~3KB
if (CSS.supports('color', 'oklch(0.5 0.1 0)')) {
  document.body.classList.add('modern-color');
}
```

```js
// ANTI-PATTERN — importing a runtime ponyfill for a use case Array.reduce handles
import groupBy from 'es-shims/Object/groupBy/auto'; // ~1KB
const grouped = groupBy(items, item => item.category);
// ...when this would have worked, with no import, in every supported engine:
// const grouped = items.reduce((acc, item) => {
//   (acc[item.category] ??= []).push(item);
//   return acc;
// }, {});
```

```js
// ANTI-PATTERN — conditionally importing a scroll-driven-animations polyfill for Firefox
import scrollTimelinePolyfill from 'scroll-timeline'; // ~25KB
if (!('animationTimeline' in document.documentElement.style)) {
  scrollTimelinePolyfill();
}
// ...when a CSS-native feature query would have shipped the enhancement only to supporters:
// @supports (animation-timeline: scroll()) and (animation-range: 0% 100%) {
//   .hero { animation-timeline: scroll(); }
// }
```

In each case, the ponyfill makes the feature available unconditionally. The team ships it because "it makes the code path uniform." But the conditional path is the feature — it's how progressive enhancement works.

## Why it persists

Three reasons:

1. **Ponyfills feel "more correct" than feature queries.** A ponyfill makes the same code path run for every user. A feature query splits the code path. Engineers trained on uniform-execution paradigms (server-side, CLI tools, native apps) often default to the uniform-execution model on the web — even though the web has been progressive-enhancement-shaped since CSS itself shipped.
2. **"We need to support every user equally."** Stated as a fairness principle, this argument sounds compelling. In practice it means **leveling down** — every user gets the worst-case experience the unsupported browser can manage. The feature-query alternative levels *up* — every user gets the best-case experience their browser can deliver, and unsupported browsers fall back gracefully. Equal-by-leveling-down is rarely what the team actually wants once the trade-off is named.
3. **CSS feature queries are unfamiliar to JS-first engineers.** `@supports` is in the CSS spec, not the JS toolchain. Engineers who write CSS via emotion / styled-components / Tailwind may not realize `@supports` is available, or may not know the exact syntax for selector-form queries (`@supports selector(:has(*))`). The ponyfill route sidesteps the unfamiliarity.

## Why it's wrong at the modern baseline

### Ponyfills add bundle size; feature queries don't

A `@supports` rule is parsed once by the CSS engine. It contributes maybe ~50 bytes to the stylesheet. There is no runtime cost — the engine evaluates the condition during stylesheet parsing and applies the matching block (or doesn't). No JS runs. No bundle bloat.

A ponyfill, by contrast:

- `css-supports-polyfill` — 2–3 KB minified, even though `CSS.supports` is itself native at our baseline (Chrome 28+, Safari 9+, Firefox 22+; effectively universal since 2014).
- `es-shims/Object/groupBy` ponyfill — ~1 KB to replicate behavior `Array.reduce` already does in 5 native lines.
- `scroll-timeline` polyfill — ~25 KB minified to simulate scroll-driven animations in JS via `requestAnimationFrame`. The polyfill works, but it runs on the main thread, allocating per-frame closures, in browsers where the native CSS-engine implementation would never execute JS at all.
- `@oddbird/css-anchor-positioning` polyfill — ~30 KB to simulate anchor positioning via scroll-and-resize observers + recomputed layout.

These are not free. Every byte ships to every user. Every byte is on the critical path.

### Ponyfills run in the JS thread; feature queries are CSS-native

When a `@supports` rule fires, the work happens in the browser's CSS engine — written in C++ in Chromium (Blink), in C++ in WebKit (Safari), in Rust in Gecko (Firefox via Stylo). It is the fastest possible path: the engine knows what it supports, the rule applies or doesn't, no JS context-switch, no recompute on every paint, no observer overhead.

When a JS-based polyfill simulates a CSS feature, the work happens in JS:

- `scroll-timeline` polyfill: `requestAnimationFrame` callback per frame, computes scroll position, mutates inline styles or CSS variables. **Cost: ~0.1ms per frame, all in JS, contending with React reconciliation and other work on the main thread.**
- `anchor-positioning` polyfill: `IntersectionObserver` + `ResizeObserver` watching anchor element, `requestAnimationFrame` to recompute target position, mutations to inline styles. **Cost: layout invalidations on every observed change.**
- `Object.groupBy` ponyfill (via `es-shims/Object/groupBy/auto`): an extra function-call indirection on every grouping. Trivial cost individually, but it sets a default that says "polyfills are free."

The native CSS path has none of this overhead. It is also more correct: the native implementation handles edge cases (subpixel rounding, transforms, scroll containers in fragmented contexts) that JS polyfills typically handle imperfectly.

### Feature queries enable progressive enhancement

This is the load-bearing argument. A feature query says: **the user gets the best UX their browser can support.** Modern browsers see the modern code path. Older browsers see the fallback. Both work. The split is intentional, named, and tested.

A ponyfill says: **all users get the same UX.** Sometimes this is what you want (e.g., a critical interaction must work identically everywhere). Often it is not — the modern users are paying the cost of the polyfill (bundle size, runtime overhead, imperfect fidelity) so that older users can have a degraded approximation of a feature they wouldn't have noticed missing.

The "all users get the same UX" mindset is the wrong default at the modern baseline. The web's progressive-enhancement story has worked for 25 years; it works at this baseline too.

### Feature queries are testable; ponyfills hide assumptions

A `@supports (color: oklch(0.5 0.1 0)) { ... }` rule is testable: you can disable the rule in DevTools, see the fallback, and verify it works. You can run Playwright against engines without OKLCH support and see the fallback path. The two paths are explicit.

A ponyfill that "makes the feature work everywhere" hides the fallback path. The polyfilled `Object.groupBy` is ostensibly identical to the native one, but in practice may diverge on edge cases (callback throwing, prototype pollution, integer key coercion). When something breaks in a polyfilled branch, you debug a polyfill, not your code.

## The decision tree

A practical heuristic for picking between the two patterns. Three questions:

### 1. Is the differentiation between "supported" and "unsupported" graceful?

**If yes → feature query.**

Examples:

- OKLCH colors with sRGB fallback. An unsupported browser shows a slightly less vibrant color; the user is fine.
- `text-wrap: balance` for headings. An unsupported browser shows normal wrapping; the heading is still readable.
- Container queries with media-query fallback. An unsupported browser uses the breakpoint approach; the layout still works.
- `:has()` selector with explicit-class fallback. The unsupported browser falls back to JS-emitted class names; no user-visible regression.
- Scroll-driven animations. An unsupported browser shows static content; the modern user gets parallax.
- Anchor positioning. An unsupported browser shows the popover at fixed coordinates; the modern user gets dynamic anchoring.

In all these cases, the fallback path is a working subset of the modern path. The user doesn't notice the absence; they just don't get the enhancement. Use `@supports`.

### 2. Does the unsupported case need a different code path entirely?

**If yes → ponyfill (or alternative algorithm).**

Examples:

- A feature where the missing engine support means the *primary* user task is broken, not just stylistically degraded. (Rare at our baseline.)
- A polyfill for a critical security primitive (Web Crypto fallback). The wrong answer is "skip the feature for unsupported users"; the right answer is to ship a polyfill so the security primitive works for everyone.
- An iterator-helpers ponyfill for Safari 17.4–18.3 specifically, because the `Iterator.prototype.map` / `.filter` API doesn't have a CSS-style fallback — the JS code either runs or it doesn't.

In these cases, "the user gets nothing" is not acceptable, so you ship the polyfill. The cost is real; it's the correct trade-off.

### 3. Is the feature CSS or JS?

**CSS → `@supports` first.** Always. There is no scenario where a CSS polyfill is preferable to a CSS feature query at the modern baseline. The CSS engine is faster, the cost is zero, and the fallback path is testable.

**JS → feature-detect first.** Use `'feature' in obj` or `typeof feature === 'function'` checks. Only reach for a ponyfill if the behavior of the unsupported case is genuinely unacceptable. For most cases — `Object.groupBy`, `Array.findLast`, `Promise.try`, set methods — the ES5 fallback or the ponyfill-import-only-when-missing pattern is the right answer. See [`../feature-detection/js-feature-detection.md`](../feature-detection/js-feature-detection.md).

## Worked examples — feature query, not ponyfill

### Example 1 — OKLCH colors

```css
/* Anti-pattern: a JS polyfill that translates OKLCH to RGB everywhere */
/* (No good polyfill exists; teams hand-roll one or import a color library. ~10KB.) */

/* Modern pattern: feature query with sRGB fallback */
.button {
  background: #3b82f6; /* sRGB fallback for engines without OKLCH */
}
@supports (color: oklch(0.5 0.1 0)) {
  .button {
    background: oklch(60% 0.18 245); /* OKLCH for engines that support it */
  }
}
```

Bundle cost: 0 bytes. Engines that support OKLCH render the precise OKLCH value. Engines that don't render the sRGB hex. No JS runs. See [`../css-color-bugs/oklch-oklab-safari.md`](../css-color-bugs/oklch-oklab-safari.md) for the Safari-specific edge cases.

### Example 2 — Scroll-driven animations

```css
/* Anti-pattern: import a 25KB scroll-timeline polyfill for non-Chromium browsers */

/* Modern pattern: feature query with reduced-motion respect */
@media (prefers-reduced-motion: no-preference) {
  @supports (animation-timeline: scroll()) and (animation-range: 0% 100%) {
    .parallax-hero {
      animation: parallax linear;
      animation-timeline: scroll();
      animation-range: 0% 100%;
    }
  }
}
```

Engines that support scroll-driven animations get the parallax. Firefox 129 (which doesn't ship the unflagged feature until 147 in Jan 2026) gets static content. Reduced-motion users always get static content. Three layers of opt-in, all native, zero JS. See [`../css-polyfills-and-shims/scroll-timeline-polyfill.md`](../css-polyfills-and-shims/scroll-timeline-polyfill.md) for the polyfill option if you genuinely need it (you usually don't).

### Example 3 — Anchor positioning

```css
/* Modern pattern: feature query with absolute-positioning fallback */
.tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
}
@supports (anchor-name: --my-anchor) {
  .anchor-element {
    anchor-name: --my-anchor;
  }
  .tooltip {
    position-anchor: --my-anchor;
    position-area: bottom center;
    /* Reset the fallback transforms */
    top: auto;
    left: auto;
    transform: none;
  }
}
```

The ~30KB OddBird anchor-positioning polyfill is a real option — see [`../css-polyfills-and-shims/anchor-positioning-polyfill.md`](../css-polyfills-and-shims/anchor-positioning-polyfill.md) — but the feature-query alternative gives unsupported browsers a working tooltip with no JS cost. Reach for the polyfill only when the dynamic-anchoring behavior is load-bearing for the UX.

### Example 4 — `Object.groupBy`

```js
// Anti-pattern: import a ponyfill for a function Array.reduce already covers
import groupBy from 'object.groupby/auto';
const grouped = groupBy(items, item => item.category);

// Modern pattern: just use Array.reduce, native everywhere
const grouped = items.reduce((acc, item) => {
  (acc[item.category] ??= []).push(item);
  return acc;
}, Object.create(null));

// Or, since `Object.groupBy` is itself native at our baseline (Chrome 117 /
// Safari 17.4 / Firefox 119), just use the native function:
const grouped = Object.groupBy(items, item => item.category);
```

Two correct answers — both better than the ponyfill. See [`../runtime-polyfills/array-grouping.md`](../runtime-polyfills/array-grouping.md) for the baseline status.

### Example 5 — CSS.supports detection in JS

```js
// Anti-pattern: import a CSS.supports polyfill, even though it's native everywhere
import 'css-supports-polyfill';
if (CSS.supports('color', 'oklch(0.5 0.1 0)')) { ... }

// Modern pattern: just use CSS.supports — native at the baseline (and for years before)
if (CSS.supports('color', 'oklch(0.5 0.1 0)')) { ... }
```

`CSS.supports` is native in every browser shipped since 2014. The polyfill exists for IE11, which is not in our support matrix. Drop the import.

## The "design for the floor" mindset

Build for the worst-case browser in your support matrix. Layer enhancements with feature queries on top. The baseline UX works for everyone — by definition, since you built it for the floor. The enhanced UX works for the modern user, who gets the better experience their browser can deliver.

This inverts the polyfill mindset (build for the modern, polyfill for the rest). It is also the older mindset — the way the web has worked since the late 1990s, when `<noscript>` and `<table>` fallbacks were the standard pattern. Modern feature queries make the inversion mechanical: write the floor in plain CSS, wrap each enhancement in `@supports`.

The shape of a stylesheet under this mindset:

```css
/* 1. Floor: works everywhere */
.card {
  background: #fff;
  border: 1px solid #ccc;
  padding: 1rem;
}

/* 2. Enhancement layer 1: cascade-layer-aware, container-query-aware */
@supports (container-type: inline-size) {
  .card {
    container-type: inline-size;
  }
  @container (min-width: 400px) {
    .card { padding: 1.5rem; }
  }
}

/* 3. Enhancement layer 2: modern color, surface refinement */
@supports (color: oklch(0.5 0.1 0)) {
  .card {
    background: oklch(98% 0.005 240);
    border-color: oklch(85% 0.01 240);
  }
}

/* 4. Enhancement layer 3: scroll-driven animation if available */
@supports (animation-timeline: scroll()) {
  .card {
    animation: card-reveal linear;
    animation-timeline: scroll();
    animation-range: entry 0% cover 30%;
  }
}
```

Each layer is independently usable. Each layer's absence degrades gracefully. No polyfill ships. No JS executes. The user gets the best experience their browser is capable of.

## Cross-reference

- [`../feature-detection/at-supports-recipes.md`](../feature-detection/at-supports-recipes.md) — full `@supports` recipe library.
- [`../feature-detection/progressive-enhancement.md`](../feature-detection/progressive-enhancement.md) — the broader progressive-enhancement pattern.
- [`../feature-detection/ponyfill-pattern.md`](../feature-detection/ponyfill-pattern.md) — when ponyfills *are* the right answer (rare at this baseline).
- [`../feature-detection/js-feature-detection.md`](../feature-detection/js-feature-detection.md) — JS-side feature detection idioms.
- [`../meta/decision-tree.md`](../meta/decision-tree.md) — the "do I need a polyfill?" flowchart.
- [`./defensive-overpolyfilling.md`](./defensive-overpolyfilling.md) — the broader anti-pattern this is a special case of.
- [`./corejs-entry-modern.md`](./corejs-entry-modern.md), [`./target-es5-modern.md`](./target-es5-modern.md) — sibling anti-patterns.
- [`../css-polyfills-and-shims/scroll-timeline-polyfill.md`](../css-polyfills-and-shims/scroll-timeline-polyfill.md), [`../css-polyfills-and-shims/anchor-positioning-polyfill.md`](../css-polyfills-and-shims/anchor-positioning-polyfill.md) — when these polyfills are genuinely needed.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — concrete capabilities at the baseline.
