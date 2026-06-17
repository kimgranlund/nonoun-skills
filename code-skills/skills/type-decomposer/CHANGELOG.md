# Changelog — type-decomposer

Versioned independently of the `code-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.2.4 — beta

**The remaining structural JSON-Schema keywords** in `instance-check`: `propertyNames` (every property
name validates as a string against the subschema), `dependentSchemas` (if property X is present, the
whole instance must additionally validate against a schema), and `minContains`/`maxContains` (refine
`contains`'s match count; `minContains: 0` lets zero matches pass). Recursive through `validate()`;
default-deny intact — `prefixItems`/`unevaluatedProperties` still raise `UNSUPPORTED_SCHEMA`. Legal/
illegal instance fixtures lock each.

## 0.2.3 — beta

**More JSON-Schema keywords** in `instance-check`: `patternProperties` (regex-keyed property schemas),
`contains` (an array must hold ≥1 matching element), and `dependentRequired` (if property X is present,
Y is required). Each validates through the same recursive `validate()` — type-aware equality, asserting
`format`, and local `$ref` all apply inside — and the default-deny is intact: a still-unknown keyword
(`propertyNames`, `dependentSchemas`, `minContains`) still raises `UNSUPPORTED_SCHEMA`. Legal/illegal
instance fixtures lock each.

## 0.2.2 — beta

`bin/instance-check.py` now validates **conditional + composition schemas** (closes the ROADMAP
keyword item). The composition keywords `allOf`/`anyOf`/`oneOf`/`not` were already enforced —
verified and locked — with `oneOf` confirmed **exactly-one** (a value matching two branches, or
none, is rejected: the discriminated-union contract, not at-least-one). New this cycle:
`if`/`then`/`else` — *if* the instance validates against `if` it must validate against `then`,
otherwise against `else`; each branch optional, `if` failing with no `else` is a pass, and a bare
`then`/`else` with no `if` is inert. Every composed/conditional subschema is validated by the
**same recursive `validate()`**, so type-aware equality (`true ≠ 1`), asserting `format`, local
`$ref`, and `required` all apply *inside* the branches. The **default-deny is intact**: only these
keywords joined the supported set — a genuinely unknown keyword (`contains`, `patternProperties`, …)
appearing anywhere still surfaces as `UNSUPPORTED_SCHEMA` rather than false-greening. Locked with
legal+illegal fixtures for each shape: a oneOf tagged union (both-match and neither-match rejected),
if/then/else (card-with-number passes, card-without-number fails, non-card-with-account passes), an
`if`-with-no-`else` case, allOf (fail-one rejected), anyOf (none rejected), `not` (forbidden shape
rejected), plus a `contains` fixture asserting default-deny still fires. The existing keyword set and
all hardening (bool≠int equality, `5.0 ⊨ integer`, format enforcement, `$ref` resolution) are
untouched. `references/validity-axis.md` and `references/type-systems.md` move the keywords from the
unsupported to the supported list.

## 0.2.1 — beta

`bin/model-smells.py` now reads **TypeScript and Python type definitions**, not only JSON Schema
(closes the ROADMAP "Type-stub input" item). Input dispatches on file extension — `.json` keeps the
unchanged JSON-Schema walk; `.ts`/`.tsx` are brace-matched and field-parsed (regex, no stdlib TS
parser); `.py`/`.pyi` are parsed with the stdlib `ast` module (precise — `TypedDict` subclasses and
`@dataclass` bodies), with a regex fallback for fragments that won't `ast.parse`. A directory scan
now picks up all three. The same five finding KINDS and message style are reused; each language reads
its own collapse tools as the clean form (a TS branded primitive / string-literal union / literal
discriminant; a Python `NewType`/`Literal`-typed field clears the matching smell). New TS and Python
dirty+clean selftest fixtures lock every detector; the existing JSON-Schema fixtures and assertions
are untouched. `references/type-systems.md` documents the three-dialect dispatch. The TS field parser
handles single-line `;`-separated fields, and constrained-name detection is camelCase-aware (`userId`),
both locked with selftest fixtures.

## 0.2.0 — beta

Promoted to beta as part of the marketplace **v0.2.0** milestone (see the root CHANGELOG). This cycle the skill gained a checked-in, sibling-collision-tested routing-eval corpus, an adversarial-review hardening pass (fixes locked as selftest fixtures), and a worked `examples/walkthrough.md` (a red→green bin proof).

## 0.1.0 — draft

Initial release. Decompose / design / grade a type or schema on the **MODEL × VALIDITY** crossing
axes, scored separately with a gated rubric and the opposite-defect quadrant, around the principle
*make illegal states unrepresentable*.

- **The two-axis method** (`references/decomposition-method.md`): Model (domain → state-space → sums
  vs products → invariants → evolution) × Validity (well-formed → sound → instances → round-trip →
  migration), crossing at the type/schema; gates before reviews; the *models-it-right-won't-hold* vs
  *valid-admits-illegal-states* quadrant; the state-space-is-the-contract doctrine.
- **The instance gate** (`references/validity-axis.md` + `bin/instance-check.py`): a JSON-Schema
  SUBSET validator carrying the unrepresentability tools — `oneOf` (tagged unions),
  `additionalProperties:false` (closed records), `const`/`enum`, `not`, `allOf`/`anyOf` — that runs a
  spec's LEGAL instance set (all must validate) and ILLEGAL instance set (all must be rejected). An
  illegal instance that validates is a representable illegal state — the mechanized proof of A2.
- **The model-smell linter** (`references/illegal-states.md` + `bin/model-smells.py`): a static
  scan for the state-space wideners — boolean-blindness, optional-soup, primitive-obsession,
  open-record, stringly-typed-enum.
- **The Model axis** (`references/model-axis.md`): the cardinality test, sums-vs-products, invariants
  by construction, and the fresh-context adversarial "what illegal state can I construct" probe.
- **The collapse toolkit** (`references/illegal-states.md`, the centerpiece): boolean→sum,
  optional-soup→variants, primitive→newtype, open→closed, each with before/after and the red→green
  instance-check proof.
- **Type systems** (`references/type-systems.md`): what TS / Rust / ML-family / JSON Schema /
  protobuf / SQL DDL / GraphQL can each make unrepresentable, and modelling the contract in JSON
  Schema for the mechanized B3.
- **Policy** (`references/policy.md`): the 10-point definition-of-done, the type-spec card (schema +
  legal/illegal sets), and the handoff seams to `code-decomposer`, `extraction-decomposer`,
  `query-decomposer`, `arch-system`.

The fifth skill in the `code-skills` plugin (with code-, regex-, query-decomposer and figma-plugins).
