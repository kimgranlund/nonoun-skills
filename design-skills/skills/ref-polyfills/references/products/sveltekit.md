---
date: 2026-04-27
coverage: extended
peers:
  - ../products/vite-6.md
  - ../products/nuxt.md
  - ../products/solidstart.md
  - ../build-tools/vite-build-target.md
  - ../build-tools/browserslist-recipes.md
  - ../build-tools/lightningcss-features.md
  - ../meta/the-modern-baseline.md
  - ../anti-patterns/target-es5-modern.md
primary_sources:
  - https://svelte.dev/blog/sveltekit-2 — SvelteKit 2 announcement (January 2024)
  - https://svelte.dev/blog/svelte-5-is-alive — Svelte 5 stable release (October 19, 2024)
  - https://svelte.dev/docs/kit/adapters — official adapter list and configuration
  - https://svelte.dev/docs/kit/adapter-cloudflare — Cloudflare adapter docs
  - https://svelte.dev/docs/kit/migrating-to-sveltekit-2 — SvelteKit 2 migration guide
  - https://kit.svelte.dev/docs/service-workers — built-in service worker support
  - https://github.com/sveltejs/kit/releases — SvelteKit release log
  - https://vite-pwa-org.netlify.app/frameworks/sveltekit — Vite PWA + SvelteKit recipe
---

# SvelteKit — polyfill posture at the modern baseline

SvelteKit is Vite-based — its entire build target story is downstream of [`./vite-6.md`](./vite-6.md) and [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md). Svelte's compiler emits a minimal runtime, so the React-tier polyfill discussion (preset-env, core-js entry imports, plugin-legacy) doesn't really apply. The only knobs that matter at our baseline are `vite.build.target`, the adapter, and the optional service worker.

> The TL;DR: SvelteKit ships almost nothing you need to polyfill. Set `build.target` to the canonical baseline trio in `svelte.config.js`, pick an adapter, don't bring `core-js`. That's the whole story.

## What ships today

| Component | Current major | Released | Notes |
|---|---|---|---|
| **SvelteKit** | **2.x** | January 2024 | Stable; SvelteKit 2.12 added `$app/state` (runes-based) |
| **Svelte** | **5.x** | October 19, 2024 | Runes-based reactivity; SvelteKit 2 supports both Svelte 4 and 5 |
| **Vite** | 6.x or 7.x | underlying | Project's choice; SvelteKit follows Vite's target story |

