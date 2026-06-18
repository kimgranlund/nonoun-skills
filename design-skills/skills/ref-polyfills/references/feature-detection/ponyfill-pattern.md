---
date: 2026-04-27
coverage: extended
peers:
  - ../feature-detection/at-supports-recipes.md
  - ../feature-detection/js-feature-detection.md
  - ../feature-detection/progressive-enhancement.md
  - ../feature-detection/prollyfill-pattern.md
  - ../meta/glossary.md
  - ../meta/decision-tree.md
  - ../runtime-polyfills/iterator-helpers.md
  - ../runtime-polyfills/temporal-api.md
  - ../landscape-shifts/core-js-funding-status.md
primary_sources:
  - https://github.com/sindresorhus/ponyfill — Sindre Sorhus's canonical ponyfill README
  - https://ponyfoo.com/articles/polyfills-or-ponyfills — Nicolás Bevacqua's "Polyfills or Ponyfills?" essay (Pony Foo, 2017)
  - https://github.com/es-shims — es-shims project (Jordan Harband et al.)
  - https://github.com/es-shims/es-shim-api — es-shim API contract (defines `/auto`, `/shim`, `/polyfill`)
  - https://www.npmjs.com/package/es-iterator-helpers — exemplar es-shim
  - https://kikobeats.com/polyfill-ponyfill-and-prollyfill/ — concise contrast across the three
---

# Ponyfill pattern

A ponyfill is a feature shim imported as a pure function (or set of functions). It never mutates globals. It never patches a prototype. It is the modern-default for shipping feature shims that consumers can opt into without paying global-state cost.

## The term

