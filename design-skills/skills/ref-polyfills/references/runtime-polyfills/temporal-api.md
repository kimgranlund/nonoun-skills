---
date: 2026-04-27
coverage: canonical
peers:
  - ../js-language-status/temporal.md
  - ../meta/the-modern-baseline.md
  - ../meta/decision-tree.md
primary_sources:
  - https://github.com/tc39/proposal-temporal — TC39 proposal (Stage 4) and champions group
  - https://github.com/js-temporal/temporal-polyfill — Champion-maintained `@js-temporal/polyfill` source
  - https://www.npmjs.com/package/@js-temporal/polyfill — Package, version, license, downloads
  - https://www.npmjs.com/package/temporal-polyfill — FullCalendar's lightweight alternative
  - https://socket.dev/blog/temporal-api-ships-in-chrome-144-major-shift-for-javascript-date-handling — Chrome 144 launch coverage
  - https://socket.dev/blog/tc39-advances-temporal-to-stage-4 — Stage 4 promotion (March 2026)
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Temporal — MDN reference
  - https://caniuse.com/temporal — Browser support matrix
  - https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/139 — Firefox 139 release notes
  - https://developer.chrome.com/release-notes/144 — Chrome 144 release notes
  - https://github.com/nodejs/node/issues/57127 — Node.js Temporal enablement tracking issue
---

# Temporal API — the `Date` replacement

## What Temporal is

Temporal is the TC39 proposal that replaces the JavaScript `Date` object. It is the result of a nine-year effort by champions including Philipp Dunkel, Maggie Johnson-Pint, Matt Johnson-Pint, Brian Terlson, Shane Carr, Ujjwal Sharma, Philip Chimento, Jason Williams, and Justin Grant.

The design fixes everything `Date` got wrong:

- **Immutable.** Operations return new objects; never mutate.
- **Distinguishes instants from local times.** `Temporal.Instant`, `Temporal.ZonedDateTime`, `Temporal.PlainDate`, `Temporal.PlainTime`, `Temporal.PlainDateTime`, `Temporal.PlainYearMonth`, `Temporal.PlainMonthDay`, `Temporal.Duration` are distinct types — you cannot accidentally mix wall-clock time with a UTC instant.
- **Calendar-aware.** First-class support for non-Gregorian calendars (Hebrew, Islamic, Japanese, etc.) via the Calendar protocol.
- **Time-zone-aware.** `Temporal.ZonedDateTime` carries an IANA time zone, not just an offset. Daylight-saving transitions, ambiguous wall-clock times, and skipped wall-clock times are explicitly modeled.
- **Sane parsing.** ISO 8601 only. No string-format guessing. No `new Date('2026-04-27')` vs `new Date('2026-04-27T00:00')` UTC-vs-local foot-gun.
- **Sane arithmetic.** `date.add({months: 1})` and `date.until(other, {largestUnit: 'days'})` work the way you think they should.

Spec home: https://tc39.es/proposal-temporal/. Repo: https://github.com/tc39/proposal-temporal.

## TC39 stage status

**Stage 4 — March 11, 2026.** Approved at the TC39 March 2026 plenary; will be merged into ECMA-262 / ECMA-402 as part of ECMAScript 2026. See https://socket.dev/blog/tc39-advances-temporal-to-stage-4. (Note: many older articles — including Socket's own pre-March-2026 piece on Chrome 144 — still list Stage 3; that snapshot is outdated.)

## Native shipping status (as of April 2026)

