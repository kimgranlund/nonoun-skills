---
date: 2026-04-27
coverage: esoteric
peers:
  - ../popover-quirks/safari-focus-inputs.md
  - ../popover-quirks/safari-184-tab-hang.md
  - ../popover-quirks/popover-vs-dialog-toplayer.md
  - ../css-polyfills-and-shims/popover-polyfill.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://bugs.webkit.org/show_bug.cgi?id=267688 — WebKit Bug 267688 [popover] Light dismiss doesn't work on iOS/iPadOS (RESOLVED FIXED, commit 285990@main, 2024-10-31)
  - https://webkit.org/blog/16439/webkit-features-in-safari-18-3/ — Safari 18.3 release notes (Jan 27, 2025) — "Fixed touching or clicking outside of the popover not closing it on iOS or iPadOS"
  - https://github.com/mdn/browser-compat-data/issues/22927 — MDN BCD issue: api.HTMLElement.popover should be partial support on iOS Safari
  - https://github.com/tailwindlabs/tailwindcss/discussions/15515 — Tailwind CSS discussion of the bug, with reproduction details
  - https://web.dev/blog/popover-baseline — "Popover API is now Baseline Newly available" (Jan 27, 2025) — coincides with the iOS fix
  - https://www.mail-archive.com/webkit-changes@lists.webkit.org/msg221907.html — Original commit message archive
  - https://developer.apple.com/documentation/safari-release-notes/safari-17_4-release-notes — Safari 17.4 release notes (March 5, 2024) — popover shipped here
  - https://github.com/oddbird/popover-polyfill — OddBird's BSD-3 popover polyfill (used by GitHub)
---

# WebKit Bug 267688 — light-dismiss broken on iOS/iPadOS Safari 17.x

> **Status at 2026-04-27.** RESOLVED FIXED in WebKit upstream (commit `285990@main`, October 31, 2024) and shipped in **Safari 18.3** (January 27, 2025). The polyfill window is **iOS/iPadOS Safari 17.0 through 18.2** — roughly March 5, 2024 through January 27, 2025, ten months. At our baseline (Safari 17.4+) this affects iOS users on 17.4 / 17.5 / 17.6 / 18.0 / 18.1 / 18.2, all of which are above the floor.

## The bug

On iOS and iPadOS Safari 17.0 through 18.2, tapping outside an `<element popover="auto">` does **not** dismiss the popover. The same code dismisses correctly on:

- Safari 18.3+ (the fix)
- Safari Desktop on macOS (any version)
- Chrome / Edge / Firefox on every platform
- iOS Chrome / iOS Firefox (because they use the iOS WebView, but WebView shipped its own behavior)

