---
date: 2026-04-27
coverage: extended
peers:
  - ../landscape-shifts/polyfill-io-attack.md
  - ../landscape-shifts/fastly-polyfill-mirror.md
  - ../anti-patterns/polyfill-io-after-attack.md
primary_sources:
  - https://blog.cloudflare.com/polyfill-io-now-available-on-cdnjs-reduce-your-supply-chain-risk/ — Cloudflare cdnjs mirror announcement (Feb 29, 2024)
  - https://blog.cloudflare.com/automatically-replacing-polyfill-io-links-with-cloudflares-mirror-for-a-safer-internet/ — auto-rewrite announcement (June 26, 2024)
  - https://cdnjs.com/libraries/polyfill — cdnjs library listing
---

# Cloudflare cdnjs polyfill mirror (extended)

> **Coverage tier: extended.** This file is descriptive — what the mirror is, how it differs from the original, and how to use it as a transitional measure. The skill's stance is **still self-host**; the mirror is a bridge, not a destination. See [`polyfill-io-attack.md`](./polyfill-io-attack.md) for the canonical "why."

## What it is

Cloudflare runs a free, drop-in replacement for the original `cdn.polyfill.io` at:

```
https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js
https://cdnjs.cloudflare.com/polyfill/v3/polyfill.js   (unminified)
```

