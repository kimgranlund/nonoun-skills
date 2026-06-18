---
date: 2026-04-27
coverage: extended
peers:
  - ../meta/the-modern-baseline.md
  - ../meta/decision-tree.md
  - ../feature-detection/js-feature-detection.md
  - ../anti-patterns/defensive-overpolyfilling.md
primary_sources:
  - https://developer.mozilla.org/en-US/docs/Web/API/CompressionStream — MDN CompressionStream reference
  - https://developer.mozilla.org/en-US/docs/Web/API/DecompressionStream — MDN DecompressionStream reference
  - https://wicg.github.io/compression/ — Compression Standard (WICG)
  - https://caniuse.com/mdn-api_compressionstream — Browser support data
  - https://developer.chrome.com/blog/compression-streams-api — Chrome team announcement (Chrome 80, Feb 2020)
  - https://web.dev/blog/compressionstreams — web.dev "Compression Streams are now supported on all browsers" (May 2023)
  - https://developer.apple.com/documentation/safari-release-notes/safari-16_4-release-notes — Safari 16.4 release notes (March 27, 2023)
  - https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/113 — Firefox 113 release notes (May 9, 2023)
  - https://github.com/nodeca/pako — `pako` zlib port to JavaScript
  - https://www.npmjs.com/package/pako — npm package
  - https://github.com/101arrowz/fflate — `fflate` modern alternative
  - https://github.com/mdn/browser-compat-data/issues/26994 — Safari 18.4 brotli format support
---

# Compression Streams API — STOP polyfilling, replace `pako`

The Compression Streams API exposes the gzip / deflate / deflate-raw codecs the browser already has, as a `TransformStream`. It's been Baseline Widely Available since May 2023. At our baseline, **stop polyfilling, and migrate off `pako` if you have it.** This file covers the verdict, the migration, and when `pako` / `fflate` still earn their keep.

## What the Compression Streams API is

`CompressionStream` and `DecompressionStream` are `TransformStream` constructors that wrap the browser's native zlib implementation:

```js
// Compress
const stream = blob.stream().pipeThrough(new CompressionStream('gzip'));
const compressed = new Response(stream).blob();

// Decompress
const stream = response.body.pipeThrough(new DecompressionStream('gzip'));
const text = await new Response(stream).text();
```

Three codecs are universally supported:

| Format | What it is |
|---|---|
| `'gzip'` | Standard RFC 1952 gzip — header + DEFLATE + CRC32 + length |
| `'deflate'` | Standard RFC 1950 zlib — header + DEFLATE + Adler-32 |
| `'deflate-raw'` | Raw RFC 1951 DEFLATE — no header, no checksum |

