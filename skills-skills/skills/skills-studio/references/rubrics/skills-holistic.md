---
date: 2026-05-31
status: draft
version: "0.2.0"
---

# Holistic Skill Quality — 10-Dimension Meta-Rubric

**A skill is a cognitive contract, not a document.** It makes promises about what the agent will do, when, and how it will verify. This rubric asks whether all ten load-bearing concerns are addressed — because a skill that scores 5/5 on any one dimension can still fail if another dimension is missing.

This is a **synthesis rubric**, not a replacement for the individual rubrics. Each dimension below points to a detailed rubric for drill-down. The value here is coverage — confirming that all ten concerns were considered, not just the ones that were obvious.

**Grounding**: Synthesized from the full rubric library and the 9-critic adversarial eval corpus. The model emerged from the observation that individual rubrics missed cross-dimensional failures (e.g., a mechanized skill with no injection guard; a well-routed skill with self-assessment as its verify step). It began as eight dimensions; **Context Engineering (D9) and Plan Anatomy (D10) were promoted from cross-cutting rubrics** once their solo/authoring scale made them per-skill quality dimensions (see §Scope).

---

## §The Problem

The individual rubrics in this library are drill bits. They score specific concerns deeply. But a skill can score 5/5 on `skills-authoring` (description quality, discoverability, inversion) and still have:

- A control mode that uses prescriptive instructions for a judgment task — producing brittle, over-fitted behavior
- Rubric criteria that are stated as facts but are actually untested hypotheses
- No injection guard for external content it reads while having write access
- A verify step that closes on the agent's own output, not on real product state

**The individual rubrics don't catch these failures because they don't look across dimensions.** This rubric is the site plan that tells you which drills to run and whether all ten load-bearing concerns were considered.

---

## §First Principles

### 1. Prompting and rubrics are different tools for different task entropy

Instructions are for deterministic tasks (the agent should do X, not choose). Rubrics are for judgment tasks (the agent should evaluate against criteria and exercise judgment). The choice between them is not stylistic — it is a consequence of task entropy. Using instructions for judgment tasks produces brittle, over-fitted behavior. Using rubrics for deterministic tasks produces variance where there should be none. **Control mode is a design decision, not a default.**

### 2. A skill without evaluation infrastructure doesn't compound — it accumulates drift

Without a routing corpus, routing accuracy is unknown. Without a PEV loop that closes on real product state (not self-assessment), quality is a belief. Without a regression baseline, every change is vibes. Evaluation infrastructure is what separates a skill that improves from one that becomes archaeology.

### 3. Mechanization is the compounding engine

Each time an agent manually executes a repeatable, deterministic procedure, variance is introduced and context is consumed. Each time that procedure becomes a script, variance disappears and the skill gets faster. Mechanization debt is the single largest predictor of non-compounding skills over a 6-month window.

### 4. Trust is a design property, not a model property

A skill that reads external content while having write access is structurally exploitable regardless of what the system prompt says. "The model will refuse" is not a defense — it degrades under context pressure. Injection defense and scope containment must be designed in.

### 5. Extensibility is measured by evidence, not by infrastructure

A ROADMAP.md can exist without any item ever graduating into the skill. A §Teach section can exist without any session's learnings being incorporated. The extensibility dimension scores on observed compounding over real invocations, not on the presence of extension infrastructure.

---

## §The Rubric

### D1 — Instructions & Harness Design `[review]`

Does the skill route correctly and equip a cold-start agent within the first screen?

| Score | Evidence |
| --- | --- |
| **5** | Description ≤ 1024 chars: one WHAT sentence, specific WHEN conditions, NOT clause for nearest sibling. SKILL.md first screen: mode menu, posture, reference pointers. §SelfAudit present. Agent routes to correct mode within 3 cold-start actions. |
| **4** | WHAT + WHEN in description. Mode menu present. §SelfAudit present. Minor sibling overlap or 2-read first screen — not causing active misrouting. |
| **3** | Description activates correctly but is over-broad. No §SelfAudit. Agent completes primary task but improvises setup steps. |
| **2** | Missing NOT clause with sibling overlap. No §SelfAudit. Agent must guess posture and starting mode. |
| **1** | Description is a tag cloud or vague one-liner. Skill cannot be discovered without being named explicitly. |

