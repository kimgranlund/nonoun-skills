---
date: 2026-04-27
coverage: extended
peers:
  - ../transpilation/esbuild-targets.md
  - ../build-tools/browserslist-recipes.md
  - ../build-tools/vite-build-target.md
  - ../build-tools/tsconfig-lib-target.md
  - ../products/vite-6.md
  - ../runtime-polyfills/temporal-api.md
  - ../runtime-polyfills/urlpattern.md
primary_sources:
  - https://esbuild.github.io/api/ — esbuild API reference (format, bundle, splitting, external, sourcemap, watch, plugins)
  - https://esbuild.github.io/api/#format — format option (esm | cjs | iife)
  - https://esbuild.github.io/api/#splitting — code splitting (ESM-only)
  - https://esbuild.github.io/api/#external — external option for peer dependencies
  - https://esbuild.github.io/api/#sourcemap — sourcemap option (linked | inline | external | both)
  - https://esbuild.github.io/api/#keep-names — keepNames option
  - https://esbuild.github.io/plugins/ — plugin API + community plugins index
  - https://esbuild.github.io/content-types/ — supported file types and loaders
  - https://github.com/evanw/esbuild/releases/tag/v0.17.0 — context API (replaced incremental + watch options)
  - https://github.com/esbuild/community-plugins — community plugin registry
  - https://github.com/evanw/esbuild/issues/3803 — "How to work with core-js?" (esbuild does not inject polyfills)
---

# esbuild — config landscape beyond `target`

[`../transpilation/esbuild-targets.md`](../transpilation/esbuild-targets.md) covers the syntax-target story: `target: ['chrome125', 'safari17.4', 'firefox129']`, what gets lowered, what stays. This file covers the *rest* of esbuild's surface — the bundling options that decide what gets shipped to the browser before lowering happens at all. Format, splitting, externals, sourcemaps, watch, plugins.

> The TL;DR: esbuild is a bundler, not a polyfill orchestrator. `format` decides how modules talk to each other; `splitting` decides whether dynamic imports become chunks; `external` decides what's left out of the bundle; sourcemaps and watch are operational. None of these inject polyfills — that's still your job.

## `format` — `'esm'` | `'cjs'` | `'iife'`

