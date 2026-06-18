---
date: 2026-04-27
coverage: advisory
peers:
  - ../transpilation/babel-preset-env.md
  - ../transpilation/transform-runtime-vs-preset-env.md
  - ../transpilation/swc-targets.md
  - ../transpilation/esbuild-targets.md
  - ../landscape-shifts/core-js-funding-status.md
  - ../anti-patterns/preset-env-no-browserslist.md
  - ../anti-patterns/target-es5-modern.md
  - ../build-tools/browserslist-recipes.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://babeljs.io/docs/babel-preset-env — `useBuiltIns` option spec
  - https://babeljs.io/docs/babel-plugin-transform-runtime — sandboxed-runtime alternative
  - https://github.com/zloirock/core-js — core-js README and `corejs` version semantics
  - https://github.com/babel/babel/discussions/14443 — canonical "entry vs usage" discussion thread
  - https://www.debugbear.com/blog/how-does-browser-support-impact-bundle-size — measured bundle impact by target
  - https://web.dev/articles/baseline-and-polyfills — modern stance on polyfilling
---

# Anti-pattern: shipping `core-js` to modern browsers via `useBuiltIns: 'entry'`

## The anti-pattern

The configuration is unmistakable. In `babel.config.js`:

```js
module.exports = {
  presets: [
    ['@babel/preset-env', {
      useBuiltIns: 'entry',
      corejs: 3,
    }],
  ],
};
```

…and at the top of the application entrypoint:

```js
import 'core-js/stable';
import 'regenerator-runtime/runtime';
```

The result: every user, on every browser at or above your support floor, downloads and parses the full set of core-js polyfills that `@babel/preset-env` decides are not yet "Baseline" by `browserslist`'s reckoning. At the modern baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+) almost all of those polyfills are dead weight. Bundle bloat measured at **30–60 KB gzipped** in typical projects, and **100 KB+ gzipped** when a stale browserslist still includes ancient mobile Safari, KaiOS, or Samsung Internet entries ([DebugBear](https://www.debugbear.com/blog/how-does-browser-support-impact-bundle-size)).

It's slow. It's wasteful. It's the default in roughly half the open-source project templates from 2018–2020 still in circulation, and it's a near-certain finding in any audit of a long-lived React/Vue codebase.

## Why it persists

Three reasons, in roughly this order of cultural weight:

