---
date: 2026-04-27
coverage: extended
peers:
  - ../js-language-status/set-methods.md
  - ../meta/the-modern-baseline.md
  - ../anti-patterns/defensive-overpolyfilling.md
primary_sources:
  - https://github.com/tc39/proposal-set-methods — TC39 proposal (Stage 4, April 2024 plenary)
  - https://web.dev/blog/set-methods — Baseline Newly available announcement (June 11, 2024)
  - https://caniuse.com/mdn-javascript_builtins_set_intersection — Browser support
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set/intersection — MDN reference
  - https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/127 — Firefox 127 (June 11, 2024) release notes
  - https://www.macrumors.com/2023/09/26/apple-releases-safari-17/ — Safari 17 (September 18, 2023) release coverage
  - https://github.com/zloirock/core-js — `core-js` for sub-baseline targets
  - https://github.com/es-shims — Per-method `set.prototype.*` shims listed in the TC39 proposal
---

# Set methods — STOP polyfilling

The punchline of this file is the title. Every Set method shipped before our baseline. Polyfilling them today is bundle bloat.

## What Set methods are

The TC39 [proposal-set-methods](https://github.com/tc39/proposal-set-methods) added seven instance methods to `Set.prototype`:

| Method | Returns |
|---|---|
| `Set.prototype.intersection(other)` | new Set of elements in both |
| `Set.prototype.union(other)` | new Set of elements in either |
| `Set.prototype.difference(other)` | new Set of elements in `this` not in `other` |
| `Set.prototype.symmetricDifference(other)` | new Set of elements in exactly one |
| `Set.prototype.isSubsetOf(other)` | boolean |
| `Set.prototype.isSupersetOf(other)` | boolean |
| `Set.prototype.isDisjointFrom(other)` | boolean |

The proposal reached **Stage 4 in April 2024** at TC39 plenary; included in **ES2025**.

## Native shipping status (as of April 2026)

| Engine | Version | Date |
|---|---|---|
| **Safari** | **17.0** | **September 18, 2023** — first to ship |
| **Chrome / Edge** | **122** | **February 20, 2024** |
| **Firefox** | **127** | **June 11, 2024** — same day as Baseline Newly available designation |

**Baseline Newly available: June 11, 2024.** See https://web.dev/blog/set-methods.

## The decisive verdict

Our baseline: **Chromium 125+ (May 2024) / Safari 17.4+ (March 2024) / Firefox 129+ (August 2024)**.

| Engine | Native ships | Baseline floor | Verdict |
|---|---|---|---|
| Chrome | **122** (Feb 2024) | 125 | Native predates baseline by 3 versions |
| Safari | **17.0** (Sept 2023) | 17.4 | Native predates baseline by 0.4 versions |
| Firefox | **127** (June 2024) | 129 | Native predates baseline by 2 versions |

**Every engine ships Set methods natively at every version that meets our baseline.** There is no polyfill window. Shipping a Set-methods polyfill at this baseline is shipping bytes that cannot help any user the baseline is configured for.

> **Stop polyfilling Set methods at this baseline.** This is the value of this file.

## When is the polyfill still relevant?

Only if your project's actual support matrix is **below the modern baseline**. Concrete examples:

- **You support Safari 16.x.** Safari 16 lacks all Set methods; if you depend on them and you support Safari 16 in production, you need a shim.
- **You support Firefox ESR 115 or 128.** ESR 115 (released July 2023) does not have Set methods. Firefox ESR 128 (released July 2024) does have them — Set methods backported into ESR 128 because ESR 128 is based on Firefox 128. Verify your ESR target.
- **You support Chrome 120 or 121.** Set methods shipped in Chrome 122; older Chrome lacks them.

If any of those apply, your support matrix is below this skill's baseline and the modern-first stance does not yet apply to you. Use one of:

### Option 1 — `core-js` modular import

```js
// Selective: just the Set methods, not the whole core-js bundle
import 'core-js/actual/set';
```

`core-js/actual/set` includes Stage 3+ ESnext Set features (the methods) on top of the stable Set baseline. See https://github.com/zloirock/core-js.

For finer granularity:

```js
import 'core-js/actual/set/intersection';
import 'core-js/actual/set/union';
import 'core-js/actual/set/difference';
// etc.
```

This is the right move when you need Set methods on a sub-baseline target. It is the **wrong move** when your floor is the modern baseline — `useBuiltIns: 'usage'` in `@babel/preset-env` will not insert these imports if your `browserslist` correctly reflects modern targets, because the targets already have them. (If you see `core-js/modules/es.set.intersection.js` in your bundle and your browserslist is modern, your build config is wrong; see `../anti-patterns/preset-env-no-browserslist.md`.)

### Option 2 — Per-method `es-shims` packages

The TC39 proposal explicitly lists the es-shims packages:

- `set.prototype.intersection`
- `set.prototype.union`
- `set.prototype.difference`
- `set.prototype.symmetricdifference`
- `set.prototype.isdisjointfrom`
- `set.prototype.issubsetof`
- `set.prototype.issupersetof`

```js
import shimIntersection from 'set.prototype.intersection/shim';
shimIntersection(); // installs only if missing
```

These packages are MIT-licensed, maintained by Jordan Harband, and follow a stable API across the es-shims family. Use them if you want method-by-method granularity without core-js's larger surface.

## Code example — native usage only

If your project meets the modern baseline, all you need is:

```js
const a = new Set([1, 2, 3, 4]);
const b = new Set([3, 4, 5, 6]);

a.intersection(b);          // Set { 3, 4 }
a.union(b);                 // Set { 1, 2, 3, 4, 5, 6 }
a.difference(b);            // Set { 1, 2 }
a.symmetricDifference(b);   // Set { 1, 2, 5, 6 }
a.isSubsetOf(b);            // false
a.isSupersetOf(b);          // false
a.isDisjointFrom(b);        // false
```

No imports. No detection. No fallback. Native is shipped at every supported browser.

## What about `core-js/stable` or `core-js/full`?

If your build is using `useBuiltIns: 'entry'` and importing `core-js/stable` at the application entry, you are pulling in the entire stable shim bundle including Set methods, including `Promise.allSettled`, including `Object.fromEntries`, all of which are native at our baseline. This is a **bundle-size anti-pattern** independent of Set methods specifically. See `../anti-patterns/corejs-entry-modern.md`.

The fix: switch to `useBuiltIns: 'usage'` with a correctly configured `browserslist`. With a modern browserslist, `@babel/preset-env` will skip injecting Set-method polyfills entirely.

## Pitfalls and gotchas

- **The methods accept any iterable, not just `Set`.** `setA.intersection([1, 2, 3])` is valid; the argument is converted via `Set` semantics. Useful for "is this value in this allowlist?" patterns without constructing a Set first.
- **Ordering.** `intersection`, `union`, etc. preserve insertion order from the receiver `Set`. Spec-defined; cross-engine consistent at our baseline.
- **`Set.prototype.symmetricDifference` is the long name.** Don't typo it; engines do not accept `symDifference` or `xor`.
- **Dilemma with iterables vs. SetLike objects.** The spec uses an internal "SetLike" protocol — argument must be either a `Set`, a `Map` (which iterates entries), or have `size`, `has`, and `keys` methods. A plain `Array` is iterable but not SetLike; engines that strictly follow the spec will accept `[1, 2, 3]` because it is iterable, and the algorithm walks the iteration. Cross-check edge cases against MDN if you depend on subtle behavior.

## TL;DR

If you are reading this file because your build tool just told you "Set.prototype.intersection is not a function" — your **build target is too low**, not your runtime. Raise the floor or stop using the methods. If you are reading this file to decide whether to add a polyfill at the modern baseline — **don't**. The data does not support adding one.

## Cross-references

- TC39 stage / language status: `../js-language-status/set-methods.md`
- Why modern baselines should not ship `core-js/stable`: `../anti-patterns/corejs-entry-modern.md`
- Defensive over-polyfilling pattern: `../anti-patterns/defensive-overpolyfilling.md`
- Modern baseline definition: `../meta/the-modern-baseline.md`
