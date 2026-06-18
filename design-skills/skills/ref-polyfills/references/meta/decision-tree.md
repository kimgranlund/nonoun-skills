---
date: 2026-04-27
coverage: canonical
peers:
  - ../meta/glossary.md
  - ../meta/baseline-glossary.md
  - ../meta/the-modern-baseline.md
  - ../build-tools/lightningcss-features.md
  - ../build-tools/postcss-preset-env.md
  - ../build-tools/browserslist-recipes.md
  - ../transpilation/babel-preset-env.md
  - ../transpilation/swc-targets.md
  - ../transpilation/esbuild-targets.md
  - ../feature-detection/at-supports-recipes.md
  - ../feature-detection/ponyfill-pattern.md
  - ../feature-detection/js-feature-detection.md
  - ../runtime-polyfills/temporal-api.md
  - ../landscape-shifts/polyfill-io-attack.md
primary_sources:
  - https://web.dev/articles/baseline-and-polyfills — modern position on Baseline + polyfilling
  - https://developer.mozilla.org/en-US/docs/Web/CSS/@supports — @supports definition
  - https://github.com/sindresorhus/ponyfill — ponyfill canonical README
  - https://babeljs.io/docs/babel-preset-env — Babel preset-env decision points
  - https://lightningcss.dev/transpilation.html — Lightning CSS transpilation behavior
  - https://github.com/postcss/postcss-preset-env#features — postcss-preset-env feature list
  - https://web.dev/baseline — Baseline reference
---

# Decision Tree — Do I need a polyfill?

Single canonical flowchart for "I'm using feature X — what do I do?" Use this every time the question comes up. Skip steps at your peril.

## The flow

```
Question: my code uses feature X. Do I need to polyfill it?

├── 1. Is X already in my browserslist baseline?
│       (Check meta/the-modern-baseline.md or caniuse against your support floor.)
│   ├── Yes → STOP. Do not polyfill. Ship it natively.
│   └── No  → continue
│
├── 2. Is X CSS or JS?
│   ├── CSS → continue at 3
│   └── JS  → continue at 5
│
├── 3. Can lightningcss / postcss-preset-env LOWER X to your baseline?
│       (See build-tools/lightningcss-features.md and build-tools/postcss-preset-env.md.)
│   ├── Yes → use build-time lowering. Do not ship a runtime polyfill.
│   └── No  → continue at 4
│
├── 4. Is there an @supports query that gates the missing-feature branch
│       gracefully so users without it get a working fallback?
│       (See feature-detection/at-supports-recipes.md.)
│   ├── Yes → progressive enhancement. Use @supports + flat fallback. Do not polyfill.
│   └── No  → use a CSS shim from css-polyfills-and-shims/ if one exists.
│             Otherwise skip the feature.
│
├── 5. Does Babel preset-env / SWC / esbuild TRANSPILE X for you?
│       (Syntax-level features like decorators, RegExp v flag, optional chaining, etc.
│        — see transpilation/.)
│   ├── Yes → configure browserslist correctly; let the build tool handle it.
│   └── No  → continue at 6
│
├── 6. Can you feature-detect X at runtime and provide an inline alternative?
│       (Pony pattern: `import { feature } from 'es-feature-X'`.)
│   ├── Yes → ponyfill. Pure import, no global mutation. Tree-shakes cleanly.
│   └── No  → continue at 7
│
├── 7. Is X used in code paths that ALL users hit?
│   ├── Yes → polyfill required. Use core-js (selective) or a single-feature polyfill.
│   │         Self-host. Never <script src="cdn.polyfill.io/...">.
│   └── No  → conditional load. Use feature detection + dynamic import.
│
└── DEFAULT: prefer ponyfills > polyfills > nothing. Never trust 3rd-party CDNs.
```

## The decision points, expanded

### Step 1 — Is X in my browserslist baseline?

This is the question that should answer 80% of "do I polyfill X?" questions. Check before doing anything else.

**How to check:**

1. Open caniuse for the feature.
2. Identify the first version each engine shipped X in.
3. Compare against your support floor (which for the expert-polyfills skill is **Chromium 125 / Safari 17.4 / Firefox 129** — see `the-modern-baseline.md`).
4. If all three first-versions are at-or-below your floor → **STOP. Do not polyfill.**

**Common failure mode:** developers default to "polyfill = safe" without running this check. The result is an extra 30–60 KB of `core-js` shipped to a 100% modern audience that needed nothing. See `../anti-patterns/corejs-entry-modern.md`.

**Worked example for `Object.groupBy`:**

- caniuse → Chrome 117, Firefox 119, Safari 17.4. All at-or-below baseline.
- Decision: STOP. No polyfill. No transpilation. Ship native.

**Counter-example for `Temporal`:**

- caniuse → Firefox 139 (May 2025), Chrome 144 (Jan 2026), Safari pending.
- Decision: Firefox 139 > 129, Chrome 144 > 125 (so users on 125–143 are exposed), Safari has no support at all. Continue past Step 1; this is a real polyfill candidate.

### Step 2 — CSS or JS?

