---
date: 2026-05-23
status: draft
version: "0.1.0"
---

# Progressive Context Construction — Best Practices Rubric

**Context should grow with the task, not arrive fully-formed at session start.**

Progressive context construction is the discipline of loading information incrementally — exactly when it becomes needed, not before. It is the runtime complement to the static decisions covered in `context-engineering.md` (what belongs in context at all) and the structural decisions in `skills-authoring.md` (how skills organize their references). This rubric covers the _sequencing_ and _architecture_ of context growth across a task's lifecycle.

The contrast with context-stuffing:

- **Context-stuffing**: load everything that might be relevant at session start. The agent reads thousands of tokens of irrelevant documentation before taking the first action.
- **Progressive construction**: load the minimum at session start (harness + mode menu). As the task is understood, load the mode reference. As a specific procedure is needed, load the relevant sub-reference. Each load is triggered by task state, not by pre-loaded anxiety.

The result: at any point in the task, the context contains exactly what's needed — not more, not less. The agent's attention is on the task, not on filtering irrelevant content.

**Why this deserves its own rubric**: context engineering (what goes in) and progressive construction (when it goes in and how it grows) are related but distinct. A system can have excellent decisions about what to include and poor decisions about when to include it — front-loading valid content is still a violation of the minimum-effective-dose principle.

**Companion docs:**

- `context-engineering.md` (this folder) — what belongs in context; memory systems; caching architecture
- `skills-authoring.md` (this folder) — cold-start surface vs. on-demand references; mode routing
- `inversion-and-abstraction.md` (this folder) — token economy at the procedure level

---

## §The Problem

Context accumulates in two directions that compound each other:

**Vertical accumulation** (conversation history): as a task proceeds, the conversation grows. Early context that was load-bearing at turn 5 is noise at turn 30. The agent's attention is distributed across the full window — including the irrelevant early content — reducing the signal density of the current task state.

**Horizontal accumulation** (reference loading): as the agent explores the skill library, it loads references. Some are loaded because the task needed them; others are loaded "to be safe" or "to understand the context." Both categories consume tokens. Only the former earns its keep.

Without progressive construction discipline, a 40-turn session that touches 3 references will accumulate 50,000 tokens of context even though the current task only requires 5,000. The agent in turn 40 is working with 10x the noise of the agent in turn 5 — and the task hasn't gotten 10x harder.

**The goal**: at turn N, the context should contain exactly the state needed to complete turn N's action. No more from the past that is no longer relevant; no more loaded references than the current task requires.

---

## §First Principles

### 1. Context grows in response to task state, not in anticipation of it

Loading a reference before the task requires it is a bet that the reference will be needed. Sometimes the bet is right; often it isn't. The cost of a wrong bet is paid on every subsequent turn. The right discipline: load references in response to task signals, not in anticipation of them.

The routing table in SKILL.md (the mode menu) is the mechanism: cold-start renders the menu, the agent selects a mode, and only then loads the mode's reference. The reference is loaded because a specific task state (mode selection) has been reached — not because it might be needed.

### 2. Context checkpoints prevent accumulation debt

Long-running tasks accumulate history that was useful earlier but is noise now. A context checkpoint collapses prior turns into a minimal summary: current task state, active decisions, known constraints, errors encountered. The collapsed summary is smaller than the full history and contains only forward-looking content.

Checkpoints should fire at natural task boundaries: after planning (before execution), after a major subtask completes, when errors accumulate. The discipline is not to delay the checkpoint until the context window is full — by then, the accumulation has already degraded agent quality.

### 3. The loading event is a semantic signal, not a mechanical operation

Loading a reference is not just "add tokens to context." It is a semantic signal to the agent: "we have entered the domain of this reference." The agent should acknowledge the load implicitly in its next action — not re-read the cold-start content, not re-explore the mode menu, but proceed with the loaded reference's guidance.

A well-designed skill triggers a specific loading event when the agent enters a specific domain. The trigger is in the cold-start routing table: "entering mode X → load reference Y." The agent doesn't decide to load Y independently; the routing table makes the load event deterministic.

### 4. Deferred loading is the complement of progressive loading

Progressive context construction has two sides: loading content when it's needed (progressive loading) and _not_ loading content until it's needed (deferred loading). Deferred loading is often more important: the default should be "don't load" and the exception should be "load because task state requires it."

