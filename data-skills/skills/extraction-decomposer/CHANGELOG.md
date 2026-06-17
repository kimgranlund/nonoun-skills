# Changelog — extraction-decomposer

Versioned independently of the `data-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.2.0 — beta

Promoted to beta as part of the marketplace **v0.2.0** milestone (see the root CHANGELOG). This cycle the skill gained a checked-in, sibling-collision-tested routing-eval corpus, an adversarial-review hardening pass (fixes locked as selftest fixtures), and a worked `examples/walkthrough.md` (a red→green bin proof).

## Unreleased — fidelity/validity gate hardening

Closes concrete false-negative defects in both `bin/` gates (each with adversarial selftest fixtures):

- **groundedness-check.py — token/word-boundary grounding (was raw substring).** A raw-substring test
  grounded invented *fragments* of real words: `"Fran"`←`San Francisco`, `"Ware"`←`warehouse`, a split
  `"John"`+`"Smith"`←`Johnson`/`Smithfield`. Now both sides are tokenized and a value grounds only when
  its whole tokens appear as a contiguous run of whole source tokens. Adds a **weak-grounding floor**
  (1-token ≤3-char hits → `WEAK_GROUNDING — verify manually`) and a distinct `EMPTY` finding for
  empty/whitespace values (were silently "grounded"). New must-FLAG fixtures: `Fran`/`Ware`/`Del`/
  `John`/`Smith`, plus `WEAK_GROUNDING`/`EMPTY` coverage.
- **groundedness-check.py — anchored numeric back door.** A string scalar takes the NUMERIC path only
  when the *entire* trimmed string is one number token; a string that merely *starts* with a grounded
  digit (`"12 Nonexistent Street"`, `"12-FAKE-ID-9999"`) no longer grounds via the leading number. New
  must-FLAG fixture.
- **groundedness-check.py — opt-in proximity / wrong-span APPROXIMATION (`WEAK_CONTEXT`).** A new,
  optional per-field **context-cue** signal: pass `cues.json` (a map of a field's leaf name → cue
  strings, e.g. `buyer → ["buyer","bill to","purchaser"]`) and an optional `--window N` (default 12
  tokens). For a *grounded* scalar whose field has cues, if its nearest source occurrence is not within
  the window of any cue occurrence, the tool emits a `WEAK_CONTEXT` advisory — a *possible* wrong-span
  (e.g. `"Acme"` extracted as `buyer` when the source has Acme as `seller`). **Honest by design:** the
  signal is **opt-in** (no cues → no `WEAK_CONTEXT`, never a false positive on cue-less specs and never
  a regression to token-boundary grounding + the weak floor) and **advisory** (printed but does **not**
  affect the exit code — an ungrounded scalar still fails). It only *approximates* role; true role
  confirmation is a fresh-context **adversarial verify** step, **not** a claimed deterministic
  wrong-span oracle. New selftest fixtures: (a) wrong-span with cues → flagged, (b) same value near its
  cue → not flagged, (c) cue-less spec → no `WEAK_CONTEXT`, plus window-tunability and no-perturbation
  of grounding outcomes. Docs add a **"Wrong-span — the role the value plays"** subsection
  (`groundedness.md`) framing *gate presence (code) · gauge proximity (code, opt-in) · confirm role
  (adversarial verify)*, and a **role-confirmation adversarial prompt** (`fidelity-axis.md`).
- **schema-check.py — unknown/unsupported keywords no longer silently ignored.** A schema-author typo
  (`requried`, `minimun`) or an unsupported keyword (`additionalProperties`) was a silent no-op → false
  green. Each now emits `WARN: unknown/unsupported keyword 'X' — not enforced` and the run exits
  nonzero; meta/annotation keywords are ignored without warning. New typo'd-keyword fixture.
- **Docs (honesty + minors):** SKILL.md / fidelity-axis.md / groundedness.md now name the
  substring-fragment false-negative class (mitigated by token matching + the weak floor) instead of
  claiming the check comprehensively catches "the value that appears nowhere"; the FAIL message says
  "verify" rather than asserting hallucination (locale/scientific-notation false positives);
  schema-design.md notes `pattern` is unanchored (recommend `^…$`); the decomposition-method.md
  quadrant is reconciled to label **bottom-left** (valid JSON, invented values) the signature failure,
  matching SKILL.md.

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
