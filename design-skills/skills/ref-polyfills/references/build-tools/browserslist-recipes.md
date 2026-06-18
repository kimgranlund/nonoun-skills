---
date: 2026-04-27
coverage: canonical
peers:
  - ../build-tools/vite-build-target.md
  - ../build-tools/lightningcss-features.md
  - ../build-tools/postcss-preset-env.md
  - ../build-tools/esbuild-config.md
  - ../build-tools/tsconfig-lib-target.md
  - ../transpilation/babel-preset-env.md
  - ../transpilation/swc-targets.md
  - ../transpilation/esbuild-targets.md
  - ../anti-patterns/preset-env-no-browserslist.md
  - ../anti-patterns/target-es5-modern.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://browsersl.ist/ — interactive query inspector with audience-coverage data (Statcounter-backed)
  - https://github.com/browserslist/browserslist — main repo, README, query syntax reference
  - https://github.com/browserslist/browserslist/blob/main/README.md — full query syntax including Baseline queries (4.26.0+)
  - https://github.com/browserslist/caniuse-lite — usage data subset (caniuse + Statcounter)
  - https://web.dev/articles/use-baseline-with-browserslist — Baseline integration guide
  - https://web.dev/blog/browserslist-supports-baseline — Baseline query announcement
  - https://gs.statcounter.com/ — underlying global usage statistics
---

# Browserslist — recipes for the modern baseline

The single most-cited config in this skill. Browserslist is the shared engine-target query language that powers Babel, autoprefixer, postcss-preset-env, Lightning CSS, SWC, and (via wrappers) esbuild. Every other tool in the build-tools/ axis reads from one of these queries.

> The TL;DR: at our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+), the canonical query is three lines:
>
> ```
> chrome >= 125
> firefox >= 129
> safari >= 17.4
> ```
>
> Everything else in this file is variant, expansion, or audit guidance.

## What browserslist is