**Go deeper**: `harness-design.md`, `skills-authoring.md` D1–D2. **Test**: give a fresh agent the skill's primary task without naming the skill. Does it route correctly within 5 actions?

---

### D2 — Control Mode Design `[review]`

Does each mode in the skill use the right control mode for its task entropy?

The five control modes (`prompt-control-modes.md`): **Instruction** (constrain the action, deterministic) → **Procedure** (constrain the sequence, known method) → **Rubric** (constrain the judgment, quality-matters-more-than-method) → **Objective** (constrain the outcome, path requires judgment) → **Mission** (constrain the process, decomposition required).

| Score | Evidence |
| --- | --- |
| **5** | Every mode uses the appropriate control mode. Deterministic sub-tasks use Instruction/Procedure. Judgment sub-tasks use Rubric. Open-ended composition uses Objective/Mission. No mismatch. |
| **4** | Mostly correct. 1–2 mismatches exist (e.g., a judgment step written as a procedure) but don't cause active failure. |
| **3** | Mixed. Some judgment tasks are over-specified as procedures; some deterministic tasks are under-specified as objectives. Produces variance or inflexibility. |
| **2** | Most judgment tasks written as prescriptive instructions. Agent follows steps rather than applying judgment — inconsistent results across runs. |
| **1** | Single control mode used throughout regardless of task type. Either everything is instructions (over-constrained) or everything is mission (under-constrained). |

**Go deeper**: `prompt-control-modes.md`. **Test**: for each mode, classify the task entropy (deterministic / judgment / open-ended). Classify the actual control mode used. Count mismatches. > 1 mismatch = D2 fails.

---

### D3 — Rubric Quality `[gate]` `[review]`

Where the skill uses scoring criteria, are they labeled, calibrated, and falsifiable?

| Score | Evidence |
| --- | --- |
| **5** | Every quality criterion labeled `[gate]` (pass/fail, mechanical), `[review]` (explicit evidence required), or `[hypothesis]` (unverified — measurement plan present). Gate criteria state their specific check. Review criteria cite their evidence source. Hypothesis criteria have a measurement plan. No criterion is stated as a fact that is actually an untested assumption. |
| **4** | Most criteria labeled. 1–2 hypothesis items missing the label but recognizable as unverified. Gate checks present for all `[gate]` items. |
| **3** | Criteria present but unlabeled. Reader cannot distinguish mechanical checks from judgment calls. Performance claims stated as facts without evidence. |
| **2** | Some criteria present but stated as assertions. No labels. No measurement plan. Scores vary by reviewer because criteria are subjective. |
| **1** | No explicit rubric. Quality is "know it when you see it." Cannot score consistently across reviewers or invocations. |

**Go deeper**: `evaluation-workflows.md`, `skills-authoring.md` D5 (drift resistance). **Test**: run the same rubric with two agents against the same artifact. If any dimension differs by > 1, the rubric is not calibrated — it is generating noise, not measurement.

---

### D4 — Mechanization & Tool Use `[gate]`

Are repeatable, deterministic, failure-prone procedures in scripts — not prose the agent re-executes by hand?

| Score | Evidence |
| --- | --- |
| **5** | Every step that is (a) repeatable AND (b) has clear pass/fail AND (c) has silent failure modes is a script with `--help` output. No mechanize-bait steps remain in prose. Agent decides and observes — does not manually execute what a script should do. |
| **4** | Most procedures inverted. 1–2 judgment-heavy prose blocks remain for genuinely non-deterministic steps. Scripts have `--help`. |
| **3** | Some scripts exist; 3+ multi-step prose procedures remain for steps that could be scripts. Variance between invocations. |
| **2** | Most procedures are prose. Agent is the script. High variance. |
| **1** | No mechanization. Every mode is a list of manual steps. The skill is a tutorial, not a capability contract. |

**Go deeper**: `inversion-and-abstraction.md`, `mechanization-best-practices.md`. **Test** (mechanize-bait count): for the most-used mode, count steps that are repeatable + have clear pass/fail + have silent failure modes or destructive blast radius. Any step meeting 2+ criteria is mechanize-bait. Count > 3 = D4 fails.

---

### D5 — Evaluation `[gate]`

