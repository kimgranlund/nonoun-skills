---
date: 2026-05-23
status: draft
version: "0.1.1"
---

# Evaluation and Validation Workflows — Best Practices Rubric

**Untested systems are hypotheses.** A skill library with no evals is a collection of guesses. A harness with no regression tests is a contract that cannot be verified. An agent workflow that has never been run against adversarial cases has never actually been tested — it has only been demonstrated under favorable conditions.

Evaluation is the discipline of treating your agentic systems the same way you'd treat production software: with held-out test sets, regression gates, adversarial coverage, and measured baselines. The failure to run evals before authoring design documents is the most commonly observed mistake in skills ecosystems — called out explicitly in BORIS-feedback.md §P5 and VISION-extensibility.md anti-pattern 8: spec-before-prototype.

**The Boris principle**: _"Give Claude a way to verify its work. If Claude has that feedback loop, it will 2-3x the quality."_ This applies to the skill system itself, not just individual invocations: give the skill system a way to verify that its skills work — with evals — and it will 2-3x the system's quality.

**Companion docs:**

- `agentic-coding.md` (this folder) — PEV as the per-invocation eval loop
- `skills-authoring.md` (this folder) — routing accuracy as the skills-level eval
- `../critics/eval-prompts.md` — the adversarial role-play prompts this rubric governs (critique mode)
- `prompt-control-modes.md` (this folder) — prompt agency modes and output contract expectations
- `BORIS-feedback.md §T1, §P5` — evals as falsification tests for the architecture

---

## §The Problem

Most agent system failures are not discovered by the system itself — they are discovered by users hitting broken behavior. The root cause is almost always the same: the system was never tested against the failure mode it encountered. There is no mechanism to distinguish a correct system from a plausible-sounding incorrect one.

Evaluation fills this gap. The specific failure modes evaluation prevents:

1. **Routing failures**: a skill's description claims to handle case X, but when tested, it routes X to a sibling skill or doesn't activate at all.
2. **Behavioral drift**: a skill that worked correctly 6 weeks ago now fails on the same inputs because a §Teach landing changed the decision tree in a non-obvious way.
3. **Harness bypass**: an agent was given a task the harness's surfaced skills should handle, but the agent improvised instead. The harness surfacing is broken.
4. **Adversarial blindspots**: the system passes all happy-path tests but fails under any unusual phrasing, edge case, or adversarial input.
5. **Untestable claims**: the system's design docs assert properties ("this skill routes correctly," "this workflow closes the PEV loop") that have never been measured. Claims without measurement are hypotheses.

---

## §First Principles

### 1. Fresh context is a non-negotiable eval property

An evaluator who built the system being evaluated will unconsciously steer toward success. They know how to phrase inputs to avoid the rough edges; they know which modes to use; they have the background knowledge that makes ambiguous instructions interpretable. This is not evaluation — it is self-confirmation.

**Fresh context** means: a new agent session with no prior knowledge of the system under review. The evaluator reads only what a genuine first-time user would read. This is the difference between "I know this works because I built it" and "I know this works because a stranger tested it."

For role-play evaluations: the agent impersonating Boris, Steve, or Elon must have fresh context — no memory of having built the system, no author's intuition. If the role-play agent shares context with the author agent, the evaluation is contaminated.

### 2. Adversarial evals find more than happy-path evals

Happy-path evals confirm that the system works when used correctly. They are necessary but not sufficient. **Adversarial evals** test:

