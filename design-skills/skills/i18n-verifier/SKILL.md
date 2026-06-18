---
name: i18n-verifier
description: Reason about the locale-shaped primitives a UI system must absorb — bidirectionality, script-specific metrics, locale-sensitive number/date/currency formatting, pluralization, and text-expansion budgets — and emit the invariants other composition skills must honor. Use when a UI system must hold up across scripts and locales without being re-authored per locale.
---

# i18n-verifier

Reasoning skill that owns the *locale* layer of ui-dev. It does not translate content; it constrains how every other skill must behave so that translated content, locale-formatted numbers, bidi text, and non-Latin scripts compose cleanly. Upstream: UISchema, BrandSchema, `color-verifier` (for writing-direction-independent iconography cues). Downstream: `ui-compose-typography`, `ui-compose-spacing`, `ui-compose-icons`, `ui-build-theme`, `ui-audit-quality`.


## Invocation

This is a **constraint** decomposition skill. The user needs locale-shaped primitives. Decompose: (1) identify script and directionality requirements, (2) define text-expansion budgets, (3) specify locale-sensitive formatting, (4) enumerate plural/list categories.

### Step 1 — Ingestion

Classify the ask surface:
- "RTL needed" → determine bidi requirements; physical properties forbidden
- "Non-Latin script" → font coverage, line-break rules, vertical text if CJK
- "Copy expansion" → per-locale budgets for translation
- "Number/date formatting" → `Intl` API wiring; locale-sensitive parsing

### Step 2 — Decomposition

| Sub-ask | Constraint |
|---|---|
| Directionality | Logical properties (`inline-start`, `block-end`); `dir="auto"` for user content |
| Script metrics | Line-height adjustment for scripts with tall ascenders (Devanagari, Thai, Arabic) |
| Text expansion | European +35–50%; Russian +100%; CJK 0–10% (often contraction) |
| Pluralization | ICU MessageFormat with CLDR plural rules; never concatenate |
| Locale formatting | `Intl.NumberFormat`, `Intl.DateTimeFormat`, `Intl.ListFormat`; locale-param, not hardcoded |
| Bidirectional flow | `bidiIsolation` for mixed-content strings; `LRM`/`RLM` for neutral characters |

### Step 3 — Execution routing

Internationalization constraints are consumed by all composition skills. `ui-compose-typography` adjusts line-height per script; `ui-compose-spacing` widens inline gaps for expansion budgets; `ui-compose-voice` uses ICU MessageFormat for all slot copy.


## When to use

- A UI system is being authored or audited for more than one locale.
- Copy lengths or date/number formats vary across target locales.
- RTL support (Arabic, Hebrew, Persian, Urdu) is in scope — now or imminent.
- CJK or Indic scripts must share the same type scale as Latin without breaking rhythm.
- The product exposes user-generated content that may arrive in any script.

## When NOT to use

- Truly single-locale product with no UGC across scripts → skip, but record the assumption.
- Copy editing / translation authoring → `ui-compose-voice` (sibling).
- Raw `Intl.*` API debugging → outside this skill's corridor; this skill constrains *what must be Intl-formatted*, not how.

## Rate-limiting factor

**Text is not a string — it is a pair (content, locale).** The irreducible operation is: every rendered piece of text must carry its locale + writing direction, and every layout decision must be derivable from logical (not physical) axes. A UI that uses `left`/`right`/`margin-left` anywhere on text-bearing surfaces cannot be locale-flipped without re-authoring.

## First principles

