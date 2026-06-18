---
date: 2026-05-23
status: draft
version: "0.1.0"
---

# Prompt Control Modes — Best Practices Rubric

**A prompt is a control surface for agency.** It does not merely tell an agent what to do; it determines how much judgment the agent may exercise, where variance is allowed, where variance is dangerous, and what must be verified before the agent can claim success.

The common mistake is treating prompt detail as a single dial: "more prescriptive" vs. "less prescriptive." The better model is to ask **what kind of control the task needs**:

- Narrow tasks need action constraints.
- Broad tasks need judgment constraints.
- Agentic tasks need process constraints.
- Risky tasks need scope constraints.
- Production tasks need verification constraints.

Prompt control modes give skill authors a shared vocabulary for choosing the right prompt shape for the task's entropy, risk, and desired agent autonomy.

**Companion docs:**

- `skills-authoring.md` (this folder) — how prompts become reusable skills
- `agentic-coding.md` (this folder) — PEV, decomposition, circuit breakers, and coding execution
- `security-and-scope-containment.md` (this folder) — autonomy boundaries, blast radius, and confirmation gates
- `progressive-context-construction.md` (this folder) — when context enters the task
- `evaluation-workflows.md` (this folder) — how prompt behavior is tested and regression-gated

---

## §The Problem

Prompt authors often choose the wrong control mode for the work:

1. **Over-open prompts for deterministic work** — "clean this up" causes broad rewrites when a one-line fix was needed.
2. **Over-prescriptive prompts for ambiguous work** — the prompt locks the agent into an execution path before it has diagnosed the system.
3. **Rubric-free delegation** — the agent is asked to "make it production-ready" without being given, or asked to create, a definition of production-ready.
4. **Unbounded autonomy** — the agent is trusted to "figure it out" but no stop condition, blast-radius boundary, or verification target is named.
5. **Plan without execution rights** — the agent produces a reasonable plan but stalls because the prompt does not say whether it may execute the first safe phase.
6. **Execution without evidence** — the agent makes changes and summarizes them, but the prompt never required real verification.

The result is avoidable variance. The model may be capable, but the prompt gave it the wrong operating mode.

---

## §First Principles

### 1. Specificity should match task entropy

Task entropy is the number of plausible valid outcomes. A typo fix is low entropy. "Improve the architecture" is high entropy. Low-entropy work should constrain action tightly. High-entropy work should constrain judgment and process, not prematurely constrain implementation.

The mistake is not being detailed or being concise. The mistake is putting detail in the wrong place: action details for ambiguous work, or vague objective language for deterministic work.

### 2. Prescriptive prompts reduce variance; they do not create judgment

Prescriptive prompts are appropriate when the correct solution shape is already known. They are poor at discovery because they suppress the agent's ability to find a better decomposition. Use prescription to keep an agent on rails, not to ask it to design the rails.

### 3. Open-ended prompts need sharp intent

Open-ended does not mean vague. A good open-ended prompt relaxes the path while keeping the intent, constraints, and evaluation lens clear. "Review this package from the perspective of a platform-native Web Components design system" is open-ended but focused. "Make this better" is not.

### 4. Rubrics turn taste into inspectable judgment

When the output could be valid in several different forms, the agent needs a rubric. The rubric may be supplied by the user or created by the agent before execution. Either way, the rubric must be visible before major decisions are made; otherwise the agent optimizes against implicit taste.

### 5. Agentic prompts constrain process, scope, and verification

For agentic coding, the prompt should not micromanage every edit. It should constrain the operating loop: inspect → diagnose → plan → execute safe phase → verify → report. The agent needs room to solve the problem, but not room to expand scope, skip verification, or loop indefinitely.

### 6. Autonomy requires a decision boundary

A prompt that says "do whatever is needed" is not autonomy; it is missing scope. Useful autonomy is bounded by blast radius, reversibility, and verifiability:

```txt id="pc-001"
Low blast radius + reversible + verifiable → act
High blast radius OR irreversible OR unverifiable → stop, dry-run, or ask
```

