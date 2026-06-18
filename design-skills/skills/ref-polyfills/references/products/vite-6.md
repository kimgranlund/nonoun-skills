---
date: 2026-04-27
coverage: extended
peers:
  - ../products/next-js-15.md
  - ../products/react-router-v7.md
  - ../products/astro.md
  - ../build-tools/vite-build-target.md
  - ../build-tools/lightningcss-features.md
  - ../build-tools/browserslist-recipes.md
  - ../transpilation/esbuild-targets.md
  - ../anti-patterns/target-es5-modern.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://vite.dev/blog/announcing-vite6 — Vite 6.0 release announcement (November 26, 2024)
  - https://vite.dev/blog/announcing-vite7 — Vite 7.0 release announcement (June 24, 2025); `baseline-widely-available` becomes default
  - https://vite.dev/config/build-options — `build.target`, `build.cssTarget`, `build.modulePreload`
  - https://vite.dev/guide/build — Build guide; "syntax transforms only, does not cover polyfills"
  - https://vite.dev/guide/api-environment — Environment API (Vite 6 introduction)
  - https://www.npmjs.com/package/@vitejs/plugin-legacy — plugin-legacy package reference
  - https://github.com/vitejs/vite/tree/main/packages/plugin-legacy — plugin-legacy source + README
---

# Vite 6 / 7 — polyfill posture

Vite is the dominant non-Next.js build tool — the basis for React Router v7's framework mode, Astro, SvelteKit, Nuxt 3+, Solid Start, and most modern SPA starter templates. This file is the **product-level** view: how Vite-as-a-product handles polyfills, what its defaults imply, and what to watch for. The **config-level** companion is [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md), which goes deep on `build.target`.

> The TL;DR: Vite 7 (June 2025) defaults `build.target` to `'baseline-widely-available'`, which expands to `['chrome111', 'edge111', 'firefox114', 'safari16.4']` — older than our Chromium 125+ / Safari 17.4+ / Firefox 129+ floor. Override it. Avoid `@vitejs/plugin-legacy` at this baseline — it's an IE/legacy bridge that ships SystemJS to every visitor.

## Version + ship-date matrix

| Vite version | Released | Default `build.target` |
|---|---|---|
| 5.x | December 2023 | `'modules'` → `['es2020', 'edge88', 'firefox78', 'chrome87', 'safari14']` |
| 6.x | November 26, 2024 | `'modules'` (unchanged); `'baseline-widely-available'` added as **opt-in** |
| 7.x | June 24, 2025 | `'baseline-widely-available'` → `['chrome111', 'edge111', 'firefox114', 'safari16.4']` |

The big shifts:

