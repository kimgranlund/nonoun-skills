---
date: 2026-04-27
coverage: canonical
peers:
  - ../anchor-positioning-quirks/firefox-147-anchor-shipped.md
  - ../anchor-positioning-quirks/safari-26-anchor-shipped.md
  - ../anchor-positioning-quirks/inset-area-rename.md
  - ../anchor-positioning-quirks/popover-margins-interaction.md
  - ../anchor-positioning-quirks/default-anchor-resolution.md
  - ./popover-polyfill.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://github.com/oddbird/css-anchor-positioning — repository, issue tracker, BSD-3-Clause license
  - https://www.npmjs.com/package/@oddbird/css-anchor-positioning — npm package, latest 0.9.0 (April 2026)
  - https://anchor-positioning.oddbird.net/ — demo, status, browser-support detection page
  - https://www.oddbird.net/2025/05/06/polyfill-updates/ — OddBird May 2025 polyfill update post; v0.7 same-shadow-root support
  - https://www.oddbird.net/2025/10/13/anchor-position-area-update/ — OddBird Fall 2025 roundup (anchor positioning landscape)
  - https://www.oddbird.net/polyfill/ — OddBird HTML & CSS polyfills overview
  - https://github.com/oddbird/css-anchor-positioning/blob/main/README.md — install, usage, known limitations
  - https://github.com/oddbird/css-anchor-positioning/releases — release notes
---

# `@oddbird/css-anchor-positioning` — the canonical anchor-positioning polyfill

> **Status at 2026-04-27.** Active. Latest npm: **0.9.0** (April 2026). Maintained by OddBird (Miriam Suzanne, Jonny Gerig Meyer, James Stuckey Weber, plus contributors). License: **BSD-3-Clause**. The polyfill targets the post-rename canonical surface (`position-area`, `position-anchor`, `anchor()`, `anchor-size()`, `@position-try`, `position-try-fallbacks`).

## Why this polyfill exists

CSS Anchor Positioning is a Baseline-Newly-Available feature as of January 13, 2026, when Firefox 147 flipped the preference. At our skill's baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+), there is a meaningful polyfill window:

- **Firefox 129–146**: 18 versions, ~17 months. Native arrives in Firefox 147 (Jan 13, 2026). See `../anchor-positioning-quirks/firefox-147-anchor-shipped.md`.
- **Safari 17.4–25.x**: 15 months. Native arrives in Safari 26.0 (Sept 15, 2025). See `../anchor-positioning-quirks/safari-26-anchor-shipped.md`.
- **Chrome 125+**: native at our floor — no polyfill needed.

For audiences with significant pre-Safari-26 iOS share or pre-Firefox-147 Firefox share (especially Firefox ESR 140), the OddBird polyfill is the only viable cross-engine answer. There is no second, comparable maintained anchor-positioning polyfill at this date.

## Package metadata