esbuild [supports three output formats](https://esbuild.github.io/api/#format). Pick by consumer.

| Format | When to use | Notes |
|---|---|---|
| `'esm'` | Browser at the modern baseline; modern Node (≥14); library `dist/*.mjs` outputs; any consumer that imports via `import`. | The right default at our baseline. Native ESM is supported in every browser at Chromium 125+ / Safari 17.4+ / Firefox 129+. Required for `splitting: true`. |
| `'cjs'` | Legacy Node consumers; tooling that expects `require()`; `dist/*.cjs` for dual-package libraries. | Default when `bundle: true` and `platform: 'node'`. ES `export` becomes `module.exports` getters. |
| `'iife'` | A single `<script>` tag in HTML, where you want a self-contained bundle that doesn't leak globals. Common for embeddable widgets, bookmarklets, `<script>`-only deployments. | Wraps the bundle in `(() => { ... })()`. |

For mixed Node consumers, the practical advice from the [esbuild API docs](https://esbuild.github.io/api/) is: when bundling for Node and you depend on packages that mix CJS and ESM entry points, set `format: 'cjs'` to avoid resolution mismatches. For browser bundles at our baseline, `format: 'esm'` is correct and unlocks the rest of esbuild's bundling features.

## `bundle: true | false` — bundling vs single-file transpile

```js
{
  bundle: false, // default — esbuild transforms each file independently
}
```

With `bundle: false`, esbuild treats each entry point as a one-file transformation: TypeScript stripped, JSX compiled, syntax lowered to `target`, output written. No `import` resolution, no module concatenation, no tree-shaking. This is the right mode when another tool (Vite, Rollup, webpack, or a downstream bundler) handles bundling.

```js
{
  bundle: true, // walks the import graph, concatenates modules, tree-shakes
}
```

With `bundle: true`, esbuild follows the `import` / `require` graph from each entry, packages everything into one output file per entry (or chunks if `splitting: true`), and emits in the configured `format`. Tree-shaking happens automatically for ESM imports.

**At our baseline.** Most app builds want `bundle: true` + `format: 'esm'` + `splitting: true`. Library builds (publishing to npm) often want `bundle: true` for the published distribution, with `external` for peer dependencies (next section). Toolchain integrations (Vite using esbuild for transformation only) often want `bundle: false`.

## `splitting: true` — code splitting (ESM-only)

[`splitting: true`](https://esbuild.github.io/api/#splitting) turns dynamic `import()` calls into separate chunks that the browser fetches on demand. Multiple entry points sharing modules also get those modules extracted into a shared chunk — no duplication.

```js
import { build } from 'esbuild';

await build({
  entryPoints: ['src/main.ts', 'src/admin.ts'],
  bundle: true,
  splitting: true,         // requires format: 'esm'
  format: 'esm',           // splitting only works for esm
  outdir: 'dist',          // splitting needs a directory, not a single outfile
  target: ['chrome125', 'safari17.4', 'firefox129'],
});
```

**Hard requirements** ([esbuild #16](https://github.com/evanw/esbuild/issues/16)):

1. `format: 'esm'`. CJS and IIFE do not support splitting.
2. `outdir` (not `outfile`). Splitting produces multiple files; you need a directory.
3. The browser must load entries with `<script type="module">` — the chunks are real ES modules and use native `import` at runtime.

If you set `splitting: true` with `format: 'cjs'` or `format: 'iife'`, esbuild errors out at config time. There's no workaround — different bundlers (Rollup, webpack) support splitting in CJS, but esbuild is ESM-only for this feature.

**At our baseline this is fine** — every browser at Chromium 125+ / Safari 17.4+ / Firefox 129+ has native ESM and dynamic `import()`. No legacy fallback story.

## `external: ['react', 'react-dom']` — peer-dependency externalization

[`external`](https://esbuild.github.io/api/#external) tells esbuild "do not include this module in the bundle; assume the runtime will provide it." The import is preserved as a runtime `require()` (CJS/IIFE) or `import` (ESM).

```js
{
  bundle: true,
  format: 'esm',
  external: ['react', 'react-dom'],  // consumer provides these
}
```

The two main use cases:

1. **Library publishing.** When you publish a React component library to npm, you do not bundle React itself — that would risk multiple React copies in consumers' apps (a hard correctness bug, "Invalid hook call" errors). React is a peer dependency. The library imports `react`; esbuild marks it external; the published bundle contains only your code.
2. **Node built-ins.** All built-in Node modules (`fs`, `path`, `node:fs`, `node:url`, etc.) are automatically external when `platform: 'node'`. You don't need to list them.

A common pattern for library builds is to derive `external` from `package.json`:

```js
import pkg from './package.json' with { type: 'json' };

await build({
  entryPoints: ['src/index.ts'],
  bundle: true,
  format: 'esm',
  outfile: 'dist/index.mjs',
  external: [
    ...Object.keys(pkg.dependencies ?? {}),
    ...Object.keys(pkg.peerDependencies ?? {}),
  ],
  target: ['chrome125', 'safari17.4', 'firefox129'],
});
```

This automatically externalizes everything declared in `dependencies` and `peerDependencies` — exactly the modules a consumer will install for themselves. Wildcard patterns work: `external: ['@scope/*']` excludes all packages under a scope. ([esbuild #727](https://github.com/evanw/esbuild/issues/727) tracks the long-running request to make `peerDependencies` external automatically; until that ships, the `package.json`-driven pattern above is the standard.)

## `sourcemap` — `'linked'` | `'inline'` | `'external'` | `'both'`

[Sourcemap modes](https://esbuild.github.io/api/#sourcemap):

| Value | Output | Use when |
|---|---|---|
| `true` / `'linked'` | `.js.map` file written next to the bundle; bundle gets `//# sourceMappingURL=...` comment. | **Default for production**. Browsers fetch the map only when DevTools is open. |
| `'inline'` | Sourcemap base64-encoded into the bundle as a data URL. | Single-file deployments where you can't host a `.map`. Adds 30-100% to bundle size. |
| `'external'` | `.js.map` file written; **no** `//# sourceMappingURL=` comment. Tools fetch the map another way (e.g. Sentry uploads). | Production where you want maps but don't want to advertise them in-source. |
| `'both'` | Sourcemap is inlined in the bundle **and** written as a `.map` file. | Rarely needed. Useful for builds shipped to multiple environments where one wants inline and one wants external. |

A historical wart noted in [esbuild #1722](https://github.com/evanw/esbuild/issues/1722): older esbuild versions did not accept `'linked'` as a string value — only `true`, `'inline'`, `'external'`, `'both'`. Modern esbuild (≥0.14) accepts `'linked'` as the documented synonym for `true`. If you see a "valid options are: inline, external, both" error, you're on an older version; upgrade.

**At our baseline**: `sourcemap: true` (linked) for production, `sourcemap: 'inline'` for dev, paired with `keepNames: true` for readable error reports.

## `watch` — moved to the context API in v0.17

[esbuild 0.17.0](https://github.com/evanw/esbuild/releases/tag/v0.17.0) (January 2023) **removed** the `watch` and `incremental` options from the `build()` call. The replacement is the context API:

```js
import { context } from 'esbuild';

const ctx = await context({
  entryPoints: ['src/main.ts'],
  bundle: true,
  format: 'esm',
  outdir: 'dist',
  target: ['chrome125', 'safari17.4', 'firefox129'],
  sourcemap: true,
});

await ctx.watch();   // start watching the file system
// later: await ctx.rebuild()  // manual rebuild
// later: await ctx.serve({ port: 8000 })  // dev server
// finally: ctx.dispose()  // tear down
```

The context API holds parsed ASTs and metadata between rebuilds, so incremental rebuilds are dramatically faster than re-running `build()` from scratch. `ctx.watch()` and `ctx.serve()` can run on the same context simultaneously — `serve` will trigger a rebuild on each request and `watch` will rebuild on file changes.

**If you still use `watch: true` in a `build()` call**, you're on esbuild < 0.17. Upgrade — the context API is universal in 2026 tooling.

## `keepNames: true` — preserve function and class names

[`keepNames`](https://esbuild.github.io/api/#keep-names) prevents esbuild's minifier from renaming functions and classes. Useful for:

- **Stack traces.** `Function.name` in error reports remains the original identifier instead of `t` or `e`.
- **Error monitoring.** Sentry, Datadog, Honeybadger, etc. group errors by stack signature; renamed functions fragment the groups.
- **Reflection-driven libraries.** Some frameworks (NestJS, TypeORM patterns, `class-transformer`) use `constructor.name` to dispatch. Renaming breaks them.

```js
{
  minify: true,
  keepNames: true,   // costs ~2-5% bundle size
}
```

Default is `false`. The bundle-size cost is small enough that **enabling it for production is the recommended default** at our baseline. Pair with `sourcemap: true` and your error monitoring becomes much more useful.

## Loaders — built-in file types

[esbuild's content-types page](https://esbuild.github.io/content-types/) lists the built-in loaders:

| Loader | Behavior |
|---|---|
| `js`, `jsx`, `ts`, `tsx` | JavaScript / TypeScript / JSX transformation. Default for the matching extensions. |
| `css` | CSS bundling and minification (when `minify: true`). |
| `json` | Parse and inline as a JS object. |
| `text` | Import file contents as a string. |
| `base64` | Import file contents as a base64-encoded string. |
| `dataurl` | Import as a `data:` URL with auto-detected MIME type. |
| `file` | Copy the file to `outdir` and import the hashed URL as a string. |
| `binary` | Import as a `Uint8Array`. |
| `default` | Loader is inferred from the file extension. |
| `empty` | Treat the file as empty — strips the import entirely. |

Configuration is per-extension:

```js
{
  loader: {
    '.png': 'file',
    '.svg': 'text',     // import the SVG markup as a string
    '.css': 'empty',    // skip CSS imports — Vite/another tool handles them
  },
}
```

JSX in `.js` files is **not** enabled by default. Either rename to `.jsx` or set `loader: { '.js': 'jsx' }` if you have legacy `.js` files containing JSX.

## Plugin ecosystem (briefly)

esbuild's [plugin API](https://esbuild.github.io/plugins/) is intentionally minimal: plugins register `onResolve` and `onLoad` callbacks, can rewrite paths, can return synthesized contents. Plugins run in JS (the JS API) or Go (the Go API). The [community plugin index](https://github.com/esbuild/community-plugins) lists ~150 plugins; the npm `esbuild-plugin` keyword finds more.

The plugins worth knowing at our baseline:

- **`esbuild-sass-plugin`** ([npm](https://www.npmjs.com/package/esbuild-sass-plugin)) — SCSS/Sass support with internal CSS caching (since v2.7.0), works with PostCSS downstream.
- **`esbuild-plugin-postcss`** — run PostCSS plugins (autoprefixer, postcss-preset-env) inline. Mostly redundant at our baseline if Lightning CSS is in the pipeline; see [`./lightningcss-features.md`](./lightningcss-features.md).
- **`@anatine/esbuild-decorators`** — runs `tsc` for files containing decorators (specifically when `emitDecoratorMetadata: true` is needed, which esbuild itself doesn't emit). See [`../transpilation/decorators-stage-3.md`](../transpilation/decorators-stage-3.md).
- **`browserslist-to-esbuild`** — translates a `.browserslistrc` query into an esbuild-compatible target array. See [`./browserslist-recipes.md`](./browserslist-recipes.md).
- **Framework-specific plugins** — `esbuild-plugin-vue`, `esbuild-svelte`, etc. These are rarely first-party; the more common pattern is "use Vite, which uses esbuild internally."

The plugin ecosystem is much smaller than webpack's. That's a deliberate design choice — esbuild stays opinionated and minimal. If you need a sprawling plugin graph, Rollup or webpack are the tools; esbuild's pitch is "you probably don't."

## What esbuild does NOT do (the polyfill caveat)

This is the load-bearing point: **esbuild does not inject runtime polyfills**. ([esbuild #3803](https://github.com/evanw/esbuild/issues/3803)) If your code calls `URLPattern`, `Object.groupBy()`, `Set.prototype.intersection()`, or `Temporal.Now`, esbuild will emit those identifiers as-is. If the target browser doesn't have them, the code throws at runtime.

The split:

- **`target: 'chrome125,safari17.4,firefox129'`** — esbuild lowers *syntax* below the floor: optional chaining if you have a target that lacks it, class fields if a target lacks them, etc. At our baseline, very little syntax needs lowering.
- **API polyfills** — esbuild does not handle. If you use a runtime-polyfillable API and any target lacks it, you bring your own polyfill. See [`../runtime-polyfills/`](../runtime-polyfills/) for the per-API decisions.

The practical consequence: the only path to "esbuild + automatic polyfilling" is to put Babel (with `@babel/preset-env` + `core-js`) somewhere in the pipeline, **or** SWC with `env.mode: 'usage'`. esbuild itself stays in its lane. See [`../transpilation/babel-preset-env.md`](../transpilation/babel-preset-env.md) and [`../transpilation/swc-targets.md`](../transpilation/swc-targets.md).

If you're at our baseline, this is rarely a problem — the polyfill set is tiny (Temporal, URLPattern for Firefox 129–141, Iterator helpers for Safari 17.4–18.3, a couple of trivial ES2025 finishers). Import them explicitly where needed.

## At our baseline — the recipe

Production app build:

```js
// build.mjs
import { build } from 'esbuild';
import pkg from './package.json' with { type: 'json' };

await build({
  entryPoints: ['src/main.ts'],
  bundle: true,
  format: 'esm',
  splitting: true,
  outdir: 'dist',
  target: ['chrome125', 'safari17.4', 'firefox129'],
  sourcemap: true,
  minify: true,
  keepNames: true,
  external: [
    ...Object.keys(pkg.dependencies ?? {}),
    ...Object.keys(pkg.peerDependencies ?? {}),
  ],
});
```

Dev with watch + serve:

```js
// dev.mjs
import { context } from 'esbuild';

const ctx = await context({
  entryPoints: ['src/main.ts'],
  bundle: true,
  format: 'esm',
  outdir: 'dist',
  target: 'esnext',           // dev mode: don't lower
  sourcemap: 'inline',
});

await ctx.watch();
await ctx.serve({
  port: 8000,
  servedir: 'dist',
});

console.log('Dev server: http://localhost:8000');
```

Library publishing (dual ESM/CJS output):

```js
// build-lib.mjs
import { build } from 'esbuild';
import pkg from './package.json' with { type: 'json' };

const external = [
  ...Object.keys(pkg.dependencies ?? {}),
  ...Object.keys(pkg.peerDependencies ?? {}),
];

await Promise.all([
  build({
    entryPoints: ['src/index.ts'],
    bundle: true,
    format: 'esm',
    outfile: 'dist/index.mjs',
    target: ['chrome125', 'safari17.4', 'firefox129', 'node20'],
    sourcemap: true,
    external,
  }),
  build({
    entryPoints: ['src/index.ts'],
    bundle: true,
    format: 'cjs',
    outfile: 'dist/index.cjs',
    target: ['node20'],
    sourcemap: true,
    external,
  }),
]);
```

## Common esbuild-config mistakes (audit checklist)

1. **`splitting: true` with `format: 'cjs'`** — silently fails at config time. Switch to ESM or drop splitting.
2. **No `external` on a library build** — bundles `react`, `vue`, etc. into your published package. Multiple React copies on the consumer side, broken hooks. Always externalize peer deps.
3. **`watch: true` in a `build()` call on esbuild 0.17+** — errors out. Migrate to `context()` + `ctx.watch()`.
4. **`sourcemap: true` in production without restricting upload** — your map files end up on the public origin. Use `sourcemap: 'external'` and upload the maps to your error monitor only.
5. **`keepNames: false` on a build with Sentry/Datadog wired up** — minified function names destroy stack-trace grouping. Set `keepNames: true`.
6. **`bundle: true` + missing `target`** — esbuild's default target is `esnext`, which means *no syntax lowering at all*. At our baseline that's mostly fine, but verify.
7. **Assuming esbuild polyfills APIs** — it does not. Check [`../runtime-polyfills/`](../runtime-polyfills/) for any API you depend on.

## Cross-references

- [`../transpilation/esbuild-targets.md`](../transpilation/esbuild-targets.md) — the syntax-target story (this file's sibling).
- [`./browserslist-recipes.md`](./browserslist-recipes.md) — canonical browserslist queries; `browserslist-to-esbuild` bridge.
- [`./vite-build-target.md`](./vite-build-target.md) — Vite uses esbuild internally; `build.target` flows through.
- [`./tsconfig-lib-target.md`](./tsconfig-lib-target.md) — TypeScript `lib` is independent of esbuild's API surface.
- [`../products/vite-6.md`](../products/vite-6.md) — Vite-as-product wraps esbuild.
- [`../runtime-polyfills/`](../runtime-polyfills/) — what esbuild won't inject; pick polyfills explicitly.
- [`../transpilation/babel-preset-env.md`](../transpilation/babel-preset-env.md) — the polyfill-aware tool esbuild deliberately isn't.