- **Vite 6** ([release post](https://vite.dev/blog/announcing-vite6)) introduced the [Environment API](https://vite.dev/guide/api-environment) and the new `'baseline-widely-available'` keyword *as an option*, but kept `'modules'` as default for backward compatibility.
- **Vite 7** ([release post](https://vite.dev/blog/announcing-vite7)) flipped the default to `'baseline-widely-available'`. This is a breaking change relative to Vite 6 defaults; older starter templates that don't set `build.target` explicitly silently inherit the new floor.

The Vite docs spell this out: *"The set of browsers will be updated on each major Vite release to match the list of minimum browser versions compatible with Baseline Widely Available features."* So `'baseline-widely-available'` is a **moving target**, pinned to whatever Baseline considered widely-available on the date of that Vite major. In Vite 7 (June 2025), the resolved date is 2026-01-01.

## What Vite ships and doesn't ship

The load-bearing line from the [Vite build guide](https://vite.dev/guide/build): *"Vite only handles syntax transforms and does not cover polyfills."* That sentence is the entire polyfill posture in eight words.

What Vite *does*:

- **esbuild for development.** Source files are transformed on demand; no bundling in dev.
- **Rollup for production builds.** (Vite 7 added experimental Rolldown support; eventually replaces Rollup but not yet stable as default.)
- **Lightning CSS** for CSS in Vite 6+ when configured, or the default since Vite 7. See [`../build-tools/lightningcss-features.md`](../build-tools/lightningcss-features.md). Otherwise PostCSS.
- **Module preload polyfill** — a tiny shim Vite injects to handle `<link rel="modulepreload">` in browsers that haven't implemented it. Toggleable via `build.modulePreload.polyfill` (default `true`).

What Vite *does NOT* do:

- **No runtime polyfills for JS APIs.** If your code calls `URLPattern`, `Temporal`, `Object.groupBy()`, `Array.prototype.toSorted`, you ship the unfilled call. Vite passes them through. Bring your own polyfill — see [`../runtime-polyfills/`](../runtime-polyfills/).
- **No core-js injection.** Unlike `@babel/preset-env` with `useBuiltIns: 'usage'`, Vite has no equivalent automatic-detection mode. By design.
- **No CSS-feature runtime shimming.** Lightning CSS lowers what it can at build time (logical props on older engines, color() fallbacks, etc.); Vite does not bundle `@oddbird/css-anchor-positioning` or `popover-polyfill` for you. See [`../css-polyfills-and-shims/`](../css-polyfills-and-shims/).
- **No browserslist auto-discovery for `build.target`.** Lightning CSS reads `.browserslistrc`; esbuild does not. You must spell out engine versions in `build.target` or use [`browserslist-to-esbuild`](https://github.com/marcofugaro/browserslist-to-esbuild). See [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md).

## `@vitejs/plugin-legacy` — the anti-pattern

[`@vitejs/plugin-legacy`](https://www.npmjs.com/package/@vitejs/plugin-legacy) generates a second bundle transformed by `@babel/preset-env` (or `vite-plugin-legacy-swc` for an SWC variant), emitted as SystemJS modules and paired with `<script nomodule>` so legacy browsers without ESM support can still load. It also injects a polyfills chunk based on usage detection (`useBuiltIns: 'usage'`).

The plugin's own README is honest: *"Vite's minimum browser support target is native ESM dynamic import, and `import.meta`. This plugin provides support for legacy browsers that do not support those features when building for production."*

**At the expert-polyfills baseline, `@vitejs/plugin-legacy` is an anti-pattern.** Every supported engine has ESM, dynamic import, and `import.meta` shipped natively. Adding the plugin:

- Doubles the build output (modern + legacy chunks emitted, deployed, served).
- Requires `terser` as a peer dep.
- Ships SystemJS runtime + core-js polyfills to every visitor whose browser's UA can't be classified as "modern" before JS runs.
- Inflates Time-to-Interactive measurably — 30–80 KB of polyfill payload depending on usage detection.

The only legitimate use is supporting IE 11 or pre-Safari-14 audiences. At Chromium 125+ / Safari 17.4+ / Firefox 129+, that's a contradiction. Strip it out. See [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md).

## CSS — Lightning CSS as default

Vite 6+ uses Lightning CSS for CSS transformation when `css.transformer: 'lightningcss'` is configured; Vite 7+ recommends it as the default path in starter templates. From [`../build-tools/lightningcss-features.md`](../build-tools/lightningcss-features.md):

- Reads `.browserslistrc` automatically when no explicit `targets` is set.
- Lowers very little at our baseline — most modern CSS is native at Chromium 125+ / Safari 17.4+ / Firefox 129+.
- Handles vendor prefix injection / removal, minification.
- Does **not** inject runtime CSS polyfills (anchor positioning, popover, scroll-driven animations).

When Vite is configured with both `build.cssTarget` and a browserslist, the dev/build pipeline reads them differently:

- `build.cssTarget` — read by Lightning CSS / esbuild's CSS path. Defaults to mirroring `build.target` if unset.
- `package.json` `"browserslist"` — read by Lightning CSS for CSS-feature lowering decisions.

If both are present, Vite + Lightning CSS reconcile them; if only browserslist is present, Vite defers to it for CSS only — *not* for JS.

## Recommended setup at our baseline

```ts
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: ['chrome125', 'safari17.4', 'firefox129'],
    cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
    minify: 'esbuild',
    cssMinify: 'lightningcss',
    sourcemap: true,
  },
});
```

If you also keep a `package.json` `"browserslist"` for tooling parity (autoprefixer-style consumers, postcss-preset-env, future ports):

```jsonc
// package.json
{
  "browserslist": [
    "chrome >= 125",
    "firefox >= 129",
    "safari >= 17.4",
    "not dead"
  ]
}
```

You can deduplicate via [`browserslist-to-esbuild`](https://github.com/marcofugaro/browserslist-to-esbuild) if you want one source of truth — at the cost of one transitive dependency. See [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md).

## Plugin ecosystem and polyfills

Three Vite plugin patterns to know:

- **`@vitejs/plugin-react` vs `@vitejs/plugin-react-swc`** — Babel-based vs SWC-based React transform. SWC variant is faster; Babel variant has more plugin compatibility. Neither injects runtime polyfills.
- **`vite-plugin-pwa`** — adds a service worker. Service Worker registration is fully shipped at our baseline; no polyfill needed.
- **`vite-plugin-legacy-swc`** — community SWC port of plugin-legacy. Same anti-pattern verdict at our baseline.

If a plugin's README mentions polyfills or "broad compatibility," check whether it ships polyfill code into the bundle. Many starter templates carry plugin-legacy invocations as defaults you'd be wise to remove.

## When Vite is the wrong choice

Two scenarios where you'd pick something else:

1. **Server-rendered React with extensive routing + data loading** — Next.js (App Router) or React Router v7 framework mode are richer. Vite alone is great for SPAs, less great for full-stack frameworks unless wrapped (e.g., Vinxi, vite-plugin-ssr).
2. **Static-content-heavy sites with islands** — Astro is purpose-built. See [`./astro.md`](./astro.md).

For everything else — SPAs, libraries, design systems, demo apps, internal tools — Vite is the modern default.

## Cross-references

- [`./next-js-15.md`](./next-js-15.md) — Next.js's polyfill story (the SWC-default alternative)
- [`./react-router-v7.md`](./react-router-v7.md) — React Router framework mode runs on Vite; same posture applies
- [`./astro.md`](./astro.md) — Astro runs on Vite; same posture, different mental model
- [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md) — `build.target` deep dive at the config level
- [`../build-tools/lightningcss-features.md`](../build-tools/lightningcss-features.md) — what Lightning CSS lowers under Vite
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical baseline query
- [`../transpilation/esbuild-targets.md`](../transpilation/esbuild-targets.md) — the engine Vite ships with
- [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) — why aggressive lowering hurts at this baseline
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what our floor means in features
