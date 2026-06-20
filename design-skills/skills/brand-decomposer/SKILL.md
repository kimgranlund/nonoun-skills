---
name: brand-decomposer
description: >
  Decompose, design, grade, or critique a brand-guidelines artifact — a brand book / design-system spec
  — on two crossing axes: INSIDE-OUT (idea → meaning chain → voice·mark·color·type·expression →
  governance) and OUTSIDE-IN (well-formed → traced → contrast → complete → retrievable), scored
  separately so a beautiful-but-unusable deck can't hide a hollow one. Doctrine: a brand book is a typed,
  evidence-linked OPERATING SYSTEM, not a logo rulebook — core object is evidence, three truths never
  collapsed. Operability routes to bin/brand-spec-check.py (schema, provenance, WCAG contrast,
  completeness); the operable-but-hollow quadrant is adversarially verified. CRITIQUE grounds
  work-critique in a VALIDATED spec — name the mechanism, never "feels off-brand". NOT for MAKING the
  brand or expert-taste judgment (brand-forge:
  brand-muse/brand-copywriter/brand-council/brand-evaluate); NOT layout (layout-decomposer),
  rendered contrast/CVD (color-verifier), color science (color-science), or type craft
  (typography-lettering).
---

# brand-decomposer — grade a brand spec on two crossing axes

A high-quality brand-guidelines document is a **brand operating system, not a logo rulebook** — it lets
a designer, writer, PM, agency, or partner make coherent *new* work without asking the brand team for
every decision. That reframe is what makes a brand — usually dismissed as "taste" — gradeable: you grade
the **spec**, not the beauty. Like every decomposer in this repo, a brand spec is **correct on two
independent axes that walk the same hierarchy** (`idea → voice·mark·color·type·expression → tokens/rules
→ surfaces`) **in opposite directions:**

- **Inside-out · whole → part** grades the **meaning**: brand idea → meaning chain
  (idea→voice→mark→color→type→expression→applications) → primitives expressing the idea → range without
  losing identity → governance. *"Is it the **right brand**, and does the idea reach the primitives?"*
  Judgment — where an LLM is strong.
- **Outside-in · part → whole** grades the **operability**: every record well-formed & typed → traced &
  trusted (evidence + confidence + three-truths) → accessible (contrast) → complete & surfaced →
  retrievable in context. *"Can an agent **retrieve, cite, trust, and apply** it at any surface,
  accessibly?"* Where an LLM fails silently — so it routes to a deterministic gate, `bin/brand-spec-check.py`.

They **cross at the typed primitive** — a token or rule is *both* an expression of the idea (the claim)
and a well-formed, evidence-linked, accessible record (the mechanism). The two defects are **opposite**:
a spec can be **right meaning, won't operate** (a sharp idea trapped in unsourced prose — the corpus's
"beautiful but unusable") or **operable but hollow** (a perfectly typed, contrast-clean token system
around a generic idea — "typed but hollow / voice is only adjectives"). Opposite fixes — so you **score
and report the two axes separately, never averaged**, and name the quadrant.

## Quick Start

**You bring:** a brand artifact (a deck, a brand book, a design-system page) and the question — "design
this", "is this brand book actually usable?", "grade this spec", "does this work align to the brand?".
**You get:** a brand-spec card (idea + meaning chain + typed primitives), an operability report from the
bin, and a two-axis grade with the defect quadrant named — or, in CRITIQUE, mechanism-named findings
grounded in a validated spec.

> *"Is this brand book ready to hand to an agency?"* →
> 1. **Inside-out — idea → chain:** the brand idea is sharp, not interchangeable adjectives `[gate:
>    GENERIC_IDEA]`; the meaning chain propagates idea→voice→mark→color→type→… `[gate]`. Then the
>    100-pt rubric over voice/mark/color/type (A3), expression/examples (A4), governance/usability (A5).
> 2. **Outside-in — operate it, don't read it:** `bin/brand-spec-check.py lint card.brand.json` runs
>    well-formed `[gate]` + traced/confidence/three-truths `[gate]` + WCAG contrast `[gate]` +
>    completeness. A green parse proves nothing the bin didn't check.
> 3. **Attack the dangerous quadrant:** a skeptic in a fresh context tries to *refute* the idea — could
>    a competitor copy-paste it? does the chain force the primitives or just list them?
> 4. **Report:** two axis scores + the quadrant cell, gate failures first, with review_flags for
>    anything needing human/legal verification.

