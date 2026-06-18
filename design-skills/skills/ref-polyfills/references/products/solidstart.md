---
date: 2026-04-27
coverage: extended
peers:
  - ../products/vite-6.md
  - ../products/sveltekit.md
  - ../products/nuxt.md
  - ../build-tools/vite-build-target.md
  - ../build-tools/browserslist-recipes.md
  - ../build-tools/lightningcss-features.md
  - ../meta/the-modern-baseline.md
  - ../anti-patterns/target-es5-modern.md
primary_sources:
  - https://start.solidjs.com/ — SolidStart official site
  - https://docs.solidjs.com/solid-start — SolidStart docs
  - https://github.com/solidjs/solid-start — SolidStart repo
  - https://github.com/solidjs/solid-start/releases — release log
  - https://github.com/solidjs/solid-start/releases/tag/@solidjs/start@1.1.0 — v1.1.0 "Gear 5" notes
  - https://docs.solidjs.com/solid-start/reference/config/define-config — defineConfig reference
  - https://www.solidjs.com/blog/solid-start-the-shape-frameworks-to-come — v1.0 announcement
  - https://github.com/solidjs/solid/discussions/2618 — SolidStart 2.0 alpha + Vite 8 plans
---

# SolidStart — polyfill posture at the modern baseline

SolidStart is Solid + Vite + Nitro (via Vinxi). Solid's runtime is tiny (~7KB gzipped); Solid's compiler emits direct DOM instructions like Svelte. Like SvelteKit and Nuxt, the polyfill story is downstream of [`./vite-6.md`](./vite-6.md). The only knob at our baseline is `vite.build.target`, exposed through SolidStart's `defineConfig`.

> The TL;DR: SolidStart ships nothing you need to polyfill. Solid's compiler output uses standard DOM APIs that are universal at our baseline. Set `vite.build.target` via `defineConfig` and call it done.

## What ships today

| Component | Current major | Released | Notes |
|---|---|---|---|
| **SolidStart** | **1.x** | February 2024 (v1.0) | v1.1.0 "Gear 5" updated to Vite 6; v2.0.0-alpha.2 in heavy development as of February 2026 |
| **Solid** | **1.x** | Solid.js core, current | Fine-grained reactivity via signals; ~7KB gzipped |
| **Vite** | 6.x | underlying | SolidStart 1.1+ on Vite 6; SolidStart 2.0 plans Vite 8 + DeVinxi |
| **Vinxi** | underlying | application bundler | Wraps Nitro + Vite; SolidStart 2.0 will replace with pure Vite ("DeVinxi") |
| **Nitro** | server engine | via Vinxi | Same Nitro as Nuxt — see [`./nuxt.md`](./nuxt.md) |

