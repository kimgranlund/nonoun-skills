---
date: 2026-04-27
coverage: extended
peers:
  - ../js-language-status/decorators.md
  - ../transpilation/typescript-target-esnext.md
  - ../transpilation/babel-preset-env.md
  - ../transpilation/swc-targets.md
  - ../transpilation/esbuild-targets.md
  - ../products/web-components-frameworks.md
primary_sources:
  - https://github.com/tc39/proposal-decorators — TC39 decorators proposal
  - https://babeljs.io/docs/babel-plugin-proposal-decorators — Babel plugin reference
  - https://babeljs.io/docs/v8-migration — Babel 8 migration (decorator version constraints)
  - https://babeljs.io/blog/2022/09/05/7.19.0 — Babel 7.19 stage 3 decorators landed
  - https://babeljs.io/blog/2023/02/20/7.21.0 — Babel 7.21 decorator updates
  - https://www.typescriptlang.org/docs/handbook/decorators.html — TS standard decorator handbook
  - https://devblogs.microsoft.com/typescript/announcing-typescript-5-0/ — TS 5.0 standard decorators
  - https://swc.rs/docs/configuration/compilation — SWC `jsc.transform.decoratorVersion`
  - https://swc.rs/docs/configuration/swcrc — SWC `.swcrc` reference
  - https://esbuild.github.io/content-types/#typescript — esbuild TypeScript decorators stance
  - https://github.com/evanw/esbuild/issues/3482 — esbuild does not transform decorators
---

# Decorators — Stage 3 transpilation across Babel, SWC, TypeScript, esbuild

The Stage 3 decorator transpilation story. As of April 2026, **no JavaScript engine ships standard decorators natively** — your toolchain MUST transpile them. This file is the matrix.

> Cross-reference: [`../js-language-status/decorators.md`](../js-language-status/decorators.md) is the language-status (TC39 stage, engine support). This file is the *transpilation* config matrix.

## What the Stage 3 proposal is

