---
date: 2026-04-27
coverage: canonical
peers:
  - ./babel-preset-env.md
  - ./swc-targets.md
  - ./typescript-target-esnext.md
  - ../anti-patterns/target-es5-modern.md
  - ../anti-patterns/corejs-entry-modern.md
  - ../build-tools/browserslist-recipes.md
  - ../products/vite-6.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://esbuild.github.io/ — project home
  - https://esbuild.github.io/api/ — API reference (target, format, etc.)
  - https://esbuild.github.io/api/#target — target option specifics
  - https://esbuild.github.io/content-types/ — supported syntaxes; what gets transformed
  - https://github.com/evanw/esbuild — monorepo, issue tracker
  - https://github.com/evanw/esbuild/blob/main/CHANGELOG-2024.md — changelog with ES2024 target addition
  - https://github.com/marcofugaro/browserslist-to-esbuild — browserslist-to-esbuild bridge package
---

# esbuild targets

The Go-based bundler/transpiler. ~10–100× faster than Webpack+Babel for typical builds. Used by Vite (in dev mode and for transformation in build), tsup (the modern library bundler), Bun (similar architectural model), and frequently invoked directly via `esbuild` CLI or `esbuild` Node API. This file covers the `target` option and how esbuild's transpilation differs from Babel/SWC's polyfill-aware mode.

## What it is

esbuild is a Go-based JavaScript and TypeScript bundler designed for raw speed. It parses, transforms, bundles, and minifies in a single pass; emits CommonJS, ESM, or IIFE; supports tree-shaking, source maps, plugins (in JS), and a bundling subset of webpack-style features. It does not target a polyfill ecosystem — it's a syntax transformer, not a runtime-polyfill orchestrator. ([esbuild.github.io](https://esbuild.github.io/))

The trade-off vs Babel and SWC: esbuild is faster than both, but it has nothing like preset-env's `useBuiltIns: 'usage'`. If your code calls `[].at(0)` and your target is too old to have it, esbuild will not inject the polyfill. That's a feature — esbuild is opinionated about staying in its lane — but it shifts the polyfill burden onto you.

## `target` configuration

The single most important option. Specifies which environments your code should run in. esbuild lowers syntax (and a select few selectively-known features) to be compatible with the lowest common denominator across the target list.

Two forms:

```js
// Browser-version target — lowercase, no separator
target: ['chrome125', 'safari17.4', 'firefox129']

// ECMAScript-version target — for syntax-only floor
target: 'es2024'
```

Both are valid. The browser-version form is more precise (esbuild knows exactly what each engine supports); the ES-version form is coarser (esbuild lowers anything past that ES year). At the modern baseline either works; the browser-version form is the recommended primary, with `es2024` as a documentation-friendly secondary.

