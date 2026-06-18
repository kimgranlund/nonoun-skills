---
date: 2026-04-27
coverage: extended
peers:
  - ../products/vite-6.md
  - ../products/sveltekit.md
  - ../products/solidstart.md
  - ../build-tools/vite-build-target.md
  - ../build-tools/browserslist-recipes.md
  - ../build-tools/lightningcss-features.md
  - ../meta/the-modern-baseline.md
  - ../anti-patterns/target-es5-modern.md
primary_sources:
  - https://nuxt.com/blog/v4 — Nuxt 4 announcement (July 2025)
  - https://nuxt.com/blog/roadmap-v4 — roadmap to v4
  - https://nuxt.com/docs/4.x/guide/concepts/server-engine — Nitro server engine docs
  - https://nuxt.com/docs/4.x/api/nuxt-config — nuxt.config reference
  - https://nitro.build/config — Nitro configuration
  - https://nitro.build/blog/v3-beta — Nitro v3 beta announcement
  - https://endoflife.date/nuxt — Nuxt EOL dates
  - https://github.com/nuxt/nuxt/issues/20065 — exposing Vite build.target through nuxt.config
---

# Nuxt — polyfill posture at the modern baseline

Nuxt 4 is Vue 3 + Vite + Nitro. Like SvelteKit, the polyfill story is downstream of Vite — see [`./vite-6.md`](./vite-6.md) and [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md). Vue 3 is small, modern, and assumes `Proxy`. Nitro handles server adapters; server code doesn't care about browser polyfills. The only knob that matters at our baseline is `nuxt.config.ts` `vite.build.target`.

> The TL;DR: Nuxt 4 ships nothing you need to polyfill. Set `vite.build.target` in `nuxt.config.ts` to the canonical baseline trio. Don't bring `core-js`. Vue 3 + Nitro do the rest.

## What ships today

| Component | Current major | Released | Notes |
|---|---|---|---|
| **Nuxt** | **4.x** | July 15, 2025 | Stable; Nuxt 4.4.2 latest as of March 2026 |
| **Vue** | **3.x** | September 2020 | Composition API, Proxy reactivity, native Suspense + Teleport |
| **Vite** | 6.x or 7.x | underlying | Project's choice; Nuxt follows Vite's target story |
| **Nitro** | **2.x** | server engine | Nitro v3 beta available; will power Nuxt 5 |

