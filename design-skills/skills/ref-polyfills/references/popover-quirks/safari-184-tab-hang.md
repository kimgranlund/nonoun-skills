---
date: 2026-04-27
coverage: esoteric
peers:
  - ../popover-quirks/ios-safari-light-dismiss.md
  - ../popover-quirks/safari-focus-inputs.md
  - ../popover-quirks/popover-vs-dialog-toplayer.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://webkit.org/blog/16574/webkit-features-in-safari-18-4/ — Safari 18.4 release notes (March 31, 2025) — "Fixed tabbing out of a popover causing a hang in certain cases. (143145544)"
  - https://github.com/WebKit/WebKit/commit/c5c4b9c561811faabfb7148569c71d58ea9f58ac — WebKit commit "[popover] Improve focus handling"
  - https://github.com/WebKit/WebKit/commit/d8c15ed26f95a54f6136b94ac284cda4f4a451ec — WebKit commit "[popover] Improve popover-focus-2.html"
  - https://webkit.org/blog/16439/webkit-features-in-safari-18-3/ — Safari 18.3 release notes (Jan 27, 2025)
  - https://webkit.org/blog/16301/webkit-features-in-safari-18-2/ — Safari 18.2 release notes — "Fixed popover tab navigation" (partial earlier fix)
  - https://html.spec.whatwg.org/multipage/popover.html — HTML spec §6.12 The popover attribute and focus order
  - https://developer.apple.com/documentation/safari-release-notes/safari-18_4-release-notes — Apple-developer release notes for Safari 18.4
---

# Safari < 18.4 — tab-out-of-popover hangs the focus loop