1. **Logical > physical axes.** Use `inline-start` / `inline-end` / `block-start` / `block-end`, never `left`/`right`/`top`/`bottom`, on anything that holds or positions text.
2. **Direction is declared, not inferred.** Every text-bearing root declares `dir` and `lang`. No heuristics.
3. **Scripts have metrics.** x-height, cap-height, ideographic em-box, and default line-height differ across Latin / CJK / Arabic / Devanagari. A single `line-height: 1.4` rule is locale-incorrect.
4. **Numbers, dates, currencies, plurals, and lists are functions, not strings.** They must flow through `Intl.*` at render time, not be concatenated from parts.
5. **Copy has a budget, not a fixed length.** Reserve +40% expansion headroom for DE/FR/FI and ±30% for CJK compaction; UI must not crop, truncate silently, or overflow.
6. **Icons can be directional.** Back/forward, undo/redo, list-bullet-indent, progress direction — flip with writing mode. Clock, checkmark, and brand logos do *not* flip. The distinction is declared.
7. **Mirroring is a component property, not a global toggle.** Logical axes handle layout; directional *semantics* (e.g., a play-button triangle) still need explicit flip flags.
8. **Bidi isolation is mandatory around user content.** Without `<bdi>` or `unicode-bidi: isolate`, interpolating RTL user content into LTR chrome produces garbled glyphs.

## Procedure

### Step 1 — Enumerate target locales
Produce a locale matrix: `{locale, script, direction, Intl-fallback}`. Record expansion factor and contraction factor per locale. If unknown → assume +40% / −30%.

### Step 2 — Declare writing-mode primitives
Emit a small set of CSS properties that every other skill consumes:
- `:root[dir="rtl"]` sets logical direction.
- `:root[lang]` drives `:lang()` overrides for script-specific type/spacing.
- All text-bearing surfaces declare `unicode-bidi: plaintext` or `isolate` as appropriate.

### Step 3 — Constrain typography
Hand `ui-compose-typography` three constraints:
- Per-script line-height override band (Latin 1.4–1.7 / CJK 1.55–1.8 / Arabic 1.6–2.0 / Devanagari 1.5–1.8).
- Per-script min body size (Latin ≥ 14px / CJK ≥ 15px for equivalent legibility).
- `:lang()` allowed to raise size 1 step for scripts with taller ink height.

### Step 4 — Constrain spacing
Hand `ui-compose-spacing` two constraints:
- All inset/stack/inline tokens use logical properties at emission (`padding-inline-*`, `margin-block-*`).
- Slot budgets reserve expansion headroom (see Step 5). Squish-family tokens may only shrink up to `contraction_factor`.

### Step 5 — Budget copy expansion
For every component with text:
- Width budget = `base × (1 + expansion_factor)` OR width is fluid with `min-content` safety.
- Truncation must use `text-overflow: ellipsis` only where a tooltip / disclosure is present; silent truncation refused.
- Button labels: either fluid-width or designed-for-longest-locale-at-authoring.

### Step 6 — Constrain iconography
Hand `ui-compose-icons` the mirroring table:
- `mirroring ∈ {"always", "never", "ltr-only", "rtl-only"}`.
- Directional icons (arrows, chevrons, undo/redo, indent/outdent) → `"always"` (flip with dir).
- Logos, checkmarks, clocks, media play-indicators (by convention) → `"never"`.
- Require each icon to declare its policy; no unset defaults.

### Step 7 — Constrain formatting
For every numeric, date, currency, list, or relative-time surface:
- Render via `new Intl.NumberFormat(locale)`, `DateTimeFormat`, `RelativeTimeFormat`, `ListFormat`, `PluralRules`.
- No concatenation of pre-formatted parts — `formatToParts` when mixed markup is required.
- Currency tokens carry `{amount, currency}`, not `"$12.50"`.

### Step 8 — Require bidi isolation
Any interpolation of runtime strings into chrome wraps the variable with `<bdi>` (HTML) or `unicode-bidi: isolate` (CSS). Includes: user names, search queries, filenames, tag chips.

### Step 9 — Emit the locale schema
Produce a LocaleSchema consumed by downstream skills:

