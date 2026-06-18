---
date: 2026-05-23
status: draft
version: "0.1.0"
---

# Observability and Telemetry — Best Practices Rubric

**You cannot improve what you cannot measure.** The rubrics in this folder score routing accuracy, compounding velocity, context load, and coordination quality. Every one of those scores is a guess unless telemetry exists to ground it in observed data.

Observability is the discipline of making agentic systems legible: what modes were invoked, which references were loaded, which tools were called, what the verify outcome was, how many tokens it cost, and where it failed. Without this data, every rubric score is an opinion. With it, rubric scores become measurements with baselines, trends, and regression signals.

The distinction between structural audit (§SelfAudit in SKILLS-best-practices) and behavioral observability matters here: structural audit checks the _skill itself_ for drift — declared vs. on-disk state, capability menu vs. existing sections. Behavioral observability checks _agent behavior at runtime_ — which paths are actually taken, which references are actually useful, which tools actually fail. Both are required. A skill with only structural audit is well-maintained but may still route incorrectly. A skill with only behavioral observability is measured but may be measuring a drifting target.

This is the measurement layer. It makes every other rubric in this folder data-driven.

**Companion docs:**

- `evaluation-workflows.md` (this folder) — evals use telemetry data as inputs to routing accuracy measurement
- `skills-authoring.md` (this folder) — §SelfAudit as the structural complement to this rubric
- `inversion-and-abstraction.md` (this folder) — script usage data is one telemetry signal
- `context-engineering.md` (this folder) — reference utilization data feeds into context load optimization

---

## §The Problem

Agentic systems without observability have four specific blind spots:

1. **Dead references**: skill references that are declared in SKILL.md and load correctly but are never actually accessed during task completion. They consume tokens on every relevant session without providing value. Without telemetry, nobody knows they're dead. With telemetry, they appear as references with load events but zero access events.

2. **Silent routing failures**: a skill's description routes some phrases correctly and misroutes others. Without telemetry, misrouting is only discovered when a user complains. With telemetry, misrouting appears as sessions where the wrong skill was activated for a task type that has a dedicated skill.

3. **Cost blindness**: some task types cost 3x what others do, for no clear reason. Without per-task-type token tracking, this is invisible until the monthly bill arrives. With telemetry, the expensive task types are immediately visible and can be targeted for optimization.

4. **Quality-without-measurement**: "the system works well" is an unverifiable claim without verify outcome data. With verify outcome data, "works well" becomes "84% of tasks pass verify on first attempt; 12% require one retry; 4% require operator intervention."

5. **Post-deploy blindness**: agents that write and commit code produce changes at a rate the production feedback loop may not absorb. Session telemetry records that a verify step passed — but has no signal for whether the deployed code is working in production. A post-deploy error, regression, or silent failure that occurs after the agent's session ends is invisible to the observability system. At agent velocity (10x human commit rate), the gap between "agent thinks it's done" and "production is healthy" becomes the primary blind spot. Defects arrive faster than any human monitoring cadence designed around human commit rates.

---

## §First Principles

### 1. Log the event, not the content

Telemetry records what happened (mode invoked, reference loaded, tool called, verify outcome) — not the content of those events (the full prompt, the full tool response, the full reference). Content is PII-adjacent and expensive to store; events are cheap and sufficient for analysis.

The distinction: `{ "event": "reference_loaded", "skill": "adia-ui-kit", "reference": "pattern-gallery.md", "session_id": "abc123", "turn": 7 }` is telemetry. The full content of `pattern-gallery.md` is not.

### 2. Append-only, minimal schema

Telemetry files grow; they never shrink. The schema must remain stable as the system evolves — a telemetry format that requires migration when a skill is renamed is a telemetry format that will be abandoned. Use append-only JSONL: one event per line, typed by `event_type`, with optional fields for event-specific data. New event types are additive; existing types never change.

### 3. Telemetry earns its keep by driving decisions

A telemetry system that produces data nobody reads is overhead, not observability. Telemetry earns its keep when it produces specific decisions: "prune reference X (zero accesses in 30 days)," "fix routing for skill Y (20% misrouting rate)," "optimize task type Z (3x average cost of similar tasks)."

The discipline: at least monthly, read the telemetry. Produce a short list of decisions it implies. Act on at least one. If no decisions are produced in a month, the telemetry schema is not capturing the right signals.

### 4. Behavioral data supersedes structural claims

