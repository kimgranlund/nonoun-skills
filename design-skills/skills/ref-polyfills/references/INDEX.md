# expert-polyfills — Reference Index

_Authoritative manifest of reference files. Updated at end of every wave._

**Baseline (load-bearing)**: Chromium 125+ (May 2024), Safari 17.4+ (March 2024), Firefox 129+ (August 2024).

## Status legend

- ✅ — present, reviewed, current
- 🟡 — present but needs update or review
- ⬜ — planned, not yet authored

## Coverage tiers

- **canonical** — load-bearing, quote freely
- **extended** — solid practical coverage
- **esoteric** — narrow / browser-specific / niche
- **advisory** — opinionated guidance, may shift faster

## Axes (13)

| # | Axis | Lens | Files | Purpose |
|---|---|---|---|---|
| 1 | `meta/` | substrate | 4 | Glossary, baseline definition, decision tree |
| 2 | `runtime-polyfills/` | capability | 8 | JS runtime polyfills the baseline still needs (Temporal, URLPattern, etc.) |
| 3 | `css-polyfills-and-shims/` | capability | 7 | CSS feature lowering and runtime shims |
| 4 | `transpilation/` | capability | 6 | Babel, SWC, esbuild, TypeScript build-time transformation |
| 5 | `build-tools/` | capability | 7 | Per-tool target lowering, browserslist, Vite/Next/Tailwind floors |
| 6 | `products/` | comparative | 8 | Per-framework polyfill story (Next, Vite, Astro, SvelteKit, etc.) |
| 7 | `css-color-bugs/` | esoteric | 8 | **User-flagged** — CSS color function bugs at baseline |
| 8 | `popover-quirks/` | esoteric | 7 | **User-flagged** — Popover API quirks at baseline |
| 9 | `anchor-positioning-quirks/` | esoteric | 5 | Anchor positioning interop and rename history |
| 10 | `js-language-status/` | capability | 8 | TC39 stage map + current shipping state |
| 11 | `landscape-shifts/` | comparative | 5 | polyfill.io attack, core-js, mirrors, Interop 2026 |
| 12 | `anti-patterns/` | substrate | 6 | What NOT to do |
| 13 | `feature-detection/` | capability | 5 | `@supports`, JS detection, ponyfill / prollyfill patterns |
| | **Total target** | | **84** | |

## Wave plan

| Wave | Files | Axis emphasis | Status |
|---|---|---|---|
| Scoping | — | Cross-axis survey, axis list, file plan | ✅ complete 2026-04-27 |
| Wave 1 — Foundations + landscape | 16 | meta (4), landscape-shifts (5), runtime-polyfills core (4), anti-patterns top half (3) | ✅ complete 2026-04-27 |
| Wave 2 — JS + transpilation | 18 | js-language-status (8), transpilation (6), build-tools first half (4) | ✅ complete 2026-04-27 |
| Wave 3 — Esoteric bugs | 20 | css-color-bugs (8), popover-quirks (7), anchor-positioning-quirks (5) | ✅ complete 2026-04-27 |
| Wave 4 — CSS + features + tools | 16 | css-polyfills-and-shims (7), build-tools tail (3), feature-detection (5), runtime-polyfills tail (1) | ✅ complete 2026-04-27 |
| Wave 5 — Products + completion | 14 | products (8), anti-patterns tail (3), runtime-polyfills final (3) | ✅ complete 2026-04-27 |
| **v1.0.0 release** | — | All 84 files landed; status `complete` | **✅ released 2026-04-27** |

## File manifest

### meta/ (4)

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `meta/glossary.md` | canonical | polyfill / ponyfill / prollyfill / shim / transpiler / lowering definitions |
| ✅ | `meta/baseline-glossary.md` | canonical | Baseline newly available vs widely available; Baseline 2024/2025/2026 sets |
| ✅ | `meta/the-modern-baseline.md` | canonical | What Chrome 125+ / Safari 17.4+ / Firefox 129+ means in practice |
| ✅ | `meta/decision-tree.md` | canonical | "Do I need a polyfill?" flowchart |

