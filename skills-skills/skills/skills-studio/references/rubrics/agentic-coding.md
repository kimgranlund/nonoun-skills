---
date: 2026-05-23
status: draft
version: "0.1.1"
---

# Agentic Coding — Best Practices Rubric

**Agentic coding is not "autocomplete at larger scale."** It is a different paradigm: the agent has a complete task specification, works autonomously over many steps, and is responsible for verifying its own output before declaring done. The failure modes are correspondingly different — not wrong tokens, but wrong architecture, wrong decomposition, silent verification gaps.

88% of AI agent projects fail to reach production. 65% of enterprise agent failures trace to **context drift** (stale or incomplete information). The remainder fail from poor decomposition, missing verification gates, and agents that go off the rails with no circuit breaker. This rubric addresses all three failure modes.

**Steve Yegge on the state of the art (2026)**: "I built Gas Town, an orchestration system that coordinates 20-30 Claude Code instances in parallel. The IDE is dead by 2026. The future is orchestrated multi-agent coding — developer articulates intent and manages an ensemble of agents." Chat programming showed a 5x productivity boost; agent programming is adding another 5x on top. (Pragmatic Engineer interview, Steve Yegge on AI Agents)

**Companion docs:**

- `harness-design.md` (this folder) — the infrastructure that makes PEV reliable
- `prompt-control-modes.md` (this folder) — choosing the right level of prescription vs. agency
- `security-and-scope-containment.md` (this folder) — blast-radius boundaries and confirmation gates
- `evaluation-workflows.md` (this folder) — evals and regression checks for agent behavior
- `BORIS-feedback.md §Boris's actual stated principles B1` — PEV as the central loop

---

## §The Problem

An agentic coding system that lacks a disciplined execution model will:

1. **Execute without a plan** — the agent starts making changes before it understands the full scope, then discovers mid-execution that earlier work is wrong.
2. **Declare done without verifying** — the agent returns "done" when the code compiles, not when the feature actually works in the real product.
3. **Silently fail at scale** — parallel agents overwrite each other's files; one bad assumption cascades across 10 files; the failure is noticed hours later.
4. **Repeat old errors** — no mechanism to carry forward learnings from prior sessions; every session re-discovers the same constraints.

The PEV loop (Plan → Execute → Verify) is the structural answer to failures 1 and 2. Git worktrees and spec-driven decomposition address 3. Corrective feedback integration addresses 4.

---

## §First Principles

### 1. Plan first, then name the verify target

Per Boris Cherny: _"A good plan is really important to avoid issues down the line. Once there is a good plan, it will one-shot the implementation almost every time."_ The plan has two outputs: (a) the task decomposition, and (b) the verify target. **Both must be named before execution starts.** An agent that executes without a named verify target will confuse "the script ran" with "the work is done."

### 2. Verify against reality, not against self

Per Boris: _"Give Claude a way to verify its work. If Claude has that feedback loop, it will 2-3x the quality."_ The key word is "feedback loop" — feedback from the real product, not from the agent's own internal consistency check. A test suite that passes is not the same as a feature that works. A type-check that passes is not the same as an API that returns the right data.

### 3. Isolation prevents silent corruption

Each agent working in isolation (git worktrees, separate checkouts) converts silent filesystem corruption into visible merge conflicts. This is the prerequisite for parallel agent work. Without isolation, two agents editing the same file produce silent overwrites — the more dangerous failure mode because it looks like success.

### 4. Decompose by interface, not by file

Spec-driven decomposition assigns agents tasks with explicit file boundaries and interface contracts: "Task A modifies `auth/service.ts` interface; Task B modifies `ui/forms.ts` to use the new interface; Task C writes integration tests." File-boundary decomposition is mechanically enforceable; "do the auth part" is not. The spec is the coordination surface between agents.

### 5. Sub-agents specialize; the orchestrator synthesizes

A sub-agent optimized for test coverage will make different choices than one optimized for code style. Parallel specialization is a feature, not a problem. The orchestrator's job is synthesis — merge the specialized outputs, resolve conflicts, verify the whole. Trying to make one agent do everything is the path to mediocre results on all dimensions.

### 6. Circuit breakers over infinite loops

Magentic-One's "stuck-counter" mechanism: if an agent loops more than twice on the same subtask without forward progress, it reflects, replans, and hands the task to another approach. This converts infinite loops into bounded failures. Any agentic system without a stuck-counter or equivalent will eventually infinite-loop in production.

