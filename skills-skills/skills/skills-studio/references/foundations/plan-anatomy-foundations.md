---
date: 2026-05-31
status: research-verified
coverage: canonical
version: "1.0.0"
primary_sources:
  - "Yao et al. (2023). ReAct: Synergizing Reasoning and Acting in Language Models. ICLR 2023. arXiv:2210.03629"
  - "Wang et al. (2023). Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models. ACL 2023. arXiv:2305.04091"
  - "Shinn et al. (2023). Reflexion: Language Agents with Verbal Reinforcement Learning. NeurIPS 2023. arXiv:2303.11366"
  - "Shen et al. (2023). HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in HuggingFace. NeurIPS 2023. arXiv:2303.17580"
  - "Zhuang et al. (2023). TaskBench: Benchmarking Large Language Models for Task Automation. NeurIPS 2024. arXiv:2311.18760"
  - "Wang et al. (2025). GAP: Graph-based Agent Planning with Parallel Tool Use and Reinforcement Learning. arXiv:2510.25320"
  - "Goldie et al. (2025). Plan Verification for LLM-Based Embodied Task Completion Agents. arXiv:2509.02761"
  - "Liang et al. (2025). A Subgoal-driven Framework for Improving Long-Horizon LLM Agents. arXiv:2603.19685"
---

# What Is Plan Anatomy? — Foundational Knowledge Document

## The Core Claim

A plan is the structural bridge between reasoning and action in an agentic system. Without plan anatomy — the explicit internal structure of goals, subgoals, assumptions, dependencies, constraints, checkpoints, tool calls, decision points, recovery paths, and completion criteria — an agent is executing a random walk that looks purposeful from the outside. With it, the agent can decompose work correctly, sequence tool use, expose its uncertainty, validate intermediate results, recover from failures, and know when the task is actually complete rather than when it feels done.

This matters because LLMs are not planners by default; they are next-token predictors. Left without plan structure, they produce reasoning that appears coherent but lacks the invariants that make complex tasks executable: they cannot verify intermediate state, they lose track of dependencies, they hallucinate progress, and they terminate prematurely when they run out of obvious next steps. Plan anatomy is not optional scaffolding — it is the mechanism by which a reasoning model becomes an executing agent. The research is unambiguous: structured planning improves task completion rates on every benchmark where it has been evaluated, from ReAct's original HotpotQA results (34% improvement over chain-of-thought alone) to the Reflexion framework's 97% AlfWorld success rate versus a ~50% reactive baseline.

**How plan anatomy relates to adjacent dimensions** — the four boundary concepts in this skill library are complementary but distinct:

- **Instructions** define _what_ the agent should do — the task, the constraints, the expected output
- **Control mode design** defines _how much autonomy_ the agent has — when to act, when to ask, when to escalate
- **Mechanization** turns repeatable patterns into executable structures — scripts, tools, hooks
- **Plan anatomy** defines the _internal shape of the work itself_ — how goals are decomposed, how dependencies are ordered, where checkpoints sit, what "done" means, and how failures are recovered from

An instruction can be perfectly written, the control mode correctly calibrated, and every repeatable step mechanized — and the system still fails if the plan structure is wrong. Conversely, excellent plan anatomy operates within whatever instructions, autonomy level, and execution infrastructure the other three dimensions provide. They do not substitute for each other.

---

## The Anatomy of a Plan: Nine Components

A plan is not a list of steps. A plan is a structured object with components that serve distinct functions. These nine components collectively distinguish a plan from a sequence of intentions:

### 1. Goal

The goal is the single, unambiguous statement of what success looks like for the whole task. It is _not_ the task description — task descriptions are often vague, multi-part, or underspecified. The goal is the agent's interpretation of the task description, resolved to a concrete, verifiable endpoint. A good goal has three properties:

- **Bounded scope**: it describes a final state, not an ongoing process ("the report is committed and CI passes" not "work on the report")
- **Verifiable**: an external observer can determine whether it is achieved without consulting the agent
- **Singular**: it captures one coherent outcome; compound goals must be decomposed

