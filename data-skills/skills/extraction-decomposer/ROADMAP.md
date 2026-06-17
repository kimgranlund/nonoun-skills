# Roadmap — extraction-decomposer

Ships its core in 0.1.0 (the two axes, the groundedness check, the schema validator, the
extraction-report card, the inversion doctrine). Everything below is additive.

## `bin/groundedness-check.py`

- [ ] **Fuzzy / derivable grounding** — a configurable similarity threshold for near-verbatim spans
      (OCR noise, hyphenation, ligatures), and arithmetic derivation (a `total` that is the *sum* of
      grounded line items, grounded by computation rather than appearance).
- [ ] **Span emission** — for each grounded scalar, emit the source offset/snippet that grounded it,
      so a green run also produces A5 provenance instead of only a pass/fail.
- [ ] **Wrong-span detection (partial)** — when a value grounds at multiple spans, surface the
      ambiguity for the adversarial verifier instead of silently passing the first match.
- [ ] More date/number locales (DD.MM.YYYY-dominant regions, non-ASCII digits, scientific notation),
      each behind its own fixtures.
- [ ] A machine-readable (`--json`) report so GRADE can fold `groundedness_findings[]` into the card.

## `bin/schema-check.py`

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
