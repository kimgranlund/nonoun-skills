---
date: 2026-04-27
coverage: canonical
peers:
  - ../transpilation/typescript-target-esnext.md
  - ../transpilation/babel-preset-env.md
  - ../build-tools/browserslist-recipes.md
  - ../build-tools/esbuild-config.md
  - ../runtime-polyfills/temporal-api.md
  - ../runtime-polyfills/iterator-helpers.md
  - ../js-language-status/iterator-helpers.md
  - ../js-language-status/set-methods.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://www.typescriptlang.org/tsconfig/lib.html — TypeScript `lib` reference + sub-library list
  - https://www.typescriptlang.org/tsconfig/target.html — TypeScript `target` reference
  - https://www.typescriptlang.org/tsconfig/noLib.html — `noLib` option
  - https://github.com/microsoft/TypeScript/issues/60621 — `target: 'ES2024'` library inclusion fix
  - https://github.com/microsoft/TypeScript/pull/60622 — Fix library inclusions for ES2024 target
  - https://github.com/microsoft/TypeScript/issues/20595 — DOM + WebWorker mutual-exclusion issue
  - https://github.com/microsoft/TypeScript/blob/main/lib — TypeScript bundled `.d.ts` files (ground truth)
  - https://github.com/sindresorhus/type-fest/blob/main/source/tsconfig-json.d.ts — full sub-library enumeration
---

# TypeScript `lib` and `target` — the API-surface lever vs the syntax lever

[`../transpilation/typescript-target-esnext.md`](../transpilation/typescript-target-esnext.md) covers `target` primarily — what syntax TypeScript emits. This file covers `lib` in depth: the option that controls which **type definitions** TypeScript loads, and the load-bearing distinction between "what syntax I emit" and "what APIs I assume exist at runtime."

> The TL;DR: `target` is a *syntax* knob. `lib` is an *API surface* knob. They're independent. The mismatch trap (`target: 'ES2020' + lib: ['ES2024']`) is a real pattern — type-check assuming polyfills, emit conservative syntax — but only safe if those polyfills actually load at runtime.

## What `lib` actually does

