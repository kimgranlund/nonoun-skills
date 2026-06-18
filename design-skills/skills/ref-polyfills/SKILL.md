---
name: ref-polyfills
description: Use when working with polyfills, ponyfills, transpilation, browser-compatibility shims, feature detection, or known browser bugs at a modern baseline (Chromium 125+, Safari 17.4+, Firefox 129+) — opinionated and modern-first. Triggers on "polyfill", "ponyfill", "shim", "browserslist", "babel", "swc", "esbuild", "core-js", "transpile", "@supports", "is X Baseline", "feature detection", or any "do I need to polyfill X for browser Y" question. Also triggers on browser-quirk questions ("Safari oklch bug", "popover light-dismiss iOS", "polyfill.io safe?"). NOT for color math / OKLCH conversion / WCAG-APCA contrast (color-science); NOT to build an OKLCH ramp (color-verifier), derive focus-ring/hit-target tokens (focus-verifier), emit locale/bidi invariants (i18n-verifier), fix perceived-latency/CLS (perf-verifier), or undo-over-confirm destructive UI (safety-verifier); NOT to grade a component's API+geometry (component-decomposer), generate component code (ui-build-components), or debug a stylesheet (analyze-css).
---

# ref-polyfills

A reference for the small set of polyfills you still need at a modern baseline — and the much larger set you should stop shipping.

_**v1.0.0 — released 2026-04-27.** 84 dated reference files across 13 axes._

> **The baseline (load-bearing).** See `../.docs/browser-baseline.json` for the centralized support floor (Chromium 125+, Safari 17.4+, Firefox 129+). Everything below is calibrated to this shared baseline. Lower your build target if your audience demands; raise it (or remove polyfills) if it doesn't.

## Invocation (the 3-phase contract)

### Step 1 — Ingest

Watch for vocabulary drift and steelman the actual question:

| Surface prompt | Watch for | Likely actual question |
|---|---|---|
| "Polyfill for X" | Caller may mean transpile / lower / shim / ponyfill — different tools | "What's the right tool for shipping X to my baseline?" |
| "Does X work in Y?" | Single-browser vs cross-browser; baseline-aware vs absolute | "Is X usable across my support floor?" |
| "Safari is broken" | Often a known bug at baseline, not absence | Bug-catalog lookup, not polyfill |
| "Should I `useBuiltIns: 'entry'`?" | The ES5-era answer is no for modern targets | "What's the modern Babel config?" |
| "polyfill.io is fine, right?" | NO. Hostile since June 2024 | "What replaced polyfill.io?" |

### Step 2 — Decompose

Question-shape decomposition. Most polyfill questions route to one of six sub-questions:

| Question shape | Routes to |
|---|---|
| "Do I need to polyfill X at this baseline?" | `runtime-polyfills/<X>.md` or `css-polyfills-and-shims/<X>.md` (lookup) |
| "What does my build tool transpile?" | `transpilation/` + `build-tools/` |
| "Why is Safari/Firefox/Chrome rendering Y weirdly?" | `css-color-bugs/`, `popover-quirks/`, `anchor-positioning-quirks/` (bug lookup) |
| "What's framework Z's polyfill story?" | `products/<framework>.md` |
| "What should I stop doing?" | `anti-patterns/` |
| "What's the news on TC39 / browsers / polyfill.io?" | `landscape-shifts/`, `js-language-status/` |

### Step 3 — Route

