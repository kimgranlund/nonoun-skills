# B · The outside-in axis — can an agent operate the spec?

Outside-in reasoning **starts from the surface the audience encounters** and asks whether the brand
system can actually show up there: *what is this piece trying to do, where does it live, who is it for,
and can the agent retrieve, cite, trust, and apply the right rules — accessibly?* This is the
**operability** axis. It is exactly where an LLM fails silently — a vague prose deck *feels* complete —
so its gates are **routed to a deterministic, self-tested tool, `bin/brand-spec-check.py`**, and a
clean run is **necessary, not sufficient.**

You walk it **part → whole**: each record must be well-formed, then trusted, then accessible, before
the spec as a whole can be called complete and retrievable. The first three levels are **gates**
(mechanized); the last two are reviews. This axis is where the **right-meaning-won't-operate** defect
lives — a sharp idea trapped in unsourced, untyped prose.

## B1 · Well-formed & typed `[gate]` — mechanized

The data is structured as **claims, rules, tokens, examples** — not one summary blob. Every record has
its required fields; severities, token types, and confidences are in range.

- **Mechanized by `brand-spec-check.py lint`:** `WELL_FORMED` (required fields present), severity ∈
  {`must`, `should`, `may`} (the corpus's RFC-2119 enum — must = hard rule, may = flexible range),
  token type ∈ {`color`, `type`, `space`, `radius`, `motion`, `elevation`}, confidence ∈ `[0,1]` (and
  not a bool masquerading as a number). `BARE_TOKEN` warns when a token has a value but no role +
  meaning — a palette, not a color *system*. Corpus fine-grained domains (`logo`, `typography`,
  `layout`…) normalize to the six rubric domains, so a faithful corpus card does not trip warnings.
- **Gate failure:** a missing required field, an out-of-range severity (`"loud"`), a confidence of
  `true`. The spec cannot be reasoned over until its records are typed.

## B2 · Traced & trusted `[gate]` — mechanized

Every non-obvious claim has **source evidence** and a **confidence**, and the **three truths are never
collapsed.** This is the trust contract; full detail in `references/evidence-and-confidence.md`.

- **`UNTRACED`** — a rule / token / example with no `evidence[]`. *Every non-obvious claim needs a
  source* — a deck id, slide id, source URL, extraction method. An unsourced rule is indistinguishable
  from an invention.
- **`LOW_CONFIDENCE`** — an `inferred` record below `0.75` that is not `review`-flagged. The confidence
  band `0.50–0.74` means "plausible inference requiring review"; below `0.50` means "do not use." An
  inferred rule presented as settled fact is a trust defect.
- **`COLLAPSED_TRUTH`** — a record whose `truth` is not one of `observed` / `inferred` / `proposed`.
  Fusing what the slide *shows* with what the system *infers* with what the agent *proposes* destroys
  the reader's ability to tell a rule from a guess.

## B3 · Accessible `[gate]` — mechanized

The one accessibility joint a deck **almost never proves by hand**: every declared color role-pair
clears the WCAG AA contrast floor.

- **Mechanized by `brand-spec-check.py` (`CONTRAST_FAIL`)** over `color_pairs[]`, using the same
  sRGB→relative-luminance→`(L1+0.05)/(L2+0.05)` math as `color-verifier`'s `contrast-check`. Floor:
  **4.5:1** normal text, **3.0:1** large text or UI components. `contrast <fg> <bg> [large|ui]` checks
  a pair directly.
- **Gate failure:** a brand grey on white at 2.64:1. The color system "looks" on-brand and is
  inaccessible — a defect no amount of meaning-axis polish detects.

## B4 · Complete & surfaced `[review]` — mechanized smell + judgment

Can the spec answer **"how here?"** for every domain and every surface it claims?

- **Mechanized smell (`INCOMPLETE`):** every rubric domain — **mark · voice · color · type · expression
  · governance** — is covered by at least one rule or token, and `surfaces[]` is non-empty. The bin
  warns on a domain with no rule/token, or a spec with no surfaces. (Tokens map to domains: `color`→
  color, `type`→type, `space`/`radius`/`motion`/`elevation`→expression.)
- **Judgment on top:** are the surfaces the ones the brand actually lives on (homepage, product UI,
  campaign, social, packaging, signage, deck, email, OOH, partner lockup)? Are **failure modes**
  captured (do/don't, misuse, contrast failures, logo-placement errors, off-voice copy)? A spec that
  only documents the happy path cannot critique real work.

## B5 · Retrievable in context `[review]` — judgment

The deepest operability question, from the corpus's **agent-readiness QA**: can the agent **retrieve
the right subset** for a given designer intent and surface, and does every rule **know where it applies
and where it should not**?

The spec passes B5 when it can answer all six agent-readiness questions:

1. What does this brand believe? *(idea)*
2. How does the mark express the idea? *(meaning chain)*
3. How should this brand write? *(voice behavior)*
4. Which color/type/layout rules are hard constraints? *(severity)*
5. What does a good example look like on this surface? *(evidence-linked examples)*
6. What would be off-brand, and why? *(failure modes + the mechanism named)*

A rule without a **context** (where it applies / where it does not) cannot be retrieved correctly — it
will fire on the wrong surface. *Rules know where they apply* is the corpus's "Contextual" quality bar.

## Scoring the outside-in axis — and the discipline

Run `brand-spec-check.py lint <card.brand.json>` first. B1·B2·B3 gate failures **cascade and block**
B4·B5; a green gate means the spec is well-formed, traced, accessible, and complete *enough to
operate*. The axis is **≥4 with zero gate failures** to ship.

- **A clean run is a pre-filter, not an oracle.** It proves the *common, mechanizable* shapes are
  clean; it does not prove the evidence is *real* (a fabricated slide id passes a presence check) or
  that the brand idea is good. Confirm provenance and meaning out of band.
- **An unrun gate is no evidence, not a pass.** If you have not run the bin, you have not graded B —
  do not certify "it's well-formed / traced / accessible" from reading.
- **The defect this axis catches outright is *right-meaning-won't-operate*** — the sharp idea trapped
  in prose. The defect it *cannot* catch is *operable-but-hollow*; that one is on axis A, behind the
  gate's one mechanizable smell (`GENERIC_IDEA`) and the adversarial idea-refutation.