| Field | Value |
|---|---|
| npm | https://www.npmjs.com/package/@oddbird/css-anchor-positioning |
| Repository | https://github.com/oddbird/css-anchor-positioning |
| Latest version | 0.9.0 (April 2026) |
| License | BSD-3-Clause |
| Maintainer | OddBird (https://www.oddbird.net/) |
| Demo / status page | https://anchor-positioning.oddbird.net/ |

The package is OddBird-funded engineering work, not a single-maintainer side project. Not a supply-chain red flag.

## Installation and minimal wiring

The recommended pattern is feature-detect + dynamic import. The polyfill ships with no payload to browsers that already have native anchor positioning.

### Pattern 1 — script tag, CDN-detected (simplest)

```html
<script type="module">
  if (!('anchorName' in document.documentElement.style)) {
    import('https://unpkg.com/@oddbird/css-anchor-positioning');
  }
</script>
```

`'anchorName' in document.documentElement.style` is the canonical detection surface — equivalent to `CSS.supports('anchor-name', '--x')` but without parsing the value. Modern Chromium / Firefox 147+ / Safari 26+ resolve the check in microseconds and skip the import.

For production, **self-host** the polyfill bundle. Don't load from `unpkg.com` in production traffic. See `../anti-patterns/polyfill-io-after-attack.md` for the supply-chain reasoning that applies to any 3rd-party JS CDN.

### Pattern 2 — bundler import (Vite / Webpack / esbuild)

The package exposes a `/fn` entry that exports a `polyfill` function returning a promise:

```js
import polyfill from '@oddbird/css-anchor-positioning/fn';

if (!('anchorName' in document.documentElement.style)) {
  await polyfill();
}
```

Code-split this branch so the polyfill chunk is only fetched when needed:

```js
if (!('anchorName' in document.documentElement.style)) {
  const { default: polyfill } = await import(
    '@oddbird/css-anchor-positioning/fn'
  );
  await polyfill();
}
```

Bundlers will produce a separate chunk for the dynamic-import target. Modern browsers never request it.

### Pattern 3 — bare side-effect import (heavyweight)

```js
import '@oddbird/css-anchor-positioning';
```

This auto-runs the polyfill when imported. It bypasses the feature-detect, so every visitor downloads the polyfill bundle even if their browser supports anchor positioning natively. Avoid in production unless you have a specific reason; the dynamic-import pattern wins on bundle delivery.

## How the polyfill works

From OddBird's README and the [v0.7 release post](https://www.oddbird.net/2025/05/06/polyfill-updates/):

1. **Scan stylesheets** for anchor-positioning declarations (`anchor-name`, `position-anchor`, `position-area`, `anchor()` / `anchor-size()` calls, `@position-try` blocks).
2. **Compute layout positions in JS** at first run. The polyfill reads element rects, applies positioning logic, and writes inline styles to the targets.
3. **Update on scroll, resize, and DOM mutation.** Listens via `IntersectionObserver`, `ResizeObserver`, and `MutationObserver`.
4. **Position-area lowering**: wraps each target in a positioning container element to simulate the layout effect.

Because the polyfill works by writing inline styles, runtime cost scales with the number of anchored elements and the frequency of layout changes. For a tooltip-heavy or popover-heavy app, this is fine; for a virtualized data grid with hundreds of simultaneous anchored elements, profile before shipping.

## Known limitations

These limitations are documented in OddBird's README and are stable enough to plan around. They are not bugs; they are deliberate trade-offs against the polyfill's scope.

| Area | Limitation | Workaround |
|---|---|---|
| `@position-try` | `position-try-order` parsed but ignored; use `position-try-fallbacks` shorthand for full coverage | Author the fallback list explicitly; don't rely on `try-order` |
| `@position-try` | `flip-start` tactic — partial support (property names + anchor sides only) | Test under polyfill before shipping `flip-start` chains |
| `@position-try` | `position-area` as a fallback tactic — unsupported | Use explicit positioning fallbacks instead |
| `position-area` | Implemented by wrapping the target in a positioning element; **breaks selectors that depend on direct parent/child relationships** | Audit `> ` selectors targeting anchored elements; use `:has()` or descendant selectors |
| `position-area` | Overflow-alignment cases not applied identically to native | Visual diff against Chrome native before shipping |
| Shadow DOM | Same-shadow-root support added in **v0.7.0** (May 2025); cross-shadow-root anchoring still NOT supported (issue #191) | Keep anchor + target in the same shadow root |
| Stylesheets | Constructed stylesheets (`new CSSStyleSheet()`) **NOT supported** (issue #228) | Use `<style>` elements or external CSS for anchor declarations |
| Writing modes | Vertical / RTL writing modes — partial `anchor()` support | Test in your specific writing mode before shipping |
| `position-visibility` | Not implemented | Use feature-query `@supports` to skip in pre-native browsers |

If your design requires any of the unsupported surface, the answer is feature-query gating + a flat CSS fallback rather than the polyfill. See `at-property-fallbacks.md` for the gating pattern.

## v0.7+ — same-shadow-root support

v0.7.0 (May 2025) was a significant release: it added support for elements inside the same shadow DOM, enabling the polyfill to run inside web-component-based UIs without requiring authors to flatten DOM. From the [OddBird update post](https://www.oddbird.net/2025/05/06/polyfill-updates/): *"v0.7.0 of the CSS Anchor Positioning Polyfill adds the ability to polyfill elements inside of the same shadow DOM."*

The constraint that remains: **elements anchored across different shadow roots are still not supported**. If your tooltip is in light DOM and the trigger is inside a shadow root (or vice versa), the polyfill cannot resolve the relationship. Track [issue #191](https://github.com/oddbird/css-anchor-positioning/issues/191).

For ui-build-components skill consumers: most well-designed components keep anchor + target in the same shadow root anyway, so this is rarely a blocker in practice.

## Bundle size and runtime cost

OddBird halved the bundle size in 2025 by curating runtime dependencies. The 0.9.0 minified+gzipped payload is in the **15–25 KB** range — the team's blog notes the polyfill could shrink by ~85% if browsers shipped CSS Parser Extensions (which would let the polyfill skip its own CSS parser). Since CSS Parser Extensions don't exist yet, the parser cost is fundamental.

For comparison: Tailwind v4's runtime is also ~25 KB. The OddBird polyfill is in the same bundle-cost ballpark as a CSS framework. For audiences that need it (Safari 17.4–25.x, Firefox 129–146), this is acceptable; for audiences that don't need it, feature-detect + dynamic-import keeps the bytes off the wire.

## When to use this polyfill

- Your audience has measurable Safari 17.4–25.x share (iOS 17 / iOS 18 long tail).
- Your audience has measurable Firefox 129–146 share (especially Firefox ESR 140-bound enterprise installs).
- You're building a tooltip / popover / dropdown system that depends on anchor positioning specifically (rather than a JS positioning library like Floating UI).

## When NOT to use this polyfill

- Your audience is overwhelmingly Chrome and recent Safari/Firefox — native shipping covers your floor; polyfill is dead weight.
- You're already using Floating UI / Popper.js for positioning and have invested in that API. Migrating from Floating UI to anchor positioning + polyfill is rarely worth it; native anchor positioning is the right migration target, and Floating UI ports cleanly.
- Your design uses cross-shadow-root anchoring or constructed stylesheets — the polyfill won't help; redesign or accept degraded experience.
- You can't accept the bundle cost on the affected segment of users.

## Cross-references

- `../anchor-positioning-quirks/firefox-147-anchor-shipped.md` — when Firefox got native (the polyfill window's upper bound on Firefox).
- `../anchor-positioning-quirks/safari-26-anchor-shipped.md` — when Safari got native (the upper bound on iOS/macOS).
- `../anchor-positioning-quirks/inset-area-rename.md` — the `inset-area` → `position-area` rename. The polyfill targets the post-rename name.
- `../anchor-positioning-quirks/popover-margins-interaction.md` — UA-style margin interference; polyfill does not paper over.
- `./popover-polyfill.md` — sibling polyfill from same maintainer; often used together for popover + anchor combinations.
- `../meta/the-modern-baseline.md` — why the polyfill window matters at our floor.