[Svelte 5](https://svelte.dev/blog/svelte-5-is-alive) shipped at Svelte Summit Fall 2024 with a new reactivity primitive surface — `$state`, `$derived`, `$effect`, `$props` — replacing Svelte 4's compiler-detected reactive declarations. The compiler still emits minimal runtime per component; **no polyfill posture changed in the 4 → 5 transition**. Both produce small bundles that target modern browsers cleanly.

## Build target — the single load-bearing knob

SvelteKit's build target is configured via the underlying Vite config in `svelte.config.js`:

```js
// svelte.config.js
import adapter from '@sveltejs/adapter-auto';

export default {
  kit: {
    adapter: adapter(),
  },
  vite: {
    build: {
      target: ['chrome125', 'safari17.4', 'firefox129'],
      cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
    },
  },
};
```

This is the same target story as plain Vite — see [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md) for the full discussion. The key points repeated:

- esbuild lowers JS syntax to the engine versions you specify.
- Lightning CSS lowers CSS to the same versions if `cssTarget` matches (or reads `.browserslistrc` if `cssTarget` is omitted).
- **Vite does not polyfill runtime APIs.** If your code uses `URLPattern` or `Temporal`, SvelteKit ships those identifiers as-is.

If you'd rather drive both from `.browserslistrc`, the [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) canonical query applies unchanged:

```
chrome >= 125
firefox >= 129
safari >= 17.4
not dead
```

Lightning CSS will read it for `cssTarget`. The duplication for esbuild's `target` (Vite quirk — esbuild has [no browserslist support](https://github.com/evanw/esbuild/issues/121)) is unavoidable.

## Svelte's runtime — what it produces

The Svelte compiler analyzes each component and emits imperative DOM update code. The shared runtime — what every Svelte app ships in addition to per-component code — is small:

- **Svelte 4**: ~3KB minified + gzipped.
- **Svelte 5**: ~6KB minified + gzipped (runes machinery is slightly bigger but enables fine-grained reactivity).

Neither requires polyfills at our baseline. Svelte's compiler output uses standard DOM APIs (`document.createElement`, `addEventListener`, `requestAnimationFrame`, `Proxy` for runes), all universal at Chromium 125+ / Safari 17.4+ / Firefox 129+. There is no `core-js` injection step in the SvelteKit pipeline.

## Adapters — server-side, never browser

SvelteKit's [adapter ecosystem](https://svelte.dev/docs/kit/adapters) handles the server side of the build. Adapters are pure Node tooling — they package the SvelteKit output for a given deployment target. They do not touch the browser bundle's polyfill posture.

The official adapters:

| Adapter | Target | Server runtime | Polyfill notes |
|---|---|---|---|
| `@sveltejs/adapter-node` | Node servers | Node 18+ | None. Server bundle assumes Node, not browser. |
| `@sveltejs/adapter-cloudflare` | Cloudflare Workers + Pages | Workers runtime | Workers run web-standard APIs (fetch, streams) — close to browser, no polyfill needed at baseline |
| `@sveltejs/adapter-vercel` | Vercel | Node or Edge runtime | Vercel handles polyfilling its own runtime |
| `@sveltejs/adapter-netlify` | Netlify | Functions / Edge | Same — provider responsibility |
| `@sveltejs/adapter-static` | Static SSG | None — pure HTML | Browser-only; client bundle is the only concern |
| `@sveltejs/adapter-auto` | Detected from environment | Varies | Auto-installs a specific adapter at deploy time |

[`adapter-auto`](https://svelte.dev/docs/kit/adapter-auto) is the default for new projects via `npx sv create`. It probes deploy environment variables and swaps in the correct adapter — Cloudflare Pages, Netlify, Vercel, Azure SWA, AWS via SST, or Google Cloud Run via adapter-node. None of this affects the client bundle's browser target.

**The split: adapter = server, `vite.build.target` = browser.** They're orthogonal.

## What SvelteKit transpiles automatically

Out of the box, SvelteKit (via Vite + esbuild) handles:

- **TypeScript** — esbuild strips types. No type-check during build (run `svelte-check` or `tsc --noEmit` in CI).
- **Svelte components** — `.svelte` files compiled by `svelte/compiler`; output is JS calling Svelte's runtime.
- **CSS modules and `<style>` blocks** — scoped per component via Svelte's compiler; processed via Lightning CSS or PostCSS.
- **Asset imports** — hashed URLs, emitted to `dist/_app/immutable/assets/`.
- **Dynamic imports + code splitting** — Vite's standard treatment.
- **Server vs browser code split** — `+page.server.ts` vs `+page.ts` (server-only modules excluded from browser bundle).

## What SvelteKit does NOT polyfill

- **Runtime JS APIs** — same caveat as Vite. If you use `URLPattern`, `Temporal`, or `Object.groupBy` and they aren't shipped at your target floor, you ship them unfilled or BYO polyfill (see `../runtime-polyfills/`).
- **CSS runtime shims** — anchor positioning, scroll-driven animations, `@scope` are platform features. SvelteKit emits them as authored; Lightning CSS lowers what it can.
- **`core-js`** — there is no equivalent of `useBuiltIns: 'usage'` injection. Svelte assumes modern engines.
- **Legacy-browser bundle** — there is no `@vitejs/plugin-legacy` equivalent in SvelteKit's official toolchain. Don't add one at this baseline; see [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md).

## Service worker — built in, no polyfill burden

SvelteKit has [first-class service worker support](https://kit.svelte.dev/docs/service-workers): drop a file at `src/service-worker.js` (or `.ts`) and SvelteKit registers it automatically. The service worker is built as a separate bundle by Vite and runs in the browser's service worker context.

Service workers are universally supported at our baseline (Chrome since 40, Firefox since 44, Safari since 11.1). **No polyfill required.** The service worker bundle inherits `vite.build.target`; any worker-specific overrides go through `kit.serviceWorker` config.

For PWA features beyond what SvelteKit provides — install prompts, Workbox integration, manifest generation — the [`@vite-pwa/sveltekit`](https://vite-pwa-org.netlify.app/frameworks/sveltekit) plugin is the standard add-on. It expects you to disable SvelteKit's built-in registration:

```js
// svelte.config.js
export default {
  kit: {
    serviceWorker: { register: false }, // Vite PWA handles registration
  },
};
```

The plugin uses Workbox under the hood; Workbox itself is browser-modern and ships nothing exotic at our baseline.

## Recommended setup at our baseline

```js
// svelte.config.js
import adapter from '@sveltejs/adapter-auto';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter(),
  },
  vite: {
    build: {
      target: ['chrome125', 'safari17.4', 'firefox129'],
      cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
      sourcemap: true,
    },
  },
};
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

The duplication between `vite.build.target` and `browserslist` is the same Vite quirk discussed in [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md). Optionally use [`browserslist-to-esbuild`](https://github.com/marcofugaro/browserslist-to-esbuild) to compute the array from the browserslist source of truth.

## Common SvelteKit polyfill mistakes (the audit checklist)

The four patterns most likely to appear in real projects:

1. **No `vite.build.target` set at all.** Project inherits Vite 5/6's `'modules'` default (Safari 14 / Firefox 78 floor) or Vite 7's `'baseline-widely-available'` (Safari 16.4 / Firefox 114 floor). Both over-lower at our baseline.
2. **`@vitejs/plugin-legacy` added "for compatibility."** Doubles bundle output, ships SystemJS + core-js to every visitor. Strip it unless your audience genuinely includes pre-Safari 14. See [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md).
3. **`URLPattern` used in routing helpers without polyfill.** Firefox 129–141 lacks native support; if your routing code calls `new URLPattern(...)` you'll error. SvelteKit's own router doesn't use URLPattern; risk is in user code. See [`../runtime-polyfills/urlpattern.md`](../runtime-polyfills/urlpattern.md).
4. **Server-only Node API leaking into browser bundle.** Importing `fs`, `path`, or `crypto` (Node) into a `+page.svelte` file fails the build. Move to `+page.server.ts` or guard with `import.meta.env.SSR`.

## Cross-references

- [`./vite-6.md`](./vite-6.md) — the underlying build tool; SvelteKit inherits its target story.
- [`./nuxt.md`](./nuxt.md), [`./solidstart.md`](./solidstart.md) — sister Vite-based meta-frameworks with similar postures.
- [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md) — `vite.build.target` deep dive.
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical browserslist queries.
- [`../build-tools/lightningcss-features.md`](../build-tools/lightningcss-features.md) — what Lightning CSS lowers under SvelteKit's CSS pipeline.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what the baseline floor means in features.
- [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) — why over-broad targets hurt at this baseline.
