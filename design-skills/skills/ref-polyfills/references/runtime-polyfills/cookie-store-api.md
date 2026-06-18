---
date: 2026-04-27
coverage: extended
peers:
  - ../meta/the-modern-baseline.md
  - ../meta/decision-tree.md
  - ../feature-detection/ponyfill-pattern.md
  - ../runtime-polyfills/temporal-api.md
  - ../runtime-polyfills/urlpattern.md
primary_sources:
  - https://caniuse.com/cookie-store-api — Cookie Store API browser support data
  - https://developer.mozilla.org/en-US/docs/Web/API/CookieStore — MDN CookieStore reference
  - https://developer.mozilla.org/en-US/docs/Web/API/Cookie_Store_API — MDN Cookie Store API overview
  - https://wicg.github.io/cookie-store/ — original WICG spec (now WHATWG)
  - https://github.com/whatwg/cookiestore — WHATWG specification repository
  - https://github.com/whatwg/cookiestore/issues/241 — Reduced scope to match Firefox/Safari implementations (subset agreement)
  - https://github.com/markcellus/cookie-store — markcellus/cookie-store polyfill (the one polyfill in town; partial coverage)
  - https://www.npmjs.com/package/cookie-store — npm package
  - https://github.com/mdn/browser-compat-data/issues/26301 — Firefox shipping confirmation (Nightly 138.0a1, March 2025)
  - https://webkit.org/blog/16574/webkit-features-in-safari-18-4/ — Safari 18.4 release (CookieStore landed) — March 31, 2025
  - https://chromestatus.com/feature/5658847691669504 — Chrome platform status (shipped Chrome 87)
  - https://developer.chrome.com/blog/asynchronous-access-to-http-cookies — Chrome team's Cookie Store API explainer
---

# Cookie Store API — the polyfill landscape (mostly absent)

The Cookie Store API replaces `document.cookie` with an async, structured, Service-Worker-accessible interface. Chrome shipped it in 2020. Firefox and Safari took five years to follow, and they shipped a *subset* — not the full spec. This file covers the polyfill story at our baseline, which is mostly: **don't polyfill, feature-detect, fall back to `document.cookie`**.

> The TL;DR: at our baseline (Safari 17.4+, Firefox 129+), Cookie Store is **not** universally available — Safari 18.4+ and Firefox 138+ have it; below that, no good polyfill exists. Use progressive enhancement: feature-detect `'cookieStore' in self`, and use `document.cookie` for the gap. Don't gate critical paths on Cookie Store until your floor rises.

## What the Cookie Store API is

