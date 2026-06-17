# Worked example — "valid JSON, invented values" on FIDELITY × VALIDITY

A complete DECOMPOSE → fix → GRADE for one extraction, showing the **A2 groundedness gate** catching
a hallucinated field that schema validation waves straight through — the signature LLM extraction
failure this skill exists to catch. The two extractions here are checked in and the groundedness
engine actually flags / clears them against the source.

## The artifact

A five-token invoice (`examples/invoice.source.txt`):

```
Invoice 4471. Bill to: Globex Corp. Net 30. Total: $1,250.00.
```

…and an extraction an LLM pulled from it (`examples/invoice.red.json`):

```json
{ "invoice_no": "4471", "buyer": "Globex Corp", "contact": "Jane Doe", "total": "$1,250.00" }
```

It is well-formed JSON, every field is a string, types check — a schema validator passes it. Ship it?

## DECOMPOSE

**A · Fidelity** (whole → part) — *the right data?*
- **A1 Completeness** `[gate]` — every field the source provides is captured: invoice no, buyer, total. ✓
- **A2 Faithfulness** `[gate, code]` — every scalar must be grounded in the source. **This is the
  dangerous axis.** Run the engine on the spec:

```
$ python3 bin/groundedness-check.py examples/invoice.red.json examples/invoice.source.txt
  UNGROUNDED     $.contact                    'Jane Doe'
groundedness-check: FAIL — 1 of 4 scalar(s) not cleanly grounded in the source — verify each against the source before shipping (an ungrounded scalar is a LIKELY but not certain hallucination)
```

**A2 fails.** `"Jane Doe"` grounds **nowhere** in the source — no contact appears at all; the model
invented a plausible-looking person. The other three scalars ground cleanly: `"4471"` (NUMERIC),
`"Globex Corp"` (token-boundary EXACT), `"$1,250.00"` (NUMERIC key). A failed `[gate]` blocks the
A-axis reviews (A3–A5): no point grading normalization or provenance on an invented value.

## VALIDITY is silent here — and that's the lesson

The instructive inversion: a schema check on the red extraction is **green** (well-formed, all strings,
types conform). The cheap gate is *blind to the dangerous failure* — schema-conformant JSON with a
hallucinated value passes it cleanly. Fidelity is **not schema-gateable**; it routes to groundedness.

## Fix

Drop the invented field — represent the absent contact as `null`, never a guess
(`examples/invoice.green.json`: `"contact": null`). `null` is the *correct* encoding of "the source
didn't say," and the scalar walk skips it (a judgment, not a copied token):

```
$ python3 bin/groundedness-check.py examples/invoice.green.json examples/invoice.source.txt
groundedness-check: OK — all 3 scalar value(s) grounded in the source
```

The corrective is **delete-and-null**, never invent a different plausible value — *allow null over
hallucinate*.

## GRADE — two scores, never averaged

- **Fidelity: A2 gate-fail → (after fix) 5/5** — A2 was the only blocker; with the invented field
  nulled, completeness (A1) / normalization (A3) / disambiguation (A4) / provenance (A5) all clear.
- **Validity: 5/5** — well-formed, schema-conformant, constraints satisfied (it was green throughout).

**Quadrant:** the red extraction sat in **"valid JSON, invented values"** (Validity passed — it's fine
JSON — but Fidelity's A2 carried a value the source never stated) — *built right, designed wrong*. The
fix is fidelity work the schema can't see, not schema machinery. After it: **SHIPPABLE**.

The lesson: "does it conform to the schema?" is the wrong question; "is every value something the
source actually says?" is the right one — and the cheap gate that proves the first is *deliberately
blind* to the second, so you gate fidelity in code, never by a sympathetic read.
