---
date: 2026-05-23
status: draft
version: "0.1.0"
---

# Inversion and Proper Abstraction — Best Practices Rubric

**The most expensive thing in an agentic system is unnecessary work.** Unnecessary work includes: tokens spent on prose the agent is supposed to manually execute step-by-step (instead of a one-line script citation), tokens spent loading knowledge the agent doesn't need (instead of on-demand references), and tokens spent on an over-abstract wrapper that adds indirection without adding value.

**Inversion** is the design principle that the skill tells the agent _which tool and when_ — not _how to manually execute the work the tool does_. The agent's job is decision-making (which mode? which command?) and observation (did the gate pass?). Not procedure execution.

**Proper abstraction** is knowing when an abstraction reduces complexity vs. when it adds it: the right abstraction makes the N+1 invocation faster than the Nth; the wrong abstraction makes every invocation slower because the agent must reason through additional indirection.

**Dynamic tool creation** extends inversion: instead of writing procedural prose that the agent executes, create the tool at the moment the procedure is proven reusable. The script becomes the abstraction; the skill cites it.

This rubric is concerned with the **economy of agent work** — every token is a real cost, every manual procedure step is a variance source, every unnecessary abstraction layer is debt.

**Companion docs:**

- `skills-authoring.md` (this folder) — Dimension 3 (inversion quality) is the skills-specific scoring
- `context-engineering.md` (this folder) — minimum effective dose principle
- `tool-use.md` (this folder) — tool contracts as the natural landing for inverted procedures

---

## §The Problem

Agent systems accumulate two opposing pathologies over time:

**Under-inversion** (the manual-execution trap): procedures that should be mechanized stay as prose. The agent reads a 12-step procedure, executes each step manually, introduces variance at every step, and produces results that depend on how well it interpreted the prose. The same procedure executed by `scripts/bump.mjs` would be deterministic, auditable, and 10x faster.

**Over-abstraction** (the indirection trap): every capability is wrapped in a skill, every skill is wrapped in a meta-skill, every concrete tool reference is hidden behind a three-layer abstraction. The agent must navigate the abstraction pyramid before reaching the action. Tokens spent navigating abstractions are tokens not spent on the task.

Both pathologies waste tokens, introduce variance, and slow down agent work. The discipline is finding the right abstraction level for each capability: concrete enough to be direct, abstract enough to be reusable.

---

## §First Principles

### 1. The inversion principle: cite commands, don't describe procedures

From SKILLS-best-practices §1 (Inversion): the LLM does NOT reason through what `bump.mjs` does internally. It reads the citation, runs the command, oversees the result. The script is the SoT for _how_; the skill is the SoT for _when + which_.

Every time a skill says "to do X, open file Y, find field Z, change it to..." — that is mechanize-bait. The procedure is repeatable, has clear pass/fail, and has silent failure modes. Those are the three signals that a script should exist. Write the script; cite the script; retire the prose.

### 2. The mechanize threshold: 3-strike rule

From SKILLS-best-practices §1 (Boris B7): _"I tallied code review issues in spreadsheets, then wrote lint rules when patterns hit 3-4 occurrences."_ The same discipline applies here.

A procedure earns a script when it meets **any three** of:

- Repeated across 3+ invocation cycles (pattern)
- Has a clear success/failure criterion (testable)
- Has silent failure modes the agent won't notice (dangerous prose)
- Has a destructive blast radius if wrong (high stakes)
- Involves multi-step orchestration with checkpoints (complexity)

A procedure that meets only one criterion is still prose-worthy. A procedure that meets three or more is mechanize-bait. Write the script.

### 3. Abstraction value is measured in compounding, not cleverness

An abstraction earns its keep if the N+1th invocation of the abstracted capability is demonstrably faster than the Nth. If the abstraction requires the agent to reason through the layer's logic every time (because the layer itself has logic), it adds latency without adding speed. The test for an abstraction: after 10 invocations, is it faster or slower than direct access would have been?

### 4. Dynamic tool creation: scripts emerge from usage, not design

Tools should not be designed in advance for hypothetical future cases. They should emerge from observed repeated procedures. The lifecycle:

1. Procedure written as prose in a skill
2. Same procedure repeated in 3+ invocations (3-strike threshold)
3. Script authored to replace the prose
4. Skill updated to cite the script (`scripts/X.mjs --flag`) instead of describing the steps
5. Prose deleted

