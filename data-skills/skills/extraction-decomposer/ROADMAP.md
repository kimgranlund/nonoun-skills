# Roadmap — extraction-decomposer

Ships its core in 0.1.0 (the two axes, the groundedness check, the schema validator, the
extraction-report card, the inversion doctrine). Everything below is additive.

## `bin/groundedness-check.py`

- [x] **Token / word-boundary matching** (was: raw substring) — closes the substring-fragment false
      negative where an invented `"Fran"`/`"Ware"` grounded against `San Francisco`/`warehouse`, and a
      split `"John"`+`"Smith"` grounded against `Johnson`/`Smithfield`. Plus a **weak-grounding floor**
      (1-token ≤3-char hits → `WEAK_GROUNDING — verify manually`) and a distinct `EMPTY` finding for
      empty/whitespace values. Adversarial fixtures added for all of these.
- [x] **Numeric back-door anchored** — a string scalar takes the NUMERIC path only when the *entire*
      trimmed string is one number token; a string that merely *starts* with a grounded digit
      (`"12 Nonexistent Street"`, `"12-FAKE-ID-9999"`) no longer grounds. Fixture added.
- [ ] **Deferred — residual false-negative class:** a value that is a faithful *multi-token span* of
      the source copied into the **wrong field** still grounds (token matching is containment, not
      alignment). This is by design the **adversarial verifier's** job, not the deterministic gate's.
- [x] **EU-format & scientific NUMBERS grounded** (0.2.1) — a faithful value normalized from an
      EU-format source (`1.234,56`) or scientific notation (`1.5e3`) now grounds, via additive
      source-side keys (the EU pattern requires a `,\d+` decimal, so a bare `1.234` stays US — no new
      false groundings). Locked behind selftest fixtures.
- [x] **DD.MM.YYYY-dominant dates & non-ASCII digits** (0.2.2) — a slashed/dotted numeric date now
      keys under **both** D/M/Y and M/D/Y, so a European `02.01.2026` grounds `2026-01-02` while a US
      `02/01/2026` still grounds `2026-02-01`; an unambiguous `25/12/2026` (day > 12) emits only the
      valid reading (a `_valid_ymd` guard drops the impossible month-25 M/D/Y key). Non-ASCII digit
      scripts (Arabic-Indic, Eastern-Arabic/Persian, Devanagari, fullwidth) are folded to ASCII via
      `unicodedata.digit` before numeric/date key extraction, on both the source and the value. Both
      are additive (all-ASCII text is byte-identical; an impossible date key never matched anything).
      Locked with must-GROUND + must-NOT-ground (FP-guard) selftest fixtures.
- [x] **Configurable weak-grounding floor** (0.2.3) — `MIN_TOKENS`/`MIN_CHARS` exposed as
      `--min-tokens`/`--min-chars` so a high-recall corpus can tighten or loosen the WEAK_GROUNDING band.
- [ ] **Fuzzy / derivable grounding** — a configurable similarity threshold for near-verbatim spans
      (OCR noise, hyphenation, ligatures), and arithmetic derivation (a `total` that is the *sum* of
      grounded line items, grounded by computation rather than appearance).
- [x] **Span emission** (0.2.3) — `--spans` emits, for each grounded scalar, the source offset/snippet
      that grounded it, so a green run also produces A5 provenance instead of only a pass/fail.
- [ ] **Wrong-span detection (partial)** — when a value grounds at multiple spans, surface the
      ambiguity for the adversarial verifier instead of silently passing the first match.
- [x] More date/number locales — DD.MM.YYYY-dominant regions (0.2.2), non-ASCII digits (0.2.2), and
      scientific notation (0.2.1), each behind its own fixtures. (Further locales — e.g. RTL date
      ordering, two-digit years, locale-specific month names — remain future work.)
- [ ] A machine-readable (`--json`) report so GRADE can fold `groundedness_findings[]` into the card.

## `bin/schema-check.py`

- [x] **Unknown / unsupported keyword detection** — a schema-author typo (`requried`, `minimun`) or an
      unsupported keyword (`additionalProperties`, `uniqueItems`) is no longer a silent no-op (which
      produced a false green); each surfaces a `WARN: unknown/unsupported keyword 'X' — not enforced`
      line and the run exits nonzero. Meta/annotation keywords ($schema, title, description, …) are
      ignored without a warning. Adversarial fixture added.
- [ ] **`$defs` / local `$ref`** resolution (same-document only — no remote fetch, keeping the
      clean-checkout-true contract).
- [ ] More keywords as the extraction corpus demands: `additionalProperties`, `uniqueItems`,
      `minItems`/`maxItems`, `const`, `format` (as advisory, since format is not a hard gate).
- [ ] **Coercion-aware mode** — report a value that would pass only after a string→number coercion, so
      a `"13020"` in a numeric field is flagged as a normalization (A3) issue, not silently rejected.

## Method & corpus

- [ ] A **routing-eval corpus** (the maturity step the repo ROADMAP tracks) — especially the
      boundaries with `query-decomposer` (store-backed query correctness), `code-decomposer` (the
      extractor's *implementation*), and `plan-prd` (schema-validated spec corpora), which are the
      likely mis-routes.
- [ ] A worked **end-to-end transcript** (an invoice/résumé SPECIFY → extract → DECOMPOSE → GRADE),
      with the schema, the source, the extraction, and a caught invented value checked in and
      dogfooded against both `bin/` tools.
- [ ] An **adversarial-cross-check template** (the fresh-context skeptic prompt with the source in
      hand) as a reusable reference, shared in shape with `code-decomposer`'s probe and
      `deep-research`'s verify step.

## Plugin

- [ ] As `data-skills` grows, candidate siblings from the same FIDELITY/VALIDITY lineage: a
      `transform-decomposer` (an ETL/mapping step: semantics × execution) and a `classification-
      decomposer` (a labeling task: correctness × calibration), both with deterministic example-set
      gates.
