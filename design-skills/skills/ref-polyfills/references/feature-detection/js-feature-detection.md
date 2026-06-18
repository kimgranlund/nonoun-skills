---
date: 2026-04-27
coverage: canonical
peers:
  - ../feature-detection/at-supports-recipes.md
  - ../feature-detection/progressive-enhancement.md
  - ../feature-detection/ponyfill-pattern.md
  - ../meta/decision-tree.md
  - ../meta/the-modern-baseline.md
  - ../runtime-polyfills/temporal-api.md
  - ../runtime-polyfills/urlpattern.md
  - ../runtime-polyfills/iterator-helpers.md
  - ../js-language-status/iterator-helpers.md
primary_sources:
  - https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Testing/Feature_detection — MDN feature detection
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/in — `in` operator reference
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/typeof — `typeof` reference
  - https://web.dev/articles/baseline-and-polyfills — modern baseline + dynamic-import pattern
  - https://github.com/es-shims — es-shims project for ECMAScript built-ins
---

# JS feature detection

For runtime APIs, `@supports` doesn't apply — you check the JS environment. The right test depends on whether the feature is a global, a method on a prototype, or behavior that needs probing. At our baseline, most "feature detection" is one line.

## The three idioms

| Idiom | When | Cost |
|---|---|---|
| `'feature' in object` | Property lookup on an object you already have | Cheapest; canonical |
| `typeof identifier !== 'undefined'` | Top-level (global) identifier that may not exist | Slightly heavier; safe in unscoped contexts |
| Behavioral test (try/catch around an actual call) | The presence test passes but the implementation is broken or partial | Most expensive; reserve for known-buggy surfaces |

### `'feature' in object` — the default

The fastest and most idiomatic test for property presence. Works regardless of whether the property is enumerable, on the prototype chain, or `undefined`-valued.

```js
if ('IntersectionObserver' in window) {
  const io = new IntersectionObserver(entries => { ... });
}

if ('Temporal' in globalThis) {
  // Native Temporal — Firefox 139+, Chrome 144+
} else {
  // Polyfill (see ../runtime-polyfills/temporal-api.md)
}

if ('groupBy' in Object) {
  // Object.groupBy — Baseline March 2024 (universal at our floor)
}

if ('intersection' in Set.prototype) {
  // Set methods — Baseline June 2024 (universal at our floor)
}
```

`in` walks the prototype chain — `'at' in Array.prototype` is true on every browser at our baseline.

### `typeof identifier !== 'undefined'` — for unscoped globals

When the identifier might not exist as a binding at all, `'feature' in window` works in browsers, but breaks in workers (no `window`) or strict ES module scopes. `typeof` is the universal-scope alternative:

```js
if (typeof URLPattern !== 'undefined') {
  const pattern = new URLPattern({ pathname: '/users/:id' });
}

if (typeof structuredClone === 'function') {
  // Native — universal at baseline
}
```

Use `globalThis` instead when you can — it's cleaner and reads identically across browsers, workers, and Node:

```js
if ('URLPattern' in globalThis) { ... }
if ('Temporal' in globalThis) { ... }
```

`globalThis` is universal at our baseline (Chrome 71+, Firefox 65+, Safari 12.1+).

### Behavioral tests — for known-buggy implementations

Sometimes the presence test passes and the implementation is wrong. The canonical case: `RegExp.prototype.flags` accessor existed in older Edge but returned the wrong value for sticky flags. The right test is to call it and check the return.

```js
function hasWorkingFlags() {
  try {
    return /a/iu.flags === 'iu';
  } catch {
    return false;
  }
}
```

At our baseline, behavioral tests are mostly historical — Edge Chromium replaced the legacy engine in 2020, and the bug surface is small. Reserve behavioral tests for documented engine bugs (see `../css-color-bugs/`, `../popover-quirks/`, `../anchor-positioning-quirks/` for CSS / DOM equivalents).

A current-baseline behavioral test:

```js
// Detect whether AbortSignal.timeout's abort propagates through fetch correctly.
// iOS Safari 17.4 had a bug where the request hung instead of aborting.
async function abortSignalTimeoutWorks() {
  try {
    const ctrl = AbortSignal.timeout(1);
    await new Promise(r => setTimeout(r, 5));
    return ctrl.aborted;
  } catch {
    return false;
  }
}
```

But more often: ship the workaround for everyone, don't gate.

## Web API examples at our baseline

```js
// Universal at baseline — no detection needed in most code
if ('IntersectionObserver' in window) { ... }
if ('ResizeObserver' in window) { ... }
if ('MutationObserver' in window) { ... }
if ('AbortController' in window) { ... }
if ('structuredClone' in window) { ... }
if ('CompressionStream' in window) { ... }

// Real polyfill candidates at baseline
if ('URLPattern' in globalThis) {
  // Native — Safari 26+, Firefox 142+
} else {
  // Polyfill candidate for Firefox 129–141
}

if ('Temporal' in globalThis) {
  // Native — Firefox 139+, Chrome 144+, Safari pending
} else {
  // Polyfill required (see ../runtime-polyfills/temporal-api.md)
}

if ('CookieStore' in window) {
  // Native — Safari 26.2+, Firefox 138+, Chrome 87+
} else {
  // Fall back to document.cookie — no good polyfill below this
}

// Recently shipped — verify against your floor
if ('scheduler' in window && 'yield' in scheduler) {
  await scheduler.yield(); // Chrome 129+, Safari pending, Firefox pending
}
```

## Language feature examples

