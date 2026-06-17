# The two-axis method — MODEL × VALIDITY

A type or schema is **correct on two independent axes that walk the same hierarchy in opposite
directions** — the decomposer seam applied to a data model: a set of types, a JSON Schema, a
protobuf, a database DDL.

- **Model · whole → part** grades the **state space**: does it model the right domain → make every
  ILLEGAL state unrepresentable → and every LEGAL state representable → through sums/products →
  with invariants enforced by construction. *"Does it model the domain — only the legal states?"*
- **Validity · part → whole** grades the **mechanism**: does it parse/compile → type-check /
  schema-validate soundly → accept every legal instance and REJECT every illegal one → round-trip
  losslessly → migrate safely. *"Does it actually hold, and reject what it should?"*

They **cross at the type/schema** — the declaration is *both* the claim about the domain's set of
legal values and the executable validator/compiler that admits or rejects an instance. A model can
be:

- **models it right, won't hold** — the right state space conceived, but a `$ref` that doesn't
  resolve, a recursive type the compiler rejects, a constraint that contradicts a default. *Right
  idea, won't validate.*
- **valid, admits illegal states** — compiles and validates cleanly, but boolean-blind / optional-
  soup / stringly-typed, so impossible states are representable and the bugs that should be
  impossible-by-construction stay possible. *The signature failure.*

Opposite defects, opposite fixes — so you **score and report the two axes separately, never
averaged.**

## The leveled walk

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Model** | whole → part | **A1** Domain `[gate]` → **A2** State-space `[gate]` → **A3** Sums vs products → **A4** Invariants → **A5** Evolution | "Does it model the domain — only the legal states?" |
| **B · Validity** | part → whole | **B1** Well-formed `[gate, code]` → **B2** Sound `[gate, code]` → **B3** Instances `[gate, code]` → **B4** Round-trip → **B5** Migration | "Does it actually hold, and reject what it should?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it).
`A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable model is **≥4 on every review with zero gate
failures**, reported as two separate axis scores plus the quadrant.

### A · Model (whole → part)

- **A1 Domain `[gate]`** — does it model the right concept (the entity / relationship / event), not
  an adjacent one? Name the domain in one sentence first.
- **A2 State-space `[gate]`** — the cardinality match: every LEGAL state is representable **and** no
  ILLEGAL state is representable. This is "make illegal states unrepresentable." Mis-match here
  poisons everything below.
- **A3 Sums vs products `[review]`** — sum types (unions / tagged enums) where the domain is *one
  of*; product types (records) where *all of*. Boolean blindness and flag soup encode impossible
  states; replace them with a sum.
- **A4 Invariants `[review]`** — invariants enforced **by construction** (smart constructors,
  newtypes, `NonEmpty`, refined types, `additionalProperties:false`, `oneOf`) rather than by runtime
  check or a comment. No primitive obsession (an `Email` is not a `String`).
- **A5 Evolution `[review]`** — can it change without breaking consumers (additive, optionality
  discipline, versioning), and does it fit the surrounding type system / schema conventions?

### B · Validity (part → whole)

- **B1 Well-formed `[gate, code]`** — parses/compiles as a type or schema in the target system.
- **B2 Sound `[gate, code]`** — type-checks / schema-validates with no internal contradiction (a
  default that violates a constraint, an enum value outside its own domain, a `$ref` that doesn't
  resolve).
- **B3 Instances `[gate, code]`** — **every declared LEGAL instance validates AND every declared
  ILLEGAL instance is REJECTED.** Routed to `bin/instance-check.py`. An illegal instance that
  validates is an illegal state that is representable — A2 has actually failed, proven mechanically.
- **B4 Round-trip `[review]`** — serialize → deserialize is lossless; no silent coercion (a number
  that becomes a string, a missing field that becomes a default).
- **B5 Migration `[review]`** — a change ships a safe migration; backward / forward compatibility.

## The opposite-defect quadrant

```
                 B · VALIDITY passes       B · VALIDITY fails
A · MODEL    ┌────────────────────────┬────────────────────────┐
  passes     │      SHIPPABLE         │  models it right,       │
             │                        │  won't hold — right     │
             │                        │  state space, but a     │
             │                        │  $ref / recursion /     │
             │                        │  contradiction breaks   │
             │                        │  validation             │
             ├────────────────────────┼────────────────────────┤
A · MODEL    │ valid, admits illegal  │       REBUILD           │
  fails      │ states — compiles &    │                         │
             │ validates, but boolean-│                         │
             │ blind / optional-soup /│                         │
             │ stringly-typed lets    │                         │
             │ impossible states in   │                         │
             └────────────────────────┴────────────────────────┘
```

The quadrant **names the fix**: top-right needs the schema/type machinery; bottom-left needs *model*
work — collapse the wide state space with a sum type, a closed record, a refined type.

## The doctrine — the state space is the contract

This is why the skill earns its place: a type's real meaning is the **set of values it admits**, not
its field names. You cannot eyeball whether illegal states are representable — you **prove** it.

- Route **VALIDITY** to the compiler / schema-validator (`bin/instance-check.py`): feed it a LEGAL
  instance set (all must validate) **and an ILLEGAL instance set (all must be rejected)**. The
  illegal set is the mechanized proof of "make illegal states unrepresentable."
- `bin/model-smells.py` is the cheap static pre-filter for the MODEL axis (boolean blindness,
  optional soup, primitive obsession, open records) — it points at where the state space is wider
  than the domain, before you write the counterexample.
- Probe the MODEL **adversarially**: in a fresh context, ask *"what illegal state can I still
  construct that this type accepts?"* Any answer becomes a new illegal instance — and a smell the
  static pass should have caught or a sum type you owe.

## Modes

- **SPECIFY** — design the type from the domain's state space: enumerate legal states, enumerate the
  illegal states you must forbid, then choose sums/products/refinements that make the illegal set
  unrepresentable; emit a type-spec card with both instance sets.
- **DECOMPOSE** — read a type/schema → recover the state space it actually admits → run the
  legal/illegal instance sets + the smell scan → grade.
- **GRADE** — score both axes, gates first (run `instance-check.py` + `model-smells.py`), place in
  the quadrant, name one corrective per failure.
