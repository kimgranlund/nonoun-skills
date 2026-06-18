---
date: 2026-04-27
coverage: canonical
peers:
  - ../build-tools/vite-build-target.md
  - ../build-tools/postcss-preset-env.md
  - ../build-tools/browserslist-recipes.md
  - ../css-polyfills-and-shims/lightningcss-css-lowering.md
  - ../css-polyfills-and-shims/at-property-fallbacks.md
  - ../css-color-bugs/oklch-oklab-safari.md
  - ../css-color-bugs/relative-color-syntax.md
  - ../products/vite-6.md
primary_sources:
  - https://lightningcss.dev/ — Lightning CSS landing page; "extremely fast Rust-based CSS parser, transformer, bundler, and minifier"
  - https://lightningcss.dev/transpilation.html — feature list and lowering matrix
  - https://lightningcss.dev/options.html — CLI / API options including targets, include/exclude
  - https://lightningcss.dev/docs.html — getting started, browserslist integration
  - https://github.com/parcel-bundler/lightningcss — repository, issue tracker, license (MPL-2.0)
  - https://github.com/vitejs/vite/discussions/13835 — Stabilizing Lightning CSS in Vite
---

# Lightning CSS — what it lowers, and what it doesn't

Lightning CSS (formerly `parcel-css`) is the Parcel team's Rust-based CSS parser, transformer, minifier, and bundler. It's the default CSS pipeline in Bun, Parcel, and Vite (since Vite 6+ when configured), and it's the answer to "do I still need PostCSS just for autoprefixer and minification?" — at this baseline, almost certainly no.

> The TL;DR: at our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+), Lightning CSS will be doing very little lowering — most modern CSS is native. Its real value at this baseline is **fast minification + cleanup of vendor prefixes you accidentally authored**.

## What it is

