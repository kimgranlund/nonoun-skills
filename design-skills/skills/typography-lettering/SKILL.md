---
name: typography-lettering
description: Use when working with typography at any level — choosing fonts, naming classifications, explaining anatomy or metrics, comparing approaches, pairing families, auditing legibility, specifying CSS text properties (text-wrap, text-box, initial-letter, leading-trim, font-size-adjust, metric overrides), deriving fallback stacks, applying OpenType features, wiring variable-font axes (wght/wdth/ital/slnt/opsz), handling non-Latin scripts (Arabic, CJK, Devanagari, Hebrew, Greek, Cyrillic, Thai, Hangul, Ethiopic), or reasoning about reading and legibility research-survey. Use whenever the user is choosing, comparing, pairing, explaining, or specifying type — even when they don't explicitly say "typography". Peers with ui-compose-typography (which generates scales and tokens) and ui-verify-i18n (which reasons about locale).
---

# Typography Expert

A knowledge base for typography-related work: letterforms, type systems, reading science, delivery mechanics, and the historical/script context that makes them coherent. See `references/INDEX.md` for the full reference tree; this file holds the essential knowledge to answer most questions directly.

> **Status — v1.0.0 (2026-04-18).** All 59 planned reference files shipped across 5 research-survey waves. The `references/` tree is complete and quote-able; this entry file holds the quick-reference tables and routing.
>
> **This skill answers; it does not generate.** Token math, scale derivation, axis wiring, and metric computation belong to **`ui-compose-typography`**. Locale formatting and bidirectional reasoning belong to **`ui-verify-i18n`**. Iconography alignment belongs to **`ui-compose-icons`**. Color belongs to **`color-science`**. Reach for those peers when the user wants output; reach for this skill when they want understanding.

---


## Invocation

This is an **expert-knowledge** skill. The ask touches any aspect of type — classification, metrics, pairing, web features, non-Latin scripts, legibility research-survey. Route via axis decomposition.

### Step 1 — Ingestion

Typography prompts often hide specificity:
- "What font should I use?" → for what role? display, body, or UI?
- "Fix this layout" → is it a metrics issue (x-height mismatch) or a CSS issue?
- "Variable fonts" → which axes (wght/wdth/opsz/ital)?
- "Non-Latin script" → which script? metrics, line-break, and font coverage vary wildly

### Step 2 — Decomposition

| Surface ask | Routes to |
|---|---|
| Font classification / pairing | `references/classification/`, `references/pairing/` |
| Metrics / legibility research-survey | `references/legibility/`, `references/metrics/` |
| CSS text features | `references/css-features/` |
| Variable-font axes | `references/variable-fonts/` |
| Non-Latin scripts | `references/scripts/` (Arabic, CJK, Devanagari, Hebrew, etc.) |
| OpenType features | `references/opentype/` |

### Step 3 — Execution routing

**Context Size Warning:** Expert reference files frequently exceed 1000 lines. Do not load these files entirely into context using `read_file`. Instead, use `grep_search` to surgically extract relevant sections or use chunked reading.

Peers with `ui-compose-typography` (generates scales) and `ui-verify-i18n` (script metrics). This skill answers and explains; it does not emit tokens.


## How to Read This Skill

1. Skim the quick-reference tables below — the majority of typography questions resolve there.
2. For depth, open `references/INDEX.md` and jump to the relevant axis (`contemporary/`, `historical/`, `scripts/`, `techniques/`, `classification/`, `science/`, `accessibility/`, `metrics/`, `foundries/`).
3. Every reference file is dated at the top. If the date is stale relative to the question (CSS properties, browser support, variable-font spec), flag that to the user rather than quoting blindly.
4. When a reference file doesn't exist yet, say so explicitly and either answer from general knowledge (flagging it as such) or offer to author the reference file.

---

## Quick Reference — Task → Where to Look

<!-- To be expanded in v0.2.0 once reference files exist. Skeleton only. -->

