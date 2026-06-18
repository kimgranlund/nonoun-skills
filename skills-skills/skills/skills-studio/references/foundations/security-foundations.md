---
date: 2026-05-31
status: research-verified
coverage: canonical
version: "1.0.0"
primary_sources:
  - "Willison, S. (2025). The lethal trifecta for AI agents. simonwillison.net/2025/Jun/16/the-lethal-trifecta/"
  - "OWASP (2025). OWASP Top 10 for LLM Applications 2025. owasp.org/www-project-top-10-for-large-language-model-applications/"
  - "Debenedetti, E. et al. / Google DeepMind (2025). Defeating Prompt Injections by Design (CaMeL). arXiv:2503.18813"
  - "Piet, J. et al. (2025). Design Patterns for Securing LLM Agents against Prompt Injections. arXiv:2506.08837"
  - "Meta AI (2025). Agents Rule of Two. simonwillison.net/2025/Nov/2/new-prompt-injection-papers/"
  - "Kour, G. et al. (2025). The Attacker Moves Second. simonwillison.net/2025/Nov/2/new-prompt-injection-papers/"
  - "OWASP (2025). AI Agent Security Cheat Sheet. cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html"
  - "Anthropic (2026). Trustworthy Agents in Practice. anthropic.com/research/trustworthy-agents"
---

# What Is Security in Agentic Systems? — Foundational Knowledge Document

## The Core Claim

Security in agentic LLM systems is a **design discipline, not a detection discipline**. The dominant assumption inherited from traditional software — that security is a filter applied to bad inputs at the boundary — fails for agents because the attack surface is the agent's reasoning process, not a network port or a SQL query parameter. An agent that can access private data, process untrusted content, and communicate externally is unconditionally exploitable regardless of how well-trained or carefully instructed it is. This is not a temporary limitation of current models; it is a structural property of systems that treat all text as potentially instructional.

The practical implication is blunt: security properties must be enforced by the system architecture — the tool registry, the permission model, the trust hierarchy, the reversibility gates — not by the agent's judgment. Instruction-based defenses ("never do X," "always verify before acting") fail under adaptive attack. Structural defenses — architectural separations that make certain data flows physically impossible — are the only controls that hold. This document grounds the distinction, catalogs the canonical threat taxonomy, and establishes the design principles that follow from it.

---

## The Lethal Trifecta: Three Conditions That Create Unconditional Vulnerability

Simon Willison, who coined the term "prompt injection" in 2022, formalized the concept of the **lethal trifecta** in June 2025. The trifecta is a precondition analysis, not an attack description: when three capabilities co-exist in an agentic system, no instruction-based defense can protect it.

The three conditions are:

1. **Access to private data** — the agent can retrieve information that should not leave the system: user inboxes, customer databases, credential stores, private repositories, financial records.

2. **Exposure to untrusted content** — the agent processes text originating from outside the trust boundary: emails, web pages, shared documents, public issue trackers, API responses from third parties.

3. **External communication ability** — the agent can send data outside the system: make HTTP requests, render external images (which can carry query parameters), call external APIs, send messages.

When all three are present simultaneously, an attacker embeds instructions in untrusted content. The agent processes the content, treats the embedded instructions as legitimate (because LLMs cannot reliably distinguish instruction source from instruction content), accesses private data, and exfiltrates it via the external communication vector. The attack requires no vulnerability in the traditional sense — no buffer overflow, no injection into parameterized queries. The "vulnerability" is the agent's core capability: following instructions found in text.

Willison's catalog of real-world incidents confirms the pattern: Microsoft 365 Copilot, GitHub's MCP server, GitLab's Duo Chatbot, ChatGPT plugins, Google NotebookLM, Amazon Q — all exploited via indirect injection through content the agent was legitimately asked to process.

**Why instruction-based defenses fail.** The statistical baseline is damning. Research from "The Attacker Moves Second" (Kour et al., 2025) evaluated 12 published prompt injection defenses using adaptive attacks. Static defenses showing near-zero bypass rates under fixed test prompts were compromised at rates exceeding 90% under adaptive optimization. Human red-teamers achieved 100% success across all tested systems. The "Best-of-N" family of attacks — systematic variation using gradient descent, reinforcement learning, and random search — achieves over 90% success against GPT-4o and 78% against Claude 3.5 Sonnet with sufficient attempts. A defense that works 95% of the time is not adequate when the attacker controls thousands of attempts. Instruction-level filtering must therefore be treated as delay, not prevention.

