---
date: 2026-05-31
status: draft
version: "0.1.0"
---

# Plan Anatomy — Best Practices Rubric

**A plan is not a to-do list.** A plan is an executable specification: every subgoal scoped, every dependency ordered, every checkpoint defined, every branch condition named, every completion criterion grounded in observable external state, every failure mode anticipated. An agent with a vague plan starts well and degrades; an agent with a well-structured plan executes reliably even when the environment surprises it.

**The bridge from intent to execution fails at specific seams.** Knowing where those seams are — goal decomposition, dependency ordering, checkpoint design, decision point specification, completion criteria, recovery paths, and plan representation — lets you audit a plan before it runs rather than diagnose it after it breaks.

**Boris Cherny on plan quality**: _"A good plan is really important to avoid issues down the line. Once there is a good plan, it will one-shot the implementation almost every time."_ One-shot execution is not luck; it is the downstream consequence of plan anatomy.

**Companion docs:**

- `agentic-coding.md` (this folder) — D1 plan quality as part of the broader PEV loop
- `harness-design.md` (this folder) — the infrastructure that enforces PEV posture
- `context-engineering.md` (this folder) — keeping the plan's context fresh during execution
- `evaluation-workflows.md` (this folder) — verifying plan quality before execution begins
- `multi-agent-coordination.md` (this folder) — how plan anatomy scales to parallel agents

---

## §The Problem

Plans fail at known structural seams:

1. **Goal decomposition failure** — the agent breaks "implement the feature" into "do the auth part, then the UI part" rather than into scoped subtasks with file boundaries and interface contracts. The vague subtask leaves decomposition to execution-time judgment, where it is most expensive to get wrong.

2. **Dependency and ordering failure** — the agent executes tasks that have unstated prerequisites, then discovers mid-run that the work must be redone. Database schema changes require migrations before API changes; interface changes require both sides before integration tests. Unordered plans produce cascading rework.

3. **Checkpoint absence** — the agent runs 20 steps before discovering that step 3 produced wrong output. No intermediate validation; the error propagates silently and every downstream step must be redone. Checkpoints are the blast-radius limiter for planning errors.

4. **Decision point under-specification** — the plan says "if X, do Y" but leaves "X" undefined or dependent on model judgment at execution time. When the plan is executed by a different agent, a different model, or a future session, the decision produces a different outcome. Decision points must name the observable signal, not the vibe.

5. **Completion criteria self-assessment** — the agent declares done when the code looks right to itself, not when an external signal confirms the goal is met. The distinction between "the script ran without errors" and "the feature works in production" is a completion-criteria problem.

6. **Recovery path absence** — the plan accounts only for the happy path. The first unexpected error requires either the agent to improvise recovery (introducing new risk) or the operator to intervene (defeating the purpose of automation).

7. **Plan representation opacity** — the plan lives entirely in the agent's working context. A human reviewer cannot inspect it; a new agent cannot resume from it; an auditor cannot verify it was followed. The plan that only the executing agent can read is not a plan — it is a note to self.

---

## §First Principles

### 1. A plan is an artifact, not a warm-up

The plan is produced before execution begins and is externalized as a document that can be reviewed, challenged, approved, and handed off. A plan that exists only as reasoning trace in the working context fails when the context is truncated, when execution is handed to another agent, or when a mid-execution error requires replanning from a clean state.

### 2. Subgoals are executable when they can be independently verified

A subgoal that cannot be independently verified is not a subgoal — it is a fuzzy intention. The test for executability: can you write a binary pass/fail check that confirms the subgoal is complete without running any subsequent steps? If not, the subgoal is underspecified.

### 3. Dependencies are obligations, not suggestions

An agent that executes out of dependency order is not being efficient — it is producing work that may need to be redone. The dependency graph is the plan's skeleton; optional orderings may be parallelized, but hard dependencies must be sequenced mechanically, not by judgment.

### 4. Checkpoints are the blast-radius control mechanism

