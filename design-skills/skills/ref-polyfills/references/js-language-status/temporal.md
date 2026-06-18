---
date: 2026-04-27
coverage: canonical
peers:
  - ../runtime-polyfills/temporal-api.md
  - ../js-language-status/iterator-helpers.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://github.com/tc39/proposal-temporal — TC39 proposal repo (Stage 4)
  - https://socket.dev/blog/tc39-advances-temporal-to-stage-4 — Stage 4 advancement (March 11, 2026 plenary)
  - https://www.igalia.com/2026/03/13/Temporal-Reaches-Stage-4.html — Igalia coverage of Stage 4 outcome
  - https://tc39.es/proposal-temporal/ — Spec text
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Temporal — MDN Temporal reference
  - https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/139 — Firefox 139 release notes (May 27, 2025)
  - https://socket.dev/blog/temporal-api-ships-in-chrome-144-major-shift-for-javascript-date-handling — Chrome 144 ship (January 13, 2026)
  - https://developer.chrome.com/release-notes/144 — Chrome 144 release notes
  - https://caniuse.com/temporal — caniuse browser support
  - https://github.com/nodejs/node/issues/57127 — Node.js Temporal enablement tracking
  - https://bloomberg.github.io/js-blog/post/temporal/ — Bloomberg's Temporal retrospective (champion narrative)
---

# Temporal — language status

A namespace of immutable date/time/zone/calendar types replacing `Date`. Stage 4 as of March 2026. Native in Firefox + Chrome. Safari pending. Polyfill mandatory at our baseline.

> **For polyfill packages and bundle-size guidance, see [`../runtime-polyfills/temporal-api.md`](../runtime-polyfills/temporal-api.md).** This file covers the language-status angle — TC39 stage history, ECMA-262 placement, engine ship matrix, why Temporal exists.

## What

Temporal is a top-level namespace exposing eight types and a small set of static utilities. The core types:

| Type | Use |
|---|---|
| `Temporal.Instant` | A point in time (UTC, nanosecond-precise) |
| `Temporal.ZonedDateTime` | An instant in a specific IANA time zone |
| `Temporal.PlainDate` | A calendar date with no time, no zone |
| `Temporal.PlainTime` | A wall-clock time, no date, no zone |
| `Temporal.PlainDateTime` | A wall-clock date+time, no zone |
| `Temporal.PlainYearMonth` | A year and month (e.g., billing period) |
| `Temporal.PlainMonthDay` | A month and day (e.g., birthday without year) |
| `Temporal.Duration` | A length of time, calendar-aware |

Plus `Temporal.Now` for current readings and `Temporal.Calendar` / `Temporal.TimeZone` for protocol implementations. Spec home: https://tc39.es/proposal-temporal/.

## Why it exists

`Date` is broken in ways no library can fully patch:

- **Mutable.** `date.setMonth(1)` mutates in place, surprising consumers.
- **Conflates instants and wall times.** A `Date` is a millisecond offset from epoch; "January 5, 2026 at 9:00 AM in Tokyo" cannot be expressed as a `Date` without losing zone information.
- **String parsing is undefined behavior.** `new Date('2026-04-27')` is UTC; `new Date('2026-04-27T00:00')` is local. Engines disagree on edge cases.
- **No calendar awareness.** Hebrew, Islamic, Japanese imperial era calendars are second-class.
- **No DST primitives.** Skipped/repeated wall-clock times are silently coerced.
- **Arithmetic is broken.** "Add one month to January 31" — `Date` says March 3 in February-28 years, March 2 in leap years; no spec says it must do anything coherent.

Temporal fixes all of the above. Immutable, namespaced, calendar+zone-aware, ISO-8601-only parsing, explicit handling of DST ambiguity (`disambiguation: 'earlier' | 'later' | 'compatible' | 'reject'`).

The design is the work of nine years and seven champions including Philipp Dunkel (Bloomberg), Maggie Johnson-Pint, Matt Johnson-Pint, Brian Terlson, Shane F. Carr, Ujjwal Sharma, Philip Chimento (Igalia), Jason Williams (Bloomberg), and Justin Grant. See https://bloomberg.github.io/js-blog/post/temporal/ for the long-form retrospective.

## TC39 stage history

| Stage | When | Note |
|---|---|---|
| Stage 1 | 2017 | Original problem statement; champion Maggie Johnson-Pint |
| Stage 2 | 2018 | |
| Stage 3 | **late 2021** | Long Stage 3 dwell; spec hardening, polyfill iteration, engine implementations |
| Stage 4 | **March 11, 2026** plenary (113th, New York) | https://socket.dev/blog/tc39-advances-temporal-to-stage-4 ; https://www.igalia.com/2026/03/13/Temporal-Reaches-Stage-4.html |

The Stage 3 → 4 gap (~4.5 years) is the longest of any major recent proposal. Reason: Temporal is enormous (8 new global types, calendar/timezone protocols), engine implementations are non-trivial, and the spec uncovered subtle issues during shipping (parser ambiguities, ISO-week handling, era support) that all needed resolution before Stage 4.

## ECMAScript edition

**ECMAScript 2026.** Will be merged into ECMA-262 (parts 1, 2) and ECMA-402 (Internationalization API) for the 2026 edition. The `Intl.eraDisplay` and `monthCode` proposals also reached Stage 4 alongside Temporal at the March 2026 plenary.

## Engine ship matrix (as of April 2026)

