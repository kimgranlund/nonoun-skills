---
date: 2026-04-27
coverage: advisory
peers:
  - ../anti-patterns/corejs-entry-modern.md
  - ../anti-patterns/target-es5-modern.md
  - ../anti-patterns/defensive-overpolyfilling.md
  - ../anti-patterns/polyfill-io-after-attack.md
  - ../transpilation/babel-preset-env.md
  - ../transpilation/swc-targets.md
  - ../transpilation/esbuild-targets.md
  - ../build-tools/browserslist-recipes.md
  - ../landscape-shifts/core-js-funding-status.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://babeljs.io/docs/babel-preset-env — `@babel/preset-env` reference, "No targets" section
  - https://babeljs.io/docs/babel-preset-env#no-targets — explicit "No targets" docs section
  - https://github.com/babel/babel/issues/9513 — "preset-env: do you not support ES5?" (defaults behavior)
  - https://github.com/babel/website/issues/2245 — "Default targets for preset-env shall be 'defaults'"
  - https://github.com/babel/babel/pull/7835 — "Change babel-preset-env docs according Browserslist best practices"
  - https://github.com/browserslist/browserslist — `defaults` query semantics
  - https://www.debugbear.com/blog/how-does-browser-support-impact-bundle-size — measured bundle impact by target
  - https://github.com/zloirock/core-js — core-js README, version-pin semantics
---

# Anti-pattern: `@babel/preset-env` without configured targets

## The anti-pattern

The Babel config that ships across half of the bootstrapped React, Vue, and vanilla-JS projects from 2018–2022:

```js
// babel.config.js (or .babelrc.json)
module.exports = {
  presets: ['@babel/preset-env'],
};
```

…with no `targets` option, no `.browserslistrc`, no `"browserslist"` field in `package.json`. The team assumed `@babel/preset-env` would "do the right thing." It is doing what its docs say it does — and what its docs say it does is the worst case.

