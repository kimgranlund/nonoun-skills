---
date: 2026-04-27
coverage: advisory
peers:
  - ../landscape-shifts/polyfill-io-attack.md
  - ../transpilation/babel-preset-env.md
  - ../anti-patterns/corejs-entry-modern.md
primary_sources:
  - https://github.com/zloirock/core-js — core-js repository (README, sponsorship section)
  - https://github.com/zloirock/core-js/releases — release notes (latest 3.49.0, March 16, 2026)
  - https://www.npmjs.com/package/core-js — npm registry page
  - https://opencollective.com/core-js — OpenCollective funding page
  - https://www.thestack.technology/core-js-maintainer-denis-pusharev-license-broke-angry/ — The Stack, Feb 14, 2023
  - https://www.theregister.com/2023/02/15/corejs_russia_open_source/ — The Register, Feb 15, 2023
  - https://www.versio.io/en/product-release-end-of-life-eol-denis-pushkarev-core-js.html — release lifecycle reference
---

# core-js — single-maintainer crisis (advisory)

> **Coverage tier: advisory.** This file describes a situation that may shift faster than baseline-and-bug references. Pushkarev's funding state, his legal status, and core-js's maintenance posture have all moved several times since 2023. Treat the framing as durable, the specifics as needing re-verification.

## What core-js is

