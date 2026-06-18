---
date: 2026-04-27
coverage: esoteric
peers:
  - ../meta/the-modern-baseline.md
  - ../anchor-positioning-quirks/inset-area-rename.md
  - ../anchor-positioning-quirks/safari-26-anchor-shipped.md
  - ../anchor-positioning-quirks/firefox-147-anchor-shipped.md
  - ../popover-quirks/popover-defaults.md
primary_sources:
  - https://github.com/w3c/csswg-drafts/issues/10258 — CSSWG Issue 10258 — "[css-anchor-position][other] Handling popover default styles"
  - https://www.oddbird.net/2025/10/13/anchor-position-area-update/ — OddBird Fall 2025 anchor-positioning roundup (the resolved direction)
  - https://hidde.blog/positioning-anchored-popovers/ — Hidde de Vries — Positioning anchored popovers
  - https://matuzo.at/blog/2026/better-defaults-for-popovers — Manuel Matuzović — Better defaults for popovers (2026)
  - https://developer.mozilla.org/en-US/docs/Web/API/Popover_API/Using — MDN: Using the Popover API
  - https://github.com/whatwg/html/issues/9311 — WHATWG HTML Issue 9311 — Popover ⨯ Anchor Positioning interaction
---

# UA-style popover margins fight `position-area`

The HTML spec defines a UA stylesheet for `[popover]` elements that includes `inset: 0`, `place-self: center`, and `margin: auto`. Those rules exist to center modal popovers in the viewport when no positioning is specified. They actively interfere with anchor-positioned popovers — and the interference is engine-agnostic, because every browser ships the same UA stylesheet. This file is the canonical record of the bug, the CSSWG resolution, and the workaround that holds at this baseline.

## The conflict

The HTML-spec UA rule for `[popover]:not(:popover-open)` and friends includes (paraphrased — exact text in the WHATWG HTML rendering section):

```css
[popover] {
  position: fixed;
  inset: 0;
  width: fit-content;
  height: fit-content;
  margin: auto;
  /* + other modal-centering rules */
}
```

The `inset: 0` + `margin: auto` combination is the classic "absolute-positioned, full-bounds, auto-margin" centering trick. It centers the popover in the viewport when no other positioning is given.

When you try to anchor-position the same popover:

```html
<button popovertarget="p" style="anchor-name: --btn">Open</button>
<div id="p" popover style="
  position-anchor: --btn;
  position-area: bottom;
">…</div>
```

The `position-area: bottom` declaration *should* place the popover beneath the button. Instead, on every browser that ships anchor positioning, the popover renders offset — sometimes by a few pixels, sometimes dramatically — because the UA-supplied `inset: 0` and `margin: auto` are still in effect. The author's `position-area` is fighting `inset: 0`, and the auto margins distribute leftover space.