The string format is **lowercase**, with no punctuation between name and version: `chrome125`, `safari17.4`, `firefox129`, `edge126`, `ios17.4`, `node20`. Periods *are* permitted in the version (Safari uses minor versions; iOS does too). ([esbuild API — target](https://esbuild.github.io/api/#target))

## Per esbuild's docs: `target` lowers syntax, NOT API

When `target` is set, esbuild does two things:

1. **Lowers syntax** that is too new for the target. Arrow functions are lowered for `es5`; class fields are lowered for `chrome84`; private methods are lowered for `safari14`; the `?.` optional chaining operator is lowered for `chrome79`; the `??` nullish coalescing operator is lowered for `chrome79`; etc.
2. **Pass-through, with awareness.** Where the target supports a syntax, esbuild emits it directly (no transformation cost).

What it does **not** do:

- **No `core-js` injection.** esbuild will not include polyfills for `Array.prototype.at`, `Object.hasOwn`, Set methods, `Promise.withResolvers`, `Object.groupBy`, etc. If you call these methods and your target lacks them, the code will throw at runtime in the unsupported browser. The user has to import a polyfill (or, ideally, raise the target). ([esbuild #3803 — How to work with core-js?](https://github.com/evanw/esbuild/issues/3803))
- **No `regenerator-runtime`.** Native `async`/`await` support is widespread; esbuild never lowers async to ES5 generator simulations.
- **No automatic decorator transform metadata.** esbuild supports decorator syntax (legacy and 2023-11) but doesn't emit `emitDecoratorMetadata` reflection records the way TypeScript or Babel can. Reflection-dependent code (older NestJS apps, TypeORM, `class-transformer`) needs the TypeScript compiler or a separate plugin.

This matters because esbuild's `target` is only as protective as its syntax coverage suggests. **Don't assume `target: 'chrome58'` makes your code run on Chrome 58** — it makes the syntax run on Chrome 58. The APIs your code calls might not exist there.

## What esbuild DOES transpile

A representative list of ES2015–ES2024 syntax esbuild lowers when target is below introduction:

- Arrow functions, classes, async functions, generators
- Template literals, default parameters, rest/spread, destructuring
- `let` / `const`, `for...of`
- Optional chaining (`?.`), nullish coalescing (`??`), logical assignment (`||=`, `&&=`, `??=`)
- BigInt literals (`123n`), numeric separators (`1_000_000`)
- Top-level `await`
- Class private fields (`#x`), private methods, static fields
- ES modules (and conversion to ESM/CJS/IIFE per `format`)
- JSX (when `loader: 'jsx'` or `.jsx`/`.tsx` extensions)
- TypeScript types (stripped, not type-checked)
- The RegExp `d` flag (for `match.indices`)
- The RegExp `v` flag (passed through unchanged for `target: es2024+`; transformed for older targets)

## What esbuild does NOT transpile

- **Decorators (the 2023-11 stage 3 proposal)** — esbuild supports decorator *syntax* (parses both legacy and 2023-11 forms) and applies them with the documented runtime semantics, but it does so per the latest spec. There's an issue history around method decorators in class expressions specifically (`evanw/esbuild#3045`); class declarations are well-supported.
- **The pipeline operator (`|>`)** — Stage 2; no esbuild support; would need to be transformed to a function-composition by hand or via SWC/Babel before esbuild sees it.
- **Pattern Matching, Records & Tuples successors, other early-stage proposals** — none supported.

## At our baseline (the recipe)

Two equivalent forms for the modern baseline:

```jsonc
// Browser-version targets — recommended primary
{
  "target": ["chrome125", "safari17.4", "firefox129"]
}

// ES-version target — coarser, simpler
{
  "target": "es2024"
}
```

For a Node API (`esbuild` package), both are accepted as `target` values:

```js
import { build } from 'esbuild';
await build({
  entryPoints: ['src/index.ts'],
  bundle: true,
  format: 'esm',
  target: ['chrome125', 'safari17.4', 'firefox129'],
  outfile: 'dist/bundle.js',
});
```

For `tsup` (which wraps esbuild for library packaging), `target` lives at the top level of `tsup.config.ts`:

```ts
import { defineConfig } from 'tsup';
export default defineConfig({
  entry: ['src/index.ts'],
  format: ['esm', 'cjs'],
  target: ['chrome125', 'safari17.4', 'firefox129'],
  dts: true,
});
```

For Vite (which uses esbuild for transformation), `build.target` controls esbuild's target during the build phase:

```ts
// vite.config.ts
export default {
  build: {
    target: ['chrome125', 'safari17.4', 'firefox129'],
  },
};
```

Vite's default since v6 is `'baseline-widely-available'`, which dynamically resolves to a Baseline-recent target. See [`../products/vite-6.md`](../products/vite-6.md) for the exact resolution semantics.

## `format`

Choose based on consumer:

| Format | Use when |
|---|---|
| `'esm'` | Browser at the modern baseline; Node 14+; tsup library output |
| `'cjs'` | Legacy Node; CommonJS-only consumers |
| `'iife'` | A single-file `<script>` tag in HTML, wrapped to avoid leaking globals |

At the modern baseline, **prefer `'esm'`** for browser bundles. Native ESM is supported in every engine in our baseline and unlocks dynamic `import()` for code-splitting, top-level `await` in dependencies, and import maps when using browser ESM directly.

## `keepNames: true`

Preserves function and class names through minification — useful for stack traces, error monitoring (Sentry, Datadog), and debugging. Costs a small bundle-size increment but pays for itself on production observability.

```js
{
  keepNames: true,
}
```

Default is `false`. Recommended `true` for production builds where you want readable error reports.

## No browserslist auto-discovery

esbuild does **not** read `.browserslistrc` or `package.json` `"browserslist"`. This is a deliberate choice — Evan Wallace's design philosophy is that esbuild stays minimal and orthogonal. If you want to share a browserslist across Babel/SWC/lightningcss/esbuild, you bridge it manually.

The standard bridge is `browserslist-to-esbuild` (npm package, current version 2.1.1, MIT, by Marco Fugaro):

```js
import browserslistToEsbuild from 'browserslist-to-esbuild';

await build({
  // …
  target: browserslistToEsbuild(),  // reads from .browserslistrc / package.json
});
```

The function returns an esbuild-compatible target array (e.g., `['chrome125', 'safari17.4', 'firefox129']`) by translating the browserslist resolution. ([github.com/marcofugaro/browserslist-to-esbuild](https://github.com/marcofugaro/browserslist-to-esbuild))

A second option, `esbuild-plugin-browserslist`, integrates as an esbuild plugin rather than a target-generator. Either works; `browserslist-to-esbuild` is simpler.

## When esbuild is wrong

Two cases:

- **You need polyfill auditing for a low browser floor.** esbuild won't inject polyfills. If your floor is old enough that you depend on `core-js` injection, you need Babel (or SWC's `env.mode: 'usage'`) somewhere in the chain. A common pattern in legacy chains is "Babel → esbuild" or "Babel + esbuild via plugin," but it's complexity worth avoiding when the floor is modern.
- **You need decorator metadata.** TypeScript's `emitDecoratorMetadata` flag emits Reflect-based metadata that some older frameworks (NestJS pre-v10, TypeORM, `class-transformer`) require. esbuild does not emit it. The fix is the TypeScript compiler — run `tsc` to emit the metadata, then esbuild as a downstream bundler. Or use the `esbuild-decorators` plugin family (third-party, varying maintenance).

## Cross-reference

- [`./babel-preset-env.md`](./babel-preset-env.md) — Babel's polyfill-aware mode (the thing esbuild deliberately doesn't have).
- [`./swc-targets.md`](./swc-targets.md) — SWC's `env.mode` (the closer analog if you want polyfill injection with Rust speed).
- [`./typescript-target-esnext.md`](./typescript-target-esnext.md) — `tsc` `target` is independent of esbuild `target`; both can be set.
- [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) — don't set `target: 'es5'` in esbuild any more than you would in tsconfig.
- [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md) — context for why polyfill injection is rarely the right move at this baseline.
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical browserslist queries.
- [`../products/vite-6.md`](../products/vite-6.md) — Vite 6's `build.target: 'baseline-widely-available'` and how it interacts with esbuild.
