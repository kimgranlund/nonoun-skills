---
date: 2026-05-31
status: research-verified
coverage: canonical
version: "1.0.0"
primary_sources:
  - "Soares, N., Fallenstein, B., Yudkowsky, E., & Armstrong, S. (2015). Corrigibility. AAAI Workshop on AI and Ethics. MIRI Technical Report."
  - "Anthropic (2026). Our framework for developing safe and trustworthy agents. anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents"
  - "Anthropic (2026). Measuring AI agent autonomy in practice. anthropic.com/research/measuring-agent-autonomy"
  - "Cloud Security Alliance (2026). Autonomy Levels for Agentic AI. cloudsecurityalliance.org"
  - "Komissarov, O. (2025). Agentic Foundation: Managing Entropy in AI Systems. Medium."
  - "Swarmia Engineering (2025). Five levels of AI coding agent autonomy. swarmia.com/blog"
  - "MindStudio (2026). How to Classify AI Agent Actions by Risk: A Four-Tier Framework. mindstudio.ai"
  - "TianPan (2026). Agent Blast Radius: Bounding Worst-Case Impact Before Your Agent Misfires in Production. tianpan.co"
  - "TianPan (2026). The Minimal Footprint Principle: Least Privilege for Autonomous AI Agents. tianpan.co"
  - "Huntley, G. (2025–2026). Inventing the Ralph Wiggum Loop. devinterrupted.substack.com"
---

# What Is Control Mode Design? — Foundational Knowledge Document

## The Core Claim

Control mode design is the discipline of matching how an agent receives its task definition to the task's entropy, reversibility, and blast radius. The common failure is treating prompts as a single dial between "vague" and "prescriptive." The actual design space has five distinct control modes — Instruction, Procedure, Rubric, Objective, and Mission — each appropriate for a different task class. Selecting the wrong mode causes predictable, avoidable failures: over-constraining discovery, under-constraining execution, or delegating judgment without a judgment surface.

The deeper claim, grounded in corrigibility research and Anthropic's agent autonomy framework, is that control mode selection is not a stylistic choice. It is a safety decision. A fully corrigible agent that never exercises independent judgment is brittle in open-ended work. A fully autonomous agent that always exercises judgment accumulates blast radius without check. The correct disposition lives between these poles, and it must be **specified per task**, not set once per agent. This is control mode design: calibrating agent autonomy to the work, not to the agent's general capability.

---

## 1. The Autonomy Spectrum: From Corrigible to Autonomous

In 2015, Nate Soares, Benja Fallenstein, Eliezer Yudkowsky, and Stuart Armstrong at MIRI published the foundational paper on corrigibility. Their definition: an agent is corrigible if it "cooperates with what its creators regard as a corrective intervention, despite default incentives for rational agents to resist attempts to shut them down or modify their preferences." This is not mere obedience; it is the structural property of remaining correctable.

The spectrum Anthropic's model spec derives from this work runs from **fully corrigible** (the agent always submits to its principal hierarchy — Anthropic, operator, user — even when disagreeing) to **fully autonomous** (the agent acts on its own values, acquires independent capabilities, and may resist correction). Both extremes are failure modes.

- **Fully corrigible** agents are dangerous when the principal hierarchy is wrong, corrupt, or under-informed. An agent that executes every instruction is only as safe as its operator.
- **Fully autonomous** agents are dangerous because we lack the tools to verify that their values and capabilities are trustworthy enough to warrant full independence. Premature trust in agent judgment exposes systems to compounding errors without recovery gates.

Anthropic's current position — reflected in Claude's training — places the appropriate disposition closer to the corrigible end during this period of AI development, while accepting limited independent judgment where human oversight would be clearly infeasible or where the instruction is clearly unethical. The practical formulation: **defer by default; exercise judgment only when the stakes are clear and the principal hierarchy is unreachable or mistaken**.