A skill's SKILL.md may claim "agents typically invoke mode 2 for authoring tasks." Telemetry may show "mode 2 is invoked for 8% of authoring tasks; mode 1 handles 70% of them." The behavioral data is correct; the structural claim is wrong. When they conflict, update the structural claim — and ask why the model routes differently than expected.

Behavioral data is the ground truth for what the system actually does, not what it was designed to do. The two diverge over time. Telemetry is how you detect the divergence.

### 5. Privacy and cost are first-class constraints

Agent sessions may process sensitive data (PII, proprietary code, credentials). Telemetry must never capture prompt content, user data, or full tool responses. Beyond privacy: storing full session content at scale is expensive. The discipline: log event metadata only. If debugging requires content, use session replay with explicit, time-bounded, operator-scoped access — not as ambient telemetry.

### 6. The threshold test: telemetry before, or telemetry after?

Per Boris's B4 principle (ship → measure → write), the right order is: build the smallest testable version, run it, observe behavior, then improve. Telemetry that is designed upfront for hypothetical future analysis needs is over-engineered. Telemetry that captures observed failure modes and optimization targets is load-bearing.

The threshold: add a new telemetry signal when you have a specific question it would answer. Not because "it might be useful." The question must exist first.

---

## §The Rubric

### Dimension 1 [gate] — Session event logging completeness

Are the right events captured per session?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Per session: skill activated, mode selected, references loaded (by name), tool calls made (name + exit status), verify outcome (pass/fail/retry), token count (input + output), duration (seconds), error events (type, not content). Written to append-only JSONL. All fields typed and stable. |
| **4 — Good** | Most events captured. Token counts missing or approximate. Error events captured but as prose rather than typed. Schema stable for current skills. |
| **3 — Adequate** | Skill activation and mode selection captured. References and tool calls not systematically logged. Session-level token count available from API billing but not per-mode. |
| **2 — Poor** | Only task completion logged (success/failure). No mode, reference, or tool detail. Cannot diagnose why a session succeeded or failed. |
| **1 — Failing** | No per-session logging. System has never been instrumented. All analysis is retrospective and anecdotal. |

**Test**: run a typical session. Can you answer within 5 minutes: which skill, which mode, which references, which tools, what outcome, how many tokens? If any answer requires reading the raw conversation, the telemetry schema is incomplete.

---

### Dimension 2 [gate] — Reference utilization tracking

Is it known which references are useful and which are dead weight?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Per reference: load events (session + turn) AND access events (the reference content was actually read/used). Load-without-access events are tracked separately. 30-day rolling window query: any reference with 0 access events across 10+ loads is a dead reference candidate. |
| **4 — Good** | Reference loads tracked. Access not distinguished from load (conservative: load is treated as access). Dead references detectable at the "never loaded" level but not the "loaded but never accessed" level. |
| **3 — Adequate** | Reference loads tracked at the session level. Cannot query "how many sessions loaded reference X?" without manual log scanning. |
| **2 — Poor** | No reference-level telemetry. Dead references only discovered when an agent fails because a referenced file doesn't exist. |
| **1 — Failing** | No reference tracking at all. References may have been unused for months with no mechanism to detect it. |

**Test**: query the 30-day reference utilization. Which references have the highest load-to-access ratio (loaded often, accessed rarely)? Those are your optimization targets. If this query takes > 30 minutes, the telemetry is not queryable.

---

### Dimension 3 [gate] — Tool call telemetry

Are tool calls logged in enough detail to identify failure patterns?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Per tool call: tool name, arguments (non-sensitive), exit status (success / typed error), duration, retry count. Aggregated: per-tool failure rate, per-tool average duration, per-tool most common error type. Anomalies surface automatically (tool X failing at 3x baseline rate). |
| **4 — Good** | Tool name and exit status logged. Arguments logged for non-sensitive tools. No automated anomaly detection but queries are possible. |
| **3 — Adequate** | Tool calls logged at session level (which tools were invoked) but not per-call detail (arguments, per-call outcomes). Can answer "which tools were used" but not "which calls failed and why." |
| **2 — Poor** | Tool calls not logged. Failures only discovered via session-level outcomes or user reports. |
| **1 — Failing** | No tool telemetry. Tool hallucination rate, failure rate, and cost distribution are unknown. |

**Test**: which tool has the highest failure rate over the last 7 days? What is its most common error type? If you can't answer in < 10 minutes from telemetry, tool call observability is insufficient.

---

### Dimension 4 [gate] — Cost accountability (per task type)

