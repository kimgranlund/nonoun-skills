---
date: 2026-04-27
coverage: canonical
peers:
  - ../landscape-shifts/cloudflare-cdnjs-polyfill.md
  - ../landscape-shifts/fastly-polyfill-mirror.md
  - ../anti-patterns/polyfill-io-after-attack.md
primary_sources:
  - https://blog.cloudflare.com/automatically-replacing-polyfill-io-links-with-cloudflares-mirror-for-a-safer-internet/ — Cloudflare auto-rewrite announcement (June 26, 2024)
  - https://blog.cloudflare.com/polyfill-io-now-available-on-cdnjs-reduce-your-supply-chain-risk/ — Cloudflare cdnjs mirror announcement (Feb 29, 2024)
  - https://sansec.io/research-survey/polyfill-supply-chain-attack — Sansec disclosure of conditional malware (June 25, 2024)
  - https://community.fastly.com/t/new-options-for-polyfill-io-users/2540 — Fastly's drop-in replacement announcement (Feb 28, 2024)
  - https://www.theregister.com/2024/06/25/polyfillio_china_crisis/ — Andrew Betts statement reporting
  - https://www.sonatype.com/blog/polyfill.io-supply-chain-attack-hits-100000-websites-all-you-need-to-know — Sonatype primer (June 26, 2024)
  - https://x.com/triblondon/status/1761852117579427975 — Andrew Betts' original tweet (Feb 25, 2024)
  - https://www.bleepingcomputer.com/news/security/polyfill-claims-it-has-been-defamed-returns-after-domain-shut-down/ — Namecheap suspension (June 27, 2024)
  - https://censys.com/blog/july-2-polyfill-io-supply-chain-attack-digging-into-the-web-of-compromised-domains/ — Censys host count (July 2, 2024)
---

# polyfill.io supply-chain attack — the load-bearing story

> **Status at 2026-04-27.** The original `cdn.polyfill.io` domain has been suspended for 22 months. Cloudflare and Fastly run clean mirrors. The skill's stance is unchanged: **self-host. Don't load polyfills from any third-party CDN at runtime — including the mirrors.** This file is the canonical reference; every other file that says "polyfill.io is hostile" links here.

## Why this file is canonical

Three reasons the polyfill.io attack matters for the skill:

1. **It killed the most-recommended polyfill delivery mechanism overnight.** For ~10 years (2014–2024), `<script src="https://cdn.polyfill.io/v3/polyfill.min.js">` was the canonical "just sprinkle polyfills on it" pattern. Tutorials, Stack Overflow answers, and major sites still referenced it. Every one of those references became a malware vector in February 2024.

2. **It is the canonical real-world example of supply-chain compromise via domain transfer.** Not a typosquat, not a malicious-package-update — a transfer of a *trusted* domain name and *trusted* GitHub repo to a hostile actor. The attacker inherited 100K+ existing `<script>` tags pointing at the URL.

3. **The "fix" — Cloudflare/Fastly mirrors — does not address the structural risk.** Mirrors are still 3rd-party JS, still load at runtime, still represent a vector if the mirror is ever compromised, the URL ever changes, or the customer's CDN provider is ever subverted. The only real fix is to stop loading polyfills from any 3rd party and self-host whatever (small) set you actually need.

## Timeline (verified dates)

