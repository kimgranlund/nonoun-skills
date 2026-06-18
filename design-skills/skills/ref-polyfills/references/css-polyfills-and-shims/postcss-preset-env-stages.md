---
date: 2026-04-27
coverage: extended
peers:
  - ../build-tools/postcss-preset-env.md
  - ../build-tools/lightningcss-features.md
  - ../build-tools/browserslist-recipes.md
  - ./lightningcss-css-lowering.md
  - ./at-property-fallbacks.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://github.com/csstools/cssdb/blob/main/STAGES.md — exact stage definitions (0–4)
  - https://cssdb.org/ — CSS feature staging database
  - https://preset-env.cssdb.org/features/ — full feature list with stages
  - https://preset-env.cssdb.org/ — postcss-preset-env homepage
  - https://github.com/csstools/postcss-plugins/wiki/PostCSS-Preset-Env-8 — preset-env 8 changelog (introduces enableClientSidePolyfills)
  - https://www.npmjs.com/package/postcss-preset-env — npm; latest 11.2.x as of April 2026
  - https://github.com/csstools/postcss-plugins/blob/main/plugin-packs/postcss-preset-env/CHANGELOG.md — release history
---

# postcss-preset-env stages — cssdb stage detail at our baseline

> **Status at 2026-04-27.** This file is the **cssdb-stage-detail angle**. For the build-tool angle (when to choose preset-env vs Lightning CSS, config recipes, migration notes) see `../build-tools/postcss-preset-env.md`. At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+), most Stage-4 features are already native — preset-env's value at our floor is mostly Stage-2 features that don't have native shipping anywhere.

## The five stages