- Ambiguous inputs (does the skill activate when it shouldn't? does it fail to activate when it should?)
- Edge cases (what happens at the boundary of the skill's stated scope?)
- Incorrect inputs (what does the skill do when given inputs from the wrong domain?)
- Role-play critics (what does an expert with adversarial intent find wrong with the system?)

A system that passes only happy-path evals has demonstrated "this works when nothing is surprising." It has not demonstrated "this works in production."

### 3. Baselines before claims

A routing eval that reports "96.7% accuracy" is meaningful only if you know what 50% accuracy looks like (random routing among N skills = 1/N) and what the previous version's accuracy was. Claims without baselines are marketing, not measurement.

Every eval should produce: (a) the current score, (b) the random baseline for context, (c) the previous version's score for regression detection. Without all three, the score is a fact without an interpretation.

### 4. Eval regression gates before description edits

A skill description edit that doesn't run the routing eval is a guess about routing accuracy. The routing eval is the regression check. Without it, description edits compound — each one may help the target case while hurting 5 adjacent cases, and no one notices until 3 weeks of edits have accumulated into a 15% accuracy drop.

The mechanized gate: any edit to a skill's `description:` or `trigger:` fields must re-run the routing eval and confirm no accuracy drop below the established floor. This converts description editing from a vibes-based operation to a measured one.

### 5. Role-play evaluations must be grounded in the persona's actual positions

A "Boris Cherny evaluation" that asks "does this look good?" is not a Boris Cherny evaluation. Boris has specific, documented positions: PEV is the central loop; vanilla > ceremony; ship → measure → write; evals before specs. An agent impersonating Boris should be briefed on these positions and should apply them. Generic adversarial questioning produces generic feedback. Persona-grounded questioning produces feedback calibrated to the perspective that matters.

### 6. The N=1→N=3 graduation criterion applies to evals too

A single eval run against a new skill is a hint, not a proof. Three eval runs against three different representative tasks, producing consistent results, is a pattern. Evals are not one-time events — they are the regression infrastructure that makes skill editing safe to do at any velocity.

### 7. Output contracts are eval interfaces

A freeform answer is difficult to score. A stable output contract turns agent behavior into an evaluable interface: the scorer can check whether required fields are present, whether evidence is cited, whether risks are separated from facts, and whether the next action is safe. Without an output contract, evaluation drifts into taste. With one, evaluation can become a regression gate.

---

## §The Rubric

### Dimension 1 [gate] — Routing eval coverage

Does the skill ecosystem have routing evals, and are they run as regression gates?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Routing corpus with ≥20 phrases per senior skill, plus ambiguous and negative cases. Scorer produces accuracy + per-skill F1 + no-skill F1. Run on every description/trigger edit. Accuracy floor established (e.g., 92%). Any drop below floor blocks the edit. |
| **4 — Good** | Routing corpus exists (may be smaller, 10-15 phrases per skill). Scorer exists. Run manually before major description changes. Floor not yet established as a hard gate. |
| **3 — Adequate** | Routing corpus exists as a list of test phrases. No automated scorer. Manual review confirms correct routing on each change. |
| **2 — Poor** | No routing corpus. Description edits made by intuition. No regression detection mechanism. |
| **1 — Failing** | No routing evals. System has never been tested for routing accuracy. Claims about routing are unverified assertions. |

**Test**: edit one skill's description (minor change). Was the routing eval run? Did the score change? If neither question can be answered, the eval infrastructure is missing.

---

### Dimension 2 [review] — Behavioral eval coverage

Beyond routing: does the system test whether skills produce correct outputs?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Per-skill behavioral evals: input phrase → expected mode + expected references loaded + expected verify target invoked. Run after every §Teach landing. Baseline documented. Regressions surface within one session of being introduced. |
| **4 — Good** | Behavioral evals for the highest-stakes modes (e.g., release skill's deploy mode). Other modes tested manually. |
| **3 — Adequate** | Behavioral evals planned but not yet implemented. The verify step in PEV acts as an informal post-hoc eval. |
| **2 — Poor** | No behavioral evals. Correctness verified by "it worked last time." Regressions discovered by users. |
| **1 — Failing** | No evals of any kind for skill behavior. |

**Test**: trigger the most critical mode in the most load-bearing skill. Is there a documented expected behavior to compare against?

---

### Dimension 3 [review] — Fresh-context eval discipline

Are evaluations run with genuine fresh context, or contaminated by author knowledge?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | All evals use a fresh agent session with no prior context. Role-play evals brief the agent on the persona's positions but not on the system's internal design. Evaluator is explicitly prohibited from using information not available to a first-time user. |
| **4 — Good** | Evals run in a fresh session. Role-play persona briefing doesn't reveal internal design choices. Some contamination possible from implied knowledge in the prompts, but minimal. |
| **3 — Adequate** | Evals run by the author in their existing session. Some unconscious steering toward success. Evaluation is useful but not rigorous. |
| **2 — Poor** | Author tests their own work in the same session they built it. Extensive unconscious bias toward confirming it works. |
| **1 — Failing** | "Testing" consists of "I tried it and it worked." No fresh context. No systematic inputs. |

**Test**: pick a skill you didn't build. Read only the cold-start harness (AGENTS.md) and the skill's SKILL.md. Can you complete the skill's primary task correctly? This simulates fresh-context evaluation.

---

### Dimension 4 [gate] — Adversarial eval coverage

Does the eval corpus include cases designed to find failures, not confirm successes?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Eval corpus includes: ambiguous activations (phrases that could activate multiple skills), boundary cases (phrases at the edge of the skill's stated scope), negative cases (phrases that should NOT activate any skill), and role-play adversarial reviews covering all rubric dimensions. |
| **4 — Good** | Ambiguous and negative cases present in the routing corpus. Role-play evals run at major version points. Boundary cases present for high-stakes modes. |
| **3 — Adequate** | Routing corpus is primarily happy-path. A few negative cases. No systematic adversarial review. |
| **2 — Poor** | Eval corpus is entirely happy-path. Every test phrase is one the author designed to succeed. |
| **1 — Failing** | No adversarial coverage. System has never been tested against inputs designed to find failures. |

**Test**: take the routing corpus. Count happy-path phrases vs. adversarial (ambiguous + negative + boundary). If the ratio is less than 3:1 happy-path to adversarial, the corpus is probably too easy.

---

### Dimension 5 [review] — Role-play evaluation quality

When role-play evaluations are used (Boris, Steve, Elon, or domain experts), are they rigorous?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Role-play agent briefed on the persona's documented positions (citations to real sources). Questions are specific and cite evidence from the artifact under review. Findings are classified by severity (critical / major / minor / noise). Follow-up actions tracked. Persona is adversarial, not complimentary. |
| **4 — Good** | Persona briefed with key positions. Questions are specific. Some findings cite evidence; others are impressionistic. Evaluation produces actionable improvements. |
| **3 — Adequate** | Persona is named and roughly characterized. Questions are generic ("is this good design?"). Findings are vague but directionally useful. |
| **2 — Poor** | "Impersonation" means the agent uses the person's name but applies generic criticism. Findings are indistinguishable from any generic reviewer's feedback. |
| **1 — Failing** | Role-play evaluation is performative. The persona agrees with the design and praises it. No real adversarial pressure. |

**Test**: run a role-play evaluation. Does the agent cite specific lines? Does it produce critical findings, not just minor ones? If every finding is "minor" or "noise," the role-play is not adversarial enough.

---

### Dimension 6 [gate] — Eval maintenance (baselines, regression gates, schedules)

Are evals maintained as living infrastructure, or authored once and forgotten?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Baseline scores documented and versioned. Regression floor enforced as a gate on relevant edits. Evals re-run on a schedule (quarterly minimum). Corpus updated when new failure modes are discovered in production. Stale evals (testing scenarios no longer present) are pruned. |
| **4 — Good** | Baseline scores documented. Regression floor enforced for high-stakes edits. Some corpus decay (old cases not pruned) but not causing false passes. |
| **3 — Adequate** | Baseline documented once. No regression gate. Evals run periodically but not consistently. |
| **2 — Poor** | No maintained baseline. Evals run ad-hoc when someone remembers. Score fluctuates with no tracking. |
| **1 — Failing** | Evals were run once at v1.0 and never touched again. Corpus reflects the system as it was, not as it is. |

**Test**: find the baseline score for the most important eval. When was it last run? What was the score then vs. now? If you can't answer these questions, the eval has no maintenance discipline.

---

---

### Dimension 7 [gate] — Output contract evaluability

Do evals check the shape and evidence quality of the agent's output, not just the final answer?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Eval scorer checks required fields, evidence presence, risk separation, verification reporting, and next-safe-step quality. Freeform summaries fail unless the contract is satisfied. |
| **4 — Good** | Output contract checked manually or semi-automatically. Most required fields enforced. |
| **3 — Adequate** | Expected output shape documented but not consistently scored. Reviewers notice missing fields ad hoc. |
| **2 — Poor** | Evals score only high-level correctness. Output may be unusable for handoff even when marked pass. |
| **1 — Failing** | No output contract. Evaluation depends on subjective reading of prose. |

**Test**: take a passing eval output and remove the verification evidence or risk field. Does the eval fail? If not, the output contract is not enforced.

## §Anti-patterns

### AP-01 — Spec-before-prototype (the original sin)

**Symptom**: the vision document and best-practices rubrics were authored before any evals were run. They describe the _intended_ behavior of the system, not the _observed_ behavior. **Root cause**: writing theory first feels like progress. Authoring evals first feels like incomplete work because nothing is "ready" to test yet. **Correction**: ship the smallest testable version. Run evals. Observe what the model actually does. Then write the meta-docs that explain the pattern. Boris: "PRDs are dead. There's no way we could have shipped this if we started with Figma or PRDs." The right order: ship → measure → write. Not write → ship → maybe-measure.

### AP-02 — Happy-path corpus (confirmation bias at scale)

**Symptom**: every phrase in the routing corpus was designed to succeed. The eval confirms the system works when used as intended. Nothing tests what happens when the user does something unexpected. **Root cause**: evals written by the system's author, who knows how to phrase inputs correctly. **Correction**: for every happy-path phrase, add one ambiguous phrase (could activate skill A or B), one negative phrase (should not activate any skill), and one boundary phrase (at the edge of the stated scope). A 3:1 happy-path to adversarial ratio is the minimum for a useful corpus.

### AP-03 — Contaminated fresh context

**Symptom**: the author tests their own skill in the same session they built it. They know the rough edges; they unconsciously avoid triggering them. The test confirms the skill works under expert guidance, not under first-time use. **Root cause**: it's faster and easier to test in the same session. **Correction**: always eval in a fresh session. If using role-play, brief the persona on their positions and the artifact to review — never on the system's internal reasoning or design choices. The evaluator must be informationally isolated from the builder.

### AP-04 — Generic role-play (persona in name only)

**Symptom**: "Boris review" produces generic feedback: "looks good," "could be clearer," "consider adding examples." No specific citations. No hard questions. No critical findings. **Root cause**: the agent impersonating Boris wasn't briefed on Boris's actual positions. It applied generic "helpful reviewer" behavior instead. **Correction**: ground the persona brief in documented positions (howborisusesclaudecode.com, primary source quotes, stated methodology). The persona's questions should directly apply their known positions: Boris asks "where are your evals?" not "could this be improved?"

### AP-05 — Eval as one-time event

**Symptom**: evals were run at v1.0. The system has been through 3 major versions and 20 §Teach landings since. The evals still pass — because they test v1.0 behavior, which hasn't changed much. The system's new behavior has never been tested. **Root cause**: treating evals as a milestone rather than as regression infrastructure. **Correction**: every §Teach landing re-runs the behavioral eval for the affected skill. Every description edit re-runs the routing eval. Evals are not done; they are the ongoing check that editing is not breaking things.

### AP-07 — Freeform-output pass

**Symptom**: an eval passes because the answer sounds right, even though it omits verification evidence, risk, or next action. **Root cause**: the eval checks semantic correctness but not handoff quality. **Correction**: include output-contract assertions in the scorer. Required fields are not style; they are part of correctness.

### AP-06 — Severity inflation (everything is "minor")

**Symptom**: a role-play eval produces 12 findings, all classified "minor." The author accepts them all as low-priority, schedules them "next sprint," and ships. Three weeks later, one of the "minor" findings turns out to be a critical routing failure. **Root cause**: evaluators default to "minor" to avoid confrontation. Authors accept "minor" because it's actionable without being urgent. **Correction**: every evaluation must try to produce at least one critical finding. If no critical findings emerge after a thorough adversarial pass, the evaluator should explicitly document: "I looked for critical findings and couldn't find any because [specific reasons]." "No critical findings" as an absence of looking is a different thing from "no critical findings" as a result of thorough search.

---

## §Hard Tests

1. **The fresh-start test**: find someone who didn't build the skill. Give them only the harness and the skill's SKILL.md. Ask them to complete the skill's primary task. Count mid-task interventions. Each intervention is a discoverability or clarity failure that happy-path testing would miss.

2. **The regression test**: make a small change to a skill description. Run the routing eval. Did accuracy change? If you can't answer this within 5 minutes, the eval infrastructure is not production-grade.

3. **The adversarial phrase test**: add 5 ambiguous phrases to the routing corpus (phrases that could activate multiple skills). How many route correctly? If < 60%, the skill descriptions are under-differentiated.

4. **The Boris test**: find an agent. Brief it on Boris's documented positions (PEV, evals before docs, vanilla > ceremony). Give it the skill library and ask it to find the gaps. If the agent produces only minor findings — or the findings don't specifically apply Boris's positions — the role-play briefing was inadequate.

5. **The baseline test**: what is the current routing accuracy? What was it 90 days ago? If you can't answer the second question, there's no regression baseline — the current score is a snapshot with no context.

6. **The production-failure test**: list the last 3 agent errors that reached users. For each: was there an eval that should have caught it? If yes, why did it miss? If no, what eval would catch the class of failure this represents?

7. **The spec-before-prototype audit**: for each major design document in the system, ask: were evals run before this document was authored? If the documents describe intended behavior rather than observed behavior, they are specifications, not lessons.

8. **The output-contract regression test**: run a behavioral eval and intentionally omit one required output field. The scorer should fail the run. If it still passes, the eval is measuring answer plausibility, not operational usability.
