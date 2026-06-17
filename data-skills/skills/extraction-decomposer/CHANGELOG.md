# Changelog — extraction-decomposer

Versioned independently of the `data-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.1.0 — draft

Initial release. Decompose / design / grade a structured extraction on the **FIDELITY × VALIDITY**
crossing axes, scored separately with a gated rubric and the opposite-defect quadrant.

- **The two-axis method** (`references/decomposition-method.md`): Fidelity (completeness →
  faithfulness → normalization → disambiguation → provenance) × Validity (well-formed → schema →
  constraints → robustness → stability), crossing at the schema; gates before reviews; the *valid
  JSON, invented values* vs *faithful but malformed* quadrant; and **the instructive inversion** — the
  cheap gate (schema validation) is blind to the dangerous failure, so the *gate-where-you-can,
  adversarially-verify-where-you-can't* doctrine routes VALIDITY to a schema check and FIDELITY to a
  groundedness check plus a fresh-context adversarial cross-check.
- **The groundedness check** (`references/groundedness.md` + `bin/groundedness-check.py`): the
  centerpiece — a deterministic attack on the *valid JSON, invented values* quadrant. Asserts every
  scalar is grounded in the source (exact / normalized / numeric-key / date-reformat), flags any
  ungrounded scalar as a likely hallucination, skips booleans/nulls. `selftest` proves a faithful
  extraction passes clean and an invented value is flagged. The failure taxonomy: invented ·
  wrong-span · over-normalized · coerced-to-satisfy-required.
- **The schema validator** (`references/validity-axis.md` + `bin/schema-check.py`): a stdlib-only
  JSON-Schema-subset validator (type incl. nullable type-lists, required, properties, items, enum,
  minimum/maximum, minLength/maxLength, pattern). `selftest` proves a conforming doc validates and
  each type/required/enum/pattern/range/nested violation is caught.
- **The Fidelity axis** (`references/fidelity-axis.md`): completeness, the no-invented-values
  discipline, normalization-without-distortion, disambiguation, provenance, and the fresh-context
  **adversarial source cross-check** prompt.
- **Schema design** (`references/schema-design.md`): required vs optional, nullable type-lists, enums
  as a closed-vocabulary gate, constraints-as-fidelity-guards, provenance-in-schema, and the
  **allow-null-over-hallucinate** rule that makes honest extraction structurally representable.
- **Policy** (`references/policy.md`): the 10-point definition-of-done, the extraction-report card
  (`{schema_verdict, groundedness_findings[], adversarial_verdict}`), and the handoff seams to
  `query-decomposer`, `code-decomposer`, and `plan-prd`.

First skill in the new `data-skills` plugin.