[SolidStart v1.0](https://www.solidjs.com/blog/solid-start-the-shape-frameworks-to-come) shipped February 2024. [v1.1.0 "Gear 5"](https://github.com/solidjs/solid-start/releases/tag/@solidjs/start@1.1.0) brought Vite 6 support and substantial server-function fixes. SolidStart 2.0 is in heavy development: alpha.2 landed February 2026, the headline architectural change is replacing Vinxi with a pure Vite-based system internally called "DeVinxi" — so the underlying build pipeline becomes plainer.

## Solid's runtime — what it produces

Solid's compiler analyzes JSX, generates imperative DOM updates, and threads signal subscriptions through the resulting code. The shared runtime — what every Solid app ships beyond per-component code — is small:

- **Solid core**: ~7KB minified + gzipped.
- **Compiled output**: per-component code calling `template`, `insert`, `effect`, `createComponent` from `solid-js/web`.

For comparison: React + ReactDOM ≈ 42KB gzipped, Vue 3 ≈ 16KB, Svelte 4 ≈ 3KB, Svelte 5 ≈ 6KB, Lit 3 ≈ 5KB. Solid sits at the low end alongside Lit and Svelte.

Solid's runtime uses standard DOM APIs — `document.createElement`, `addEventListener`, `Proxy` for stores. All universal at Chromium 125+ / Safari 17.4+ / Firefox 129+. **There is no `core-js` injection step in the SolidStart build pipeline.**

## Build target — the load-bearing knob

SolidStart's build target is configured through `defineConfig`'s nested `vite` field in `app.config.ts`:

```ts
// app.config.ts
import { defineConfig } from '@solidjs/start/config';

export default defineConfig({
  vite: {
    build: {
      target: ['chrome125', 'safari17.4', 'firefox129'],
      cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
    },
  },
});
```

This routes through Vinxi → Vite → esbuild + Lightning CSS. Same model as plain Vite — see [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md).

If you'd rather drive both from `.browserslistrc`, the [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) canonical query applies. Lightning CSS reads it for `cssTarget`. The duplication for esbuild's `target` (Vite quirk) is unavoidable.

When SolidStart 2.0 lands DeVinxi the surface stays roughly the same — a `vite` block on `defineConfig` — but the path beneath it will be more direct (no Vinxi wrapping).

## Server side — Nitro via Vinxi

SolidStart uses [Nitro](https://nitro.build/) for the server side, wrapped by Vinxi. The same Nitro discussed in [`./nuxt.md`](./nuxt.md): Node, Cloudflare Workers, Vercel, Netlify, Bun, Deno, AWS Lambda, static SSG — all available presets.

Server code in SolidStart runs in Node (or Workers / Edge / Bun / etc.), not in a browser. **The browser target (`vite.build.target`) does not constrain server output.** Nitro picks its own ECMAScript level per preset, typically `esnext`.

Server functions (`use server` directive) in SolidStart split client and server bundles automatically — the server function body runs on the server, the client gets a thin RPC stub. Polyfill posture follows the split: client stub → browser target; server body → Node runtime, no browser polyfill needed.

## What SolidStart transpiles automatically

Out of the box, SolidStart (via Vite + Vinxi + esbuild + Babel for JSX) handles:

- **TypeScript** — esbuild strips types in the client bundle.
- **JSX** — Solid uses Babel via `babel-preset-solid` (because Solid's JSX semantics differ from React's; esbuild's JSX transform doesn't fit). The Babel pass runs *only* for JSX transformation; it does not pull in `core-js` or `preset-env`.
- **CSS modules** — `*.module.css` scoping via Lightning CSS or PostCSS.
- **File-based routing** — under `src/routes/`; resolved by `@solidjs/router` at runtime.
- **`use server` directive** — splits server functions into a server-only bundle.
- **Asset imports + dynamic imports** — Vite-standard.

## What SolidStart does NOT polyfill

- **Runtime JS APIs** — same caveat as Vite. `URLPattern`, `Temporal`, `Object.groupBy` ship as authored.
- **CSS runtime shims** — anchor positioning, scroll-driven animations, `@scope` are platform features. Lightning CSS lowers what it can.
- **`core-js`** — Babel's role in SolidStart is JSX-only. There's no automatic core-js injection; no `useBuiltIns: 'usage'` equivalent.
- **Legacy bundle** — there is no `@vitejs/plugin-legacy` equivalent in the official toolchain. Don't add one at this baseline.

## Solid ecosystem polyfill posture

Solid's ecosystem (`@solidjs/router`, `@solidjs/meta`, `solid-primitives`) targets modern engines. `solid-primitives` in particular ships composables that touch every modern web API — `createIntersectionObserver`, `createResizeObserver`, `createElementVisibility`, `createShare`, `createClipboard`. **None bundle polyfills.** Each feature-detects and no-ops gracefully on unsupported browsers; at our baseline every wrapped API is native.

## Recommended setup at our baseline

```ts
// app.config.ts
import { defineConfig } from '@solidjs/start/config';

export default defineConfig({
  vite: {
    build: {
      target: ['chrome125', 'safari17.4', 'firefox129'],
      cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
      sourcemap: true,
    },
  },

  // Nitro preset selection — defaults to 'node-server';
  // override via server: { preset: 'cloudflare' } if needed
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

The duplication between `vite.build.target` and `browserslist` is the same Vite quirk discussed in [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md).

## Common SolidStart polyfill mistakes (the audit checklist)

The four patterns most likely to appear in real projects:

1. **No `vite.build.target` set.** Project inherits Vite's default — for Vite 6 that's `'modules'` (Safari 14 floor). Over-lowers at our baseline.
2. **`babel.config.js` with `@babel/preset-env` added "for safety."** The Babel pass in SolidStart is JSX-only by design. Adding preset-env on top runs core-js injection unnecessarily and inflates the client bundle. Use the Solid-curated Babel preset (`babel-preset-solid`) and stop there.
3. **`URLPattern` used in route helpers without polyfill.** Solid's router has its own pattern-matching, but if user code calls `new URLPattern(...)` you'll error in Firefox 129–141. See [`../runtime-polyfills/urlpattern.md`](../runtime-polyfills/urlpattern.md).
4. **Confusing Solid's signals with browser primitives.** Solid's `createSignal` is a userland primitive — it has no relationship to a hypothetical browser-native `Signal`. Don't reach for a polyfill expecting one to exist.

## Cross-references

- [`./vite-6.md`](./vite-6.md) — the underlying build tool; SolidStart inherits its target story.
- [`./sveltekit.md`](./sveltekit.md), [`./nuxt.md`](./nuxt.md) — sister Vite-based meta-frameworks with similar postures.
- [`../build-tools/vite-build-target.md`](../build-tools/vite-build-target.md) — `vite.build.target` deep dive.
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — canonical browserslist queries.
- [`../build-tools/lightningcss-features.md`](../build-tools/lightningcss-features.md) — what Lightning CSS lowers under SolidStart's CSS pipeline.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what the baseline floor means in features.
- [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) — why over-broad targets hurt at this baseline.