Is token cost tracked at a granularity that enables optimization?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Token cost tracked per session, broken down by: cached input, non-cached input, output. Aggregated per skill, per mode, per task type. Monthly cost report generated automatically. Outliers (sessions costing 3x average for their task type) flagged. Per-task-type cost trend over time. |
| **4 — Good** | Token cost tracked per session with skill and mode labels. Monthly aggregation possible. Outliers detectable with manual queries. |
| **3 — Adequate** | Token cost available from API billing (aggregate). Skill-level breakdown requires session log parsing. Not automated. |
| **2 — Poor** | Total API cost known. Per-task-type cost unknown. Cannot determine which task types are expensive or why. |
| **1 — Failing** | No cost tracking below the monthly billing level. Token waste is invisible until it shows up as a budget surprise. |

**Test**: which task type costs the most per session? What is the average cost for the 3 most common task types? Has cost changed over the last 60 days? If none of these are answerable from current data, cost observability is insufficient.

---

### Dimension 5 [gate] — Quality signal capture (verify outcomes, retry rates)

Are quality signals — not just completion signals — being tracked?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Per session: verify outcome (pass on first attempt, pass after retry, fail), retry count, operator intervention count. Aggregated per skill and mode: first-attempt success rate, average retry count, intervention rate. Quality trend over time: is the system improving, stable, or degrading? |
| **4 — Good** | Verify outcomes logged. Retry count tracked. Intervention not systematically tracked (operator edits noted but not queryable). First-attempt success rate computable. |
| **3 — Adequate** | Session-level success/failure logged. No retry granularity. Cannot distinguish "succeeded after 1 retry" from "succeeded after 4 retries." |
| **2 — Poor** | Only binary success/failure at session level. No quality trend data. |
| **1 — Failing** | Quality signal is "did the user complain." No systematic outcome data. |

**Test**: for the most common task type, what is the first-attempt success rate? Has it changed in the last 90 days? If these are unanswereable, the quality feedback loop is broken.

---

### Dimension 6 [review] — Telemetry-driven improvement loop

Does telemetry actually drive changes, or does it accumulate unread?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Monthly telemetry review produces a list of specific decisions (prune reference X, fix routing for skill Y, optimize task type Z). At least one decision is acted on per review cycle. Decisions are tracked to outcome (did the metric improve after the change?). |
| **4 — Good** | Telemetry reviewed periodically. Most reviews produce at least one actionable finding. Follow-through on findings is inconsistent. |
| **3 — Adequate** | Telemetry reviewed when something goes wrong. Reactive rather than proactive. Several months of data may accumulate without being read. |
| **2 — Poor** | Telemetry written but rarely read. Data exists; no review cadence. |
| **1 — Failing** | No review cadence. Telemetry was set up once, data has been accumulating, and nobody has looked at it since the initial setup. |

**Test**: when was the last telemetry review? What decision did it produce? Was that decision implemented and did the metric improve? If none of these have answers, the telemetry system is instrumenting a system nobody is measuring.

---

### Dimension 7 — Post-deploy production feedback `[review]`

Does the observability system close the loop from agent session to production health?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Post-deploy production signals (error rate delta, latency regression, smoke tests against live traffic) are captured and associated with the agent session that produced the deployment. Session records are enriched with post-deploy outcome within a defined observation window (e.g., 30 minutes post-deploy). Production degradation triggers a notification linking back to the causal session. Rollback events are session-linked outcomes. First-ship-success rate (sessions that shipped without post-deploy incident) is a tracked metric with a 90-day trend. |
| **4 — Good** | Production monitoring exists and is separate from the agent system, but a documented workflow exists for linking a production incident to the causal session. Post-deploy signals are not automatically associated with session records but can be manually correlated within a reasonable time (< 1 hour). |
| **3 — Adequate** | Production monitoring exists for the system as a whole. No formal linkage to agent sessions. Correlating a production incident to an agent session requires manual investigation that typically takes > 1 hour. |
| **2 — Poor** | Production monitoring exists but is not structured to attribute incidents to specific deployments. An operator can see that something broke; they cannot see which session caused it without archaeology. |
| **1 — Failing** | Session-level telemetry is the only feedback signal. The observability system has no visibility beyond the agent's own verify step. Post-deploy defects are invisible until a user reports them. |

**Test**: an agent ships a change that breaks a production endpoint 20 minutes after deploy. Can an on-call engineer link the production alert to the specific agent session within 5 minutes of the alert firing — without access to the conversation transcript? If not: post-deploy observability is absent.

---

## §Anti-patterns

