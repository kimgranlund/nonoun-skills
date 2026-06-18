---
date: 2026-04-27
coverage: extended
peers:
  - ../meta/the-modern-baseline.md
  - ../anchor-positioning-quirks/inset-area-rename.md
  - ../anchor-positioning-quirks/safari-26-anchor-shipped.md
  - ../anchor-positioning-quirks/popover-margins-interaction.md
  - ../css-polyfills-and-shims/anchor-positioning-polyfill.md
primary_sources:
  - https://www.firefox.com/en-US/firefox/147.0/releasenotes/ — Firefox 147 release notes (Jan 13, 2026)
  - https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/147 — Firefox 147 developer release notes
  - https://bugzilla.mozilla.org/show_bug.cgi?id=1988225 — Bug 1988225 — enable anchor positioning on all channels
  - https://bugzilla.mozilla.org/show_bug.cgi?id=1988224 — Bug 1988224 — enable anchor positioning on Nightly first
  - https://groups.google.com/a/mozilla.org/g/dev-platform/c/B71NFNrZ8Lo/m/e1ZMg8fjCAAJ — Mozilla "Intent to ship" thread
  - https://www.oddbird.net/2025/10/13/anchor-position-area-update/ — OddBird Fall 2025 roundup
  - https://web.dev/blog/web-platform-01-2026 — web.dev "New to the web platform in January 2026" recap
  - https://caniuse.com/css-anchor-positioning — caniuse data
---

# Firefox 147 shipped CSS Anchor Positioning unflagged

Firefox 147 (January 13, 2026) was the third and final major-engine release to ship CSS Anchor Positioning, completing Baseline. Earlier Firefox versions ran the implementation behind `layout.css.anchor-positioning.enabled`. This file is the canonical record of the Firefox flag history and the polyfill window that still applies at our baseline floor (Firefox 129+).

## Timeline (verified)

