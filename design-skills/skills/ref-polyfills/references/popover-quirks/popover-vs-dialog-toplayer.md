---
date: 2026-04-27
coverage: esoteric
peers:
  - ../popover-quirks/ios-safari-light-dismiss.md
  - ../popover-quirks/safari-focus-inputs.md
  - ../popover-quirks/safari-184-tab-hang.md
  - ../popover-quirks/popover-hint-chromium-only.md
primary_sources:
  - https://github.com/whatwg/html/issues/9936 — WHATWG issue "A popover on top of a modal dialog should be interactable" (filed Nov 16, 2023, OPEN)
  - https://github.com/whatwg/html/issues/11195 — WHATWG issue "A modal dialog should not make inert top layer elements above itself" (closed as duplicate of #9936)
  - https://github.com/whatwg/html/issues/9998 — WHATWG issue "Opening a dialog as modal, nested inside a popover, causes the whole page to go inert"
  - https://github.com/whatwg/html/issues/10811 — "Should non-modal top layer elements that come after modal dialogs also escape inertness?"
  - https://www.htmhell.dev/adventcalendar/2025/1/ — "Top layer troubles: popover vs. dialog" (HTMHell advent calendar 2025)
  - https://benfrain.com/failing-with-multiple-dialog-elements-understanding-the-top-layer-and-popovers/ — Ben Frain explainer on top-layer behavior
  - https://html.spec.whatwg.org/multipage/popover.html — HTML spec §6.12 Popover attribute and top-layer
  - https://drafts.csswg.org/css-position-4/ — CSS Position 4 (top-layer specification)
  - https://hidde.blog/dialog-modal-popover-differences/ — Hidde de Vries on dialog/popover differences
  - https://adrianroselli.com/2023/05/brief-note-on-popovers-with-dialogs.html — Adrian Roselli on popover-with-dialog accessibility
---

# Popover inside modal dialog is inerted; z-index has no effect inside top-layer

