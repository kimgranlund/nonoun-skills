---
date: 2026-04-27
coverage: canonical
peers:
  - ../build-tools/lightningcss-features.md
  - ../build-tools/postcss-preset-env.md
  - ../build-tools/browserslist-recipes.md
  - ../build-tools/vite-build-target.md
  - ./postcss-preset-env-stages.md
  - ./at-property-fallbacks.md
  - ./anchor-positioning-polyfill.md
  - ./scroll-timeline-polyfill.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://lightningcss.dev/transpilation.html — feature lowering matrix
  - https://lightningcss.dev/options.html — `include` / `exclude` flags via the Features enum
  - https://lightningcss.dev/docs.html — Browserslist auto-discovery
  - https://github.com/parcel-bundler/lightningcss — repo, MPL-2.0 license, maintainer Devon Govett
  - https://www.npmjs.com/package/lightningcss — npm package metadata
  - https://web.dev/blog/at-property-baseline — `@property` Baseline July 9, 2024 (already native)
  - https://caniuse.com/css-cascade-scope — `@scope` browser support; gap on Firefox < 146
---

# Lightning CSS feature lowering — what gets transformed at our baseline (mostly nothing)

> **Status at 2026-04-27.** Lightning CSS is a Rust-based CSS parser/transformer/minifier by Devon Govett (Parcel), MPL-2.0. This file documents lowering from a **CSS-feature angle** — given our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+), what does Lightning CSS actually transform, and what does it pass through? See `../build-tools/lightningcss-features.md` for the build-tool angle (config, Vite integration, when to choose Lightning vs. PostCSS).

## TL;DR — at our baseline, Lightning CSS does almost no lowering

The headline: **most modern CSS is already native at our floor**, so Lightning CSS lowers very little. Its real value at this baseline is fast minification, vendor-prefix cleanup, and CSS bundling. The lowering is a tiny corner of what it does.

That's not Lightning CSS's fault — it's a feature of the baseline. Lightning CSS calibrated against a 2020-era browserslist was the workhorse that lowered nesting, custom properties, logical properties, etc. Calibrated against our 2024+ baseline, those features are native and no lowering happens.

## Bundle-size delta from Lightning CSS at our baseline

This deserves its own callout because it's surprising:

> When the source CSS is already native-at-baseline, the **lowered output is byte-for-byte identical** to the source minus minification savings. Lightning CSS adds ~zero output bytes versus shipping the source CSS directly.

Compare with `core-js` for JavaScript: even when no polyfills run, Babel can leak CommonJS interop helpers and runtime imports into the bundle. Lightning CSS has no analogue — the output is pure CSS, no runtime, no helpers, no imports beyond what you wrote.

This is a load-bearing reason to prefer build-time CSS transformation over runtime CSS polyfills: **you pay zero deployed bytes for build-time transformation when the source is native**.

## What Lightning CSS DOES lower at our baseline

A short list. These are the features where Lightning CSS still earns its keep, even at our floor:

### 1. Vendor-prefix cleanup

Lightning CSS auto-inserts `-webkit-` prefixes for older Safari quirks (e.g. `-webkit-backdrop-filter` mirrors of `backdrop-filter`) AND removes prefixes that are no longer needed at the configured target.

At our baseline, the cleanup mostly drops `-moz-` prefixes that Firefox shipped years ago. The `-webkit-` insertions are minimal — most modern Safari quirks are gone.