| Firefox version | Date | Anchor positioning status | Notes |
|---|---|---|---|
| **Firefox 129** (our baseline floor) | August 6, 2024 | Not implemented | Mozilla's [intent to prototype](https://groups.google.com/a/mozilla.org/g/dev-platform/c/4cbytMKbHtg) had landed; no shipping code. |
| Firefox 130 – 131 | Aug–Oct 2024 | Not implemented | |
| Firefox 132 – 144 | Oct 2024 – Nov 2025 | Partial implementation behind a flag | The `layout.css.anchor-positioning.enabled` preference appeared during this window, with progressively more spec coverage. Disabled by default on all channels. |
| **Firefox 145** | November 2025 | Shipped behind flag — Nightly enabled | [Bug 1988224](https://bugzilla.mozilla.org/show_bug.cgi?id=1988224) enabled the preference on Nightly. Firefox 145's MDN release notes list it as "shipping but disabled by default." |
| **Firefox 146** | December 9, 2025 | Still flagged on stable | Implementation considered close to spec-complete, but `layout.css.anchor-positioning.enabled` remained `false` by default on Release. |
| **Firefox 147** | **January 13, 2026** | **Enabled by default on all channels** | [Bug 1988225](https://bugzilla.mozilla.org/show_bug.cgi?id=1988225) flipped the preference to `true` on every channel. Anchor positioning becomes Baseline Newly available. Firefox 147 release notes also add the `anchor-center` keyword (on `align-self`, `justify-self`, etc.) and the `position-anchor: none` value. |

January 13, 2026 is therefore the canonical "anchor positioning is Baseline" date. caniuse and web.dev both mark January 2026 as the Baseline-Newly-Available transition.

## What Firefox 147 supports

Same canonical surface that Chrome and Safari ship:

- Properties: `anchor-name`, `position-anchor`, `position-area`, `position-try`, `position-try-order`, `position-try-fallbacks`, `position-visibility`.
- Functions: `anchor()`, `anchor-size()`.
- At-rule: `@position-try`.
- Self-aligned values: `anchor-center` on `align-items` / `align-self` / `justify-items` / `justify-self` / `place-items` / `place-self` (Firefox-147-specific addition per [bug 1909339](https://bugzilla.mozilla.org/show_bug.cgi?id=1909339)).
- `position-anchor: none` value (Firefox-147-specific addition per [bug 1999972](https://bugzilla.mozilla.org/show_bug.cgi?id=1999972)) — explicitly removes an implicit or explicit anchor association.

Firefox shipped the new name `position-area` directly. There is no `inset-area` codepath in Gecko. See `inset-area-rename.md` for the Chrome rename history.

## The polyfill window at our baseline (Firefox 129+)

Our skill's baseline floor is Firefox 129 (August 6, 2024) — *eighteen versions* before anchor positioning shipped enabled-by-default. The polyfill window covers a substantial fraction of Firefox versions:

| Firefox segment | Native anchor positioning? | Polyfill needed? |
|---|---|---|
| Firefox 129 – 131 | No | **Yes** |
| Firefox 132 – 146 | Available behind `layout.css.anchor-positioning.enabled` flag, but **off by default** in stable | **Yes** (treat as no support — flag is not flippable in production user code) |
| Firefox 147+ | **Yes** | No |

That is **18 versions / ~17 months** of Firefox releases that need the OddBird polyfill or a graceful-degradation strategy at our baseline.

In practice, the practical width of the polyfill audience is much narrower than that arithmetic suggests:

- Firefox is on a 4-week release cadence. By April 2026 (this file's date), the Release channel is Firefox 150+ ([web.dev's January 2026 recap](https://web.dev/blog/web-platform-01-2026) notes 147 was "the new Firefox").
- Auto-updating Firefox installs roll forward quickly. Statcounter consistently shows the previous-2-versions of Firefox holding the dominant share within ~6 weeks of a release.
- The slow-mover audience is enterprise installs with managed updates, ESR (Extended Support Release) builds, and locked-down Linux distributions.

If your analytics show meaningful Firefox-pre-147 share — especially Firefox ESR (Extended Support Release tracks an old major version for ~12 months) — polyfill. Otherwise, ship native and feature-detect.

## Firefox ESR — the real long tail

Firefox ESR is the Long-Term-Support channel. As of April 2026, the active ESR is **Firefox 140 ESR** (released around late 2025), which receives only security updates through autumn 2026 before being replaced by a newer ESR baseline. ESR 140 does NOT have anchor positioning enabled — the feature was still flagged when 140 branched.

This means: organizations on ESR (universities, public-sector, enterprise IT) will not see anchor positioning until they migrate to the next ESR (likely Firefox 152 ESR, depending on the schedule). For ESR-bound audiences, polyfill is mandatory.

## Practical detection + polyfill wiring

```html
<script>
  // Feature-detect the post-rename canonical name.
  // Firefox 147+, Safari 26+, Chrome 125+ all return true.
  if (!CSS.supports('anchor-name', '--x')) {
    // Self-host the OddBird polyfill — never load from a 3rd-party CDN.
    // See ../css-polyfills-and-shims/anchor-positioning-polyfill.md.
    import('/vendor/css-anchor-positioning.min.js');
  }
</script>
```

Why detect `anchor-name` rather than `position-area`? Because `anchor-name` was renamed once (out of `--anchor-name` syntax in pre-shipping drafts) but has been stable since first ship; `position-area` carries the rename history. Detecting `anchor-name` is more robust against partial implementations.

## Note: this baseline is calibrated for April 2026

By the time anyone reads this file, Firefox 147+ users probably dominate the Firefox installed base — auto-updates are fast. The polyfill audience shrinks every month as the Firefox 129–146 long tail ages out. The file remains relevant for:

- ESR audiences (12+ month lag)
- Enterprise managed-update Firefox audiences
- Embedded Firefox / Firefox Focus / Tor Browser variants that lag stable
- Any project that still has Firefox 129+ in its hard support floor

For consumer-web with auto-updating Firefox users, the polyfill is dead weight by mid-2026.

## Cross-references

- For the `inset-area` → `position-area` rename history: `inset-area-rename.md`.
- For Safari's anchor-positioning ship: `safari-26-anchor-shipped.md`.
- For UA-style popover margin interference: `popover-margins-interaction.md`.
- For the OddBird polyfill specifics (version, install, bundle size, license): `../css-polyfills-and-shims/anchor-positioning-polyfill.md`.
- For Mozilla bug 1988225 (the flag flip): https://bugzilla.mozilla.org/show_bug.cgi?id=1988225.
