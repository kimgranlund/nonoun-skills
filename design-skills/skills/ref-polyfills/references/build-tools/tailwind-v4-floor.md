---
date: 2026-04-27
coverage: extended
peers:
  - ../build-tools/lightningcss-features.md
  - ../build-tools/postcss-preset-env.md
  - ../build-tools/browserslist-recipes.md
  - ../build-tools/vite-build-target.md
  - ../css-color-bugs/relative-color-syntax.md
  - ../css-color-bugs/oklch-oklab-safari.md
  - ../css-polyfills-and-shims/at-property-fallbacks.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://tailwindcss.com/docs/compatibility — Tailwind v4 official browser-support floor (Chrome 111, Safari 16.4, Firefox 128)
  - https://tailwindcss.com/blog/tailwindcss-v4 — Tailwind CSS v4.0 release announcement (January 22, 2025)
  - https://tailwindcss.com/docs/upgrade-guide — v3 → v4 upgrade guide
  - https://github.com/tailwindlabs/tailwindcss/discussions/15356 — "tailwind 4 oklch not compatibility with old browser"
  - https://github.com/tailwindlabs/tailwindcss/discussions/17547 — Maintaining Tailwind in Legacy Environments – v3 LTS or v4 polyfill options?
  - https://github.com/tailwindlabs/tailwindcss/discussions/18270 — Wider Browser Support for Tailwind v4 (community discussion)
  - https://github.com/tailwindlabs/tailwindcss/issues/14119 — [v4] Clarify browser support
  - https://endoflife.date/tailwind-css — Tailwind v3.4 supported until Feb 28, 2027
---

# Tailwind CSS v4 — the hard browser-support floor

Tailwind CSS v4 (Oxide) is built on modern CSS features that **cannot be polyfilled syntactically**. This makes Tailwind's browser-support story unusual in our skill: where most CSS tools either pass through a feature or lower it, Tailwind v4 simply *requires* the feature to be native. There is no polyfill path. Below the floor, you stay on Tailwind v3.

> The TL;DR: Tailwind v4 floor is **Chrome 111 / Safari 16.4 / Firefox 128**. At our expert-polyfills baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+), Tailwind v4 works fine — we're well above its floor. Below its floor, no polyfill exists; use Tailwind v3.4 (LTS-ish until Feb 28, 2027).

## What Tailwind v4 is

