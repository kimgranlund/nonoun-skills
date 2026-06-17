# Changelog — type-decomposer

Versioned independently of the `code-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

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
