# The ROUTING axis — does it route the right requests, measurably?

The Routing axis (B1–B5) grades *mechanism*, bottom-up: from "does this fire on its own requests" to
"does the route survive paraphrase and reword." It is the **mechanizable** axis — route it to
`bin/routing-eval.py` and **trust the measurement, not the read-through.** A description is a binary
classifier over the space of requests; precision and recall are its only honest summary, and you
cannot read them off the prose. The eval is a transparent proxy (content-token overlap above a
threshold); its job is to make every miss and every grab a *named phrase* you can fix.

## The ladder

| Level | Gate | What the eval measures | The signal |
|---|---|---|---|
| **B1 Fires** | `[gate, code]` | recall over positives | on-target phrases route here; a *missed positive* is an under-trigger hole |
| **B2 Holds** | `[gate, code]` | precision over negatives | off-target phrases stay out; a *grabbed negative* is an over-trigger hole |
| **B3 Boundary** | `[gate, code]` | precision vs the *sibling's* description | a sibling's phrase scores higher there than here |
| **B4 Robustness** | review | (manual / extended corpus) | paraphrases & indirect phrasings still route |
| **B5 Stability** | review | (manual / extended corpus) | the route is consistent across small rewordings |

The gates cascade: a description that doesn't even *fire on its own positives* (B1) can't be graded
for boundary cleanliness — fix recall first. A red gate stops the axis.

## Precision vs recall, for routing

The two errors are opposite and need opposite fixes — averaging them (or chasing one) misleads:

- **Recall hole = under-trigger.** The skill never gets picked for requests it should serve. Cause:
  the description names too few of the words real requests use (an A3 trigger gap), or describes the
  capability too abstractly to match (an A1/A5 vagueness problem). **Fix: add trigger words / concrete
  phrasings.** Evidence: the eval's *missed positives*.
- **Precision hole = over-trigger.** The skill gets grabbed for requests that belong elsewhere. Cause:
  the description is too broad, or has no NOT-for fence (an A2/A4 scope gap). **Fix: tighten scope,
  add the named NOT-for, drop the over-general clause.** Evidence: the eval's *grabbed negatives*.

F1 is the single number that won't let you cheat one for the other — a description that grabs
everything has perfect recall and useless precision, and F1 stays low. The eval gates on F1 and
*lists both kinds of hole by name* so the fix is a wording edit, not a number.

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
real test is the **sibling skill's own trigger phrases**. Two-description discipline:

- Take the boundary phrases (a sibling's positives that are near this skill's domain) and score them
  against **both** descriptions with the eval.
- **Pass** = each boundary phrase scores *higher* against the sibling's description than against this
  one. The sibling *owns* its phrases; this skill merely doesn't grab them.
- A boundary phrase that scores higher *here* is a real mis-route waiting to happen — fix it with a
  NOT-for that names the sibling (A4), which is exactly what makes the model route it onward.

This is precision measured against the worst case, and it's the gate that turns a vague "seems
distinct" into a verified one.

## B4 · Robustness `[review]` — survive paraphrase

Beyond the corpus's literal phrasings: does an **indirect** request route? A user who *describes the
problem* without naming the skill's verbs — "my new skill never seems to get used" (→ under-trigger
diagnosis) — should still land here. Score by how far the description's signal reaches past its exact
trigger words. A description that only matches its own quoted phrases is brittle; one whose capability
words are the *natural vocabulary of the problem* is robust. Extend the corpus with paraphrase
positives to measure this rather than guess it.

## B5 · Stability `[review]` — consistent across rewordings

The route shouldn't flip on a synonym. If "grade the description" routes but "evaluate the
description" doesn't, the description is leaning on one verb. Score stability by perturbing positives
(swap verbs, reorder, add filler) and checking the route holds. Instability points back at a thin A3
trigger set — broaden the capability vocabulary so the route doesn't hinge on a single token.

## Reading the eval honestly

- **F1 below the gate is a wording bug, not a corpus bug.** The temptation is to delete the missed
  positives or the grabbed negatives to make the number green. That is exactly backwards — those
  phrases *are the requirement*. Fix the description until it satisfies them.
- **A flattering score on a weak corpus means nothing.** If every negative is off-topic, perfect
  precision is free and proves nothing. The corpus's adversarial negatives (sibling phrases, near
  misses) are what make the precision number *load-bearing* — see `eval-corpus.md`.
- **The threshold is a calibration, not a target.** It's set so a well-built description (named
  capability + concrete triggers + a fence) lands the corpus cleanly; tuning it per-skill to force a
  pass defeats the measurement.

The output of this axis is the **routing half of the scorecard** — precision / recall / F1, the
listed missed positives and grabbed negatives, and the boundary verdict against each named sibling —
paired with the A-axis claim. The corpus that produced it ships next to the skill (see `policy.md`).
