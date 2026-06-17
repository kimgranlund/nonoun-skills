# The ROUTING axis — does it route the right requests, measurably?

The Routing axis (B1–B5) grades *mechanism*, bottom-up: from "does this fire on its own requests" to
"does the route survive paraphrase and reword." It is the axis you **instrument** with
`bin/routing-eval.py` — but the eval is a **legibility aid, not the proof.** A description is a binary
classifier over the space of requests; the eval makes every miss and every grab a *named phrase you
read*, so the fix is a wording edit you can see. It does **not** certify the description: it scores
**lexical token overlap only** (content-token overlap above a threshold), so a green F1 is not a pass
and a low recall may be a proxy artifact. The pass condition is `description-lint` clean **+ a human
read** of the named misses/grabs — never an F1 number.

### What the eval can and cannot see

- **It sees surface words.** Overlap between the request's tokens and the description's *positive*
  tokens (the claim + triggers) raises a phrase's route-here score.
- **The `NOT for …` fence REPELS.** The eval parses the fenced (NOT-for) sibling vocabulary OUT of the
  positive set and treats it as *negative* signal — a phrase overlapping the fenced words is pushed
  *below* threshold. So a truthful sibling fence **improves** precision here, as the doctrine intends;
  it never magnetizes the very siblings it disclaims.
- **It is BLIND to paraphrase, synonyms, and intent — it CANNOT grade B4.** A genuine paraphrase
  positive ("my new skill never gets picked") can score recall **0.000** even when the real model
  would route it fine. That is a *measurement limit of the proxy, not a defect in the description.*
  Read every low-overlap miss before "fixing" it; B4 robustness is the human's judgment, not the
  eval's number. Do not stuff trigger words to chase a paraphrase the proxy simply can't measure.

## The ladder

| Level | Gate | What the eval AIDS (you read, then judge) | The signal |
|---|---|---|---|
| **B1 Fires** | `[gate, aided]` | lists recall misses over positives | on-target phrases route here; a *missed positive* is an under-trigger hole (or, for a paraphrase, a proxy artifact) |
| **B2 Holds** | `[gate, aided]` | lists precision grabs over negatives | off-target phrases stay out; a *grabbed negative* is an over-trigger hole |
| **B3 Boundary** | `[gate, aided]` | overlap vs the in-repo *sibling's* description | a sibling's phrase scores higher there than here |
| **B4 Robustness** | review (human only) | the eval CANNOT grade this — blind to paraphrase | paraphrases & indirect phrasings still route |
| **B5 Stability** | review | (manual / extended corpus) | the route is consistent across small rewordings |

`[gate, aided]` = the eval *surfaces* the named phrases at this level; the human reads them and makes
the gate call (a green number is not the pass). The gates cascade: a description that doesn't even
*fire on its own positives* (B1) can't be graded for boundary cleanliness — fix recall first. A failed
gate stops the axis.

## Precision vs recall, for routing

The two errors are opposite and need opposite fixes — averaging them (or chasing one) misleads:

- **Recall hole = under-trigger.** The skill never gets picked for requests it should serve. Cause:
  the description names too few of the words real requests use (an A3 trigger gap), or describes the
  capability too abstractly to match (an A1/A5 vagueness problem). **Fix: add trigger words / concrete
  phrasings.** Evidence: the eval's *missed positives*.
- **Precision hole = over-trigger.** The skill gets grabbed for requests that belong elsewhere. Cause:
  the description is too broad, or has no NOT-for fence (an A2/A4 scope gap). **Fix: tighten scope,
  add the named NOT-for, drop the over-general clause.** Evidence: the eval's *grabbed negatives*.

F1 is a useful *summary* of the two — a description that grabs everything has perfect recall and
useless precision, and F1 stays low — but it is **not the pass condition.** It is gameable: a
grammarless keyword list that echoes the corpus tokens scores F1 1.000 while being no description at
all. So the eval's real product is the **named list of holes**, read by a human; the F1 (and the
`--min-f1` tripwire) only flags *that there is something to read*. Fix the wording; never treat the
number as the verdict.

## B1 · Fires `[gate, code]` — recall

Every positive phrase in the corpus must route here. Run the eval; read the *missed positives*. Each
miss is a real way a user would ask that the description fails to match. The fix is almost always an
A3 trigger phrase: add the word(s) the missed phrasing uses. **Do not lower the threshold to pass
positives** — that inflates recall by also grabbing negatives (it trades B1 for B2). Fix the words.