[`compilerOptions.lib`](https://www.typescriptlang.org/tsconfig/lib.html) is an array of strings naming the bundled `.d.ts` files TypeScript should include in the type system. Each string maps to a file in [TypeScript's `lib/` directory](https://github.com/microsoft/TypeScript/blob/main/lib).

These bundled `.d.ts` files declare the global types — `Array.prototype.includes`, `fetch`, `window`, `document`, `URL`, `Iterator`, `Set.prototype.intersection`, etc. They are not polyfills (TypeScript doesn't ship runtime code), only type declarations. They tell the compiler "assume these APIs exist at runtime; trust the developer to provide them."

A few concrete examples of what a `lib` entry brings in:

| `lib` entry | Adds types for |
|---|---|
| `"ES2015"` | `Promise`, `Map`, `Set`, `Symbol`, `Iterator`, `for...of`, generators |
| `"ES2017"` | `async`/`await`, `Object.values`, `Object.entries`, `Atomics` |
| `"ES2020"` | Optional chaining (`?.`), nullish coalescing (`??`), `BigInt`, `Promise.allSettled`, `globalThis`, `String.prototype.matchAll` |
| `"ES2022"` | Class fields (declared types), `Object.hasOwn`, `Array.prototype.at`, `error.cause`, `WeakRef`, `FinalizationRegistry`, top-level `await` |
| `"ES2023"` | `Array.prototype.toSorted`, `toReversed`, `toSpliced`, `with`, `findLast`, `findLastIndex`, `Hashbang Grammar` |
| `"ES2024"` | `Object.groupBy`, `Map.groupBy`, Set methods (intersection/union/difference/etc.), `RegExp` `v` flag, `Promise.withResolvers`, `Atomics.waitAsync` |
| `"DOM"` | `document`, `window`, `HTMLElement`, `fetch`, all DOM event types, `Element` and subclasses |
| `"DOM.Iterable"` | The iterable variants of DOM collections — `NodeList[Symbol.iterator]`, `FormData.entries()`, etc. |
| `"WebWorker"` | `self`, `postMessage`, `WorkerGlobalScope`, no `document`/`window` |

## Default `lib` (when unspecified)

If you do not set `lib`, TypeScript picks defaults based on `target`. From the [TypeScript `lib` docs](https://www.typescriptlang.org/tsconfig/lib.html), the default expansion roughly:

| `target` | Implicit `lib` |
|---|---|
| `ES3` | `["Lib"]` (just the base globals) |
| `ES5` | `["DOM", "ES5", "ScriptHost"]` |
| `ES2015` | `["DOM", "ES6", "DOM.Iterable", "ScriptHost"]` |
| `ES2020` | `["DOM", "ES2020", "DOM.Iterable", "ScriptHost"]` |
| `ES2022` | `["DOM", "ES2022", "DOM.Iterable", "ScriptHost"]` |
| `ES2024` | `["DOM", "ES2024", "DOM.Iterable", "ScriptHost"]` |
| `ESNext` | `["DOM", "ESNext", "DOM.Iterable", "ScriptHost"]` |

A subtle bug worth flagging: TypeScript 5.7 introduced `target: "ES2024"` and **initially failed to map it to the right default `lib`** — `lib.es2024.d.ts` and below were not auto-included. Fixed in [microsoft/TypeScript#60622](https://github.com/microsoft/TypeScript/pull/60622). Verify your TypeScript is 5.7.x (post-fix) or 5.8+ if relying on the default; or set `lib` explicitly.

**Recommendation: always set `lib` explicitly.** Defaults are correct most of the time but the *visibility* matters — a colleague reading your `tsconfig.json` should not have to know TypeScript's internal default-resolution rules to understand what API surface your code is type-checked against.

## Common `lib` configurations

### Browser app at our baseline

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2024", "DOM", "DOM.Iterable"]
  }
}
```

Read as: emit ES2022 syntax; type-check assuming an ES2024 runtime + the DOM + iterable DOM collections. At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+) every engine ships ES2024 APIs, so the runtime assumption holds.

The presence of `DOM.Iterable` is load-bearing if you do `for (const file of fileList)` over a `FileList`, iterate `FormData.entries()`, or spread `NodeList` into an array. Without `DOM.Iterable`, those operations fail to type-check even though they work at runtime.

### Browser app with polyfills

```jsonc
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2024", "DOM", "DOM.Iterable"]
  }
}
```

Read as: emit ES2020 syntax (lower optional chaining, nullish coalescing, etc. — wait, those *are* in ES2020; this would be `target: "ES2017"` for those to be lowered. Adjust to match your actual lowering needs.) but type-check assuming the runtime has ES2024 APIs because **you have polyfills loaded**.

This is the **mismatch pattern** — and it's a real and useful pattern, but only safe if the polyfills actually load. If `lib` includes `ES2024` but your runtime lacks `Object.groupBy` and you have no polyfill for it, you'll get a clean type-check followed by a runtime `TypeError`. The compiler trusted you, and you lied to it.

When you legitimately use this pattern: spell out which polyfills you load, in code (not just in your head):

```ts
// src/polyfills.ts — loaded as the very first import in main.ts
import 'temporal-polyfill/global';            // adds globalThis.Temporal
// (other API polyfills as needed)
```

```ts
// src/main.ts
import './polyfills';
import { Temporal } from 'temporal-polyfill'; // or use globalThis.Temporal
// rest of the app
```

The `lib` configuration is the *contract*; the `polyfills.ts` file is the *fulfillment*. Without the latter the contract is broken.

### Library publishing (don't assume your consumer has polyfills)

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM"]
  }
}
```

A published npm library cannot assume a consumer's runtime has ES2024 APIs. Pin both `target` and `lib` to ES2022 — that's what every supported runtime at our baseline ships natively, no polyfill required.

If your library actually uses ES2024 APIs (e.g., `Object.groupBy`), either:

1. Drop down to ES2022 equivalents (`Map.from(...)` + `forEach` instead of `Object.groupBy`).
2. Document it as a peer-dependency requirement on a polyfill.
3. Bundle a tree-shakeable ponyfill (per-method import, no global pollution). See [`../feature-detection/ponyfill-pattern.md`](../feature-detection/ponyfill-pattern.md).

Option 1 is almost always best for library authors at our baseline.

