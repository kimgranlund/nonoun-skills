---
date: 2026-04-27
coverage: esoteric
peers:
  - ./light-dark-color-scheme.md
  - ../meta/the-modern-baseline.md
  - ../feature-detection/at-supports-recipes.md
primary_sources:
  - https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/color_value/contrast-color — MDN reference
  - https://webkit.org/blog/16929/contrast-color/ — WebKit blog, May 2025: "How to have the browser pick a contrasting color in CSS"
  - https://chromestatus.com/feature/4841046007742464 — Chrome Platform Status: CSS contrast-color()
  - https://developer.chrome.com/release-notes/147 — Chrome 147 release notes (April 7, 2026)
  - https://drafts.csswg.org/css-color-6/ — CSS Color Module Level 6 (where contrast-color() lives)
  - https://www.w3.org/TR/css-color-5/ — CSS Color Module Level 5 (where the original color-contrast() was dropped)
  - https://bugzilla.mozilla.org/show_bug.cgi?id=1682439 — Mozilla bug: Implement CSS contrast-color()
  - https://caniuse.com/wf-contrast-color — caniuse support matrix
  - https://webkit.org/blog/17818/announcing-interop-2026/ — Interop 2026 announcement (Feb 12, 2026)
  - https://css-tricks.com/exploring-the-css-contrast-color-function-a-second-time/ — CSS-Tricks deep-dive
  - https://blog.damato.design/posts/css-only-contrast/ — D'Amato: workaround patterns
  - https://github.com/antiflasher/apcach — apcach (APCA-aware contrast computation library)
---

# `contrast-color()` shipping reality at our baseline

## TL;DR

`contrast-color()` returns `white` or `black` depending on which has higher WCAG contrast against an input color. It's the long-promised "automatic accessible text color" function — a renamed, simplified successor to the dropped `color-contrast()` function.

**As of April 27, 2026 — three weeks after Chrome 147 stable shipped April 7, 2026:**

- **Safari 26.0+** (Sept 2025): shipped
- **Firefox 146+** (early 2026): shipped
- **Chrome / Edge 147+** (April 7, 2026): **just shipped — but our baseline is Chrome 125+, so 125–146 (the entire baseline span minus the most recent two weeks) does not have it**

The cross-browser story is now positive in absolute terms, but at our baseline floor of Chromium 125+, the function is **not yet usable in production**. Use a feature query, fall back to a hardcoded black/white pair, and migrate once your Chrome floor advances past 147.

## Spec history — color-contrast() → contrast-color()

The function went through two specs and a rename:

| Spec / Era | Function | Behavior | Status |
|---|---|---|---|
| CSS Color Module Level 5 (early drafts) | `color-contrast(base vs c1, c2, c3)` | Picks one color from a candidate list with the highest contrast vs. `base` | **Dropped** — never shipped in any stable browser |
| CSS Color Module Level 6 (current) | `contrast-color(base)` | Returns `white` or `black`, whichever has higher WCAG contrast vs. `base` | Shipping 2025–2026 |

The earlier `color-contrast()` proposal allowed fancier candidate lists, optional WCAG threshold targets, and APCA contrast modes. It was deemed too complex to ship interoperably and was deferred. The simpler `contrast-color()` — which has only one decision to make (black or white?) — is what actually landed.

The CSS-Tricks coverage is unusually clear on this evolution:

