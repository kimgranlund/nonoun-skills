---
date: 2026-04-27
coverage: extended
peers:
  - ../popover-quirks/popover-hint-chromium-only.md
  - ../popover-quirks/popover-vs-dialog-toplayer.md
  - ../popover-quirks/safari-184-tab-hang.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://html.spec.whatwg.org/multipage/popover.html — HTML spec §6.12 The popover attribute
  - https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/showPopover — MDN showPopover()
  - https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/togglePopover — MDN togglePopover()
  - https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/hidePopover — MDN hidePopover()
  - https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event — MDN beforetoggle event
  - https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/toggle_event — MDN toggle event
  - https://developer.mozilla.org/en-US/docs/Web/API/HTMLButtonElement/popoverTargetAction — MDN popoverTargetAction
  - https://hidde.blog/popover-semantics/ — Hidde de Vries on popover semantics and ARIA
  - https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/ — APG Dialog (modal) pattern
  - https://www.w3.org/WAI/ARIA/apg/patterns/menu/ — APG Menu pattern
  - https://webkit.org/blog/16301/webkit-features-in-safari-18-2/ — Safari 18.2 release notes — "Fixed `popovertarget` to work on buttons in a form"
---

# Programmatic vs declarative popover API divergences

> **Status at 2026-04-27.** Both paths are interoperable across Chrome 114+ / Firefox 125+ / Safari 17+ at the API surface level. Real-world divergences cluster around three areas: (1) implicit ARIA wiring, (2) focus restoration after close, and (3) historical Safari edge cases (most notably the `popovertarget`-in-form bug fixed in Safari 18.2). Use **declarative `popovertarget`** by default for accessibility-correct behavior; reach for **programmatic `showPopover()`** only when state is tied to non-button events.

## Two ways to open a popover

### Declarative — `popovertarget` attribute

```html
<button popovertarget="menu">Open menu</button>
<div id="menu" popover>...</div>
```

