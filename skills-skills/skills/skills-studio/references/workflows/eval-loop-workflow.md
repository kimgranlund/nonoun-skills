---
date: 2026-05-26
status: draft
version: "0.1.0"
type: workflow
key_question: >
  When asked to evaluate a skill, what is the default escalating loop the
  agent should follow — starting with a small triage and scaling up to a
  full multi-rubric scorecard only when the stakes warrant — so the
  evaluation matches the question being asked rather than maximising
  rubric coverage by reflex?
companion_documents:
  - ../SKILL.md
  - rubric-manifest.json
  - README.md
  - skills-authoring.md
  - evaluation-workflows.md
---

# Eval Loop Workflow — Start Small, Escalate As Warranted

## §What this is

This document defines the **default escalating workflow** the agent should follow when invoked to evaluate a skill. It is distinct from `../rubrics/evaluation-workflows.md` — that file is a _rubric_ for scoring other skills' eval workflows; this file is _this skill's own_ evaluation loop.

The skill's three modes (`rubric-select`, `deep-audit [rubric-name]`, `scorecard`) are the available **operations**. This workflow sequences them into a coherent loop with documented stop conditions and escalation triggers so the agent does not default to the largest possible audit by reflex.

The default failure mode the workflow prevents: **launching a full scorecard against ~20 rubrics for a skill that has a missing `## Invocation` section that a triage check would have caught in 90 seconds**. The scorecard burns context, time, and reviewer attention on detailed scoring of a skill that is structurally broken, when the right output was "fix the structural issue first, then scoring becomes meaningful."

The right pattern is the opposite of the default: **start small, escalate only when the smaller stage's output is genuinely insufficient for the question being asked**.

---

## §The five stages

Each stage produces specific output and ends at a specific decision point. The decision can be: stop (output is sufficient), escalate (run the next stage), or jump (skip ahead to a specific stage because the question requires it).

```
Stage 0 — Cold-read           (60-90 seconds)
  ↓
Stage 1 — Triage check        (5-10 minutes, single rubric)
  ↓
Stage 2 — Rubric selection    (5 minutes, rubric-select mode)
  ↓
Stage 3 — Targeted deep-audit (20 minutes per rubric, deep-audit mode)
  ↓
Stage 4 — Full scorecard      (60+ minutes, scorecard mode)
  ↓
Stage 5 — Action planning     (15 minutes)
```

The progression is the **default**. Direct entry to Stage 2, 3, or 4 is permitted when the user has explicitly asked for a specific mode or when prior context already supplied the earlier-stage output. The progression is what the agent does when no other instruction overrides it.

---

## §Stage 0 — Cold-read (60-90 seconds)

**Purpose**: orient on what the skill is, before deciding how to evaluate it.

**Action**: read the target skill's `SKILL.md` only. Not the references. Not the manifest. Just the SKILL.md.

**Output** (one paragraph to the user):

```
Target: {skill-name} v{version}
Domain: {what the skill does in one sentence}
Layer: {meta / authoring / pipeline / output / operations / etc.}
Stated audience: {who is supposed to invoke this}
Claimed mode: {what triggers it; what it produces}
Apparent maturity: {draft / stable / active iteration / abandoned}
```

**Decision at end of Stage 0**:

- Skill is missing or unreadable → stop, report; the eval cannot begin
- Skill is empty / placeholder → stop, report; nothing meaningful to evaluate
- Skill is readable → proceed to Stage 1

**What Stage 0 is NOT**: it is not a scoring step. No rubric is loaded yet. The cold-read produces orientation, not findings.

---

## §Stage 1 — Triage check (5-10 minutes, single rubric)

**Purpose**: a cheap structural sanity check that catches the obvious disqualifiers before scoring against multiple rubrics.

**Action**: run a single rubric — by default `../rubrics/skills-authoring.md` — in deep-audit mode. The skills-authoring rubric is the default triage because it covers the structural and meta-discipline dimensions (routing, invocation contract, layer fit, ingestion, decomposition, references, eval coverage) that every skill should pass regardless of domain. Alternative triage rubrics:

