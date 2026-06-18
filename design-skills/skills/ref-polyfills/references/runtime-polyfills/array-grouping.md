---
date: 2026-04-27
coverage: extended
peers:
  - ../js-language-status/set-methods.md
  - ../runtime-polyfills/iterator-helpers.md
  - ../runtime-polyfills/set-methods.md
  - ../meta/the-modern-baseline.md
  - ../anti-patterns/corejs-entry-modern.md
primary_sources:
  - https://github.com/tc39/proposal-array-grouping — TC39 proposal repo (Stage 4, ES2024)
  - https://tc39.es/proposal-array-grouping/ — Spec text
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/groupBy — MDN reference
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map/groupBy — MDN reference
  - https://caniuse.com/mdn-javascript_builtins_object_groupby — Browser support
  - https://caniuse.com/mdn-javascript_builtins_map_groupby — Browser support
  - https://web.dev/blog/web-platform-03-2024 — web.dev "March 2024" recap noting Baseline newly available
  - https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/119 — Firefox 119 release notes (Oct 24, 2023)
  - https://bugzilla.mozilla.org/show_bug.cgi?id=1792650 — Firefox shipping bug for Object.groupBy / Map.groupBy
  - https://github.com/tc39/proposal-array-grouping/issues/44 — WebCompat regressions with `group` (the rename rationale)
  - https://github.com/es-shims/Object.groupBy — `object.groupby` ponyfill (es-shims)
  - https://github.com/es-shims/Map.groupBy — `map.groupby` ponyfill (es-shims)
  - https://www.npmjs.com/package/object.groupby — npm package
  - https://www.npmjs.com/package/groupby-polyfill — Smaller zero-dep alternative
---

# Array grouping — `Object.groupBy` and `Map.groupBy` — STOP polyfilling

The punchline is in the title. Both methods are Baseline Newly available since **March 2024** and ship in every browser at our floor. Polyfilling them at this baseline is bundle bloat.

## What array grouping is