This is the inversion of the common failure mode: skill authors load references "to be safe" and then ask "can I prune any of these?" The right approach: load nothing, and then ask "what does this task state require me to load?"

### 5. Verification requires its own context phase

Verification is not part of execution — it is a distinct task phase with distinct context requirements. During execution, the agent needs the task specification and the relevant procedure. During verification, the agent needs the real-product state (the curl output, the test results, the browser DOM).

A system that doesn't explicitly transition to a verification context phase will use execution context to do verification — which means it's verifying against its own expectations rather than against real-world state. This is the "verify-theater" failure mode: the context contains a plan and a completed execution; the agent declares "done" because the plan matches the execution. It never loaded the real-world state.

### 6. Context cost is proportional to relevance density, not size

A 10,000-token context where every token is relevant to the current task produces better outputs than a 5,000-token context where 50% is noise. Relevance density — the ratio of relevant tokens to total tokens — is the real measure. Progressive context construction maximizes relevance density by loading only what the current task state requires.

---

## §The Rubric

### Dimension 1 [gate] — Cold-start surface minimality

Does the cold-start surface load only what is needed to orient the agent, or does it front-load references and procedures?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Cold-start surface: harness (AGENTS.md) + mode menu (SKILL.md first screen). Contains: posture statement, mode names with one-line descriptions, reference pointers with explicit load conditions. No reference content inline. No step-by-step procedures at cold-start. Agent can orient in < 500 tokens. |
| **4 — Good** | Cold-start is compact. A few procedures inline that are short enough not to be harmful but could be pushed to references. |
| **3 — Adequate** | Cold-start includes some reference content "for convenience." Adds 200-500 tokens to every session regardless of task type. |
| **2 — Poor** | Multiple references loaded at cold-start. Cold-start > 2000 tokens from skill content alone. Agent reads reference content before understanding the task. |
| **1 — Failing** | Cold-start loads the full skill content (SKILL.md + references inlined). Every session starts with 5000+ tokens of reference material the agent may not need. |

**Test**: measure the token count of what the agent reads before it first takes a task-specific action (not a context-loading action). If > 1000 tokens, cold-start is over-loaded.

---

### Dimension 2 [review] — Reference loading discipline (triggered, not preemptive)

Is each reference load triggered by a specific task state, or pre-emptively loaded "just in case"?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every reference in `references/` has a documented load condition in SKILL.md ("load when task involves X"). Agent loads references only when the load condition is met. No reference is loaded before its condition fires. Post-task audit: all loaded references were used; no dead context. |
| **4 — Good** | Most references have explicit load conditions. One or two are loaded "if uncertain" — acceptable for references that are small and frequently needed. |
| **3 — Adequate** | Load conditions implied by mode structure (mode 1 → load reference A, mode 2 → load reference B) but not explicitly stated. Agent loads the right reference most of the time but occasionally loads both for ambiguous tasks. |
| **2 — Poor** | References loaded when the agent thinks they might be useful. No explicit conditions. Multiple references loaded per task regardless of which is actually needed. |
| **1 — Failing** | All references loaded at session start. Load is not conditional — it is invariant. |

**Test**: for a task that uses mode 2 only: which references are loaded? Should include only mode 2's reference. Any additionally loaded references are preemptive loading violations.

---

### Dimension 3 [review] — Context checkpoint cadence

For long-running tasks, are checkpoints used to prevent accumulation debt?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Explicit checkpoint protocol: fires at natural task boundaries (post-planning, post-major-subtask, on error accumulation). Checkpoint produces a forward-looking summary (current state, active decisions, known constraints). History before checkpoint is collapsed. Checkpoint size < 20% of original history. |
| **4 — Good** | Checkpoints used for tasks > 20 turns. Checkpoint captures essential state. Some non-essential history included (slightly over-verbose summaries). |
| **3 — Adequate** | No formal checkpoint protocol, but the model's native context compression handles the accumulation. Some quality degradation on very long tasks. |
| **2 — Poor** | No checkpoints. Context accumulates throughout task. Late-task behavior visibly degrades as signal density decreases. |
| **1 — Failing** | Context accumulation is never managed. 50-turn tasks accumulate full history. The agent in turn 50 has a heavily diluted context. Errors introduced in early turns persist as noise. |