### Web Worker / Service Worker

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2024", "WebWorker"]
  }
}
```

Note the **absence of `DOM`**. Workers don't have `document`, `window`, or `localStorage`; including `DOM` will compile cleanly but let you type-check code that throws at runtime ("`document is not defined`").

There's a known interop problem: [`DOM` and `WebWorker` overlap on shared types](https://github.com/microsoft/TypeScript/issues/20595) (`Event`, `EventTarget`, `MessageEvent`, etc.) and TypeScript reports duplicate-identifier errors when both are included. The standard workaround is **separate tsconfig files**: one for browser code with `lib: ["ES2024", "DOM", "DOM.Iterable"]`, one for the worker with `lib: ["ES2024", "WebWorker"]`, plus `references` in a root `tsconfig.json` to link them.

```
project/
├── tsconfig.json           # references the two below
├── tsconfig.app.json       # lib: ["ES2024", "DOM", "DOM.Iterable"]
└── tsconfig.worker.json    # lib: ["ES2024", "WebWorker"]
```

Per-file overrides via triple-slash directives are also valid:

```ts
/// <reference no-default-lib="true" />
/// <reference lib="es2024" />
/// <reference lib="webworker" />

self.addEventListener('install', (event) => {
  // Service Worker code
});
```

Use sparingly — the multi-tsconfig approach scales better.

## The `target` ↔ `lib` mismatch trap

The most common misconfiguration: **`target` and `lib` disagree about what the runtime supports**, in a way that hides bugs until production.

| Scenario | `target` | `lib` | Reality | Verdict |
|---|---|---|---|---|
| **Aligned modern** | `"ES2024"` | `["ES2024", "DOM", "DOM.Iterable"]` | Engine has ES2024 | ✅ Correct |
| **Conservative emit, polyfilled runtime** | `"ES2020"` | `["ES2024", "DOM", "DOM.Iterable"]` | Engine has ES2020; polyfills add ES2024 APIs | ✅ Safe **if polyfills load** |
| **Conservative emit, NO polyfills** | `"ES2020"` | `["ES2024", "DOM", "DOM.Iterable"]` | Engine has ES2020; no polyfills | 🔴 Trap — clean type-check, runtime `TypeError` |
| **Aggressive emit, conservative API** | `"ESNext"` | `["ES2020", "DOM"]` | You can write `await` at top level but can't see `Promise.withResolvers` | 🟡 Awkward; unusual but valid |
| **Default everything** | unspecified (`ES3`) | unspecified (default for ES3) | Old engines only | 🔴 Anti-pattern; see [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) |

The trap is row 3 — and it's how teams ship runtime errors after a "successful" type-check. The signal that you might be in row 3:

- You set `lib: ["ES2024"]` for "modern API access."
- You did *not* add a polyfill import.
- `target` is `ES2020` or below (so the syntax is lowered, but the API isn't).

Fix: either drop `lib` to match what the runtime actually has, or add explicit polyfill imports for the ES2024+ APIs you use.

## Sub-library bundles — fine-grained API surface

The `lib` option supports **sub-bundle entries** that pick up only specific feature additions. From [`@type-fest/source/tsconfig-json.d.ts`](https://github.com/sindresorhus/type-fest/blob/main/source/tsconfig-json.d.ts) and [TypeScript's lib reference](https://www.typescriptlang.org/tsconfig/lib.html), the sub-bundles include:

### ES year sub-bundles

| Bundle | Adds |
|---|---|
| `"ES2015.Iterable"` | `Iterator`, `Iterable`, `for...of` types |
| `"ES2015.Promise"` | `Promise`, `PromiseLike` |
| `"ES2015.Proxy"`, `"ES2015.Reflect"`, `"ES2015.Symbol"`, `"ES2015.Symbol.WellKnown"` | The other ES2015 finishers, individually |
| `"ES2018.AsyncIterable"`, `"ES2018.AsyncGenerator"` | Async iteration types |
| `"ES2020.BigInt"` | `BigInt` literal and `BigInt()` constructor |
| `"ES2020.Date"`, `"ES2020.Number"`, `"ES2020.String"`, `"ES2020.Symbol.WellKnown"` | Smaller ES2020 additions |
| `"ES2022.Array"` | `Array.prototype.at` |
| `"ES2022.Error"` | `error.cause` |
| `"ES2022.Object"` | `Object.hasOwn` |
| `"ES2022.RegExp"` | RegExp `d` flag (match indices) |
| `"ES2023.Array"` | `toSorted`, `toReversed`, `toSpliced`, `with`, `findLast`, `findLastIndex` |
| `"ES2023.Collection"` | `Map`/`Set` collection enhancements |
| `"ES2024.ArrayBuffer"`, `"ES2024.Collection"`, `"ES2024.Object"`, `"ES2024.Promise"`, `"ES2024.Regexp"`, `"ES2024.SharedMemory"`, `"ES2024.String"` | Individual ES2024 additions |

### ESNext sub-bundles

| Bundle | Adds |
|---|---|
| `"ESNext.Array"`, `"ESNext.Collection"`, `"ESNext.Iterator"`, `"ESNext.Object"`, `"ESNext.Promise"`, `"ESNext.Regexp"`, `"ESNext.String"`, `"ESNext.Symbol"` | TC39-stage-3-and-up additions per category |
| `"ESNext.AsyncIterable"` | Async iterator helpers (Stage 3) |
| `"ESNext.BigInt"` | BigInt-related Stage 3+ additions |
| `"ESNext.Decorators"` | Standard decorator types |
| `"ESNext.Disposable"` | `Symbol.dispose`, `using` declarations |
| `"ESNext.Error"` | Stage 3 error additions |
| `"ESNext.Intl"` | `Intl` Stage 3 additions |
| `"ESNext.WeakRef"` | `WeakRef`, `FinalizationRegistry` |

### DOM sub-bundles

| Bundle | Adds |
|---|---|
| `"DOM.AsyncIterable"` | Async iteration over DOM (e.g., `ReadableStream` async iteration) |
| `"DOM.Iterable"` | Sync iteration over DOM collections |

### Decorator sub-bundles

| Bundle | Adds |
|---|---|
| `"Decorators"` | Standard (Stage 3 / 2023-11) decorator types |
| `"Decorators.Legacy"` | Legacy (Stage 1) decorator types |

### Worker sub-bundles

| Bundle | Adds |
|---|---|
| `"WebWorker"` | Worker-scope globals |
| `"WebWorker.AsyncIterable"`, `"WebWorker.Iterable"` | Worker iteration types |
| `"WebWorker.ImportScripts"` | `importScripts()` |

### When to use sub-bundles

The sub-bundle granularity matters for:

1. **Backporting individual APIs** without the full ES year. Example: you want `Array.prototype.toSorted` from ES2023 but otherwise target ES2022:
   ```jsonc
   { "lib": ["ES2022", "ES2023.Array", "DOM"] }
   ```
2. **Stage 3 features** without all of ESNext. Example: you want `Symbol.dispose` from the Disposable proposal:
   ```jsonc
   { "lib": ["ES2024", "ESNext.Disposable", "DOM"] }
   ```
3. **Async iteration** in environments without full ES2018. Rarely needed at our baseline.

**At our baseline most projects don't need sub-bundles** — `lib: ["ES2024", "DOM", "DOM.Iterable"]` covers every API the baseline natively ships. Sub-bundles are useful when you want a Stage 3 ESNext feature *plus* a polyfill for it, without grabbing all of ESNext.

## `noLib: true` — the niche escape hatch

[`noLib: true`](https://www.typescriptlang.org/tsconfig/noLib.html) tells TypeScript to **not load any of the bundled `lib.*.d.ts` files**. The compiler will not know `Array`, `Object`, `Promise`, or anything else the standard libraries provide. You must declare every type you use yourself.

Real-world use cases are narrow:

- **Embedded JavaScript engines.** A JS engine inside a game console, a smart-TV runtime, or a niche IoT device that has a custom limited subset of JS — and where you supply your own `.d.ts` describing exactly what's available.
- **Custom DSLs that compile to JS.** Where the "JS" output is restricted to a particular API surface that doesn't match any standard.
- **Type-system experiments / TypeScript wiki samples.**

For 99% of projects, `noLib` is wrong. **What you usually want is `lib`** — a controlled, explicit subset of the standard libraries. `lib: ["ES5"]` is more useful than `noLib: true` because at least you have `Array.prototype.map`.

If you ever set `noLib: true`, you also need to decide what `target` does — TypeScript will still try to lower syntax, but with no `lib` to type-check against, you'll get errors on every standard global. Plan accordingly.

## DOM lib — what's included

The `"DOM"` lib bundle covers the entirety of the browser DOM API surface as standardized by WHATWG / W3C / W3C-WICG. This is the biggest single `.d.ts` in TypeScript's distribution (~30k lines). Highlights:

- **Top-level globals** — `window`, `document`, `console`, `localStorage`, `sessionStorage`, `history`, `location`.
- **Element types** — `HTMLElement`, `HTMLInputElement`, `HTMLDivElement`, ...one per HTML element.
- **Events** — `Event`, `MouseEvent`, `KeyboardEvent`, `PointerEvent`, `CustomEvent`, all the way through.
- **Web APIs** — `fetch`, `URL`, `URLSearchParams`, `Headers`, `Request`, `Response`, `AbortController`, `AbortSignal`.
- **Observers** — `IntersectionObserver`, `MutationObserver`, `ResizeObserver`, `PerformanceObserver`.
- **Modern platform APIs** — `CSS`, `customElements`, `ElementInternals`, `CustomStateSet`, popover/dialog typings, `view-transitions` typings.
- **Web Workers + Service Workers** (the *globals* shared with the main thread) — but **not** the worker-scope globals like `WorkerGlobalScope` (those live in `"WebWorker"`).

A subtle but important point: `"DOM"` includes types for many APIs that are also available in workers (e.g., `fetch`, `URL`, `crypto`). That's why **including `"DOM"` in a worker tsconfig will mostly compile** — but it also gives you `document`, `window`, `localStorage`, none of which are present in workers. Type-check passes, runtime fails. Hence the "use `WebWorker`, drop `DOM`" rule for worker builds.

## At our baseline — recipes by project type

### Standard browser app

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2024", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "skipLibCheck": true,
    "noUncheckedIndexedAccess": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,
    "useDefineForClassFields": true
  }
}
```

