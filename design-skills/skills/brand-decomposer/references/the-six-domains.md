# The six domains — what "good" means in each, and how each fails

The card rolls the corpus's fine-grained `brand_domain` enum up to **six rubric-aligned domains**. The
B4 completeness gate requires each to be covered by at least one rule or token (`INCOMPLETE` warns on a
gap). This file is the per-domain depth — the inside-out "capture" requirement, the rubric's "what good
means," and the **failure mode** each domain hides. Load it when grading A3/A4 or when a domain is
flagged thin.

For each domain: the meaning question (axis A), the operability check (axis B), and the weak signal.

## mark *(corpus: logo)* — rubric 12

- **Meaning (A):** origin and symbolism — *why this mark, and what does it say about the idea?* The
  corpus weak signal: *the mark has rules but no origin or meaning.* A clearspace number without a
  reason is a rulebook entry, not a system.
- **Operability (B):** construction, lockups, **clearspace**, minimum sizes, backgrounds, misuse,
  motion behavior, partner usage, accessibility/trademark constraints — each a typed rule with a
  severity (`must` for clearspace and trademark; `should` for motion).
- **Failure mode:** rules without origin; no misuse examples; partner lockups with no governance rule.

## voice — rubric 12

- **Meaning (A):** traits translated into **writing behavior**, not adjectives. The corpus weak signal:
  *voice is only adjectives.* "Confident, human, clear" is not a voice. "Lead with the outcome, name
  the action, cut the hedge — write *agreement progress*, never *document management*" is.
- **Operability (B):** vocabulary, headline patterns, UX copy patterns, tone-by-context, **banned
  phrases**, do/don't examples, sample expressions — stored as rules + examples with evidence.
- **Failure mode:** adjectives with no behavior; no do/don't; no tone-by-context (the same voice for an
  error state and a launch headline).

## color — rubric 10

- **Meaning (A):** color **roles** and semantics — *what does each color mean and do?* The corpus weak
  signal: *a palette without roles, ratios, or contrast.* A hex list is a `BARE_TOKEN`; `color.ink =
  primary text` is a system.
- **Operability (B):** roles, ratios, combinations, light/dark behavior, **contrast** (the B3 gate —
  every `color_pair` ≥ AA), product/data/marketing usage, print/digital specs, misuse. This is the one
  domain with a hard arithmetic gate (`CONTRAST_FAIL`).
- **Failure mode:** a palette with no roles (`BARE_TOKEN`); an inaccessible brand pairing
  (`CONTRAST_FAIL`); the primary used as a full-field background when the system says activation accent.

## type *(corpus: typography)* — rubric 10

- **Meaning (A):** typeface **rationale** — *why this type, and what voice does it carry?* The corpus
  weak signal: *names fonts but not hierarchy or use cases.*
- **Operability (B):** hierarchy, scale, weights, **fallback fonts**, responsive behavior,
  accessibility (line length, tracking), localization, numerals, UI use, expressive use.
- **Failure mode:** a font name with no scale; no fallback (breaks the moment the webfont fails to
  load); no localization (breaks for non-Latin scripts — see `typography-lettering` for the craft).

## expression *(corpus: layout · photography · illustration · motion · product · marketing · social · packaging · environmental · co_branding · data_visualization)* — rubric 14

The largest rubric weight and the widest rollup — the **grammar** that lets new work be generated, not
copied. This is where the inside-out "expression grammar" and the outside-in "range of expression" meet.

- **Meaning (A):** layout/grid logic, photography/illustration direction, iconography, motion
  principles, product-UI logic, data-viz rules, environmental and campaign logic — each *derived from
  the idea.* Strong signal: *examples show range without losing identity.*
- **Operability (B):** every sub-area that the brand actually uses is covered by a rule or token; the
  surfaces it claims are real. A spec that ignores product, motion, data, accessibility, or partner
  contexts is `INCOMPLETE` for those.
- **Failure mode:** one expression treated as the whole system (a template, not a grammar); campaign
  loudness applied to a high-trust product moment; stock photography where the rule says product-true.

## governance — rubric 8

- **Meaning (A):** the change process — *who owns this, and how does it evolve?* Small weight, decisive
  for whether the spec survives contact with a real org.
- **Operability (B):** versioning, owners, approvals, asset library, naming, template locations,
  partner/co-branding rules, legal/trademark requirements, change process — as `must`-severity rules
  where they are hard constraints.
- **Failure mode:** no owner, no approval path, no versioning — the spec rots the day it ships; partner
  usage with no approval gate.

## Using this file in a grade

- **A3 (primitives express the idea):** read mark/voice/color/type against the *meaning* column — is
  each primitive's reason traced to the idea, or is it a spec with no "why"?
- **A4 (range without losing identity):** read expression + examples against the range test.
- **A5 / B4:** governance presence and the `INCOMPLETE` smell — a missing domain is a coverage hole the
  agent cannot answer "how here?" for.

A domain can be **operable but hollow** (typed, traced, contrast-clean — but the meaning column is
empty: rules with no reason) or **meaningful but inoperable** (a beautiful rationale with no typed
rule, no evidence, no contrast proof). Grade the two columns separately — that is the whole method,
applied one domain at a time.
