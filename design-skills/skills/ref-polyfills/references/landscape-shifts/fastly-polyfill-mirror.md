---
date: 2026-04-27
coverage: extended
peers:
  - ../landscape-shifts/polyfill-io-attack.md
  - ../landscape-shifts/cloudflare-cdnjs-polyfill.md
  - ../anti-patterns/polyfill-io-after-attack.md
primary_sources:
  - https://community.fastly.com/t/new-options-for-polyfill-io-users/2540 — Fastly's drop-in replacement announcement (Feb 28, 2024)
  - https://polyfill-fastly.io/ — live service URL
  - https://github.com/fastly/polyfill-service-self-hosted — self-hosted Fastly fork (deprecated 2026-01-14)
---

# Fastly polyfill mirror (extended)

> **Coverage tier: extended.** Same posture as the Cloudflare mirror file: descriptive, transitional. Self-hosting remains the recommendation. See [`polyfill-io-attack.md`](./polyfill-io-attack.md) for the "why."

## What it is

Fastly runs two domains as drop-in replacements for the original `cdn.polyfill.io`:

```
https://polyfill-fastly.io/v3/polyfill.min.js
https://polyfill-fastly.net/v3/polyfill.min.js
```

Both serve identical content; Fastly maintains the dual-domain setup for resilience. Announced February 28, 2024 ([Fastly community post](https://community.fastly.com/t/new-options-for-polyfill-io-users/2540)) — one day before Cloudflare's cdnjs announcement, and four months before the malware attack went live.

The service runs on Fastly's Compute@Edge platform using **Fastly's fork of the open-source `polyfill-service`** Rust codebase. Fastly was the original CDN that hosted `cdn.polyfill.io` before the project was sold to Funnull, so they had the operational expertise to spin up the replacement quickly.

API parity is the design goal: query parameters (`?features=...`, `?ua=...`, etc.) and the per-User-Agent response semantics match the original polyfill.io as it existed before the Funnull transfer.

Service tier: Fastly classified the service as a **"Tier 2 open source project"** — free for end users, no signup, drop-in.

## Self-hosted Fastly fork — status note

Fastly maintained a sister repository, [`fastly/polyfill-service-self-hosted`](https://github.com/fastly/polyfill-service-self-hosted), that allowed customers to deploy the same service inside their own Fastly account.

> **As of 2026-01-14, that repository is marked deprecated.**

The repo's deprecation does **not** automatically mean `polyfill-fastly.io` and `polyfill-fastly.net` are going away — at the date of this file (2026-04-27) the customer-facing domains are still operational. But the deprecation is a leading indicator: Fastly is signaling that they no longer recommend the polyfill-as-a-service model going forward, even on their own infrastructure. The skill reads this as another reason to migrate off the mirror in favor of self-hosting at the application layer (i.e., the polyfill ships in your bundle, not via a request to a CDN at runtime).

> **Verification status: the deprecation notice is on the repository's GitHub page. The continued operation of the customer-facing domains is observable but may shift.** If you're depending on the Fastly mirror in production, treat this as an active situation worth monitoring quarterly.

## How it differs from Cloudflare's mirror

The two mirrors are functionally similar — both serve clean forks of the same upstream `polyfill-service` codebase, both target API parity with the pre-Funnull `cdn.polyfill.io`. Two operational differences:

### Difference 1 — No auto-rewrite

Cloudflare auto-rewrites `<script src="*polyfill.io*">` references to its own mirror for free-plan-proxied sites. Fastly does **not** do this automatically. Fastly customers who want to redirect references must do so themselves, either:

- **At the application layer**, by editing their HTML.
- **At the edge**, by writing a Fastly Compute@Edge VCL or compute service that scans HTML responses and rewrites `polyfill.io` references in flight.

The Fastly community thread includes a comment suggesting using Fastly Compute to manually scan and rewrite — but this is an opt-in custom configuration, not a default behavior.

### Difference 2 — Geographic edge

Cloudflare and Fastly have overlapping but not-identical edge POP geographies. Cloudflare has historically had broader free-tier global presence; Fastly has had stronger performance in certain regions (particularly North America / Europe). For a polyfill `<script>` on a high-traffic site, the latency difference is typically negligible; the choice usually comes down to which CDN your origin is already on.

### Difference 3 — Plan model

Cloudflare's auto-rewrite makes the mirror effectively automatic for free-plan customers; Fastly's mirror is opt-in for everyone, free or paid, customer or non-customer of Fastly. Both are free at the consumption tier — there's no charge to load `polyfill-fastly.io` even if you're not a Fastly customer.

## Same caveats as the Cloudflare mirror

The skill's stance on `polyfill-fastly.io` is identical to its stance on `cdnjs.cloudflare.com/polyfill`:

1. **Still 3rd-party JS.** Whatever Fastly serves, the browser executes. Compromise vector intact.
2. **Still a CDN dependency.** Fastly's own deprecation of `polyfill-service-self-hosted` is a reminder that the mirror's lifecycle is not under your control.
3. **Still adds a request.** No bundling benefit.
4. **SRI still doesn't apply.** Per-User-Agent responses preclude hash pinning.
5. **Still papers over the underlying question.** Most sites at a modern baseline don't need any polyfills.

The mirror is a **transitional bridge**, not a destination. See [`polyfill-io-attack.md`](./polyfill-io-attack.md) §"Why mirrors don't fully solve the problem" for the full argument.

## When to use it (the legitimate cases)

Same as for the Cloudflare mirror:

1. **Active migration.** You're on Fastly already and `<script src="polyfill.io">` is in your codebase pending fix.
2. **Legacy site you can't migrate.** Editor-templated content, 3rd-party widget you don't own.
3. **You're proxying through Fastly.** If your origin is on Fastly, using Fastly's mirror is the lowest-friction transitional option.

For everything else, follow the migration playbook in [`polyfill-io-attack.md`](./polyfill-io-attack.md).

## How to migrate off the mirror

Identical to the Cloudflare migration:

1. **DevTools → Coverage** — see which polyfilled APIs your code actually invokes at modern baselines. Most sites: zero.
2. **Delete the `<script>`** if zero invocations.
3. **Per-feature ponyfills** for what's left. See [`../runtime-polyfills/`](../runtime-polyfills/), [`../css-polyfills-and-shims/`](../css-polyfills-and-shims/).
4. **Babel `useBuiltIns: 'usage'`** for cases with broad ES2015+ polyfill needs. See [`../transpilation/babel-preset-env.md`](../transpilation/babel-preset-env.md).
5. **Self-host the bundle.** Fixed SRI hash. CSP `script-src 'self'`. Audit your own pipeline.

## Self-host the polyfill-service codebase (advanced)

If you legitimately need the User-Agent-aware polyfill-bundling architecture — large site, performance-critical, mixed-baseline audience — you can fork the upstream `polyfill-service` codebase and run it inside your own infrastructure (e.g., a Cloudflare Worker, an AWS Lambda@Edge, a container, or your own Fastly account).

Sources to start from:

- [`fastly/polyfill-service`](https://github.com/fastly/polyfill-service) — the canonical Rust implementation that originally powered `cdn.polyfill.io`. Still actively maintained for the live `polyfill-fastly.io` service.
- [`fastly/polyfill-service-self-hosted`](https://github.com/fastly/polyfill-service-self-hosted) — Fastly's customer-deployable wrapper. **Deprecated 2026-01-14**; functional but not future-supported. Use the upstream repo as your fork base instead.

Self-hosting gets you:

- Your origin, your SRI hash potential (if you fix the per-User-Agent behavior to a smaller bucket count), your CSP boundary.
- Independence from the mirror operators' lifecycle decisions.
- The ability to audit / patch the polyfill code yourself.

It costs you:

- Operational responsibility for the service.
- Staying current with whatever upstream patches the maintainers ship.
- Most of the time, this is overkill — for any project that doesn't have a serious legacy-browser support requirement, the application-layer ponyfill approach is much simpler.

## See also

- [`polyfill-io-attack.md`](./polyfill-io-attack.md) — the canonical "why polyfill.io is dead"
- [`cloudflare-cdnjs-polyfill.md`](./cloudflare-cdnjs-polyfill.md) — the parallel Cloudflare mirror
- [`../anti-patterns/polyfill-io-after-attack.md`](../anti-patterns/polyfill-io-after-attack.md) — why mirrors-as-destination is an anti-pattern
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what's actually shipped at the current baseline