**The structural answer.** Remove one or more legs of the trifecta. If the agent cannot combine private data access + untrusted content exposure + external communication in a single action sequence, the attack chain breaks. Meta AI's "Agents Rule of Two" paper (2025) formalizes this as a constraint: an agent should satisfy at most two of the three conditions at any time. Willison endorses this framing: if you cannot remove a leg, you must implement structural separation between the component that reads untrusted content and the component that can access private data or communicate externally.

---

## OWASP Top 10 for LLM Applications: The Canonical Threat Taxonomy

The OWASP LLM Top 10 (2025 edition) is the practitioner-consensus taxonomy of LLM security risks, covering the full application stack from model behavior to infrastructure. The risks most relevant to agentic systems, in order of severity:

**LLM01 — Prompt Injection.** Direct injection manipulates the model via user input. Indirect injection embeds instructions in content the model retrieves and processes (web pages, documents, database records, tool outputs). In agentic systems, indirect injection is the dominant attack vector because agents actively seek out and process external content. Mitigation requires structural defense; instruction-level filtering is insufficient (see above).

**LLM02 — Improper Output Handling.** LLM outputs are passed to downstream systems (SQL query builders, shell executors, rendering engines, further LLMs) without validation. A model that generates `'; DROP TABLE users;--` in a SQL context is not the problem — the problem is that the output was treated as trusted input to a parameterized query-builder. All agent outputs that become inputs to other systems must be schema-validated before use. This is equivalent to SQL injection prevention: the fix is structural (parameterized queries, output schema enforcement), not textual filtering.

**LLM06 — Excessive Agency.** The agent has been granted more functionality, permissions, or autonomy than required for its task. An agent with read-write database access for a read-only query task, an agent with shell execution rights for a summarization task, an agent that can approve its own actions without human review — all represent excessive agency. The mitigation is least privilege: every capability granted to the agent must be justified by a specific task requirement, and the grant must be scoped to the minimum required form (read-only vs. read-write, single resource vs. wildcard, bounded time window vs. permanent).

**LLM07 — System Prompt Leakage.** System prompts often contain security-sensitive information: behavioral constraints, internal business logic, API keys, user data schemas. Models can be prompted to reveal system prompt contents. Defense: system prompts should contain no secrets (credentials belong in environment variables accessed by tools, not in prompts); assume system prompt contents are eventually discoverable.

**LLM05 — Improper Output Handling / Insecure Deserialization.** Outputs fed to code interpreters or serialization frameworks without sandboxing create remote code execution vectors. Agents that generate and execute code must do so in sandboxed environments with no network access, limited filesystem access, and resource limits.

**LLM10 — Unbounded Consumption.** Agentic loops without termination conditions, recursion limits, or token budgets can consume unbounded resources — creating denial-of-wallet conditions and enabling amplification attacks where small attacker inputs trigger expensive model calls or tool invocations at scale.

---

## Least Privilege: The Governing Principle for Agent Tool Access

The principle of least privilege — grant any principal only the permissions required for its current task, and nothing more — is the oldest rule in security. It applies to agents with particular force because agents are high-privilege actors (they write files, call APIs, execute commands, manage secrets) processing low-privilege input (user messages, external documents, tool responses that may have been tampered with).

**Three implementation patterns** structure least-privilege enforcement for agents:

**1. Permission-Gated Tool Registry.** Tools are not handed directly to the agent; they are registered with declarative permission requirements. At invocation time, a policy service checks whether the current agent context (role, task scope, session state) is authorized for the requested tool and parameter combination before execution. The agent proposes; the registry decides. This decouples decision-making from authorization, preserving the audit log and enabling fine-grained revocation.