Tailwind CSS v4.0, [released January 22, 2025](https://tailwindcss.com/blog/tailwindcss-v4), is a ground-up rewrite of the framework with the **Oxide engine** at its core — a Rust implementation that replaces the JS-based v3 pipeline.

The headline numbers from the [v4 release announcement](https://tailwindcss.com/blog/tailwindcss-v4):

- **Up to 5× faster** full builds.
- **Over 100× faster** incremental builds, measured in microseconds.
- **First-party Vite plugin** — `@tailwindcss/vite` — replacing the PostCSS pipeline as the recommended path.
- **Automatic content detection** — no `content: [...]` array configuration.
- **CSS-first config** — `@theme { ... }` blocks in CSS replace `tailwind.config.js`.

These speed wins are real and they're a strong reason to upgrade. The cost is a higher browser floor than v3.

## The official floor (load-bearing)

From [tailwindcss.com/docs/compatibility](https://tailwindcss.com/docs/compatibility):

> Tailwind CSS v4.0 is designed for and tested on modern browsers, and the core functionality of the framework specifically requires:
> - **Safari 16.4+** (released March 2023)
> - **Chrome 111+** (released March 2023)
> - **Firefox 128+** (released July 2024)
>
> Tailwind CSS v4.0 will not work in older browsers. If you need to support older browsers, stick with v3.4 until your browser support requirements change.

This floor is **non-negotiable**. The v4 engine emits CSS that depends on:

| Feature | Why v4 needs it | First shipped |
|---|---|---|
| **`@property`** (registered custom properties) | Animatable gradients, transitionable color stops, type-safe theme variables | Chrome 85, Safari 16.4, Firefox 128 |
| **`color-mix()`** | Opacity adjustment for any color value (including CSS variables and `currentColor`) | Chrome 111, Safari 16.4, Firefox 113 |
| **Cascade layers (`@layer`)** | Authoring layers for utilities/components/base; predictable specificity | Chrome 99, Safari 15.4, Firefox 97 |
| **OKLCH (`oklch()`)** | Default color palette — wider gamut, perceptually uniform | Chrome 111, Safari 15.4, Firefox 113 |
| **Logical properties (`padding-inline`, etc.)** | RTL/LTR-agnostic spacing utilities | Chrome 87+, Safari 14.5+, Firefox 66+ |
| **CSS Nesting (`& .child`)** | `@theme` block cleanup | Chrome 112, Safari 16.5, Firefox 117 |
| **Container queries (`@container`)** | `@container` query utilities | Chrome 105, Safari 16, Firefox 110 |

The **binding constraints** — the ones that set the actual floor — are `@property`, `color-mix()`, and OKLCH. Older browsers ship some of the others but lack these three.

## What "no polyfill path" actually means

Tailwind v4's CSS output uses these features *as primary mechanisms*. There is no fallback:

- The default color palette is **emitted as `oklch()` values**. A browser that doesn't understand `oklch()` will fail to parse those declarations. There is no `rgb()` fallback in the output.
- Theme variables that animate use **`@property` registration**. A browser that ignores `@property` rules will treat the variables as untyped strings, and animations will not interpolate. CSS Tricks-style "use a type guard" doesn't apply — Tailwind v4 *depends on* `@property` working.
- Opacity utilities (`bg-blue-500/50`) **emit `color-mix(in oklab, ...)`** to compute the alpha-modulated color. A browser without `color-mix()` will fail to parse those rules.

Lightning CSS — the CSS lowering tool ostensibly capable of transforming OKLCH to sRGB and `color-mix()` to static colors — **cannot save you here**. It can lower *some* uses, but Tailwind v4's output is not a static set of declarations; it relies on runtime CSS-variable resolution and `@property` typing. The features are too entangled with v4's runtime model to be lowered to a pre-2023 browser. See [`./lightningcss-features.md`](./lightningcss-features.md) for the lowering matrix and what's actually possible.

The Tailwind team's [own statement on this](https://github.com/tailwindlabs/tailwindcss/discussions/15356): if you need legacy browser support, **stay on v3.4**. There is an active community-discussion thread ([Wider Browser Support for Tailwindcss V4](https://github.com/tailwindlabs/tailwindcss/discussions/18270)) but no committed plan to backport.

## Verdict at our expert-polyfills baseline

Our baseline:

| Engine | Floor | Tailwind v4 needs | Verdict |
|---|---|---|---|
| Chromium | 125 (May 2024) | 111 (March 2023) | ✅ 14 versions / 14 months above v4's floor |
| Safari | 17.4 (March 2024) | 16.4 (March 2023) | ✅ 1 major version / 12 months above v4's floor |
| Firefox | 129 (August 2024) | 128 (July 2024) | ✅ Just 1 version above v4's floor — close, but above |

**Tailwind v4 works fine at the expert-polyfills baseline.** Every engine at our floor ships every CSS feature v4 depends on. No polyfills, no shims, no fallback layers needed.

Note the Firefox margin is tight (129 vs 128), but on the right side. A team that pulls their Firefox floor down to 127 or earlier crosses Tailwind v4's line.

## Tailwind v3 — the LTS-ish path

Per [endoflife.date/tailwind-css](https://endoflife.date/tailwind-css), Tailwind CSS 3.4 is supported until **February 28, 2027**. That gives the v3 → v4 migration window a meaningful tail: roughly 18 months from v4's January 2025 release to v3's effective EOL.

**v3.4's browser support** ([v3 docs](https://v3.tailwindcss.com/docs/browser-support)):

> Tailwind CSS v3.0 is designed and tested on the latest stable versions of Chrome, Firefox, Edge, and Safari. It does not support any version of IE, including IE 11.

In practice, v3.4 works back to roughly Chrome 76 / Safari 13.1 / Firefox 70 with no special configuration. Significantly wider than v4's floor.

**When to stay on v3.4:**

- Your audience includes substantial Safari < 16.4 traffic (older iOS devices, iOS 15.x).
- You need Chrome < 111 support (rare in 2026 — that's a 3-year-old Chrome).
- You need Firefox < 128 support.
- You're shipping to embedded browsers (smart TVs, kiosk devices) with locked-down old engines.

**When to upgrade to v4:**

- Your floor is at-or-above Chrome 111 / Safari 16.4 / Firefox 128.
- You want the build-speed wins.
- You want the CSS-first configuration ergonomics.
- You're starting a new project in 2026 — v4 is the default; v3 is the legacy path.

At our expert-polyfills baseline, **v4 is the right choice**. The audience definition matches.

## Migration cost — what changes from v3 to v4

A non-exhaustive list, drawn from the [v4 upgrade guide](https://tailwindcss.com/docs/upgrade-guide):

- **`tailwind.config.js` is replaced with `@theme { ... }`** in CSS. The migration tool (`@tailwindcss/upgrade`) handles most of this automatically.
- **`@apply` works differently** in scoped contexts. Some patterns that worked in v3 need rewriting.
- **`@layer base/components/utilities`** are now native cascade layers, not Tailwind constructs. The semantics are slightly different (CSS layer ordering vs Tailwind's pre-2025 directive ordering).
- **Removed utilities.** A handful of utilities present in v3 are removed in v4 (e.g., the `text-opacity-*` family is gone — opacity is now part of the color utility itself: `text-blue-500/50`).
- **Default color palette is OKLCH.** The visible colors are perceptually similar but not byte-identical to v3's RGB palette. If you've calibrated visual designs against v3 colors, expect minor shifts.
- **Plugin API has changed.** v3 plugins generally need rewriting for v4. Most popular plugins (e.g., `@tailwindcss/typography`) have v4-compatible releases.

The migration tool does ~80% of the work; the rest is per-codebase. Budget more for projects with heavy customization.

## The "no polyfill path" rule and what it implies

Three operational consequences:

1. **Don't try to polyfill OKLCH or `color-mix()` for Tailwind v4.** Teams sometimes ask: "can I add a polyfill that converts OKLCH to RGB at runtime?" The answer in 2026 is *no, not realistically*. The Tailwind v4 output is too dense with these features for a runtime polyfill to cover; the build-time lowering options (Lightning CSS) cover only static cases, not the variable-driven dynamics Tailwind relies on.

2. **Don't downgrade your `build.cssTarget` below v4's floor when using v4.** If you have:
   ```ts
   // vite.config.ts
   build: { cssTarget: ['chrome100', 'safari14', 'firefox100'] }
   ```
   Lightning CSS will not auto-fix Tailwind v4's output to those targets. The OKLCH stays OKLCH; the `color-mix()` stays `color-mix()`. Your bundle ships, the older browser refuses to parse the colors. Either align `cssTarget` to ≥ v4's floor, or use v3.

3. **The "compatibility mode" question.** The Tailwind team has [acknowledged](https://github.com/tailwindlabs/tailwindcss/discussions/17547) that they are exploring a future "compatibility mode" for older browser support. As of April 2026 it has not shipped. Don't plan around it.

A community workaround exists ([`vite-plugin-tailwind-legacy`](https://www.npmjs.com/package/vite-plugin-tailwind-legacy)) that automatically serves Tailwind v3 as a fallback for legacy browsers while keeping v4 for modern browsers. It's a reasonable hack for teams who can't quite move their audience floor up to v4's, but it's a *different bundle for old vs new*, with the operational cost that implies (two CSS pipelines, two test surfaces).

## At our baseline — the recipe

```css
/* src/styles/main.css — Tailwind v4 entry */
@import "tailwindcss";

@theme {
  /* Custom theme variables */
  --color-brand-500: oklch(0.6 0.2 250);
  --color-brand-600: oklch(0.55 0.22 250);
}

/* Your own components */
@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg bg-brand-500 hover:bg-brand-600;
  }
}
```

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [
    tailwindcss(),
  ],
  build: {
    target: ['chrome125', 'safari17.4', 'firefox129'],
    cssTarget: ['chrome125', 'safari17.4', 'firefox129'],
  },
});
```

Both `target` and `cssTarget` are at or above Tailwind v4's floor — no conflict. No polyfills, no fallback layers.

## Common Tailwind-v4 mistakes (audit checklist)

1. **Setting `cssTarget` to Chrome 100 / Safari 14 / Firefox 100 with Tailwind v4.** Output won't be lowered. Either align `cssTarget` ≥ v4's floor, or use v3.
2. **Mixing v3 and v4 in one project.** They share the `tailwindcss` package name; npm cannot install both. Migrate fully, not partially.
3. **Trying to add a "polyfill plugin" for Tailwind v4 → old browsers.** Doesn't exist; doesn't work. Use v3 if you need that floor.
4. **Forgetting that v4's color palette is OKLCH.** Visual designs calibrated against v3 colors will see minor hue shifts. Audit before deploying.
5. **Keeping `tailwind.config.js` after migrating to v4.** v4 reads `@theme` blocks in CSS, not the JS config. The legacy file may be ignored silently.
6. **Loading `@tailwindcss/postcss` *and* `@tailwindcss/vite` in the same project.** Pick one. The Vite plugin is recommended for Vite-based stacks.

## Cross-references

- [`./lightningcss-features.md`](./lightningcss-features.md) — what Lightning CSS will and won't lower for OKLCH / `color-mix()`.
- [`./postcss-preset-env.md`](./postcss-preset-env.md) — the alternative CSS-lowering path; same limitations apply at v4's floor.
- [`./browserslist-recipes.md`](./browserslist-recipes.md) — verifying your audience matches v4's floor.
- [`./vite-build-target.md`](./vite-build-target.md) — `build.cssTarget` interaction with v4's output.
- [`../css-color-bugs/relative-color-syntax.md`](../css-color-bugs/relative-color-syntax.md) — relative OKLCH (`oklch(from base ...)`) used in v4 themes.
- [`../css-color-bugs/oklch-oklab-safari.md`](../css-color-bugs/oklch-oklab-safari.md) — Safari < 18 OKLCH `color-mix` bug; relevant for Tailwind v4 hover states on Safari 16.4–17.6.
- [`../css-polyfills-and-shims/at-property-fallbacks.md`](../css-polyfills-and-shims/at-property-fallbacks.md) — `@property` fallback patterns; Tailwind v4 leans on these.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — our baseline vs Tailwind v4's floor.