The failure to write an explicit goal is the root cause of most premature termination events. When a goal is implicit, the agent substitutes "I have taken reasonable actions" for "I have achieved the stated outcome" — producing the hallucinated-completion failure mode documented by Arize AI's production failure analysis and the "Are We Done Yet?" paper (arXiv:2511.20067).

### 2. Subgoals and Decomposition Structure

Subgoals are the intermediate states the agent must achieve on the path to the goal. They are not the same as steps: a step is an action; a subgoal is a verifiable state that results from one or more actions. This distinction is load-bearing.

The research on goal decomposition converges on three patterns:

**Least-to-Most ordering** (Zhou et al., 2022): decompose by increasing complexity, solving simpler subproblems first and using their outputs as context for harder ones. This achieves up to 99.7% success on compositional generalization benchmarks where standard prompting achieves 6%.

**Hierarchical decomposition**: major subgoals → minor subgoals → leaf actions, forming a tree. HuggingGPT (Shen et al., 2023) and HALO (arXiv:2505.13516) both use this structure to separate strategic intent (which capabilities to invoke) from tactical execution (how to invoke them).

**Subgoal-as-milestone** (Liang et al., 2025): treat subgoals as continuous progress indicators, not binary gates. The MiRA framework (arXiv:2603.19685) demonstrates that subgoals with partial credit — rather than hard pass/fail checkpoints — achieve 43% success on WebArena vs. 17.6% for GPT-4-Turbo without subgoal shaping. The Kendall tau correlation between subgoal completion and task success probability is 0.4585 (p < 0.001): the more subgoals completed, the more likely the task succeeds, monotonically.

TaskBench (Zhuang et al., 2023) finds that understanding tool dependencies between subgoals — the dependency structure of the decomposition — is significantly harder than identifying which tools to use. Edge prediction (dependency understanding) scores roughly 20% lower F1 than node prediction (tool selection) across all evaluated models. The decomposition structure is the hard part.

### 3. Assumptions

Assumptions are conditions the agent believes to be true but has not verified. Making them explicit serves two functions: it surfaces what the plan is contingent on, and it identifies what should be verified first before committing to expensive downstream actions.

Implicit assumptions are a primary cause of plan failure in production systems. The Arize AI failure taxonomy identifies "parametric bias overriding context" as a distinct failure mode: the agent assumes training-derived facts hold in the current context (database field names, API shapes, user permissions) and acts on them without checking. The assumption that a field is named `user_id` when the actual schema requires `customer_uuid` produces silent failures — the call returns an empty result set with no error, and the agent hallucinates progress.

A plan's assumption list should be resolved — checked against the environment — before the plan executes. This is the verify-before-proceed pattern, operationalized at plan inception rather than mid-execution.

### 4. Dependencies

Dependencies are ordering constraints between subgoals: subgoal B cannot begin until subgoal A has produced a specific output. Dependency structure determines whether steps can execute in parallel or must execute sequentially.

The GAP framework (Wang et al., 2025) represents task dependencies as directed acyclic graphs (DAGs) where edges represent input-output relationships between subtasks. The key insight: tasks within the same topological level can execute as a parallel batch; tasks at the next level wait for the batch to complete. This organization achieves up to 3.6x speedup over sequential plans on multi-tool tasks, as measured by LLMCompiler (reported in the LangChain planning agents post).

DynTaskMAS (arXiv:2503.07675) formalizes the dependency graph as G = (V, E, W) where vertices are subtasks, edges are dependencies, and weights combine computational complexity and context transfer cost. The weight structure lets a scheduler reason about which parallel paths are worth exploiting versus which have dependency overhead that makes sequencing cheaper.

The practitioner implication: every plan for a multi-step task should have an explicit dependency graph, even if only written informally. Plans without dependency structure default to fully sequential execution and sacrifice whatever parallelism the task allows.

### 5. Constraints

Constraints are invariants that cannot be violated during plan execution. They differ from subgoals (states to achieve) and assumptions (conditions believed true): constraints are boundaries the plan must stay within regardless of what intermediate states are reached.

Three constraint types appear consistently in production agent systems:

**Resource constraints**: token budget, API rate limits, execution time ceilings, cost caps. A plan without resource constraints can expand indefinitely as it encounters unexpected complexity. The "correction budget" in Reflexion-style systems (typically 2-3 retry cycles before escalating) is a constraint that prevents infinite self-correction loops.

**Scope constraints**: what the agent is and is not permitted to touch. The Replit production incident referenced in the Arize failure analysis — where an agent ignored instructions not to touch production databases — is a scope constraint violation. Scope constraints must be enforced structurally (the plan checks that each action falls within scope before executing it) not only instructionally.

**Safety constraints**: irreversible actions, data deletion, external communication. These warrant explicit confirm-before-proceed gates in the plan structure. Agentic design guidance consistently places human-in-the-loop checkpoints at irreversibility boundaries, not at arbitrary intervals.

### 6. Checkpoints and Verification Gates

A checkpoint is a point in the plan where the agent verifies intermediate state before proceeding. Checkpoints serve a specific function: they prevent error propagation. Without checkpoints, a failure at step 3 of a 10-step plan only surfaces at step 10, after 7 steps of work built on a wrong foundation.

Goldie et al. (arXiv:2509.02761) demonstrate the power of iterative verification in embodied task planning: a judge-planner loop where a Judge LLM critiques and a Planning Agent revises achieves 96.5% convergence within 3 iterations. 62% of defects are caught in a single pass; only 3.5% of sequences require more than 3 iterations. Error types caught include premature toggles, irrelevant objects, contradictions, and missing steps — all defects that would otherwise propagate silently to task completion.

The principle: checkpoints should appear at subgoal boundaries (verify the subgoal is achieved before starting the next one) and at irreversibility boundaries (verify assumptions before taking actions that cannot be undone). The SAVER framework (arXiv:2604.08401) formalizes this as "self-audited verified reasoning" — adversarial auditing of internal belief states before any action commitment.

### 7. Tool Calls and Action Specifications

Tool calls are the executable leaf nodes of the plan. A plan that specifies "search for X" is underspecified; a plan that specifies "invoke the web-search tool with query='X', max_results=5" is actionable. This distinction matters because:

- Underspecified actions invite hallucination at execution time (the agent invents arguments from training knowledge rather than plan context)
- Specified actions expose the dependency on tool availability — if the required tool is not in scope, the plan fails at verification time rather than execution time
- Specified actions enable pre-execution validation — argument types, required permissions, rate limit implications — before the action is taken

TaskBench's "parameter prediction" evaluation stage measures exactly this specification quality. It is the stage where open-source models show the largest performance gap versus frontier models, indicating that concrete action specification is a capability the plan structure must compensate for when the model's raw capability is limited.

### 8. Decision Points and Conditional Branches

Decision points are places in the plan where the next action depends on the result of a prior action. A flat plan that lists steps without decision points is not a plan — it is a script that assumes the environment cooperates. Real tasks require branching: if the tool call succeeds, proceed; if it returns an error, escalate or retry; if the result is ambiguous, request clarification.

The ReAct architecture (Yao et al., 2022) is fundamentally a mechanism for making decision points explicit at each step: Thought → Action → Observation → Thought → … The observation step creates a natural decision point before the next action. The limitation ReAct exposes is that each observation creates only local decisions; there is no global plan state that allows the agent to recognize when a pattern of local observations indicates the overall plan is infeasible.

Plan-and-Execute separates this: a high-level planner creates the decision tree upfront, and a low-level executor handles tactical decisions within each branch. The planner operates at the strategic level (what should happen and in what order); the executor operates at the tactical level (exactly how to make each step happen). GoalAct (arXiv:2504.16563) achieves a 12.22% average improvement on LegalAgentBench by maintaining a global plan updated with each observation — the global plan is the decision context that prevents local tactics from diverging from strategic intent.

### 9. Recovery Paths and Replanning Logic

Recovery paths specify what happens when a step fails. A plan without recovery paths has one failure mode for all errors: the agent either hallucinates that the step succeeded, loops attempting the same failed action, or terminates prematurely. All three are well-documented in production failure analyses.

