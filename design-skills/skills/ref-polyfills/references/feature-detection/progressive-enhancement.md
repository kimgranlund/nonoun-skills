---
date: 2026-04-27
coverage: extended
peers:
  - ../feature-detection/at-supports-recipes.md
  - ../feature-detection/js-feature-detection.md
  - ../feature-detection/ponyfill-pattern.md
  - ../meta/decision-tree.md
  - ../meta/glossary.md
  - ../css-polyfills-and-shims/anchor-positioning-polyfill.md
  - ../css-polyfills-and-shims/view-transitions.md
  - ../anti-patterns/defensive-overpolyfilling.md
primary_sources:
  - https://developer.mozilla.org/en-US/docs/Glossary/Progressive_Enhancement — MDN definition
  - https://web.dev/articles/progressively-enhance-your-pwa — web.dev guidance
  - https://web.dev/articles/baseline-and-polyfills — Baseline + polyfilling stance
  - https://github.com/voorhoede/progressive-enhancement-resources — survey of techniques
  - https://github.com/springernature/frontend-playbook/blob/main/practices/progressive-enhancement.md — Springer Nature playbook
---

# Progressive enhancement

The design pattern that makes most polyfills unnecessary at our baseline. Ship a working baseline; layer enhancements behind feature queries. The unsupported branch isn't broken — it's just plainer.

## Definition

**Progressive enhancement (PE)**: ship a working baseline that runs everywhere, then layer enhancements that activate only where the platform supports them. The fallback isn't an afterthought — it's the *floor*. Enhancement is opt-in via feature query.

**Graceful degradation (GD)** is the inverse: build the full-featured version first, then add fallbacks for missing capabilities. Identical end-state UX in some cases, but different design posture — GD treats the floor as a degraded form of the ceiling, while PE treats the ceiling as an upgrade over the floor.

