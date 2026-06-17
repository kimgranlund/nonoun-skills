# The eval corpus — the centerpiece

A description is a routing classifier, and **a classifier is only as honest as the labeled set you
test it on.** This is the heart of the skill: the corpus is the *test*, and a flattering corpus gives
a flattering, useless score. Build it adversarially or don't bother measuring.

The corpus is a single JSON object the eval reads:

```json
{
  "positives": [
    "grade this skill's description",
    "is my description routing correctly",
    "why does my skill never fire on real requests",
    "this skill over-triggers and grabs the wrong requests",
    "score the precision and recall of this routing surface",
    "build a routing corpus for my skill"
  ],
  "negatives": [
    "author a whole new skill from scratch end to end",
    "run the adversarial critic panel on my plugin",
    "decompose this UI layout into regions",
    "grade a unit of code against its contract"
  ]
}
```

- **positives** = requests that SHOULD route to this skill (they must *fire* — B1, recall).
- **negatives** = requests that SHOULD NOT (they must *hold* — B2/B3, precision).

## Positives — cover the invocation space, not one phrasing

The recall failure is a corpus with one *way of asking* repeated. Real users ask the same skill in
structurally different sentences that share few words. Cover the families:

- **Imperative** — "grade this description", "score the routing of my skill".
- **Diagnostic / why** — "why does my skill never fire", "why does this trigger on everything".
- **Symptom** — "it grabs requests meant for another skill", "no one's skill picks this up".
- **Object-first** — "this frontmatter description — is it routing right?".
- **Indirect / implied** — "my new skill isn't getting used" (the user names the symptom, not the
  task). These are the B4 robustness positives; include a few so robustness is *measured*, not hoped.

A positive set that is six rewrites of one imperative will score high and prove nothing. The eval's
*missed positives* tell you which family the description fails to cover.

## Negatives — the corpus's whole value is here

A negative drawn from an unrelated domain ("write me a sonnet") is held by every description; it
tests nothing. **The decisive negatives are adversarial**, drawn from two sources:

1. **Sibling-skill trigger phrases.** Take the actual positives of the skills nearest this one — the
   ones a router would weigh against it — and put them in *this* skill's negatives. For
   `routing-decomposer` the prime sibling is **skills-studio**: "author a new skill end to end",
   "run the critic panel", "build the routing corpus *and the whole skill*". A description that holds
   these has real precision; one that grabs them is the over-trigger defect, caught by name. This is
   the B3 Boundary gate's raw material.
2. **Near-misses — one word off a positive.** The phrase that shares most of a positive's words but
   belongs elsewhere: "grade this *layout*" (→ layout-decomposer), "grade this *code*" (→
   code-decomposer), "*write* a description for my skill" (→ authoring, skills-studio). These probe
   the *fence*: a description with no NOT-for grabs them; a fenced one holds them.

A corpus of 6 positives and 6 negatives where the negatives are *all adversarial* is worth more than
40 positives and 40 obvious off-topic negatives.

## The precision / recall / F1 read

The eval (`bin/routing-eval.py`) scores a phrase as "routes here" iff its content-token overlap with
the description clears a threshold, then computes:

- **recall** = positives that fired / all positives — *coverage* (B1). Low ⇒ under-trigger ⇒ add
  trigger words for the *missed positives* it lists.
- **precision** = positives that fired / everything that fired — *discipline* (B2). Low ⇒ over-trigger
  ⇒ tighten scope / add a NOT-for for the *grabbed negatives* it lists.
- **F1** = the harmonic mean — the single gate number. It punishes trading one for the other (a
  grab-everything description has recall 1.0 and dismal precision, and F1 stays low).

The eval gates on F1 (default 0.7) and **prints both kinds of hole as named phrases**. Fix the
*wording* until both lists empty; never edit the corpus to make the number green — those phrases are
the requirement.

## The adversarial-negative discipline (the part people skip)

The corpus is only a real test if building it *tried to break the description*:

- **Pull negatives from the router's actual confusables**, not your imagination. List the 3–5 skills
  whose descriptions are closest in vocabulary; harvest a couple of each one's real triggers as your
  negatives. (If you have the sibling descriptions, the B3 two-description check makes this rigorous —
  see `routing-axis.md`.)
- **Write each near-miss to be *barely* negative** — change one word from a positive so it belongs to
  a sibling. If you can't tell which side it's on, it's a labeling question the description must
  answer; that's a sign the fence is needed.
- **A negative you're *sure* will be held is a wasted slot.** Spend slots on the ones you suspect the
  description might grab. The corpus earns its keep by *failing* a weak description.
- **Re-derive the corpus when a sibling changes.** A new sibling skill, or a renamed one, shifts the
  boundary; stale negatives stop testing it. The corpus ships next to the skill and versions with it.

## Worked shape — `routing-decomposer`'s own corpus

This skill's own routing is tested with positives across the families above and negatives dominated by
**skills-studio** (the whole-skill-authoring sibling it must defer to) plus near-misses from the other
decomposers ("grade this layout / code / component"). The selftest fixtures in
`bin/routing-eval.py` (`GOOD_DESC` + `GOOD_CORPUS`) are a runnable miniature: a clean description
clears F1 ≥ 0.7 on them, the deliberately vague `MISROUTING_DESC` under-triggers (misses positives),
and the deliberately broad `OVERBROAD_DESC` over-triggers (grabs the skills-studio / sibling
negatives). That is the whole discipline in one selftest: a corpus that *separates* a good description
from both failure modes.

The corpus is the artifact this skill is *about*. A skill without a checked-in adversarial corpus has
an unmeasured routing surface — which is to say, a description nobody has actually tested.