1. **Babel's own docs recommended `useBuiltIns: 'entry'` as the canonical pattern in 2018–2020.** Project templates copied that recipe. Those templates didn't get updated. Nor did the blog posts, Stack Overflow answers, or course material derived from them. ([Babel preset-env docs](https://babeljs.io/docs/babel-preset-env))
2. **Migrating off it requires understanding `useBuiltIns: 'usage'`** — which, in turn, requires understanding the `corejs` option (must be `3`, not `2`), browserslist coupling, and whether you also have `@babel/plugin-transform-runtime` in the chain (you cannot use both `useBuiltIns` and `transform-runtime` at once — they'll fight). The cost of getting it wrong is a runtime error in production. The cost of leaving `'entry'` alone is a bigger bundle. Risk-averse teams pick "bigger bundle." ([Babel issue #11539 and discussion #14443](https://github.com/babel/babel/discussions/14443))
3. **It works at any browser target.** `'entry'` is correct in the sense that the code runs. The cost is invisible to QA, invisible to functional testing, and only shows up in bundle-size dashboards — which most teams don't run.

## Why it's wrong at the modern baseline

The features `core-js` polyfills are, at this baseline, **already native in every supported engine**. A non-exhaustive list of what `core-js@3` ships and Chromium 125 / Safari 17.4 / Firefox 129 already has:

- `Promise`, `Promise.allSettled`, `Promise.any`, `Promise.withResolvers` (Baseline 2024)
- `Array.prototype.at`, `findLast`, `findLastIndex`, `flat`, `flatMap`, `includes`
- `Object.fromEntries`, `Object.hasOwn`, `Object.groupBy`, `Map.groupBy` (Baseline March 2024)
- `String.prototype.replaceAll`, `String.prototype.matchAll`
- Set methods (`intersection`, `union`, `difference`, `symmetricDifference`, `isSubsetOf`, `isSupersetOf`, `isDisjointFrom`) — Baseline June 2024
- `RegExp` `v` flag — Chrome 112 / Firefox 116 / Safari 17
- `structuredClone`, `Symbol.iterator`, `WeakRef`, `FinalizationRegistry`
- `fetch`, `AbortController`, `IntersectionObserver`, `ResizeObserver`

`@babel/preset-env` with `useBuiltIns: 'entry'` filters by browserslist, but it filters **conservatively**. The default `defaults` browserslist query keeps your bundle aligned with Internet Explorer-era polyfilling assumptions because `defaults` resolves to `> 0.5%, last 2 versions, Firefox ESR, not dead` — a query designed in 2017 with IE11 in mind. Until you replace that query with one targeting your actual modern baseline, you ship core-js to users who don't need any of it.

`'entry'` also defeats tree-shaking. The bundle's `import 'core-js/stable'` is a side-effect import; webpack, esbuild, and Rollup all preserve it. The fact that a given module never calls `Array.prototype.flat` doesn't help — once `'core-js/stable'` is imported, the prototype mutations are committed regardless of which exports survive. The only escape valve is `'usage'`, which scopes core-js inclusion to features the AST analyzer actually sees in your source code. ([Bundle-size issue thread](https://github.com/zloirock/core-js/issues/617))

## The fix

### Step 1 — Move from `'entry'` to `'usage'`

```js
// Before (anti-pattern)
module.exports = {
  presets: [['@babel/preset-env', {
    useBuiltIns: 'entry',
    corejs: 3,
  }]],
};
// App entrypoint:
import 'core-js/stable';
import 'regenerator-runtime/runtime';

// After (modern best practice)
module.exports = {
  presets: [['@babel/preset-env', {
    useBuiltIns: 'usage',
    corejs: { version: '3.47', proposals: true },
    targets: {
      chrome: '125',
      firefox: '129',
      safari: '17.4',
    },
  }]],
};
// App entrypoint: NO core-js import. Babel handles it per-file.
```

Three things change:

1. `'entry'` becomes `'usage'`. Babel's AST analyzer scans each file and injects the specific polyfill imports the file needs. Files that don't reference Set methods don't get Set-method polyfills.
2. `corejs: 3` becomes `corejs: { version: '3.47', proposals: true }`. The version pin is mandatory for `'usage'`; the bare number form will warn. The minor-version pin matters because core-js's polyfill database is updated when proposals graduate. ([Babel discussion #13150](https://github.com/babel/babel/discussions/13150))
3. The `import 'core-js/stable'` line at the entrypoint is **deleted**. With `'usage'`, those imports are an error — they double-include polyfills.

### Step 2 (better) — Drop `core-js` entirely

At the Chromium 125 / Safari 17.4 / Firefox 129 baseline, the right answer for most projects is `useBuiltIns: false`. No core-js inclusion at all. Babel still transpiles syntax (optional chaining, nullish coalescing, async/await) where required, but the runtime polyfill bundle disappears.

```js
// The "I trust my baseline" config
module.exports = {
  presets: [['@babel/preset-env', {
    useBuiltIns: false, // explicit, even though it's the default
    targets: {
      chrome: '125',
      firefox: '129',
      safari: '17.4',
    },
  }]],
};
```

You can also remove `core-js` from `dependencies` entirely. Run `npm uninstall core-js core-js-pure regenerator-runtime` and watch the lockfile shrink.

If a single feature still needs polyfilling (Iterator helpers for Safari 17.4–18.3 is the live example at this baseline — see [`../runtime-polyfills/iterator-helpers.md`](../runtime-polyfills/iterator-helpers.md)), import it as a ponyfill — explicitly, per use — rather than mutating globals. See [`../feature-detection/ponyfill-pattern.md`](../feature-detection/ponyfill-pattern.md).

### Step 3 (best) — Skip Babel entirely

At the modern baseline, the strongest move is to drop Babel from the build chain. Replace it with one of:

- **SWC** — Rust-based; an order of magnitude faster than Babel; default in Next.js 12+; supports `env.targets` with browserslist auto-discovery. See [`../transpilation/swc-targets.md`](../transpilation/swc-targets.md).
- **esbuild** — Go-based; faster than SWC for pure transformation. Native `target: ['chrome125', 'safari17.4', 'firefox129']` syntax. See [`../transpilation/esbuild-targets.md`](../transpilation/esbuild-targets.md).
- **lightningcss** — only handles CSS, but pairs with the JS toolchain choice.

None of these ships a runtime polyfill bundle by default. None has a `'usage'`/`'entry'` distinction. They transform syntax, period. If you need a runtime polyfill, you import it explicitly — exactly the ponyfill pattern.

## Verification — is `core-js` in your bundle right now?

Three checks, in escalating thoroughness:

```sh
# 1. Quick: is it a direct or transitive dependency?
npm ls core-js
npm ls core-js-pure
npm ls regenerator-runtime

# 2. Footprint on disk:
du -sh node_modules/core-js node_modules/core-js-pure 2>/dev/null

# 3. In your actual emitted bundle:
npx webpack-bundle-analyzer dist/stats.json   # webpack
npx vite-bundle-visualizer                    # vite
npx source-map-explorer dist/assets/*.js      # source-map-explorer
```

For a webpack project, the bundle analyzer will show `core-js/modules/*.js` chunks. Each one is a polyfill. At the modern baseline, the right number is **zero**. Anything you see — `es.array.flat`, `es.object.has-own`, `es.set.union`, `es.regexp.to-string` — is bloat. Even `es.regenerator-runtime` is bloat: it only exists because something is transpiling `async`/`await` to ES5, which it shouldn't be at this baseline. See [`./target-es5-modern.md`](./target-es5-modern.md).

## Migration checklist

A concrete sequence to take a legacy project from `'entry'` to clean modern config:

1. **Audit current state**:
   - `npm ls core-js core-js-pure regenerator-runtime` — note versions.
   - `cat babel.config.js .babelrc.json` — find the `useBuiltIns` setting.
   - `cat .browserslistrc` (or `package.json` `browserslist`) — capture the current query.
   - Run a baseline build and bundle analyzer. Save the screenshot.

2. **Update browserslist** to your actual baseline (see [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md)):
   ```
   chrome >= 125
   firefox >= 129
   safari >= 17.4
   ```
   This step alone often shrinks the bundle by 20+ KB without any Babel-config change, because preset-env's polyfill filter respects the new query.

3. **Switch `'entry'` → `'usage'`** with the `corejs` version pinned. Update `corejs` to the latest 3.x version (`3.47.0` as of January 2026 — see [`../landscape-shifts/core-js-funding-status.md`](../landscape-shifts/core-js-funding-status.md)).

4. **Delete the entrypoint imports**:
   ```diff
   - import 'core-js/stable';
   - import 'regenerator-runtime/runtime';
   ```
   This is the most error-prone step. If you have a custom test runner, polyfill harness, or SSR setup that depended on the global pollution, you'll find it here. Run the full test suite.

5. **Compare bundles**. The "after" bundle should be 30–60 KB gzipped smaller. If it isn't, your browserslist is still wrong, or you have a transitive dependency forcing core-js inclusion (look for `core-js-pure` in particular).

6. **Try `useBuiltIns: false`** on a branch. Run the test suite, smoke-test on real devices in your support matrix. If everything works, ship it and uninstall `core-js` from `dependencies`.

7. **Consider replacing Babel with SWC or esbuild** as a follow-up. This is the largest single performance win in the chain — typical builds become 5–10× faster — but it's a separate migration with its own risks. Treat it as Phase 2.

## When `useBuiltIns: 'entry'` is actually correct

Two cases. Both rare at this baseline:

- **You're a library author** building for an unknown consumer browser matrix (e.g. a generic SDK published to npm). In this case, `useBuiltIns: 'entry'` plus an explicit `import 'core-js/stable'` at the library's entrypoint lets the *consumer's* browserslist (set in the consumer's `.browserslistrc`) decide what gets included. But: most modern library authors instead emit ESM with no polyfills and document a minimum browser target. That's strictly cleaner.
- **You're shipping to a browser matrix that genuinely includes IE11 or pre-2020 mobile Safari.** If you're reading this skill, you almost certainly aren't. The skill's whole posture is calibrated to the modern baseline.

## Cross-reference

- [`./target-es5-modern.md`](./target-es5-modern.md) — the same anti-pattern's cousin: targeting ES5 in tsconfig.
- [`./preset-env-no-browserslist.md`](./preset-env-no-browserslist.md) — what happens when Babel runs without a browserslist (defaults are wrong by ~6 years).
- [`../transpilation/babel-preset-env.md`](../transpilation/babel-preset-env.md) — full reference on `@babel/preset-env` options.
- [`../transpilation/transform-runtime-vs-preset-env.md`](../transpilation/transform-runtime-vs-preset-env.md) — when to pick `@babel/plugin-transform-runtime` instead.
- [`../landscape-shifts/core-js-funding-status.md`](../landscape-shifts/core-js-funding-status.md) — single-maintainer (Pushkarev) supply-chain context for core-js itself.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what Chromium 125 / Safari 17.4 / Firefox 129 means in concrete terms.
