---
name: research-survey
description: >
  Systematic research-survey and optimization skill. Use this skill whenever the user wants to
  investigate, optimize, debug, stress-test, or understand a system — regardless of domain.
  Triggers include phrases like: "research-survey this", "optimize", "figure out why", "what broke",
  "find the root cause", "improve the score", "tune these parameters", "what happens if we remove",
  "stress test", "find edge cases", "break this", "what's the best value for", "hill climb",
  "ablation study", "sweep", "bisect", "adversarial probe", or any request to systematically
  explore, measure, or improve something. Also triggers when the user describes a problem that
  implies one of the six techniques (e.g., "it used to work but now it doesn't" → bisect;
  "which of these settings matter?" → ablation). Works across all domains: code, configuration,
  prompts, design, writing, data pipelines, infrastructure, ML models, or any measurable system.
---

# Research — Systematic Investigation Skill

Select and execute the right research-survey technique for the problem at hand. Six techniques are
available, each suited to a different class of question. The skill auto-selects based on
problem analysis, confirms with the user, then executes — and can chain techniques when the
output of one naturally feeds the next.


## Invocation

This is a **research-survey** skill. The user wants to investigate, optimize, debug, or understand a system. Decompose: (1) scope the question, (2) choose research-survey method, (3) execute, (4) synthesize.

### Step 1 — Ingestion

Classify the ask surface:
- "Investigate X" → open-ended; needs scoping and hypothesis framing
- "Optimize Y" → bounded; needs baseline measurement then intervention
- "Debug Z" → symptom-driven; needs causal tracing
- "Understand W" → knowledge gap; needs structured literature review

### Step 2 — Decomposition

| Method | When to use |
|---|---|
| Literature review | Survey existing solutions; identify precedent and anti-precedent |
| Controlled experiment | Baseline → intervention → measurement; statistical significance |
| Causal tracing | Follow the error chain from symptom to root cause |
| Benchmarking | Compare alternatives under equal conditions |
| Adversarial analysis | Challenge assumptions; look for failure modes |

### Step 3 — Execution routing

Research outputs vary by method: literature reviews produce annotated bibliographies; experiments produce measurements with confidence intervals; debug traces produce root-cause analyses. Every output must be falsifiable — if the user can't check your conclusion, it's not research-survey.


## Technique Reference Files

Each technique's full protocol lives in `references/`. Read the relevant file before executing.

| Technique    | File                          | Read when selected |
|-------------|-------------------------------|-------------------|
| Autoresearch | `references/autoresearch.md` | Iterative single-change optimization |
| Ablation     | `references/ablation.md`     | Contribution measurement by removal |
| Bisect       | `references/bisect.md`       | Binary search for root cause |
| Adversarial  | `references/adversarial.md`  | Failure-mode discovery |
| Hill Climb   | `references/hill-climb.md`   | Exhaustive neighborhood search |
| Sweep        | `references/sweep.md`        | Parameter-space mapping |

---

## Step 1: Problem Analysis

Before selecting a technique, decompose the user's request into three elements:

1. **What is the system?** — The thing being researched (code, config, prompt, model, process, etc.)
2. **What is the question?** — What the user actually wants to know or achieve.
3. **What is the measurability?** — How can progress or results be quantified? If there's no
   obvious scorer, work with the user to define one before proceeding.

## Step 2: Technique Selection (Decision Matrix)

Match the user's question to a technique using this matrix. The core discriminator is the
**type of question** being asked:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RESEARCH TECHNIQUE SELECTOR                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  "What broke? When did it start?"                                   │
│  → BISECT (binary search for root cause)                            │
│    Signal: regression, "used to work", diff between good/bad state  │
│                                                                     │
│  "How do I improve this?"                                           │
│  → AUTORESEARCH (iterative single-change optimization)              │
│    Signal: a score to improve, known weaknesses, fix-one-at-a-time  │
│                                                                     │
│  "What's the best combination of changes?"                          │
│  → HILL CLIMB (try all neighbors, pick the winner)                  │
│    Signal: multiple viable alternatives, need the best of N options │
│                                                                     │
│  "Which parts actually matter?"                                     │
│  → ABLATION (remove components, measure contribution)               │
│    Signal: complex system, want to simplify, unsure what's pulling  │
│    its weight                                                       │
│                                                                     │
│  "What's the optimal value for X?"                                  │
│  → SWEEP (systematic parameter exploration)                         │
│    Signal: tunable knobs, numeric ranges, sensitivity analysis      │
│                                                                     │
│  "What breaks this? Where are the edge cases?"                      │
│  → ADVERSARIAL (attack the system, find failure modes)              │
│    Signal: robustness check, stress test, security audit, QA        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Disambiguation Rules

When the question could map to multiple techniques:

- **"Improve" + known weak point** → Autoresearch (targeted fix loop)
- **"Improve" + no clear weak point** → Hill Climb (explore alternatives)
- **"Improve" + numeric knob** → Sweep (map the landscape first)
- **"Why is this broken" + known-good prior state** → Bisect
- **"Why is this broken" + no prior state** → Adversarial (find what's fragile)
- **"Simplify this" or "what can I remove"** → Ablation
- **"Is this robust enough"** → Adversarial

### Confidence Check

If the match is ambiguous, present the top 2 candidates to the user with a one-sentence
rationale for each. Let them choose. Don't guess on a coin flip.

## Step 3: Confirm with User

Before executing, present:

```
Technique: {name}
Rationale: {one sentence why this fits}
System: {what we're researching}
Scorer: {how we'll measure — or "TBD, need to define"}
```

Wait for user confirmation. If they disagree, present alternatives.

## Step 4: Execute

Read the selected technique's reference file from `references/` and follow its protocol.
Every technique shares this structure:

1. **Phase -1: Research** — Use web search to gather domain knowledge before starting.
2. **Phase 0: Baseline** — Establish the starting point and measurement method.
3. **Phase 1: Loop** — Execute the technique's core iteration.
4. **Phase 2: Report** — Summarize findings, decisions, and recommendations.

## Step 5: Chain (When Logical)

After a technique completes, evaluate whether a follow-up technique is warranted.
Common chains:

| Completed      | Natural Follow-up | When                                              |
|---------------|-------------------|---------------------------------------------------|
| Bisect        | Autoresearch      | Found the root cause, now fix and improve          |
| Ablation      | Autoresearch      | Removed dead weight, now optimize what remains     |
| Adversarial   | Autoresearch      | Found failure modes, now harden iteratively        |
| Sweep         | Hill Climb        | Found the promising region, now fine-tune          |
| Hill Climb    | Adversarial       | Reached local optimum, now stress-test it          |
| Autoresearch  | Adversarial       | Optimized the score, now verify robustness         |

If a chain is appropriate, suggest it:

```
Research complete. Based on the results, a follow-up {technique} would help
because {reason}. Want to continue?
```

Only chain if the user confirms. Never auto-chain without consent.

---

## Principles

These apply across all techniques:

- **Measure everything** — No change is "obviously" good. Score before and after.
- **One variable at a time** — Isolate changes to attribute cause. Batching obscures signal.
- **Revert on regression** — If a change makes things worse, undo it immediately.
- **Log the journey** — Every round's decision, score delta, and rationale gets recorded.
- **Research before guessing** — When stuck, search for how others solved the same class of problem. External knowledge beats random attempts.
- **Stop when stuck** — Repeated failures mean the approach needs rethinking, not more rounds.
- **Define the scorer early** — If you can't measure it, you can't research-survey it. Work with the user to establish a scoring method before entering any loop.