Per [HTML spec §6.12.5](https://html.spec.whatwg.org/multipage/popover.html), clicking the button activates a UA-defined toggle action on the referenced popover. The `popovertargetaction` attribute, if present, narrows the action: `"show"`, `"hide"`, or `"toggle"` (default).

Supported on `<button>` and `<input type="button">` elements only. Not on `<a>`, `<div>`, custom elements, or `<button type="submit">` inside forms (the submit button's primary semantics override).

### Programmatic — JS methods

```js
const menu = document.querySelector('#menu');

menu.showPopover();    // Show; throws InvalidStateError if already open
menu.hidePopover();    // Hide; throws InvalidStateError if already closed (per spec — see below)
menu.togglePopover();  // Show if hidden, hide if open. Returns boolean (true if now open).
menu.togglePopover({ force: true });   // Force-show
menu.togglePopover({ force: false });  // Force-hide
```

All three methods throw `DOMException` with name `InvalidStateError` if the element doesn't have a `popover` attribute, or in some illegal states (e.g., calling `showPopover` on a popover whose ancestor is a closed `<dialog>`).

Available on `HTMLElement` since Chrome 114, Firefox 125, Safari 17 — universally at our baseline.

## Divergences

### Divergence 1: implicit ARIA wiring

**Declarative (`popovertarget`)**: the browser establishes an implicit ARIA relationship. Specifically:

- The button gets `aria-expanded="false"` / `"true"` reflecting popover state.
- The button gets an implicit `aria-details` or `aria-controls` referring to the popover (engine-dependent).
- VoiceOver / NVDA / JAWS announce the relationship.

This works on Chrome 114+, Firefox 125+, Safari 17+. See [Hidde de Vries, "Semantics and the popover attribute"](https://hidde.blog/popover-semantics/) for the engine-by-engine ARIA exposure differences.

**Programmatic (`showPopover()`)**: NO automatic ARIA wiring. The element calling `showPopover` may not be a button at all (it could be a custom element, a `keydown` handler, a hover trigger). The browser cannot guess the relationship.

You must wire `aria-expanded`, `aria-controls`, etc. by hand:

```js
function openMenu() {
  const button = document.querySelector('#menuButton');
  const menu = document.querySelector('#menu');

  menu.showPopover();
  button.setAttribute('aria-expanded', 'true');
}

menu.addEventListener('toggle', (event) => {
  if (event.newState === 'closed') {
    button.setAttribute('aria-expanded', 'false');
  }
});
```

This is the **single biggest reason to prefer declarative** when you can. Manual ARIA bookkeeping drifts; the browser gets it right when you give it the contract.

### Divergence 2: focus restoration on close

**Declarative**: when the popover closes (via Esc, light dismiss, or another `popovertarget` button), focus is automatically restored to the original `popovertarget` invoker. This is spec-required and shipped consistently across Chrome 114+, Firefox 125+, Safari 17+ (with the Safari < 18.4 caveat — see `safari-184-tab-hang.md`).

**Programmatic**: focus restoration is **not automatic**. After `hidePopover()`, focus typically falls to `<body>` or stays on whatever element had focus when the popover closed. You must restore focus explicitly:

```js
const opener = document.activeElement;
menu.showPopover();

menu.addEventListener('toggle', (event) => {
  if (event.newState === 'closed' && opener) {
    opener.focus();
  }
}, { once: true });
```

WCAG 2.1 SC 2.4.3 (Focus Order) and SC 2.4.7 (Focus Visible) practically require this restoration. Forgetting it is a common a11y regression in JS-driven popover code.

A newer signal: the [`source` option](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/showPopover) on `showPopover({ source: triggerElement })` — shipped in Chrome 131+ — tells the browser which element to restore focus to. Not yet at full interop. Do not rely on it across our baseline; do the restoration manually.

### Divergence 3: `popovertargetaction` honoring

The attribute accepts three values: `"show"`, `"hide"`, `"toggle"`. Default is `"toggle"`. All engines honor `"toggle"` (the default). Edge cases:

- `popovertargetaction="show"` on an already-open popover: per spec, no action. All engines correct.
- `popovertargetaction="hide"` on an already-closed popover: per spec, no action. All engines correct.
- `popovertargetaction="show"` then explicit attribute change to `"hide"` mid-interaction: engine-defined behavior. Test before relying on dynamic mutation of `popovertargetaction`.

A historical Safari edge case: **Safari 18.2 fixed `popovertarget` to work on buttons inside `<form>` elements** (per [Safari 18.2 release notes](https://webkit.org/blog/16301/webkit-features-in-safari-18-2/) — _"Fixed `popovertarget` to work on buttons in a form."_). On Safari 17.0–18.1, a `<button popovertarget="...">` inside a form would either be misinterpreted as a submit button or fail to invoke the popover entirely. Workaround on those versions: explicit `type="button"` and / or programmatic `showPopover()` from a click handler.

```html
<!-- Buggy on Safari 17.0–18.1 inside a <form>: -->
<form>
  <button popovertarget="filters">Filters</button>
</form>

<!-- Reliable everywhere: -->
<form>
  <button type="button" popovertarget="filters">Filters</button>
</form>
```

The explicit `type="button"` is good practice anyway.

### Divergence 4: `beforetoggle` and `toggle` event timing

Both events are spec-defined to fire on **both** declarative and programmatic paths. Per [MDN beforetoggle](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/beforetoggle_event):

- `beforetoggle` fires just before the popover state changes. **Cancelable** when toggling open (i.e., `event.preventDefault()` blocks the open). **NOT cancelable** when toggling closed.
- `toggle` fires just after the state change.
- Both events are `ToggleEvent` instances with `oldState` and `newState` properties (`"open"` or `"closed"`).

Engine consistency at our baseline is good. One historical Safari quirk: in early Safari 17.x, `beforetoggle` did not fire on Esc-key-triggered dismissal in some configurations. Not yet found a Bugzilla ID; the behavior was tightened in Safari 17.4 and is stable in our baseline window.

The non-cancelability of `beforetoggle` on close means: **you cannot prevent a popover from dismissing.** This is intentional (light dismiss is a user-initiated action; sites should not be able to trap users). It also means the iOS Safari focus-input bug (see `safari-focus-inputs.md`) cannot be worked around by canceling `beforetoggle` — the close has already won by the time your handler runs.

## When to use which

### Default to declarative

Use `<button popovertarget="...">` when:

- The popover is opened by clicking a button.
- You want correct ARIA out of the box.
- You want focus restoration on close out of the box.
- You don't need to manage popover state from JS.

This covers ~80% of popover use cases.

### Use programmatic when state is dynamic

Use `showPopover()` / `hidePopover()` / `togglePopover()` when:

- The popover opens in response to a non-click event: hover, focus, keydown, scroll, intersection, network response.
- The popover lifecycle is controlled by application state (Redux, Zustand, signals, etc.).
- You need to coordinate multiple popovers (e.g., close all peers when one opens).
- You're rendering popovers from a framework that owns the open/closed state.

In all these cases: do the ARIA wiring and focus restoration yourself. Treat them as required, not optional.

### Mixing the two paths

You can mix freely. A `<button popovertarget="x">` and a manual `x.showPopover()` both move `x` through the same state machine; both fire `beforetoggle` and `toggle`. The button's automatic ARIA reflects the current state regardless of which path opened the popover.

## Cross-references

- `safari-184-tab-hang.md` — focus restoration is the spec-correct behavior on declarative path; the Safari < 18.4 hang bug is in the implementation, not the contract.
- `popover-hint-chromium-only.md` — `popovertarget` works identically for `hint` as for `auto`/`manual`.
- `popover-vs-dialog-toplayer.md` — declarative `popovertarget` cannot reach across DOM hierarchy (the popover must be reachable by ID); programmatic `showPopover()` has the same constraint but doesn't depend on DOM proximity.
- W3C ARIA Authoring Practices: [APG Menu pattern](https://www.w3.org/WAI/ARIA/apg/patterns/menu/) and [APG Dialog (modal) pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/) — for the correct ARIA contract when authoring popovers as menus or dialogs respectively.