**Test**: run the same task to turn 5 and to turn 30. Compare output quality. If turn 30 output is visibly worse than turn 5 output on the same class of action, accumulation is degrading quality.

---

### Dimension 4 [review] — Task-phase context transitions

Does the context explicitly transition between phases (planning → execution → verification)?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Three-phase context model: (1) Planning phase: task spec + harness rules; (2) Execution phase: planning outputs + relevant procedure/script; (3) Verification phase: execution outputs + real-product state. Phase transitions are explicit and documented. Agent never uses execution context to perform verification. |
| **4 — Good** | Execution and verification are distinct. Verification always fetches real-product state. Planning context may bleed into execution (acceptable if not causing errors). |
| **3 — Adequate** | PEV loop documented but context phases not explicitly managed. Agent transitions between phases naturally; sometimes verification uses execution context without fetching real state. |
| **2 — Poor** | No phase structure. Execution and verification happen in the same context with no explicit state injection. Verify-theater is possible. |
| **1 — Failing** | No phase concept. Agent declares done based on execution state alone. Real-product state is never injected into context. |

**Test**: after the agent completes execution, what does it read before declaring done? If the answer is "nothing new — it uses the execution context," the verification phase is missing its real-product context injection.

---

### Dimension 5 [hypothesis] — Relevance density over task lifetime

Does relevance density stay high across the task, or does noise accumulate?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Relevance density measured (or estimated) at task start, middle, and end. Checkpoints prevent degradation. Reference loading is bounded (load, use, mentally "close"). Dead context identified and managed. Agent quality on task-end actions matches quality on task-start actions. |
| **4 — Good** | No formal measurement but observable: agent quality doesn't visibly degrade on long tasks. Checkpoints used when context visibly swells. |
| **3 — Adequate** | Relevance density degrades on tasks > 20 turns. Not addressed systematically; depends on native model handling. |
| **2 — Poor** | Relevance density degradation is a known quality problem. Long tasks produce worse outputs than short tasks for the same class of action. No structural response. |
| **1 — Failing** | Context has never been analyzed for relevance density. Long tasks fail and short tasks succeed; the cause is context accumulation, but it's diagnosed as "the task was hard." |

**Test**: pick a 30-turn task. Estimate the relevance density at turn 5 and at turn 30 (tokens that were accessed / total tokens in context). If turn 30 density is < 40% of turn 5 density, accumulation is the primary quality lever.

---

### Dimension 6 [review] — Recovery context (error handling and replanning)

When an agent encounters an error, does it load the right recovery context — or does it try to recover with the wrong context?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Error handling is a documented context phase. Error events trigger: (1) load the error output (fresh external state), (2) load the skill's error-recovery reference (if one exists), (3) re-plan with the new context. Agent doesn't retry with identical context. |
| **4 — Good** | Agent loads error output and re-plans. Error-recovery reference may not exist; agent improvises recovery with general knowledge. Retries use updated context. |
| **3 — Adequate** | Agent retries on error, sometimes with updated context, sometimes without. Depends on whether the error message is self-explanatory. |
| **2 — Poor** | Agent retries with the same context that produced the error. No new context injected. Stuck-counter not present; retries continue until token budget. |
| **1 — Failing** | Error state not handled. Agent either halts or continues as if the error didn't happen. Error context not distinguished from success context. |

**Test**: trigger a recoverable error (e.g., a script failure with a descriptive error message). Does the agent load the error output into context and re-plan, or does it retry the same action with the same arguments?

---

## §Anti-patterns

### AP-01 — The "orient everything" cold-start

**Symptom**: SKILL.md cold-start includes 3 reference files inline "so the agent has full context." Every session starts with 8000 tokens of reference material for tasks that will only use one reference. **Root cause**: skill authors fear the agent will "miss something" if it doesn't have everything upfront. **Correction**: the cold-start surface is the mode menu, not the mode content. The menu tells the agent what exists; the mode reference tells it how to proceed. The mode reference is loaded only after mode selection. Fear of missing context is the wrong heuristic — the right heuristic is load-condition matching.

### AP-02 — Checkpoint-phobic accumulation

