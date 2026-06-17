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
   `routing-decomposer` the closest **in-repo** neighbours are the `*-decomposer` family that share
   its "decompose / grade on two axes" vocabulary — `code-decomposer` ("grade a unit of code against
   its contract"), `component-decomposer`, `layout-decomposer` ("decompose this UI layout into
   regions"), `type-decomposer` ("grade a schema so it can't admit illegal states"),
   `config-decomposer`. The **global peer `skills-studio`** ("author a new skill end to end", "run the
   critic panel") is also fenced and belongs in the negatives — but note it is an *external/global*
   authoring skill, **not a sibling in this repo**, so its boundary is asserted by the fence rather
   than run as an in-repo two-description check. A description that holds these has real precision; one
   that grabs them is the over-trigger defect, caught by name. This is the B3 Boundary gate's raw
   material.
2. **Near-misses — one word off a positive.** The phrase that shares most of a positive's words but
   belongs elsewhere: "grade this *layout*" (→ layout-decomposer), "grade this *code*" (→
   code-decomposer), "*write* a description for my skill" (→ authoring, the global `skills-studio`).
   These probe the *fence*: a description with no NOT-for grabs them; a fenced one holds them. (The
   eval parses the `NOT for` clause OUT of the positive tokens and makes the fenced vocabulary REPEL,
   so a truthful fence makes the near-miss score *lower*, not higher.)

A corpus of 6 positives and 6 negatives where the negatives are *all adversarial* is worth more than
40 positives and 40 obvious off-topic negatives.

## The precision / recall / F1 read

The eval (`bin/routing-eval.py`) scores a phrase as "routes here" iff its **lexical token overlap**
with the description (positive tokens, minus a repulsion from any fenced NOT-for tokens) clears a
threshold, then computes:

- **recall** = positives that fired / all positives — *coverage* (B1). Low ⇒ under-trigger ⇒ add
  trigger words for the *missed positives* it lists — **but** a paraphrase positive that shares no
  surface words scores 0 *even when the description routes it fine*: the proxy is blind to synonyms, so
  a low paraphrase-recall may be an artifact, not a hole (the eval cannot grade B4 — read before
  fixing).
- **precision** = positives that fired / everything that fired — *discipline* (B2). Low ⇒ over-trigger
  ⇒ tighten scope / add a NOT-for for the *grabbed negatives* it lists.
- **F1** = the harmonic mean — a *summary*, **not the pass condition**. It is gameable: a grammarless
  keyword list that echoes the corpus tokens scores F1 1.000 while being no description at all. So a
  green F1 is no evidence; the pass is `description-lint` clean **+ a human read** of the named holes.

The eval's `--min-f1` (default 0.7) is a **tripwire** that surfaces a routing concern, and it **prints
both kinds of hole as named phrases** — that list, read by a human, is the real product. Fix the
*wording* (re-running after each edit); never edit the corpus or the threshold to make the number
green — those phrases are the requirement.

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

## Worked shape — `routing-decomposer`'s own checked-in corpus

This skill **dogfoods itself**: its routing is tested by the checked-in `routing-decomposer.corpus.json`
(listed in `skill.json`). Positives span the families above (imperative / diagnostic / symptom /
object-first / indirect-paraphrase); negatives are drawn from the **in-repo `*-decomposer` siblings**
("decompose and grade a unit of code against its contract", "decompose this UI layout into regions",
"grade a type or schema so it can't admit illegal states") plus the global peer **skills-studio**
("author a whole new skill from scratch"). Running the eval of this skill's own description against it
yields F1 ≈ 0.86 with a few named holes — and those holes are the *point*: two recall misses that are
**paraphrase artifacts** the lexical proxy can't see (not defects), and two precision grabs from the
adversarial boundary (a `code-decomposer` phrase sharing "grade/axes/spec/execution", a
`skills-studio` phrase sharing "description/whole skill") for a human to weigh. The number isn't the
verdict; the read is.

The runnable selftest fixtures in `bin/routing-eval.py` are a miniature of the discipline:
`GOOD_DESC` + `GOOD_CORPUS` clear F1 ≥ 0.7; the vague `MISROUTING_DESC` under-triggers; the broad
`OVERBROAD_DESC` over-triggers; the paired `FENCE_BASE_DESC` / `FENCE_WITH_DESC` pin the fix that a
truthful fence **repels** sibling negatives instead of grabbing them; and a gamed keyword list shows a
green F1 with no fence and no quoted triggers — proof the number alone certifies nothing.

The corpus is the artifact this skill is *about*. A skill without a checked-in adversarial corpus has
an unmeasured routing surface — which is to say, a description nobody has actually tested.