This is "dynamic" in the sense that the tool materializes from observed need — not from a pre-designed tool taxonomy. Tool taxonomies designed in advance are almost always wrong; tools that emerge from observed procedures are almost always right.

### 5. Token economy is a design constraint, not an optimization

A skill that loads 3 reference files to answer a 2-line question is not "comprehensive" — it is wasteful. Token economy is a first-class design constraint: every token loaded into context is a token that competes with the task. The relevant question is not "does this reference contain relevant information?" but "is this reference necessary for the agent to complete the current task?"

The minimum effective dose of context beats exhaustive context. At the skill level: the minimum effective dose of prose beats exhaustive documentation. The relevant test is not size — it is necessity.

### 6. Abstractions must be transparent to the agent, not just to the author

An abstraction designed by the skill's author can encode assumptions the author understands implicitly. The agent reading the abstraction has no such background. The test: can the agent invoke the abstraction correctly without reading the implementation? If the agent must read the script to understand what `scripts/bump.mjs --from X --to Y` does, the abstraction isn't complete — the `--help` output and the skill's citation are together insufficient.

The rule: every script citation in a skill must be self-sufficient. The agent reads the citation and knows: (a) what the script does in one sentence, (b) the required arguments and their meaning, (c) the expected output on success, (d) the expected output on failure.

---

## §The Rubric

### Dimension 1 [gate] — Mechanization coverage (prose → script ratio)

How much of what agents are asked to manually execute has been mechanized?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every procedure that meets the 3-strike threshold exists as a script. All scripts have `--help` (SoT for behavior), `--json` (machine consumption), `--strict` (CI gate). Skill cites scripts by command; prose describes only judgment-requiring steps. Mechanize-bait count per mode: 0. |
| **4 — Good** | High-stakes and frequently-repeated procedures are mechanized. Some medium-frequency procedures still as prose. Scripts have `--help`; not all have `--json` or `--strict`. |
| **3 — Adequate** | At least one script exists per senior skill. Most multi-step procedures are still prose. Scripts are inconsistently documented. |
| **2 — Poor** | Scripts exist for some operations but were added reactively (after a failure), not proactively from the 3-strike rule. Many mechanize-bait procedures remain as prose. |
| **1 — Failing** | No scripts. Every mode is a list of manual steps. The agent is the interpreter of step-by-step instructions on every invocation. |

**Test**: for the most-used mode in the most senior skill, count the steps the agent is expected to manually execute. Each step that is (a) repeated, (b) testable, or (c) has a silent failure mode is a mechanization gap.

---

### Dimension 2 [gate] — Script interface quality (--help, --json, --strict)