- ["Exploring color-contrast() for the First Time"](https://css-tricks.com/exploring-color-contrast-for-the-first-time/) — covers the original Level 5 proposal.
- ["Exploring the CSS contrast-color() Function… a Second Time"](https://css-tricks.com/exploring-the-css-contrast-color-function-a-second-time/) — covers the Level 6 simplified successor.

If you find blog posts or docs referencing the multi-color-list `color-contrast(base vs c1, c2)` syntax, **they are out of date**.

## Current shipping status (April 2026)

| Engine | Version | Date | Source |
|---|---|---|---|
| **Safari** | 26.0 | September 15, 2025 | [WebKit Features in Safari 26.0](https://webkit.org/blog/17333/webkit-features-in-safari-26-0/) — also previewed earlier in [Safari Tech Preview, May 2025](https://webkit.org/blog/16929/contrast-color/) |
| **Firefox** | 146 | Early 2026 | [Mozilla Bugzilla 1682439](https://bugzilla.mozilla.org/show_bug.cgi?id=1682439) — implementation tracking |
| **Chrome / Edge** | **147** | **April 7, 2026** | [Chrome 147 release notes](https://developer.chrome.com/release-notes/147), [chromestatus.com/feature/4841046007742464](https://chromestatus.com/feature/4841046007742464) |

Interop 2026 listed `contrast-color()` as a focus area in the [Feb 12, 2026 announcement](https://webkit.org/blog/17818/announcing-interop-2026/) — Chrome's 147 ship landed two months later.

## Verdict against our baseline

Our baseline is **Chromium 125+** (May 2024) / Safari 17.4+ / Firefox 129+. The Chrome 125–146 span is roughly **22 months wide** (May 2024 → March 2026) and covers most users in our floor. Within that span, **`contrast-color()` does not work** — Chrome 147 only just shipped.

Translation: at this baseline, **do not put `contrast-color()` in production CSS** without a feature query and fallback. Even with a feature query, expect ~70%+ of your Chrome users to fall through to the fallback for the next several months as 147 rolls out.

The numbers will improve fast — Chromium auto-update typically gets ~80% rollout to 95% within ~6 weeks of stable release. Revisit this assessment in late summer 2026.

## Workaround patterns

### Pattern A — feature query with hardcoded fallback

The "do nothing fancy" answer. Pick a contrast-safe fallback, gate the upgrade behind `@supports`.

```css
.button {
  background: var(--brand);
  color: white;                                /* Safe default */
}

@supports (color: contrast-color(white)) {
  .button {
    color: contrast-color(var(--brand));       /* Browser picks black/white */
  }
}
```

The fallback is whichever of `black` / `white` is right *for your specific brand color* — pick once at design time. If your brand color shifts at runtime (theming, user customization), this pattern stops working and you need pattern B.

### Pattern B — runtime computation via `apcach` or similar

For dynamic theming where the brand color is user-controlled, compute contrast at JS runtime. The community-standard library is [apcach](https://github.com/antiflasher/apcach) (Evil Martians, MIT-licensed, ~7KB minified).

```js
import { apcach, crToFg } from "apcach";

// Given a background, find a foreground that hits APCA contrast 75+
const fg = crToFg("oklch(0.65 0.2 250)", 75);
document.body.style.setProperty("--fg", fg);
```

`apcach` uses APCA contrast (the WCAG 3 successor that better predicts perceived legibility on perceptually-uniform color spaces like OKLCH); a `crToFg("...", "wcag2-aa")` mode is also available if you need WCAG 2 AA conformance specifically.

This is the right answer for: design tokens that compute at build time, theme builders that compute at runtime, and any system where the brand color is not author-known.

### Pattern C — build-time precomputation

If your color set is finite and known at build time, just compute the foreground at build time and emit static CSS. This is what Tailwind v4 and shadcn/ui do.

```js
// In your ui-build-tokens build step
import { wcagContrast } from "culori";

const tokens = {
  brand: "oklch(0.65 0.2 250)",
  brandFg: wcagContrast("oklch(0.65 0.2 250)", "white") >= 4.5 ? "white" : "black",
};
// Emit --brand and --brand-fg as static custom properties
```

This is bulletproof, has zero runtime cost, and is by far the most common pattern in production design systems today.

### Pattern D — defer to native enhanced when available

For projects whose support floor will rise past Chrome 147 within the project's lifetime:

```css
.button {
  color: var(--brand-fg);                      /* Build-time computed */
}

@supports (color: contrast-color(white)) {
  .button {
    color: contrast-color(var(--brand));       /* Native takes over when Chrome 147+ */
  }
}
```

Both branches produce the same result *for static brand colors*. The native branch is more useful in projects that have runtime-variable colors (theming, user-customizable surfaces) but want the build-time fallback for older Chromes.

## What `contrast-color()` actually returns

To be precise about behavior — `contrast-color(<color>)` returns:

- `white` if `white` has higher WCAG 2.1 contrast against the input than `black`.
- `black` if `black` has higher contrast.
- `white` (per spec tie-breaking) if both have equal contrast.

It does **not** support custom WCAG thresholds, multi-color candidate lists, or APCA — those were the dropped Level 5 features. If you need any of that, use `apcach` or a build-time pipeline.

## Why this is in the bug catalog

It's not a bug per se — it's a "newer than expected" gotcha. Articles published in late 2025 confidently claim cross-browser support; that was true for Safari and Firefox, not Chrome. Anyone writing CSS at the April 2026 cusp who believes "all three engines support `contrast-color()`" will ship it without a feature query and watch it break for the majority of their Chrome users (who are still on 125–146 for several more months).

The mitigation is mechanical: always pair `contrast-color()` with `@supports`, or precompute the foreground at build time, or use a runtime contrast library. Avoid the un-feature-queried inline use until your Chrome floor crosses 147.

## Cross-references

- Per-baseline color-feature status: [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)
- Sibling gotcha (silent no-op when `color-scheme` is missing): [`light-dark-color-scheme.md`](./light-dark-color-scheme.md)
- Feature-query authoring patterns: [`../feature-detection/at-supports-recipes.md`](../feature-detection/at-supports-recipes.md)
