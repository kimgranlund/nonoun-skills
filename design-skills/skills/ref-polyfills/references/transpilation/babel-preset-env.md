---
date: 2026-04-27
coverage: canonical
peers:
  - ../anti-patterns/corejs-entry-modern.md
  - ../anti-patterns/target-es5-modern.md
  - ../anti-patterns/preset-env-no-browserslist.md
  - ../transpilation/swc-targets.md
  - ../transpilation/esbuild-targets.md
  - ../transpilation/typescript-target-esnext.md
  - ../transpilation/transform-runtime-vs-preset-env.md
  - ../build-tools/browserslist-recipes.md
  - ../landscape-shifts/core-js-funding-status.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://babeljs.io/docs/babel-preset-env — the canonical preset-env reference
  - https://github.com/zloirock/core-js — core-js README, version semantics, Pushkarev funding context
  - https://github.com/babel/babel — Babel monorepo (preset-env source, issue tracker)
  - https://github.com/babel/babel/discussions/14443 — canonical "entry vs usage" discussion thread
  - https://github.com/babel/babel/discussions/13150 — `corejs` version pinning rationale
  - https://github.com/babel/preset-modules — preset-modules, predecessor to `bugfixes`
---

# `@babel/preset-env`

The Babel preset that decides — given a browserslist target — which syntax transforms and which runtime polyfills are required. Most-used JS transpiler config in the ecosystem; also the most-misconfigured. At the modern baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+) the right answer is "transpile almost nothing, polyfill almost nothing." This file is the option-by-option reference.

## What it is

`@babel/preset-env` replaces the older era of yearly presets (`preset-es2015`, `preset-es2016`, …, `preset-es2020`) with one preset that takes a target environment description and computes the minimal set of plugins required. It performs two jobs:

1. **Syntax lowering** — transpile syntax (optional chaining, class fields, async/await, decorators when stable) to forms the target understands.
2. **Polyfill inclusion** — when `useBuiltIns` is set, inject `core-js` imports for runtime APIs (Set methods, `Object.groupBy`, `Promise.withResolvers`, etc.) the target lacks.

At the modern baseline, both jobs reduce to near-zero work. The preset's residual value is as a tripwire: when a stage-3 proposal lands, preset-env knows whether the target browsers shipped it.

## The three `useBuiltIns` modes (deep dive)

This is the load-bearing option. It controls how core-js polyfills are included in the bundle.

### `useBuiltIns: false` (default)

No automatic polyfill inclusion. Babel transpiles syntax only. The smallest bundle. **Recommended at the modern baseline** for application code that doesn't reach for known-missing APIs.

```js
module.exports = {
  presets: [['@babel/preset-env', {
    useBuiltIns: false,  // explicit, even though it's the default
    targets: { chrome: '125', firefox: '129', safari: '17.4' },
  }]],
};
```

If a feature like Iterator helpers is genuinely needed (Safari 17.4–18.3 lacks them — see [`../runtime-polyfills/iterator-helpers.md`](../runtime-polyfills/iterator-helpers.md)), import a ponyfill explicitly at the call site. Don't reach for `useBuiltIns` to handle one feature.

### `useBuiltIns: 'usage'` (the smart mode)

Babel's AST analyzer scans each file and injects only the polyfill imports the file actually uses, scoped to gaps in the browserslist target. Files that don't reference Set methods don't get Set-method polyfills. **Recommended when polyfills are needed.**

```js
module.exports = {
  presets: [['@babel/preset-env', {
    useBuiltIns: 'usage',
    corejs: { version: '3.49', proposals: true },
    targets: { chrome: '125', firefox: '129', safari: '17.4' },
  }]],
};
```

Two caveats:

- **AST analysis isn't perfect.** Dynamic property access (`foo['a' + 't']()`) won't be detected — preset-env will not include `String.prototype.at`. SWC's `usage` mode has the same limitation, only worse.
- **Don't add a global `import 'core-js/stable'`.** With `'usage'`, that global import double-includes polyfills. Delete it.

### `useBuiltIns: 'entry'` (the 2018-era pattern)

