---
date: 2026-04-27
coverage: esoteric
peers:
  - ../popover-quirks/popover-vs-dialog-toplayer.md
  - ../anchor-positioning-quirks/safari-26-anchor-shipped.md
  - ../anchor-positioning-quirks/popover-margins-interaction.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://bugs.webkit.org/show_bug.cgi?id=279588 — WebKit Bug 279588 [CSS anchor positioning] WebProcess crash when popover uses anchoring (RESOLVED FIXED, commit ba8e7f0, Oct 17, 2024)
  - https://github.com/WebKit/WebKit/pull/33696 — WebKit PR #33696 by Pawel Lampe (Scony) — fixes the crash
  - https://www.mail-archive.com/webkit-changes@lists.webkit.org/msg221222.html — Commit message archive (commit ba8e7f0)
  - https://webkit.org/blog/17333/webkit-features-in-safari-26-0/ — Safari 26.0 release notes (Sept 15, 2025) — anchor positioning shipped
  - https://drafts.csswg.org/css-anchor-position-1/ — CSS Anchor Positioning Level 1 spec
  - https://www.oddbird.net/2025/05/06/polyfill-updates/ — OddBird's polyfill update notes
  - https://chromestatus.com/feature/5124922471874560 — Chrome platform status: CSS Anchor Positioning
---

# WebKit Bug 279588 — WebProcess crash when popover uses CSS anchor positioning

> **Status at 2026-04-27.** **RESOLVED FIXED** in WebKit upstream (commit `ba8e7f0`, October 17, 2024, by Pawel Lampe, reviewed by Antti Koivisto). The fix is in `Source/WebCore/style/AnchorPositionEvaluator.cpp`. Shipped in **Safari 26.0** (September 15, 2025) — the same release that brought CSS Anchor Positioning to Safari. The crash window was narrow: it existed only on **WebKit nightlies and Safari Technology Preview builds between Safari 18.0 (Sept 2024) and the fix landing in October 2024**, and was never on a stable Safari channel. **No production users were ever exposed to this crash.** The file documents it for historical completeness and for anyone testing CSS anchor positioning on older WebKit nightlies.

## The bug

When a popover element used CSS anchor positioning (`position-anchor` + `position-area` or `top: anchor(...)`), and that popover was hidden via `display: none`, the WebKit WebProcess crashed.

The technical cause, per the [WebKit Bugzilla report](https://bugs.webkit.org/show_bug.cgi?id=279588):

> _"element.renderer() is nullptr in the Source/WebCore/style/StyleTreeResolver.cpp:1340."_

The `AnchorPositionEvaluator` was attempting to evaluate anchor positioning for an element whose renderer had been torn down (because the element had `display: none`). The renderer pointer was null; dereferencing crashed the WebProcess (browser tab crash, not full-browser crash, but disruptive nonetheless).

The fix bails out of anchor evaluation early when the element has no renderer:

```diff
// Source/WebCore/style/AnchorPositionEvaluator.cpp
 void AnchorPositionEvaluator::evaluate(...) {
+  if (!element.renderer())
+    return;
   // ... existing logic
 }
```

(Reconstructed from commit message; not the literal patch.)

## Bug tracker, fix commit, fix version

| Field | Value |
|---|---|
| Tracker | https://bugs.webkit.org/show_bug.cgi?id=279588 |
| Title | "[CSS anchor positioning] WebProcess crash when popover uses anchoring" |
| Filed | September 12, 2024 |
| Reporter | Pawel Lampe |
| Resolution | RESOLVED FIXED |
| Fix commit | ba8e7f03c9a9b5a80b3e7dfc5873b94dba5ea5d0, October 17, 2024 |
| Reviewed by | Antti Koivisto |
| Modified files | Source/WebCore/style/AnchorPositionEvaluator.cpp; LayoutTests/TestExpectations |
| Shipped in | **Safari 26.0** — September 15, 2025 (the first stable Safari with CSS anchor positioning) |

## Affected versions

| Version | Behavior |
|---|---|
| Safari 17.x | Not affected — CSS anchor positioning not yet shipped. |
| Safari 18.0–18.4 | Not affected at the stable channel. |
| Safari Technology Preview ~Sept–Oct 2024 | **Affected** in TP builds before the fix. |
| WebKit nightlies Sept 12, 2024 – Oct 17, 2024 | **Affected**. |
| Safari 26.0+ (Sept 2025) | **Fixed** before shipping. |

CSS anchor positioning was a Chromium-led feature; Chrome 125 shipped in May 2024. WebKit was actively developing its implementation through 2024 — bug 279588 was caught and fixed during that development period. **No Safari stable release ever shipped the crash.**

## Why this file is in the skill

Three reasons:

1. **Historical fact-check.** Some blog posts and Stack Overflow answers from late 2024 mention "popover + anchor positioning crashes Safari." Those reports are accurate for nightlies and TP at the time, but not for any stable Safari. Engineers searching for the bug in 2026 need to know it was contained.

2. **Pattern caution for nightly testing.** If you're testing CSS anchor positioning in WebKit nightly builds (e.g., for early-feedback patches to OddBird's polyfill), the crash signature is documented here. The crash is reliably reproducible on builds in that 5-week window.

