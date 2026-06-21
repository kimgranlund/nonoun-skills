# The brand-decomposer method — two crossing axes over a brand-guidelines spec

A high-quality brand-guidelines document is a **brand operating system, not a logo rulebook**: it lets
a designer, writer, PM, agency, or partner make coherent *new* work without asking the brand team for
every decision. That single reframe is what makes a brand — usually dismissed as "taste" — gradeable.
You are not grading whether the brand is *beautiful*; you are grading whether the **spec** is a usable,
trustworthy, operable system, and whether its meaning actually reaches the primitives.

Like every decomposer in this repo, a brand spec is **correct on two independent axes that walk the
same hierarchy in opposite directions** — the brand hierarchy being `idea → voice · mark · color ·
type · expression → tokens/rules → surfaces/applications`.

- **A · INSIDE-OUT · whole → part** grades the **meaning**: the brand idea → the meaning chain
  (idea→voice→mark→color→type→expression→applications) → the primitives expressing the idea → range
  without losing identity → governance & usability. *"Is it the **right brand**, and does the idea
  reach the primitives?"* This is judgment — where an LLM is strong.
- **B · OUTSIDE-IN · part → whole** grades the **operability**: every record well-formed & typed →
  traced & trusted (evidence + confidence + three-truths) → accessible (contrast) → complete & surfaced
  → retrievable in context. *"Can an agent **retrieve, cite, trust, and apply** it at any surface,
  accessibly?"* This is where an LLM fails silently (a vague prose deck *feels* complete), so it is
  **routed to a deterministic, self-tested gate** — `bin/brand-spec-check.py`.

The names are the corpus's own: **inside-out** reasoning starts from the brand's strategic core and
propagates meaning outward; **outside-in** reasoning starts from the surface the audience encounters
and asks whether the system can show up there. They are the same hierarchy, opposite directions.

## The crossing — and the quadrant

The two axes **cross at the typed primitive** — a token or rule is *both* an expression of the brand
idea (the claim, axis A) and a well-formed, evidence-linked, accessible record (the mechanism, axis B).
That crossing is the whole technique, because the two defects are **opposite**:

- **Right meaning, won't operate** (high A, low B): a sharp brand idea, a coherent story — but the spec
  is prose. Untyped, unsourced, no surface coverage, no contrast proof. *An agent cannot retrieve,
  cite, or trust it.* This is the corpus's **"beautiful but unusable by non-designers."**
- **Operable but hollow** (high B, low A): a perfectly typed, fully sourced, contrast-clean token
  system — wrapped around a **generic, interchangeable brand idea** ("modern, bold, simple") whose
  meaning chain is decorative, not forcing. This is the corpus's **"typed but hollow / voice is only
  adjectives / a palette without roles."**

Opposite defects need opposite fixes (sharpen the idea & re-derive the meaning chain vs. type, source,
and measure the primitives). So you **score and report the two axes separately, never averaged**, and
name the quadrant cell.

|  | **B low — won't operate** | **B high — operable** |
|---|---|---|
| **A high — right meaning** | *beautiful but unusable* — type it, source it, measure it | **SHIPPABLE** |
| **A low — hollow meaning** | broken both ways — start over from the idea | *operable but hollow* — re-derive the idea & chain |

## The leveled walk (gates cascade, then reviews)

Each axis is a ladder. The first levels are **`[gate]`s**: a gate failure **cascades and BLOCKS** the
reviews below it on that axis — you do not grade range for a spec whose idea is generic, or
retrievability for one that won't parse. Later levels are **`[review]`s**, scored 1–5.

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Inside-out** | whole → part | **A1** Brand idea `[gate]` → **A2** Meaning chain `[gate]` → **A3** Primitives express it `[review]` → **A4** Range without losing identity `[review]` → **A5** Governance & usability `[review]` | "Is it the *right brand*?" |
| **B · Outside-in** | part → whole | **B1** Well-formed & typed `[gate]` → **B2** Traced & trusted `[gate]` → **B3** Accessible `[gate]` → **B4** Complete & surfaced `[review]` → **B5** Retrievable in context `[review]` | "Can an agent *operate* it?" |