**Symptom**: a 40-turn planning-and-execution task has no context checkpoints. By turn 35, the agent is reasoning about decisions made in turns 5-10 that were superseded in turns 15-20. Quality is visibly worse at turn 35 than at turn 10 for the same type of action. **Root cause**: checkpoints feel disruptive and add ceremony. "The model handles this natively." **Correction**: native model compression is lossy and unpredictable. Explicit checkpoints are structured and predictable. Fire them at task-phase boundaries: after planning, after major subtasks, after error accumulation. A 200-token structured checkpoint beats 2000 tokens of raw history at equal or lower cost.

### AP-03 — Phase collapse (execution context used for verification)

**Symptom**: agent completes execution ("I've made all the changes") and immediately declares done. The verification step reads only its own execution context, not the real-product state. **Root cause**: no explicit phase transition to verification. Verification is treated as the last step of execution, not as a distinct context phase. **Correction**: verification has a distinct context injection: fetch the real-product state (curl output, test results, browser DOM) and add it to context before declaring done. The agent must read external state, not its own plan, to verify.

### AP-04 — Preemptive reference loading ("to be safe")

**Symptom**: agent is given a task and immediately loads 4 references "because they might be relevant." 2 of the 4 are never accessed during the task. **Root cause**: the agent's cold-start routing table doesn't specify load conditions explicitly. "Might be relevant" is the agent's fallback when conditions are absent. **Correction**: every reference in `references/` has an explicit load condition in the SKILL.md routing table. Load conditions use task-state signals ("if the task involves X"), not vague relevance judgments ("might be relevant to Y").

### AP-05 — History bloat without checkpointing

**Symptom**: conversation history grows to 15,000 tokens. The agent's early planning (turns 1-8) is still in context and competes with the current execution state (turns 30-40). Late-task errors are harder to diagnose because the relevant signal is buried under 10,000 tokens of history. **Root cause**: no checkpoint scheduled; history assumed to be "always useful." **Correction**: checkpoint at turn 20 of a complex task. Produce a forward-looking summary (task state, decisions made, constraints active, errors encountered). Treat history before the checkpoint as archival; only the summary is in active context.

### AP-06 — Identical context on retry (the stuck-loop feeder)

**Symptom**: agent fails a step, retries with the same context that produced the failure, fails again, retries again. The stuck-loop is fed by context that hasn't changed. **Root cause**: error handling doesn't inject new external state before retry. The agent replays the same reasoning with the same inputs. **Correction**: per the agentic-coding stuck-counter principle: if a step fails twice with the same error type, the context must change before the third attempt. Load the error output freshly, load the error-recovery reference, replan. Do not retry with identical context.

---

## §Hard Tests

1. **The cold-start token test**: count the tokens the agent reads before its first task-specific action (excluding tool calls and code generation). Target: ≤ 1000 tokens from skill content. If > 2000 tokens, cold-start is over-loaded.

2. **The reference utilization test**: for a completed task, list every reference loaded. For each: how many times was it accessed? References with 0 accesses are preemptive loads. References with 1 access in a 30-turn task are marginal. Track this across 5 tasks; the pattern tells you which references are genuinely on-demand vs. preemptively loaded.

3. **The quality-vs-turn test**: run a 30-turn task. Score the quality of the agent's action at turn 5 vs. turn 25 on the same class of action (file edit, decision, summary). If turn 25 quality is visibly worse, context accumulation is degrading performance.

4. **The checkpoint recovery test**: mid-task (turn 15 of a 30-turn task), manually insert a context checkpoint summary. Complete the task. Compare outcome quality to the same task without a checkpoint. If checkpoint quality is higher, accumulation was the bottleneck.

5. **The verification phase test**: after the agent declares done, check: what was the last new external information it read? If the answer is "nothing — it used execution context," the verification phase is missing its context injection.

6. **The error-retry test**: trigger a recoverable error. Does the agent's retry contain new external state (error output, freshly fetched resource), or is it the same context that produced the original failure? Identical context on retry is a context construction failure.

7. **The load-condition audit**: for each reference in the most-used skill, find its explicit load condition in SKILL.md. If any reference lacks a stated condition, ask: when should this be loaded? If the answer is "whenever the agent thinks it's needed" — that's a preemptive loading invitation, not a condition.