Is there a routing corpus, a behavioral eval, and a verify target that closes on real product state?

| Score | Evidence |
| --- | --- |
| **5** | Routing corpus: ≥ 10 trigger + ≥ 5 adversarial phrases, F1 measured. Behavioral eval: ≥ 3 end-to-end cases with assertions. Verify target: names real external product state — not "tests pass" or "agent reviewed output." Regression baseline exists (prior F1 recorded). |
| **4** | Routing corpus present and measured. Behavioral eval exists. Verify target names real product state. Missing: adversarial corpus OR regression baseline. |
| **3** | Routing phrases in description but no corpus file, F1 never measured. Verify target exists but points to internal state (build passes, linter clean). |
| **2** | Routing phrases in description only. No corpus file, no behavioral eval. Verify step is self-assessment. |
| **1** | No routing eval, no behavioral eval, no verify target. Quality is unknown. Every description edit is a vibes-based change. |

**Go deeper**: `evaluation-workflows.md`, `skills-authoring.md` D4 (PEV binding). **Test**: what was the routing F1 90 days ago? If unknown: no regression baseline exists. Every current score is a snapshot with no interpretive frame.

---

### D6 — Extensibility `[review]`

Does the skill compound over invocations, and does it have a governed path for incorporating new knowledge?

| Score | Evidence |
| --- | --- |
| **5** | ROADMAP.md: Planned / Deferred / Out-of-scope populated from known items (not template comments). §Teach or learning protocol: decision tree for where new knowledge goes. Observed compounding: later invocations measurably faster. No forward-looking notes buried in CHANGELOG or SKILL.md. |
| **4** | ROADMAP.md populated. §Teach exists. Compounding observed qualitatively. 1–2 forward-looking notes in CHANGELOG but not causing drift. |
| **3** | ROADMAP.md present but template-only (all sections empty). §Teach absent or described but unused. No observed compounding evidence. |
| **2** | No ROADMAP.md or template-only. Deferred scope buried in CHANGELOG or SKILL.md comments. Future contributors will re-add excluded features or duplicate deferred work. |
| **1** | No extension path. Every new capability is an ad-hoc SKILL.md append. Skill accumulates drift instead of insight. |

**Go deeper**: `skill-extensibility.md`, `skills-authoring.md` D6–D7. **Test** (ROADMAP pollution scan): grep CHANGELOG and SKILL.md for `planned`, `future`, `out of scope`, `TODO`, `not yet`, `considered but`. Any match outside ROADMAP.md = convention not enforced.

---

### D7 — Security & Trust Boundaries `[gate]`

Is the skill's scope contained, with an explicit injection guard and bounded blast radius?

| Score | Evidence |
| --- | --- |
| **5** | Explicit scope statement (what the skill can and cannot read/write). If the skill reads untrusted content: either (a) reading agent is isolated from writing agent, or (b) content is treated as data with a documented injection guard. Destructive operations require structural confirmation (not just instructions). Credentials never transit agent context. |
| **4** | Scope statement present. Injection guard documented. One gap: credentials may transit context for narrow operations, OR destructive ops use instruction-based (not structural) confirmation. |
| **3** | Scope implicit. No injection guard. "The model is instructed to be careful" is the only protection. Blast radius not assessed. |
| **2** | Skill reads untrusted content and can write files in the same agent context with no documented defense. Blast radius of the most likely mistake not assessed. |
| **1** | No scope statement, no injection guard, no blast radius assessment. Lethal trifecta possible: private data access + untrusted content exposure + external action capability in one agent context. |

**Go deeper**: `security-and-scope-containment.md`. **Test** (lethal trifecta): does the skill (a) access private data, (b) process untrusted content (user files, external URLs, API responses), (c) take external actions (write files, call APIs, push commits)? Two present = elevated risk. All three = structural separation required; model behavior is not sufficient.

---

### D8 — Observability `[review]`

Is there a post-invocation signal that proves the skill ran correctly — without replaying the session?

