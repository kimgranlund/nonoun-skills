---
date: 2026-04-27
coverage: canonical
peers:
  - ../build-tools/lightningcss-features.md
  - ../build-tools/postcss-preset-env.md
  - ../build-tools/browserslist-recipes.md
  - ../build-tools/esbuild-config.md
  - ../build-tools/tsconfig-lib-target.md
  - ../products/vite-6.md
  - ../anti-patterns/target-es5-modern.md
  - ../anti-patterns/preset-env-no-browserslist.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://vite.dev/config/build-options — Vite build options reference (build.target, build.cssTarget)
  - https://vite.dev/guide/build — Vite production build guide; "syntax transforms only, does not cover polyfills"
  - https://vite.dev/blog/announcing-vite7 — Vite 7 release (June 24, 2025), `baseline-widely-available` becomes default
  - https://vite.dev/blog/announcing-vite6 — Vite 6 release (November 26, 2024)
  - https://github.com/vitejs/vite/commit/4a8aa82556eb2b9e54673a6aac77873e0eb27fa9 — feat!: bump build.target and name it baseline-widely-available
  - https://github.com/vitejs/vite/issues/19358 — Bump default build.target proposal/discussion
  - https://www.npmjs.com/package/@vitejs/plugin-legacy — plugin-legacy package reference
  - https://github.com/vitejs/vite/tree/main/packages/plugin-legacy — plugin-legacy source + README
---

# Vite — `build.target` and the modern-first story

Vite is the most-deployed build tool in the modern web ecosystem. Its `build.target` config decides what syntax esbuild lowers, and (transitively, via `build.cssTarget`) what CSS Lightning CSS lowers. Get this right and you stop shipping transpiled async generators to Chrome 130; get it wrong and you ship them anyway.

> The TL;DR: at our baseline, set `build.target: ['chrome125', 'safari17.4', 'firefox129']` explicitly. Don't rely on Vite's default — it's tuned to a wider audience than ours.

## What `build.target` does