| Date | Event |
|---|---|
| **2014** | Andrew Betts (then at the Financial Times) creates the polyfill service. |
| **~2017** | Project transitions out of FT into community / Fastly stewardship; Fastly's `polyfill-service` becomes the canonical implementation. |
| **February 2024** | Funnull (a relatively unknown Chinese CDN/registrar entity) acquires the `polyfill.io` domain and the `polyfill-service` GitHub repository. The transfer is not announced through the typical maintainer channels. |
| **Feb 25, 2024** | Andrew Betts publicly warns: "If your website uses `polyfill.io`, remove it IMMEDIATELY." Posts on X (Twitter) at [@triblondon](https://x.com/triblondon/status/1761852117579427975). Clarifies he never owned the domain and had no influence over its sale. |
| **Feb 28, 2024** | Fastly community post announces `polyfill-fastly.io` and `polyfill-fastly.net` as drop-in replacements running on a Fastly-maintained fork of the open-source codebase. |
| **Feb 29, 2024** | Cloudflare announces `cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js` as an alternative mirror. |
| **June 8, 2024 (15:23:51 UTC)** | First detected malicious response served by `cdn.polyfill.io`. Cloudflare's Page Shield observed the injection. |
| **June 25, 2024** | Sansec publicly discloses: `cdn.polyfill.io` is conditionally injecting malware into responses based on User-Agent and time-of-day. ~100K websites affected. |
| **June 26, 2024** | Cloudflare announces the [auto-rewrite feature](https://blog.cloudflare.com/automatically-replacing-polyfill-io-links-with-cloudflares-mirror-for-a-safer-internet/): for any HTML response served through Cloudflare's free plan, `<script src="*polyfill.io*">` tags are rewritten in flight to point at `cdnjs.cloudflare.com/polyfill/...`. Free plan = automatic; paid plan = single-click opt-in; opt-out via Security ⇒ Settings dashboard. |
| **June 27, 2024** | Namecheap (the registrar) suspends the `polyfill.io` domain following community pressure. The "owner" briefly claims defamation; the suspension stands. |
| **July 2, 2024** | Censys reports 384,773 hosts still embedding `cdn.polyfill.io` references in their HTML — domain suspended but the dangling `<script>` tags remain. |
| **2024 H2 onwards** | `polyfill.io` domain remains suspended / parked. Industry consensus solidifies: don't load polyfills from any 3rd-party CDN. |
| **Jan 14, 2026** | Fastly's `fastly/polyfill-service-self-hosted` repository is marked deprecated, signaling the long-term wind-down of the polyfill-as-a-service model. The `polyfill-fastly.io` and `polyfill-fastly.net` domains continue to operate as drop-in replacements but the broader project is in maintenance-only mode. |
| **2026-04-27** | At the date of this file: `cdn.polyfill.io` remains dead. Cloudflare cdnjs mirror and Fastly mirrors continue to run. The skill recommends migrating off all of them. |

## Mechanism (how the attack worked)

The attack was technically sophisticated, which is part of why it took ~4 months from acquisition to detection.

### Conditional payload delivery

The compromised `cdn.polyfill.io` server did not serve malware to *every* request. Instead, the response body was generated dynamically per request based on:

- **User-Agent inspection.** Mobile browser UAs (iPhone, iPad, Android) received the malicious payload; desktop UAs received clean polyfills. This evades developer testing on desktop.
- **Time-of-day windows.** The malware activated only during specific hourly bands (per Sansec: roughly 0–2 AM, 2–4 AM, 4–7 AM, 7–8 AM in the user's local timezone), with varying probabilities — biased toward off-hours when fewer eyes are on real-time monitoring.
- **Admin-account avoidance.** The payload checked for indicators that the visitor was logged in as an administrator (cookies, query strings, referrer patterns) and skipped injection in those cases — keeping site owners unaware.
- **Analytics avoidance.** When the page loaded common web-analytics scripts (Google Analytics, etc.), the malware delayed or skipped execution to avoid showing in traffic reports as a redirect anomaly.

### Payload behavior

Once triggered, the malware redirected the user to scam destinations:

- Fake Google Analytics domain: `www.googie-anaiytics.com` (note the homoglyph: `googie` not `google`, `anaiytics` not `analytics`).
- Sports-betting and adult-content scam sites.
- Domain rotation through `kuurza.com`, `newcrbpc.com`, and others.

### Code obfuscation

The injected JavaScript included anti-reverse-engineering protections — string obfuscation, control-flow flattening, and function names in transliterated Chinese: `check_tiaozhuan()` (跳转 / "jump" / "redirect"), `vfed_update()`, `isPc()` (is-PC, i.e., is-desktop). The transliterations are an artifact of being authored by a Chinese-speaking developer.

### IOCs (indicators of compromise) — Sansec disclosure

| Indicator | Type |
|---|---|
| `cdn.polyfill.io` | Compromised serving domain |
| `kuurza.com` | Redirect destination |
| `www.googie-anaiytics.com` | Homoglyph fake-analytics domain |
| `newcrbpc.com` | Secondary redirect destination |
| `check_tiaozhuan()` | Function name in injected JS |
| `vfed_update()` | Function name in injected JS |
| `isPc()` | Function name in injected JS |

If your site logs include any of these strings in third-party-request URLs or your CSP-violation reports, you served the malicious payload. Audit your historical CDN logs.

## Andrew Betts response

Andrew Betts (former Financial Times engineer, original creator of polyfill.io) **publicly denounced the acquisition four months before the attack** went live. His February 25, 2024 statement is preserved at [x.com/triblondon/status/1761852117579427975](https://x.com/triblondon/status/1761852117579427975). The two key claims (per The Register, June 25, 2024):

> "If your website uses `polyfill.io`, remove it IMMEDIATELY."

> "I created the polyfill service project but I have never owned the domain name and I have had no influence over its sale."

He also noted that **most websites no longer require any of the polyfills** in the polyfill.io library — a position the expert-polyfills skill formalizes as the modern-first stance. Most sites adding `<script src="cdn.polyfill.io/...">` in 2024 were transpiling for IE11 long after IE11 stopped mattering, or pasting from a 2018 Stack Overflow answer.

This is significant: the original maintainer warned, in public, that the new owner could not be trusted, **before any malware was observed.** Sites that ignored the warning had four months to migrate; the ones still embedding `cdn.polyfill.io` on June 25, 2024 had been warned.

## What replaced it

Two clean mirrors sprung up almost immediately after the Funnull acquisition was discovered. Both are clean forks of the original open-source `polyfill-service` Rust codebase:

- **Cloudflare** — `https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js` (or `polyfill.js` unminified). Free; no signup. Cloudflare additionally offers the **auto-rewrite feature** described above: if your origin is proxied through Cloudflare and your HTML still contains `<script src="*polyfill.io*">`, Cloudflare rewrites it to its mirror in flight. Free plan = automatic, paid plan = opt-in. See [`cloudflare-cdnjs-polyfill.md`](./cloudflare-cdnjs-polyfill.md).
- **Fastly** — `https://polyfill-fastly.io/v3/polyfill.min.js` and `https://polyfill-fastly.net/v3/polyfill.min.js`. Drop-in identical API; the original polyfill-service Fastly Compute@Edge implementation is the source. Opt-in only — Fastly does not auto-rewrite. See [`fastly-polyfill-mirror.md`](./fastly-polyfill-mirror.md).

Both mirrors run code identical to what `cdn.polyfill.io` ran *before* the Funnull acquisition. Both are reputable in the sense that a major infrastructure provider stands behind them. Both are still 3rd-party JS.

## Why mirrors don't fully solve the problem

The skill's stance — "self-host, don't use mirrors" — needs justification. Here's the reasoning:

1. **Mirrors are still 3rd-party JS.** The browser executes whatever the mirror serves at request time. If the mirror is ever compromised, the same vector that hit polyfill.io hits you. Cloudflare and Fastly are far more reputable than Funnull, but reputability is not a structural defense — it's a probabilistic bet.
2. **Mirrors are still 1 round-trip per page.** Even with HTTP/2 and edge caching, a `<script>` to a 3rd-party origin adds resolve + connect + TLS time. Self-hosted polyfills travel with your bundle and add zero round trips.
3. **Mirrors are still a CDN dependency.** If the mirror's URL changes, your sites break. If the mirror introduces a paid tier or rate-limit, your sites break. Mirror operators have no SLA to your team.
4. **Mirrors don't solve the original "ship code you don't need" problem.** polyfill.io's architecture was: send the User-Agent, get back only the polyfills that browser needs. At a modern baseline (Chromium 125+, Safari 17.4+, Firefox 129+), that set is **empty for most pages**. Routing the empty set through a mirror is wasted bytes, not safety.
5. **Subresource Integrity (SRI) doesn't apply.** Because polyfill.io / its mirrors generate JS dynamically per-User-Agent, no two responses share a hash — you cannot pin a SRI hash on the `<script>` tag. Self-hosting with a fixed bundle hash + SRI is a strictly stronger posture.

> **The skill's recommendation, in priority order:**
> 1. **Don't ship a polyfill at all.** Check the feature against the baseline. If it's green at Chromium 125+, Safari 17.4+, Firefox 129+, stop polyfilling. See `../meta/the-modern-baseline.md`.
> 2. **Ponyfill at build time.** Per-feature explicit imports via `es-shims/*` or the `core-js` selective `useBuiltIns: 'usage'` mode. The polyfill ships as part of *your* bundle, with *your* hash, under *your* CSP.
> 3. **Self-host the polyfill bundle.** If you need polyfill.io's User-Agent-aware bundling, fork [`fastly/polyfill-service`](https://github.com/fastly/polyfill-service) (deprecated 2026-01-14 but still functional) and run it on your own infrastructure.
> 4. **Mirror only as last resort transitional.** Cloudflare or Fastly mirrors are an acceptable bridge for the week or month between "we noticed we're loading polyfill.io" and "we've shipped a fix" — not a destination.

## Lessons learned for the field

The polyfill.io incident generated several durable lessons. The skill encodes them as invariants:

### Lesson 1 — Domains are not maintainers

A package's identity travels with whoever holds the *domain* and *registrar credentials*, not whoever wrote the code. When a maintainer hands a project off, the new owner inherits all the trust the old owner accrued. This was the entire attack vector.

The defense is to stop trusting domains as a stable identity. Pin to specific commit hashes, ship code in your bundle, and treat any 3rd-party JS URL as renegotiable trust.

### Lesson 2 — Subresource Integrity (SRI) is necessary, not sufficient

`<script integrity="sha384-...">` would have broken the conditional-malware injection — the hash wouldn't match on the malicious response. **But** polyfill.io's whole point was per-User-Agent dynamic responses; SRI literally couldn't be used.

Lesson: if a 3rd-party service requires you to *not* use SRI, that's a structural smell, not a quirk to work around.

### Lesson 3 — "But it's a respected service" is a temporary state

polyfill.io was respected for 10 years before it was sold. Funnull was unknown to anyone outside CDN-registrar circles before the acquisition. Reputation is a moving target on a unit of years; supply-chain attacks operate on a unit of hours.

The defense is paranoid build-time bundling. Whatever code your users execute, your build server pulls into a bundle, your CI hashes, your CDN serves with SRI.

### Lesson 4 — Build-time bundling is the real fix

Every major polyfill story since has reinforced this. `npm` package compromises (event-stream 2018, ua-parser-js 2021, color.js 2022, the polyfill.io domain transfer 2024) all share the property that **the build step pulled in something the developer didn't audit at the moment they took dependency**. Lockfiles + `npm audit` + build-time bundling pulls the audit window forward.

Runtime CDN-loaded JS bypasses *all* of that. polyfill.io was the canonical worst case.

### Lesson 5 — Most polyfills shipped to modern browsers are dead weight

Andrew Betts' February 2024 statement included a quieter point: **most sites loading polyfill.io don't need any polyfills.** This is the expert-polyfills skill's foundational stance, expressed in a sentence. If a site is loading polyfill.io to get IE11 compatibility, and the site no longer supports IE11, the polyfill is *only* a security surface — there's no functional benefit to weigh against the risk.

The 100K+ sites affected almost certainly include thousands that didn't need any polyfills at all and were carrying the `<script>` tag from a years-old template.

## Migration playbook

For a site currently loading `polyfill.io`, `polyfill-fastly.io`, or `cdnjs.cloudflare.com/polyfill`:

1. **Identify which polyfills the page actually invokes.** Most often: zero. Run the site against a modern Chrome/Safari/Firefox at the baseline (`Chromium >= 125`, `Safari >= 17.4`, `Firefox >= 129`); use DevTools' coverage tool to see if any polyfilled APIs are exercised. See `../meta/decision-tree.md`.
2. **If zero are needed, delete the `<script>` tag.** Confirm the site still works. Done.
3. **If some are needed, identify the specific features.** Most likely candidates at this baseline: `Temporal`, `URLPattern` (Firefox 129–143), `Iterator helpers` (Safari 17.4–18.3), `CSS Anchor Positioning` (Safari < 26 / Firefox < 147), customizable `<select>` (Chrome 135+ only). See the `STOP polyfilling these` and `DO polyfill these` tables in [SKILL.md](../../SKILL.md).
4. **Pick a per-feature ponyfill.** `@js-temporal/polyfill`, `urlpattern-polyfill`, `es-iterator-helpers`, `@oddbird/css-anchor-positioning`. Install via npm; import explicitly; bundle. See `../runtime-polyfills/` and `../css-polyfills-and-shims/`.
5. **Or, if you genuinely need User-Agent-aware bundling** (large site, performance-critical, mixed audience): self-host a fork of [`fastly/polyfill-service`](https://github.com/fastly/polyfill-service) on your own infrastructure. Deprecated upstream but functional.
6. **Pin SRI hashes.** Anything you load via `<script>` should include `integrity="sha384-..."` and `crossorigin="anonymous"`. Anything that won't accept SRI is a smell.
7. **Add a CSP `script-src` allowlist.** The CSP would have stopped the polyfill.io malware from executing — `script-src 'self' cdn.polyfill.io` allows the original origin but not the redirect destinations the malware tried. Defense in depth.

## See also

- [`cloudflare-cdnjs-polyfill.md`](./cloudflare-cdnjs-polyfill.md) — how the Cloudflare mirror works in detail
- [`fastly-polyfill-mirror.md`](./fastly-polyfill-mirror.md) — how the Fastly mirror works in detail
- [`../anti-patterns/polyfill-io-after-attack.md`](../anti-patterns/polyfill-io-after-attack.md) — why the mirrors are still an anti-pattern
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what's actually shipped at Chromium 125+ / Safari 17.4+ / Firefox 129+
- [`../meta/decision-tree.md`](../meta/decision-tree.md) — "do I need a polyfill?" flowchart
