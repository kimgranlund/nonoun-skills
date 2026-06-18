---
date: 2026-04-27
coverage: canonical
peers:
  - ../meta/glossary.md
  - ../meta/baseline-glossary.md
  - ../meta/decision-tree.md
  - ../build-tools/browserslist-recipes.md
  - ../build-tools/vite-build-target.md
  - ../runtime-polyfills/temporal-api.md
  - ../runtime-polyfills/urlpattern.md
  - ../runtime-polyfills/iterator-helpers.md
  - ../css-polyfills-and-shims/anchor-positioning-polyfill.md
  - ../landscape-shifts/polyfill-io-attack.md
primary_sources:
  - https://developer.chrome.com/release-notes/125 — Chromium 125 release notes
  - https://developer.apple.com/documentation/safari-release-notes/safari-17_4-release-notes — Safari 17.4 release notes
  - https://www.mozilla.org/en-US/firefox/129.0/releasenotes/ — Firefox 129 release notes
  - https://en.wikipedia.org/wiki/Google_Chrome_version_history — Chromium version history (date verification)
  - https://en.wikipedia.org/wiki/Safari_version_history — Safari version history
  - https://en.wikipedia.org/wiki/Firefox_version_history — Firefox version history
  - https://web.dev/baseline — Web Platform Baseline definition
  - https://gs.statcounter.com/browser-version-market-share — Statcounter usage stats
  - https://web.dev/articles/baseline-and-polyfills — Baseline + polyfilling stance
  - https://caniuse.com — feature support data
---

# The Modern Baseline — what Chromium 125+ / Safari 17.4+ / Firefox 129+ means in practice

This is the load-bearing file. Every other claim in the expert-polyfills skill is calibrated to the floor defined here. Raise your floor for safety; lower it if your audience demands; do not extend across this floor without re-deriving every per-feature recommendation.

## The exact baseline

