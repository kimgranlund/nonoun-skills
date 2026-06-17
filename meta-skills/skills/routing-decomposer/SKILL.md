---
name: routing-decomposer
description: >
  Decompose, write, and grade the ROUTING SURFACE of a skill — its frontmatter description — on two
  crossing axes: INSTRUCTION (capability → scope → triggers → disambiguation → economy) and ROUTING
  (fires → holds → boundary → robustness → stability), scored separately so a description that reads
  well can't hide that it mis-routes. A description is a routing classifier, not prose: ROUTING
  routes to a deterministic eval (bin/routing-eval.py) measuring precision/recall/F1 against a
  labeled corpus of should-trigger / should-not-trigger phrases (negatives drawn adversarially from
  siblings); INSTRUCTION gates on capability/scope honesty the eval can't see, pre-filtered by
  bin/description-lint.py. Triggers on: "grade this skill's description", "is my description routing
  correctly", "why doesn't my skill fire", "this skill over-triggers", "score the routing
  precision/recall", "build a routing corpus". NOT for authoring a whole skill end to end
  (skills-studio); NOT for grading layouts/code/components (the decomposers).
---

# routing-decomposer — grade a skill's routing surface on two crossing axes

A skill's **routing surface** — its frontmatter `description` — is **correct on two independent axes
that walk the same artifact in opposite directions** — the decomposer seam the layout-, mermaid-,
component-, and [code-decomposers](../../../code-skills/skills/code-decomposer/SKILL.md) apply to
space, diagrams, components, and code, here applied to the one string that decides when a skill
triggers:

- **Instruction · whole → part** grades the **claim**: the capability it states → its scope → its
  triggers → how it disambiguates from siblings → its economy. *"Does it say the right thing,
  honestly?"*
- **Routing · part → whole** grades the **behavior**: it fires on on-target requests → holds against
  off-target ones → routes a sibling's request to the sibling → survives paraphrase → stays stable
  across rewordings. *"Does it route the right requests, measurably?"*

They **cross at the description itself** — the same string is *both* the human-readable claim (what a
maintainer reads to know what the skill does) and the model's routing input (what the classifier
matches a request against). That crossing is the whole technique: a description can be **reads well,
mis-routes** (honest and well-scoped, but it never fires on real requests — *under-trigger / low
recall* — or grabs the wrong ones — *over-trigger / low precision*) or **routes accurately but
misleads** (the triggers land, but the capability/scope claim overclaims). Opposite defects, opposite
fixes — so you **score and report the two axes separately**, never averaged.

The reason this earns a skill: **a description is a routing classifier, not prose — you cannot eyeball
its precision and recall.** You must MEASURE it against a labeled corpus of should-trigger /
should-not-trigger phrases, with the negatives built *adversarially* from sibling skills. Route the
ROUTING axis to a deterministic eval; gate INSTRUCTION on the capability/scope honesty the eval cannot
see.

## Quick Start

**You bring:** a skill description (a draft, an existing `SKILL.md`, or just a capability) and the
question — "write this", "is it routing right?", "why doesn't it fire?", "is it production-ready?".
**You get:** a scored routing corpus, precision/recall/F1 with the missed/grabbed phrases named, and a
two-axis grade with the defect quadrant.

> *"Why does my skill never fire on real requests?"* →
> 1. **Instruction — claim first:** recover the capability `[gate]` and the scope/NOT-for fence
>    `[gate]`; run `bin/description-lint.py` (WHAT + WHEN + NOT, ≥3 concrete triggers, no first-person
>    / vagueness, ≤1024).
> 2. **Build the corpus adversarially:** positives across phrasings (imperative / diagnostic /
>    symptom / indirect); negatives from the sibling skills' own triggers + near-misses.
> 3. **Routing — measure, don't read:** `bin/routing-eval.py <desc.txt> <corpus.json>` scores
>    precision / recall / F1 `[gate]` and lists the **missed positives** (recall holes →
>    under-trigger). Add the trigger words those phrasings use; re-run.
> 4. **Boundary + report:** confirm each sibling's phrases score higher against the *sibling*'s
>    description (B3); then the two axis scores + the quadrant cell — gate failures first — handed to
>    `skills-studio` if the *skill* (not just the description) needs work.

