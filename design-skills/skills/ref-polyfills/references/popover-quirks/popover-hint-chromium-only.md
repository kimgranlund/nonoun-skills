---
date: 2026-04-27
coverage: extended
peers:
  - ../popover-quirks/popovertarget-vs-showpopover.md
  - ../popover-quirks/popover-vs-dialog-toplayer.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://developer.chrome.com/blog/popover-hint — "Popover = hint" (Feb 26, 2025) — Chrome 133 launch
  - https://developer.chrome.com/release-notes/133 — Chrome 133 release notes (Feb 4, 2025)
  - https://groups.google.com/a/chromium.org/g/blink-dev/c/2N6dnbgjzLs — blink-dev "Intent to Ship: popover=hint"
  - https://chromestatus.com/feature/5073251081912320 — Chrome Platform Status entry for popover=hint
  - https://caniuse.com/mdn-html_global_attributes_popover_hint — caniuse browser-support matrix (Chrome 133+, Edge 133+, Firefox 149+, Safari N/A)
  - https://github.com/whatwg/html/pull/9778 — WHATWG HTML PR adding popover=hint to spec
  - https://github.com/oddbird/popover-polyfill/issues/227 — OddBird popover-polyfill v0.6+ supports popover=hint
  - https://html.spec.whatwg.org/multipage/popover.html — HTML spec §6.12 (now includes Hint state)
---

# `popover="hint"` is Chromium-only at our baseline

> **Status at 2026-04-27.** Shipped in **Chrome / Edge 133** (February 4, 2025). **Firefox 149** (verify exact ship date — caniuse lists 149+ as supported). **Safari has not shipped** as of Safari 26.5 per caniuse. At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+) this means: Chrome users get `hint` natively; Firefox 129–148 users do NOT; Safari users at any baseline-eligible version do NOT. **Use `popover="auto"` as the cross-browser fallback** — invalid attribute values are treated as `auto` automatically by the parser.

## What `popover="hint"` adds

