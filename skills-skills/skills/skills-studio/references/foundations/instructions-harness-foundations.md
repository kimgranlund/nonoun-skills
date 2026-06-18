---
date: 2026-05-31
status: research-verified
coverage: canonical
version: "1.0.0"
primary_sources:
  - "Anthropic Engineering (2025). Best Practices for Claude Code. code.claude.com/docs/en/best-practices"
  - "Anthropic Engineering (2025). Effective Context Engineering for AI Agents. anthropic.com/engineering/effective-context-engineering-for-ai-agents"
  - "Anthropic Engineering (2025). Equipping Agents for the Real World with Agent Skills. anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills"
  - "Anthropic Engineering (2025). Effective Harnesses for Long-Running Agents. anthropic.com/engineering/effective-harnesses-for-long-running-agents"
  - "Anthropic Engineering (2025). How We Built Our Multi-Agent Research System. anthropic.com/engineering/multi-agent-research-system"
  - "OpenAI Research (2024). The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions. arxiv.org/html/2404.13208v1"
  - "Zhou et al. (2025). Agent Behavioral Contracts: Formal Specification and Runtime Enforcement for Reliable Autonomous AI Agents. arxiv.org/html/2602.22302v1"
  - "Cherny, Boris (2025). How Boris Uses Claude Code. howborisusesclaudecode.com"
  - "HumanLayer Blog (2025). Skill Issue: Harness Engineering for Coding Agents. humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents"
  - "Abdelnabi et al. (2025). Architectural Design Decisions in AI Agent Harnesses. arxiv.org/html/2604.18071v1"
---

# What Is Instructions & Harness Design? — Foundational Knowledge Document

## The Core Claim

A harness is not the model's wrapper — it is the model's operating context. The model brings probabilistic reasoning; the harness supplies identity, permissions, constraints, institutional memory, and feedback loops. The pivotal insight, documented by practitioners across every major agentic framework as of 2025–26, is that **two teams running the same model with different harnesses will achieve dramatically different outcomes**. In Terminal Bench evaluations, harness optimization alone moved the same Claude model from the 30th percentile to the top 5 without any model change whatsoever (HumanLayer, 2025). This is not a marginal effect — it is the primary lever.

The distinction that unlocks this is recognizing that instructions function differently from training. Instruction tuning modifies model weights, changing what the model "is." Harness instructions are declarative runtime context: they tell the model what role it is playing in this invocation, what it may and may not do, and what the verification conditions are. The harness does not override the model's probabilistic nature — it structures that nature so probabilistic reasoning operates within a deterministic frame. Understanding where that frame is tight (hooks, permissions) and where it is advisory (CLAUDE.md prose) is the central skill of harness design.

---

## 1. The Anatomy of a Harness

A harness is everything surrounding a model that enables it to behave as an agent. Boris Cherny, creator of Claude Code, puts it sharply: **"Agent = Model + Harness. If you're not the model, you're the harness."** The model alone is inert text-completion machinery. The harness provides:

- **Identity and operating scope** — system prompt / CLAUDE.md / AGENTS.md declare who the agent is, what codebase conventions apply, and what the session goals are
- **Tool ecosystem** — MCP servers, CLI access, and registered functions define the action surface
- **Execution environment** — filesystems, sandboxes, version control, and network constraints
- **Orchestration logic** — subagent spawning, routing protocols, task decomposition structures
- **Verification mechanisms** — tests, linters, hooks, Stop gates, and adversarial review subagents
- **Observability** — logging, audit trails, cost monitoring, and failure telemetry

These are not independent dials. Research by Abdelnabi et al. (2025), surveying 70 agent-system projects, found that deeper subagent coordination consistently co-occurs with persistence, summarization, and token budgeting — and stronger sandboxing co-occurs with approval flows and audit mechanisms. **Execution power and governance co-evolve architecturally.** You cannot increase agent capability without also designing its corresponding constraint layer.

---

## 2. System Prompts as Behavioral Harnesses: Structure Over Content

The instructional hierarchy in LLM systems is not just a security concern — it is the fundamental trust architecture. OpenAI's Instruction Hierarchy paper (2024) demonstrated that models trained to treat system prompts as Priority 0 (developer-controlled) versus user messages as Priority 10 showed 63% improvement in system prompt extraction robustness, with 30%+ generalization to unseen attacks. But this hierarchy does more than defend against injection — it describes the semantic contract of the harness.

What practitioners have learned empirically is that **harness structure shapes agent behavior more than harness content**. This is counterintuitive but replicable:

