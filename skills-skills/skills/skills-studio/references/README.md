---
date: 2026-05-31
status: draft
version: "0.2.0"
---

# Best Practices — Planning Document and Index

This folder contains rubrics for the emerging discipline of **agentic coding systems** — the skills, harnesses, context engineering, and tool interfaces that make AI coding agents reliable, extensible, and maintainable at scale.

**Purpose**: Build rubrics that are defensible in reviews with the sharpest critics in the industry — Boris Cherny (Head of Claude Code, pragmatic-engineer empiricist), Steve Yegge (platform-thinking veteran, Stevey's Platform Rant lineage), and Elon Musk (first-principles, delete-first manufacturing discipline). If a rubric can't survive their adversarial evaluation, it isn't earning its keep.

**Parent document**: `../BORIS-feedback.md` — the architectural review that shaped the senior skill ecosystem. The best-practices rubrics in this folder extend that review into the adjacent disciplines not covered there — now **25 rubrics** over a theory layer of **11 foundations**.

---

## Status: draft, N=0 empirical applications

**These rubrics have not been applied to any real project.** Every dimension, score description, and anti-pattern was written before any rubric was run against a real artifact. Per the evaluation-workflows rubric's own anti-pattern: this is spec-before-prototype.

The right order: apply → observe → revise → graduate. Until N≥3 applications per rubric, treat every claim here as a falsifiable hypothesis, not a validated practice. The graduation criteria below define what "validated" requires.

---

## The quality bar

A rubric here must:

1. **Name the failure modes**, not just the success criteria. A rubric that only describes success is documentation; a rubric that names what breaks and why is engineering.
2. **Be falsifiable**. Every dimension should yield a clear pass/fail or score against real artifacts. Vague guidance ("be clear and concise") is not a rubric.
3. **Cite grounded sources**. Boris Cherny (primary sources: howborisusesclaudecode.com, Pragmatic Engineer 2026, Lenny's podcast), Anthropic official docs, real production patterns. No invented credibility.
4. **Resist over-engineering**. Per Boris's B6 principle: vanilla > customization. Ceremony added before the pain demands it is a future maintenance liability.
5. **Include eval prompts** that agents impersonating the named engineers can run to surface real weaknesses. These are in `critics/eval-prompts.md` (the **critique** mode corpus).

---

## Rubrics in this folder

**25 rubrics.** `skills-holistic.md` is the meta-rubric; every other rubric is a drill-down for one of its concerns.

### Meta

| File | Topic | Key question |
| --- | --- | --- |
| `skills-holistic.md` | Holistic Skill Quality | Does this skill address all ten load-bearing dimensions (D1 instructions · D2 control mode · D3 rubric quality · D4 mechanization · D5 evaluation · D6 extensibility · D7 security · D8 observability · D9 context engineering · D10 plan anatomy)? |

### System design / authoring

| File | Topic | Key question |
| --- | --- | --- |
| `harness-design.md` | Harness Design | What belongs in AGENTS.md, and what does bloat look like? |
| `agentic-coding.md` | Agentic Coding | Does this system close the Plan→Execute→Verify loop reliably? |
| `context-engineering.md` | Context Engineering | Is context a precision instrument or a dumping ground? |
| `progressive-context-construction.md` | Progressive Context Construction | Does context grow with the task, or arrive fully-formed as noise? |
| `skills-authoring.md` | Skills Authoring | Does this skill compound over invocations, or accumulate drift? |
| `tool-use.md` | Tool Use | Are tools contracts with clear success criteria, or guesses with side effects? |
| `prompt-control-modes.md` | Prompt Control Modes | Does the control mode match the task's entropy, risk, and desired autonomy? |

### Execution quality

| File | Topic | Key question |
| --- | --- | --- |
| `evaluation-workflows.md` | Evaluation & Validation | Are systems tested adversarially with fresh context, or self-confirmed by their builders? |
| `inversion-and-abstraction.md` | Inversion & Proper Abstraction | Is the agent deciding and observing, or manually executing what a script should do? |
| `mechanization-best-practices.md` | Mechanization | Are repeatable, failure-prone procedures moved out of prose into mechanisms at the right enforcement level? |
| `skill-extensibility.md` | Skill Extensibility | Does the skill learn from evidence without bloating the cold-start surface? |
| `plan-anatomy.md` | Plan Anatomy | Are plans well-structured bridges from intent to reliable execution, or vague sequences the model improvises through? |

### Rubric & orientation quality

| File | Topic | Key question |
| --- | --- | --- |
| `rubric-quality.md` | Rubric Quality | Are quality criteria labeled, calibrated, and falsifiable — or asserted as untested fact? |
| `cold-start-orientation.md` | Cold-Start Orientation | Can a user orient in under 60 seconds (Quick Start, worked example, inline concept definitions)? |

### Output / Generative UI

| File | Topic | Key question |
| --- | --- | --- |
| `generative-ui-reasoning.md` | Generative UI Reasoning | Does the agent reason top-down from intent to decision before emitting components, or prematurely render? |
| `agents-ux-wireframing-ascii.md` | ASCII Wireframing | Does the agent produce a structural wireframe between intent and implementation, or collapse prompt→polished components? |
| `composite-css-composition-discipline.md` | CSS Composition Discipline | When composing UI from primitives + composites, does the agent respect layered @scope contracts or silently break child layout? |

### Product & spec authoring

| File | Topic | Key question |
| --- | --- | --- |
| `prd-authoring.md` | PRD Authoring | Does the PRD establish shared product intent without collapsing into a disguised implementation plan? |
| `spec-authoring.md` | Spec Authoring | Does the SPEC define an execution contract bounded enough for a coding agent to implement, verify, and stop safely? |

### Operations and safety

| File | Topic | Key question |
| --- | --- | --- |
| `multi-agent-coordination.md` | Multi-Agent Coordination | Is agent isolation structural or behavioral — and what happens when the behavioral contracts break? |
| `worktree-operations.md` | Worktree Operations | Is multi-agent Git/worktree state typed and bounded, or ambiguous and merge-resolved? |
| `observability-and-telemetry.md` | Observability & Telemetry | Can you answer the 5-minute test from telemetry, or is all analysis anecdotal? |
| `security-and-scope-containment.md` | Security & Scope Containment | Does agent privilege match task scope, or does capability exceed authorization? |
| `governance.md` | Governance | Does the system have explicit change control, audit trails, and policy-as-code — or govern by whoever-happened-to-make-the-change? |

### Field reference

| File | Purpose |
| --- | --- |
| `failure-mode-taxonomy.md` | Cross-cutting symptom index: production failure → root cause → rubric section. The debugging entry point for all rubrics. |

## Foundations (the theory layer)

Each rubric is the _scoring_ layer; its _theory_ lives in a paired research-grounded doc under `foundations/` (core claim, failure modes, primary sources). The pairing is **1:1 and machine-checked** — `rubric-manifest.json` carries a `foundation` field on each paired rubric, and `scripts/check-foundations-coverage.py` gates that **every `foundations/*.md` is claimed by exactly one rubric** (run it in CI via the repo-root `scripts/run-skill-gates.py`).

| Foundation (`foundations/`) | Rubric (`rubrics/`) | Holistic dim |
| --- | --- | --- |
| `instructions-harness-foundations.md` | `harness-design.md` | D1 |
| `control-mode-foundations.md` | `prompt-control-modes.md` | D2 |
| `rubric-foundations.md` | `rubric-quality.md` | D3 |
| `mechanization-foundations.md` | `mechanization-best-practices.md` | D4 |
| `eval-foundations.md` | `evaluation-workflows.md` | D5 |
| `extensibility-foundations.md` | `skill-extensibility.md` | D6 |
| `security-foundations.md` | `security-and-scope-containment.md` | D7 |
| `observability-foundations.md` | `observability-and-telemetry.md` | D8 |
| `context-engineering-foundations.md` | `context-engineering.md` | D9 |
| `governance-foundations.md` | `governance.md` | — (cross-cutting, team/system scale) |
| `plan-anatomy-foundations.md` | `plan-anatomy.md` | D10 |

The ten holistic dimensions each map to one foundation↔rubric pair (**D9 Context Engineering** and **D10 Plan Anatomy** were promoted into the holistic rubric in `skills-holistic` v0.2.0). **Governance** stays cross-cutting — it is a team/system concern, not a per-skill dimension (see `skills-holistic.md` §Scope). Application / composite rubrics (skills-holistic, agentic-coding, gen-ui, css, prd/spec, multi-agent, worktree, cold-start, inversion, progressive-context, skills-authoring, tool-use) have **no dedicated foundation** by design — they compose or apply the theory rather than introduce new theory.

### Dimension scoring convention

Each rubric dimension is tagged with its scoring type. These tags are defined in `rubric-manifest.json`:

| Tag | Meaning |
| --- | --- |
| `[gate]` | Scoreable mechanically — routing F1, pass/fail, counts, linter output. Can be an automated CI check. |
| `[review]` | Requires expert human judgment — quality of verify target, inversion completeness, discoverability. |
| `[hypothesis]` | Stated as an observable property but not yet empirically verified. Track with real data before treating as a fact. |

Only skills-authoring.md is fully labeled as the reference exemplar. Other rubrics should adopt these tags as they are applied to real systems.

### Machine-readable registry

`rubric-manifest.json` — machine-parseable registry of all 25 rubrics with version, layer, primary critic, dimension count, minimum scale, dependency graph, and the `foundation` link to each rubric's theory doc. Systems adopting these rubrics can declare adoption and scores in the format documented there. `scripts/check-foundations-coverage.py` gates the foundation↔rubric coverage.

### Adversarial evals (critique mode)

| File | Purpose |
| --- | --- |
| `critics/eval-prompts.md` | Entry file for **critique** mode: 9-critic roster (Boris Cherny, Steve Yegge, Elon Musk, Charity Majors, Andrej Karpathy, Simon Willison, Scott Wlaschin, Chip Huyen, David Farley), topical sections, synthesis prompts (S1–S11), scoring rubric |
| `critics/eval-as-[name].md` | One persona file per critic — load the named one for `single-critic`, all nine for `full-panel` |

---

## Graduation criterion

These rubrics are in **draft** status (version 0.x). Promotion to `stable` (v1.0.0) requires:

1. Each rubric applied to ≥3 real projects or artifacts — not theoretical
2. The rubric's failure modes caught ≥1 real problem in each application
3. The eval prompts reviewed by at least one person with engineering seniority
4. No dimension that cannot be applied mechanically (no purely vibes-based scoring)

Current status: N=0 empirical applications.

---

## How this folder relates to existing docs

- `../../chat-ui/.agents/skills/SKILLS-best-practices.md` — the practitioner's checklist (senior vs standalone, §Teach, §SelfAudit, harness integration). These rubrics are the **scoring layer** above that checklist: not just "here's how to do it" but "here's how to measure whether you did it well."

- `../BORIS-feedback.md` — the architectural review of the skills ecosystem. These rubrics are the generalization of that review's methodology, now spanning 25 rubrics across authoring, execution, output, product/spec, and operations/safety layers, over a theory layer of 11 foundations.

- `skills-authoring.md` — the rubric here is the universal version of the chat-ui SKILLS-best-practices doc, applicable across any agent skill system.

---

## Authoring a new rubric

Structure each rubric with:

```
§The Problem — why this rubric exists; what breaks without it
§First Principles — 3-5 grounded principles, not platitudes
§The Rubric — scored dimensions with explicit pass/fail criteria
§Anti-patterns — concrete failure modes with symptoms and root cause
§Hard Tests — questions to ask when reviewing; the Boris/Elon tests
```

The eval prompts live in `critics/eval-prompts.md`, not inline in each rubric, so they can be read as a coherent adversarial corpus.