| If the skill is primarily... | Triage with |
| --- | --- |
| A general-purpose authoring skill | `../rubrics/skills-authoring.md` (default) |
| A harness / cold-start surface (AGENTS.md-shaped) | `../rubrics/harness-design.md` |
| A multi-agent orchestrator | `../rubrics/multi-agent-coordination.md` |
| A generative-UI producer | `../rubrics/generative-ui-reasoning.md` |
| A specification or PRD authoring tool | `../rubrics/spec-authoring.md` or `../rubrics/prd-authoring.md` |

**Output**: a Stage-1 scorecard for the chosen triage rubric, ranked into one of three buckets:

- **Pass** (no Critical findings, ≤2 Major): skill is structurally sound; proceed to Stage 2 to identify additional applicable rubrics.
- **Conditional Pass** (1 Critical or ≥3 Major): skill has fixable structural issues; surface them, ask the user whether to address before continuing, or escalate to Stage 2 if the user wants to know the full scope.
- **Fail** (2+ Critical or pervasive Major issues): skill is structurally broken; **STOP**, report findings, recommend fixes before further scoring. Scoring a broken skill against more rubrics compounds noise — every rubric finds the same underlying structural issue surfacing differently, which produces a scorecard that looks comprehensive but is actually one issue restated 20 times.

**Decision at end of Stage 1**:

- Fail → stop, report, recommend structural fixes
- Conditional Pass → ask user whether to address now or continue
- Pass → proceed to Stage 2

**What Stage 1 is NOT**: it is not the full audit. One rubric is explicitly insufficient coverage for skills being promoted to v1.0 or being integrated into pipelines; for those use cases Stage 1 is the pre-flight, not the destination.

---

## §Stage 2 — Rubric selection (5 minutes, rubric-select mode)

**Purpose**: identify which rubrics from the manifest apply to this specific skill's domain, layer, and purpose — before scoring against any of them.

**Action**: run the skill's `rubric-select` mode. Load `references/rubric-manifest.json`. For each rubric, apply the selection criteria:

- Does the rubric's `layer` field match the target skill's layer?
- Does the rubric's stated `key_question` apply to what the target skill does?
- Does the rubric's `primary_critic` have authority over this domain?

**Output**: an ordered list of applicable rubrics with one-sentence justification per:

```
Applicable rubrics for {skill-name}:
1. {rubric-A} — {why it applies}
2. {rubric-B} — {why it applies}
...
N. {rubric-N} — {why it applies}

Not applicable (and why excluded):
- {rubric-X} — {why excluded}
- {rubric-Y} — {why excluded}
```

The **order** matters. Highest-priority rubrics go first. Default priority order:

1. **Triage rubric** — already scored in Stage 1; include the score
2. **Layer-specific rubrics** — rubrics whose `layer` field exactly matches the target's
3. **Cross-cutting rubrics** — rubrics that apply across layers (security-and-scope-containment, observability-and-telemetry, context-engineering)
4. **Output-quality rubrics** — only if the skill produces a specific output type (generative-ui-reasoning, agents-ux-wireframing-ascii, composite-css-composition-discipline)

**Decision at end of Stage 2**:

- 0 applicable rubrics beyond triage → stop, report; Stage 1 is the complete audit
- 1-3 applicable rubrics → proceed to Stage 3 (targeted deep-audit on each)
- 4+ applicable rubrics → user-stake-driven decision (see §Depth-by- stakes below): proceed to Stage 3 on the top 3, or proceed to Stage 4 (full scorecard) for high-stakes use cases

**What Stage 2 is NOT**: it is not scoring. No dimension is rated. Stage 2 produces the list; Stages 3 and 4 produce the scores.

---

## §Stage 3 — Targeted deep-audit (20 minutes per rubric, deep-audit mode)

**Purpose**: score 1-3 high-priority rubrics in full per-dimension detail. The lens is depth, not coverage.

**Action**: run the skill's `deep-audit [rubric-name]` mode for each selected rubric. Per the skill's SKILL.md §Scoring Method, score each dimension with explicit evidence:

- **[gate] dimensions**: mechanical check; state the gate, inspect the skill, produce a binary or count-based outcome
- **[review] dimensions**: judgment criterion + cited evidence + 1-5 score with one-sentence justification

**Output per rubric**:

```
Rubric: {rubric-name} v{version}

[D1] [{gate|review}] {Dimension name}
Score: {1-5}
Evidence: {specific text or absence from the skill}
Finding: {Critical|Major|Minor|Noise|Pass}

[D2] ...
...

Subtotal: {sum}/{max} ({percentage})
Verdict: {one paragraph summary of where this rubric finds the skill
   strong vs weak}
```