Browserslist is a query language plus a runtime that selects engine versions from the [`caniuse-lite`](https://github.com/browserslist/caniuse-lite) database. The data comes from caniuse + [Statcounter Global Stats](https://gs.statcounter.com/). The runtime is a Node module, but the query syntax is shared across every modern build tool — write one query, every tool obeys.

The interactive query inspector — [browsersl.ist](https://browsersl.ist/) — is the canonical way to verify what a query resolves to. It shows expanded version lists, audience coverage by region, and lets you A/B different queries side-by-side.

## The canonical baseline query

Three lines, configured as `.browserslistrc` in the project root or as `"browserslist"` in `package.json`:

```
chrome >= 125
firefox >= 129
safari >= 17.4
```

This is the **Wave 1-verified** query for the expert-polyfills baseline. Every reference file in this skill assumes it.

A few notes on the form:

- **Comma between lines is implicit OR.** `.browserslistrc` lines are OR-ed; `package.json` array entries are also OR-ed. `chrome >= 125, firefox >= 129, safari >= 17.4` (single-line) is equivalent.
- **Engine names are case-insensitive.** `Chrome >= 125` works; `chrome >= 125` works; `CHROME >= 125` works.
- **Decimal versions are valid.** Safari ships `17.4`, `17.5`, `17.6`, `18.0` — not `17`. `safari >= 17.4` is precise; `safari >= 17` is too lax (would match 17.0 and 17.2 which lack our baseline features).
- **No upper bound.** No `<= 130`. Browserslist queries are floor-only by convention.

## Common expansions of the canonical query

### Including Edge

Edge tracks Chromium release-for-release; Edge 125 ≡ Chrome 125 in feature support. The default browserslist behavior is to **include Edge automatically when you write `chrome >= N`**, because both engines share the Chromium engine identifier in caniuse data. Some build tools want explicit:

```
chrome >= 125
edge >= 125
firefox >= 129
safari >= 17.4
```

Functionally equivalent for transpilation; explicit is safer if you're auditing engine-by-engine.

### Including mobile

Mobile WebViews lag desktop in some markets. Add explicit mobile engines:

```
chrome >= 125
firefox >= 129
safari >= 17.4
chrome_android >= 125
safari_ios >= 17.4
firefox_android >= 129
```

The browserslist names are `chrome_android` (or `and_chr`), `safari_ios` (or `ios_saf`), `firefox_android` (or `and_ff`). Both forms parse — `chrome_android` is the documented spelling, `and_chr` is what caniuse returns internally.

### Including Samsung Internet

Samsung Internet is a Chromium derivative that lags Chrome by ~6 months. The mapping from Samsung-Internet major to Chromium major:

| Samsung Internet | Chromium engine | Approx. ship date |
|---|---|---|
| 21 | Chromium 102 | Q3 2023 |
| 22 | Chromium 108 | Q1 2024 |
| 23 | Chromium 115 | Q2 2024 |
| 24 | Chromium 121 | Q4 2024 |
| 25 | Chromium 122 | Q1 2025 |
| 26 | Chromium 130 | Q3 2025 |
| 27 | Chromium 133 | Q1 2026 |

To approximate Chrome ≥ 125 in Samsung terms, use `samsung >= 26`. Samsung 25 (~Chrome 122) is just below our floor; if your audience is Samsung-heavy, decide whether to gate at 25 or 26. Verify with [browsersl.ist](https://browsersl.ist/) — Samsung version data is updated less frequently than Chrome's.

### Including Opera

`opera >= 110` ≈ Chromium 124 (close to our floor). Opera tracks Chromium with a small lag; explicit Opera versions are rarely necessary, but the query syntax supports it.

### Excluding dead browsers

```
not dead
not IE 11
```

`not dead` is the convention — it excludes browsers without official updates for ≥ 24 months. ([browserslist README](https://github.com/browserslist/browserslist/blob/main/README.md)) Always include `not dead` to keep zombie browsers (Blackberry, IE Mobile, etc.) out.

`not IE 11` is technically redundant when `not dead` is present (IE 11 is dead since 2022) but explicit is safer — some legacy `caniuse-lite` databases lag behind on the `dead` definition.

## Production-ready recipes

### A — Modern web app, our baseline (the canonical recipe)

```
chrome >= 125
edge >= 125
firefox >= 129
safari >= 17.4
chrome_android >= 125
safari_ios >= 17.4
not dead
```

Tight floor; covers every supported engine in the expert-polyfills baseline. Mobile included. Use this as the default for new projects at this baseline.

### B — Library author, looser baseline

If you're publishing a library to npm, your audience is broader than your dogfooded app's. A standard library-publishing query:

```
last 3 chrome versions
last 3 firefox versions
last 3 safari versions
last 3 edge versions
not dead
not IE 11
```

`last 3 versions` is rolling; it always includes the current version + two previous. Looser than our canonical query (Safari 17.2 might still be in the floor for a few months), but sane for a library that doesn't control the consumer's deployment target.

### C — Mobile-first webapp

```
chrome_android >= 125
safari_ios >= 17.4
firefox_android >= 129
samsung >= 26
not dead
```

For a PWA or mobile-only product. Drops desktop entirely; some build tools may complain — verify each tool reads the mobile engines. Most modern ones (Lightning CSS, postcss-preset-env, Babel preset-env) handle mobile engines transparently.

### D — Internal tool with controlled environment

```
chrome >= 125
edge >= 125
```

Some enterprises ship managed Chrome / Edge to all employees. Drop Firefox and Safari entirely. Allows the most aggressive transpilation savings (no need to lower for cross-engine differences). Use only when you genuinely control the deployed browser.

### E — Baseline-aware (uses Browserslist 4.26+ syntax)

Browserslist 4.26.0 (released September 2025) added native [Baseline queries](https://web.dev/blog/browserslist-supports-baseline):

```
baseline widely available
not dead
```

`baseline widely available` selects engines that support all features in the [Baseline Widely Available](https://web-platform-dx.github.io/web-features/) set — features interoperable across the Baseline core browsers (Chrome, Edge, Firefox, Safari) for ≥ 30 months. As of April 2026, this resolves to roughly Chrome 111 / Firefox 114 / Safari 16.4 — **looser than our floor**.

For a tighter Baseline cut:

```
baseline widely available on 2026-01-01
```

Or pin to a year:

```
baseline 2024
```

Useful if your team thinks in Baseline terms, but the date-pinned form drifts with each engine release. Most teams find the explicit-version form (`chrome >= 125`) more predictable.

## The `defaults` query — what it actually resolves to

`defaults` is browserslist's most common shortcut and the one most likely to be wrong:

```
> 0.5%, last 2 versions, Firefox ESR, not dead
```

Components:

- `> 0.5%` — any browser with > 0.5% global market share. Includes ancient versions of Chrome/Safari with persistent installations.
- `last 2 versions` — last two majors of every tracked engine. **Including dead engines** unless paired with `not dead`.
- `Firefox ESR` — current Firefox Extended Support Release. Drifts to the long-term-support version, not the latest.
- `not dead` — excludes engines without updates in 24 months.

What this resolves to in April 2026 (rough):

```
Chrome >= 119, Firefox >= 122, Safari >= 16.4, Edge >= 132,
Opera >= 102, Samsung >= 23, ChromeAndroid >= 130,
FirefoxAndroid >= 122, SafariIOS >= 16.4, ...
```

That's a much wider net than our baseline. **`defaults` is almost always wrong for modern web projects** — it includes engines below our floor, defeats native fast paths, and inflates bundles. Replace it with the canonical query above.

A lot of projects inherit `defaults` from a tool default (e.g. `create-react-app` set it years ago; `@babel/preset-env` falls back to it when no `targets` is configured — see [`../anti-patterns/preset-env-no-browserslist.md`](../anti-patterns/preset-env-no-browserslist.md)).

## Where to put the query

Three valid locations, in order of preference:

### 1. `package.json` `"browserslist"` field

```jsonc
{
  "name": "my-app",
  "version": "1.0.0",
  "browserslist": [
    "chrome >= 125",
    "firefox >= 129",
    "safari >= 17.4",
    "not dead"
  ]
}
```

**Preferred** — shareable across tools, no extra file, version-controlled with the rest of project metadata. Every modern tool reads it.

### 2. `.browserslistrc`

```
# .browserslistrc
chrome >= 125
firefox >= 129
safari >= 17.4
not dead
```

Also fine; useful when the query is large or commented. Some teams prefer one file per concern; others prefer fewer files.

### 3. Per-tool config (Babel `targets`, Lightning CSS `targets`, etc.)

```js
// babel.config.js
module.exports = {
  presets: [['@babel/preset-env', {
    targets: {
      chrome: '125',
      firefox: '129',
      safari: '17.4',
    },
  }]],
};
```

**Use only when you need a tool-specific override** — e.g. a worker bundle that targets a different engine floor than the main app. For the common case where every tool reads the same query, prefer `package.json` `"browserslist"` and let each tool auto-discover.

## Per-tool browserslist support matrix

The asymmetric one. Every tool in the modern stack treats browserslist differently:

| Tool | Browserslist support | Notes |
|---|---|---|
| `@babel/preset-env` | **Full** (auto-discover from `package.json` / `.browserslistrc`) | Default since Babel 7; `bugfixes: true` strongly recommended |
| `autoprefixer` | **Full** | Reads browserslist directly; the most-cited consumer of the format |
| `postcss-preset-env` | **Full** | Auto-discovers; `browsers` option overrides |
| `lightningcss` | **Full** | `browserslistToTargets()` adapter; auto-detects in Vite/Bun/Parcel pipelines |
| `cssnano` | **Full** | Reads browserslist for unsafe-optimization gating |
| `SWC` | **Full** (since v1.1.10) | `env.targets` auto-discovers if not set explicitly; ([fix(preset-env) PR #8921](https://github.com/swc-project/swc/pull/8921)) |
| `esbuild` | **NONE** | Use `browserslist-to-esbuild` or hardcode versions; long-running [issue #121](https://github.com/evanw/esbuild/issues/121) |
| `Vite` `build.cssTarget` | **Full** | Reads browserslist when not set explicitly |
| `Vite` `build.target` | **NONE** (uses esbuild) | Either hardcode versions or use `browserslist-to-esbuild` |
| `tsc` | **NONE** | TypeScript ignores browserslist; `target` is independent |
| `Rollup` | **None natively**; relies on plugins | Use `@rollup/plugin-babel` which reads browserslist |
| `webpack` | Indirect (via loaders) | Babel-loader, css-loader, etc. each read browserslist independently |

The two big drop-offs are **esbuild** and **TypeScript** — both ignore browserslist by design. Bridge with `browserslist-to-esbuild` for esbuild, or hardcode the same engine versions in `tsconfig.json`'s `target` (note: TS uses ECMAScript syntax levels, not engine versions — see [`./tsconfig-lib-target.md`](./tsconfig-lib-target.md)).

## Verifying coverage

The CLI:

```sh
# Show resolved version list for a query
npx browserslist 'chrome >= 125, firefox >= 129, safari >= 17.4'

# Show audience coverage globally
npx browserslist 'chrome >= 125, firefox >= 129, safari >= 17.4' --coverage

# Show audience coverage in a specific country
npx browserslist 'chrome >= 125, firefox >= 129, safari >= 17.4' --coverage=US
npx browserslist 'chrome >= 125, firefox >= 129, safari >= 17.4' --coverage=DE
npx browserslist 'chrome >= 125, firefox >= 129, safari >= 17.4' --coverage=alt-AS
```

Underlying data: [Statcounter Global Stats](https://gs.statcounter.com/), refreshed by [`caniuse-lite`](https://github.com/browserslist/caniuse-lite) updates. Cite Statcounter when reporting coverage figures externally.

The interactive equivalent is [browsersl.ist](https://browsersl.ist/) — paste a query, see the version list and audience coverage by region. Faster for ad-hoc verification.

## Refreshing `caniuse-lite`

Browserslist's data is shipped via the `caniuse-lite` package. Stale data ⇒ stale queries. Run periodically:

```sh
npx update-browserslist-db@latest
```

Or as `npx browserslist@latest --update-db`. Updates the `caniuse-lite` lock without touching your application's `node_modules` resolution. CI projects often add this to a quarterly maintenance task.

## Audit checklist for an existing project

When taking over a project, verify the browserslist config in this order:

1. `cat package.json | grep -A 5 browserslist` — explicit config in package.json?
2. `ls .browserslistrc` — separate config file?
3. `grep -rn 'targets:' babel.config.* .babelrc* postcss.config.*` — per-tool overrides?
4. `npx browserslist` (no args, in project root) — actual resolved version list?
5. `npx browserslist --coverage=US` — audience coverage at the resolved query?

If step 4 returns Chrome 87, Safari 14, or anything pre-2022, you're over-targeting at our baseline. Step 5 sanity-checks the trade-off — covering 99.9% of users vs covering 99% may not be worth a 30 KB bundle.

## Cross-references

- [`./vite-build-target.md`](./vite-build-target.md) — how Vite reads (and doesn't read) browserslist.
- [`./lightningcss-features.md`](./lightningcss-features.md) — Lightning CSS's `browserslistToTargets()` adapter.
- [`./postcss-preset-env.md`](./postcss-preset-env.md) — auto-discovery and the `browsers` override.
- [`./esbuild-config.md`](./esbuild-config.md) — the no-browserslist tool; `browserslist-to-esbuild` recipe.
- [`./tsconfig-lib-target.md`](./tsconfig-lib-target.md) — TypeScript's separate, browserslist-ignorant target system.
- [`../transpilation/babel-preset-env.md`](../transpilation/babel-preset-env.md) — preset-env browserslist auto-discovery.
- [`../transpilation/swc-targets.md`](../transpilation/swc-targets.md) — SWC's auto-discovery (since v1.1.10).
- [`../anti-patterns/preset-env-no-browserslist.md`](../anti-patterns/preset-env-no-browserslist.md) — what happens when targets are unset.
- [`../anti-patterns/target-es5-modern.md`](../anti-patterns/target-es5-modern.md) — why over-broad queries hurt at this baseline.
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what the canonical floor means in practice.
