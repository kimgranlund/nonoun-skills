---
date: 2026-04-27
coverage: extended
peers:
  - ../transpilation/decorators-stage-3.md
  - ../transpilation/babel-preset-env.md
  - ../transpilation/swc-targets.md
  - ../transpilation/esbuild-targets.md
  - ../transpilation/typescript-target-esnext.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://github.com/tc39/proposal-decorators — TC39 proposal-decorators (Stage 3)
  - https://tc39.es/proposal-decorators/ — Spec text
  - https://github.com/tc39/proposal-decorator-metadata — Companion decorator-metadata proposal
  - https://babeljs.io/docs/babel-plugin-proposal-decorators — `@babel/plugin-proposal-decorators` config reference
  - https://babeljs.io/blog/2024/02/28/7.24.0 — Babel 7.24 decorator update notes
  - https://www.typescriptlang.org/docs/handbook/decorators.html — TypeScript decorators handbook (notes Stage 3 since TS 5.0)
  - https://devblogs.microsoft.com/typescript/announcing-typescript-5-0/ — TypeScript 5.0 announcement (March 16, 2023)
  - https://swc.rs/docs/configuration/compilation — SWC compilation config (decorators)
  - https://github.com/swc-project/swc/discussions/5053 — SWC Stage 3 decorator support discussion
  - https://github.com/evanw/esbuild/issues/3482 — esbuild "decorators not supported" tracking issue
  - https://github.com/evanw/esbuild/issues/104 — esbuild decorator feature request
  - https://caniuse.com/decorators — caniuse decorators (no native support across any engine)
---

# Decorators — TC39 Stage 3, native zero, transpile-only at our baseline

The decorator story is the most painful in active TC39 history. Three drafts shipped with three different shapes; existing code in the wild targets a draft that does not match the current proposal; build tools are calibrated to multiple incompatible versions simultaneously. Read this file before configuring decorators on any project.

**TL;DR**: Decorators must be transpiled at our baseline. Use Babel `@babel/plugin-proposal-decorators` with `version: "2023-11"` or SWC `decoratorVersion: "2022-03"` (closest available). TypeScript 5.0+ targets the same Stage-3 shape natively when `experimentalDecorators` is `false`. Do NOT mix legacy `experimentalDecorators` with the standard proposal — different runtime semantics, different emitted output.

## What standard decorators are