### 7. Output contracts are execution state, not polish

The final response is a handoff artifact. It must expose the task state clearly enough that a reviewer or another agent can continue without reconstructing the whole transcript. For coding work, the minimum contract is: objective, files changed, what changed, verification run, result, remaining risks, and next safe step. A polished paragraph is not a contract if it hides scope, evidence, or unresolved risk.

### 8. Autonomy is bounded by reversibility, blast radius, and verifiability

Agentic coding should not require approval for every safe edit. That defeats the purpose of an agent. But autonomy must be explicitly bounded: reversible, in-scope, and verifiable changes can be executed; dependency additions, public API changes, destructive operations, production actions, and broad refactors require a stop, dry-run, or operator authorization.

---

## §The Rubric

### Dimension 1 [review] — Plan quality

Does the agent produce a real plan before executing, or just start writing code?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Plan names: (a) what files will change, (b) what interfaces will be modified, (c) what the verify target is. Plan is produced before the first code edit. Human reviews and approves before execution begins. |
| **4 — Good** | Plan produced before execution. Names files and high-level approach. Verify target is implied but not fully specified. |
| **3 — Adequate** | Some planning happens but it's mixed with execution. Agent starts typing before the full scope is clear. |
| **2 — Poor** | "Plan" is one sentence. No file boundaries. No verify target. Agent improvises the approach during execution. |
| **1 — Failing** | No planning. Agent receives task and immediately begins editing. |

**Test**: show the agent a non-trivial task (3+ files, 1 interface change). Does it produce a structured plan before touching any file?

---

### Dimension 2 [review] — Verify-against-reality quality

Does the agent verify the real product, or just the internal consistency of its own work?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Each mode has an explicit, named real-product verify target (npm publish → curl registry; UI change → browser/Playwright; API change → integration test against running server). Verify runs after execution. Pass/fail is binary and grounded. |
| **4 — Good** | Verification exists and usually hits the real product. Occasionally falls back to compile/lint as the final signal. |
| **3 — Adequate** | Verification is test-suite pass. Tests cover the change but don't verify production behavior. Agent treats "tests pass" as done. |
| **2 — Poor** | Verification is "type-check passed" or "no linter errors." Agent declares done at the first automated signal. |
| **1 — Failing** | No verification. Agent declares done when the edit is complete. |

**Test**: for the most common task type, what is the last thing the agent checks before declaring done? If the answer is a compiler or linter, the verify step is inadequate.

---

### Dimension 3 [review] — Task decomposition quality

When the task requires changes to multiple files or systems, does decomposition happen explicitly and before work begins?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Decomposition produces subtasks with explicit file boundaries and interface contracts. Each subtask is independently verifiable. Decomposition is produced as an artifact before any subtask begins. |
| **4 — Good** | Decomposition names major work areas. File boundaries mentioned. Subtask ordering clear. No formal contract but experienced agents can work from it. |
| **3 — Adequate** | Agent lists "things to do" but without clear file boundaries. Ordering is implied. Works for simple tasks; breaks for complex ones. |
| **2 — Poor** | Decomposition is feature-level ("implement the auth flow") without sub-task detail. |
| **1 — Failing** | No decomposition. Agent treats multi-file changes as one monolithic task. |

**Test**: give a task touching 4+ files. Does the agent produce subtasks with file boundaries, or does it make changes incrementally with no advance structure?

---

### Dimension 4 [gate] — Isolation and coordination (parallel agents)

When multiple agents work in parallel, are they isolated from each other and coordinated at merge time?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Each agent works in a git worktree (or equivalent isolated checkout). File-boundary specs prevent overlapping writes. Merge happens after subtasks complete, with conflict resolution protocol. Silent overwrites are impossible by construction. |
| **4 — Good** | Isolation exists (worktrees or separate directories). Specs aren't always perfectly non-overlapping. Merge conflicts happen occasionally but are visible and resolved. |
| **3 — Adequate** | Agents coordinate by convention (e.g., naming files they'll edit) rather than by hard isolation. Works with small teams; fails with 4+ agents. |
| **2 — Poor** | Multiple agents editing the same repo without isolation. Overwrites and conflicts caught by luck. |
| **1 — Failing** | No coordination at all. Agents overwrite each other and the most-recently-completed agent wins. |

**Test**: run two agents on overlapping files simultaneously. Do they produce a merge conflict (safe failure), or does one silently overwrite the other (silent corruption)?

---

### Dimension 5 [gate] — Stuck-counter / circuit breaker

Does the system have a mechanism for detecting and recovering from loops?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Explicit stuck-counter or equivalent: after N repetitions without forward progress, the agent pauses, reflects, replans, and escalates to operator if replanning doesn't help. Counter is mechanized (not depends on the agent's own judgment). |
| **4 — Good** | Token budget or step-count limit acts as a natural circuit breaker. Agent doesn't infinite-loop, but recovery is abrupt (timeout) rather than graceful (replan). |
| **3 — Adequate** | No explicit stuck-counter but operators intervene when loops are noticed. Loops are caught but not prevented. |
| **2 — Poor** | Loops happen and are sometimes not noticed for minutes or hours. Cost accumulates before intervention. |
| **1 — Failing** | No circuit breaker at all. Agent loops until human intervenes or tokens exhaust. |