Babel splits a single global `import 'core-js/stable'` at the application entrypoint into per-feature imports, filtered by browserslist. Larger bundles than `'usage'` because the split is coarse — every feature core-js targets that's missing in any browser in the query goes in, regardless of whether your code uses it.

```js
// babel.config.js
module.exports = {
  presets: [['@babel/preset-env', {
    useBuiltIns: 'entry',
    corejs: { version: '3.49', proposals: true },
    targets: { chrome: '125', firefox: '129', safari: '17.4' },
  }]],
};

// App entrypoint
import 'core-js/stable';
import 'regenerator-runtime/runtime';
```

**Use only if you can't add per-file analysis** — e.g., a build pipeline that rejects new dependencies, or a shared library where the consumer's browserslist drives inclusion. At the modern baseline, this is wasteful for application code. See [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md) for the full anti-pattern writeup.

## `corejs` configuration

When `useBuiltIns` is `'usage'` or `'entry'`, the `corejs` option is mandatory. Two forms:

```js
// Bare number — interpreted as 3.0; will warn that newer features won't be polyfilled
corejs: 3,

// Pinned to minor version — recommended
corejs: { version: '3.49', proposals: true },
```

Why pin to a minor version? core-js's polyfill database is updated when proposals graduate. A pin of `'3.49'` tells preset-env that all polyfills available through 3.49.0 are usable; older pins exclude newer polyfills. Core-js 3.49.0 was released March 16, 2026 and is the current version. See [`../landscape-shifts/core-js-funding-status.md`](../landscape-shifts/core-js-funding-status.md) for context on the (single-maintainer) project status.

The `proposals: true` opt-in includes Stage 3+ proposals' polyfills. Without it, only finished-stage features (Stage 4) get polyfilled. The trade-off: `proposals: true` includes more polyfills, but tracks the spec as it evolves; if a Stage 3 feature changes its surface area before Stage 4, the polyfilled behavior may diverge from the eventual native shipping. At the modern baseline most Stage 3 proposals worth polyfilling have already landed natively; this flag is mostly a forward-compat gate.

The `corejs` option's `proposals` flag (a core-js setting) is distinct from preset-env's own `shippedProposals` flag (a Babel setting). They control different things — see "shippedProposals" below.

## `targets` field

The browser target description. Three accepted forms:

```js
// Direct, explicit
targets: { chrome: '125', firefox: '129', safari: '17.4' }

// Browserslist string
targets: 'chrome >= 125, firefox >= 129, safari >= 17.4'

// Defer to .browserslistrc / package.json "browserslist"
// (omit targets entirely)
```

The browserslist form is preferred at the modern baseline because the same query drives autoprefixer, postcss-preset-env, lightningcss, and (with helpers) esbuild. See [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) for canonical queries.

If `targets` is omitted **and** there's no `.browserslistrc`, preset-env falls back to its `defaults` browserslist query — which resolves to `> 0.5%, last 2 versions, Firefox ESR, not dead`. That's an Internet Explorer-era query designed in 2017. Never let this happen in production. See [`../anti-patterns/preset-env-no-browserslist.md`](../anti-patterns/preset-env-no-browserslist.md).

## `bugfixes: true`

Recommended; opt-in in Babel 7, on-by-default in Babel 8. Tells preset-env to compile broken syntax to the closest non-broken modern syntax instead of broadly lowering the whole feature group. Result: fewer transforms, smaller bundles.

```js
{
  bugfixes: true,  // explicit, in case Babel 7 is in use
}
```