```ts
type LocaleSchema = {
  locales: Array<{
    tag: string;           // BCP 47
    script: "Latn" | "Arab" | "Hebr" | "Hans" | "Hant" | "Jpan" | "Kore" | "Deva" | ...;
    direction: "ltr" | "rtl";
    expansionFactor: number;   // e.g., 1.4
    contractionFactor: number; // e.g., 0.7
    lineHeightBand: [number, number];
    minBodyPx: number;
  }>;
  iconMirroring: Record<IconId, "always" | "never" | "ltr-only" | "rtl-only">;
  formattedSurfaces: Array<{ id: string; intl: "Number" | "DateTime" | "RelativeTime" | "List" | "Plural" }>;
  bidiIsolationPoints: string[]; // component slot ids that must isolate
};
```

## Invariants

1. No physical-axis CSS (`left/right/margin-left/padding-right`) on text-bearing surfaces.
2. Every text surface declares `dir` and `lang` — inherited from a declared ancestor counts.
3. Every formatted-surface passes through `Intl.*`. Pre-formatted strings at interpolation sites refused.
4. Every icon declares a mirroring policy. Unset → fails audit.
5. Every component text slot declares an expansion budget or is fluid-width.
6. User-provided runtime strings are bidi-isolated at every interpolation point.
7. Line-height and min-size bands are script-keyed, not locale-keyed — keeps the matrix bounded.
8. No locale-specific component forks. Locale shapes primitives; components remain universal.


- **INV-INT-001** — Every proof cites specific schema paths or CSS rules it evaluates (enforcement: convention)
- **INV-INT-002** — Remediation suggestions are scoped to the schema/artifact that can fix them (enforcement: convention)

## Typed Interface

**Domain:** `ui-design`

**Consumes:** Relevant schemas and artifacts.

**Produces:** `InternationalizationProof` — constraint-satisfaction proof or violation report.

**Invariants:** Evaluations cite schema paths or CSS rules; remediation suggestions scoped to fixable artifact.

**Downstream:** `ui-audit-quality`.

## Anti-patterns this skill refuses

- Swapping `left` for `right` at build-time to "support RTL" — logical axes exist for exactly this reason.
- Using a single hardcoded `line-height: 1.5` across Latin + CJK + Arabic.
- Pre-computing `"$12.50"` on the server and interpolating as a string.
- Concatenating translated fragments (`"Welcome, " + name`) — use `Intl.MessageFormat` or an ICU template.
- Silent truncation without a disclosure affordance.
- Toggling RTL with a JS class that rewrites component internals — direction belongs on `:root`.
- Locale-specific component variants ("ButtonRtl") — splits the component surface needlessly.
- Treating Hebrew and Arabic as interchangeable — different metrics, different letterforms, different shaping.
- Assuming `Intl.Collator` default sort works for locale-sensitive ordering — specify `sensitivity` and `numeric`.
- Icon flipping by CSS `transform: scaleX(-1)` without declaring a per-icon policy — flips the clock and the logo.

## Handoff

- `ui-compose-typography` consumes `LocaleSchema.locales[*].{lineHeightBand, minBodyPx}` and emits `:lang()` overrides.
- `ui-compose-spacing` consumes logical-axis constraint; emits `padding-inline-*` / `margin-block-*`.
- `ui-compose-icons` consumes `iconMirroring` and emits `[dir="rtl"]` flip rules or neutral-by-default SVGs.
- `ui-compose-voice` consumes expansion factors to size copy within budget.
- `ui-build-theme` forbids physical-axis properties in emitted theme CSS.
- `ui-audit-quality` runs i18n checks independently: logical-axis-only, Intl-on-formatted-surfaces, bidi isolation present, mirroring declared, lang/dir present.

## Bundled reference files

- `locales/script-metrics.json` — per-script line-height bands and min body sizes.
- `locales/expansion-factors.json` — canonical per-locale text-expansion / contraction factors.
- `mirroring/icon-policies.json` — canonical mirroring-policy table for common icon types.
- `formatting/intl-surfaces.json` — enumeration of surfaces that must route through `Intl.*` (numbers, dates, relative time, currencies, plurals, lists, collation).
- `bidi/isolation-points.json` — canonical list of component slot types that require bidi isolation.
