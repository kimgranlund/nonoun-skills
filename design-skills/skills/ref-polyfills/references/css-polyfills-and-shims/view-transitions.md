---
date: 2026-04-27
coverage: canonical
peers:
  - ../meta/the-modern-baseline.md
  - ./scroll-timeline-polyfill.md
  - ./at-property-fallbacks.md
  - ../landscape-shifts/interop-2026-priorities.md
primary_sources:
  - https://web.dev/blog/same-document-view-transitions-are-now-baseline-newly-available — "Same-document view transitions have become Baseline Newly available," October 14, 2025
  - https://developer.chrome.com/docs/web-platform/view-transitions/same-document — Chrome same-doc reference
  - https://developer.chrome.com/docs/web-platform/view-transitions/cross-document — Chrome cross-doc reference (`@view-transition`)
  - https://developer.mozilla.org/en-US/docs/Web/CSS/@view-transition — MDN reference
  - https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API — MDN API reference
  - https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/144 — Firefox 144 release notes
  - https://caniuse.com/view-transitions — caniuse same-doc support data
  - https://caniuse.com/cross-document-view-transitions — caniuse cross-doc support data
  - https://webkit.org/blog/17818/announcing-interop-2026/ — Interop 2026 includes cross-document view transitions
  - https://www.bram.us/2026/03/11/view-transitions-mock-is-a-non-visual-polyfill-for-same-document-view-transitions/ — Bramus's view-transitions-mock; non-visual polyfill
---

# View Transitions — same-doc is Baseline; cross-doc is Chromium+Safari only

> **Status at 2026-04-27.** Same-document view transitions became **Baseline Newly Available on October 14, 2025**, when Firefox 144 shipped. Cross-document view transitions (the `@view-transition` rule) ship in Chromium 126+ and Safari 18.2+; **Firefox does not ship cross-doc**, with implementation expected during Interop 2026 but not committed at this date. There is **no production-grade visual polyfill** for view transitions; the answer is feature-query gating + skip-enhancement for non-supporters.

## Two distinct features under the same umbrella

Many tutorials conflate these. They have different baseline status and different polyfill stories.

| Feature | What it is | At our baseline |
|---|---|---|
| **Same-document view transitions** | `document.startViewTransition(updateCallback)` JS API + `view-transition-name` CSS for SPA-style DOM swaps within a single page | **Baseline Newly Available** (Oct 14, 2025) |
| **Cross-document view transitions** | `@view-transition { navigation: auto; }` CSS rule for MPA-style transitions between distinct documents (full page navigations) | **Chromium + Safari only** (Firefox pending) |

The same-doc API has been in Chromium since version 111 (March 2023) and Safari since 18.0 (Sept 2024). The cross-doc additions (`@view-transition` rule, `pageswap` / `pagereveal` events) shipped in Chromium 126 and Safari 18.2.

## Same-document view transitions — Baseline Oct 14, 2025

