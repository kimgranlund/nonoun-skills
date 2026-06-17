---
name: routing-decomposer
description: >
  Decompose, write, and grade the ROUTING SURFACE of a skill — its frontmatter description — on two
  crossing axes: INSTRUCTION (capability → scope → triggers → disambiguation → economy) and ROUTING
  (fires → holds → boundary → robustness → stability), scored separately so a description that reads
  well can't hide that it mis-routes. A description is a routing classifier, not prose: ROUTING uses a
  deterministic eval (bin/routing-eval.py) over a labeled corpus to LIST the recall/precision holes by
  name for a human to read (negatives drawn from siblings); INSTRUCTION gates on capability/scope
  honesty the eval can't see, via bin/description-lint.py. Triggers on: "grade this skill's
  description", "is my description routing correctly", "why doesn't my skill fire", "this skill
  over-triggers", "score the routing precision/recall", "build a routing corpus". NOT for authoring a
  whole skill (skills-studio, a global peer); NOT for grading layouts/code/components/types/configs
  (the in-repo *-decomposer siblings).
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
>    symptom / indirect); negatives from the **in-repo `*-decomposer` siblings'** own triggers +
>    near-misses (a checked-in example: `routing-decomposer.corpus.json`).
> 3. **Routing — list the misses, then READ them:** `bin/routing-eval.py <desc.txt> <corpus.json>`
>    lists the **missed positives** (recall holes) and **grabbed negatives** (precision holes) by name.
>    The F1 is a tripwire, *not* a pass — read each: a lexical miss on a direct phrasing → add the
>    trigger word; a miss on a *paraphrase* may be a proxy artifact the eval can't see (it grades
>    surface overlap only). Fix the wording; re-run.
> 4. **Boundary + report:** confirm each in-repo sibling's phrases score higher against the
>    *sibling*'s description (B3); then the two axis scores + the quadrant cell — gate failures first —
>    handed to `skills-studio` (the global authoring peer) if the *skill* (not just the description)
>    needs work.

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
are *aided* by `bin/routing-eval.py` (it surfaces the misses/grabs to read; it does not by itself pass
them — the human reads the named phrases); the A gates are honesty calls the eval can't see,
pre-filtered by `bin/description-lint.py`. **B4 robustness is the human's call** — the eval grades
lexical overlap only and is blind to paraphrase.

## The doctrine — the eval is a legibility AID, the read is the proof

The non-obvious core, and the reason it earns a skill:

- **The eval LISTS misses; it does not CERTIFY.** Route B1/B2/B3 to `bin/routing-eval.py` to make
  every recall hole and precision hole a *named phrase you can read* — not to produce a pass/fail
  number. **A green F1 is not evidence of a good description:** the eval measures *lexical token
  overlap only*, so a grammarless keyword list that echoes the corpus tokens scores F1 1.000. The
  pass condition is **`bin/description-lint.py` clean + a human read of the named misses/grabs**, never
  an F1 number. Treat a low F1 as a *prompt to look*, not a verdict.
- **The eval is blind to paraphrase — it cannot grade B4.** It scores surface-word overlap, so a
  genuine paraphrase or indirect positive ("my new skill never gets picked") can score recall 0.000
  *even when the description routes it fine*. A low recall on indirect phrasings may be a **proxy
  artifact, not a defect** — read each miss before "fixing" it; robustness (B4) is judged by the human,
  not the eval.
- **The fence must REPEL, not magnetize.** The eval parses the `NOT for …` clause OUT of the positive
  routing tokens and treats that fenced vocabulary as *negative* signal — a phrase overlapping the
  fenced (sibling) words is pushed *down*. So adding the doctrine's truthful sibling fence improves
  precision, as it should; it never grabs the very siblings it disclaims.
- **The corpus is the test — build the negatives adversarially.** A corpus of off-topic negatives
  ("write me a poem") proves nothing; every description holds those. The decisive negatives are the
  **in-repo sibling skills' own trigger phrases** (the `*-decomposer` family — `code-`, `component-`,
  `layout-`, `type-`, `config-decomposer`) and **near-misses** one word off a positive. A description
  that holds *those* has real precision. (`references/eval-corpus.md` is the centerpiece.)
- **INSTRUCTION's gates are honesty no eval can see** — the corpus confirms the words *match*
  requests, not whether the skill *delivers* what they claim. `routes accurately but misleads`
  (overclaim) is exactly what a corpus rubber-stamps. Gate A1/A2 against the skill's real behavior.

## §SelfAudit

