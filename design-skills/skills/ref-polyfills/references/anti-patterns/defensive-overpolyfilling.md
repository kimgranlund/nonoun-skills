---
date: 2026-04-27
coverage: advisory
peers:
  - ../anti-patterns/corejs-entry-modern.md
  - ../anti-patterns/target-es5-modern.md
  - ../anti-patterns/preset-env-no-browserslist.md
  - ../anti-patterns/polyfill-io-after-attack.md
  - ../build-tools/browserslist-recipes.md
  - ../transpilation/babel-preset-env.md
  - ../meta/the-modern-baseline.md
  - ../meta/decision-tree.md
  - ../feature-detection/progressive-enhancement.md
primary_sources:
  - https://github.com/browserslist/browserslist — `dead`, `last N versions`, query semantics
  - https://github.com/browserslist/browserslist-ga — Google Analytics → browserslist-stats.json
  - https://www.npmjs.com/package/browserslist-plausible — Plausible Analytics → browserslist-stats.json
  - https://gs.statcounter.com/ — Statcounter Global Stats
  - https://plausible.io/docs/devices — Plausible's browser/version reporting surface
  - https://web.dev/articles/baseline-and-polyfills — modern Baseline guidance
  - https://www.debugbear.com/blog/how-does-browser-support-impact-bundle-size — measured bundle impact by target
---

# Anti-pattern: shipping polyfills for browsers you don't actually support

## The anti-pattern

The configuration shape varies; the underlying mistake is the same. A 2026 project with one of these in production:

```jsonc
// package.json — the kitchen-sink browserslist
{
  "browserslist": [
    "last 5 versions",
    "ie >= 10",
    "Firefox ESR",
    "> 0.25%",
    "not dead"
  ]
}
```

```js
// src/index.js — the "just in case" polyfill block
import 'core-js/stable';
import 'regenerator-runtime/runtime';
import 'whatwg-fetch';
import 'intersection-observer';
import 'resize-observer-polyfill';
import 'url-polyfill';
import 'classlist-polyfill';
import 'element-closest-polyfill';
```

```html
<!-- public/index.html — the belt-and-braces script tag -->
<script src="https://cdnjs.cloudflare.com/polyfill/v3/polyfill.min.js?features=fetch%2CPromise%2CObject.assign%2CIntersectionObserver"></script>
```

The team never measured. Nobody could name the last user who hit the legacy code path. The only justification anyone offered was **"what if a user is on an old browser?"** — phrased as a rhetorical question, treated as a closed argument.

The result: every modern user — which is to say, every user — pays for the legacy branch. Bundles inflate by **30–80 KB gzipped**. First contentful paint is delayed. Critical-path JS includes IE11 fallbacks for a browser that hit end-of-life in June 2022 and dropped below 0.1% global market share by mid-2023.

## What "defensive overpolyfilling" looks like in the wild

Six manifestations in approximate order of frequency:

1. **IE11 polyfills in a 2026 project.** `useBuiltIns: 'entry'` with a browserslist that resolves to include IE 11. `core-js/es/symbol`, `core-js/es/promise`, `regenerator-runtime`. `babel-polyfill` (deprecated since Babel 7, still showing up in legacy templates).
2. **Edge Legacy (pre-Chromium) polyfills.** Edge dropped its EdgeHTML engine in January 2020; new Edge is Chromium-only. Polyfills for the old Edge — `Microsoft Edge` versions 12–18 in browserslist queries — are pure waste in 2026.
3. **Safari < 13 polyfills with a declared Safari 17+ floor.** Common cause: a `last 4 Safari versions` query that nobody re-evaluated when the team set "Safari 17+" as the support floor in a marketing doc but never propagated the change to the build config.
4. **Babel `targets: 'last 5 versions'`** when the declared baseline is Chromium 125+ / Safari 17.4+ / Firefox 129+. `last 5 versions` includes Chrome 121, Safari 16.6, Firefox 125 — three versions below our baseline.
5. **Per-feature polyfill imports for native APIs.** `whatwg-fetch` (fetch is native everywhere since 2015), `intersection-observer` (native everywhere since 2019), `url-polyfill` (URL is native everywhere since 2018), `classlist-polyfill` (classList is native since IE10).
6. **`<script src="cdn.polyfill.io/...">`** even after the June 2024 supply-chain attack — the worst form, because it's both wasted bytes *and* a 3rd-party JS dependency. See [`./polyfill-io-after-attack.md`](./polyfill-io-after-attack.md).

