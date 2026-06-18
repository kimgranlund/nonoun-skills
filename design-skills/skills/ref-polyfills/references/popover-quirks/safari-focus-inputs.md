---
date: 2026-04-27
coverage: esoteric
peers:
  - ../popover-quirks/ios-safari-light-dismiss.md
  - ../popover-quirks/safari-184-tab-hang.md
  - ../popover-quirks/popover-vs-dialog-toplayer.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://github.com/adobe/react-spectrum/issues/7579 — "Inputs in popovers do not work on iOS" — confirmed on iOS 17.5 and 18.2
  - https://github.com/Shopify/polaris-react/issues/1370 — "[Popover] TextField in Popover may be covered by iOS keyboard" (related)
  - https://github.com/alexkatz/react-tiny-popover/issues/143 — react-tiny-popover virtual-keyboard positioning issue
  - https://imeugenia.medium.com/debugging-is-thinking-the-story-of-virtual-keyboard-bug-in-mobile-safari-1623c878660e — Engineering write-up on the virtual-keyboard scroll mechanism
  - https://bugs.webkit.org/show_bug.cgi?id=267688 — Light-dismiss bug (related root cause: scroll-triggers-dismiss)
  - https://html.spec.whatwg.org/multipage/popover.html — HTML spec §6.12 The popover attribute
  - https://developer.mozilla.org/en-US/docs/Web/API/Popover_API/Using — MDN Popover API guide
---

# iOS Safari closes popover when focusing inputs (virtual-keyboard scroll)