Every checkpoint converts a potential late-discovery failure into an early-recovery opportunity. The cost of a checkpoint (time to validate) must be weighed against the cost of late discovery (all downstream steps invalidated). For steps with high downstream propagation, the checkpoint cost is almost always lower.

### 5. Decision points must name their oracle

A decision condition that cannot be evaluated by inspecting external state requires model judgment, which is session-specific and non-reproducible. A decision condition that names its observable oracle (file exists, API returns 200, schema version matches) is reproducible, auditable, and can be mechanized.

### 6. Completion criteria are external state assertions

"Done" is not "I have finished the work" — it is "the world now matches the goal state." The completion criterion names a specific external observable: the endpoint returns the expected response, the package is visible in the registry, the UI element renders in the expected viewport. An agent that cannot name the external state assertion does not know when to stop.

### 7. Recovery paths are part of the plan, not improvisation

A plan without recovery paths is a bet that nothing goes wrong. Production plans must specify: what constitutes failure for each major step, what the recovery action is, and at what escalation threshold the agent stops acting and requests operator input. Recovery paths specified before execution are cheaper and more reliable than improvised recovery during failure.

---

## §The Rubric

### Dimension 1 [review] — Goal decomposition quality

Are goals broken into executable subgoals with clear scope and independently verifiable completion signals?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every goal is decomposed into subgoals, each with: explicit file scope or API boundary, a named completion signal verifiable without running downstream steps, and a size small enough to execute in one context window without mid-task improvisation. Decomposition is produced as an artifact before execution. |
| **4 — Good** | Decomposition names major work areas with file boundaries. Completion signals are implied but not fully specified. A few subgoals are still larger than one context window but could be split. |
| **3 — Adequate** | Agent lists tasks but without file boundaries. Subgoals are phase-level ("do the auth part") rather than action-level. Ordering is present but verification signals are not. Works for simple tasks; breaks when a subgoal spans multiple files with interfering changes. |
| **2 — Poor** | Decomposition is feature-level ("implement authentication") without subtask structure. The agent has a direction, not a decomposition. Execution improvises the actual steps. |
| **1 — Failing** | No decomposition. Agent receives the goal and immediately begins execution. The full scope only becomes clear after several steps. |

**Test**: show the plan to an agent that has not read the task description. Can it execute any single subgoal independently, verify it is complete, and stop — without needing to understand the overall goal or subsequent steps?

---

### Dimension 2 [gate] — Dependency and ordering

Are task dependencies explicit and correctly sequenced so that later steps never require undone prior work?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | The plan has an explicit dependency graph or ordered step list with stated rationale for each ordering constraint. Hard dependencies (B cannot start until A produces artifact X) are distinguished from soft orderings (C is easier after B but not blocked). Parallelizable steps are identified. |
| **4 — Good** | Steps are ordered correctly and execution would not encounter undone prerequisites. The ordering rationale is not always stated but is traceable from the step descriptions. No explicit parallel identification. |
| **3 — Adequate** | Steps are in a plausible sequence but dependencies between specific steps are not named. An agent could violate ordering without the plan detecting it. Works for linear tasks; breaks when one agent is handed a subset of steps. |
| **2 — Poor** | Steps are listed in an order that seems reasonable but contains at least one dependency violation: a step that assumes an artifact produced by a later step. Execution will require backtracking or improvised reordering. |
| **1 — Failing** | No ordering structure. Steps are listed as a flat set. The agent decides at execution time what to do next, producing inconsistent results across runs. |

**Test**: extract the dependency graph from the plan. For each step, identify what it assumes is already complete. Does any step assume something that appears later in the sequence?

---

### Dimension 3 [gate] — Checkpoint design