Per [cssdb STAGES.md](https://github.com/csstools/cssdb/blob/main/STAGES.md), feature progression through cssdb maps to W3C maturity stages:

| Stage | Name | Description |
|---|---|---|
| **0** | **Aspirational** | "This is a silly idea." Unofficial / Editor's Draft championed by a single W3C WG member; highly unstable. Don't ship. |
| **1** | **Experimental** | "This idea might not be silly." Editor's Draft / early Working Draft; a real problem is recognized, but no committed solution. |
| **2** | **Allowable** (default) | "This idea is not silly." Working Draft championed by a W3C Working Group; relatively unstable, tied to a specific solution. |
| **3** | **Embraced** | "This idea is becoming part of the web." Candidate Recommendation; usually 2+ vendor implementations; little expected change. |
| **4** | **Standardized** | "This idea is part of the web." W3C Recommendation; implemented by all recognized vendors. Native everywhere. |

postcss-preset-env's `stage` config selects the **lower bound** of which features to apply. Default is `stage: 2` — applies Stage 2, 3, and 4. Setting `stage: 3` excludes Stage 2; setting `stage: 1` includes Stage 1 (riskier).

## Stage 4 features at our baseline — already native, no lowering needed

These are the success stories. Stage 4 means W3C Recommendation, multi-vendor shipping, baseline status. At our floor, lowering them is wasted effort.

| Feature | Native floor | Conclusion |
|---|---|---|
| Custom Properties (CSS Variables) | Chrome 49 / Firefox 31 / Safari 9.1 | Native everywhere — no lowering |
| `:has()` selector | Chrome 105 / Firefox 121 / Safari 15.4 | Native — no lowering |
| CSS Nesting (`& .child`) | Chrome 120 / Firefox 117 / Safari 17.2 | Native — no lowering |
| Logical properties | Chrome 87 / Firefox 66 / Safari 14.1 | Native — no lowering |
| Cascade layers (`@layer`) | Chrome 99 / Firefox 97 / Safari 15.4 | Native — no lowering |
| `aspect-ratio` | Chrome 88 / Firefox 89 / Safari 15 | Native — no lowering |
| Container queries | Chrome 105 / Firefox 110 / Safari 16 | Native — no lowering |
| Color functional notation (`rgb(255 0 0)`) | Chrome 65 / Firefox 52 / Safari 12.1 | Native — no lowering |
| Hex with alpha (`#rrggbbaa`) | Chrome 62 / Firefox 49 / Safari 10 | Native — no lowering |
| Two-value `display` syntax (`display: inline flow-root`) | Chrome 115 / Firefox 70 / Safari 15 | Native — no lowering |

If you're on preset-env at our baseline, the Stage-4 features are passing through with no transformation applied. **The bytes Lightning CSS would also pass through unchanged.** No polyfill cost, no lowering cost.

## Stage 3 features at our baseline — also mostly native

Stage 3 ("Embraced," Candidate Recommendation, 2+ vendor commitments) at our floor:

| Feature | Native floor | Conclusion |
|---|---|---|
| `oklch()` / `oklab()` / `lab()` / `lch()` | Chrome 111 / Firefox 113 / Safari 15.4 | Native — no lowering |
| `color()` with display-p3 | Chrome 111 / Firefox 113 / Safari 15 | Native (Firefox renders mapped to sRGB; see `../css-color-bugs/display-p3-firefox-lag.md`) |
| `color-mix()` | Chrome 111 / Firefox 113 / Safari 16.2 | Native — no lowering (with quirks; see `../css-color-bugs/color-mix-interpolation.md`) |
| `light-dark()` | Chrome 123 / Firefox 120 / Safari 17.5 | Native at our floor (Safari 17.5 just past 17.4) |
| `text-wrap: balance` | Chrome 114 / Firefox 121 / Safari 17.5 | Native at our floor |
| `:nth-child(an+b of selector)` | Chrome 111 / Firefox 113 / Safari 9 | Native — no lowering |

Stage 3 is also mostly native. preset-env's lowering here is dormant at our baseline.

## Stage 2 features at our baseline — the interesting ones

Stage 2 is where preset-env's value shows up at our floor. These features have W3C Working Group commitment and a specific solution, but multi-vendor native shipping isn't there yet.

| Feature | Stage | Native at our floor? | Lower via preset-env? |
|---|---|---|---|
| **`@custom-media`** | 2 | **Not native anywhere** | **Yes — preset-env genuinely useful** |
| **`@custom-selectors`** | 2 | **Not native anywhere** | **Yes — preset-env genuinely useful** |
| Relative color syntax (`oklch(from base ...)`) | 2 | Native at our floor (Chrome 119, Safari 16.4, Firefox 128) | No |
| `@scope` | 2 | NOT in Firefox 129–145; preset-env doesn't lower | n/a — see `./at-property-fallbacks.md` |
| Trigonometric color functions (`hsl(from blue calc(h + 30) s l)`) | 2 | Mostly native; verify per sub-feature | Edge case |
| `@property` | 2 / advancing | Native at our floor (Chrome 85 / Firefox 128 / Safari 16.4) | No |

The two genuinely useful preset-env Stage-2 features at our baseline are **`@custom-media`** and **`@custom-selectors`**.

### `@custom-media` — preset-env still earns its keep here

```css
/* Source — Stage 2 syntax */
@custom-media --small (max-width: 480px);
@custom-media --large (min-width: 1024px);

.button {
  @media (--small) { padding: 0.5rem; }
  @media (--large) { padding: 1.5rem; }
}
```

```css
/* preset-env output — inline expansion */
.button {
  @media (max-width: 480px) { padding: 0.5rem; }
  @media (min-width: 1024px) { padding: 1.5rem; }
}
```

`@custom-media` is genuinely useful for DRY breakpoint definitions, and **no engine ships it natively** as of April 2026. preset-env handles the lowering at build time; the output is plain `@media` queries that work everywhere. Lightning CSS does NOT do this lowering; it passes `@custom-media` through unchanged, breaking the page on every browser.

If you use `@custom-media`, **stay on preset-env** until native lands. (Tracking: it's been Stage 2 for a long time; not currently scheduled for Stage 3 promotion.)

### `@custom-selectors` — same story

```css
/* Source */
@custom-selector :--heading h1, h2, h3, h4, h5, h6;

article :--heading {
  font-family: var(--font-display);
}
```

```css
/* preset-env output */
article h1,
article h2,
article h3,
article h4,
article h5,
article h6 {
  font-family: var(--font-display);
}
```

Native nowhere; preset-env lowers cleanly. Useful for keeping selector lists DRY.

## The interplay with `enableClientSidePolyfills`

Per the [postcss-preset-env 8 changelog](https://github.com/csstools/postcss-plugins/wiki/PostCSS-Preset-Env-8): preset-env 8.0 introduced the `enableClientSidePolyfills` option. Default: `false`.

> *"Plugins that require browser polyfills transform your CSS in ways that make you dependent on the browser polyfill. As these plugins are rarely used and can appear to break your CSS, they are disabled by default."*

When `enableClientSidePolyfills: false` (default), preset-env skips features that need a runtime browser library — even if you'd otherwise opt into them via `stage` or `features`. This includes:

- **PostCSS Custom Media** (specifically when used in JS contexts that require runtime resolution)
- **PostCSS Custom Properties** (the JS-API parts; the CSS at-rule lowering still happens)
- **PostCSS Custom Selectors** (the JS-runtime aspects)

The CSS-only build-time portion of these features still runs. The flag specifically gates the **runtime JS** that some plugins ship.

### Why `enableClientSidePolyfills: true` is usually wrong

Client-side polyfills are typically **bigger than build-time transforms** — and by definition they need runtime JS in the user's browser. The trade-off:

| Approach | Bundle cost on user | Browser support |
|---|---|---|
| Build-time transform (preset-env default) | 0 bytes | Whatever the lowered output supports |
| Client-side polyfill (`enableClientSidePolyfills: true`) | KB-scale runtime | Whatever the polyfill supports |

**Favor build-time when possible.** If a feature can be lowered at build time, do that. Reach for client-side polyfills only when:

1. The feature genuinely cannot be lowered at build time (anchor positioning, scroll-driven animations, view transitions — but preset-env doesn't ship polyfills for these; you'd use OddBird / flackr packages directly).
2. You need the same runtime semantics across all browsers, not just the static output.

In practice, **leave `enableClientSidePolyfills: false`** at our baseline. The runtime polyfills preset-env wraps are mostly historical; the modern answer for runtime CSS is the dedicated polyfills (`@oddbird/css-anchor-positioning`, etc.) used directly.

## Recommended preset-env config at our baseline

```js
// postcss.config.js
module.exports = {
  plugins: [
    require('postcss-preset-env')({
      stage: 3,                      // more conservative than default 2
      minimumVendorImplementations: 2, // exclude single-vendor features
      enableClientSidePolyfills: false, // build-time only
      browsers: 'chrome >= 125, firefox >= 129, safari >= 17.4',
      features: {
        // Explicit opt-ins for Stage-2 features we still need:
        'custom-media-queries': true,
        'custom-selectors': true,
        // Explicit opt-out for things native at our floor:
        'oklab-function': false,
        'color-functional-notation': false,
        'cascade-layers': false,
        'nesting-rules': false,
        'has-pseudo-class': false,
      },
    }),
    require('cssnano')({ preset: 'default' }),
  ],
};
```

Why `stage: 3` instead of the default 2? Most Stage-2 features at our baseline are either native (so lowering wastes bytes) or unpolyfillable (`@scope`). Going to Stage 3 tightens the surface to only embraced features. The two Stage-2 features we genuinely want (`@custom-media`, `@custom-selectors`) are explicitly opted-in via `features`.

`minimumVendorImplementations: 2` is the npm docs' recommended stability floor — excludes single-vendor experiments.

## When preset-env beats Lightning CSS at our baseline

Three scenarios:

1. **You use `@custom-media` or `@custom-selectors`.** Lightning CSS doesn't lower these; preset-env does.
2. **You depend on the broader PostCSS plugin ecosystem.** `postcss-import`, `postcss-mixins`, third-party plugins, internal plugins. Lightning CSS doesn't have a plugin model; you'd lose those.
3. **You want stage-aware feature inclusion** (e.g., opt into a Stage-1 experimental feature for prototyping). Lightning CSS's feature set is hand-curated; you can't easily say "give me Stage 1+."

For everything else at our baseline, Lightning CSS is faster and produces equivalent output. See `../build-tools/postcss-preset-env.md` for the migration boundary.

## When NOT to use preset-env (at our baseline)

- Your CSS is already native at our floor (very common at this baseline).
- You're not using `@custom-media` or `@custom-selectors`.
- You don't depend on other PostCSS plugins.
- Build-time speed matters.

In that case: drop preset-env, use Lightning CSS, simplify the toolchain.

## Cross-references

- `../build-tools/postcss-preset-env.md` — build-tool angle; config, recipes, migration to Lightning CSS.
- `../build-tools/lightningcss-features.md` — the faster alternative.
- `./lightningcss-css-lowering.md` — sibling file on Lightning CSS lowering.
- `./at-property-fallbacks.md` — what to do when no lowering exists (e.g., `@scope`).
- `../meta/the-modern-baseline.md` — why most preset-env Stage-3/4 features are dormant at our floor.
