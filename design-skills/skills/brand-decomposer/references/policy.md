# Definition-of-done, the brand-spec card, and the seams

This file is the **handoff contract** — when a brand spec is *done*, the card object the skill produces,
and the boundaries to the `brand-forge` makers/judges and the design-skills verifiers. Load it in GRADE
to close out, or when deciding "is this someone else's skill?".

## The 12-point definition-of-done

A brand spec is **SHIPPABLE** when all twelve hold (gate failures are zeros, not deductions):

**Outside-in (meaning) — axis A:**

1. **Brand idea is sharp** — not interchangeable adjectives; would not copy-paste to a competitor
   (A1 gate; `GENERIC_IDEA` clean).
2. **Meaning chain propagates** — `idea→voice→mark→color→type→expression→applications`, each link
   forced by the one above (A2 gate; ≥ 4 links).
3. **Primitives express the idea** — voice/mark/color/type each carry a *reason*, not just a spec
   (A3 ≥ 4; rubric Voice/Mark/Color/Type).
4. **Range without losing identity** — expression grammar + realistic examples across surfaces, with
   right/wrong comparisons (A4 ≥ 4; rubric Expression/Examples).
5. **Governance & usability** — owners, approvals, change process; navigable, examples near rules
   (A5 ≥ 4; rubric Governance/Usability).

**Inside-out (operability) — axis B (gated by `brand-spec-check.py`):**

6. **Well-formed & typed** — typed records, severities/types/confidences in range, no `BARE_TOKEN`
   (B1 gate).
7. **Traced & trusted** — `evidence[]` + `confidence` on every record, inferred-below-`0.75`
   review-flagged, three truths never collapsed (B2 gate; `UNTRACED`/`LOW_CONFIDENCE`/`COLLAPSED_TRUTH`
   clean).
8. **Accessible** — every `color_pair` clears the WCAG AA floor (B3 gate; `CONTRAST_FAIL` clean).
9. **Complete & surfaced** — all six domains covered, surfaces enumerated, failure modes captured
   (B4 ≥ 4; `INCOMPLETE` clean).
10. **Retrievable in context** — rules know where they apply; the spec answers all six agent-readiness
    questions (B5 ≥ 4).

**Both axes:**

11. **Two scores, never one** — axis A and axis B reported separately with the quadrant cell named;
    never averaged.
12. **Adversarially verified on the dangerous quadrant** — the idea + meaning chain survived a
    fresh-context refutation (operable-but-hollow ruled out).

**NOT done** when: the idea is generic or the chain is decorative (*operable-but-hollow*); or the idea
is sharp but trapped in unsourced, untyped prose with no contrast proof (*right-meaning-won't-operate*);
or a gate was skipped (bin not run) and reported as a pass; or one blended score is reported.

## The brand-spec card (the deliverable)

GRADE and DESIGN emit a card object:

```json
{
  "brand": "DocuSign",
  "axis_A_inside_out": { "score": 4, "rubric_total": 86, "gate_failures": [] },
  "axis_B_outside_in": { "score": 5, "gate_failures": [], "bin_report": "brand-spec-check --json …" },
  "quadrant": "SHIPPABLE",
  "spec_card": "docusign.brand.json",
  "review_flags": ["color.x exact hex unverified", "partner trademark needs legal review"],
  "adversarial_idea_check": "survived — idea is non-generic, chain forces primitives"
}
```

The `spec_card` is the validated `*.brand.json` (`references/brand-spec-schema.md`). It is the input to
CRITIQUE and the artifact other skills consume.

## The seams — what is *not* this skill

brand-decomposer **grades the spec** (operability × meaning) and **grounds work-critique in a validated
spec**. It does not make the brand, and it does not pass expert-taste judgment. Hand off cleanly:

| When the job is… | It belongs to | Not here because |
|---|---|---|
| **make** the brand idea / aspiration | `brand-forge` · `brand-muse` | the Muse sets the ideal to pull toward; the decomposer grades the artifact that results |
| **make** voice, naming, copy | `brand-forge` · `brand-copywriter` | the decomposer grades whether voice is documented as behavior, not whether *this* copy is good |
| **judge** brand work by expert taste | `brand-forge` · `brand-council` / `brand-evaluate` | the named-critic panel asks "is this good / differentiated / is the Big Idea there"; the decomposer asks "is the spec operable, and does work align to *its* documented rules" |
| **grade** the page/screen **layout** | `layout-decomposer` | layout is its own INSIDE-OUT × OUTSIDE-IN decomposer; brand-decomposer grades the brand system, not the composition |
| **measure** rendered contrast / CVD | `color-verifier` | the spec's contrast floor is a *constraint*; the rendered work must still be measured |
| the **science** of a color choice | `color-science` | brand-decomposer uses the WCAG math; it does not teach perceptual color |
| **type craft** (anatomy, scripts, CSS) | `typography-lettering` | brand-decomposer grades that type is documented with hierarchy/fallback; it does not teach the craft |

The clean test: if the question is **"is this brand book a usable operating system, and does this work
align to it?"** it is this skill. If it is **"make me a brand"** or **"is this brand work brilliant?"**
it is `brand-forge`. If it is **"is this specific surface right?"** it is a verifier or
`layout-decomposer`.

## CRITIQUE handoff

CRITIQUE consumes a validated `spec_card` and emits structured findings
(`references/critique-mode.md`): `{alignment, tension, missing_opportunity, severity, evidence,
recommended_move}[]` plus `review_flags[]`. Accessibility findings that need *measurement of the
rendered work* hand off to `color-verifier`; "is the brand idea itself ambitious enough" hands off to
`brand-forge`'s council.