Announced February 29, 2024 ([Cloudflare blog](https://blog.cloudflare.com/polyfill-io-now-available-on-cdnjs-reduce-your-supply-chain-risk/)) — *before* the malware attack went live in June 2024. Cloudflare anticipated the risk after the Funnull domain transfer was disclosed and stood up the mirror as a precaution.

The mirror runs from Cloudflare's `cdnjs` infrastructure (the same CDN that hosts thousands of other open-source JS libraries) and uses **Cloudflare's own fork** of the open-source `polyfill-service` codebase. Cloudflare's blog notes:

> "Cloudflare forked the project to add the compatibility for Cloudflare Workers."

> "Usage and deployment is intended to be identical to the original polyfill.io site. As a developer, you should be able to simply 'replace' the old link with the new cdnjs-hosted link without observing any side effects."

API parity with the pre-Funnull `cdn.polyfill.io` is the design goal. Same User-Agent-aware feature negotiation, same query parameters (`?features=...`), same `v3` versioning. Drop-in.

## Auto-rewrite (the load-bearing feature)

The more aggressive thing Cloudflare did: on **June 26, 2024**, the day after Sansec's disclosure, Cloudflare launched an [auto-rewrite feature](https://blog.cloudflare.com/automatically-replacing-polyfill-io-links-with-cloudflares-mirror-for-a-safer-internet/) for sites proxied through Cloudflare.

What it does:

> "For any HTTP response with an HTML Content-Type, we parse all JavaScript script tag source attributes. If any are found linking to polyfill.io, we rewrite the src attribute to link to our mirror instead."

So if your site is on Cloudflare and your HTML still contains:

```html
<script src="https://cdn.polyfill.io/v3/polyfill.min.js"></script>
```

Cloudflare's edge will rewrite it in flight to:

```html
<script src="https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js"></script>
```

The user's browser sees only the rewritten version.

### Auto-rewrite plan tier behavior

| Plan | Behavior |
|---|---|
| **Free** | Auto-enabled. The rewrite happens automatically; the customer doesn't have to opt in. |
| **Paid (Pro / Business / Enterprise)** | Available via single-click activation in the dashboard. Not auto-enabled. |
| **All plans** | Opt-out is available at any time via Security ⇒ Settings in the Cloudflare dashboard. |

This was a deliberate choice: free-plan customers are statistically more likely to be running stale templates and less likely to be actively maintaining their `<script>` tags, so the auto-rewrite default is biased toward "save the site from itself."

### What auto-rewrite does *not* do

- **It does not parse JavaScript.** It only inspects HTML `<script src>` attributes. Polyfill.io references *injected dynamically* by JS or rendered via a non-Cloudflare-proxied origin are not rewritten.
- **It does not work for non-HTML responses.** JSON responses that include `polyfill.io` URLs in some payload are untouched.
- **It does not work for sites not proxied through Cloudflare.** If your origin is on a different CDN, the auto-rewrite has no opportunity to inspect the response.

## Coverage

The mirror serves the same feature set as the original `cdn.polyfill.io` at the time of the Funnull acquisition. The feature catalog is essentially: every polyfill that the original `polyfill-service` repository covered, scoped to whatever User-Agent makes the request.

Important nuance: this means the mirror is **shipping a 2024-era polyfill catalog**. If you want a 2026-era polyfill, the mirror is not where you find it — and likely you don't need one for a 2026 baseline anyway.

Cloudflare's fork lives in their internal infrastructure; they note in the cdnjs announcement that they "plan to make the fork publicly accessible in the near future" though as of this file's date there's no clearly-public canonical fork URL. The skill treats the source-of-truth as the original `JakeChampion/polyfill-service` and `fastly/polyfill-service` codebases.

## What it doesn't fix (the skill's stance)

The Cloudflare cdnjs mirror is **a transitional measure, not a destination.** Five reasons:

1. **It's still 3rd-party JS.** The browser still loads + executes code from a non-origin URL. If `cdnjs.cloudflare.com` is ever compromised, you're back where polyfill.io ended up. Cloudflare is far more reputable than Funnull, but that's a probabilistic defense, not a structural one.
2. **It's still a CDN dependency.** If Cloudflare ever changes the URL, sunsets the mirror, or imposes rate limits, your sites break in a way you can't proactively detect. Mirror operators have no SLA to your team.
3. **It still adds a request.** Even with HTTP/2 + edge caching, a 3rd-party `<script>` adds a DNS lookup + TCP/TLS handshake on cold connections. A self-hosted polyfill bundle ships in your existing connection.
4. **SRI doesn't apply.** Like the original polyfill.io, the mirror generates per-User-Agent responses, so no two responses share a hash; you can't `integrity="sha384-..."` pin the `<script>`. Self-hosting with a fixed bundle hash and SRI is strictly stronger.
5. **It papers over the underlying question.** The most important question — "do I need to ship *any* of these polyfills to a 2024+ browser?" — is one the mirror lets you defer indefinitely. At a modern baseline, the answer is almost always no.

## When to use it (the legitimate cases)

The skill recommends the mirror for **at most three scenarios**:

1. **Active migration.** You've discovered a `<script src="polyfill.io">` in your codebase and you need it to keep working *while* you migrate to native or self-hosted. The mirror is fine for the days or weeks it takes to ship the fix. Don't make it permanent.
2. **Legacy site you can't migrate.** A WordPress / Drupal site with thousands of pages of editor-pasted templates, or a 3rd-party widget you don't own. Cloudflare's auto-rewrite lets you stop the bleeding without per-page edits. Document the compromise; revisit annually.
3. **You're the operator of a customer-facing CDN.** If your platform serves HTML where end users have pasted polyfill.io references and you can't audit them all, the mirror gives you a safe default. (This is essentially Cloudflare's own use case.)

For everything else, the answer is the migration playbook in [`polyfill-io-attack.md`](./polyfill-io-attack.md).

## How to migrate off the mirror

Once you're on the mirror, the same migration applies as the polyfill.io migration:

1. **Open DevTools → Coverage → reload the page.** Look at which polyfills the script bundle exposes. Most sites will see *zero* polyfilled APIs actually invoked in modern browsers.
2. **If zero invocations: delete the `<script>` tag.** Test in Chromium 125+, Safari 17.4+, Firefox 129+. Done.
3. **If some invocations: identify the specific features.** Map them to per-feature ponyfills via [`../runtime-polyfills/`](../runtime-polyfills/) and [`../css-polyfills-and-shims/`](../css-polyfills-and-shims/). Most candidates at this baseline are narrow: `Temporal`, `URLPattern` (Firefox 129–143), CSS Anchor Positioning (Safari < 26 / Firefox < 147), customizable `<select>` (Chrome 135+ only).
4. **Use Babel `useBuiltIns: 'usage'` for unmappable cases.** If you have a long tail of ES2015+ polyfill needs and your `browserslist` floor is genuinely below baseline, configure Babel's preset-env to selectively inject polyfills at build time. See [`../transpilation/babel-preset-env.md`](../transpilation/babel-preset-env.md).
5. **Self-host the bundle.** Whatever ends up in your final polyfill set, ship it through your own pipeline with a fixed SRI hash. Add `script-src 'self'` to your CSP. The supply-chain surface is now your own build pipeline, which you can audit.

## See also

- [`polyfill-io-attack.md`](./polyfill-io-attack.md) — the canonical "why polyfill.io is dead"
- [`fastly-polyfill-mirror.md`](./fastly-polyfill-mirror.md) — the parallel Fastly mirror
- [`../anti-patterns/polyfill-io-after-attack.md`](../anti-patterns/polyfill-io-after-attack.md) — why the mirrors are still an anti-pattern as a destination
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what's actually shipped at Chromium 125+ / Safari 17.4+ / Firefox 129+