Per [web.dev's announcement post](https://web.dev/blog/same-document-view-transitions-are-now-baseline-newly-available): *"Firefox 144 was released. This release forms an exciting new milestone for view transitions, as Firefox 144 includes support for the following view transitions-related features, making them Baseline Newly available."*

| Engine | Version | Date |
|---|---|---|
| Chrome / Edge | 111 | March 7, 2023 |
| Safari | 18.0 | Sept 16, 2024 |
| Firefox | **144** | **October 14, 2025** |

Firefox 144 also added `view-transition-class`, `view-transition-name: match-element`, and the `:active-view-transition` pseudo-class.

### What this means at our baseline

| Engine segment | Native same-doc view transitions? |
|---|---|
| Chrome 125+ | Yes |
| Safari 17.4 – 17.x | No |
| Safari 18.0+ | Yes |
| Firefox 129 – 143 | **No** |
| Firefox 144+ | Yes |

Firefox 129–143 (~14 months of releases) is the gap segment for same-doc. Safari 17.4–17.x (a smaller window — Safari 18 shipped relatively early after our floor) is also a gap.

### Polyfill availability

There is no production-grade visual polyfill for same-doc view transitions. The closest thing is [`view-transitions-mock`](https://www.bram.us/2026/03/11/view-transitions-mock-is-a-non-visual-polyfill-for-same-document-view-transitions/) by Bramus Van Damme — explicitly **non-visual**: it polyfills the JS API surface (`document.startViewTransition` returning a `ViewTransition` object, the promise lifecycle) but does NOT actually animate. It's useful for code that depends on the API existing (so feature-detect branches don't need to fork) but won't make the user-visible animation appear in unsupporting browsers.

A full visual polyfill would need to:
1. Snapshot the DOM before mutation.
2. Snapshot after mutation.
3. Cross-fade between snapshots while running CSS animations on `::view-transition-*` pseudo-elements.
4. Coordinate with the document scroll position.

This is **fundamentally difficult** to polyfill correctly. The complexity makes a real polyfill rarely worth it.

### Recommended pattern: feature-query gate + skip enhancement

The right answer at our baseline is to ship same-doc view transitions as a progressive enhancement and skip the animation for unsupporters:

```js
function navigateWithTransition(updateDOM) {
  if (!document.startViewTransition) {
    updateDOM(); // browsers without support: instant swap, no animation
    return;
  }
  document.startViewTransition(updateDOM);
}

// Usage:
navigateWithTransition(() => {
  // swap content here
  document.querySelector('main').innerHTML = newContent;
});
```

CSS side:

```css
@supports (view-transition-name: a) {
  .article-card { view-transition-name: var(--card-id); }
  ::view-transition-old(*),
  ::view-transition-new(*) { animation-duration: 200ms; }
}
```

Firefox 129–143 users get an instant swap. Firefox 144+ users get the animation. No polyfill bytes shipped.

## Cross-document view transitions — Chromium + Safari, NOT Firefox

The `@view-transition` rule and `pageswap` / `pagereveal` events for full-page navigations.

| Engine | Cross-doc view transitions? |
|---|---|
| Chrome / Edge 126+ | **Yes** (Chrome 126, June 2024) |
| Safari 18.2+ | **Yes** (Safari 18.2, Dec 11, 2024) |
| Firefox | **No** — implementation pending |

Firefox cross-doc support is on Mozilla's roadmap and was named in [Interop 2026](https://webkit.org/blog/17818/announcing-interop-2026/) as a focus area, but no shipping target has been announced as of April 2026.

### What this means at our baseline

| Engine segment | Native cross-doc view transitions? |
|---|---|
| Chrome 125 | No |
| Chrome 126+ | Yes |
| Safari 17.4 – 18.1 | No |
| Safari 18.2+ | Yes |
| Firefox 129+ | **No** (any version, as of April 2026) |

For an MPA (multi-page app) that wants page-transition animations: roughly 60% of your traffic gets the animation (Chromium + recent Safari), 40% doesn't (older Safari + all Firefox).

### Recommended pattern: opt-in CSS, accept the gap

```css
@view-transition {
  navigation: auto;
}

::view-transition-group(*) {
  animation-duration: 250ms;
}
```

This is fail-safe: browsers without support ignore `@view-transition` and `::view-transition-group(...)` and serve a normal navigation. Firefox users get a clean default browser navigation; Chromium + Safari 18.2+ get the animation.

Don't reach for a polyfill. The complexity isn't worth it. View transitions are a presentational enhancement; treat the animation as the bonus, not the baseline.

## Why this baseline matters

Same-doc view transitions reached Baseline on October 14, 2025. From this skill's calibration perspective:

- **For new builds at our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+)**: same-doc view transitions work for ~all Chromium users, ~all Safari 18.0+ users, and ~all Firefox 144+ users. By April 2026, that's the dominant majority of the install base. The Firefox 129–143 gap is closing as auto-updates roll users forward.
- **For MPA cross-doc transitions**: ship them, accept that Firefox users see no animation. Don't polyfill.

## Decision tree

```
Are you using view transitions?
├── Same-document?
│   ├── Audience is overwhelmingly Chrome / Safari / Firefox 144+
│   │   → Ship native, no fallback needed
│   ├── Audience has meaningful Firefox 129–143 share
│   │   → Use feature-query gate; instant swap for non-supporters
│   └── You need the API to exist for code branching
│       → Use view-transitions-mock (non-visual polyfill)
└── Cross-document (`@view-transition` rule)?
    ├── Firefox is in your support matrix
    │   → Ship the CSS rule; Firefox ignores it gracefully (normal navigation)
    └── Chromium + Safari 18.2+ only
        → Ship and enjoy
```

## Cross-references

- `./scroll-timeline-polyfill.md` — sibling animation feature with a real polyfill; contrast with view transitions where a real polyfill is impractical.
- `./at-property-fallbacks.md` — the broader pattern of "no polyfill exists; use feature query + accept degraded experience."
- `../meta/the-modern-baseline.md` — why same-doc view transitions are usable at our floor for most engines.
- `../landscape-shifts/interop-2026-priorities.md` — cross-doc view transitions named for Firefox parity.