### 7. The output contract is part of the prompt

The expected response shape is not cosmetic. It determines whether the result can be reviewed, scored, merged, or handed off. A prompt without an output contract invites the agent to bury state in prose. A good output contract exposes objective, scope, changes, verification, risk, and next safe step.

### 8. Verification must be named before execution begins

The agent should know what evidence will prove success before it starts. If the verify target is not named early, the agent will often treat completion of edits as completion of the task.

---

## §Prompt Control Modes

### Mode 1 — Instruction prompt

Use when the task is narrow, deterministic, and low-risk.

```txt id="pc-002"
Rename `parseColor` to `parseOklchColor`.
Update all imports.
Do not change behavior.
Run the relevant tests.
```

**Control type:** constrain action.

**Best for:** renames, formatting, targeted bug fixes, import updates, small migrations.

**Risk:** if used for broad work, it locks the agent into a path before diagnosis.

---

### Mode 2 — Procedure prompt

Use when the method is known but the exact findings are unknown.

```txt id="pc-003"
Audit this component in this order:
1. Public attributes
2. Shadow DOM styling boundaries
3. Accessibility semantics
4. Event naming
5. Cleanup and lifecycle

Return findings before editing.
```

**Control type:** constrain sequence.

**Best for:** audits, reviews, checklists, migration passes, release preparation.

**Risk:** if the procedure is repeated and testable, it may be mechanize-bait and should move to a script or tool.

---

### Mode 3 — Rubric prompt

Use when quality matters more than a fixed method.

```txt id="pc-004"
Evaluate this skill against a rubric for:
- Activation precision
- Context loading discipline
- Tool inversion
- Verification target clarity
- Failure recovery

Rank findings by severity and cite evidence.
```

**Control type:** constrain judgment.

**Best for:** architecture review, design systems review, skill review, prompt evaluation, tradeoff analysis.

**Risk:** weak rubrics produce generic feedback. Each dimension must have observable evidence.

---

### Mode 4 — Objective prompt

Use when the outcome is clear but the path requires agent judgment.

```txt id="pc-005"
Make this component production-ready as a design-system primitive.
Preserve the public API unless there is a clear reason to change it.
Before editing, identify the highest-risk gaps and the verify target.
```

**Control type:** constrain outcome.

**Best for:** bounded implementation work, component hardening, test additions, documentation improvement, focused refactors.

**Risk:** without scope boundaries, objective prompts can turn into broad rewrites.

---

### Mode 5 — Mission prompt

Use when the task requires decomposition, rubric creation, and execution planning.

```txt id="pc-006"
Analyze this package and create a plan to turn it into a publishable Web Component library.
First build the success rubric, then inspect the current state, identify gaps, propose phases,
and execute only the first safe phase.
```

**Control type:** constrain process.

**Best for:** open-ended refactors, skill creation, library hardening, system design, multi-step agentic coding tasks.

**Risk:** mission prompts need stop conditions. Otherwise the agent may continue expanding the work after the useful first phase is complete.

---

## §The Rubric

### Dimension 1 [review] — Entropy matching

Does the prompt's control mode match the task's ambiguity?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Low-entropy tasks use instruction/procedure prompts. High-entropy tasks use rubric/objective/mission prompts. The prompt does not overconstrain discovery or underconstrain execution. |
| **4 — Good** | Control mode mostly matches task entropy. One minor mismatch, but not enough to produce bad behavior. |
| **3 — Adequate** | Prompt works but relies on model judgment to compensate for under-specified or over-specified areas. |
| **2 — Poor** | Prompt is too vague for deterministic work or too prescriptive for exploratory work. Agent behavior is inconsistent. |
| **1 — Failing** | Prompt mode is inverted: open-ended where rails are required, prescriptive where diagnosis is required. |

**Test**: classify the task as low, medium, or high entropy. Does the prompt constrain the right thing: action, sequence, judgment, outcome, or process?

