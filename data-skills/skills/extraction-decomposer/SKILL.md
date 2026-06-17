---
name: extraction-decomposer
description: >
  Decompose, design, and grade a structured extraction — JSON pulled out of a source document by an
  LLM — on two crossing axes: FIDELITY (completeness → faithfulness → normalization → disambiguation
  → provenance) and VALIDITY (well-formed → schema → constraints → robustness → stability) — scored
  separately so schema-conformant JSON can't hide invented values. The instructive inversion: the
  cheap gate (schema validation) is blind to the dangerous failure — valid JSON with hallucinated
  values the source never stated. VALIDITY routes to a schema check (bin/schema-check.py); FIDELITY
  routes to a deterministic groundedness check (bin/groundedness-check.py) plus a fresh-context
  adversarial source cross-check. Use when designing an extraction schema, grading an extraction
  against its source, or hunting hallucinated fields. NOT for query correctness (query-decomposer),
  a unit of code (code-decomposer), or stored-data audits.
---

# extraction-decomposer — grade a structured extraction on two crossing axes

A structured extraction — JSON an LLM pulled out of a source document — is **correct on two
independent axes that walk the same hierarchy in opposite directions** — the decomposer seam the
layout-, mermaid-, component-, and code-decomposers apply to space, diagrams, components, and code,
here applied to a structured extraction:

- **Fidelity · whole → part** grades the **intent** (the **dangerous** axis): is every field the
  source provides extracted → is every value grounded in the source (*no invented values*) →
  normalized without distorting meaning → the right entity → traceable to a span. *"Is it the right
  data — what the source actually says?"*
- **Validity · part → whole** grades the **mechanism** (the **cheap, gateable** axis): does it parse
  → conform to the schema → satisfy the constraints → represent missing data as null → reproduce
  deterministically. *"Is it well-formed, schema-conformant data?"*

They **cross at the schema** — the schema is *both* the validity contract (what makes the document
valid) *and* the extraction contract (which fields must be extracted). That crossing is the whole
technique: an extraction can be **valid JSON, invented values** (schema-clean, but a value the source
never stated — *the signature LLM failure*) or **faithful but malformed** (every value true to the
source, but off-schema or unparseable). Opposite defects, opposite fixes — so you **score and report
the two axes separately**, never averaged.

## The doctrine — gate where you can, adversarially verify where you can't

The non-obvious core, and the reason this earns a skill — it is **the instructive inversion** of every
other decomposer:

> For every other decomposer the cheap mechanizable gate guards the dangerous failure. **Here it does
> not.** A schema validator proves the JSON is VALID; it is **silent** on whether the values are TRUE.
> Schema-conformant JSON with an **invented value the source never stated** passes schema validation
> cleanly — and that is THE signature LLM extraction failure.

So the doctrine inverts: **route VALIDITY to a schema check** (`bin/schema-check.py` — trust the
tool), but **FIDELITY is not schema-gateable** — attack it two ways: (1) a **deterministic
groundedness check** (`bin/groundedness-check.py` — every extracted scalar must appear in / be
derivable from the source), and (2) a **fresh-context adversarial verifier** that hunts any extracted
value the source does not support (for the *wrong-span* value groundedness can't see). **Gate where
you can (schema); adversarially verify where you can't (fidelity).**

## Quick Start

**You bring:** an extraction (a `*.json`) and its source document, plus the schema — and the question:
"design this schema", "is this extraction faithful?", "are any fields invented?", "is it
production-ready?". **You get:** an extraction-report card (`{schema_verdict, groundedness_findings[],
adversarial_verdict}`) and a two-axis grade with the defect quadrant named.

> *"Is this invoice extraction done?"* →
> 1. **Validity — run the schema check:** `bin/schema-check.py extraction.json schema.json` —
>    parses? `[gate]` conforms (types/required/enum)? `[gate]` constraints (ranges/patterns)? `[gate]`.
>    Green. **But green proves nothing about fidelity** — keep going.
> 2. **Fidelity — ground every value:** `bin/groundedness-check.py extraction.json source.txt` — every
>    scalar must appear in / be derivable from the source `[gate]`. `$.contact.name = "John Smith"`
>    grounds **nowhere** → flagged: a likely invented value.
> 3. **Adversarial cross-check:** in a fresh context, with the source, hunt any value the source
>    doesn't support — especially a *wrong-span* value (ship-to city in `bill_to.city`) groundedness
>    can't catch.
> 4. **Robustness + report:** is each absent field `null`, or a `required` field invented to satisfy
>    the schema (B4)? Then the two axis scores + the quadrant cell — gate failures first.

**Modes:** **SPECIFY** (design the schema + extraction contract — required/nullable/enum, the
allow-null-over-hallucinate rule) · **DECOMPOSE** (read an extraction + its source → run schema +
groundedness + adversarial → grade) · **GRADE** (score both axes, gates before reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Fidelity** | whole → part | **A1** Completeness → **A2** Faithfulness → **A3** Normalization → **A4** Disambiguation → **A5** Provenance | "Is it the *right data*?" |
| **B · Validity** | part → whole | **B1** Well-formed → **B2** Schema → **B3** Constraints → **B4** Robustness → **B5** Stability | "Is it *well-formed, schema-conformant* data?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on
that axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable extraction is **≥4 on every review
with zero gate failures**, reported as two separate axis scores plus the defect quadrant. The gates
route to code: **B1/B2/B3** → `bin/schema-check.py`; **A2** → `bin/groundedness-check.py` + the
adversarial verifier.

## The opposite-defect quadrant

```
                 B · VALIDITY passes         B · VALIDITY fails