The TC39 [decorators proposal](https://github.com/tc39/proposal-decorators) (champions: Daniel Ehrenberg et al.) reached Stage 3 in March 2022 and has had subsequent semantic refinements; the current API shape is **2023-11**, named after the November 2023 TC39 meeting.

Stage 3 decorators are class-member decorators with a specific runtime contract: the decorator receives `(value, context)` where `context` includes `kind`, `name`, `static`, `private`, and optional helpers (`addInitializer`, `access`). They can be applied to **classes**, **methods**, **getters/setters**, **fields**, **accessors**, and (with `auto-accessor`) the new `accessor` keyword.

What Stage 3 decorators are **not**:

- Not the legacy "Stage 1" form. Legacy decorators are the older shape used by TypeScript's `experimentalDecorators: true`, Angular, NestJS pre-v11, older `class-validator`, `class-transformer`, etc. Different runtime shape; not interchangeable.
- Not parameter decorators. Stage 3 does not include parameter decorators; the legacy form did. Frameworks that need parameter decorators (older NestJS dependency-injection, TypeORM column metadata) currently still need legacy. The TC39 metadata proposal (Stage 2) is the eventual successor.

## Babel — `@babel/plugin-proposal-decorators`

```js
// babel.config.js
module.exports = {
  plugins: [['@babel/plugin-proposal-decorators', {
    version: '2023-11',
  }]],
  // also include preset-env for syntax lowering as needed
  presets: [['@babel/preset-env', {
    targets: { chrome: '125', firefox: '129', safari: '17.4' },
    bugfixes: true,
  }]],
};
```

The plugin's `version` option accepts five values historically:

| Value | Semantic | Status |
|---|---|---|
| `"2023-11"` | November 2023 TC39 update | **Current. Use this.** |
| `"2023-05"` | May 2023 update | Older Stage 3 draft. Migrate to `2023-11`. |
| `"2022-03"` | March 2022 (when Stage 3 was reached) | Older Stage 3 draft. Migrate. |
| `"2021-12"` | Earlier draft | Don't use. |
| `"legacy"` | Stage 1 / TypeScript-experimental shape | For migrating legacy code only. Not interchangeable with the above. |

**Babel 8 will only support `"2023-11"` and `"legacy"`.** All intermediate `2022-03` / `2023-05` / `2021-12` values will be dropped in Babel 8. Migrate now. ([babeljs.io/docs/v8-migration](https://babeljs.io/docs/v8-migration))

If you set Stage 3 decorators (`version: "2023-11"`) and also use `@babel/preset-env`, you can safely **remove any explicit class-elements transform plugins** — Babel will automatically apply the decorators transform before any preset-env class-field processing. ([babeljs.io/docs/babel-plugin-proposal-decorators](https://babeljs.io/docs/babel-plugin-proposal-decorators))

## TypeScript — standard decorators (5.0+)

```jsonc
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "experimentalDecorators": false,    // or omit; false is the modern default
    "useDefineForClassFields": true,
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true
  }
}
```

TypeScript 5.0 (March 2023) shipped Stage 3 standard decorators natively. The implementation follows the TC39 Stage 3 proposal and **does not require any compiler flag** — `experimentalDecorators: false` (or omitted entirely) gives you Stage 3.

Two important notes:

1. **Standard decorators DON'T support method-parameter decoration or `emitDecoratorMetadata`.** If your framework needs those (older NestJS DI, TypeORM column metadata, Angular reflection), you must keep `experimentalDecorators: true` until either the framework migrates or the TC39 metadata proposal lands. ([TS 5.0 announcement](https://devblogs.microsoft.com/typescript/announcing-typescript-5-0/))
2. **TypeScript 4.x doesn't support standard decorators at all.** Must upgrade to 5.0+ (and ideally 5.7+ for `target: "ES2024"` and the cleanest `lib` story). See [`./typescript-target-esnext.md`](./typescript-target-esnext.md).

`useDefineForClassFields: true` is **required** at our baseline when using Stage 3 decorators that replace fields with accessors; the [[Define]] semantic is what the spec assumes. ([microsoft/TypeScript#48814](https://github.com/microsoft/TypeScript/issues/48814))

For frameworks still on legacy decorators (Angular ≤ v17, NestJS ≤ v10, older Lit ≤ 2.x): keep `experimentalDecorators: true`, set `useDefineForClassFields: false` (because Lit and TypeORM expect [[Set]] semantics for legacy field decoration), and don't mix legacy and standard in the same project.

## SWC — `decoratorVersion`

```jsonc
// .swcrc
{
  "$schema": "https://swc.rs/schema.json",
  "jsc": {
    "parser": {
      "syntax": "typescript",
      "decorators": true
    },
    "target": "es2024",
    "transform": {
      "legacyDecorator": false,
      "decoratorVersion": "2023-11"
    }
  }
}
```

SWC supports the same three values as Babel for `decoratorVersion`: `"2021-12"`, `"2022-03"`, `"2023-11"`. **Use `"2023-11"`.** Set `legacyDecorator: false` explicitly (the default is `false` in current SWC versions, but explicit is safer).

For TypeScript projects, set `parser.syntax: "typescript"` and `parser.decorators: true`. For plain JS, `parser.syntax: "ecmascript"` and `parser.decorators: true`. ([swc.rs/docs/configuration/compilation](https://swc.rs/docs/configuration/compilation))

If you migrate from legacy decorators on SWC, the legacy config form is:

```jsonc
{
  "jsc": {
    "parser": { "syntax": "typescript", "decorators": true },
    "transform": {
      "legacyDecorator": true,
      "decoratorMetadata": true   // for emitDecoratorMetadata-equivalent
    }
  }
}
```

SWC is **the only mainstream Rust-based compiler that supports legacy `emitDecoratorMetadata`** — esbuild does not. NestJS, TypeORM, and similar frameworks that depend on metadata historically pinned to SWC for that reason. As they migrate to Stage 3, the legacy metadata flag becomes unnecessary. ([swc-project/swc#5053](https://github.com/swc-project/swc/discussions/5053))

Recent SWC stability: as of April 2026, SWC 1.11+ has stable Stage 3 decorator support; SWC 1.13+ added negative-number decorator argument support and decorator-metadata improvements. Verify your installed SWC ≥ 1.11 if using `decoratorVersion: "2023-11"` in production.

## esbuild — does NOT transpile decorators

esbuild **does not implement the decorator transform.** This is intentional and load-bearing for our toolchain decisions. ([esbuild.github.io/content-types](https://esbuild.github.io/content-types/), [evanw/esbuild#3482](https://github.com/evanw/esbuild/issues/3482))

What this means in practice:

- **`target: "esnext"`** — esbuild passes decorators through unchanged. Native engines do not yet ship standard decorators (April 2026), so this only works if a downstream tool transforms them or if you're targeting a hypothetical future native-decorators environment.
- **`target` < `"esnext"`** — esbuild errors with `Transforming JavaScript decorators to the configured target environment ("es2022") is not supported yet.` ([evanw/esbuild#3482](https://github.com/evanw/esbuild/issues/3482))
- **`emitDecoratorMetadata: true`** in tsconfig — esbuild does NOT support this. It does not replicate TypeScript's type system, so it cannot generate metadata. Frameworks needing metadata cannot use esbuild as the sole compiler.

The right pattern: **transpile decorators with Babel, SWC, or TypeScript BEFORE handing the code to esbuild.** Then run esbuild with `--target=esnext` (or whatever your effective syntax floor is) to do bundling and final lowering. Examples:

- **TypeScript-first**: `tsc` → emits ES2022 with decorators transformed → esbuild bundles. (Tooling: `tsc --build && esbuild --bundle ...`)
- **SWC-first**: `swc src --out-dir build` → esbuild bundles `build/`. Common pattern for Vite / Rspack / Turbopack pipelines.
- **Babel-first**: `babel src --out-dir build` → esbuild bundles `build/`. Slower; mostly for legacy migrations.
- **Vite + plugin-react-swc / plugin-react**: SWC or Babel transforms decorators in the dev/build pipeline before esbuild's pre-bundling step kicks in. Vite handles this orchestration internally.

## Native engine support — none, as of April 2026

| Engine | Stage 3 decorators native? |
|---|---|
| V8 (Chrome / Edge / Node) | No. Tracking: chromestatus.com — "no signals yet" as of April 2026. |
| JavaScriptCore (Safari) | No. WebKit position is "neutral" (https://github.com/WebKit/standards-positions). |
| SpiderMonkey (Firefox) | No. Mozilla position is "non-harmful" (Stage 3) — open to implement, no shipping date. |

Conclusion: **decorators MUST be transpiled at our baseline.** Your toolchain MUST include either:

- Babel with `@babel/plugin-proposal-decorators` `version: "2023-11"`, or
- TypeScript 5+ with `experimentalDecorators: false` (or omitted), or
- SWC 1.11+ with `decoratorVersion: "2023-11"`.

Cross-reference [`../js-language-status/decorators.md`](../js-language-status/decorators.md) for the full TC39 stage map and engine signal tracking.

## Mixing legacy + standard breaks

This is the most common decorator pitfall in mixed codebases:

- **Legacy decorators** (TypeScript `experimentalDecorators: true`) — Stage 1 shape. Decorator receives the descriptor or the class/prototype; mutates in place; returns void or replacement. Used by Angular, NestJS ≤ v10, older `class-validator`, older Lit, MobX legacy mode, TypeORM.
- **Standard decorators** (TypeScript `experimentalDecorators: false`, Babel `version: "2023-11"`, SWC `decoratorVersion: "2023-11"`) — Stage 3 shape. Decorator receives `(value, context)`; returns replacement value or `void`. Used by modern Lit (3+), modern MobX, modern `@workspace/decorators`-style packages.

The two are **incompatible at runtime.** A Stage 1 decorator function called in a Stage 3 context will receive arguments it doesn't expect (and vice versa). You cannot mix them in the same compilation unit. **Pick one.**

If your project uses a framework that mandates legacy (Angular ≤ v17), keep legacy throughout. If you can move forward, migrate to Stage 3 — but check that all your decorator-using libraries support it. Common decorator-heavy libraries' Stage 3 status (April 2026):

| Library | Stage 1 (legacy) | Stage 3 |
|---|---|---|
| Lit | ≤ 2.x | 3.x+ ✅ |
| MobX | legacy mode | strict mode ✅ |
| Angular | all versions ≤ 18 | partial as of v19 |
| NestJS | ≤ v10 | partial (v11 starts migration) |
| `class-validator` | ≤ v0.14 | v0.15+ partial |
| `class-transformer` | all current | not yet |
| TypeORM | all current | not yet |

Verify against the library's current README before flipping `experimentalDecorators` in a project that depends on any of them.

## Common pitfalls

- **Mixing legacy + standard decorator-libraries.** E.g., older `class-validator` (Stage 1) imported into a TypeScript project with `experimentalDecorators: false`. Decorators run, but the validator's expected runtime shape is wrong; validation silently misbehaves. **Symptom: decorators "work" but validators don't fire.**
- **Using `@babel/plugin-proposal-decorators` with `version: "legacy"` when you mean Stage 3.** The legacy form is for migrating *off* old codebases, not for new projects.
- **TypeScript 4.x project trying to adopt Stage 3 decorators.** Won't work — must upgrade to 5.0+. ([TS 5.0 announcement](https://devblogs.microsoft.com/typescript/announcing-typescript-5-0/))
- **esbuild trying to transform decorators directly.** Will error out (`Transforming JavaScript decorators to the configured target environment ... is not supported yet`). Either set `target: esnext` and let a prior step handle decorators, or switch to SWC for the decorator pass.
- **Setting `target: "ES5"` with Stage 3 decorators.** Both TypeScript and Babel will emit working code, but the helper overhead is large and the ES5 fast paths are gone. At our baseline, never `ES5`.
- **`emitDecoratorMetadata` with esbuild.** Not supported; esbuild has no type system.
- **Writing a decorator function shaped for Stage 1 in a Stage 3 context.** Stage 3 decorators receive `(value, context)`, not `(target, propertyKey, descriptor)`. The argument-shape change breaks any decorator function that wasn't rewritten.

## Quick decision matrix

| Tool | Stage 3 decorator config | Notes |
|---|---|---|
| **Babel** | `@babel/plugin-proposal-decorators` with `version: "2023-11"` | Babel 8 will keep only `"2023-11"` and `"legacy"` |
| **TypeScript 5+** | `experimentalDecorators: false` (or omit) + `target: "ES2022"` + `useDefineForClassFields: true` | No flag required — Stage 3 is the modern default |
| **SWC 1.11+** | `jsc.parser.decorators: true` + `jsc.transform.decoratorVersion: "2023-11"` + `legacyDecorator: false` | Faster than Babel; same semantics |
| **esbuild** | Does not transform; pass through with `target: esnext` and let Babel/SWC/tsc handle decorators upstream | No decorator transform; no `emitDecoratorMetadata` |

## Cross-references

- [`../js-language-status/decorators.md`](../js-language-status/decorators.md) — TC39 stage map, engine signals, where the proposal sits
- [`./typescript-target-esnext.md`](./typescript-target-esnext.md) — TypeScript `target` / `lib` / `experimentalDecorators` reference
- [`./babel-preset-env.md`](./babel-preset-env.md) — preset-env reference; coexistence with `plugin-proposal-decorators`
- [`./swc-targets.md`](./swc-targets.md) — SWC `jsc.target` and `env.targets` reference
- [`./esbuild-targets.md`](./esbuild-targets.md) — what esbuild does and doesn't transform
- [`../products/web-components-frameworks.md`](../products/web-components-frameworks.md) — Lit's decorator story, scoped registries