> **Status at 2026-04-27.** Fixed in **Safari 18.4** (March 31, 2025) per the [release-notes entry](https://webkit.org/blog/16574/webkit-features-in-safari-18-4/): _"Fixed tabbing out of a popover causing a hang in certain cases. (143145544)"_. The polyfill / workaround window is **Safari 17.0 through 18.3** — both desktop and iOS — roughly Sept 2023 through Jan 2025, eighteen months. Safari 18.2 had a partial earlier fix ("Fixed popover tab navigation") that addressed easier cases; the full hang-fix is 18.4. Affects every keyboard-driven user testing a popover on those Safari versions.

## The bug

When focus is inside a `<element popover="auto">` on Safari 17.0–18.3 and the user presses Tab past the last focusable element in the popover, Safari enters a focus-management hang state:

- Tab key produces no observable effect.
- Focus is stuck on (or near) the last popover-internal element.
- VoiceOver announces nothing on subsequent Tab presses.
- The page becomes inaccessible-by-keyboard until the user clicks outside the popover or refreshes.

The HTML spec (§6.12 [Popover focus navigation order](https://html.spec.whatwg.org/multipage/popover.html)) defines that, on Tab past a popover's last element, focus should:

1. Move to the next focusable element **after** the popover's invoker (in document order).
2. If no invoker is associated, move to the next focusable element after the popover element itself.
3. If neither exists, fall through to the address bar / browser chrome (the standard end-of-document behavior).

On affected Safari versions, step 1 fails — Safari does not correctly compute the "next focusable after the invoker" position when the popover was opened via `popovertarget` and the invoker is far from the popover in DOM order. The result is a hang rather than a graceful fall-through.

The fix in Safari 18.4 is referenced in WebKit commits `c5c4b9c5` ("[popover] Improve focus handling") and `d8c15ed2` ("[popover] Improve popover-focus-2.html"), both landed in early 2025 and shipped in 18.4.

## Affected Safari versions

| Version | Behavior |
|---|---|
| **17.0–17.6** | Affected on desktop AND iOS |
| **18.0–18.1** | Affected on desktop AND iOS |
| **18.2** | Partially fixed — release notes say "Fixed popover tab navigation" but the hang case persists. |
| **18.3** | Still affected for the hang-on-last-element edge case. |
| **18.4 (March 31, 2025)** | **Fixed.** Tab now exits the popover correctly. |
| 18.5+, 26.x | Not affected. |

Safari Desktop and iOS both shipped the fix in 18.4 — the iOS version of WebKit tracks the desktop's bug-fix cadence here.

## Reproduction

```html
<!doctype html>
<button id="opener" popovertarget="menu">Open menu</button>
<a href="#after">Skip-link target after the popover</a>

<div id="menu" popover="auto" style="padding: 1rem; background: white; border: 1px solid;">
  <button>First action</button>
  <button>Second action</button>
  <button>Third action</button>
</div>

<a id="after" href="#">After</a>
```

**Test sequence:**
1. Press Tab to focus "Open menu".
2. Press Enter — popover opens; focus is moved into the popover (Safari's auto-focus on the first focusable element).
3. Press Tab three times to walk through "First action" / "Second action" / "Third action".
4. Press Tab a fourth time.

**Expected (per spec):** focus moves to the "Skip-link target after the popover" link or to "After".
**Actual on Safari 17–18.3:** focus appears to be retained on the third button or on no element at all. Subsequent Tab presses do nothing. Keyboard navigation is broken until the popover is dismissed.

VoiceOver users experience this as "focus disappears." The popover remains visually open. The only way out is to press Esc (which does still work on macOS) or to click outside (which is broken on iOS — see `ios-safari-light-dismiss.md` — making this bug compound on iOS).

## Workarounds

Two practical options. The native API gives no clean fix; you have to detect and intervene.

### 1. Force focus restoration on `keydown` Tab past the last element

Catch the Tab keystroke before the browser handles it, and explicitly move focus to the next focusable element after the popover's invoker.

```js
const popover = document.querySelector('#menu');
const invoker = document.querySelector('#opener');

popover.addEventListener('keydown', (event) => {
  if (event.key !== 'Tab') return;

  const focusables = popover.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const last = focusables[focusables.length - 1];
  const first = focusables[0];

  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    focusNextFocusableAfter(invoker, { reverse: true });
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    focusNextFocusableAfter(invoker, { reverse: false });
  }
});

function focusNextFocusableAfter(el, { reverse }) {
  const all = [...document.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  )];
  const idx = all.indexOf(el);
  const next = reverse ? all[idx - 1] : all[idx + 1];
  if (next) next.focus();
}
```

This re-implements the focus-handoff that WebKit gets wrong. Run it unconditionally — on Safari 18.4+ both your handler and the native handler will fire, but `event.preventDefault()` ensures only your handler's `focus()` call wins, and the result is identical to native behavior.

### 2. Restore focus to the invoker on close

Even with workaround 1, you should restore focus to the invoker when the popover closes — it's [WCAG 2.4.3 Focus Order](https://www.w3.org/WAI/WCAG22/quickref/#focus-order) and APG-recommended best practice anyway.

```js
popover.addEventListener('toggle', (event) => {
  if (event.newState === 'closed') {
    invoker.focus();
  }
});
```

The Popover API in modern browsers does this automatically when the popover was opened via `popovertarget` — but the auto-restore is precisely what's broken on Safari 17–18.3 in some cases. Doing it explicitly is a belt-and-suspenders fix that costs nothing.

### What NOT to do

- **Don't trap focus inside the popover.** Popovers are not modal dialogs. Trapping focus violates the spec; the Tab key should be able to leave the popover. Focus traps are correct for `<dialog showModal()>` only.
- **Don't disable Tab inside the popover.** Some Stack Overflow answers suggest `event.preventDefault()` on every Tab to "stop the bug." This breaks keyboard navigation for users with assistive technology far worse than the bug itself.

## Why this matters for accessibility audits

A keyboard-only user on Safari 17.4–18.3 cannot cleanly navigate past a popover. WAVE, Axe, and Lighthouse will not catch this — they don't simulate Tab past the last focusable element in a top-layer surface. Manual keyboard testing on the affected Safari versions will catch it.

If your test matrix includes Safari Desktop or iOS Safari at our baseline (17.4+) and the audit standard is WCAG 2.2 AA, this bug puts SC 2.1.1 (Keyboard) and SC 2.4.3 (Focus Order) at risk on the affected versions. Document the workaround in your accessibility statement, or raise your minimum supported Safari to 18.4.

## Cross-references

- `ios-safari-light-dismiss.md` — separate iOS Safari 17–18.2 bug; in combination with this one, popovers on iOS are nearly unusable for keyboard users on those versions.
- `safari-focus-inputs.md` — separate iOS Safari bug on focusing inputs inside popovers; related "focus management is hard on iOS" theme.
- `popover-vs-dialog-toplayer.md` — when keyboard accessibility matters more than popover semantics, `<dialog showModal()>` is more reliable.
- `../meta/the-modern-baseline.md` — Safari 17.4 is our floor; this bug means 17.4 through 18.3 (a year and a half of releases) need this workaround if you serve keyboard-driven users.