Tab Atkins (CSSWG editor) summarized in [csswg-drafts #10258](https://github.com/w3c/csswg-drafts/issues/10258): *"Both of them end up interacting with the default `inset: 0;`"* — the simplest anchor-positioning attempt collides with the UA rule.

## The CSSWG resolution (Fall 2025)

The CSSWG considered two paths and chose the simpler one:

1. **Introduce a new `dialog` value** for `align-self` / `justify-self` that means "center if no anchor positioning is set, otherwise be normal." Rejected — too narrow.
2. **Disable `margin: auto` on popovers when `position-area` is set.** Adopted. The UA stylesheet effectively becomes "if anchor positioning is in use, drop the modal-centering margins."

The OddBird Fall 2025 roundup ([oddbird.net/2025/10/13](https://www.oddbird.net/2025/10/13/anchor-position-area-update/)) records the resolution: *"Instead of a dialog value, `margins: auto` will be disabled when a `position-area` is set."* The plan is to update HTML's UA stylesheet rules and update browser implementations accordingly.

This is good news for the future. It is not yet shipped. As of April 2026, all three engines still ship the legacy UA-stylesheet behavior — author CSS must continue to override.

## Cross-engine — yes, all three

Because the bug originates in the UA stylesheet (which every engine ships from the HTML spec), the symptom appears in:

- **Chrome / Edge / Chromium derivatives** — Chrome 125+, every version since ship.
- **Safari 26+** — the bug is present in WebKit 26.0 / 26.1 / 26.2 (verified via the OddBird Fall 2025 testing).
- **Firefox 147+** — also present (Mozilla ships the same UA-stylesheet pattern).

This is one of the few anchor-positioning quirks that is *not* engine-specific. Practitioners who first hit it on Chrome and then assumed "this works correctly on Safari" should re-test — it doesn't.

## The author-side workaround (canonical)

Reset the conflicting properties explicitly on any anchor-positioned popover:

```css
[popover].anchored {
  /* Drop the UA stylesheet's modal-centering rules. */
  inset: auto;
  margin: 0;

  /* Now your anchor positioning takes effect cleanly. */
  position-anchor: --btn;
  position-area: bottom;
}
```

`margin: 0` is sometimes shown as `margin: unset` in older write-ups (Hidde de Vries' [Positioning anchored popovers](https://hidde.blog/positioning-anchored-popovers/) post used `margin: unset`). Both work — `margin: 0` is more explicit; `margin: unset` lets cascade contributions remain (rare, since UA is usually the only contributor). Pick `margin: 0` for the floor; switch to `unset` only if you have a deliberate non-UA cascade you want to preserve.

`inset: auto` is the more important reset. Without it, `inset: 0` from the UA stylesheet pins the popover to all four viewport edges, which can produce surprising results (huge popovers, scroll containers behaving weirdly). With `inset: auto`, the anchor-positioning algorithm starts from a clean slate.

## Belt-and-suspenders — also reset `width` / `height`

The full UA stylesheet includes `width: fit-content` and `height: fit-content`, which are usually fine but can interact awkwardly with `position-area: span-x` values that imply a width. If you observe sizing weirdness, reset:

```css
[popover].anchored {
  inset: auto;
  margin: 0;
  width: auto;
  height: auto;

  position-anchor: --btn;
  position-area: bottom span-right;
}
```

Most popovers do not need this, but it's a useful diagnostic to know.

## Don't wait for the CSSWG fix

The CSSWG resolution (disable `margin: auto` when `position-area` is set) is in-flight in HTML / WHATWG specs, and browsers will eventually update their UA stylesheets to match. As of April 2026, this has not shipped in any release-channel browser. Even when it does ship, the rollout will be staggered across Chrome, Safari, and Firefox over months — and your codebase will still have to support pre-fix versions for some time.

The recommendation is to keep the explicit `inset: auto; margin: 0` reset in author CSS indefinitely. It costs ~20 bytes per popover-with-anchor and removes the entire class of "popover renders 8px off" bugs. The reset is harmless after the UA-stylesheet fix lands.

## Manuel Matuzović's "Better defaults for popovers" (2026)

Manuel Matuzović's January 2026 post [Better defaults for popovers](https://matuzo.at/blog/2026/better-defaults-for-popovers) catalogs the broader set of UA-stylesheet annoyances on `[popover]`. Beyond `margin: auto` colliding with anchor positioning, the post flags:

- `width: fit-content` interacting awkwardly with `max-inline-size` constraints.
- Default `padding` (engine-dependent) showing up unexpectedly inside popovers.
- `border` being ~1px in some UAs and 0 in others.

The takeaway, mirrored in this skill: do not rely on the UA stylesheet to be reasonable for popovers. Reset what you care about. The defaults are calibrated for non-anchored modal centering — anything else fights them.

## Reproduction recipe (paste into a blank file)

```html
<!doctype html>
<style>
  body { margin: 0; padding: 2rem; }
  button { anchor-name: --btn; }
  /* Comment out this rule to see the bug: */
  [popover] {
    inset: auto;
    margin: 0;
  }
  [popover] {
    position-anchor: --btn;
    position-area: bottom;
    background: tomato;
    padding: 0.5rem 1rem;
  }
</style>
<button popovertarget="p">Open</button>
<div id="p" popover>Anchored popover</div>
```

With the reset rule active, the popover sits cleanly under the button. Comment out the reset rule and the popover appears in the centre of the viewport (UA `inset: 0; margin: auto;`), ignoring `position-area`.

## Cross-references

- For the inset-area → position-area rename history (so the example syntax above is canonical): `inset-area-rename.md`.
- For Safari's anchor-positioning ship including the `@position-try` arrival in 26.0: `safari-26-anchor-shipped.md`.
- For Firefox's enable-by-default in 147: `firefox-147-anchor-shipped.md`.
- For broader popover quirks (light-dismiss, focus, top-layer issues): `../popover-quirks/`.
- The CSSWG issue: https://github.com/w3c/csswg-drafts/issues/10258.
- The HTML interop issue: https://github.com/whatwg/html/issues/9311.
