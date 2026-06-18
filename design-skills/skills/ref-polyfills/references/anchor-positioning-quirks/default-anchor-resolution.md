---
date: 2026-04-27
coverage: esoteric
peers:
  - ../meta/the-modern-baseline.md
  - ../anchor-positioning-quirks/safari-26-anchor-shipped.md
  - ../anchor-positioning-quirks/popover-margins-interaction.md
primary_sources:
  - https://bugs.webkit.org/show_bug.cgi?id=283295 — WebKit Bug 283295 — "[css-anchor-position-1] Fix evaluation of default anchor elements"
  - https://webkit.org/blog/17541/webkit-features-for-safari-26-1/ — Safari 26.1 release post (related fix list)
  - https://blogs.igalia.com/plampe/contributing-to-css-anchor-positioning-in-webkit/ — Igalia post on contributions to WebKit anchor positioning
  - https://drafts.csswg.org/css-anchor-position-1/ — CSS Anchor Positioning spec (default-anchor resolution algorithm)
  - https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position-anchor — MDN: position-anchor
---

# WebKit Bug 283295 — implicit default-anchor resolution

The CSS Anchor Positioning spec lets `anchor()` and `anchor-size()` work with an implicit "default anchor" — the element referenced by `position-anchor` — without requiring authors to repeat the anchor name in every function call. WebKit Bug 283295 covers a subtle hole in WebKit's default-anchor resolution path that affected early-shipping Safari builds. This file is the canonical record so the skill can recognize the symptom on contact.

## What the spec says (briefly)

For an element `E` with `position-anchor: --button`, two things are true:

1. `top: anchor(bottom)` (without the anchor name) resolves to "bottom edge of `--button`," because `--button` is `E`'s default anchor.
2. The anchor is "in scope" for any inset property that uses `anchor()` — even if no inset property actually does. Setting `position-anchor: --button` alone, without any `anchor()` call, still establishes the anchor relationship for layout (e.g. for `position-area`).

The spec algorithm: when computing layout for an anchor-positioned element, look up the element named by `position-anchor`; that's the default anchor. Don't require an `anchor()` reference in inset properties to "activate" the relationship.

## What the bug was

