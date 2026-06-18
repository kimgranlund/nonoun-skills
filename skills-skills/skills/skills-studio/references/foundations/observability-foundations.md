---
date: 2026-05-31
status: research-verified
coverage: canonical
version: "1.0.0"
primary_sources:
  - "Braintrust (2025). The Three Pillars of AI Observability. braintrust.dev/blog/three-pillars-ai-observability"
  - "Braintrust (2026). Agent Observability: The Complete Guide for 2026. braintrust.dev/articles/agent-observability-complete-guide-2026"
  - "LangChain (2025). Why LLM Observability and Monitoring Needs Evaluations. langchain.com/articles/llm-monitoring-observability"
  - "LangChain (2025). LLM Evals: Production Monitoring to Regression Tests. langchain.com/articles/llm-evals"
  - "Honeycomb / Majors, Charity (2025). The Role of AI Observability in 2025. honeycomb.io/blog/observability-age-of-ai"
  - "Honeycomb (2024). Observability 2.0 vs. Observability 1.0. honeycomb.io/blog/one-key-difference-observability1dot0-2dot0"
  - "OpenTelemetry (2026). Semantic Conventions for Generative AI Spans. opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/"
  - "OpenTelemetry (2026). Semantic Conventions for GenAI Agent and Framework Spans. opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/"
  - "Langfuse (2024). AI Agent Observability, Tracing and Evaluation with Langfuse. langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse"
  - "Liang et al. (2025). AgentTrace: A Structured Logging Framework for Agent System Observability. arxiv.org/html/2602.10133v1"
  - "PolicyLayer (2025). SOC 2 Compliance for AI Agents: Audit Trails, Access Controls and Monitoring. policylayer.com/blog/soc2-compliance-ai-agents"
  - "Anthropic (2025). Our Framework for Developing Safe and Trustworthy Agents. anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents"
---

# What Is Observability in Agentic Systems? — Foundational Knowledge Document

## The Core Claim

Observability in agentic LLM systems is not an extension of traditional software observability — it is a different discipline that addresses a different problem. Traditional observability answers "is the system running correctly?" by measuring infrastructure health: latency, error rates, CPU, throughput. These metrics are necessary but completely insufficient for agents. An agent can exhibit 99.9% uptime, sub-100ms p95 latency, and zero HTTP errors while simultaneously hallucinating answers, looping on a tool call, ignoring explicit instructions, and losing user intent across turns. The system is healthy; the behavior is broken. Conventional monitoring cannot detect this class of failure.

The essential shift: agent observability measures whether the _reasoning process_ was correct, not whether the _infrastructure_ was healthy. This requires capturing the full trajectory of an agent's execution — every LLM call, every tool invocation, every context window state, every decision branch — and then scoring that trajectory against quality criteria that are themselves probabilistic. The implication is architectural: you need traces (execution), evaluations (quality), and datasets (regression baselines) working as a closed loop. Without all three, you have monitoring but not observability.

---

## How Agent Observability Differs from Traditional Observability

### The Three-Pillar Shift

Traditional observability is organized around metrics, logs, and traces — three separate data types stored in separate systems, queried separately. Honeycomb's Charity Majors calls this "Observability 1.0": many sources of truth that cannot be correlated, tools that force teams to make data-structure decisions at write time, cardinality thresholds that prevent capturing high-dimensional context. For deterministic software this is workable. For agents it fails for a structural reason: the failure modes are not infrastructure failures, they are semantic failures embedded in the reasoning chain.

AI observability's three pillars are different in kind:

**Traces** — not request-response logs, but full execution graphs. An agent trace must capture: every LLM call with its full input context, the model's output (including any intermediate reasoning), every tool call with arguments and return values, state transitions in working memory, retrieval queries and their results, latency and token cost at each step, and the correlation IDs that link parent and child spans in multi-agent handoffs. A research agent running for 30 minutes may produce thousands of spans. The trace is the primary artifact of debugging; it is not a supplement to a log.

**Evaluations** — not test assertions, but quality signals on probabilistic outputs. Because the same agent input can trigger different tool sequences, retrieve different documents, and generate different responses on each run, you cannot write a unit test that asserts `output == expected`. Evaluations instead score the trajectory along dimensions like intent alignment, hallucination presence, tool selection correctness, and reasoning coherence. They run both offline (against curated datasets) and online (sampling live production traffic). An LLM-as-judge runs as a scorer; a code-based evaluator handles objective criteria; human annotators handle the long tail.

