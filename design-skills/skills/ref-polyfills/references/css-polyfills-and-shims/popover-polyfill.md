---
date: 2026-04-27
coverage: extended
peers:
  - ../popover-quirks/ios-safari-light-dismiss.md
  - ../popover-quirks/safari-focus-inputs.md
  - ../popover-quirks/safari-184-tab-hang.md
  - ../popover-quirks/popover-vs-dialog-toplayer.md
  - ../popover-quirks/popover-hint-chromium-only.md
  - ../popover-quirks/popovertarget-vs-showpopover.md
  - ./anchor-positioning-polyfill.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://github.com/oddbird/popover-polyfill — repository, BSD-3-Clause license
  - https://www.npmjs.com/package/@oddbird/popover-polyfill — npm package
  - https://popover.oddbird.net/ — demo and status page
  - https://github.com/oddbird/popover-polyfill/blob/main/README.md — install + usage
  - https://web.dev/blog/popover-baseline — Popover became Baseline Newly Available, January 27, 2025
  - https://bugs.webkit.org/show_bug.cgi?id=267688 — WebKit Bug 267688 (iOS light-dismiss); fixed in Safari 18.3
---

# `@oddbird/popover-polyfill` — historical at our baseline, surgical for one iOS bug window

> **Status at 2026-04-27.** Active. Latest npm: **0.6.1**. Maintained by OddBird, in collaboration with Keith Cirkel (GitHub). License: **BSD-3-Clause**. Used in production at GitHub. At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+), the Popover API is **native everywhere** — the polyfill is mostly historical. The exception is the iOS Safari 17.0–18.2 light-dismiss bug (see `../popover-quirks/ios-safari-light-dismiss.md`), where the polyfill is one of three workaround options.

## Why this polyfill is mostly historical now

