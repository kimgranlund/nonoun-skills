# CRITIQUE mode — grounding work-critique in a validated brand spec

The other three modes grade the **spec**. CRITIQUE turns a *validated* spec around and points it at a
piece of design **work** — a homepage, a campaign frame, a product screen, a headline — to say where
the work aligns with the brand system, where it creates tension, and what controlled moves are
available next. This is the corpus's `AGENTIC_BRAND_DESIGN_REQUIREMENTS` use case: *work with designers
as an intelligent brand-context layer.*

The whole value of CRITIQUE is that it is **grounded** — every observation cites a rule, a token, an
example, or a contrast measurement in the spec. An ungrounded "this feels off-brand" is exactly what
this mode exists to replace.

## The precondition — a spec that passes the gate `[gate]`

**CRITIQUE requires a brand-spec card that passes `brand-spec-check.py`.** A critique grounded in an
unvalidated spec inherits every defect of that spec: it will cite an `UNTRACED` rule as if it were
documented, treat a `LOW_CONFIDENCE` inference as settled, or miss the `CONTRAST_FAIL` the work
inherited from the brand. If the spec is not validated, you are not doing CRITIQUE — you are improvising
taste. Run the gate first; if it fails, fix the spec (or say plainly that the critique is ungrounded).

## The agent behavior contract

Always separate these five — never blur them into a verdict:

1. **What the work is doing now** *(observed — read the actual piece)*
2. **What the brand system says** *(cite the rule / token / example / contrast floor)*
3. **Where the work aligns** *(name the mechanism it satisfies)*
4. **Where the work creates tension** *(name the mechanism it violates, with severity)*
5. **What design moves are available next** *(proposed — controlled, not "be bolder")*

This is the three-truths discipline applied to critique: **observed** (the work) vs **the spec** (the
documented system) vs **proposed** (your recommended move). Never present a proposal as if the spec
mandated it; never present your reading of the work as if it were the spec's rule.

## Never say "off-brand" — name the mechanism

The corpus's hard rule: *the agent should not simply say "on brand" or "off brand." It should name the
mechanism* — voice behavior, color role, contrast, mark usage, image logic, typographic hierarchy,
surface context, or expression range.

**Avoid** (ungrounded, unactionable):

- "Make it more modern."
- "This feels off-brand."
- "Use brand colors."
- "Be bolder."

**Prefer** (mechanism-named, spec-cited, with a move):

- "This uses the primary color as a full-field background, but `color.activation` (should) shows it as
  an *activation layer* for campaign emphasis. Reduce it to a highlight and let the neutral system
  carry the base." *(color role)*
- "The headline is category-generic. The brand's voice rule `voice.active` prefers active, concrete
  outcome language over abstract benefit language. Rewrite from static description into a direct
  action/result pattern." *(voice behavior)*
- "Given this is a high-trust product-UI moment, reduce campaign expressiveness, prioritize clarity,
  keep accessible contrast (`color.ink` on `color.surface` clears AA), and use the product-imagery
  rule rather than campaign photography." *(surface context + contrast)*

## The structured critique (the output shape)

Each finding carries six fields — the corpus's required critique structure:

| Field | What it holds |
|---|---|
| **alignment** | where the work *satisfies* the system — cite the rule/token it follows |
| **tension** | where it *conflicts* — cite the rule it breaks, name the mechanism |
| **missing opportunity** | a move the system enables that the work didn't take |
| **severity** | from the cited rule's severity — `must` (hard) > `should` > `may` (flexible) |
| **evidence** | the spec record(s) cited *and* the part of the work observed |
| **recommended move** | a controlled, specific next step — `proposed`, not a mandate |

## Exploration axes — controlled variation, not "different"

When the ask is "give me other directions," generate along the corpus's **controlled axes** rather than
random variety. Each axis is a dial the spec's range section should bound:

`functional ↔ expressive · product-led ↔ human-led · quiet ↔ high-energy · literal ↔ metaphorical ·
premium restraint ↔ campaign loudness · institutional ↔ conversational · systematic ↔ organic`

A direction is *on-system* when it moves along an axis the spec documents a range for, and *off-system*
when it leaves the identity. The exploration is bounded by the spec, not by taste.

## What CRITIQUE flags for human review

The corpus's review-and-verification requirement — surface, don't silently decide:

- Exact specs needing verification (a measurement the spec marks uncertain).
- Legal / trademark rules needing official review.
- Low-confidence inferences (a spec record below `0.75`).
- Asset-rights uncertainty.
- Accessibility checks that require *measurement* of the actual rendered work (the spec's contrast
  floor is a constraint; the rendered work must still be measured — hand off to `color-verifier`).

## The seam to brand-forge's judges

CRITIQUE is **alignment-to-this-brand's-documented-system**, citing the spec. It is *not* expert taste
judgment of whether the brand work is *good* — that is `brand-forge`'s `brand-council` /
`brand-evaluate` (the named-critic panel: "what would Paula S. say", is the Big Idea there, is it
differentiated). Different question, different grounding: CRITIQUE answers *"does this align with the
rule the brand documented, and which rule?"*; the council answers *"is this good by expert taste?"*.
Use CRITIQUE to check fidelity to a system; use the council to pressure-test the system's ambition.
