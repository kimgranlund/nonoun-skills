---
date: 2026-04-27
coverage: canonical
peers:
  - ../landscape-shifts/polyfill-io-attack.md
  - ../landscape-shifts/cloudflare-cdnjs-polyfill.md
  - ../landscape-shifts/fastly-polyfill-mirror.md
  - ../anti-patterns/corejs-entry-modern.md
  - ../anti-patterns/target-es5-modern.md
  - ../transpilation/babel-preset-env.md
  - ../feature-detection/ponyfill-pattern.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://blog.cloudflare.com/automatically-replacing-polyfill-io-links-with-cloudflares-mirror-for-a-safer-internet/ — Cloudflare's June 26, 2024 announcement
  - https://blog.cloudflare.com/polyfill-io-now-available-on-cdnjs-reduce-your-supply-chain-risk/ — cdnjs.cloudflare.com/polyfill rollout
  - https://community.fastly.com/t/new-options-for-polyfill-io-users/2540 — Fastly's polyfill-fastly.io / .net mirror
  - https://www.bleepingcomputer.com/news/security/cloudflare-we-never-authorized-polyfillio-to-use-our-name/ — Cloudflare's disavowal of polyfill.io's prior use of their name
  - https://content-security-policy.com/script-src/ — CSP `script-src` reference
  - https://web.dev/articles/baseline-and-polyfills — modern Baseline guidance
  - https://github.com/cdnjs/polyfill-service — cdnjs/Cloudflare's open-source mirror
---

# Anti-pattern: relying on polyfill.io mirrors after the June 2024 attack

## The anti-pattern

After the polyfill.io supply-chain attack of June 2024, projects migrated their `<script>` tags from `cdn.polyfill.io` to one of the safe mirrors:

```html
<!-- Before the attack — compromised by Funnull-served malware -->
<script src="https://cdn.polyfill.io/v3/polyfill.min.js?features=fetch%2Cdefault"></script>

<!-- The hasty, partially-correct migration -->
<script src="https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js?features=fetch%2Cdefault"></script>
<!-- or -->
<script src="https://polyfill-fastly.io/v3/polyfill.min.js?features=fetch%2Cdefault"></script>
```

The migration was correct — sites running malware needed to stop running malware immediately, and switching the domain was the fastest fix. But treating the mirror as **the solution** is the anti-pattern this file argues against. The mirror is still 3rd-party JS that loads at runtime from a domain you don't control. At the modern baseline, the right answer is to remove the polyfill request entirely.

## Background — what happened

The timeline, anchored to what the skill's [`../landscape-shifts/polyfill-io-attack.md`](../landscape-shifts/polyfill-io-attack.md) covers in full:

- **February 2024**: A Chinese company, Funnull, acquired the polyfill.io domain and the project's GitHub repository from the previous owner. The original maintainer of the open-source polyfill-service codebase (Andrew Betts, formerly of the Financial Times) immediately and publicly disavowed the new owner and warned users to stop using `cdn.polyfill.io`. ([Sansec investigation](https://sansec.io/research-survey/polyfill-supply-chain-attack))
- **June 25, 2024**: Sansec published forensic evidence showing the polyfill.io CDN was injecting malware into the responses it served. The injection was conditional — bot/crawler User-Agents got clean responses; real users on mobile got redirects to sports-betting and adult sites with sophisticated evasion techniques.
- **June 26, 2024**: Cloudflare announced automatic rewriting of `polyfill.io` script-src URLs to `cdnjs.cloudflare.com/polyfill` for sites on their free plan. ([Cloudflare announcement](https://blog.cloudflare.com/automatically-replacing-polyfill-io-links-with-cloudflares-mirror-for-a-safer-internet/))
- **June 27, 2024**: Namecheap, the domain registrar, suspended the polyfill.io domain. The active malware-serving CDN was offline. Cloudflare and Fastly continued to operate clean mirrors at `cdnjs.cloudflare.com/polyfill` and `polyfill-fastly.io` for sites that had not yet migrated.

The attack affected an estimated 100,000+ sites at peak (Sansec's number), with Cloudflare suggesting the headline-traffic figure was closer to "tens of millions." Whichever number you pick, it is one of the largest web supply-chain incidents on record.

## Why the mirror-as-solution anti-pattern persists

Three reasons:

1. **The migration was the right immediate move.** During the active attack, switching `cdn.polyfill.io` to `cdnjs.cloudflare.com/polyfill` was the fastest way to stop serving malware. Teams under incident-response pressure made that change and moved on. The work to remove the polyfill request entirely never made it onto the backlog.
2. **Cloudflare's automatic rewrite hid the problem.** Cloudflare turned on URL rewriting for free-plan sites by default — proxied HTML responses had `polyfill.io` script srcs rewritten on the fly to point at `cdnjs.cloudflare.com/polyfill`. Many sites switched without any code change, and consequently without ever auditing their templates for `polyfill.io` references. The HTML still says `polyfill.io`. The user gets bytes from `cdnjs.cloudflare.com`. ([Cloudflare blog](https://blog.cloudflare.com/automatically-replacing-polyfill-io-links-with-cloudflares-mirror-for-a-safer-internet/))
3. **Inertia.** "We already switched, that's the fix." Treating an emergency mitigation as the durable answer is human; auditing post-incident architecture is work that nobody schedules until the next incident.

## Why the mirror is still wrong

### Mirror is still a 3rd-party CDN dependency

If `cdnjs.cloudflare.com` or `polyfill-fastly.io` experiences an outage — Cloudflare's June 2022 outage, the August 2022 Cloudflare outage, the November 2024 Fastly incidents, the global routing event in October 2025 — your polyfill request 404s. If your application's polyfilled feature is in the critical path, the application breaks. Self-hosted polyfills go down only if your own origin goes down, in which case the polyfill is the least of your problems.

### Mirror is still 3rd-party JS

Cloudflare and Fastly are both reputable operators. Neither has a record of malicious behavior. But the trust boundary moved one hop, not zero hops. A future compromise of `cdnjs.cloudflare.com` — by an internal threat actor, a state-level adversary, or a chain-of-trust failure at Cloudflare's CA — puts you back where polyfill.io was. The probability is genuinely lower (Cloudflare invests heavily in SDLC; the cdnjs ecosystem is open-source and watched). The probability is not zero. **The supply-chain risk of any 3rd-party CDN is non-zero, and self-hosted code is the only zero-risk option** ([Cloudflare's own disavowal of polyfill.io](https://www.bleepingcomputer.com/news/security/cloudflare-we-never-authorized-polyfillio-to-use-our-name/) — even Cloudflare did not want their name attached to a polyfill service they did not run).

### Mirror's per-request bundle breaks caching

The polyfill.io API works by sniffing the User-Agent of the requesting browser server-side and returning the smallest bundle that fills the gap for *that* browser. cdnjs.cloudflare.com/polyfill and polyfill-fastly.io preserve this behavior. The consequence:

- The bundle is **different for every User-Agent**. Two users on the same site get different polyfill bytes.
- Strict CSP (`script-src 'self'`) cannot whitelist this — you'd have to allow the entire mirror domain, which whitelists the whole world's polyfills.
- HTTP caching is fragmented: Cache-Control headers vary by UA, and shared caches (corporate proxies, ISPs) may serve the wrong bundle to the wrong UA.
- Subresource Integrity (SRI) cannot be used, because the hash of the response is not known in advance.

A self-hosted polyfill, by contrast: one URL, one hash, one CSP entry, one cache key.

### Mirror still ships polyfills the user doesn't need

Polyfill.io's `?features=` query parameter was always a coarse filter — request `fetch,IntersectionObserver,structuredClone` and you got those features (or no-ops where the requesting UA already supported them). At the modern baseline, **all three are native everywhere**. The bundle sent to a Chrome 125 / Safari 17.4 / Firefox 129 user is empty or near-empty. The cost is the request itself: the round-trip latency, the DNS lookup, the TLS handshake, the response wait — even when the body is the literal string `/* No polyfills needed for current settings */`. At p95 mobile network latency (~600ms), this is wasted user time.

The math at the modern baseline:

| Polyfill.io feature | Native at baseline? | Polyfill bytes |
|---|---|---|
| `fetch` | Yes (Chrome 42, Safari 10.1, Firefox 39) | 0 |
| `Promise` | Yes | 0 |
| `IntersectionObserver` | Yes | 0 |
| `structuredClone` | Yes (Chrome 98, Safari 15.4, Firefox 94) | 0 |
| `Array.prototype.flat` | Yes | 0 |
| `Object.fromEntries` | Yes | 0 |
| `String.prototype.replaceAll` | Yes | 0 |
| `URL`, `URLSearchParams` | Yes | 0 |

If the request is going out for any of these, **delete the request**. There is no benefit. The mirror was already a 3rd-party dependency for zero functional gain.

## The fix — a five-step migration

### Step 1: audit what your site actually requests from polyfill.io / mirrors

```sh
# Search the codebase
grep -rn 'polyfill\.io\|cdnjs\.cloudflare\.com/polyfill\|polyfill-fastly' \
  src/ public/ templates/ pages/ app/ --include='*.html' --include='*.tsx' \
  --include='*.jsx' --include='*.vue' --include='*.svelte' --include='*.astro' \
  --include='*.liquid' --include='*.erb' --include='*.haml' --include='*.pug'

# Check live HTML for the canonical entries
curl -s https://yoursite.com/ | grep -E 'polyfill\.io|cdnjs.*polyfill|polyfill-fastly'

# Audit Cloudflare's auto-rewrite if you're on the free plan:
# Dashboard → Speed → Optimization → "Auto-replace polyfill.io"
```

Note the `?features=...` query string in each occurrence — that's the list you need to mentally cross-check against your modern baseline.

### Step 2: for each requested feature, decide its post-baseline status

For each `?features=` entry, look it up in the skill's [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) cheat sheet. Decision tree:

- **Already native at baseline** → delete the polyfill request. No replacement.
- **Not native at baseline, but there's a build-time transform** (e.g. lightningcss for relative-color CSS) → configure the build tool, no runtime polyfill.
- **Not native at baseline, runtime polyfill needed** (e.g. Iterator helpers for Safari 17.4–18.3, Temporal, URLPattern in Firefox 129–143) → import the per-feature polyfill or ponyfill at build time. See [`../runtime-polyfills/`](../runtime-polyfills/).
- **Bug workaround masquerading as polyfill** (rare) → see [`../css-color-bugs/`](../css-color-bugs/), [`../popover-quirks/`](../popover-quirks/), [`../anchor-positioning-quirks/`](../anchor-positioning-quirks/) for the catalog.

For the long tail of 2017-era polyfills (`fetch`, `Promise`, `Array.prototype.includes`, `Object.assign`), the answer is almost always "delete." This is the bulk of the migration.

### Step 3: replace runtime requests with build-time inclusion

If a polyfill is genuinely needed, import it at build time and let your bundler handle it. The pattern, per tool:

```js
// Babel preset-env — see ./corejs-entry-modern.md for the full config
{
  useBuiltIns: 'usage',
  corejs: { version: '3.47', proposals: true },
  targets: { chrome: '125', firefox: '129', safari: '17.4' },
}
```

```js
// Per-feature ponyfill — preferred for narrow needs
import { groupBy } from 'es-feature-helpers';
const groups = groupBy(items, x => x.category);
```

```js
// Conditional, only-when-needed
if (typeof Array.prototype.findLast !== 'function') {
  await import('./polyfills/find-last.js');
}
```

The result: polyfill bytes that are part of *your* bundle, served from *your* origin, with *your* hash, under *your* CSP.

### Step 4: remove all references to polyfill mirrors from HTML/templates

```diff
- <script src="https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js?features=fetch"></script>
+ <!-- removed; fetch is native at baseline -->
```

Audit every template, every layout, every email-template-that-renders-HTML, every PDF-generation pipeline. The polyfill.io references propagate further than expected — many CMSes had `<script src="https://cdn.polyfill.io/...">` baked into theme defaults. Drupal, WordPress, Magento, and Salesforce all had affected modules that needed patching. ([Drupal webform polyfill issue](https://www.drupal.org/project/webform/issues/3458611) is a representative example.)

### Step 5: lock the door with CSP

Add a Content Security Policy that disallows external script CDNs by default, and whitelist only what you actually need:

```http
Content-Security-Policy: default-src 'self';
  script-src 'self' 'wasm-unsafe-eval' 'strict-dynamic';
  script-src-elem 'self';
  object-src 'none';
  base-uri 'self';
  upgrade-insecure-requests;
```

Critically: **no entries for `cdn.polyfill.io`, `cdnjs.cloudflare.com`, or `polyfill-fastly.io`**. If any code attempts to load from those origins, the browser will block it and you'll see a CSP violation in your reports — exactly the alarm you want.

If your application genuinely needs Cloudflare's CDN for non-polyfill assets (e.g. you serve from `cdn.yourdomain.com` which is a Cloudflare-fronted origin), allowlist *your* CDN subdomain, not `cdnjs.cloudflare.com` as a generic. ([CSP `script-src` reference](https://content-security-policy.com/script-src/))

## A concrete migration: before/after

A representative WordPress site, mid-traffic, with a typical theme:

```html
<!-- BEFORE: post-attack, mirror migration done, no audit -->
<head>
  <script src="https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js?features=fetch%2CPromise%2CIntersectionObserver%2CObject.assign%2CArray.from"></script>
  <link rel="stylesheet" href="https://yoursite.com/wp-content/themes/twentytwentyfour/style.css">
  <script src="https://yoursite.com/wp-content/themes/twentytwentyfour/main.js"></script>
</head>
```

```html
<!-- AFTER: polyfill request deleted (all five features are native at baseline) -->
<head>
  <link rel="stylesheet" href="https://yoursite.com/wp-content/themes/twentytwentyfour/style.css">
  <script src="https://yoursite.com/wp-content/themes/twentytwentyfour/main.js"></script>
</head>
<!--
  Content-Security-Policy: default-src 'self'; script-src 'self';
  No external script CDN allowed.
-->
```

Two lines deleted. A round-trip saved. A 3rd-party dependency removed. A CSP that disallows the entire class of supply-chain attack the polyfill.io incident represented.

## Self-hosting recipe

If your audit (step 2 above) actually surfaces a polyfill you do need at the modern baseline — Iterator helpers for Safari 17.4–18.3 is a real one, Temporal is another for Safari at-baseline — ship the polyfill JS as part of *your* bundle. Three approaches:

```js
// 1. Babel preset-env handles it (see ./corejs-entry-modern.md)
// useBuiltIns: 'usage' will inject the per-feature import where Babel sees the feature used.

// 2. Per-feature ponyfill, explicit import (preferred when feasible)
import { Iterator } from 'es-iterator-helpers'; // for Safari 17.4–18.3 only
const result = Iterator.from([1,2,3]).filter(x => x % 2).toArray();

// 3. Conditional import, deferred load
if (!('helpers' in Iterator.prototype)) {
  await import('./polyfills/iterator-helpers.js');
}
```

For SWC and esbuild, the pattern is identical: explicit imports go through the bundler, which inlines them. Neither tool has Babel's `useBuiltIns: 'usage'` magic — you import what you need, by hand, and that is fine.

## Cross-reference

- [`../landscape-shifts/polyfill-io-attack.md`](../landscape-shifts/polyfill-io-attack.md) — the full timeline of the attack, with citations to Sansec, Cloudflare, Namecheap, and Censys.
- [`../landscape-shifts/cloudflare-cdnjs-polyfill.md`](../landscape-shifts/cloudflare-cdnjs-polyfill.md) — the Cloudflare mirror, its automatic-rewrite feature, and operational details.
- [`../landscape-shifts/fastly-polyfill-mirror.md`](../landscape-shifts/fastly-polyfill-mirror.md) — Fastly's `polyfill-fastly.io` and `polyfill-fastly.net` mirrors.
- [`./corejs-entry-modern.md`](./corejs-entry-modern.md) — the build-time pattern that replaces runtime polyfills.
- [`./target-es5-modern.md`](./target-es5-modern.md) — its sibling: don't transpile to ES5.
- [`../feature-detection/ponyfill-pattern.md`](../feature-detection/ponyfill-pattern.md) — explicit-import polyfill pattern.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — the cheat sheet for "is this native at baseline?"