The Popover API entered Baseline Newly Available on **January 27, 2025** ([web.dev/blog/popover-baseline](https://web.dev/blog/popover-baseline)) when Safari 18.3 fixed the iOS light-dismiss bug. At our skill's baseline:

| Engine | Floor | Native popover support? |
|---|---|---|
| Chrome / Edge | 125+ | **Yes** — native since Chrome 114 (May 2023) |
| Firefox | 129+ | **Yes** — native since Firefox 125 (April 2024) |
| Safari Desktop | 17.4+ | **Yes** — native since Safari 17 (Sept 2023) |
| Safari iOS / iPadOS | 17.4+ | **Yes** — but with the light-dismiss bug on 17.0–18.2 (fixed 18.3) |

Native Popover is everywhere at our baseline. **There is no general reason to ship this polyfill in 2026.** The only situations where it earns its bytes:

1. **iOS Safari 17.4–18.2 light-dismiss workaround** (the most common reason). See `../popover-quirks/ios-safari-light-dismiss.md` for the bug. The polyfill is option 3 of 3 workarounds — the simpler answer is "add a close button."
2. **Audiences below our baseline** (Safari < 17, Firefox < 125). If your support floor is lower than our skill's, this polyfill becomes load-bearing.
3. **GitHub-style legacy-target workloads** — GitHub uses this polyfill in production for its broad-browser footprint. If you're authoring a CMS or a UGC-rich page that ships to long-tail browsers, the polyfill is reasonable insurance.

For most modern app builds at our baseline, **don't ship this polyfill**. Use feature-query gating or accept the iOS 17.4–18.2 light-dismiss gap with an explicit close button.

## Package metadata

| Field | Value |
|---|---|
| npm | https://www.npmjs.com/package/@oddbird/popover-polyfill |
| Repository | https://github.com/oddbird/popover-polyfill |
| Latest version | 0.6.1 |
| License | BSD-3-Clause |
| Maintainers | OddBird, in collaboration with Keith Cirkel (GitHub) |
| Demo | https://popover.oddbird.net/ |
| Production usage | GitHub (cited on the demo page) |
| Bundle size | ~3 KB minified+gzipped — lightweight for what it polyfills |

The collaboration with Keith Cirkel is meaningful: Cirkel is one of the popover spec champions and is on GitHub's accessibility team. The polyfill's behavior is closely informed by spec authoring.

## What it polyfills

- The HTML `popover` attribute (`popover="auto"`, `popover="manual"`, and synthesized `:popover-open`).
- `HTMLElement.prototype.showPopover()`, `.hidePopover()`, `.togglePopover()` methods.
- The `popovertarget` and `popovertargetaction` attributes on `<button>` elements.
- Light-dismiss algorithm for `popover="auto"`.

What it does NOT polyfill:
- `popover="hint"` — Chromium 133+ only, no spec-stable polyfill exists. See `../popover-quirks/popover-hint-chromium-only.md`.
- The CSS top layer (`::backdrop`, native stacking-context promotion). The polyfill simulates it with z-index hacks; not pixel-identical to native.
- `:popover-open` selector (synthesized via attribute, not pseudo-class — selectors using `:popover-open` directly may break in polyfilled mode).

## Installation and usage

### Pattern 1 — bare side-effect import (auto-applies to unsupported browsers)

```js
import '@oddbird/popover-polyfill';
```

This is the simplest pattern. The polyfill detects native Popover support at module-evaluation time and no-ops when the browser already implements it. Safe to ship to a mixed audience — modern browsers pay only the script-evaluation cost (~1ms), not the runtime cost.

### Pattern 2 — surgical apply (force-override for the iOS bug window)

For the specific case of iOS Safari 17.0–18.2 (the light-dismiss bug), default detection won't trigger the polyfill — the iOS browser claims native support but is buggy. To force-override:

```js
import { isSupported, apply, isPolyfilled } from '@oddbird/popover-polyfill/fn';

const ua = navigator.userAgent;
const isAffectedIOS =
  /iP(hone|ad|od)/.test(ua) &&
  /Version\/(17|18\.[012])/.test(ua) &&
  /Safari/.test(ua);

if (isAffectedIOS && !isPolyfilled()) {
  apply();
}
```

UA sniffing is fragile — but for the iOS 17.4–18.2 window specifically, there's no clean alternative. The bug isn't detectable via feature-query (the API is "supported," it just doesn't dismiss correctly). For most teams, **option 1 from `../popover-quirks/ios-safari-light-dismiss.md` (add an explicit close button)** is the better answer.

### Pattern 3 — bundler chunk + dynamic import (only ship to those who need it)

```js
const ua = navigator.userAgent;
const needsPolyfill =
  /iP(hone|ad|od)/.test(ua) && /Version\/(17|18\.[012])/.test(ua);

if (needsPolyfill) {
  const { apply } = await import('@oddbird/popover-polyfill/fn');
  apply();
}
```

Splits the polyfill into its own chunk. Modern browsers and post-fix iOS Safari never request it.

## API surface (the `/fn` entry)

```js
import {
  isSupported, // () => boolean — does the current browser implement Popover natively?
  apply,       // () => void — force-apply the polyfill, overriding native
  isPolyfilled // () => boolean — has the polyfill already been applied?
} from '@oddbird/popover-polyfill/fn';
```

`isSupported()` returns `true` on any browser that has the Popover API in DOM (it does NOT check whether the API behaves correctly — see iOS 17.4–18.2). `apply()` is idempotent; calling it on a browser where it's already applied is a no-op.

## Trade-offs vs. native

The polyfill simulates the top layer using z-index promotion and inserts polyfilled CSS into the document. Differences vs. native that may matter:

- **`:popover-open` selector**: native is a CSS pseudo-class; the polyfill synthesizes it via `[popover-open]` attribute. Selectors targeting `[popover]:popover-open` will not match in polyfilled mode unless authored as `[popover][popover-open]` (or equivalent with `.popover-open`). The polyfill's CSS includes a translation, but author CSS targeting `:popover-open` directly may not transform.
- **`::backdrop`**: simulated; visual fidelity is high but not pixel-identical.
- **z-index stacking**: native uses the top layer; polyfill uses very-high z-index. If your app already has elements at extreme z-index values (modals, tooltips at z-index 99999), conflicts can occur.
- **Light-dismiss timing**: the polyfill listens for `pointerdown` on the document; very subtle differences vs. spec-defined dismiss timing. Acceptable for ~all tooltip/menu UX.

For a fresh project that targets our baseline, prefer native + close-button fallback. The polyfill is the answer when you cannot author a close-button (third-party content embed, generated UI, etc.).

## Why GitHub uses it

GitHub's audience includes long-tail enterprise browsers, locked-down corporate Windows installs, older Android WebView, etc. — populations that don't track our skill's modern baseline. The OddBird polyfill is GitHub's compatibility-floor strategy. That production exposure means the polyfill gets stress-tested at scale, which is why it's the safe default if you do need a popover polyfill.

## When to use this polyfill

- iOS Safari 17.0–18.2 light-dismiss workaround when option 1 (close button) doesn't fit your design.
- Audiences below our baseline (Safari < 17, Firefox < 125, Chrome < 114).
- Long-tail / enterprise / WebView audiences where you can't enforce a modern-browser floor.

## When NOT to use this polyfill

- Your audience matches our skill's baseline. Native is everywhere — the polyfill is bundle bloat.
- You can add an explicit close button. That's accessible AND solves the iOS 17.4–18.2 case for free.
- You depend on `popover="hint"` — the polyfill doesn't implement it (Chromium 133+ native only).
- You depend on exact native top-layer rendering, custom `::backdrop` styling, or precise `:popover-open` pseudo-class matching.

## Cross-references

- `../popover-quirks/ios-safari-light-dismiss.md` — the canonical bug this polyfill is sometimes used to work around (the practical use case at our baseline).
- `../popover-quirks/safari-focus-inputs.md` — a related iOS bug (virtual-keyboard scroll closes popover); the polyfill does NOT fix this.
- `../popover-quirks/safari-184-tab-hang.md` — Safari < 18.4 tab-out hang; the polyfill MIGHT mitigate by re-implementing focus loop, but the canonical answer is "Safari 18.4+".
- `../popover-quirks/popover-hint-chromium-only.md` — `popover="hint"` is not polyfilled here.
- `./anchor-positioning-polyfill.md` — sibling polyfill from same maintainer; popovers + anchor positioning often combined.
- `../meta/the-modern-baseline.md` — why this polyfill is mostly historical at our floor.