Control mode design operationalizes this principle task-by-task. Instruction and Procedure modes sit near the corrigible end: they define the path. Rubric and Objective modes allow bounded judgment. Mission mode is the highest autonomy level in the stack — appropriate when the problem space cannot be prespecified, but requiring explicit stop conditions and process constraints to remain tractable.

---

## 2. Task Entropy: The Primary Classification Variable

Task entropy is the number of plausible valid outcomes for a given input. It is the single most important variable in control mode selection.

The concept maps naturally to information-theoretic entropy: when an agent faces many equally plausible continuations, each step compounds uncertainty. When the path is narrow and well-defined, variance is low and deterministic control is achievable.

Practical classification by entropy level:

**Low entropy (deterministic):** The correct output is identifiable in advance. A typo fix, a rename, a targeted bug patch. These tasks warrant Instruction mode: constrain the action tightly, leave no room for "improvement adjacent to the task." Any variance here is a defect. Tool use (function calling with schema-validated inputs) is the extreme form of low-entropy control — it removes model-space variance entirely for the sub-task.

**Medium entropy (judgment-required):** Multiple valid solutions exist, but they are constrained by the domain, the architecture, and the team's values. An audit, a code review, a refactor toward an established pattern. These warrant Procedure mode (constrain the sequence of evaluation) or Rubric mode (constrain the judgment surface). The agent must exercise judgment, but that judgment must be grounded in visible criteria — not implicit taste.

**High entropy (open-ended):** The problem space is not fully specifiable in advance. "Turn this prototype into a publishable library." The decomposition, the scope, the prioritization — all require agent judgment. These warrant Objective mode (constrain the outcome, allow path judgment) or Mission mode (constrain the process, allow decomposition and execution judgment). High-entropy tasks require the most explicit process constraints because the model has the most room to accumulate error.

The key diagnostic: **specificity detail in the wrong place is the most common prompt failure.** Adding procedural detail to a high-entropy task suppresses the agent's ability to diagnose the problem correctly. Adding vague objective language to a low-entropy task invites scope creep. The correct prompt puts detail where variance must be eliminated, and relaxes detail where judgment must be exercised.

---

## 3. The Five Control Modes

These modes are defined fully in `prompt-control-modes.md` in this references folder. This section provides the theoretical grounding for why the five modes exist as a set.

The modes form a gradient across two axes simultaneously: **action specificity** (how precisely the action is defined) and **judgment delegation** (how much the agent decides vs. the prompter).

```
Mode             Action specificity    Judgment delegation    Risk if misapplied
─────────────────────────────────────────────────────────────────────────────────────
Instruction      Very high             None                   Locks in wrong path
Procedure        High (sequence)       Low                    Mechanize-bait
Rubric           None                  Constrained            Generic feedback
Objective        Low                   High (path only)       Scope explosion
Mission          None                  Full (decomp+exec)     Infinite loop
```

The modes are not ranked by "better" or "more advanced." Mission mode is not the goal; Instruction mode is not beginner play. Each mode is correct for exactly one class of task. The maturity signal is knowing which to apply, not defaulting to a single mode because it is comfortable.

One structural insight: **higher-autonomy modes require more explicit constraints on process and stopping, not fewer.** A Mission prompt without stop conditions is not powerful — it is broken. The additional freedom in mode selection must be balanced by additional harness around termination, blast radius, and verification.

---

## 4. Human-in-the-Loop Patterns: When Humans Enter the Loop

"Human in the loop" is not a property of an agent — it is a design decision about which events require a human gate. Anthropic's research on agent autonomy in practice (2026) found that:

- Approximately 73% of tool calls involve human oversight in some form
- Only 0.8% of agent actions are irreversible
- As users gain experience, they shift from per-action approval (~20% of sessions use full auto-approve for new users) to monitoring-and-intervening (~40%+ after 750 sessions)
- Claude initiates clarification requests more than twice as often on complex tasks as humans interrupt it — the agent's own uncertainty detection is the primary escalation mechanism

