# The two-axis method — FIDELITY × VALIDITY

A structured extraction — JSON pulled out of a source document by an LLM — is **correct on two
independent axes that walk the same hierarchy in opposite directions** — the decomposer seam the
layout-, mermaid-, component-, and code-decomposers apply to space, diagrams, components, and code,
here applied to a structured extraction.

- **Fidelity · whole → part** grades the **intent** (and is the **dangerous** axis): is every field
  the source actually provides extracted (completeness), is every extracted value grounded in the
  source — *no invented values* (faithfulness), normalized without distorting meaning, the right
  entity, traceable to a span? *"Is it the right data — what the source actually says?"*
- **Validity · part → whole** grades the **mechanism** (and is the **cheap, gateable** axis): does it
  parse as JSON, conform to the schema, satisfy the constraints, represent missing data as null (not
  invented), and reproduce deterministically? *"Is it well-formed, schema-conformant data?"*

They **cross at the schema** — the schema is *both* the validity contract (what types/required/enum
make the document VALID) *and* the extraction contract (which fields must be EXTRACTED). That crossing
is the whole technique, and it carries the skill's defining lesson.

## The instructive inversion (read this first)

For every other decomposer, the cheap mechanizable gate guards the dangerous failure. **Here it does
not.** The cheap gate — schema validation — is *blind* to the dangerous failure:

> A schema validator proves the JSON is VALID. It is **silent** on whether the values are TRUE.
> Schema-conformant JSON that contains an **invented value the source never stated** passes schema
> validation cleanly. That — *valid JSON, invented values* — is THE signature LLM extraction failure,
> and it lives on the axis the cheap gate cannot see.

So the doctrine inverts the usual move:

- Route **VALIDITY** to a schema check (`bin/schema-check.py`) — fully mechanizable, trust the tool.
- **FIDELITY is not schema-gateable.** Attack it two ways:
  1. a **deterministic groundedness check** (`bin/groundedness-check.py`) — every extracted scalar
     must appear in, or be derivable from, the source; an ungrounded scalar is a likely hallucination;
  2. a **fresh-context adversarial verifier** that hunts for any extracted value the source does not
     support (groundedness is necessary, not sufficient — it cannot catch a *wrong-span* value that
     happens to appear elsewhere in the source).

**Gate where you can (schema); adversarially verify where you can't (fidelity).**

