---
date: 2026-04-27
coverage: extended
peers:
  - ../build-tools/lightningcss-features.md
  - ../build-tools/vite-build-target.md
  - ../build-tools/browserslist-recipes.md
  - ../css-polyfills-and-shims/postcss-preset-env-stages.md
  - ../css-polyfills-and-shims/lightningcss-css-lowering.md
  - ../products/vite-6.md
primary_sources:
  - https://preset-env.cssdb.org/ — postcss-preset-env home; "Convert modern CSS into something browsers understand"
  - https://preset-env.cssdb.org/features/ — full feature list with cssdb stage tags
  - https://cssdb.org/ — CSS feature staging database
  - https://github.com/csstools/cssdb/blob/main/STAGES.md — exact stage definitions (0-4)
  - https://github.com/csstools/postcss-plugins/tree/main/plugin-packs/postcss-preset-env — repo + options reference
  - https://www.npmjs.com/package/postcss-preset-env — npm metadata, latest version
  - https://github.com/csstools/postcss-plugins/blob/main/plugin-packs/postcss-preset-env/CHANGELOG.md — release history
---

# postcss-preset-env — staged CSS feature lowering via PostCSS

`postcss-preset-env` is a PostCSS plugin pack that uses the `cssdb` feature catalog plus a browserslist target to decide which CSS features to lower. It's been the de-facto "Babel for CSS" for nearly a decade. At our baseline, much of what it lowered is now native — but its stage-aware model still has uses Lightning CSS doesn't cover.