Per [WebKit Bug 283295](https://bugs.webkit.org/show_bug.cgi?id=283295), titled *"[css-anchor-position-1] Fix evaluation of default anchor elements"*: WebKit's resolution code "only looks for anchor references in `anchor()` and `anchor-size()`" — it did not recognize a `position-anchor` declaration on its own as enough to establish the anchor relationship.

Two specific failure cases are documented in the bug:

1. **`position-anchor` references a valid anchor, but inset properties use `anchor()` with unknown references.** The element should still be anchored to the default anchor for the purposes of `position-area` and any successful `anchor()` calls — but it wasn't.
2. **`position-anchor` is set to a valid anchor, but no inset properties use `anchor()` at all.** Same bug — the default anchor should be active for `position-area` and `@position-try` even with no `anchor()` calls in scope.

In both cases, "the resolution of anchoring is not done and therefore the anchored elements are not being linked to anchors" — the positioned element falls back to its containing block's default coordinates, not to the anchor's geometry.

## Where the symptom shows up

The most common reproduction:

```html
<button id="trigger" style="anchor-name: --btn">Open</button>
<div popover style="
  position: absolute;
  position-anchor: --btn;
  position-area: bottom;
">…</div>
```

This should anchor the popover to the button's bottom edge. On affected Safari versions, the popover positioned itself relative to the viewport / containing block instead — `position-area: bottom` evaluated against the wrong frame because the default anchor was never resolved.

The bug is `position-area`-flavoured and `@position-try`-flavoured rather than `anchor()`-flavoured. If your CSS uses `top: anchor(--btn bottom)` explicitly (with the anchor name), the resolution path that handles `anchor()` finds the reference directly and the bug doesn't trigger. The bug only matters when anchor establishment is supposed to flow through `position-anchor` alone.

## Affected versions

The bug was filed and worked against pre-stable WebKit builds. Resolution: **RESOLVED FIXED**, committed to WebKit `main` on **February 18, 2025** (commit 290534@main).

| Safari version | Default-anchor resolution behavior |
|---|---|
| Safari Tech Preview pre-Feb 2025 | Bug present |
| Safari 26.0 (Sept 15, 2025) | Fix included — WebKit 26.0's anchor positioning ship has the corrected path. |
| Safari 26.1 (Nov 2025) | Further default-anchor fix shipped (recomputation when the default anchor *changes* — distinct from initial resolution). See `safari-26-anchor-shipped.md` for the 26.1 release-note quote. |

Practical implication for the skill: **Bug 283295 itself does not affect any release-channel Safari version.** Safari 26.0 was the first stable shipped Safari with anchor positioning, and it shipped *after* the fix landed. The bug is documented here for archaeology — if a developer follows a 2025 link and wonders if it bites them, the answer is no for any Safari 26+ install.

A separate bug — [WebKit 279588](https://bugs.webkit.org/show_bug.cgi?id=279588) — covered a WebProcess crash when a popover used anchoring; also fixed before 26.0.

## Why explicitly declaring `position-anchor` is still good practice

Even though Safari 26+ resolves the default anchor correctly, keeping `position-anchor` explicit on every anchor-positioned element is the recommended posture:

- **Implicit-anchor resolution is interaction-heavy with the popover invoker mechanism.** When a popover is opened by a `popovertarget` button, the spec (and current implementations) infer an *implicit anchor relationship* between the invoker and the popover. This implicit relationship can shadow or interact with explicit `position-anchor` declarations in nuanced ways. Declaring `position-anchor` explicitly removes any ambiguity.
- **`anchor()` without an anchor name is a recent addition.** Some early-2024 Chrome content predates the unnamed `anchor()` form. Defaulting to the named form (`anchor(--btn bottom)`) is more portable across stale codebases.
- **Tooling support is friendlier with explicit names.** Lints and editor IntelliSense can verify the reference is in scope; an unnamed `anchor()` call requires the tool to follow `position-anchor` resolution itself, which most don't.

The spec-correct minimum:

```css
.popover {
  position: absolute;
  position-anchor: --btn;       /* explicit; safe across all engines */
  position-area: bottom;        /* uses the default anchor, established by position-anchor */
}
```

The implicit-anchor variant (works in Safari 26+, Chrome 125+, Firefox 147+ but historically buggy):

```css
.popover {
  position: absolute;
  /* No position-anchor — relying on popover invoker → implicit anchor inference. */
  top: anchor(bottom);          /* Which anchor? The implicit one from the popover invoker. */
}
```

The first form is the recommended floor. Use the second only when you have a clear reason and have tested across all three engines.

## What to grep for if you suspect this bug

If your team has Safari 26.0 (specifically 26.0, before 26.1's recomputation fix) and sees popovers freeze in a wrong-looking position when the anchor moves:

- Check for `position-anchor` declarations without explicit `anchor()` references in the same rule. This is the bug's most common shape.
- Add an explicit `top: anchor(<name> bottom)` (or similar) to force the resolution path that always worked.
- Confirm by setting `position-anchor: var(--anchor-name)` and watching whether the layout re-anchors correctly when `--anchor-name` changes.

For Safari 26.1+, this bug is closed; further default-anchor weirdness is more likely related to the recomputation fix or to general layout-recomputation interactions with scroll / container queries (see WebKit 26.1 release notes for the broader fix list).

## Cross-references

- For Safari 26's anchor-positioning ship and the 26.1 default-anchor recomputation fix: `safari-26-anchor-shipped.md`.
- For UA-style popover margin interference (a different bug, also surfacing as "popover in wrong place"): `popover-margins-interaction.md`.
- The bug itself: https://bugs.webkit.org/show_bug.cgi?id=283295.