The term "ponyfill" is associated with **Sindre Sorhus**'s canonical [ponyfill repository](https://github.com/sindresorhus/ponyfill) — the README is the de-facto definition document, and Sorhus has authored hundreds of single-feature ponyfills (e.g. `math-log2`, `math-sign`, `math-hypot`, `user-info`). The term entered wider currency through Nicolás Bevacqua's [Pony Foo](https://ponyfoo.com/) essay [*Polyfills or Ponyfills?*](https://ponyfoo.com/articles/polyfills-or-ponyfills), which contrasts the two approaches.

The etymology is a wordplay: a polyfill is "polyfill" + "but pony pure" — the implementation is *like* a polyfill but doesn't pretend to be the platform. Sorhus's README sets this up explicitly: "polyfill, but with pony pureness."

For the term's exact first-use date, the canonical README is the load-bearing reference; Bevacqua's essay is the popularization vector. Both are linked above.

## Polyfill vs ponyfill — the core distinction

```js
// POLYFILL — mutates a global
import 'core-js/proposals/object-group-by';
const grouped = Object.groupBy(items, x => x.kind);
// Object.prototype now permanently has groupBy installed,
// regardless of whether anyone wanted that.

// PONYFILL — pure function import
import groupBy from 'es-shims/Object/groupBy';
const grouped = groupBy(items, x => x.kind);
// Nothing was added to Object. The function is local.

// PONYFILL with auto-fallback — install only if missing
import groupBy from 'es-shims/Object/groupBy/auto';
// (See "/auto entry point" below.)
```

| Aspect | Polyfill | Ponyfill |
|---|---|---|
| Global mutation | Yes — installs on prototype / global | No |
| Tree-shaking | Compromised — side-effect import | Clean — pure-function import |
| Conflict surface | Global; multiple polyfills can step on each other | None — local scope |
| Library-friendly? | No — you'd be mutating consumers' globals | Yes — opt-in import per use site |
| Detection cost | Whole feature must be installed before any usage | Per-call site |
| Removal | Must coordinate the unimport across the codebase | Just stop importing |

## Why ponyfills > polyfills

### 1. Tree-shaking

Polyfills are inherently side-effectful — `import 'core-js/...'` runs install code at module load. Bundlers can't eliminate them without explicit `sideEffects: false` in `package.json`, which most polyfill packages can't honestly assert.

Ponyfills are pure-function exports. Unused imports → eliminated. Used imports → emitted only as the function. No install code, no conditional branches, no prototype walks.

### 2. No global pollution

Polyfilling `Array.prototype.at` mutates `Array.prototype` for every consumer of your code, including 3rd-party libraries you ship alongside. If two libraries polyfill the same prototype method with subtly different semantics, the last one wins — and "last" depends on import order, which is fragile across bundlers.

Ponyfills can't collide — each consumer has its own imported function. Two libraries each importing `es-shims/Object/groupBy` get the same source, called locally; neither affects the other or the host.

### 3. Predictable consumer behavior

Polyfills change the semantics of *built-in* operations. Code that wasn't yours, written by someone else, will silently behave differently because you imported a polyfill. This is fine when the polyfill is faithful, but pragma-defying when it has bugs (which polyfills, especially older ones, often do).

Ponyfills only affect code paths that explicitly call them. If a polyfill has a bug, every call site for that built-in is suspect; if a ponyfill has a bug, only the call sites that explicitly imported it are.

### 4. Library-author friendly

Library authors can't polyfill — doing so mutates consumers' globals without asking. Ponyfills let library authors ship working code on browsers that don't have the feature, without imposing on consumers.

```js
// In your library, this is fine:
import groupBy from 'es-shims/Object/groupBy';
export function summarize(items) {
  return groupBy(items, x => x.kind);
}

// In your library, this is NOT fine:
import 'core-js/proposals/object-group-by';
export function summarize(items) {
  return Object.groupBy(items, x => x.kind);
}
```

The second form modifies the consumer's `Object` whether they wanted it or not. The first form is invisible.

## es-shims — the canonical ponyfill ecosystem

[es-shims](https://github.com/es-shims) (Jordan Harband and contributors) maintains spec-compliant ponyfills for ECMAScript built-ins. The project predates the term "ponyfill" but follows the pattern strictly: per-method modules, no automatic prototype mutation, with optional `/auto` and `/shim` install hooks.

Representative packages:

| Package | What it ponyfills |
|---|---|
| `es-iterator-helpers` | Iterator helpers (Stage 4 / ES2025) |
| `es-shims/Object.groupBy` | `Object.groupBy` |
| `es-shims/Set.prototype.intersection` | Set methods |
| `es-shims/Promise.try` | `Promise.try` |
| `es-shims/Promise.withResolvers` | `Promise.withResolvers` |
| `es-shims/RegExp.escape` | `RegExp.escape` |
| `es-shims/Float16Array` | `Float16Array` |

Each follows the [es-shim API contract](https://github.com/es-shims/es-shim-api):

| Entry | Behavior |
|---|---|
| Default export | The pure-function ponyfill — call directly |
| `/polyfill` | Returns the implementation (native if present, ponyfill otherwise) |
| `/shim` | Function that, when called, installs on the global / prototype if missing |
| `/auto` | Auto-invokes `/shim` on import — convenience for the polyfill use case |

The `/auto` form is the canonical "I want polyfill behavior, but spec-compliant" entry point:

```js
// Calls the install function on import; safe — no-op when feature exists
import 'es-iterator-helpers/auto';
```

For pure ponyfill use:

```js
import getIterator from 'es-iterator-helpers/Iterator.from';
import map from 'es-iterator-helpers/Iterator.prototype.map';
const it = getIterator(arr);
const mapped = map.call(it, x => x * 2);
```

## "Import only on demand" via dynamic import

Pair the ponyfill with feature detection to load it only when needed:

```js
async function getGroupBy() {
  if ('groupBy' in Object) return Object.groupBy;
  const { default: groupBy } = await import('es-shims/Object/groupBy');
  return groupBy;
}

const groupBy = await getGroupBy();
const grouped = groupBy(items, x => x.kind);
```

Bundlers split the dynamic `import()` into its own chunk; modern engines pay zero bytes. This is the pattern used in `../runtime-polyfills/temporal-api.md`, `../runtime-polyfills/urlpattern.md`, and `../runtime-polyfills/iterator-helpers.md`.

## Inline ponyfill — when an `npm install` is overkill

For simple features, an inline ponyfill is cheaper than a package:

```js
// Inline ponyfill for Object.groupBy
function groupBy(items, keyFn) {
  return items.reduce((acc, item) => {
    const key = keyFn(item);
    (acc[key] ??= []).push(item);
    return acc;
  }, Object.create(null));
}
```

Trade-off: you own the spec compliance. For simple cases (groupBy, intersection on small Sets) this is fine. For complex cases (Temporal — calendar systems, time zones, ISO 8601 parsing) the package is worth its weight; rolling your own is months of work.

## When NOT to ponyfill

- **The feature must be on a global because 3rd-party code references it directly.** `globalThis.fetch` is an example — every library expects `fetch` on the global, not as an import. Polyfill (with `/auto`) is the right call.
- **The feature is universal at your baseline.** If `'groupBy' in Object` is true on every browser you support, neither polyfill nor ponyfill — use native.
- **The feature is a behavior change to a host object you don't own.** E.g. fixing a `JSON.stringify` bug for a specific edge case. Mutating `JSON.stringify` via a polyfill is the only path; no ponyfill helps.

## When ponyfill > polyfill (most of the time)

- Library code (you don't get to mutate consumers' globals).
- Application code where the feature is local to specific call sites.
- Anywhere tree-shaking is a goal.
- Anywhere you want to remove the shim cleanly when your floor moves up.

## Anti-patterns

### Mixing polyfill + ponyfill imports for the same feature

```js
// In one file:
import 'core-js/proposals/object-group-by';
const grouped = Object.groupBy(items, x => x.kind);

// In another file:
import groupBy from 'es-shims/Object/groupBy';
const grouped2 = groupBy(otherItems, x => x.kind);
```

Both work, but the polyfill side-effect ships globally. Pick one and stick to it. At our baseline, the ponyfill side is almost always cheaper.

### Importing the polyfill "just in case" alongside native usage

```js
import 'es-iterator-helpers/auto'; // ~10 KB
const result = Iterator.from(arr).map(...).take(5).toArray();
```

If your floor is Safari 18.4+ / Firefox 131+ / Chrome 122+, the `/auto` import is dead-weight. Either drop it (your code now requires native iterator helpers — universal at the higher floor) or guard it behind dynamic import.

## Cross-references

- `prollyfill-pattern.md` — speculative pre-spec implementations; distinct from ponyfill.
- `js-feature-detection.md` — the detection patterns that gate dynamic-import ponyfill loading.
- `progressive-enhancement.md` — when to skip the ponyfill and degrade.
- `../meta/glossary.md` — short definitions of polyfill / ponyfill / shim / prollyfill.
- `../meta/decision-tree.md` — Step 6 of the do-I-need-a-polyfill flow.
- `../runtime-polyfills/iterator-helpers.md` — concrete es-shim usage example.
- `../runtime-polyfills/temporal-api.md` — concrete ponyfill-via-dynamic-import example.
- `../landscape-shifts/core-js-funding-status.md` — why core-js (the polyfill ecosystem's heavyweight) is increasingly fragile, and why ponyfills are the safer default.
