---
date: 2026-04-27
coverage: extended
peers:
  - ../products/vite-6.md
  - ../products/react-router-v7.md
  - ../products/astro.md
  - ../build-tools/browserslist-recipes.md
  - ../transpilation/swc-targets.md
  - ../transpilation/babel-preset-env.md
  - ../anti-patterns/preset-env-no-browserslist.md
  - ../landscape-shifts/polyfill-io-attack.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://nextjs.org/docs/architecture/supported-browsers — Architecture: Supported Browsers (canonical default browserslist + polyfill list)
  - https://nextjs.org/docs/architecture/nextjs-compiler — Next.js Compiler (SWC) reference
  - https://nextjs.org/docs/app/getting-started/server-and-client-components — Server/Client Components model
  - https://nextjs.org/blog/next-16 — Next.js 16 release announcement (October 2025) — Turbopack stable default
  - https://nextjs.org/docs/app/guides/upgrading/version-16 — Version 16 upgrade guide
  - https://nextjs.org/blog/next-12-2 — Next.js 12.2 (origin of `browsersListForSwc` experimental flag)
  - https://github.com/vercel/next.js/discussions/77768 — Why `browsersListForSwc` and `legacyBrowsers` were removed
  - https://github.com/vercel/next.js/blob/canary/packages/next-polyfill-nomodule/src/index.js — `next-polyfill-nomodule` source list
  - https://nextjs.org/docs/messages/no-unwanted-polyfillio — Next.js's own warning against polyfill.io usage
---

# Next.js 15 / 16 — polyfill posture

The most-deployed React meta-framework. Next.js 15 (October 2024) and Next.js 16 (October 2025, Turbopack stable as default) share the same browser-support model: a fixed default browserslist, an opinionated nomodule polyfill set, and SWC-driven transpilation. Babel is opt-in; almost no app needs it at this baseline.

> The TL;DR: Next.js's default browserslist is **`chrome 111, edge 111, firefox 111, safari 16.4`** — well below our Chromium 125+ / Safari 17.4+ / Firefox 129+ floor. Override it via `package.json` `"browserslist"`. There is **no `supportedBrowsers` config option** — that was a Wave-1 misread; the canonical knob is plain browserslist.

## Default browserslist (canonical)