### Library publishing to npm

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM"],
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "strict": true,
    "skipLibCheck": true
  }
}
```

### Service Worker (separate tsconfig)

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2024", "WebWorker"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "skipLibCheck": true,
    "types": []
  },
  "include": ["src/sw/**/*.ts"]
}
```

### Mixed app + worker (TypeScript references)

```jsonc
// tsconfig.json (root)
{
  "files": [],
  "references": [
    { "path": "./tsconfig.app.json" },
    { "path": "./tsconfig.worker.json" }
  ]
}
```

## Common `lib` mistakes (the audit checklist)

1. **`lib: ["DOM"]` only**, no `ES<year>`. The compiler falls back to defaults for the JS lib based on `target`, which means the types track `target` not your intent. Always include the JS year explicitly.
2. **`lib: ["ES2024", "DOM"]`** without `DOM.Iterable`. You can't iterate `NodeList`, `HTMLCollection`, `FileList`, etc. — type errors on basic patterns. Add `DOM.Iterable`.
3. **`lib: ["ES2024", "DOM", "WebWorker"]`** in a single config. Duplicate-identifier explosions. Split into two tsconfigs.
4. **`lib` mismatched with polyfills.** You wrote `lib: ["ES2024"]` but didn't load `temporal-polyfill` even though you use `Temporal`. Type-check passes, runtime fails. Audit your polyfill imports against your `lib`.
5. **No `lib`** on a library publication. The implicit default tracks `target`, so a future TypeScript version could change the API surface your published types declare. Pin explicitly.
6. **`noLib: true`** without a deliberate replacement. Almost always wrong; use `lib` with the right subset.

## Cross-references

- [`../transpilation/typescript-target-esnext.md`](../transpilation/typescript-target-esnext.md) — `target` primer; `module`/`moduleResolution` interactions.
- [`./browserslist-recipes.md`](./browserslist-recipes.md) — what the runtime floor looks like in browserslist queries.
- [`./esbuild-config.md`](./esbuild-config.md) — esbuild's `target` is independent of `tsc` `target`/`lib`; both can be set.
- [`../runtime-polyfills/temporal-api.md`](../runtime-polyfills/temporal-api.md), [`../runtime-polyfills/iterator-helpers.md`](../runtime-polyfills/iterator-helpers.md) — concrete polyfills that fulfill `lib` claims.
- [`../js-language-status/iterator-helpers.md`](../js-language-status/iterator-helpers.md), [`../js-language-status/set-methods.md`](../js-language-status/set-methods.md) — TC39 stage map; what each `lib: ESxxxx` actually unlocks.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what the baseline natively ships (the safe `lib` floor).