| Engine | Version | Date | Notes |
|---|---|---|---|
| **Firefox** | **139** | **May 27, 2025** | First browser to ship Temporal by default. SpiderMonkey implementation by Andre Bargull et al.; tracking bug [Bugzilla 1519167](https://bugzilla.mozilla.org/show_bug.cgi?id=1519167). |
| **Chrome / Edge** | **144** | **January 13, 2026** | V8 implementation. See https://developer.chrome.com/release-notes/144 and https://chromereleases.googleblog.com/2026/01/stable-channel-update-for-desktop_13.html. |
| **Safari** | _pending_ | _not yet_ | Visible in Safari Technology Preview but not yet enabled in stable Safari (including Safari 26.x as of April 2026). |
| **Node.js** | _flagged_ | _ongoing_ | Available in Node.js 24 behind `--harmony-temporal`. Tracking issues: [nodejs/node#57127](https://github.com/nodejs/node/issues/57127) ("Let's enable Temporal by default") and [nodejs/node#57891](https://github.com/nodejs/node/issues/57891) ("Support Temporal across Node.js APIs"). Unflagged enablement expected once V8 ships it stably. |

caniuse currently reports ~69% global usage — the "Safari pending" gap is the binding constraint at our baseline.

## Verdict against the modern baseline

Our baseline is **Chromium 125+ / Safari 17.4+ / Firefox 129+ (April 2024 floor)**.

- Chrome 125 → Chrome 143: **needs polyfill**. Native ships Chrome 144 (January 2026).
- Firefox 129 → Firefox 138: **needs polyfill**. Native ships Firefox 139 (May 2025).
- Safari 17.4 → all current Safari: **needs polyfill**. Native has not shipped.

Temporal is a **canonical polyfill candidate** at this baseline. There is no version of any of the three engines, at our floor, that ships it natively. This will change for Chrome and Firefox as user populations roll forward, but Safari is the long pole — until Safari ships, you must polyfill if you want Temporal in production.

## Polyfill: `@js-temporal/polyfill`

The TC39-champion-maintained polyfill. Authored alongside the spec by the same people writing it; the closest you can get to a reference implementation.

| Field | Value |
|---|---|
| npm | https://www.npmjs.com/package/@js-temporal/polyfill |
| Repository | https://github.com/js-temporal/temporal-polyfill |
| Latest version | 0.5.1 |
| License | ISC |
| Bundle size | ~52 KB minified+gzipped (per Bundlephobia; full Gregorian + non-Gregorian calendars + ICU integration) |
| Spec compliance | Tracks the proposal closely; updated as spec evolves |
| Maintainers | Philipp Dunkel (author), Justin Grant, Philip Chimento, Shane F. Carr, Ujjwal Sharma, plus other proposal champions |

The package note historically said "not for production use" pending Stage 4. With Stage 4 secured March 11, 2026, expect a 1.0.0 release tracking the final ECMA-262 spec.

### Alternative: `temporal-polyfill` (FullCalendar)

A leaner alternative maintained by the FullCalendar team. Different trade-offs.

| Field | Value |
|---|---|
| npm | https://www.npmjs.com/package/temporal-polyfill |
| Repository | https://github.com/fullcalendar/temporal-polyfill |
| Bundle size | ~20 KB minified+gzipped (~62% smaller than `@js-temporal/polyfill`) |
| License | MIT |
| Trade-off | Smaller bundle; spec coverage closes against `@js-temporal` over time. Designed with bundle-size-conscious library authors in mind. |

If you are **a library author** redistributing Temporal via your own package, prefer `temporal-polyfill` for the size win. If you are **an application author** and want to be on the safest bet against spec drift, use `@js-temporal/polyfill`.

### Even smaller: `temporal-polyfill-lite`

For Gregorian-only use cases, https://github.com/fabon-f/temporal-polyfill-lite is ~10% smaller than FullCalendar's polyfill. Drops non-Gregorian calendars. Niche; verify your locale needs before adopting.

## When to use the polyfill

Use it when **all three** of the following are true:

1. You ship to browsers, and your support matrix includes any of: Chrome ≤ 143, Firefox ≤ 138, all current Safari versions.
2. You actually want Temporal's API. (If you are reaching for `Luxon` or `date-fns` and have no specific need for IANA-zone correctness, calendar awareness, or duration arithmetic, the polyfill cost may not be worth it — see below.)
3. You can absorb the bundle cost: ~20–52 KB gzipped lands in the 0.5–2% of typical app bundles.

## When NOT to polyfill

- **Server-side Node.js generally.** Use the date library you already have (`date-fns`, `Luxon`, `dayjs`) until Node.js ships Temporal unflagged. Node 24 has Temporal behind `--harmony-temporal`; running with that flag is fine for servers under your full control, but unconditionally requiring the polyfill in a `package.json` you ship through npm pollutes downstream consumers.
- **You don't need Temporal's specific guarantees.** If your "date logic" is `formatDistance(then, now)` and "is today after this date", `date-fns` (~14 KB tree-shaken) or `dayjs` (~3 KB) is fine. The polyfill's correctness benefits compound only when you do real date arithmetic across time zones, calendars, or DST transitions.
- **Your app already ships `Luxon` for IANA-zone work.** Don't add Temporal as a second source of truth. Pick one. Migrate to native Temporal once Safari ships.

## Code examples

### Explicit-import (recommended)

```js
import { Temporal } from '@js-temporal/polyfill';

const today = Temporal.PlainDate.from('2026-04-27');
const oneMonthLater = today.add({ months: 1 });
console.log(oneMonthLater.toString()); // '2026-05-27'

const meeting = Temporal.ZonedDateTime.from({
  year: 2026, month: 5, day: 1, hour: 14,
  timeZone: 'America/Los_Angeles',
});
const inUTC = meeting.toInstant();
```

This pattern is a **ponyfill** — it does not mutate globals. The polyfill object is scoped to the import. When you migrate off later, you change one line.

### Global-pollution (auto-shim)

The package also exposes a side-effect form that polyfills `globalThis.Temporal`:

```js
import '@js-temporal/polyfill/global';
// Temporal is now available globally
const today = Temporal.PlainDate.from('2026-04-27');
```

Avoid this in libraries. Acceptable in application entry points if you are sure no other code in your dependency tree polyfills `Temporal` differently.

### Feature-detect + dynamic import

For applications where you want to skip the polyfill cost on browsers that already ship Temporal natively:

```js
let Temporal;
if ('Temporal' in globalThis) {
  Temporal = globalThis.Temporal;
} else {
  ({ Temporal } = await import('@js-temporal/polyfill'));
}
```

The dynamic-import branch is split-bundled by every modern bundler; the polyfill is only fetched on browsers that need it. As Safari ships, this form's payoff grows.

## Migration path off the polyfill

1. **Watch the floor.** When your support matrix's Safari minimum is ≥ the version that first ships native Temporal, you can drop the polyfill.
2. **Remove the import.** With ES modules, you do not need `if (Temporal in window)` runtime checks if the import is gone — the global resolves naturally on every supported browser.
3. **Test against the native implementation.** Spec edge cases (rounding modes, calendar arithmetic) sometimes differ subtly between the polyfill and a fresh native implementation. Run your existing test suite against a native-Temporal browser before flipping the switch in production.
4. **For Node.js**, watch for `--harmony-temporal` to be removed (i.e., Temporal unflagged in V8). Tracking issue: https://github.com/nodejs/node/issues/57127.

The migration is easy because Temporal is namespaced. There is no global-prototype-method conflict, no built-in patching, no polyfill leakage to worry about. The cost of polyfilling is bundle size, not API hygiene.

## Pitfalls and gotchas

- **Don't mix `Date` and `Temporal`.** They are not interconvertible without explicit conversion. Use `Temporal.Instant.fromEpochMilliseconds(date.getTime())` and `instant.epochMilliseconds` as the bridge. See the `Date` interop section in the proposal docs.
- **`Temporal.Now.zonedDateTimeISO()` returns a `ZonedDateTime`** — not a `PlainDateTime`. The "now" of a particular zone is always zone-bound; convert with `.toPlainDateTime()` if you need a wall-clock-only value.
- **String formats are strict.** ISO 8601 only. `'2026-04-27'` works; `'04/27/2026'` does not. Localized formatting goes through `Intl.DateTimeFormat` — Temporal types implement `[Symbol.toPrimitive]` and pass cleanly into `Intl.DateTimeFormat#format`.
- **The polyfill is large.** Audit your bundle. If you are using Temporal only for `Temporal.Now.plainDateISO()` and a couple of `.add({days: 7})` calls, `dayjs` is genuinely smaller. Polyfill cost is highest for apps that benefit least.
- **Calendar bundles vary.** `@js-temporal/polyfill` includes ICU calendar data (Hebrew, Islamic, Japanese, etc.) which is a large fraction of its size. `temporal-polyfill-lite` strips this. If you only need Gregorian, you can bundle-shave.

## Cross-references

- TC39 stage / language status: `../js-language-status/temporal.md`
- Decision tree for "do I need to polyfill X?": `../meta/decision-tree.md`
- Why Node.js polyfilling is usually wrong: `../meta/the-modern-baseline.md`
- Ponyfill pattern explainer: `../feature-detection/ponyfill-pattern.md`
