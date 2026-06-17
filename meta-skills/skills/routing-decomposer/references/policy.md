# Policy — definition-of-done, the corpus + scorecard, and the handoff

The reusable artifacts and boundaries: what "done" means for a routing surface, the shape of the
corpus and the scorecard the skill emits, and how this hands off to `skills-studio` without
overlapping it.

## Definition-of-done (a description is shippable when…)

Gated items route to `bin/`; review items are 1–5 judgments. SHIPPABLE = the quadrant top-left.

1. **Honest capability (A1)** — states WHAT the skill does, accurately, with no overclaim, verified
   against the skill's actual body + bin.
2. **Truthful fence (A2)** — an explicit NOT-for that names the confusable sibling(s) and is true.
3. **Triggers cover the space (A3)** — concrete quoted phrases across the imperative / diagnostic /
   symptom / indirect families, not one phrasing (≥4).
4. **Disambiguates siblings (A4)** — names the neighbour and routes onward for each confusable (≥4).
5. **Economical (A5)** — ≤1024 chars, no filler, no author voice; every clause earns routing signal
   (≥4). `bin/description-lint.py` is clean.
6. **Fires on its positives (B1)** — a human has READ `bin/routing-eval.py`'s recall misses and
   confirmed each direct phrasing is covered (a paraphrase miss may be a proxy artifact, not a hole).
7. **Holds its negatives (B2)** — the eval's grabbed-negative list is empty (or each grab is read and
   the fence tightened); the truthful `NOT for` fence repels the in-repo sibling negatives.
8. **Beats siblings on the boundary (B3)** — every boundary phrase scores higher against the in-repo
   `*-decomposer` sibling's description than against this one.
9. **Robust + stable (B4/B5)** — paraphrases and indirect phrasings still route; the route survives
   small rewordings (≥4). **B4 is a human judgment — the eval is blind to paraphrase and cannot grade
   it; do not read a low paraphrase-recall as an automatic defect.**
10. **Both axes ≥4, zero gate fails, SHIPPABLE quadrant** — reported as two scores, gate failures
    first, with the adversarial corpus checked in and the scorecard recorded. **The pass condition is
    the `description-lint` pass + the human read — never the F1 number** (a keyword list scores F1
    1.000; the eval is a legibility aid, not a certifier).

## The two artifacts

**Routing corpus** (`*.corpus.json`) — the labeled test, built adversarially (see `eval-corpus.md`),
checked in next to the skill and versioned with it:

```json
{
  "skill": "routing-decomposer",
  "positives": [
    "grade this skill's description",
    "why does my skill never fire on real requests",
    "this skill over-triggers and grabs the wrong requests",
    "score the precision and recall of this description"
  ],
  "negatives": [
    "decompose and grade a unit of code against its contract",
    "decompose this UI layout into regions and groups",
    "grade a type or schema so it can't admit illegal states",
    "author a whole new skill from scratch end to end"
  ],
  "siblings_in_repo": ["code-decomposer", "component-decomposer", "layout-decomposer", "type-decomposer", "config-decomposer"],
  "global_peers": ["skills-studio"]
}
```

Note the split: **`siblings_in_repo`** are the real `*-decomposer` skills in this marketplace whose
boundary is *testable* (the B3 two-description check works against them); **`global_peers`** names
`skills-studio` honestly as an external/global authoring skill — it is fenced and routed to, but it is
**not** a skill in this repo, so its boundary is asserted by the fence, not measured here. (This skill's
own checked-in corpus, `routing-decomposer.corpus.json`, follows exactly this shape.)

**Scorecard** — emitted by GRADE / DECOMPOSE, the two axes reported separately:

```
INSTRUCTION (claim)                 ROUTING (behavior)
  A1 Capability   gate  pass          B1 Fires       gate  pass   recall    1.00
  A2 Scope        gate  pass          B2 Holds       gate  pass   precision 0.92
  A3 Triggers     review 4            B3 Boundary    gate  pass   (beats skills-studio)
  A4 Disambig.    review 4            B4 Robustness  review 4     F1 0.96
  A5 Economy      review 5            B5 Stability   review 4
  axis: 4.3                           axis: 4.0
quadrant: SHIPPABLE   |   lint: clean (612 chars, 6 triggers)   |   missed: none   grabbed: none
```