Reflexion (Shinn et al., 2023) introduced verbal reinforcement learning as a recovery mechanism: on failure, the agent generates a natural-language reflection summarizing what went wrong and what it would do differently, stores it in episodic memory, and uses it as context for the next attempt. Results: 97% success on AlfWorld (vs. ~50% baseline), 91% pass@1 on HumanEval (vs. 80% for GPT-4 direct). The architecture: Actor → Evaluator → Self-Reflection → repeat.

However, Reflexion has a critical limitation identified in subsequent research: the "coherence trap" — the model making the original error shares the same blind spots as the model evaluating that error. Self-correction without external grounding does not reliably improve performance. The most effective recovery paths anchor in environmental feedback: test execution results, tool error codes, database query results. The agent reflects on factual evidence, not on its own opinion of its performance.

The practical structure for recovery paths: a correction budget (typically 2-3 retry cycles) with escalation logic when the budget is exhausted. Within the budget: diagnose the error type (is it a wrong argument? a wrong tool? a wrong subgoal?), revise the plan at the appropriate level (leaf revision for wrong arguments; branch revision for wrong subgoal; full replanning for wrong goal interpretation), re-execute, and checkpoint.

---

## The Reactive-Proactive Spectrum and Plan Selection

Not every task needs a full upfront plan. The planning literature identifies a spectrum:

**Fully reactive (ReAct)**: the agent generates the next action based only on current observations and no upfront plan. Good for exploration, discovery, and tasks where the path cannot be known until intermediate results are observed. Limitation: no global coherence — each step is locally reasonable but the sequence can diverge from the overall goal, especially over long horizons.

**Proactive planning (Plan-and-Execute, Pre-Act)**: the agent generates a complete plan before executing any steps. Good for tasks with known structure and stable environments. Pre-Act (arXiv:2505.09970) demonstrates that multi-step planning before action reduces compounding errors that accumulate in purely reactive approaches. Limitation: brittle to unexpected environment changes — a rigid upfront plan fails when the environment diverges from prediction.

**Adaptive replanning (GoalAct, DynTaskMAS)**: the agent maintains a global plan that updates with each observation. The plan is proactive but not rigid; it serves as a coherence anchor that guides tactical decisions without constraining them to a fixed script. This is the dominant production architecture for complex tasks because it combines the stability of planning with the adaptability of reactivity.

**Hybrid hierarchical (HuggingGPT, ReWOO)**: a strategic planner generates a high-level plan; tactical executors (which may themselves be reactive) handle each step. The planner is insulated from low-level execution details; the executors are insulated from strategic context. ReWOO enables variable passing between steps (referencing earlier outputs as `#E2`), solving the coordination problem that pure sequential planning cannot address.

The selection criteria: use reactive for open-ended exploration; use proactive planning for well-defined tasks with stable environments; use adaptive replanning for complex tasks in partially observable environments; use hierarchical decomposition when the strategic and tactical layers have fundamentally different information needs.

---

## Completion Criteria and the "Declare Done" Problem

The hardest problem in plan execution is not execution itself — it is knowing when to stop. The "declare done" problem appears in multiple research threads under different labels: premature termination, hallucinated completion, false positive task declaration, and trajectory degeneration.

The problem has two failure modes:

**Premature termination**: the agent stops when obvious next steps are exhausted rather than when the goal is achieved. The agent has taken reasonable-looking actions and cannot identify the next obvious step, so it declares completion. This is the most common failure mode in production agents, equivalent to 42-49% of failures in the WebArena subgoal analysis (Liang et al., 2025 — classified as "get stuck midway").

**Hallucinated completion**: the agent convinces itself it has achieved the goal based on its own assessment of its actions rather than on evidence from the environment. The agent that writes tests and then confirms the tests pass without running them is the canonical example. The GitHub issues referenced in this research document this pattern: an agent's local validation passes, CI passes, but the actual user flow is broken because the agent never ran the thing it built.

The solution is structural, not instructional. Completion criteria must be:

1. **Externally verifiable**: specified in terms of observable environment state, not agent self-assessment. "CI passes on main" is verifiable; "I believe the implementation is correct" is not.

2. **Specified upfront**: completion criteria written before plan execution cannot be retroactively adjusted to match whatever the agent happened to produce. Post-hoc completion criteria are the mechanism of hallucinated completion.