The tooling diverges. CSS gets *lowered* by lightningcss / postcss-preset-env into older equivalents at build time. JS gets *transpiled* by Babel / SWC / esbuild for syntax, and *polyfilled* by core-js / ponyfills for APIs.

The two paths are not interchangeable. A CSS-only feature can't be JS-polyfilled (the browser parses CSS; injecting JS runtime won't help). A JS-only feature can't be `@supports`-gated.

### Step 3 — Can lightningcss / postcss-preset-env lower X?

Many CSS features have build-time lowering paths. The build tool reads your browserslist, sees X isn't shipped at the floor, and rewrites the CSS to an equivalent older form. No runtime cost, no polyfill.

**Lightning CSS lowers** (selective list, see `../build-tools/lightningcss-features.md` for the full list):

- Modern color functions (`oklch()`, `lab()`, `color()`) → fallback `rgb()` for older targets
- CSS Nesting → flat selectors
- Cascade layers (`@layer`) → unwrapped specificity tricks for older targets (limited)
- Logical properties (`margin-inline`, `block-size`) → physical properties
- `:has()` → no lowering (no equivalent)
- Container queries → no lowering (no equivalent)
- Custom property `@property` → emit fallback custom-property declarations

**postcss-preset-env lowers** (see `../build-tools/postcss-preset-env.md`):

- Custom media queries (`@custom-media`) → media-query expansion
- `@nest` → flat selectors
- Color functional notation (`rgb(255 0 0 / 50%)`) → comma syntax
- `:focus-visible` → `:focus` for ancient targets

**Lowering is not free** — for color features, lowered output ships *both* the modern and the fallback declaration, increasing CSS bundle size by ~10–20% in color-heavy stylesheets. But it's still cheaper than a runtime polyfill.

**When step 3 fails:** features without an older-syntax equivalent — `:has()`, container queries, `@scope`, anchor positioning. Those route to step 4.

### Step 4 — Is there an `@supports` query that lets users without X get a working fallback?

Progressive enhancement. The unsupported branch ships a working-but-less-fancy version; the supported branch upgrades.

**Standard pattern:**

```css
/* Default: works everywhere */
.card {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

/* Enhancement: anchor positioning if available */
@supports (anchor-name: --foo) {
  .card {
    anchor-name: --card;
    position: absolute;
    top: anchor(bottom);
    left: anchor(center);
    transform: none;
  }
}
```

**Composable forms:**

```css
@supports (text-wrap: balance) and (selector(:has(*))) { ... }
@supports not (color: oklch(0.5 0.1 0)) { /* sRGB fallback */ }
@supports selector(:has(*)) { /* :has-using rule */ }
```

See `../feature-detection/at-supports-recipes.md` for the full @supports cookbook.

**When step 4 fails:** when there's no graceful fallback for users without X (e.g. an animation that requires scroll-driven timeline, with no static substitute). Route to step 5 — but for CSS, runtime polyfills are rare, and skipping the feature is often the right call. See `../css-polyfills-and-shims/scroll-timeline-polyfill.md` for the rare exception (`flackr/scroll-timeline`).

### Step 5 — Does Babel preset-env / SWC / esbuild transpile X?

For JS features, the question is whether the build tool can rewrite your modern syntax into older syntax. **Syntax features** (parser-level) are transpilable; **runtime APIs** (prototype methods, global functions) are not.

| Category | Transpilable? | Examples |
|---|---|---|
| Optional chaining (`a?.b`) | Yes | All build tools |
| Nullish coalescing (`a ?? b`) | Yes | All build tools |
| Class fields (`class { #priv = 1 }`) | Yes | All build tools |
| Decorators (`@decorator`) | Yes (Stage 3 `2023-11`) | Babel + SWC + TypeScript |
| `using` declaration (Explicit Resource Management) | Yes | Babel + SWC + TypeScript 5.2+ |
| RegExp `v` flag | Yes (lowered to fallback patterns where possible) | Babel + SWC |
| Top-level await | Mostly module-level decision | esbuild + SWC + TypeScript |
| `Array.prototype.at` | **No** — runtime API | Polyfill required |
| `Object.groupBy` | **No** — runtime API | Polyfill required |
| `Promise.withResolvers` | **No** — runtime API | Polyfill required |
| `Temporal` | **No** — runtime API | Polyfill required |

Configure your `browserslist` correctly and let the build tool handle the syntax. **Don't manually configure preset-env to target ES5** — that's `../anti-patterns/target-es5-modern.md`.

**When step 5 fails:** runtime APIs. Route to step 6.

### Step 6 — Can you feature-detect X at runtime and ponyfill?

Ponyfills are the modern default for JS API gaps. Pure-function imports, no global mutation, tree-shakes cleanly.

**Standard pattern:**

```js
// Don't:
import 'core-js/actual/array/group-by'; // Mutates Array.prototype
[1, 2, 3].groupBy(x => x % 2);

// Do:
import { groupBy } from 'es-feature-helpers'; // Or write inline
groupBy([1, 2, 3], x => x % 2);
```

**Inline ponyfill (often preferable for small features):**

