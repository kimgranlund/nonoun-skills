---
date: 2026-04-27
coverage: advisory
peers:
  - ../transpilation/typescript-target-esnext.md
  - ../transpilation/babel-preset-env.md
  - ../transpilation/swc-targets.md
  - ../transpilation/esbuild-targets.md
  - ../anti-patterns/corejs-entry-modern.md
  - ../anti-patterns/preset-env-no-browserslist.md
  - ../build-tools/browserslist-recipes.md
  - ../build-tools/tsconfig-lib-target.md
  - ../products/vite-6.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://www.typescriptlang.org/tsconfig/target.html — TypeScript `target` reference
  - https://github.com/microsoft/TypeScript/wiki/Performance — TypeScript performance wiki
  - https://v8.dev/blog/high-performance-es2015 — V8 blog on ES2015+ fast paths
  - https://web.dev/articles/baseline-and-polyfills — modern Baseline guidance
  - https://www.debugbear.com/blog/how-does-browser-support-impact-bundle-size — measured bundle impact by target
  - https://www.npmjs.com/package/regenerator-runtime — runtime size reference
---

# Anti-pattern: transpiling to ES5 (or ES2015) in 2026

## The anti-pattern

Three concrete forms, each found in the wild every week of every audit:

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "target": "es5",          // or "ES2015", or "ES2016"
    "module": "commonjs",
    "lib": ["es5", "dom"]
  }
}
```

```js
// babel.config.js
module.exports = {
  presets: [['@babel/preset-env', {
    targets: '> 0.25%, not dead', // still includes IE 11
  }]],
};
```

```js
// build.js (esbuild)
require('esbuild').build({
  entryPoints: ['src/index.ts'],
  target: 'es2015',           // or 'es5'
  outfile: 'dist/bundle.js',
});
```

The result: code that runs on browsers from 2015, but is significantly slower on every browser any of your real users actually runs. **Native modern syntax has fast paths in V8, JavaScriptCore, and SpiderMonkey that transpiled ES5 equivalents do not hit** ([V8 high-performance ES2015](https://v8.dev/blog/high-performance-es2015)). You're shipping more code, that runs slower, to support browsers nobody you serve uses.

## Why it persists

Three reasons, in order of cultural inertia:

1. **`tsconfig.json` files get copy-pasted.** Most TypeScript configs in the wild trace their lineage to a 2018–2019 Stack Overflow answer or boilerplate generator. Those configs specified `"target": "es5"` because it was conservative — it would never break for someone on IE11. The conservatism made sense in 2018. It does not make sense in 2026. ([TypeScript wiki — Performance](https://github.com/microsoft/TypeScript/wiki/Performance))
2. **TypeScript's default `target` was `"ES3"` for years.** The default flipped to `"ES5"` only in TypeScript 3.x, and to `"ES2016"` in 5.0 (March 2023) — but only when no `target` is specified. Existing configs explicitly written before those releases preserve their old value forever. The TypeScript team chose not to change the meaning of `"target": "es5"` (correctly), so the migration burden falls on the consumer.
3. **"Modern syntax breaks in old browsers."** True, but a non-sequitur: old browsers aren't in your support matrix at the modern baseline. The fear is a holdover from when "support matrix" included IE11 by default in the corporate world. At Chromium 125+ / Safari 17.4+ / Firefox 129+, every supported engine parses ES2024 syntax natively. The "safe" choice is to not transpile syntax that's already supported.

## Why it's wrong at the modern baseline

### Performance: native > transpiled

Modern engines have heavily-optimized fast paths for native syntax. Transpiled equivalents fall off those fast paths. Specific cases documented in V8 / JSC / SpiderMonkey benchmarks:

- **Native `class` declarations** hit V8's TurboFan optimization tier directly. ES5 prototype-and-closure simulations do not — they look to the optimizer like generic functions assigning to `this`, and inline-caching is less effective. ([V8 blog — high-performance ES2015](https://v8.dev/blog/high-performance-es2015))
- **Native `async`/`await`** is implemented in V8 by Ignition (the bytecode interpreter) using direct generator-state primitives. Transpiled `async` via `regenerator-runtime` runs as ES5 generator simulation: a state machine emitted as a `switch` statement inside a closure, called per `await` point. The overhead is real and shows up in micro- and macro-benchmarks alike — V8's team highlighted async/generator optimization as one of the biggest wins of the Ignition/TurboFan pipeline.
- **Native `for...of`** uses an iterator-aware fast loop. Transpiled `for...of` calls `Symbol.iterator` lookups and a closure-wrapped iteration helper for every iteration.
- **Native destructuring, rest/spread, default parameters** all have specialized opcodes in modern engines. Transpiled ES5 emits temporary objects and explicit `.length` checks.

Concrete benchmark numbers vary by workload; "transpiled async is 50% slower" is sometimes-true, sometimes-not — but the direction is consistent: native wins, in our experience by 20–60% on async-heavy workloads, and no transpilation strategy will close that gap. The hottest-path generator/async code is where the gap is widest.

### Bundle size: transpiled is bigger

When Babel transpiles async iterator functions, the original source can expand by **6× or more** in transpiled form ([regenerator-runtime PR #17213 size analysis](https://github.com/babel/babel/pull/17213)). The relevant numbers:

- `regenerator-runtime` itself is small in source (~1 KB compressed) but adds **~6.3 KiB** to the bundle when included; some bundle reports it at ~25 KB minified depending on the transpilation pattern.
- Per-file helpers — `_classCallCheck`, `_defineProperty`, `_createClass`, `_inherits`, `_asyncToGenerator`, `_objectSpread`, `_slicedToArray`, `_toConsumableArray`, `_typeof` — accumulate. A medium-sized React app emits 30–50 such helpers, each duplicated per file unless `@babel/plugin-transform-runtime` is configured. Without `transform-runtime` they bloat the bundle linearly with file count. With `transform-runtime` they consolidate to runtime imports — at the cost of an extra `@babel/runtime` dependency.
- Total impact at typical TypeScript-React projects with `target: "es5"`: **30–60 KB gzipped of pure transpilation overhead**, on top of any core-js polyfill bundle ([DebugBear](https://www.debugbear.com/blog/how-does-browser-support-impact-bundle-size)).

### Debuggability: stack traces are worse

Transpiled async/generator code produces stack traces that go through `_asyncToGenerator`, `tryCatch`, `regeneratorRuntime.wrap`, and other internal frames. The original `async function fetchData()` becomes a synthetic `_callee` in the trace. Source maps mitigate this but don't eliminate it — many error monitors (Sentry, Datadog, Rollbar) still surface the transpiled frame when source-map upload misbehaves. Native async preserves the original function name and call site.

## The fix

### TypeScript

```jsonc
// tsconfig.json — modern baseline
{
  "compilerOptions": {
    "target": "ES2022",       // or "ESNext" if you control the toolchain end-to-end
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "lib": ["ES2024", "DOM", "DOM.Iterable"],
    "strict": true
  }
}
```

`ES2022` is the conservative-modern choice: it includes class fields, top-level `await`, `Object.hasOwn`, `Array.prototype.at`, error cause, and `WeakRef` — all natively supported at the modern baseline. `ESNext` is the aggressive choice: it lets you use the `using` declaration, decorators (when stable), and emerging syntax. The TypeScript team's own docs note that `ESNext` "produces output using the latest finalized JavaScript features while transforming only experimental proposals or TypeScript-specific syntax" ([TypeScript tsconfig — `target`](https://www.typescriptlang.org/tsconfig/target.html)).

The tradeoff: `ESNext` means TypeScript will not transpile features that have arrived since your TypeScript version was released — so library authors who can't predict the consumer's runtime should pin to a specific year (`ES2022` or `ES2023`). Application authors can use `ESNext`.

### Babel

Drop the IE-era browserslist query. Use one that matches your actual baseline:

```js
// babel.config.js — modern baseline
module.exports = {
  presets: [['@babel/preset-env', {
    targets: {
      chrome: '125',
      firefox: '129',
      safari: '17.4',
    },
    bugfixes: true,
    useBuiltIns: false,
  }]],
};
```

Or, equivalently, define the targets in `.browserslistrc` and let Babel auto-discover:

```
# .browserslistrc
chrome >= 125
firefox >= 129
safari >= 17.4
```

`bugfixes: true` is worth setting explicitly: it tells preset-env to apply only the syntax transforms required to fix specific browser bugs in your target list, instead of broadly lowering everything. Babel 7.9+ enables this by default in some configurations, but explicit is safer.

### esbuild / SWC

```js
// esbuild
{
  target: ['chrome125', 'safari17.4', 'firefox129'],
}
```

```js
// swc
{
  jsc: {
    target: 'es2022',  // or use env.targets with browserslist
  },
  env: {
    targets: 'chrome >= 125, firefox >= 129, safari >= 17.4',
  },
}
```

## The "modern + legacy" pattern (rarely needed)

If you genuinely need to support IE11 or pre-Safari 14 — and at this baseline you almost certainly don't — the right pattern is **differential serving**: ship two bundles, one modern, one legacy.

The two implementations:

- **`<script type="module">` + `<script nomodule>`** — modern browsers honor `type="module"` and ignore `nomodule`; old browsers do the opposite. Crude but effective for IE11.
- **`@vitejs/plugin-legacy`** — ships modern + legacy chunks with the right script tags emitted automatically. See [`../products/vite-6.md`](../products/vite-6.md). The plugin's own README documents its purpose: "If your target browsers support ESM, you don't need this plugin" — Vite 6+ defaults explicitly drop IE.

If you don't have a legacy floor, don't reach for these tools. The complexity isn't worth it.

## How to audit your project

A search-and-flag audit in the order most likely to find drift:

```sh
# 1. tsconfig targets
grep -rn '"target"' tsconfig*.json packages/*/tsconfig*.json | grep -i 'es5\|es2015\|es2016'

# 2. Babel configs
grep -rn 'targets\|preset-env' babel.config.* .babelrc* package.json

# 3. Browserslist queries that include IE
grep -rn 'browserslist\|\.browserslistrc' package.json .browserslistrc | grep -i 'ie\b\|defaults\|> 0.5%\|last 2 versions'

# 4. esbuild / vite / swc targets
grep -rn 'target.*\(es5\|es2015\|es2016\|"chrome.*1[0-7]"\|"safari.*1[0-3]"\)' \
  vite.config.* webpack.config.* esbuild.config.* swc.config.*

# 5. Polyfill artifacts in the bundle
ls node_modules/.cache/babel-loader/ 2>/dev/null && \
  grep -rn 'regeneratorRuntime\|_asyncToGenerator\|_classCallCheck' dist/
```

Bundle-analyzer evidence: if you see `regenerator-runtime`, `core-js`, or any `node_modules/@babel/runtime/helpers/*` chunk in your shipped bundle, transpilation-to-ES5 is happening somewhere. Hunt it down.

User-agent test: open Chrome DevTools, set the device emulation to a Galaxy S20 (or any modern UA), reload, and check the Network tab. Compare bundle sizes between modern and legacy emulation if differential serving is configured. If they're identical, you're paying the legacy cost on every visit.

## Targets recommendation at this baseline

The four canonical recipes:

| Tool | Setting | Why |
|---|---|---|
| TypeScript | `target: "ES2022"` (apps), `"ESNext"` (apps with controlled toolchain), `"ES2022"` or `"ES2023"` (libraries) | Modern syntax preserved; safe for the baseline |
| Browserslist | `chrome >= 125, firefox >= 129, safari >= 17.4` | Drives Babel, autoprefixer, postcss-preset-env, lightningcss, esbuild |
| Babel preset-env | `targets` from browserslist; `bugfixes: true`; `useBuiltIns: false` | Only fixes specific bugs; no core-js bloat |
| esbuild | `target: ['chrome125', 'safari17.4', 'firefox129']` | Direct, explicit; no auto-discovery surprise |
| SWC | `env.targets` from browserslist OR `jsc.target: 'es2022'` | Same model as Babel |

See [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) for the canonical query and variants (mobile-only, dual-floor, with explicit IE drop).

## Cross-reference

- [`./corejs-entry-modern.md`](./corejs-entry-modern.md) — its sibling: shipping core-js polyfills to modern browsers.
- [`./preset-env-no-browserslist.md`](./preset-env-no-browserslist.md) — what `defaults` actually resolves to (worse than you think).
- [`../transpilation/typescript-target-esnext.md`](../transpilation/typescript-target-esnext.md) — full reference on TypeScript `target` and `lib`.
- [`../transpilation/babel-preset-env.md`](../transpilation/babel-preset-env.md) — preset-env reference, including `bugfixes` and `useBuiltIns`.
- [`../transpilation/swc-targets.md`](../transpilation/swc-targets.md), [`../transpilation/esbuild-targets.md`](../transpilation/esbuild-targets.md) — the non-Babel paths.
- [`../products/vite-6.md`](../products/vite-6.md) — Vite 6+ defaults and `@vitejs/plugin-legacy`.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — concrete capabilities at the baseline.
