# The VALIDITY axis — is it well-formed, schema-conformant data?

The Validity axis (B1–B5) grades *mechanism*, bottom-up: from "does this even parse" to "does the
same source reproduce the same extraction." It is the **cheap, mechanizable** axis — route B1/B2/B3 to
`bin/schema-check.py` and **trust the tool, not the read-through**. An LLM cannot reliably tell by
reading whether a document conforms to a schema; running the validator is the evidence.

**But never mistake validity for fidelity.** Everything on this axis can pass on a document that is
entirely invented. A schema gate is necessary and it is *not the dangerous gate* — that is the whole
inversion (see `decomposition-method.md`). This file is the validity ladder and, crucially, the seam
where validity *tempts* a fidelity failure.

## The schema ladder

| Level | Gate | The tool proves it | The signal |
|---|---|---|---|
| **B1 Well-formed** | `[gate, code]` | `json.load` via `schema-check.py` | the output is parseable JSON at all (an LLM emits prose, trailing commas, code fences) |
| **B2 Schema** | `[gate, code]` | `schema-check.py` | types match, every `required` field present, every `enum` value legal |
| **B3 Constraints** | `[gate, code]` | `schema-check.py` | `minimum`/`maximum`, `pattern`, `minLength`/`maxLength`, referential integrity |
| **B4 Robustness** | review | the schema + a read | missing data is `null` per the schema — **NOT invented to satisfy `required`** |
| **B5 Stability** | review | re-run | same source → same extraction (determinism) |

The gates cascade: a document that won't parse (B1) can't be schema-checked (B2). Run them in order;
`schema-check.py` reports a parse failure as B1 before attempting B2/B3.

## B1 · Well-formed `[gate, code]`

The cheapest, highest-value validity gate. An LLM extractor's output is frequently *not JSON*: wrapped
in ```` ```json ```` fences, prefixed with "Here is the extraction:", carrying a trailing comma, or
truncated mid-object by a token limit. Strip the wrapper, parse, and if it won't parse, **stop the
validity axis here** — there's nothing to schema-check. (Note this is independent of fidelity: a
faithful extraction can be malformed — the *faithful-but-malformed* top-right quadrant.)

## B2 · Schema `[gate, code]`

Conformance to the declared schema. `schema-check.py` supports the extraction-relevant subset: `type`
(incl. a type *list* for nullable fields), `required`, `properties`, `items`, `enum`. Two notes:

- **`integer`/`number` exclude booleans** — in JSON, `true` is not `1`. The validator enforces this so
  a boolean can't sneak through a numeric field.
- **`enum` is the cheap closed-vocabulary gate** — a `status` that must be one of `paid|unpaid|void`
  catches a hallucinated `"pending"` outright. Prefer enums over free strings wherever the source's
  vocabulary is closed (see `schema-design.md`).

## B3 · Constraints `[gate, code]`

The finer mechanizable checks: `minimum`/`maximum` (a negative `total`, an `age` over 150),
`pattern` (an invoice id `^INV-\d{4}-\d{4}$`, an email shape), `minLength`/`maxLength`, and
referential integrity (a `line_item.product_id` that must resolve to a known product). A constraint
violation is a gate failure — but note it often reveals a *fidelity* problem underneath (a value that
violates a range is frequently invented).

## B4 · Robustness `[review]` — null vs invented (the cross-axis trap)

This is the most insidious seam in the whole skill, and it is why VALIDITY and FIDELITY must be scored
separately.

> **A required field the source does NOT provide must be `null` (or absent), never a plausible
> guess.** Filling a `required` field with an invented value to make the schema pass is *valid* (B2
> green) and *unfaithful* (A2 red) at the same time.

The mechanism: a `required` field creates pressure. The extractor "must" produce a value, the source
doesn't give one, so it **manufactures** a plausible one — a guessed phone number, an inferred date, a
default status. The schema is satisfied; the data is fiction. This is the *valid JSON, invented values*
quadrant manufactured by the schema itself.

The corrective is **structural**, in `schema-design.md`: make the field **nullable**
(`{"type": ["string", "null"]}`) and drop it from `required`, so the honest answer — "the source
didn't say" — is *representable* and *valid*. A schema that forces a value for data the source may
omit is a schema that mandates hallucination. The rule: **allow null over hallucinate.**

When grading: any value that is grounded *nowhere* in the source **and** sits in a `required` field is
a double finding — a B4 robustness defect *and* an A2 faithfulness defect. Report it on both axes; the
fix (null it + relax `required`) clears both.

## B5 · Stability `[review]`

Determinism: extract the same source twice and get the same JSON (key order aside). Non-determinism on
identical input means the extraction can't be trusted to reproduce — a value that appears on one run
and not the next is, at best, low-confidence, at worst a coin-flip hallucination. Reduce temperature,
pin the prompt, and treat run-to-run drift on the same source as a real reliability defect.

The output of this axis feeds the **extraction-report card**'s `schema_verdict` (see `policy.md`),
emitted by `schema-check.py`.
