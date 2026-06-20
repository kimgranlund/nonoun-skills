# A · The inside-out axis — does the meaning reach the primitives?

Inside-out reasoning **starts from the brand's strategic core and propagates meaning outward** into
visual and verbal decisions. It asks: *what is the brand idea, what does it force, and how do the
primitives express it?* This is the **meaning** axis — judgment, where an LLM is strong — and it is
where the **operable-but-hollow** defect lives: a perfectly typed token system wrapped around a
generic idea whose meaning chain is decorative rather than forcing.

You walk it **whole → part**: idea first, then the chain, then each primitive, then range, then
governance. The first two levels are **gates** (a generic idea or a broken chain blocks the reviews
below — there is no point grading whether the color expresses an idea that does not exist). The reviews
are scored by the 100-point rubric in `references/the-rubric.md`.

## A1 · Brand idea `[gate]`

The central idea, promise, positioning, tension, mission, or creative platform — **specific enough
that a competitor could not copy-paste it.** Reject generic adjectives unless tied to behavior.

- **Gate failure — `GENERIC_IDEA`:** the idea is only interchangeable adjectives ("modern, bold,
  simple", "innovative and trusted", "clean and friendly"). This is the rubric's **#1 weak signal**,
  and it is mechanizable — `brand-spec-check.py` raises it as a hard fail. If the idea would fit any
  competitor unchanged, the whole inside-out axis is hollow; stop and fix the idea.
- **What good looks like:** a sharp idea + audience + tension + promise + proof + behaviors + strategic
  *exclusions* (what this brand refuses). DocuSign's "*agreements are dynamic moments of connection,
  not static documents — make the moment of agreement feel like forward progress*" forces voice (active
  progress, not "document management"), color (activation accent, not full-field), and imagery
  (product-true). That is an idea doing work.

## A2 · Meaning chain `[gate]`

The idea must **propagate**: `idea → voice → mark → color → type → layout → imagery → applications`.
Each link should be *forced* by the one above it, not merely listed next to it.

- **Gate failure:** the chain is missing or stops at one or two links — the idea names itself and then
  nothing downstream is derived from it. (`brand-spec-check.py` warns when the chain has < 4 links.)
- **The test:** for each primitive, ask *"why this, and not the opposite?"* and trace the answer up to
  the idea. If the answer is "it looked good" or "it's on trend," the link is decorative. A real chain
  lets you predict a primitive you have not seen yet from the idea alone.

## A3 · Primitives express the idea `[review]` — voice · mark · color · type

Each primitive is graded on **meaning, not just spec** — the corpus's "every primitive has a reason,"
"explains both meaning and mechanics." The rubric weights: **Voice 12 · Mark 12 · Color 10 · Type 10.**
Per-domain depth is in `references/the-six-domains.md`; in brief:

- **Voice (12)** — traits translated into *writing behavior*: vocabulary, headline patterns, UX copy,
  tone-by-context, banned phrases, do/don't examples, sample expressions. Weak signal: *voice is only
  adjectives.* "Confident" is not a voice; "lead with the outcome, name the action, cut the hedge" is.
- **Mark (12)** — origin, meaning, construction, lockups, clearspace, minimum sizes, backgrounds,
  misuse, motion, partner usage, accessibility. Weak signal: *the mark has rules but no origin or
  meaning.* A clearspace rule without a reason is a rulebook, not a system.
- **Color (10)** — meaning, **roles**, ratios, combinations, light/dark behavior, contrast, product/
  data/marketing usage, print/digital specs, misuse. Weak signal: *a palette without roles, ratios, or
  contrast.* A hex list is a `BARE_TOKEN` (the gate warns); a role + meaning makes it a system.
- **Type (10)** — rationale, hierarchy, scale, weights, fallback fonts, responsive behavior,
  accessibility, localization, numerals, UI use, expressive use. Weak signal: *names fonts but not
  hierarchy or use cases.*

## A4 · Range without losing identity `[review]` — expression · examples

The corpus's strong signal: *examples show range without losing identity; the system explains both
meaning and mechanics.* Rubric weights: **Expression 14 · Examples 12** (the two largest after the
idea).

- **Expression system (14)** — layout, grid, photography, illustration, iconography, motion, product
  UI, data visualization, environmental, social, campaign logic. The grammar that lets new work be
  generated, not copied.
- **Examples & applications (12)** — realistic executions across web, app, social, email, ads, decks,
  signage, merch, packaging, partner contexts, **and right/wrong comparisons.** Each example must say
  *what it teaches*, not just what it looks like (an evidence-linked record, not a screenshot).
- **The range test:** does the system identify its ranges — quiet/loud, functional/expressive,
  premium/playful, institutional/conversational — *where the deck shows them*? A brand with one
  expression is a template; a brand with named ranges and a stable identity across them is a system.

## A5 · Governance & usability `[review]`

Rubric weights: **Governance 8 · Usability 6.** The least glamorous, most operationally decisive.

- **Governance & assets (8)** — versioning, owners, approvals, asset library, naming, template
  locations, partner/co-branding rules, legal requirements, change process. Without owners and a change
  process, the spec rots the day it ships.
- **Document usability (6)** — clear navigation, modular structure, searchable specs, quick-start
  rules, examples *near* rules, and enough judgment guidance to avoid brittle policing. The corpus's
  non-goal: *do not turn brand design into a rigid style-policing checklist.* Usability is what lets a
  non-designer use the system; it is the bridge to the outside-in axis.

## Scoring the inside-out axis

A1 and A2 are gates — a `GENERIC_IDEA` or a broken chain caps the axis low regardless of how polished
the primitives are. A3–A5 are the 100-point rubric, normalized to the 1–5 review scale. The axis is
**≥4 with zero gate failures** to ship.

**The adversarial check (the dangerous quadrant).** Because "operable but hollow" hides behind a green
operability gate, send the idea + meaning chain to a **skeptic in a fresh context** and have it try to
*refute*: could a competitor copy-paste this idea unchanged? Does each meaning-chain link actually
force its primitive, or is it a label glued next to it? Is the voice a behavior or a list of adjectives?
Default to "hollow" when uncertain. Only an idea that survives refutation scores high on A.