---

### Dimension 2 [review] — Agency boundary clarity

Does the prompt state what the agent may decide vs. what is fixed?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Prompt clearly separates fixed requirements, agent-decidable choices, and forbidden actions. Agent knows when to act, when to dry-run, and when to stop. |
| **4 — Good** | Most boundaries clear. One or two assumptions left to agent judgment but low-risk. |
| **3 — Adequate** | Boundaries implied by wording. Agent usually behaves correctly but may expand scope in complex cases. |
| **2 — Poor** | Agent must infer whether it may edit, refactor, add dependencies, change APIs, or run destructive commands. |
| **1 — Failing** | No agency boundary. Agent decides scope, method, blast radius, and completion criteria unilaterally. |

**Test**: after reading the prompt, can the agent answer: what can I change, what must I preserve, what requires confirmation?

---

### Dimension 3 [review] — Rubric presence for judgment-heavy work

When the task requires judgment, is the judgment surface explicit?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Prompt provides a rubric or requires the agent to build one before execution. Rubric dimensions are observable and tied to success. |
| **4 — Good** | Evaluation criteria present but not fully scored. Agent can still make grounded decisions. |
| **3 — Adequate** | Some criteria named, but several important values are implicit. |
| **2 — Poor** | Judgment-heavy task has no rubric. Agent optimizes for generic quality. |
| **1 — Failing** | Task depends on taste, architecture, or risk tradeoffs, but the prompt gives no value system. |

**Test**: if two agents produce different valid solutions, does the prompt contain enough criteria to decide which one is better?

---

### Dimension 4 [gate] — Scope and blast-radius control

Does the prompt bound the possible damage of autonomous action?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Scope includes allowed files/systems, forbidden changes, dependency rules, API compatibility rules, and confirmation gates for irreversible actions. |
| **4 — Good** | Scope mostly clear. Destructive actions gated. Some adjacent-file exploration allowed but not editing. |
| **3 — Adequate** | Scope described in natural language. Agent can infer boundaries but enforcement is behavioral. |
| **2 — Poor** | Prompt asks for broad outcome with no blast-radius limits. Scope creep likely. |
| **1 — Failing** | Prompt explicitly authorizes unbounded changes for a bounded task. |

**Test**: give the prompt to an agent and inspect the diff. Did it change only what was necessary, or did it improve unrelated code?

---

### Dimension 5 [review] — Verification binding

Does the prompt require evidence before completion?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Verify target named before execution. Verification is grounded in real product state where possible. Agent cannot claim done without reporting evidence. |
| **4 — Good** | Verification required, but target may be chosen during execution rather than before. |
| **3 — Adequate** | Prompt says to run tests/checks but does not distinguish internal checks from real-product verification. |
| **2 — Poor** | Verification implied but not required. Agent may summarize changes without evidence. |
| **1 — Failing** | No verification requirement. Completion means edits were made. |

**Test**: what is the last external signal the agent must read before declaring done? If none, verification is not bound.

---

### Dimension 6 [review] — Output contract quality

Does the prompt make the result reviewable and handoff-safe?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Output contract includes objective, diagnosis, plan/changes, verification evidence, risks, and next safe step. Format is stable across invocations. |
| **4 — Good** | Output has stable sections. One useful field missing, usually risk or next step. |
| **3 — Adequate** | Output is readable but not contract-grade. Reviewers must infer status from prose. |
| **2 — Poor** | Output is a freeform summary. Verification, scope, and risk are buried or absent. |
| **1 — Failing** | Output does not reveal what happened, what was verified, or what remains uncertain. |

**Test**: can a different agent continue the work from the output alone without rereading the entire conversation?

---

## §Prompt Templates

### Prescriptive execution template

```txt id="pc-007"
Objective:
[Exact change]

Scope:
- Allowed files: [list]
- Forbidden changes: [list]

Rules:
- Preserve public API.
- Do not add dependencies.
- Prefer the smallest correct change.

Verification:
- Run [specific check].
- Do not claim done unless it passes.

Output:
- Files changed
- What changed
- Verification result
- Remaining risk, if any
```

