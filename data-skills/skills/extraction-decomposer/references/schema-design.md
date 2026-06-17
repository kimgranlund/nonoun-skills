# Schema design — the extraction contract that makes honesty representable

The schema is the **crossing seam**: it defines *both* what makes the document VALID (types, required,
constraints) *and* what must be EXTRACTED (the fields). A well-designed extraction schema does more
than validate — it **makes the honest answer representable**, so the extractor never has to choose
between conforming and telling the truth. A badly-designed schema *mandates hallucination*. This file
is the SPECIFY-mode reference: how to design a schema that helps fidelity instead of fighting it.

## The governing rule: allow null over hallucinate

> **For every field the source might omit, the schema must make `null` (or absence) a VALID answer.**
> A `required`, non-nullable field for data the source may not provide is a schema that *forces a
> guess* — it converts a fidelity problem into a validity requirement, and the extractor satisfies the
> validity requirement by inventing.

This single rule drives most schema-design decisions below. The schema's job is to ensure that "the
source didn't say" is always *expressible* and *conformant*.

## Required vs optional

- **`required` only for fields the source is GUARANTEED to provide** for every document in scope — the
  invoice number on an invoice, the patient id on a record. If a single in-scope document might omit
  it, it is **not** `required`.
- Everything the source *might* omit is **optional** (drop it from `required`) — and usually also
  **nullable** (below), so the extractor can say "present-but-empty" vs "absent" distinctly if the
  domain needs that distinction.
- The test for `required`: *"If I make this required and a real source omits it, what does a faithful
  extractor do?"* If the answer is "invent a plausible value to conform," the field must not be
  required. The B4 *coerced-to-satisfy-required* failure (see `validity-axis.md`, `groundedness.md`)
  is born here.

## Nullable fields — making "the source didn't say" valid

Express nullability with a **type list** including `null`:

```json
{ "due_date":  { "type": ["string", "null"], "pattern": "^\\d{4}-\\d{2}-\\d{2}$" },
  "phone":     { "type": ["string", "null"] },
  "discount":  { "type": ["number", "null"], "minimum": 0 } }
```

`schema-check.py` validates a type list by accepting the value if it matches *any* member — so `null`
passes, and a real value passes its own constraints. Now the extractor has a **valid, faithful** way
to represent absent data, and the *allow-null-over-hallucinate* rule has teeth. Pair every non-required
field with nullability unless the field is genuinely always present when present at all.

## Enums — the closed-vocabulary fidelity gate

When the source's vocabulary for a field is **closed**, encode it as an `enum`:

```json
{ "status": { "type": "string", "enum": ["paid", "unpaid", "void", "overdue"] } }
```

An enum does double duty: it's a validity constraint (B2) *and* a cheap fidelity guard — a hallucinated
`"pending"` is caught outright by the schema check, with no source needed. Prefer enums over free
strings wherever the domain vocabulary is finite. (When the vocabulary is open or uncertain, a free
string + the groundedness check is the right tool — don't fake an enum you can't enumerate.)

## Constraints that double as fidelity guards

The constraint keywords aren't just validity hygiene — a violated constraint is often a *fidelity*
signal:

- **`pattern`** — an id shape (`^INV-\d{4}-\d{4}$`), an email, a date format. A value that fails the
  pattern is frequently invented or wrong-span.
- **`minimum`/`maximum`** — a `total` that can't be negative, a `quantity` with a sane ceiling, a
  `year` in a plausible range. An out-of-range value is a hallucination tell.
- **`minLength`** — a non-empty name (`minLength: 1`) rules out the empty-string "I had to put
  *something*" answer (which is worse than `null`).

Design constraints **tight enough to catch the implausible value, loose enough not to reject a real
one** — an over-tight pattern rejects faithful data and pushes the extractor toward a conforming
invention.

## Provenance in the schema (turn A5 into structure)

For high-stakes extraction, bind provenance into the schema so every value carries its source span:

```json
{ "vendor": {
    "type": "object",
    "required": ["value", "source_span"],
    "properties": {
      "value":       { "type": ["string", "null"] },
      "source_span": { "type": ["string", "null"] }   // a quoted snippet or offset
    } } }
```

This makes A5 (Provenance) a **structural guarantee** rather than a hope, and makes the adversarial
cross-check trivial — the verifier checks each `value` against its declared `source_span`. The cost is
a heavier schema; spend it where audit matters.

## The SPECIFY checklist

When designing an extraction schema (SPECIFY mode), confirm:

1. **Every field the source might omit is non-`required` and nullable** — `null` is a valid answer.
2. **`required` holds only for guaranteed-present fields** — none that a real source could omit.
3. **Closed vocabularies are enums** — not free strings inviting an out-of-vocabulary invention.
4. **Constraints are tight-but-faithful** — they catch the implausible without rejecting the real.
5. **Provenance is bound in** where audit matters — `{value, source_span}` per high-stakes field.
6. **The schema can express the honest extraction of every in-scope document** — including the messy,
   partial, ambiguous one. If a real source can't be faithfully extracted into this schema, the schema
   is the bug.

A schema that passes this checklist makes the *valid JSON, invented values* quadrant **structurally
harder to fall into** — the extractor never has to hallucinate to conform.