## The leveled walk

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Fidelity** | whole → part | **A1** Completeness `[gate]` → **A2** Faithfulness `[gate]` → **A3** Normalization → **A4** Disambiguation → **A5** Provenance | "Is it the *right data*?" |
| **B · Validity** | part → whole | **B1** Well-formed `[gate, code]` → **B2** Schema `[gate, code]` → **B3** Constraints `[gate, code]` → **B4** Robustness → **B5** Stability | "Is it *well-formed, schema-conformant* data?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** — a failure cascades and BLOCKS the reviews below it on
that axis (you cannot judge normalization for a value that's invented, or constraints for a document
that won't parse). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable extraction is **≥4 on every
review with zero gate failures**, reported as two separate axis scores plus the quadrant.

Two of Fidelity's defects route to code via the inversion above; all three Validity gates route to
`bin/schema-check.py`.

### A · Fidelity (whole → part)

- **A1 Completeness `[gate]`** — is every field the source *actually provides* extracted? A dropped
  value the source plainly states (the due date that's right there in the header) is a fidelity gate
  failure, distinct from a field the source is silent on (which belongs as `null` — see B4).
- **A2 Faithfulness `[gate]`** — is every extracted value **grounded in the source**? **No invented /
  hallucinated values.** This is the dangerous gate. Routed to `bin/groundedness-check.py` for the
  deterministic pass, then to the adversarial verifier for what groundedness can't see.
- **A3 Normalization `[review]`** — units/dates/casing/number formats made consistent **without
  distorting meaning**. `"June 16, 2026" → "2026-06-16"` is faithful normalization; rounding `13,020`
  to `13,000` is a *fidelity* defect wearing normalization's clothes.
- **A4 Disambiguation `[review]`** — when the source is ambiguous (two "Lee"s, a bare "the company",
  a pronoun), did the extraction resolve to the **right** entity/sense — or guess?
- **A5 Provenance `[review]`** — is each value traceable back to a specific source span (offset,
  line, quoted snippet)? Provenance is what makes A2 auditable after the fact.

### B · Validity (part → whole)

- **B1 Well-formed `[gate, code]`** — does the output parse as JSON at all? Routed to
  `bin/schema-check.py` (a parse failure is reported before any schema check).
- **B2 Schema `[gate, code]`** — does it conform to the declared schema: types, `required`, `enum`?
  The required-fields rule is the seam where Validity *tempts* a Fidelity failure (see below).
- **B3 Constraints `[gate, code]`** — ranges (`minimum`/`maximum`), patterns, lengths, and
  referential integrity (an id that must resolve). Routed to `bin/schema-check.py`.
- **B4 Robustness `[review]`** — is **missing data represented as `null`** per the schema, **not
  invented to satisfy a required field**? The most insidious cross-axis trap: a `required` field the
  source omits, filled with a plausible guess, is *valid* (B2 passes) and *unfaithful* (A2 fails).
- **B5 Stability `[review]`** — deterministic: the same source extracted twice yields the same JSON
  (modulo key order). Non-determinism on the same input is a reliability defect.

## The opposite-defect quadrant

```
                 B · VALIDITY passes         B · VALIDITY fails
A · FIDELITY  ┌────────────────────────┬────────────────────────┐
   passes     │      SHIPPABLE         │  faithful but           │
              │  (≥4 every review,     │  malformed — every      │
              │   zero gate fails)     │  value is true to the   │
              │                        │  source, but off-schema │
              │                        │  / won't parse / wrong  │
              │                        │  types or enums         │
              ├────────────────────────┼────────────────────────┤
A · FIDELITY  │ VALID JSON, INVENTED   │       REBUILD           │
   fails      │ VALUES — schema-clean, │                         │
              │ but a value the source │  (both invented AND     │
              │ never stated (THE      │   off-schema / unparse- │
              │ signature failure)     │   able — start over)    │
              └────────────────────────┴────────────────────────┘
```

The **signature LLM failure is the bottom-LEFT cell** — *valid JSON, invented values* — schema-clean
yet carrying a value the source never stated. (Bottom-right, REBUILD, is the doubly-broken case:
invented AND malformed.)

The quadrant **names the fix**: bottom-left (*valid JSON, invented values* — the dangerous,
common-for-an-LLM cell) needs **fidelity** work the schema cannot see — drop the hallucination,
ground every value, represent the unknown as `null`; top-right (*faithful but malformed*) needs
**validity** work the schema check finds for you — fix types, conform to the schema. **Report the
cell, not an average** — a blended "3/5" hides which of the two opposite defects you have.

## Modes

- **SPECIFY** (before extracting) — design the **schema + extraction contract**: required vs optional,
  nullable fields, enums, the *allow-null-over-hallucinate* rule. Walk Fidelity-down (what must be
  captured, what the source might omit) and declare the Validity schema (types/required/constraints).
  Output: a schema + a contract note on which fields are nullable and why. See `schema-design.md`.
- **DECOMPOSE** (an extraction + its source) — read both. Run `schema-check.py` (B1–B3), then
  `groundedness-check.py` (A2), then the adversarial verifier on what's left, then score the reviews.
  Output: the extraction-report card + a defect list (e.g. *"valid, but `$.contact.name` is
  ungrounded — likely invented"*).
- **GRADE** — score both axes against the rubric, gates first (schema → groundedness → adversarial),
  place in the quadrant, name one corrective per failure.

## Walk order (do not skip)

1. **B1/B2/B3 Validity** — run `schema-check.py`. Off-schema ⇒ note it, but **do not stop the
   fidelity walk** — a faithful-but-malformed extraction (top-right) still needs its A-axis scored.
2. **A1 Completeness** — does any field the source plainly provides go missing? Dropped ⇒ gate fail.
3. **A2 Faithfulness** — run `groundedness-check.py`. Any ungrounded scalar ⇒ a likely invented value
   ⇒ gate fail; this is the dangerous one, do not skip it because the schema was green.
4. **Adversarial verify** — in a fresh context, hunt one extracted value the source does not support
   (especially a *wrong-span* value groundedness can't catch). Any counterexample ⇒ A2 fail.
5. **B4 Robustness** — is each absent field `null`, or was a `required` field invented to satisfy the
   schema? An invented-to-satisfy-required value is *both* a B4 and an A2 finding.
6. **Reviews** — A3–A5 then B5, 1–5 each. Below 4 ⇒ name the single corrective.
7. **Report** — two axis scores, the quadrant cell, gate failures first.