A · FIDELITY  ┌────────────────────────┬────────────────────────┐
   passes     │      SHIPPABLE         │  faithful but malformed │
              │                        │  — true to the source,  │
              │                        │  but off-schema / won't │
              │                        │  parse / wrong types    │
              ├────────────────────────┼────────────────────────┤
A · FIDELITY  │ VALID JSON, INVENTED   │       REBUILD           │
   fails      │ VALUES — schema-clean, │                         │
              │ but a value the source │                         │
              │ never stated (THE      │                         │
              │ signature failure)     │                         │
              └────────────────────────┴────────────────────────┘
```

The quadrant **names the fix**: bottom-left (the dangerous, common-for-an-LLM cell) needs **fidelity**
work the schema can't see — drop the hallucination, ground every value, null the unknown; top-right
needs **validity** work the schema check finds for you. Report the cell, not an average.

## The two mechanized gates

| Gate | Tool | What it proves |
|---|---|---|
| **Validity (B1/B2/B3)** | `bin/schema-check.py <doc> <schema>` | well-formed JSON, conforms to types/`required`/`enum`, satisfies range/pattern/length. The cheap axis — trust the tool. |
| **Faithfulness (A2)** | `bin/groundedness-check.py <extraction> <source>` | every scalar is grounded — exact / normalized / numeric-key / date-reformat match. Flags any **ungrounded** scalar as a likely hallucination. |

`schema-check.py` is necessary but **cannot see hallucination**; `groundedness-check.py` catches the
*invented* (absent) value but **cannot see a wrong-span** value — that's the adversarial verifier's
job. Full grounding ladder + failure taxonomy in `references/groundedness.md`.

## §SelfAudit

- **A clean schema check is evidence of validity, NOT fidelity.** The whole skill exists because
  schema-conformant JSON can carry invented values. Never certify an extraction from `schema-check.py`
  alone — run `groundedness-check.py` and the adversarial cross-check, always.
- **No invented values, ever.** Every extracted value must be grounded in the source. An ungrounded
  scalar is a likely hallucination — the corrective is to *delete it and null the field*, never to
  invent a different plausible value.
- **Groundedness is necessary, not sufficient.** It catches the value that appears nowhere; it cannot
  catch a *wrong-span* value that grounds against the wrong part of the source. That gap is the
  adversarial verifier's reason to exist — run it in a fresh context, not the author's.
- **`required` tempts hallucination.** A `required` field the source omits, filled with a guess, is
  *valid* (B2) and *unfaithful* (A2) at once. The fix is structural: make it nullable, relax
  `required` — **allow null over hallucinate**.
- **Gates before reviews, always.** Don't grade normalization for an invented value, or constraints
  for JSON that won't parse. Stop each axis at its first failed gate (but score *both* axes — a
  faithful-but-malformed extraction still earns its fidelity score).
- **Two scores, never one.** *Valid-JSON-invented-values* and *faithful-but-malformed* need opposite
  fixes (fidelity vs validity). Report both axes and name the quadrant cell; never average.
- **Grade, don't extract.** This skill designs the schema, runs the checks, and grades — it does not
  perform the extraction or build the pipeline. Hand the locked schema + report card to the extractor
  author.

## Verify Target

An extraction is **done** when: every field the source provides is captured (A1); every value is
grounded — `groundedness-check.py` clean **and** the adversarial cross-check finds nothing unsupported,
wrong-span, or mis-resolved (A2); normalization/disambiguation/provenance ≥4; `schema-check.py` parses
and conforms it (B1/B2/B3); every absent field is `null` not invented-to-satisfy-`required` (B4); it
re-extracts deterministically (B5); and both axes score ≥4 with zero gate failures, landing in the
**SHIPPABLE** quadrant — with the extraction-report card ready for handoff. **NOT done** when: the JSON
is schema-clean but carries a value the source never stated (*valid JSON, invented values*); or every
value is faithful but it's off-schema or won't parse (*faithful but malformed*); or a `required` field
was invented to satisfy the schema; or one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Fidelity × Validity), the leveled walk with gates, the quadrant, the **gate-vs-adversarial-verify inversion doctrine**, and the SPECIFY / DECOMPOSE / GRADE workflows |
| `references/fidelity-axis.md` | **the Fidelity axis** — completeness, the **no-invented-values discipline**, normalization-without-distortion, disambiguation, provenance, and the **adversarial source cross-check** prompt |
| `references/validity-axis.md` | **the Validity axis** — the schema ladder (well-formed → schema → constraints), **null-vs-invented**, and how `required` fields tempt hallucination; mechanized by `bin/schema-check.py` |
| `references/groundedness.md` | **any "is this value real?" question** — the centerpiece: the grounding ladder (exact / normalized / numeric / date), what counts as "supported by the source", and the failure taxonomy (invented · wrong-span · over-normalized · coerced-to-satisfy-required); mechanized by `bin/groundedness-check.py` |
| `references/schema-design.md` | **SPECIFY / designing an extraction schema** — required vs optional, nullable type-lists, enums as a closed-vocabulary gate, constraints-as-fidelity-guards, provenance-in-schema, and the **allow-null-over-hallucinate** rule |
| `references/policy.md` | **definition-of-done / handoff** — the 10-point DoD, the extraction-report card (`{schema_verdict, groundedness_findings[], adversarial_verdict}`), and the seams to `query-decomposer`, `code-decomposer`, and `plan-prd` |
| `bin/schema-check.py` | **mechanizes B1–B3** — a minimal JSON-Schema-subset validator (type/required/properties/items/enum/minimum/maximum/minLength/maxLength/pattern); `<doc.json> <schema.json>` · `selftest` |
| `bin/groundedness-check.py` | **mechanizes A2** — asserts every scalar is grounded in the source (exact/normalized/numeric/date); flags ungrounded scalars as likely hallucinations; `<extraction.json> <source.txt>` · `selftest` |
