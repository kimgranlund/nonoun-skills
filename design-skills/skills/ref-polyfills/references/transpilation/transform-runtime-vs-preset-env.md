---
date: 2026-04-27
coverage: extended
peers:
  - ../transpilation/babel-preset-env.md
  - ../transpilation/typescript-target-esnext.md
  - ../transpilation/swc-targets.md
  - ../anti-patterns/corejs-entry-modern.md
  - ../anti-patterns/preset-env-no-browserslist.md
  - ../landscape-shifts/core-js-funding-status.md
  - ../build-tools/browserslist-recipes.md
primary_sources:
  - https://babeljs.io/docs/babel-plugin-transform-runtime — `@babel/plugin-transform-runtime` reference
  - https://babeljs.io/docs/babel-preset-env — `@babel/preset-env` reference
  - https://babeljs.io/docs/options — Babel `caller` API and options
  - https://github.com/babel/babel/issues/10271 — preset-env conflicts with transform-runtime when using core-js@3
  - https://github.com/babel/babel/issues/16149 — clarification on combining transform-runtime with useBuiltIns
  - https://github.com/babel/babel/issues/9853 — bundle size impact of @babel/runtime-corejs3
  - https://github.com/zloirock/core-js/issues/905 — best practice of babel & core-js
---

# `@babel/plugin-transform-runtime` vs `@babel/preset-env` (with `useBuiltIns`)

The Babel-internal split. Two ways to ship polyfills via Babel; they are **mutually exclusive** for polyfilling, and the right choice depends on whether you are an **app author** or a **library author**.