Are intermediate validation points specified before costly or propagating steps, making early failure visible before downstream work is invalidated?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | The plan identifies the high-propagation steps (those where a wrong output invalidates the most downstream work) and inserts a named checkpoint before each. Each checkpoint specifies: what to check, how to check it (command, observable, test), and what to do on failure (recover, replan, escalate). Checkpoint results are externalized, not self-assessed. |
| **4 — Good** | Checkpoints are present before the most obviously expensive steps. Not every high-propagation step has a checkpoint, but the major ones do. Failure actions are implied (stop and replan) rather than specified. |
| **3 — Adequate** | Some checkpoints exist as notes ("verify this works before continuing") but without specified check method or failure response. Agent must judge whether the checkpoint passes. |
| **2 — Poor** | No explicit checkpoints. Agent proceeds through all steps and validates only at the end. A failure discovered at step 15 of 20 requires replanning from an uncertain intermediate state. |
| **1 — Failing** | No checkpoints and no plan-level awareness that they are needed. Agent treats the plan as a command sequence to execute fully before any validation. |

**Test**: identify the step in the plan with the highest downstream propagation (the one that, if wrong, invalidates the most subsequent work). Is there an explicit checkpoint before it? Does the checkpoint name its oracle and failure response?

---

### Dimension 4 [gate] — Decision point specification

Are branch conditions named in terms of observable external signals, or are they left to model judgment at execution time?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every conditional branch in the plan names its observable oracle: the file path that must exist, the API response code that signals success, the schema version that must match, the environment variable that must be set. An agent executing the plan can evaluate the condition without exercising judgment — it is a binary check against a named external signal. |
| **4 — Good** | Most decision points name their oracle. One or two rely on qualitative judgment ("if the test suite looks healthy") but these are low-stakes decisions with limited downstream propagation. |
| **3 — Adequate** | Decision points are named ("if the build succeeds") but the build success condition is not specified — the agent uses its own judgment about what constitutes success. Reproducibility depends on consistent model judgment, which is not guaranteed. |
| **2 — Poor** | Decision points are implicit or vague ("if something goes wrong, try again"). The agent improvises branch evaluation at execution time. Different runs of the same plan can produce different branches for the same external state. |
| **1 — Failing** | No branch conditions. The plan is a linear sequence with no provision for conditional execution. When reality diverges from the plan's assumptions, the agent improvises entirely. |

**Test**: pick the plan's most consequential branch condition. Can you write a shell command or API call that evaluates it to true or false, without reading the agent's internal state or model output?

---

### Dimension 5 [gate] — Completion criteria

Is "done" defined as an external state assertion, verifiable without the executing agent's self-assessment?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | The plan names a specific external state assertion for each major goal: the endpoint returns status 200 with the expected body, the package is visible in the registry at the specified version, the database row exists with the correct field values, the UI element renders at the expected pixel dimensions. The verification command or procedure is named. A different agent running the same check would produce the same pass/fail result. |
| **4 — Good** | Completion criteria are externalized and specific. Verification command not always named but can be derived from the criterion. A different agent could reproduce the check. |
| **3 — Adequate** | Completion criteria reference internal signals ("tests pass," "no linter errors") that confirm internal consistency but not goal achievement. The feature may be broken in production while all named criteria pass. |
| **2 — Poor** | Completion criteria are self-assessments ("I believe the implementation is correct") or proxies ("code review approved") that do not ground the goal in external observable state. Different agents assessing the same output may reach different conclusions. |
| **1 — Failing** | No completion criteria. The agent declares done when it has finished executing its planned steps. No external signal is consulted. |

**Test**: take the plan's completion criteria and hand them to a different agent with no knowledge of the task. Can that agent run a check and produce a binary pass/fail? If the agent must read code or make a judgment call, the criteria are not externalized.

---

### Dimension 6 [review] — Recovery paths

Are failure modes anticipated with explicit fallback strategies, escalation thresholds, and handoff contracts that allow graceful degradation?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | For each major step, the plan specifies: (a) what constitutes failure (observable signal), (b) the first recovery action (retry with X, rollback to Y, switch to alternative approach Z), (c) the escalation trigger (after N failures, escalate to operator), and (d) the handoff contract (what state to expose to the operator or next agent). Recovery paths are specified before execution, not improvised during failure. |
| **4 — Good** | Recovery paths exist for the most likely failure modes. Not every step is covered. Escalation threshold is implied (stop and report) rather than specified (stop after 2 retry attempts). Handoff contract exists but is informal. |
| **3 — Adequate** | Recovery is treated as "try again" without structural differentiation. No escalation threshold; agent retries indefinitely or gives up immediately. Handoff contract missing: operator inherits an unknown intermediate state. |
| **2 — Poor** | Recovery path is generic ("if it fails, report the error"). No per-step failure specification. No escalation threshold. Agent either loops on failure or halts with an unusable intermediate state. |
| **1 — Failing** | No recovery paths. Plan assumes all steps succeed. First failure causes unstructured stop or infinite loop. |