**Modes:** **SPECIFY** (write/optimize a description from a capability + a corpus → iterate the
wording against the eval) · **DECOMPOSE** (read a description → recover claimed capability/scope → run
the routing eval → grade) · **GRADE** (score both axes, gates before reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Instruction** | whole → part | **A1** Capability → **A2** Scope → **A3** Triggers → **A4** Disambiguation → **A5** Economy | "Does it say the *right thing*, honestly?" |
| **B · Routing** | part → whole | **B1** Fires → **B2** Holds → **B3** Boundary → **B4** Robustness → **B5** Stability | "Does it *route the right requests*, measurably?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on
that axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable description is **≥4 on every review
with zero gate failures**, reported as two separate axis scores plus the defect quadrant. The B gates
route to `bin/routing-eval.py`; the A gates are honesty calls the eval can't see, pre-filtered by
`bin/description-lint.py`.

## The doctrine — measure routing, gate honesty on what the eval can't see

The non-obvious core, and the reason it earns a skill:

- **ROUTING is the cheap, deterministic axis** — route B1/B2/B3 to `bin/routing-eval.py` and **trust
  the measurement, not the read-through**. It scores precision / recall / F1 over a labeled corpus and
  lists the exact missed positives (recall holes) and grabbed negatives (precision holes), so the fix
  is a *named wording edit*, not a number. A description that "obviously triggers right" routinely
  misses half its real phrasings — only the eval shows it.
- **The corpus is the test — build the negatives adversarially.** A corpus of off-topic negatives
  ("write me a poem") proves nothing; every description holds those. The decisive negatives are the
  **sibling skills' own trigger phrases** and **near-misses** one word off a positive. A description
  that holds *those* has real precision. (`references/eval-corpus.md` is the centerpiece.)
- **INSTRUCTION's gates are honesty the eval cannot see** — the corpus confirms the words *match*
  requests, not whether the skill *delivers* what they claim. `routes accurately but misleads`
  (overclaim) is exactly what a corpus rubber-stamps. Gate A1/A2 against the skill's real behavior.

## §SelfAudit

- **A description is a classifier — measure it, don't admire it.** Run `routing-eval.py` over an
  adversarial corpus; "it obviously routes right" is *no evidence*, not a pass. Precision and recall
  do not read off the prose.
- **The corpus's whole value is in adversarial negatives.** A flattering corpus (off-topic negatives,
  one-phrasing positives) gives a green F1 that proves nothing. Pull negatives from sibling skills'
  real triggers and from near-misses; spend slots on the negatives you suspect the description might
  grab.
- **Fix the wording, never the corpus or the threshold.** A missed positive points at a trigger word
  to add; a grabbed negative points at a NOT-for fence to tighten. Deleting the phrase, or moving the
  threshold, fakes the score — the phrases *are* the requirement.
- **Gates before reviews, always.** Don't grade economy for a description that overclaims its
  capability, or robustness for one that doesn't fire on its own positives. Stop each axis at its
  first failed gate.
- **Two scores, never one.** *Reads-well-mis-routes* (fix the wording for the corpus) and
  *routes-accurately-but-misleads* (honest rewrite of the claim) need opposite fixes. Report both
  axes and name the quadrant; never average.
- **Description, not skill.** This skill grades and fixes the *routing surface* — it does not author
  the skill, edit its body, or run the critic panel. When grading surfaces that the *skill itself* is
  wrong, hand off to `skills-studio`; don't re-author from this seat.

## Verify Target

A description is **done** when: it states an honest capability with no overclaim and a truthful
NOT-for fence (A1/A2); triggers/disambiguation/economy ≥4 with `description-lint.py` clean (WHAT +
WHEN + ≥3 concrete triggers, no first-person/vagueness, ≤1024); `routing-eval.py` fires on every
corpus positive (recall, B1) and holds every adversarial negative (precision, B2); each sibling's
phrases score higher against the *sibling*'s description (boundary, B3); robustness + stability ≥4;
and both axes score ≥4 with zero gate failures, landing in the **SHIPPABLE** quadrant — corpus +
scorecard checked in. **NOT done** when: it reads well but the eval misses real phrasings or grabs
sibling negatives (*reads well, mis-routes*); or the triggers land but the capability/scope claim
overclaims (*routes accurately but misleads*); or the corpus's negatives are off-topic (a flattering,
unmeasured score); or one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Instruction × Routing), the leveled walk (A1–A5 × B1–B5) with gates, the defect quadrant, the measure-routing / gate-honesty doctrine, and the SPECIFY / DECOMPOSE / GRADE workflows |
| `references/instruction-axis.md` | **the Instruction axis** — capability honesty + no-overclaim, the NOT-for fence, WHAT+WHEN+NOT craft, disambiguating named siblings, and the ≤1024 economy; the honesty gates the eval can't see |
| `references/routing-axis.md` | **the Routing axis** — precision vs recall for routing, the fires / holds / boundary gates, the two-description boundary check, and reading the eval honestly; mechanized by `bin/routing-eval.py` |
| `references/eval-corpus.md` | **THE centerpiece** — how to build a labeled routing corpus: positives across phrasings, negatives drawn adversarially from sibling skills + near-misses, the precision/recall/F1 read, and the adversarial-negative discipline |
| `references/description-craft.md` | **writing or fixing the words** — concrete before/after rewrites that move precision or recall (recall hole / precision hole / overclaim), the trigger-phrase family patterns, and the anti-patterns the lint flags |
| `references/policy.md` | **definition-of-done / handoff** — the 10-point DoD, the corpus + scorecard shapes, running the gates, and the seam to `skills-studio` (whole-skill authoring) it defers to |
| `bin/routing-eval.py` | **mechanizes B1–B3** — scores precision / recall / F1 of a description against a labeled corpus via a transparent token-overlap proxy; lists missed positives + grabbed negatives. `<description.txt> <corpus.json> [--threshold T] [--min-f1 F]` · `selftest` |
| `bin/description-lint.py` | **the A-axis static pre-filter** — checks a `SKILL.md` description: ≤1024, WHAT + WHEN/trigger + NOT-for signals, ≥N concrete quoted triggers; flags first-person + vagueness. `<SKILL.md> [--min-triggers N]` · `selftest` |
