# Changelog — brand-decomposer

Versioned independently of the `design-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.1.0 — draft

Initial release. Decompose / design / grade / critique a **brand-guidelines artifact** — a brand book,
a design-system spec — on two crossing axes, scored separately with a gated rubric and the
opposite-defect quadrant. Built from an analysis of a 21-file agentic brand-guidelines corpus (the
DocuSign-and-16-peers Deck.gallery reference set), which reframes a brand from "taste" into a typed,
evidence-linked **operating system** that *has* gradeable properties.

- **The two-axis method** (`references/decomposition-method.md`): **A · Inside-out** (brand idea →
  meaning chain → primitives express it → range without losing identity → governance) × **B ·
  Outside-in** (well-formed → traced & trusted → accessible → complete & surfaced → retrievable),
  crossing at the typed primitive; gates before reviews; the *right-meaning-won't-operate* (beautiful
  but unusable) vs *operable-but-hollow* (typed but hollow) quadrant; and the **core-object-is-evidence**
  doctrine (three truths never collapsed; confidence as an operational band).
- **The operability gate** (`references/outside-in-axis.md` + `bin/brand-spec-check.py`): a stdlib-only
  static checker over a `*.brand.json` card — `WELL_FORMED` · `UNTRACED` · `LOW_CONFIDENCE` ·
  `COLLAPSED_TRUTH` · `CONTRAST_FAIL` (WCAG AA, shared math with `color-verifier`) · `BARE_TOKEN` ·
  `GENERIC_IDEA` · `INCOMPLETE`. `lint` · `contrast <fg> <bg> [large|ui]` · `selftest` · `--json` (the
  shared `{tool, ok, summary, findings[]}` report). Green (DocuSign) / red (degraded) fixtures.
- **The inside-out axis + the 100-point rubric** (`references/inside-out-axis.md` +
  `references/the-rubric.md`): the nine rubric areas (idea 16 · expression 14 · voice/mark/examples 12 ·
  color/type 10 · governance 8 · usability 6) mapped onto the A-levels, the 1–5 normalization, the fast
  audit (weak/strong signals), and the **adversarial idea-refutation** for the operable-but-hollow
  quadrant.
- **The trust contract** (`references/evidence-and-confidence.md`): the evidence model
  (deck→slide→source_url→method→confidence), the four confidence bands, the three truths
  (observed/inferred/proposed, never collapsed), and what the gate enforces vs. what you must still read.
- **The card schema** (`references/brand-spec-schema.md`): the `*.brand.json` card field-by-field, the
  enums faithful to the corpus schema (`severity ∈ {must, should, may}`, the three truths, the six
  rubric domains with corpus-domain normalization — `logo→mark`, `typography→type`, 11 expression
  sub-domains→`expression`), and how the card projects from the full corpus schema.
- **The six domains** (`references/the-six-domains.md`): mark · voice · color · type · expression ·
  governance — what "good" means, the operability check, and the failure mode each hides.
- **CRITIQUE mode** (`references/critique-mode.md`): grounding design-**work** critique in a *validated*
  spec — the precondition gate, the agent behavior contract (separate observed / spec / proposed),
  the never-say-"off-brand" rule (name the mechanism), the structured-critique shape
  `{alignment, tension, missing_opportunity, severity, evidence, recommended_move}`, the controlled
  exploration axes, and the seam to `brand-forge`'s judges.
- **Policy** (`references/policy.md`): the 12-point definition-of-done, the brand-spec card object, and
  the handoff seams to `brand-forge` (`brand-muse`/`brand-copywriter`/`brand-council`/`brand-evaluate`),
  `layout-decomposer`, `color-verifier`, `color-science`, and `typography-lettering`.
- A checked-in, sibling-collision-tested routing-eval corpus (`brand-decomposer.corpus.json`) and a
  worked `examples/walkthrough.md` (green→SHIPPABLE, red→both-defects, plus a grounded CRITIQUE).

Fourth crossing-axis decomposer in the `design-skills` plugin (after layout-, mermaid-,
component-decomposer).

### Defect fixes (pre-release hardening)

- **brand-spec-check — GENERIC_IDEA stopword hole:** the generic-idea check counted any non-`GENERIC`
  word as "substantive," so a stopword defeated it — `"Modern, bold, and simple."` read as non-generic
  because **"and"** is not an interchangeable adjective. Added a `STOPWORDS` set so a brand idea made of
  *only* generic adjectives + stopwords is caught. The degraded fixture's idea is exactly this shape,
  locking the fix.
- **brand-spec-check — faithfulness to the corpus schema:** the `severity` enum was an invented
  `{hard, recommended, flexible}`; aligned to the corpus's actual `{must, should, may}` (RFC-2119).
  Added `DOMAIN_ALIASES` + `_norm_domain` so a card authored against the full corpus `brand_domain`
  enum (`logo`, `typography`, the 11 expression sub-domains) normalizes to the six rubric domains
  instead of tripping spurious "unknown domain" warnings. Verified with a corpus-style fixture.

### Defect fixes — adversarial-review hardening (fresh-context red-team, locked as fixtures)

A fresh-context adversarial review (which *ran* the bin against crafted cards) surfaced five real
defects; each fix is locked by a selftest fixture so it can't regress:

- **(CRITICAL) `LOW_CONFIDENCE` / `COLLAPSED_TRUTH` were advisory WARNs but every doc page calls them
  B2 gate fails** — so the skill's own central trust defect (a guess shown as a documented rule, a weak
  inference shown as settled) passed the gate **green**. Escalated both to FAILs, matching the
  documented B2-gate contract; the selftest now asserts they appear among `fails`, not `warns`.
- **(MAJOR) `GENERIC_IDEA` was one-noun-evadable** — `"Modern, bold, simple solutions."` slipped through
  because the filler noun `solutions` read as substantive. Added a `GENERIC_NOUNS` set (category/filler
  words); locked with a must-FLAG fixture (`"…simple solutions"`) **and** a must-NOT-flag fixture (a real
  idea naming a concrete subject — `"Agreements are dynamic moments of connection."`).
- **(MAJOR) the bin tracebacked on plausible malformed cards** (`[]`, `null`, `"strategy": "text"`,
  `"rules": "oops"`, `"color_pairs": ["#000"]`). Added type-guards so every shape returns a graded
  `WELL_FORMED` FAIL (never an uncaught exception), preserving the `--json` contract; locked with a
  no-crash / must-FAIL fixture loop.
- **(MINOR) `BARE_TOKEN` was bypassed by a falsy `value`** (`""`/`0`) — switched the truthiness test to
  `"value" in tok`.
- **(MINOR) the `--json` `kind` was reverse-parsed from the message** (garbage for code-less findings).
  Findings now carry an explicit `(kind, message)` tuple, so `--json` emits a real `kind` per finding —
  the shared `{tool, ok, summary, findings[]}` report is now harness-keyable.

The corpus-faithfulness and routing-fence surfaces were found clean; the "operable-but-hollow" quadrant
is (by design) caught by the adversarial idea-refutation, with `GENERIC_IDEA` as its now-hardened
deterministic backstop.

### Added — the formal card schema (declarative B1 contract)

- **`schema/brand-spec.schema.json`** — a machine-readable JSON Schema (Draft 2020-12, with `$defs` for
  `evidence_ref` / `token` / `rule` / `example` / `color_pair`) for the `*.brand.json` card: structure,
  types, enums (`severity {must,should,may}`, the three truths, token `type`, the 19-value `domain`
  set), and required fields. `references/brand-spec-schema.md` is now its prose companion. Print it with
  `bin/brand-spec-check.py schema`; validate an arbitrary card against it with `type-decomposer`'s
  `instance-check.py` (the skill that owns instance-validation — not reimplemented here, which would
  degrade the gate's domain-meaningful findings into generic `SCHEMA_INVALID`).
- **Drift guard** — the selftest's `_schema_coherence()` asserts the schema's enums match the bin's
  constants and that the GREEN fixture satisfies the schema's required-field contract, so the artifact
  and the executable gate can't silently diverge. Proven non-trivial by a corrupt-the-enum negative
  test (mutating the schema's `severity` enum is detected). Closes the ROADMAP's top item to "formal
  schema + drift-guard shipped; full per-card validation delegated to type-decomposer."

### Added — four B-axis depth checks (advisory; locked with must-flag/must-not-flag fixtures)

Two more ROADMAP items, deepening the B axis beyond bare presence — all advisory, none can fire on the
GREEN fixture (no false positives), each locked by a fixture:

- **Evidence-reference integrity** — `THIN_EVIDENCE` (an `evidence[]` entry present but with no
  `deck_id`/`slide_id`/`source_url` — it points nowhere; still can't prove the id is *real*) and
  `DANGLING_REF` (an example's `rules_demonstrated[]` names a rule `id` not in the card — a silent B5
  retrieval break).
- **Confidence/severity & truth coherence** — `WEAK_MANDATE` (a `must` hard rule at `confidence < 0.90`
  — mandating what the deck didn't explicitly state) and `TRUTH_CONFIDENCE_MISMATCH` (an `observed`
  record at `confidence < 0.90` — a direct observation you're unsure of is really an inference). Locked
  with must-NOT-flag fixtures too (a `should` rule / an `inferred` record at the same confidence stays
  quiet). *(The sketched token role↔type mismatch was dropped — role is free-text, no low-false-positive
  deterministic form.)*
