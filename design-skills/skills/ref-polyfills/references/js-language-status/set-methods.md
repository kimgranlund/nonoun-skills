---
date: 2026-04-27
coverage: canonical
peers:
  - ../runtime-polyfills/set-methods.md
  - ../js-language-status/iterator-helpers.md
  - ../anti-patterns/corejs-entry-modern.md
primary_sources:
  - https://github.com/tc39/proposal-set-methods — TC39 proposal repo (Stage 4)
  - https://github.com/tc39/proposals/commit/bda5a6bccbaca183e193f9e680889ea5b5462ce4 — Set Methods to Stage 4, per 2024.04.08 TC39 plenary
  - https://tc39.es/proposal-set-methods/ — Spec text
  - https://tc39.es/ecma262/2025/ — ECMAScript 2025 Language Specification
  - https://web.dev/blog/set-methods — Baseline Newly available announcement (June 11, 2024)
  - https://webkit.org/blog/14445/webkit-features-in-safari-17-0/ — WebKit Features in Safari 17.0 (September 18, 2023)
  - https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/127 — Firefox 127 release notes
  - https://caniuse.com/mdn-javascript_builtins_set_intersection — caniuse browser support
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set/intersection — MDN reference
---

# Set methods — language status

Seven instance methods on `Set.prototype` for set-theory operations. Stage 4 / ES2025 / Baseline since June 2024 / **shipped natively at every version that meets our baseline**.

> **For the (mostly historical) polyfill discussion, see [`../runtime-polyfills/set-methods.md`](../runtime-polyfills/set-methods.md).** This file covers the language-status angle — TC39 stage history, ECMA-262 placement, engine ship matrix.

## What

