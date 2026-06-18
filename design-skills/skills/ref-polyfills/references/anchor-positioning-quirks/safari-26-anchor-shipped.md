---
date: 2026-04-27
coverage: extended
peers:
  - ../meta/the-modern-baseline.md
  - ../anchor-positioning-quirks/inset-area-rename.md
  - ../anchor-positioning-quirks/firefox-147-anchor-shipped.md
  - ../anchor-positioning-quirks/default-anchor-resolution.md
  - ../css-polyfills-and-shims/anchor-positioning-polyfill.md
primary_sources:
  - https://webkit.org/blog/17333/webkit-features-in-safari-26-0/ — Safari 26.0 release post (Sept 15, 2025)
  - https://webkit.org/blog/17541/webkit-features-for-safari-26-1/ — Safari 26.1 release post
  - https://webkit.org/blog/17640/webkit-features-for-safari-26-2/ — Safari 26.2 release post
  - https://www.oddbird.net/2025/10/13/anchor-position-area-update/ — OddBird Fall 2025 anchor-positioning roundup
  - https://caniuse.com/css-anchor-positioning — caniuse browser support data
  - https://caniuse.com/mdn-css_at-rules_position-try — caniuse data for `@position-try`
  - https://web-standards.dev/news/2025/09/safari-26/ — Web Standards summary of Safari 26 features
  - https://blogs.igalia.com/plampe/contributing-to-css-anchor-positioning-in-webkit/ — Igalia post on WebKit anchor-positioning work
---

# Safari 26 shipped CSS Anchor Positioning

Safari 26.0 (September 15, 2025) was the first Apple-platform release with CSS Anchor Positioning enabled. This file is the canonical record of what shipped, what was added in 26.1 / 26.2 follow-ups, and the polyfill window that still applies at our baseline (Safari 17.4+).

## What shipped, and when

| Safari version | Date | Anchor positioning support |
|---|---|---|
| **Safari 17.4** (our baseline floor) | March 5, 2024 | None |
| Safari 17.x – 18.1 | through October 2024 | None |
| Safari 18.2 | December 11, 2024 | Still none — search results for "Safari 18.2 anchor positioning" turn up nothing in WebKit's [18.2 release post](https://webkit.org/blog/16301/webkit-features-in-safari-18-2/). Anchor positioning did not arrive in any 18.x release. |
| Safari 18.4 | March 31, 2025 | Still none |
| **Safari 26.0** | **September 15, 2025** | **First Apple-platform support.** Ships `anchor-name`, `position-anchor`, `position-area`, the `anchor()` function, the `anchor-size()` function, the `position-try-fallbacks` property, and the `@position-try` at-rule. Per the WebKit 26.0 features post: "anchor positioning is a new layout mechanism for anchoring one element to another on the web." Implicit-anchor support for pseudo-elements with anchor functions also shipped with the first beta. |
| **Safari 26.1** | November 2025 | A dozen anchor-positioning fixes. Notable: *"Fixed an issue where anchor-positioned elements failed to update their position when the default anchor changed."* Also fixes for fragmented multi-column flows, scrolling behavior, container-query interaction, and several positioning edge cases. The browser now remembers the last successful `@position-try` fallback to reduce layout jumps. |
| Safari 26.2 | December 2025 | Further refinements — see WebKit's [26.2 features post](https://webkit.org/blog/17640/webkit-features-for-safari-26-2/). |

WebKit shipped the new property name `position-area` directly, with no `inset-area` legacy. The Chrome 129 rename had landed before Safari started its public-shipping work, so iOS and macOS users never had to migrate. See `inset-area-rename.md` for the Chrome timeline.

## Implementation note: `@position-try` is part of 26.0

