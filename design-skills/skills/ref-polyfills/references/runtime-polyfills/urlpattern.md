---
date: 2026-04-27
coverage: canonical
peers:
  - ../meta/the-modern-baseline.md
  - ../meta/decision-tree.md
  - ../feature-detection/ponyfill-pattern.md
primary_sources:
  - https://github.com/kenchris/urlpattern-polyfill — Reference polyfill, MIT, kenchris/Ken Christiansen
  - https://www.npmjs.com/package/urlpattern-polyfill — Latest version (10.x), downloads
  - https://github.com/denosaurs/urlpattern — Deno-friendly variant (rust-urlpattern + WASM)
  - https://urlpattern.spec.whatwg.org/ — WHATWG URL Pattern spec (now WHATWG-hosted)
  - https://developer.mozilla.org/en-US/docs/Web/API/URLPattern — MDN reference
  - https://caniuse.com/urlpattern — Browser support data
  - https://developer.chrome.com/blog/new-in-chrome-95 — Chrome 95 ship announcement (Oct 19, 2021)
  - https://developer.chrome.com/docs/web-platform/urlpattern — Chrome team's URLPattern guide
  - https://webkit.org/blog/17333/webkit-features-in-safari-26-0/ — Safari 26.0 (Sept 15, 2025) ships URLPattern
  - https://www.firefox.com/en-US/firefox/142.0/releasenotes/ — Firefox 142 (Aug 19, 2025) ships URLPattern
---

# URLPattern API — pattern-matching for URLs

## What URLPattern is

A standardized URL pattern-matching API. Replaces the regex-soup that frameworks have been shipping for routing since the dawn of single-page apps.

```js
const p = new URLPattern({ pathname: '/users/:id' });
const match = p.exec('https://example.com/users/42');
// match.pathname.groups.id === '42'
```

The syntax is familiar from `path-to-regexp` (Express, React Router, Next.js): `:named`, `*` wildcards, optional `?` segments, custom regex per segment via `(...)`. The API is structured: each URL component (`protocol`, `username`, `password`, `hostname`, `port`, `pathname`, `search`, `hash`) is matched independently.

Why it matters:

- **Service workers.** Routing inside a Service Worker is a primary use case. The Workbox router and most modern SW patterns now expect URLPattern.
- **Modern routers.** Next.js App Router, SvelteKit, React Router 7 all benefit when the underlying matcher is native instead of bundled.
- **Node.js, Deno, Bun.** `URLPattern` is available across modern runtimes — patterns are portable between server and browser.

Spec home: https://urlpattern.spec.whatwg.org/. The spec has migrated from WICG (incubation) to WHATWG (mature). MDN: https://developer.mozilla.org/en-US/docs/Web/API/URLPattern.

## Native shipping status (as of April 2026)

| Engine | Version | Date | Notes |
|---|---|---|---|
| **Chrome / Edge** | **95** | **October 19, 2021** | Long shipped. https://developer.chrome.com/blog/new-in-chrome-95. |
| **Safari** | **26.0** | **September 15, 2025** | First Apple-platform support. https://webkit.org/blog/17333/webkit-features-in-safari-26-0/. |
| **Firefox** | **142** | **August 19, 2025** | https://www.firefox.com/en-US/firefox/142.0/releasenotes/. |
| **Node.js** | **23.8** (~Feb 2025) | _native_ | Available globally without flag in recent Node versions; Deno and Bun have shipped longer. |

Per https://caniuse.com/urlpattern, URLPattern has been **Baseline Newly available since September 2025** — it works across all three major browser engines on the latest devices.

## The polyfill window at this baseline

Our baseline: **Chromium 125+ / Safari 17.4+ / Firefox 129+ (April 2024 floor)**.

| Browser | At baseline | Native URLPattern? | Polyfill needed? |
|---|---|---|---|
| Chrome 125–latest | Yes | **Yes** (since 95) | No |
| Edge 125–latest | Yes | **Yes** (since 95) | No |
| Safari 17.4 – 25.x | Yes | No (ships in 26.0) | **Yes**, but those Safari versions are only relevant if you support older Safari beyond our baseline |
| Safari 26+ | Yes | **Yes** | No |
| Firefox 129–141 | Yes | No (ships in 142) | **Yes** |
| Firefox 142+ | Yes | **Yes** | No |

**The polyfill window is Firefox 129 → 141 (~13 versions, ~9 months of releases, August 2024 → August 2025).** Safari 17.4 → 25.x technically also needs the polyfill, but Safari 26 has been out since September 2025 and our baseline is Safari 17.4, so the Safari window is older than our floor — most teams treating Safari 17.4 as the floor will have moved past it by the time they care about URLPattern.

**Practical guidance:** if you support Firefox below 142 in production, polyfill. Otherwise, ship native.

## Polyfill: `urlpattern-polyfill` (kenchris)