### runtime-polyfills/ (8)

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `runtime-polyfills/temporal-api.md` | canonical | `@js-temporal/polyfill` (~52KB) or `temporal-polyfill` (~20KB FullCalendar fork); native in Firefox 139+, Chrome 144+, Safari pending |
| ✅ | `runtime-polyfills/urlpattern.md` | canonical | `urlpattern-polyfill` (kenchris); needed for Firefox 129–141 (Firefox 142 ships native, Aug 2025) |
| ✅ | `runtime-polyfills/iterator-helpers.md` | extended | `es-iterator-helpers` for Safari 17.4–18.3 |
| ✅ | `runtime-polyfills/set-methods.md` | extended | Baseline since June 2024; only needed below Safari 17 / Firefox 127 (mostly historical) |
| ✅ | `runtime-polyfills/array-grouping.md` | extended | `Object.groupBy` / `Map.groupBy` Baseline March 2024 (Safari 17.4 was the gating engine); rename history Sugar.js webcompat → `Array.prototype.group` → static methods on `Object`/`Map`; **stop-polyfilling verdict** at baseline |
| ✅ | `runtime-polyfills/cookie-store-api.md` | extended | Chrome 87+ / Safari 18.4+ (March 31, 2025) / Firefox 138+ (April 29, 2025); markcellus/cookie-store polyfill covers Window scope only — SW scope can't be polyfilled |
| ✅ | `runtime-polyfills/compression-streams.md` | extended | Native Chrome 80 / Safari 16.4 / Firefox 113; Baseline Widely Available since ~Nov 2025; **stop-polyfilling verdict** — migrate off `pako` (~22KB) at baseline; three concrete pako→native migration patterns; Brotli partial support (Safari 18.4 only) |
| ✅ | `runtime-polyfills/error-iserror-promise-try.md` | extended | Five ES2025/2026 finishers: `Promise.withResolvers` (universal native), `Promise.try` (Stage 4 Oct 2024), `Error.isError` (Stage 4 May 2025), `RegExp.escape` (Stage 4 Feb 2025), `Float16Array` (Stage 4 Feb 2025); inline shims for the four small ones; `@petamoriken/float16` for the typed array |

### css-polyfills-and-shims/ (7)

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `css-polyfills-and-shims/anchor-positioning-polyfill.md` | canonical | `@oddbird/css-anchor-positioning`; needed for Safari < 26 / Firefox < 147 |
| ✅ | `css-polyfills-and-shims/popover-polyfill.md` | extended | `@oddbird/popover-polyfill` (used by GitHub); historical at baseline |
| ✅ | `css-polyfills-and-shims/scroll-timeline-polyfill.md` | extended | `flackr/scroll-timeline`; Firefox flag, Safari < 26 |
| ✅ | `css-polyfills-and-shims/view-transitions.md` | canonical | same-doc Baseline Oct 2025; cross-doc Chromium-only |
| ✅ | `css-polyfills-and-shims/at-property-fallbacks.md` | extended | Feature-query gating; no real polyfill |
| ✅ | `css-polyfills-and-shims/lightningcss-css-lowering.md` | canonical | What gets lowered automatically vs needs runtime |
| ✅ | `css-polyfills-and-shims/postcss-preset-env-stages.md` | extended | cssdb stages 0-4; default is stage 2 |

### transpilation/ (6)

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `transpilation/babel-preset-env.md` | canonical | `useBuiltIns: 'usage'`, `corejs: 3`, browserslist coupling |
| ✅ | `transpilation/swc-targets.md` | canonical | `env.targets`, browserslist auto-discovery (since v1.1.10) |
| ✅ | `transpilation/esbuild-targets.md` | canonical | `target: ['chrome125','safari17.4','firefox129']`; what it skips |
| ✅ | `transpilation/typescript-target-esnext.md` | canonical | `target` vs `lib`; never ship `target: 'es5'` to modern |
| ✅ | `transpilation/transform-runtime-vs-preset-env.md` | extended | Sandbox vs global pollution; mutual exclusion |
| ✅ | `transpilation/decorators-stage-3.md` | extended | `2023-11` Babel proposal; TypeScript 5+ standard mode |