The current proposal — formally [tc39/proposal-decorators](https://github.com/tc39/proposal-decorators), Stage 3 — adds `@`-prefixed annotations on:

- **Class declarations** (`@logged class Foo {}`)
- **Class methods**, getters, setters
- **Class fields** (since the 2022-03 revision)
- **Class auto-accessors** (the new `accessor` keyword)
- **Class init blocks** via `context.addInitializer(fn)` (since the 2023-11 revision)

A decorator is a function that receives `(value, context)`, where `context` is a structured object describing the kind, name, and metadata slot of the decorated element. Decorators may return a replacement value or `undefined`. Decorator order is **bottom-up** (innermost first) for reading and **top-down** for application (outermost runs first when applied to its target).

The companion [proposal-decorator-metadata](https://github.com/tc39/proposal-decorator-metadata) — separately tracked — adds `Symbol.metadata` and a `context.metadata` slot. As of April 2026 it is also at Stage 3.

## History — three incompatible drafts

The reason this proposal is dangerous to misconfigure: there have been three substantively different shapes, and code on disk in the wild targets all three.

### Draft 1 — "Stage 1 legacy" decorators (~2014–2016)

The original proposal — the version TypeScript shipped behind `experimentalDecorators`, and the version Babel still implements behind `version: "legacy"`. **Different runtime contract** from anything that followed:

- Decorator function signature: `(target, key, descriptor)` for methods, `(target, key)` for properties.
- No `context` object — decorator authors mutated the property descriptor directly.
- Parameter decorators existed (`function method(@inject('foo') bar) {}`) — TypeScript still supports these; Stage 3 does not.

Most legacy NestJS, TypeORM, MikroORM, MobX, Inversify, and Angular Decorator code on disk targets this shape. **It is not forward-compatible with Stage 3.**

### Draft 2 — "Static decorators" (2018, withdrawn)

A radically different design pushed by the TC39 champions in mid-2018. Static, declarative; intended to enable engine optimization. **Withdrawn** after extensive community feedback that it was too restrictive for real decorator use cases (especially `@observable`-style state mutation hooks). Never shipped in any tool. Mentioned here only because it appears in older TC39 meeting notes and may surface in research-survey.

### Draft 3 — "2022-03 / 2023-11" Stage 3 decorators

The current proposal. Champions: Kristen Hewell Garrett (formerly Kristen Weiss-Garrett), Daniel Ehrenberg, Chris Hewell Garrett. Reached Stage 3 at the **March 2022** TC39 plenary. Two revisions since:

- **2022-03** — initial Stage 3 shape. `(value, context)` signature, `context.addInitializer`, `accessor` keyword.
- **2023-05** — small refinements; allowed decorators on either side of `export`.
- **2023-11** — reached consensus at the November 2023 TC39 meeting; the current canonical shape. The main difference from 2023-05 is in the **execution order of initializers registered through `context.addInitializer`**.

Babel 8 will support **only** `2023-11` and `legacy`; the other versions are deprecation paths.

## Native shipping status (April 2026)

| Engine | Status | Source |
|---|---|---|
| **V8 (Chrome / Edge / Node)** | **Not implemented** | https://chromestatus.com/feature/5197544941158400 — "no signal" |
| **SpiderMonkey (Firefox)** | **Not implemented** | No tracking bug filed for the standard proposal |
| **JavaScriptCore (Safari)** | **Not implemented** | No public commitment |
| **caniuse aggregate** | **0% native support across all browsers** | https://caniuse.com/decorators |

**No engine ships standard decorators at any version.** This has been the steady state for ~3 years post-Stage-3. As of April 2026 there is no signal from V8, SpiderMonkey, or JSC that an implementation is imminent.

## At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+)

**Decorators must be transpiled.** This is non-negotiable at the current baseline; native support is at zero across all three engines and there is no near-term path.

## Build-tool configuration matrix

| Tool | Standard decorators? | Config |
|---|---|---|
| **Babel** | Yes — full support | `@babel/plugin-proposal-decorators` with `{ version: "2023-11" }` |
| **SWC** | Yes — closest available is `2022-03` | `jsc.parser.decorators: true` + `jsc.transform.decoratorVersion: "2022-03"` (since SWC v1.3.47) |
| **esbuild** | **NO transpile** | Parses the syntax but does NOT lower; emit only works if target supports decorators natively (which nothing does). See [issue #104](https://github.com/evanw/esbuild/issues/104), [issue #3482](https://github.com/evanw/esbuild/issues/3482) |
| **TypeScript 5.0+** | Yes — native Stage 3 emit when `experimentalDecorators: false` | `target: "ES2022"` (or higher) + `experimentalDecorators` unset/`false` |
| **TypeScript 4.x** | Legacy only | `experimentalDecorators: true` — Stage 1 emit; not forward-compatible |

See `../transpilation/decorators-stage-3.md` for production-ready recipes per tool.

### The Babel canonical config

```json
{
  "plugins": [
    ["@babel/plugin-proposal-decorators", { "version": "2023-11" }]
  ]
}
```

Available `version` values, per Babel 7.x:

| Version | Origin |
|---|---|
| `"2023-11"` | November 2023 TC39 plenary (current canonical) |
| `"2023-05"` | March/May 2023 TC39 meetings |
| `"2023-01"` | January 2023 TC39 meeting |
| `"2022-03"` | Stage 3 consensus, March 2022 |
| `"2021-12"` | Dec 2021 TC39 presentation |
| `"2018-09"` | Initial Stage 2 proposal |
| `"legacy"` | Stage 1 / TypeScript-compatible legacy decorators |

Babel 8 (in development as of April 2026) will accept only `"2023-11"` and `"legacy"`. Migrate from older versions before upgrading.

### The SWC config

```json
{
  "jsc": {
    "parser": {
      "syntax": "ecmascript",
      "decorators": true
    },
    "transform": {
      "decoratorVersion": "2022-03"
    }
  }
}
```

SWC's decorator transform is calibrated to the **2022-03** spec — the `2023-11` semantics are not yet implemented. For most decorator code (no `addInitializer` reliance) this is functionally equivalent. If you depend on the 2023-11-specific initializer ordering, use Babel.

### The TypeScript 5.0+ config

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "experimentalDecorators": false
  }
}
```

`experimentalDecorators: false` (or omitted) is the key — TypeScript then emits the standard-track shape. With `experimentalDecorators: true`, you are still on legacy decorators, regardless of `target`. **Do not mix**: a decorator function compatible with Stage 3 (signature `(value, context)`) will not run correctly under `experimentalDecorators: true`.

## TypeScript history — the migration trap

TypeScript shipped legacy decorators behind `experimentalDecorators` in **early 2015** (around TS 1.5). Almost a decade of decorator code on disk targets that shape — Angular, NestJS, TypeORM, MikroORM, class-validator, MobX, Inversify, and tens of thousands of internal codebases.

[TypeScript 5.0](https://devblogs.microsoft.com/typescript/announcing-typescript-5-0/) was released **March 16, 2023** with a parallel implementation of Stage-3 decorators. The old flag still exists for backward compatibility:

| Flag state | Decorator shape |
|---|---|
| `experimentalDecorators: true` | Legacy / Stage 1; `(target, key, descriptor)` signature |
| `experimentalDecorators: false` (or unset) | Standard / Stage 3; `(value, context)` signature |

The TypeScript handbook page at https://www.typescriptlang.org/docs/handbook/decorators.html still documents the legacy shape with a note pointing at the 5.0 announcement for the new shape. The TS 5.0 release notes are the source of truth for Stage 3 emit behavior.

**Migration is non-trivial** — the decorator function bodies must be rewritten because the signatures differ. Most ecosystem libraries (Angular, NestJS, etc.) are still on legacy decorators in April 2026 because the migration cost is high and Stage 3 doesn't support parameter decorators that those frameworks rely on.

## Caveats

- **Do not mix `experimentalDecorators` with Babel 2023-11.** The two emit incompatible shapes. Pick one mode and align all tools (TS / Babel / SWC) to the same shape.
- **Parameter decorators are NOT in the Stage 3 proposal.** TypeScript's legacy mode supports them; the standard does not. If you are writing Angular- or NestJS-flavor decorators with `@Inject` on constructor parameters, you are using the legacy shape.
- **`emitDecoratorMetadata` is NOT in the Stage 3 proposal.** That's a TypeScript-specific extension to legacy decorators that emits `Reflect.metadata(...)` calls. The standard `decorator-metadata` proposal uses `context.metadata` instead — no auto-emission. Frameworks relying on `emitDecoratorMetadata` (NestJS, TypeORM) cannot migrate to Stage 3 without rewriting their reflection logic.
- **esbuild does not lower decorators.** It will parse the syntax but emit raw `@decorator` annotations. Since no engine implements them, this means esbuild-built code with decorators will not run unless paired with a separate transpile step (typically `tsc` or Babel before esbuild). This is the load-bearing reason esbuild-only build pipelines fail with decorator-heavy codebases.

## TC39 plenary status — Stage 4 movement

As of **April 2026**, decorators remain at **Stage 3**. There has been no public movement toward Stage 4 in the most recent plenaries. The proposal has been Stage 3 since **March 2022** — over four years. The blocking concern is implementer interest: until at least one engine commits to shipping, Stage 4 (which requires "two compatible implementations") is unreachable.

Verify status against [tc39/proposals](https://github.com/tc39/proposals) and the [proposal-decorators repo](https://github.com/tc39/proposal-decorators) before relying on this file's snapshot.

## Cross-references

- Build-tool recipes: `../transpilation/decorators-stage-3.md`
- Babel preset-env coupling: `../transpilation/babel-preset-env.md`
- SWC targets: `../transpilation/swc-targets.md`
- esbuild targets (and what it skips): `../transpilation/esbuild-targets.md`
- TypeScript target/lib separation: `../transpilation/typescript-target-esnext.md`
- The modern baseline (why nothing native): `../meta/the-modern-baseline.md`