**Datasets** — not fixtures, but curated regression baselines built from production. When a production trace reveals a failure, that trace becomes a permanent test case. When annotators correct a trajectory, the corrected version enters the dataset. Datasets grow continuously; they encode institutional memory about failure modes, edge cases, and quality boundaries. Without datasets, every new model version or prompt change is validated only against intuition.

### The High-Cardinality Requirement

Majors argues that the decisive technical requirement for AI observability is high-cardinality data: "You can't possibly hope to understand and improve your LLM code or models if all you have are aggregates." Agent failures are not distributed uniformly across users or sessions. A specific model version, a specific user segment, a specific tool configuration, a specific instruction phrasing can each produce failures that aggregate metrics will bury. Effective agent observability requires structured wide events that preserve: model version, prompt hash, tool set, retrieval configuration, session ID, user segment, and any other dimension that could explain differential behavior. These dimensions must be queryable at query time, not pre-aggregated at write time.

### The Context-Is-Software Principle

Majors' second core argument: "You can't evolve the model independently of the context of the rest of the software system." A model does not fail in isolation — it fails in a specific context: a specific system prompt, a specific set of tool definitions, a specific conversation history, a specific retrieval result. Observability that captures model calls but not context state is incomplete. The context window at each step is part of the trace, not a side effect. Teams that store only inputs and outputs lose the ability to answer why: why did the model choose this tool? why did it refuse? why did it hallucinate? The answer lives in what it saw.

---

## Trace Structure for Agents

### The Minimum Viable Trace Schema

A useful agent trace is a hierarchical span tree. Each span represents one unit of work. The root span is the user's request. Child spans are LLM calls, tool calls, retrievals, and sub-agent invocations. The minimum schema per span:

- **span_id** — unique identifier
- **parent_span_id** — links to parent, enabling tree reconstruction
- **trace_id** — shared across all spans in one user session
- **span_type** — one of: `llm_call`, `tool_call`, `retrieval`, `agent_invocation`, `workflow`
- **inputs** — the full input to this step (prompt, arguments, query)
- **outputs** — the full output from this step (completion, return value, results)
- **start_time / end_time** — wall-clock times for latency measurement
- **token_usage** — `input_tokens`, `output_tokens`, `total_cost` (for LLM spans)
- **error** — structured error type if the span failed
- **model** — model name and provider (for LLM spans)

The OpenTelemetry GenAI Semantic Conventions (as of 2026, experimental status) define the standard attribute names: `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.request.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.response.finish_reasons`, `gen_ai.conversation.id`. Opt-in content attributes include `gen_ai.input.messages`, `gen_ai.output.messages`, and `gen_ai.system_instructions`. Content capture is off by default because prompts and completions frequently contain PII.

For agent-specific spans, the convention adds: `gen_ai.agent.name`, `gen_ai.agent.id`, `gen_ai.agent.version`, and `invoke_workflow` as a span type for multi-agent coordination. Multi-agent systems require propagating the trace context across agent boundaries so that a delegated agent's entire execution nests under the parent agent's span, all sharing one trace ID.

### The Trajectory Concept

A trajectory is the full ordered sequence of decisions an agent made to complete a task. Trajectory evaluation asks: was this the correct path? Evaluation frameworks compare the actual trajectory against an expected trajectory (or against a quality rubric when no ground-truth path exists). Trajectory evaluation catches failure modes that single-step evaluation misses: unnecessary tool calls, repeated loops, skipped verification steps, inefficient reasoning paths, sub-agent handoffs that lose context.

AgentTrace (Liang et al., 2025) formalizes three observable surfaces within a trajectory:

1. **Operational surface** — method calls, arguments, return values, timing
2. **Cognitive surface** — raw prompts, completions, extracted reasoning chains, confidence estimates
3. **Contextual surface** — HTTP APIs, databases, caches, vector stores accessed during execution

All three surfaces must be captured to reconstruct why a failure occurred. Operational-only traces tell you what happened; cognitive traces tell you what the model thought; contextual traces tell you what information it had access to.

### What Traditional APM Cannot See

Traditional APM reports: HTTP 200, latency 340ms, no exception. Agent observability reports: the agent looped on tool call `search_docs` three times with identical arguments before returning a hallucinated synthesis, cost $0.23, achieved zero of the user's three stated goals. The 200 status code says nothing about whether the agent succeeded. The agent trace says everything.

---

