---
date: 2026-04-27
coverage: extended
peers:
  - ../meta/the-modern-baseline.md
  - ../meta/baseline-glossary.md
  - ../js-language-status/temporal.md
  - ../anchor-positioning-quirks/firefox-147-anchor-shipped.md
primary_sources:
  - https://web.dev/blog/interop-2026 — Google / web.dev announcement (Feb 12, 2026)
  - https://webkit.org/blog/17818/announcing-interop-2026/ — WebKit announcement (Feb 12, 2026)
  - https://wpt.fyi/interop-2026 — WPT scoreboard
  - https://github.com/web-platform-tests/interop — interop project repo
---

# Interop 2026 — what's coming this year (extended)

> **Coverage tier: extended.** Interop priorities are *forward-looking* — they predict where the spec gap will close in the year ahead. The skill uses this file to forecast which polyfills will become obsolete during 2026 and which features (still missing from the list) will need polyfills *longer*.

## What Interop is

[Interop](https://github.com/web-platform-tests/interop) is the annual cross-vendor collaboration to **close the most painful interoperability gaps in the web platform**. Each year, the participating browser engine teams agree on a finite list of focus areas where they will prioritize implementation work, run identical Web Platform Tests (WPT), and publish a public scoreboard tracking each engine's score.

The premise: developers can't use a feature reliably until *all* engines ship it the same way. Interop forces the conversation past "Chrome shipped it" into "Chrome, Safari, and Firefox all pass the same tests."

**Participating organizations (2026):**

- **Apple** (WebKit / Safari)
- **Google** (Blink / Chrome)
- **Igalia** (consultancy contributing to multiple engines)
- **Microsoft** (Edge, contributing to Blink)
- **Mozilla** (Gecko / Firefox)

The scoreboard lives at [wpt.fyi/interop-2026](https://wpt.fyi/interop-2026). Each participating engine gets a percentage score on each focus area, plus an overall score; the public scoreboard is updated continuously as new test runs land.

## Interop 2026 announcement

Interop 2026 was announced on **February 12, 2026**, jointly across the participating vendors:

- Google: [web.dev/blog/interop-2026](https://web.dev/blog/interop-2026)
- WebKit: [webkit.org/blog/17818/announcing-interop-2026](https://webkit.org/blog/17818/announcing-interop-2026/)

Each vendor publishes their own announcement with their own framing, but the focus-area list is shared — what differs is the perspective on *which* areas each team is "behind" on and which they're proud to have shipped first.

## The 2026 focus areas (20)

The focus areas form the "scoring set" — each contributes to the scoreboard percentage. There are also "investigation" areas (non-scoring, exploring how to test a feature) noted at the end.

### CSS & Layout (8)

1. **Anchor positioning** — Positioning elements relative to other elements via `anchor()` and `position-area`. Carryover from Interop 2025 (extended into 2026 to fix remaining gaps and clarify spec ambiguities). At 2026 baseline (Apr 2026): Chrome 125+, Safari 26+, Firefox 147 (Jan 13, 2026). The expert-polyfills skill flags this as the highest-impact carryover — see [`../anchor-positioning-quirks/firefox-147-anchor-shipped.md`](../anchor-positioning-quirks/firefox-147-anchor-shipped.md).

2. **Container style queries** — `@container style(--my-prop: value)`. Conditional styling based on a custom property's value at the container, distinct from size queries. Already shipping in some engines but with interop gaps in spec corners.

3. **`contrast-color()` CSS function** — Returns black or white for highest contrast against a given color. WebKit highlights it as one of four functions Safari "shipped first." **Not yet in Chrome stable as of April 2026** — see [`../css-color-bugs/contrast-color-availability.md`](../css-color-bugs/contrast-color-availability.md).

4. **`attr()` CSS function (advanced/typed)** — Extending HTML attribute values to all CSS properties with type conversion (e.g., `attr(width type(<length>))`). The legacy `attr()` form was content-only; the typed form has been a standards goal for years.

5. **`shape()` CSS function** — Complex shapes with curves using percentage-based coordinates, replacing the older `path()`-only form for clipping and offset paths.

6. **CSS `zoom` property** — Carryover from Interop 2025. Scales elements while affecting layout participation (unlike `transform: scale()` which preserves layout box). Interoperability work continues into 2026.

7. **Scroll-driven animations** — CSS animations that respond to scroll position without JavaScript. Includes `scroll-timeline` and `view-timeline`. Polyfilled by [`flackr/scroll-timeline`](https://github.com/flackr/scroll-timeline). At 2026 baseline: Chrome 115+, Safari 26+, Firefox behind a flag (continuing).

8. **Scroll snap** — Carousel-like panning with snap points. Already widely shipped but with interop gaps in edge cases (multi-axis snap, `scroll-snap-stop`, `block-scope-flex` interactions).

### UI components & APIs (4)

9. **Custom Highlights** — Styling arbitrary text ranges via the CSS Highlight API without DOM modifications. Use cases: search results, collaborative cursors, spell-check overlays. WebKit highlights this as another "shipped first" capability.

10. **Dialog and popover additions** — Including the `closedby` attribute, `popover="hint"`, and the `:open` pseudo-class. The skill maintains a [whole axis on popover quirks](../popover-quirks/) — these features are at the cutting edge of that surface.

11. **Scoped Custom Element Registries** — Multiple web component definitions per tag name in different scopes. Shipping in WebKit and Blink; Firefox is behind. WebKit notes this as a "shipped first" capability. The skill has [`../runtime-polyfills/`](../runtime-polyfills/) coverage of the [`@webcomponents/scoped-custom-element-registry`](https://github.com/webcomponents/polyfills/tree/master/packages/scoped-custom-element-registry) polyfill for the Firefox gap.

12. **View Transitions** — Same-document and cross-document animated transitions between UI states. Same-document went Baseline Newly Available October 2025; cross-document is the 2026 priority. Carryover from 2025 in the cross-document form.

### Network & data (4)

13. **Fetch uploads and ranges** — `ReadableStream` request bodies, enhanced `FormData`, and `Range` header support. Interop gaps in streaming-upload semantics across engines.

14. **`getAllRecords()` for IndexedDB** — Batch retrieval with directional options for structured browser storage. A long-requested IndexedDB ergonomic improvement.

15. **WebTransport API** — HTTP/3-based bidirectional communication with multiple streams. The successor to WebSocket for many use cases; WebKit specifically committed to landing it.

16. **WebRTC** — Real-time audio, video, and data communication. Carryover from Interop 2025 — fixing remaining failing tests in established-but-unevenly-implemented APIs.

### JavaScript & performance (3)

17. **JSPI (JavaScript Promise Integration) for Wasm** — Promise integration enabling synchronous Wasm code to work with async JavaScript. Important for Emscripten-compiled C++ that uses Asyncify.

18. **Navigation API** — Cleaner alternative to `history.pushState()` with the new `precommitHandler` option. Carryover from 2025.

19. **Media pseudo-classes** — Seven new selectors for audio/video states: `:playing`, `:paused`, `:seeking`, `:buffering`, `:stalled`, `:muted`, `:volume-locked`. WebKit "shipped first."

### Compatibility (1)

20. **Web Compat** — Addressing residual cross-engine bugs in ESM module loading, scroll/animation event timing, and `user-select` support. The grab-bag focus area; usually 5–10 narrowly-scoped tests.

### Investigation areas (non-scoring)

These don't contribute to the scoreboard percentage but represent ongoing collaborative exploration:

- **Accessibility Testing** — Building cross-engine ARIA / a11y test infrastructure.
- **JPEG XL** — Image-format interop. Apple ships it; Chrome removed it; Mozilla on the fence. Investigation ≠ scoring.
- **Mobile Testing** — Better WPT coverage on mobile engines.
- **WebVTT** — Caption format interop. Long-running gap; not in 2026 scoring set.

## Carryover from Interop 2025

The 2026 list explicitly **continues** five 2025 priorities rather than declaring them "done":

| Carryover | Why it's continuing |
|---|---|
| Anchor positioning | Spec clarifications + closing the last interop gaps; Firefox shipping (Jan 2026) only made the cross-engine landscape *exist* |
| CSS `zoom` | Edge cases in layout box semantics |
| Navigation API | New `precommitHandler` semantics; cleanup of older `history.*` interop bugs |
| View Transitions | Cross-document is the 2026 priority; same-doc reached Baseline in Oct 2025 |
| WebRTC | Remaining failing tests in established APIs — perennial |

What this means for the polyfill stance: features on a multi-year carryover list are likely to need polyfills for **another year** beyond the original "Chrome shipped" date. Anchor positioning is the canonical example — Chrome 125 shipped May 2024; Safari 26 shipped 2025; Firefox 147 shipped January 2026. Now in April 2026, it's *finally* in all three engines unflagged, but the Interop 2026 inclusion signals that interop is still wobbly enough to need cross-engine work. **Polyfill until at least Q3 2026** before treating it as "done."

## What carryover from earlier did NOT make 2026

Interop 2024 and 2025 included some priorities that didn't carry over to 2026:

- **`text-box-trim` / `text-box-edge`** — Was on the 2025 investigation list. Not on 2026. Still implementation-divergent. Polyfill: feature query + fallback to manual leading-trim.
- **COLRv1 fonts in Safari** — Long-running 2024–2025 priority. Made significant progress; not on the 2026 scoring list. Considered "good enough."
- **Customizable `<select>` (`appearance: base-select`)** — Despite Chrome 135 shipping it, this is *not* on Interop 2026. Implies Safari and Firefox aren't ready to commit. Polyfill / progressive enhancement candidate for **at least another year**.

## What this means for polyfill-expert users

**Reading the Interop list as a polyfill timeline:**

1. **Features on Interop 2026 will likely be Baseline by year-end.** If something's a 2026 focus area and was at "Newly Available" or "interim" status in early 2026, it should reach "Widely Available" by Q4 2026 — at which point most polyfills become unnecessary at the *next* year's baseline.

2. **Carryover from prior years = "polyfill another year."** Anchor positioning (3rd year on the list), WebRTC (perennial), View Transitions cross-doc — none are "done" even though all three are partially shipping. Plan polyfill phase-outs at the carryover-end date, not at the first-engine-ship date.

3. **Features NOT on the list = "polyfill longer or accept progressive enhancement."** Customizable `<select>`, `popover="hint"`, `text-box-trim`, COLRv1 — not on Interop 2026. These will take *more* than one year to reach Baseline status. The skill recommends progressive enhancement + feature query rather than runtime polyfilling for these — see [`../feature-detection/at-supports-recipes.md`](../feature-detection/at-supports-recipes.md).

4. **Investigation areas = "no polyfill timeline; treat as experimental."** JPEG XL, WebVTT — these are politically contested (in the case of JPEG XL) or technically deprioritized (in the case of WebVTT). Don't build a polyfill strategy around them.

### Forecast — what becomes safely native by end of 2026

If Interop 2026 hits its targets (typical historical scoreboard rises by ~15–25 points per year per focus area), the following should be **Baseline-ready by Q4 2026 or Q1 2027**:

- Anchor positioning (Interop 2025+2026 carryover; Firefox shipped Jan 2026)
- Cross-document View Transitions
- Container style queries (the `style()` form)
- `contrast-color()` (assuming Chrome ships it during 2026)
- `attr()` typed function
- `shape()`
- Media pseudo-classes
- Custom Highlights
- IndexedDB `getAllRecords`

That's a lot of polyfills the skill expects to mark deprecated by the **2027 baseline** revision. If your team has a roadmap budget for "remove polyfills," Q4 2026 / Q1 2027 is when the next pruning pass is worthwhile.

### Forecast — what still needs polyfills past 2026

Features the skill expects to remain polyfill candidates beyond 2026:

- **Temporal API** — Not on Interop 2026. Stage 4 March 2026; Firefox 139 (May 2025), Chrome 144 (Jan 2026), Safari pending. Polyfill via [`@js-temporal/polyfill`](https://www.npmjs.com/package/@js-temporal/polyfill) for Safari. Likely safe to drop sometime in 2027.
- **Customizable `<select>`** — Not on Interop 2026. Chrome 135+ only. Use progressive enhancement; no real polyfill exists.
- **`popover="hint"`** — Not on Interop 2026 explicitly (popover *additions* are, but the skill's reading is that `closedby` and `:open` are the priorities, with `hint` deferred). Chrome 133+ only.
- **JPEG XL, WebVTT** — Investigation only; no shipping commitment.
- **Cross-doc View Transitions** — On the list but the harder of the two; expect Chromium-only well into 2026.

## How to read the WPT scoreboard

The [wpt.fyi/interop-2026](https://wpt.fyi/interop-2026) scoreboard shows:

- **Per-engine score** — Chrome / Safari / Firefox each get a percentage on each focus area, plus an overall.
- **Trend lines** — How each engine's score has moved over the year. Sharp jumps usually correspond to a release shipping.
- **Test-level drilldown** — Click into a focus area to see which specific WPT tests are passing on which engine.

For the expert-polyfills skill's purposes, the most useful view is: **at any point in 2026, what's the lowest-engine score?** That's the cap on "interoperable enough." A focus area at 40% / 60% / 90% (Chrome / Safari / Firefox) has a 40% interop ceiling — wait until the laggard engine catches up.

## See also

- [`./polyfill-io-attack.md`](./polyfill-io-attack.md) — landscape-shifts companion file
- [`./core-js-funding-status.md`](./core-js-funding-status.md) — landscape-shifts companion file
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — what's already shipped at the current baseline
- [`../meta/baseline-glossary.md`](../meta/baseline-glossary.md) — Baseline Newly Available vs Widely Available
- [`../js-language-status/temporal.md`](../js-language-status/temporal.md) — example of a feature *not* on Interop 2026 with its own polyfill story
- [`../anchor-positioning-quirks/firefox-147-anchor-shipped.md`](../anchor-positioning-quirks/firefox-147-anchor-shipped.md) — how Firefox 147 closed the anchor positioning gap
- [`../css-color-bugs/contrast-color-availability.md`](../css-color-bugs/contrast-color-availability.md) — `contrast-color()` Safari/Firefox vs Chrome status
