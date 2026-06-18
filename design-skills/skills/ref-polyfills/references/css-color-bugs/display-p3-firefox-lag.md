---
date: 2026-04-27
coverage: esoteric
peers:
  - ./wide-gamut-fallbacks.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://bugzilla.mozilla.org/show_bug.cgi?id=1626624 — Mozilla bug: Support Wide Gamut Color in CSS with Display-P3 (still open)
  - https://github.com/mdn/browser-compat-data/issues/21422 — BCD issue: color-gamut media feature is not supported by Firefox
  - https://webkit.org/blog/10042/wide-gamut-color-in-css-with-display-p3/ — WebKit blog: Wide Gamut Color in CSS with Display-P3
  - https://developer.mozilla.org/en-US/docs/Web/CSS/@media/color-gamut — MDN: color-gamut media feature
  - https://web.dev/articles/color-spaces-and-css — web.dev: Color spaces and CSS
  - https://www.the-ninth.com/blog/firefox-and-its-color-management-quirks — Firefox color-management overview
  - https://zidhuss.tech/posts/p3-firefox-mac/ — workaround config for Firefox-on-Mac users
---

# Firefox renders `color(display-p3 ...)` mapped to sRGB

## TL;DR

Firefox **does not render P3 colors at wide gamut** on most platforms — even on hardware that supports it. The CSS parses fine; the color values resolve fine; but at the rendering layer, Firefox gamut-maps everything to sRGB before painting. A vivid red defined as `color(display-p3 1 0 0)` looks identical to plain `#ff0000` in Firefox, while looking distinctly more saturated in Safari and Chrome on the same P3 display. Additionally, **`@media (color-gamut: p3)` always evaluates to false in Firefox**, breaking the standard progressive-enhancement gate.

