---
date: 2026-04-27
coverage: extended
peers:
  - ../products/next-js-15.md
  - ../products/vite-6.md
  - ../products/react-router-v7.md
  - ../build-tools/vite-build-target.md
  - ../build-tools/lightningcss-features.md
  - ../build-tools/browserslist-recipes.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://docs.astro.build/en/concepts/islands/ — Islands architecture (canonical concept)
  - https://docs.astro.build/en/reference/configuration-reference/ — Configuration Reference (vite.build.target passthrough)
  - https://docs.astro.build/en/reference/directives-reference/ — Template / client directives reference
  - https://docs.astro.build/en/guides/framework-components/ — Front-end frameworks integration guide
  - https://docs.astro.build/en/guides/upgrade-to/v6/ — Upgrade to Astro v6 (Vite 7 alignment)
  - https://astro.build/blog/astro-5/ — Astro 5.0 (December 2024) release announcement
  - https://docs.astro.build/en/guides/integrations-guide/react/ — React integration
  - https://docs.astro.build/en/guides/integrations-guide/svelte/ — Svelte integration
  - https://docs.astro.build/en/guides/integrations-guide/solid-js/ — SolidJS integration
---

# Astro — polyfill posture

Islands architecture; static-by-default with selective hydration. Astro 5 (December 2024) and Astro 6 (built on Vite 7's Environment API) are the current generations. Vite under the hood — same default-target situation as everywhere else, with one twist: most Astro pages have **no client-side JS at all**, so polyfill questions only apply to the islands you explicitly hydrate.

> The TL;DR: Astro renders to static HTML+CSS by default; static pages have **no polyfill concerns**. Interactive islands inherit Vite's polyfill posture (which is "none — bring your own"), so their floor is whatever your `vite.build.target` resolves to. Override Vite 7's `'baseline-widely-available'` default for our baseline.

## Islands architecture, briefly

From the [Astro Islands docs](https://docs.astro.build/en/concepts/islands/): *"An 'island' refers to any interactive UI component on the page. Think of an island as an interactive widget floating in a sea of otherwise static, lightweight, server-rendered HTML."*

The key implication for polyfills: a page with no interactive islands ships **zero JavaScript** to the browser. There's nothing to polyfill, nothing to lower, nothing to break. The polyfill posture only matters for the islands.

Hydration is opt-in via [client directives](https://docs.astro.build/en/reference/directives-reference/):

| Directive | Behavior |
|---|---|
| (none) | Component server-renders to HTML; no JS shipped |
| `client:load` | Hydrate on initial page load |
| `client:idle` | Hydrate on `requestIdleCallback` (falls back to `load` event) |
| `client:visible` | Hydrate when intersecting viewport (uses `IntersectionObserver`) |
| `client:media={query}` | Hydrate when CSS media query matches |
| `client:only={framework}` | Skip server render entirely; render only on client |

`requestIdleCallback`, `IntersectionObserver`, and matchMedia — the three browser APIs Astro's directive runtime uses — are **all native at our entire baseline**. No polyfill needed.

## Vite under the hood

Astro is a Vite-based build tool. From the [Configuration Reference](https://docs.astro.build/en/reference/configuration-reference/), Vite options pass through under the `vite` key:

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';

export default defineConfig({
  vite: {
    build: {
      target: ['chrome125', 'safari17.4', 'firefox129'],
      cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
    },
  },
});
```

This applies to the islands' bundles and to any client-side JS Astro emits.

**Default target inheritance**:

- **Astro 5** (December 2024) — built on Vite 6; default `build.target` is `'modules'` unless overridden.
- **Astro 6** (built on Vite 7's Environment API) — inherits Vite 7's `'baseline-widely-available'` default → `['chrome111', 'edge111', 'firefox114', 'safari16.4']`. Older than our floor; override.

Per [Upgrade to Astro v6](https://docs.astro.build/en/guides/upgrade-to/v6/), the major change for v6 is the move to Vite's Environment API and Vite 7. The `vite.build.target` config surface is unchanged.

## Per-island, per-framework polyfill story

Astro supports multiple JS frameworks in the same page via [official integrations](https://docs.astro.build/en/guides/framework-components/):

- `@astrojs/react`
- `@astrojs/preact`
- `@astrojs/svelte`
- `@astrojs/vue`
- `@astrojs/solid-js`
- `@astrojs/alpinejs`

Each integration emits a small runtime per framework, hydrated only on the islands using that framework. **None of them inject polyfills automatically.** The polyfill posture for each island is whatever the framework + Vite produce.

For example: a React island in an Astro page has the same polyfill needs as the same component in a vanilla Vite + React app. If your code uses `URLPattern`, you ship the unfilled call; the framework doesn't fix it for you. See [`../runtime-polyfills/`](../runtime-polyfills/) for what to add.

If two islands use the same framework (e.g., two React components on the same page), the framework runtime is bundled once and shared.

## What Astro doesn't polyfill

The list, mirroring Vite's:

- **No core-js injection.** Astro inherits Vite's "syntax transforms only" posture.
- **No CSS-feature runtime shimming.** Lightning CSS handles build-time lowering; runtime CSS polyfills are your responsibility.
- **No automatic IntersectionObserver shim.** Astro uses it for `client:visible`. Our baseline ships it natively; if you genuinely target below the floor, that directive degrades to "always hydrate" (because the polyfill isn't there).
- **No View Transitions polyfill.** Astro's `<ClientRouter />` (and in v5+ the page-transitions API) uses native View Transitions where available; you can opt out with `transition:animate="none"`. See [`../css-polyfills-and-shims/view-transitions.md`](../css-polyfills-and-shims/view-transitions.md).

## Scripts and `<script>` tags

Astro's `<script>` tags get bundled and processed by Vite, *unless* you opt out with `is:inline`. The bundled scripts default to `defer` ([Astro docs](https://docs.astro.build/en/guides/client-side-scripts/)) — no FOUC concerns from script-loading order, no `async`/`defer` debate. Your responsibility is just feature support.

If you write a top-level `.astro` file with a `<script>` block:

```astro
---
// frontmatter (server-side)
---

<script>
  // bundled, processed by Vite, deferred by default
  import { somethingFromAModule } from './lib.ts';
</script>
```

…the script is subject to your `vite.build.target`. Below baseline ⇒ esbuild lowers; at our baseline ⇒ ships as-is.

## Recommended setup at our baseline

```js
// astro.config.mjs
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

export default defineConfig({
  integrations: [react()],
  vite: {
    build: {
      target: ['chrome125', 'safari17.4', 'firefox129'],
      cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
      minify: 'esbuild',
      cssMinify: 'lightningcss',
    },
  },
});
```

```jsonc
// package.json
{
  "browserslist": [
    "chrome >= 125",
    "firefox >= 129",
    "safari >= 17.4",
    "not dead"
  ]
}
```

For static-only Astro sites (no `client:*` directives anywhere), the `vite.build.target` config is essentially academic — there's no client JS to lower. But it's cheap to set, and protects against the moment you add the first interactive island.

## Server islands (Astro 5+)

Astro 5 introduced **server islands** — components that re-render on the server, separately from the rest of the page, after initial paint. They use a small client-side runtime to fetch the rendered HTML and slot it in.

The runtime uses `fetch` (long shipped at baseline) and standard DOM APIs. No new polyfill obligations. ([Server Islands docs](https://docs.astro.build/en/guides/server-islands/))

## When Astro is the wrong choice

Two scenarios where you'd reach for Next.js or React Router v7 instead:

1. **App-shaped routing** with rich data dependencies, optimistic updates, and deep nested layouts. Astro's content-first model is great for marketing/docs/blogs; less great for Linear-shaped applications.
2. **Need streaming SSR with React Server Components.** Astro doesn't expose RSC. If RSC is a hard requirement, Next.js is the answer.

For everything content-heavy — docs sites, marketing pages, blogs, light-dynamic sites — Astro is the sharpest tool, and the polyfill posture is the simplest of the four products in this axis (because most pages have no JS at all).

## Cross-references

- [`./next-js-15.md`](./next-js-15.md) — the App Router alternative for app-shaped sites
- [`./vite-6.md`](./vite-6.md) — the build tool Astro runs on
- [`./react-router-v7.md`](./react-router-v7.md) — the SSR-React alternative
- [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md) — `vite.build.target` deep dive
- [`../build-tools/lightningcss-features.md`](../build-tools/lightningcss-features.md) — Lightning CSS in Astro's CSS pipeline
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical baseline query
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what our floor means in features
