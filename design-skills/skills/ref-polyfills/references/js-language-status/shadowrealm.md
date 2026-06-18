---
date: 2026-04-27
coverage: extended
peers:
  - ../meta/the-modern-baseline.md
  - ../runtime-polyfills/temporal-api.md
primary_sources:
  - https://github.com/tc39/proposal-shadowrealm — TC39 proposal-shadowrealm (Stage 2.7)
  - https://tc39.es/proposal-shadowrealm/ — Spec text
  - https://blogs.igalia.com/compilers/2025/03/27/summary-of-the-february-2025-tc39-plenary/ — February 2025 plenary status update
  - https://github.com/tc39/proposal-shadowrealm/issues/393 — Stage 3 web-API exposure tracking
  - https://github.com/tc39/proposal-shadowrealm/issues/304 — Stage 3 reviewers
  - https://github.com/leobalter/shadowrealms-polyfill — Leo Balter / Rick Waldron polyfill (reference)
  - https://github.com/ambit-tsai/shadowrealm-api — `shadowrealm-api` npm polyfill
  - https://hardenedjs.org/blog/ — Hardened JavaScript / SES context
  - https://github.com/endojs/endo — Endo / SES (the broader hardened-JS ecosystem)
  - https://2ality.com/2022/04/shadow-realms.html — Axel Rauschmayer ShadowRealm explainer
---

# ShadowRealm — Stage 2.7, no native, do not adopt at our baseline

ShadowRealm is the proposal that would give JavaScript a synchronous, in-process sandbox — a fresh global environment with its own intrinsics, separate from the host realm. **It is not in any engine.** It has not been at Stage 3 since being moved back to Stage 2.7 (or never quite reaching Stage 3 in a sense the spec author tracks consistently — see history below). At the modern baseline, do not adopt; use Web Workers or sandboxed iframes for the same use cases.

## What ShadowRealm is

