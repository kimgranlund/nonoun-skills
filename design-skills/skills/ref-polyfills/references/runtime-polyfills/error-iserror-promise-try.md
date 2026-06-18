---
date: 2026-04-27
coverage: extended
peers:
  - ../js-language-status/iterator-helpers.md
  - ../js-language-status/set-methods.md
  - ../runtime-polyfills/iterator-helpers.md
  - ../runtime-polyfills/array-grouping.md
  - ../meta/the-modern-baseline.md
  - ../feature-detection/ponyfill-pattern.md
primary_sources:
  - https://github.com/tc39/proposal-is-error — `Error.isError` proposal (Stage 4, May 2025)
  - https://github.com/tc39/proposal-promise-try — `Promise.try` proposal (Stage 4, October 2024)
  - https://github.com/tc39/proposal-promise-with-resolvers — `Promise.withResolvers` proposal (Stage 4, ES2024)
  - https://github.com/tc39/proposal-regex-escaping — `RegExp.escape` proposal (Stage 4, February 2025)
  - https://github.com/tc39/proposal-float16array — `Float16Array` proposal (Stage 4, February 2025)
  - https://blogs.igalia.com/compilers/2025/03/27/summary-of-the-february-2025-tc39-plenary/ — Igalia plenary summary covering RegExp.escape and Float16Array Stage 4
  - https://blogs.igalia.com/compilers/2025/07/03/summary-of-the-may-2025-tc39-plenary/ — Igalia plenary summary covering Error.isError Stage 4
  - https://socket.dev/blog/tc39-advances-9-proposals — May 2025 plenary coverage
  - https://socket.dev/blog/tc39-advances-3-proposals-to-stage-4-regexp-escaping-float16array-and-redeclarable-global-eval — February 2025 plenary coverage
  - https://web.dev/blog/web-platform-01-2025 — January 2025 web.dev recap (Promise.try Baseline newly available)
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/isError — MDN Error.isError
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/try — MDN Promise.try
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/withResolvers — MDN Promise.withResolvers
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp/escape — MDN RegExp.escape
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Float16Array — MDN Float16Array
  - https://caniuse.com/mdn-javascript_builtins_promise_withresolvers — Promise.withResolvers support
  - https://caniuse.com/mdn-javascript_builtins_promise_try — Promise.try support
  - https://caniuse.com/mdn-javascript_builtins_regexp_escape — RegExp.escape support
  - https://caniuse.com/mdn-javascript_builtins_float16array — Float16Array support
  - https://github.com/es-shims/Error.isError — `error.iserror` ponyfill
  - https://github.com/es-shims/Promise.try — `promise.try` ponyfill
  - https://github.com/es-shims/Promise.withResolvers — `promise.withresolvers` ponyfill
  - https://github.com/es-shims/RegExp.escape — `regexp.escape` ponyfill
  - https://github.com/sindresorhus/escape-string-regexp — Sindre Sorhus's pre-spec alternative
  - https://github.com/petamoriken/float16 — `@petamoriken/float16` ponyfill
---

# Small ES2025 finishers — `Error.isError`, `Promise.try`, `Promise.withResolvers`, `RegExp.escape`, `Float16Array`

A bundle of late-Stage-4 additions, each tiny in scope and tractable to polyfill — most via inline shims. This file consolidates them because none warrants its own runtime-polyfill page; the polyfill story for each fits in a paragraph.

> The recurring pattern: **most are inline-shimmable in <10 lines, OR universally native at our baseline**. The es-shims project has spec-compliant per-method ponyfills if you need them; explicit imports keep bundle minimal.

## Cheat table

| Feature | Stage 4 | First ship | At our baseline | Shim |
|---|---|---|---|---|
| `Promise.withResolvers` | ES2024 | Chrome 119 / Firefox 121 / Safari 17.4 | ✅ universal — **stop polyfilling** | n/a |
| `Promise.try` | Oct 2024 | Chrome 128 / Safari 18.2 / Firefox 134 | ⚠️ Firefox 129–133 polyfill window | 4-line inline |
| `Error.isError` | May 2025 | shipping 2026; verify per engine | ⚠️ verify; polyfill window real | 1-line inline |
| `RegExp.escape` | Feb 2025 | Safari 18.2 / Firefox 134 / Chrome 136 | ⚠️ partial polyfill window | `escape-string-regexp` or es-shims |
| `Float16Array` | Feb 2025 | Safari 16.4 (limited) / Firefox 133 / Chrome 135 | ⚠️ verify per platform; complex polyfill | `@petamoriken/float16` |