## Evaluation Loops as Observability Infrastructure

### Online vs. Offline Evaluation

Evaluations do not run only at test time. In production-grade agent systems, evaluations are continuous:

**Offline evaluations** run against curated datasets before deployment. They catch regressions: a new model version, a prompt change, a tool update that degrades quality on known failure cases. They run in CI. They gate deployment. They are only as good as the datasets they run against.

**Online evaluations** sample live production traffic and score it in near-real-time. They answer questions offline evals cannot: what is the hallucination rate on this specific user segment? did intent alignment drop after the system prompt change at 14:00? are tool calls succeeding at a lower rate on weekend traffic? Online evals do not require reference answers — they use LLM-as-judge or rule-based scorers to evaluate quality patterns against production behavior.

The combination is mandatory. Offline evals without online evals leave production behavior unobserved. Online evals without offline evals leave regressions undetected until they reach users.

### The Production-to-Dataset Feedback Loop

The critical operational mechanic that closes the observability loop: production failure traces become regression datasets. The workflow:

1. Online eval flags a production trace as low quality (hallucination detected, tool call failed, intent not satisfied)
2. Engineer or annotation queue reviews the trace
3. The trace is added to the offline regression dataset with a quality label
4. The corrected or expected behavior is recorded alongside it
5. Future deployments must pass this case before shipping

LangSmith implements this as "add to dataset with one click." Langfuse implements annotation queues where domain experts label complex traces, feeding corrections directly into datasets. Braintrust calls this the "continuous improvement cycle where production traces become datasets that power evaluations." The practical effect: every production failure, once captured, prevents future recurrence of the same failure. The dataset is the institutional memory of what the system is expected to do.

### Quality Signals Beyond Correctness

Agent quality signals cluster into four categories:

- **Task completion**: did the agent achieve the user's stated goal?
- **Faithfulness**: are claims grounded in retrieved context, or hallucinated?
- **Efficiency**: were tool calls necessary, or did the agent loop or over-call?
- **Safety**: did the agent stay within intended scope, avoid prohibited actions, respect user data?

Each category requires different evaluation techniques. Task completion often requires LLM-as-judge with explicit rubrics. Faithfulness requires comparing claims to source documents. Efficiency requires trajectory analysis. Safety requires behavioral classifiers. A complete observability system scores all four categories on sampled production traffic.

---

## Debugging Agent Failures

### The Root Cause Analysis Problem

Agent failures are non-deterministic and frequently silent. Unlike a stack trace that identifies a line of code, an agent failure manifests as an output that was subtly wrong, a tool call that was plausible but incorrect, a reasoning chain that drifted from the user's intent. Finding the root cause requires reconstructing the exact execution state at the point of failure.

The core technique: compare a failed trace to a successful trace on the same task type. The divergence point — where the execution paths separate — is the candidate root cause. This requires that traces are stored, queryable, and comparable. Without trace storage, failed sessions are lost permanently.

### Checkpoint-Based State Replay

For multi-step agents, the gold standard debugging technique is checkpoint-based state replay. LangGraph implements this as "Time Travel": every node completion creates a checkpoint containing inputs, intermediate results, and decisions. Engineers can:

1. **View history** — retrieve all checkpoints for a session chronologically
2. **Inspect state** — examine the exact working memory at any step
3. **Modify state** — correct a value at any checkpoint without rerunning earlier steps
4. **Resume execution** — continue from the corrected checkpoint forward

This transforms ephemeral agent executions into persistent, replayable state machines. The debugging workflow shifts from "why did output X occur?" (unanswerable without a trace) to "which checkpoint produced unexpected intermediate state?" (answerable with checkpointed traces). The key insight: you cannot debug non-determinism by re-running the same agent — you will get a different failure. You must replay from the original captured state.

### Counterfactual Analysis

Once a failure is isolated to a specific step, counterfactual analysis asks: what would have happened with a different input at this step? This requires the ability to inject a corrected value at a checkpoint and observe downstream behavior. This is how prompt changes and tool call fixes are validated before deployment: run the corrected version against the original captured state, compare outcomes.

### Session Replay vs. Aggregate Analysis

Two complementary debugging modes:

**Session replay** — reconstruct exactly what happened in one specific session. Required for investigating a user complaint, a compliance incident, or a critical failure. Requires full trace storage with content (prompt text, tool outputs, reasoning chains).