| Engine | Version | Date | Source |
|---|---|---|---|
| Firefox | **139** | May 27, 2025 | First to ship; SpiderMonkey impl by Andre Bargull et al.; https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/139 |
| Chrome / Edge / Chromium | **144** | January 13, 2026 | V8 impl; https://socket.dev/blog/temporal-api-ships-in-chrome-144-major-shift-for-javascript-date-handling |
| Safari / WebKit | _pending_ | _not yet_ | Visible in Safari Technology Preview; not in stable Safari (incl. 26.x) as of April 2026 |
| Node.js | _flagged_ | ongoing | Node 24 has it behind `--harmony-temporal`; tracking [nodejs/node#57127](https://github.com/nodejs/node/issues/57127) |
| Deno | _shipped_ | mid-2025 | Inherits V8 once stable in Chromium |
| Bun | _flagged_ | varies | Tracks JSC; ships when Safari ships |

caniuse reports ~69% global support as of April 2026. The Safari gap is the binding constraint.

## At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+)

| Engine | Floor | Native ships at | Polyfill window |
|---|---|---|---|
| Chrome 125–143 | yes | **144** | **needs polyfill** |
| Chrome 144+ | yes | yes | none |
| Firefox 129–138 | yes | **139** | **needs polyfill** |
| Firefox 139+ | yes | yes | none |
| Safari (any current) | yes | not yet | **needs polyfill** |

**Verdict at this baseline.** Temporal is **not yet Baseline.** Polyfilling is required if you want Temporal in production today. Safari is the long pole; Chrome and Firefox at our floor will roll forward into native support as users update, but Safari has not shipped at all.

For polyfill packages and trade-offs (`@js-temporal/polyfill` ~52KB vs. `temporal-polyfill` ~20KB FullCalendar fork vs. `temporal-polyfill-lite` Gregorian-only), see [`../runtime-polyfills/temporal-api.md`](../runtime-polyfills/temporal-api.md).

## Common idioms (native or via ponyfill)

```js
// Current zoned datetime
const now = Temporal.Now.zonedDateTimeISO('America/New_York');

// Plain date arithmetic — calendar-aware
const today = Temporal.PlainDate.from('2026-04-27');
const nextWeek = today.add({ days: 7 });               // PlainDate 2026-05-04
const nextMonth = today.add({ months: 1 });            // PlainDate 2026-05-27 (calendar-coherent)

// Cross-zone scheduling
const meetingNYC = Temporal.ZonedDateTime.from({
  year: 2026, month: 5, day: 1, hour: 14,
  timeZone: 'America/New_York',
});
const meetingTokyo = meetingNYC.withTimeZone('Asia/Tokyo');
const utcInstant = meetingNYC.toInstant();

// Duration arithmetic
const project = Temporal.Duration.from({ months: 3, weeks: 2 });
const endDate = today.add(project);

// Difference (returns Duration)
const elapsed = Temporal.PlainDate.from('2026-01-01').until(today, { largestUnit: 'days' });
```

## Pitfalls and gotchas

- **`Date` and `Temporal` are not interconvertible without explicit bridges.** Use `Temporal.Instant.fromEpochMilliseconds(date.getTime())` and `instant.epochMilliseconds`. There is no `Date#toTemporal()`.
- **`Temporal.Now.zonedDateTimeISO()` returns a `ZonedDateTime`, not a `PlainDateTime`.** "Now" is always zone-bound; convert with `.toPlainDateTime()` if you need wall-clock-only.
- **String parsing is strict.** ISO 8601 only. `'2026-04-27'` works; `'04/27/2026'` does not. Use `Intl.DateTimeFormat` for localized formatting and parsing.
- **DST disambiguation is explicit.** `ZonedDateTime.from({...})` accepts a `disambiguation` option for ambiguous wall times during DST transitions. Default is `'compatible'` (matches typical user expectations) but spring-forward / fall-back code paths are now visible in the API.
- **Calendars are pluggable.** `Temporal.PlainDate.from('2026-04-27[u-ca=hebrew]')` produces a Hebrew-calendar date. Most apps stay on Gregorian; non-Gregorian support requires ICU data, which is large.
- **Performance, memory.** Each operation returns a fresh object — no in-place mutation. For tight loops over millions of dates, this matters; profile.

## Migration path off the polyfill

When Safari ships Temporal in stable, the path is:

1. **Watch the floor.** Once your support matrix's Safari minimum is the version that ships native Temporal, you can drop the polyfill.
2. **Remove the import.** Replace `import { Temporal } from '@js-temporal/polyfill'` with the global `Temporal`. With ES modules, the global resolves naturally on every supported browser.
3. **Test against the native implementation.** Spec edge cases (rounding modes, calendar arithmetic, DST disambiguation) sometimes differ subtly between polyfill versions and a fresh native implementation. Run your test suite against a native-Temporal browser before flipping the switch.
4. **For Node.js**, watch for `--harmony-temporal` to be removed (i.e., Temporal unflagged in V8).

The migration is clean because Temporal is namespaced — no global-prototype-method conflict, no built-in patching, no polyfill leakage. The cost of polyfilling is bundle size, not API hygiene. The cost of waiting is feature parity with the rest of the platform.

## Cross-references

- Polyfill packages and bundle-size trade-offs: [`../runtime-polyfills/temporal-api.md`](../runtime-polyfills/temporal-api.md)
- Modern baseline definition: [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)
- Companion ES2025/ES2026 language features: [`./iterator-helpers.md`](./iterator-helpers.md), [`./set-methods.md`](./set-methods.md), [`./regexp-v-flag.md`](./regexp-v-flag.md)
