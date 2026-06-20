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
