---
date: 2026-04-27
coverage: advisory
peers:
  - ../meta/the-modern-baseline.md
  - ../js-language-status/shadowrealm.md
  - ../js-language-status/pipeline-operator.md
  - ../anti-patterns/preset-env-no-browserslist.md
primary_sources:
  - https://github.com/tc39/proposal-record-tuple — TC39 Records and Tuples proposal (archived April 15, 2025; status WITHDRAWN)
  - https://github.com/tc39/proposal-record-tuple/issues/394 — "Proposal is withdrawn" — withdrawal notice
  - https://github.com/tc39/proposal-record-tuple/issues/393 — Final February 2025 presentation update
  - https://blogs.igalia.com/compilers/2025/05/20/summary-of-the-april-2025-tc39-plenary/ — April 2025 plenary summary (consensus to withdraw)
  - https://news.ycombinator.com/item?id=43699939 — Hacker News withdrawal discussion
  - https://lobste.rs/s/gt4wye/record_tuple_ecmascript_proposal_has — Lobsters discussion
  - https://github.com/tc39/proposal-composites — Composites successor proposal (Stage 1)
  - https://www.npmjs.com/package/@bloomberg/record-tuple-polyfill — `@bloomberg/record-tuple-polyfill` (now historical)
  - https://github.com/bloomberg/record-tuple-polyfill — Polyfill repo (inactive ~12 months pre-withdrawal)
  - https://waspdev.com/articles/2025-04-25/why-was-records-and-tuples-proposal-withdrawn — Withdrawal post-mortem
---

# Records & Tuples — WITHDRAWN, do not use, do not cite as "upcoming"

This file is the cautionary-tale advisory. The Records & Tuples proposal — long expected to add immutable, deeply-equal `#{}` and `#[]` value types to JavaScript — was **withdrawn from the TC39 process on April 14, 2025**. The repository was archived April 15, 2025. Any tutorial, documentation page, or codebase that references R&T as "future ECMAScript" is **out of date**.

**Position**: Records & Tuples never shipped natively. Don't use them. Don't cite the proposal. The polyfill is now a historical artifact. Use `Object.freeze` / `structuredClone` for shallow immutability and existing libraries (Immutable.js, Mori) for persistent data structures.

## What Records & Tuples were