| Task | Primary reference | Supporting |
|------|-------------------|-----------|
| Choosing a body font for a UI | `references/techniques/pairing.md`, `references/techniques/measure.md` | `references/metrics/metrics-glossary.md` |
| Setting up a modular scale | *(defer to `ui-compose-typography`)* | `references/techniques/modular-scale.md` (rationale) |
| Understanding variable-font axes | `references/contemporary/variable-fonts.md` | `references/techniques/optical-size.md` |
| Picking OpenType features | `references/contemporary/opentype-features.md` | `references/techniques/figures.md`, `references/techniques/small-caps.md` |
| Metric-compatible fallback stacks | `references/techniques/fallback-stacks.md` | `references/contemporary/metric-overrides.md` |
| Modern CSS text properties | `references/contemporary/css-text-properties.md` | — |
| Font delivery (font-display, subsetting, WOFF2) | `references/contemporary/font-delivery.md` | — |
| Script-specific typographic norms | `references/scripts/<script>.md` | `references/metrics/anatomy.md` |
| Classifying a given typeface | `references/classification/bringhurst.md`, `references/classification/vox-atypi.md` | `references/historical/<era>.md` |
| Legibility & readability research-survey | `references/science/legibility-vs-readability.md` | `references/science/crowding.md` |
| Accessibility — dyslexia, low vision | `references/accessibility/dyslexia.md`, `references/accessibility/low-vision.md` | `references/accessibility/wcag-type.md` |
| Pairing two families | `references/techniques/pairing.md` | `references/metrics/metrics-glossary.md` |
| Vertical rhythm and baseline | `references/techniques/vertical-rhythm.md` | `references/metrics/metrics-glossary.md` |
| Measure (CPL) | `references/techniques/measure.md` | `references/science/crowding.md` |
| Historical era of a typeface | `references/historical/<era>.md` | `references/foundries/canon-designers.md` |
| Type-designer or foundry lookup | `references/foundries/canon-designers.md`, `references/foundries/contemporary-foundries.md` | — |
| Color-font rendering (COLRv1 / SVG / sbix) | `references/contemporary/color-fonts.md` | `references/contemporary/font-palette.md` |

---

## Quick Reference — Metrics Cheat Sheet

<!-- Stub. Full glossary in references/metrics/metrics-glossary.md after Phase 2. -->

| Metric | Short definition | Why it matters |
|--------|------------------|----------------|
| UPM (Units Per Em) | Internal design grid of the font (commonly 1000 or 2048) | Divides all other metrics; different UPMs aren't directly comparable |
| x-height | Height of lowercase `x` relative to em | Primary driver of perceived size and legibility at small sizes |
| Cap height | Height of uppercase letters | Matters for UI where caps sit alongside icons |
| Ascender height | Top of `h`, `l`, `k` | Should not collide with line above |
| Descender depth | Bottom of `g`, `y`, `p` | Should not collide with line below |
| Overshoot | Extension of round forms beyond flat forms | Optical correction — rounds look smaller without it |
| Sidebearing | Space on either side of a glyph | Driver of letter spacing/tracking |
| Advance width | Horizontal step after a glyph | Basis of `ch` unit |
| Optical size | Design variant tuned for a specific size range | Use `font-optical-sizing: auto` or explicit `opsz` |

(Full anatomy — stem/apex/vertex/bowl/counter/aperture/spur/ear/eye/tail/terminal/finial/crossbar/crotch — lives in `references/metrics/anatomy.md`.)

---

## Quick Reference — CSS Text Surface (as of 2026-04)

<!-- Stub. Authoritative detail + dated browser support matrix in references/contemporary/css-text-properties.md. -->

| Property / At-rule | Purpose | Notes |
|---------------------|---------|-------|
| `font-optical-sizing` | Auto-activates `opsz` axis when present | Default `auto` is usually right |
| `font-variation-settings` | Custom-axis control (and fallback for registered axes on old UAs) | Prefer high-level props (`font-weight`, `font-stretch`, `font-style`) when available |
| `font-feature-settings` | OpenType feature toggles | Prefer high-level props (`font-variant-*`) where they exist |
| `font-palette` + `@font-palette-values` | Color-font palette selection | Works with COLRv1 fonts |
| `font-size-adjust` | Normalize perceived size across families by x-height ratio | Critical for fallback stacks |
| `@font-face` metric overrides (`ascent-override`, `descent-override`, `line-gap-override`, `size-adjust`) | Tune the fallback to match the primary font's box | Reduces layout shift on font-swap |
| `text-wrap: pretty` / `balance` | Improve paragraph raggedness and heading balance | Implemented widely; `pretty` is newer |
| `text-box` / `text-box-trim` / `text-box-edge` | Trim leading half-leading and descender space from first/last line | Replaces ad-hoc negative-margin hacks |
| `leading-trim` *(older name)* | See `text-box-trim` | Renamed; prefer `text-box-*` |
| `initial-letter` | Drop-cap / raised-cap layout | Composes with `text-box` |
| `hanging-punctuation` | Pull quotes/periods outside the text box | Good for editorial layouts |
| `word-break: auto-phrase` | Phrase-aware line breaking (CJK + some Latin patterns) | Ship behind a check |
| `font-display` | Swap/fallback/optional/block/auto during font load | Default varies; pick explicitly |
| `font-synthesis-*` | Control synthetic bold/italic/small-caps | Turn off for proper families; on for fallback robustness |

(Each entry needs a dated browser-support note in `references/contemporary/css-text-properties.md` before being cited for production.)

---

## Quick Reference — Variable-Font Registered Axes

<!-- Stub. Custom axes and interpolation semantics in references/contemporary/variable-fonts.md. -->