The light-dismiss algorithm — defined in [HTML §6.12.4 "Light dismiss algorithm"](https://html.spec.whatwg.org/multipage/popover.html) — should fire on pointer events outside the topmost popover and close the auto popover stack. On the affected iOS versions, the pointer event reaches the document but the dismiss algorithm does not run. Bug filed by Tim Nguyen (Mozilla) at WebKit Bugzilla #267688 ([bugs.webkit.org/show_bug.cgi?id=267688](https://bugs.webkit.org/show_bug.cgi?id=267688)).

The root cause was diagnosed by the WebKit team as event-region invalidation: the auto-popover list mutation didn't trigger event-region recomputation, so the browser's hit-testing for outside-the-popover tap didn't reach the dismissal handler. Fix invalidates event regions when the auto popover list changes.

## Bug tracker, fix commit, fix version

| Field | Value |
|---|---|
| Tracker | https://bugs.webkit.org/show_bug.cgi?id=267688 |
| Title | "[popover] Light dismiss doesn't work on iOS/iPadOS" |
| Filed | January 19, 2024 |
| Resolution | RESOLVED FIXED |
| Fix commit | 285990@main, by Tim Nguyen, October 31, 2024 |
| Fix shipped in | **Safari 18.3** — January 27, 2025 release |
| Release-notes confirmation | [Safari 18.3 release notes](https://webkit.org/blog/16439/webkit-features-in-safari-18-3/): _"Fixed touching or clicking outside of the popover not closing it on iOS or iPadOS."_ |

The fix landed exactly when the Popover API entered Baseline Newly available — see [web.dev/blog/popover-baseline](https://web.dev/blog/popover-baseline). The Web Platform Status team waited for the iOS fix before promoting Popover into Baseline.

## Reproduction

Save this as `popover-ios-test.html`, serve over HTTP, open on an iPhone or iPad running iOS 17.4–18.2:

```html
<!doctype html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<button popovertarget="menu">Open menu</button>
<div id="menu" popover="auto" style="padding: 1rem; border: 1px solid; background: white;">
  <p>This popover should dismiss when you tap outside.</p>
</div>
```

**Expected (per spec):** tapping anywhere outside `#menu` after opening it closes the popover.
**Actual on iOS 17.4–18.2:** tap registers but popover stays open. Only the Esc key (via external keyboard) or an explicit dismiss button works. On iPhone without an external keyboard, the user is **stuck** unless you provide an explicit close button.

## Workarounds

Three options ordered by recommendation.

### 1. Add an explicit close button (recommended, no JS)

The simplest, most accessible fallback. A close button is good UX on touch devices anyway — users on Safari 18.3+ get the redundant convenience.

```html
<div id="menu" popover="auto">
  <button popovertarget="menu" popovertargetaction="hide" aria-label="Close menu">×</button>
  <!-- menu content -->
</div>
```

`popovertargetaction="hide"` is supported across all browsers that support `popovertarget` — Chrome 114+, Firefox 125+, Safari 17+. The `aria-label` is required for screen-reader users on the close glyph.

### 2. Listen to outside taps via a backdrop click handler

For audiences where close buttons are off-brand (e.g., menus that need the entire surface as the popover content):

```js
const menu = document.querySelector('#menu');
menu.addEventListener('toggle', (event) => {
  if (event.newState === 'open') {
    document.documentElement.addEventListener('pointerdown', onOutsideTap, { capture: true });
  } else {
    document.documentElement.removeEventListener('pointerdown', onOutsideTap, { capture: true });
  }
});

function onOutsideTap(event) {
  if (!menu.contains(event.target)) {
    menu.hidePopover();
  }
}
```

Caveat: this re-implements light dismiss in JS, so on Safari 18.3+ both the native handler AND your handler will fire. Either feature-detect Safari < 18.3 (UA sniffing — fragile) or accept that the native handler runs first and your `hidePopover()` becomes a no-op (safe).

### 3. Ship `@oddbird/popover-polyfill` and force-replace native

The OddBird polyfill ([`@oddbird/popover-polyfill`](https://github.com/oddbird/popover-polyfill), v0.6.1, BSD-3-Clause, ~3KB gzipped) implements the Popover API in JS. By default it's a no-op when native popover is available. To force-override on affected iOS versions:

```js
import { isSupported, apply } from '@oddbird/popover-polyfill/fn';

// Detect iOS Safari 17.0–18.2 specifically
const ua = navigator.userAgent;
const isAffectedIOS = /iP(hone|ad|od)/.test(ua) &&
  /Version\/(17|18\.[012])/.test(ua) &&
  /Safari/.test(ua);

if (isAffectedIOS) {
  apply(); // overrides native popover with polyfill
}
```

Trade-offs: bundle weight, the polyfill's own behavior diverges slightly from native (e.g., it uses `:popover-open` synthesis), and UA sniffing is fragile. Reach for this only if option 1 doesn't fit your design.

GitHub uses the OddBird polyfill in production; their version drives broad real-world testing. See [popover.oddbird.net](https://popover.oddbird.net/) for the demo.

### What NOT to do

- **Don't switch to `popover="manual"`.** This is what some teams reach for first — it disables light dismiss on every browser, including the ones where it works. You'll regress UX for ~95% of users to fix the remaining ~5%.
- **Don't rely on `Esc` only.** iOS without an external keyboard has no Esc.
- **Don't sniff "is iOS" generically.** The bug is fixed in 18.3; sniffing "iOS Safari" without a version test will continue applying the workaround on fixed browsers.

## Real-world impact and prevalence

Per Statcounter (April 2026), iOS Safari 17.x and 18.0–18.2 collectively account for ~12–18% of mobile-browser traffic depending on geography. The bug was the **single biggest reason** the Popover API was held back from Baseline Newly Available status until January 2025. Multiple frameworks documented the bug:

- React Spectrum (Adobe) — see `safari-focus-inputs.md` for the related input-focus bug they tracked
- Bootstrap 5 — issue [#15935](https://github.com/twbs/bootstrap/issues/15935) on a related-but-separate `data-trigger="focus"` pattern
- Tailwind discussion — [#15515](https://github.com/tailwindlabs/tailwindcss/discussions/15515)
- MDN BCD — issue [#22927](https://github.com/mdn/browser-compat-data/issues/22927) requesting "partial support" downgrade for iOS until 18.3

If your audience analytics show meaningful iOS Safari 17.4–18.2 traffic in April 2026, ship the close-button workaround.

## Cross-references

- `safari-focus-inputs.md` — related iOS Safari bug: focusing inputs in popovers triggers virtual-keyboard scroll which closes the popover. Different mechanism, same target audience.
- `safari-184-tab-hang.md` — separate Safari < 18.4 bug (desktop AND iOS) where tabbing out of a popover hangs the focus loop.
- `../css-polyfills-and-shims/popover-polyfill.md` — full reference on the OddBird polyfill, including when it makes sense as a global override vs. surgical fallback.
- `../meta/the-modern-baseline.md` — the Popover API entered Baseline at January 27, 2025; this bug is the reason that date is later than the cross-engine ship-date.