```js
const groupBy = (items, keyFn) =>
  items.reduce((acc, item) => {
    const key = keyFn(item);
    (acc[key] ??= []).push(item);
    return acc;
  }, {});
```

**See:** `../feature-detection/ponyfill-pattern.md`, `../feature-detection/js-feature-detection.md`.

**When step 6 fails:** the feature MUST be installed under its standard name on a global. Examples:
- `globalThis.fetch` — third-party libraries reference it directly.
- `globalThis.URLPattern` — same.
- `Array.prototype.findLast` — if the codebase mixes prototype-method calls and the ponyfill author chose not to ponyfill it (rare; this case usually has an inline shim).

### Step 7 — Polyfill, but properly

If steps 1–6 all failed and you must polyfill:

1. **Self-host.** Never `<script src="cdn.polyfill.io/...">`. Even Cloudflare's `cdnjs.cloudflare.com/polyfill` and Fastly's `polyfill-fastly.io` mirrors load 3rd-party JS — supply-chain risk. See `../landscape-shifts/polyfill-io-attack.md`.
2. **Single-feature polyfill > core-js bundle.** If you need `URLPattern`, install `urlpattern-polyfill` and import it directly. Don't pull `core-js` for one feature.
3. **Inline before imports** so it's installed before user code runs:
   ```js
   if (!('URLPattern' in globalThis)) {
     await import('urlpattern-polyfill');
   }
   ```
4. **Use `corejs: 3`, never `corejs: 2`.** Core-js 3.x is the only supported line; 2.x is unmaintained. See `../landscape-shifts/core-js-funding-status.md`.
5. **Set `useBuiltIns: 'usage'`, never `'entry'`.** `'entry'` ships polyfills your code never references. See `../anti-patterns/corejs-entry-modern.md`.

For non-critical paths, conditional load via dynamic import (step 7's "No" branch):

```js
async function withTemporal() {
  if (!('Temporal' in globalThis)) {
    await import('@js-temporal/polyfill');
  }
  return Temporal;
}
```

Network round-trip is cheap when the feature isn't first-paint-blocking.

## Default ordering: ponyfill > polyfill > nothing

When in doubt:

1. **Ponyfill** if the feature is API-shaped and you control the call sites.
2. **Polyfill** if 3rd-party code references the feature on globals and you can't avoid that coupling.
3. **Nothing** (skip the feature, or use a different approach) if neither works *and* the feature isn't load-bearing.

Adding a polyfill is a commitment to ship code, maintain it, and remove it later. Adding nothing is reversible.

## Quick reference — common questions, decision-tree exits

| Question | Step | Answer |
|---|---|---|
| "Should I polyfill `Array.prototype.at`?" | Step 1 | No. Universal at baseline. |
| "Should I polyfill `Object.groupBy`?" | Step 1 | No. Chrome 117, Firefox 119, Safari 17.4 — all at-or-below baseline. |
| "Should I polyfill `Temporal`?" | Steps 1, 6, 7 | Yes for now. `@js-temporal/polyfill`, ~60KB. Single-feature, self-host. |
| "Should I polyfill `URLPattern`?" | Steps 1, 7 | Yes for Firefox 129–143. `urlpattern-polyfill`, single-feature, self-host. |
| "Should I polyfill `:has()`?" | Step 1 | No. Universal at baseline. |
| "Should I polyfill anchor positioning?" | Steps 1, 4, 7 | Step 4 if a flat fallback works (often yes). Otherwise `@oddbird/css-anchor-positioning`. |
| "Should I polyfill `text-wrap: balance`?" | Step 1 | No. Universal at baseline (Firefox 121 closed it). |
| "Should I polyfill `Promise.withResolvers`?" | Step 1 | No. Chrome 119, Firefox 121, Safari 17.4. |
| "Should I polyfill `light-dark()`?" | Steps 1, 4 | Yes for Safari 17.4 (17.5 closed it). Step 4 with `prefers-color-scheme` flat fallback. |
| "Should I install `@babel/polyfill`?" | Step 7 | No, ever. Deprecated since Babel 7.4 (2019). Use `@babel/preset-env` with `useBuiltIns: 'usage'` and `corejs: 3`. See `../anti-patterns/corejs-entry-modern.md`. |
| "Should I use polyfill.io?" | Step 7 | **No**, ever. Compromised June 2024; mirrors are still 3rd-party JS. Self-host. See `../landscape-shifts/polyfill-io-attack.md`. |

## Cross-references

- For the exact baseline this tree assumes: `the-modern-baseline.md`.
- For the term definitions used: `glossary.md`.
- For the Baseline tier definitions cited: `baseline-glossary.md`.
- For build-time lowering: `../build-tools/lightningcss-features.md`, `../build-tools/postcss-preset-env.md`.
- For transpilation specifics: `../transpilation/babel-preset-env.md`, `../transpilation/swc-targets.md`, `../transpilation/esbuild-targets.md`.
- For ponyfill mechanics: `../feature-detection/ponyfill-pattern.md`.
- For per-polyfill recipes: `../runtime-polyfills/`, `../css-polyfills-and-shims/`.
- For the polyfill.io situation: `../landscape-shifts/polyfill-io-attack.md`.