| Engine | Version | Release date | Source |
|---|---|---|---|
| **Chromium** | **125** | **May 14, 2024** | [Chrome 125 release notes](https://developer.chrome.com/release-notes/125) — "Chrome 125 is rolling out now" |
| **Safari** | **17.4** | **March 5, 2024** | [Safari 17.4 release notes](https://developer.apple.com/documentation/safari-release-notes/safari-17_4-release-notes) — shipped with iOS 17.4 / macOS 14.4 / visionOS 1.1 |
| **Firefox** | **129** | **August 6, 2024** | [Firefox 129 release notes](https://www.mozilla.org/en-US/firefox/129.0/releasenotes/) |

These three versions span a five-month window — Safari 17.4 was the earliest, Firefox 129 the latest. The expert-polyfills skill's effective release-date floor is **August 6, 2024**, ~20 months before this file's authoring date of April 27, 2026.

**Edge tracks Chromium with a 1–2 week offset**; Edge 125 shipped within the same May 2024 window. iOS Safari version is locked to the Safari version (no diverging shipping cycles). Mobile Firefox tracks desktop Firefox.

## Why this baseline

Three properties make this floor opinionated-but-defensible at April 2026:

1. **~18–22 months old.** Old enough that auto-updating browsers have rolled forward to it (~95% of users on these versions or later per Statcounter); new enough that we get nearly all of ES2024 plus most of ES2025 natively.
2. **All three engines closed major Baseline 2024 features.** Set methods, Object/Map.groupBy, Promise.withResolvers, Iterator helpers (Safari got it slightly later in 18.4), Popover API, light-dark() — all supported.
3. **Single specifiable browserslist query.** `Chrome >= 125, Firefox >= 129, Safari >= 17.4` resolves consistently across Babel, SWC, esbuild, lightningcss, postcss-preset-env, autoprefixer, Vite, and Next.js. No engine-specific exceptions, no minor-version-only oddities.

The trade-off: ~3–5% of global users are on browser versions below this floor. That tail is mostly enterprise IE-replacement Edge installs (a vanishing segment), Samsung Internet < 23 (Chromium-based, lags by ~6–12 months), and locked-down WebView installs in older Android versions. For consumer-facing audiences with auto-updating browsers, the trade-off is conservative; for B2B with corporate-managed browsers, raise the floor by negotiation.

## What's natively supported across all three

The full surface of "stop polyfilling these" — every entry below is shipped at all three baseline versions. Polyfilling any of these is bundle bloat at this floor.

### Promises + async

| Feature | Status |
|---|---|
| `Promise`, `Promise.all`, `Promise.race` | Universal since ES2015 |
| `Promise.allSettled` | All three since 2020 |
| `Promise.any` | All three since 2021 |
| `Promise.withResolvers` | Chrome 119, Firefox 121, Safari 17.4 — at baseline |
| `async`/`await` | Universal since 2017 |
| `AbortController`, `AbortSignal`, `signal.timeout()`, `AbortSignal.any()` | All shipped — `AbortSignal.timeout()` Chrome 103, Firefox 100, Safari 17.4; `any()` Chrome 116, Firefox 124, Safari 17.4 |

### Fetch + streams

| Feature | Status |
|---|---|
| `fetch`, `Request`, `Response`, `Headers` | Universal at baseline |
| `ReadableStream`, `WritableStream`, `TransformStream` | Universal at baseline |
| `TextEncoder`, `TextDecoder`, `TextEncoderStream`, `TextDecoderStream` | All shipped at baseline |
| `CompressionStream`, `DecompressionStream` | Chrome 80, Firefox 113, Safari 16.4 — at baseline; Tailwind v4 used to ship `pako` for this and no longer needs to |
| Server-Sent Events (`EventSource`) | Universal at baseline |

### Observers

| Feature | Status |
|---|---|
| `IntersectionObserver` | Universal at baseline (Chrome 51, Firefox 55, Safari 12.1) |
| `ResizeObserver` | Universal at baseline (Chrome 64, Firefox 69, Safari 13.1) |
| `MutationObserver` | Universal — pre-dates baseline by years |
| `PerformanceObserver` | Universal at baseline; LCP/FID/INP all observable |

### Cloning + structured data

| Feature | Status |
|---|---|
| `structuredClone` | Chrome 98, Firefox 94, Safari 15.4 — at baseline |
| `Symbol`, `Symbol.iterator`, `Symbol.asyncIterator` | Universal |
| `WeakMap`, `WeakSet`, `WeakRef` | Universal at baseline (`WeakRef` Chrome 84, Firefox 79, Safari 14.1) |
| `FinalizationRegistry` | Universal at baseline |

### Array + Object methods (ES2024 complete)

| Feature | Status |
|---|---|
| `Array.flat`, `Array.flatMap`, `Array.at` | Universal |
| `Array.findLast`, `Array.findLastIndex` | All three by mid-2022 |
| `Array.includes`, `Array.from`, `Array.of` | Universal |
| `Object.entries`, `Object.fromEntries`, `Object.values` | Universal |
| `Object.hasOwn` | Chrome 93, Firefox 92, Safari 15.4 |
| `Object.groupBy`, `Map.groupBy` | Chrome 117, Firefox 119, Safari 17.4 — Baseline March 2024 |

### ES2024–2025 finished work

| Feature | Status |
|---|---|
| **Set methods** (`intersection`, `union`, `difference`, `symmetricDifference`, `isSubsetOf`, `isSupersetOf`, `isDisjointFrom`) | Chrome 122, Firefox 127, Safari 17 — Baseline June 11, 2024 |
| **`RegExp v` flag** (set notation, properties of strings, intersection) | Chrome 112, Firefox 116, Safari 17 — Baseline 2023 |
| **`Promise.withResolvers`** | Chrome 119, Firefox 121, Safari 17.4 |
| **`Array.fromAsync`** | Chrome 121, Firefox 115, Safari 16.4 |
| **`String.prototype.isWellFormed` / `toWellFormed`** | All three by Safari 16.4 / Firefox 119 / Chrome 111 |

### Modules

| Feature | Status |
|---|---|
| `<script type="module">`, dynamic `import()`, `import.meta` | Universal at baseline |
| **JSON modules / import attributes** (`with { type: "json" }`) | Chrome 123, Firefox 128, Safari 17.2 — Baseline Newly Available April 2025 |
| Top-level await | Chrome 89, Firefox 89, Safari 15 |
| Module workers (`type: "module"` in Worker constructor) | Chrome 80, Firefox 114, Safari 15 |

### DOM APIs

| Feature | Status |
|---|---|
| `classList`, `dataset`, `closest()`, `matches()`, `getRootNode()` | Universal at baseline |
| `replaceChildren`, `toggleAttribute`, `append`, `prepend` | All shipped at baseline |
| `Element.checkVisibility()` | Chrome 105, Firefox 125, Safari 17.4 |
| `customElements`, `attachShadow`, `slot` | Universal at baseline |

### CSS layout

| Feature | Status |
|---|---|
| Flexbox | Universal |
| Grid | Universal at baseline |
| **Subgrid** (`grid-template-columns: subgrid`) | Firefox 71, Safari 16, Chrome 117 — Baseline Sept 2023 |
| `aspect-ratio` | Chrome 88, Firefox 89, Safari 15 |
| **Container queries** (`@container`, `cqi`, `cqw`, `cqh`, `cqb`, `cqmin`, `cqmax`) | Chrome 105, Firefox 110, Safari 16 — Baseline Feb 2023 |
| Style queries (`@container style(...)`) | Chrome 111, Firefox 124, Safari 18 |
| **Cascade layers** (`@layer`) | Chrome 99, Firefox 97, Safari 15.4 |
| **`:has()`** | Chrome 105, Firefox 121, Safari 15.4 |
| **CSS Nesting** (no `&` required for type selectors at baseline) | Chrome 112, Firefox 117, Safari 16.5; relaxed parser Chrome 120, Firefox 117, Safari 17.2 |
| Logical properties (`block-size`, `inline-size`, `margin-inline`, etc.) | Universal at baseline |

### CSS color

| Feature | Status |
|---|---|
| `oklch()`, `oklab()`, `lch()`, `lab()`, `color()` | Chrome 111, Firefox 113, Safari 15.4 |
| `color-mix()` | Chrome 111, Firefox 113, Safari 16.2 |
| **`light-dark()`** | Chrome 123, Firefox 120, Safari 17.5 — at baseline (Safari 17.4 needs 17.5 — verify iOS user mix) |
| **Relative color syntax** (`oklch(from base ...)`) | Chrome 119, Firefox 128, Safari 16.4 — Baseline 2024 |
| `color-scheme` (gates `light-dark()`) | Chrome 81, Firefox 96, Safari 13 |
| Wide-gamut color (`color(display-p3 ...)`) | Chrome 111, Firefox 113 *(maps to sRGB — see `../css-color-bugs/display-p3-firefox-lag.md`)*, Safari 15 |

### CSS typography

| Feature | Status |
|---|---|
| **`text-wrap: balance`** | Chrome 114, Firefox 121, Safari 17.5 — Baseline Jan 2024 |
| `text-wrap: pretty` | Chrome 117, Safari 17.5 — **Firefox unshipped** at baseline |
| `font-variation-settings`, variable fonts | Universal at baseline |
| `font-palette`, `@font-palette-values` | Chrome 101, Firefox 107, Safari 15.4 |
| `font-size-adjust` | Firefox 118, Safari 17, Chrome 127 — Baseline 2024 |
| `text-decoration-thickness`, `text-underline-offset` | Universal at baseline |

### Web platform

| Feature | Status |
|---|---|
| **Popover API** (`popover`, `popovertarget`, `showPopover()`) | Chrome 114, Firefox 125, Safari 17 — Baseline April 2024. **Quirks at baseline — see `../popover-quirks/`** |
| `<dialog>` (modal + non-modal) | Chrome 37, Firefox 98, Safari 15.4 |
| **Declarative Shadow DOM** (`<template shadowrootmode="open">`) | Chrome 124, Firefox 123, Safari 16.4. Note: standardized name is `shadowrootmode`; older `shadowroot` only worked in Chrome 90–124. |
| **ElementInternals** (`attachInternals()`) | Chrome 90, Firefox 126, Safari 17.4 |
| **CustomStateSet** (`:state()` pseudo-class) | Chrome 121, Firefox 126, Safari 17.4 |
| **Form-Associated Custom Elements** (FACE) | Chrome 90, Firefox 126, Safari 17.4 |

### Web APIs

| Feature | Status |
|---|---|
| **Web Locks** (`navigator.locks`) | Chrome 69, Firefox 96, Safari 15.4 |
| IndexedDB v3 | Universal at baseline |
| Web Crypto (`crypto.subtle`) | Universal at baseline |
| Web Workers, Service Workers | Universal at baseline |
| `requestIdleCallback`, `requestAnimationFrame` | Universal at baseline |
| `URL`, `URLSearchParams` | Universal at baseline |
| WebSockets, BroadcastChannel | Universal at baseline |

## What's NOT supported across all three (the polyfill candidate space)

Smaller table — the surface where polyfills, shims, or feature-query gates still earn their bundle weight at this baseline.

| Feature | Status at baseline | Polyfill posture |
|---|---|---|
| **Temporal** | Firefox 139 (May 2025), Chrome 144 (Jan 2026), Safari **pending** | `@js-temporal/polyfill` (~60KB compressed). See `../runtime-polyfills/temporal-api.md` |
| **URLPattern** | Safari 26 (Sept 2025), Firefox 144 (Oct 2025), Chrome 95+. **Firefox 129–143 is the polyfill window** | `urlpattern-polyfill`. See `../runtime-polyfills/urlpattern.md` |
| **Iterator helpers** | Chrome 122, Firefox 131, Safari 18.4. **Safari 17.4–18.3 is the polyfill window** | `es-iterator-helpers`. See `../runtime-polyfills/iterator-helpers.md` |
| **`Promise.try`** | Chrome 128, Firefox 134, Safari 18.2. **Firefox 129–133 needs trivial inline shim** | Inline shim — 3-line implementation |
| **CSS Anchor Positioning** | Chrome 125+, Safari 26+ (post-baseline by ~9 versions), Firefox 147+ (post-baseline by 18 versions) | `@oddbird/css-anchor-positioning`. See `../css-polyfills-and-shims/anchor-positioning-polyfill.md` |
| **Scroll-driven animations** | Chrome 115+, Safari 26+ (post-baseline), Firefox flag-only | `flackr/scroll-timeline`. See `../css-polyfills-and-shims/scroll-timeline-polyfill.md` |
| **`@scope`** | Chrome 118, Safari 17.4, Firefox 146 (post-baseline by 17 versions). **Firefox 129–145 is the polyfill window** — but no real polyfill exists | Feature query + flat fallback |
| **`contrast-color()`** | Safari TP, Firefox-only — **Chrome stable does not ship** | Use `apcach` library or compute at build time. See `../css-color-bugs/contrast-color-availability.md` |
| **Cookie Store API** | Safari 26.2+ (Dec 2025), Firefox 138+, Chrome 87+. **Below those, no good polyfill exists** | `document.cookie` fallback |
| **Customizable `<select>`** (`appearance: base-select`) | Chrome 135+ only | None; defer to native enhanced when available |
| **`popover="hint"`** | Chrome 133+ only | None; use `popover="auto"` fallback |
| **View Transitions cross-document** | Chromium-only at baseline | None; feature query + skip enhancement |
| **Scoped Custom Element Registries** | Safari 26+, Chrome 146+. **Firefox does not ship** | `@webcomponents/scoped-custom-element-registry` for Firefox |
| **`field-sizing: content`** | Editor's draft only — no shipping | Wait |
| **`calc-size()` / `interpolate-size`** | Chromium 129+ only | Feature query gate |

This is the entire active polyfill candidate surface at our baseline. The list of "still need to polyfill" is short. The list of "stop polyfilling" is the entire ES2015–ES2024 corpus, the entire DOM and CSS Layout 1–2 surface, and most of CSS Color Module 4–5, CSS Containment 3, and CSS Custom Properties 1.

## Caveats — where the baseline frays

### Mobile WebView versions

WebViews bundled into older Android versions can lag desktop Chrome substantially. An Android 11 device using the system WebView 2.0–2.2 may run a Chromium build well below 125, even when Chrome standalone is at 132+. Check `User-Agent` if you ship to mobile-web traffic and care about non-Chrome consumer apps embedding WebViews.

iOS WebViews (WKWebView) are locked to the Safari version of the OS — there's no Safari-of-a-newer-version inside an iOS app. Older iOS users running iOS 17.0–17.3 will hit pre-baseline Safari without your knowing.

### Edge offsets

Microsoft Edge ships Chromium with a 1–2 week lag, with rare exceptions during major-version transitions. Edge 125 shipped May 30, 2024, two weeks after Chrome 125. If you check "Chrome 125+" via User-Agent sniffing, Edge users may briefly fall outside; in practice, browserslist queries with `last 2 versions` for Edge handle this implicitly.

### Server-side rendering

If you're targeting Node, Deno, or Bun — that's a separate concern from browser baseline. Node 22 LTS implements all of ES2024 plus most ES2025; Bun matches modern V8; Deno matches recent V8. SSR polyfilling is sometimes needed for browser-only APIs (`document`, `window`, `localStorage`) but that's a runtime-environment problem, not a feature-shipping problem.

### Enterprise managed-browser audiences

If your audience runs corporate-managed Chrome/Edge/Firefox installs, those installs may be pinned several versions behind. The baseline above assumes auto-updating consumer browsers. Adjust upward (more conservative) for enterprise-only audiences; the polyfill candidate list grows accordingly.

### Audit traffic

Always check actual user analytics before shipping a build target. The baseline here is a starting point; the right floor is determined by your top 5–10% tail-of-distribution users.

## How to express this baseline in tools

Preview of `../build-tools/browserslist-recipes.md`. The canonical query:

```
chrome >= 125
firefox >= 129
safari >= 17.4
```

Or the equivalent expanded form:

```
last 2 Chrome versions
last 2 ChromeAndroid versions
Chrome >= 125
last 2 Firefox versions
last 2 FirefoxAndroid versions
Firefox >= 129
last 2 Safari versions
last 2 iOS versions
Safari >= 17.4
iOS >= 17.4
```

In Vite (don't use the `'baseline-widely-available'` keyword for our baseline — it's older):

```js
// vite.config.js
export default {
  build: {
    target: ['chrome125', 'firefox129', 'safari17.4'],
  },
};
```

In esbuild:

```js
{ target: ['chrome125', 'firefox129', 'safari17.4'] }
```

In Babel preset-env (browserslist-discovered):

```js
{ presets: [['@babel/preset-env', { useBuiltIns: 'usage', corejs: { version: 3, proposals: false } }]] }
// Plus a .browserslistrc with the canonical query above
```

## Cross-references

- For Baseline tier definitions: `baseline-glossary.md`.
- For do-I-need-a-polyfill flow: `decision-tree.md`.
- For the term definitions used here: `glossary.md`.
- For per-tool browserslist recipes: `../build-tools/browserslist-recipes.md`.
- For Vite v6 `'baseline-widely-available'` keyword behavior: `../build-tools/vite-build-target.md`.
- For each polyfill candidate's specifics: `../runtime-polyfills/`, `../css-polyfills-and-shims/`.