| You're doing… | Go to |
|---|---|
| Looking up a feature's baseline status | `references/js-language-status/` (JS) or per-axis files (CSS, web platform) |
| Picking a runtime polyfill | `references/runtime-polyfills/` |
| Picking a CSS shim or build-tool transformer | `references/css-polyfills-and-shims/` + `references/build-tools/` |
| Diagnosing a Safari color bug | `references/css-color-bugs/` |
| Diagnosing a Popover bug | `references/popover-quirks/` |
| Diagnosing an anchor-positioning bug | `references/anchor-positioning-quirks/` |
| Choosing a build-tool target | `references/build-tools/browserslist-recipes.md` |
| Configuring Babel / SWC / esbuild / TS | `references/transpilation/` |
| Per-framework setup (Next, Vite, Astro, etc.) | `references/products/` |
| Avoiding common mistakes | `references/anti-patterns/` |
| Understanding the polyfill.io / core-js situation | `references/landscape-shifts/` |
| Feature detection patterns | `references/feature-detection/` |
| Glossary / definitions / decision tree | `references/meta/` |

## What this skill contains

- `SKILL.md` — this file: opinionated stance + cheat sheets + routing
- `references/INDEX.md` — authoritative manifest, ✅/⬜ status, ~84 files across 13 axes
- `references/<axis>/*.md` — dated reference files with primary-source citations
- `CHANGELOG.md` — per-wave entries
- `skill.json` — machine-readable manifest

## The opinionated stance

Most things you used to polyfill are native now. Before you reach for `core-js`, `polyfill.io`, or a runtime shim:

1. **Check `caniuse.com` against this skill's baseline.** If it's green across all three engines at or before our baseline versions, **stop polyfilling**.
2. **Prefer build-time transpilation over runtime polyfills.** `lightningcss`, `esbuild`, `SWC`, Babel-with-`useBuiltIns: 'usage'` lower syntax + select features without shipping bundled runtime code to users who don't need it.
3. **Prefer feature queries over polyfills.** `@supports (...)` for CSS, `'feature' in obj` for JS — let the browser tell you what it has.
4. **When you must polyfill, ponyfill.** A pure import is safer than mutating globals. See `references/feature-detection/ponyfill-pattern.md`.
5. **Self-host. Never `<script src="cdn.polyfill.io/...">`.** Even via Cloudflare/Fastly mirrors. The polyfill.io domain was compromised June 2024; 3rd-party-JS supply-chain risk is real. See `references/landscape-shifts/polyfill-io-attack.md`.

## Quick reference — STOP polyfilling these (already native at baseline)

These are **fully shipped at all three baseline versions**. Shipping a polyfill for any of them is bundle bloat.

| Category | Features (representative, not exhaustive) |
|---|---|
| **Promises + async** | `Promise`, `Promise.allSettled`, `Promise.any`, `Promise.withResolvers`, `async`/`await`, `AbortController`, `AbortSignal` |
| **Fetch + streams** | `fetch`, `Request`, `Response`, `Headers`, `ReadableStream`, `WritableStream`, `TextEncoder`/`TextDecoder`, **`CompressionStream`** |
| **Observers** | `IntersectionObserver`, `ResizeObserver`, `MutationObserver`, `PerformanceObserver` |
| **Cloning + structured data** | `structuredClone`, `Symbol`, `Symbol.iterator`, `Symbol.asyncIterator`, `WeakMap`, `WeakSet`, `WeakRef` |
| **Array + Object** | `Array.flat`, `flatMap`, `at`, `findLast`, `findLastIndex`, `includes`, `Array.from`, `Object.entries`, `Object.fromEntries`, `Object.hasOwn`, **`Object.groupBy`**, **`Map.groupBy`** |
| **JS 2024–2025 built-ins** | **Set methods** (`intersection`, `union`, `difference`, `symmetricDifference`, `isSubsetOf`, `isSupersetOf`, `isDisjointFrom`), **`RegExp v` flag**, **`Promise.withResolvers`** |
| **Modules** | ESM `<script type="module">`, dynamic `import()`, `import.meta`, **JSON modules / import attributes** (Baseline Apr 2025) |
| **DOM** | `classList`, `dataset`, `closest`, `matches`, `getRootNode`, `replaceChildren`, `toggleAttribute` |
| **CSS layout** | Flexbox, Grid, **Subgrid**, `aspect-ratio`, container queries (`@container`, `cqi`/`cqw`), cascade layers (`@layer`), `:has()`, CSS Nesting, logical properties |
| **CSS color** | `oklch()`, `oklab()`, `lch()`, `lab()`, `color()`, `color-mix()`, **`light-dark()`**, **relative color syntax** (`oklch(from base ...)`) |
| **CSS typography** | `text-wrap: balance`, `font-variation-settings`, `font-palette`, `font-size-adjust`, `text-decoration-thickness` |
| **Web platform** | **Popover API** (with quirks — see below), `<dialog>`, **Declarative Shadow DOM**, **ElementInternals**, **CustomStateSet `:state()`** |
| **Web APIs** | **Web Locks**, IndexedDB, Web Crypto, Web Workers, Service Workers, `requestIdleCallback`, `requestAnimationFrame` |

