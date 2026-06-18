---
date: 2026-04-27
coverage: canonical
peers:
  - ../js-language-status/iterator-helpers.md
  - ../js-language-status/set-methods.md
  - ../meta/the-modern-baseline.md
primary_sources:
  - https://github.com/tc39/proposal-regexp-v-flag — TC39 proposal (Stage 4, ES2024)
  - https://v8.dev/features/regexp-v-flag — V8 announcement (Mathias Bynens, Markus Jungmann)
  - https://tc39.es/ecma262/2024/ — ECMAScript 2024 Language Specification
  - https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp/unicodeSets — MDN unicodeSets reference
  - https://chromereleases.googleblog.com/2023/04/stable-channel-update-for-desktop_14.html — Chrome 112 stable update (April 2023)
  - https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/116 — Firefox 116 release notes (August 1, 2023)
  - https://webkit.org/blog/14445/webkit-features-in-safari-17-0/ — WebKit Features in Safari 17.0
  - https://caniuse.com/mdn-javascript_builtins_regexp_unicodesets — caniuse support table
  - https://github.com/tc39/proposal-regex-escaping — `RegExp.escape` proposal (Stage 4, February 2025)
  - https://socket.dev/blog/tc39-advances-3-proposals-to-stage-4-regexp-escaping-float16array-and-redeclarable-global-eval — Coverage of February 2025 plenary
---

# RegExp `v` flag — language status

Stage 4 / ES2024. Set notation, properties of strings, nested character classes, string-aware operations. Universal at our baseline.

## What