## B2 · Holds `[gate, code]` — precision

Every negative phrase must stay below threshold. Read the *grabbed negatives*. Each grab is a request
that belongs to another skill (or to no skill) that this description wrongly claims. The fix is an
A2/A4 scope tightening: a NOT-for that names the territory, or removing an over-general capability
clause that overlaps the negative. **Do not raise the threshold to repel negatives** — that drops
positives too. Tighten the *scope*, not the knob.

## B3 · Boundary `[gate, code]` — beat the sibling on its own turf

The hardest, most decisive gate. A negative drawn from an *unrelated* domain is easy to hold; the
real test is the **in-repo sibling skill's own trigger phrases** — the `*-decomposer` family
(`code-`, `component-`, `layout-`, `type-`, `config-decomposer`, …) that share this skill's
"decompose / grade on two axes" vocabulary. (The global authoring peer `skills-studio` is fenced too,
but it lives outside this repo — its boundary is asserted by the fence, not testable as an in-repo
two-description check.) Two-description discipline:

- Take the boundary phrases (a sibling's positives that are near this skill's domain) and score them
  against **both** descriptions with the eval.
- **Pass** = each boundary phrase scores *higher* against the sibling's description than against this
  one. The sibling *owns* its phrases; this skill merely doesn't grab them.
- A boundary phrase that scores higher *here* is a real mis-route waiting to happen — fix it with a
  NOT-for that names the sibling (A4), which is exactly what makes the model route it onward.

This is precision measured against the worst case, and it's the gate that turns a vague "seems
distinct" into a verified one.

## B4 · Robustness `[review]` — survive paraphrase (the eval CANNOT grade this)

Beyond the corpus's literal phrasings: does an **indirect** request route? A user who *describes the
problem* without naming the skill's verbs — "my new skill never seems to get used" (→ under-trigger
diagnosis) — should still land here. **This is a human review, not an eval gate.** The proxy grades
lexical overlap, so a paraphrase that shares no surface words scores recall 0.000 *regardless of how
robust the description actually is* — its number here is meaningless. Judge robustness by reasoning
about how far the description's *vocabulary* reaches past its exact trigger words: a description whose
capability words are the natural vocabulary of the problem is robust; one that only matches its own
quoted phrases is brittle. You may add paraphrase positives to the corpus to *make the gap visible*
(the eval will list them as misses), but read them as "is this a real coverage hole, or a proxy
artifact?" — never read a low paraphrase-recall as an automatic defect.

## B5 · Stability `[review]` — consistent across rewordings

The route shouldn't flip on a synonym. If "grade the description" routes but "evaluate the
description" doesn't, the description is leaning on one verb. Score stability by perturbing positives
(swap verbs, reorder, add filler) and checking the route holds. Instability points back at a thin A3
trigger set — broaden the capability vocabulary so the route doesn't hinge on a single token.

## Reading the eval honestly

- **The number is a tripwire; the list is the work.** A red F1 (below `--min-f1`) means *go read the
  named misses/grabs* — it is not a verdict, and a green F1 is not a pass (a keyword list scores
  1.000). The pass condition is `description-lint` clean **+ a human read**.
- **A miss on a direct phrasing is a wording bug; a miss on a paraphrase may be a proxy artifact.**
  For a direct phrasing, add the trigger word the request uses. For an indirect/paraphrase positive
  that shares no surface words, ask whether the real model would route it — the eval is blind to
  synonyms (it cannot grade B4), so a 0.000 there is often the proxy's limit, not a hole. Either way,
  never delete the phrase to green the number — the phrases *are the requirement*.
- **A flattering score on a weak corpus means nothing.** If every negative is off-topic, perfect
  precision is free and proves nothing. The corpus's adversarial negatives (in-repo sibling phrases,
  near misses) are what make the precision number *load-bearing* — see `eval-corpus.md`.
- **The threshold is a calibration, not a target.** It's set so a well-built description (named
  capability + concrete triggers + a fence) lands the corpus cleanly; tuning it per-skill to force a
  pass defeats the measurement.

The output of this axis is the **routing half of the scorecard** — the listed missed positives and
grabbed negatives (read by a human), the boundary verdict against each in-repo sibling, and the
precision/recall/F1 as a *legibility summary* — paired with the A-axis claim. The corpus that produced
it ships next to the skill (this skill's own is `routing-decomposer.corpus.json`; see `policy.md`).