A common piece of stale information from early-2025 Safari Tech Preview coverage: "Safari has anchor positioning but not `@position-try`, so fallback positioning doesn't work." That was true for Safari Tech Preview builds and (briefly) for some 18.x previews — but it does NOT describe Safari 26.0. WebKit's 26.0 release post explicitly mentions `position-try` as part of the shipped set, and the OddBird Fall 2025 roundup confirms that all four pillars — anchor naming, anchor functions, `position-area`, and fallback positioning — landed together in 26.0.

If a tutorial or article claims "Safari ships anchor positioning but not `@position-try`," verify the date. Pre-September 2025 commentary is stale.

## Why this matters at our baseline (Safari 17.4+)

Our skill's baseline floor is Safari 17.4 (March 5, 2024) — eighteen months *before* anchor positioning shipped in Safari 26.0. The polyfill window at this baseline is therefore wide:

| Safari segment | At April 2026 | Native anchor positioning? | Polyfill needed? |
|---|---|---|---|
| Safari 17.4 – 17.6 | Long-tail iOS 17 holdouts | No | **Yes** |
| Safari 18.0 – 18.6 | iOS 18 / macOS 15 — large installed base before Sept 2025 | No | **Yes** |
| Safari 26.0+ | iOS 26 / macOS Tahoe / visionOS 26 — auto-update target | Yes | No |

The polyfill window is **Safari 17.4 → 25.x** — fifteen months of Safari versions, from March 5, 2024 to September 15, 2025. That covers the entire iOS 17 + iOS 18 cycles. Many users are not yet on iOS 26 by April 2026; the iOS 18 long tail is real, especially on devices that didn't get iOS 26 (older iPads, iPhone X / 8-series).

If your audience has any meaningful iOS 17–18 share, **anchor positioning needs the OddBird polyfill or a CSS fallback**. See `../css-polyfills-and-shims/anchor-positioning-polyfill.md`.

If your audience is heavy macOS Safari and skews recent, the polyfill window narrows substantially — Safari 26 auto-updates fast on managed macOS installs.

## What "the polyfill window" actually means

OddBird's `@oddbird/css-anchor-positioning` polyfill works by:

1. Scanning your stylesheet for anchor-positioning declarations.
2. Computing positions in JavaScript at layout time.
3. Updating positions on scroll, resize, and mutation.

It targets the new property names (`position-area`, `position-anchor`, `anchor()`, `anchor-size()`, `@position-try`, `position-try-fallbacks`) — i.e. the post-rename canonical surface. Ship the polyfill via `<script>` tag at the bottom of `<body>` and feature-detect:

```html
<script>
  if (!CSS.supports('anchor-name', '--x')) {
    import('https://your-cdn/css-anchor-positioning/dist/css-anchor-positioning.min.js');
    // or — better — self-host and import from your origin
  }
</script>
```

The feature-detect short-circuits download on Safari 26+, Chrome 125+, and Firefox 147+, so the polyfill payload is delivered only to Safari 17.4–25.x and Firefox 129–146 (and any other below-baseline browsers).

## A note on Safari 26.1's "default anchor" fix

Safari 26.0 shipped with a known issue where anchor-positioned elements did not update their layout when the default anchor (the element referenced by `position-anchor`) changed. WebKit 26.1 release notes log: *"Fixed an issue where anchor-positioned elements failed to update their position when the default anchor changed."* This is related but distinct from WebKit Bug 283295 (default-anchor *resolution*, see `default-anchor-resolution.md`); the 26.1 fix targets a *recomputation* path, not an initial-resolution path.

If you developed against Safari 26.0 and saw popovers freezing in their first-painted position when the anchor moved, that bug is fixed in 26.1 with no author code change.

## Cross-references

- For the `inset-area` → `position-area` rename history: `inset-area-rename.md`.
- For Firefox's anchor-positioning ship in v147: `firefox-147-anchor-shipped.md`.
- For the OddBird polyfill: `../css-polyfills-and-shims/anchor-positioning-polyfill.md`.
- For the implicit-default-anchor edge case (WebKit Bug 283295): `default-anchor-resolution.md`.
- For the popover UA-style margin interaction: `popover-margins-interaction.md`.