> **Status at 2026-04-27.** This is **two related spec-level constraints**, not browser bugs. Both are universal across all engines (Chrome, Safari, Firefox). The relevant WHATWG issue [#9936](https://github.com/whatwg/html/issues/9936) is **open** since November 2023 with no consensus solution. The skill stance: don't nest popovers inside modal dialogs, and don't try to fix top-layer ordering with z-index.

## Two distinct gotchas

### Gotcha 1: a popover rendered while a modal `<dialog>` is open is inerted

When `<dialog>.showModal()` is called, the dialog enters the [top layer](https://drafts.csswg.org/css-position-4/#top-layer) and the rest of the document — everything **outside** the dialog's subtree — becomes [inert](https://html.spec.whatwg.org/multipage/interaction.html#inert). Inert means: not focusable, not click-targetable, ignored by assistive technology.

Now suppose you open a `<element popover>` from elsewhere in the document — say, a toast notification, a tooltip overlay, or a deeply nested popover that wasn't authored as a child of the dialog. The popover element itself enters the top layer and renders **visually above** the dialog (top-layer elements stack in insertion order; the later-inserted popover paints on top). But because its DOM position is **outside** the dialog's subtree, it inherits inertness from the modal dialog's blocking effect.

Result: the user sees a popover floating over a dialog, but cannot click it, focus it, or interact with it in any way. It is purely decorative.

This is **not a bug**. The HTML spec ([§6.12](https://html.spec.whatwg.org/multipage/popover.html) and the inertness algorithm) explicitly defines this behavior. WHATWG issue [#9936](https://github.com/whatwg/html/issues/9936) (filed November 2023 by Ben Frain, **still open** April 2026) proposes that top-layer elements that visually sit above the modal dialog should escape inertness. No engine has shipped a change. The spec text remains: modal dialog inerts everything not in its subtree, full stop.

### Gotcha 2: z-index has no effect inside the top layer

The CSS top layer is a separate layering mechanism above all stacking contexts in the regular page flow. Per [CSS Position 4 §3](https://drafts.csswg.org/css-position-4/#top-layer):

> _The top layer is a special layer that elements are rendered into, on top of all other content. ... Elements in the top layer are rendered in their insertion order._

`z-index` is a stacking-context property. Once an element is promoted to the top layer (via `<dialog showModal()>`, `popover`, or fullscreen API), its position in the top-layer stack is determined **only** by its insertion order, not by `z-index`. Setting `z-index: 99999` on a popover does nothing relative to another popover or modal dialog also in the top layer.

This catches developers who try to "force" a popover above a modal dialog via z-index. It will not work. The popover will paint above the modal dialog (because it was inserted later — top-layer stacks LIFO-by-insertion), but it will be inerted (gotcha 1).

The interaction: **z-index affects nothing in the top layer; insertion order affects paint order; modal dialog blocking affects interactivity.** Three separate mechanisms, often confused.

## Affected engines

| Engine | Behavior |
|---|---|
| **Chromium 114+** | Spec-compliant: popovers outside modal dialog subtree are inerted. |
| **Safari 17+** | Spec-compliant. |
| **Firefox 125+** | Spec-compliant. |

All engines agree. This is a spec-level design choice, not an interop gap.

## Reproduction

```html
<!doctype html>

<dialog id="d">
  <h2>Modal dialog</h2>
  <button id="trigger" popovertarget="m">Open menu</button>
  <button id="closeDialog">Close dialog</button>
</dialog>

<!-- Popover lives OUTSIDE the dialog -->
<div id="m" popover style="padding: 1rem; background: white; border: 1px solid;">
  <button>Item 1</button>
  <button>Item 2</button>
</div>

<button id="openDialog">Open dialog</button>

<script>
  document.querySelector('#openDialog').addEventListener('click', () => {
    document.querySelector('#d').showModal();
  });
  document.querySelector('#closeDialog').addEventListener('click', () => {
    document.querySelector('#d').close();
  });
</script>
```

**Sequence:**
1. Click "Open dialog" — modal opens, page outside is inerted.
2. Click "Open menu" inside the dialog — `popovertarget="m"` triggers `#m`'s `.showPopover()`.
3. `#m` paints above the dialog (top-layer LIFO insertion).
4. `#m`'s buttons appear visible and styled.
5. Try to click "Item 1" — **nothing happens**. Click is ignored. Focus cannot reach it via Tab. VoiceOver does not announce it.

The popover is rendered but inert.

**Now try the alternative — popover inside the dialog subtree:**

```html
<dialog id="d">
  <button popovertarget="m">Open menu</button>
  <div id="m" popover>...</div>  <!-- Inside dialog, not outside -->
</dialog>
```

This works. The popover, being inside the dialog's subtree, is not inerted by the dialog's modal blocking. It paints in the top layer above the dialog and is interactable.

## Workarounds

Three options. The first is the spec-aligned answer; the others are escape hatches when you can't restructure.

### 1. Place the popover inside the dialog's subtree (recommended)

If the popover is conceptually part of the dialog's UI — a dropdown inside a form, a tooltip on a dialog button — author it as a descendant of the dialog. The DOM hierarchy and the visual hierarchy match; the inertness logic does the right thing.

```html
<dialog id="d">
  <form>
    <button popovertarget="filters">Filters</button>
    <div id="filters" popover>
      <label><input type="checkbox"> Apply filter A</label>
    </div>
  </form>
</dialog>
```

### 2. Use a non-modal `<dialog>` instead of `showModal()`

`<dialog>.show()` (without "Modal") makes the dialog a top-layer element **without** inerting the rest of the page. Background popovers remain interactive.

```html
<dialog id="d">...</dialog>

<script>
  document.querySelector('#d').show();   // not showModal()
</script>
```

Trade-off: you lose modality. The user can interact with content outside the dialog. For toast-style or notification dialogs this is appropriate; for "you must answer this question before continuing" prompts, it isn't.

### 3. Don't open popovers while a modal dialog is open

Coordinate state: close any open popovers before calling `showModal()`. If an event would normally open a popover, intercept and either route through the dialog or queue it for after dialog close.

```js
const dialog = document.querySelector('#d');
const popover = document.querySelector('#m');

function openDialogSafely() {
  if (popover.matches(':popover-open')) {
    popover.hidePopover();
  }
  dialog.showModal();
}
```

This is sometimes the cleanest answer: modal dialog and popover are competing for the user's attention, and the design probably should pick one.

### What NOT to do

- **Don't apply `z-index: 999999` to the popover.** It will not change the inert state. The popover is already in the top layer paint-wise; the issue is interactivity, not paint order.
- **Don't set `inert="false"` on the popover.** `inert` doesn't have a "force-uninert" mode; the modal dialog's blocking inheritance is computed separately from the `inert` attribute.
- **Don't dynamically move the popover into the dialog at the moment of opening** unless you also handle DOM ordering, focus restoration, and any references to the popover element from elsewhere in your app. It's invasive surgery.

## Z-index inside top-layer — practical implications

Some patterns where z-index seems like the answer but isn't:

- **Two open popovers, you want one above the other.** They stack by insertion order. Open popover A first, then B; B paints above A. There's no way to flip that with z-index.
- **A popover above a fullscreen-API element.** Both are in the top layer; ordering is by entry order. Fullscreen API adds entries; popovers add entries; whichever is added last wins paint order.
- **Custom dropdown that you implemented with `position: fixed; z-index: 99999`.** This dropdown is **not** in the top layer, just in a deeply-stacked stacking context. It will paint **below** any top-layer element (modal, popover, fullscreen) regardless of its z-index. To reach the top layer, use `<dialog>.show()`, `<element popover>`, or `requestFullscreen()`.

## Cross-references

- `popover-hint-chromium-only.md` — `popover="hint"` introduces a third top-layer ordering rule (hints don't close auto popovers). Relevant for layered UI.
- `ios-safari-light-dismiss.md`, `safari-focus-inputs.md`, `safari-184-tab-hang.md` — engine-specific bugs on top of the spec-level constraints documented here.
- `../anchor-positioning-quirks/popover-margins-interaction.md` — popover UA-style margins also interact with anchor positioning; combined with top-layer behavior, popovers have a complex layout story.
