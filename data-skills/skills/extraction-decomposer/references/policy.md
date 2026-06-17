# Policy — definition-of-done, the report card, and the handoff

The reusable artifacts and boundaries: what "done" means for an extraction, the shape of the
extraction-report card the skill emits, and how this hands off to the rest of the data-tooling fleet
without overlapping it.

## Definition-of-done (an extraction is shippable when…)

Gated items route to `bin/`; review items are 1–5 judgments. SHIPPABLE = the quadrant top-left.

1. **Complete (A1)** — every field the source actually provides is extracted; nothing dropped.
2. **Faithful (A2)** — every extracted value is grounded in the source; `groundedness-check.py` is
   clean **and** the adversarial cross-check finds no unsupported / wrong-span / mis-resolved value.
   **No invented values.**
3. **Normalized (A3)** — units/dates/casing/number formats consistent, meaning preserved (≥4).
4. **Disambiguated (A4)** — the right entity/sense on every ambiguous reference; irreducible ambiguity
   surfaced as `null` + a note, not guessed (≥4).
5. **Provenanced (A5)** — each value traceable to a source span (≥4).
6. **Well-formed + schema-conformant (B1/B2)** — `schema-check.py` parses the JSON and conforms it to
   types / `required` / `enum`.
7. **Constraints satisfied (B3)** — ranges, patterns, lengths, referential integrity all pass.
8. **Robust (B4)** — every absent field is `null` per the schema, **not invented to satisfy
   `required`** (≥4).
9. **Stable (B5)** — the same source re-extracts to the same JSON (≥4).
10. **Both axes ≥4, zero gate fails, SHIPPABLE quadrant** — reported as two scores, gate failures
    first, with the extraction-report card ready for handoff.

## The extraction-report card

The artifact DECOMPOSE/GRADE emits — the three findings the two `bin/` tools and the verifier produce:

```json
{
  "source": "invoice-0042.txt",
  "extraction": "invoice-0042.json",
  "schema_verdict": {
    "well_formed": true,
    "schema_conformant": true,
    "violations": []
  },
  "groundedness_findings": [
    { "path": "$.contact.name", "value": "John Smith", "kind": "UNGROUNDED",
      "class": "invented", "fix": "null the field; source names no contact" },
    { "path": "$.total", "value": 99999, "kind": "UNGROUNDED",
      "class": "invented", "fix": "source total is 13,020" }
  ],
  "adversarial_verdict": {
    "checked_in_fresh_context": true,
    "unsupported": ["$.contact.name", "$.total"],
    "wrong_span": [],
    "mis_resolved": [],
    "verdict": "FIDELITY FAIL — 2 invented values"
  },
  "axes": { "fidelity": 1, "validity": 5 },
  "quadrant": "valid JSON, invented values"
}
```

- **`schema_verdict`** — from `schema-check.py` (B1–B3): parsed? conformant? what violated?
- **`groundedness_findings[]`** — from `groundedness-check.py` (A2): each ungrounded scalar, classified
  by the `groundedness.md` failure taxonomy (invented / wrong-span / over-normalized / coerced).
- **`adversarial_verdict`** — from the fresh-context cross-check (A2/A4): what the deterministic check
  couldn't see (wrong-span, mis-resolved entities), and the overall fidelity call.
- **`axes` + `quadrant`** — the two separate scores and the named cell. Never an average.

The card above is the **signature failure** caught: `validity: 5` (perfectly valid JSON) with
`fidelity: 1` (two invented values) → the *valid JSON, invented values* quadrant. A schema-only review
would have shipped it.

## Governance

- **The schema is checked in** as the contract of record — the extraction's `schema_verdict` is read
  against *that* schema, versioned with the extractor.
- **Run groundedness on every extraction, schema on every extraction; run the adversarial cross-check
  on the sample / the high-stakes ones** — groundedness is the cheap everywhere-gate, the adversarial
  verifier the targeted proof (the same cost split as code-decomposer's vacuity-vs-mutation).
- **Stability is a re-run, not a read** — pin temperature/prompt and re-extract a sample to measure
  B5; run-to-run drift on identical input is a real defect.

## Handoff — what this skill does NOT do

`extraction-decomposer` is the **extraction-grading** stage; it grades fidelity + validity of one
extraction against its source and schema. It does not:

- **Author the schema from a spec corpus** — for a schema-validated PRD/spec corpus, that's `plan-prd`;
  this skill *designs an extraction schema* (SPECIFY) and *grades* against it, it doesn't run a
  spec-doc pipeline.
- **Grade a database query** — `query-decomposer` owns SQL/query correctness (semantics × execution
  over a database). This skill owns pulling structured data *out of an unstructured/semi-structured
  document*; the seam is "is there a query engine and a schema'd store" (query-decomposer) vs "is
  there a source document and an output schema" (here).
- **Grade arbitrary code** — `code-decomposer` owns a unit of code (spec × execution). The extractor's
  *implementation* (the parser, the prompt-program) is a code unit graded there; this skill grades its
  *output* against the source.
- **Run the LLM / build the extractor** — this skill grades an extraction; it does not perform the
  extraction or build the pipeline. Hand the locked schema + report card to the extractor author.
- **Audit data quality at rest** — drift, dedup, and reconciliation of a *stored* dataset is a
  different altitude; this skill is point-of-extraction fidelity, document-scoped.

## The niche, in one line

`extraction-decomposer` owns **extraction fidelity + validity grading** — is this JSON both
well-formed *and* true to the source — distinct from `query-decomposer` (query correctness over a
store) and `code-decomposer` (a unit of code against its contract).
