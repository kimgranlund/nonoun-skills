---
date: 2026-04-27
coverage: canonical
peers:
  - ../js-language-status/decorators.md
  - ../transpilation/decorators-stage-3.md
  - ../transpilation/babel-preset-env.md
  - ../transpilation/swc-targets.md
  - ../transpilation/esbuild-targets.md
  - ../anti-patterns/target-es5-modern.md
  - ../build-tools/tsconfig-lib-target.md
  - ../build-tools/browserslist-recipes.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://www.typescriptlang.org/tsconfig/target.html — TypeScript `target` reference
  - https://www.typescriptlang.org/tsconfig/lib.html — TypeScript `lib` reference
  - https://www.typescriptlang.org/tsconfig/module.html — TypeScript `module` reference
  - https://www.typescriptlang.org/tsconfig/moduleResolution.html — TypeScript `moduleResolution` reference
  - https://www.typescriptlang.org/docs/handbook/2/decorators.html — Standard decorator handbook
  - https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-0.html — TS 5.0 standard decorators
  - https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-7.html — TS 5.7 ES2024 target
  - https://github.com/microsoft/TypeScript/wiki/Performance — TypeScript performance wiki
  - https://github.com/microsoft/TypeScript/issues/48814 — `useDefineForClassFields` defaults at ES2022
  - https://github.com/microsoft/TypeScript/pull/62338 — Deprecate `--moduleResolution node10`
---

# TypeScript `target`, `lib`, `module`, `moduleResolution` — what each one actually does

The most-misconfigured aspect of typical TypeScript projects. Most of the confusion is caused by treating `target` as if it were a polyfill setting. It is not.

## What `target` actually does

`compilerOptions.target` sets the **syntax-level downlevel target** for the JavaScript that TypeScript emits. It controls which language features get syntactically transformed into older equivalents:

- `class` → ES5 prototype boilerplate (only at `target: "ES3"` / `"ES5"`)
- `async`/`await` → generator state machine + `regenerator-runtime` (only at `target: "ES5"` / `"ES2016"`)
- `??` and `?.` → conditional + null-check expressions (only at `target` < `"ES2020"`)
- Class fields → constructor assignments (only at `target` < `"ES2022"`)
- Top-level `await` → not supported below `"ES2017"` for emit reasons
- Decorators → see decorator section below

What `target` does **not** do:

- **It does not polyfill APIs.** `target: "ES2015"` does not make `Promise`, `Map`, or `Set` available at runtime. Those are runtime APIs; you need a polyfill (or a runtime that ships them).
- **It does not change type-checking.** Type-checking is driven by `lib`, not `target`. Setting `target: "ES5"` does not make `Promise` disappear from the type system.
- **It does not affect module syntax.** Module syntax is driven by `module`, not `target`.