**Test**: inject a controlled failure at the plan's most propagating step. Does the agent follow a specified recovery path, escalate at a named threshold, and hand off a usable state — or does it loop, improvise, or halt without exposing what it had accomplished?

---

### Dimension 7 [review] — Plan representation quality

Is the plan structured for both machine execution (step-level precision, checkable conditions) and human inspection (readable, auditable, resumable after interruption)?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | The plan is externalized as a durable artifact (markdown document, structured JSON, or equivalent) that survives context truncation. It contains: goal statement, subgoal list with file scope, dependency graph or ordered sequence, checkpoint definitions, decision point oracles, completion criteria, and recovery paths. A human reviewer can inspect it without reading the execution transcript. A new agent can resume from any named checkpoint without reconstructing prior context. |
| **4 — Good** | Plan is externalized and readable. Contains goal statement, subgoal list, and completion criteria. Checkpoint and recovery sections may be thin or implied. Resume after interruption is possible but requires reconstructing some context. |
| **3 — Adequate** | Plan exists in the conversation or context window but is not externalized as a durable artifact. Truncated context loses the plan. A new agent cannot resume without rereading a long transcript. Human inspection requires reading execution reasoning, not a clean plan document. |
| **2 — Poor** | Plan is implicit in the agent's execution behavior. The "plan" could be reconstructed from the action sequence but was never stated explicitly. Review requires forensic reconstruction. |
| **1 — Failing** | No externalized plan. Execution proceeds directly from the task description. The plan exists only in the moment of each individual action decision. |

**Test**: take the plan artifact (if any) and hide the execution transcript. Can a human reviewer understand the intended sequence, verify that execution followed the plan, and restart execution from the midpoint if interrupted — using only the plan artifact?

---

## §Anti-patterns

### AP-01 — Decomposition by phase, not by scope

**Symptom**: Plan says "first do the backend, then the frontend." No file boundaries. No interface contracts. No independent verification signals. The agent improvises everything inside each phase. **Root cause**: Phase decomposition reflects product thinking (what gets built in what order) rather than execution thinking (what unit of work can be independently verified). **Correction**: Decompose by file boundary and interface contract. Each subgoal names the files it modifies, the interfaces it produces or consumes, and the check that confirms it is complete without running downstream steps.

### AP-02 — Dependency by convention

**Symptom**: Plan lists steps in order, but no step names what it assumes is already complete. Ordering is implied by sequence, not stated as a constraint. **Root cause**: The plan was authored in execution order and never audited for hard dependency violations — steps where out-of-order execution produces wrong output, not just slow output. **Correction**: For each step, add a "requires:" field naming the artifact or state that must exist before it runs. Steps without requirements are parallelizable. Steps with requirements inherit the dependency graph.

### AP-03 — Checkpoint as comment

**Symptom**: Plan contains "verify this is working before proceeding" without naming what to verify, how to verify it, or what to do on failure. The checkpoint is advisory, not structural. **Root cause**: Checkpoints are added to signal diligence rather than to mechanize validation. **Correction**: Every checkpoint must name its oracle (what to check), its method (how to check it), and its failure action (what to do if the check fails). A checkpoint without these three fields is not a checkpoint — it is a note.

### AP-04 — Decision points that require taste

**Symptom**: "If the code quality is acceptable, proceed. Otherwise, refactor." What constitutes acceptable? The agent decides at execution time, producing different choices on different runs. **Root cause**: Decision conditions were written for a human reader who shares the author's judgment. They are not machine-evaluable. **Correction**: Replace judgment-based conditions with oracle conditions: "If `npm run lint` exits 0, proceed. Otherwise, apply auto-fix and recheck. If lint still fails after auto-fix, escalate." The oracle is named; the threshold is named; the escalation is named.