> If no targets are specified, @babel/preset-env will transform all ECMAScript 2015+ code by default. ([Babel docs — `@babel/preset-env`](https://babeljs.io/docs/babel-preset-env#no-targets))

Translated: every `class` declaration becomes an ES5 prototype-chain dance. Every `async`/`await` becomes a `regeneratorRuntime`-driven state machine. Every `let`/`const` becomes `var`. Every arrow function becomes a `function`. Optional chaining becomes verbose `if`-guarded property access. Nullish coalescing becomes a triple-`undefined` check. The full ES5 transpilation overhead, plus core-js polyfills (when `useBuiltIns` is set), gets shipped to every user — including the user on Chrome 132 with native support for everything.

## What Babel actually does without targets

The behavior is documented and deterministic. The exact resolution chain:

1. **Babel reads `targets`** from preset-env options. If present → use it.
2. **Babel reads `package.json`'s `"browserslist"` field.** If present → use that as targets.
3. **Babel reads `.browserslistrc`** in the project root (or any ancestor directory). If present → use that.
4. **Babel reads the `BROWSERSLIST` environment variable.** If set → use that.
5. **None of the above? Babel falls back to the `defaults` browserslist query.** This is the trap. ([Babel preset-env — "Targets" section](https://babeljs.io/docs/babel-preset-env))

The `defaults` query expands to:

```
> 0.5%, last 2 versions, Firefox ESR, not dead
```

In April 2026, this resolves to roughly:

```
Chrome >= 119, Edge >= 132, Firefox >= 122,
Safari >= 16.4, Opera >= 102, Samsung >= 23,
ChromeAndroid >= 130, FirefoxAndroid >= 122, SafariIOS >= 16.4,
KaiOS, QQ Browser, UC Browser, ...
```

Six years of legacy in the floor. **Per-feature, that means**:

- Class fields → transpiled (Safari < 16 lacks them).
- Top-level `await` → transpiled (Safari < 15 lacks it; Firefox < 89 lacks it).
- `Object.hasOwn` → polyfilled (Safari < 16.4 lacks it).
- `Promise.allSettled` → polyfilled (Samsung Internet < 14 lacks it).
- Set methods (intersection, union, difference, symmetric difference, etc.) → polyfilled (Safari < 17 lacks them).
- Optional chaining → transpiled (older Samsung browsers, KaiOS).
- The `RegExp v` flag → polyfilled.
- async/await → transpiled (anywhere `defaults` resolves to a non-async-supporting engine, which is now nowhere — but the transform plugin still gets included unless `bugfixes: true` is set).

You ship all of this to users on Chrome 132. The bundle pays the ES5 cost on every page load.

### The "defaults" cul-de-sac is documented as a known issue

The Babel team has explicitly flagged this as a problem. [Babel issue #2245](https://github.com/babel/website/issues/2245) is the canonical "default targets shall be `defaults` is misleading" thread. PR #7835 ("Change babel-preset-env docs according Browserslist best practices") moved the recommendation toward "always specify targets explicitly." The docs now lead with:

> If you are relying on browserslist's defaults query (either explicitly or by having no browserslist config), you will want to check out the No targets section for information on preset-env's behavior. ([Babel docs](https://babeljs.io/docs/babel-preset-env))

The behavior is preserved for backward compatibility. The expectation that you will configure targets is documented. Most projects don't read the doc that closely.

## Bundle impact

The cost is large and measurable. Three reference points:

### Empty React app, no targets

A bare-bones `create-react-app` (template ejected) with `@babel/preset-env` and no browserslist override:

- **Bundle size**: ~180 KB minified, ~55 KB gzipped, for a "Hello World" component.
- **Of that**: ~30 KB gzipped is `core-js` polyfills.
- **Of that**: ~5–6 KB is `regenerator-runtime` (every async function passes through it).
- **Of that**: ~10 KB is per-file Babel helpers (`_classCallCheck`, `_inherits`, `_defineProperty`, etc., one set per transpiled file).

For a 5-line component. Most of the bundle is transpilation infrastructure for browsers nobody uses.

### Real-world TypeScript-React project

DebugBear's bundle-size analysis ([source](https://www.debugbear.com/blog/how-does-browser-support-impact-bundle-size)) measured a typical TypeScript-React project under several browserslist queries:

| Browserslist | Bundle (gzipped) | Polyfill overhead |
|---|---|---|
| `> 0.5%, last 2 versions, Firefox ESR, not dead` (the `defaults`) | **~120 KB** | ~30–60 KB of pure polyfill/transpilation |
| `last 2 versions, not dead` | ~95 KB | ~10–15 KB |
| `chrome >= 125, firefox >= 129, safari >= 17.4` (this skill's baseline) | ~85 KB | ~0–5 KB (only Iterator helpers etc.) |

**The "no browserslist" config (which falls back to `defaults`) costs roughly 35 KB gzipped over the modern-baseline config.** That's a quarter of typical bundle on a small app. On a larger app, the absolute savings stay roughly the same; the relative impact is smaller, but the user experience cost is identical (every user pays the load cost regardless of bundle size).

### One project's "100KB of preset-env"

The Babel team's own [preset-modules issue #7](https://github.com/babel/preset-modules/issues/7) tracked a TypeScript React-Redux project: 101.29 KB minified+gzipped with `@babel/preset-env` (defaults), 100.27 KB with `@babel/preset-modules`. Within preset-env, switching to a tight modern target plus `bugfixes: true` recovered 30+ KB. The `defaults`-fallback path is a 30 KB tax.

## Why it persists

Five reasons:

1. **`@babel/preset-env` "just works" in the most basic sense.** The build doesn't fail. The code runs. There is no error to alert you that you're paying a 30+ KB tax. The cost lives in bundle-analyzer reports and Lighthouse scores, both of which most teams don't look at.
2. **Tutorials and starter templates omit the browserslist step.** A 2020 blog post showing how to set up Babel for a React project will install `@babel/core @babel/preset-env @babel/preset-react`, write a five-line `babel.config.js`, and call it done. It works. The reader copies it. The tutorial is correct in the narrow sense; it teaches the trap.
3. **Babel's own docs show terse examples.** The minimal `babel.config.js` in early Babel docs read `presets: ['@babel/preset-env']` with no targets. The "No targets" section is in the docs but is lower-priority reading. Most engineers don't go past the first example.
4. **The fix requires understanding browserslist.** Adding `targets` is one option; adding a `package.json` `browserslist` field is the better option. Both require knowing what query string to write. The skill's `../build-tools/browserslist-recipes.md` is the canonical reference, but engineers who don't know about it are stuck.
5. **Risk-aversion.** Once the build works, changing the config feels risky. "What if I break the build for IE11 users we don't have but might?" Defensive thinking dominates; the team ships the larger bundle.

## The fix

A two-step migration. Both steps are safe; both are mechanical.

### Step 1 — Add a browserslist config

The single most-important change. Add `"browserslist"` to `package.json`:

```jsonc
{
  "name": "my-app",
  "browserslist": [
    "chrome >= 125",
    "firefox >= 129",
    "safari >= 17.4"
  ]
}
```

Or `.browserslistrc` in the project root:

```
chrome >= 125
firefox >= 129
safari >= 17.4
```

Either form works; `package.json` is preferred (one less file). Once this is in place, **`@babel/preset-env` automatically reads it** — no Babel-config change required. The `defaults` fallback no longer fires.

Verify with:

```sh
npx browserslist
# Should print: chrome 125, chrome 126, ..., firefox 129, ..., safari 17.4, ...
# NOT: chrome 119, edge 132, firefox 122, safari 16.4, ie 11, ...
```

### Step 2 — Add `bugfixes` and (optionally) tight targets

Even with browserslist configured, set `bugfixes: true` to enable preset-env's modern transform mode. Babel 7.9+ supports this; Babel 8 enables it by default. Recommended explicit config:

```js
// babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', {
      // targets are auto-loaded from package.json or .browserslistrc
      bugfixes: true,
      shippedProposals: true,
      useBuiltIns: 'usage',
      corejs: { version: '3.49', proposals: true },
    }],
  ],
};
```

What each option does:

- **`bugfixes: true`** — tells preset-env to apply only the syntax transforms required to fix specific browser bugs in your target list, instead of broadly lowering the whole feature group. Smaller bundles. ([Babel preset-modules merge into preset-env](https://github.com/babel/preset-modules))
- **`shippedProposals: true`** — opts into Stage 3 features the engines have shipped (decorators, etc.). Reduces transpilation when the target supports the feature.
- **`useBuiltIns: 'usage'`** — lets Babel inject only the polyfills the source actually uses, scoped to gaps in the target. See [`./corejs-entry-modern.md`](./corejs-entry-modern.md) for the full reasoning.
- **`corejs: { version: '3.49', proposals: true }`** — pins the polyfill database to the current core-js version (3.49.0, March 2026 — see [`../landscape-shifts/core-js-funding-status.md`](../landscape-shifts/core-js-funding-status.md)). Required when `useBuiltIns` is `'usage'` or `'entry'`.

`useBuiltIns: false` is also valid at the modern baseline — see the recommendation in [`../transpilation/babel-preset-env.md`](../transpilation/babel-preset-env.md). For most apps at this baseline, it's the right answer.

## Verification

Three ways to confirm the fix worked. Run them in order; each catches a different class of leftover problem.

### 1. `npx browserslist` returns a modern version list

```sh
$ npx browserslist
chrome 125
chrome 126
chrome 127
...
firefox 129
firefox 130
firefox 131
...
safari 17.4
safari 17.5
safari 17.6
safari 18.0
...
```

If this returns engines below the baseline (Chrome 119, Safari 16.4, etc.), browserslist is reading from somewhere unexpected. Run `npx browserslist --config=` to see the resolved config path. Common culprits: a `.browserslistrc` in a parent directory, a `BROWSERSLIST` env var, a `browserslist` field in a monorepo root `package.json`.

### 2. `npx browserslist --coverage` reports realistic audience coverage

```sh
$ npx browserslist --coverage
These browsers account for X.XX% of all users globally
```

For our baseline, expect 85–90% global coverage. If you see 99%+, your query is too wide; if you see 70% or less, it might be too narrow for your audience (run `--coverage=US` or your specific market).

### 3. Bundle analyzer shows zero (or near-zero) core-js chunks

```sh
# Webpack
npx webpack-bundle-analyzer dist/stats.json

# Vite
npx vite-bundle-visualizer

# Source-map-explorer (works for any bundle with sourcemaps)
npx source-map-explorer 'dist/assets/*.js'
```

In the analyzer output, look for the `core-js/modules/*` directory. **At the modern baseline with `useBuiltIns: 'usage'`, the right number is "very few or zero."** Specific chunks that may legitimately appear:

- `es-iterator-helpers/*` — Safari 17.4–18.3 polyfill (real gap, see [`../runtime-polyfills/iterator-helpers.md`](../runtime-polyfills/iterator-helpers.md))
- `core-js/modules/es.iterator.*` — same as above, Babel's path
- A `Promise.try` shim — trivial, ~50 bytes

What should NOT be there:

- `core-js/modules/es.array.flat`
- `core-js/modules/es.array.includes`
- `core-js/modules/es.object.has-own`
- `core-js/modules/es.set.union`
- `core-js/modules/es.regexp.to-string`
- `regenerator-runtime/*`
- `core-js/modules/web.url`
- `core-js/modules/web.fetch`

If you see any of these, the build is still polyfilling features that are native at the baseline. Most likely cause: stale browserslist (re-check step 1), stale `caniuse-lite` (run `npx update-browserslist-db@latest`), or a transitive dependency forcing core-js inclusion (`npm ls core-js`).

### A grep-based smoke test for transpiled syntax

A quick last-mile check on the emitted bundle:

```sh
# Look for ES5 transpilation artifacts in the output:
grep -l 'regeneratorRuntime\|_asyncToGenerator\|_classCallCheck\|_defineProperty' dist/assets/*.js

# Look for transpiled async/await (regenerator state machine):
grep -l '_callee\|_async\|wrap(function' dist/assets/*.js
```

If any of these appear in the modern bundle, transpilation-to-ES5 is happening. The fix from step 1 should eliminate them; if not, check for other tools in the chain (esbuild, swc, terser passes) that may be lowering syntax independently.

## Recommended config at our baseline

The full canonical recipe, copy-pasteable:

```jsonc
// package.json
{
  "name": "my-app",
  "browserslist": [
    "chrome >= 125",
    "firefox >= 129",
    "safari >= 17.4"
  ]
}
```

```js
// babel.config.js
module.exports = {
  presets: [
    ['@babel/preset-env', {
      // targets auto-load from package.json's "browserslist"
      bugfixes: true,
      shippedProposals: true,
      useBuiltIns: 'usage',
      corejs: { version: '3.49', proposals: true },
    }],
    '@babel/preset-react', // if applicable
    '@babel/preset-typescript', // if applicable
  ],
};
```

Pair with no `import 'core-js/stable'` at the entrypoint. Pair with no `<script src="cdn.polyfill.io/...">` in HTML. See [`./corejs-entry-modern.md`](./corejs-entry-modern.md) and [`./polyfill-io-after-attack.md`](./polyfill-io-after-attack.md) for the entrypoint and CDN cleanup.

If you're using Vite, Next.js, or another modern framework, the framework likely sets browserslist for you — but verify. See [`../products/`](../products/) for per-framework details (in progress).

## Cross-reference

- [`./corejs-entry-modern.md`](./corejs-entry-modern.md) — the related anti-pattern: `useBuiltIns: 'entry'` shipping core-js to modern users.
- [`./target-es5-modern.md`](./target-es5-modern.md) — its sibling: targeting ES5 in tsconfig.
- [`./defensive-overpolyfilling.md`](./defensive-overpolyfilling.md) — the broader anti-pattern this is a special case of.
- [`./polyfill-io-after-attack.md`](./polyfill-io-after-attack.md) — the runtime-CDN counterpart.
- [`../transpilation/babel-preset-env.md`](../transpilation/babel-preset-env.md) — full preset-env reference.
- [`../transpilation/swc-targets.md`](../transpilation/swc-targets.md), [`../transpilation/esbuild-targets.md`](../transpilation/esbuild-targets.md) — non-Babel paths (which have their own browserslist gotchas — esbuild ignores it entirely).
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical browserslist queries for the modern baseline.
- [`../landscape-shifts/core-js-funding-status.md`](../landscape-shifts/core-js-funding-status.md) — single-maintainer context for core-js itself.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what Chromium 125 / Safari 17.4 / Firefox 129 means in practice.