3. **Safari 26.0 anchor-positioning landing.** Safari 26.0 (September 2025) is the first stable Safari with CSS anchor positioning support. Anyone shipping anchor positioning to Safari 26.0+ should know that the implementation was carefully tested through the 2024–2025 development cycle, including this crash.

## Reproduction (for nightly builds in the affected window)

```html
<!doctype html>
<style>
  #anchor {
    anchor-name: --my-anchor;
  }
  #popover {
    position-anchor: --my-anchor;
    position-area: bottom;
  }
</style>

<button id="anchor" popovertarget="popover">Open</button>
<div id="popover" popover>Popover content</div>

<script>
  const popover = document.querySelector('#popover');
  popover.showPopover();

  // Trigger the crash:
  popover.style.display = 'none';
  // WebProcess crashes during the next style resolution pass.
</script>
```

On Safari nightlies between Sept 12 and Oct 17, 2024, this would crash the WebProcess. On Safari 26.0+ stable, this is safe.

## Workaround (historical, for the affected window only)

Not applicable in production. The bug never reached a stable Safari channel.

If you encountered this on a nightly during testing, the workaround was:

- Use `visibility: hidden` instead of `display: none` to hide the popover. Visibility-hidden elements still have renderers, so `AnchorPositionEvaluator` doesn't dereference null.
- Or: use programmatic `hidePopover()` instead of CSS-driven `display: none` toggling. The Popover API's hide path doesn't go through the same anchor-evaluation codepath.

```js
// Instead of: popover.style.display = 'none';
popover.hidePopover();
```

This is also generally a better pattern — Popover API state should be managed via the API methods, not via CSS display toggling.

## What this means for the broader Safari + anchor positioning story

CSS Anchor Positioning landed in Safari 26.0. Before that, Safari users got anchor positioning **only via the OddBird polyfill** (`@oddbird/css-anchor-positioning`), which doesn't go through WebProcess and has no exposure to this bug.

For our baseline (Safari 17.4+), CSS anchor positioning is a polyfill-candidate feature — see `../anchor-positioning-quirks/safari-26-anchor-shipped.md` for the full Safari + anchor positioning timeline. The crash bug is incidental to that larger story.

## Cross-references

- `popover-vs-dialog-toplayer.md` — anchor-positioned popovers still obey top-layer rules; combining anchor positioning with modal dialog inerts is yet another interaction surface.
- `../anchor-positioning-quirks/safari-26-anchor-shipped.md` — full Safari anchor-positioning timeline; bug 279588 is one of many landed during that development cycle.
- `../anchor-positioning-quirks/popover-margins-interaction.md` — separate (and **at our baseline** more relevant) bug: popover UA-style margins interfere with anchor positioning. CSSWG actively adjusting.
- `../css-polyfills-and-shims/anchor-positioning-polyfill.md` — `@oddbird/css-anchor-positioning` polyfill, which avoided this crash entirely by running in JS instead of WebProcess.
- `../meta/the-modern-baseline.md` — at our baseline, CSS anchor positioning is "polyfill candidate, post-baseline shipping in Safari 26 / Firefox 147."