### AP-05 — Completion criteria by self-report

**Symptom**: Agent declares done because it completed all planned steps and the code "looks correct." The actual feature is broken in production because no external state was checked. **Root cause**: Completion criteria were written in terms of agent action ("implement X") rather than external state ("the endpoint returns X with status 200"). **Correction**: For every goal, write the completion assertion as an external state check. Name the command or observable that produces the binary result. If you cannot name the external check, you do not know what "done" means for this goal.

### AP-06 — Recovery by retry

**Symptom**: Plan's only recovery strategy is "try again." No limit on retries. No differentiation between transient failures (worth retrying) and structural failures (require replanning). Agent loops. **Root cause**: Recovery was treated as "handle the failure" rather than "recover the plan's state." Retry is appropriate for transient failures; replanning is required for structural ones; escalation is required when the agent cannot distinguish the two. **Correction**: Specify per-step failure categories: transient (retry N times), structural (replan), unknown (escalate). Name the escalation trigger (N attempts without progress). Name the handoff contract (what state the operator inherits).

### AP-07 — Plan as context-window resident

**Symptom**: The plan exists only in the agent's current context. Context compaction, truncation, or handoff to a new session loses the plan. Execution continues from habit or improvisation. **Root cause**: The plan was treated as planning-phase reasoning rather than as a durable execution artifact. **Correction**: Externalize the plan as a file before execution begins. Name the file in the task setup. Reference the file at every checkpoint. A plan that only the original agent can access is not a plan for a distributed or multi-session system.

---

## §Hard Tests

These are the questions to apply to any plan before authorizing execution. A plan that cannot answer these questions cleanly is not ready to run.

1. **The independent-subgoal test**: pick any single subgoal from the plan. Can an agent that has not read the overall goal or any other subgoal execute it, verify completion, and stop — without improvising anything? If not, the subgoal is underspecified.

2. **The dependency-violation test**: extract the dependency graph. For each step, list what it assumes is complete. Does any step assume something produced later in the sequence? One violation means the plan will require mid-execution replanning for a predictable reason.

3. **The checkpoint-before-propagation test**: identify the step with the highest downstream propagation — the one whose wrong output invalidates the most subsequent work. Is there a checkpoint immediately before it, with a named oracle and failure action?

4. **The oracle test**: pick the plan's most consequential decision branch. Write the shell command or API call that evaluates the branch condition to true or false. If you cannot write the command, the decision point requires model judgment and is non-reproducible.

5. **The handoff test**: remove the executing agent and hand only the plan to a new agent. Does it know what "done" looks like for the overall goal? Can it run the completion check? Can it determine which steps have been completed and which remain?

6. **The injection test**: inject a controlled failure at the plan's highest-propagation step. Does the agent follow a recovery path within the plan, hit a named escalation threshold, and expose a usable intermediate state — or does it loop, improvise, or halt without leaving usable context?

7. **The truncation test**: truncate the agent's context to remove the planning phase. Is the plan still accessible as an externalized artifact? Can execution resume from the nearest checkpoint without reconstructing the plan from conversation history?

8. **The external-state test**: for the plan's primary completion criterion, run the verification check on a system where the plan has NOT been executed. What does the check return? If the check cannot be run independently of agent context, the criterion is not externalized.

9. **The parallel-execution test**: could two agents each execute a disjoint subset of the plan's steps simultaneously without producing conflicts? If not, which dependencies prevent parallelism? Are they real dependencies or ordering conventions? Unexamined dependencies cap throughput unnecessarily.

10. **The resume test**: simulate an interruption at the plan's midpoint. A new agent reads only the plan artifact (not the transcript). Does it know: what has been completed, what remains, what the current state of the world is, and what the next safe step is? If any of these is unclear, the plan's representation is insufficient for real-world interruptions.