| Score | Evidence |
| --- | --- |
| **5** | Verify target names real external product state (not self-assessment). Audit trail produced per invocation (structured, queryable). A human or automated check can confirm correctness post-invocation without reading the session transcript. |
| **4** | Verify target names real product state. Audit trail exists but requires human effort to query (logs, not structured index). |
| **3** | Verify target exists but names internal state (compilation succeeds, linter clean, tests pass). No audit trail. Post-invocation check requires transcript replay. |
| **2** | Verify step is self-assessment: the agent reviews its own output. Loop closes on the agent's beliefs, not on reality. |
| **1** | No verify step. Work is declared done when the last instruction completes. There is no signal — internal or external — that the skill succeeded. |

**Go deeper**: `observability-and-telemetry.md`, `agentic-coding.md` D2 (verify-against-reality). **Test**: after the most recent invocation, answer without reading the transcript: did the skill succeed? If the answer requires archaeology: D8 fails.

---

### D9 — Context Engineering `[review]`

Is the skill's context a precision instrument — loaded by relevance and kept fresh — or a dumping ground the model must sort out?

| Score | Evidence |
| --- | --- |
| **5** | References load on explicit task-relevant conditions (progressive disclosure), not preemptively — no reference is loaded "just in case." Staleness is checked before stale context reaches the model; conflicting context is surfaced, not silently resolved. The agent reads close to the minimum effective dose. |
| **4** | Mostly relevance-driven loading with stated load conditions. 1–2 preemptive loads, or a missing freshness check on one source — not causing active misreasoning. |
| **3** | Some references load preemptively; load conditions are vague ("load when needed"), so the agent guesses what to pull. No staleness check. |
| **2** | Most context is front-loaded as noise that competes with the signal. No relevance discipline; stale context can reach the model silently. |
| **1** | The skill dumps its whole reference tree up front with no load conditions and hopes the model sorts it. Context is a dumping ground. |

**Go deeper**: `context-engineering.md`, `progressive-context-construction.md`. **Test** (preemptive-load audit): for a typical task, list the references loaded and how many were actually accessed. If preemptive loads (0 accesses) outnumber relevant loads, D9 fails. (Distinct from D1, which scores the _static_ harness; D9 scores the _dynamic, per-task_ context.)

---

### D10 — Plan Anatomy `[review]`

When the skill produces a plan, is it a well-structured bridge from intent to reliable execution — or a vague sequence the model improvises through, producing a different path each run?

| Score | Evidence |
| --- | --- |
| **5** | Subgoals are independently executable and each produces a verifiable intermediate state. Dependencies are explicit (not order-of-appearance implicit). A checkpoint validates preconditions before each expensive or irreversible step. Completion criteria name real external state. The most likely failure point has an explicit recovery path. |
| **4** | Mostly verifiable subgoals with explicit dependencies and checkpoints. 1 implicit dependency, or a missing recovery path for a non-critical step. |
| **3** | The plan is a narrative: some subgoals are vague phase labels ("think about the architecture") with no verifiable state. Dependencies are implicit; completion is "I did the steps." |
| **2** | A sequence of actions with no verifiable intermediate state and no checkpoint before expensive steps. Completion is self-referential ("I wrote the file"), not outcome-based. |
| **1** | No plan structure — the agent improvises. Identical inputs produce different execution paths; failures spiral rather than recover. |

**Go deeper**: `plan-anatomy.md`, `agentic-coding.md` (the Plan→Execute→Verify loop). **Test** (subgoal verifiability): count the plan's subgoals that produce a verifiable intermediate state vs vague phase labels. > 30% vague = the plan is a narrative, not a structure. (Distinct from `agentic-coding`, which scores whether the loop _closes_; D10 scores whether the _plan itself_ is well-formed.)

---

## §Scope — what these ten cover, and what is deliberately cross-cutting

These ten are **per-skill quality dimensions** at solo/authoring scale — properties a single skill can be scored on in isolation. Three library concerns are intentionally **not** holistic dimensions:

- **Governance** (`governance.md`) — change control, audit trails, policy-as-code, override authority — is a **team/system concern** (team scale, runtime layer). A solo skill has no governance to score; it applies to a _system_ of skills and agents, so it stays a cross-cutting rubric rather than a holistic dimension. **This is why the meta-rubric is D1–D10, not D1–D11.**
- **D9 and D10 overlap their neighbors but earn their place:** Context Engineering (D9) overlaps D1, but D1 scores the _static_ harness while D9 scores the _dynamic, per-task_ context. Plan Anatomy (D10) overlaps `agentic-coding`, but that rubric scores whether the PEV loop _closes_ while D10 scores whether the _plan itself_ is well-formed.