The TC39 [proposal-set-methods](https://github.com/tc39/proposal-set-methods) added seven methods to `Set.prototype`:

| Method | Returns |
|---|---|
| `Set.prototype.intersection(other)` | new `Set` of elements in both |
| `Set.prototype.union(other)` | new `Set` of elements in either |
| `Set.prototype.difference(other)` | new `Set` of elements in `this` not in `other` |
| `Set.prototype.symmetricDifference(other)` | new `Set` of elements in exactly one |
| `Set.prototype.isSubsetOf(other)` | boolean |
| `Set.prototype.isSupersetOf(other)` | boolean |
| `Set.prototype.isDisjointFrom(other)` | boolean |

Each method takes a **Set-like** argument, not strictly a `Set`. The spec defines a set-like protocol: anything with a `size` property, a `.has(value)` method, and a `.keys()` method that returns an iterator. `Set` and `Map` satisfy this; plain arrays do not (they lack `.keys()` returning the element iterator with `.has`-equivalent semantics — consult MDN for the exact algorithm). This means you can intersect a `Set` against a `Map`, a custom set-like wrapper, or anything implementing the protocol.

## TC39 stage history

The proposal had a long stay in committee — initially Stage 1 in 2018, championed by Michał Wadas, later by Sathya Gunasekaran and Kevin Gibbons. Highlights:

| Stage | When | Note |
|---|---|---|
| Stage 1 | 2018 | Original author Michał Wadas |
| Stage 2 | ~2020 | |
| Stage 3 | 2022 | Implementations begin |
| Stage 4 | **April 8, 2024** plenary | https://github.com/tc39/proposals/commit/bda5a6bccbaca183e193f9e680889ea5b5462ce4 |

Set methods were among the headline items of the April 2024 plenary, alongside RegExp `v` flag follow-on work.

## ECMAScript edition

**ECMAScript 2025.** Spec text at https://tc39.es/proposal-set-methods/; merged into ECMA-262 §24 (Keyed Collections) for the 2025 edition. After Stage 4, the proposal repo is no longer the source of truth — ECMA-262 is.

## Engine ship matrix

| Engine | Version | Date | Source |
|---|---|---|---|
| Safari / WebKit | **17.0** | September 18, 2023 | First to ship; https://webkit.org/blog/14445/webkit-features-in-safari-17-0/ |
| Chrome / Edge / Chromium | **122** | February 20, 2024 | V8 12.2 |
| Firefox | **127** | June 11, 2024 | https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/127 |

Note the order: Safari shipped **first**, almost five months ahead of Chrome and ~9 months ahead of Firefox — an unusually inverted timeline for an ES feature.

## Baseline status

**Baseline Newly available: June 11, 2024**, the day Firefox 127 shipped. Per https://web.dev/blog/set-methods. Baseline Widely available expected late 2026 / early 2027.

## At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+)

| Engine | Floor | Native ships at | Verdict |
|---|---|---|---|
| Chrome | 125 | **122** (Feb 2024) | predates baseline by 3 versions |
| Safari | 17.4 | **17.0** (Sept 2023) | predates baseline by 0.4 versions |
| Firefox | 129 | **127** (Jun 2024) | predates baseline by 2 versions |

**All three engines ship Set methods natively at every version that meets our baseline.** There is no polyfill window. Shipping a Set-methods polyfill at this baseline is shipping bytes that cannot help any user the baseline is configured for.

> **Stop polyfilling Set methods at this baseline.**

If you see `core-js/modules/es.set.intersection.js` in your bundle and your `browserslist` reflects modern targets, your build config is misconfigured — see [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md) and [`../anti-patterns/preset-env-no-browserslist.md`](../anti-patterns/preset-env-no-browserslist.md).

## Common idioms (native)

```js
const a = new Set([1, 2, 3, 4]);
const b = new Set([3, 4, 5, 6]);

a.intersection(b);          // Set { 3, 4 }
a.union(b);                 // Set { 1, 2, 3, 4, 5, 6 }
a.difference(b);            // Set { 1, 2 }
a.symmetricDifference(b);   // Set { 1, 2, 5, 6 }
a.isSubsetOf(b);            // false
a.isDisjointFrom(b);        // false

// Set-like argument: works with Map (Map iterates entries through .keys())
const allowed = new Map([[1, 'a'], [2, 'b'], [3, 'c']]);
new Set([1, 4]).intersection(allowed); // Set { 1 }
```

## Related ES2024 / ES2025 additions

A few neighboring additions worth noting at the same baseline — none need polyfilling either:

- **`Object.groupBy` / `Map.groupBy`** — Baseline Newly available March 2024. Group an iterable by a key function. Replaces the lodash `_.groupBy` import for most use cases.
- **`Promise.withResolvers`** — Baseline Newly available April 2024. Returns `{ promise, resolve, reject }` in one expression; eliminates the deferred-pattern boilerplate.
- **`structuredClone`** — Long shipped (Baseline since 2022). Use for deep-cloning structured data instead of `JSON.parse(JSON.stringify(x))`.
- **`Array.prototype.findLast` / `findLastIndex`** — Baseline since 2023.

All four are native at our baseline. None need polyfills.

## Pitfalls

- **It's `symmetricDifference`, not `symDifference` or `xor`.** Long name; engines do not accept variants.
- **Argument type is set-like, not iterable.** A plain `Array` is iterable but does not satisfy the spec's set-like protocol; passing one may throw. Convert with `new Set(arr)` if needed.
- **Order is preserved from `this`.** `intersection`, `union`, etc. preserve insertion order from the receiver `Set`. This is spec-defined and consistent across engines at our baseline.
- **Identity is `SameValueZero`.** Same as `Set` itself — `NaN` matches `NaN`, but `+0` and `-0` are equal.

## Cross-references

- Polyfill (mostly archived) discussion: [`../runtime-polyfills/set-methods.md`](../runtime-polyfills/set-methods.md)
- Why over-polyfilling at modern baselines is bundle bloat: [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md)
- Companion ES2025 features: [`./iterator-helpers.md`](./iterator-helpers.md), [`./regexp-v-flag.md`](./regexp-v-flag.md)