> The TL;DR: at our baseline, prefer Lightning CSS for speed and to drop the PostCSS dependency entirely. Reach for `postcss-preset-env` when (a) you depend on the broader PostCSS plugin ecosystem, or (b) you want stage-driven feature inclusion (Stage 1 / Stage 0 experimental features Lightning CSS doesn't ship).

## What it is

From [preset-env.cssdb.org](https://preset-env.cssdb.org/): *"PostCSS Preset Env lets you convert modern CSS into something most browsers can understand, determining the polyfills you need based on your targeted browsers or runtime environments."*

The model:

1. Read the project's `browserslist` query to determine the engine floor.
2. Look up each Stage-N feature in [`cssdb`](https://cssdb.org/) — the curated CSS feature staging database.
3. Apply the corresponding PostCSS plugin if (a) the feature's stage is ≥ the configured stage threshold, AND (b) any browser in the target list lacks native support.

It bundles ~30 PostCSS plugins, one per cssdb feature, plus `autoprefixer`. License: MIT (the csstools org as a whole).

## cssdb stages — what they mean

The exact stage definitions, [from the cssdb STAGES.md](https://github.com/csstools/cssdb/blob/main/STAGES.md):

| Stage | Name | Description |
|---|---|---|
| **0** | Aspirational | "This is a silly idea." Unofficial / Editor's Draft championed by a W3C WG member; highly unstable. |
| **1** | Experimental | "This idea might not be silly." Editor's Draft / early Working Draft; a real problem is recognized, but no committed solution. |
| **2** | Allowable | "This idea is not silly." Working Draft championed by a W3C Working Group; relatively unstable, tied to a specific solution. |
| **3** | Embraced | "This idea is becoming part of the web." Candidate Recommendation; usually 2+ vendor implementations; little expected change. |
| **4** | Standardized | "This idea is part of the web." W3C Recommendation; implemented by all recognized vendors. Native everywhere. |

These map roughly to W3C spec maturity. Stage 4 is "you don't need a polyfill, just use it." Stage 0 is "this is a research-survey experiment."

## The `stage` config

The default is `stage: 2` — postcss-preset-env applies Stage 2, 3, and 4 features (the "embraced + allowable + stable" superset). Setting `stage: 3` includes only embraced + stable; `stage: 1` adds experimental; `stage: 0` adds everything including aspirational.

```js
// postcss.config.js
module.exports = {
  plugins: [
    require('postcss-preset-env')({
      stage: 2,           // default
      browsers: 'last 2 versions, not dead',
    }),
  ],
};
```

There's also `stage: false` — disables the stage filter entirely; only features explicitly enabled in `features` are processed.

## Per-feature `features` config

Override the stage default per feature:

```js
require('postcss-preset-env')({
  stage: 3,
  features: {
    'nesting-rules': true,           // enable Stage-2 feature even though stage:3
    'custom-properties': false,      // disable a Stage-4 feature you don't want lowered
    'oklab-function': { preserve: true }, // pass plugin-specific config
  },
});
```

Feature IDs match cssdb's slugs — see [preset-env.cssdb.org/features/](https://preset-env.cssdb.org/features/) for the full list. Each feature shows its current stage, browser-support data, and the underlying PostCSS plugin.

## At our baseline — what's still worth lowering

At Chromium 125+ / Safari 17.4+ / Firefox 129+, almost every Stage-3 and Stage-4 feature is native. The interesting question is **which Stage-2 features are still worth running through postcss-preset-env**.

A pragmatic survey:

| Feature | Stage | Status at our baseline | Lower via preset-env? |
|---|---|---|---|
| Custom Properties (CSS Variables) | 4 | Native everywhere | No |
| `:has()` | 4 | Native (Chrome 105, Firefox 121, Safari 15.4) | No |
| CSS Nesting (`& .child`) | 4 | Native (Chrome 120, Firefox 117, Safari 17.2) | No |
| Logical properties | 4 | Native everywhere | No |
| Cascade layers (`@layer`) | 4 | Native (Chrome 99, Firefox 97, Safari 15.4) | No |
| `aspect-ratio` | 4 | Native everywhere | No |
| Container queries | 4 | Native (Chrome 105, Firefox 110, Safari 16) | No |
| Custom media queries (`@custom-media`) | 2 | **Not native anywhere yet** | **Yes** — preset-env still useful |
| `@nest` (older nesting syntax) | 3 → deprecated | Use modern nesting | n/a |
| Color functional notation (`rgb(255 0 0)`) | 4 | Native everywhere | No |
| Hex with alpha (`#rrggbbaa`) | 4 | Native everywhere | No |
| `light-dark()` | 3 | Native everywhere at our floor | No |
| `oklch()` / `oklab()` | 3 | Native everywhere at our floor | No |
| Relative color syntax | 2 | Native at our floor (Chrome 119+, Safari 16.4+, Firefox 128+) | No |
| `@scope` | 2 | NOT in Firefox 129–145; preset-env doesn't polyfill | n/a |

The honest assessment: at our baseline, the only Stage-2 feature you'd genuinely lower is **custom media queries** (`@custom-media`), which has no shipping native implementation in any engine. Everything else is either native or unpolyfillable.

If your baseline is lower than ours (last 2 Firefox ESRs, broader audience), the picture shifts — preset-env still earns its keep. At ours, the value is mostly historical.

## All the configuration options

From the [postcss-preset-env options reference](https://github.com/csstools/postcss-plugins/tree/main/plugin-packs/postcss-preset-env):

| Option | Purpose | Default |
|---|---|---|
| `stage` | Minimum cssdb stage to include (0–4 or `false`) | `2` |
| `minimumVendorImplementations` | Filter features by # of shipping vendors (0–3); `2` is the recommended stability floor | `0` |
| `features` | Per-feature opt-in / opt-out / config | `{}` |
| `browsers` | Override the browserslist query (string or array) | reads `.browserslistrc` |
| `env` | Browserslist environment name (e.g. `'production'` vs `'development'`) | `'production'` |
| `autoprefixer` | Pass options to bundled autoprefixer; `false` disables | `{}` |
| `preserve` | Whether to keep the un-lowered original alongside the polyfill | `true` (per-plugin) |
| `enableClientSidePolyfills` | Allow features that need a runtime browser library | `false` |
| `insertBefore` / `insertAfter` | Insert other PostCSS plugins at specific stages | `null` |
| `debug` | Console-log which features got enabled and why | `false` |
| `logical` | Configure direction for logical-property lowering (`{ blockDirection, inlineDirection }`) | `{}` |

The two newest options worth knowing:

### `minimumVendorImplementations`

Filters out features that haven't shipped in ≥ N major engines. **Recommended `2`** for stability — it excludes features that only Chromium or only Firefox has shipped, which can drift unpredictably between preset-env updates. ([npm postcss-preset-env](https://www.npmjs.com/package/postcss-preset-env))

### `enableClientSidePolyfills`

Default `false`. Some features (e.g. legacy `image-set()` polyfills) require a runtime library shipped to the browser. Setting this to `false` keeps preset-env build-time-only and avoids surprise client-bundle additions. Leave it false unless you specifically need a feature that requires a runtime polyfill — and then carefully evaluate whether that polyfill is worth its bytes at your baseline.

## Lightning CSS vs postcss-preset-env — a deciding tree

Both tools transform modern CSS into older equivalents. They overlap heavily but differ in scope, speed, and ecosystem fit:

| Dimension | Lightning CSS | postcss-preset-env |
|---|---|---|
| Speed | Rust, ~100× faster on large files | Node-based, slower |
| Feature surface | Curated, hand-coded in Rust | Curated via cssdb (~30+ features) |
| Stage awareness | None — lower or don't | Yes — `stage: 0–4` selector |
| PostCSS plugin compatibility | None directly; can be a PostCSS plugin via [`postcss-lightningcss`](https://github.com/onigoetz/postcss-lightningcss) | Fully compatible (it IS PostCSS) |
| Browserslist auto-discovery | Yes (`browserslistToTargets`) | Yes |
| Handles vendor prefixes | Yes (built-in) | Yes (via bundled `autoprefixer`) |
| Minification | Built-in, fast | Out of scope (use `cssnano`) |
| `@scope` lowering | No | No |
| Custom media queries | No (passes through) | Yes (still useful) |
| Anchor positioning polyfill | No | No |
| License | MPL-2.0 | MIT (csstools) |

### Use Lightning CSS when

- Build-time speed matters (large CSS bundles, monorepos with many packages).
- You're on Vite, Parcel, or Bun where Lightning CSS is the default path.
- You don't need Stage 0–1 experimental features.
- You want to drop PostCSS as a dependency entirely.
- You're combining transformer + minifier in one pass.

### Use postcss-preset-env when

- You need stage-aware feature inclusion (e.g. opt into a Stage-1 experimental feature for prototyping).
- You depend on other PostCSS plugins (`postcss-import`, `postcss-mixins`, `postcss-flexbugs-fixes`, custom in-house plugins).
- You want a familiar PostCSS pipeline without changing tooling.
- Your CSS is small enough that build-time speed isn't load-bearing.
- You need to lower `@custom-media` (which Lightning CSS doesn't do).

### Use both?

Possible, via [`postcss-lightningcss`](https://github.com/onigoetz/postcss-lightningcss) — runs Lightning CSS as a PostCSS plugin. Useful when you want Lightning's vendor-prefixing + minification but still need a PostCSS plugin chain elsewhere. Adds two dependencies and a layer of configuration; only worth it for narrow cases.

## Migration: from postcss-preset-env to Lightning CSS

If your baseline matches ours and your PostCSS stack is just `postcss-preset-env + autoprefixer + cssnano`, the migration is a straight swap:

1. Remove `postcss.config.js` (or empty it out).
2. Set `css.transformer: 'lightningcss'` and `build.cssMinify: 'lightningcss'` in `vite.config.ts`. (See [`./vite-build-target.md`](./vite-build-target.md).)
3. Set `.browserslistrc` to the canonical baseline query.
4. `npm uninstall postcss postcss-preset-env autoprefixer cssnano`.
5. Run a visual diff (`backstop`, Playwright snapshots) to verify nothing regressed.

Common gotchas:

- **`@custom-media` is the most likely regression** — Lightning CSS doesn't lower it. If you use `@custom-media`, either inline the queries by hand, or stay on PostCSS for that one transform.
- **Plugin-specific options** that postcss-preset-env exposed (e.g. `oklab-function: { preserve: true }`) don't translate; Lightning CSS has its own `include`/`exclude` flags via the `Features` enum.
- **Source maps** — both produce them, but column offsets can differ slightly under aggressive minification. If your error monitoring is column-precise, re-upload source maps after the switch.

## At our baseline — the recipe (postcss-preset-env path)

If you're keeping PostCSS:

```js
// postcss.config.js
module.exports = {
  plugins: [
    require('postcss-preset-env')({
      stage: 3,
      minimumVendorImplementations: 2,
      enableClientSidePolyfills: false,
      features: {
        'custom-media-queries': true,  // explicit; native nowhere yet
      },
    }),
    require('cssnano')({ preset: 'default' }),
  ],
};
```

```
# .browserslistrc
chrome >= 125
firefox >= 129
safari >= 17.4
```

`stage: 3` is more conservative than the default `2` and matches our "modern-first" stance — only embrace Stage 3+ features that have multi-vendor commitment. `minimumVendorImplementations: 2` adds a second guardrail.

## Cross-references

- [`./lightningcss-features.md`](./lightningcss-features.md) — the faster alternative; recommended at our baseline.
- [`./vite-build-target.md`](./vite-build-target.md) — how Vite invokes both Lightning CSS and PostCSS.
- [`./browserslist-recipes.md`](./browserslist-recipes.md) — the canonical query both tools read.
- [`../css-polyfills-and-shims/postcss-preset-env-stages.md`](../css-polyfills-and-shims/postcss-preset-env-stages.md) — feature-by-feature stage map.
- [`../css-polyfills-and-shims/lightningcss-css-lowering.md`](../css-polyfills-and-shims/lightningcss-css-lowering.md) — what each tool actually lowers.
- [`../products/vite-6.md`](../products/vite-6.md) — Vite-as-product polyfill story.