**2. Sandboxed Execution Environments.** Code execution, file access, and external process invocation are routed through sandboxes with restricted system calls, no network access by default, and resource limits on CPU, memory, and time. Docker containers, seccomp profiles, and language-level sandboxes (e.g., Python's `resource` module) provide graded isolation levels. The key design choice: the sandbox is the safety boundary, not the agent's instructions.

**3. Scoped, Time-Limited Credentials.** When the agent needs external service access, it receives a token scoped to the minimum required permission (read-only, single resource, short TTL) rather than inheriting ambient host permissions or a long-lived admin token. Each agent session is treated as an untrusted principal by default. Credentials are injected by the harness at session initialization and expire with the session. This pattern eliminates the class of attacks where a compromised agent inherits production credentials from its execution environment.

**What "minimum required" means in practice.** The OWASP AI Agent Security Cheat Sheet specifies: enumerate tools explicitly (no wildcards), distinguish read vs. write access per tool, scope file access to specific directories rather than the root filesystem, restrict API calls to specific endpoints rather than full service permissions, and set short TTLs on any credential that must be passed into agent context.

**The MiniScope framework** (arXiv:2512.11147) proposes formal least-privilege authorization for tool-calling agents: each tool call is associated with a capability set, and the orchestrator validates at runtime that the capability set required by the tool call is a subset of the capabilities authorized for the current task. Excess capabilities are rejected before the call executes.

---

## Structural Injection Defense: The Dual LLM Pattern and CaMeL

Because instruction-based filtering is demonstrably inadequate, the research community has converged on **structural separation** as the correct approach — making certain data flows architecturally impossible rather than instructionally forbidden.

**The Dual LLM Pattern** was proposed by Willison and formalized in the IBM/ETH Zurich/Google/Microsoft design patterns paper (Piet et al., arXiv:2506.08837). The pattern creates two separated components:

- **Privileged LLM**: receives only trusted input (operator system prompt, user request). Has access to tools and can invoke actions. Never processes untrusted external content directly.
- **Quarantined LLM**: processes untrusted content (web pages, emails, file contents, API responses). Has no tool access. Returns only structured symbolic outputs — typed labels, extracted fields, boolean classifiers — that the privileged LLM handles without ever seeing the raw untrusted text.

The critical mechanism: the privileged LLM receives symbolic variables (e.g., `$EMAIL_SENDER`, `$DOCUMENT_SUMMARY`) that represent processed content without exposing the raw text. The privileged LLM cannot dereference these variables into raw text — that dereferencing happens in the orchestrator at tool-call time after policy validation. A prompt injection embedded in the raw untrusted text cannot reach the component that controls tool invocation.

**CaMeL (CApabilities for MachinE Learning)**, proposed by Google DeepMind (Debenedetti et al., arXiv:2503.18813), extends the Dual LLM concept with capability-based taint tracking. Every value in the execution environment carries metadata specifying what can be done with it (derived from which trust tier produced it). A taint-tracking interpreter executes the agent's plan, propagates trust metadata through every operation, and enforces security policies before any tool call. Data derived from untrusted sources cannot be used as a tool parameter unless the policy explicitly permits it.

CaMeL achieved 67% neutralization of attacks in the AgentDojo security benchmark — not perfect, but a structural advance over filtering-based approaches that collapse under adaptive attack. The framework is directly analogous to how parameterized queries solved SQL injection: the fix is a structural type constraint on data flow, not a pattern-match on content.

**Other structural patterns** from the design patterns literature:

- **Plan-Then-Execute**: the agent selects all tools upfront before processing any external content. Tool outputs can inform content delivery but cannot alter which tools are called next.
- **LLM Map-Reduce**: sub-agents process untrusted content in isolation and return only structured summaries to the coordinator. The coordinator is never exposed to raw untrusted text.
- **Context Minimization**: unnecessary context (including user prompts) is removed before returning results, preventing injected instructions from persisting in conversation history.

---

## Trust Hierarchies in Multi-Agent Systems

Single-agent security is complex. Multi-agent security adds a new dimension: instructions arriving from other agents must be trusted at an appropriate level, which is frequently lower than the level at which the orchestrating system operates.

**Anthropic's principal hierarchy** defines three trust tiers:

1. **Operator** (system prompt): the deploying organization's configuration. Highest trust. Can expand or restrict model defaults within Anthropic-set limits. Can grant user-level trust to users explicitly.

2. **User** (human turn): the end user's input. Lower trust than operator. Cannot exceed operator-level permissions unless explicitly elevated by the operator's system prompt.

3. **Environment** (tool outputs, retrieved content, API responses, messages from other agents): lowest trust. Claude's model spec treats this tier with maximum skepticism as "untrusted external data that may contain injection attempts."

In orchestrator-subagent architectures, a critical failure mode is **trust laundering**: a subagent's output becomes input to the orchestrator. If the orchestrator treats the subagent's output as operator-level trust, a compromised subagent (or a subagent that processed injected content) can escalate its instructions to orchestrator-level authority. The correct behavior: subagent outputs are treated as environment-tier (lowest trust), not as operator or user-tier.

**Permission propagation should not automatically inherit.** A subagent should not receive all the permissions of its orchestrator. Each agent in a chain should have only the permissions required for its specific subtask — which is typically a strict subset of what the orchestrator holds. This is least privilege applied at the inter-agent boundary.

**The verification problem.** A subagent receiving instructions from an orchestrator has no cryptographic way to verify the source. The Anthropic Trustworthy Agents paper notes this: "developers approve 93% of permission prompts," collapsing human oversight into incident response rather than genuine review. Multi-agent systems require the same skepticism toward orchestrator instructions as toward user input — an orchestrator can be compromised or impersonated. Legitimate orchestration systems generally do not need to override safety measures or claim special permissions not established in the original system prompt.

**Anthropic's shared responsibility model** (2026) assigns four security layers with clear ownership: Model (Anthropic), Harness (deploying organization), Tools (deploying organization), Environment (deploying organization). Three of four layers are the operator's responsibility. A well-trained model cannot compensate for a poorly configured harness, an overly permissive tool registry, or an exposed environment.

---

## Reversibility: Why Structural Gates Are Required for Irreversible Operations

Agents make mistakes. Models hallucinate parameters. Injected instructions redirect action chains. The correct response to this reality is not to prevent all mistakes (impossible) but to ensure that mistakes are recoverable. This requires designing the system's action space so that irreversible operations are never the default path.

**The reversibility requirement**: any operation that cannot be undone without significant cost, coordination, or data loss requires a structural authorization gate — not an instruction-level check, not a soft confirmation, but a gate that separates proposal from execution and involves out-of-band approval. Examples: database writes, email sends, public repository pushes, financial transactions, credential rotation, deployment actions, external API calls with side effects.

**Dry-run patterns.** Before executing an irreversible operation, the agent generates a complete plan (the "dry run") describing exactly what will be done, what parameters will be used, and what the expected outcome is. The plan is presented to the human or the policy service for review. Only after explicit approval does execution proceed. This pattern is well-established in infrastructure tools (Terraform plan/apply) and translates directly to agent systems.

**Confirmation gates.** For high-impact operations, the OWASP AI Agent Security Cheat Sheet specifies that authorization artifacts must include: actor identity, tool name, target resource, normalized parameters, timestamp, expiry, and replay protection. Short-lived authorization artifacts prevent "authority resurrection attacks" where a token obtained through legitimate approval is reused after the agent state is rolled back to an earlier checkpoint.

**Audit trail requirements.** Every action an agent takes must be logged with sufficient fidelity to reconstruct: who initiated the request, which agent instance executed it, which model version was used, which tool was called with which parameters, what the result was, and whether human review occurred. The enterprise standard (Augment Code, 2025) specifies that any decision from the past 30 days must be fully reconstructable from audit logs alone, without developer interviews or manual correlation, within one hour.

**Compensating actions.** The design requirement is not just "can we undo this" but "have we pre-defined how to undo this." Each irreversible agent action should have a corresponding compensating action defined at workflow design time, executable in reverse-dependency order. This is operational discipline borrowed from database transaction design.

**The probabilistic security problem.** Unlike traditional software, LLM agents cannot be formally verified. A rule encoded in a system prompt might be followed 99% of the time and violated 1% of the time under adversarial prompting. This makes agent security probabilistic in a way that traditional software security is not. The correct response: for high-stakes operations, accept that probabilistic LLM judgment is insufficient and require **deterministic controls** — schema validation, allowlists, parameter range checks, rate limits — that do not depend on the model's judgment at all. The model generates a proposal (probabilistic); the policy service validates it (deterministic). This separation is the architectural equivalent of the principle "generate probabilistically, validate deterministically."

---

## Implications for This Skill Library

Security in agentic systems maps directly to several of this skill library's structural conventions:

**[gate] annotations** in rubrics correspond to the irreversibility requirement: any action classified as a gate requires out-of-band authorization, cannot be bypassed by instruction, and must be logged with full audit context. The `[gate]` designation is not stylistic — it signals that the corresponding control must be structurally enforced, not instruction-enforced.

**§SelfAudit sections** in skill SKILL.md files implement a weak form of the Dual LLM pattern at the meta level: a separate reasoning pass (the self-audit) reviews the outputs of the primary generation pass before they are delivered. This does not provide the structural separation of a true Dual LLM (both passes share context), but it implements the verification-before-delivery discipline that is the minimum standard for irreversible skill outputs.

**ROADMAP.md's required three-section structure** (Planned / Deferred / Out of scope) relates to the scope containment principle: explicitly defining what the skill will not do bounds the skill's effective permission surface. A skill with no explicit "Out of scope" section has an implicit unlimited scope — a form of excessive agency applied at the skill level.

**The `files` array in skill.json** is a least-privilege inventory: it declares exactly what files the skill is expected to read. Skill consumers should treat files not listed in this array as out-of-scope for the skill, even if physically accessible. This is the skill-level equivalent of a sandboxed file-access permission.

**Trust levels in skill-to-skill references.** When one skill invokes another (via `peer_skills` or `## Invocation` chain references), the invoked skill's outputs should be treated as environment-tier (lowest trust) until validated against the invoking skill's expected schema. This prevents a compromised or misbehaving peer skill from injecting instructions into the invoking skill's execution context.

The companion doc `security-and-scope-containment.md` in this folder translates these foundational principles into actionable rubric items with [gate]/[review]/[hypothesis] classifications.

---

## Source Citations

1. Willison, S. (2025). "The lethal trifecta for AI agents: private data, untrusted content, and external communication." simonwillison.net. https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/

2. Willison, S. (2025). "Design Patterns for Securing LLM Agents against Prompt Injections." (Summary of Piet et al.) simonwillison.net. https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/

3. Willison, S. (2025). "New prompt injection papers: Agents Rule of Two and The Attacker Moves Second." simonwillison.net. https://simonwillison.net/2025/Nov/2/new-prompt-injection-papers/

4. Debenedetti, E. et al. / Google DeepMind (2025). "Defeating Prompt Injections by Design." arXiv:2503.18813. (CaMeL framework — taint-tracking structural defense, 67% AgentDojo neutralization rate.) https://arxiv.org/pdf/2503.18813

5. Piet, J. et al. / IBM, Invariant Labs, ETH Zurich, Google, Microsoft (2025). "Design Patterns for Securing LLM Agents against Prompt Injections." arXiv:2506.08837. (Six structural patterns: Action-Selector, Plan-Then-Execute, Map-Reduce, Dual LLM, Code-Then-Execute, Context-Minimization.) https://arxiv.org/html/2506.08837v1

6. OWASP (2025). "Top 10 for LLM Applications 2025." OWASP Foundation. (Canonical threat taxonomy: LLM01 Prompt Injection, LLM02 Improper Output Handling, LLM06 Excessive Agency, LLM07 System Prompt Leakage, LLM10 Unbounded Consumption.) https://owasp.org/www-project-top-10-for-large-language-model-applications/

7. OWASP (2025). "AI Agent Security Cheat Sheet." OWASP Cheat Sheet Series. (Least-privilege implementation, confirmation gate specification, adversarial testing requirements.) https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html

8. OWASP (2025). "LLM Prompt Injection Prevention Cheat Sheet." OWASP Cheat Sheet Series. (Defense categories, Dual LLM pattern, Best-of-N attack statistics: 89% on GPT-4o, 78% on Claude 3.5 Sonnet.) https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html

9. Anthropic (2026). "Trustworthy Agents in Practice." Anthropic Research. (Shared responsibility model: Model / Harness / Tools / Environment; 93% operator approval-prompt bypass rate; trust hierarchy: operator, user, environment tiers.) https://www.anthropic.com/research/trustworthy-agents

10. Augment Code (2025). "What Multi-Agent Outputs Need to Pass Enterprise Audit: Attributability and Reversibility." augmentcode.com. (Seven-field audit log standard; compensating actions; EU AI Act Article 12/14 alignment; authority resurrection attacks.) https://www.augmentcode.com/guides/multi-agent-outputs-n-pass-enterprise-audit

11. Haulos, P. (2025). "Securing Agentic AI Is a Probabilistic Problem." haulos.com. (Swiss cheese defense model; probabilistic vs. deterministic control separation; P(failure) = 1-(1-p)^n autonomy-oversight tension.) https://haulos.com/blog/agentic-ai-security/

12. Patel, K. et al. (2024). "MiniScope: A Least Privilege Framework for Authorizing Tool Calling Agents." arXiv:2512.11147. (Formal capability-set validation for least-privilege tool calls.) https://arxiv.org/pdf/2512.11147