The [Cookie Store API](https://developer.mozilla.org/en-US/docs/Web/API/Cookie_Store_API) replaces the synchronous, string-mangling `document.cookie` API with a **structured, Promise-based** interface accessible from both `Window` and Service Worker contexts.

```js
// Read all cookies
const cookies = await cookieStore.getAll();

// Get a single cookie
const session = await cookieStore.get('session');

// Set a cookie
await cookieStore.set({
  name: 'theme',
  value: 'dark',
  expires: Date.now() + 86_400_000, // 24 hours
  path: '/',
  sameSite: 'lax',
});

// Delete a cookie
await cookieStore.delete('theme');

// Listen for cookie changes
cookieStore.addEventListener('change', (event) => {
  console.log('Cookies changed:', event.changed, event.deleted);
});
```

**Why it matters:**

- **Service Worker access.** This is the killer feature. `document.cookie` is unavailable in Service Workers (no `document`); Cookie Store *is* available. SW-driven authentication, server-driven session refresh, and offline-aware cookie sync all benefit.
- **Async by design.** Setting / deleting cookies is non-blocking. Real Cookie Store calls cannot block the main thread the way `document.cookie = '...'` synchronously can.
- **Structured fields.** No more parsing `"name=value; expires=Wed, 09 Jun 2026 ...; path=/; SameSite=Lax"` strings. The API takes and returns objects.

The spec moved from **WICG** (incubation, [`wicg.github.io/cookie-store/`](https://wicg.github.io/cookie-store/)) to **WHATWG** ([github.com/whatwg/cookiestore](https://github.com/whatwg/cookiestore)) in 2024.

## Native shipping status (as of April 2026)

| Engine | Version | Date | Coverage |
|---|---|---|---|
| **Chrome / Edge** | **87** | **November 17, 2020** | Full spec — `cookieStore`, `CookieStoreManager`, `ServiceWorkerRegistration.cookies`, change events |
| **Safari** | **18.4** | **March 31, 2025** | Subset — `window.cookieStore` and SW `cookieStore`; **no** `CookieStoreManager`, **no** `ServiceWorkerRegistration.cookies` |
| **Firefox** | **138** | **April 29, 2025** (per [MDN BCD issue #26301](https://github.com/mdn/browser-compat-data/issues/26301)) | Subset — same Firefox-Safari agreed subset; no `CookieStoreManager`, no SW registration cookie subscription |

Chrome shipped it long-ago and Chromium-based browsers (Edge, Opera, Brave) inherited support. Firefox and Safari **agreed on a reduced scope** ([whatwg/cookiestore#241](https://github.com/whatwg/cookiestore/issues/241)) that mirrors the API surface of `document.cookie`:

- ✅ `cookieStore.get()`, `getAll()`, `set()`, `delete()` — implemented in Firefox / Safari.
- ✅ `cookieStore.addEventListener('change', ...)` — implemented in Firefox / Safari (when in a context with cookieStore present).
- ❌ `CookieStoreManager` — **not implemented** in Firefox or Safari.
- ❌ `ServiceWorkerRegistration.cookies` (the subscription manager) — **not implemented** in Firefox or Safari.

The subscription manager is what would let a Service Worker say "wake me up whenever the `session` cookie changes." Chrome implements this; Firefox and Safari decided not to. If you depend on it, you're Chrome-only.

## Verdict at our baseline

Our baseline: **Chromium 125+ / Safari 17.4+ / Firefox 129+**.

| Browser at baseline | Native CookieStore? | What works |
|---|---|---|
| Chrome 125+ | **Yes** (since 87) | Full spec — including `CookieStoreManager` |
| Edge 125+ | **Yes** (since 87) | Full spec |
| Safari 17.4 – 18.3 | **No** | Need fallback |
| Safari 18.4+ | **Yes** (subset) | `cookieStore.get/set/delete/addEventListener` only |
| Firefox 129 – 137 | **No** | Need fallback |
| Firefox 138+ | **Yes** (subset) | `cookieStore.get/set/delete/addEventListener` only |

**The polyfill window:**
- **Safari 17.4 → 18.3** (~1 year of versions, March 2024 → March 2025).
- **Firefox 129 → 137** (~9 versions, ~9 months, August 2024 → April 2025).

Cookie Store is **NOT at our baseline** in the sense of "universally native at our floor." It's polyfill-window territory.

## The polyfill landscape — mostly empty

There is **no production-grade polyfill** that covers the full Cookie Store API for browsers that don't ship it. The reason is structural: cookies are an HTTP/document-managed resource, and the Cookie Store API exposes capabilities (Service-Worker-context access, granular subscription) that **`document.cookie` cannot replicate**. A polyfill can mirror the *shape* of the API, but not the *Service-Worker-context* coverage.

The packages that exist:

### `cookie-store` (markcellus)

The closest thing to a Cookie Store polyfill.

| Field | Value |
|---|---|
| Repository | https://github.com/markcellus/cookie-store |
| npm | https://www.npmjs.com/package/cookie-store |
| License | MIT |
| Maintainer | Mark Kellus (single maintainer) |
| Coverage | `Window.cookieStore` only — uses `document.cookie` under the hood |
| Service Worker | **Not covered** — the polyfill cannot synthesize SW cookie access from `document.cookie` because SWs have no `document` |
| `CookieStoreManager` | **Not implemented** (per [the project's own README](https://github.com/markcellus/cookie-store)) |
| Cookie change events | Implemented via polling `document.cookie`; real-time notification is approximate |
| Bundle size | ~3 KB minified+gzipped |

This polyfill is **acceptable for `Window`-scope cookie access** in browsers that don't natively support Cookie Store. It is **not acceptable for Service Worker cookie access** — the polyfill simply cannot help there, and Service Worker code that depends on Cookie Store will throw on Safari 17.4–18.3 and Firefox 129–137 regardless of whether you import the polyfill.

Single-maintainer dependency note: the package is small and stable, but if Cookie Store coverage is critical to your product, audit the dependency before relying on it. See [`../landscape-shifts/core-js-funding-status.md`](../landscape-shifts/core-js-funding-status.md) for an analogue on single-maintainer-polyfill risk.

### `cookie-store-polyfill` (npm)

A separate, much smaller package on npm. Less maintained than `markcellus/cookie-store`. Generally redundant; if you're going to polyfill, use `cookie-store`.

### Conclusion: there is no "use Cookie Store everywhere" polyfill

If Cookie Store API is in your code, the practical answer at our baseline is **progressive enhancement**, not "import a polyfill that fixes it everywhere."

## The recommended pattern: progressive enhancement

```js
// Detect first; use the right primitive for the runtime.
function getCookie(name) {
  if ('cookieStore' in self) {
    return self.cookieStore.get(name).then((c) => c?.value ?? null);
  }
  // Fallback: parse document.cookie (sync, but wrapped in a Promise for API parity)
  return Promise.resolve(parseCookieString(document.cookie, name));
}

function setCookie(name, value, options = {}) {
  if ('cookieStore' in self) {
    return self.cookieStore.set({ name, value, ...options });
  }
  document.cookie = serializeCookie(name, value, options);
  return Promise.resolve();
}

function parseCookieString(cookieHeader, name) {
  for (const part of cookieHeader.split('; ')) {
    const [k, ...v] = part.split('=');
    if (k === name) return decodeURIComponent(v.join('='));
  }
  return null;
}

function serializeCookie(name, value, options) {
  let s = `${name}=${encodeURIComponent(value)}`;
  if (options.expires) s += `; expires=${new Date(options.expires).toUTCString()}`;
  if (options.path) s += `; path=${options.path}`;
  if (options.sameSite) s += `; SameSite=${options.sameSite}`;
  if (options.secure) s += `; Secure`;
  return s;
}
```

This is the **Window-scope** pattern. For **Service Workers**, there's no fallback — if you need Cookie Store API in an SW and you support browsers below the floors above, you have no path. The recommendation is to **postpone Service Worker cookie work** until your floors rise, or **route SW-cookie operations through `postMessage` to the Window context** where `document.cookie` is available.

A more elaborate pattern using a small wrapper:

```js
// cookies.js
class CookieAdapter {
  constructor() {
    this.native = 'cookieStore' in globalThis;
  }
  async get(name) {
    if (this.native) {
      const c = await globalThis.cookieStore.get(name);
      return c?.value ?? null;
    }
    if (typeof document !== 'undefined') {
      return parseCookieString(document.cookie, name);
    }
    throw new Error('No cookie access available in this context (likely a Service Worker on a non-supporting browser)');
  }
  async set(name, value, options = {}) {
    if (this.native) {
      return globalThis.cookieStore.set({ name, value, ...options });
    }
    if (typeof document !== 'undefined') {
      document.cookie = serializeCookie(name, value, options);
      return;
    }
    throw new Error('No cookie write available in this context');
  }
  async delete(name) {
    if (this.native) {
      return globalThis.cookieStore.delete(name);
    }
    if (typeof document !== 'undefined') {
      document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
      return;
    }
    throw new Error('No cookie delete available in this context');
  }
}
```

The throw-on-SW-without-CookieStore is the honest fail mode. Better to fail loudly in development than to silently degrade in production.

## Change events — the partial story

Cookie Store's `change` event lets you react to cookies being set or deleted by *other* code (e.g., another tab, the browser's network stack). On the native API:

```js
cookieStore.addEventListener('change', (event) => {
  for (const c of event.changed) console.log('Set:', c.name, c.value);
  for (const c of event.deleted) console.log('Deleted:', c.name);
});
```

There is no `document.cookie` equivalent. If you need cross-tab cookie synchronization on browsers without native Cookie Store, the practical alternatives are:

- **`storage` event** — only fires for `localStorage`, not cookies.
- **`BroadcastChannel`** — works, but you have to manually broadcast cookie changes from the writer side.
- **Polling** — read `document.cookie` periodically; compare against a snapshot. Pragmatic but wasteful.

The `markcellus/cookie-store` polyfill uses polling internally for its `change` event approximation. Acceptable for low-frequency UX updates; not acceptable for security-critical session-state synchronization.

## Critical-path advisory

**Don't gate critical user paths on Cookie Store API at our baseline.** Concretely:

- Authentication / login flows that must work on Safari 17.4 → 18.3 should not depend on Cookie Store.
- Service Worker session-refresh logic that must work on Firefox 129 → 137 has no path.
- Service-Worker-driven offline mode that needs to read auth cookies will fail on Firefox 129 → 137 and Safari 17.4 → 18.3.

If your product needs SW cookie access and you must support these versions, the architectural answer is to **defer the cookie operation to the Window context** via `postMessage`:

```js
// In the Service Worker
self.addEventListener('message', async (event) => {
  if (event.data.type === 'GET_AUTH_TOKEN' && 'cookieStore' in self) {
    const token = await self.cookieStore.get('auth');
    event.source?.postMessage({ type: 'AUTH_TOKEN', value: token?.value });
  }
});
```

```js
// In the Window
const sw = await navigator.serviceWorker.ready;
sw.active?.postMessage({ type: 'GET_AUTH_TOKEN' });
```

This works on all browsers — the SW asks the page; the page reads `document.cookie` if Cookie Store isn't available. Operationally awkward but the only universal answer.

## Migration path — when can the polyfill code go?

Watch the floors:

- When your minimum is **Safari 18.4+ AND Firefox 138+**, native Cookie Store is universally available (in the subset both ship).
- Remove the feature-detect; replace with direct `cookieStore` usage.
- For full-spec Cookie Store (including `CookieStoreManager`), your floor needs to be **Chrome-only or Chromium-only**.

Realistically, given Safari 18.4 (March 2025) and Firefox 138 (April 2025), most products that maintain a 12-month support window will have Cookie Store as universally-available by mid-2026 — *if* they keep their floors moving.

## Pitfalls and gotchas

- **Cookie Store ≠ `document.cookie` parity.** Cookie Store doesn't expose `HttpOnly` cookies (they're invisible to JS by spec). `document.cookie` doesn't either, but the failure mode differs — Cookie Store returns `undefined`; `document.cookie` returns the cookie string with `HttpOnly` cookies omitted. Don't assume "if I don't see it in `cookieStore.get()`, it doesn't exist."
- **Safari ITP cookie-lifetime caps.** Safari's [Intelligent Tracking Prevention](https://webkit.org/tracking-prevention/) caps JavaScript-set cookies to **7 days** (since 2019), and as of Safari 16.4, even server-set cookies are 7-day-capped under certain conditions. This applies regardless of whether you use Cookie Store or `document.cookie`. Plan your auth/session strategy around this — long-lived JS-set cookies on Safari are a pretender.
- **Subset confusion.** Documentation, tutorials, and Stack Overflow answers written when only Chrome shipped Cookie Store assume the full spec. The Firefox/Safari subset doesn't have `CookieStoreManager`. Code that does `await registration.cookies.subscribe(...)` will throw on Firefox/Safari and look broken to a developer who copy-pasted from a Chrome-era guide.
- **Spec moved from WICG to WHATWG.** Older references at `wicg.github.io/cookie-store/` are mostly accurate but the canonical source is now https://github.com/whatwg/cookiestore.
- **The `partitioned` (CHIPS) attribute** is a separate, partly-orthogonal feature. Cookie Store can read/write `partitioned: true` cookies on browsers that support both — but CHIPS itself has its own browser-support story (Chrome 114+, Safari 18.4+ opt-in, Firefox not yet).

## Cross-references

- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what the baseline includes natively (Cookie Store doesn't qualify).
- [`../meta/decision-tree.md`](../meta/decision-tree.md) — "Do I need a polyfill?" — Cookie Store routes to "feature-detect, no good polyfill."
- [`../feature-detection/ponyfill-pattern.md`](../feature-detection/ponyfill-pattern.md) — explicit-import patterns; less relevant here since `markcellus/cookie-store` does mutate the global.
- [`../runtime-polyfills/temporal-api.md`](../runtime-polyfills/temporal-api.md), [`../runtime-polyfills/urlpattern.md`](../runtime-polyfills/urlpattern.md) — siblings with cleaner polyfill stories (clean ponyfill imports work).