**If your team is shipping a `core-js` bundle to users on these versions, you have a bundle-size problem, not a compatibility problem.** See `references/anti-patterns/corejs-entry-modern.md`.

## Quick reference — DO polyfill these (still candidates at baseline)

These are NOT supported across all three baseline versions, or have load-bearing bugs. The skill gives each its own reference file.

| Feature | Status at baseline | Polyfill |
|---|---|---|
| **Temporal** | Firefox 139+, Chrome 144+, Safari pending | `@js-temporal/polyfill` (~60KB) — see `runtime-polyfills/temporal-api.md` |
| **URLPattern** | Safari 26+ / Firefox 142+ — Firefox 129–141 needs polyfill | `urlpattern-polyfill` — see `runtime-polyfills/urlpattern.md` |
| **Iterator helpers** | Safari 18.4+ shipped — Safari 17.4–18.3 needs | `es-iterator-helpers` — see `runtime-polyfills/iterator-helpers.md` |
| **Promise.try** | Firefox 134+ — Firefox 129–133 needs | Trivial inline shim |
| **CSS Anchor Positioning** | Chrome 125+, Safari 26+ (post-baseline), Firefox 147+ (post-baseline by 18 versions) | `@oddbird/css-anchor-positioning` — see `css-polyfills-and-shims/anchor-positioning-polyfill.md` |
| **Scroll-driven animations** | Chrome 115+, Safari 26+ (post-baseline), Firefox flag | `flackr/scroll-timeline` |
| **`@scope`** | Chrome 118+, Safari 17.4+, Firefox 146+ (post-baseline) | No real polyfill; use feature query + flat fallback |
| **`contrast-color()`** | Chrome 147+ (April 7, 2026), Safari 26+, Firefox 146+ — all post-baseline | Use `apcach` library or compute at build time for Chrome 125–146 / Safari 17.4–25 / Firefox 129–145 |
| **Cookie Store API** | Safari 26.2+, Firefox 138+ | No good polyfill below; use `document.cookie` fallback |
| **Customizable `<select>`** | Chrome 135+ only | None; defer to native enhanced when available |
| **`popover="hint"`** | Chrome 133+ only | None; use `popover="auto"` fallback |
| **View Transitions cross-doc** | Chromium-only at baseline | None; use feature query + skip enhancement |
| **Scoped Custom Element Registries** | Safari 26+, Chrome 146+ — Firefox doesn't ship | `@webcomponents/scoped-custom-element-registry` for Firefox |

## Quick reference — known browser bugs at baseline (esoteric)

The long tail. Each gets its own file in the bug-axis directories.

### CSS color (`references/css-color-bugs/`)

| Bug | Affected | Workaround |
|---|---|---|
| Safari < 18 OKLCH `color-mix` red-shift (interpolates as LCH) | Safari Desktop < 18 | Use `in oklab` for transparent/gray mixing — Tailwind v4 PR #15201 |
| Chrome ↔ Safari OKLCH hue divergence in `color-mix` | All | Choose `in oklab` for cross-browser stability |
| `light-dark()` silently no-ops without `color-scheme` | All | Set `color-scheme: light dark` on `:root` |
| Firefox renders `color(display-p3 ...)` mapped to sRGB; `@media (color-gamut: p3)` always false | Firefox | Layer P3 enhancement via `@supports (color: color(display-p3 1 0 0))` |
| `contrast-color()` not in Chrome stable | Chrome at baseline | Use `apcach` or build-time contrast computation |