`bugfixes` is the successor to the (now-deprecated) `babel-preset-modules`, which was a separate preset that targeted modern browsers by working around specific engine bugs. Babel folded that logic into preset-env via this flag. ([Babel commit `e45d86c` — "Enable preset-env bugfixes by default" for Babel 8](https://github.com/babel/babel/commit/e45d86c33380e2e7e98b5713443b8e20658494a9))

## `shippedProposals: true`

Opt-in for Stage 3 features that engines have shipped. When a target has native support for a feature proposal, preset-env enables only the parser plugin for it (so Babel can read the syntax) and skips the transform. Reduces transpilation when supported.

```js
{
  shippedProposals: true,
}
```

Distinct from `corejs.proposals`: `shippedProposals` controls *syntax* proposals (decorators, the pipeline operator), while `corejs.proposals` controls *runtime API* proposals (`Array.prototype.toReversed`, etc.). You can opt into both, neither, or one — they're orthogonal. ([Babel discussion #16243](https://github.com/babel/babel/discussions/16243))

## At our baseline (the recipe)

A complete, current-as-of-April-2026 `babel.config.js` for the modern baseline:

```js
module.exports = {
  presets: [['@babel/preset-env', {
    // Syntax + polyfill behavior:
    useBuiltIns: 'usage',                         // or false if you trust the baseline
    corejs: { version: '3.49', proposals: true },
    bugfixes: true,
    shippedProposals: true,

    // Browser target:
    targets: {
      chrome: '125',
      firefox: '129',
      safari: '17.4',
    },
  }]],
};
```

Pair with no entrypoint `import 'core-js/stable'`. Pair with a real `.browserslistrc` or `package.json` `browserslist` for cross-tool sharing.

## Browserslist alternative (more sharing-friendly)

Move the target into `.browserslistrc` or `package.json` so autoprefixer, postcss-preset-env, and lightningcss read the same query:

```jsonc
// package.json
{
  "browserslist": [
    "chrome >= 125",
    "firefox >= 129",
    "safari >= 17.4"
  ]
}
```

```js
// babel.config.js — drop targets, browserslist takes over
module.exports = {
  presets: [['@babel/preset-env', {
    useBuiltIns: 'usage',
    corejs: { version: '3.49', proposals: true },
    bugfixes: true,
    shippedProposals: true,
  }]],
};
```

This is the preferred form. See [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) for production-ready variants (with progressive-enhancement floors, mobile-only, dual-target).

## What gets transpiled at this baseline

Almost nothing. The features preset-env still touches at Chromium 125 / Safari 17.4 / Firefox 129:

- **Decorators** — Stage 3 proposal (`2023-11`); no engine ships it natively yet, so preset-env still transforms.
- **Pipeline operator** — Stage 2; Babel-only syntax; transformed if used.
- **JSX** — always transformed (it's not part of the ECMAScript spec).
- A handful of stage-3 proposals (Pattern Matching, Records & Tuples successors) when the source uses them.

Everything else — optional chaining, nullish coalescing, class fields, top-level `await`, `Object.hasOwn`, structured clone, dynamic `import()`, BigInt, async iterators — passes through native at all three baseline engines.

## What polyfills get included

With `useBuiltIns: 'usage'` at this baseline, almost none. The baseline is high enough that Set methods, `Object.groupBy`/`Map.groupBy`, `Promise.withResolvers`, the `RegExp v` flag, and `Object.hasOwn` are all native. The exceptions:

- **Iterator helpers** — Safari 17.4–18.3 needs them; Safari 18.4 ships native. preset-env will inject `es-iterator-helpers` for files that use `Iterator.prototype.map` etc. (See [`../runtime-polyfills/iterator-helpers.md`](../runtime-polyfills/iterator-helpers.md).)
- **`Promise.try`** — Firefox 129–133 lacks it; Firefox 134+ ships. Trivial inline shim is usually enough.

If your `useBuiltIns: 'usage'` build is including substantially more than this, your browserslist is probably stale. Run a bundle-analyzer pass (see verification recipe in [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md)).

## Cross-reference

- [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md) — when `useBuiltIns: 'entry'` is wrong (most of the time).
- [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) — sibling pattern: targeting ES5 in tsconfig.
- [`../anti-patterns/preset-env-no-browserslist.md`](../anti-patterns/preset-env-no-browserslist.md) — what `defaults` resolves to and why it's wrong.
- [`./swc-targets.md`](./swc-targets.md) — SWC equivalent (faster, slightly less complete polyfill auditing).
- [`./esbuild-targets.md`](./esbuild-targets.md) — esbuild equivalent (no polyfill story; syntax only).
- [`./transform-runtime-vs-preset-env.md`](./transform-runtime-vs-preset-env.md) — when to pick `@babel/plugin-transform-runtime` instead.
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical queries for the modern baseline.
- [`../landscape-shifts/core-js-funding-status.md`](../landscape-shifts/core-js-funding-status.md) — supply-chain context for core-js.
