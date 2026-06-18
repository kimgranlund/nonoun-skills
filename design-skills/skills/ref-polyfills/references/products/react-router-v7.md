---
date: 2026-04-27
coverage: extended
peers:
  - ../products/next-js-15.md
  - ../products/vite-6.md
  - ../products/astro.md
  - ../build-tools/vite-build-target.md
  - ../build-tools/browserslist-recipes.md
  - ../transpilation/esbuild-targets.md
  - ../runtime-polyfills/urlpattern.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://reactrouter.com/ — React Router official documentation home
  - https://reactrouter.com/start/modes — Picking a mode (Library / Framework / Data)
  - https://reactrouter.com/upgrading/v6 — Upgrading from v6 (Node 20+, React 18+ requirements)
  - https://reactrouter.com/upgrading/remix — Upgrading from Remix to React Router v7
  - https://remix.run/blog/merging-remix-and-react-router — Merging Remix and React Router (announcement)
  - https://remix.run/blog/react-router-v7 — React Router v7 release blog (December 2024)
  - https://github.com/remix-run/react-router/issues/12363 — `[Bug]: ReferenceError: TextEncoder is not defined`
  - https://github.com/remix-run/remix/discussions/10635 — Best practice for adding polyfills to support older browsers
  - https://caniuse.com/textencoder — TextEncoder/TextDecoder support tables (TextEncoderStream subset)
---

# React Router v7 — polyfill posture

The Remix successor. React Router v7 (released December 2024) merged Remix's full-stack framework into React Router as **framework mode**, alongside the existing **library mode** (the `react-router-dom` API your v6 code already used) and **data mode** (loaders + actions without the framework). Built on Vite. Inherits Vite's posture.

> The TL;DR: React Router v7 is Vite-based — same defaults, same overrides, same polyfill rules as [`./vite-6.md`](./vite-6.md). The one v7-specific note: framework-mode SSR uses `TextEncoderStream` to stream the response, native at our entire baseline. No browser polyfills needed.

## What it is