### AP-01 — Logging content instead of events

**Symptom**: telemetry file contains full prompts, full reference content, full tool responses. File grows at 100MB per day. Nobody queries it because it's too large. Privacy audit flags it because it contains PII. **Root cause**: "log everything" heuristic applied without thinking about what will actually be analyzed. **Correction**: log event metadata only. The event schema should be stable at < 500 bytes per event. If debugging requires content, use time-bounded session replay with explicit scope — not ambient logging.

### AP-02 — Measuring load, not access (the dead-reference blind spot)

**Symptom**: reference utilization report shows every reference is "used" (loaded). Pruning analysis finds nothing to remove. In reality, 6 references are loaded on every session but never actually contribute to any output. **Root cause**: "reference was loaded" treated as "reference was useful." These are not the same. **Correction**: distinguish load events (file read into context) from access events (content from this file appeared in the agent's reasoning). Only access events indicate usefulness.

### AP-03 — Aggregate-only cost tracking

**Symptom**: monthly API bill is higher than expected. Investigation needed to find the cause. Three weeks of manual log parsing later: one rarely-used task type that loads 12 references at cold-start is responsible for 40% of the cost. **Root cause**: cost tracked at the billing aggregate level, not per task type. **Correction**: tag every session with skill + mode + task type at log time. Aggregate by tag. The expensive task types are immediately visible without investigation.

### AP-04 — Telemetry graveyard (instrumenting but not reviewing)

**Symptom**: JSONL files exist. They've been growing for 4 months. Nobody has analyzed them. The system has had 3 routing failures in that period, all discoverable from the telemetry. **Root cause**: instrumenting is satisfying; reviewing is discipline. **Correction**: monthly telemetry review is on the calendar, not optional. Each review produces a list of decisions with owners. The review that produces no decisions is treated as a telemetry schema problem — the schema isn't capturing the signals needed to produce decisions.

### AP-05 — Over-instrumented before needed (speculative telemetry)

**Symptom**: 47 distinct event types, 12 aggregated dashboards, a telemetry service with 3 external dependencies. Used by a 3-person team with 5 skills. Telemetry maintenance costs more than the operational overhead it would prevent. **Root cause**: over-engineering telemetry before knowing what questions it needs to answer. **Correction**: per the threshold principle — add a telemetry signal when a specific question exists that it would answer. The question must precede the signal. Start with 5 event types (skill activated, reference loaded, tool called, verify outcome, session cost) and add from observed need.

### AP-06 — Quality as binary (success/failure only)

**Symptom**: telemetry shows 95% session success rate. Sounds great. In reality, 30% of "successful" sessions required 3+ retries and operator intervention before succeeding. The first-attempt success rate is 60%. The trend is declining. **Root cause**: binary success/failure doesn't distinguish "succeeded easily" from "succeeded after heroic effort." **Correction**: log: first-attempt outcome, retry count, operator intervention count. "Success" is qualified: "succeeded on first attempt," "succeeded after retry," "succeeded after operator intervention." The nuance is where the optimization signal lives.

---

## §Hard Tests

1. **The 5-minute test**: given the telemetry from the last 7 days, can you answer these questions in 5 minutes each: (a) which skill was most invoked, (b) which reference had the highest load-to-access ratio, (c) which tool had the highest failure rate, (d) which task type had the highest cost per session, (e) what was the first-attempt verify success rate? Any question that takes > 5 minutes indicates a telemetry query gap.

2. **The dead reference test**: query the last 30 days for references with load events but zero (or near-zero) access events. How many exist? These are prime pruning candidates.

3. **The anomaly detection test**: has any tool's failure rate increased by > 2x in the last 14 days? Has any task type's average cost increased by > 50% in the last 30 days? If these anomalies are not automatically surfaced, the system requires manual inspection to detect degradation.

4. **The improvement loop test**: pick a metric (first-attempt success rate for skill X). Find the value 90 days ago. Find the value today. Has it improved? If it hasn't changed, either the metric is not being used to drive improvements, or the improvements being made aren't targeting the right problems.

5. **The cost surprise test**: before looking at the monthly API bill, estimate what it should be based on your per-task-type cost data. Is the estimate within 20% of the actual? If not, cost tracking is not granular enough to predict costs from known usage patterns.

6. **The decision audit test**: over the last 90 days, how many changes to the skill library, harness, or tooling were explicitly informed by telemetry data? If the answer is zero, telemetry is producing data that isn't driving decisions — which means it's overhead, not observability.
