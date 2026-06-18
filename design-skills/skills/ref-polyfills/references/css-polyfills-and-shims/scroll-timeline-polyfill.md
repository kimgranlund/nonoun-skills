---
date: 2026-04-27
coverage: extended
peers:
  - ../meta/the-modern-baseline.md
  - ./view-transitions.md
  - ./at-property-fallbacks.md
  - ../build-tools/lightningcss-features.md
primary_sources:
  - https://github.com/flackr/scroll-timeline — repository, MIT license, by Robert Flack (Google)
  - https://www.npmjs.com/package/scroll-timeline-polyfill — npm package (community-published mirror)
  - https://flackr.github.io/scroll-timeline/ — GitHub Pages demo + canonical CDN entry
  - https://drafts.csswg.org/scroll-animations-1/ — spec
  - https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Scroll-driven_animations — MDN guide
  - https://bugzilla.mozilla.org/show_bug.cgi?id=1676780 — Firefox tracking bug for scroll-driven animations
  - https://webkit.org/blog/17333/webkit-features-in-safari-26-0/ — Safari 26.0 ships scroll-driven animations
  - https://developer.chrome.com/release-notes/115 — Chrome 115 release notes (initial ship)
  - https://caniuse.com/css-scroll-timeline — caniuse data
---

# `flackr/scroll-timeline` — the canonical scroll-driven-animations polyfill

> **Status at 2026-04-27.** Active. Maintained by **Robert Flack** (Google, Chromium animations team). License: **Apache-2.0**. Implements `ScrollTimeline`, `ViewTimeline`, the `animation-timeline` CSS property, and the `scroll()` / `view()` timeline functions. Required for Firefox 129+ at our baseline (until the flag flips to default) and for Safari 17.4–25.x.

## Native shipping status — what works without the polyfill