Tracking bug: [Mozilla Bugzilla 1626624](https://bugzilla.mozilla.org/show_bug.cgi?id=1626624) — "Support Wide Gamut Color in CSS with Display-P3" — open since 2020. WebRender/Cairo backend rewrite is the blocker. ETA per Mozilla's Firefox roadmap (per H1 2026 messaging) is unconfirmed at this writing.

## What's broken, precisely

### 1. CSS parses, computes, and looks correct — except where it matters

```css
.vivid-red {
  background: color(display-p3 1 0 0);
}
```

In Firefox 129+ on a P3-capable Mac display:

- `getComputedStyle(...).background` returns `color(display-p3 1 0 0)` correctly.
- The Inspector pane shows the swatch.
- DevTools color picker can edit it.
- The actual painted pixels on screen: same RGB triple as `#ff0000`. The display's wide-gamut headroom is unused.

The conversion happens at the rendering backend (WebRender on Mac, Cairo on Linux/Windows). Both backends as of April 2026 only natively understand sRGB. P3 colors are gamut-mapped to sRGB at the point of rasterization and lose their wide-gamut character.

WebKit and Blink, by contrast, hand the P3 color through to a P3-aware compositor on macOS / iOS / iPadOS, and on Windows when an HDR display is configured.

### 2. `@media (color-gamut: p3)` is permanently false

This is the second half of the bug. Per [BCD issue 21422](https://github.com/mdn/browser-compat-data/issues/21422):

```js
window.matchMedia('(color-gamut: p3)').matches
// Chrome on P3 display: true
// Safari on P3 display: true
// Firefox on P3 display: false
```

Even on a calibrated Display P3 monitor with Firefox running natively. The query reports `srgb` (the lowest tier) and never advances. This means the standard progressive-enhancement pattern…

```css
@media (color-gamut: p3) {
  .accent { background: color(display-p3 1 0.2 0.4); }
}
```

…**never fires in Firefox**, even on users with capable hardware. Firefox falls through to whatever your sRGB fallback is.

This is filed against MDN's compat data because MDN historically claimed Firefox supports `color-gamut`. Implementation is technically present (the query is parsed, returns a value), but the value is incorrect on every platform. The discrepancy is being tracked rather than the property re-listed as unsupported.

## The user-visible effect

For most websites: **negligible**. sRGB is enough for almost all content; users on Firefox + P3 displays have been seeing slightly less-saturated brand colors for years and almost no one notices.

For visual-design-load-bearing surfaces: **noticeable**. Photo galleries, color-grading apps, brand pages with vivid magenta/orange/teal accents, dashboard charts where hue distinguishes series — these look meaningfully duller in Firefox compared to Chrome/Safari on the same hardware.

For perceptual-color systems built on OKLCH: **moderate**. OKLCH lets you specify colors that are *outside* sRGB but *inside* P3. Examples like `oklch(0.7 0.25 30)` (a saturated orange) sit outside sRGB; in Firefox, this gets clipped/mapped back into sRGB and you see a duller orange. In Chrome/Safari on a P3 display, you see the actual saturated value.

## Reproduction

Save as `p3-test.html`, open in Firefox 129+ vs Safari 17.4+ vs Chrome 125+ on a P3-capable display:

```html
<!DOCTYPE html>
<style>
  .row { display: flex; gap: 4px; margin: 8px 0; }
  .swatch { width: 100px; height: 80px; }
  .a { background: #ff0000; }
  .b { background: color(display-p3 1 0 0); }
  .c { background: oklch(0.65 0.3 30); }    /* saturated orange, outside sRGB */
  .gamut-info {
    padding: 12px; font: 14px monospace;
    background: light-dark(#f0f0f0, #222);
  }
</style>
<div class="row">
  <div class="swatch a"></div>           <!-- sRGB red -->
  <div class="swatch b"></div>           <!-- P3 red -->
  <div class="swatch c"></div>           <!-- OKLCH wide-gamut orange -->
</div>
<div class="gamut-info" id="info"></div>
<script>
  const info = document.getElementById("info");
  const queries = ["srgb", "p3", "rec2020"];
  info.textContent = queries.map(q =>
    `(color-gamut: ${q}) → ${matchMedia('(color-gamut: ' + q + ')').matches}`
  ).join("\n");
</script>
```

Expected results on a Display P3 macOS monitor:

- Safari/Chrome: `.a` and `.b` are visibly different. `.b` is more saturated. `(color-gamut: p3)` is `true`.
- Firefox: `.a` and `.b` look identical. `.c` is a duller orange than the same swatch in Chrome/Safari. `(color-gamut: p3)` is `false`.

## Workarounds

### Don't gate progressive enhancement on `@media (color-gamut: p3)` for Firefox

Use feature queries, not media queries:

```css
.button {
  background: #1a73e8;                                  /* sRGB fallback */
}
@supports (color: color(display-p3 0 0 0)) {
  .button {
    background: color(display-p3 0.1 0.45 0.91);        /* P3 enhanced */
  }
}
```

`@supports (color: color(display-p3 ...))` returns `true` in Firefox — the parser accepts the syntax, even though the renderer flattens it. The result: Firefox users still see the P3 declaration *value*, but it gets gamut-mapped to sRGB at render time. **This is fine.** Firefox users get sRGB output regardless; what matters is that Chrome/Safari users on capable hardware get the wide-gamut version.

The principle: **enhance via `@supports` when the cost of the fallback equals the cost of the enhancement on the affected engine** (which is the case here — the value resolves regardless, only the painting differs).

### Always provide an sRGB-equivalent fallback

For wide-gamut design choices that matter, hand-pick the sRGB fallback that *most closely* approximates the P3 target. Don't rely on the browser's gamut-mapping algorithm — it is cross-engine inconsistent (Firefox uses its own, WebKit uses CSS Color 4's algorithm, Chrome currently uses neither in some pipelines). The author-controlled fallback always wins for predictability.

```css
:root {
  --brand: #ff7e3e;                                  /* sRGB approximation */
}
@supports (color: color(display-p3 0 0 0)) {
  :root {
    --brand: color(display-p3 1 0.5 0.25);           /* Authored P3 target */
  }
}
```

### When you need to know the user is *actually* on a P3 display

If you have a use case that genuinely needs P3 capability detection (e.g., serving different image sources), use feature detection at the JS level with a documented Firefox carve-out:

```js
function userIsOnP3Display() {
  // Reliable on Chrome and Safari.
  // Firefox: always returns false even on P3 hardware (Bug 1626624).
  // We accept this as a "Firefox shows sRGB version" tradeoff.
  return matchMedia('(color-gamut: p3)').matches;
}
```

There is no reliable browser-side workaround for the Firefox media-query bug. Some apps inspect the `screen.colorGamut` property — that doesn't exist (it was a proposal that didn't ship). Others use canvas-based detection — that also fails because Firefox's canvas backend is sRGB-only too.

If your use case absolutely demands knowing the display capabilities (color-grading professional tools), serve your app's "wide gamut" mode opt-in via a settings toggle and document the Firefox limitation.

### Power users on Mac can flip a config flag

Some Firefox-on-Mac users get partial wide-gamut behavior by setting `gfx.color_management.native_srgb = true` and configuring a Display P3 ICC profile in `about:config`. **This is not a developer workaround** — it's a per-user fix that you can mention in your help docs but cannot rely on for production rendering.

## At our baseline

Our floor is Firefox **129+** (August 2024). Bug 1626624 has been open since 2020 and remains open as of April 2026. The HDR rendering work that would fix this is targeted for H1 2026 in Mozilla's roadmap messaging, but no shipping commitment has appeared in the bug or in release notes through Firefox 145.

**Posture at this baseline:**

- Use `@supports`, not `@media (color-gamut: p3)`, for P3 progressive enhancement.
- Always author an explicit sRGB fallback for any P3-load-bearing color.
- Accept that Firefox users will see the sRGB version. Don't try to detect "is this a P3 display" reliably from script — Firefox cannot tell you.
- Watch [Bugzilla 1626624](https://bugzilla.mozilla.org/show_bug.cgi?id=1626624) for status changes.

## Cross-references

- The progressive-enhancement pattern in detail: [`wide-gamut-fallbacks.md`](./wide-gamut-fallbacks.md)
- Baseline color-feature support: [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)