The reference implementation. Maintained by Ken Christiansen, who also drove the original WICG spec work.

| Field | Value |
|---|---|
| npm | https://www.npmjs.com/package/urlpattern-polyfill |
| Repository | https://github.com/kenchris/urlpattern-polyfill |
| Latest version | 10.1.0 |
| License | MIT |
| Bundle size | ~6 KB minified+gzipped (current 10.x; v9.0 trimmed ~2.5 KB / ~13% from prior versions) |
| WPT | Passes the official Web Platform Test suite for URLPattern |
| Maintenance | Active; tracks the WHATWG spec |

Notable behavior: the package's auto-applying entry point only installs `globalThis.URLPattern` if it is not already present. Side-effect-on-import is shipped as a deliberate convenience for browser bundles.

## Polyfill: `denosaurs/urlpattern` (Deno-friendly variant)

A Rust-and-WASM-backed alternative that wraps the same Rust crate (`rust-urlpattern`) Deno uses internally.

| Field | Value |
|---|---|
| Repository | https://github.com/denosaurs/urlpattern |
| Deno entry | https://deno.land/x/urlpattern |
| Bundle size | Larger than `urlpattern-polyfill` (carries a WASM blob) |
| Why pick it | Deno projects pre-stabilization; environments where you want exact byte-for-byte parity with the Deno runtime's `URLPattern` |

For browser bundles, the WASM payload is usually a deal-breaker. Stick with `urlpattern-polyfill`.

## Code examples

### Explicit-import (preferred — ponyfill style)

```js
import { URLPattern } from 'urlpattern-polyfill';

const route = new URLPattern({ pathname: '/articles/:slug' });
const match = route.exec('https://example.com/articles/hello-world');
console.log(match.pathname.groups.slug); // 'hello-world'
```

This form is a true ponyfill: it does not touch `globalThis`. Safe to use in libraries.

### Feature-detect + dynamic import (best for apps)

```js
if (!('URLPattern' in globalThis)) {
  await import('urlpattern-polyfill');
}
// URLPattern now safely usable as a global
const p = new URLPattern({ pathname: '/users/:id' });
```

Bundlers split the dynamic import into a chunk that is only fetched on browsers that need the polyfill. The cost on Chrome / modern Safari / Firefox 142+ is **zero bytes downloaded**.

### Side-effect import (convenient, but sticky)

```js
import 'urlpattern-polyfill';
// globalThis.URLPattern is now installed if it was missing
```

Acceptable in app entry points, dangerous in libraries — you do not want to mutate consumers' globals.

## When NOT to polyfill

- **Your support matrix is Chrome + Edge only.** URLPattern has shipped since Chrome 95 (October 2021); you have already had it for years.
- **You don't actually use URLPattern.** If your routing library still uses regex internally and does not call into `URLPattern`, polyfilling adds bytes for nothing. Audit your dependencies before polyfilling reflexively.
- **You only need basic `URL` parsing.** `new URL(href)` is universal. URLPattern is for *pattern matching*, not URL construction.

## Migration path off the polyfill

1. Watch the Firefox floor. Once your minimum is Firefox 142+, the polyfill is dead weight.
2. Remove the explicit import. If you used the dynamic-import + feature-detect pattern, remove the entire detection block; modern Firefox / Safari / Chrome all have it.
3. Strip the dependency from `package.json`.

URLPattern, like Temporal, lives in its own constructor — there is no prototype-method patching, no global pollution to worry about. Migration is one removed import.

## Pitfalls and gotchas

- **Spec evolution.** The spec moved from WICG to WHATWG; some early references (and a few older articles) may cite `wicg.github.io/urlpattern/`. The current canonical location is https://urlpattern.spec.whatwg.org/.
- **Same-origin shorthand.** `new URLPattern('/users/:id', 'https://example.com')` is valid (the second argument is a `baseURL`). Without a base URL, you must use the structured form (`{ pathname: '/users/:id' }`) or explicitly include the protocol.
- **Hostname patterns and dots.** `*.example.com` matches single subdomains; `**.example.com` is not part of the spec. Multi-segment subdomain matching needs explicit per-segment patterns.
- **Performance.** URLPattern compiles to optimized native matchers in browsers that ship it. The polyfill is JS — same algorithmic complexity, but slower per-match. For high-volume Service Worker routing, prefer the native path; the feature-detect-and-skip-polyfill pattern matters here.
- **Service Worker context.** The polyfill works in Service Worker contexts (the kenchris polyfill explicitly tests this). If you import the polyfill in your SW bundle and feature-detect first, you cover Firefox 129–141 SW routing without leaking the polyfill into other browsers' SWs.

## Cross-references

- Decision tree: `../meta/decision-tree.md`
- Ponyfill pattern: `../feature-detection/ponyfill-pattern.md`
- Modern baseline definition: `../meta/the-modern-baseline.md`