Are scripts self-documenting contracts, or black boxes the agent must reason about?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every script: `--help` is the complete behavioral spec (skill.md doesn't duplicate it); `--json` outputs machine-parseable results; `--strict` exits 1 on any finding for CI gating; no behavior documented only in prose outside the script. |
| **4 — Good** | `--help` exists and is accurate. `--json` and `--strict` present for most scripts. A few scripts have undocumented behavior the agent must infer from context. |
| **3 — Adequate** | `--help` is present but terse. JSON output ad-hoc. Agent can use the script but may misinterpret edge-case output. |
| **2 — Poor** | Scripts exist but have no `--help`. Documentation lives only in SKILL.md prose (which will drift). Agent must read the script source to understand behavior. |
| **1 — Failing** | Scripts are undocumented. Neither the script nor the skill explains what success looks like. Agent guesses. |

**Test**: run `scripts/X.mjs --help` for the most-invoked script. Does the output tell the agent everything it needs to invoke the script correctly without reading anything else?

---

### Dimension 3 [review] — Abstraction value (does each layer earn its keep?)

Is each abstraction layer making the N+1 invocation faster, or adding indirection?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Each abstraction layer reduces invocation time. The agent invokes the abstraction directly without reasoning through its implementation. No layer exists "in case it's useful" — each is proven by ≥3 invocations. Compounding is observed: invocations get faster over time. |
| **4 — Good** | Most layers earn their keep. One or two layers exist that could be collapsed without observable cost. No layer actively adds latency. |
| **3 — Adequate** | Layers exist but their value is assumed, not measured. Compounding not documented. System works but it's not clear which abstractions are load-bearing. |
| **2 — Poor** | Multiple abstraction layers that require the agent to navigate indirection on every invocation. Each layer was designed before use; some are never actually needed. |
| **1 — Failing** | Deep abstraction pyramid designed upfront. Agent must traverse 3-4 levels before reaching an action. Invocations take longer as the system "matures." |

**Test**: trace the path an agent takes from cold-start to completing the most common task. Count the layers of indirection. Each layer should have a documented reason it exists.

---

### Dimension 4 [review] — Dynamic tool emergence (tools from observed need)

Do tools exist because observed procedures demanded them, or because someone designed a taxonomy?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every script in `scripts/` can be traced to a specific observed repeated procedure. No script exists for a use case that hasn't occurred ≥3 times. Scripts preemptively authored for "likely future use" are explicitly flagged as speculative. |
| **4 — Good** | Most scripts emerged from observed procedures. A few were authored speculatively but proved useful within 2-3 invocations. No major unused scripts. |
| **3 — Adequate** | Scripts exist for major operations. Some were designed upfront based on the author's anticipation of need. Most are used; a few have never been invoked. |
| **2 — Poor** | Significant number of scripts authored upfront as part of the "initial skill structure." Usage tracking doesn't exist. Unknown which scripts are actually invoked. |
| **1 — Failing** | Complete tool taxonomy designed before any invocations. Scripts exist for hypothetical cases. Many have never been invoked. The taxonomy is the primary artifact; usage is an afterthought. |

**Test**: for each script, count invocations over the last 30 days (or estimate if telemetry doesn't exist). Scripts with 0 invocations are candidates for deletion.

---

### Dimension 5 [gate] — Token economy (minimum effective dose)

Is every token loaded into context earning its keep?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Cold-start skill surface is ≤500 lines and contains only: mode menu, posture, PEV targets, script citations, reference pointers. Step-by-step procedures live in references/ (loaded on demand). No reference is loaded unless the current task needs it. Dead context (loaded but never accessed) is 0. |
| **4 — Good** | Cold-start surface is compact. A few procedures inline that could be pushed to references/. Reference loading mostly on-demand. Dead context < 10% of total loaded. |
| **3 — Adequate** | SKILL.md is within the ≤500-line guideline. Some references loaded preemptively. Agent occasionally reads content irrelevant to the current task. |
| **2 — Poor** | SKILL.md > 500 lines with procedural content that should be in references. Multiple references loaded at cold-start regardless of task. |
| **1 — Failing** | SKILL.md is a dump of all knowledge related to the domain. References loaded in full at cold-start. Token cost is proportional to document size, not task complexity. |

**Test**: for a simple task, trace every reference loaded. What fraction of loaded content was accessed during task completion? The inaccessible fraction is token waste.

---

### Dimension 6 [review] — Delegation clarity (what the agent decides vs. what the script decides)

Is the agent's decision-making role clearly scoped, or is it expected to reason through implementation details?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | The agent decides: which mode, which tool, which scope, whether the output is correct. The script decides: how to execute the procedure, how to handle internal edge cases, what format to output. The agent never reads script source code to understand what to do. |
| **4 — Good** | Clear conceptual delegation. A few edge cases where the agent must reason about script behavior (not just invoke it). |
| **3 — Adequate** | Delegation is implicit. The agent mostly invokes scripts correctly but occasionally reasons about implementation details when edge cases arise. |
| **2 — Poor** | The agent is frequently expected to interpret script output that isn't in `--json` format, infer script behavior from undocumented flags, or debug script errors that don't have actionable messages. |
| **1 — Failing** | The agent is the script. Every operation is specified as step-by-step prose that the agent interprets and executes manually. The agent is a general-purpose interpreter with infinite variance. |

**Test**: trigger a script error. Does the agent read the error and know what to do (script error is self-explanatory), or does it need to reason through the script's behavior to recover?

---

## §Anti-patterns

### AP-01 — The LLM-as-script anti-pattern

**Symptom**: the skill says "for each package.json, find the version field, change X.Y.Z to X.Y.Z+1." The LLM is doing regex matching, file editing, and format validation manually. **Root cause**: the procedure was written as prose because "it's simple enough for the LLM to do." **Correction**: the simplicity of a procedure is not the question. The question is: does it meet the mechanize threshold (repeatable, testable, silent failure modes, or destructive)? If yes, mechanize it regardless of how "simple" it looks.

### AP-02 — The taxonomy trap (tools designed before use)

**Symptom**: a skill launches with 12 scripts covering every anticipated operation. 8 of the 12 are never invoked in the first 6 months. **Root cause**: taxonomy design feels like architecture. "What operations will we need?" is an answerable question; the answer just happens to be wrong until you have observed usage. **Correction**: start with zero scripts. Write prose for everything. After the 3rd invocation of the same procedure, write the script. After the 3rd invocation of the same argument pattern, add a convenience flag. Tools emerge from observed need.

### AP-03 — The abstraction pyramid

**Symptom**: to deploy a change, the agent invokes `deploy-skill` → which invokes `release-pipeline` → which invokes `version-manager` → which invokes `bump.mjs`. Four levels of indirection. The agent must understand (or at least not misunderstand) each layer. **Root cause**: incremental abstraction that was never pruned as needs stabilized. **Correction**: regularly collapse the pyramid. If layer N always calls layer N+1 with the same arguments, collapse them into one layer. Indirection is only valuable if it's hiding genuine complexity that would otherwise need to be duplicated.

### AP-04 — Undocumented script behavior

**Symptom**: `scripts/deploy.mjs` has 15 flags. The `--help` output shows 8. The other 7 are undocumented; their behavior must be inferred from source code. **Root cause**: scripts grow; `--help` doesn't. **Correction**: `--help` is the contract. It must be updated with every flag addition. The skill's prose does NOT duplicate the `--help` content — it only cites the script and says "see --help." When `--help` and skill prose diverge, skill prose is always wrong (because it drifts); `--help` is always right (because it's the source of truth).

### AP-05 — Prose for mechanizable steps, scripts for judgment steps (inverted)

**Symptom**: the skill has a script for "pick the right branch name strategy" (which requires judgment) and prose for "increment the version number across 9 files" (which is mechanical). The agent uses the script for judgment (wrong: judgment needs the agent's attention) and manually executes the mechanical steps (wrong: the agent introduces variance). **Root cause**: scripts authored for "complex" operations and prose written for "simple" operations. Complexity is the wrong criterion. **Correction**: the mechanize threshold is about **repeatability and testability**, not complexity. Simple + repeatable + binary-checkable = script. Complex + judgment-heavy + context-dependent = prose.

### AP-06 — Token-opaque skill (the "be helpful" anti-pattern)

**Symptom**: the skill loads 5 reference files on cold-start because each one "might be relevant." The agent spends 3000 tokens loading irrelevant context before the task begins. **Root cause**: skill authors default to "more context is better" because they can't predict which case the agent will encounter. **Correction**: the cold-start surface should never load references. It should only name them and describe when to load each one. The routing table (mode menu) is the cold-start surface. References load on demand. Every reference should have an explicit load condition: "load if the current task involves X" — not "load because it might be relevant."

---

## §Hard Tests

1. **The mechanize-bait audit**: read the most-used mode in the most senior skill. For each step in the procedure: is it (a) repeated across cycles, (b) testable, (c) has silent failure modes, (d) has destructive blast radius? Count the mechanize-bait steps. Each one is a variance source and a token cost. Give me a ranked list by risk.

2. **The script-usage test**: for each script in `scripts/`, estimate invocations in the last 30 days. Scripts at 0 invocations are candidates for deletion. Scripts at 1-2 invocations are below the 3-strike threshold and possibly premature.

3. **The token-trace test**: for a simple task (one file change, one decision), trace every token the agent reads before taking the first action. What fraction was actually needed? The rest is token waste from poor inversion or front-loaded context.

4. **The --help completeness test**: run `--help` on the 3 most-invoked scripts. Is the output sufficient to use the script correctly without reading the script source or the SKILL.md? If not, which flags are undocumented?

5. **The abstraction collapse test**: pick one abstraction layer. Remove it and have the agent invoke the underlying layer directly. Is the outcome the same? Is the agent behavior different? If the outcome is identical and behavior unchanged, the layer is collapsible.

6. **The dynamic emergence test**: can you trace each script in `scripts/` to the specific observed procedure that created it? If not, some scripts were designed speculatively. Are they being used?

7. **The Elon test**: for each step in the skill's primary mode, ask "why does this step exist?" Accept only "it prevents failure X" or "it produces output Y that the next step requires." Reject "because the process says so" and "for completeness." Every step that can't pass this test is a candidate for deletion.