**Test**: deliberately give the agent a circular task (task A requires task B requires task A). Does it detect the loop and escalate, or does it run until the token budget is empty?

---

### Dimension 6 [review] — Corrective feedback integration

Does the system carry forward learnings from prior sessions so the same errors don't recur?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Each session's errors are captured and promoted to durable corrections: per-agent memory → hard rule → harness (the 3-tier ladder from BORIS-feedback §B2). The same mistake doesn't recur after one correction cycle. |
| **4 — Good** | CLAUDE.md or equivalent is updated when agents err. Corrections compound over sessions. Same mistake rarely recurs. |
| **3 — Adequate** | Some corrections captured but inconsistently. Some mistakes recur. No systematic correction pipeline. |
| **2 — Poor** | Corrections are verbal ("don't do that again"). Nothing persists between sessions. |
| **1 — Failing** | No corrective feedback mechanism. Same mistakes recur indefinitely. |

**Test**: identify 3 recent agent errors. For each: is there a durable correction somewhere that prevents recurrence? If not, how would an agent avoid the same error next session?

---

---

### Dimension 7 [review] — Output contract quality

Does the agent's final response expose enough state to support review, continuation, and audit?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every non-trivial coding task ends with a stable contract: objective, files changed, what changed, verification run, result, remaining risks, next safe step. The report distinguishes verified facts from assumptions. |
| **4 — Good** | Final response is structured and includes changes plus verification. Risk or next-step fields occasionally omitted. |
| **3 — Adequate** | Summary is readable but not contract-grade. Reviewer can infer state, but continuation requires rereading parts of the transcript or diff. |
| **2 — Poor** | Summary is freeform. Files changed, verification, and risk are inconsistent or buried. |
| **1 — Failing** | Agent says "done" without a usable record of what changed or what evidence supports completion. |

**Test**: give the final response to a new agent with no transcript. Can it continue the work safely? If not, the output contract is underpowered.

---

### Dimension 8 [review] — Autonomy boundary quality

Does the agent know when it may act independently and when it must stop, dry-run, or ask?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Prompt or harness defines autonomous-safe actions vs. approval-required actions. Reversible, in-scope, verifiable edits proceed. Irreversible, broad, external, or unverifiable actions stop at a gate. |
| **4 — Good** | Boundaries mostly clear. Agent occasionally asks for confirmation when it could have safely acted, but does not overreach on high-risk actions. |
| **3 — Adequate** | Boundaries implied by task wording. Agent usually behaves well but sometimes expands scope under plausible reasoning. |
| **2 — Poor** | Agent infers autonomy from objective language. Scope creep and unnecessary approval requests both occur. |
| **1 — Failing** | No autonomy model. Agent either stalls on safe work or performs risky work without authorization. |

**Test**: give the agent a task that includes one safe edit and one tempting dependency/API change. Does it execute the safe edit and stop before the risky change?

## §Anti-patterns

### AP-01 — Verify-theater (self-check masquerading as PEV)

**Symptom**: Agent declares done after running tests or type checks. Tests pass; feature is broken in production. **Root cause**: "Does the code compile/test?" is a different question from "does the product work?" **Correction**: Name the real-product verify target before execution. For UI work: browser render. For API work: integration test against running server. For npm release: `curl registry.npmjs.org/<pkg>/<version>`.

### AP-02 — Plan-as-vibe