A spec is **SHIPPABLE** when every review is **≥4 with zero gate failures on either axis**, reported as
two separate axis scores plus the quadrant cell. The B-axis gates (B1·B2·B3) and the one mechanizable
A-axis smell (A1's GENERIC_IDEA) route to **`bin/brand-spec-check.py`**; the A-axis reviews are the
100-point rubric (`references/the-rubric.md`), judged and adversarially verified.

- The **A axis** is detailed in `references/inside-out-axis.md`, scored by `references/the-rubric.md`.
- The **B axis** is detailed in `references/outside-in-axis.md`, mechanized by the bin, with the trust
  contract in `references/evidence-and-confidence.md`.

## The doctrine — the core object is evidence, not the brand

The non-obvious core, straight from the corpus, and the reason this earns a skill:

- **The core object is not "the brand." It is evidence.** A deck page says or shows something → it is
  captured as raw text + slide metadata + a visual observation → it is *extracted* into typed claims,
  rules, tokens, examples → the agent reasons over those typed records **while preserving provenance.**
  A summary blob is not a spec. *Typed, evidence-linked, or it does not count.*
- **Three truths, never collapsed.** **Observed** (what the slide visibly says/shows) · **Inferred**
  (what it likely means from repeated evidence) · **Proposed** (what the agent recommends for the
  current work). Fusing these into one field is a defect (`COLLAPSED_TRUTH`) — the reader can no longer
  tell a documented rule from a guess. See `references/evidence-and-confidence.md`.
- **Confidence is an operational signal, not decoration.** `0.90–1.00` explicit · `0.75–0.89` strong ·
  `0.50–0.74` review-required · `<0.50` do-not-use. An inferred record below `0.75` that is **not**
  review-flagged is a trust defect (`LOW_CONFIDENCE`).
- **Operability is mechanizable — so a beautiful prose deck cannot pass on looks.** Well-formedness,
  provenance, the three-truths separation, the WCAG contrast floor, and domain/surface completeness are
  arithmetic, not taste. Route them to `brand-spec-check.py`. A clean run is **necessary, not
  sufficient** — it means *well-formed, traced, accessible, complete enough to operate*; it does **not**
  mean the idea is good or the meaning chain is right (that is axis A, judged + adversarially verified).
- **The dangerous quadrant is "operable but hollow" — attack the idea, not the tokens.** A green gate
  hides a generic brand wrapped in perfect structure. The gate raises the one mechanizable smell
  (`GENERIC_IDEA` — the idea is only interchangeable adjectives), but the rest needs a **skeptic in a
  fresh context**: *could a competitor copy-paste this idea? does the meaning chain actually force the
  primitives, or merely list them? is the voice a behavior or just adjectives?*

## The four modes

- **DECOMPOSE** — read an existing brand-guidelines artifact (a deck, a PDF, a Notion page) → recover
  the meaning chain and extract typed primitives into a brand-spec card → run `brand-spec-check.py` →
  grade both axes. *"Is this brand book actually operable?"* When the source is already an *ingested
  corpus record* (the dossier shape), `brand-spec-check.py project <record.json>` does the extraction
  mechanically — mapping the idea/mark/colors/platform into typed records and deriving `truth` from the
  confidence band — so you can pipe `project … | lint …` and read the grade (see `examples/walkthrough.md` §5).
- **DESIGN** — inside-out down: lock the brand idea (A1) → propagate the meaning chain (A2) → declare
  the operability plan (which domains, surfaces, tokens, evidence) → emit a brand-spec card. *"Help me
  structure this brand into an operating system."*
- **GRADE** — score both axes, gates before reviews, report two scores + the quadrant cell, never
  averaged. *"Grade this brand spec."*
- **CRITIQUE** — use a **validated** brand-spec card to ground critique of a piece of design *work* —
  alignment / tensions / missing opportunities / severity / evidence / recommended moves, always
  **naming the mechanism** (voice behavior, color role, contrast, mark usage, type hierarchy, surface
  context, expression range), never "feels off-brand." Requires a spec that *passes the gate* — an
  ungrounded critique is exactly what this mode exists to prevent. See `references/critique-mode.md`.

Read `references/inside-out-axis.md` and `references/outside-in-axis.md` next for the two axes in full,
`references/brand-spec-schema.md` for the card the gate consumes, and `references/policy.md` for the
definition-of-done and the seams to the `brand-forge` makers and judges.
