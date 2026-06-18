---
date: 2026-04-27
coverage: canonical
peers:
  - ../meta/glossary.md
  - ../meta/the-modern-baseline.md
  - ../meta/decision-tree.md
  - ../build-tools/browserslist-recipes.md
  - ../build-tools/vite-build-target.md
primary_sources:
  - https://web.dev/baseline — canonical Baseline definition
  - https://web.dev/blog/baseline-definition-update — 2024 update introducing the 30-month threshold
  - https://web-platform-dx.github.io/web-features/ — the web-features repo + group
  - https://web.dev/blog/baseline-newly-available — Baseline tier mechanics
  - https://web.dev/blog/baseline-progress-2024 — Baseline 2024 retrospective
  - https://web.dev/articles/how-to-choose-your-baseline-target — practitioner guidance
  - https://vite.dev/config/build-options — Vite's `'baseline-widely-available'` keyword
  - https://github.com/browserslist/browserslist#queries — `defaults` query semantics
  - https://github.com/web-platform-dx/baseline-browser-mapping — the baseline-browser-mapping package
  - https://developer.mozilla.org/en-US/docs/Glossary/Baseline/Compatibility — MDN Baseline glossary entry
---

# Baseline Glossary — Web Platform Baseline reference

The Web Platform Baseline ([web.dev/baseline](https://web.dev/baseline)) is the cross-engine support tier system maintained by the **Web Platform DX Community Group** (Apple, Google, Microsoft, Mozilla, Igalia, Bocoup contributors). It replaces ad-hoc "is this safe to use" decisions with two named tiers and an annual cohort label.

This file is the reference for what those tiers mean, how to read them in caniuse / MDN BCD, and how to translate them to actual browser-version targets.

## The two tiers

### Baseline Newly Available

A feature is **Newly Available** the moment it ships in the last of the four "core" engines (Chromium-based, Gecko, WebKit-based on iOS/Mac, plus all corresponding mobile builds). It does not require any waiting period.

Source: [web.dev/blog/baseline-newly-available](https://web.dev/blog/baseline-newly-available).

**What "Newly Available" tells you:** every up-to-date browser supports it. **What it does NOT tell you:** how many of your users are on up-to-date browsers. A feature can be Newly Available the day it ships in the last engine, when ~0% of users have that engine's release. The 30-month wait below addresses this.

### Baseline Widely Available

A feature is **Widely Available** when 30 months have passed since it became Newly Available. The 30-month figure is the WPDX Community Group's chosen safety horizon — long enough that auto-updating browsers have rolled forward past the introduction point, short enough that Widely Available stays current rather than ossifying.

Source: [web.dev/blog/baseline-definition-update](https://web.dev/blog/baseline-definition-update).

**What "Widely Available" tells you:** safe for production with very high confidence (>95% user coverage in most demographics). Translates roughly to "use without thinking."

**What it doesn't fix:** locked-down enterprise environments running stale browsers, embedded WebViews that lag, niche browsers (UC, Samsung Internet versions behind Chromium). Widely Available is a probabilistic tool, not a guarantee.

### Tier transitions table (April 2026)

| Status | Means | Polyfill posture |
|---|---|---|
| Limited Available | Some engines ship; others don't | Polyfill candidate or feature query |
| Newly Available | All engines ship | Stop polyfilling; verify your user mix |
| Widely Available | All engines + 30 months | Don't polyfill; ship native |

## Annual sets — Baseline 2024 / 2025

The Web Platform DX group publishes year-named cohorts. A feature is in the **Baseline 2024** set if it became Newly Available within calendar 2024.

### Baseline 2024 (sampling)

Per [web.dev/blog/baseline-progress-2024](https://web.dev/blog/baseline-progress-2024):

- **CSS**: `@scope` (Dec 2024 — Firefox 146 closing); `text-wrap: balance` (Firefox 121 closed it, Jan 2024); `text-wrap: pretty` (still partial — Firefox unshipped); `align-content` for block layout; CSS Anchor Positioning Limited Availability through 2024; `field-sizing: content` (still draft); `light-dark()` Newly Available May 2024 (Firefox 120, Chrome 123, Safari 17.5).
- **JS**: Set methods (June 11, 2024 — Safari 17 closed it); `Object.groupBy` / `Map.groupBy` (March 2024 — Safari 17.4 closed it); `Promise.withResolvers` (March 2024 — Safari 17.4); `RegExp v flag` (Sept 2023 — Safari 17 closed it, in the 2023 cohort).
- **Web platform**: Popover API (April 2024 — Firefox 125 closed it); `<dialog>` (Newly Available since 2022 — in 2022 cohort); CustomStateSet `:state()` (Newly Available 2024).
- **APIs**: WebRTC AV1 codec.

### Baseline 2025 (sampling)

Per [web.dev/baseline](https://web.dev/baseline) live data:

- **CSS**: View Transitions same-document (Oct 14, 2025 — Firefox 144 closed it); CSS Anchor Positioning closed Jan 13, 2026 with Firefox 147 (so technically Baseline 2026 cohort); relative color syntax (`oklch(from base ...)`) Newly Available 2024–2025 cusp.
- **JS**: Iterator helpers (April 2025 — Safari 18.4 closed it); Promise.try (Jan 2025 — Firefox 134 closed it); JSON modules / import attributes (April 2025 — Chrome 123 / Firefox 128 / Safari 17.2); Explicit Resource Management (`using`) — Stage 4, 2025; Float16Array, RegExp.escape, Error.isError — all Stage 4 in 2025 cohort.
- **Web platform**: Speculation Rules (Chromium-only at baseline; not yet Newly Available cross-engine); URLPattern (Safari 26 Sept 2025 + Firefox 144 closed it Oct 2025 — Newly Available late 2025).

### Why year sets matter

A feature in the **Baseline 2024** set has been Newly Available for 18+ months by April 2026. It crosses the Widely Available threshold (30 months) somewhere between July 2026 and December 2026 depending on its specific Newly-Available date. Year sets give you a coarse-grained "how mature is this feature?" answer without checking the exact ship date.

## Tool-specific Baseline keywords

### Vite v6+ `build.target = 'baseline-widely-available'`

Vite 6 introduced `'baseline-widely-available'` as a special `build.target` value that resolves to the set of browser versions corresponding to "Baseline Widely Available on January 1, 2026". Per [Vite docs](https://vite.dev/config/build-options):

```
build.target = 'baseline-widely-available'
// Resolves to: ['chrome111', 'edge111', 'firefox114', 'safari16.4']
```

**Critical:** this is **older** than our baseline by ~14 versions per browser. Vite's keyword targets a wider audience than the expert-polyfills baseline. If you're at our baseline (Chrome 125+, Safari 17.4+, Firefox 129+), set an explicit target:

```js
// vite.config.js
export default {
  build: {
    target: ['chrome125', 'firefox129', 'safari17.4'],
  },
};
```

### caniuse Baseline status

caniuse.com displays Baseline status in feature pages — green "Baseline" badges with "Newly available" or "Widely available" labels. The badges are sourced from web-features, the same data store as web.dev/baseline.

When reading caniuse:
- A Baseline-Widely-Available green badge = use without thinking.
- A Baseline-Newly-Available green badge = check your user mix; for our baseline this is fine.
- A "Limited availability" yellow badge = polyfill candidate or feature query.
- No badge = either too new (no Baseline data yet) or too old (Baseline preceded the feature).

### MDN BCD Baseline flags

MDN's Browser Compat Data (BCD) tables show Baseline status in the per-feature info banner at the top of every relevant article. Same source data as caniuse and web.dev/baseline. Per-API, per-property, per-syntax granularity.

**Trust pecking order**: web.dev/baseline > MDN BCD > caniuse > anywhere else. Web-features is the source-of-truth; the others are renderers.

## Browserslist `defaults` — what it actually means

Browserslist's `defaults` query expands to ([browserslist README](https://github.com/browserslist/browserslist#readme)):

```
> 0.5% and last 2 versions and Firefox ESR and not dead
```

In practice this matches:
- Chrome (last 2 versions)
- Firefox (last 2 versions + ESR)
- Safari (last 2 versions)
- Edge (last 2 versions)
- Opera, Samsung Internet, UC Browser, Android, iOS Safari (last versions matching > 0.5% global)
- Excludes browsers without updates for 24+ months (`not dead`)

**Why `defaults` is almost always wrong for modern projects:** it includes browsers that are well below our baseline. As of April 2026, `defaults` matches:
- Chrome ≥ 132 (last 2 versions, ~Jan 2026)
- Firefox ≥ 144 ESR
- Safari ≥ 17 (because iOS 17 still has > 0.5% share in some demographics)
- Samsung Internet ≥ 23
- UC Browser, Opera Mini, KaiOS browser — all included if they hit > 0.5%.

Setting `defaults` causes Babel preset-env, postcss-preset-env, autoprefixer, etc. to ship transforms targeting whatever Samsung Internet 23 lacks. **This is bundle bloat for users who don't exist in your audience.**

**Better:** explicit query like `Chrome >= 125, Firefox >= 129, Safari >= 17.4`, or for the team-shared Baseline approach, `baseline widely available`.

## Browserslist `--coverage` flag

Verifies the actual user-coverage of your query. Run:

```
npx browserslist --coverage "Chrome >= 125, Firefox >= 129, Safari >= 17.4"
```

Returns a percentage of global users matched, sourced from caniuse-lite stats. As of April 2026, the above query covers **~92–95%** depending on the demographic slice. Trade more bundle bloat for a higher coverage number; trade ~5% coverage loss for substantial savings.

**Pitfall:** caniuse-lite stats default to global usage. For region- or audience-specific coverage, pass `--region`:

```
npx browserslist --coverage --region=KR "Chrome >= 125, Firefox >= 129, Safari >= 17.4"
```

## `baseline-browser-mapping` package

The [baseline-browser-mapping](https://github.com/web-platform-dx/baseline-browser-mapping) npm package translates a Baseline year (or Newly/Widely Available) to a specific browser-version set, and vice versa. Use it programmatically:

```js
import { getBrowserList } from 'baseline-browser-mapping';
const browsers = getBrowserList({ targetYear: 2024, channel: 'widely' });
// → { chrome: 121, edge: 121, firefox: 115, safari: 17.0 }
```

**When to use:** scripted browserslist generation; testing infrastructure that derives target-version matrices from Baseline cohorts.

## Reading caniuse against this baseline

For the expert-polyfills baseline (Chrome 125+ / Safari 17.4+ / Firefox 129+):

1. Open the feature's caniuse page.
2. Find the **first version** for each engine that supports the feature.
3. If all three first-versions are at-or-below our baseline (e.g. Chrome 122, Firefox 127, Safari 17) — **stop polyfilling**.
4. If any first-version exceeds our baseline — feature is candidate for polyfill, build-time lowering, or feature-query gating.

Worked example for `light-dark()`:
- Chrome: 123 (May 2024) — at-or-below 125. ✓
- Firefox: 120 (Nov 2023) — at-or-below 129. ✓
- Safari: 17.5 (May 2024) — Safari 17.4 baseline, so 17.5 is one minor above; verify your iOS audience.

For `light-dark()` at our baseline, this means: native-supported on the latest Chrome and Firefox; Safari 17.4 lacks it, Safari 17.5+ has it. Polyfill posture: feature query gate or build-time `light-dark` polyfill via `postcss-light-dark-function`.

## Cross-references

- For the expert-polyfills baseline's exact composition: `the-modern-baseline.md`.
- For browserslist queries calibrated to this baseline: `../build-tools/browserslist-recipes.md`.
- For Vite's `'baseline-widely-available'` keyword in production context: `../build-tools/vite-build-target.md`.
- For the do-I-need-a-polyfill decision flow: `decision-tree.md`.