From the [Vite build options reference](https://vite.dev/config/build-options): `build.target` is a list of browser engines (or an esbuild syntax level like `'es2020'`) that controls which JS features esbuild will lower during production build. It does **not** apply to dev — dev mode targets `esnext` (modern engines only) by design.

The companion option is `build.cssTarget`, which controls what Lightning CSS / esbuild lowers in CSS. **Default**: same as `build.target`. Vite's docs note `build.cssTarget` exists for cases where you need different CSS targets than JS — e.g. targeting an unusual engine whose CSS support is older than its JS.

A critical corollary from the Vite build guide: *"Vite only handles syntax transforms and does not cover polyfills."* If your code calls `Object.groupBy()` or `URLPattern`, Vite will emit those identifiers as-is. Lowering targets does not add a runtime polyfill. That's a separate decision — see `../runtime-polyfills/`.

## Default in current Vite (Vite 7+)

Since Vite 7.0 (released June 24, 2025), the default `build.target` is the special string `'baseline-widely-available'`, which expands to:

```
['chrome111', 'edge111', 'firefox114', 'safari16.4']
```

These are the engines that supported the [Baseline Widely Available](https://web-platform-dx.github.io/web-features/) feature set on **2026-01-01**. Per the Vite docs, the special string is rebound on each major Vite release — so what `'baseline-widely-available'` *means* will drift forward over time, but Vite 7 specifically pins to the values above.

**Why this matters at our baseline.** The expert-polyfills baseline is **Chromium 125+ / Safari 17.4+ / Firefox 129+** — well above Vite 7's default. Adopting Vite's default at our baseline means **over-lowering**: esbuild will downlevel features (top-level await, optional chaining, nullish coalescing assignment, etc.) that every supported engine ships natively. Bundle size grows; native fast paths get bypassed. See [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md).

## Vite 5 vs Vite 6 vs Vite 7 — the version matrix

| Vite version | Released | Default `build.target` | Resolves to |
|---|---|---|---|
| 5.x | December 2023 | `'modules'` | `['es2020', 'edge88', 'firefox78', 'chrome87', 'safari14']` |
| 6.x | November 26, 2024 | `'modules'` (unchanged) | `['es2020', 'edge88', 'firefox78', 'chrome87', 'safari14']` |
| 7.x | June 24, 2025 | `'baseline-widely-available'` | `['chrome111', 'edge111', 'firefox114', 'safari16.4']` |

Vite 6 introduced `'baseline-widely-available'` as an *option* but kept `'modules'` as the default — the changeover happened in Vite 7. Project teams who upgraded major-version-by-major-version may have inherited the older `'modules'` default from a Vite 5/6 era and never revisited it. Audit before assuming.

## Recommended target at this baseline

Two valid forms, with different trade-offs:

### Option A — explicit per-engine (preferred)

```ts
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: ['chrome125', 'safari17.4', 'firefox129'],
    cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
    minify: 'esbuild',
  },
});
```

This is the most direct mapping to the expert-polyfills baseline. esbuild gets exact engine versions and only lowers the small set of features missing from any one engine. Lightning CSS (which Vite invokes for CSS at this version) reads `cssTarget` the same way.

### Option B — `'es2024'` (syntax-only)

```ts
build: {
  target: 'es2024',
}
```

`es2024` is an esbuild syntax keyword; it tells esbuild "lower nothing newer than the ES2024 spec." It does **not** describe CSS, only JS. At our baseline every engine fully supports ES2024, so this is functionally a no-op for syntax — useful when you genuinely don't want any lowering and trust your authoring not to use ES2025+ proposals (decorators, etc.).

The downside: `'es2024'` doesn't constrain Lightning CSS at all. You still need `cssTarget` set explicitly if you want CSS lowered to a particular engine floor. So in practice option A is more complete.

## What Vite transpiles automatically

Out of the box, Vite handles:

- **TypeScript** — esbuild strips types. **No type-check during build** — TS is not validated, only stripped. (Run `tsc --noEmit` in CI for type-safety.)
- **JSX** — esbuild compiles to JS. Defaults match React conventions; configurable via `esbuild.jsx`.
- **CSS modules** — `*.module.css` files get scoped class names, processed via Lightning CSS or PostCSS.
- **PostCSS plugins** — if a `postcss.config.js` exists, plugins run before Lightning CSS / esbuild minification.
- **Image / asset imports** — `import logo from './logo.svg'` returns a hashed URL; assets emitted to `dist/assets/`.
- **Dynamic imports** — `import('./foo')` becomes a code-split chunk.
- **CSS at-imports** — `@import './foo.css'` resolves and inlines.

It also handles Lightning CSS-driven CSS lowering automatically when `build.cssTarget` is set — see [`./lightningcss-features.md`](./lightningcss-features.md) for the feature list.

## What Vite does NOT transpile or polyfill

This is the load-bearing list — every item is a frequent surprise:

- **Decorators** — esbuild passes them through if the TypeScript compiler emits them. Stage-3 decorator syntax (`2023-11`) is not lowered by esbuild itself; if your target engines don't support decorators natively, you need Babel or SWC. See [`../transpilation/decorators-stage-3.md`](../transpilation/decorators-stage-3.md).
- **Runtime polyfills** — no automatic `core-js` injection. If your code uses `URLPattern`, `Temporal`, or `Object.groupBy()` and those aren't shipped at your target floor, you ship the unfilled code or you bring your own polyfill. See `../runtime-polyfills/`.
- **View Transitions / Popover / Anchor Positioning** — these are platform APIs (CSS + JS), native at our baseline. Vite passes them through; gating is your responsibility (`@supports`, JS feature detection).
- **`@property`-based custom-property fallbacks** — Lightning CSS does not synthesize `@property` registrations; if you author them they pass through. See [`../css-polyfills-and-shims/at-property-fallbacks.md`](../css-polyfills-and-shims/at-property-fallbacks.md).
- **JSX runtime selection** — defaults to React's automatic runtime; if you need Preact / Solid / Vue, configure `esbuild.jsxImportSource` or use the relevant Vite plugin.

## At our baseline — the recipe

```ts
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: ['chrome125', 'safari17.4', 'firefox129'],
    cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
    minify: 'esbuild',
    sourcemap: true,
  },
  esbuild: {
    // Optional: drop console + debugger in production
    drop: ['console', 'debugger'],
  },
});
```

If you also want to drive `cssTarget` from a shared `.browserslistrc` (next section), you can omit `cssTarget` — Vite will read browserslist for CSS automatically.

## Browserslist coupling

Vite's interaction with `.browserslistrc` (and `package.json` `"browserslist"`) is asymmetric:

- **`build.cssTarget`** — if not set explicitly, Vite + Lightning CSS will read browserslist and use that for CSS lowering. ([Vite + Lightning CSS integration discussion](https://github.com/vitejs/vite/discussions/13835))
- **`build.target`** — does **NOT** auto-discover from browserslist. You must spell out engine versions explicitly (or use the `'baseline-widely-available'` / `'esXXXX'` keywords). esbuild itself has [no browserslist support](https://github.com/evanw/esbuild/issues/121); Vite does not bridge it.

If you want a single source of truth for both CSS and JS targets, the practical pattern is:

```
# .browserslistrc
chrome >= 125
firefox >= 129
safari >= 17.4
```

```ts
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: ['chrome125', 'safari17.4', 'firefox129'], // duplicate of browserslist; required
    // cssTarget omitted — Lightning CSS reads .browserslistrc
  },
});
```

The duplication smells but is unavoidable until esbuild ships browserslist support (long-running issue, no resolution as of April 2026). Some teams use [`browserslist-to-esbuild`](https://github.com/marcofugaro/browserslist-to-esbuild) as a stop-gap:

```ts
import browserslistToEsbuild from 'browserslist-to-esbuild';
import { defineConfig } from 'vite';

export default defineConfig({
  build: {
    target: browserslistToEsbuild(),
  },
});
```

That reads the project's browserslist config and emits an esbuild-compatible target array. Adds one transitive dependency; your call whether the deduplication is worth it. See [`./browserslist-recipes.md`](./browserslist-recipes.md) for the full browserslist tour.

## `@vitejs/plugin-legacy` — when (not) to use it

[`@vitejs/plugin-legacy`](https://www.npmjs.com/package/@vitejs/plugin-legacy) generates a second bundle transformed by `@babel/preset-env` and emitted as SystemJS modules, paired with `<script nomodule>` tags so legacy browsers without ESM support can still load. It also injects a polyfills chunk based on usage detection (`useBuiltIns: 'usage'`).

The README's load-bearing line: *"Vite's minimum browser support target is native ESM dynamic import, and `import.meta`. This plugin provides support for legacy browsers that do not support those features when building for production."*

**At the expert-polyfills baseline, `@vitejs/plugin-legacy` is an anti-pattern.** Every supported engine has ESM, dynamic import, and `import.meta` built in. Adding the plugin:

- Doubles the build output (modern + legacy chunks).
- Requires `terser` as a peer dep.
- Ships SystemJS runtime + core-js polyfills to every visitor whose browser can't tell modern from legacy until JS runs.
- Inflates Time-to-Interactive measurably.

The only reason to enable it is if your audience genuinely includes IE11 or pre-Safari-14. At Chromium 125+ / Safari 17.4+ / Firefox 129+, that's a contradiction. See [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md).

## Common Vite-target mistakes (the audit checklist)

The five drift patterns most likely to appear in real projects:

1. **No `build.target` set at all on Vite 5/6 projects.** Default is `'modules'`, which keeps Safari 14 and Firefox 78 in the support floor. Bundle is over-lowered relative to your actual audience.
2. **`build.target: 'es2015'`** copy-pasted from a 2019 webpack config. Defeats every modern engine fast path; see [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md).
3. **`@vitejs/plugin-legacy` enabled by default in a Vue / React starter template.** Some templates ship it for "broadest compatibility." Strip it unless you genuinely need IE11.
4. **`build.cssTarget` left at default while `build.target` is explicit.** They diverge silently — CSS lowers to one floor, JS to another. Set both, or neither.
5. **`browserslist` config in `package.json` that contradicts `build.target`.** Lightning CSS reads browserslist, esbuild reads `build.target`. If they disagree your CSS and JS targets are split. Audit both.

## Cross-references

- [`./lightningcss-features.md`](./lightningcss-features.md) — what Lightning CSS lowers when Vite hands it CSS.
- [`./postcss-preset-env.md`](./postcss-preset-env.md) — the alternative CSS-lowering path via PostCSS.
- [`./browserslist-recipes.md`](./browserslist-recipes.md) — the canonical baseline query in production-ready forms.
- [`./esbuild-config.md`](./esbuild-config.md) — what `build.target` actually does inside esbuild.
- [`../products/vite-6.md`](../products/vite-6.md) — Vite-as-product polyfill story (vs this file's config-level focus).
- [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) — why `target: 'es5'` is wrong at this baseline.
- [`../anti-patterns/preset-env-no-browserslist.md`](../anti-patterns/preset-env-no-browserslist.md) — the consequences of leaving `targets` unset.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what the baseline actually means in features.