**Decision at end of Stage 3**:

- Findings are sufficient to act on (the user can address them and re-run, or the answer to the original question is clear) → proceed to Stage 5 (action planning); skip Stage 4
- Findings reveal additional rubric exposure not surfaced in Stage 2 → return to Stage 2, re-select, then either run more deep-audits or proceed to Stage 4
- Stakes require comprehensive coverage and Stage 3 has covered only 1-3 of N applicable rubrics → proceed to Stage 4

**What Stage 3 is NOT**: it is not the same as Stage 4. Stage 3 is _targeted_ — selected rubrics, in depth. Stage 4 is _comprehensive_ — all applicable rubrics, in depth.

---

## §Stage 4 — Full scorecard (60+ minutes, scorecard mode)

**Purpose**: score the skill against all applicable rubrics comprehensively. The lens is coverage and produces the artifact for v1.0 promotion, post-incident review, or library-level health reporting.

**Action**: run the skill's `scorecard` mode. Load each applicable rubric file sequentially (per the SKILL.md guidance: do not load all at once). Score each rubric per the Stage-3 format. Produce the full scorecard summary per the SKILL.md Output Contract:

```
Skill: [skill name] v[version]
Rubrics applied: [list]
Scorecard:
| Rubric | Dim | Type | Score | Finding |
...
Top issues:
1. [Critical] [rubric] D[n]: [issue] — Recommended: [action]
2. [Major] [rubric] D[n]: [issue] — Recommended: [action]
...
Minimum score to address before v1.0: [list]
```

**Output additions** beyond the scorecard:

- **Coverage summary**: how many rubrics applied, how many dimensions scored, time invested
- **Confidence note**: where the agent had high confidence vs where the evidence was thin
- **Cross-rubric findings**: issues that appeared across multiple rubrics (these are usually the deepest structural issues)

**Decision at end of Stage 4**:

- Proceed to Stage 5 (action planning) — Stage 4 always feeds action planning; the scorecard itself is not the deliverable, the actions it produces are.

**What Stage 4 is NOT**: it is not the end of the loop. The scorecard without action planning is a document that gets filed and forgotten. Stage 5 is non-optional after Stage 4.

---

## §Stage 5 — Action planning (15 minutes)

**Purpose**: convert findings into prioritized actions with owners, time-boxes, and gate-vs-defer decisions. The eval loop's actual output is the action plan, not the scorecard.

**Action**: for each Critical and Major finding from Stage 3 or 4:

1. Name the specific action that addresses the finding
2. Assign an owner (the user, the skill's maintainer, a specific role)
3. Time-box the action (today / this week / this sprint / this quarter)
4. Decide gate-vs-defer:
   - **Gate**: action must complete before the next release / promotion / integration milestone
   - **Defer**: action is logged but does not block; revisit at next audit
5. Note dependencies between actions (some fixes unlock other fixes)

**Output**:

```
Action plan for {skill-name}:

GATES (block next release):
1. [Critical] {action} — Owner: {x} — Due: {date}
2. [Major]    {action} — Owner: {x} — Due: {date}
...

DEFERRED (logged, revisit at next audit):
3. [Major] {action} — Owner: {x} — Revisit: {date}
4. [Minor] {action} — Owner: {x} — Revisit: {date}
...

Next audit: {date or trigger condition}
```

**Decision at end of Stage 5**: the loop is complete. Report to user.

**What Stage 5 is NOT**: it is not implementation. The agent produces the plan; the user (or another skill) executes against it.

---

## §Stop conditions

Stop the loop early when any of these apply. Document the stop and the reason in the output so the user knows what was and wasn't evaluated.

| Stop condition | When it fires |
| --- | --- |
| **Cold-read empty** | Stage 0 reveals the skill is missing, unreadable, or a placeholder. Loop ends at Stage 0. |
| **Triage Fail** | Stage 1 produces 2+ Critical or pervasive Major findings. Fixing structural issues comes before further scoring; loop ends at Stage 1 with a fix-this-first report. |
| **Zero rubric exposure** | Stage 2 finds no applicable rubrics beyond the triage. Stage 1's output IS the complete audit; loop ends at Stage 2. |
| **Stage 3 sufficient** | Targeted deep-audit produces findings sufficient to act on; Stage 4 would not change the action plan. Skip to Stage 5. |
| **Time-box exhausted** | The agreed time for evaluation has been reached. Report state at whatever stage completed; do not start a new stage you cannot finish. |
| **Diminishing returns** | Stage 4 has covered N rubrics and the last 2 produced no new findings beyond what earlier rubrics surfaced. Stop, note coverage, proceed to Stage 5. |
| **User redirect** | User asks to stop, change focus, or jump to a different stage. Honor it. |

---

## §Escalation triggers

When the smaller stage's output is insufficient, the next stage is triggered. Common escalation conditions:

| Context | Escalation pattern |
| --- | --- |
| **Skill is being promoted to v1.0** | Run Stages 0-5 in full. Promotion is the highest-stakes use case; full scorecard + action plan is the bar. |
| **Recent production incident traced to this skill** | Run Stages 0-5 in full PLUS switch to **critique** mode for an adversarial pass (the 9-critic panel). The post-incident audit is the strictest. |
| **Pipeline integration in progress** | Run Stages 0-4. Stage 5 action planning happens jointly with the pipeline integration plan. Focus particularly on [gate] dimensions because pipeline failures cascade. |
| **Quarterly skill health check** | Run Stages 0-2 by default. Escalate to Stage 3 only on skills that scored Conditional Pass in Stage 1 or that have shipped significant changes since last audit. |
| **New skill triage (less than 30 days old, no production use)** | Stages 0-1 are usually sufficient. Stages 3-4 are premature for skills that have not yet accumulated the evidence to be scored meaningfully. |
| **Specific dimension question** ("does the skill pass the routing-accuracy gate?") | Jump directly to Stage 3 with the relevant single rubric. Do not run Stage 4 unless the user asks. |
| **Library-wide audit** | Run Stages 0-2 across every skill in the library, then Stages 3-4 only on outliers (skills that scored Conditional Pass or Fail in Stage 1, or whose Stage 2 surfaced unexpected rubric exposure). |
| **Pre-merge skill changes** | Run Stage 0-1 on the changed skill, plus Stage 3 on any rubrics whose dimensions the change affects. Full scorecard is usually overkill for incremental changes. |

---

## §Depth-by-stakes matrix

The right stage to stop at depends on the stakes of the answer. This table provides defaults; the user can always override.

| Use case | Default stop stage | Why |
| --- | --- | --- |
| Casual curiosity ("what's wrong with this skill?") | Stage 1 | Triage + single-paragraph findings is enough |
| New skill onboarding | Stage 1 | Same; let it accumulate evidence before deeper scoring |
| Quarterly health check | Stage 2 (with Stage 3 for outliers) | Coverage breadth, not per-skill depth |
| Pre-feature-release | Stage 3 | Targeted depth on the rubrics most affected by the change |
| Pre-v1.0 promotion | Stage 5 | Full scorecard + action plan; the highest-stakes use case |
| Post-incident audit | Stage 5 + adversarial | Stage 5 plus a **critique**-mode adversarial pass (9-critic panel) |
| Library-wide audit | Stage 2 across library, then Stage 4 on outliers | Breadth across library, depth on flagged skills |
| Specific dimension check | Stage 3 jump (single rubric) | Direct entry; no need to triage |
| Routing eval (does it activate?) | Stage 3 jump on `../rubrics/skills-authoring.md` D1 | Direct entry on the dimension that scores routing |

---

## §Direct-jump overrides (the three modes as entry points)

When the user invokes the skill with a specific mode, treat the mode as a direct-jump override. The workflow above is the default when no mode is specified; the modes are still available as direct entries.

| User invocation | Default action |
| --- | --- |
| `score this skill` (no mode named) | Run Stages 0-5 with default escalation triggers; stop at the stage matching the stakes-by-default table |
| `rubric-select for {skill}` | Jump to Stage 2. Skip Stages 0-1 only if the user has already given context, otherwise run Stage 0 to confirm orientation, then Stage 2. |
| `deep-audit {skill} against {rubric}` | Jump to Stage 3 with the named rubric. Skip Stage 1 only if the user is sure; otherwise run Stage 1 (quick) as pre-flight. |
| `full scorecard on {skill}` | Run Stages 0-5 in full (full scorecard is Stage 4 + Stage 5; Stages 0-2 prepare for it). |
| `triage {skill}` | Run Stages 0-1 only. Stop at Stage 1 regardless of findings unless user explicitly extends. |
| `health check on {skill}` | Run Stages 0-2. |
| `pre-v1.0 audit on {skill}` | Run Stages 0-5 in full + a **critique**-mode adversarial pass (9-critic panel). |

---

## §Anti-patterns

| Anti-pattern | Symptom | Correction |
| --- | --- | --- |
| **Default-to-largest** | Agent runs the full scorecard against 20 rubrics for every evaluation request, regardless of stakes. | Apply the depth-by-stakes matrix. Most evaluation requests stop before Stage 4. |
| **Skip-triage** | Agent runs Stage 2-4 against a skill with a missing `## Invocation` section. The scorecard surfaces 15 findings, all of which trace to the missing Invocation. | Triage always. Stage 1 is 5-10 minutes and prevents 60 minutes of compounding noise. |
| **Score-without-reading** | Agent loads a rubric and starts scoring without reading the target skill first. Scores are generic impressions, not evidence-cited findings. | Stage 0 cold-read is non-optional. The 90 seconds it takes prevents scoring from impression. |
| **Scorecard-without-actions** | Agent produces a scorecard, hands it to the user, ends the conversation. The scorecard becomes a document that gets filed and forgotten. | Stage 5 action planning is non-optional after Stage 4. The scorecard is the input to actions; actions are the deliverable. |
| **Single-rubric-as-comprehensive** | Agent runs Stage 1 only, then reports as if it is a comprehensive audit. The skill is being promoted to v1.0 on a single-rubric pass. | Match the stage to the stakes. Stage 1 is triage, not comprehensive audit. |
| **All-rubric-coverage** | Agent loads every rubric in the manifest because "more coverage is better." Context burns, time burns, output is unfocused. | Stage 2 applicability check explicitly excludes non-applicable rubrics. Loading non-applicable rubrics is waste. |
| **No-stop-conditions** | Agent runs every stage to completion regardless of intermediate findings. Stage 1 produced a triage Fail; agent continued to Stage 4 anyway and produced 15 findings, 13 of which trace to the Stage 1 issue. | Honor stop conditions. Triage Fail means STOP. Diminishing-returns means STOP. Time-box means STOP. |
| **No-cross-rubric-synthesis** | Agent runs Stage 4 against 8 rubrics, reports 40 dimension scores, but does not identify the 3 structural issues that appear across multiple rubrics. | Stage 4 output includes a cross-rubric findings section. Issues that appear in multiple rubrics are usually the load-bearing ones. |

---

## §Self-audit for the eval loop itself

Before reporting evaluation output, the agent runs this checklist:

- [ ] Did I run Stage 0 cold-read, or did I start scoring without reading the skill first?
- [ ] Did I run Stage 1 triage, or did I skip it and risk compounding structural issues across multiple rubric scores?
- [ ] Did I match the stop stage to the stakes (per the depth-by-stakes matrix), or did I default to the largest possible audit by reflex?
- [ ] Did I cite evidence for every score, or did I produce generic-impression scoring?
- [ ] Did I produce Stage 5 action planning, or did I stop at the scorecard?
- [ ] Did I name the stop condition (or completion at Stage 5) in the output so the user knows what was and wasn't evaluated?

If any item is unchecked, the evaluation is incomplete regardless of how many rubrics were scored.

---

## §Companion to the SKILL.md modes

The three modes in `SKILL.md` are the operations this workflow sequences:

| Mode | Corresponds to |
| --- | --- |
| `rubric-select` | Stage 2 of the workflow |
| `deep-audit [rubric-name]` | Stage 3 of the workflow (one rubric); also the implementation Stage 1 uses (single triage rubric) |
| `scorecard` | Stage 4 of the workflow |

Stages 0, 1, and 5 are not separate modes — they are workflow stages that wrap and sequence the modes. Stage 0 is reading; Stage 1 is deep-audit on a triage rubric; Stage 5 is action planning over the scorecard output.

The workflow does not replace the modes; it gives them an explicit sequence and decision points. A user who wants direct entry to a specific mode can still invoke it; the workflow is the default when no mode is specified.