3. **Explicit about what "done" requires that "tried" does not**: the completion criteria must distinguish between "I executed all planned steps" (sufficient for some tasks) and "I verified that the execution produced the intended outcomes" (required for most non-trivial tasks).

The deepeval TaskCompletion metric (deepeval.com) operationalizes this as an LLM-as-judge metric that: (1) infers the intended goal of the trace, (2) evaluates whether the final output achieves that goal based on the trace, and (3) returns a binary pass/fail with reasoning. The key insight in its design: the evaluator reasons about the goal and the output independently of the agent's own self-assessment, preventing the coherence trap.

---

## Failure Mode Taxonomy for Plan Anatomy

The production literature converges on four categories of plan-level failure:

**1. Decomposition failures**: the goal is decomposed into subgoals that do not cover the original goal, contain logical contradictions, ignore critical dependencies, or are not independently executable. TaskBench shows this is the dimension most correlated with overall agent capability — GPT-4 outperforms competitors by ~10% on decomposition alone. Recovery: verify decomposition coverage before execution begins.

**2. Trajectory degeneration**: the agent loops on a failed step, oscillates between two states, or expands indefinitely without converging. Caused by missing completion criteria and missing recovery paths. The DynTaskMAS maximum-iteration threshold (N ≤ 3) with explicit termination when quality threshold or improvement bound ε is not met is the structural solution.

**3. Environment-plan mismatch**: the plan's assumptions about environment state prove false during execution (API schema changes, permissions missing, resource unavailable). Caused by unverified assumptions and no early assumption-checking step. Recovery: verify assumptions before committing to dependent steps; design recovery paths for common environment failures.

**4. Premature or hallucinated completion**: the agent declares the task done when it is not. Caused by missing external verification in completion criteria. The vision-based judge paper (arXiv:2511.20067) documents this for computer use agents — the agent misidentifies an intermediate state as completion because it does not have explicit criteria for what the final state should look like. Recovery: write completion criteria as externally checkable predicates before plan execution.

The Arize AI field analysis adds three tool-specific failure modes that interact with plan anatomy: hallucinated tool arguments (specifications were underspecified), API schema drift (assumptions about tool behavior were not re-verified), and instruction drift in extended sessions (plan context is lost as conversation grows, causing the agent to revert to training defaults). All three are addressable at plan structure level: argument specification at action nodes, assumption verification checkpoints, and plan context pinning at key intervals.

---

## Plan Representation Formats

A plan's structure must be both machine-executable and human-inspectable. The representation format determines whether the plan can be debugged, replanned, persisted across sessions, and passed between orchestrator and executor components.

Three formats in common production use:

**Structured JSON/Pydantic schemas**: the dominant machine-readable format. A plan object with fields for `goal`, `assumptions`, `steps` (each step carrying `id`, `description`, `tool`, `args`, `depends_on`, `completion_criteria`, `recovery`), `constraints`, and `done_criteria`. Grammar-constrained decoding guarantees schema compliance. Pydantic models validate types at runtime. This format is auditable, serializable, and passable between agents. The limitation: JSON plans tend toward flat structure, losing the hierarchical organization that complex tasks need.

**DAG representations**: for dependency-heavy tasks, the plan is a directed acyclic graph where nodes are tasks and edges are dependency relationships. GAP (Wang et al., 2025) and DynTaskMAS both use this format. DAG plans enable automated topological sorting to identify parallelizable task batches. The limitation: DAGs require explicit dependency reasoning at plan-creation time — they are harder to generate correctly than flat lists.

**Hierarchical outlines**: strategic subgoals as major nodes, tactical steps as leaf nodes. The format used by GoalAct and HuggingGPT. Human-readable, inspectable, debuggable. Can be generated in markdown with explicit parent-child relationships. The limitation: harder to execute mechanically — requires the executor to understand the tree structure.

The practitioner recommendation: use JSON for machine-to-machine plan passing; use hierarchical outlines for human review of plans before execution; use DAGs explicitly when the task has significant parallelization potential. All three representations should capture the same nine components; the format determines how the components are organized, not whether they are present.

---

## Implications for This Skill Library