**Symptom**: Agent "plans" by saying "I'll start with the authentication layer." No file list. No interfaces. No verify target. Execution starts immediately. **Root cause**: Planning is treated as a warm-up, not a gate. **Correction**: Plan is an artifact. It has an interface-contract section, a file-list section, and a verify-target section. Execution doesn't begin until the plan is reviewed.

### AP-03 — Isolation theater

**Symptom**: Agents "agree" to work on separate parts of the codebase by convention. Two agents still edit `utils/helpers.ts` independently. The later one's work silently overwrites the first. **Root cause**: Coordination is behavioral (promises), not structural (file system isolation). **Correction**: Git worktrees or separate checkouts. The harness enforces file-boundary assignments. Overlap detection runs before agent launch, not after.

### AP-04 — Infinite-loop blindness

**Symptom**: Agent tries to fix a compilation error, introduces a new error, tries to fix that, circles back. 15 minutes and $2 of tokens later, an operator notices. **Root cause**: No stuck-counter. Agent has no mechanism for recognizing circular progress. **Correction**: Three-strike rule: if the last 3 attempts failed for the same class of reason, pause and escalate. Don't attempt a 4th variant without operator input.

### AP-05 — Scope creep under autonomy

**Symptom**: Given "fix the login bug," the agent refactors 4 files, updates 3 dependencies, and adds 2 new features. The login bug is fixed, but there are 6 new bugs. **Root cause**: No constraint on scope. Agent optimizes for code quality in the files it touches, not for minimal blast radius. **Correction**: Spec the scope boundary explicitly: "modify auth/session.ts and auth/login.ts only; do not refactor, do not add dependencies." The spec is enforced by the harness, not just requested.

### AP-07 — Output fog

**Symptom**: Agent completes a task with a polished summary but no clear file list, verification evidence, or remaining risk. **Root cause**: Final responses are treated as communication, not as handoff artifacts. **Correction**: Require the coding output contract: objective, files changed, what changed, verification run, result, remaining risks, next safe step.

### AP-08 — Autonomy without decision boundaries

**Symptom**: Agent treats "do what is needed" as permission to add dependencies, change APIs, or refactor adjacent systems. **Root cause**: The prompt grants objective-level autonomy without blast-radius limits. **Correction**: Define first-safe-phase execution. Let the agent act on reversible, in-scope, verifiable work; stop before irreversible or broad changes.

### AP-06 — Session amnesia

**Symptom**: Agent makes the same mistake it made last Tuesday. Correction was verbal; nothing durable captured it. **Root cause**: No corrective feedback pipeline. Corrections disappear when the session ends. **Correction**: After any agent error: write a memory entry. After 3 instances of the same error: promote to hard rule. The Boris loop: see Claude err → add to CLAUDE.md → next session, it doesn't happen.

---

## §Hard Tests

1. **The one-shot test**: give the agent a moderately complex task (3-5 files, one new interface). Does it plan, execute, and verify in one session without operator intervention? If it requires more than 2 mid-session corrections, the system lacks planning depth.

2. **The verify-reality test**: after the agent declares done, run the product manually. Did it actually work? If you're discovering bugs post-declaration regularly, the verify step is incomplete.

3. **The parallel corruption test**: run two agents simultaneously on overlapping file scopes. Does the system produce a conflict (safe failure) or silent corruption? The answer tells you whether isolation is structural or behavioral.

4. **The stuck-loop test**: give an agent a task that requires a tool it doesn't have. Does it loop retrying the tool call indefinitely, or does it recognize the loop and escalate within 3 attempts?

5. **The session-memory test**: identify an agent error from last week. Run a fresh session. Does the same error occur? If yes, the corrective feedback loop is broken.

6. **The scope test**: give an agent a one-line bug fix in a 2000-line file. After it's done, check the diff. Did it change only what was needed? Or did it "improve" 40 lines of surrounding code? Scope creep is a harness problem, not a model problem.

7. **The Yegge test**: would 10 instances of this agent, running in parallel on 10 different tasks, produce 10x the output of one — or would they produce 3x the output and 5x the merge conflicts? The answer tells you whether your decomposition and isolation are production-grade.

8. **The output-contract test**: after a completed task, hide the transcript and inspect only the final response. Can a reviewer identify objective, files changed, verification evidence, and remaining risk? If not, the agent's output is not handoff-safe.

9. **The first-safe-phase test**: give the agent a broad task with one obviously safe phase and one risky follow-on phase. Does it execute the safe phase and stop before the risky phase, or does it either stall entirely or overrun the boundary?