From [lightningcss.dev](https://lightningcss.dev/): *"An extremely fast CSS parser, transformer, bundler, and minifier written in Rust."* The pitch:

- **~100× faster** than equivalent JS-based PostCSS pipelines on large files. ([CSS-Tricks measurement](https://css-tricks.com/so-you-want-to-give-up-css-pre-and-post-processors/))
- **Single binary** — no plugin ecosystem, all features built-in.
- **Browserslist-aware** — reads `.browserslistrc` and `package.json`'s `"browserslist"` field.
- **MPL-2.0 licensed**, maintained by Devon Govett (Parcel team) plus an active GitHub community.
- Bundles for Node, Bun, Deno; also has a CLI and a WASM build.

It does four things, in order: **parse → transform (lower features) → vendor-prefix → minify**. Each step is gated on the configured `targets`.

## Targets format

Lightning CSS uses a different shape than browserslist or esbuild. From [lightningcss.dev/transpilation.html](https://lightningcss.dev/transpilation.html), targets are a JS object encoding browser version as a 24-bit number — one byte per semver component:

```js
import { transform, browserslistToTargets } from 'lightningcss';
import browserslist from 'browserslist';

const targets = browserslistToTargets(browserslist('>= 0.25%'));
```

`browserslistToTargets` is the practical entry point — pass any browserslist query and Lightning CSS converts it to its internal format. You rarely write target objects by hand.

## What Lightning CSS lowers

The full feature list is on [lightningcss.dev/transpilation.html](https://lightningcss.dev/transpilation.html). At our baseline most are no-ops because the engines already support them; below is the lowering matrix annotated with what's *actually active* at Chromium 125+ / Safari 17.4+ / Firefox 129+.

### Color features

| Feature | Lowering target | Active at our baseline? |
|---|---|---|
| `oklch()`, `oklab()`, `lab()`, `lch()` | sRGB / `color()` fallback | **No** — all four engines ship these natively at our floor |
| `color()` with `display-p3`, `xyz`, `a98-rgb` | sRGB fallback | **No** — native at our floor (Firefox renders P3 mapped to sRGB; see `../css-color-bugs/display-p3-firefox-lag.md`) |
| `color-mix()` | static color | **No** — native everywhere at our floor; see `../css-color-bugs/color-mix-interpolation.md` for hue-divergence quirks |
| `light-dark()` | `@media (prefers-color-scheme)` | **No** — native at our floor; see `../css-color-bugs/light-dark-color-scheme.md` for the `color-scheme` requirement |
| Relative color syntax (`oklch(from base ...)`) | computed static color | **Possibly** — Safari 16.4+, but check exact sub-feature (some color-math is still being interop-tested) |
| `hwb()` | `rgb()` | **No** — native at our floor |
| Hex alpha (`#rrggbbaa`) | `rgba()` | **No** — native everywhere |
| Space-separated color notation (`rgb(255 0 0)`) | comma form | **No** — native everywhere |

### Selectors and nesting

| Feature | Lowering target | Active at our baseline? |
|---|---|---|
| CSS Nesting (`& .child`) | flat selectors | **No** — native at all three engines at our floor |
| `:is()` with multiple args | `-webkit-any` / `-moz-any` fallback | **No** — native everywhere |
| `:not()` with multiple args | repeated `:not()` chains | **No** — native |
| `:has()` | no fallback exists; passes through | n/a |
| `:dir()` | compiled to `:lang()` (approximation) | **Possibly** — `:dir()` not in older Firefox / Safari combos; verify per project |
| `:lang()` with multiple args | comma-list expansion | **No** — native |

### Layout and properties

| Feature | Lowering target | Active at our baseline? |
|---|---|---|
| Logical properties (`inline-size`, `block-size`, `padding-inline`, etc.) | physical-axis equivalents | **No** — native everywhere at our floor |
| `place-items`, `place-content`, `place-self` shorthand | longhand | **No** — native |
| Multi-value `overflow` shorthand | `overflow-x` / `overflow-y` | **No** — native |
| Two-value `display: inline flow-root` syntax | older single-keyword | Possibly — verify; mostly native |

### Math, media, gradients

| Feature | Lowering target | Active at our baseline? |
|---|---|---|
| `clamp()`, `round()`, `rem()`, `mod()`, `abs()`, `sign()`, trig, exp | static / `calc()` fallback | **`clamp()` no**; trig functions (`sin`, `cos`, etc.) are native at our floor; `round()`/`mod()`/`rem()` likely native, verify |
| Media query range syntax (`@media (200px <= width <= 800px)`) | `min-width` / `max-width` form | **No** — native at our floor |
| Custom media queries (`@custom-media --small (...)`) | inlined | **Yes** — still not native; Lightning CSS keeps lowering this |
| Double-position gradient stops (`linear-gradient(red 0% 50%, blue 50% 100%)`) | duplicated stops | **No** — native everywhere |

### Vendor prefixing

This is Lightning CSS's most-used feature at our baseline:

- Auto-applies `-webkit-` for older Safari quirks (e.g. `-webkit-backdrop-filter` mirrors of `backdrop-filter`).
- Removes prefixes that are no longer needed at the configured target (e.g. drops `-moz-` prefixes that Firefox shipped years ago).
- Uses a bundled prefix database — no external dependency on `caniuse-lite` for this part.

You can stop using `autoprefixer` if Lightning CSS is in the pipeline. ([CSS-Tricks](https://css-tricks.com/so-you-want-to-give-up-css-pre-and-post-processors/))

## What Lightning CSS does NOT do

The list of *non-features* matters:

- **No client-side polyfills.** Lightning CSS only does build-time lowering. It does not bundle `@oddbird/css-anchor-positioning`, `popover-polyfill`, or `flackr/scroll-timeline`. If a feature has no purely-syntactic lowering target — e.g. anchor positioning, container queries (in older browsers), `@scope` — Lightning CSS passes it through. See [`../css-polyfills-and-shims/anchor-positioning-polyfill.md`](../css-polyfills-and-shims/anchor-positioning-polyfill.md) and siblings.
- **No `@scope` polyfill.** `@scope` is in Chrome 118+, Safari 17.4+, but **not** Firefox 129–145 (shipping unflagged in 146+). Lightning CSS does not flatten `@scope` rules to non-scoped equivalents. There's no real polyfill for `@scope`; use feature queries and a flat fallback. See [`../css-polyfills-and-shims/at-property-fallbacks.md`](../css-polyfills-and-shims/at-property-fallbacks.md).
- **No `cssdb`-style staged-feature transforms.** Lightning CSS's feature set is curated, not stage-driven. It will not adopt a new Stage-2 CSSWG proposal until the maintainers add it to the Rust codebase. For staged features (some Stage-1/2 ideas not yet in Lightning CSS), you need [`postcss-preset-env`](./postcss-preset-env.md).
- **No PostCSS plugin ecosystem.** If your pipeline depends on `postcss-import`, custom plugins, or third-party transforms, you can't drop PostCSS entirely — but you can let Lightning CSS handle minification and prefixing while PostCSS handles the rest. See [`./postcss-preset-env.md`](./postcss-preset-env.md) for migration boundaries.
- **No image / asset processing.** Lightning CSS doesn't optimize images, hash asset URLs, or do anything beyond CSS text. Vite, Parcel, etc. handle that separately.

## Minification

Lightning CSS's minifier is aggressive and correct:

- Shortens hex colors (`#ffffff` → `#fff`).
- Merges redundant rules (`color: red; color: red;` → `color: red`).
- Combines `font-family`, `margin`, `padding` longhands into shorthands when safe.
- Drops vendor prefixes that don't apply to the target list.
- Removes whitespace, comments, and trailing semicolons.

Comparable to or better than `cssnano` in size; ~100× faster. ([Lightning CSS docs](https://lightningcss.dev/docs.html))

## Vite integration

Vite has shipped Lightning CSS support since v4 (opt-in via `css.transformer: 'lightningcss'`). From Vite 6 onwards it's the recommended path; some templates default to it. ([Vite + Lightning CSS stabilization discussion](https://github.com/vitejs/vite/discussions/13835))

```ts
// vite.config.ts — explicit Lightning CSS opt-in (still useful pre-Vite-7)
import { defineConfig } from 'vite';

export default defineConfig({
  css: {
    transformer: 'lightningcss',
    lightningcss: {
      targets: {
        chrome: 125 << 16,
        firefox: 129 << 16,
        safari: (17 << 16) | (4 << 8),
      },
    },
  },
});
```

For Vite ≥ 6 with browserslist set, the `lightningcss` block can be empty — Vite reads `.browserslistrc` and feeds it to Lightning CSS automatically. See [`./vite-build-target.md`](./vite-build-target.md) for the integrated recipe.

## At our baseline — the recipe

```
# .browserslistrc
chrome >= 125
firefox >= 129
safari >= 17.4
```

```ts
// vite.config.ts (Vite 6+)
import { defineConfig } from 'vite';

export default defineConfig({
  css: {
    transformer: 'lightningcss',
    // No explicit targets needed — Lightning CSS reads .browserslistrc
  },
  build: {
    cssMinify: 'lightningcss', // also enable for production minification
    target: ['chrome125', 'safari17.4', 'firefox129'],
  },
});
```

Notice `cssMinify: 'lightningcss'` is separate from `css.transformer`. The transformer runs in dev + build; the minifier only runs in build. Both should be set if you want the full Lightning CSS pipeline.

## Direct (non-Vite) usage

For Hugo, Eleventy, Astro, custom build scripts:

```js
import { transform } from 'lightningcss';
import { readFileSync } from 'node:fs';
import browserslist from 'browserslist';
import { browserslistToTargets } from 'lightningcss';

const code = readFileSync('src/styles.css');
const { code: output } = transform({
  filename: 'styles.css',
  code,
  minify: true,
  targets: browserslistToTargets(browserslist()),
});
```

Or use the CLI: `lightningcss --bundle --minify --targets '>= 0.25%' src/styles.css -o dist/styles.css`.

## When NOT to use Lightning CSS

Two scenarios:

1. **You depend on PostCSS plugins Lightning CSS doesn't replicate.** Tailwind v4 has its own engine — fine. But if you use `postcss-flexbugs-fixes`, `postcss-mixins`, or third-party PostCSS-only plugins, you'll lose them.
2. **You need Stage 0–1 CSS features that aren't in Lightning CSS yet.** Examples: experimental `@apply` directives, `cssnext`-era proposals. Use `postcss-preset-env` instead — see [`./postcss-preset-env.md`](./postcss-preset-env.md).

For most modern projects neither blocker applies, and Lightning CSS is the right answer.

## Cross-references

- [`./vite-build-target.md`](./vite-build-target.md) — Vite-side configuration; how `build.cssTarget` and Lightning CSS interact.
- [`./postcss-preset-env.md`](./postcss-preset-env.md) — when to keep PostCSS instead.
- [`./browserslist-recipes.md`](./browserslist-recipes.md) — the canonical query Lightning CSS reads.
- [`../css-polyfills-and-shims/lightningcss-css-lowering.md`](../css-polyfills-and-shims/lightningcss-css-lowering.md) — feature-by-feature lowering vs runtime polyfill split.
- [`../css-polyfills-and-shims/at-property-fallbacks.md`](../css-polyfills-and-shims/at-property-fallbacks.md) — features Lightning CSS doesn't lower.
- [`../css-color-bugs/oklch-oklab-safari.md`](../css-color-bugs/oklch-oklab-safari.md) — Safari color quirks Lightning CSS does not paper over.
- [`../products/vite-6.md`](../products/vite-6.md) — Vite-as-product polyfill story.