| Axis | CSS property | Typical range | When to use |
|------|--------------|---------------|-------------|
| `wght` | `font-weight` | 1–1000 (100–900 common) | Everywhere; primary hierarchy driver |
| `wdth` | `font-stretch` | 50–200 (% of normal) | Density shifts, headlines, column fitting |
| `ital` | `font-style: italic` | 0–1 (discrete) | True italic vs roman |
| `slnt` | `font-style: oblique <deg>` | -15 to 0 (typical) | Oblique only; not a substitute for `ital` when a true italic exists |
| `opsz` | `font-optical-sizing` | Design-defined | Let `auto` switch optical variants at size breakpoints |

---

## Quick Reference — Script Depth Declaration

<!-- Honest coverage tier per script. Updated as reference files land. -->

| Script | Coverage tier | Notes |
|--------|---------------|-------|
| Latin | *(planned — deep)* | UI default; widest type availability |
| Cyrillic | *(planned — medium)* | Italics vs italics, superscript usage |
| Greek | *(planned — medium)* | Polytonic diacritics, Greek question mark |
| Arabic | *(planned — medium)* | Four contextual forms, connected-script rules, nastaliq/naskh/kufi |
| Hebrew | *(planned — medium)* | Niqqud, cantillation, RTL |
| Devanagari | *(planned — medium)* | Shirorekha, conjuncts, vowel-sign placement |
| Thai | *(planned — medium)* | Three-level mark stack (tone over vowel over base), no word spaces |
| CJK (Han) | *(planned — medium)* | Simplified vs traditional, fullwidth punctuation, vertical text |
| Japanese | *(planned — medium)* | Kanji + hiragana + katakana + romaji, ruby, tategaki |
| Hangul | *(planned — light)* | Jamo composition, spacing rules |
| Ethiopic | *(planned — stub)* | Pointer to external resources |

> **Honesty rule.** When asked about a script with lighter coverage than the question warrants, say so and point the user to the authoritative external source rather than extrapolating.

---

## Classifications — When They Disagree

<!-- Stub. Full treatment in references/classification/. -->

| System | Strength | Weakness |
|--------|----------|----------|
| Vox-ATypI (1954 → 2010 update) | Broad acceptance; international | Coarse on post-1960 design; weak on sans subfamilies |
| Bringhurst (*The Elements of Typographic Style*) | Historically grounded, readable | Author-opinionated; overlaps Vox |
| DIN 16518 (1964) | Mechanical and unambiguous | Very Germanic; pre-digital |
| Thibaudeau (1921) | Useful for silhouette identification | Obsolete for modern design detail |

**When to name a typeface:** use Bringhurst or Vox-ATypI in prose; use DIN when an unambiguous mechanical category is required.

---

## Principles

- **Knowledge first, generation elsewhere.** This skill answers and explains. When the user needs computed tokens, hand off to `ui-compose-typography`.
- **Dated claims only.** CSS, variable-font specs, and browser support change. Every reference file is dated; quote the date when citing.
- **Script depth is declared, not assumed.** Latin is deep; other scripts are marked by coverage tier. Don't pretend equal depth.
- **Name the camps.** Pairing, dyslexia-font efficacy, word-shape vs parallel-letter recognition — there are two-or-more honest positions on each. Describe the positions and the tradeoffs, don't pick one for the user.
- **Foundry neutrality.** Name foundries and designers when citing fact. Don't promote commercial fonts beyond what the user's context warrants.
- **History contextualizes, doesn't dictate.** A typeface's era informs expectation; it doesn't constrain use.

---

## Composition

| Scenario | Chain |
|----------|-------|
| User wants a type *system* (scale, rhythm, tokens) | `typography-lettering` (for principles) → `ui-compose-typography` (for output) |
| User wants a type *audit* of an existing UI | `typography-lettering` → `ui-audit-quality` |
| User wants locale-safe type across scripts | `typography-lettering` (script norms) + `ui-verify-i18n` (locale formatting) |
| User wants icons aligned to text | `typography-lettering` (metrics) → `ui-compose-icons` |
| User wants color + type coherence | `typography-lettering` + `color-science` |

---

## What's Not In This Skill

- **Token math and scale generation** — see `ui-compose-typography`.
- **Locale-sensitive formatting** (dates, numbers, pluralization, bidi algorithm) — see `ui-verify-i18n`.
- **Brand-level voice and tone** (what to *say*, not how to set it) — see `ui-compose-voice`.
- **Icon system derivation** — see `ui-compose-icons`.
- **Color choices** — see `color-science` and `ui-verify-color`.

---

<!--
IMPLEMENTATION STATUS — v0.1.0 skeleton (2026-04-17)

This file is intentionally skeletal. In Phase 2:
  1. Reference agents populate references/*/*.md in parallel.
  2. Each quick-reference table above is replaced with dense tables synthesized from the references.
  3. Script-depth declaration updates as coverage lands.
  4. Dated-claims discipline starts enforcing at this version.
-->