A third popover type beyond `auto` and `manual`. Its semantics, from the [HTML spec](https://html.spec.whatwg.org/multipage/popover.html):

| Type | Light dismiss? | Closes other popovers? | Use case |
|---|---|---|---|
| `auto` | Yes | Closes other `auto` popovers and `hint`s when opened | Menus, dropdowns, settings panels |
| `manual` | No | Doesn't close anything | Toasts, persistent overlays |
| `hint` | Yes | Closes other `hint`s but **NOT `auto` popovers** | Tooltips, status pills, hovercards |

The key innovation of `hint`: it allows a tooltip to appear **without dismissing an open menu**. The canonical example, from [the Chrome blog](https://developer.chrome.com/blog/popover-hint):

> _A `<select>` picker is open (`popover=auto`) and a hover-triggered tooltip (`popover=hint`) is shown. That action does not close the `<select>` picker._

Without `hint`, the only options were `auto` (which would dismiss the picker) or `manual` (which gives up light dismiss and outside-tap-to-close, plus requires custom dismissal logic).

`hint` also has a special nesting rule: when shown nested inside an `auto` popover, the hint joins the `auto` stack and behaves consistently with that stack's dismiss order. This avoids the "tooltip on a button inside a menu" awkwardness.

## Browser support (April 2026)

Per [caniuse.com/mdn-html_global_attributes_popover_hint](https://caniuse.com/mdn-html_global_attributes_popover_hint):

| Engine | Version | Status |
|---|---|---|
| **Chrome** | 133+ (Feb 4, 2025) | Shipped |
| **Edge** | 133+ (mid-Feb 2025) | Shipped |
| **Firefox** | 149+ (verify ship date) | Shipped |
| **Safari Desktop** | 26.3 and earlier | **Not shipped** |
| **Safari iOS** | 26.5 and earlier | **Not shipped** |
| **Opera** | Tracks Chromium | Shipped |
| **Samsung Internet** | Tracks Chromium with lag | Pending |

caniuse global usage: ~72% as of April 2026 — Chrome's ubiquity carries it over the line, but cross-browser is incomplete.

## At our baseline

Our baseline is **Chromium 125+ / Safari 17.4+ / Firefox 129+** (April 2024 floor).

| Cell | Native `popover="hint"`? |
|---|---|
| Chrome 125–132 | **No** — predates the Feb 2025 ship |
| Chrome 133+ | Yes |
| Edge 125–132 | No |
| Edge 133+ | Yes |
| Firefox 129–148 | **No** |
| Firefox 149+ | Yes |
| Safari 17.4–26.5 | **No** |

Conclusion: at our baseline, `popover="hint"` is **not cross-browser**. Use it as a progressive enhancement, not a primary mechanism.

## Fallback pattern

The HTML parser treats unknown attribute values as the attribute's `invalidStateDefault`, which for `popover` is the **Auto state**. So:

```html
<div id="tooltip" popover="hint">…</div>
```

In Chrome 133+ / Edge 133+ / Firefox 149+: `hint` semantics — does not dismiss open auto popovers.
In Safari 17.4+, Chrome ≤ 132, Firefox ≤ 148: parsed as `auto` — light-dismissible, but **does** dismiss other open auto popovers.

This may be acceptable, depending on your design. For tooltips on standalone buttons, it's fine — there usually isn't an open `auto` popover for the tooltip to fight with. For tooltips that overlap menus or dropdowns (the canonical `hint` use case), the fallback degrades to a worse experience: showing the tooltip closes the menu.

If your design requires the non-dismissive tooltip behavior across all engines, two paths:

### Option A: Detect support and gate the feature

```js
const supportsHint = (() => {
  const probe = document.createElement('div');
  probe.setAttribute('popover', 'hint');
  return probe.popover === 'hint';
})();

if (!supportsHint) {
  // Don't show tooltip at all if the open menu would be dismissed;
  // OR upgrade to popover="manual" with explicit dismiss logic.
}
```

`HTMLElement.popover` reflects the parsed state; a non-supporting browser returns `"auto"` instead of `"hint"`, allowing reliable detection.

### Option B: Use the OddBird `@oddbird/popover-polyfill` v0.6+

OddBird's polyfill ([github.com/oddbird/popover-polyfill](https://github.com/oddbird/popover-polyfill), BSD-3-Clause) added `popover=hint` support in v0.6.0 (issue [#227](https://github.com/oddbird/popover-polyfill/issues/227) closed via PR #240, ~Q1 2025). The polyfill is a no-op when native popover is fully supported (which it is across our entire baseline) — but a `hint`-aware polyfill can be force-applied to provide consistent semantics.

Trade-off: the polyfill is now overriding native `popover`, including any non-hint popovers in the page, with a JS implementation. Bundle weight (~3KB), runtime cost (event-listener overhead per popover), and behavior parity are all considerations.

For most teams, **Option A's detect-and-degrade-gracefully** is the right answer. Reserve Option B for design systems where the non-dismissive tooltip is load-bearing UX.

### Option C: Stick to `popover="auto"` and live with the dismissal

If your tooltips are simple, transient, and don't need to coexist with open menus, just use `popover="auto"`. This is the most boring and most reliable answer. Many UIs don't actually need the `hint` semantics — they were just over-specified.

## Why `hint` was added at all

The Open UI Community Group ([open-ui.org/components/popover.research-survey.explainer/](https://open-ui.org/components/popover.research-survey.explainer/)) and the Chrome team identified that **tooltips and hovercards** were a category of overlay that didn't fit cleanly into `auto` or `manual`:

- `auto` was wrong because tooltips don't *replace* menus — they sit alongside.
- `manual` was wrong because tooltips need light dismiss when the user clicks elsewhere; manual gives up that affordance.

The solution was a third type that combines `auto`'s light-dismiss with selective non-replacement of other `auto` popovers. Spec discussion is in WHATWG HTML PR [#9778](https://github.com/whatwg/html/pull/9778).

## Cross-references

- `popovertarget-vs-showpopover.md` — declarative vs. programmatic API; the `popovertarget` attribute works identically for `hint` as for `auto`/`manual`.
- `popover-vs-dialog-toplayer.md` — `hint` introduces a different stacking rule but the top-layer mechanics still apply: insertion-order paint, no z-index inside top layer.
- `../meta/the-modern-baseline.md` — `popover="hint"` is on the "do polyfill candidate" cheat sheet at this baseline.
- `../css-polyfills-and-shims/popover-polyfill.md` — when forcing the OddBird polyfill makes sense.