The rest of this file goes per-feature with shipping detail, the inline shim where applicable, and verdicts.

## `Promise.withResolvers` — universally native, **stop polyfilling**

Returns `{ promise, resolve, reject }` in one expression. Eliminates the "deferred" pattern boilerplate.

```js
const { promise, resolve, reject } = Promise.withResolvers();
someEventEmitter.once('done', resolve);
someEventEmitter.once('error', reject);
return promise;
```

### TC39 / ES edition
**Stage 4: November 2023 plenary.** Part of **ECMAScript 2024**.

### Native shipping

| Engine | Version | Date |
|---|---|---|
| Chrome / Edge | **119** | October 31, 2023 |
| Firefox | **121** | December 19, 2023 |
| Safari | **17.4** | March 5, 2024 |
| Node.js | **22.0** | April 24, 2024 (also backported to **20.12** LTS, March 26, 2024) |

**Baseline Newly available: April 2024.** Per https://caniuse.com/mdn-javascript_builtins_promise_withresolvers.

### Verdict at our baseline

| Engine | Floor | Native ships at | Verdict |
|---|---|---|---|
| Chrome | 125 | 119 | predates baseline |
| Safari | 17.4 | 17.4 | matches baseline exactly |
| Firefox | 129 | 121 | predates baseline |

**Universal at our baseline. Stop polyfilling.** If you see imports of `promise.withresolvers` from the es-shims package and your browserslist is modern, it's dead weight.

If you still need it for sub-baseline support, the trivial inline shim:

```js
const withResolvers = Promise.withResolvers ?? function () {
  let resolve, reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
};
```

