---
name: type-decomposer
description: >
  Decompose, design, and grade a type or schema (a domain model, JSON Schema, protobuf, SQL DDL) on
  two crossing axes — MODEL (domain → state-space → sums vs products → invariants → evolution) and
  VALIDITY (well-formed → sound → instances → round-trip → migration) — scored separately so a valid
  schema can't hide a state space that admits illegal states. The core is "make illegal states
  unrepresentable", proven mechanically: VALIDITY routes to a JSON-Schema-subset validator that runs
  a LEGAL instance set (all must validate) AND an ILLEGAL instance set (all must be rejected) via
  bin/instance-check.py, plus a model-smell linter (boolean-blindness, optional-soup,
  primitive-obsession, open-record). Use when designing a domain model, reviewing a type/schema,
  tightening a type so impossible states can't exist, or grading a data model. NOT for code that uses
  the type (code-decomposer), an extraction's fidelity (extraction-decomposer), SQL query logic
  (query-decomposer), or system boundaries (architecture-decomposer).
---

# type-decomposer — grade a type on two crossing axes

A type or schema is **correct on two independent axes that walk the same hierarchy in opposite
directions** — the decomposer seam the sibling skills apply to code, queries, and components, here
applied to a data model (a set of types, a JSON Schema, a protobuf, a database DDL):

- **Model · whole → part** grades the **state space**: the domain → making every illegal state
  unrepresentable and every legal state representable → sums vs products → invariants by
  construction → evolution. *"Does it model the domain — only the legal states?"*
- **Validity · part → whole** grades the **mechanism**: it parses/compiles → type-checks soundly →
  accepts every legal instance and **rejects every illegal one** → round-trips → migrates safely.
  *"Does it actually hold, and reject what it should?"*

They **cross at the type/schema** — the declaration is *both* the claim about the domain's set of
legal values and the executable validator/compiler. A model can be **models it right, won't hold**
(the right state space, but a `$ref` that won't resolve or a contradiction breaks validation) or
**valid, admits illegal states** (compiles and validates cleanly, but boolean-blind / optional-soup /
stringly-typed lets impossible states through). Opposite defects, opposite fixes — so you **score and
report the two axes separately**, never averaged.

Why this is outsized for an LLM author: models reach for the familiar shape — a bag of optional
fields, a pair of booleans — which type-checks perfectly while quietly admitting impossible states.
That failure is invisible to the compiler and to a sympathetic read, but it is **provable**: a type's
real meaning is the *set of values it admits*, so feeding it an illegal instance set turns "make
illegal states unrepresentable" from a claim into a test.

## Quick Start

**You bring:** a type/schema (or a domain to model) and the question — "design this", "is this model
sound?", "can an illegal state exist here?", "tighten this". **You get:** a type-spec card (schema +
legal/illegal instance sets), a validity report, and a two-axis grade with the defect quadrant named.

> *"Is this `RequestState` type sound?"* (fields: `is_loading`, `is_error`, `data?`, `error?`) →
> 1. **Model — domain → state-space:** the domain is "a request is *one of* loading / ready /
>    failed" `[gate]`. The type is two booleans + two optionals = 16 *shape* states (ignoring payload); the domain allows 3
>    `[gate]` → **state-space mismatch**: `is_loading && is_error`, `data && error` are representable
>    but illegal.
> 2. **Collapse (A3):** replace with a tagged union `oneOf [loading, ready{data}, failed{error}]`.
> 3. **Validity — prove it:** write the illegal set (`{is_loading,is_error}`, `{data,error}`) and run
>    `bin/instance-check.py` `[gate]` — before the collapse they validate (illegal state
>    representable, FAIL); after, they're rejected. Run `bin/model-smells.py` to catch the
>    boolean-blindness statically.
> 4. **Review + report:** invariants/evolution (A4/A5), round-trip/migration (B4/B5), then two axis
>    scores + the quadrant cell — gate failures first.