[core-js](https://github.com/zloirock/core-js) is **the most-deployed JavaScript polyfill on Earth.** It's the runtime that Babel's `@babel/preset-env` reaches for when you write `useBuiltIns: 'usage'` or `'entry'`. It's a transitive dependency of nearly every JavaScript build pipeline shipped this decade. It receives **billions of downloads per year** on npm and appears on **over half of the top 10,000 websites** ([The Register, 2023-02-15](https://www.theregister.com/2023/02/15/corejs_russia_open_source/)).

It is maintained, almost single-handedly, by **Denis Pushkarev** (GitHub: [zloirock](https://github.com/zloirock)), since the project was published as open source in 2014. He has been the primary author of every release.

License: **MIT** (verified on the GitHub repository).

Latest version at the date of this file: **core-js 3.49.0**, published **March 16, 2026** ([releases page](https://github.com/zloirock/core-js/releases)).

## Why this matters for the expert-polyfills skill

Three reasons core-js gets its own file:

1. **If you're using `@babel/preset-env` with `useBuiltIns`, you're shipping core-js.** Most production JavaScript bundles in 2024–2026 contain a slice of it, often without the developer realizing.
2. **The bus-factor is one.** A single human, in a single jurisdiction, with a single set of credentials, ships and signs every release. Compared to the typical maintainer-collective behind a similarly-deployed library, this is an outlier.
3. **Pushkarev has stated, on the record, that the situation is unsustainable.** This is not speculation; he authored an [11,000-word public statement in February 2023](https://github.com/zloirock/core-js/blob/master/docs/2023-02-14-so-whats-next.md) describing the funding crisis. The skill takes him at his word and treats core-js as a supply-chain risk worth managing, not a freebie.

## The funding crisis (timeline)

### 2014 — Project starts

Pushkarev publishes core-js as open source. License: MIT. Initial funding mechanism: none.

### 2017–2020 — Slow donation growth

Pushkarev adds funding mechanisms (Patreon, OpenCollective). Total raised: small. Per The Register reporting (2023-02-15), monthly donations fluctuated; at peak when working full time, ~$2,500/month; declined to ~$400/month by 2023.

### 2020 — Personal incident

Pushkarev was involved in a fatal motorcycle accident in 2020 and **served approximately 10 months in prison** in Russia, after which he was released early ([The Stack, 2023-02-14](https://www.thestack.technology/core-js-maintainer-denis-pusharev-license-broke-angry/); [The Register, 2023-02-15](https://www.theregister.com/2023/02/15/corejs_russia_open_source/)). The conviction created ongoing legal complications, including outstanding civil lawsuits that have at times prevented him from leaving Russia.

> **Verification status: this section is reported by multiple secondary sources but should be treated carefully.** The skill mentions it because (a) it's load-bearing context for the funding crisis Pushkarev wrote about publicly, (b) it has been independently reported by at least The Register, The Stack, and Hacker News commentary, and (c) Pushkarev has not publicly disputed the reporting. We do not link to or quote primary court records.

### Feb 14, 2023 — The "So, what's next?" statement

Pushkarev publishes [an 11,000-word statement on GitHub](https://github.com/zloirock/core-js) discussing the unsustainability of his situation. Key public claims:

- "Free open source software is fundamentally broken."
- "I could stop working on this silently, but I want to give open source one last chance."
- Initial fundraising: "$57 / month."
- When he placed a Patreon link in the install postinstall console output, the response was a "continuous stream of hate. Hundreds of messages, posts, and comments per day."
- He proposed several future paths: appropriate financial backing, employment by a company that pays him to work on core-js + web standards, going closed-source / commercial, or "slow death."

(All quotes via [The Stack, 2023-02-14](https://www.thestack.technology/core-js-maintainer-denis-pusharev-license-broke-angry/).)

### 2022–2024 — Sanctions impact

Following the Russian invasion of Ukraine (Feb 2022), Western payment processors progressively cut off Pushkarev's donation channels. Patreon, GitHub Sponsors, OpenCollective, and Stripe all imposed restrictions that reduced his ability to receive funds. The drop from ~$2,500/month to ~$400/month is partially attributable to these sanctions.

### 2023–2026 — Maintenance continues, alternative funding via direct channels

Pushkarev continues to ship releases on a regular cadence (roughly one minor or patch release per 2–6 weeks based on the [releases page](https://github.com/zloirock/core-js/releases)). Funding has migrated partly to direct channels (Boosty, Patreon where still accessible, OpenCollective). The maintenance burden has not been distributed across additional contributors in any meaningful way.

### Jan 7, 2026 — core-js 3.47.0

A maintenance + ECMAScript-feature release shipped per regular cadence. (This was the version cited in the skill's scoping survey in early 2026.)

### March 16, 2026 — core-js 3.49.0

Latest release at the date of this file. Adds and refines support for several Stage 3 / Stage 4 ECMAScript proposals — see "What core-js@3.49.0 covers" below.

### Ongoing — single-maintainer state

As of the date of this file: Pushkarev remains the sole primary maintainer. The funding situation has not been publicly resolved. The bus-factor remains one.

## Supply-chain advisory

What does "single-maintainer" mean in practice for a project with billions of monthly downloads?

### Risk vector 1 — Compromise of credentials

If Pushkarev's npm publish credentials, GitHub account, or signing keys are ever compromised — phishing, malware, theft, or coercion — an attacker has a one-shot path to publish a malicious core-js to npm that will land in millions of bundles within 24 hours.

### Risk vector 2 — Coercion / legal pressure

A single-maintainer project in any jurisdiction is more vulnerable to legal or political pressure than a distributed project. The maintainer can be compelled (or, more subtly, financially incentivized) to ship code they wouldn't otherwise.

### Risk vector 3 — Burnout / withdrawal

If Pushkarev steps away — voluntary or not — the project does not have an obvious successor. There is no formal contributor pipeline equivalent to (e.g.) Node.js's TSC or React's core team. A handoff would either be ad-hoc (a fork picks up momentum) or absent (the project goes unmaintained for an extended period). Both outcomes are bad for production users.

### Risk vector 4 — Fork-and-replace by a hostile party

The polyfill.io case (see [`polyfill-io-attack.md`](./polyfill-io-attack.md)) demonstrated that even a *legitimate* maintainer can sell a project to a *hostile* party. core-js is on npm, not a domain, so the analog isn't a domain transfer — but `npm` package transfers happen routinely, and the surface area is real.

### What the skill recommends (production usage)

The skill does not recommend abandoning core-js — it's not realistic, the alternatives are not drop-in. But it does recommend a discipline:

1. **Don't ship core-js wholesale.** Do not use `useBuiltIns: 'entry'` with `import 'core-js'` at the top of your entry point. That ships *all* of core-js to *all* users. See [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md).
2. **Use selective inclusion via `useBuiltIns: 'usage'`.** Babel's preset-env will pull in only the polyfills your code actually uses, scoped to the targets in your `browserslist`. At a modern baseline (Chromium 125+, Safari 17.4+, Firefox 129+), this should yield a small set — often empty.
3. **Pin the version.** Use `core-js@3.49.0` in your lockfile, not `^3.49.0`. Audit before bumping. The supply-chain risk window is "the time between a malicious release and your discovery"; pinning + manual review reduces it.
4. **`npm audit` + signature verification.** core-js is signed; verify the signature in CI. Subscribe to GitHub's security advisories for the repo. If the package's ownership ever changes or the maintainer composition shifts unexpectedly, treat it as a yellow flag.
5. **Prefer per-feature ponyfills where practical.** `es-shims/*` packages (e.g., [`array.prototype.flat`](https://www.npmjs.com/package/array.prototype.flat), [`object.fromentries`](https://www.npmjs.com/package/object.fromentries)) are smaller, narrower, and often by a different maintainer. They don't replace core-js for transpilation-driven coverage but they're a viable fallback for individual hot features.

See also `../transpilation/babel-preset-env.md` for the canonical `useBuiltIns` configuration.

## Alternatives (none are drop-in equivalent)

| Alternative | Coverage | Trade-off |
|---|---|---|
| **`es-shims/*`** | ~150 individual ponyfill packages, one per ECMAScript method | Explicit imports only; no automatic preset-env coupling. Multiple maintainers. Smaller surface per package. Doesn't solve "I need ES2015+ in my bundle automatically." |
| **`@babel/runtime-corejs3`** | Same coverage as core-js, sandboxed (no global pollution) | Still depends on core-js. Solves a different problem (sandbox isolation), not a supply-chain problem. |
| **Native + minimal targeted polyfills** | Whatever's already in the browser; per-feature ponyfills for gaps | Burden of identification on the developer. The skill's preferred path at a modern baseline. |
| **Fork of core-js** | Same as core-js | You inherit the maintenance burden. Several forks exist; none have meaningful traction. The bus-factor doesn't go away by forking. |
| **Stop transpiling for old targets** | The features you'd polyfill are already shipped | The skill's *strongest* recommendation. If your `browserslist` floor is at the Baseline of Chromium 125+ / Safari 17.4+ / Firefox 129+, core-js polyfills almost nothing useful. |

## What core-js@3.49.0 covers

core-js tracks ECMAScript proposals through stages 1–4 and provides polyfills for everything from ES5 onwards. As of 3.49.0 (March 16, 2026), notable recent additions / refinements (per the [releases page](https://github.com/zloirock/core-js/releases)):

- **Explicit Resource Management (Stage 4, ES2026)** — `DisposableStack`, `AsyncDisposableStack`, `Symbol.dispose`, `Symbol.asyncDispose`, `SuppressedError`. Added in v3.43.x.
- **Iterator helpers (Stage 4, ES2025)** — `Iterator.prototype.map/filter/take/drop/flatMap/reduce/toArray/forEach/some/every/find` plus the more recent `Iterator.concat`, `Iterator.zip`, `Iterator.zipKeyed`. Refined through v3.45.x.
- **Uint8Array base64 / hex** — `Uint8Array.fromBase64`, `.toHex`, `.setFromBase64`, etc. Added in v3.45.x.
- **Map upsert** — `Map.prototype.getOrInsert`, `WeakMap.prototype.getOrInsertComputed`. Added in v3.48.x.
- **Iterator.range** — Following the actual spec version, throwing `RangeError` on `NaN` start/end/step parameters. Added/refined in v3.49.x.
- **Float16Array, Error.isError, Promise.try, Promise.withResolvers, RegExp.escape** — All previously added.
- **Temporal (Stage 4 March 2026, ES2026)** — Polyfilled by core-js (though the canonical recommendation is the dedicated `@js-temporal/polyfill` package — see `../runtime-polyfills/temporal-api.md`).

What's been **removed** over recent versions: support for ancient legacy environments (IE9 and below), proposals that were never standardized (Records & Tuples, withdrawn April 2025), and some early stage-1 / stage-2 features whose specs shifted incompatibly.

## Where the skill points users

The expert-polyfills skill's stance: **core-js is a tool of last resort at this baseline, used carefully via `useBuiltIns: 'usage'`, with a pinned version and `npm audit` discipline. It is not the default.** The default is to not polyfill at all, and to use per-feature ponyfills only where the baseline genuinely lacks support.

For specific routing:

- Configuring core-js inside Babel: [`../transpilation/babel-preset-env.md`](../transpilation/babel-preset-env.md)
- Anti-pattern of `useBuiltIns: 'entry'` for modern targets: [`../anti-patterns/corejs-entry-modern.md`](../anti-patterns/corejs-entry-modern.md)
- The "is this even needed" decision tree: [`../meta/decision-tree.md`](../meta/decision-tree.md)
- The supply-chain story for the comparable polyfill.io domain: [`./polyfill-io-attack.md`](./polyfill-io-attack.md)