The [proposal-record-tuple](https://github.com/tc39/proposal-record-tuple) proposed two new **deeply immutable primitive value types**:

```js
// Record literal — like a frozen object, but a new primitive
const point = #{ x: 1, y: 2 };

// Tuple literal — like a frozen array, but a new primitive
const list = #[1, 2, 3, 4];

// Deep structural equality via ===
#{ x: 1 } === #{ x: 1 };       // true
#[1, 2, 3] === #[1, 2, 3];     // true
```

Records and Tuples could only contain **primitives or other Records and Tuples**. No regular objects, no functions, no symbols. This containment rule enforced deep immutability by design.

The promise was substantial:

- Native deep-equality (`===` checks structural equality, not reference)
- Lock-free immutable updates ("change one property" returns a new value)
- Map/Set keys with structural identity ("the point `(1, 2)`" is one key, not many)
- A first-class shape for state-management libraries that today reach for Immutable.js

Champions: Robin Ricard, Rick Button, Daniel Ehrenberg (later joined by Nicolò Ribaudo).

## Stage history — long Stage 2, never advanced

The proposal reached **Stage 2 in 2020** under the original ECMAScript champions. It stayed at Stage 2 for **five years**, longest of any active proposal. Reasons:

- Engine implementers (V8, SpiderMonkey, JSC) raised performance concerns about modifying `===`.
- The deep-equality algorithm has worst-case linear cost per comparison; without **interning** (assigning each unique R&T value a stable identity), every `===` between R&T values does an O(n) walk.
- Interning has its own costs: memory pressure, GC complexity, hash collisions. Engine implementers were not convinced the optimization was achievable.
- The proposal also broke a long-standing JavaScript invariant: that `===`, `Object.is`, and `SameValueZero` agree on equality outcomes for all primitives. R&T would have introduced a new equality relation (or required redefining the old ones), which raised additional concerns.

## The April 2025 withdrawal

At the **TC39 plenary on April 14, 2025**, consensus was achieved to **withdraw the Records and Tuples proposal**. The proposal repository was **archived on April 15, 2025**. See:

- The withdrawal notice: [tc39/proposal-record-tuple#394](https://github.com/tc39/proposal-record-tuple/issues/394) — "At yesterday's TC39 plenary (14th April 2025) consensus was achieved to withdraw the Records and Tuples proposal."
- The April 2025 plenary summary: [Igalia compilers blog](https://blogs.igalia.com/compilers/2025/05/20/summary-of-the-april-2025-tc39-plenary/)
- Withdrawal post-mortem: [waspdev — why was R&T withdrawn](https://waspdev.com/articles/2025-04-25/why-was-records-and-tuples-proposal-withdrawn)

The withdrawal was **mutually agreed**, not a unilateral termination. Champions and implementers concluded the proposal could not advance with the existing primitive-based design.

## Why it was withdrawn — three reasons

Per the public post-mortem and plenary discussion:

1. **Engine performance cost.** Adding new primitives requires modifying every type-check fast path in V8/SpiderMonkey/JSC. Every `===`, `typeof`, `Object.is`, prototype lookup, and hash table operation needs branches for the new primitives. Engine implementers consistently raised this as the blocking concern from 2021 through 2025.
2. **Deep equality semantics inconsistency.** The proposal would break the invariant that `===`, `SameValue`, and `SameValueZero` agree for all primitives. Maintaining the invariant required complex spec text; breaking it would have introduced a fifth equality relation, weakening the semantic clarity that already differentiates `==`, `===`, `Object.is`, and `SameValueZero`.
3. **Containment restriction was painful.** Records could only contain primitives + other Records/Tuples. Real-world usage often needs to embed objects (DOM nodes, class instances, functions) inside structural data. The restriction made R&T awkward for the use cases that motivated it (state stores, immutable stores, key tuples).

## Successor — Composites (Stage 1)

A narrower, object-based successor proposal — [tc39/proposal-composites](https://github.com/tc39/proposal-composites) — was presented in early 2025 and reached **Stage 1 in February 2025** (verify against [tc39/proposals](https://github.com/tc39/proposals)). Champion: **Ashley Claymore** (Bloomberg).

Composites differs from R&T in three important ways:

| | Records & Tuples (withdrawn) | Composites (Stage 1) |
|---|---|---|
| **Type** | New primitive types | Frozen objects (no new primitives) |
| **Equality via `===`** | Yes — deep structural | No — reference equality, like normal objects |
| **Map/Set integration** | Native via `===` | Special-cased: `Map`/`Set` recognize composites and use structural keying for them |
| **Containment** | Primitives + R&T only | Anything (objects, functions, symbols allowed) |
| **Literal syntax** | `#{}` and `#[]` | `Composite({ x: 1 })` constructor function |
| **Spec impact** | Substantial (new primitives, new equality relation) | Minimal (existing object semantics + Map/Set special case) |

Composites trades the elegance of native syntax + identity-via-`===` for **implementability**. Engine implementers indicated tentative support because the spec footprint is far smaller — most of the work happens in `Map` and `Set` internals, not in core value semantics.

**Status as of April 2026: Stage 1.** Stage 1 means "the committee believes this problem is worth solving" — it does not commit to syntax, semantics, or shipping. Treat Composites as exploratory; do not adopt or pre-design around it.

## At our baseline — the polyfill is now historical

The [`@bloomberg/record-tuple-polyfill`](https://www.npmjs.com/package/@bloomberg/record-tuple-polyfill) (also forked by Nicolò Ribaudo) was the canonical R&T polyfill during the Stage 2 years. As of April 2026:

- The polyfill repo at [bloomberg/record-tuple-polyfill](https://github.com/bloomberg/record-tuple-polyfill) **has not received an npm release in over 12 months**.
- The polyfill itself was **always experimental** — its README explicitly says "experimental and explicitly not production ready."
- Every browser engine at our baseline (Chromium 125+, Safari 17.4+, Firefox 129+) parses `#{}` and `#[]` as **syntax errors** — there is no engine support to fall through to, and there will not be.
- The polyfill remains downloadable (~60K weekly downloads at withdrawal time) but is now downloaded mostly by build-system caches, not actively used.

**Do not adopt this polyfill at our baseline.** Even if you can get it to run, you are betting on a syntax that will not exist in any future ECMAScript. Migrating off the polyfill later requires touching every `#{}` and `#[]` literal in your codebase.

## How to spot R&T-era code in the wild

Code, docs, or tutorials that smell like pre-withdrawal R&T thinking:

- **Hash-prefixed literals**: any file containing `#{}` or `#[]` outside class-private-member context. (Class private members `#field` look similar but are unrelated.)
- **`@bloomberg/record-tuple-polyfill` in `package.json`**: the polyfill is downloadable but no longer needed. Remove the dep; rewrite call sites to plain objects + `Object.freeze` or `structuredClone`.
- **Babel config with `@babel/plugin-proposal-record-and-tuple`**: same — remove. Modern Babel will warn if it's still active.
- **TypeScript with `--enable-feature=records-and-tuples`**: never officially supported by TS; if any third-party TS plugin enabled it, the codebase is on a fork.
- **Documentation that says "deeply equal records":** if it cites the proposal-record-tuple repo, the doc is stale by April 2025.

If you inherit code that uses R&T-shape literals, the migration is mechanical. `#{ x: 1 }` becomes `Object.freeze({ x: 1 })`; `#[1, 2, 3]` becomes `Object.freeze([1, 2, 3])`. The `===` semantics change — you must replace identity checks with explicit deep-equality calls (e.g., `dequal` from npm, or `Object.is` chains for shallow cases).

## What to use instead

For each R&T use case there is a working answer at this baseline:

| Use case | Replacement |
|---|---|
| **Shallow immutability** (prevent direct mutation) | `Object.freeze(obj)` — native, ES5, every engine |
| **Deep cloning** (defensive copy) | `structuredClone(value)` — native at our baseline (see [meta/the-modern-baseline](../meta/the-modern-baseline.md)) |
| **Structural sharing / persistent data** | [Immutable.js](https://immutable-js.com/) — battle-tested; or [Mori](https://github.com/swannodette/mori); or build with `Map` / `Set` plus immutability discipline |
| **Map keys with structural identity** | Stringify with stable order (`JSON.stringify` + key sort), or use a `Map` of `Map`s for tuple keys, or wait for Composites if it ships |
| **State management** (Redux-style) | [Immer](https://immerjs.github.io/immer/) — produces frozen objects via mutation-as-API |
| **Tuple types in TypeScript** | `as const` arrays; `readonly [number, number]` tuple types — pure TypeScript, erased at runtime |

## The cautionary lesson — don't pre-adopt Stage 2 proposals

Records & Tuples is the canonical example of a Stage 2 proposal that didn't make it. Lessons for design tools, documentation authors, and codebase maintainers:

1. **Stage 2 is not a commitment to ship.** Stage 2 means "the committee thinks the problem is worth solving and the proposed shape is plausible." Many Stage 2 proposals stall or get withdrawn.
2. **The TC39 process can fail-stop a proposal at any stage below 4.** Even Stage 3 proposals occasionally regress (see ShadowRealm, which moved to Stage 2.7 from a higher status).
3. **Polyfills for unshipped proposals are technical debt with a half-life.** Every line of code targeting a Stage 2 syntax becomes liability when the proposal moves, withdraws, or changes shape.
4. **Tutorials and docs that cite "upcoming ECMAScript features" age fast.** If you see R&T cited as "coming soon" in a 2024-or-earlier blog post, treat the rest of the post as suspect.

The skill flags this explicitly: **when documentation, tutorials, or library docs cite Records & Tuples as "future ECMAScript," they are out of date.** Update or replace.

## Cross-references

- ShadowRealm — another long-Stage-not-yet-Stage-3 proposal: `./shadowrealm.md`
- Pipeline operator — long-Stage-2 proposal also stalled: `./pipeline-operator.md`
- Modern baseline (which excludes anything not shipping in engines): `../meta/the-modern-baseline.md`
- Anti-pattern: shipping proposal-stage syntax to consumers: `../anti-patterns/preset-env-no-browserslist.md`
