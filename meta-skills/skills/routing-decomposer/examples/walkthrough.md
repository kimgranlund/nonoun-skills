# Worked example — "reads well, mis-routes" on INSTRUCTION × ROUTING

A complete DECOMPOSE → fix → GRADE for one skill's frontmatter `description`, showing the routing
eval **listing** a precision hole *and* a recall hole, then the red→green proof. The two description
files and the corpus here are checked in, and `bin/routing-eval.py` actually scores them.

> The eval is a **lexical-overlap legibility AID**, not a verdict. It LISTS the misses/grabs by name
> so a human can read them; a green F1 is not a pass (the pass is `description-lint` clean + the read).
> Here the holes it lists are *real* (direct phrasings, not paraphrase), so the read confirms them.

## The artifact

A toy skill **`widget-painter`** (paints widgets — colors, fills, themes). Its draft description
(`examples/widget-skill.red.txt`) *reads* fine — "Design and model widgets — handle the widget's
fields and overall appearance." But it never quotes a paint trigger, and it has no `NOT for` fence
against its sibling **`widget-modeler`** (which owns the widget's data model). Does it route?

## DECOMPOSE

**A · Instruction** (whole → part)
- **A1 Capability** `[gate]` — "paint a widget's surface." But the draft says "design and model" — a
  capability claim that bleeds into the sibling. ✗
- **A2 Scope** `[gate]` — no `NOT for` fence naming `widget-modeler`. ✗
- A3 Triggers — zero quoted concrete phrases ("widget needs attention" is a category, not a request).

**B · Routing** (part → whole) — `[gate, code]` — run the eval over the adversarial corpus
(`examples/widget-skill.corpus.json`: paint positives; negatives lifted from `widget-modeler`):

```
$ python3 bin/routing-eval.py examples/widget-skill.red.txt examples/widget-skill.corpus.json
  precision 0.000   recall 0.000   F1 0.000   (tp=0 fp=4 fn=5 tn=0)
  recall holes — positives that do NOT route here:
    ✗ 0.33  paint this widget blue
    ✗ 0.20  set the widget fill and stroke colors          (… all 5 paint requests miss)
  precision holes — negatives this WRONGLY grabs (over-trigger):
    ✗ 0.75  design the widget schema and fields
    ✗ 0.50  build the widget's data model                  (… all 4 modeler requests grabbed)
```

**B1 and B2 both fail, and the eval names every phrase.** It *under-triggers* on its own job (recall
0.000 — "design and model" shares no words with "paint", "recolor", "restyle") **and** *over-triggers*
onto the sibling (precision 0.000 — "design"/"model"/"fields" magnetize the data-model negatives). A
read confirms these are direct phrasings, not paraphrase artifacts — the wording is the defect.

## Fix

Rewrite to the honest capability with concrete quoted triggers **and** a fence naming the sibling
(`examples/widget-skill.green.txt`): "Paint and restyle a widget's surface … Triggers on: 'paint
this widget blue', 'restyle the widget surface' … NOT for the widget's data model — schema, fields,
validation (widget-modeler)."

```
$ python3 bin/routing-eval.py examples/widget-skill.green.txt examples/widget-skill.corpus.json
  precision 1.000   recall 1.000   F1 1.000   (tp=5 fp=0 fn=0 tn=4)
  · every corpus positive cleared threshold and every negative held
routing-eval: clear — F1 1.000 (a legibility check, not a pass; the read is the proof)
```

The triggers now overlap the paint positives (recall closed); the `NOT for` fence's sibling
vocabulary (`schema`, `fields`, `model`, `validation`) acts as a *repellent*, pushing every
`widget-modeler` negative below threshold (precision closed). The red→green is the proof.

## GRADE — two scores, never averaged

- **Instruction: A1/A2 gate-fail → (after rewrite) 5/5** — capability now honest ("paint", not
  "model"), scope fenced against `widget-modeler`, ≥3 concrete triggers (`description-lint` clean).
- **Routing: B1/B2 gate-fail → (after rewrite) 5/5** — fires on every paint positive, holds every
  modeler negative; a human read confirms the listed holes are closed, not papered over.

**Quadrant:** the red description sat in **"reads well, mis-routes"** (Instruction's claim looked
plausible but the Routing axis was red both ways) — *good prose, wrong classifier*. The fix is the
wording, never the corpus or the threshold. After it: **SHIPPABLE**.

The lesson: a description is a routing classifier, not prose — you can't eyeball its precision and
recall. The eval doesn't *certify* a pass; it makes each miss and grab a **named phrase you read** —
and the truthful sibling fence repels, never magnetizes.