### build-tools/ (7)

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `build-tools/vite-build-target.md` | canonical | Vite 7+ default `'baseline-widely-available'` (Vite 6 added option as opt-in; Vite 7 made it default) |
| ✅ | `build-tools/lightningcss-features.md` | canonical | Relative color, gradient stops, range syntax, nesting, logical props |
| ✅ | `build-tools/postcss-preset-env.md` | extended | Stage groups; default stage 2; cssdb feature list |
| ✅ | `build-tools/esbuild-config.md` | extended | esbuild bundling surface beyond target — format, bundle, splitting, external, sourcemap, watch (v0.17 context API) |
| ✅ | `build-tools/browserslist-recipes.md` | canonical | Verified queries matching the Chromium 125 / Safari 17.4 / Firefox 129 baseline |
| ✅ | `build-tools/tsconfig-lib-target.md` | canonical | TypeScript `lib` deep dive; default per target; mismatch trap; sub-bundle enumeration; DOM vs WebWorker exclusion |
| ✅ | `build-tools/tailwind-v4-floor.md` | extended | Tailwind v4 hard floor Chrome 111 / Safari 16.4 / Firefox 128; v3.4 EOL Feb 28, 2027 |

### products/ (8)

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `products/next-js-15.md` | extended | Default browserslist `chrome 111 / edge 111 / firefox 111 / safari 16.4` (NOT what older briefs assumed); no `supportedBrowsers` config option exists; `next-polyfill-nomodule` auto-injection; Next 16 (Oct 2025) Turbopack default |
| ✅ | `products/vite-6.md` | extended | `'baseline-widely-available'` opt-in in v6 (Nov 26, 2024), DEFAULT in v7 (June 24, 2025); `@vitejs/plugin-legacy` for sub-baseline split builds |
| ✅ | `products/react-router-v7.md` | extended | Vite-based; TextEncoderStream Chrome 71+ / Safari 14.1+ / Firefox 105+ — fully native at baseline |
| ✅ | `products/astro.md` | extended | Astro 5 (Dec 2024) and Astro 6 (Vite 7 + Environment API); islands architecture means most pages have zero polyfill concerns |
| ✅ | `products/sveltekit.md` | extended | Svelte 5 (Oct 19, 2024) ~6KB runtime; Vite-based; no automatic core-js; built-in service worker support adds no polyfill burden; `vite.build.target` set in `svelte.config.js` |
| ✅ | `products/nuxt.md` | extended | Nuxt 4 (July 15, 2025; 4.4.2 current); Vue 3 (Proxy reactivity); Nitro v3 beta; `nuxt.config.ts` `vite.build.target` is the single load-bearing knob |
| ✅ | `products/solidstart.md` | extended | SolidStart 1.x (v1.1.0 "Gear 5" on Vite 6); v2 alpha replacing Vinxi with DeVinxi; ~7KB runtime; Babel role is JSX-only |
| ✅ | `products/web-components-frameworks.md` | extended | Lit 3.3.x (~5KB ES2021); Stencil 4.43.4 (April 2026); Microsoft FAST maintenance; **stop shipping `@webcomponents/webcomponentsjs`**; Scoped Custom Element Registries: Safari 26 + Chrome 146 native, Firefox does NOT — `@webcomponents/scoped-custom-element-registry` required for Firefox |