**Aggregate analysis** — understand patterns across 500 concurrent sessions. Required for detecting drift, identifying the most common failure modes, understanding which user segments are affected. Requires structured telemetry that can be aggregated and filtered by high-cardinality dimensions.

Session replay answers "why did this specific session fail?" Aggregate analysis answers "how often does this type of failure occur, and under what conditions?" Both are required. The mistake is treating session replay as the only debugging method — it scales to one session at a time, which is insufficient for production systems with thousands of concurrent users.

---

## Audit Trails for Agentic Actions

### Why Agent Actions Require Structured Audit Logs

Traditional software audit logs record who accessed what data, when. Agent audit logs must record something more complex: what the agent decided to do, why it decided it, what information it had when it decided, and what the downstream effect was. This is necessary because agents act autonomously — they call tools, modify state, access external APIs, and produce outputs without synchronous human approval. If a compliance incident occurs, the audit trail must be able to reconstruct the exact decision chain that led to the action.

### The Minimum Viable Audit Record

Per the SOC 2 compliance framework for AI agents, every agent action record should contain:

- **event_id** — globally unique identifier
- **timestamp** — UTC, immutable
- **agent_id** — unique identifier for the specific agent instance
- **session_id / conversation_id** — correlates to user session
- **action_type** — structured type (tool_call, data_access, external_api, state_modification)
- **inputs** — exact arguments provided to the action
- **outputs** — exact return value from the action
- **policy_decision** — ALLOW/DENY if a policy layer evaluated this action
- **policy_version** — which policy version was applied
- **source_metadata** — what triggered this action (user request, agent plan, upstream tool result)
- **model** — which model produced the decision to take this action

Records must be append-only, tamper-evident, and retained according to organizational policy (financial/healthcare standards typically require 1–7 years).

### The Two-Gate Principle

Effective agent audit architecture separates the agent that acts from the layer that records. The agent generates an intent (what action to take and why); the audit layer captures the intent, records it, evaluates it against policy, and either permits or blocks the action. This separation has two benefits: the agent's reasoning is preserved independently of the action outcome, and the policy evaluation is itself auditable. Audit trails that only record successful actions hide the more important data: what was blocked, what was attempted but failed policy checks, and what was approved against a policy version that was later revised.

### MCP and Audit Logging

The Model Context Protocol (MCP), developed at Anthropic, creates a natural audit boundary: every tool call goes through a defined protocol surface. MCP-compliant implementations can emit structured audit events at the protocol layer, capturing tool name, arguments, session context, and response, without requiring instrumentation inside the tool itself. This makes MCP server implementations a natural integration point for compliance-grade audit logging.

---

## Observability Infrastructure: A Stack View

Production-grade agent observability requires five layers working together:

**Layer 1 — Instrumentation**: OpenTelemetry SDK with GenAI semantic conventions, emitting structured spans for every LLM call, tool call, retrieval, and agent invocation. Framework-specific integrations (LangSmith for LangChain/LangGraph, Langfuse for framework-agnostic, Arize Phoenix for eval-heavy workflows) accelerate this. Content capture (prompt text, tool outputs) should be opt-in with PII awareness.

**Layer 2 — Trace storage**: A queryable trace store that preserves full span trees, supports high-cardinality dimension filtering (session ID, model version, user segment, tool set), and enables session replay. ClickHouse, Postgres with JSONB, or a purpose-built tracing backend. Retention must satisfy compliance requirements.

**Layer 3 — Online evaluation**: Automated scorers running on sampled production traces. LLM-as-judge for subjective quality dimensions; rule-based scorers for objective criteria. Results stored alongside traces as quality metadata. Threshold alerts when quality metrics drop below baselines.

**Layer 4 — Dataset management**: Curated test cases drawn from production failures, annotation queues, and expert-labeled examples. Versioned datasets with clear provenance. Integration into CI/CD so offline evals run against current datasets before every deployment.

**Layer 5 — Analytics surface**: High-cardinality query capability for aggregate analysis. Ability to slice quality metrics by any combination of dimensions. Cost and latency dashboards broken down by task type, model, and tool set. Regression detection against historical baselines.

---

## Implications for This Skill Library

Agent observability has direct consequences for how this skill library is built, validated, and maintained.

**[gate] Routing as a testable behavior**: Skill routing is an agent behavior. The description field in each skill determines whether the correct skill activates for a given user request. Without observability, routing is validated only through qualitative sense-checking. With observability, routing accuracy is a metric: what fraction of sessions activate the correct skill for the task type presented? This is a trajectory-level measurement, not a single-call measurement.