From the [Next.js Supported Browsers reference](https://nextjs.org/docs/architecture/supported-browsers) (last updated 2026-04-23, Next 16.2.4):

```json
{
  "browserslist": ["chrome 111", "edge 111", "firefox 111", "safari 16.4"]
}
```

This is the **default if you set nothing**. Chrome 111 shipped March 2023; Safari 16.4 shipped March 2023; Firefox 111 shipped March 2023; Edge 111 shipped March 2023. The default was last bumped in this era and pegs Next.js to roughly the [Baseline Widely Available](https://web-platform-dx.github.io/web-features/) cut as of early 2024.

**Implication at our baseline**: every supported Next user has a browser ≥ 14 versions newer than Next.js's default floor. SWC will lower syntax (decorators, top-level await, etc.) that every modern engine ships natively. Override it.

## Overriding the browserslist

The official, supported override is **`package.json` `"browserslist"`** — Next.js reads it directly. From [Next.js Architecture: Supported Browsers](https://nextjs.org/docs/architecture/supported-browsers):

```json
{
  "browserslist": [
    "chrome >= 125",
    "edge >= 125",
    "firefox >= 129",
    "safari >= 17.4",
    "not dead"
  ]
}
```

This is the canonical override at the expert-polyfills baseline.

### What does NOT work

- **No `supportedBrowsers` field in `next.config.ts`.** That option does not exist. (The Wave 5 spec referenced "verify URL" — confirmed: there is no such option in current Next.js docs.) ([Next.js next.config.js reference](https://nextjs.org/docs/app/api-reference/config/next-config-js))
- **`.browserslistrc` file** historically had inconsistent honoring. As of Next.js 12+, the `package.json` form is the documented path. ([Next #12826](https://github.com/vercel/next.js/discussions/12826))
- **`experimental.browsersListForSwc` and `experimental.legacyBrowsers`** — these flags existed briefly in Next.js 12.2 and have been removed. Don't use them. ([Next #77768](https://github.com/vercel/next.js/discussions/77768))

## Polyfills Next.js injects automatically

This is the load-bearing detail most engineers miss. Per [Next.js Architecture: Supported Browsers](https://nextjs.org/docs/architecture/supported-browsers), Next ships a **nomodule polyfill bundle** containing:

- **`fetch()`** — replaces `whatwg-fetch` / `unfetch`
- **`URL`** — replaces the `url` Node.js shim
- **`Object.assign()`** — replaces `object-assign` / `object.assign` / `core-js/object/assign`

Source: [`packages/next-polyfill-nomodule/src/index.js`](https://github.com/vercel/next.js/blob/canary/packages/next-polyfill-nomodule/src/index.js).

Two important behaviors:

1. **Automatic deduplication.** If your dependencies pull in any of those packages, Next strips them from the production bundle. Single source of truth is Next's own polyfill chunk.
2. **Conditional loading.** The polyfill bundle is delivered via `<script nomodule>` and only loads in browsers without ES module support. **At our baseline, no user downloads it.**

So while Next defaults to a Safari-16.4 floor, the polyfills it ships are scoped to a Safari-9-and-below floor (nomodule). The two are decoupled. Raising your browserslist does not remove the polyfill chunk; it just means the SWC pass lowers fewer syntax features.

## What the SWC compiler handles

Next.js 12+ uses SWC by default for transformation; Babel only kicks in if a `.babelrc` is present (which disables SWC). ([Next.js Compiler](https://nextjs.org/docs/architecture/nextjs-compiler))

Out of the box, SWC handles:

- TypeScript type-stripping (no type-check; run `tsc --noEmit` in CI)
- JSX (automatic React 17+ runtime; configurable)
- Class fields, optional chaining, nullish coalescing — only lowered when target requires it
- Decorators (TypeScript legacy or 2023-11; controlled via `tsconfig.json` and `next.config.ts`'s `experimental` block)
- Production minification (replaces Terser since Next 13)

What it does **not** automatically inject:

- **`core-js`** — there is no automatic core-js inclusion in Next 14+. If your code uses `URLPattern`, `Temporal`, `Object.groupBy()`, you ship the unfilled call. See [`../runtime-polyfills/`](../runtime-polyfills/) for picking the right shim.
- **CSS lowering** — Next runs PostCSS by default. Lightning CSS is not the default in Next; you can opt in via custom config. See [`../build-tools/lightningcss-features.md`](../build-tools/lightningcss-features.md).

See [`../transpilation/swc-targets.md`](../transpilation/swc-targets.md) for the full SWC config surface.

## App Router specifics

Next.js 13+ added the App Router (now the default in Next 14+). Two distinct runtime contexts:

- **Server Components** (default, every component without `"use client"`) — render in Node.js (or the Edge runtime). **No browser polyfills needed; Node is the host.** Use Node-shaped APIs freely.
- **Client Components** (`"use client"` directive) — bundled and shipped to the browser. **Subject to your browserslist.** Polyfill posture from this file applies only to these.

The split means Server Components can call `URLPattern` (Node 23+) without thinking about Firefox 130. Client Components calling the same API need a polyfill — see [`../runtime-polyfills/urlpattern.md`](../runtime-polyfills/urlpattern.md). ([Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components))

## `next/font` and `next/image` — no polyfill concerns

Two of Next's most-used built-ins are polyfill-free:

- **`next/font`** (App Router and Pages Router) — self-hosts fonts at build time, removes external network requests. No JS polyfill needed; uses standard `@font-face`. ([Next.js Fonts](https://nextjs.org/docs/app/getting-started/images-and-fonts))
- **`next/image`** — renders a native `<img>` (since Next 13) with `sizes`/`srcset` for responsive. No polyfill; the lazy-loading is `loading="lazy"`, which is supported across our entire baseline. The previous IntersectionObserver shim was removed when Next 13 dropped Next 11/12 fallback paths. ([Next.js Image](https://nextjs.org/docs/app/getting-started/images-and-fonts))

## Custom polyfills (when you actually need one)

Per [Next.js Custom Polyfills](https://nextjs.org/docs/architecture/supported-browsers), the App Router pattern is `instrumentation-client.ts`:

```ts
// instrumentation-client.ts
import './polyfills';
```

Pages Router pattern is a top-level import in `pages/_app.tsx`. The docs also recommend conditionally loading polyfills via dynamic `import()`:

```ts
if (!('structuredClone' in globalThis)) {
  import('polyfills/structured-clone').then((mod) => {
    globalThis.structuredClone = mod.default;
  });
}
```

At our baseline this should be rare — most APIs your code uses are native. Reach for this only when targeting a feature that's actually missing (Temporal, URLPattern below Firefox 142, etc.).

## Recommended setup at our baseline

```jsonc
// package.json
{
  "name": "my-next-app",
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
// next.config.ts
import type { NextConfig } from 'next';

const config: NextConfig = {
  // Browserslist auto-discovered from package.json
  // No `supportedBrowsers` option exists; do not look for one
};

export default config;
```

If you need finer-grained SWC config (e.g. decorator version), drop a `.swcrc` next to `next.config.ts`. Don't add a `.babelrc` unless you have a hard dependency on a Babel plugin SWC can't replicate — that disables SWC entirely. See [`../transpilation/swc-targets.md`](../transpilation/swc-targets.md).

## Anti-patterns specific to Next

The five drift patterns most likely in real Next projects:

1. **No `browserslist` set in `package.json`.** Falls through to Next's `chrome 111 / safari 16.4` default. Over-lowering for our actual audience.
2. **`@vercel/next` template inheriting CRA-era browserslist.** Many teams copied `defaults` years ago and never revisited. See [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md).
3. **Adding `core-js` directly to `package.json`.** Doesn't get picked up by Next's auto-injection — you ship a duplicate copy. Either configure Babel or remove.
4. **Importing `polyfill.io` script in `_document.tsx`.** Next.js explicitly warns against this in [`/docs/messages/no-unwanted-polyfillio`](https://nextjs.org/docs/messages/no-unwanted-polyfillio). Hostile since June 2024 — see [`../landscape-shifts/polyfill-io-attack.md`](../landscape-shifts/polyfill-io-attack.md).
5. **Adding `.babelrc` to enable a single Babel plugin.** Disables SWC for the whole project. Performance loss is measurable; check whether the SWC equivalent or a Vercel-maintained plugin exists first.

## Cross-references

- [`./vite-6.md`](./vite-6.md) — Vite, the Next.js alternative for SPAs
- [`./react-router-v7.md`](./react-router-v7.md) — React Router framework mode (the Remix successor; competitor to App Router)
- [`./astro.md`](./astro.md) — Astro for content-heavy sites
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical query format
- [`../transpilation/swc-targets.md`](../transpilation/swc-targets.md) — Next.js's compiler under the hood
- [`../transpilation/babel-preset-env.md`](../transpilation/babel-preset-env.md) — opt-in path for Next, generally avoid
- [`../anti-patterns/preset-env-no-browserslist.md`](../anti-patterns/preset-env-no-browserslist.md) — what happens with no `targets` set
- [`../landscape-shifts/polyfill-io-attack.md`](../landscape-shifts/polyfill-io-attack.md) — why never reach for the CDN
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what our baseline means in features