```js
// Object.groupBy / Map.groupBy — Baseline March 2024 (universal at our floor)
// NOTE: Array.prototype.groupBy was the original proposal but never shipped —
// the final spec moved the methods to Object and Map static functions.
if ('groupBy' in Object) {
  Object.groupBy(items, item => item.kind);
}

// Set methods — Baseline June 2024 (universal at our floor)
if ('intersection' in Set.prototype) {
  setA.intersection(setB);
}

// Iterator helpers — Safari 18.4+, Firefox 131+, Chrome 122+
// Polyfill candidate for Safari 17.4–18.3 (see ../runtime-polyfills/iterator-helpers.md)
if (typeof Iterator !== 'undefined' && typeof Iterator.from === 'function') {
  Iterator.from(iter).map(fn).take(10).toArray();
}

// Promise.try — Firefox 134+, Chrome 128+, Safari 18.2+
if ('try' in Promise) {
  Promise.try(() => maybeThrow());
}

// Promise.withResolvers — Baseline February 2024
if ('withResolvers' in Promise) {
  const { promise, resolve, reject } = Promise.withResolvers();
}

// RegExp.escape — ES2025; Chrome 136+, Firefox 134+, Safari 18.4+
if ('escape' in RegExp) {
  RegExp.escape(userInput);
}

// Float16Array — ES2025; Chrome 134+, Firefox 134+, Safari 26+
if ('Float16Array' in globalThis) {
  new Float16Array([0.5, 1.5]);
}
```

A common trap: testing `Array.prototype.groupBy` instead of `Object.groupBy`. The original proposal put `groupBy` on `Array.prototype`; the final spec moved it. **`Array.prototype.groupBy === undefined`** is true on every modern engine — the method never shipped under that name.

## Conditional polyfill loading via dynamic import

The canonical pattern for loading a polyfill only when the native API is missing:

```js
async function ensureTemporal() {
  if (!('Temporal' in globalThis)) {
    await import('@js-temporal/polyfill');
  }
  return globalThis.Temporal;
}

// Call once during app boot
const Temporal = await ensureTemporal();
```

The polyfill is loaded as a separate chunk; modern engines pay zero bytes for it. Bundlers (Vite, esbuild, webpack 5+, Rollup, SWC) split the dynamic `import()` into its own chunk automatically.

For polyfills that auto-install on the prototype:

```js
if (!('intersection' in Set.prototype)) {
  await import('es-shims/Set.prototype.intersection/auto');
}
// Now Set.prototype.intersection is guaranteed
```

The `/auto` entry point convention is documented in `ponyfill-pattern.md`.

For first-paint-blocking code, eager-load the polyfill inline instead — the round-trip cost is too high if the feature is needed before the page renders.

## Tree-shaking implications

Feature detection patterns affect what bundlers can eliminate:

```js
// Tree-shakes well — the import is conditional, dynamic, and side-effect-free
if (!('URLPattern' in globalThis)) {
  await import('urlpattern-polyfill');
}

// Tree-shakes poorly — the side-effect import is unconditional
import 'urlpattern-polyfill';

// Tree-shakes well — pure-function import
import { groupBy } from './group-by-ponyfill.js';
groupBy(items, x => x.kind);
```

Bundlers can statically analyze static imports. Dynamic `import()` produces a separate chunk; conditional dynamic imports give the cleanest tree-shaking when the feature is absent.

For libraries you ship to others, prefer ponyfills over polyfills — see `ponyfill-pattern.md`.

## Behavioral test for accessor-shaped features

Some specs add new accessors (getters/setters) on existing prototypes. A presence test won't tell you whether the accessor *works* — only that the descriptor exists. For accessor verification:

```js
// Verify the accessor returns the expected shape
function regExpFlagsWorks() {
  try {
    const flags = /a/giu.flags;
    return typeof flags === 'string' && flags.split('').sort().join('') === 'giu';
  } catch {
    return false;
  }
}
```

At our baseline, accessor bugs are rare. The behavioral pattern matters for older floors and for surfaces under active development (e.g. `ElementInternals` validation API behavior in Safari 17.x).

## When NOT to feature-detect

- **Universal-at-baseline features.** Don't gate `IntersectionObserver`, `Promise.allSettled`, `Object.fromEntries`, etc. behind detection — every browser at our floor has them. The detection itself becomes dead code that bundlers may not eliminate.
- **Things `@supports` can answer for CSS.** Use `@supports`, not `CSS.supports()` from JS, for cascade-time decisions.
- **Behavioral tests on every call.** Detect once at boot, cache the result.

## Anti-patterns

```js
// DON'T — UA sniffing
if (navigator.userAgent.includes('Safari')) { ... }

// DON'T — version-string parsing
const safariVersion = parseFloat(navigator.userAgent.match(/Version\/(\d+\.\d+)/)?.[1] ?? '0');
if (safariVersion < 18) { ... }

// DON'T — feature-detect-then-ignore
if (!('Temporal' in globalThis)) {
  console.warn('Temporal missing');
}
// ... uses Temporal anyway, throws ReferenceError

// DO — actually branch on the detection result, or load the polyfill
if (!('Temporal' in globalThis)) {
  await import('@js-temporal/polyfill');
}
const now = Temporal.Now.zonedDateTimeISO();
```

UA sniffing lies — Brave reports as Chrome, Edge reports as Chrome, Vivaldi reports as Chrome, headless tests report as anything. Feature detection answers the only question that matters: *is the feature present and working in this runtime, right now?*

## Cross-references

- `at-supports-recipes.md` — the CSS counterpart.
- `ponyfill-pattern.md` — for the ponyfill / `/auto` import conventions referenced above.
- `progressive-enhancement.md` — when to skip the polyfill and just degrade gracefully.
- `../meta/decision-tree.md` — Step 6 of the do-I-need-a-polyfill flow.
- `../runtime-polyfills/temporal-api.md`, `../runtime-polyfills/urlpattern.md`, `../runtime-polyfills/iterator-helpers.md` — concrete polyfill loaders that use these detection patterns.