## Why it persists

Five reasons, each compounding the others:

1. **Defensive coding mindset.** "What if a user is on an old browser?" is a question asked by someone who has not measured. The framing is sympathetic but the data is missing. The cost of *not* polyfilling is one user, on one browser, hitting a console error that never reaches your error monitor. The cost of polyfilling is every user paying every page load. The visible cost is invisible (a single broken session); the invisible cost is unmeasured (everyone's slower load). Defensive coding picks the invisible cost.
2. **Polyfills ship from copy-pasted templates.** `create-react-app` set `defaults` as the browserslist default circa 2017. The Vue CLI did the same. Many WordPress and Drupal themes baked in polyfill.io script tags. Years pass; the world moves; the templates don't.
3. **No post-incident review.** Most teams don't audit their polyfills until a security incident (polyfill.io) or a performance investigation (LCP regression) forces it. Without a forcing function, the legacy continues.
4. **"Supporting old browsers" sounds good in a brief.** Product, not engineering, often writes the support matrix. The brief says "support old Safari" because someone read a 2018 blog post about Safari market share. Engineering implements that brief literally — including iOS Safari 13, Edge Legacy, the long tail. Nobody returns to the brief to ask whether the support claim is still accurate.
5. **The audience is theoretical, not empirical.** The team has never run `npx browserslist --coverage=US`. They have never piped Plausible data through `browserslist-plausible` to derive real-audience targets. They have never opened a single user-agent log. The browser support discussion happens in the abstract.

## Why it's wrong at the modern baseline

### Bundle bloat is paid by everyone, not just the unsupported

This is the load-bearing point. **Polyfills don't selectively activate for old browsers.** They ship to every user, parse on every device, and execute (or are ignored) regardless of whether they're needed. A `core-js/stable` import that adds 60 KB gzipped to your bundle adds 60 KB to every user's first load — the Chrome 132 user, the Safari 17.5 user, the user on a brand-new iPhone. The "unsupported user" the polyfill exists to help is a fraction of a percent of traffic; the cost is borne 100% of the time.

Concrete numbers from real audits ([DebugBear's bundle-size analysis](https://www.debugbear.com/blog/how-does-browser-support-impact-bundle-size)):

- A typical TypeScript-React project with `target: "es5"` plus `useBuiltIns: 'entry'` plus a `last 5 versions, > 0.25%, not dead` browserslist: **~80 KB gzipped of pure polyfill + transpilation overhead**, on a 200 KB application bundle. 40% bloat ratio.
- The same project with the modern baseline (`chrome >= 125, firefox >= 129, safari >= 17.4`), `target: "ES2022"`, `useBuiltIns: 'usage'`: **~120 KB total bundle**. 40% smaller. No functional regression for any modern user.
- The narrowest case (the canonical recipe in this skill, `useBuiltIns: false`, no Babel polyfilling): **~100 KB total bundle**. 50% smaller than the defensive-overpolyfilled version.

### Maintenance burden compounds

Every polyfill is a dependency to track. `whatwg-fetch` had a CVE in 2018. `core-js` has had funding-sustainability concerns since 2023 (single maintainer; see [`../landscape-shifts/core-js-funding-status.md`](../landscape-shifts/core-js-funding-status.md)). `regenerator-runtime` is pinned to specific Babel versions. `intersection-observer` polyfill has known semantic drift from the spec on edge cases (`isIntersecting` boundary behavior). Each polyfill in your dependency tree:

- Is tracked by Renovate / Dependabot, generating PRs your team must review.
- Adds attack surface to your supply chain.
- Has its own version-resolution rules that interact with peer dependencies.
- May become unmaintained without notice.

The fewer polyfills, the smaller this surface area. **Trimming polyfills is a security-and-maintenance win, not just a performance win.**

### Polyfills can't fix all bugs

A polyfill is a JS implementation of a feature the engine lacks. It cannot patch:

- DOM-engine differences (e.g. iOS Safari 17.0–18.2 popover light-dismiss bug — see [`../popover-quirks/ios-safari-light-dismiss.md`](../popover-quirks/ios-safari-light-dismiss.md))
- CSS layout bugs (e.g. Safari < 18 OKLCH `color-mix` red-shift — see [`../css-color-bugs/oklch-oklab-safari.md`](../css-color-bugs/oklch-oklab-safari.md))
- Performance characteristics (a polyfilled `IntersectionObserver` runs in JS via `setTimeout`-driven scroll polling; it has different perf characteristics from the native one)
- Security primitives (Web Crypto, Trusted Types, CSP enforcement)
- Form/validation primitives (ElementInternals, `:state()`)

"Supporting" old browsers via polyfills implies an experience parity that polyfills can't deliver. The user on Safari 13 with your polyfilled bundle still encounters bugs your QA didn't test, performance degradation your benchmarks didn't capture, and missing features you can't shim. **Declaring "we don't support Safari 13" is more honest than partially supporting it via polyfills.**

### Audience reality: the long tail is sub-1%

If you run [`gs.statcounter.com`](https://gs.statcounter.com/) for any month in 2026, the global browser distribution looks roughly like:

- Chrome: ~65% (mostly current major + previous one or two)
- Safari: ~18% (mostly current major + previous one)
- Edge: ~5% (Chromium-based)
- Firefox: ~3%
- Samsung Internet, Opera, others: ~9%
- IE11: < 0.1% — and concentrated in specific markets (parts of East Asia, internal corporate fleets)
- Edge Legacy (pre-Chromium): ~0.0% — effectively gone

Your audience may differ from global stats. A B2B SaaS skewed toward US enterprise has more Edge. A consumer-fashion brand skewed toward iOS-heavy markets has more Safari. **None of these audiences include enough IE11 users to justify the bundle cost of supporting them.** The exception is a very specific set of legacy enterprise (Korean banking, Chinese government, internal industrial systems) where IE11 is contractually required — and those projects know it; they don't reach for this skill.

## The fix

A four-step migration from defensive overpolyfilling to a measured, minimal posture.

### Step 1 — Measure your actual user-agent distribution

Pick one of these data sources:

```sh
# Option A — Plausible Analytics (privacy-respecting, open-source)
# Configure browserslist-plausible to read your Plausible site stats:
npx browserslist-plausible --site yoursite.com --duration 30d > browserslist-stats.json

# Option B — Google Analytics (GA4)
# browserslist-ga reads GA4's `Browser` and `Browser Version` dimensions:
npx browserslist-ga --view-id $GA_VIEW_ID > browserslist-stats.json

# Option C — Statcounter (global, no per-site data)
# Just use the canonical query at this skill's baseline:
npx browserslist 'chrome >= 125, firefox >= 129, safari >= 17.4' --coverage
```

The output of `browserslist-plausible` or `browserslist-ga` is a `browserslist-stats.json` file with rows like `Chrome 132: 12.4%, Safari 17.5: 8.1%, ...` The shape is the same as Statcounter's global data, but tailored to your real audience.

### Step 2 — Set browserslist to match your 95th-or-higher percentile

Once you have `browserslist-stats.json`, run:

```sh
npx browserslist '> 0.5% in my stats, not dead' --coverage
# Or, more aggressive:
npx browserslist '> 1% in my stats, not dead' --coverage
```

The `> N% in my stats` query reads your project-local stats file rather than global Statcounter data. The output tells you what percentage of *your audience* your query covers. Aim for 95%+; better, 99%.

For most modern web projects the result will be a tight floor — Chrome ≥ 125 or higher, Safari ≥ 17.4 or higher, Firefox ≥ 129 or higher — closely matching this skill's canonical baseline. If your data shows a meaningfully different floor (e.g. you have a Korean enterprise audience with a long IE11 tail), you'll see it; otherwise, the modern floor is the right answer.

### Step 3 — Declare what you don't support

Document this explicitly. In a `BROWSER_SUPPORT.md` at the project root, or in your release notes, or in your customer-facing docs:

> **Supported browsers**: Chrome 125+, Edge 125+, Safari 17.4+, Firefox 129+, iOS Safari 17.4+, Chrome on Android 125+. Other browsers are not tested. Older versions may work but are not supported.

This is more honest than "we support all browsers." It is more useful than silently partial support via polyfills. If a customer reports a bug from Safari 16.5, your support team has a clear answer.

The same declaration goes in your CI: a Playwright matrix that runs against the supported browsers, no others. Your ground-truth functional verification matches your declared support.

### Step 4 — Trim polyfills accordingly

With the new browserslist in place, the polyfill cleanup proceeds mechanically:

```sh
# Step 1: identify what's still being included
npx webpack-bundle-analyzer dist/stats.json
# Or: npx vite-bundle-visualizer
# Or: npx source-map-explorer dist/assets/*.js

# Step 2: remove explicit polyfill imports for native-at-baseline features
# Edit src/index.js — delete:
#   import 'whatwg-fetch';
#   import 'intersection-observer';
#   import 'resize-observer-polyfill';
#   import 'url-polyfill';
#   import 'classlist-polyfill';
#   import 'element-closest-polyfill';

# Step 3: switch Babel useBuiltIns from 'entry' to 'usage' (or 'false')
# See ./corejs-entry-modern.md

# Step 4: uninstall the now-unused packages
npm uninstall whatwg-fetch intersection-observer resize-observer-polyfill \
  url-polyfill classlist-polyfill element-closest-polyfill \
  babel-polyfill

# Step 5: rebuild + re-measure
npm run build
npx webpack-bundle-analyzer dist/stats.json
```

The "after" bundle should be 30–80 KB gzipped smaller. If it isn't, your browserslist still has bloat — verify with `npx browserslist` that the resolved version list looks like your modern baseline.

## The "graceful degradation" alternative

For the rare case that a meaningful slice of your audience genuinely is on an unsupported browser — you measured, and 1.2% of your traffic is on Safari 16 — the modern alternative to polyfilling is **graceful degradation at the page level**, not at the JS-runtime level.

Two patterns:

### Pattern A — Static HTML fallback

Ship modern code at full speed for the supported audience. For unsupported browsers, render a server-side static HTML view that doesn't require the modern JS. This works particularly well for SSR-first frameworks (Next.js, Remix, Astro):

```js
// In your SSR entrypoint, detect critical-feature support server-side:
import { matchesUA } from 'browserslist-useragent';

export async function loader({ request }) {
  const ua = request.headers.get('user-agent');
  const supported = matchesUA(ua, {
    browsers: ['chrome >= 125', 'firefox >= 129', 'safari >= 17.4']
  });
  if (!supported) {
    // Render a non-interactive HTML fallback
    return redirect('/legacy/static.html');
  }
  // ... normal modern flow
}
```

The legacy user gets a working static page with text and links. They don't get the interactive client-side experience. They don't get a polyfilled approximation. They get an honest, working subset.

### Pattern B — "Please upgrade" page with detection

For applications where the static fallback isn't viable (heavy SaaS dashboards, complex SPAs), ship a small detection script that fires before the main bundle and redirects unsupported browsers to an upgrade page:

```html
<!-- public/index.html -->
<script>
  // ~200 bytes of feature-detect; uses no modern syntax itself
  if (
    typeof Promise === 'undefined' ||
    typeof fetch === 'undefined' ||
    typeof IntersectionObserver === 'undefined' ||
    !('replaceChildren' in Element.prototype)
  ) {
    location.replace('/upgrade.html');
  }
</script>
<!-- ...rest of the page loads modern JS only -->
```

`upgrade.html` is a static, 5KB page that explains the supported browsers and links to download Chrome / Firefox / Safari. The detection script tests for the *minimum* features your app requires; the main bundle assumes them. Modern users see the script run for ~1ms and are unblocked. Legacy users see the upgrade page and have an honest path forward.

This is genuinely uglier UX than "we support every browser." It is also genuinely better engineering than "we partially support every browser via 80 KB of polyfills." The trade-off is a deliberate choice your team should make explicitly, not a default that drifts in from a 2017 boilerplate.

## Verification checklist

Before declaring an audit complete:

- [ ] `npx browserslist` returns a version list that matches the documented support floor — no IE 11, no Edge Legacy, no Safari < 17.4 unless deliberately included.
- [ ] `npx browserslist --coverage` (or with `--coverage=US` etc.) reports ≥ 95% audience coverage.
- [ ] No `import 'whatwg-fetch'` / `import 'intersection-observer'` / etc. in source — none of these features need polyfilling at the modern baseline.
- [ ] No `<script src="cdn.polyfill.io">` or mirror equivalents in HTML/templates. See [`./polyfill-io-after-attack.md`](./polyfill-io-after-attack.md).
- [ ] Bundle analyzer (webpack / vite / esbuild) shows zero `core-js/modules/*` chunks — or, if `useBuiltIns: 'usage'` is on, only the chunks that match documented gaps (Iterator helpers for Safari 17.4–18.3, Temporal for Safari at-baseline, etc.).
- [ ] Babel/SWC/esbuild target matches the documented support floor.
- [ ] A `BROWSER_SUPPORT.md` (or equivalent) declares what the project supports and what it doesn't.
- [ ] CI runs Playwright (or equivalent) against the supported browsers — not "all browsers", not unspecified.

## When defensive overpolyfilling is actually correct

Two cases. Both rare:

1. **You're a public-facing library.** `lodash`, `axios`, `react`, `vue` — the consumer's audience is unknown. Library authors typically polyfill conservatively and document a minimum browser target. But: most modern libraries instead emit ESM, target ES2020, and document a floor. If you're at this skill's baseline, your library authors should be too.
2. **You have a contractual obligation to a specific legacy environment.** Korean banking (IE11 was mandated until 2024 in some financial subsystems). Chinese government portals (still mandated for some agencies). Industrial control systems (Siemens HMIs, some SCADA frontends). These projects know they're legacy; they don't reach for this skill.

For everyone else: measure, declare, trim.

## Cross-reference

- [`./corejs-entry-modern.md`](./corejs-entry-modern.md) — the related anti-pattern: shipping core-js even when targets are correct.
- [`./target-es5-modern.md`](./target-es5-modern.md) — its sibling: targeting ES5 in tsconfig.
- [`./preset-env-no-browserslist.md`](./preset-env-no-browserslist.md) — what happens when no browserslist is configured.
- [`./polyfill-io-after-attack.md`](./polyfill-io-after-attack.md) — the worst form of defensive overpolyfilling.
- [`../build-tools/browserslist-recipes.md`](../build-tools/browserslist-recipes.md) — the canonical baseline query.
- [`../meta/decision-tree.md`](../meta/decision-tree.md) — "do I need a polyfill?" flowchart.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what Chromium 125 / Safari 17.4 / Firefox 129 means in practice.
- [`../feature-detection/progressive-enhancement.md`](../feature-detection/progressive-enhancement.md) — the modern alternative pattern.