**[gate] §SelfAudit as structured audit record**: The §SelfAudit pattern in skill SKILL.md files is a structural audit (does the declared state match the on-disk state?). Observability adds a behavioral audit layer: does the runtime behavior match the declared capability? A skill that declares five modes but routes 90% of sessions through one mode has a behavioral gap that structural audit cannot detect.

**[review] Reference utilization as cost signal**: Context engineering matters because context is cost. References loaded into context but never accessed are dead weight — they consume tokens on every relevant session. Behavioral telemetry exposes this: load events without access events identify dead references. The `observability-and-telemetry.md` rubric in this folder operationalizes this measurement.

**[review] Evaluation as a first-class skill artifact**: Skills in the `evals/` subdirectory (where present) encode the offline evaluation dataset for that skill. These datasets should be grown from production traces, not authored only from intuition. Every Critical finding from a **critique**-mode run that survives verification should become a dataset entry, not just a ROADMAP item.

**[hypothesis] Skill-level online evaluation**: The skill library currently lacks runtime quality signals. An unanswered question: can online evals be instrumented at the skill invocation level, scoring each skill's output on task completion and faithfulness dimensions, feeding into per-skill quality baselines? This would transform ROADMAP.md from a forward-looking document into a living quality dashboard.

**ROADMAP.md as behavioral contract**: The ROADMAP.md convention (Planned / Deferred / Out of scope) documents intended future behavior. When behavioral observability exists, ROADMAP items can be validated against actual usage: does "Out of scope" mean the behavior is absent from traces, or does the skill actually attempt it? Observable systems can enforce their own scope boundaries.

The companion document `observability-and-telemetry.md` in this folder provides the rubric-level prescriptions for instrumentation practice. This document provides the foundational rationale for why those prescriptions exist.

---

## Source Citations

1. Braintrust (2025). "The Three Pillars of AI Observability." braintrust.dev. https://www.braintrust.dev/blog/three-pillars-ai-observability

2. Braintrust (2026). "Agent Observability: The Complete Guide for 2026." braintrust.dev. https://www.braintrust.dev/articles/agent-observability-complete-guide-2026

3. Braintrust (2025). "What Is Agent Observability? Tracing Tool Calls, Memory, and Multi-Step Reasoning." braintrust.dev. https://www.braintrust.dev/articles/agent-observability-tracing-tool-calls-memory

4. LangChain (2025). "Why LLM Observability and Monitoring Needs Evaluations." langchain.com. https://www.langchain.com/articles/llm-monitoring-observability

5. LangChain (2025). "LLM Evals: Production Monitoring to Regression Tests." langchain.com. https://www.langchain.com/articles/llm-evals

6. LangChain (2025). "AI Agent Observability: Tracing, Testing, and Improving Agents." langchain.com. https://www.langchain.com/articles/agent-observability

7. Honeycomb / Majors, Charity (2025). "The Role of AI Observability in 2025." honeycomb.io. https://www.honeycomb.io/blog/observability-age-of-ai

8. Honeycomb (2024). "Observability 2.0 vs. Observability 1.0: One Key Difference." honeycomb.io. https://www.honeycomb.io/blog/one-key-difference-observability1dot0-2dot0

9. OpenTelemetry (2026). "Semantic Conventions for Generative Client AI Spans." opentelemetry.io. https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/

10. OpenTelemetry (2026). "Semantic Conventions for GenAI Agent and Framework Spans." opentelemetry.io. https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/

11. Langfuse (2024). "AI Agent Observability, Tracing and Evaluation with Langfuse." langfuse.com. https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse

12. Liang et al. (2025). "AgentTrace: A Structured Logging Framework for Agent System Observability." arXiv:2602.10133. https://arxiv.org/html/2602.10133v1

13. PolicyLayer (2025). "SOC 2 Compliance for AI Agents: Audit Trails, Access Controls and Monitoring." policylayer.com. https://policylayer.com/blog/soc2-compliance-ai-agents

14. Anthropic (2025). "Our Framework for Developing Safe and Trustworthy Agents." anthropic.com. https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents

15. Dev.to / Sreenivas (2025). "Debugging Non-Deterministic LLM Agents: Implementing Checkpoint-Based State Replay with LangGraph." dev.to. https://dev.to/sreeni5018/debugging-non-deterministic-llm-agents-implementing-checkpoint-based-state-replay-with-langgraph-5171