Safari 18.4 added `'brotli'` (see [browser-compat-data #26994](https://github.com/mdn/browser-compat-data/issues/26994)); the older three are universal.

Why it matters:

- **No JS runtime cost.** The browser's already-shipped zlib (typically a system or libdeflate-derived implementation) does the work. No DEFLATE state machine in your bundle.
- **Streaming.** The API is a `TransformStream`, so you compress / decompress data as it flows. No need to buffer a full payload before processing.
- **Universal target.** Web Workers, Service Workers, fetch streams, `ReadableStream` from anywhere — all interoperate.

Spec home: [WICG/compression](https://wicg.github.io/compression/) (now standards-track).

## Native shipping status (as of April 2026)

| Engine | Version | Date | Notes |
|---|---|---|---|
| **Chrome / Edge** | **80** | **February 4, 2020** | First to ship. Six years of Chromium support. |
| **Safari** | **16.4** | **March 27, 2023** | https://developer.apple.com/documentation/safari-release-notes/safari-16_4-release-notes |
| **Firefox** | **113** | **May 9, 2023** | https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/113 |

**Baseline Newly available: May 2023** (the day Firefox 113 closed the cross-engine gap). **Baseline Widely available since approximately November 2025** (~30 months after Newly available, the standard Baseline graduation cadence). See https://web.dev/blog/compressionstreams.

## At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+)

| Engine | Floor | Native ships at | Verdict |
|---|---|---|---|
| Chrome | 125 | **80** (Feb 2020) | predates baseline by 45 versions / 4 years |
| Safari | 17.4 | **16.4** (March 2023) | predates baseline by 1 major version / 1 year |
| Firefox | 129 | **113** (May 2023) | predates baseline by 16 versions / ~14 months |

**Every engine ships Compression Streams natively at every version that meets our baseline.** There is no polyfill window. Shipping a JS-runtime gzip implementation at this baseline is shipping bytes that cannot help any user the baseline is configured for.

> **Stop polyfilling Compression Streams at this baseline. If your bundle has `pako`, audit whether it still earns its keep.**

## The `pako` migration story

[`pako`](https://github.com/nodeca/pako) is the canonical pure-JS zlib port — high quality, widely used, and (importantly for this skill) **larger than the native API it duplicates**.

| Field | Value |
|---|---|
| Repository | https://github.com/nodeca/pako |
| npm | https://www.npmjs.com/package/pako |
| Latest version | 2.1.0 |
| License | (MIT AND Zlib) |
| Bundle size | ~45 KB minified, ~22 KB minified+gzipped (full inflate+deflate) |
| Standalone deflate | ~10 KB minified+gzipped |
| Standalone inflate | ~12 KB minified+gzipped |
| Runtime | Pure JS, ports zlib's C source line-by-line |

`pako` was the right answer **before May 2023**. At our baseline, you have native APIs that do the same job in C — faster, smaller (zero-byte cost in your bundle), and streaming-by-design.

### Drop-in replacements

```js
// Before — pako
import pako from 'pako';
const compressed = pako.gzip(data);              // Uint8Array → Uint8Array
const decompressed = pako.ungzip(compressedData); // Uint8Array → Uint8Array

// After — native, async (the whole API is stream-based)
async function gzip(uint8) {
  const stream = new Blob([uint8]).stream().pipeThrough(new CompressionStream('gzip'));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}

async function ungzip(uint8) {
  const stream = new Blob([uint8]).stream().pipeThrough(new DecompressionStream('gzip'));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}
```

The native API is **always async** — the streaming model demands it. If your call sites assume synchronous `pako.gzip(...) → Uint8Array`, you must refactor to `await`. This is the only material API gap.

### Performance reality check

`CompressionStream` is roughly twice as fast as `pako` for streaming workloads, per the [Wikimedia evaluation](https://phabricator.wikimedia.org/T235237) and Chrome team benchmarks (compressing 800 KB of HTML in ~40 ms with `CompressionStream` vs ~100 ms with `pako`). For data already loaded into memory, [`fflate`](https://github.com/101arrowz/fflate) is sometimes competitive or faster than the native API due to marshalling overhead in `Blob`/`Response` round-trips. If you measure a hot path showing native is slower, the answer may be to skip the `Blob` wrapper and pipe straight from a `ReadableStream`, not to keep `pako`.

## Feature detection

The canonical idiom:

```js
if ('CompressionStream' in globalThis) {
  // native available
}
```

For `'brotli'` support specifically (Safari 18.4+ only at baseline):

```js
function supportsBrotli() {
  if (!('CompressionStream' in globalThis)) return false;
  try {
    new CompressionStream('brotli');
    return true;
  } catch {
    return false;
  }
}
```

The `try/catch` is necessary — engines throw on unsupported format strings. See [`../feature-detection/js-feature-detection.md`](../feature-detection/js-feature-detection.md) for general patterns.

## When `pako` / `fflate` still earn their keep

- **Node.js without Web Streams.** If you target Node.js < 18 (which doesn't expose `CompressionStream` globally), use Node's built-in `zlib` module instead — `pako` is rarely the right answer in Node when `require('zlib')` is one line away. From Node 18+, `CompressionStream` is global.
- **Synchronous API requirement.** If you cannot refactor call sites to be async (e.g., a tight synchronous library boundary), `pako`'s sync API is irreplaceable. `fflate` also offers sync compression with a smaller bundle (~8 KB minified for the core; ~3 KB for decompression-only).
- **Sub-baseline support.** If your support matrix dips below Safari 16.4 / Firefox 113 / Chrome 80, you still need a JS runtime fallback. Use feature detection + dynamic import:
  ```js
  async function gzipUniversal(data) {
    if ('CompressionStream' in globalThis) {
      const stream = new Blob([data]).stream().pipeThrough(new CompressionStream('gzip'));
      return new Uint8Array(await new Response(stream).arrayBuffer());
    }
    const { gzip } = await import('pako');
    return gzip(data);
  }
  ```
  At our baseline, the dynamic-import branch is dead code — bundlers split it into a chunk that nobody fetches. Cost on modern browsers: zero bytes.
- **Brotli compression** at write side. Native `CompressionStream` brotli is **read-only** in Safari (decompression yes, compression no in some engines); for write-side brotli you may still need a WASM library. Verify against your specific target.
- **Specific zlib options.** `pako` exposes `level`, `dictionary`, `windowBits`, etc. The native API does not — the format is fixed. If your protocol requires a specific dictionary or window size, native won't work.

For 95%+ of "compress this payload before posting it" / "decompress this gzipped response" cases, native is the answer. The above are the genuine exceptions.

## When NOT to polyfill — concrete checks

If your `package.json` includes `pako` and your `browserslist` is modern, audit for these patterns and migrate them:

```js
// 1. Compressing fetch bodies
//    BEFORE
const body = pako.gzip(JSON.stringify(payload));
fetch(url, { method: 'POST', body, headers: { 'Content-Encoding': 'gzip' } });

//    AFTER
const stream = new Blob([JSON.stringify(payload)])
  .stream()
  .pipeThrough(new CompressionStream('gzip'));
fetch(url, { method: 'POST', body: stream, headers: { 'Content-Encoding': 'gzip' }, duplex: 'half' });
```

```js
// 2. Decompressing a gzipped response
//    BEFORE
const buffer = await response.arrayBuffer();
const text = new TextDecoder().decode(pako.ungzip(new Uint8Array(buffer)));

//    AFTER
const stream = response.body.pipeThrough(new DecompressionStream('gzip'));
const text = await new Response(stream).text();
```

```js
// 3. Compressing IndexedDB blobs
//    BEFORE
const compressed = pako.deflate(uint8Array);
db.put({ data: compressed });

//    AFTER
const stream = new Blob([uint8Array]).stream().pipeThrough(new CompressionStream('deflate'));
const compressed = new Uint8Array(await new Response(stream).arrayBuffer());
db.put({ data: compressed });
```

The migration mostly entails marking call-sites `async` and accepting the streaming API shape. Bundle savings are ~22 KB gzipped if you used `pako` for both deflate and inflate. For an app whose total JS is 100–300 KB gzipped, that is a 7–22% bundle reduction from a single dependency removal.

## Pitfalls and gotchas

- **`fetch` body streams require `duplex: 'half'`.** When passing a `ReadableStream` as the request body, modern Chrome / Safari / Firefox all require the `duplex: 'half'` option. Forgetting it throws a `TypeError`. This is unrelated to Compression Streams but bites people migrating from `pako` because suddenly their `fetch` bodies are streams.
- **Format strings are case-sensitive.** `new CompressionStream('GZIP')` throws. Spec mandates lowercase: `'gzip'`, `'deflate'`, `'deflate-raw'`.
- **`'deflate'` ≠ `'deflate-raw'`.** `'deflate'` writes the zlib (RFC 1950) header; `'deflate-raw'` writes pure DEFLATE (RFC 1951). HTTP `Content-Encoding: deflate` is **historically ambiguous** — some servers send raw, some send zlib-wrapped. If you decompress server responses with `'deflate'` and get garbage, try `'deflate-raw'`. `pako`'s heuristic auto-detects; the native API does not.
- **CRC and length integrity.** `'gzip'` validates CRC32 and length on decompression and throws on mismatch — `pako` has the same behavior, but quietly with a different error type. If you depended on `pako`'s exception shape for error handling, the catch will need updating.
- **Memory profile.** The streaming model means peak memory is "one chunk at a time," roughly 16–64 KB. `pako`'s sync API requires the entire input/output in memory at once. For large blobs (multi-MB), native is significantly more memory-efficient.
- **Older Safari quirks.** Safari 16.4 was the first version with `CompressionStream`. Subtle bugs around stream backpressure existed in 16.4–16.6 release variants; if you support those exact versions and observe corruption with very large inputs, fall back to `pako` for that narrow window. At our baseline (Safari 17.4+) this is not a concern.
- **Brotli is partial.** `'brotli'` decompression shipped in Safari 18.4 (March 2025). It is **not Baseline** as of April 2026. For brotli today, you still need a WASM library (e.g., [`brotli-wasm`](https://www.npmjs.com/package/brotli-wasm)) or to decompress at the server.

## TL;DR

If you are using `pako` in a project that targets the modern baseline, **migrate to `CompressionStream`**. Refactor to async; delete the dependency; save 20+ KB gzipped. Keep `pako` only for synchronous-API hot paths or sub-baseline support. If you are starting fresh in 2026, do not reach for `pako` — the native API has been Baseline Widely available for over a year.

## Cross-references

- [`../feature-detection/js-feature-detection.md`](../feature-detection/js-feature-detection.md) — `'CompressionStream' in globalThis` idiom
- [`../anti-patterns/defensive-overpolyfilling.md`](../anti-patterns/defensive-overpolyfilling.md) — shipping `pako` to modern browsers is the same family of mistake as shipping `core-js/stable`
- [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md) — Compression Streams is one of the major Baseline-since-2023 features
- Companion runtime polyfills (clean ponyfill stories, where polyfill IS warranted): [`./temporal-api.md`](./temporal-api.md), [`./urlpattern.md`](./urlpattern.md)