- A CLAUDE.md that is too long causes Claude to ignore the rules buried in the middle, because frontier LLMs weight the periphery (beginning and end) most heavily (HumanLayer, 2025)
- A CLAUDE.md with 150+ entries shows measurably worse instruction-following than one with 30 targeted entries, even when the longer version contains strictly more correct guidance
- Hooks are deterministic where CLAUDE.md prose is advisory — they guarantee the action fires regardless of whether the model "decides" to follow instructions in that context window

The practical implication: every line in a harness file should be traceable to a specific past failure. The Addyosmani.com formulation — **"every line in a good AGENTS.md should be traceable back to a specific thing that went wrong"** — is the correct design philosophy. Harness files grow by learning from failures, not by anticipating all possible rules upfront.

### The Three-Tier Authority Model

| Tier | Mechanism | Reliability | Use for |
| --- | --- | --- | --- |
| **Deterministic gates** | Hooks, sandbox permissions, Stop hooks | Guaranteed | Destructive-action prevention, mandatory formatting, CI gates |
| **Structured instructions** | CLAUDE.md / AGENTS.md | High (degrades with length) | Project conventions, architecture constraints, non-obvious patterns |
| **Advisory guidance** | Session prompts, task descriptions | Probabilistic | Task-specific framing, effort calibration, goal clarification |

---

## 3. What the Harness Declares vs. What the Model Knows

There is a crucial epistemic distinction between what a model **knows** (from pretraining and instruction tuning) and what a harness **declares** (from the system prompt and supporting files). This distinction governs what belongs in a harness and what does not.

**Do not put in the harness:**

- Standard language conventions the model already follows correctly without prompting
- File-by-file codebase descriptions (the model can read files on demand)
- API documentation the model was trained on
- Style guidelines that deterministic linters enforce

**Do put in the harness:**