`target` is a *syntax* lever, period. ([TypeScript tsconfig — target](https://www.typescriptlang.org/tsconfig/target.html))

## Available values

`ES3`, `ES5`, `ES2015` (= `ES6`), `ES2016`, `ES2017`, `ES2018`, `ES2019`, `ES2020`, `ES2021`, `ES2022`, `ES2023`, `ES2024` (added in TypeScript 5.7), `ESNext`.

`ESNext` is a moving target that resolves to whatever the latest finalized JavaScript syntax is in your TypeScript version. Library authors usually pin a specific year (e.g. `ES2022`); application authors often use `ESNext`.

## Default value

If `target` is unspecified, TypeScript defaults to `ES3` (per the official tsconfig docs and the wiki performance notes). This default is preserved for backward compatibility with very old configs. Real projects almost always override it; if you don't see a `target` in your config, **you are emitting ES3** — assume legacy and audit. ([TypeScript tsconfig — target](https://www.typescriptlang.org/tsconfig/target.html))

(Note: TypeScript 5.0 changed the *bundled-template* default in `tsc --init` to `ES2016`, and the TS team has been migrating recommendations forward — but the unspecified-`target` semantic is still `ES3`.)

## At our baseline (recommendation)

For Chromium 125+ / Safari 17.4+ / Firefox 129+:

- **`target: "ES2022"`** — conservative-modern. Includes class fields, `Object.hasOwn`, `Array.prototype.at`, error cause, `WeakRef`, top-level `await` (with the right `module` setting). All natively supported across the baseline. **This is the safest "modern" choice for libraries and apps.**
- **`target: "ESNext"`** — aggressive. Use only when you control the entire toolchain end-to-end. Acceptable for applications. **Not recommended for libraries**, because emit changes between TypeScript versions, which is unstable for downstream consumers.
- **Never `ES5` at this baseline.** Cross-reference [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md). Modern engines have specialized fast paths for native syntax that transpiled equivalents do not hit; ES5 emit is bigger, slower, and harder to debug.

The 2ality 2025 tsconfig guide and Effective TypeScript 2025 review converge on `ES2022` as the modern sweet spot for both browser and Node.js targets at this baseline. ([2ality](https://2ality.com/2025/01/tsconfig-json.html))

## `lib` vs `target` — the load-bearing distinction

`lib` controls the **type definitions** TypeScript loads — i.e., what TypeScript thinks is available at runtime. `target` controls **syntax emit**. They are independent and can diverge intentionally.

Common pattern:

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",                       // emit ES2022 syntax
    "lib": ["ES2024", "DOM", "DOM.Iterable"]  // type-check assuming ES2024 APIs
  }
}
```

This says: *I want to emit ES2022 syntax (because I have a downlevel target like older Node or older browsers), but I have polyfills (or a runtime) that supplies ES2024 APIs at runtime, so let me use them in my code.*

You see this in:

- **Browser apps with polyfills**: `target` matches your downlevel needs; `lib` includes everything your polyfills supply.
- **Node.js apps**: `target: "ES2022"` (works on all current LTS Node), `lib: ["ES2024"]` (Node 22+ ships ES2024 APIs).
- **Library authors**: pin both — `target: "ES2022"`, `lib: ["ES2022", "DOM"]` — because you cannot assume your consumer has polyfills.

If you don't set `lib`, TypeScript uses a default that's tied to your `target`. The default for `target: "ES2022"` is `["ES2022", "DOM", "DOM.Iterable", "ScriptHost"]`. Setting `lib` explicitly is recommended; it makes your assumptions visible. ([TypeScript tsconfig — lib](https://www.typescriptlang.org/tsconfig/lib.html))

## `module` vs `target`

`module` controls the **module syntax** in the emitted JavaScript: CommonJS, ESM, UMD, AMD, SystemJS, or Node-resolution-aware variants.

| `module` value | When to use |
|---|---|
| `ESNext` | Browser bundles via Vite, esbuild, Rollup, webpack ESM mode. The right default for modern apps. |
| `Node16` / `NodeNext` | Node.js without a bundler. Properly handles dual-package CommonJS/ESM and `package.json` `"exports"`. |
| `Preserve` | TypeScript 5.4+. Keeps the input module syntax intact for downstream tooling. Used with `moduleResolution: "Bundler"`. |
| `CommonJS` | Legacy Node.js without a bundler. Don't pick this for new code. |
| `UMD`, `AMD`, `System` | Don't use these in 2026 unless you have a specific legacy reason. |

Typical modern config: `module: "ESNext"` (browser apps) or `module: "NodeNext"` (Node libraries). The browser bundler handles the actual chunking; TypeScript's job is to keep ESM intact. ([TypeScript tsconfig — module](https://www.typescriptlang.org/tsconfig/module.html))

## `moduleResolution` — `"Bundler"` is the modern default

TypeScript 5.0 introduced `"moduleResolution": "Bundler"`. It is the modern default for applications using a bundler (Vite, esbuild, webpack, Rollup, Turbopack, Rspack).

| Value | Semantics |
|---|---|
| `Bundler` (TS 5.0+) | Like `Node16`/`NodeNext` — supports `package.json` `"exports"`/`"imports"`, conditional exports — but *never* requires file extensions on relative imports. The right default when a bundler handles resolution downstream. |
| `NodeNext` / `Node16` | Strict Node.js ESM resolution. Requires explicit file extensions (`./foo.js`) on relative imports in ESM. The right default for Node.js libraries you publish to npm. |
| `Node10` (formerly `Node`) | **Legacy.** Does not understand `package.json` `"exports"`/`"imports"`. Will be deprecated in TypeScript 6.0 and removed in 7.0. ([microsoft/TypeScript#62338](https://github.com/microsoft/TypeScript/pull/62338)) |
| `Classic` | Older still. Don't use. |

If you are starting a new project in 2026, choose `"Bundler"` (apps) or `"NodeNext"` (libraries you publish). `"Node10"` should not appear in new code. ([TypeScript tsconfig — moduleResolution](https://www.typescriptlang.org/tsconfig/moduleResolution.html))

Note the `module` ↔ `moduleResolution` constraint: if `moduleResolution` is `NodeNext`, then `module` must also be `NodeNext` (or `Node16`). Mismatches throw a compiler error.

## Common misconfigurations

- **`target: "ES5"` on a modern project.** Anti-pattern. See [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md).
- **`lib: ["DOM"]` only.** Missing the JS runtime types. Always include `lib: [<JS year>, "DOM", "DOM.Iterable"]`.
- **`experimentalDecorators: true` + `target: "ESNext"`.** This still emits the legacy Stage 1 decorator form, even though the target supports Stage 3. If you want standard decorators, set `experimentalDecorators: false` (or omit it). See decorator section below.
- **`useDefineForClassFields: false` + Stage 3 decorators on `target: "ES2022"`.** Mismatched semantics; some decorator-based libraries break. Recommended at this baseline: `useDefineForClassFields: true`.
- **`moduleResolution: "Node"` (or `"Node10"`).** Legacy. Will be deprecated in TypeScript 6.0.
- **No `module` set, `target: "ES2022"`.** TypeScript infers `module` from `target` in some cases, but the inference rules are not what you'd expect; always set `module` explicitly.
- **`target: "ES2022"` without `lib`.** TypeScript picks a default `lib` matching your `target`. If you have polyfills for newer APIs, you need to set `lib` to include them — otherwise type-checking misses them.

## TypeScript 5+ standard decorators

TypeScript 5.0 (March 2023) shipped the TC39 Stage 3 standard decorator implementation. The behavior depends on `experimentalDecorators`:

- **`experimentalDecorators: false`** (or omit it) — TypeScript emits **standard Stage 3 decorators**. No flag required; decorators are valid syntax for all new code. The emitted JavaScript follows the 2023-11 decorator semantics.
- **`experimentalDecorators: true`** — TypeScript emits **legacy Stage 1 decorators**. This is the pre-2023 form. Different runtime shape; not interchangeable with Stage 3.

TypeScript 5+ standard decorators work without Babel, without SWC, without anything else. If you use them, you can keep `target: "ES2022"` or higher; TypeScript will emit native decorators at that target.

The two forms are **not interchangeable**. A library written for Stage 1 (legacy) decorators will not work with Stage 3 (standard) decorators, and vice versa. Frameworks that historically used Stage 1 (Angular, NestJS, older `class-validator`) are migrating; do not mix the two in one codebase.

Cross-references:

- [`../js-language-status/decorators.md`](../js-language-status/decorators.md) — TC39 stage map and engine support
- [`./decorators-stage-3.md`](./decorators-stage-3.md) — Babel/SWC/TypeScript transpilation matrix for Stage 3

A known wart: TypeScript 5.0 noted that some features (decorating method parameters, `emitDecoratorMetadata`) are *missing* from standard decorators. Frameworks that depend on `emitDecoratorMetadata` (e.g. older NestJS / TypeORM patterns) still need `experimentalDecorators: true` until the TC39 metadata proposal lands. ([Announcing TypeScript 5.0](https://devblogs.microsoft.com/typescript/announcing-typescript-5-0/))

## Recommended `tsconfig.json` at our baseline

For application authors, browser target:

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2024", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "experimentalDecorators": false,
    "useDefineForClassFields": true,
    "esModuleInterop": true,
    "forceConsistentCasingInFileNames": true,
    "strict": true,
    "skipLibCheck": true,
    "noUncheckedIndexedAccess": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true
  }
}
```

For library authors publishing to npm:

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "experimentalDecorators": false,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "skipLibCheck": true
  }
}
```

The library variant pins `lib` to `ES2022` (don't assume your consumer has ES2024 polyfills) and uses `NodeNext` resolution (so the published types resolve correctly under both Node and bundlers).

## `useDefineForClassFields: true`

Enables the **standard ES2022 class field semantics**. Without it, TypeScript uses its own pre-2022 legacy assignment semantics, which differ from spec.

Specifically:

- `useDefineForClassFields: true` — TypeScript emits `Object.defineProperty(this, "x", ...)` (the spec [[Define]] semantic).
- `useDefineForClassFields: false` — TypeScript emits `this.x = ...` (the pre-2022 [[Set]] semantic).

The difference matters when class fields shadow getters/setters in superclasses, or when decorators replace fields with accessors. The spec semantic is [[Define]]; the legacy TypeScript semantic is [[Set]].

**Default**: when `target` is `ES2022` or higher, TypeScript defaults `useDefineForClassFields` to `true`. ([microsoft/TypeScript#48814](https://github.com/microsoft/TypeScript/issues/48814))

**Set it explicitly** in your config. If you use Stage 3 decorators that replace fields with accessors, the [[Define]] semantic is required and `useDefineForClassFields: true` is correct. If you use Stage 1 (legacy) decorators on field declarations, you may need `useDefineForClassFields: false` — frameworks like Lit historically required this with `experimentalDecorators: true`.

At our baseline with `experimentalDecorators: false` and Stage 3 decorators: **`useDefineForClassFields: true`**.

## TypeScript version notes (April 2026)

The currently shipped 5.x line (per https://www.typescriptlang.org/docs/handbook/release-notes/):

| Version | Released | Notable for this skill |
|---|---|---|
| **5.0** | March 2023 | Stage 3 standard decorators land |
| **5.7** | November 2024 | `target: "ES2024"` lands; `lib: "ES2024"` includes Set methods, `Object.groupBy`, `Promise.withResolvers`, etc. |
| **5.8** | February 2025 | Iteration-checking improvements; ECMAScript-direct execution previews |
| **5.9** | July 2025 | `import defer` support (deferred module evaluation proposal) |

TypeScript 6.0 is anticipated for Q1/Q2 2026 as a transitional release on the existing TypeScript codebase. TypeScript 7.0 is anticipated mid/late 2026 as the Go-based "Corsa" compiler — same language, ~5–10× faster compile, ~50% memory reduction. The Strada → Corsa migration does not change the `target` / `lib` / `module` semantics. ([State of TypeScript 2026](https://devnewsletter.com/p/state-of-typescript-2026/))

Verify your installed TypeScript before relying on `target: "ES2024"` — that flag requires TypeScript 5.7+.

## Cross-references

- [`./babel-preset-env.md`](./babel-preset-env.md) — when TypeScript hands off to Babel for further transformation.
- [`./decorators-stage-3.md`](./decorators-stage-3.md) — Stage 3 decorator transpilation matrix.
- [`./swc-targets.md`](./swc-targets.md), [`./esbuild-targets.md`](./esbuild-targets.md) — non-tsc paths that consume the same `tsconfig.json` for type-checking only.
- [`./transform-runtime-vs-preset-env.md`](./transform-runtime-vs-preset-env.md) — Babel split for libraries vs apps.
- [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) — why `target: "ES5"` is wrong at this baseline.
- [`../js-language-status/decorators.md`](../js-language-status/decorators.md) — TC39 stage map for decorators.
- [`../build-tools/tsconfig-lib-target.md`](../build-tools/tsconfig-lib-target.md) — separating syntax target from API surface.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what the baseline includes natively.
