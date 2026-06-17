# The VALIDITY axis — does it hold, and reject what it should?

The Validity axis (B1–B5) grades the *mechanism*, bottom-up: from "does this declaration even parse"
to "does it migrate safely." It is the **mechanizable** axis — route it to the compiler / schema
validator and **trust the tool, not the read-through**. The decisive, non-obvious gate is B3: a
validator that accepts everything legal proves nothing until it also REJECTS everything illegal.

## The ladder

| Level | Gate | What proves it | The signal |
|---|---|---|---|
| **B1 Well-formed** | `[gate]` | the type checker / schema parser / DDL parser | it parses and loads as a type/schema in the target system |
| **B2 Sound** | `[gate]` | the same, plus `$ref`/import resolution | no internal contradiction: a default that violates its constraint, an enum value outside its domain, an unresolved `$ref`, an uninhabited type |
| **B3 Instances** | `[gate, code]` | `bin/instance-check.py` | **every legal instance validates AND every illegal instance is rejected** |
| **B4 Round-trip** | review | encode/decode tests | serialize→deserialize is lossless; no silent coercion |
| **B5 Migration** | review | a migration + compat test | a schema change has a safe forward/backward path |

Gates cascade: don't grade migration (B5) for a schema that doesn't resolve (B2). A red gate stops
the axis.

## B3 — the legal/illegal instance discipline (the crux)

"Make illegal states unrepresentable" (A2) becomes a *test* here. Maintain two sets alongside the
schema:

- **Legal instances** — at least one per legal state (each sum variant, each boundary, the
  empty/optional cases). All must validate. A legal instance that's rejected means the model is too
  tight (it forbids a legal state) — a real A2 failure in the other direction.
- **Illegal instances** — one per illegal state you claim is unrepresentable: the cross-variant mix
  (cash + card number), the missing discriminant, the out-of-range value, the extra field on a
  closed record, the empty where `minItems:1`. **Every one must be REJECTED.** An illegal instance
  that validates is the headline finding: *that illegal state is representable* — the schema does not
  actually make it impossible.

Run it: `python3 bin/instance-check.py spec.json`, where the spec is
`{ "schema": {…}, "legal": [...], "illegal": [...] }`. The validator carries the subset that
expresses the unrepresentability tools — `oneOf` (tagged unions), `additionalProperties:false`
(closed records), `const`/`enum`, `required`, `not`, `allOf`/`anyOf`, `pattern`, an asserting
`format` set, and local `$ref` — so the illegal set can actually be rejected by the schema rather
than by hand-waving. It is a **subset** and **default-deny**: a schema using a keyword it can't
enforce (`if/then/else`, `patternProperties`, tuple-`items`, a remote `$ref`, …) FAILS LOUD as an
`UNSUPPORTED_SCHEMA` finding instead of false-greening — so a green is a green over the *supported*
subset, never a silent pass. The full supported/unsupported list lives in
`references/type-systems.md`.

A green B3 is the mechanized proof of A2. This is why the two axes cross at the schema: the illegal
instance set is simultaneously a MODEL claim (these states are illegal) and a VALIDITY test (the
schema rejects them).

## Reading each tool's signal

- **Parser / compiler (B1)** — the cheapest gate; catches the malformed schema, the unresolved
  `$ref`, the unknown keyword, the recursive type the system can't express.
- **Type checker / validator (B2)** — catches contradictions a parse can't: a `default` outside its
  `enum`, a `const` that conflicts with a sibling, an `allOf` whose branches can never both hold
  (an uninhabited type — representable in the schema, impossible to instantiate).
- **`instance-check.py` (B3)** — the verdict. Treat a missing illegal set as *no evidence* that
  illegal states are unrepresentable, exactly like a missing test suite.
- **Round-trip (B4)** — the place silent coercion hides: a JSON number decoded into a string, a
  missing optional materialized as a default, a sum variant flattened on the wire. Test the
  serializer, not just the schema.

The output of this axis is the **validity report** — which gates ran, the instance-set verdict, and
any round-trip/migration findings — handed with the type-spec card to the consumers of the model
(`code-decomposer` for the code that uses it, `extraction-decomposer` for extractions validated
against it).