Every `foundations/*.md` theory doc still has exactly one rubric (gated by `scripts/check-foundations-coverage.py`). Eight of the ten holistic dimensions drill into one foundation-paired rubric each, and D9/D10 drill into `context-engineering.md` / `plan-anatomy.md`. **`governance.md` is the one foundation-paired rubric with no holistic dimension** — applied to systems on demand, not scored per skill.

---

## §Anti-patterns (cross-dimensional)

These failures span multiple dimensions, which is why no single dimension rubric catches them.

### AP-H1 — The confident rubric without calibration

**Symptom**: Skill uses rubric-based judgment (D2 ✓), criteria are present (D3 partial), but every criterion is asserted without evidence or measurement plan. The rubric looks rigorous but produces different scores from different reviewers. **Root cause**: D3 [gate] failure (no calibration) combined with D5 failure (no behavioral eval to catch inconsistency between runs). **Correction**: For each `[hypothesis]` dimension, define a measurement plan and record the first scored application before calling the rubric usable.

### AP-H2 — The mechanized shell with a judgment core

**Symptom**: D4 scores high (scripts exist), but the scripts wrap judgment steps that are never made explicit. Confident output, no quality gate. **Root cause**: Mechanization of the wrong layer — execution is automated but the quality criterion is inside the black box. **Correction**: Judgment steps inside scripts must surface their criteria (D3) and produce structured output the verify step (D8) can inspect.

### AP-H3 — The trusted content reader

**Symptom**: Skill reads repo files or external URLs (reasonable alone), processes content through an agent that also writes to AGENTS.md or memory (reasonable alone), no injection guard (D7 missing). Fine until an adversarial file is introduced. **Root cause**: Each design choice reviewed in isolation. No one evaluated the combination — private-data + untrusted-content + external-actions — as a trifecta. **Correction**: Explicitly audit D7 whenever a skill reads external content. State the injection guard or the structural separation between reading and writing contexts.

### AP-H4 — The extensible skill that never extends

**Symptom**: D6 looks fine (ROADMAP.md present, §Teach defined) but the skill has not compounded in 3+ months. The extension path exists in theory. **Root cause**: D6 scored on structure, not on observed use. D5 failure (no behavioral eval to detect when the skill needs updating) and D8 failure (no observability to detect when quality is degrading). **Correction**: Score D6 on observed compounding, not on the presence of §Teach infrastructure.

---

## §Hard Tests

1. **The trifecta test** (D7): does the skill read untrusted content + take external actions + access private data? Two = elevated risk; all three = structural separation required.

2. **The cold-start test** (D1): fresh agent, target task, no mention of the skill. Routes correctly within 5 actions?

3. **The entropy-match test** (D2): for each mode, what is the actual task entropy? Deterministic tasks using Mode 3–5 = over-delegated. Judgment tasks using Mode 1–2 = over-constrained. Count mismatches. > 1 = D2 fails.

4. **The calibration test** (D3): two agents, same rubric, same artifact. Any dimension differing by > 1 = the rubric is noise, not measurement.

5. **The mechanize-bait count** (D4): for the most-used mode, count steps meeting 2+ of: repeatable, clear pass/fail, silent failure modes, destructive blast radius. Count > 3 = D4 fails.

6. **The baseline test** (D5): what was the routing F1 90 days ago? If unknown: no regression baseline. D5 fails.

7. **The ROADMAP pollution test** (D6): grep CHANGELOG + SKILL.md for `planned`, `future`, `out of scope`, `TODO`, `not yet`. Any match outside ROADMAP.md = D6 fails.

8. **The post-invocation test** (D8): without reading the transcript, confirm whether the most recent invocation succeeded. If the answer requires session replay: D8 fails — the verify target is self-assessment.

9. **The preemptive-load audit** (D9): for a typical task, count references loaded vs references actually accessed. Preemptive loads (0 accesses) outnumbering relevant loads = D9 fails — context is front-loaded noise.

10. **The subgoal-verifiability test** (D10): in the skill's plan for a complex task, count subgoals that yield a verifiable intermediate state vs vague phase labels. > 30% vague = the plan is a narrative, not a structure.