[Nuxt 4](https://nuxt.com/blog/v4) shipped July 15, 2025 after RC on July 8, 2025. Headline changes: new `app/` directory layout, smarter `useAsyncData` / `useFetch`, `shallowRef` data by default, improved Suspense lifecycle. None of those affect polyfill posture. **Vue 3 is the runtime, has been since 2020, and assumes engines that ship `Proxy`** — a hard floor that's well below our baseline.

[Nuxt 3 EOL is July 31, 2026](https://endoflife.date/nuxt); maintenance backports stop January 2026. New projects should start on Nuxt 4.

## Build target — the load-bearing knob

Nuxt's build target is configured via `vite.build.target` in `nuxt.config.ts`:

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  vite: {
    build: {
      target: ['chrome125', 'safari17.4', 'firefox129'],
      cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
    },
  },
});
```

This routes through Nuxt's Vite integration to esbuild and Lightning CSS exactly as a plain Vite project would — see [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md) for the full discussion. Historical note: [issue nuxt/nuxt#20065](https://github.com/nuxt/nuxt/issues/20065) tracked some early Nuxt-3 cases where `vite.build.target` didn't fully propagate to Nitro's server build. By Nuxt 4 the propagation is solid for the **client bundle**; the server bundle has its own preset (Nitro), discussed below.

If you'd rather drive both from `.browserslistrc`, the [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) canonical query applies. Lightning CSS will read it for `cssTarget`. The duplication for esbuild's `target` (Vite quirk) is unavoidable — same as every other Vite-based meta-framework.

## Vue 3's polyfill posture

Vue 3 (the rendering layer) ships:

- **`Proxy`-based reactivity** — assumes `Proxy` is available. Native everywhere at our baseline (universal since Chrome 49, Firefox 18, Safari 10).
- **`<Suspense>` and `<Teleport>`** — both are Vue 3 components, **not browser features**. They render to plain DOM. No polyfill needed.
- **`<script setup>` + Composition API** — compile-time syntax; no runtime polyfill.

Vue 3's runtime is roughly 16KB minified + gzipped. It uses standard DOM APIs — `document.createElement`, `addEventListener`, `MutationObserver` for nested transitions, `Proxy` for reactivity. Every API is universal at our baseline. **There is no `core-js` injection step in the Nuxt build pipeline.**

Note: do not confuse Vue's `<Suspense>` (a renderer component for managing async children) with React's `<Suspense>` (also a renderer component). Both predate any standardized browser primitive named "suspense" — there isn't one.

## Nitro — server engine, not a browser concern

[Nitro](https://nitro.build/) is Nuxt's server engine. It builds the server side of a Nuxt app and supports a wide preset library — Node, Deno, Bun, Cloudflare Workers, Vercel, Netlify, AWS Lambda, Edge runtimes, static SSG, and more. Each preset emits the right bundle format for its runtime.

Nitro presets (representative — there are 25+):

| Preset | Target runtime | Polyfill notes |
|---|---|---|
| `node` / `node-server` | Node 18+ | Native fetch, web streams; no browser polyfills |
| `cloudflare` / `cloudflare-pages` | Cloudflare Workers | Web-standard APIs (fetch, streams) — close to browser |
| `vercel` / `vercel-edge` | Vercel Node + Edge | Provider runtime |
| `netlify` / `netlify-edge` | Netlify Functions + Edge | Provider runtime |
| `bun` | Bun | Web-standard APIs |
| `deno-deploy` | Deno Deploy | Web-standard APIs |
| `aws-lambda` | AWS Lambda | Node runtime |
| `static` | Static SSG (no server) | Pure HTML output; client bundle is the only concern |

**Nitro server code never runs in a browser.** The `target` of `vite.build.target` does not apply to server output. Nitro picks its own ECMAScript level per preset (typically `esnext` because Node 22+ implements all of ES2024).

[Nitro v3](https://nitro.build/blog/v3-beta) is in public beta as of early 2026 — built on Rolldown, Vite 8 (when stable), and the Vite Environment API. It will power Nuxt 5. At our authoring date Nuxt 4 ships Nitro v2.

## What Nuxt transpiles automatically

Out of the box, Nuxt (via Vite + esbuild + Nitro) handles:

- **TypeScript** — esbuild strips types in the client bundle; Nitro uses unjs/unbuild for the server bundle.
- **Vue SFC components** — `.vue` files compiled by `@vue/compiler-sfc`; output is JS calling Vue's runtime.
- **CSS modules and `<style scoped>`** — scoped per component via Vue's compiler; processed via Lightning CSS or PostCSS.
- **Auto-imports** — Nuxt's signature feature; `defineNuxtConfig`, `useFetch`, `useAsyncData`, etc. injected without explicit imports.
- **Hybrid rendering** — per-route SSR / SSG / SPA / ISR via `routeRules` in `nuxt.config.ts`.
- **Asset imports + dynamic imports** — Vite-standard.
- **Server vs browser code split** — `~/server/` directory excluded from client bundle.

## What Nuxt does NOT polyfill

- **Runtime JS APIs** — same caveat as Vite. `URLPattern`, `Temporal`, `Object.groupBy` ship as authored.
- **CSS runtime shims** — anchor positioning, scroll-driven animations, `@scope` are platform features. Lightning CSS lowers what it can; the rest is your responsibility.
- **`core-js`** — there is no automatic injection; no `useBuiltIns: 'usage'` equivalent.
- **Legacy bundle** — Nuxt 4 has no equivalent of `@vitejs/plugin-legacy`. Don't add one at this baseline.

## Vue ecosystem assumes Baseline 2024+

Vue 3.4+ (released December 2023) and the broader Vue ecosystem (Pinia, VueUse, Vue Router 4) assume modern engines. VueUse in particular ships composables that touch every modern web API — `useIntersectionObserver`, `useResizeObserver`, `useElementVisibility`, `useShare`, `useWebShare`, `useClipboard`. **None of these come with polyfills bundled.** They feature-detect and no-op gracefully on unsupported browsers, but at our baseline every API they wrap is native.

## Recommended setup at our baseline

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  devtools: { enabled: true },

  vite: {
    build: {
      target: ['chrome125', 'safari17.4', 'firefox129'],
      cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
      sourcemap: true,
    },
  },

  // Nitro picks its own server preset based on deploy target;
  // override via nitro: { preset: 'cloudflare' } if needed
});
```

```jsonc
// package.json — paired with the canonical browserslist
{
  "browserslist": [
    "chrome >= 125",
    "firefox >= 129",
    "safari >= 17.4",
    "not dead"
  ]
}
```

The duplication between `vite.build.target` and `browserslist` is the same Vite quirk discussed in [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md). Optionally bridge with [`browserslist-to-esbuild`](https://github.com/marcofugaro/browserslist-to-esbuild).

## Common Nuxt polyfill mistakes (the audit checklist)

The four patterns most likely to appear in real projects:

1. **No `vite.build.target` set at all.** Project inherits Vite's default — for Vite 5/6 that's `'modules'` (Safari 14 floor); for Vite 7 it's `'baseline-widely-available'` (Safari 16.4 floor). Both over-lower at our baseline.
2. **`@nuxtjs/legacy-bundle` or hand-rolled legacy build added "for compatibility."** Strip it unless your audience genuinely includes pre-Safari 14. Doubles bundle output and defeats native fast paths. See [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md).
3. **`URLPattern` used in custom server middleware without polyfill.** Nitro server code targets Node 18+ which got native URLPattern in Node 23.8 — older Node LTS lines lack it. Either upgrade Node or use [`urlpattern-polyfill`](../runtime-polyfills/urlpattern.md).
4. **Vue 2 lock-in via `@vue/compat`.** `@vue/compat` ships Vue 3 with Vue 2 compatibility shims; it's heavier and has its own polyfill assumptions. Migrate fully to Vue 3 idioms before this baseline becomes painful.

## Cross-references

- [`./vite-6.md`](./vite-6.md) — the underlying build tool; Nuxt inherits its target story.
- [`./sveltekit.md`](./sveltekit.md), [`./solidstart.md`](./solidstart.md) — sister Vite-based meta-frameworks with similar postures.
- [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md) — `vite.build.target` deep dive.
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical browserslist queries.
- [`../build-tools/lightningcss-features.md`](../build-tools/lightningcss-features.md) — what Lightning CSS lowers under Nuxt's CSS pipeline.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what the baseline floor means in features.
- [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) — why over-broad targets hurt at this baseline.