### css-color-bugs/ (8) — **USER-FLAGGED**

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `css-color-bugs/oklch-oklab-safari.md` | esoteric | Safari < 18 hue-mix bug (LCH instead of OKLCH); Tailwind v4 PR #15201 |
| ✅ | `css-color-bugs/color-mix-interpolation.md` | esoteric | Chrome vs Safari hue-value divergence in oklch; oklab safer for transparent/gray |
| ✅ | `css-color-bugs/light-dark-color-scheme.md` | esoteric | Requires `color-scheme: light dark`; common gotcha |
| ✅ | `css-color-bugs/contrast-color-availability.md` | esoteric | Safari TP / Firefox only; Chrome stable does not ship |
| ✅ | `css-color-bugs/display-p3-firefox-lag.md` | esoteric | Firefox doesn't render P3 distinct from sRGB |
| ✅ | `css-color-bugs/relative-color-syntax.md` | extended | `oklch(from base ...)` Chrome 119+; Safari 16.4+; feature query |
| ✅ | `css-color-bugs/currentcolor-resolution.md` | esoteric | Timing in modern color functions; container interactions |
| ✅ | `css-color-bugs/wide-gamut-fallbacks.md` | extended | `@media (color-gamut: p3)` and CSS color() fallback patterns |

### popover-quirks/ (7) — **USER-FLAGGED**

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `popover-quirks/ios-safari-light-dismiss.md` | esoteric | WebKit Bug 267688: light dismiss broken on iOS/iPadOS 17.x |
| ✅ | `popover-quirks/safari-focus-inputs.md` | esoteric | Focus-on-tap closes popover; iOS keyboard scrolls and dismisses |
| ✅ | `popover-quirks/safari-184-tab-hang.md` | esoteric | Safari 18.4 fixed tab-out hang; before 18.4 it hangs |
| ✅ | `popover-quirks/popover-vs-dialog-toplayer.md` | esoteric | z-index has no effect inside top layer; dialog inerts background-page popovers |
| ✅ | `popover-quirks/popover-hint-chromium-only.md` | extended | `popover="hint"` Chrome 133+ only |
| ✅ | `popover-quirks/popovertarget-vs-showpopover.md` | extended | Programmatic vs declarative API divergences |
| ✅ | `popover-quirks/popover-anchor-crash.md` | esoteric | WebKit Bug 279588: WebProcess crash when popover uses anchoring |

### anchor-positioning-quirks/ (5)

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `anchor-positioning-quirks/inset-area-rename.md` | extended | Chrome 129 renamed to `position-area`; old name through Chrome 131 only |
| ✅ | `anchor-positioning-quirks/safari-26-anchor-shipped.md` | extended | Safari 26 ships full; 18.4 needed for `@position-try` |
| ✅ | `anchor-positioning-quirks/firefox-147-anchor-shipped.md` | extended | Firefox 147 (Jan 2026) ships unflagged; 132 had partial |
| ✅ | `anchor-positioning-quirks/default-anchor-resolution.md` | esoteric | WebKit 283295 evaluation of default anchor elements |
| ✅ | `anchor-positioning-quirks/popover-margins-interaction.md` | esoteric | UA-style margin interferes; CSSWG actively adjusting |

### js-language-status/ (8)

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `js-language-status/iterator-helpers.md` | canonical | Stage 4; Chrome 122 / Firefox 131 / Safari 18.4 |
| ✅ | `js-language-status/set-methods.md` | canonical | Stage 4 / Baseline June 2024; Chrome 122 / Firefox 127 / Safari 17 |
| ✅ | `js-language-status/regexp-v-flag.md` | canonical | Stage 4; Chrome 112 / Firefox 116 / Safari 17 |
| ✅ | `js-language-status/temporal.md` | canonical | Stage 4 (March 2026); Firefox 139 / Chrome 144 / Safari pending |
| ✅ | `js-language-status/decorators.md` | extended | Stage 3; Babel `2023-11` / TypeScript 5+ stable |
| ✅ | `js-language-status/pipeline-operator.md` | extended | Stage 2 (no progress 2025); Babel-only |
| ✅ | `js-language-status/shadowrealm.md` | extended | Stage 2.7 (NOT Stage 3); no native shipping yet |
| ✅ | `js-language-status/withdrawn-records-tuples.md` | advisory | Withdrawn April 14, 2025 at TC39 plenary; Composites is the successor |

