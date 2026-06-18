---
date: 2026-04-27
coverage: canonical
peers:
  - ./babel-preset-env.md
  - ./esbuild-targets.md
  - ./typescript-target-esnext.md
  - ../anti-patterns/corejs-entry-modern.md
  - ../anti-patterns/target-es5-modern.md
  - ../build-tools/browserslist-recipes.md
  - ../products/next-js-15.md
  - ../products/vite-6.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://swc.rs/ — project home
  - https://swc.rs/docs/configuration/swcrc — `.swcrc` reference
  - https://swc.rs/docs/configuration/compilation — `jsc.target` and compilation options
  - https://swc.rs/docs/configuration/supported-browsers — `env.targets`, browserslist auto-discovery
  - https://github.com/swc-project/swc — monorepo, issue tracker
  - https://github.com/swc-project/swc/issues/9593 — ES2023/ES2024 target support tracking
  - https://github.com/swc-project/swc/discussions/3942 — polyfill global-pollution discussion
---

# SWC targets and polyfills

The Rust-based Babel alternative. ~20–70× faster than Babel for typical workloads. Default in Next.js 12+, the React-SWC plugin in Vite, Bun's transformation fallback, Parcel 2+, Deno's deploy infrastructure. This file is the targets-and-polyfills reference; for syntax-level options see the linked SWC docs.

## What it is

SWC (Speedy Web Compiler) is a Rust-based TypeScript/JavaScript compiler with the same broad job description as Babel: parse, transform, emit. Unlike Babel, it's a single Rust binary with no plugin ecosystem in JavaScript — plugins are either bundled or written in Rust (with WASM-based extensibility added in v1.4+, still maturing).

The trade-off vs Babel is speed-for-coverage: SWC is dramatically faster but its `env` (polyfill) coverage is shallower. Babel's preset-env knows about more proposals and edge cases. For application code at the modern baseline this rarely matters; for libraries trying to support every browser ever, Babel is still safer.

## Targets configuration

A complete `.swcrc` for the modern baseline:

```jsonc
{
  "jsc": {
    "parser": {
      "syntax": "typescript",
      "tsx": true,
      "decorators": true
    },
    "target": "es2024",
    "experimental": {
      "plugins": []
    }
  },
  "env": {
    "targets": "chrome >= 125, firefox >= 129, safari >= 17.4",
    "mode": "usage",
    "coreJs": "3.49"
  }
}
```

Two distinct target axes are at play: `jsc.target` (syntax-level) and `env.targets` (browser-version-level for polyfill inclusion).

## `jsc.target` — syntax-level target