| Engine | Native scroll-driven animations? | Notes |
|---|---|---|
| **Chrome / Edge** | **Yes**, since Chrome 115 (June 27, 2023) | Full surface — `ScrollTimeline`, `ViewTimeline`, `animation-timeline`, `scroll()`, `view()`. |
| **Safari** | **Yes**, since **Safari 26.0** (Sept 15, 2025). On Safari 17.4–25.x, the feature is behind a developer feature flag ("Scroll-driven Animations" in WebKit Feature Flags) and not exposed to production users. | See [Safari 26.0 features](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/). |
| **Firefox** | **Behind a flag** — `layout.css.scroll-driven-animations.enabled`. Not enabled by default in any stable Firefox release as of April 2026. | Tracking bug [Bugzilla 1676780](https://bugzilla.mozilla.org/show_bug.cgi?id=1676780). Part of [Interop 2026](https://webkit.org/blog/17818/announcing-interop-2026/) priorities — flag flip expected during the year, but not committed at this date. |

## The polyfill window at our baseline

Our skill's floor is Chromium 125+ / Safari 17.4+ / Firefox 129+. Where does the polyfill earn its keep?

| Engine segment | Native? | Polyfill needed? |
|---|---|---|
| Chrome / Edge 125+ | Yes | No |
| Safari 17.4 – 25.x | No | **Yes** (the 18-month window from March 2024 to Sept 2025) |
| Safari 26.0+ | Yes | No |
| **Firefox 129 – present (April 2026)** | **No** (still flagged) | **Yes — every Firefox version at our floor** |

This is the unusual case where the polyfill window remains open for one engine indefinitely until the flag flips. As long as Firefox keeps `layout.css.scroll-driven-animations.enabled` off-by-default on Release, the polyfill is the only cross-browser answer for Firefox audiences.

If your audience is Chromium-heavy and you don't care about Firefox, the polyfill is dead weight. If you do care about Firefox, the polyfill is currently mandatory.

## Package metadata

| Field | Value |
|---|---|
| Repository | https://github.com/flackr/scroll-timeline |
| Maintainer | Robert Flack (Google, Chromium animations team) |
| License | Apache-2.0 |
| Primary distribution | GitHub Pages: `https://flackr.github.io/scroll-timeline/dist/scroll-timeline.js` |
| npm mirror | `scroll-timeline-polyfill` (community-published) — see [npm](https://www.npmjs.com/package/scroll-timeline-polyfill) |
| Spec tracker | https://drafts.csswg.org/scroll-animations-1/ |

The official distribution is the GitHub Pages bundle. There is a community-published `scroll-timeline-polyfill` package on npm that mirrors the source. For self-hosting (recommended), download the bundle from the GitHub Pages URL or build from the source repo.

## Installation patterns

### Pattern 1 — script tag (simplest, no bundler)

```html
<script src="/vendor/scroll-timeline.js"></script>
```

Self-hosted from your origin. The polyfill auto-detects native support and no-ops when the browser already implements scroll-driven animations.

For prototyping (NOT production), the GitHub Pages CDN works directly:

```html
<script src="https://flackr.github.io/scroll-timeline/dist/scroll-timeline.js"></script>
```

For production traffic, **always self-host**. Don't depend on `flackr.github.io` for production CDN service. See `../anti-patterns/polyfill-io-after-attack.md` for the supply-chain reasoning.

### Pattern 2 — module import + feature detect

```js
if (!('ScrollTimeline' in window) || !('ViewTimeline' in window)) {
  await import('/vendor/scroll-timeline.js');
}
```

Modern browsers (Chrome 115+, Safari 26+, Firefox with flag) have `window.ScrollTimeline` and `window.ViewTimeline` natively; the import is skipped. Code-split friendly.

### Pattern 3 — npm + bundler

```bash
npm install scroll-timeline-polyfill
```

```js
import 'scroll-timeline-polyfill';
```

Note: the npm package is a community mirror, not the official distribution. Verify the version against the source repository before adopting in production.

## What the polyfill provides

- `ScrollTimeline` constructor on `window` — `new ScrollTimeline({ source, axis })`.
- `ViewTimeline` constructor on `window` — `new ViewTimeline({ subject, axis, inset })`.
- `Element.prototype.animate()` accepts a `timeline:` option for scroll-driven animation.
- The `animation-timeline` CSS property (lowered by parsing stylesheets at runtime).
- The `scroll()` and `view()` functions inside `animation-timeline`.
- `animation-range`, `animation-range-start`, `animation-range-end`.

It does NOT polyfill:
- `timeline-scope` — newer surface, partial support.
- Custom `@scroll-timeline` rules (deprecated; old WAAPI shape).

## Code examples

### CSS + animation-timeline (native syntax, polyfill-compatible)

```css
@keyframes slide-in {
  from { transform: translateX(-100%); }
  to   { transform: translateX(0); }
}

.parallax-image {
  animation: slide-in linear both;
  animation-timeline: scroll(block root); /* root vertical scroll */
  animation-range: 0px 200px;
}
```

The polyfill parses `animation-timeline: scroll(...)` and `view(...)` from your stylesheets and rewrites it to `Element.animate()` calls under the hood. Author the modern syntax; the polyfill handles lowering for unsupported engines.

### JavaScript API

```js
import 'https://flackr.github.io/scroll-timeline/dist/scroll-timeline.js'; // or self-hosted

document.getElementById('parallax').animate(
  { transform: ['translateY(0)', 'translateY(100px)'] },
  {
    fill: 'both',
    timeline: new ScrollTimeline({ source: document.documentElement }),
    rangeStart: new CSSUnitValue(0, 'px'),
    rangeEnd: new CSSUnitValue(200, 'px'),
  }
);
```

`CSSUnitValue` is a CSS Typed OM type; available natively in modern browsers, polyfilled by the scroll-timeline polyfill internally.

## Performance notes

The polyfill drives animations from JS in response to `scroll` events. Compared to native (which runs on the compositor thread):

- **Polyfilled animations are not compositor-driven** — they re-layout on scroll. Expect some jank on slow scroll devices.
- **`will-change: transform`** on the animated element helps performance even under the polyfill.
- **Limit the number of polyfilled scroll-driven animations on a page**. Native handles dozens; the polyfill prefers a handful.
- **Consider `prefers-reduced-motion`** — both native and polyfilled scroll-driven animations should respect the user setting. Wrap with `@media (prefers-reduced-motion: no-preference)` in CSS.

For a hero parallax + a few scroll-bound progress indicators, the polyfill is fine. For a page with 50+ scroll-tied elements, profile carefully.

## Detecting "is the polyfill active vs. native"

The polyfill assigns its own `ScrollTimeline` class, which in many cases will be the only `ScrollTimeline` available. To distinguish:

```js
const isPolyfilled = window.ScrollTimeline?.toString().includes('flackr');
```

Fragile but useful for debugging. In Safari with the developer feature flag enabled, the polyfill detects native support and no-ops; user-side feature flags don't reach production users, so you don't normally need to worry about this distinction.

## Bundle size

The bundle is ~30–40 KB minified+gzipped depending on version. Larger than the popover or anchor-positioning polyfills because the surface area is larger (scroll observation, animation timing, multiple constructors). Acceptable for audiences who need it; route via dynamic import to avoid the cost on Chromium / Safari 26+ users.

## When to use this polyfill

- You want scroll-driven animations and ship to Firefox.
- Your Safari floor is below Safari 26.0 (i.e., iOS 17 / iOS 18 audience).
- You're using progressive enhancement and the polyfill is a clean fit.

## When NOT to use this polyfill

- You're Chromium-only (extension, kiosk, Electron app, internal tool with enforced browser).
- The animation is decorative and reduced-motion-okay; ship the keyframes without scroll-tied timing and accept native-only scroll-driven enhancement.
- The polyfill's perf cost on your animation count is unacceptable.
- Your animation can be expressed with `IntersectionObserver` + Web Animations API directly (often simpler and smaller than the full polyfill).

## Cross-references

- `./view-transitions.md` — sibling "modern animation API" decision; same baseline-gating logic applies.
- `./at-property-fallbacks.md` — feature-query pattern when no polyfill exists; useful when the polyfill is too heavy.
- `../meta/the-modern-baseline.md` — why the polyfill window matters at our floor.
- `../build-tools/lightningcss-features.md` — Lightning CSS does NOT lower `animation-timeline`; the polyfill is the only path.
