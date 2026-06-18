---
date: 2026-05-23
status: draft
version: "0.1.0"
---

# Harness Design — Best Practices Rubric

**The harness is the file an agent reads first.** Everything that follows — which skills activate, which rules apply, which tools are available — flows from what the harness contains and how it's structured. A poorly designed harness produces inconsistent agent behavior at scale; an over-designed harness drowns agents in irrelevant context before they've read anything useful.

**Companion docs:**

- `BORIS-feedback.md` §Boris's actual stated principles (B1, B2, B6)
- `skills-authoring.md` (this folder) — tiered surfacing model
- `SKILLS-best-practices.md §13` (chat-ui) — harness integration POV

---

## §The Problem

LLM agents are stateless at cold-start. The harness is the **persistent context** they load every session. It must answer four questions before the agent takes its first action:

1. **What is this environment?** (repo type, stack, conventions)
2. **What are the non-negotiable rules?** (hard rules that supersede model defaults)
3. **What capabilities exist?** (which skills, which tools, which modes)
4. **What verification is required?** (how does the agent know work is done?)

Without answers to these four, the agent improvises — and improvisation at scale produces drift, repeated errors, and skill bypasses.

---

## §First Principles

### 1. The harness is earned context, not accumulated context

Context has a cost: every line in AGENTS.md is loaded on every session. The test for any harness entry is not "is this true?" but "does an agent need this in the first 5 actions of a typical session?" If not, it belongs in a skill, a reference file, or the substrate.

### 2. Discoverability vs. compactness — both are real constraints

An agent who doesn't know a skill exists will improvise instead. An agent reading a 2000-line AGENTS.md will miss the 10 lines that matter. The tension is genuine; the solution is **tiered surfacing** (load-bearing rules inline → Tier 1 skills inline → Tier 2 via INDEX.md).

### 3. Hard rules must be falsifiable and bounded

A hard rule that says "be careful about database migrations" is advice, not a rule. A hard rule that says "never run `DROP TABLE` without explicit user confirmation, even when asked" is falsifiable, bounded, and enforceable. Hard rules accumulate; audit them for staleness.

### 4. The harness is the floor, not the ceiling

The harness sets minimums: minimum rules, minimum skill surface, minimum verification posture. Skills and references extend the floor on demand. The harness that tries to be the ceiling becomes the token-budget liability that caps agent quality.

### 5. Corrective feedback belongs in the harness (at the right tier)

Per Boris (howborisusesclaudecode.com): "Anytime we see Claude do something incorrectly we add it to the CLAUDE.md, so Claude knows not to do it next time." The discipline is real; the single-file approach works at small scale. At multi-agent/multi-consumer scale, the correction needs routing (see BORIS-feedback.md §B2 for the 3-tier promotion ladder).

---

## §The Rubric

### Dimension 1 — Structural clarity (cold-start readability) `[review]`

Does an agent reading the harness for the first time understand the environment within the first 30 lines?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Environment, stack, rules, and capability surface are all visible in the first screen. Each section is bounded and labeled. An agent can pick a skill within 5 actions. |
| **4 — Good** | Structure is clear but some context requires reading past the first screen. Agent can navigate but takes 8-10 actions. |
| **3 — Adequate** | Sections exist but ordering is by age of addition, not relevance. Hard rules buried after capability surface. |
| **2 — Poor** | No clear structure. Rules, descriptions, and examples mixed inline. Agent reads everything before understanding what it's doing. |
| **1 — Failing** | Harness is a wall of prose. No headings, no sections. Cold-start agent has no anchors. |

**Test**: paste the first 50 lines of AGENTS.md and ask: what type of repo is this? what are the 3 most important rules? what skills exist?

---

### Dimension 2 — Token economy (compactness) `[gate]`