- **The eval lists misses; the read is the proof.** Run `routing-eval.py` over an adversarial corpus
  to *surface* the named recall/precision holes — then READ them. A green F1 is **not** a pass (a
  keyword list echoing the corpus scores F1 1.000); the pass condition is `description-lint` clean + a
  human read. "It obviously routes right" is also no evidence — but neither is the number on its own.
- **It grades lexical overlap only — a low recall may be a proxy artifact.** A genuine paraphrase
  positive can score recall 0.000 while the description routes it fine; the eval cannot see synonyms
  or intent (it cannot grade B4). Read each miss before "fixing" it — don't stuff trigger words to
  chase a paraphrase the proxy simply can't measure.
- **The corpus's whole value is in adversarial negatives.** A flattering corpus (off-topic negatives,
  one-phrasing positives) gives a green F1 that proves nothing. Pull negatives from the **in-repo
  `*-decomposer` siblings'** real triggers and from near-misses; spend slots on the negatives you
  suspect the description might grab. The truthful `NOT for` fence *helps* here — the eval treats the
  fenced sibling vocabulary as a repellent, not a magnet.
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
  wrong, hand off to `skills-studio` (a **global/external authoring peer**, not a skill in this repo);
  don't re-author from this seat.

## Verify Target

A description is **done** when: it states an honest capability with no overclaim and a truthful
NOT-for fence (A1/A2); triggers/disambiguation/economy ≥4 with **`description-lint.py` clean** (WHAT +
WHEN + ≥3 concrete triggers, no first-person/vagueness, ≤1024); a **human has read** the
`routing-eval.py` output and confirmed every named recall miss is either covered or a known paraphrase
artifact (B1), and every named grab is repelled (precision, B2) — the lint pass + the read are the
condition, **not the F1 number**; each in-repo `*-decomposer` sibling's phrases score higher against
the *sibling*'s description (boundary, B3); robustness + stability are judged ≥4 by the human (the eval
can't grade paraphrase); and both axes score ≥4 with zero gate failures, landing in the **SHIPPABLE**
quadrant — **the adversarial corpus checked in** (e.g. `routing-decomposer.corpus.json`) and the
scorecard recorded. **NOT done** when: it reads well but real direct phrasings miss or sibling
negatives are grabbed (*reads well, mis-routes*); or the triggers land but the capability/scope claim
overclaims (*routes accurately but misleads*); or the corpus's negatives are off-topic (a flattering,
unmeasured score); or a green F1 is treated as the pass; or one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Instruction × Routing), the leveled walk (A1–A5 × B1–B5) with gates, the defect quadrant, the measure-routing / gate-honesty doctrine, and the SPECIFY / DECOMPOSE / GRADE workflows |
| `references/instruction-axis.md` | **the Instruction axis** — capability honesty + no-overclaim, the NOT-for fence, WHAT+WHEN+NOT craft, disambiguating named siblings, and the ≤1024 economy; the honesty gates the eval can't see |
| `references/routing-axis.md` | **the Routing axis** — precision vs recall for routing, the fires / holds / boundary gates, the two-description boundary check, and reading the eval honestly; mechanized by `bin/routing-eval.py` |
| `references/eval-corpus.md` | **THE centerpiece** — how to build a labeled routing corpus: positives across phrasings, negatives drawn adversarially from sibling skills + near-misses, the precision/recall/F1 read, and the adversarial-negative discipline |
| `references/description-craft.md` | **writing or fixing the words** — concrete before/after rewrites that move precision or recall (recall hole / precision hole / overclaim), the trigger-phrase family patterns, and the anti-patterns the lint flags |
| `references/policy.md` | **definition-of-done / handoff** — the 10-point DoD, the corpus + scorecard shapes, running the gates, and the seam to `skills-studio` (the global whole-skill-authoring peer) it defers to |
| `routing-decomposer.corpus.json` | **the checked-in dogfood corpus** — this skill's own labeled test: positives across phrasing families, negatives drawn from the real in-repo `*-decomposer` siblings + the global peer skills-studio. The worked example of an adversarial corpus |
| `bin/routing-eval.py` | **the B1–B3 legibility AID** (not a certifier) — lists the recall/precision holes by name via a transparent *lexical-overlap* proxy (fence vocabulary repels). Grades surface overlap only — blind to paraphrase, so it cannot grade B4; a green F1 is not a pass. `<description.txt> <corpus.json> [--threshold T] [--min-f1 F]` · `selftest` |
| `bin/description-lint.py` | **the A-axis static pre-filter (the pass gate)** — checks a `SKILL.md` description: ≤1024, WHAT + WHEN/trigger + clause-boundary NOT-for signals, ≥N concrete quoted triggers (vague-category quotes rejected); flags first-person + vagueness. `<SKILL.md> [--min-triggers N]` · `selftest` |