React Router v7 has three distinct modes ([Picking a mode](https://reactrouter.com/start/modes)):

| Mode | What it is | Vite required? |
|---|---|---|
| **Library mode** | The classic `react-router-dom` API — components + hooks for routing inside an existing app | No |
| **Data mode** | Library mode + loaders/actions; no SSR | No |
| **Framework mode** | Full-stack with SSR, code splitting, file-system routing, build pipeline (the Remix successor) | **Yes** |

Framework mode is the headline. It's what pulls in Vite as a hard dependency, ships with `@react-router/dev/vite` plugin, and brings the Remix-shaped ergonomics (`loader`, `action`, route modules) into React Router. ([Merging Remix and React Router](https://remix.run/blog/merging-remix-and-react-router))

If you're using v7 in **library mode** or **data mode**, this whole file collapses to: "you're a React app, polyfill posture is whatever your build tool says." Vite if you use Vite; Webpack if Webpack; Next.js if you're inside Next; etc.

The rest of this file assumes **framework mode** unless otherwise stated.

## Runtime requirements

From [Upgrading from v6](https://reactrouter.com/upgrading/v6):

- `node@20`
- `react@18`
- `react-dom@18`

No browser version is documented as a hard floor. The implicit floor is whatever Vite's `build.target` resolves to (Vite 7 defaults to `'baseline-widely-available'` ≈ Chrome 111 / Safari 16.4) — see [`./vite-6.md`](./vite-6.md).

## TextEncoderStream — the one notable browser API

The v7-specific gotcha. React Router v7's SSR streaming response wraps the rendered HTML in a `TextEncoderStream` to convert text chunks to bytes. This means the **server** runtime needs `TextEncoderStream` (Node 18+, Workers, Deno — all fine).

Some community guidance (e.g., [PostHog's React Router v7 docs](https://posthog.com/docs/libraries/react-router/react-router-v7-framework-mode)) and Stack Overflow answers note that **client-side** code paths can also reach `TextEncoderStream` in some hydration scenarios, with browser support starting at:

- **Chrome 71+** (December 2018)
- **Safari 14.1+** (April 2021)
- **Firefox 105+** (September 2022)

([caniuse: TextEncoderStream](https://developer.mozilla.org/en-US/docs/Web/API/TextEncoderStream))

**At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+), `TextEncoderStream` is shipped everywhere — by 50+ versions in Chrome, 36+ Safari minors, 24+ Firefox versions.** No polyfill is needed for any user inside our baseline.

The Wave-1 spec for this file noted "TextEncoderStream / TextDecoderStream — Chrome 71+ / Safari 14.1+ — at baseline ✓" — that lookup is correct. The only scenario where a polyfill matters is if you're *targeting below our baseline* and serving v7's framework mode to those users. Not our scope.

There's a known [issue #12363](https://github.com/remix-run/react-router/issues/12363) — `ReferenceError: TextEncoder is not defined` — but that's a server-side / test-environment problem (jsdom, vitest with `environment: 'node'` not exposing `TextEncoder` until Node 11+, which is moot now). Browser-side, no problem at baseline.

## Other browser APIs framework mode uses

A short audit of v7's runtime touchpoints:

| API | Used for | Baseline status |
|---|---|---|
| `ReadableStream` / `WritableStream` | Streaming SSR response | Long shipped at baseline (Chrome 43+ / Safari 11+ / Firefox 65+) |
| `TextEncoderStream` / `TextDecoderStream` | Stream wrapping (above) | Chrome 71+ / Safari 14.1+ / Firefox 105+ — at baseline |
| `crypto.randomUUID` | Form/route IDs in some adapters | Chrome 92+ / Safari 15.4+ / Firefox 95+ — at baseline |
| `URL`, `URLSearchParams` | Routing primitives | Long shipped |
| `fetch`, `Request`, `Response`, `Headers` | Loader/action transport | Long shipped |
| `AbortController`, `AbortSignal` | Cancellation in loaders | Long shipped |
| `structuredClone` | Some serialization paths | Chrome 98+ / Safari 15.4+ / Firefox 94+ — at baseline |

Nothing on this list requires a polyfill at our baseline. If you target below the baseline and a stream/crypto API breaks, fall back through the standard polyfill paths in [`../runtime-polyfills/`](../runtime-polyfills/).

**Not relevant**: `URLPattern`. v7 does not use `URLPattern` for its file-system routing — it has its own matcher. So you don't inherit a Firefox 129–141 gap from React Router itself. If your *own* code uses `URLPattern`, the polyfill discussion stands; see [`../runtime-polyfills/urlpattern.md`](../runtime-polyfills/urlpattern.md).

## Loaders, actions, and the server side

`loader` and `action` functions run on the server in framework mode (Node, Edge, or Workers). **No browser-polyfill concerns** for code inside them — use whatever Node 20+ offers. Many teams reach for `URLPattern`, `AsyncIterator.from`, or Node's built-in fetch without thinking; that's fine on the server, problematic if the same module accidentally ships to the client.

The dual-bundle nature of framework mode (server + client) means every shared module needs auditing for browser compatibility. The convention from Remix carries over: server-only files use `.server.ts` suffix; client-only use `.client.ts`. See [React Router framework mode docs](https://reactrouter.com/) for the full split.

## Vite plugin and config

The standard framework-mode `vite.config.ts`:

```ts
import { reactRouter } from '@react-router/dev/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [reactRouter()],
  build: {
    target: ['chrome125', 'safari17.4', 'firefox129'],
    cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
  },
});
```

Notes:

- The `reactRouter()` plugin handles the SSR/CSR build split, generates the route manifest, and wires Vite for the framework's conventions.
- `build.target` is **your responsibility** — the plugin does not set it. Vite 7's `'baseline-widely-available'` default applies if you don't override.
- `browserslist-to-esbuild` works the same here as in vanilla Vite if you want package.json as the single source of truth.

## Recommended setup at our baseline

```jsonc
// package.json
{
  "name": "my-rrv7-app",
  "browserslist": [
    "chrome >= 125",
    "edge >= 125",
    "firefox >= 129",
    "safari >= 17.4",
    "not dead"
  ]
}
```

```ts
// vite.config.ts
import { reactRouter } from '@react-router/dev/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [reactRouter()],
  build: {
    target: ['chrome125', 'safari17.4', 'firefox129'],
    cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
    minify: 'esbuild',
    sourcemap: true,
  },
});
```

No additional polyfill setup needed at this baseline. The framework's runtime requirements are all native.

## Migration from Remix v2 → React Router v7

If you're coming from Remix:

- `@remix-run/react` exports → `react-router` exports (with a few path changes; see [Upgrading from Remix](https://reactrouter.com/upgrading/remix))
- `@remix-run/node` / `@remix-run/cloudflare` → `@react-router/node` / `@react-router/cloudflare`
- The `app/entry.client.tsx` and `app/entry.server.tsx` patterns are unchanged
- Your existing browserslist (if any) carries over verbatim

The polyfill posture is also unchanged — Remix v2 ran on Vite (after the Vite plugin shipped) and v7 inherits that.

## Cross-references

- [`./next-js-15.md`](./next-js-15.md) — the SWC-default alternative for full-stack React
- [`./vite-6.md`](./vite-6.md) — the build tool R-R v7 framework mode runs on
- [`./astro.md`](./astro.md) — for content-heavy or partial-hydration shapes
- [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md) — `build.target` deep dive
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical baseline query
- [`../transpilation/esbuild-targets.md`](../transpilation/esbuild-targets.md) — what Vite hands esbuild
- [`../runtime-polyfills/urlpattern.md`](../runtime-polyfills/urlpattern.md) — for app code (not RR-v7 itself) using URLPattern
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — feature semantics of our floor