### landscape-shifts/ (5)

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `landscape-shifts/polyfill-io-attack.md` | canonical | Funnull acquisition Feb 2024; first malware June 8, 2024 15:23:51 UTC; Sansec disclosure June 25, 2024; Namecheap suspension June 27, 2024 |
| ✅ | `landscape-shifts/core-js-funding-status.md` | advisory | Pushkarev funding crisis; latest core-js **3.49.0** (March 16, 2026); single-maintainer risk |
| ✅ | `landscape-shifts/cloudflare-cdnjs-polyfill.md` | extended | `cdnjs.cloudflare.com/polyfill`; auto-rewrite for free plans; announced Feb 29, 2024 (pre-attack) |
| ✅ | `landscape-shifts/fastly-polyfill-mirror.md` | extended | `polyfill-fastly.io` and `polyfill-fastly.net`; self-hosted repo deprecated 2026-01-14 |
| ✅ | `landscape-shifts/interop-2026-priorities.md` | extended | 20 focus areas; announced Feb 12, 2026; 5 carryovers from 2025 |

### anti-patterns/ (6)

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `anti-patterns/corejs-entry-modern.md` | advisory | `useBuiltIns: 'entry'` shipped to modern browsers; bundle bloat |
| ✅ | `anti-patterns/target-es5-modern.md` | advisory | `target: 'es5'` defeats modern engines |
| ✅ | `anti-patterns/defensive-overpolyfilling.md` | advisory | Polyfilling for browsers you don't support; `browserslist-plausible` / `browserslist-ga` for real-audience targeting |
| ✅ | `anti-patterns/pony-vs-feature-query.md` | advisory | Pony pattern when `@supports` would do; canonical `@supports (animation-timeline: scroll())` for scroll-driven animations; `@supports (color: oklch(0% 0 0))` for color-mix progressive enhancement |
| ✅ | `anti-patterns/preset-env-no-browserslist.md` | advisory | `@babel/preset-env` without targets falls back to `defaults` browserslist query (`> 0.5%, last 2 versions, Firefox ESR, not dead`), transforming all ES2015+ to ES5; 30-60 KB gzipped overhead at `defaults` vs modern baseline |
| ✅ | `anti-patterns/polyfill-io-after-attack.md` | canonical | Cloudflare/Fastly mirror still load 3rd-party JS; consider self-hosting |

### feature-detection/ (5)

| Status | Path | Coverage | Purpose |
|---|---|---|---|
| ✅ | `feature-detection/at-supports-recipes.md` | canonical | `selector()`, `font-tech()`, `font-format()`, nested at-rule detection |
| ✅ | `feature-detection/js-feature-detection.md` | canonical | `typeof`, presence-checks, behavioral tests |
| ✅ | `feature-detection/progressive-enhancement.md` | extended | `@supports`-gated CSS, JS feature gating |
| ✅ | `feature-detection/ponyfill-pattern.md` | extended | Explicit-import vs global-pollution; sindresorhus's patterns |
| ✅ | `feature-detection/prollyfill-pattern.md` | advisory | Speculative shipping of pre-spec features |

## Conventions

- **YAML frontmatter** on every reference file: `date` (ISO), `coverage` (canonical/extended/esoteric/advisory), `peers`, `primary_sources`.
- **Browser version claims cite caniuse.com or MDN BCD.**
- **Bug claims cite Bugzilla / WebKit Bugzilla / Chromium Issues / Mozilla standards-positions.**
- **TC39 stage claims cite tc39/proposals or proposal-* repos.**
- **Polyfill recommendations cite npm version + GitHub repo + maintainer + license.**
- **Cross-references use relative paths** (e.g., `../meta/decision-tree.md`).

## Companion files at skill root

- [`SKILL.md`](../SKILL.md) — flat-prose entry, Invocation contract, cheat tables.
- [`CHANGELOG.md`](../CHANGELOG.md) — per-wave entries.
- [`skill.json`](../skill.json) — machine-readable manifest.
