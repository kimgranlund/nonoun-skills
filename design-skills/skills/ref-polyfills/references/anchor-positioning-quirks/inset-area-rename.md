---
date: 2026-04-27
coverage: extended
peers:
  - ../meta/the-modern-baseline.md
  - ../anchor-positioning-quirks/safari-26-anchor-shipped.md
  - ../anchor-positioning-quirks/firefox-147-anchor-shipped.md
  - ../anchor-positioning-quirks/popover-margins-interaction.md
  - ../css-polyfills-and-shims/anchor-positioning-polyfill.md
primary_sources:
  - https://github.com/mdn/content/issues/34893 — MDN tracking issue for the rename
  - https://developer.chrome.com/blog/anchor-syntax-changes — Chrome team's "Anchor positioning syntax changes" blog
  - https://developer.chrome.com/release-notes/129 — Chrome 129 release notes
  - https://developer.chrome.com/release-notes/131 — Chrome 131 release notes (where inset-area was removed)
  - https://developer.mozilla.org/en-US/docs/Web/CSS/position-area — MDN reference for the renamed property
  - https://github.com/w3c/csswg-drafts/issues/10209 — CSSWG resolution thread for the rename
---

# `inset-area` → `position-area` — the Chrome 129 rename

If you read an anchor-positioning tutorial published before October 2024 and copy-paste the CSS, it will not work in any current browser. The placement property was renamed mid-shipping cycle in Chrome, and every other engine adopted only the new name. This file is the canonical record of the rename window so the skill can correct stale tutorials on contact.

## Timeline (verified)