> **Status at 2026-04-27.** Persists across iOS Safari 17.4 through at least 18.2 — confirmed in [react-spectrum issue #7579](https://github.com/adobe/react-spectrum/issues/7579) on both iOS 17.5 and iOS 18.2. Likely present in 18.3+ as well; the underlying mechanism (virtual keyboard triggers scroll, scroll triggers dismiss) was not addressed by the Safari 18.3 light-dismiss fix. **Affects every iOS user the moment they tap an input inside a popover.** No clean fix; workaround is `popover="manual"` or `<dialog showModal()>`.

## The bug

On iOS Safari, when an `<input>`, `<textarea>`, or `<select>` is focused inside an `<element popover="auto">`, the popover dismisses immediately — *before* the virtual keyboard finishes opening, often before the user can type a single character.

The mechanism, per the [react-spectrum issue thread](https://github.com/adobe/react-spectrum/issues/7579) and the engineering write-up by [Eugenia Zigisova](https://imeugenia.medium.com/debugging-is-thinking-the-story-of-virtual-keyboard-bug-in-mobile-safari-1623c878660e):

1. User taps an input inside an open popover.
2. iOS begins to show the virtual keyboard.
3. The virtual-keyboard appearance forces a viewport resize and a scroll event on the page (iOS scrolls the focused input into view above the keyboard).
4. The scroll-up moves the popover relative to the viewport.
5. iOS's light-dismiss heuristic interprets this scroll-induced viewport change as an outside-the-popover interaction.
6. Light-dismiss fires; popover closes; keyboard never finishes appearing.

The user sees the popover flash closed the instant they tap an input. This is **separate from** Bug 267688 (light-dismiss not firing on outside taps) — the Safari 18.3 fix landed light-dismiss but did not change the input-focus dismiss behavior. They share a root cause (event-region invalidation around scroll/focus) but were not fixed by the same commit.

## Affected versions

| iOS / iPadOS Safari | Behavior |
|---|---|
| 17.0–17.3 | Unverified; probably affected. Below baseline (17.4). |
| **17.4** | Affected. Baseline floor. |
| 17.5 | **Confirmed affected** in react-spectrum #7579 |
| 17.6 | Probably affected. |
| 18.0 | Probably affected. |
| 18.1 | Probably affected. |
| 18.2 | **Confirmed affected** in react-spectrum #7579 |
| 18.3 | Probably still affected — light-dismiss fix did not address this path. |
| 18.4+ | Unverified at 2026-04-27. No release-notes mention of fix. |

Desktop Safari is **not** affected — no virtual keyboard, no scroll event on focus.

## Reproduction

Test on a real iPhone or iPad. Simulators do not reproduce reliably (no real virtual keyboard).

```html
<!doctype html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<button popovertarget="search">Search</button>
<div id="search" popover="auto" style="padding: 1rem; background: white; border: 1px solid;">
  <label>
    Query: <input type="search" autocomplete="off">
  </label>
  <button popovertarget="search" popovertargetaction="hide">Cancel</button>
</div>
```

**Expected:** tap "Search" → popover opens → tap input → keyboard rises → user types.
**Actual on iOS Safari 17.4–18.2:** tap "Search" → popover opens → tap input → popover snaps closed before keyboard finishes opening. User taps "Search" again → repeat. Input is essentially unusable inside a popover with `popover="auto"`.

## Workarounds

Four options. Pick based on whether the popover semantics permit demoting to manual or modal.

### 1. Use `popover="manual"` instead of `popover="auto"` (recommended)

Manual popovers do not light-dismiss. The downside is that you lose Esc-to-close, click-outside-to-close, and the auto-stack management — your popover stays open until you call `hidePopover()` explicitly.

```html
<div id="search" popover="manual">
  <input type="search">
  <button popovertarget="search" popovertargetaction="hide">Done</button>
</div>
```

If your popover is form-like (search, filter, settings panel), manual is usually the right semantic anyway: the user is committing to interaction, not browsing a transient surface.

### 2. Render as a modal `<dialog>` instead

For form-heavy popovers, a true modal dialog is more appropriate and avoids the bug entirely:

```html
<dialog id="search">
  <form method="dialog">
    <input type="search">
    <button>Search</button>
    <button formmethod="dialog" value="cancel">Cancel</button>
  </form>
</dialog>

<script>
  document.querySelector('#openSearch').addEventListener('click', () => {
    document.querySelector('#search').showModal();
  });
</script>
```

`<dialog showModal()>` puts the dialog in the top layer, inerts the rest of the page, and is unaffected by the popover light-dismiss heuristic. Trade-off: it inerts background content (sometimes intentional, sometimes not). See `popover-vs-dialog-toplayer.md` for when this trade-off is acceptable.

### 3. Listen for `beforetoggle` and `preventDefault` on focus-triggered dismiss (limited, fragile)

The `beforetoggle` event is cancelable when toggling **to open**, but per [MDN](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event), **not cancelable when closing**. So you cannot cancel the dismissal when iOS triggers it. This workaround does NOT work — listed here so you don't waste time on it.

### 4. Suppress scroll during input focus (engineering-heavy)

Listen for `focus` on inputs inside the popover, store the current scroll position, and restore it after a tick:

```js
const popover = document.querySelector('#search');
popover.addEventListener('focusin', (event) => {
  if (!event.target.matches('input, textarea, select')) return;
  const scrollY = window.scrollY;
  requestAnimationFrame(() => {
    if (window.scrollY !== scrollY) {
      window.scrollTo(0, scrollY);
    }
  });
});
```

This races the iOS virtual-keyboard scroll. Reliability is poor; the keyboard appearance fires multiple scroll events over ~200ms, and aggressively restoring scroll fights the user's expectation that focused inputs scroll into view above the keyboard. **Last resort only**; option 1 or 2 is almost always better.

## GitHub issue trail (well-documented)

Despite no WebKit Bugzilla entry that exclusively names this behavior (it gets bundled with #267688 in many threads), the framework-level issue threads are detailed:

- **Adobe React Spectrum issue [#7579](https://github.com/adobe/react-spectrum/issues/7579)** — "Inputs in popovers do not work on iOS". Reproduction steps, version confirmation across iOS 17.5 and 18.2, manifests in `ColorPicker` and form-input popovers. Reporter quote: _"This seems to happen only when the page is scrolled. I believe that when the iOS virtual keyboard is brought up, it scrolls the page and therefore closes the popover."_
- **Shopify Polaris [#1370](https://github.com/Shopify/polaris-react/issues/1370)** — related: TextField inside popover obscured by iOS keyboard.
- **react-tiny-popover [#143](https://github.com/alexkatz/react-tiny-popover/issues/143)** — positioning bug under virtual keyboard.

These are JavaScript-popover-library issues (not native Popover API), but the underlying iOS Safari behavior — virtual keyboard scrolls the viewport and disrupts open overlays — is the same root cause as the native Popover API issue.

## Cross-references

- `ios-safari-light-dismiss.md` — sibling iOS Safari popover bug. Both are heuristic-driven dismissals on iOS; both are why the Popover API took until January 2025 to enter Baseline Newly available.
- `safari-184-tab-hang.md` — different Safari < 18.4 popover bug (focus management on Tab). All three combined make iOS Safari 17.4–18.2 the most popover-hostile cell of our baseline matrix.
- `popover-vs-dialog-toplayer.md` — for the `<dialog showModal()>` migration path, including its drawback of inerting background content.
