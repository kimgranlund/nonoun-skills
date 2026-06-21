# Roadmap — brand-decomposer

Ships its core in 0.1.0 (the two axes, the operability gate, the 100-point rubric, the trust contract,
the `*.brand.json` card, the six-domain depth, and CRITIQUE mode). Everything below is additive.

## `bin/brand-spec-check.py`

- [~] **JSON-Schema validation of the card (partially done).**
      - [x] **The formal schema ships** — `schema/brand-spec.schema.json` (Draft 2020-12, with `$defs`
        for evidence_ref/token/rule/example/color_pair) is the declarative B1 contract, printable via
        `bin/brand-spec-check.py schema` and documented by `references/brand-spec-schema.md`.
      - [x] **Drift guard** — the selftest's `_schema_coherence()` asserts the schema's enums
        (`severity`, `truth`, token `type`, `domain`) match the bin's constants and that the GREEN
        fixture meets the schema's required-field contract, so the artifact and the gate can't silently
        diverge (proven by a corrupt-the-enum negative test).
      - [ ] **Full per-card validation** is intentionally **delegated** to `type-decomposer`'s
        `instance-check.py` (the skill that owns "does an instance validate against a schema") rather
        than reimplemented here — a generic validator would also degrade the gate's domain-meaningful
        findings (`COLLAPSED_TRUTH`, `BARE_TOKEN`) into generic `SCHEMA_INVALID`. If a self-contained
        structural pre-gate is later wanted, vendor a *minimal* validator (type/required/enum/$ref only)
        and lock the bool-is-not-number / string-is-not-int traps as fixtures.
- [x] **Evidence-reference integrity** (done) — `THIN_EVIDENCE` flags an `evidence[]` entry present but
      with no `deck_id`/`slide_id`/`source_url` (it points nowhere — a structural strengthening of the
      presence-only check; it still can't prove the id is *real*), and `DANGLING_REF` flags an example's
      `rules_demonstrated[]` naming a rule `id` not in the card (a silent B5 retrieval break). Both
      advisory; locked with must-flag fixtures.
- [x] **Confidence/severity & truth coherence smells** (done) — `WEAK_MANDATE` flags a `must` (hard)
      rule at `confidence < 0.90` (mandating what the deck didn't explicitly state), and
      `TRUTH_CONFIDENCE_MISMATCH` flags an `observed` record at `confidence < 0.90` (a direct
      observation you're unsure of is really an inference). Both advisory band-coherence checks; locked
      with must-flag **and** must-NOT-flag fixtures (a `should` rule / an `inferred` record at the same
      confidence must stay quiet). *(The originally-sketched token role↔type mismatch was dropped — role
      is free-text, so it has no low-false-positive deterministic form; the truth↔band check is the
      cleaner, corpus-grounded coherence smell.)*
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

- [ ] **A surface-checklist generator** — the corpus's inside-out requirement: from a validated card +
      a named surface (landing page, product UI, email, campaign, packaging, partner lockup), emit the
      surface-specific checklist of the rules that apply *there* (filtered by rule `context`/domain), so
      CRITIQUE can run against a focused subset rather than the whole spec.
- [ ] **Exploration-axis bounding** — make the seven controlled axes (functional↔expressive, etc.)
      machine-checkable against a card's documented ranges, so a proposed direction can be labeled
      *on-system* (within a documented range) or *off-system* (leaves the identity) deterministically.

## Reach

- [x] **A `project` (corpus → card) helper** (done) — `brand-spec-check.py project <record.json>` reads
      a corpus brand record in the dossier shape (`examples/docusign_seed_example.json`: brand / deck /
      strategy{brand_idea, creative_platform} / visual_identity{mark_system, color_system}) and projects
      it into a gradeable card, deriving `truth` from the confidence band so the projection is
      band-coherent by construction. Closes the DECOMPOSE loop from a real ingested corpus to the gate
      (`project … | lint …`), verified end-to-end against the real DocuSign seed (it grades clean on the
      operability gates and honestly flags the voice/type/governance/surface coverage the *seed* lacks).
      Locked with the embedded `_CORPUS_SEED` fixture. *(Next: as full corpus `brand_system` records
      with `verbal_identity`/`expression_system`/`governance` and hex `value`s appear, extend the
      mapping to those branches — the schema leaves them open, so the shape is example-driven.)*
- [ ] Promote draft → beta once the JSON-Schema card validation and the behavioral-eval pilot land, the
      adversarial-review hardening pass is folded in as selftest fixtures, and a second worked example
      ships.
