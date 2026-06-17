# Changelog — extraction-decomposer

Versioned independently of the `data-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.2.3 — beta

**Span emission (provenance) + a configurable weak-grounding floor** — two additive, opt-in CLI flags:
- `--spans` — for each grounded scalar, also emit the SOURCE offset + snippet that grounded it (A5
  provenance), so a green run shows *where* each value came from, not only pass/fail.
- `--min-tokens N` / `--min-chars N` — expose the WEAK_GROUNDING floor (was a hardcoded 2/4) so a
  high-recall corpus can tighten or loosen the band.

Default output and exit code are byte-identical to before (no flag → unchanged). Locked with fixtures.

## 0.2.2 — beta

**Locale dates & non-ASCII digits grounded.** The follow-on to 0.2.1, in the same additive,
source-side style — the tuned `_num_key`/date canonicalizers' existing output is untouched.

- **DD.MM.YYYY-dominant dates.** A slashed *or dotted* numeric date is ambiguous, so the source keys
  under **both** the D/M/Y and M/D/Y readings: a European `02.01.2026` now grounds an extraction
  normalized to `2026-01-02` (D/M/Y), while a US `02/01/2026` still grounds `2026-02-01` (M/D/Y) —
  accepting either is correct for a fidelity *aid*. A new `_valid_ymd` range guard drops impossible
  readings, so an unambiguous `25/12/2026` (day > 12) emits only the D/M/Y key, never a phantom
  month-25 M/D/Y one. Additive: an impossible key could never match a real extraction, so no existing
  grounding is lost. Locked with must-GROUND (`2026-01-02`←`02.01.2026`, `2026-12-25`←`25/12/2026`,
  `2026-02-01`←`02/01/2026`), the impossible-key guard, and a must-NOT-ground fixture (`2026-07-04`
  against a source with no such date).
- **Non-ASCII digit scripts.** Arabic-Indic (`٠١٢…`), Eastern-Arabic/Persian (`۰۱۲…`), Devanagari
  (`०१२…`), and fullwidth (`０１２…`) digits are folded to ASCII (via `unicodedata.digit`, stdlib)
  **before** numeric/date key extraction, on both the source and the value. So a source `المبلغ ١٢٣٤`
  grounds `1234`, `２０２６` grounds `2026`, and `٢٠٢٦-٠١-٠٢` grounds the date `2026-01-02`. Additive: an
  all-ASCII string takes a fast path and is byte-identical, so no existing grounding moves. Guarded
  against over-match with a must-NOT-ground fixture (`5678` stays ungrounded against `١٢٣٤`).

All existing M1 (numeric back-door) and 0.2.1 EU/scientific fixtures still pass; the repo gate
(`bin/check-skills.py`) is green.

## 0.2.1 — beta

**Locale-aware numeric grounding.** A faithful value normalized from an EU-format source number
(`1.234,56` → `1234.56`) or scientific notation (`1.5e3` → `1500`) now grounds, instead of being
flagged as a value to verify. The fix is **additive and source-side only** — extra grounding keys for
EU/scientific source tokens, leaving the adversarially-tuned `_num_key` and its M1 (numeric back-door)
fixtures untouched. The EU pattern requires a `,\d+` decimal tail, so a bare `1.234` stays US-format
(no new false groundings). Locked with selftest fixtures (EU + scientific ground; an invented value
still does not). The 0.2.2 follow-on closes the then-deferred DD.MM.YYYY dates and non-ASCII digits.

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