> Even at the modern baseline, this matters: not because you need many polyfills (you don't — see [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)), but because library authors who get this wrong ship core-js to all their consumers regardless of those consumers' actual needs. That's the bundle-bloat amplifier.

## What's the difference

### `@babel/preset-env`

- Analyzes each source file and **modifies the source** to inject polyfill imports (`import "core-js/modules/es.array.flat";` etc.).
- Bundle-aware: polyfills land in the application bundle alongside the application code.
- `useBuiltIns` controls *whether and how* polyfills get injected:
  - `false` (default): no polyfills injected. Babel only transforms syntax. **This is the right setting at the modern baseline for most apps.**
  - `'usage'`: per-file analysis; only polyfills the features your code actually uses.
  - `'entry'`: replaces `import 'core-js/stable'` at your entry point with explicit per-feature imports targeting your browserslist.
- **Pollutes the global scope.** `Array.prototype.flat = function(){...}` and friends are written to globals.

### `@babel/plugin-transform-runtime`

- Uses a **sandboxed runtime helper module** (`@babel/runtime` or `@babel/runtime-corejs3`).
- Does **not** modify globals. Built-ins are aliased to imports from `@babel/runtime-corejs3/core-js-stable/array/flat`, etc.
- Smaller per-file emit — Babel's per-file helpers (like `_classCallCheck`, `_objectSpread`) are extracted to imports rather than duplicated inline.
- Adds a runtime dependency: `@babel/runtime` (or `@babel/runtime-corejs3` if you opt into core-js).
- Target-blind: it does **not** consult your browserslist. It includes whatever polyfills you ask for, regardless of whether the target needs them. ([babel/babel#10271](https://github.com/babel/babel/issues/10271))

## Mutual exclusion

**Do not use `useBuiltIns: 'usage' | 'entry'` together with `plugin-transform-runtime` with `corejs`.** The Babel docs are explicit: "When `@babel/plugin-transform-runtime` is enabled, the `useBuiltIns` option in `@babel/preset-env` must not be set, otherwise the plugin may not be able to completely sandbox the environment." ([babeljs.io/docs/babel-plugin-transform-runtime](https://babeljs.io/docs/babel-plugin-transform-runtime), [babel/babel#16149](https://github.com/babel/babel/issues/16149))

The two paths:

1. **Apps** — `@babel/preset-env` with `useBuiltIns: 'usage'` (and `corejs: 3`). No `transform-runtime`.
2. **Libraries** — `@babel/preset-env` with `useBuiltIns: false`, plus `@babel/plugin-transform-runtime` with `corejs: 3`. The two-plugin combo with `useBuiltIns: false` is fine; the conflict is specifically with `'usage'` or `'entry'`.

## Use case: applications

```js
// babel.config.js — application
module.exports = {
  presets: [['@babel/preset-env', {
    targets: { chrome: '125', firefox: '129', safari: '17.4' },
    bugfixes: true,
    useBuiltIns: 'usage',
    corejs: { version: '3.49', proposals: false },
  }]],
};
```

Why `useBuiltIns: 'usage'` for apps:

- The bundle is finalized at build time. Polluting the global scope is fine — your app owns the page.
- Per-file analysis gives the smallest possible polyfill surface. preset-env trims everything not actually used.
- `'usage'` is target-aware: it consults your browserslist and skips polyfills already supported.
- The per-file polyfill imports tree-shake cleanly under modern bundlers (webpack 5, Rollup, esbuild, Vite).

At our baseline, **most apps need `useBuiltIns: false`** — meaning don't polyfill at all — because every feature in [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) is shipped natively. Use `'usage'` only if you have a known polyfill candidate (Temporal, URLPattern at older Firefox, iterator helpers at older Safari).

`useBuiltIns: 'entry'` is the worst-of-both-worlds option at this baseline — it ships every polyfill matching your browserslist regardless of whether your code uses them. Avoid. See [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md). ([babel/babel discussion #14443](https://github.com/babel/babel/discussions/14443))

## Use case: libraries

```js
// babel.config.js — library
module.exports = {
  presets: [['@babel/preset-env', {
    targets: { chrome: '125', firefox: '129', safari: '17.4' },
    bugfixes: true,
    useBuiltIns: false,
  }]],
  plugins: [['@babel/plugin-transform-runtime', {
    corejs: { version: 3, proposals: true },
    version: '^7.24.0',
    useESModules: true,  // deprecated in Babel 8; see note below
  }]],
};

// package.json
{
  "dependencies": {
    "@babel/runtime-corejs3": "^7.24.0"
  }
}
```

Why `transform-runtime` for libraries:

- **No global pollution.** Your library doesn't write to `Array.prototype` of the consumer's page. Two libraries each polyfilling `Array.prototype.at` differently won't fight.
- **Predictable polyfill surface.** Your library's polyfills come from `@babel/runtime-corejs3`, a known dependency. The consumer doesn't ship duplicate polyfills — bundlers deduplicate the runtime imports.
- **Safer for downstream consumers.** A consumer of your library might support a different browser matrix than you do. Your library's `@babel/runtime-corejs3` imports work the same way regardless.

The trade-off: every `@babel/runtime-corejs3` import is a real import in the published code, which adds a small per-file overhead. `version: '^7.24.0'` in the plugin config (matching your declared `@babel/runtime-corejs3` peer dependency) lets Babel use the smallest helper variants available. ([babeljs.io/docs/babel-plugin-transform-runtime](https://babeljs.io/docs/babel-plugin-transform-runtime))

## Bundle-size implications

Two facts that drive the choice:

- **`@babel/runtime-corejs3` is large.** Issue [babel/babel#9853](https://github.com/babel/babel/issues/9853) reports a ~7× bundle-size increase from `@babel/runtime-corejs2` and ~11× from `@babel/runtime-corejs3` *when adopted naively in libraries that didn't need polyfills.* The increase is from including polyfill imports for features your consumer's browser already has natively.
- **`preset-env` + `useBuiltIns: 'usage'` gives the smallest bundle for apps.** The per-file analysis is more aggressive than transform-runtime's blanket inclusion. Apps that switch from `transform-runtime` to `preset-env useBuiltIns: 'usage'` typically see 30–50% polyfill-bundle shrinkage. ([babel/babel discussion #14443](https://github.com/babel/babel/discussions/14443))

The takeaway for libraries: **don't add `corejs: 3` to your `transform-runtime` config unless you actually need it.** If your library doesn't use any features that need polyfilling at the modern baseline, use `transform-runtime` *without* `corejs` — that gives you the per-file helper extraction (which still saves bytes vs preset-env-with-no-runtime) without bundling polyfills. The plain `@babel/runtime` package (no `corejs3`) is ~4 KB; `@babel/runtime-corejs3` is multiple times larger.

## `useESModules` — deprecated

The `useESModules` option to `transform-runtime` was historically used to emit ES-module-aware helper imports for smaller webpack bundles. **Babel 7.13+ uses `package.json`'s `exports` field to choose CJS or ESM helpers automatically; `useESModules` is deprecated and will be removed in Babel 8.** Don't set it in new code. ([babeljs.io/docs/babel-plugin-transform-runtime](https://babeljs.io/docs/babel-plugin-transform-runtime))

## Why this matters at the modern baseline

The most consequential decision is **whether to polyfill at all.** The modern baseline (Chromium 125+, Safari 17.4+, Firefox 129+) ships nearly every ECMAScript runtime feature you'd reach for. The answer for most apps and libraries in 2026 is:

- App: `useBuiltIns: false` (no polyfills). Babel does *syntax* lowering only, and even that is minimal at `target: "ES2022"`.
- Library: `transform-runtime` *without* `corejs` (just helpers). No polyfills shipped to consumers.

Reach for `corejs` only when you have a verified polyfill candidate (see [`../runtime-polyfills/`](../runtime-polyfills/)), and only if you can't ponyfill it explicitly via a dedicated package (e.g. `@js-temporal/polyfill`).

The single-maintainer / funding situation on `core-js` is also a relevant input: it remains a single-maintainer project ([zloirock](https://github.com/zloirock/core-js)) with chronic underfunding. Reducing your dependency on it where practical is good supply-chain hygiene. See [`../landscape-shifts/core-js-funding-status.md`](../landscape-shifts/core-js-funding-status.md).

## Quick decision matrix

| You are… | Use… | Polyfills? |
|---|---|---|
| App, modern baseline, no polyfill candidates | `preset-env` with `useBuiltIns: false` | none |
| App, modern baseline, with Temporal/URLPattern needs | `preset-env` with `useBuiltIns: 'usage'`, `corejs: 3` (or use the dedicated polyfill packages directly) | minimal |
| App, supporting older floors | `preset-env` with `useBuiltIns: 'usage'`, `corejs: 3` | scoped to usage |
| Library, modern baseline, no polyfill needs | `transform-runtime` without `corejs` (just helpers) | none |
| Library, modern baseline, with feature usage | `transform-runtime` with `corejs: 3` | bundled via `@babel/runtime-corejs3` |
| Library, supporting older floors | `transform-runtime` with `corejs: 3` | bundled via `@babel/runtime-corejs3` |
| Anyone | NEVER `preset-env` with `useBuiltIns: 'entry'` AND `transform-runtime` simultaneously | conflict, see Mutual exclusion |

## Pitfalls

- **Specifying `corejs` on `transform-runtime` without declaring `@babel/runtime-corejs3` as a real dependency.** Your library will import a package the consumer doesn't have. Always pair `corejs: 3` in the plugin config with `"@babel/runtime-corejs3": "^7.x"` in `dependencies`.
- **`transform-runtime` blind to your browserslist.** It will include polyfills even for features your target browsers natively support. There is no `targets` option on `transform-runtime`. Either accept this cost, or migrate the polyfill surface to `preset-env useBuiltIns: 'usage'` (apps only).
- **`preset-env useBuiltIns: 'usage'` doesn't polyfill your dependencies.** It only inspects code that flows through Babel. If your `node_modules` ship un-transpiled modern syntax, `'usage'` won't add polyfills for them. Either compile dependencies through Babel (slow) or use `'entry'` (worse for bundle size) or don't worry about it because at the modern baseline your dependencies' modern syntax is supported natively. ([babel/babel#9625](https://github.com/babel/babel/issues/9625))
- **Mixing both paths.** Don't enable `useBuiltIns: 'usage'` *and* `transform-runtime` with `corejs`. Pick one path.

## Cross-references

- [`./babel-preset-env.md`](./babel-preset-env.md) — full preset-env reference, including `bugfixes`, `targets`, browserslist coupling.
- [`./typescript-target-esnext.md`](./typescript-target-esnext.md) — when TypeScript hands code to Babel.
- [`./swc-targets.md`](./swc-targets.md) — the Rust-based alternative; analogous split exists.
- [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md) — why `useBuiltIns: 'entry'` is wrong at this baseline.
- [`../anti-patterns/preset-env-no-browserslist.md`](../anti-patterns/preset-env-no-browserslist.md) — what `defaults` actually resolves to.
- [`../landscape-shifts/core-js-funding-status.md`](../landscape-shifts/core-js-funding-status.md) — supply-chain context for core-js.
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — the canonical query for our baseline.