### Popover API (`references/popover-quirks/`)

| Bug | Affected | Workaround |
|---|---|---|
| Light-dismiss broken on iOS/iPadOS Safari 17.0–18.2 (WebKit Bug 267688) | iOS Safari 17.0–18.2 | Fixed in Safari 18.3 (Jan 27, 2025); for older, add explicit dismiss UI / OddBird polyfill |
| Focusing `<input>` inside popover closes popover (iOS keyboard scroll) | iOS Safari (persists past 18.3 fix) | Distinct mechanism from light-dismiss — virtual keyboard scrolls; use `popover="manual"` or render as modal |
| Safari < 18.4 hangs when tabbing out of popover | Safari < 18.4 | Fixed in Safari 18.4 (March 31, 2025); force focus restoration on close for older |
| `popover` inside modal `<dialog>` is inerted (top-layer interaction) | All | Don't nest popover inside modal dialog |
| z-index has no effect inside top-layer | All | Order DOM correctly; promote elements explicitly |
| `popover="hint"` Chrome 133+ only | Firefox/Safari at baseline | Use `popover="auto"` fallback |

### CSS anchor positioning (`references/anchor-positioning-quirks/`)

| Bug | Affected | Workaround |
|---|---|---|
| `inset-area` → `position-area` rename in Chrome 129; Chrome 131 removed `inset-area` entirely | All | Use `position-area`; old name through Chrome 130 only |
| Firefox 147 (Jan 13, 2026) shipped unflagged; Firefox 129–146 = polyfill candidate | Firefox 129–146 | OddBird polyfill |
| Popover UA-style margin interferes with anchor positioning | All | Reset `margin: 0` explicitly on popover |

## Browserslist for this baseline (the canonical query)

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

Or the more compact equivalent (verified during Wave 1):

```
chrome >= 125
firefox >= 129
safari >= 17.4
```

Use this in `.browserslistrc`, `package.json` `"browserslist"`, or per-tool config. See `references/build-tools/browserslist-recipes.md` for production-ready variants (with progressive-enhancement fallbacks, mobile-only, etc.).

## Composition

**Peers**:
- `ui-build-components` — consumes baseline guidance for ElementInternals, declarative shadow DOM, scoped registries
- `analyze-css` — CSS feature targeting overlap (`@supports`, modern CSS surface)
- `ref-color` — owns canonical color theory; this skill owns color-function bugs
- `ref-dashboard` — popover/dialog interaction overlap; this skill owns the bug catalog
- `ui-compose-responsive` — container queries + anchor positioning + viewport features

**Consumed by**:
- Any skill that emits CSS or JS targeting browsers — to verify that what it emits is actually shipped at the baseline.

## Invariants

1. **Modern-first.** Default stance: don't polyfill. Burden of proof is on the polyfill, not on going without.
2. **Baseline-calibrated.** Every claim is anchored to Chromium 125+ / Safari 17.4+ / Firefox 129+. Higher floors are fine; lower floors are out of scope.
3. **Primary sources only.** caniuse, MDN BCD, vendor changelogs, vendor bug trackers (Bugzilla, WebKit Bugzilla, Chromium Issues), W3C/WHATWG specs.
4. **No fabricated bug IDs, RFC numbers, or commit SHAs.**
5. **Every reference file is dated.** YAML frontmatter `date:` is mandatory; staleness is visible.
6. **Coverage tier per file** (canonical / extended / esoteric / advisory).
7. **Polyfill recommendations cite version + maintainer + license.** Single-maintainer or unmaintained packages get a supply-chain note.
8. **Self-host polyfills.** Never recommend a 3rd-party CDN as the production answer.
