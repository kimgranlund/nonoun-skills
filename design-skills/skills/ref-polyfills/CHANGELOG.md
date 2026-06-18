# Changelog

## 1.0.1 — 2026-05-07 — Improved Naming Convention

- Renamed from `expert-polyfills` to `ref-polyfills` per the ref- domain/verb convention.
- All cross-references updated.

## 0.2.0 — 2026-05-07 — Naming Convention Rename

- Renamed from `polyfills-expert` to `expert-polyfills` per the `expert-` domain/phase convention.
- All cross-references in downstream/upstream skills updated.

## [1.0.0] — 2026-04-27 — Wave 5 complete + v1.0.0 release (14 files)

**The expert-polyfills skill is complete.** 84 reference files / ~16,930 lines / 13 axes / 5 waves authored over a single day with parallel-agent dispatch and rigorous primary-source verification.

### Added — Wave 5 (14 reference files / ~2,260 lines)

**products/** (8 files / ~1,470 lines):
- `next-js-15.md` — Next 15/16 polyfill posture; **default browserslist is `chrome 111 / edge 111 / firefox 111 / safari 16.4`** (NOT the older default user spec assumed); **no `supportedBrowsers` config option exists** in Next.js — override is plain `package.json` `"browserslist"`; **Next.js DOES auto-inject polyfills** via `next-polyfill-nomodule` (`<script nomodule>`, no cost on modern browsers); Next 16 (Oct 2025) Turbopack stable as default
- `vite-6.md` — Vite 5/6/7 matrix preserved; 6.0 = Nov 26, 2024; 7.0 = June 24, 2025 (default `'baseline-widely-available'`); `@vitejs/plugin-legacy` for sub-baseline split builds
- `react-router-v7.md` — Vite-based; **TextEncoderStream** Chrome 71+ / Safari 14.1+ / Firefox 105+ — fully native at our baseline
- `astro.md` — Astro 5 (Dec 2024) and Astro 6 (Vite 7 + Environment API); islands architecture means most pages have zero polyfill concerns
- `sveltekit.md` — Svelte 5 (Oct 19, 2024) ~6KB runtime; SvelteKit 2 Vite-based; minimal runtime; no automatic core-js; built-in service worker support adds no polyfill burden
- `nuxt.md` — Nuxt 4 (released July 15, 2025; 4.4.2 current); Vue 3 (Proxy reactivity, native `<Suspense>`/`<Teleport>` are Vue components not browser features); Nitro v3 beta; 25+ deploy presets are server-only
- `solidstart.md` — SolidStart 1.x (v1.1.0 "Gear 5" on Vite 6); v2.0.0-alpha.2 in development with "DeVinxi" replacing Vinxi; ~7KB runtime; Babel role is JSX-only
- `web-components-frameworks.md` — Lit 3.3.x (~5KB ES2021); Stencil 4.43.4 (April 2026); Microsoft FAST maintenance posture; **stop shipping `@webcomponents/webcomponentsjs`** — loads code no modern engine needs; **Scoped Custom Element Registries: Safari 26 (Sept 15, 2025) + Chrome 146 (March 10, 2026) ship native, but Firefox does NOT** — `@webcomponents/scoped-custom-element-registry` polyfill required for Firefox users; documents the Firefox event-propagation caveat (webcomponents/polyfills#580)

**anti-patterns/** tail (3 files / ~936 lines):
- `defensive-overpolyfilling.md` — Polyfilling for browsers you don't support; `browserslist-plausible` and `browserslist-ga` for real-audience targeting
- `pony-vs-feature-query.md` — Pony pattern when `@supports` would do; canonical `@supports (animation-timeline: scroll())` for scroll-driven animations; `@supports (color: oklch(0% 0 0))` for color-mix progressive enhancement
- `preset-env-no-browserslist.md` — `@babel/preset-env` without targets falls back to `defaults` browserslist query (`> 0.5%, last 2 versions, Firefox ESR, not dead`), transforming all ES2015+ to ES5; **30–60 KB gzipped overhead** at `defaults` vs modern baseline (DebugBear measurement); 100KB+ figures from Babel preset-modules issue #7

**runtime-polyfills/** final (3 files / ~835 lines):
- `array-grouping.md` — `Object.groupBy` / `Map.groupBy` Baseline Newly Available **March 2024** (Safari 17.4 was the gating engine); rename history (Sugar.js webcompat collision broke ~660 origins → `Array.prototype.group` → static methods on `Object`/`Map`); inline shim provided; **stop-polyfilling verdict** at our baseline
- `compression-streams.md` — Native Chrome 80 (Feb 2020), Safari 16.4 (March 27, 2023), Firefox 113 (May 9, 2023); Baseline Widely Available since ~Nov 2025; **stop-polyfilling verdict** — migrate off `pako` (~22 KB) at baseline; three concrete pako→native migration patterns; Brotli partial support (Safari 18.4 only)
- `error-iserror-promise-try.md` — Bundles five small ES2025/2026 finishers: `Promise.withResolvers` (universal native — stop polyfilling), `Promise.try` (Stage 4 Oct 2024, shipping Chrome 128 / Safari 18.2 / Firefox 134), `Error.isError` (Stage 4 May 28, 2025, in-flight), `RegExp.escape` (Stage 4 Feb 18, 2025, shipping Chrome 136 / Safari 18.2 / Firefox 134), `Float16Array` (Stage 4 Feb 18, 2025; `@petamoriken/float16` is canonical ponyfill); `escape-string-regexp` v5.0.0 by Sindre Sorhus (244M+ downloads)

### Notable corrections caught during Wave 5 authoring

1. **Next.js default browserslist** is `["chrome 111", "edge 111", "firefox 111", "safari 16.4"]` per Next docs (last updated 2026-04-23, Next 16.2.4) — NOT the older `chrome 64+ / edge 79+ / firefox 67+ / opera 51+ / safari 12+` default brief assumed.
2. **No `supportedBrowsers` config option exists in Next.js.** Confirmed false lead. Override is plain `package.json` `"browserslist"`.
3. **Next.js DOES inject polyfills automatically** — `fetch()`, `URL`, `Object.assign()` via `next-polyfill-nomodule`, delivered as a `<script nomodule>` chunk. User spec said "no automatic core-js inclusion" — correct for core-js but missed the nomodule polyfill bundle.
4. **Object.groupBy Baseline date**: March 2024 (Safari 17.4 was the gating engine), not just "March 2024" generic.
5. **Sugar.js webcompat collision**: Renaming `Array.prototype.groupBy` to `group` was driven by ~660 origins breaking — load-bearing context for the static-method on Object/Map redesign.

### Why v1.0.0 (release notes)

**Skill complete and ready for production.** Coverage:

- 13 axes: meta, runtime-polyfills, css-polyfills-and-shims, transpilation, build-tools, products, css-color-bugs, popover-quirks, anchor-positioning-quirks, js-language-status, landscape-shifts, anti-patterns, feature-detection
- 84 dated reference files with primary-source citations (caniuse, MDN BCD, vendor changelogs, vendor bug trackers, W3C/WHATWG specs)
- ~16,930 lines of opinionated, baseline-calibrated guidance
- User-flagged priorities (CSS color bugs, Popover API quirks) given the canonical Wave 3 treatment with 20 esoteric-bug files
- Polyfill.io supply-chain attack (June 2024), core-js single-maintainer crisis, and Records & Tuples withdrawal documented as load-bearing landscape facts
- Primary-source corrections at every wave — see corrections sections in each version entry

**Open issue carried into v1.0:**

- **SWC decorator version label discrepancy**: `js-language-status/decorators.md` says SWC implements `decoratorVersion: "2022-03"`; `transpilation/decorators-stage-3.md` says SWC 1.11+ ships `"2023-11"`. Both may be partially true (SWC supports multiple versions via `jsc.experimental.decoratorVersion`). Reconcile against SWC v1.11.x release notes in next maintenance pass.

### Bookkeeping

- `skill.json` → v1.0.0; status `complete`; `files[]` = 84 entries; description and notes updated with v1.0.0 release record.
- `references/INDEX.md` — 14 statuses flipped ⬜→✅; Wave 5 row marked ✅; v1.0.0 release row added.
- This `CHANGELOG.md` entry consolidates Wave 5 + v1.0.0 release.
- All v0.x entries preserved below for historical accuracy.

### Final wave summary

| Wave | Files | Lines | Date completed |
|---|---|---|---|
| Scoping survey | — | — | 2026-04-27 |
| Wave 1 — Foundations + landscape | 16 | ~3,162 | 2026-04-27 |
| Wave 2 — JS + transpilation | 18 | ~3,274 | 2026-04-27 |
| Wave 3 — Esoteric bugs (USER-FLAGGED) | 20 | ~3,494 | 2026-04-27 |
| Wave 4 — CSS + features + tools | 16 | ~3,726 | 2026-04-27 |
| Wave 5 — Products + completion | 14 | ~2,260 | 2026-04-27 |
| **v1.0.0 release** | **84** | **~16,930** | **2026-04-27** |

---

## [0.5.0] — 2026-04-27 — Wave 4 complete (16 files): CSS shims + build-tools tail + feature-detection

### Added (16 reference files / ~3,726 lines)

**css-polyfills-and-shims/** (7 files / 1,370 lines):
- `anchor-positioning-polyfill.md` — `@oddbird/css-anchor-positioning` v0.9.0 (BSD-3-Clause); cross-shadow-root unsupported (#191), constructed stylesheets unsupported (#228), `position-try-order` parsed-but-ignored
- `popover-polyfill.md` — `@oddbird/popover-polyfill` v0.6.1 (BSD-3-Clause, ~3KB gzipped); used at GitHub in collab with Keith Cirkel
- `scroll-timeline-polyfill.md` — `flackr/scroll-timeline` (Apache-2.0, Robert Flack/Google); needed for Firefox at our baseline (still flag-gated April 2026)
- `view-transitions.md` — Same-doc Baseline Newly Available **October 14, 2025** (Firefox 144); cross-doc `@view-transition` Chromium 126+ AND Safari 18.2+ (correction — earlier brief said Chromium-only)
- `at-property-fallbacks.md` — `@property` Baseline since July 9, 2024; `@scope` Baseline only with Firefox 146 (Dec 9, 2025) — 17-version Firefox gap, no real polyfill exists
- `lightningcss-css-lowering.md` — At our baseline: ~zero output bytes vs source for most CSS (everything's already native)
- `postcss-preset-env-stages.md` — At our baseline: useful primarily for `@custom-media` and `@custom-selectors` (Stage 2, native nowhere); `enableClientSidePolyfills: false` recommended

**build-tools/** tail (3 files / 934 lines):
- `esbuild-config.md` — Bundling surface beyond `target`: `format`, `bundle`, `splitting` (ESM-only + needs `outdir`), `external` for peer deps, sourcemap modes, watch→context API migration in v0.17 (Jan 2023). Reminder: esbuild does NOT inject polyfills (#3803)
- `tsconfig-lib-target.md` — `lib` deep dive (companion to `transpilation/typescript-target-esnext.md`'s `target` focus); default `lib` per `target`; mismatch trap; sub-bundle enumeration; DOM vs WebWorker mutual exclusion
- `tailwind-v4-floor.md` — Hard floor Chrome 111 / Safari 16.4 / Firefox 128 verified via tailwindcss.com/docs/compatibility; Tailwind 3.4 EOL Feb 28, 2027

**runtime-polyfills/** tail (1 file / 291 lines):
- `cookie-store-api.md` — Chrome 87+ (long), Safari 18.4 (March 31, 2025), Firefox 138 (April 29, 2025). Polyfill window: Safari 17.4–18.3 + Firefox 129–137. Firefox/Safari subset agreement (whatwg/cookiestore#241): no `CookieStoreManager`, no SW registration cookies. `markcellus/cookie-store` covers Window scope only

**feature-detection/** (5 files / 1,131 lines):
- `at-supports-recipes.md` (canonical) — Full `@supports` syntax (selector(), font-tech(), font-format(), at-rule()); Chromium 148+ has `@supports at-rule(@keyword)` only; `:has()` empty-arg gotcha
- `js-feature-detection.md` (canonical) — `'feature' in obj`, `typeof`, behavioral tests; dynamic-import patterns; Object.groupBy / Map.groupBy NOT Array.groupBy gotcha
- `progressive-enhancement.md` — vs graceful degradation; design-for-the-floor mindset
- `ponyfill-pattern.md` — Sindre Sorhus's [`sindresorhus/ponyfill`](https://github.com/sindresorhus/ponyfill) is canonical anchor; Nicolás Bevacqua popularized via Pony Foo; es-shims `/auto`, `/shim`, `/polyfill` entry-point convention
- `prollyfill-pattern.md` — **Brian Kardell** coined "prollyfill" circa 2013-14 (Extensible Web CG chair) — NOT Alex Russell as earlier docs suggested. Russell co-authored Extensible Web Manifesto

### Notable corrections caught during Wave 4

1. **"Prollyfill" attribution**: Brian Kardell (W3C Extensible Web CG chair, ~2013-14), not Alex Russell. Russell co-authored the Extensible Web Manifesto (the philosophical container) but didn't coin the term.
2. **Cross-doc View Transitions**: Safari **18.2+ ships `@view-transition`** rule, not Chromium-only as earlier docs suggested. Firefox still pending (Interop 2026).
3. **Cookie Store Firefox**: Firefox 138 (April 29, 2025), not 138+ as a generic claim — exact ship date verified.
4. **`@scope` Firefox status**: Reached Firefox 146 (Dec 9, 2025); 17-version gap on Firefox at our floor; no real polyfill exists — feature-query + flat fallback is the only path.
5. **esbuild watch API**: Moved to context API in v0.17 (Jan 2023). Pre-v0.17 watch syntax is broken; old tutorials propagate the wrong syntax.

### Bookkeeping

- `skill.json` → v0.5.0; `files[]` extended with 16 new paths.
- `references/INDEX.md` — 16 statuses flipped ⬜→✅; Wave 4 status flipped ✅; Wave 5 marked next; verified-fact entries enriched.

### Wave 5 plan — Products + completion (14 files)

- `products/` (8): next-js-15, vite-6, react-router-v7, astro, sveltekit, nuxt, solidstart, web-components-frameworks
- `anti-patterns/` tail (3): defensive-overpolyfilling, pony-vs-feature-query, preset-env-no-browserslist
- `runtime-polyfills/` final (3): array-grouping, compression-streams, error-iserror-promise-try

4 parallel agents.

---

## [0.4.0] — 2026-04-27 — Wave 3 complete (20 files): the esoteric-bugs core (USER-FLAGGED)

### Added (20 reference files / ~3,494 lines)

**css-color-bugs/** (8 files / 1,411 lines, mostly esoteric):
- `oklch-oklab-safari.md` — Safari < 18 OKLCH `color-mix` red-shift; Tailwind PR #15201 (merged Nov 27, 2024); WebKit Bugzilla 255939; **iOS Safari IS affected** (corrected from earlier brief)
- `color-mix-interpolation.md` — Chrome ↔ Safari OKLCH hue-value divergence; csswg-drafts #10484; canonical example: 264° spec / 323.92° Chrome / 177° Safari
- `light-dark-color-scheme.md` — Silent no-op without `color-scheme: light dark`; #1 dark-mode bug
- `contrast-color-availability.md` — **Chrome 147 (April 7, 2026) shipped — TOO NEW for our 125+ baseline**; Safari 26+, Firefox 146+
- `display-p3-firefox-lag.md` — Firefox renders P3 as sRGB; `@media (color-gamut: p3)` always false; Mozilla Bugzilla 1626624 (open since 2020); MDN BCD issue 21422
- `relative-color-syntax.md` — Universal at baseline; achromatic NaN gotcha; canonical detection `@supports (color: rgb(from white r g b))`
- `currentcolor-resolution.md` — Computed-value resolution timing; shadow DOM, programmatic mutations, `@property` for animation
- `wide-gamut-fallbacks.md` — `@supports`-based progressive enhancement vs broken `@media (color-gamut: p3)` in Firefox

**popover-quirks/** (7 files / 1,083 lines, mostly esoteric):
- `ios-safari-light-dismiss.md` — WebKit Bug 267688 RESOLVED FIXED commit `285990@main` (Tim Nguyen, Oct 31 2024); shipped **Safari 18.3 (Jan 27, 2025)** [NOT 18.4 as earlier brief assumed]; polyfill window: iOS Safari 17.0–18.2 (10 months)
- `safari-focus-inputs.md` — Distinct from Bug 267688; mechanism = virtual keyboard scrolls viewport → light-dismiss heuristic fires; persists past Safari 18.3; react-spectrum #7579
- `safari-184-tab-hang.md` — **Safari 18.4 (March 31, 2025) fixed** the tab-out hang; commits `c5c4b9c5` and `d8c15ed2`; bug ID 143145544
- `popover-vs-dialog-toplayer.md` — Two gotchas: popover-outside-modal-dialog inerts; z-index meaningless inside top layer; WHATWG #9936 still OPEN at April 2026
- `popover-hint-chromium-only.md` — Chrome 133 (Feb 4, 2025), Edge 133, Firefox 149, Safari none at 26.5; fallback parses to `auto`; OddBird polyfill v0.6+
- `popovertarget-vs-showpopover.md` — Four divergences: implicit ARIA, focus restoration, `popovertarget` in `<form>` (Safari 18.2 fix), `beforetoggle` non-cancelability
- `popover-anchor-crash.md` — WebKit Bug 279588 filed Sept 12 2024, fixed Oct 17 2024 (commit `ba8e7f0`); **NEVER shipped to stable Safari** — TP/nightlies only for ~5 weeks; documented for historical completeness

**anchor-positioning-quirks/** (5 files / ~700-1000 lines, esoteric+extended):
- `inset-area-rename.md` — Chrome **131** (not 132) removed `inset-area`; dual-name window was Chrome 129–130; also `position-try-options` → `position-try-fallbacks` rename in Chrome 128
- `safari-26-anchor-shipped.md` — Safari 26.0 (Sept 15, 2025) shipped FULL surface including `@position-try` (corrected — earlier brief assumed 26.0 lacked it); Safari 18.2 did NOT ship anchor positioning at all (also corrected)
- `firefox-147-anchor-shipped.md` — Firefox 147 (Jan 13, 2026) flipped flag via Bug 1988225; ESR 140 has zero anchor support (enterprise note)
- `default-anchor-resolution.md` — WebKit Bug 283295 RESOLVED FIXED Feb 18, 2025 (commit 290534@main); landed before Safari 26.0
- `popover-margins-interaction.md` — UA-stylesheet `inset: 0; margin: auto` collides with `position-area`; CSSWG resolved (issue #10258) but not yet shipped

### Notable corrections caught during Wave 3 authoring

1. **Safari 18.3 (Jan 27, 2025) fixed light-dismiss** [WebKit Bug 267688], NOT Safari 18.4 as earlier docs assumed. Safari 18.4 (March 31, 2025) is the separate tab-hang fix.
2. **Chrome 131 removed `inset-area`**, not Chrome 132. Dual-name acceptance window was Chrome 129–130 only.
3. **Safari 26.0 (Sept 15, 2025) shipped `@position-try`** in 26.0 itself (not requiring 26.1). Earlier assumption that Safari 18.2 had partial anchor support was wrong — Safari 18.2 had no anchor support at all.
4. **iOS Safari IS affected by Safari < 18 OKLCH `color-mix` bug** — brief said NOT iOS; iOS shares WebKit build with matching macOS. Patched in `css-color-bugs/oklch-oklab-safari.md`.
5. **Chrome 147 (April 7, 2026) shipped `contrast-color()`** — too new for our 125+ baseline; the SKILL.md previously said "Chrome stable does not ship" which is now stale. **Patched in SKILL.md.**
6. **WebKit Bug 279588 (popover-anchor crash)** never shipped to stable Safari — TP/nightlies only for ~5 weeks; historical interest only.
7. Mozilla **ESR 140 has zero anchor positioning support** — important advisory for enterprise audiences.

### Patched in SKILL.md

- `contrast-color()` row in DO-polyfill table: shipping reality per Chrome 147 / Safari 26 / Firefox 146.
- `popover-quirks/` row in browser-bugs table: Safari 18.3 (not 18.4) for light-dismiss fix; iOS focus-inputs distinct mechanism.
- `inset-area-rename` row: Chrome **131** removed it, not Chrome 132.

### Bookkeeping

- `skill.json` → v0.4.0; `files[]` extended with 20 new paths.
- `references/INDEX.md` — 20 statuses flipped ⬜→✅; Wave 3 status flipped to ✅; Wave 4 marked next.
- `SKILL.md` — three quick-reference table corrections (above).

### Wave 4 plan — CSS + features + tools (16 files)

- `css-polyfills-and-shims/` (7) — anchor-positioning-polyfill, popover-polyfill, scroll-timeline-polyfill, view-transitions, at-property-fallbacks, lightningcss-css-lowering, postcss-preset-env-stages
- `build-tools/` tail (3) — esbuild-config, tsconfig-lib-target, tailwind-v4-floor
- `feature-detection/` (5) — at-supports-recipes, js-feature-detection, progressive-enhancement, ponyfill-pattern, prollyfill-pattern
- `runtime-polyfills/` tail (1) — cookie-store-api

4 parallel agents.

---

## [0.3.0] — 2026-04-27 — Wave 2 complete (18 files)

### Added (18 reference files / ~3,274 lines)

**js-language-status/** (8 files / 1,158 lines):
- `iterator-helpers.md` (canonical) — Stage 4 ES2025; Chrome 122 / Firefox 131 / Safari 18.4 (March 31, 2025); Baseline Newly Available March 31, 2025
- `set-methods.md` (canonical) — Stage 4 = April 8, 2024 plenary; Safari 17 first / Chrome 122 / Firefox 127; Baseline June 11, 2024; **stop-polyfilling verdict** at this baseline
- `regexp-v-flag.md` (canonical) — Stage 4 ES2024; universal at baseline; cross-reference to RegExp.escape (Stage 4 Feb 18, 2025)
- `temporal.md` (canonical) — Stage 4 March 11, 2026 plenary (113th NYC); Firefox 139 / Chrome 144 / Safari pending
- `decorators.md` (extended) — Stage 3 "2023-11"; three-draft history; TypeScript 5.0 (March 16, 2023) introduced standard decorators
- `pipeline-operator.md` (extended) — Stage 2 since 2021; Hack-style with `%` placeholder; **no plenary movement in 2024-2025**; skip until Stage 3
- `shadowrealm.md` (extended) — Stage 2.7 since Feb 7, 2024 (NOT demoted in 2025); Dec 2024 Stage 3 attempt deferred; use Workers / iframes instead
- `withdrawn-records-tuples.md` (advisory) — WITHDRAWN April 14, 2025 plenary; repo archived April 15, 2025; **Composites** is Stage 1 successor

**transpilation/** (6 files / 1,089 lines):
- `babel-preset-env.md` (canonical) — `useBuiltIns: 'usage'` recipe; `corejs: { version: '3.49' }`; bugfixes default in Babel 8 (opt-in in 7); shippedProposals; full config example
- `swc-targets.md` (canonical) — `.swcrc` env.targets, browserslist auto-discovery since v1.1.10, ES2024 target since v1.8.0; `env.coreJs` is a string (not Babel's object)
- `esbuild-targets.md` (canonical) — Lowercase target syntax `chrome125`/`safari17.4`/`firefox129`; **NO browserslist support** — use `browserslist-to-esbuild` (marcofugaro/marcofugaro v2.1.1)
- `typescript-target-esnext.md` (canonical) — TS 5.7 (Nov 2024) added ES2024 target/lib; `target: "ES2022"` recommended; `experimentalDecorators: false` for standard decorators; `useDefineForClassFields: true` default at ES2022+
- `transform-runtime-vs-preset-env.md` (extended) — App vs library split; mutual exclusion; `useESModules` deprecated in Babel 8
- `decorators-stage-3.md` (extended) — Babel 8 will drop older decorator versions (only `2023-11` + `legacy` survive); **esbuild has zero decorator support** (#3482); `emitDecoratorMetadata` is esbuild gap; library compatibility table

**build-tools/** (4 files / 1,027 lines):
- `vite-build-target.md` (canonical) — **Vite 7+ default** `'baseline-widely-available'` (Vite 6 added option as opt-in; Vite 7 made default June 24, 2025) → `['chrome111', 'edge111', 'firefox114', 'safari16.4']`. Recommend explicit target at our baseline
- `lightningcss-features.md` (canonical) — 24-bit semver-per-byte target object format; per-feature "active at baseline?" matrix; Vite 6+ uses Lightning CSS by default
- `postcss-preset-env.md` (extended) — cssdb stages (Aspirational/Experimental/Allowable/Embraced/Standardized); default stage 2; `enableClientSidePolyfills` option; at our baseline only `@custom-media` worth lowering
- `browserslist-recipes.md` (canonical) — Canonical baseline query; Edge/mobile/Samsung/Opera expansions; production recipes (web app, library, mobile-first, internal tool, Baseline-aware); per-tool support matrix (Babel/SWC full; esbuild and tsc none)

### Notable corrections caught during Wave 2 authoring

1. **Vite default version**: Scoping survey + Wave 1 said "Vite 6+ default `'baseline-widely-available'`". Verified via vite.dev/blog/announcing-vite7: option was added in Vite 6 (Nov 26, 2024) but only became DEFAULT in Vite 7 (June 24, 2025). **Patched in INDEX.md, skill.json**. CHANGELOG v0.1.0 entry preserved as-is for historical accuracy.
2. **Safari 18.4 ship date**: Wave 1's `runtime-polyfills/iterator-helpers.md` used April 3, 2025. Wave 2A verified March 31, 2025 against WebKit blog and web.dev/baseline-iterator-helpers. **Patched in `runtime-polyfills/iterator-helpers.md`** (line 65).
3. **`browserslist-to-esbuild` author**: marcofugaro (not "marsidev" as in earlier brief). Latest 2.1.1, MIT.
4. **SWC `env.coreJs` shape**: String (e.g. `"3.49"`), NOT Babel's `{ version, proposals }` object form.
5. **TypeScript 5.0**: March 16, 2023 ship; `experimentalDecorators: false` at TS 5+ enables standard Stage 3 decorators.
6. **ShadowRealm stage history**: Stage 2.7 since Feb 7, 2024. NOT demoted in 2025 — Dec 2024 Stage 3 attempt deferred; Feb 2025 plenary said "TC39 side resolved, web-integration interest pending."

### Discrepancy flagged for v1.0.0 reconciliation

**SWC decorator version label**:
- Wave 2B's `js-language-status/decorators.md` says SWC implements `decoratorVersion: "2022-03"` (older spec).
- Wave 2D's `transpilation/decorators-stage-3.md` says SWC 1.11+ ships `"2023-11"` (current spec).

These claims contradict. Likely both are partially true (SWC may support multiple via `jsc.experimental.decoratorVersion`). **Verify against SWC v1.11.x release notes during v1.0.0 link-verification pass.**

### Bookkeeping

- `skill.json` → v0.3.0; `files[]` extended with 18 new paths; notes updated.
- `references/INDEX.md` — 18 statuses flipped ⬜→✅; Vite version reference corrected; Wave 2 status flipped to ✅; Wave 3 marked next.
- `runtime-polyfills/iterator-helpers.md` — Safari 18.4 date corrected (April 3 → March 31, 2025).

### Wave 3 plan — Esoteric bugs (20 files, USER-FLAGGED PRIORITY)

- `css-color-bugs/` (8) — Safari OKLCH mix bug, Chrome↔Safari hue divergence, light-dark color-scheme gotcha, contrast-color shipping status, Display P3 Firefox lag, relative color syntax gating, currentColor resolution, wide-gamut fallbacks
- `popover-quirks/` (7) — iOS light-dismiss WebKit Bug 267688, Safari focus-input bug, Safari < 18.4 tab-hang, popover-vs-dialog top-layer, popover="hint" Chromium-only, popovertarget vs showPopover, popover-anchor crash WebKit Bug 279588
- `anchor-positioning-quirks/` (5) — inset-area→position-area rename Chrome 129, Safari 26 anchor shipped, Firefox 147 (Jan 2026) shipped, default-anchor resolution WebKit 283295, popover-margins interaction

5-6 parallel agents.

---

## [0.2.0] — 2026-04-27 — Wave 1 complete (16 files)

### Added (16 reference files / ~3,162 lines)

**meta/** (4 files, 1,055 lines, all canonical):
- `glossary.md` — polyfill / ponyfill / prollyfill / shim / transpiler / lowering / Sindre Sorhus's pony pattern / Alex Russell's prollyfill term
- `baseline-glossary.md` — Web Platform Baseline; Newly Available vs Widely Available (30-month threshold); Baseline 2024/2025 cohorts; Vite 6 `'baseline-widely-available'` keyword
- `the-modern-baseline.md` — Chrome 125 / Safari 17.4 / Firefox 129 ship dates; what's native at baseline; what's polyfill candidate; mobile WebView caveats
- `decision-tree.md` — 7-step "do I need a polyfill?" flowchart with prose

**landscape-shifts/** (5 files, 762 lines, 8,547 words; 1 canonical / 1 advisory / 3 extended):
- `polyfill-io-attack.md` — Andrew Betts public warning Feb 25, 2024; first malicious response June 8, 2024 15:23:51 UTC; Sansec disclosure June 25; Namecheap suspension June 27; Censys 384,773 dangling-host count July 2; full IOC list
- `core-js-funding-status.md` — Pushkarev sole maintainer since 2014; Feb 14, 2023 funding statement; ~$2,500/mo → ~$400/mo income drop due to Western sanctions; ~10 months prison 2020 (motorcycle accident, multiply reported); **latest core-js 3.49.0 (March 16, 2026)**
- `cloudflare-cdnjs-polyfill.md` — `cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js` announced Feb 29, 2024 (pre-attack)
- `fastly-polyfill-mirror.md` — `polyfill-fastly.io` and `polyfill-fastly.net`; self-hosted repo deprecated 2026-01-14
- `interop-2026-priorities.md` — 20 focus areas announced Feb 12, 2026 jointly by Apple / Google / Igalia / Microsoft / Mozilla; 5 carryovers (anchor positioning, CSS zoom, Navigation API, View Transitions, WebRTC); 4 investigations (Accessibility Testing, JPEG XL, Mobile Testing, WebVTT)

**runtime-polyfills/** (4 files, 666 lines; 2 canonical / 2 extended):
- `temporal-api.md` — Stage 4 Mar 11, 2026; Firefox 139 (May 27, 2025) first; Chrome 144 (Jan 13, 2026); Safari pending; `@js-temporal/polyfill` v0.5.1 ISC ~52KB; `temporal-polyfill` (FullCalendar) v0.x MIT ~20KB
- `urlpattern.md` — Chrome 95 (Oct 2021); Safari 26.0 (Sep 2025); **Firefox 142 (Aug 19, 2025)** [scoping survey said 144 — corrected]; `urlpattern-polyfill` v10.1.0 MIT ~6KB
- `iterator-helpers.md` — Stage 4 Oct 2024; Chrome 122 / Firefox 131 / Safari 18.4; Baseline Newly Available Mar 31, 2025; `es-iterator-helpers` v1.2.1 MIT
- `set-methods.md` — Stage 4 April 2024; Safari 17 / Chrome 122 / Firefox 127; **stop-polyfilling verdict** at this baseline

**anti-patterns/** (3 files, 679 lines; 1 canonical / 2 advisory):
- `corejs-entry-modern.md` — `useBuiltIns: 'entry'` shipped to modern = 30-100KB bloat; migration ladder `'entry'`→`'usage'`→`false`→drop Babel; before/after `babel.config.js`; 7-step checklist
- `target-es5-modern.md` — `target: 'es5'` in 2026 = ~50% perf hit on V8/JSC/SpiderMonkey fast paths; regenerator-runtime ~7KB hidden cost; recommended `ES2022` or `ESNext`
- `polyfill-io-after-attack.md` — Cloudflare/Fastly mirrors are partial fix; durable answer is self-host or delete the request; CSP `script-src 'self'` lockdown; 5-step migration playbook

### Notable corrections caught during Wave 1

1. **URLPattern Firefox shipping version**: Scoping survey said Firefox 144. Mozilla release notes confirm Firefox **142** (Aug 19, 2025). Polyfill window: Firefox 129–141, not 129–143. **Patched in SKILL.md, INDEX.md, skill.json.**
2. **core-js latest version**: Scoping survey said 3.47.0 (Jan 7, 2026). GitHub releases confirm **3.49.0 (March 16, 2026)**. Patched in INDEX.md and skill.json.
3. **`@js-temporal/polyfill` size**: Scoping survey said ~60KB; Bundlephobia returns ~52KB for v0.5.1. Updated in `runtime-polyfills/temporal-api.md`. Also surfaced FullCalendar's `temporal-polyfill` fork at ~20KB as a smaller alternative.
4. **`light-dark()` Safari edge case**: Safari 17.5 closed `light-dark()` (May 2024). Our floor is 17.4 — users at exactly 17.4 hit unsupported `light-dark()`. Documented in `meta/the-modern-baseline.md` as a baseline-floor edge case requiring feature-query gating.

### Bookkeeping

- `skill.json` → v0.2.0; `files[]` extended with 16 new paths; URLPattern Firefox version corrected; notes updated.
- `references/INDEX.md` — 16 statuses flipped ⬜→✅; URLPattern entry corrected; core-js version corrected; landscape-shift entries enriched with verified dates.
- `SKILL.md` — URLPattern row corrected (Firefox 142 / 129–141 polyfill window).

### Wave 2 plan — JS + transpilation core (18 files)

- `js-language-status/` (8): iterator-helpers, set-methods, regexp-v-flag, temporal, decorators, pipeline-operator, shadowrealm, withdrawn-records-tuples
- `transpilation/` (6): babel-preset-env, swc-targets, esbuild-targets, typescript-target-esnext, transform-runtime-vs-preset-env, decorators-stage-3
- `build-tools/` first half (4): vite-build-target, lightningcss-features, postcss-preset-env, browserslist-recipes

5-6 parallel agents.

---

## [0.1.0] — 2026-04-27 — Skeleton + scoping survey complete

### Scoping survey

One agent, ~50 web queries spread across 12 research-survey areas. Verified primary sources for every fact below; no fabricated bug IDs / dates / version numbers. See the verified-facts table at scoping survey output (preserved in this CHANGELOG).

### Axes proposed (13)

1. `meta/` (4 files) — glossary, baseline definition, decision tree
2. `runtime-polyfills/` (8) — JS runtime polyfills the baseline still needs
3. `css-polyfills-and-shims/` (7) — CSS feature lowering + runtime shims
4. `transpilation/` (6) — Babel, SWC, esbuild, TypeScript build-time transformation
5. `build-tools/` (7) — Vite, lightningcss, postcss-preset-env, browserslist, tsconfig, Tailwind v4
6. `products/` (8) — per-framework polyfill story
7. **`css-color-bugs/`** (8) — **user-flagged priority** — CSS color function bugs at baseline
8. **`popover-quirks/`** (7) — **user-flagged priority** — Popover API quirks at baseline
9. `anchor-positioning-quirks/` (5) — interop and rename history
10. `js-language-status/` (8) — TC39 stage map + current shipping state
11. `landscape-shifts/` (5) — polyfill.io attack, core-js, mirrors, Interop 2026
12. `anti-patterns/` (6) — what NOT to do
13. `feature-detection/` (5) — `@supports`, JS detection, ponyfill / prollyfill patterns

**Total file target: 84.** Mirrors expert-typography (59), expert-genui (88), expert-dashboard (101) in capability-mode discipline.

### Notable findings (load-bearing facts seeded by scoping)

#### Polyfill landscape (the news)

- **polyfill.io supply-chain attack**: Funnull (Chinese entity) acquired the domain Feb 2024; Sansec disclosed malware injection June 25, 2024; Namecheap suspended the domain June 27, 2024. **100K+ sites affected.** Cloudflare runs `cdnjs.cloudflare.com/polyfill` as a free mirror with auto-rewrite for proxied sites; Fastly runs `polyfill-fastly.io` and `polyfill-fastly.net`. **Even via these mirrors, polyfill.io is 3rd-party JS — self-host is the actual best practice.**
- **core-js single-maintainer crisis**: Denis Pushkarev's funding situation remains unresolved. Latest core-js 3.47.0 released 2026-01-07. Most-used JS polyfill in the world; supply-chain risk noted.

#### TC39 / JS shipping (2024–2026)

- **Records & Tuples WITHDRAWN** April 14, 2025 at TC39 plenary; repo archived April 15, 2025. Successor proposal: **Composites**.
- **Iterator Helpers** Stage 4: Chrome 122 / Firefox 131 / Safari 18.4. ES2025.
- **Set methods** Baseline June 11, 2024: Chrome 122 / Firefox 127 / Safari 17.
- **Object.groupBy / Map.groupBy** Baseline March 2024: Chrome 117 / Firefox 119.
- **Promise.try** Baseline Newly Available January 2025: Firefox 134+.
- **Promise.withResolvers** Chrome 117 / Firefox 119 / Safari 17.4 / Node 20.12.
- **RegExp `v` flag** Chrome 112 / Firefox 116 / Safari 17.
- **RegExp.escape, Float16Array** Stage 4 February 18, 2025; ES2025.
- **Error.isError** Stage 4 (May 2025).
- **Array.fromAsync** Stage 4: Chrome 121 / Firefox 115 / Safari 16.4.
- **Explicit Resource Management (`using`)** Stage 4 (2025); Chrome 134+ shipped.
- **JSON modules / import attributes** Baseline Newly Available April 2025: Chrome 123 / Firefox 128 / Safari 17.2.
- **Temporal API** Stage 4 March 11, 2026 (ES2026); Firefox 139 (May 2025) / Chrome 144 (Jan 2026) / Safari pending. Polyfill: `@js-temporal/polyfill` (~60KB).
- **ShadowRealm** at Stage 2.7 (NOT Stage 3); no native shipping yet.
- **Pipeline operator** at Stage 2; no movement 2025; Babel-only.
- **Decorators** at Stage 3; `2023-11` Babel proposal version.

#### CSS shipping (2024–2026)

- **CSS Anchor Positioning**: Chrome 125+, Safari 26+, Firefox 147+ (Jan 13, 2026) closed the three-engine gap. `@position-try` needs Safari 18.4+. **`inset-area` renamed to `position-area` in Chrome 129; old name accepted only through Chrome 131.**
- **View Transitions** same-doc Baseline October 14, 2025 (Firefox 144); cross-doc Chromium-only at baseline.
- **Same-doc View Transitions** went Baseline Oct 2025.
- **`@scope`** Baseline-Newly-Available December 2025 (Safari 26.2 / Firefox 146).
- **Customizable `<select>`** (`appearance: base-select`) Chrome 135+ ONLY.
- **`popover="hint"`** Chrome 133+ ONLY.
- **`contrast-color()`** only in Safari TP / Firefox at April 2026; **NOT shipping in Chrome stable**.
- **Tailwind v4 (Oxide)** requires Chrome 111+, Safari 16.4+, Firefox 128+; no polyfill path below.
- **Vite 6+** default `build.target = 'baseline-widely-available'`: Chrome 111 / Edge 111 / Firefox 114 / Safari 16.4.

#### Browser-quirk highlights (the esoteric-bugs core)

- **Safari < 18 OKLCH `color-mix` red-shift bug.** Mixing color with transparent or gray in `color-mix(in oklch, ...)` interpolates as if Safari is doing LCH not OKLCH. Tailwind v4 PR #15201 fix: use `in oklab` for transparent/gray mixing.
- **Chrome ↔ Safari OKLCH hue divergence** in `color-mix(in oklch, ...)` (e.g., 264 vs 177 in known case).
- **Firefox renders `color(display-p3 ...)` mapped to sRGB.** `@media (color-gamut: p3)` always false in Firefox.
- **`light-dark()` requires `color-scheme: light dark`** on `:root` or relevant element. Common gotcha.
- **iOS/iPadOS popover light-dismiss broken at Safari 17.x** (WebKit Bug 267688).
- **iOS Safari**: focusing `<input>` inside popover closes popover (virtual keyboard scroll).
- **Safari < 18.4 hangs when tabbing out of a popover.** Fixed in 18.4.
- **`popover` inside modal `<dialog>` is inerted** (top-layer interaction).
- **z-index has no effect inside top-layer.** Popover and dialog both promote to top layer.
- **WebKit Bug 279588**: WebProcess crash when popover uses anchoring (fixed via display:none case).
- **Cross-document view transitions Chromium-only** at April 2026 baseline.
- **`@scope` in Firefox 129–145**: needs polyfill (no real polyfill exists; use feature query + flat fallback).
- **`shadowrootmode` standardized in Chrome 124**; older browsers used `shadowroot` attribute.
- **`scroll-driven` animations**: Safari 26+ shipped; Firefox needs flag at baseline.
- **`field-sizing: content`** editor's draft only.
- **`calc-size()` / `interpolate-size`**: Chromium 129+ ONLY at baseline.
- **`text-wrap: pretty`** no Firefox at baseline.
- **Scoped Custom Element Registries**: Safari 26 / Chrome 146 — Firefox does NOT support; needs `@webcomponents/scoped-custom-element-registry` polyfill at baseline.
- **Cookie Store API**: Safari 26.2+ / Firefox 138+ at April 2026; below those no good polyfill exists.

#### Vocabulary drift (must explicitly flag)

- `color-contrast()` → `contrast-color()` (renamed).
- `inset-area` → `position-area` (renamed Chrome 129; old through Chrome 131 only).
- `<selectlist>` → customizable `<select>` (`appearance: base-select`).
- `shadowroot` attribute → `shadowrootmode`.
- `polyfill.io` → Cloudflare/Fastly mirrors (with self-host advisory).
- `@babel/polyfill` (deprecated) → `@babel/preset-env` + `core-js@3` or `@babel/plugin-transform-runtime`.
- Records & Tuples (withdrawn) → Composites (successor).
- "modern" / "evergreen" / "last 2 versions" browserslist queries — none calibrated to this baseline.

### Wave plan

| Wave | Files | Focus |
|---|---|---|
| Wave 1 — Foundations + landscape | 16 | meta (4) + landscape-shifts (5) + runtime-polyfills core (4) + anti-patterns top half (3) |
| Wave 2 — JS + transpilation | 18 | js-language-status (8) + transpilation (6) + build-tools first half (4) |
| Wave 3 — Esoteric bugs | 20 | css-color-bugs (8) + popover-quirks (7) + anchor-positioning-quirks (5) — **user-flagged priority** |
| Wave 4 — CSS + features + tools | 16 | css-polyfills-and-shims (7) + build-tools tail (3) + feature-detection (5) + runtime-polyfills tail (1) |
| Wave 5 — Products + completion | 14 | products (8) + anti-patterns tail (3) + runtime-polyfills final (3) |

### Bookkeeping

- Skeleton scaffolded: `SKILL.md`, `skill.json` (v0.1.0), `references/INDEX.md`, this `CHANGELOG.md`.
- Wave 1 dispatching: 4 parallel agents covering 15 files (one slot held in reserve for the Wave 1 cheat-table SKILL.md polish).
- Status: `in-progress`.