This data supports a staged model of human involvement:

**Pre-task gate:** Before a long autonomous sequence, confirm scope and verify target. This is the single most leverage human touch — it prevents the agent from executing a well-formed plan against the wrong objective.

**Checkpoint gate:** When an agent encounters ambiguity, reaches a decision boundary, or completes a phase, it should pause rather than resolve silently. Anthropic's Building Effective Agents guidance is explicit: "agents can then pause for human feedback at checkpoints or when encountering blockers." The checkpoint is not a failure mode; it is evidence the agent is calibrated.

**Escalation gate:** When an action is irreversible, high blast radius, or involves external systems (financial transactions, production writes, credential operations), the agent must stop and surface the decision. This is not optional autonomy — it is a required control surface. The decision boundary rule from `prompt-control-modes.md` applies directly:

```
Low blast radius + reversible + verifiable → act
High blast radius OR irreversible OR unverifiable → stop, dry-run, or ask
```

**Post-task verification:** Human review of completed outputs, particularly for PR creation, deployed changes, or published artifacts. Strong CI and grounded verification reduce — but do not eliminate — the need for human post-review.

The sophistication is in the calibration: which gate type, on which events, with what turnaround expectation. The Cloud Security Alliance's six-level autonomy taxonomy formalizes this: Level 1 (explicit approval for every action) through Level 4 (monitoring and exception handling only). Level 5 (full autonomy with strategic oversight only) is explicitly not recommended for enterprise deployment, as the control mechanisms required do not yet exist.

---

## 5. Reversibility and Blast Radius: The Safety Gate Calculus

Reversibility is the most operationally useful safety variable for control mode design. Unlike "risk" (which requires judgment about probability and impact), reversibility is often binary and assessable in advance.

TianPan's agent blast radius framework (2026) defines blast radius as "the worst action this agent can take, given the tools and permissions it currently holds." This framing is deliberate: it is not about the expected action, but the worst-case action given the current permission scope. The practical implication is that **removing unnecessary permissions is more effective than adding guardrails** — guardrails operate on model reasoning, which is probabilistic; permission removal operates at the harness layer, which is deterministic.

The four-tier classification by reversibility:

| Tier | Characteristics | Gate required |
| --- | --- | --- |
| Read-only | No state change, fully reversible | None — log and proceed |
| Reversible write | State changed, can be undone | Proceed with audit trail |
| External action | Third-party receives; reversal is coordination-dependent | Staging queue or dry-run |
| Irreversible | Deletion, financial, credential change | Human approval, no exceptions |

The interaction of blast radius and reversibility creates a 2×2 that surfaces the non-obvious cases:

- **Large blast radius + reversible:** Higher risk than it looks (rolling back a mass migration is costly), but still tractable with dry-run and phased execution.
- **Small blast radius + irreversible:** Lower risk than it looks, but still requires an explicit gate — the size of the action does not eliminate the permanence of the consequence.

The enforcement principle: **control tiers must be enforced at the harness layer, not the model layer.** System prompts alone cannot prevent misuse; the harness must intercept tool calls before execution, independent of model decisions. This is the structural argument for capability-scoped tool grants rather than broad permission grants with model-level instructions to be careful.

---

## 6. Tool Use as Deterministic Control Rail

Function calling (tool use) is often treated as a feature — a way to give agents capabilities. The more precise framing: **tool use is a control mode for sub-tasks.** When an agent executes a structured tool call with schema-validated inputs and deterministic outputs, it has temporarily exited the probabilistic reasoning space and entered a deterministic execution space.

This boundary matters for control mode design because it means:

- Tool calls should be the preferred implementation mechanism for any sub-task that is low-entropy (verifiable, deterministic, schema-definable). The tool call imposes Instruction-mode constraints on the sub-task even when the parent task is operating in Rubric or Objective mode.
- The reliability of tool-using agents is disproportionately determined by the tool layer, not the reasoning layer. "Most AI agent failures do not trace back to bad reasoning; the model understands the task but calls the wrong tool, passes malformed arguments, or encounters unhandled errors." The tool interface is the production reliability surface.
- Output shape is a stronger reliability lever than output content. Well-defined tool schemas constrain the distribution of agent behaviors more effectively than prose instructions.

The minimal footprint principle applies with particular force to tools: grant only the tools the current task requires, not tools the agent might need in the future. Runtime credential scoping (task-scoped tokens with short TTL, granted per-operation and revoked on completion) is the rigorous implementation of this principle.

The Ralph Wiggum Loop — Geoffrey Huntley's agentic iteration pattern (2025) — demonstrates the complementary insight: fresh-context resets between iterations prevent "context rot" (compounding reasoning errors from accumulated conversation history) and make each loop iteration independently deterministic given its inputs. The loop structure imposes procedural control on a task that would otherwise be a single open-ended mission, recursively applying lower-entropy control modes at each iteration.

---

## 7. The Minimal Footprint Principle

Anthropic's minimal footprint principle is the synthesis of the above into a single behavioral norm for agents: request only necessary permissions, prefer reversible over irreversible actions, avoid retaining sensitive data beyond immediate needs, and confirm scope when uncertain.

This principle cannot be implemented by model-level instructions alone. It requires structural enforcement at the harness layer:

- **Task-scoped credentials:** Rather than persistent API keys with broad access, mint short-lived credentials scoped to the specific operation. Revoke on task completion.
- **Tiered permission escalation:** Read-only by default → task-scoped write on explicit grant → external API calls on user authorization → broad system access on senior approval.
- **Reversibility preference:** When two approaches accomplish the same objective, the agent should default to the approach that can be undone. This preference must be explicit in the prompt or system prompt — agents do not apply it automatically.
- **Scope confirmation under ambiguity:** When the task scope is unclear, stop and ask before proceeding. The cost of an unnecessary confirmation is a brief pause. The cost of proceeding on an incorrect scope assumption in a long agentic task is full rework or permanent damage.

The minimal footprint principle is the agent-level instantiation of least-privilege security practice. Its value is not primarily security (though that applies) — it is **predictability**. An agent with minimal footprint produces effects that are narrow enough to be verified, narrow enough to be reversed, and narrow enough to be understood.

---

## 8. Bringing It Together: The Control Mode Selection Decision

Given a task, the selection process is:

1. **Classify the entropy.** Is the correct output prespecifiable (low), constrained-but-multiple (medium), or open-ended (high)? This determines the mode family: Instruction/Procedure for low and medium; Rubric/Objective/Mission for medium-high and high.

2. **Assess blast radius and reversibility.** What is the worst-case impact of an error? Can it be undone? High blast radius or irreversible actions require explicit human gates, regardless of task entropy. A low-entropy task with irreversible consequences still requires a confirmation gate; the predictability of the action does not reduce the permanence of its consequence.

3. **Define the human gate pattern.** Pre-task, checkpoint, escalation, or post-task? The gate type should match the task duration and risk profile. Long tasks benefit from pre-task scope confirmation. High-entropy tasks benefit from checkpoint gates after planning but before execution. Irreversible actions require escalation gates regardless of confidence.

4. **Set the stopping condition.** Higher-autonomy modes (Objective, Mission) must name their stop condition before execution begins. "Execute only the first safe phase" is a stop condition. "Complete the task" is not. Without an explicit stop, agentic tasks expand to fill the available context and tool access.

5. **Specify the output contract.** What evidence will prove success? The verification target must be named before execution, not after. The output contract must expose objective, changes, verification evidence, risks, and next safe step — enough for a new agent or human reviewer to continue without rereading the transcript.

This five-step decision is the operational form of control mode design. It is not overhead — it is the minimum viable design for an agent that produces predictable, verifiable, safe behavior.

