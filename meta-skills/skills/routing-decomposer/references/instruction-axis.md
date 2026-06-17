# The INSTRUCTION axis — does it say the right thing, honestly?

The Instruction axis (A1–A5) grades *intent*, top-down: from the capability the description claims to
the economy of the words that claim it. This is the axis the routing eval **cannot fully see** — the
corpus can confirm the words match requests, but not whether the skill actually delivers what the
words promise. So A1/A2 are **honesty gates**, verified against the skill's real behavior, not the
corpus. It is also the axis LLMs fail silently on: a description that reads fluent and confident while
overclaiming or under-fencing.

## A1 · Capability `[gate]` — WHAT, accurately

State what the skill does, in the request's terms, with **no overclaim**. This is the anchor both the
human reader and the classifier hold.

- **Name the action and the object** — "*grade* a *skill's description*", not "*help with* skills".
  A capability verb the model can match (decompose/grade/score/audit/design/build/convert/extract)
  plus the concrete object is the WHAT.
- **No overclaim.** The single most common A1 failure: the description promises more than the skill
  delivers. "Optimizes any description for perfect routing" when the skill only *measures* and
  *reports* is dishonest — it lands in the `routes accurately but misleads` quadrant, and the corpus
  will happily rubber-stamp it. **Verify the claim against what the skill's body + bin actually do.**
- **Don't underclaim either** — a description that hides a real capability under-triggers on the
  requests that capability serves (a recall hole the corpus catches as missed positives).
- **Gate:** if the capability claim is wrong or dishonest, stop — every trigger below it routes
  requests to a skill that won't satisfy them. Re-write the claim, don't tune the triggers.

## A2 · Scope `[gate]` — the NOT-for fence

Boundaries are not decoration; the **explicit NOT-for clause is the structural cause of precision.**
A description with no fence bleeds onto every neighbour's territory.

- **Fence the siblings, by name.** "NOT for authoring a whole skill (skills-studio)" tells the
  classifier *and* the reader where this skill stops and who picks up. A fence that names the sibling
  is worth more than three adjectives of self-description.
- **The fence must be truthful** — it's the scope half of the honesty gate. A NOT-for that disclaims
  something the skill actually does (or claims a boundary it doesn't respect) is as dishonest as
  overclaim, and equally invisible to the corpus.
- **Fence the near-misses, not just the obvious.** The dangerous over-trigger is onto an *adjacent*
  skill, not an unrelated one. The phrase one word away from a positive is where precision is won or
  lost (see `routing-axis.md` B2/B3 and the adversarial negatives in `eval-corpus.md`).
- **Gate:** no fence (or a false fence) ⇒ the description cannot have reliable precision. Add the
  truthful NOT-for before measuring.

## A3 · Triggers `[review]` — cover the invocation space

Concrete trigger phrases are what the classifier matches a request against. The failure here is
**one phrasing**: the author's pet way of asking, which leaves every other real phrasing un-routed.

- **Enumerate the real ways a user asks** — imperative ("grade this description"), diagnostic ("why
  doesn't my skill fire"), and symptom ("it triggers on everything") phrasings all route here, and
  they share *few words*. One per family, minimum.
- **Quote them.** A quoted phrase ("grade this description") is a concrete routing target; a vague
  category ("routing tasks") is not. The lint requires ≥3 concrete trigger phrases for this reason.
- **Score by coverage of the space, not count** — ten paraphrases of one phrasing is still one
  phrasing. The routing eval's *missed positives* are the direct evidence: each one is an uncovered
  region of the invocation space.

## A4 · Disambiguation `[review]` — name who's on the other side

Where A2 *draws* the boundary, A4 *names the neighbour* and routes the request onward.

- **Distinguish from named sibling skills** it could be confused with — not "other tools" but
  "skills-studio (whole-skill authoring)", "the critic panel (adversarial review)". The model uses
  the named alternative to route *away* from this skill when the request is really the sibling's.
- **One clause per confusable sibling**, in the form "NOT X (do that with `sibling`)". This is what
  turns a B3 Boundary failure (a sibling's phrase grabbed here) into a clean route.
- A description with strong A4 reads as a *map of the neighbourhood*, not an island.

## A5 · Economy `[review]` — every clause earns routing signal

The ≤1024-char budget (the repo's hard contract) is a routing budget, not a style limit.

- **No filler.** Vagueness words — "powerful", "comprehensive", "robust", "various", "and more",
  "leverage" — spend budget and add zero routing signal (the lint flags them). Replace each with a
  concrete capability or trigger phrase.
- **No author voice.** "I will help you…" / "my skill enables you to…" describes the author, not the
  request; the classifier matches against the request. Write WHAT + WHEN, third-person, imperative.
- **Front-load the WHAT and the triggers**; back-load the NOT-for. The most routing-dense clauses
  earn the most space.
- **Within budget is a gate-adjacent fact** — over 1024 chars is a hard FAIL in the repo (and the
  lint), not a review; A5 is the *quality* of the spend under that hard cap.

## The craft loop (writing or fixing the claim)

The A axis is honesty + coverage; you fix it by *rewriting words*, then proving the fix with the eval:

1. **Recover or write the true capability** (A1) and the truthful fence (A2) against what the skill
   actually does — this is the human honesty call.
2. **Run `bin/description-lint.py`** for the structural floor: WHAT present, WHEN/trigger present, ≥3
   concrete triggers, no first-person, no vagueness, within budget.
3. **Run `bin/routing-eval.py`** for coverage: each *missed positive* points at an A3 trigger to add;
   each *grabbed negative* points at an A2/A4 fence to tighten. Fix the wording, re-measure.

The output of this axis is the **claim half of the scorecard** — the recovered/declared capability +
scope + the trigger inventory — paired with the B-axis routing metrics. Concrete before/after rewrites
that move precision or recall live in `description-craft.md`.