Plan anatomy is the structural foundation beneath every skill that involves multi-step agent execution. The rubric dimensions in this library that touch planning translate directly to the nine components:

**`[gate]` dimensions from plan anatomy:**

- Goal explicitness: can the agent state a verifiable completion condition before starting?
- Dependency acknowledgment: does the plan identify which steps must precede which?
- Assumption surfacing: are unverified conditions listed before execution commits to them?

**`[review]` dimensions:**

- Decomposition quality: are subgoals independently verifiable, covering, and non-redundant?
- Recovery path adequacy: does the plan specify what happens on each anticipated failure mode?
- Completion criteria precision: is "done" defined in terms of externally checkable evidence?

**`[hypothesis]` dimensions:**

- Optimal planning depth: the right level of plan granularity for a given task type remains task-specific and has not been calibrated for this library's skill tasks. Hypothesis: skills invoking 5+ tool calls benefit from explicit dependency graphs; skills invoking 1-3 tool calls do not require them.

The `core-agent-loops` skill (v0.1.0) provides the loop-selection layer — which loop topology to use — while plan anatomy is the within-loop structure. These are complementary: loop topology determines the control flow mechanism; plan anatomy populates the plan object that flows through that mechanism. Skills that orchestrate agent work should produce plans conforming to the nine components above, regardless of which loop topology they operate within.

The `agentic-coding.md` rubric's verification dimensions and the `eval-foundations.md` completion criteria section are the most directly downstream of this document. Any rubric dimension in this library that evaluates whether an agent "knows when it is done" is a completion-criteria gate; any dimension that evaluates step ordering is a dependency gate; any dimension that evaluates error handling is a recovery-path gate. The nine-component anatomy provides the vocabulary for those labels.

---

## Source Citations

1. Yao, S., et al. (2022). "ReAct: Synergizing Reasoning and Acting in Language Models." ICLR 2023. https://arxiv.org/abs/2210.03629

2. Wang, L., et al. (2023). "Plan-and-Solve Prompting: Improving Zero-Shot Chain-of-Thought Reasoning by Large Language Models." ACL 2023. https://arxiv.org/abs/2305.04091

3. Shinn, N., et al. (2023). "Reflexion: Language Agents with Verbal Reinforcement Learning." NeurIPS 2023. https://arxiv.org/abs/2303.11366

4. Shen, Y., et al. (2023). "HuggingGPT: Solving AI Tasks with ChatGPT and its Friends in HuggingFace." NeurIPS 2023. https://arxiv.org/abs/2303.17580

5. Zhuang, Y., et al. (2023). "TaskBench: Benchmarking Large Language Models for Task Automation." NeurIPS 2024. https://arxiv.org/abs/2311.18760

6. Wang, Y., et al. (2025). "GAP: Graph-based Agent Planning with Parallel Tool Use and Reinforcement Learning." https://arxiv.org/abs/2510.25320

7. Goldie, A., et al. (2025). "Plan Verification for LLM-Based Embodied Task Completion Agents." https://arxiv.org/abs/2509.02761

8. Liang, J., et al. (2025). "A Subgoal-driven Framework for Improving Long-Horizon LLM Agents." https://arxiv.org/abs/2603.19685

9. Weng, L. (2023). "LLM Powered Autonomous Agents." Lil'Log. https://lilianweng.github.io/posts/2023-06-23-agent/

10. Kojima, T., et al. (2022). "Least-to-Most Prompting Enables Complex Reasoning in Large Language Models." https://arxiv.org/abs/2205.10625

11. "Are We Done Yet?: A Vision-Based Judge for Autonomous Task Completion of Computer Use Agents." (2025). https://arxiv.org/abs/2511.20067

12. Arize AI (2025). "Why AI Agents Break: A Field Analysis of Production Failures." https://arize.com/blog/common-ai-agent-failures/

13. LangChain (2024). "Plan-and-Execute Agents." LangChain Blog. https://www.langchain.com/blog/planning-agents

14. Zylos Research (2026). "Agent Self-Correction: From Reflexion to Process Reward Models." https://zylos.ai/research/2026-05-12-agent-self-correction-reflexion-to-prm