What syntax SWC will lower the source to. Accepted values: `es3`, `es5`, `es2015`, `es2016`, `es2017`, `es2018`, `es2019`, `es2020`, `es2021`, `es2022`, `es2023`, `es2024`, `esnext`. ES2023 and ES2024 support landed in SWC v1.8.0 (November 4, 2024). ([swc-project/swc#9593](https://github.com/swc-project/swc/issues/9593))

At our baseline, use `"es2024"` or higher. `esnext` is also reasonable for application code where SWC's version pin is under your control.

This option controls *only* syntax. Setting `jsc.target: "es2024"` will not include `Set.prototype.intersection` polyfills if the engine lacks them — that's the `env` block's job.

## `env.targets` — browser-version target

The browser-version target. Controls which features are considered "missing" and may be polyfilled (when `env.mode` requests it). Same string format as Babel's `targets` and as a browserslist query.

Three accepted forms, matching Babel:

```jsonc
// Direct, explicit
"env": { "targets": { "chrome": "125", "firefox": "129", "safari": "17.4" } }

// Browserslist string
"env": { "targets": "chrome >= 125, firefox >= 129, safari >= 17.4" }

// Defer to .browserslistrc / package.json "browserslist" — omit env.targets
"env": { "mode": "usage", "coreJs": "3.49" }
```

## `env.mode` — polyfill inclusion mode

Same semantics as Babel's `useBuiltIns`. Three values:

| `env.mode` | Behavior | Recommended |
|---|---|---|
| `undefined` (omitted) | No polyfill inclusion. Smallest bundle. | At the modern baseline if no polyfill is needed |
| `"usage"` | Per-file AST analysis; only used polyfills are injected | When polyfills are needed |
| `"entry"` | A single global `import 'core-js/stable'` is split per browserslist | The 2018-era pattern; see [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md) |

SWC's `usage` mode has a documented limitation relative to Babel: dynamic property access (`foo['a' + 't']()`) is not statically analyzed, so the relevant polyfill is not injected. The SWC docs note this directly. ([SWC supported-browsers docs](https://swc.rs/docs/configuration/supported-browsers))

## `env.coreJs` — core-js version

A string version, typically `"3.49"`. Pin to a minor version (recommended) so SWC knows which polyfill database to consult. A bare `"3"` is interpreted as `"3.0"` and excludes the last several years of polyfills — don't.

```jsonc
{
  "env": {
    "mode": "usage",
    "coreJs": "3.49"
  }
}
```

Note the field is `coreJs` (camelCase, capital-J) in `.swcrc` — distinct from Babel's `corejs` (lowercase). SWC also doesn't accept the `{ version, proposals }` object form Babel does; the proposals opt-in is implicit via the version pin.

## What SWC handles (the surface)

- **TypeScript** — first-class support; `jsc.parser.syntax: "typescript"` is the entry point. Stripping types is the most common SWC use case.
- **JSX** — `jsc.parser.tsx: true` plus `jsc.transform.react.runtime: "automatic"` for the modern (React 17+) JSX transform.
- **Decorators** — both legacy TypeScript-style (`jsc.parser.decorators: true`, `jsc.transform.decoratorVersion: "2021-12"`) and the standard 2023-11 proposal (`"2022-03"` — the value naming is historical and slightly out of sync with the proposal versions).
- **Class fields, private methods, top-level await, optional chaining, nullish coalescing** — all transpiled when target is below the syntax's introduction year.
- **Runtime polyfill inclusion via core-js** — when `env.mode` is `"usage"` or `"entry"`.

## What SWC doesn't handle as deeply

- **Polyfill auditing.** Per the SWC docs and as flagged in tracker issues, `env` coverage is shallower than Babel's preset-env. Some core-js polyfills don't get injected in `usage` mode even when the AST plainly contains the call. ([SWC #9544 — `forEach` polyfill not working with `usage`](https://github.com/swc-project/swc/issues/9544); [SWC #6460 — `.at()` not polyfilled in some configurations](https://github.com/swc-project/swc/issues/6460))
- **Stage 3+ proposals.** SWC tracks shipped/Stage 4 proposals reliably. Earlier-stage proposals (Pattern Matching, the pipeline operator) have spotty support and may need a separate plugin.
- **Plugin ecosystem.** Babel's plugin ecosystem in npm is enormous; SWC's WASM-plugin story is younger and many third-party plugins don't exist (or exist only as Rust forks).

If your project actively depends on a niche Babel plugin, the migration to SWC may not be drop-in. For pure TypeScript-and-React-and-modern-syntax application code, it usually is.

## Browserslist auto-discovery

Since v1.1.10 (per the SWC supported-browsers docs), SWC reads `.browserslistrc` and `package.json` `"browserslist"` automatically when `env.targets` is omitted. ([swc.rs/docs/configuration/supported-browsers](https://swc.rs/docs/configuration/supported-browsers))

There are caveats: some integrations (e.g., older `swc-loader` versions) shipped before this auto-discovery was reliable. ([swc-loader#37](https://github.com/swc-project/swc-loader/issues/37)). At current versions of `@swc/core`, `swc-loader`, and the `@swc/cli`, browserslist is honored. Verify by running `npx swc src/index.ts -o /tmp/out.js` and checking that output reflects your `.browserslistrc`.

## At our baseline (the recipe)

For an application using TypeScript, React, and the modern baseline:

```jsonc
// .swcrc
{
  "jsc": {
    "parser": {
      "syntax": "typescript",
      "tsx": true,
      "decorators": true
    },
    "target": "es2024",
    "transform": {
      "react": {
        "runtime": "automatic",
        "development": false,
        "refresh": false
      },
      "decoratorVersion": "2022-03"
    }
  },
  "env": {
    "targets": "chrome >= 125, firefox >= 129, safari >= 17.4",
    "mode": "usage",
    "coreJs": "3.49"
  },
  "minify": false
}
```

If you're delegating browserslist to `.browserslistrc`, drop `env.targets`:

```jsonc
{
  "jsc": { "target": "es2024", "parser": { "syntax": "typescript", "tsx": true } },
  "env": { "mode": "usage", "coreJs": "3.49" }
}
```

## Where you're already using SWC

You probably are, even if you didn't pick it directly:

- **Next.js 12+** — SWC is the default compiler. Next.js 15 uses SWC for transformation under Turbopack. Babel still kicks in if a `.babelrc` is present in the project (which disables SWC). The Next docs explicitly recommend dropping `.babelrc` to keep SWC active. ([Next.js architecture: Next.js Compiler](https://nextjs.org/docs/architecture/nextjs-compiler))
- **Vite** — `@vitejs/plugin-react-swc` is the React-with-SWC plugin (vs `@vitejs/plugin-react` which uses Babel). Many starter templates default to SWC.
- **Bun** — Bun's bundler ships its own JS/TS transformer (not SWC), but SWC is still common via plugin paths and tooling.
- **Parcel 2+** — uses SWC for JS/TS transformation by default.
- **Deno Deploy / Deno** — uses SWC internally for JS parsing.

In Next.js, Vite-with-plugin-react-swc, and Parcel, your `.swcrc` (if present) is honored. Most projects don't write one — the framework's built-in defaults match the modern baseline well enough.

## When SWC is wrong

Two cases:

- **You depend on a Babel plugin with no SWC equivalent.** Common examples: `babel-plugin-styled-components` (has SWC ports of varying quality), `@babel/plugin-proposal-pattern-matching` (Stage 1; no SWC equivalent), `babel-plugin-macros` (Babel-specific by design). Audit your `babel.config.js` plugins list before migrating.
- **You need exhaustive polyfill coverage at a very low browser floor.** Babel's preset-env has more polyfills wired in than SWC's `env` block. At the modern baseline this gap is invisible; at IE11/Safari 12 floors it isn't.

## Cross-reference

- [`./babel-preset-env.md`](./babel-preset-env.md) — the option-by-option Babel reference; SWC mirrors most of it.
- [`./esbuild-targets.md`](./esbuild-targets.md) — the no-polyfill alternative.
- [`./typescript-target-esnext.md`](./typescript-target-esnext.md) — what `target` means in tsconfig vs SWC's `jsc.target`.
- [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md) — the `mode: "entry"` anti-pattern.
- [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) — the `jsc.target: "es5"` anti-pattern.
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical queries for the modern baseline.
- [`../products/next-js-15.md`](../products/next-js-15.md) — Next.js 15's SWC defaults.
- [`../products/vite-6.md`](../products/vite-6.md) — Vite 6 + plugin-react-swc.