The [proposal-shadowrealm](https://github.com/tc39/proposal-shadowrealm) constructor `new ShadowRealm()` returns a secondary execution context with:

- Its own global object (with its own `Object`, `Array`, `Promise`, `Math`, etc.)
- Its own intrinsic prototypes (so `arr instanceof Array` from the outer realm fails for arrays from inside the realm)
- Two methods on the realm: `evaluate(sourceText)` for synchronous string-eval, and `importValue(specifier, name)` for dynamic ES module import returning a Promise
- **Strict primitive-only data passing**: only primitives (and callable wrapper proxies) cross the boundary. Objects do NOT cross — this is the structural sandbox guarantee.

```js
// The aspirational shape (does not run in any engine today)
const realm = new ShadowRealm();
realm.evaluate('globalThis.x = 42');
const getX = await realm.importValue('./module.js', 'getX');
const x = getX(); // primitive return only
```

ShadowRealm is the spec-track replacement for the older `Realms` proposal, which was withdrawn in favor of this narrower, more security-focused shape.

## TC39 stage history

The stage trajectory is unusual — read carefully:

| Date | Status |
|---|---|
| 2018–2020 | Original `Realms` proposal (broader, withdrawn) |
| **September 2023** | Advanced to **Stage 2** (under the ShadowRealm name) |
| **February 7, 2024** | Advanced to **Stage 2.7** (the new validation stage that was added to the TC39 process in late 2023) |
| June 2024 | Stage 2.7 update presented |
| December 2024 | **Stage 3 Request** presented to TC39; advancement deferred |
| February 2025 | Status update — committee notes "we have resolved all of the open questions on the TC39 side, but what remains is to gauge the interest in implementing the web integration parts." See [Igalia's Feb 2025 plenary summary](https://blogs.igalia.com/compilers/2025/03/27/summary-of-the-february-2025-tc39-plenary/). |
| April 2026 | Still at **Stage 2.7**. No native engine ships it. |

Verify the current stage against [tc39/proposals](https://github.com/tc39/proposals) and the proposal repo before relying on this snapshot — the stage label has been actively contested.

The block to Stage 3 is not the spec text. The committee believes the spec is implementable. The block is **engine-implementer interest**: V8, SpiderMonkey, and JavaScriptCore have not committed to ship. Without that signal, Stage 3 (which formally requires "complete and reviewed spec; designated reviewers approved") and Stage 4 (which requires "two compatible implementations") are unreachable.

Champions: Dave Herman, Caridy Patiño, Mark Miller, Leo Balter, Rick Waldron, Chengzhong Wu (Legendecas).

## Native shipping status (April 2026)

| Engine | Status |
|---|---|
| **V8 (Chrome / Edge / Node)** | Not implemented. No active commitment. |
| **SpiderMonkey (Firefox)** | Not implemented. Mozilla has not signaled. |
| **JavaScriptCore (Safari)** | Some prototyping documented in 2021 by Phillip Mates, but no shipping intent. |

**Zero engines, zero versions.** Same status as decorators.

## At our baseline

**Not adoptable.** ShadowRealm is a runtime feature — there is no transpilation that creates synchronous sandboxed evaluation contexts. The polyfills that exist (`shadowrealm-api`, the leobalter reference impl, the SES/Endo ecosystem) are **not equivalent**:

| Polyfill | Approach | Trade-off |
|---|---|---|
| [`shadowrealm-api`](https://www.npmjs.com/package/shadowrealm-api) | iframe-backed sandbox in browser; vm-backed in Node | Heavyweight; cross-realm calls become async-ish; passes most Test262 cases but breaks under SES-style hardening |
| [SES + Compartment](https://github.com/endojs/endo) (the `ses` npm package) | Same-realm "compartment" with frozen intrinsics via `lockdown()` | Reflects a particular **hardened-JavaScript** stance; mutates global intrinsics for the host realm; not a drop-in replacement; ~150KB |
| [`leobalter/shadowrealms-polyfill`](https://github.com/leobalter/shadowrealms-polyfill) | Reference impl by proposal champions | Demonstration-grade; not production polyfill |

**None of these is what the production ShadowRealm spec promises.** The native semantics rely on engine-level isolation that JavaScript-land polyfills cannot fully recreate. Synchronous module instantiation, proper intrinsic separation, and the security guarantees against shared-global-prototype mutation are all absent or weakened in any polyfill.

## Use cases (theoretical) and the practical alternatives

The ShadowRealm pitch covers four use cases. **At this baseline, all four have working alternatives that are battle-tested.**

| Use case | ShadowRealm pitch | Practical alternative today |
|---|---|---|
| **Plugin systems** (run third-party JS without ambient access) | Synchronous sandbox; primitives in/out | Web Workers + `postMessage` + structured-clone; or `<iframe sandbox>` + `postMessage` |
| **Sandboxed eval** (run user-supplied scripts) | Isolated globals; no DOM access | `<iframe sandbox="allow-scripts">` with `srcdoc`, communicate via `postMessage` |
| **Dependency isolation** (test a library without polluting the global) | Each test in fresh realm | Worker-per-test; or vm modules in Node; or `jsdom` |
| **Hardened JS / supply-chain defense** (freeze intrinsics, audit capabilities) | Compose with SES `lockdown()` inside the realm | SES alone (without ShadowRealm) — already in production at Agoric, MetaMask, others |

The Web Workers + structured-clone path is canonical for everything except "I need synchronous evaluation." If you actually need synchronous-with-isolation (rare in browser code), ShadowRealm is theoretically the right shape — but until it ships, that need is best handled by **inlining the code in a try/catch and accepting the lack of isolation**, or by re-architecting to be async.

## Position

**Do not adopt ShadowRealm at this baseline.** The cost (heavyweight polyfill, security caveats, weird semantics under polyfilling) is high. The benefit is theoretical — there is no native engine to fall through to.

Reconsider when:

- The proposal re-promotes to Stage 3 with at least one engine commitment to implement.
- Chromium ships an experimental flag-gated implementation (the leading indicator).
- The Web Integration spec — the part that exposes Web APIs (fetch, console, structured clone) inside the realm — reaches consensus. The current blocker per the Feb 2025 plenary is the web-platform side, not TC39.

For the use cases ShadowRealm targets, **Web Workers + structured-clone messaging** or **sandboxed iframes with postMessage** are the production answer at this baseline. Both ship in every browser at our floor and have been mature for over a decade.

## What about Hardened JavaScript / SES?

Worth disambiguating from ShadowRealm: the [SES](https://hardenedjs.org/) ("Secure ECMAScript") and [Endo](https://github.com/endojs/endo) ecosystems exist independently of ShadowRealm. SES uses `lockdown()` to freeze the host realm's intrinsics (Object.prototype, Array.prototype, etc.) and `Compartment` objects for code isolation within that hardened realm. **SES does not require ShadowRealm.**

If your motivation is supply-chain defense or capability-based security:

- **SES today** with `lockdown()` + `Compartment` is shipped at scale (Agoric blockchain, MetaMask wallet, others).
- The trade-off: `lockdown()` is global and irreversible — once you call it, the host realm's intrinsics are frozen forever.
- Bundle cost is ~150KB minified.
- This is a **stance**, not a polyfill — adopting SES is committing to write code in the hardened-JS subset (no `Date.now()` access without explicit grant, no ambient I/O, etc.).

ShadowRealm would compose with SES (you'd run `lockdown()` inside each ShadowRealm), but SES is independently usable today. The skill does not endorse SES as a default — it's a niche, opinionated tool — but it is the only path to capability-based JS security at this baseline.

## Common confusions

- **ShadowRealm is not a Worker.** Workers have their own thread + own globals + async-only message passing. ShadowRealm is same-thread + own globals + synchronous string/module evaluation. The use cases overlap; the implementation profiles do not.
- **ShadowRealm is not `vm` from Node.** Node's `vm` module has been around since early Node and provides similar same-thread sandboxing. It is **not** a polyfill for ShadowRealm — it has a different API surface and is not portable to browsers.
- **ShadowRealm is not an `<iframe>`.** Iframes have own globals + own document tree + cross-document message passing. ShadowRealm has no DOM. The two are not interchangeable for use cases that need DOM access (e.g., visualizing third-party components).
- **ShadowRealm does not require SES.** They are independent. ShadowRealm gives you a fresh global environment; SES gives you a hardened global environment. You can have either, both, or neither.

## Cross-references

- Modern baseline (why "no native" is load-bearing): `../meta/the-modern-baseline.md`
- Hardened-JS / SES context (the broader ecosystem ShadowRealm sits in): https://hardenedjs.org/blog/
- No transpilation peer — ShadowRealm requires runtime support that build tools cannot provide
