# Policy — definition-of-done, the card, and the handoff

The reusable artifacts and boundaries: what "done" means for a type/schema, the shape of the
type-spec card the skill emits, and how it hands off to the rest of the fleet without overlapping it.

## Definition-of-done (a type/schema is shippable when…)

Gated items route to `bin/`; review items are 1–5 judgments. SHIPPABLE = the quadrant top-left.

1. **Right domain (A1)** — models the actual concept, named in one sentence (not the transport).
2. **State space matches (A2)** — every legal state representable; no illegal state representable.
3. **Sums where the domain is "one of" (A3)** — no boolean blindness, no flag soup; cardinality is
   sum-not-product where it should be (≥4).
4. **Invariants by construction (A4)** — newtypes/refinements/closed records over primitives and
   runtime checks; no primitive obsession (≥4).
5. **Evolves safely (A5)** — additive change path, optionality/nullability discipline, fits
   conventions (≥4).
6. **Well-formed & sound (B1/B2)** — parses/compiles; `$ref`s resolve; no contradiction, no
   uninhabited type.
7. **Instances prove it (B3)** — `instance-check.py` green: every legal instance validates **and
   every illegal instance is rejected**; the illegal set covers each forbidden state from A2.
8. **Round-trips losslessly (B4)** — serialize→deserialize preserves the value; no silent coercion
   (≥4).
9. **Migration-safe (B5)** — a schema change ships a forward/backward path (≥4).
10. **Both axes ≥4, zero gate fails, SHIPPABLE quadrant** — two scores, gate failures first, with the
    type-spec card + validity report ready for handoff.

## The type-spec card

The artifact SPECIFY emits and DECOMPOSE re-derives — a JSON spec checked by `bin/instance-check.py`:

```json
{
  "type": "PaymentMethod",
  "domain": "how a customer pays — exactly one of card or cash",
  "schema": {
    "oneOf": [
      { "type": "object", "additionalProperties": false, "required": ["method", "card_number"],
        "properties": { "method": { "const": "card" },
                        "card_number": { "type": "string", "minLength": 12 } } },
      { "type": "object", "additionalProperties": false, "required": ["method"],
        "properties": { "method": { "const": "cash" } } }
    ]
  },
  "legal":   [ { "method": "card", "card_number": "4111111111111" }, { "method": "cash" } ],
  "illegal": [ { "method": "card" },
               { "method": "cash", "card_number": "4111111111111" },
               { "method": "wire" },
               {} ]
}
```
The legal/illegal sets are the contract of record — they version with the schema and are the diff a
reviewer reads first. `bin/model-smells.py` is the cheap everywhere-pass; the illegal set is the
targeted proof.

## Governance

- **Keep the instance sets next to the schema** and check them in; a new legal state adds a legal
  instance, a newly-forbidden state adds an illegal one. CI runs `instance-check.py` so a model
  change that re-admits an illegal state fails the build.
- **Model the contract in JSON Schema for the mechanized B3** even when the runtime type lives in
  TS/Rust/SQL (see `type-systems.md`), then mirror it into the host system.

## Handoff — what this skill does NOT do

`type-decomposer` designs and grades the *model*; it feeds the others:

- **→ `code-decomposer`**: the code that *uses* the type — its contract (A2 of code-decomposer) is
  usually a type this skill graded. type-decomposer grades the type; code-decomposer grades the
  function over it.
- **→ `extraction-decomposer`**: an LLM extraction is validated against a schema — type-decomposer
  designs/grades that schema (is it tight enough that an invented or illegal value can't be valid),
  extraction-decomposer grades a given extraction's fidelity to a source.
- **→ `query-decomposer`**: a SQL schema's grain/constraints; type-decomposer owns the DDL's state
  space, query-decomposer owns a query over it.
- **← `arch-system`**: hands *in* the domain boundaries and where state lives. type-decomposer grades
  the type at a boundary; it doesn't design the system topology.
- **not `/code-review` or `/verify`**: diff-time bug review and app-time behavior — different
  altitude and phase.