**Modes:** **SPECIFY** (enumerate legal + illegal states → choose sums/refinements that forbid the
illegal set → emit a type-spec card) · **DECOMPOSE** (read a type → recover the state space it admits
→ run the instance sets + smell scan → grade) · **GRADE** (score both axes, gates before reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Model** | whole → part | **A1** Domain → **A2** State-space → **A3** Sums vs products → **A4** Invariants → **A5** Evolution | "Does it model the domain — *only* the legal states?" |
| **B · Validity** | part → whole | **B1** Well-formed → **B2** Sound → **B3** Instances → **B4** Round-trip → **B5** Migration | "Does it *hold*, and *reject* what it should?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it).
`A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable model is **≥4 on every review with zero gate
failures**, reported as two separate axis scores plus the defect quadrant.

## The doctrine — the state space is the contract

The reason this earns a skill: a type's real meaning is the **set of values it admits**, not its
field names — and you cannot eyeball whether illegal states are representable, you **prove** it.

- Route **VALIDITY** to the validator: `bin/instance-check.py` runs a LEGAL instance set (all must
  validate) **and an ILLEGAL instance set (all must be rejected)**. An illegal instance that
  validates *is* a representable illegal state — A2 has failed, proven mechanically. The validator
  carries the unrepresentability tools (`oneOf`, `additionalProperties:false`, `const`/`enum`,
  `not`, `pattern`, asserting `format`, local `$ref`) so the illegal set can actually be rejected by
  the schema. It is a **subset** and **default-deny**: a schema using a keyword it can't enforce
  fails loud as `UNSUPPORTED_SCHEMA`, never a silent green (the supported/unsupported list lives in
  `references/type-systems.md`).
- `bin/model-smells.py` is the cheap static pre-filter for the MODEL axis — boolean-blindness,
  optional-soup, primitive-obsession, open-record — pointing at where the state space is wider than
  the domain before you write the counterexample.
- Probe the MODEL **adversarially** in a fresh context: *"what illegal state can I still construct
  that this type accepts?"* Every answer becomes a new illegal instance and a smell to catch.

The toolkit of collapses (boolean→sum, optional-soup→variants, primitive→newtype, open→closed) is in
`references/illegal-states.md`.

## §SelfAudit

- **The state space is the contract, not the field names.** Grade the set of values the type admits.
  A model that type-checks can still admit impossible states — that's the defect this skill exists to
  catch.
- **"Unrepresentable" is a test, not a claim.** Prove A2 with an ILLEGAL instance set that
  `instance-check.py` rejects; a missing illegal set is *no evidence*, like a missing test suite.
- **Tightening can over-shoot — keep the legal set.** A model that rejects a *legal* instance is as
  wrong as one that admits an illegal one. The target is the exact state space, not the smallest.
- **Gates before reviews, always.** Don't grade invariants for a schema that won't resolve, or
  evolution for a type whose state space is wrong. Stop each axis at its first failed gate.
- **Two scores, never one.** *Models-it-right-won't-hold* and *valid-admits-illegal-states* need
  opposite fixes (the schema machinery vs a sum type). Report both axes and name the quadrant.
- **Model, not code or content.** This skill grades the type's state space — it does not grade the
  code that uses it (`code-decomposer`), an extraction's fidelity (`extraction-decomposer`), or query
  logic (`query-decomposer`). Hand off; don't overlap.

## Verify Target

A type/schema is **done** when: it models the right domain with a state space that matches it —
every legal state representable, no illegal state representable (A1/A2); sums/invariants/evolution
≥4; it parses, resolves, and is contradiction-free (B1/B2); `instance-check.py` is green — **every
legal instance validates and every illegal instance is rejected**, the illegal set covering each
forbidden state; round-trip/migration ≥4; and both axes score ≥4 with zero gate failures, landing in
the **SHIPPABLE** quadrant, with the type-spec card + validity report ready for handoff. **NOT done**
when: it validates cleanly but a boolean-blind / optional-soup / stringly-typed shape admits an
illegal state (*valid, admits illegal states*); or the model is right but won't resolve/compile
(*models it right, won't hold*); or there's no illegal instance set (unrepresentability unproven); or
one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Model × Validity), the leveled walk with gates, the quadrant, the state-space-is-the-contract doctrine, and the SPECIFY / DECOMPOSE / GRADE workflows |
| `references/model-axis.md` | **the Model axis** — the state-space cardinality test, sums vs products, invariants by construction, evolution, and the adversarial "what illegal state can I construct" probe |
| `references/validity-axis.md` | **the Validity axis** — the well-formed/sound/instances ladder and the legal/illegal instance-set discipline (the mechanized proof of A2); mechanized by `bin/instance-check.py` |
| `references/illegal-states.md` | **the centerpiece** — the make-illegal-states-unrepresentable toolkit: boolean-blindness→sum, optional-soup→variants, primitive-obsession→newtype, open→closed records, with before/after and the red→green proof |
| `references/type-systems.md` | **choosing the target** — what TS / Rust / ML-family / JSON Schema / protobuf / SQL DDL / GraphQL can each make unrepresentable, nullability hazards, and modelling the contract in JSON Schema for the mechanized B3 |
| `references/policy.md` | **definition-of-done / handoff** — the 10-point DoD, the type-spec card (schema + legal/illegal sets), and the seams to `code-decomposer`, `extraction-decomposer`, `query-decomposer`, `architecture-decomposer` |
| `bin/instance-check.py` | **mechanizes B3** — a JSON-Schema-subset validator (`oneOf`, `additionalProperties:false`, `const`/`enum`, `not`, `pattern`, asserting `format`, local `$ref`, …) that runs a spec's legal/illegal instance sets; a legal reject, an illegal accept, or an unsupported keyword (default-deny → `UNSUPPORTED_SCHEMA`) is a finding. `<spec.json>` · `selftest` |
| `bin/model-smells.py` | **mechanizes the A3/A4 pre-filter** — flags boolean-blindness, optional-soup, primitive-obsession, open-record, stringly-typed-enum over a **JSON Schema (`.json`), TypeScript (`.ts`/`.tsx`), or Python (`.py`/`.pyi`)** type definition, dispatched by extension (a dir scan reads all three). `<schema.json\|types.ts\|types.py\|dir>` · `selftest` |