The TC39 [proposal-regexp-v-flag](https://github.com/tc39/proposal-regexp-v-flag) introduces a new RegExp flag, `v` (also called "unicodeSets"), that supersedes `u`. The `v` flag adds:

- **Set notation in character classes** — intersection (`&&`), subtraction (`--`), and nested classes:
  ```js
  /[\p{ASCII}--\p{White_Space}]+/v;       // ASCII minus whitespace
  /[[a-z]&&[^aeiou]]/v;                   // lowercase consonants
  /[\p{Decimal_Number}--[0-9]]/v;         // decimal digits in non-Arabic scripts
  ```
- **Properties of strings** — `\p{...}` matches multi-code-point grapheme clusters:
  ```js
  /^\p{RGI_Emoji}$/v.test('👨‍👩‍👧');         // true (ZWJ-joined family emoji)
  ```
- **String-aware operations** — `\q{string}` matches literal multi-character strings inside a character class.
- **Stricter error reporting** — ambiguous syntax that `u` silently allowed becomes a `SyntaxError` under `v`.

Mathias Bynens and Markus Jungmann at Google led the V8 implementation. Spec home: https://tc39.es/ecma262/2024/.

## TC39 stage history

| Stage | When | Note |
|---|---|---|
| Stage 1 | 2021 | Champion: Mark Davis (Unicode), Mathias Bynens, Ron Buckton |
| Stage 2 | 2022 | |
| Stage 3 | September 2022 | |
| Stage 4 | **March 2023** plenary | Included in **ES2024** |

The proposal moved relatively quickly — ~2 years from Stage 1 to Stage 4. Most engine work landed before Stage 4, which is why all three browsers shipped within ~5 months of each other in 2023.

## ECMAScript edition

**ECMAScript 2024.** Specification text at https://tc39.es/ecma262/2024/ §22 (Text Processing) — RegExp pattern grammar augmented with the `v`-flag productions.

## Engine ship matrix

| Engine | Version | Date | Source |
|---|---|---|---|
| Chrome / Edge / Chromium | **112** | April 4, 2023 | V8 12.0; https://v8.dev/features/regexp-v-flag |
| Firefox | **116** | August 1, 2023 | https://developer.mozilla.org/en-US/docs/Mozilla/Firefox/Releases/116 |
| Safari / WebKit | **17.0** | September 18, 2023 | https://webkit.org/blog/14445/webkit-features-in-safari-17-0/ |

All three engines shipped within 6 months of each other — unusually tight for a regex feature.

## Baseline status

**Baseline Newly available: September 18, 2023** (Safari 17 closing the matrix). Already **Baseline Widely available** as of early 2026 — 30 months past the last engine ship places the Widely-available milestone around March 2026.

## At our baseline (Chromium 125+ / Safari 17.4+ / Firefox 129+)

Universal. Every floor version ships the `v` flag natively:

| Engine | Floor | Native ships at | Margin |
|---|---|---|---|
| Chrome | 125 | **112** | 13 versions |
| Firefox | 129 | **116** | 13 versions |
| Safari | 17.4 | **17.0** | 0.4 versions |

**Stop polyfilling.** Use `v` directly. There is no runtime polyfill that meaningfully reproduces the `v` flag — it is a regex grammar extension implemented inside the engine. If your build target is below the modern baseline, you have to either avoid the feature or use a non-RegExp library (like `XRegExp`) for the equivalent functionality. There is no Babel transform that will lower `v` to `u`.

## Common idioms

```js
// String-aware Unicode property
/\p{Script=Greek}/v.test('α');                    // true

// Set difference: ASCII minus whitespace
/[\p{ASCII}--\p{White_Space}]+/v;

// Set intersection: lowercase consonants
/[[a-z]&&[^aeiou]]/v;

// Multi-code-point grapheme matching (ZWJ-joined emoji)
/^\p{RGI_Emoji}$/v.test('🏳️‍🌈');                   // true

// String literal in character class
/[\q{www}\q{ftp}]:\/\//v.test('www://x');         // true

// Detect support at runtime (rarely needed at this baseline)
const supportsV = (() => { try { new RegExp('', 'v'); return true; } catch { return false; } })();
```

## Caveats

- **`v` cannot combine with `u`.** They are mutually exclusive flags. `new RegExp('', 'uv')` throws `SyntaxError`. Code that programmatically composes flags (e.g., `flags + 'u'`) needs an audit.
- **Stricter syntax under `v`.** Patterns that worked under `u` may throw under `v`. Examples: unescaped `]`, `{`, `}`, and certain quantifier combinations now error. Most code is unaffected; some hand-rolled regex generators need fixing.
- **Performance.** `v` is generally as fast as `u` for the same patterns — the new features add cost only when used. No reason to avoid `v` for performance.
- **Tooling.** ESLint's `no-misleading-character-class` rule, regex linters, and source-map tools all gained `v`-flag awareness through 2023–2024. If you're on tooling pinned before mid-2024, upgrade.

## Migration from `u`

For most code, `s/u/v/g` works. To be safe:

1. Run your test suite against `v`. Stricter errors will surface real ambiguities.
2. If you hit `SyntaxError`, the pattern likely had a latent bug masked by `u`'s permissiveness.
3. If you want set notation or `\q{...}`, that's net-new — `u` does not support them.

## Related: `RegExp.escape`

The TC39 [proposal-regex-escaping](https://github.com/tc39/proposal-regex-escaping) advanced to **Stage 4 on February 18, 2025** at the TC39 plenary, alongside `Float16Array` and the redeclarable-global-eval proposal — see https://socket.dev/blog/tc39-advances-3-proposals-to-stage-4-regexp-escaping-float16array-and-redeclarable-global-eval. It is now part of **ES2025**.

`RegExp.escape(str)` returns a string with regex metacharacters escaped, suitable for embedding into a `RegExp` constructor:

```js
RegExp.escape('1.2.3');          // '\\1\\.2\\.3'
new RegExp(RegExp.escape(input)); // safe to construct from user input
```

The V8 commit landed February 12, 2025 (Chrome 134 timeframe). Firefox and Safari shipped through 2025. As of April 2026, support is still rolling into the Baseline pipeline — verify against [caniuse](https://caniuse.com/mdn-javascript_builtins_regexp_escape) before assuming universal availability. The trivial userland workaround — `str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')` — has been used for two decades and remains correct as a fallback.

## Cross-references

- Companion ES2024/ES2025 features: [`./iterator-helpers.md`](./iterator-helpers.md), [`./set-methods.md`](./set-methods.md), [`./temporal.md`](./temporal.md)
- Modern baseline definition: [`../meta/the-modern-baseline.md`](../meta/the-modern-baseline.md)