---

## Implications for This Skill Library

Control mode design directly shapes how skills in this library are authored and evaluated.

**[gate] — Blast radius and scope control (Dimension 4 in `prompt-control-modes.md`):** Every skill that produces agentic execution must include scope constraints that can be enforced at the harness layer. System prompt instructions to "be careful" are insufficient. Skills that involve writes, external calls, or credential use must specify the confirmation gate type.

**[review] — Entropy matching (Dimension 1):** The five modes in `prompt-control-modes.md` are not stylistic preferences. A skill that uses Mission mode for a deterministic task is actively harmful — it introduces variance where none is appropriate. Mode selection must be justified by the task's entropy class.

**[review] — Verification binding (Dimension 5):** The corrigibility research establishes that verification is a form of human oversight, even when automated. A skill that does not require grounded verification evidence before completion is operating as if the agent's self-assessment is reliable — which contradicts both the research and observed failure patterns.

**[hypothesis] — Autonomy progression:** As Anthropic's research shows, experienced users shift from per-action approval to monitoring-and-intervening. Skills that support progressive autonomy (starting at Level 1, graduating to Level 3 after demonstrated reliability) should be preferred over skills that require fixed oversight levels. This is a hypothesis pending empirical calibration within skill library usage.

**ROADMAP.md and §SelfAudit:** The corrigibility-autonomy spectrum implies that skill design decisions about autonomy level should be explicitly documented and revisited. A skill that starts as draft with low-autonomy defaults and graduates to stable should document why the autonomy level was chosen and what evidence would trigger a revision.

---

## Source Citations

1. Soares, N., Fallenstein, B., Yudkowsky, E., & Armstrong, S. (2015). **Corrigibility.** AAAI Workshop on AI and Ethics. Machine Intelligence Research Institute Technical Report. https://intelligence.org/files/Corrigibility.pdf

2. Anthropic (2026). **Our framework for developing safe and trustworthy agents.** https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents

3. Anthropic (2026). **Measuring AI agent autonomy in practice.** https://www.anthropic.com/research/measuring-agent-autonomy

4. Anthropic (2024). **Building effective agents.** (Via Simon Willison's summary.) https://simonwillison.net/2024/Dec/20/building-effective-agents/

5. Cloud Security Alliance (2026). **Autonomy Levels for Agentic AI.** https://cloudsecurityalliance.org/blog/2026/01/28/levels-of-autonomy

6. Komissarov, O. (2025). **Agentic Foundation: Managing Entropy in AI Systems.** Medium. https://medium.com/@olegkomissarov/agentic-foundation-managing-entropy-in-ai-systems-e5833e76c768

7. Swarmia Engineering (2025). **Five levels of AI coding agent autonomy, and why higher isn't always better.** https://www.swarmia.com/blog/five-levels-ai-agent-autonomy/

8. MindStudio (2026). **How to Classify AI Agent Actions by Risk: A Four-Tier Framework.** https://www.mindstudio.ai/blog/classify-ai-agent-actions-by-risk

9. TianPan (2026). **Agent Blast Radius: Bounding Worst-Case Impact Before Your Agent Misfires in Production.** https://tianpan.co/blog/2026-05-05-agent-blast-radius-bounding-worst-case-impact-production

10. TianPan (2026). **The Minimal Footprint Principle: Least Privilege for Autonomous AI Agents.** https://tianpan.co/blog/2026-04-17-minimal-footprint-principle-autonomous-ai-agents

11. Huntley, G. (2025–2026). **Inventing the Ralph Wiggum Loop.** Dev Interrupted (Substack). https://devinterrupted.substack.com/p/inventing-the-ralph-wiggum-loop-creator

12. AltersSquare (2026). **Tool-Calling Reliability for Agent Frameworks.** https://altersquare.io/tool-calling-reliability-agent-frameworks-measurements-architecture/