### Rubric-first review template

```txt id="pc-008"
Objective:
Evaluate [artifact] for [domain-specific quality].

Before judging:
1. Build or apply a rubric with observable dimensions.
2. Inspect the artifact against each dimension.
3. Rank findings by severity.

Do not edit the artifact unless explicitly asked.

Output:
- Rubric
- Findings with evidence
- Severity
- Recommended next action
```

### Agentic coding template

```txt id="pc-009"
Objective:
[Outcome]

Mode:
Agentic coding — inspect, diagnose, plan, execute first safe phase, verify.

Process:
1. Restate the objective.
2. Inspect relevant files before editing.
3. Identify root cause or architectural gap.
4. Name the verify target.
5. Propose the smallest safe plan.
6. Execute only the first safe phase.
7. Verify against real state where possible.
8. Report results using the output contract.

Decision boundary:
- Act autonomously for reversible, in-scope, verifiable changes.
- Stop before dependency additions, public API changes, destructive operations, or broad refactors.

Output:
- Objective
- Diagnosis
- Plan
- Changes made
- Verification evidence
- Remaining risks
- Next safe step
```

---

## §Anti-patterns

### AP-01 — The vague objective

**Symptom**: "Make this better." Agent rewrites broadly or gives generic feedback. **Root cause**: the prompt names a desire, not an intent, rubric, or scope. **Correction**: name the evaluation lens, constraints, and output contract.

### AP-02 — The false rail

**Symptom**: prompt specifies exact steps for a problem that has not been diagnosed. **Root cause**: author confuses confidence in desired outcome with confidence in method. **Correction**: use rubric/objective mode first; prescribe execution only after diagnosis.

### AP-03 — Rubric theater

**Symptom**: agent creates a rubric with generic criteria: clarity, quality, maintainability. **Root cause**: prompt asks for a rubric but not observable evidence. **Correction**: each rubric dimension must define what evidence would prove a 5 vs. a 1.

### AP-04 — Autonomy without stop condition

**Symptom**: agent keeps expanding work: refactor, dependency update, docs, tests, cleanup. **Root cause**: mission prompt has no boundary for first safe phase or stop point. **Correction**: explicitly define stop conditions and confirmation gates.

### AP-05 — Verification afterthought

**Symptom**: agent decides how to verify only after editing, usually choosing the easiest check. **Root cause**: verify target not named before execution. **Correction**: require the verify target in the plan.

### AP-06 — Output fog

**Symptom**: agent returns a polished paragraph but the reviewer cannot tell what changed or what was verified. **Root cause**: prompt lacks an output contract. **Correction**: require structured fields for objective, changes, evidence, risk, and next step.

---

## §Hard Tests

1. **The entropy test**: classify the task before writing the prompt. If the task is low-entropy, does the prompt constrain action? If high-entropy, does it constrain judgment/process instead?

2. **The two-agent divergence test**: give the same prompt to two agents. If they produce wildly different outputs on a low-entropy task, the prompt is under-specified. If they produce the same shallow output on a high-entropy task, the prompt may be over-constrained.

3. **The scope-diff test**: after execution, inspect the diff. Every changed file should be explainable from the prompt's objective and scope. Unexplainable files indicate weak boundaries.

4. **The verify-before-edit test**: before the first edit, can the agent name what evidence will prove success? If not, the prompt has not bound verification.

5. **The continuation test**: hand the agent's final output to a new agent. Can the new agent continue without reading the whole transcript? If not, the output contract is insufficient.

6. **The approval-gate test**: insert an irreversible action into the task path. Does the prompt require dry-run and confirmation, or does the agent proceed because the objective sounds reasonable?

7. **The prompt shrink test**: remove one instruction from the prompt. Does behavior degrade? If not, that instruction may be dead weight. Repeat until every remaining line earns its keep.
