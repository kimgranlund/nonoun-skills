# Roadmap — type-decomposer

Ships its core in 0.1.0 (the two axes, the instance-check validator, the model-smell linter, the
type-spec card, the collapse toolkit). Everything below is additive.

## `bin/instance-check.py`

- [x] **Conditional + composition keywords** — `if`/`then`/`else` (cross-field legality), and the
      composition set `allOf`/`anyOf`/`oneOf`/`not` (`oneOf` is exactly-one). Each composed/conditional
      subschema reuses the same recursive `validate()`, so type-aware equality / `format` / `$ref` /
      `required` apply inside the branches; default-deny is preserved for still-unknown keywords.
      Local `$ref`/`$defs` resolution already shipped. Locked with legal+illegal fixtures. *(0.2.2)*
- [x] More JSON Schema keywords (0.2.3): `patternProperties`, `contains`, and `dependentRequired`
      (cross-field legality) added (recursive, default-deny preserved).
- [x] The remaining structural keywords (0.2.4): `propertyNames` (each key validates as a string),
      `dependentSchemas` (X present → whole instance must validate against a schema), and
      `minContains`/`maxContains` (refine `contains`'s match count). Default-deny still holds for
      `prefixItems`/`unevaluatedProperties`.
- [ ] **Uninhabited-type detection** (B2) — flag an `allOf`/`oneOf` whose branches can never be
      satisfied together (a representable-in-schema, impossible-to-instantiate type).
- [ ] **Cardinality report** — estimate the admitted-state count vs the declared legal-state count
      to surface over/under-modeling numerically.
- [ ] Emit a machine-readable report (JSON) so GRADE can fold instance findings into the card.

## `bin/model-smells.py`

- [x] **Type-stub input** — detect the smells over TypeScript `type`/`interface` (regex +
      brace-matching) and Python `TypedDict`/`dataclass` (stdlib `ast`) text, not just JSON Schema.
      Dispatched by file extension; `.ts`/`.tsx`/`.py`/`.pyi` join `.json` in a dir scan. *(0.2.1)*
- [ ] **Nullable-confusion** smell — flag fields that are both optional and nullable (the
      absent/null/value three-state trap).
- [ ] **Sum-without-discriminant** smell — a `oneOf` of object branches with no shared `const`
      discriminant (hard to narrow, easy to mis-validate).

## Deferred review minors (noted, not yet done)

- **OPEN_RECORD noise on extensible bags** — the smell fires on *every* object lacking
  `additionalProperties:false`, including legitimately-extensible maps/bags. Add a suppression when a
  field is clearly a typed open bag (e.g. `additionalProperties` is a schema, or the name reads
  `*_meta`/`extra`/`extensions`), or downgrade it to advisory-only for such shapes.
- **Format coverage** — `instance-check.py` asserts `email`/`uri`/`url`/`uuid`/`date`/`date-time`;
  other formats (`ipv4`, `hostname`, `time`, `duration`, `regex`, …) are accepted as non-asserting.
  Express those as `pattern` for now, or extend `_FORMAT`.
- **Local `$ref` only** — `$ref` resolution covers `#/$defs` and `#/definitions`; remote refs and
  `$dynamicRef`/recursive cross-document refs remain default-deny (`UNSUPPORTED_SCHEMA`). Full
  resolution is tracked under the keyword backlog above.

## Method & corpus

- [ ] A **routing-eval corpus** (the maturity step the repo ROADMAP tracks) — especially the
      boundaries with `code-decomposer` (the code over the type), `extraction-decomposer` (the schema
      an extraction is checked against), `query-decomposer` (DDL), and `arch-system` (boundaries).
- [ ] A worked **end-to-end transcript** (a `RequestState` boolean-blind type → DECOMPOSE → collapse
      to a tagged union → the red→green illegal-instance proof), checked in and dogfooded.
- [ ] A **per-target cheat-sheet** appendix to `type-systems.md` (the exact construct in each
      language for each of the four collapses).
- [ ] A shared **adversarial-probe template** (the fresh-context "construct an illegal state" prompt),
      aligned in shape with the probes in `extraction-decomposer` and `proof-decomposer`.