The Springer Nature engineering playbook captures it well: "Build for the lowest-common-denominator version of the platform, then enhance." (https://github.com/springernature/frontend-playbook/blob/main/practices/progressive-enhancement.md)

## Why PE is the modern-first default

At our baseline (Chromium 125 / Safari 17.4 / Firefox 129), polyfilling has measurable costs that PE avoids:

| Cost | Polyfill | PE |
|---|---|---|
| Bundle size | 30–60 KB for `core-js`, 60 KB for `Temporal`, 8 KB for `urlpattern-polyfill` | Zero |
| Runtime detection | Sometimes (conditional polyfills) | Native (`@supports` is parser-time, JS detection is one branch) |
| Maintenance | Track polyfill releases, security patches, spec drift | None — the platform owns the contract |
| Tree-shaking | Side-effect imports defeat dead-code elimination | Pure CSS / pure if-branches tree-shake naturally |
| Future-readiness | Polyfill must be removed when floor moves up | Branch becomes the only branch when floor moves up |

The default question shouldn't be "is there a polyfill for X?" but "can users without X still get a working experience, and can I layer X on top?"

## Concrete patterns

### Anchor positioning

Anchor positioning is shipped in Chrome 125+ and Safari 26+ (post-baseline), but Firefox 147 (Jan 2026) is post-baseline by 18 versions. PE works cleanly:

```css
/* Floor: floating-ui-style JS positioning, or static placement */
.tooltip {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
}

/* Enhancement: anchor positioning if available */
@supports (anchor-name: --foo) {
  .anchor { anchor-name: --tooltip-anchor; }
  .tooltip {
    position-anchor: --tooltip-anchor;
    top: anchor(bottom);
    position-area: bottom span-x;
    transform: none;
  }
}
```

Compare to `../css-polyfills-and-shims/anchor-positioning-polyfill.md` (OddBird's polyfill, ~30 KB). PE-only delivery means Firefox users see a static-positioned tooltip; that's not broken, just plainer.

### View Transitions

Same-doc View Transitions are Baseline (Oct 2025) but cross-doc is Chromium-only at our baseline. PE means: skip the animation in unsupported engines, run it in supported ones.

```js
function navigate(url) {
  if (!document.startViewTransition) {
    // No animation — just update the DOM
    updateContent(url);
    return;
  }
  document.startViewTransition(() => updateContent(url));
}
```

Firefox users get an instant DOM update. Chrome / Safari users get the transition. Neither user sees a broken page.

### `@scope`

`@scope` is in Chrome 118+, Safari 17.4+, but Firefox 146+ — leaving Firefox 129–145 in the gap at baseline. PE means: write flat-cascade CSS that works everywhere, layer scoped CSS where supported.

```css
/* Flat fallback — relies on classnames or specificity */
.card-title { font-weight: 600; }
.card-content .card-title { /* won't accidentally match nested cards */
  font-weight: 600;
  font-size: 1rem;
}

/* @scope scopes the cascade naturally where supported */
@scope (.card) {
  .title { font-weight: 600; }
  .content .title { font-size: 1rem; }
}
```

The flat version still works in `@scope`-supporting browsers; the scoped version is an upgrade. No detection needed if both are written defensively — the cascade picks the most specific match.

### Modern color functions

OKLCH, OKLab, and `color-mix` are universal at baseline. But P3 / Rec2020 wide-gamut colors and `contrast-color()` aren't. PE pattern:

```css
.surface {
  /* Floor: sRGB color works everywhere */
  background: #2563eb;
}

@supports (color: color(display-p3 0.15 0.39 0.92)) {
  .surface {
    /* Enhancement: P3 for wide-gamut displays */
    background: color(display-p3 0.15 0.39 0.92);
  }
}
```

For Firefox's lag in actually rendering P3 distinct from sRGB, see `../css-color-bugs/display-p3-firefox-lag.md` — PE doesn't help with engine bugs, only with absence-of-feature.

### Form `:user-valid` / `:user-invalid`

Universal at baseline. But for older floors:

```css
/* Floor: standard :valid / :invalid (tracks pristine state) */
input:invalid { border-color: red; }

/* Enhancement: :user-invalid only fires after user interaction */
@supports selector(:user-invalid) {
  input:invalid { border-color: initial; } /* reset */
  input:user-invalid { border-color: red; }
}
```

## When PE works, when polyfill is right

PE is the right tool when:

- **The fallback is reasonable.** A static tooltip is fine; a "nothing happens when you scroll" tooltip is not.
- **The feature is presentational.** Layout, color, animation, motion can be skipped without breaking core flows.
- **The cost of skipping the feature is acceptable.** A simpler look on Firefox ≠ broken.
- **No 3rd-party code references the missing API.** PE breaks down if your dependencies expect `globalThis.fetch` and you're below its support floor.

Polyfill is the right tool when:

- **The feature is structurally load-bearing.** `Temporal.ZonedDateTime` parsing in business logic that affects every user — no graceful fallback. (See `../runtime-polyfills/temporal-api.md`.)
- **3rd-party libraries assume the API exists.** Shimming a global so that imported code keeps working.
- **The "skip it" branch is materially worse for the user.** Charts that won't render, forms that won't validate, payments that won't process.

The decision tree (`../meta/decision-tree.md`) walks through this systematically. Most CSS questions land on PE; most JS questions either land on "ship native" (the feature is universal at baseline) or on a small targeted polyfill / ponyfill.

## Design for the floor

The mindset shift: **the platform's minimum capability is the canvas.** Everything you draw must work within it. Enhancements are oil paint on top — they make the painting richer, but the underlying drawing is still recognizable when stripped away.

Contrast with **design for the ceiling**, where you start with the most capable browser, build everything against it, and then *retroactively* think about fallbacks. This produces:

- Codebases where removing the polyfill breaks the app, even on browsers that don't need it.
- Polyfills that get shipped to 95% of users who don't need them, because removing them is too risky.
- Feature gating that's coupled to "is the polyfill installed?" rather than "is the feature present?"

The Floor-First approach inverts this. Every CSS file starts with the safe-everywhere version. Every JS module starts with the universal-at-baseline path. Enhancements are explicit, conditional, and removable.

## The PE / polyfill decision

```
Question: I want to use feature X, which isn't universal at my baseline.

├── Can I write a fallback that works for users without X?
│   ├── Yes → PE. Ship the fallback as the default; gate X behind @supports / `'X' in obj`.
│   └── No  → continue
│
├── Is the feature load-bearing for the experience?
│   ├── Yes → polyfill. Self-host. Single-feature. (See ../meta/decision-tree.md step 7.)
│   └── No  → consider skipping the feature entirely. Adding a polyfill is a commitment.
```

## Anti-patterns

### "Polyfill defensively, just in case"

The 2017-era reflex: ship `core-js` to every user, on every browser, because "you never know who has what." At baseline, this is bundle bloat — ~30–60 KB shipped to a 100% modern audience that needed nothing. See `../anti-patterns/defensive-overpolyfilling.md`.

### "If we can't polyfill it, we can't ship the feature"

False. `@scope` has no real polyfill, and `@scope` is shippable today via PE — flat-cascade fallback for Firefox 129–145, scoped CSS where supported. The presence of a polyfill should not be a prerequisite for using a modern feature.

### "PE is for content sites; apps need polyfills"

Also false. App frontends — dashboards, editors, design tools — benefit from PE more than content sites do, because their feature surface is richer and more polyfill-resistant. Linear, Figma, Stripe Dashboard, and Vercel Dashboard all ship modern CSS / JS without `core-js`-style polyfill bundles.

## When PE is wrong

PE has real limits:

- **Behavior, not appearance.** PE excels at "this looks plainer on Firefox" but is harder when the feature changes *behavior* (e.g. `URLPattern`-based routing). Polyfill is often right for behavioral features.
- **Below-baseline support floors.** If your support matrix includes IE11 or Safari 12, you're outside the modern baseline; PE plus polyfill is more typical there.
- **3rd-party-coupled APIs.** If a library imports `globalThis.fetch` directly, you can't PE it — the import resolves at module-load, not at usage. Polyfill (or a ponyfill the library accepts via injection) is needed.

## Cross-references

- `at-supports-recipes.md` — the CSS feature-query patterns PE depends on.
- `js-feature-detection.md` — the JS patterns for runtime PE.
- `ponyfill-pattern.md` — for cases where PE shells out to a pure-function helper.
- `../meta/decision-tree.md` — Step 4 of the do-I-need-a-polyfill flow.
- `../meta/glossary.md` — definitions of polyfill / ponyfill / shim / PE.
- `../anti-patterns/defensive-overpolyfilling.md` — the failure mode PE replaces.