- Bash commands the model cannot guess from file structure alone (e.g., "use bun, not npm")
- Code style rules that diverge from language defaults your team chose deliberately
- Testing patterns specific to your test runner and fixture conventions
- Repository etiquette (branch naming, PR conventions, commit message format)
- Architectural decisions and their rationale (so the model doesn't undo them)
- Developer environment quirks — required env vars, non-obvious service dependencies
- Common gotchas that have caused regressions before

The Anthropic best-practices doc states the test precisely: **"For each line, ask: 'Would removing this cause Claude to make mistakes?' If not, cut it."** Bloated harness files are not neutral — they cause real degradation because important rules get lost in noise.

---

## 4. Negative Constraints Are More Powerful Than Positive Ones

In probabilistic systems, the most effective behavioral specification is negative. Telling a model what NOT to do is more durable than telling it what TO do, because positive instructions can be satisfied in multiple ways while negative constraints eliminate entire possibility spaces.

This shows up across the research:

- **Agent Behavioral Contracts** (Zhou et al., 2025) formalizes this: their framework distinguishes _hard invariants_ (must never be violated) from _soft invariants_ (should hold, with recovery). Hard invariants correspond to negative constraints. Experimental results across 1,980 sessions show 88–100% hard constraint compliance, with drift bounded below 0.27.
- **Prompt injection design patterns** (Willison, 2025; ArXiv 2506.08837) show that the most robust defenses against injection are structural negatives: agents that "must not be able to invoke tools that can break integrity or confidentiality" are more durable than agents told to "verify input trustworthiness before acting."
- **Constraint decay research** (ArXiv 2605.06445) demonstrates that positive behavioral instructions erode across longer sessions, while hard constraint framing ("never write to migrations/") degrades much more slowly.

**Architectural anti-patterns to eliminate via negative constraints:**

1. **The Monolithic Mega-Prompt** — overloading a single agent with hundreds of instructions it cannot reliably follow; solution: split into focused subagents
2. **All-or-Nothing Autonomy** — giving agents either full permission or constant interruption; solution: pre-allow common safe operations, block destructive ones via hooks
3. **Invisible State** — relying on the LLM to remember what happened; solution: explicit external state files with defined read/write patterns
4. **The Trust-Then-Verify Gap** — assuming plausible-looking output is correct; solution: mandatory verification as a Stop hook, not a courtesy step

The deeper principle: **in a probabilistic system, what you block is more reliable than what you request.** Use hooks for blocking. Use CLAUDE.md for requesting.

---

## 5. Progressive Disclosure: Cold-Start Surface vs. Deep Reference Loading

One of the most consequential advances in harness design is the separation of skill discovery from skill loading. The naive approach — put all domain knowledge in the system prompt — creates "context rot": as the prompt grows, instruction-following quality degrades linearly for frontier models and exponentially for smaller models.

Anthropic's Agent Skills architecture (2025) formalizes the correct pattern. Skills implement a three-tier loading model:

1. **Discovery layer** (always loaded): Name and description only — ~80 tokens per skill, allowing an agent to be aware of dozens of skills for less context than a single activated skill consumes
2. **Activation layer** (loaded on relevance): Full SKILL.md content — loaded only when the agent determines the skill applies to the current task
3. **Reference layer** (loaded on demand): Supporting documents, schemas, worked examples — retrieved as needed during execution

This mirrors effective human cognition: we index information in external systems (file names, book titles, directory structure) rather than maintaining full recall of everything. The file system metadata — folder structure, naming conventions, timestamps — provides orientation signals that guide retrieval without consuming context budget.

**Cold-start surface design principles:**

- The root harness file (CLAUDE.md / AGENTS.md) should be under 60–100 lines and contain only universally applicable instructions
- Anthropic internal teams report that CLAUDE.md files beyond ~300 lines show measurable instruction-following degradation
- Task-specific knowledge belongs in referenced files (`agent_docs/building_the_project.md`, skill files, subagent prompts), not in the root harness
- The root file should function as a routing map: point to the right resources, do not duplicate them

**Session startup sequence** for long-running agents (Anthropic Engineering, 2025):

1. Run environmental orientation commands (`pwd`, `git log --oneline -10`)
2. Read progress tracking file and feature status
3. Select highest-priority incomplete task
4. Start verification infrastructure (dev server, test runner)
5. Begin incremental work within the session scope

This sequence externalizes context — the agent learns what it needs by reading artifacts, not by pre-loading everything into system prompt tokens.

---

## 6. The Harness as Trust Boundary

The system prompt establishes the trust topology of an agentic session. Research on LLM trust boundaries (nullmirror.com, 2025; ArXiv 2512.06914) has converged on a framework for understanding the attack surface: **diverse security threats share a common root — desynchronization between dynamic trust states and static authorization boundaries.**

For harness designers, this means the system prompt is not just instructions — it is a claims layer that the model treats as authoritative. What the harness declares about the agent's identity, permissions, and operating context shapes how the model interprets all downstream input, including user messages, tool outputs, and retrieved content.

**Trust boundary design principles:**

- **Minimum viable permission set**: Agents should receive only the tools required for their assigned scope. Broad tools with wildcard permissions make small interpretation errors catastrophically expensive.
- **Structural isolation over instruction-based isolation**: Subagent architectures physically enforce context separation; telling a single agent to "ignore untrusted input" does not.
- **Per-operation authorization at MCP layer**: Each tool invocation individually authorized via RBAC/ABAC is more robust than session-level permission grants.
- **Tool description as trust surface**: Malicious or sloppy MCP tool descriptions are a prompt injection vector; every tool description in the harness is trusted text.

The Instruction Hierarchy paper (OpenAI, 2024) provides the research foundation: system-prompt-level instructions take Priority 0 precedence over user-level (Priority 10) and tool-output-level (Priority 20–30) content. **The harness is the agent's highest-trust context frame.** This is why structural harness design (hooks, permissions, sandboxing) is more durable than instructional harness design (CLAUDE.md prose): structural mechanisms do not depend on the model's probabilistic decision-making to enforce them.

---

## 7. Multi-Agent Harness Design

The orchestrator/subagent pattern introduces a second harness layer: the orchestrator's system prompt must encode how to delegate, not just how to act. Anthropic's multi-agent research system (2025) identified that vague delegation ("research the semiconductor shortage") causes duplicated effort, gaps, and misaligned work — because subagents inherit none of the orchestrator's context unless it is explicitly transmitted.

**Effective delegation requires four elements in every subagent invocation:**

1. **Clear objective** — success criteria in plain language
2. **Expected output format** — structure the receiving agent can parse
3. **Tool and source guidance** — which MCP servers, files, or APIs to prioritize
4. **Explicit task boundaries** — what is out of scope for this subagent

**Architectural finding** (Abdelnabi et al., 2025): Orchestrator-worker patterns consistently pair with hybrid context management — combining file persistence, summarization, and vector databases. The orchestrator does not "remember" across context windows; it reads structured artifacts written by subagents. This is the multi-agent harness's answer to context overflow: **replace in-context memory with out-of-context artifacts**.

Subagents serve an additional architectural function: they are context firewalls. When a subagent investigates a codebase, it reads hundreds of files — all of which would pollute the orchestrator's context window if done inline. The subagent runs in an isolated context, returns a condensed summary, and the orchestrator's context stays clean for synthesis and decision-making.

**Harness files for multi-agent systems should specify:**

- Which tasks may be delegated vs. must be handled inline
- The output schema for subagent reports (so the orchestrator can reliably parse them)
- Effort/model-tier selection per task type (complex synthesis → higher tier; file reading → smaller model)
- Handoff artifacts: what the subagent must write to disk before returning control

---

## Implications for This Skill Library

**Harness design is the implementation layer of every meta-skill in this library.** The [gate]/[review]/[hypothesis] labeling in rubric dimensions maps directly onto the three-tier authority model:

- **[gate]** dimensions correspond to deterministic enforcement — items that should be implemented as hooks, permissions, or Stop conditions rather than advisory prose
- **[review]** dimensions correspond to structured instructions — items that belong in CLAUDE.md / AGENTS.md at the root harness level
- **[hypothesis]** dimensions correspond to advisory guidance — claims that require calibration against real session data before elevation

**ROADMAP.md as a harness artifact.** The ROADMAP.md requirement (v3.0.0) exists partly because future-looking notes in SKILL.md or CHANGELOG.md pollute the active context the agent reads. ROADMAP.md is designed to be skipped during normal operation — it is a reference-layer document, not a cold-start document. This is progressive disclosure applied to skill library governance.

**§SelfAudit as negative constraint.** The SelfAudit section in SKILL.md functions as a negative constraint checklist — a list of failure modes the agent must verify it has NOT fallen into before declaring completion. This is structurally more reliable than positive completion criteria ("I have done X") because it requires the agent to actively falsify its own output.

**Validation checklist as Stop hook.** The `scripts/check-skill-metadata.py` gate functions as a deterministic Stop hook in the skill authoring workflow. It does not rely on the agent's judgment about whether metadata is correct — it fails mechanically. This is the correct design: move quality gates from advisory prose to deterministic execution wherever possible.

**Skill description length (≤1024 chars) is a harness design constraint.** Skill descriptions are part of the discovery layer — they must fit in the cold-start surface without bloating every session. The 1024-char limit is not aesthetic; it is a context-budget constraint derived from the progressive disclosure model. Violating it degrades harness performance across all sessions that load the skill library.

---

## Source Citations

1. Anthropic Engineering (2025). _Best Practices for Claude Code_. Claude Code Documentation. https://code.claude.com/docs/en/best-practices

2. Anthropic Engineering (2025). _Effective Context Engineering for AI Agents_. Anthropic Engineering Blog. https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents

3. Anthropic Engineering (2025). _Equipping Agents for the Real World with Agent Skills_. Anthropic Engineering Blog. https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

4. Anthropic Engineering (2025). _Effective Harnesses for Long-Running Agents_. Anthropic Engineering Blog. https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

5. Anthropic Engineering (2025). _How We Built Our Multi-Agent Research System_. Anthropic Engineering Blog. https://www.anthropic.com/engineering/multi-agent-research-system

6. Wallace, E., Xiao, K., Leike, J., Weng, L., Heidecke, J., & Beutel, A. (2024). _The Instruction Hierarchy: Training LLMs to Prioritize Privileged Instructions_. ArXiv 2404.13208. https://arxiv.org/html/2404.13208v1

7. Zhou, L., et al. (2025). _Agent Behavioral Contracts: Formal Specification and Runtime Enforcement for Reliable Autonomous AI Agents_. ArXiv 2602.22302. https://arxiv.org/html/2602.22302v1

8. Cherny, Boris (2025). _How Boris Uses Claude Code_. howborisusesclaudecode.com. https://howborisusesclaudecode.com/

9. HumanLayer Blog (2025). _Skill Issue: Harness Engineering for Coding Agents_. https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents

10. HumanLayer Blog (2025). _Writing a Good CLAUDE.md_. https://www.humanlayer.dev/blog/writing-a-good-claude-md

11. Abdelnabi, S., et al. (2025). _Architectural Design Decisions in AI Agent Harnesses_. ArXiv 2604.18071. https://arxiv.org/html/2604.18071v1

12. Osmani, Addy (2025). _Agent Harness Engineering_. addyosmani.com. https://addyosmani.com/blog/agent-harness-engineering/

13. Anthropic Engineering (2025). _Building Agents with the Claude Agent SDK_. Anthropic Engineering Blog. https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk

14. Willison, Simon (2025). _Design Patterns for Securing LLM Agents against Prompt Injections_. https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/

15. ArXiv (2025). _Constraint decay: The Fragility of LLM Agents in Backend Code Generation_. ArXiv 2605.06445. https://arxiv.org/html/2605.06445v1
