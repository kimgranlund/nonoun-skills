---
date: 2026-04-27
coverage: canonical
peers:
  - ../runtime-polyfills/iterator-helpers.md
  - ../js-language-status/set-methods.md
  - ../js-language-status/temporal.md
primary_sources:
  - https://github.com/tc39/proposal-iterator-helpers — TC39 proposal repo (Stage 4, archived October 8, 2024)
  - https://tc39.es/ecma262/2025/ — ECMAScript 2025 Language Specification
  - https://v8.dev/features/iterator-helpers — V8 announcement (Chrome 122, V8 12.2)
  - https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/131 — Firefox 131 release notes (October 1, 2024)
  - https://webkit.org/blog/16574/webkit-features-in-safari-18-4/ — WebKit Features in Safari 18.4
  - https://web.dev/blog/baseline-iterator-helpers — Baseline Newly available designation (March 31, 2025)
  - https://caniuse.com/mdn-javascript_builtins_iterator — caniuse browser support
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Iterator — MDN Iterator reference
  - https://blogs.igalia.com/compilers/2024/11/13/summary-of-the-october-2024-tc39-plenary/ — Igalia plenary summary noting archival
---

# Iterator helpers — language status

Lazy chainable methods on `Iterator.prototype` plus `Iterator.from(iterable)`. Eleven instance methods, one static. Stage 4 / ES2025 / now native everywhere.

> **For the polyfill recommendation, see [`../runtime-polyfills/iterator-helpers.md`](../runtime-polyfills/iterator-helpers.md).** This file covers the language-status angle — TC39 stage history, ECMA-262 placement, engine ship matrix.

## What

The TC39 [proposal-iterator-helpers](https://github.com/tc39/proposal-iterator-helpers) finalizes a set of array-like methods directly on `Iterator.prototype`, plus the static `Iterator.from(iterable)` constructor.

The full surface:

| Kind | Methods |
|---|---|
| Static | `Iterator.from(iterable)` |
| Lazy chainable (return iterators) | `.map(fn)`, `.filter(fn)`, `.take(n)`, `.drop(n)`, `.flatMap(fn)` |
| Eager terminal | `.reduce(reducer, init?)`, `.toArray()`, `.forEach(fn)`, `.some(fn)`, `.every(fn)`, `.find(fn)` |

The chainable methods are **lazy**: `iter.map(f).filter(g).take(10).toArray()` pulls one value at a time and never allocates intermediate arrays. This is the central correctness and memory win, and it is the reason iterator helpers are not redundant with `Array.prototype` methods. Iterators are also **single-consumption** — once you have called a terminal helper, the iterator is exhausted.

## TC39 stage history

The proposal's stage trail (from the proposal repo + tracking issues):

| Stage | When | Note |
|---|---|---|
| Stage 1 | 2018 | Initial acceptance into TC39 process, original champion Gus Caplan |
| Stage 2 | 2019 | |
| Stage 3 | November 2022 | See https://github.com/tc39/proposal-iterator-helpers/issues/117 (stage 3 tracking) |
| Stage 4 | **December 5, 2023** plenary | Per the proposals tracker; included in ES2025 |
| Repo archived | **October 8, 2024** | https://blogs.igalia.com/compilers/2024/11/13/summary-of-the-october-2024-tc39-plenary/ — repo archived; spec source is now ECMA-262 |

The proposal champions over the lifetime: Gus Caplan, Michael Ficarra, Adam Vandolder, Jonas Haukenes, HE Shi-Jun.

## ECMAScript edition

Iterator helpers are part of **ECMAScript 2025**. The normative spec lives in ECMA-262 §27 (Iteration); see https://tc39.es/ecma262/2025/. Once the proposal repo is archived, **ECMA-262 itself is the source of truth** for behavior and edge cases — not the proposal README.

## Engine ship matrix

| Engine | Version | Date | Source |
|---|---|---|---|
| Chrome / Edge / Chromium | **122** | February 20, 2024 | V8 12.2; https://v8.dev/features/iterator-helpers |
| Firefox | **131** | October 1, 2024 | Synchronous helpers; https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/131 |
| Safari / WebKit | **18.4** | March 31, 2025 | Last to ship; https://webkit.org/blog/16574/webkit-features-in-safari-18-4/ |

Async iterator helpers (`AsyncIterator.prototype.*`) are a **separate proposal** at Stage 3 as of April 2026. Don't conflate the two when reading caniuse / MDN.

## Baseline status

**Baseline Newly available: March 31, 2025**, the day Safari 18.4 shipped. Per https://web.dev/blog/baseline-iterator-helpers, this is when iterator helpers cleared all three engines and entered the Baseline tracking system.

Baseline Widely available is reached 30 months after the last engine ship — **expected ~September 2027**.

## At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+)

| Engine | Floor | Native? | Polyfill window |
|---|---|---|---|
| Chrome 125+ | yes | **Yes** (since 122) | none |
| Firefox 129–130 | yes | No | 2 versions, ~2 months (Aug–Sept 2024) |
| Firefox 131+ | yes | **Yes** | none |
| Safari 17.4–18.3 | yes | No | ~6 minor versions, ~1 year (Mar 2024 → Mar 2025) |
| Safari 18.4+ | yes | **Yes** | none |

**Verdict at this baseline.** Iterator helpers are a **narrow polyfill candidate**: Chrome ships above the floor, the Firefox window is two minor versions most teams have already moved past, and Safari is the long pole at ~1 year. If your support matrix's Safari minimum is ≥ 18.4, you can use the API natively with no polyfill at all.

For the polyfill — see [`../runtime-polyfills/iterator-helpers.md`](../runtime-polyfills/iterator-helpers.md) (`es-iterator-helpers` from the es-shims project).

## Common idioms (native)

```js
// Lazy chain over an infinite generator — Array.prototype cannot do this
function* primes() {
  for (let n = 2; ; n++) if (isPrime(n)) yield n;
}
const firstTen = primes().map(p => p * p).take(10).toArray();

// Wrap any iterable into a real Iterator
const evens = Iterator.from(numbers).filter(n => n % 2 === 0).take(10).toArray();

// Eager terminal — short-circuits on first match
const found = Iterator.from(records).find(r => r.id === target);

// Reduce without an intermediate array
const total = Iterator.from(transactions).reduce((sum, t) => sum + t.cents, 0);
```

## Pitfalls

- **`Iterator` is now a real global.** Code that defined `class Iterator` or `const Iterator = ...` at module scope will collide. Audit before adopting.
- **Generators are auto-instances of `Iterator`.** A generator's return value already has `.map()`, `.take()`, etc. natively in supporting engines. The polyfill ensures this for Safari 17.4–18.3.
- **Once consumed, gone.** `.toArray()` exhausts the iterator. Calling `.map()` again on the same iterator after consumption returns nothing.
- **Async helpers are not these helpers.** [`proposal-async-iterator-helpers`](https://github.com/tc39/proposal-async-iterator-helpers) is its own Stage 3 proposal in flight; if you want `.map()` on an async iterator, that is a different shipping story.

## Cross-references

- Polyfill recommendation: [`../runtime-polyfills/iterator-helpers.md`](../runtime-polyfills/iterator-helpers.md)
- Companion ES2025 features: [`./set-methods.md`](./set-methods.md), [`./regexp-v-flag.md`](./regexp-v-flag.md)
- Modern baseline definition: [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)
