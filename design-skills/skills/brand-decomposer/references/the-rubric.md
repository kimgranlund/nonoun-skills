# The 100-point rubric — scoring the outside-in axis

A high-quality brand-guidelines document is a **brand operating system, not a logo rulebook.** It
should let a designer, writer, PM, agency, or partner make coherent new work without asking the brand
team for every decision. This 100-point rubric scores the **A · outside-in (meaning)** axis. (The
**B · inside-out (operability)** axis is gated mechanically by `brand-spec-check.py` — see
`references/inside-out-axis.md`; the two are scored **separately, never averaged.**)

Map the nine areas onto the A-axis levels: **A1** = Brand idea · **A3** = Voice/Mark/Color/Type ·
**A4** = Expression/Examples · **A5** = Governance/Usability. (A2, the meaning chain, is the *connective
tissue* the rubric assumes — it is graded as the gate that the idea actually propagates into these
areas.)

## The 100 points

| Area | Pts | A-level | What good means |
|---|---:|---|---|
| **Brand idea & strategy** | 16 | A1 | A sharp idea, audience, tension, promise, proof, behaviors, and strategic *exclusions*. Specific enough that a competitor could not copy-paste it. |
| **Voice & verbal expression** | 12 | A3 | Voice traits translated into writing *behavior*: vocabulary, headline patterns, UX copy, tone by context, do/don't examples, sample expressions. |
| **Brand mark** | 12 | A3 | Origin, meaning, construction, lockups, clearspace, minimum sizes, backgrounds, misuse, motion, partner usage, accessibility constraints. |
| **Color system** | 10 | A3 | Color *meaning*, roles, ratios, combinations, light/dark behavior, contrast rules, product/data/marketing usage, print/digital specs, misuse. |
| **Typography** | 10 | A3 | Type rationale, hierarchy, scale, weights, fallback fonts, responsive behavior, accessibility, localization, numerals, UI use, expressive use. |
| **Expression system** | 14 | A4 | Layout, grid, photography, illustration, iconography, motion, product UI, data visualization, environmental, social, campaign logic. |
| **Examples & applications** | 12 | A4 | Realistic executions across web, app, social, email, ads, decks, signage, merch, packaging, partner contexts, and right/wrong comparisons. |
| **Governance & assets** | 8 | A5 | Versioning, owners, approvals, asset library, naming, template locations, partner/co-branding rules, legal requirements, change process. |
| **Document usability** | 6 | A5 | Clear navigation, modular structure, searchable specs, quick-start rules, examples near rules, judgment guidance over brittle policing. |

**Note the weighting.** Idea (16) and Expression (14) dominate — a brand is its central idea and the
grammar that expresses it, not its logo rules. Mark, Voice, Examples cluster at 12. Governance and
Usability are small but **gate operability**: a brilliant system no one can navigate or maintain fails
the inside-out axis regardless of its rubric score.

## Normalizing to the 1–5 review scale

The decomposer reports each axis on a 1–5 review scale. Convert the rubric total: **90–100 → 5 ·
75–89 → 4 · 60–74 → 3 · 40–59 → 2 · <40 → 1.** A spec ships at **≥4 on the A axis with zero gate
failures** (A1 `GENERIC_IDEA`, A2 broken chain). Report the rubric total *and* the normalized score so
the area-level diagnosis survives.

## Fast audit — the weak/strong signals

Use these before the full rubric to locate the quadrant quickly.

**Weak signals (operable-but-hollow or unusable):**

- Brand idea is interchangeable with competitors. *(→ A1 `GENERIC_IDEA`, gate fail)*
- Voice is only adjectives.
- Color is a palette without roles, ratios, or contrast. *(→ B1 `BARE_TOKEN`)*
- Typography names fonts but not hierarchy or use cases.
- Mark has rules but no origin or meaning.
- No realistic examples.
- Product, motion, data, accessibility, and partner contexts are ignored. *(→ B4 `INCOMPLETE`)*
- The guide is beautiful but unusable by non-designers. *(the right-meaning-won't-operate quadrant)*

**Strong signals:**

- Every primitive has a reason.
- The system explains both meaning and mechanics.
- Examples show range without losing identity.
- Rules are specific without being brittle.
- The document helps teams make new decisions rather than copy old assets.

The fast audit is a triage, not the grade. A spec can pass the fast audit and still fail B on
provenance or contrast — always run `brand-spec-check.py` for the inside-out gates, and always run the
adversarial idea-refutation (`references/outside-in-axis.md`) for the hollow-idea quadrant.
