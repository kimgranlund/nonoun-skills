---
date: 2026-04-27
coverage: extended
peers:
  - ../js-language-status/iterator-helpers.md
  - ../meta/the-modern-baseline.md
  - ../feature-detection/ponyfill-pattern.md
primary_sources:
  - https://github.com/tc39/proposal-iterator-helpers — TC39 proposal (Stage 4, archived October 8, 2024)
  - https://www.npmjs.com/package/es-iterator-helpers — `es-iterator-helpers` ponyfill (es-shims)
  - https://github.com/es-shims/iterator-helpers — Source repo
  - https://v8.dev/features/iterator-helpers — V8 announcement (Chrome 122, March 27, 2024)
  - https://web.dev/blog/baseline-iterator-helpers — Baseline Newly available milestone (March 31, 2025)
  - https://socket.dev/blog/safari-18-4-ships-3-new-javascript-features-from-the-tc39-pipeline — Safari 18.4 ship coverage
  - https://caniuse.com/mdn-javascript_builtins_iterator — Browser support
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Iterator — MDN reference
  - https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/131 — Firefox 131 release notes
  - https://developer.apple.com/documentation/safari-release-notes/safari-18_4-release-notes — Safari 18.4 release notes
---

# Iterator helpers

## What iterator helpers are

The TC39 [proposal-iterator-helpers](https://github.com/tc39/proposal-iterator-helpers) finalizes a set of array-like methods directly on the `Iterator` prototype, plus a static `Iterator.from()` constructor. Twelve methods total:

| Method | Behavior |
|---|---|
| `Iterator.from(obj)` | Static — wraps any iterable or iterator-like object into a real `Iterator` |
| `.map(fn)` | Lazy mapping; returns a new iterator |
| `.filter(predicate)` | Lazy filtering |
| `.take(n)` | Lazy first-n |
| `.drop(n)` | Lazy skip-n |
| `.flatMap(fn)` | Lazy flat-map |
| `.reduce(reducer, initialValue?)` | Eager reduction |
| `.toArray()` | Eager collection |
| `.forEach(fn)` | Eager iteration with side effects |
| `.some(fn)`, `.every(fn)`, `.find(fn)` | Eager short-circuiting predicates |

Crucially, the chainable methods (`map`, `filter`, `take`, `drop`, `flatMap`) are **lazy**. No intermediate arrays are allocated; the chain pulls one value at a time. This is the single biggest correctness and memory win — you can `.map().filter().take(10)` over an infinite generator without exploding memory.

```js
function* primes() {
  for (let n = 2; ; n++) {
    if (isPrime(n)) yield n;
  }
}

const firstTenSquaredPrimes = primes()
  .map(p => p * p)
  .take(10)
  .toArray();
```

`Array.prototype` cannot do this — `Array.from(primes())` never returns. Iterator helpers are the answer.

The proposal reached **Stage 4** and shipped as part of **ES2025**. The repository was archived October 8, 2024 — the source of truth is now ECMA-262 itself.

## Native shipping status (as of April 2026)

| Engine | Version | Date | Notes |
|---|---|---|---|
| **Chrome / Edge** | **122** | **February 20, 2024** | V8 v12.2; https://v8.dev/features/iterator-helpers |
| **Firefox** | **131** | **October 1, 2024** | https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/131 — synchronous helpers (forEach, map, etc.) |
| **Safari** | **18.4** | **March 31, 2025** | The last major engine to ship; closed the cross-browser gap. https://webkit.org/blog/16574/webkit-features-in-safari-18-4/ |

**Baseline Newly available: March 31, 2025** (per https://web.dev/blog/baseline-iterator-helpers).

## Verdict against the modern baseline

Our baseline: **Chromium 125+ / Safari 17.4+ / Firefox 129+**.

| Browser | At baseline | Native iterator helpers? | Polyfill needed? |
|---|---|---|---|
| Chrome 125+ | Yes | **Yes** (since 122) | No |
| Edge 125+ | Yes | **Yes** (since 122) | No |
| Firefox 129+ | Yes | **No until Firefox 131** | **Firefox 129–130 needs it** (~2 versions, 2 months — likely not in your support matrix today) |
| Firefox 131+ | Yes | **Yes** | No |
| Safari 17.4–18.3 | Yes | **No** | **Yes** — about 1 year of Safari versions (March 2024 → March 2025) |
| Safari 18.4+ | Yes | **Yes** | No |

**The polyfill window is Safari 17.4 → 18.3 (~1 year of Safari, ~6 minor versions).** Chrome and Firefox are above-baseline almost immediately at our floor. Firefox 129–130 is a tiny window most teams will have already moved past.

This makes iterator helpers an **extended-tier polyfill candidate**, not a canonical one — the window is narrow, the workaround is easy (use `Array.from(iterable).map(...)` and accept the intermediate array), and the polyfill is small if you do reach for it.

## Polyfill: `es-iterator-helpers`

The es-shims project's iterator-helpers ponyfill.

| Field | Value |
|---|---|
| npm | https://www.npmjs.com/package/es-iterator-helpers |
| Repository | https://github.com/es-shims/iterator-helpers |
| Latest version | 1.2.1 |
| License | MIT |
| Author | Jordan Harband and the es-shims contributors |
| Spec compliance | ESnext-compliant; works back to ES3 |

**Bundle size impact.** The full polyfill is small (a few KB gzipped), but the package is structured as **per-method modules** so you only pay for what you import. Importing only `Iterator.prototype.toArray` is ~1 KB. Importing the auto-applying entry point installs the full set on the prototype.

## Code examples

### Native usage (works above baseline)

```js
const result = Iterator.from([1, 2, 3, 4, 5])
  .map(x => x * 2)
  .filter(x => x > 4)
  .take(2)
  .toArray();
// [6, 8]
```

This compiles natively on Chrome 122+, Firefox 131+, Safari 18.4+. No polyfill needed.

### Auto-shim (Safari 17.4–18.3 fallback)

```js
import 'es-iterator-helpers/auto';
// Iterator.prototype methods are now installed if missing
```

The `/auto` entry point installs all helpers on `Iterator.prototype` only if they are not already present. Safe to import unconditionally — Chrome / modern Firefox / Safari 18.4+ no-op the install.

### Per-method ponyfill (no global mutation)

```js
import getIterator from 'es-iterator-helpers/Iterator.from';
import map from 'es-iterator-helpers/Iterator.prototype.map';

const it = getIterator(arr);
const mapped = map.call(it, x => x * 2);
```

Verbose, but ideal for libraries that should never mutate consumers' iterator prototype.

### Feature-detect + dynamic import

```js
if (typeof Iterator === 'undefined' || typeof Iterator.from !== 'function') {
  await import('es-iterator-helpers/auto');
}
const result = Iterator.from(arr).map(x => x * 2).take(5).toArray();
```

Bundlers split the polyfill into a chunk fetched only on Safari 17.4–18.3. Chrome / Firefox 131+ / Safari 18.4+ pay zero bytes.

## When NOT to polyfill

- **Your floor is already Safari 18.4+ / Firefox 131+ / Chrome 122+.** Just use the native API. No imports, no detection.
- **You aren't actually using iterator helpers.** If your code is `arr.map(...).filter(...)`, you are using `Array.prototype` methods, not iterator helpers — those have been native everywhere for a decade. No polyfill needed.
- **The intermediate-array cost is fine for your data.** For a 10-element array, `Array.from(iter).map(x => ...).filter(...)` is functionally equivalent to the iterator-helper chain and avoids the polyfill cost entirely. Iterator helpers' lazy-evaluation win is real only at scale or with infinite generators.

## Migration path off the polyfill

1. Watch the Safari floor. When your minimum is Safari 18.4+, all three engines have native support and the polyfill is unneeded.
2. Remove the import. The auto-shim form has been a no-op since the floor moved up; removing it is risk-free.
3. If you used per-method ponyfill imports (`import map from 'es-iterator-helpers/Iterator.prototype.map'`), refactor to native: `iterator.map(fn)`.

## Pitfalls and gotchas

- **`Iterator` is a new global.** Older code that defined `Iterator` as a custom symbol or class globally will collide with the native one. Audit your codebase for `class Iterator` and `const Iterator = ...`.
- **Generators are auto-instances of `Iterator`.** A generator function's return value already has the helper methods natively (in supporting engines). The polyfill ensures this on Safari 17.4–18.3.
- **Async iterator helpers are a separate proposal.** [`proposal-async-iterator-helpers`](https://github.com/tc39/proposal-async-iterator-helpers) is at Stage 3 (April 2026) — distinct from the synchronous proposal. If you need `.map()` on an async iterator, that is a different polyfill story (currently `iterator-helpers-polyfill` covers both, but check the spec status).
- **The es-shims package is well-maintained.** Jordan Harband's es-shims project has been the canonical source of TC39-spec-compliant polyfills for years; it is stable, but verify the `latest` tag matches the final ES2025 spec wording before relying on edge-case behavior.

## Cross-references

- TC39 stage / language status: `../js-language-status/iterator-helpers.md`
- Modern baseline definition: `../meta/the-modern-baseline.md`
- Ponyfill pattern explainer: `../feature-detection/ponyfill-pattern.md`
