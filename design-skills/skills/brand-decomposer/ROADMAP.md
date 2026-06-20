# Roadmap — brand-decomposer

Ships its core in 0.1.0 (the two axes, the operability gate, the 100-point rubric, the trust contract,
the `*.brand.json` card, the six-domain depth, and CRITIQUE mode). Everything below is additive.

## `bin/brand-spec-check.py`

- [ ] **JSON-Schema validation of the card** — `B1` currently checks required fields and enums
      imperatively. Vendor or generate a JSON Schema for the `*.brand.json` card (the gradeable subset
      of `brand_guideline_corpus.schema.json`) and validate against it, so the well-formedness gate is
      declarative and a card-shape change can't silently drift from the docstring. Reuse
      `type-decomposer`'s `instance-check.py` validator pattern.
- [ ] **Evidence-reference integrity** — beyond *presence*, check that each `evidence[]` entry is
      well-formed (`deck_id` + `slide_id`/`source_url` + `extraction_method` + a per-evidence
      `confidence`), and that `rules_demonstrated[]` in an example points at a real rule `id` in the
      card. A dangling rule reference is a silent retrieval break (B5).
- [ ] **Confidence/role coherence smells** — flag a `must`-severity rule whose `confidence < 0.90`
      (a hard constraint presented on weak evidence), and a token whose declared `role` contradicts its
      `type` (a `color` token with a `type`-domain role). Lock each with a must-FLAG / must-NOT-flag
      fixture pair.
- [ ] **Contrast: large-text + non-text UI defaults** — the gate reads `size`/`role` per `color_pair`;
      add an optional check that a pair used for *both* body and large text is graded at the stricter
      4.5 floor, and surface APCA as an advisory alongside WCAG 2.x (mirroring `color-verifier`'s
      trajectory) without changing the gate verdict.

## The meaning axis (A)

- [ ] **A behavioral-eval pilot** — run the `behavioral-eval-method.md` protocol (with-skill vs
      SUPPRESSED-baseline) on a real brand deck. The hypothesis: base-model competence is *inside* the
      domain (it can talk about brand fluently), so the metric is **verification/structure** — does the
      skill make the model separate the two axes, run the gate, and refute the idea rather than emit a
      confident holistic "this is a strong brand" blob? Ground the metric in the bin's findings.
- [ ] **A worked DECOMPOSE of a second corpus brand** (Burger King / Monzo / Hulu) as a second
      `examples/` card, to show the method on a louder, more expressive brand than DocuSign — and to
      stress the *range-without-losing-identity* (A4) review where a high-energy brand is most likely to
      look "inconsistent" to a naive grader.

## CRITIQUE mode

- [ ] **A surface-checklist generator** — the corpus's outside-in requirement: from a validated card +
      a named surface (landing page, product UI, email, campaign, packaging, partner lockup), emit the
      surface-specific checklist of the rules that apply *there* (filtered by rule `context`/domain), so
      CRITIQUE can run against a focused subset rather than the whole spec.
- [ ] **Exploration-axis bounding** — make the seven controlled axes (functional↔expressive, etc.)
      machine-checkable against a card's documented ranges, so a proposed direction can be labeled
      *on-system* (within a documented range) or *off-system* (leaves the identity) deterministically.

## Reach

- [ ] **A `--corpus` projection helper** — read a full `brand_guideline_corpus.schema.json` brand
      record and project it down to a gradeable `*.brand.json` card (strategy + typed primitives),
      closing the DECOMPOSE loop from a real ingested corpus to the gate without hand-authoring.
- [ ] Promote draft → beta once the JSON-Schema card validation and the behavioral-eval pilot land, the
      adversarial-review hardening pass is folded in as selftest fixtures, and a second worked example
      ships.