**Modes:** **DECOMPOSE** (read an artifact → recover the chain → extract a card → run the gate → grade)
· **DESIGN** (inside-out down → declare the operability plan → emit a card) · **GRADE** (score both
axes, gates before reviews) · **CRITIQUE** (use a *validated* card to ground critique of design work —
mechanism-named, spec-cited, never "off-brand").

## The two axes (the method)

Load `references/decomposition-method.md` first for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Inside-out** | whole → part | **A1** Brand idea `[gate]` → **A2** Meaning chain `[gate]` → **A3** Primitives express it `[review]` → **A4** Range without losing identity `[review]` → **A5** Governance & usability `[review]` | "Is it the *right brand*?" |
| **B · Outside-in** | part → whole | **B1** Well-formed & typed `[gate]` → **B2** Traced & trusted `[gate]` → **B3** Accessible `[gate]` → **B4** Complete & surfaced `[review]` → **B5** Retrievable in context `[review]` | "Can an agent *operate* it?" |

`A1·A2` and `B1·B2·B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on that
axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A spec is **SHIPPABLE** at **≥4 on every review with
zero gate failures on either axis**, reported as two separate scores plus the quadrant cell. The B-axis
gates and the one mechanizable A-axis smell (A1's `GENERIC_IDEA`) route to **`bin/brand-spec-check.py`**;
the A-axis reviews are the 100-point rubric (`references/the-rubric.md`), judged + adversarially verified.

## The doctrine — the core object is evidence

The non-obvious core, straight from the source corpus, and the reason this earns a skill:

- **The core object is not "the brand." It is evidence.** A deck says/shows something → captured as raw
  text + metadata + a visual observation → *extracted* into typed claims, rules, tokens, examples → the
  agent reasons over those **while preserving provenance.** A summary blob is not a spec.
- **Three truths, never collapsed.** **Observed** (what the slide shows) · **Inferred** (what it likely
  means) · **Proposed** (what the agent recommends now). Fusing them is `COLLAPSED_TRUTH` — the reader
  can no longer tell a rule from a guess.
- **Confidence is an operational signal.** `0.90–1.00` explicit · `0.75–0.89` strong · `0.50–0.74`
  review-required · `<0.50` do-not-use. An inferred record below `0.75` not review-flagged is
  `LOW_CONFIDENCE`.
- **Operability is mechanizable — so a beautiful prose deck can't pass on looks.** Well-formedness,
  provenance, the three-truths separation, the WCAG contrast floor, and domain/surface completeness are
  arithmetic. Route them to `brand-spec-check.py`. A clean run is **necessary, not sufficient** — it
  means *operable*, not *good*.
- **The dangerous quadrant is "operable but hollow" — attack the idea, not the tokens.** The gate raises
  the one mechanizable smell (`GENERIC_IDEA`); the rest needs a skeptic in a fresh context refuting the
  idea and the chain.

## §SelfAudit

- **Operability is the gate the LLM fails silently.** Run `brand-spec-check.py`; do not certify "it's
  well-formed / traced / accessible / complete" from reading. An unrun gate is *no evidence*, not a pass.
- **A green gate is a pre-filter, not an oracle.** It checks the *common, mechanizable* shapes — it does
  not prove the evidence is *real* (a fabricated slide id passes a presence check) or the idea is good.
  Confirm provenance and meaning out of band.
- **The dangerous defect is invisible to the gate — refute the idea in a fresh context.** "Operable but
  hollow" needs a skeptic: could a competitor copy-paste this idea? does the chain force the primitives?
  is the voice a behavior or just adjectives? Default to "hollow" when uncertain.
- **Three truths, never collapsed; confidence is a trust band, not decoration.** An unsourced rule is an
  invention; a `0.60` inference shown as settled fact is a defect. Grade B2 with the bin, not by eye.
- **Gates before reviews, always.** Don't grade range for a generic idea, or retrievability for a spec
  that won't parse. Stop each axis at its first failed gate.
- **Two scores, never one.** *Right-meaning-won't-operate* and *operable-but-hollow* need opposite fixes
  (type/source/measure it vs re-derive the idea & chain). Report both axes and name the quadrant; never
  average.
- **CRITIQUE requires a validated spec, and names the mechanism.** Grounding critique in an unvalidated
  spec inherits its defects. Never say "off-brand" — cite the rule, the role, the contrast (see
  `references/critique-mode.md`).
- **Grade the spec; don't make the brand or judge its taste.** Making the brand is `brand-forge`
  (`brand-muse`/`brand-copywriter`); expert-taste judgment is `brand-forge`'s `brand-council`/
  `brand-evaluate`. Hand off; don't overlap.

## Verify Target

A brand spec is **done** when: the idea is sharp (A1, `GENERIC_IDEA` clean) and the meaning chain
propagates (A2); voice/mark/color/type carry a *reason*, expression shows range without losing identity,
governance/usability hold (A3–A5 ≥ 4 on the rubric); the bin's well-formed + traced + **contrast** gates
ran **green** (B1·B2·B3 — no `UNTRACED`/`LOW_CONFIDENCE`/`COLLAPSED_TRUTH`/`CONTRAST_FAIL`/`BARE_TOKEN`);
all six domains are covered and surfaces enumerated with failure modes (B4); rules know where they apply
and the spec answers the six agent-readiness questions (B5); the idea **survived a fresh-context
refutation** (operable-but-hollow ruled out); and both axes score ≥4 with zero gate failures, landing in
**SHIPPABLE** — with the brand-spec card + review_flags ready for an agency, an agent, or CRITIQUE.
**NOT done** when: the idea is generic or the chain decorative (*operable-but-hollow*); the idea is sharp
but trapped in unsourced, untyped prose with no contrast proof (*right-meaning-won't-operate*); a gate
was skipped (bin not run) and reported as a pass; or one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Inside-out × Outside-in), the leveled walk with gates, the quadrant, the brand-as-operating-system + evidence doctrine, and the four modes |
| `references/inside-out-axis.md` | **the meaning axis (A)** — idea → meaning chain → primitives express it → range → governance; the gates; the adversarial idea-refutation; where **operable-but-hollow** lives |
| `references/outside-in-axis.md` | **the operability axis (B)** — well-formed → traced → accessible → complete → retrievable; the agent-readiness questions; mechanized by `bin/brand-spec-check.py`; where **right-meaning-won't-operate** lives |
| `references/the-rubric.md` | **scoring axis A** — the 100-point rubric (9 areas), the area→A-level map, the 1–5 normalization, and the fast audit (weak/strong signals) |
| `references/evidence-and-confidence.md` | **the trust contract (B2)** — the evidence model, the four confidence bands, the three truths, and the QA the gate enforces vs. what you must still read |
| `references/brand-spec-schema.md` | **the `*.brand.json` card** — field-by-field, the enums (severity `must/should/may`, the three truths, the six domains + corpus normalization), and how the card projects from the full corpus schema |
| `references/the-six-domains.md` | **per-domain depth (A3/A4/B4)** — mark·voice·color·type·expression·governance: what good means, the operability check, and the failure mode each hides |
| `references/critique-mode.md` | **CRITIQUE mode** — using a validated spec to ground work-critique: the precondition gate, the agent behavior contract, never-say-"off-brand", the structured-critique shape, exploration axes, and the seam to brand-forge's judges |
| `references/policy.md` | **definition-of-done / handoff** — the 12-point DoD, the brand-spec card object, and the seams to `brand-forge` (muse/copywriter/council/evaluate), `layout-decomposer`, `color-verifier`, `color-science`, `typography-lettering` |
| `schema/brand-spec.schema.json` | **the formal card contract** (JSON Schema, Draft 2020-12) — structure, types, enums, required fields; drift-guarded against the bin's enums by the selftest. Print with `bin/brand-spec-check.py schema`; validate a card with `type-decomposer`'s `instance-check.py` |
| `bin/brand-spec-check.py` | **mechanizes the B axis** — `lint <card.brand.json>` (well-formed · UNTRACED · LOW_CONFIDENCE · COLLAPSED_TRUTH · CONTRAST_FAIL · BARE_TOKEN · GENERIC_IDEA · INCOMPLETE · THIN_EVIDENCE · DANGLING_REF · WEAK_MANDATE · TRUTH_CONFIDENCE_MISMATCH) · `contrast <fg> <bg> [large\|ui]` · `schema` (print the formal schema) · `selftest` · `--json` |