The TC39 [proposal-array-grouping](https://github.com/tc39/proposal-array-grouping) added two **static** methods:

| Method | Returns |
|---|---|
| `Object.groupBy(iterable, keyFn)` | A null-prototype object with one array property per group key |
| `Map.groupBy(iterable, keyFn)` | A `Map` whose keys are the values returned by `keyFn` |

```js
Object.groupBy([1, 2, 3, 4], n => n % 2 === 0 ? 'even' : 'odd');
// → { odd: [1, 3], even: [2, 4] }   (null-prototype object)

Map.groupBy(['apple', 'banana', 'avocado'], s => s[0]);
// → Map { 'a' => ['apple', 'avocado'], 'b' => ['banana'] }
```

Use `Object.groupBy` when keys are strings and you want ergonomic destructuring. Use `Map.groupBy` when keys are arbitrary values (objects, numbers, anything `===`-comparable). The null-prototype on `Object.groupBy`'s result is intentional — it prevents `__proto__` and inherited-property collisions you would hit with a plain `{}` accumulator inside `Array.prototype.reduce`.

## Not `Array.prototype.groupBy` — the rename history

The original proposal was `Array.prototype.groupBy` / `Array.prototype.groupByToMap`. Both names hit web-compatibility walls:

1. **`Array.prototype.groupBy`** collided with [Sugar.js](https://sugarjs.com/) v1.4.0 and earlier, which monkey-patched `Array.prototype` with an incompatible `groupBy`. Telemetry caught ~660 origins still loading vulnerable Sugar versions; shipping a native, differently-shaped `groupBy` would break those pages.
2. **`Array.prototype.group`** (the next attempt) collided with code that used arrays as ad-hoc hashmaps — `arr.group` was already meaningful in some real-world libraries, again breaking the web.

TC39 ([discussion](https://github.com/tc39/proposal-array-grouping/issues/44), see also [WebKit commit 317e700](https://github.com/WebKit/WebKit/commit/317e70035de4f830152ae3fc5ed483f10c837f5d) reverting the earlier rename) ultimately moved the methods off `Array.prototype` and onto `Object` and `Map` as **static** methods. This is the version that shipped. So when reading older articles, blog posts, or Stack Overflow answers about `[1,2,3].group(...)` or `[1,2,3].groupBy(...)`, treat them as historical — that API never landed.

## TC39 stage and ECMAScript edition

- **Stage 4: November 2023 plenary.** Champions: Justin Ridgewell, Jordan Harband (et al.).
- **ECMAScript 2024.** Merged into ECMA-262 as part of the ES2024 candidate (released June 2024). Spec text: https://tc39.es/proposal-array-grouping/.

## Native shipping status (as of April 2026)

| Engine | Version | Date | Source |
|---|---|---|---|
| **Chrome / Edge** | **117** | **September 12, 2023** | V8 11.7 — first to ship |
| **Firefox** | **119** | **October 24, 2023** | https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/119; tracking bug [Bugzilla 1792650](https://bugzilla.mozilla.org/show_bug.cgi?id=1792650) |
| **Safari** | **17.4** | **March 5, 2024** | The decisive engine — flips the methods to Baseline Newly available |

**Baseline Newly available: March 2024**, the day Safari 17.4 shipped. See https://web.dev/blog/web-platform-03-2024 for the web.dev rollup.

## At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+)

| Engine | Floor | Native ships at | Verdict |
|---|---|---|---|
| Chrome | 125 | **117** (Sept 2023) | predates baseline by 8 versions |
| Safari | 17.4 | **17.4** (March 2024) | matches baseline exactly |
| Firefox | 129 | **119** (Oct 2023) | predates baseline by 10 versions |

**Every engine ships array grouping natively at every version that meets our baseline.** There is no polyfill window. Shipping an `Object.groupBy` polyfill at this baseline is shipping bytes that cannot help any user the baseline is configured for.

> **Stop polyfilling array grouping at this baseline.** This is the value of this file.

The Safari case is the tightest — Safari 17.4 is both our floor and the first Safari with the methods. If you ever lower your Safari floor below 17.4, you re-enter the polyfill window. At the modern baseline, you do not.

## When is the polyfill still relevant?

Only if your project's actual support matrix is **below the modern baseline**. Concrete examples:

- **You support Safari 17.0 – 17.3.** Those versions don't have the methods.
- **You support Firefox ESR 115.** ESR 115 (released July 2023) predates Firefox 119 and does not have them. Firefox ESR 128+ does.
- **You support Chrome 116 or older.** The methods shipped in Chrome 117.

If any of those apply, your support matrix is below this skill's baseline and the modern-first stance does not yet apply.

### Option 1 — `core-js` modular import

```js
// Selective: only the array-grouping methods
import 'core-js/actual/object/group-by';
import 'core-js/actual/map/group-by';
```

`useBuiltIns: 'usage'` in `@babel/preset-env` will inject these only if your `browserslist` actually targets a browser that needs them. If you see `core-js/modules/esnext.object.group-by.js` in your bundle and your browserslist is modern, your build config is wrong — see [`../anti-patterns/preset-env-no-browserslist.md`](../anti-patterns/preset-env-no-browserslist.md).

### Option 2 — Per-method `es-shims` packages

The es-shims project publishes spec-compliant per-method ponyfills:

- [`object.groupby`](https://www.npmjs.com/package/object.groupby) — https://github.com/es-shims/Object.groupBy
- [`map.groupby`](https://github.com/es-shims/Map.groupBy)

```js
import groupBy from 'object.groupby';
const groups = groupBy([1, 2, 3, 4], n => n % 2 === 0 ? 'even' : 'odd');
```

Both packages are MIT-licensed, maintained by Jordan Harband, and follow the standard es-shims API (a callable function plus `.shim()` / `.getPolyfill()` helpers). 500+ npm projects depend on `object.groupby`; it's the canonical sub-baseline shim.

### Option 3 — `groupby-polyfill` (zero-dep, smaller)

[`groupby-polyfill`](https://www.npmjs.com/package/groupby-polyfill) is a small zero-dependency polyfill covering both methods. Use it if you want the lightest possible install with no es-shims meta-package overhead. (Single-maintainer dependency note: smaller install but smaller maintenance surface — audit before relying.)

### Option 4 — Inline (the laziest path)

If you only need `Object.groupBy` once, the polyfill fits in a few lines:

```js
const groupBy = Object.groupBy ?? ((iterable, fn) => {
  const result = Object.create(null);
  let i = 0;
  for (const item of iterable) {
    const key = fn(item, i++);
    (result[key] ??= []).push(item);
  }
  return result;
});
```

This satisfies the spec for the common case (string keys, null-prototype result). Use the es-shims package if you need exact spec compliance for edge cases (numeric keys coerced to strings, `Symbol` keys throwing, etc.).

## Code example — native usage only

If your project meets the modern baseline, all you need is:

```js
const data = [
  { id: 1, status: 'active' },
  { id: 2, status: 'archived' },
  { id: 3, status: 'active' },
  { id: 4, status: 'archived' },
];

// String-keyed grouping → Object.groupBy
const byStatus = Object.groupBy(data, item => item.status);
// { active: [{id:1,…}, {id:3,…}], archived: [{id:2,…}, {id:4,…}] }

// Object-keyed grouping → Map.groupBy
const today = new Date('2026-04-27');
const yesterday = new Date('2026-04-26');
const events = [
  { date: today, name: 'A' },
  { date: yesterday, name: 'B' },
  { date: today, name: 'C' },
];
const byDate = Map.groupBy(events, e => e.date);
// Map { Date(today) => [{name:'A'}, {name:'C'}], Date(yesterday) => [{name:'B'}] }
```

No imports. No detection. No fallback. Native is shipped at every browser the baseline is configured for.

## Replacing the lodash habit

If your codebase reaches for `_.groupBy` from lodash, this is your migration target:

```js
// Before
import groupBy from 'lodash.groupby';
const result = groupBy(data, 'status');

// After
const result = Object.groupBy(data, item => item.status);
```

The lodash `'status'`-as-string-shorthand becomes an explicit `item => item.status` arrow. The win: ~7 KB of lodash gone, plus a native, optimizable code path. For most apps, dropping `lodash.groupby` is the single largest payoff of array grouping shipping.

## Pitfalls and gotchas

- **The result of `Object.groupBy` has a null prototype.** That means `result.toString` is `undefined`, `result.hasOwnProperty` is `undefined`, and `JSON.stringify(result)` works as you'd expect (no inherited properties leak). If you need a normal-prototype result, spread it: `{...Object.groupBy(...)}`.
- **Keys are coerced to strings (for `Object.groupBy`).** A key function returning `42` and one returning `'42'` produce the same group. If you need true value-equality keys (objects, dates), use `Map.groupBy`.
- **`null` and `undefined` keys.** `Object.groupBy` coerces these to `'null'` and `'undefined'` strings. `Map.groupBy` keeps them as the original values.
- **Iteration order.** Group order matches first-occurrence order from the input iterable. Spec-defined; consistent across engines at our baseline.
- **Static, not prototype.** Don't write `[1,2,3].groupBy(...)` — it doesn't exist. The methods are static on `Object` and `Map`. This trips up people coming from old proposal docs or library docs.
- **The methods take any iterable.** `Object.groupBy(new Set([1,2,3]), …)` works. `Object.groupBy(map.values(), …)` works. The argument doesn't need to be an array.

## TL;DR

If you are reading this file because your build tool just told you "Object.groupBy is not a function" — your **build target is too low**, not your runtime. Raise the floor or use the es-shims ponyfill scoped to a sub-baseline branch. If you are reading this to decide whether to add a polyfill at the modern baseline — **don't**. The data does not support adding one.

## Cross-references

- Companion ES2024/ES2025 features that are also already-Baseline: [`../runtime-polyfills/set-methods.md`](../runtime-polyfills/set-methods.md), [`../runtime-polyfills/iterator-helpers.md`](../runtime-polyfills/iterator-helpers.md)
- TC39 stage discussion of similar Stage 4 finishers: [`../js-language-status/set-methods.md`](../js-language-status/set-methods.md)
- Why over-polyfilling at modern baselines is bundle bloat: [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md)
- Modern baseline definition: [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)
