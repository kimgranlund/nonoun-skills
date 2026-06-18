---
title: Expert Council Design (the critic panel a skill ships — personas, coverage, calibration)
key_question: Is the skill's panel of critics/personas a well-designed instrument — each voice grounded in verifiable authority, the set partitioning the space without redundancy, judgment-via-persona the right control mode, each persona's output falsifiable, and the panel proven to discriminate a *failing* artifact rather than only bless good ones?
layer: meta-evaluation
primary_critic: scott-wlaschin  # The panel is a type system over a judgment space — overlapping or uncovered critics are the illegal states
companion_rubrics:
  - rubric-quality                       # scores the *rubrics* a skill ships; this scores the *critic panel* it ships — the sibling instrument
  - multi-agent-coordination             # a council run as sub-agents is a coordination problem (coverage, isolation, synthesis)
  - prompt-control-modes                 # D3 here is the control-mode question (persona vs rubric) applied to a judgment panel
version: 0.1.0
status: empirically-derived
source: "Derived 2026-05-31 from the brand-studio re-review (skills-studio dogfood): the instrument could score the rubrics a skill ships but had no home for scoring the critic/persona panel it ships — a gap general to every council-bearing skill (brand-studio, core-agentic-ux-best-practices, skills-studio itself)."
---

# Expert Council Design (for skills whose output is expert judgment delivered through personas)

## What this rubric measures

Some skills don't just ship rubrics — they ship a **panel of critics/personas** that deliver expert judgment (a brand skill's 14 practitioner critics; an agentic-UX skill's 8-critic council; `skills-studio`'s own 9 engineering critics). This rubric scores whether that **panel is a well-designed instrument** rather than a roster of names: are the voices real, do they cover the space without overlap, is persona-judgment the right mechanism, is each voice falsifiable, and has the panel ever _failed_ an artifact (not just passed the good ones it was demoed on)?

The failure mode it defends against: **a panel that looks authoritative but is decorative** — invented voices with no traceable authority, overlapping or gap-ridden coverage, personas that emit vibes with no "what I will not do" boundary, and a council demonstrated only against artifacts chosen because they pass.

## Why this is its own rubric

`rubric-quality.md` scores the **rubrics** a skill ships (are _their_ criteria labeled, calibrated, falsifiable). This scores the **critic panel** a skill ships — a different artifact with different failure modes. A skill can have well-labeled rubrics _and_ a decorative council, or vice versa. For a skill whose deliverable is **expert judgment through personas**, the panel is the load-bearing instrument and needs its own audit.

## 5 scoring dimensions

| # | Dimension | Type | Question |
| --- | --- | --- | --- |
| **C1** | Authority grounding | review | Does each persona trace to **verifiable** real-world authority — a named practitioner / school / body of work — with cited primary sources and reusable specifics, or is it an invented "wise voice"? A persona with no source is a costume. |
| **C2** | Non-redundancy & coverage | gate | Is there an explicit **coverage map** — each part of the judged space assigned to a critic, each role mapped to who reviews it — and do the critics **partition** the space rather than overlap? Two critics with the same lens is mass; an unowned region is a blind spot. (Mechanizable: the map exists and every role/dimension has ≥1 owner and no dimension has 3+ near-identical owners.) |
| **C3** | Control-mode fitness | review | Is **judgment-via-persona** the right control mode for this space (genuinely high-entropy, taste-dependent judgment) — or would a labeled rubric per lens be more reproducible? Personas earn their keep where the call is irreducibly expert; they are over-engineering where a checklist would converge. |
| **C4** | Falsifiable persona output | gate | Does each persona ship a **"what I will not do" boundary** _and_ a self-check that its critique must be **evidence-cited, not vibes** (quote the artifact, name the failure)? A critic that can't be wrong isn't a critic. (Mechanizable: grep each persona file for a stated boundary + an evidence-citation requirement.) |
| **C5** | Calibration — does the panel discriminate? | hypothesis | Has the council been run against a **failing** artifact and shown to _fail_ it — not only against hand-picked exemplars it blesses? A panel demonstrated only on artifacts chosen because they're excellent proves it can _validate_, never that it can _discriminate_. Measurement plan: one negative exemplar that the panel correctly marks down + one inter-rater check (two runs converge). |

**Gate dimensions** (C2, C4) — mechanically inspectable: the coverage map exists and partitions cleanly; every persona file carries a boundary + an evidence requirement. **Review** (C1, C3) — judgment: is the authority real, is persona the right mode. **Hypothesis** (C5) — the calibration claim is unproven until the panel is run against a failing case; label it `[hypothesis]` until that exemplar + inter-rater record exist.

## 5 named anti-patterns

- **AP-EC-01 — Costume critic.** A persona with an authoritative name but no traceable source, no cited work, no reusable specifics — a generic "wise reviewer" wearing a face. (Fails C1.)
- **AP-EC-02 — Overlapping lenses.** Three critics who all make the same point; the panel feels big but covers little. (Fails C2.)
- **AP-EC-03 — Unowned region.** A part of the judged space (a dimension, a stakeholder, a failure mode) no critic owns — the panel's blind spot, invisible because nothing flags it. (Fails C2.)
- **AP-EC-04 — Persona theater.** Personas with strong voice but no "won't do" boundary and no evidence requirement — they emit confident vibes that can't be checked or refuted. (Fails C4.)
- **AP-EC-05 — Demo-only calibration.** The council is only ever shown on artifacts picked because they pass; it has never failed one, so "it works" is unfalsified. (Fails C5 — the most common and most invisible.)

## 5 hard tests

1. **Source trace (C1):** pick three personas; for each, follow it to a named real-world authority + a cited work. Any that resolve to "an invented voice" fail C1.
2. **Coverage hunt (C2):** find the coverage/role map. Is every judged region owned exactly once? Name an unowned region and the most-overlapping pair.
3. **Mode test (C3):** pick the panel's most reproducible lens. Would a labeled rubric give the same verdict more consistently than the persona? If yes, that lens is persona-theater over a checklist.
4. **Refutation test (C4):** take one persona's output. Could a defender refute it with evidence, or is it unfalsifiable? Does the persona's own file demand it cite the artifact?
5. **Discrimination test (C5):** find the worst artifact the skill ships or can construct. Run the panel. Does it _fail_ it at full strength — or does the council soften, the way it never does on the demo exemplar?

## Operating procedure (when scoring)

1. Locate the panel and its coverage/role map (if none exists, C2 fails immediately — start there).
2. Run the two gate tests first (coverage hunt, refutation/boundary grep) — fast, and they catch the structural failures.
3. Score C1/C3 with cited evidence from the persona files.
4. For C5, look for a negative exemplar in the skill's own examples; its absence is the `[hypothesis]` flag — the panel's discrimination is unproven, not disproven.
5. Note explicitly whether the panel **validates** (passes good artifacts) vs **discriminates** (also fails bad ones) — that distinction is the rubric's headline.