| Chrome version | Date | `inset-area` | `position-area` | Notes |
|---|---|---|---|---|
| **Chrome 125** | May 14, 2024 | Accepted | Not recognized | First ship of CSS Anchor Positioning. The placement property shipped under the original name `inset-area`. |
| **Chrome 128** | August 27, 2024 | Accepted | Not recognized | Last release with `inset-area` as the only name. (`position-try-options` was renamed to `position-try-fallbacks` in this release — separate rename, same syntax-changes wave.) |
| **Chrome 129** | September 17, 2024 | Accepted (deprecated) | **Accepted** | Both names work. The rename ships per the [CSSWG resolution](https://github.com/w3c/csswg-drafts/issues/10209). Chrome team's [Anchor positioning syntax changes](https://developer.chrome.com/blog/anchor-syntax-changes) post documents the migration. |
| **Chrome 130** | October 15, 2024 | Accepted (deprecated) | Accepted | Both names continue to work — backwards-compatibility window. |
| **Chrome 131** | November 12, 2024 | **Removed** | Accepted | Last Chrome release that touched `inset-area`. The Chrome 131 release notes' Deprecations and removals section: *"With the CSS Working Group resolution on renaming the `inset-area` property to `position-area`, this removal cleans up the implementation in Chromium for a standards compliant feature."* From this point on, Chrome silently drops `inset-area` declarations as unknown CSS. |
| **Chrome 132+** | January 14, 2025 onward | Not recognized | Accepted | `position-area` is the only legal name. |

The window where both names worked is **Chrome 129–130** (about two months of stable releases). Chrome 131 removed `inset-area` outright; it was never a long-lived alias.

## Why the CSSWG renamed it

From the resolution discussion (CSSWG draft #10209) and the Chrome team's syntax-changes post: the prefix `inset-` suggested kinship with the established `inset` shorthand (top/right/bottom/left). It isn't related — `inset-area` sets which *region* relative to an anchor a positioned element occupies, which then drives implicit insets. The new prefix `position-` matches the property's semantic neighbors (`position-anchor`, `position-try-fallbacks`) and avoids implying composition with `inset`.

Same wave, the at-rule and property pair `position-try-options` was renamed to `position-try-fallbacks` to make explicit that the entries are fallbacks, not alternatives evaluated in parallel. Chrome 128 already accepted only the new name; the migration there had no overlap window.

## What the migration looks like

Plain search-and-replace of the property name. Every value is identical:

```css
/* before — pre-Chrome 129 tutorials */
.tooltip {
  position: absolute;
  position-anchor: --button;
  inset-area: bottom;
}

/* after — current-canonical */
.tooltip {
  position: absolute;
  position-anchor: --button;
  position-area: bottom;
}
```

For `position-try` blocks, the same property rename applies — and the at-rule name `position-try-options` itself was replaced with `position-try-fallbacks`:

```css
/* before */
.tooltip {
  position-try-options: --flip-bottom, --flip-left;
}
@position-try --flip-bottom { inset-area: top; }

/* after */
.tooltip {
  position-try-fallbacks: --flip-bottom, --flip-left;
}
@position-try --flip-bottom { position-area: top; }
```

The `inset-area()` *functional* form inside `position-try-fallbacks` (e.g. `position-try-fallbacks: inset-area(top)`) was also dropped in Chrome 129. Use the bare keyword instead: `position-try-fallbacks: top`.

## Other engines

The rename happened during the Chromium-only era. Safari and Firefox shipped support after the resolution had landed, so they never had `inset-area`:

- **Safari 26.0** (September 15, 2025) — shipped with `position-area`. No `inset-area` codepath ever existed in WebKit. See `safari-26-anchor-shipped.md`.
- **Firefox 147** (January 13, 2026) — enabled-by-default with `position-area`. Earlier flagged builds (Firefox 145–146 with `layout.css.anchor-positioning.enabled`) also used `position-area` — no Firefox release ever shipped `inset-area`. See `firefox-147-anchor-shipped.md`.

This means: any browser that ships anchor positioning today, *other than* Chrome 129 and 130, accepts only `position-area`. The dual-name window was strictly Chromium-internal and lasted ~two months.

## Why this still bites in 2026

The first wave of practitioner content about CSS Anchor Positioning was written in May–September 2024 — before the rename. Many of those posts have not been updated. When the skill is asked "why isn't `inset-area: bottom` working?" the cause is almost always:

1. The author copied from a 2024 blog post (Smashing Magazine, CSS-Tricks, web.dev, dev.to, Ahmad Shadeed, etc. — most have either been updated or are stale).
2. Their target browser is anything other than Chrome 129 or Chrome 130 — i.e. Chrome 131+ (the dominant Chromium installed base), Safari 26+, or Firefox 147+.

The fix is mechanical: replace `inset-area` with `position-area` and `inset-area(...)` with the bare keyword form.

## Detection — is the codebase still using `inset-area`?

Grep is sufficient — there is no legitimate use of the old name at this baseline:

```bash
grep -rn "inset-area" --include="*.css" --include="*.scss" --include="*.html" --include="*.tsx" --include="*.jsx" .
```

LightningCSS, PostCSS, and modern Stylelint configurations do not transform `inset-area` to `position-area` — there is no equivalent to the autoprefixer alias for this property. Authoring is the only fix point.

If you must keep both names temporarily for a heterogenous-Chrome audience (Chrome 130 still in long-tail enterprise installs), declare both:

```css
.tooltip {
  inset-area: bottom;       /* dropped silently by Chrome 131+ */
  position-area: bottom;    /* the canonical name */
}
```

Chrome 131+ ignores the first declaration; Chrome 129–130 honours either. This is belt-and-suspenders and almost never necessary at our baseline.

## Cross-references

- For Safari's anchor-positioning ship and the `@position-try` Safari 18.4 split: `safari-26-anchor-shipped.md`.
- For Firefox 147's enable-by-default: `firefox-147-anchor-shipped.md`.
- For UA-style margin interference between popover and `position-area`: `popover-margins-interaction.md`.
- For the OddBird anchor-positioning polyfill (used for Safari 17.4–25 and Firefox 129–146): `../css-polyfills-and-shims/anchor-positioning-polyfill.md`.