Report **two axis scores, never one** — `reads well, mis-routes` (A passes, B fails) and `routes
accurately but misleads` (B passes, A fails) need opposite fixes (wording-for-corpus vs honest
rewrite), and averaging hides which you have.

## Running the gates

```sh
# A-axis structural floor (cheap static pre-filter)
python3 bin/description-lint.py path/to/SKILL.md

# B-axis routing measurement (the centerpiece) — extract the description first, or point at a .txt
python3 bin/routing-eval.py description.txt path/to/skill.corpus.json --min-f1 0.7
```

The lint is the **everywhere-gate and the pass condition** (run it on every description; it must be
clean). The eval is a **legibility aid** — run it against the adversarial corpus to *surface* the
named recall/precision holes for a human to read; its F1 is a tripwire, **not** the proof (a
grammarless keyword list echoing the corpus scores F1 1.000). A SHIPPABLE verdict requires: the lint
clean, the eval run, the corpus's negatives drawn from the in-repo siblings, **and a human read** of
every named miss/grab — not a green number (see `eval-corpus.md`).

This skill **dogfoods itself**: its own corpus is `routing-decomposer.corpus.json` (checked in,
listed in `skill.json`). Running the eval of this skill's description against it yields F1 ≈ 0.86 with
a handful of named holes — exactly the human-read material the discipline produces: two recall misses
that are *paraphrase artifacts* (the proxy's lexical-overlap limit, not defects) and two precision
grabs from the adversarial boundary (a `code-decomposer` phrase sharing "grade/axes/spec/execution"
and a `skills-studio` phrase sharing "description/whole skill"). The number is not the verdict; the
read is.

## Handoff — what this skill does NOT do

`routing-decomposer` is the **focused two-axis grade of the description's routing behavior**, aided by
a deterministic eval. It is a *narrow* tool, and the boundary with `skills-studio` is the most
important thing it gets right about itself — with the honest caveat that **`skills-studio` is a
global/external authoring skill, not a sibling in this repo.** It is the deferral target by name; it
just isn't a marketplace neighbour whose boundary you can run the in-repo two-description check
against:

- **→ `skills-studio`** (external/global) owns the *whole* skill lifecycle: authoring a new skill
  end-to-end (interview → research → draft → package), editing/optimizing the *body*, running the
  9-critic adversarial panel, and producing SKILL.md + skill.json + CHANGELOG + ROADMAP.
  `routing-decomposer` grades and fixes **the description's routing**, one surface, with a
  precision/recall eval.
  - If the request is "*author / build / refactor my skill*" → that's `skills-studio`.
  - If the request is "*is my description routing right / why doesn't it fire / score its precision*"
    → that's here.
  - When grading a description here surfaces that the *skill itself* (not just the description) is
    wrong — wrong capability, missing a mode — **hand off to `skills-studio`**; don't re-author the
    skill from this seat.
- **not the other decomposers** — "grade this layout / code / component / diagram" route to
  `layout-`, `code-`, `component-`, `mermaid-decomposer`. This skill grades a *routing surface*, not
  those artifacts.
- **not the repo gate** — `bin/check-skills.py` enforces the ≤1024 hard contract structurally;
  `routing-decomposer` grades the *quality of routing* within that contract. The gate says "valid";
  this skill says "routes well".

## Governance

- **Corpora are checked in** next to the skill as the test of record; they version with the
  description and are the first thing a reviewer reads when a routing change is proposed.
- **Re-derive the corpus when the neighbourhood changes** — a new or renamed sibling shifts the
  boundary; stale negatives stop testing precision (see `eval-corpus.md`).
- **The eval threshold is a calibration, not a per-skill knob** — don't tune it to force a pass; fix
  the wording so a well-built description clears it at the default.
- **One description, two axes, two scores** — the discipline the whole skill exists to enforce: never
  ship a routing surface that hasn't been *measured* against an adversarial corpus, and never average
  the claim with the behavior.