You can stop using `autoprefixer` if Lightning CSS is in the pipeline. ([Lightning CSS docs](https://lightningcss.dev/docs.html))

### 2. Relative color syntax → absolute

```css
/* Source */
.button {
  background: oklch(from var(--brand) calc(l * 0.9) c h);
}
```

If your `targets` includes a browser before relative-color-syntax shipped (Chrome 119, Safari 16.4, Firefox 128), Lightning CSS computes the relative color at build time and emits a static result. At our floor (Chrome 125, Safari 17.4, Firefox 129), relative color syntax is **native** in all three engines, so this lowering doesn't trigger.

If you ship to a lower floor than ours, this is one of the most useful lowerings.

### 3. Gradient stop shorthands → expanded

```css
/* Source — double-position stop syntax */
background: linear-gradient(red 0% 50%, blue 50% 100%);

/* Lowered (for older targets) */
background: linear-gradient(red 0%, red 50%, blue 50%, blue 100%);
```

Native everywhere at our floor; no-op at our baseline.

### 4. Range media-query → traditional

```css
/* Source */
@media (200px <= width <= 800px) { ... }

/* Lowered (for older targets) */
@media (min-width: 200px) and (max-width: 800px) { ... }
```

Native at our floor (Chrome 104, Safari 16.4, Firefox 102). No-op for us.

### 5. Color function fallbacks

For audiences below our floor, Lightning CSS can emit `rgb()` / sRGB fallbacks before `oklch()` / `lab()` / wide-gamut declarations:

```css
/* Source */
.brand { color: oklch(0.7 0.15 195); }

/* Lowered */
.brand { color: rgb(50, 180, 200); }
.brand { color: oklch(0.7 0.15 195); }
```

At our floor, all three engines ship `oklch()` / `oklab()` / `lab()` natively, so this lowering is gated off.

### 6. Hex with alpha → `rgba()`

```css
/* Source */
.fade { background: #00000080; }

/* Lowered */
.fade { background: rgba(0, 0, 0, 0.5); }
```

Native everywhere; no-op for us.

### 7. CSS Nesting → flat selectors

```css
/* Source */
.card {
  & .title { font-size: 1.5rem; }
}

/* Lowered */
.card .title { font-size: 1.5rem; }
```

Native in Chrome 120, Firefox 117, Safari 17.2 — all three at our floor. No-op at our baseline.

## What Lightning CSS does NOT lower

This is the more important list. **Lightning CSS does NOT polyfill features that require runtime support** — no JavaScript is shipped to the browser, ever. If a feature requires runtime computation that can't be flattened to static CSS, Lightning CSS passes it through unchanged.

### Anchor positioning

`anchor-name`, `position-anchor`, `position-area`, `anchor()`, `anchor-size()`, `@position-try`, `position-try-fallbacks`. These require runtime layout computation against a referenced element. Lightning CSS cannot lower this to flat CSS because the position depends on the live anchor's box, which only exists at layout time.

For audiences below the native floor, use `@oddbird/css-anchor-positioning`. See `./anchor-positioning-polyfill.md`.

### Scroll-driven animations

`animation-timeline: scroll(...)` / `view(...)`, `ScrollTimeline`, `ViewTimeline`. Lightning CSS does not flatten these; the timeline is a runtime construct.

For audiences without native support, use `flackr/scroll-timeline`. See `./scroll-timeline-polyfill.md`.

### `@scope`

The dynamic root/limit binding cannot be flattened to static CSS. Lightning CSS passes `@scope` rules through unchanged. There is no polyfill. See `./at-property-fallbacks.md`.

### Container queries (in older browsers)

`@container` requires a runtime layout-aware container. Native at our floor (Chrome 105, Firefox 110, Safari 16); Lightning CSS does NOT have a JS-runtime polyfill for older browsers — there is no native-CSS lowering target.

### View transitions

Same reasoning. Lightning CSS does not lower `@view-transition` or `::view-transition-*` pseudo-elements; the feature requires the runtime DOM-snapshot machinery.

### `@property` (registered custom properties)

Lightning CSS does not polyfill `@property`. The runtime semantics (typed interpolation, inherits, initial-value) cannot be replicated in pre-`@property` browsers without runtime JS. Native at our floor anyway. See `./at-property-fallbacks.md`.

### `@starting-style`

Native at Chrome 117, Firefox 129 (just at our floor!), Safari 17.5. Pre-baseline at our exact floor; Lightning CSS doesn't lower it.

### `field-sizing: content`

Layout-runtime feature; not flat-CSS-expressible. Lightning CSS passes through.

### Houdini Paint / Layout API

Worklet-based; require browser-thread infrastructure. Cannot be polyfilled without a much larger runtime.

## The decision tree

Given a feature, ask:

1. **Is it native at our baseline?** Check `caniuse.com` or web.dev's Baseline status against Chrome 125 / Safari 17.4 / Firefox 129.
   - **Yes** → Ship the native syntax. Lightning CSS passes it through. No lowering, no runtime.
2. **Is it not native, but expressible as flat CSS for the gap?**
   - **Yes** → Lightning CSS lowers it (relative color, gradient stops, range media, etc.).
3. **Is it not native, and requires runtime support?**
   - **Yes** → Lightning CSS does NOT help. Either:
     - Use a runtime polyfill (`@oddbird/css-anchor-positioning`, `flackr/scroll-timeline`, etc.).
     - Use feature-query gate + flat fallback (`@scope`, view transitions, etc.).
     - Skip the feature for the gap audience.

## The configurable knobs (briefly)

The full reference is in `../build-tools/lightningcss-features.md`. The relevant flags for understanding lowering at our baseline:

- **`targets`** — usually populated from browserslist. Lower targets → more lowering.
- **`include` / `exclude`** — bitmask flags via the `Features` enum to opt-in / opt-out of specific lowerings, overriding the target-derived defaults. Useful when you want to **drop a lowering** that the target would normally trigger (e.g., your audience supports relative color via a feature flag, even though caniuse data suggests they shouldn't).
- **`drafts`** — opt into draft-stage features (vendor-prefixed nesting variants, etc.). Mostly historical at our baseline.

For 99% of projects: set browserslist correctly, leave Lightning CSS at defaults, ship.

## Practical advice at our baseline

- **Author native CSS.** Use `oklch()`, nesting, container queries, logical properties, `:has()`, `@layer`, `light-dark()`, `color-mix()` directly. Lightning CSS won't slow you down by lowering — most of these are native.
- **Don't manually duplicate fallbacks** for features Lightning CSS will handle if your floor drops. If your floor stays at Chrome 125 / Safari 17.4 / Firefox 129, skip the manual duplication entirely. If your floor occasionally drops below for a release, set the lower browserslist for that release and let Lightning CSS auto-emit fallbacks.
- **Skip Lightning CSS for runtime features.** Anchor positioning, scroll-driven animations, view transitions, `@scope` — these are not Lightning CSS's job. Reach for runtime polyfills or flat fallbacks accordingly.
- **Don't ship `autoprefixer` alongside Lightning CSS.** Lightning CSS handles vendor prefixing; doubling up risks duplicate or stale prefixes.

## A small worked example

Source CSS at our baseline:

```css
@layer components {
  .card {
    background: oklch(from var(--surface) calc(l + 0.05) c h);
    container-type: inline-size;

    & .title {
      font-size: clamp(1rem, 2vw, 1.5rem);
    }

    @container (min-width: 400px) {
      padding: 2rem;
    }
  }
}
```

Lightning CSS output (with our baseline targets, minified):

```css
@layer components{.card{background:oklch(from var(--surface) calc(l + .05) c h);container-type:inline-size}.card .title{font-size:clamp(1rem,2vw,1.5rem)}@container (min-width:400px){.card{padding:2rem}}}
```

What changed: nesting was flattened (purely a code-organization difference, even though native nesting works); whitespace removed; numbers shortened (`0.05` → `.05`). No fallbacks emitted, no runtime polyfill, no behavior change.

That's the baseline reality: Lightning CSS makes your CSS faster to ship and parse. It does NOT add features to your audience's browsers.

## Cross-references

- `../build-tools/lightningcss-features.md` — build-tool angle: config, Vite integration, license, when to use.
- `../build-tools/postcss-preset-env.md` — alternative tool with stage-aware lowering.
- `../build-tools/browserslist-recipes.md` — the canonical browserslist for our floor.
- `../build-tools/vite-build-target.md` — Vite + Lightning CSS wiring.
- `./postcss-preset-env-stages.md` — cssdb stage detail; what features are at which stage.
- `./at-property-fallbacks.md` — what to do when build-time lowering can't help (e.g., `@scope`).
- `./anchor-positioning-polyfill.md` — runtime polyfill for a feature Lightning CSS cannot lower.
- `./scroll-timeline-polyfill.md` — same.
- `../meta/the-modern-baseline.md` — why the lowering matrix is so empty at our floor.