The es-shims package [`promise.withresolvers`](https://github.com/es-shims/Promise.withResolvers) covers the rare engine corner cases.

## `Promise.try` — Firefox 129–133 polyfill window

Wraps a callback (sync or async, may throw or return) into a Promise. Removes the `new Promise(resolve => resolve(fn()))` boilerplate that everyone has written wrong at least once.

```js
// All of these end up as a Promise that resolves or rejects "correctly"
Promise.try(() => 42);                              // → Promise<42>
Promise.try(() => Promise.resolve(42));             // → Promise<42>
Promise.try(() => { throw new Error('x') });        // → rejected Promise
Promise.try(async () => 42);                        // → Promise<42>

// With trailing args (avoid closures, mirror Promise.resolve overloads)
Promise.try(fetch, '/api/data');
```

### TC39 / ES edition
**Stage 4: October 2024 plenary** — see the [Path to Stage 4 issue](https://github.com/tc39/proposal-promise-try/issues/15). Champions: Jordan Harband. Part of ECMAScript 2025.

### Native shipping

| Engine | Version | Date |
|---|---|---|
| Chrome / Edge | **128** | August 20, 2024 |
| Safari | **18.2** | December 11, 2024 |
| Firefox | **134** | January 7, 2025 |

**Baseline Newly available: January 2025**, per https://web.dev/blog/web-platform-01-2025.

### Verdict at our baseline

| Engine | Floor | Native ships at | Verdict |
|---|---|---|---|
| Chrome | 125 | 128 | needs polyfill at exactly Chrome 125–127 (3 versions, ~3 months — likely past your support floor) |
| Safari | 17.4 | 18.2 | needs polyfill at Safari 17.4–18.1 (~9 months of versions) |
| Firefox | 129 | 134 | needs polyfill at Firefox 129–133 (5 versions, ~5 months) |

**Polyfill window is real but narrow** — the Safari window is widest (~9 months of releases). At our floor, this is an extended-tier polyfill candidate, not canonical.

### Inline shim — the only one you need

```js
const promiseTry = Promise.try ?? function (fn, ...args) {
  return new Promise(resolve => resolve(fn(...args)));
};
```

That's it. Three lines. The official es-shims package [`promise.try`](https://github.com/es-shims/Promise.try) is spec-compliant if you want exact edge-case behavior (e.g., when `fn` is not callable, the spec mandates a rejected Promise; the inline shim above will throw synchronously). For most code paths, the inline form is fine.

## `Error.isError` — realm-safe error detection, Stage 4 May 2025

The reliable way to ask "is this thing actually an `Error`?" — not just an object that walked into the `Error.prototype` chain. Branded check on a private slot installed by `Error()` itself.

```js
const err = new TypeError('boom');
Error.isError(err);                                // true
Error.isError({ name: 'Error', message: 'fake' }); // false (no brand)
Error.isError(Object.create(Error.prototype));     // false (no brand)

// Cross-realm: works for errors from another iframe / worker
const otherRealmError = await iframe.contentWindow.eval('new Error("x")');
Error.isError(otherRealmError);                    // true (instanceof would fail)
otherRealmError instanceof Error;                  // false in this realm
```

### TC39 / ES edition
**Stage 4: May 2025 plenary** — see the [stage-4 commit](https://github.com/tc39/proposals/commit/a5d4bb99d79f328533d0c36b0cd20597fa12c7a8) and the [plenary summary](https://blogs.igalia.com/compilers/2025/07/03/summary-of-the-may-2025-tc39-plenary/). Champions: Jordan Harband. Targeted for ECMAScript 2026.

### Native shipping (verify per engine — this is in-flight)

`Error.isError` was just at Stage 4 in May 2025; engine ship dates are late 2025 / 2026 and partial as of this file's date. Per [caniuse.com/mdn-javascript_builtins_error_iserror](https://caniuse.com/mdn-javascript_builtins_error_iserror):

| Engine | Status as of April 2026 |
|---|---|
| Chrome / Edge | shipping ~Chrome 144+ (verify against current caniuse) |
| Firefox | shipping ~Firefox 145+ (verify) |
| Safari | partial — verify against current Safari version |

**Always re-check caniuse before relying on this.** This file is dated 2026-04-27; the situation evolves monthly.

### Verdict at our baseline

Polyfill window is real and probably long — Safari 17.4 / Firefox 129 / Chrome 125 all predate native shipping. Use a polyfill if you need it.

### Inline shim

```js
const errorIsError = Error.isError ?? (e => e instanceof Error);
```

Note: this is **not spec-compliant** — `instanceof Error` returns `false` for cross-realm errors, which is the whole point of `Error.isError`. For the realm-safe spec semantics, use [`error.iserror`](https://www.npmjs.com/package/error.iserror) (the [es-shims package](https://github.com/es-shims/Error.isError)). For most application code, `instanceof Error` is fine — cross-realm errors are an edge case for libraries handling `iframe`/`Worker` boundaries.

```js
// Spec-compliant fallback via es-shims
import isError from 'error.iserror';
isError(err); // realm-safe
```

## `RegExp.escape` — string-to-regex-source escaping, Stage 4 February 2025

Sanitizes a string for safe inclusion as a literal pattern in a `RegExp`.

```js
const userInput = 'a.b+c';
const re = new RegExp(RegExp.escape(userInput));
// → /\a\.b\+c/  (escapes the . and +; escapes safe chars too for spec-required determinism)

re.test('a.b+c');  // true (literal match, not regex match)
re.test('axbXc');  // false
```

### TC39 / ES edition
**Stage 4: February 18, 2025 plenary** — see [Float16Array and RegExp.escape stage-4 commit](https://github.com/tc39/proposals/commit/b81fa9bccf4b51f33de0cbe797976a84d05d4b76) and the [Igalia plenary summary](https://blogs.igalia.com/compilers/2025/03/27/summary-of-the-february-2025-tc39-plenary/). Champions: Jordan Harband, Kevin Gibbons. Part of ECMAScript 2025.

### Native shipping

| Engine | Version | Date |
|---|---|---|
| Safari | **18.2** | December 11, 2024 (shipped pre-Stage-4) |
| Firefox | **134** | January 7, 2025 |
| Chrome / Edge | **136** | April 29, 2025 |

**Baseline Newly available: ~May 2025.** Per https://caniuse.com/mdn-javascript_builtins_regexp_escape.

### Verdict at our baseline

| Engine | Floor | Native ships at | Verdict |
|---|---|---|---|
| Chrome | 125 | 136 | needs polyfill at Chrome 125–135 (11 versions, ~11 months) |
| Safari | 17.4 | 18.2 | needs polyfill at Safari 17.4–18.1 |
| Firefox | 129 | 134 | needs polyfill at Firefox 129–133 |

**Real polyfill window.** Extended-tier candidate. The Chrome window in particular is non-trivial because Chrome shipped last.

### Polyfills

**Spec-compliant:** [`regexp.escape`](https://github.com/es-shims/RegExp.escape) (es-shims, MIT, Jordan Harband). The right answer if you depend on the exact spec output (which escapes more characters than strictly necessary, for cross-engine determinism).

**Pragmatic and smaller:** [`escape-string-regexp`](https://github.com/sindresorhus/escape-string-regexp) by Sindre Sorhus, MIT. Tiny (~150 bytes minified+gzipped). Predates the spec; output is similar but not identical (it escapes the documented "regex special character" set rather than the spec's broader set). For 99% of "I want to interpolate user input into a regex" use cases, it works perfectly. **244M+ npm downloads** — the de-facto pre-spec library.

```js
import escapeStringRegexp from 'escape-string-regexp';
const re = new RegExp(escapeStringRegexp(userInput));
```

### Inline shim — pragmatic version

```js
const escapeRegex = RegExp.escape ?? (s => s.replace(/[\\^$.*+?()[\]{}|]/g, '\\$&'));
```

Same character set as `escape-string-regexp`. Not byte-for-byte spec-compliant (the spec also escapes leading-character-position-sensitive characters), but functionally correct for "safely interpolate user input into a regex literal."

## `Float16Array` — half-precision typed arrays, Stage 4 February 2025

A typed array of IEEE 754 binary16 (half-precision) floats. Pairs with `DataView.prototype.getFloat16` / `setFloat16` and `Math.f16round`. Primarily for WebGPU, ML workloads, and anywhere half-precision is the wire format.

```js
const f16 = new Float16Array(4);
f16[0] = 0.1;
f16[1] = Math.PI;
console.log(f16[0]);  // 0.0999755859375  (rounded to nearest representable f16)
console.log(f16[1]);  // 3.140625

// DataView companions
const buf = new ArrayBuffer(2);
const dv = new DataView(buf);
dv.setFloat16(0, 1.5);
dv.getFloat16(0);  // 1.5

// f16round — round a number to nearest f16 representable value
Math.f16round(0.1);  // 0.0999755859375
```

### TC39 / ES edition
**Stage 4: February 18, 2025 plenary** — see the same [stage-4 commit](https://github.com/tc39/proposals/commit/b81fa9bccf4b51f33de0cbe797976a84d05d4b76) as `RegExp.escape`. Author: Kevin Gibbons. Part of ECMAScript 2025.

### Native shipping

| Engine | Version | Date |
|---|---|---|
| Safari | **16.4** | March 27, 2023 (limited; partial constructor support) |
| Firefox | **133** | December 3, 2024 |
| Chrome / Edge | **135** | April 1, 2025 |

**Verify per platform** — Safari shipped early but partially; the full API (constructor + DataView + Math.f16round) consolidated in 2024–2025. Per https://caniuse.com/mdn-javascript_builtins_float16array.

### Verdict at our baseline

| Engine | Floor | Full native ships at | Verdict |
|---|---|---|---|
| Chrome | 125 | 135 | needs polyfill at Chrome 125–134 |
| Safari | 17.4 | 16.4 (partial) → check 18.x for full | partial below recent versions |
| Firefox | 129 | 133 | needs polyfill at Firefox 129–132 |

**Polyfill window is real and platform-dependent.** This is a niche feature — most apps don't use it. If you do, polyfill carefully.

### Polyfill: `@petamoriken/float16` (the reference)

The de-facto Float16 polyfill, predating the proposal by years.

| Field | Value |
|---|---|
| npm | https://www.npmjs.com/package/@petamoriken/float16 |
| Repository | https://github.com/petamoriken/float16 |
| License | MIT |
| Author | petamoriken |
| Type | Ponyfill (named exports; doesn't mutate globals) |
| Bundle size | ~6 KB minified+gzipped |
| Implementation | `Proxy` + `Reflect` over a `Uint16Array` backing store |

```js
import { Float16Array, getFloat16, setFloat16, hfround as f16round } from '@petamoriken/float16';

const arr = new Float16Array([0.1, 0.2, 0.3]);
```

The `Proxy`-based implementation imposes a meaningful per-element overhead — for tight loops, native is significantly faster. The polyfill is correctness-first, not performance-first. For ML / WebGPU hot paths, **gate behind feature detection** so the native path is taken when available.

### When you genuinely need Float16

Half-precision is meaningful for:

- **WebGPU shader interop** (textures, buffers using `f16` types).
- **TensorFlow.js / ONNX Runtime Web** quantized models.
- **Wire formats** that pack half-precision floats for bandwidth.
- **Storage / persistence** of large arrays where 50% size reduction matters.

If you are not in one of those buckets, you don't need `Float16Array` — `Float32Array` is universal and almost always the right choice.

### Feature detection

```js
let Float16ArrayImpl;
if ('Float16Array' in globalThis) {
  Float16ArrayImpl = globalThis.Float16Array;
} else {
  ({ Float16Array: Float16ArrayImpl } = await import('@petamoriken/float16'));
}
```

The dynamic import keeps the polyfill out of bundles for browsers that ship native.

## Iterator helpers and `Iterator.from`

Cross-reference: [`./iterator-helpers.md`](./iterator-helpers.md). The synchronous iterator-helpers proposal (including `Iterator.from`, `.map`, `.filter`, `.take`, etc.) is also Stage 4 / ES2025; its polyfill story is more elaborate and gets its own file.

## Combined inline-shim block

If you want all of these in your codebase below the baseline, this is the entire block:

```js
// One-liners that handle 90%+ of cases without a library
const errorIsError = Error.isError ?? (e => e instanceof Error);

const promiseTry = Promise.try ?? ((fn, ...args) =>
  new Promise(resolve => resolve(fn(...args))));

const promiseWithResolvers = Promise.withResolvers ?? (() => {
  let resolve, reject;
  const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
  return { promise, resolve, reject };
});

const escapeRegex = RegExp.escape ??
  (s => s.replace(/[\\^$.*+?()[\]{}|]/g, '\\$&'));

// Float16Array does NOT have a useful one-line shim — use @petamoriken/float16
```

If your `browserslist` is modern, none of these `??` fallbacks ever trigger — the native form runs. The bundle cost is approximately zero (a few `??` ternary operators).

## When NOT to polyfill

- **Your floor matches the native ship floors per the per-feature tables above.** Just use native.
- **You don't actually use the feature.** Audit before polyfilling. `Promise.withResolvers` is fashionable; you may not need it.
- **For `Error.isError`** specifically: most app code can just use `instanceof Error`. The realm-safe property only matters when bridging cross-realm boundaries (iframes, workers, vm contexts).
- **For `Float16Array`**: unless you have a specific WebGPU / ML / wire-format need, use `Float32Array`.

## TL;DR

These are small, late-Stage-4 finishers. Most are inline-shimmable in 1–4 lines, none demand a heavyweight runtime polyfill except `Float16Array` (which is niche enough to gate behind feature detection). At the modern baseline:

- **Stop polyfilling `Promise.withResolvers`** — universally native.
- **Inline-shim `Promise.try` / `Error.isError` / `RegExp.escape`** if your floor predates their respective ship versions; the shims are tiny.
- **Polyfill `Float16Array` selectively** with `@petamoriken/float16` and feature-detect dynamic import.

## Cross-references

- [`./iterator-helpers.md`](./iterator-helpers.md), [`./set-methods.md`](./set-methods.md), [`./array-grouping.md`](./array-grouping.md) — neighboring ES2024–2025 features
- [`../js-language-status/iterator-helpers.md`](../js-language-status/iterator-helpers.md), [`../js-language-status/set-methods.md`](../js-language-status/set-methods.md) — language-status angle
- [`../feature-detection/ponyfill-pattern.md`](../feature-detection/ponyfill-pattern.md) — explicit-import idioms
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what the baseline includes natively