Is every line earning its keep? Or is the harness a graveyard of outdated rules, stale project descriptions, and skills that nobody uses?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Each line answers at least one of the 4 cold-start questions. Dead rules pruned. Tier 1 skills only. Tier 2 delegated to INDEX.md with one-line pointer. |
| **4 — Good** | Some redundancy but nothing actively misleading. INDEX.md or equivalent manifest exists. |
| **3 — Adequate** | Several outdated entries but agent can filter. Total harness < 200 lines. |
| **2 — Poor** | 300-500 lines. Multiple stale rules. Agent spends significant context on irrelevant material. |
| **1 — Failing** | 500+ lines. No pruning ever happened. Harness contains full skill documentation inline. |

**Test**: run a line-count. Count lines per section. Flag any section > 50 lines for justification audit.

---

### Dimension 3 — Rule quality (hard rules that hold up) `[review]`

Are the hard rules specific, falsifiable, and bounded to real failure modes?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Each hard rule names the failure mode it prevents, is testable (the agent either did it or didn't), and has a traceable origin (incident, ticket, or principle). |
| **4 — Good** | Rules are specific and actionable but some lack origin tracing. No rules that are just good practice repeated from model defaults. |
| **3 — Adequate** | Mix of specific rules and vague guidance ("be careful about X"). Hard rules and soft guidelines not visually distinguished. |
| **2 — Poor** | Most "rules" are general LLM advice the model already knows. Rule count high but signal low. |
| **1 — Failing** | Hard rules contain contradictions, stale references, or instructions that apply only to past project states. |

**Test**: for each hard rule, ask: (a) could an agent check whether it was followed? (b) what incident does it prevent? If either answer is "unclear," the rule is underpowered.

---

### Dimension 4 — Skill surfacing (tiered discoverability) `[gate]`

Are the right skills visible at cold-start, and is the surfacing bounded?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Tier 1 (load-bearing senior skills) visible in harness with 1-row summary each. Pointer to INDEX.md or manifest for Tier 2. Harness skill section ≤ 50 lines. Any agent can use the right skill on the first try. |
| **4 — Good** | Tier 1 skills visible. INDEX.md exists. Some Tier 1 entries are slightly verbose (2-3 lines each vs 1) but still bounded. |
| **3 — Adequate** | All skills listed inline. No tiering. An agent sees all skills on every session regardless of relevance. Workable but noisy. |
| **2 — Poor** | No skill surfacing at all — agent must browse the skills directory manually. OR all skills inlined with full descriptions, producing a 500+ line harness. |
| **1 — Failing** | Skills listed but with stale names, wrong descriptions, or references to deleted files. Agent is actively misled. |

**Test**: count the skills section. If > 50 lines: identify which skills should be in INDEX.md. If < 10 lines: verify all Tier 1 skills are present.

---

### Dimension 5 — Verification posture (PEV binding) `[review]`

Does the harness make Plan→Execute→Verify the agent's default posture?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | PEV is a named principle in the harness. At least one hard rule explicitly requires verification before claiming work done. Verify targets cited per work type. |
| **4 — Good** | PEV referenced but not enforced as a hard rule. Agents who read the harness understand they should verify. |
| **3 — Adequate** | No explicit PEV mention but the hard rules imply it (e.g., "never commit without running tests"). Agents may or may not close the loop. |
| **2 — Poor** | No verification posture. Agents read the harness and receive no signal about when work is done. |
| **1 — Failing** | Harness actively discourages verification ("proceed immediately," "skip tests for speed"). |

**Test**: can you find an explicit statement in the harness about what constitutes "done" for the most common work type?

---

### Dimension 6 — Corrective feedback integration `[review]`

Does the harness reflect lessons learned from past agent errors?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Hard rules are traceable to incidents. A correction pipeline exists (however minimal — even one CLAUDE.md used consistently). Rules are dated or have version history. Stale rules are pruned. |
| **4 — Good** | ≥3 rules carry a parenthetical origin note (incident reference, date, or principle name). No rules are visibly stale (still reference conditions that no longer apply). No systematic pipeline but the correction discipline is observable from the text. |
| **3 — Adequate** | A few rules clearly came from incidents but most rules are generic. No tracking of when rules were added. |
| **2 — Poor** | Rules added but never reviewed. Multiple rules probably already violated and nobody noticed. |
| **1 — Failing** | Harness has never been updated after agent errors. The same mistakes recur session after session. |

**Test**: pick 3 hard rules. Ask "what does this prevent?" If the answer is obvious from the rule, that's a pass. If the answer requires reading a 2-year-old incident report that doesn't exist, that's a fail.

---

## §Anti-patterns

### AP-01 — Harness bloat (the graveyard accumulation)

**Symptom**: AGENTS.md grows by appending, never by pruning. Every new rule stacks. No rule ever graduates out or gets demoted. **Root cause**: Treating the harness as a changelog rather than a living specification. **Correction**: Audit quarterly. For each rule: is this still violated? is this still needed? Demote to per-skill reference if it's skill-specific.

### AP-02 — Dead rule syndrome

**Symptom**: Hard rules that reference deleted files, renamed tools, or project states that no longer exist. **Root cause**: Rules added for a specific incident, never revisited when the incident's context changed. **Correction**: Each hard rule should cite what it prevents. When the threat vector changes, update or remove the rule.

### AP-03 — Capability surface buried

**Symptom**: The agent has to read 300+ lines before encountering the skills it can use. **Root cause**: Structure by chronological addition, not by what agents need first. **Correction**: Reorder. Environment → Hard rules → Capability surface → Verification posture. Capabilities come BEFORE detailed environment context.

### AP-04 — Missing tier distinction

**Symptom**: All skills listed inline at equal weight. Agent treats a one-off utility skill the same as a load-bearing senior skill. **Root cause**: Skills added as discovered, without evaluating what belongs at cold-start. **Correction**: Apply the Tier 1 rubric (§13 of SKILLS-best-practices): cross-cutting + needed in first 5 actions + bypass-harm + extensible. Only those skills belong in the harness body.

### AP-05 — Solo-scale ceremony at team scale (or vice versa)

**Symptom A**: An individual's harness has a 3-tier skill surfacing model, INDEX.md, harness-currency audit, and §Teach-required rules for a 5-skill library. Pure overhead. **Symptom B**: A 15-agent, 50-skill project uses a single CLAUDE.md with no routing. Corrections conflict; skills bypass. **Root cause**: Applying Boris's vanilla posture at team scale, or vice versa. **Correction**: Per Boris's B6 and §13.8 of SKILLS-best-practices: scale the discipline to the problem. Solo workflows default to vanilla. Multi-agent / multi-consumer escalate only when the vanilla approach is demonstrably failing.

### AP-06 — No PEV binding

**Symptom**: Harness is purely instructional — it describes environment and rules but never describes when work is done. **Root cause**: Authors think the verify step is obvious and doesn't need stating. **Correction**: Add one explicit PEV statement. At minimum: "For every non-trivial task, state the verify target before executing. Don't claim done until the real product shows the right state."

---

## §Hard Tests

These are the questions to ask when reviewing a harness. If you can't answer them from the harness alone, the rubric score drops.

1. **The 5-action test**: can a cold-start agent understand what kind of repo this is, what the top 3 rules are, and which skill to use — in 5 actions or fewer?

2. **The 50-line test**: count the skill-surfacing section. If > 50 lines, which skills don't belong at Tier 1? The answer should be immediate.

3. **The stale rule test**: pick 3 hard rules. For each: what incident does it prevent? Is that incident still possible? Is the rule still worded for current project state?

4. **The verify test**: for the most common work type (authoring, releasing, reviewing — whatever this project does), is there an explicit statement of what "done" looks like?

5. **The Boris test**: if you showed this harness to someone who follows Boris's vanilla-setup discipline, would they immediately ask "why is all of this here?" If yes, you have unjustified ceremony.

6. **The new-agent test**: assume an agent has never worked in this repo. It reads only AGENTS.md. Does it know enough to do its first task correctly? Or does it need to read 4 other files first?

7. **The bloat-growth test**: is the harness longer than it was 90 days ago? If yes, did it get longer because the project genuinely needed more rules — or because nobody pruned old ones?
