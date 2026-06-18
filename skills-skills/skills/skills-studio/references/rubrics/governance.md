---
date: 2026-05-31
status: draft
version: "0.1.0"
---

# Governance — Best Practices Rubric

**Without governance, an agentic skill system has no memory of who decided what, no way to challenge a bad decision, and no mechanism to stop an agent from doing something its operators never authorized.** Skills encode behavior at scale — a single poorly-governed skill propagates across every consumer in the network. Governance is not bureaucracy; it is the set of structures that make accountability possible when something goes wrong, and correction possible before it compounds.

**Grounding**: Anthropic "Building Effective Agents" (2024); NIST AI Risk Management Framework 1.0 (2023); Simon Willison on LLM governance and prompt injection risk (simonwillison.net, 2023-2025); Mitchell Hashimoto on operator-seat discipline (hashimoto.io); Anthropic operator/user role distinction (docs.anthropic.com/en/docs/build-with-claude/claude-in-claude); Charity Majors on observability as accountability substrate (honeycomb.io/blog).

**Companion docs:**

- `skills-authoring.md` — authoring rubric; D7 covers verification targets (audit prerequisite)
- `evaluation-workflows.md` — eval governance is a sub-problem of governance
- `security-and-scope-containment.md` — scope containment is the enforcement arm of policy encoding
- `observability-and-telemetry.md` — audit trail infrastructure
- `harness-design.md` — harness is the policy-encoding surface for operator-level rules
- `multi-agent-coordination.md` — role separation becomes critical in multi-agent deployments

---

## §The Problem

Governance failure in agentic systems is usually invisible until it is catastrophic. A skill that was authored once, approved by no one, and deployed across forty consumers has no owner when it produces a wrong answer at 2 AM. An eval that scores "4 — Good" because the author who wrote the rubric also ran the eval is not an eval — it is a formality. An agent that can override its own verification gate "for efficiency" is an agent without a verification gate. These are not hypothetical edge cases; they are the default state of ungoverned skill libraries.

The core failure modes are three. First, **authority ambiguity**: the system has no clear answer to "who can change this?" and "who decided this was acceptable?" Changes accumulate through social pressure or convenience rather than explicit authorization. A corrective rule gets added to the harness by whoever noticed the failure; a skill gets deprecated by whoever got annoyed by it. There is no record, no challenge path, and no rollback. Second, **policy opacity**: behavioral constraints exist but are not machine-verifiable — they live in prose that agents read inconsistently and that humans interpret differently across teams. The gap between stated policy and actual behavior is undetectable until it surfaces as an incident. Third, **override creep**: emergency overrides, debug modes, and "for now" bypasses accumulate without expiry. Over time, the override surface is larger than the governed surface. No one knows what the actual policy is because the overrides are undocumented and often contradictory.

What governance provides is not control — agents cannot be controlled the way a traditional software system can. What governance provides is **accountability infrastructure**: the structures that make it possible to reconstruct what happened, who authorized it, and what the intended boundary was. Without that infrastructure, post-incident learning is impossible and recurrence is nearly guaranteed.

---

## §First Principles

### 1. Authorization must be explicit and traceable

Every consequential decision in a skill system — what a skill can do, who can invoke it, what constitutes a passing eval, when an agent can override a human — requires an explicit authorization record. "We agreed informally" is not authorization at governance scale. The question to ask of any policy: if the author left the team tomorrow, could a new maintainer determine why this rule exists and whether to keep it?

### 2. Role separation is a design requirement, not an org chart concern

Operators (those who configure the system), users (those who invoke skills), developers (those who author skills), and evaluators (those who score and approve skills) must have separated authority surfaces. When the same person authors a skill and approves its eval, the approval is structurally invalid regardless of their competence. Separation is not about distrust; it is about ensuring that errors in one role cannot propagate unchallenged.

### 3. Policy must be machine-verifiable, not just prose-stated

A policy that says "skills must not access external systems without explicit user consent" is only a governance artifact if it can be checked — by a script, a gate, a structured manifest field, or a mechanical pre-commit hook. Prose policies that live only in documents are intentions, not policies. The gap between stated and enforced policy is the primary surface for undetected governance failure.

### 4. Audit trails are the substrate of accountability

You cannot hold an agent — or a human — accountable for a decision that was not recorded. Every non-trivial state change in a skill system (skill version bump, eval score assignment, override grant, role assignment) must produce a durable, attributable record. "We can look at git history" is a starting point; it is not sufficient for systems where non-code decisions (eval approvals, override grants) also need traceability.

### 5. Override authority must be bounded, attributed, and time-limited

Every governance structure will face situations where the governed path is too slow or unavailable. Override authority is legitimate. Ungoverned override authority is a backdoor. Any override — human or agent — must name the authorizing party, document the reason, and carry an expiry. An override with no expiry is a permanent policy change that bypassed the change control process.

---

## §The Rubric

### Dimension 1 — Change Control `[gate]`

Who can modify a skill, and what process authorizes the modification? Is the process documented, followed, and verifiable — or is it informal convention that collapses under pressure?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every skill has a named owner in skill.json. Version bumps require a CHANGELOG entry with author attribution. Major version changes (breaking) require an explicit sign-off record (PR approval, review comment, or equivalent). Modification history is fully reconstructable from artifacts alone, without asking anyone. |
| **4 — Good** | Ownership is documented, CHANGELOG is maintained, but sign-off for major changes is social rather than structural (e.g., "team agreed in Slack"). History is mostly reconstructable. |
| **3 — Adequate** | CHANGELOG exists but is sometimes incomplete. Ownership is implicit (whoever last touched it). Breaking changes are recognizable in git but not explicitly flagged as requiring review. |
| **2 — Poor** | No CHANGELOG discipline. Skills are modified ad-hoc. Ownership is unknown. The only change history is git blame, and it is incomplete due to squash merges or force-pushes. |
| **1 — Failing** | Skills are edited in place with no versioning, no attribution, and no history. The current state of a skill cannot be compared to any prior state. There is no ownership concept. |

**Test**: pick a skill, open its CHANGELOG, and ask: who made the last three significant changes, when, and why? If the answer requires more than reading the CHANGELOG, score drops by at least one point.

---

### Dimension 2 — Eval Governance `[gate]`

Who decides what scores mean, and are evaluators separated from skill authors? Does the eval process produce authoritative records, or scores that exist only in conversation context?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Rubric definitions are versioned and owned separately from skills. Evaluators are not the skill authors for the skills they score. Scores are persisted in durable artifacts (e.g., `reviews/` directory, structured eval output). Score thresholds for promotion (draft→stable) are documented and consistent across skills. Score disputes have a defined resolution path. |
| **4 — Good** | Rubric ownership is separate. Evaluators are usually (but not always) different from authors. Scores are persisted. Promotion thresholds exist but are inconsistently applied. |
| **3 — Adequate** | Rubric exists and is shared, but authorship and evaluation are sometimes the same person. Scores are partially persisted (some in files, some lost to conversation). No explicit promotion thresholds. |
| **2 — Poor** | Authors self-evaluate. No rubric versioning. Scores are not persisted. "The skill feels ready" is the de facto promotion criterion. |
| **1 — Failing** | No eval process. Skills are promoted based on recency of authorship, not quality assessment. There are no rubrics, no scores, and no records. |

**Test**: for any skill marked "stable," locate the eval record that justified the promotion. If it cannot be found in the repo, the governance score for this dimension is 2 or lower.

---

### Dimension 3 — Role Separation `[review]`

Are operator, user, developer, and evaluator roles distinct — both in documentation and in practice? Can the same party simultaneously author, approve, and invoke a skill?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Roles are named and defined in system documentation (not just AGENTS.md). Each role has a documented authority surface (what they can change, approve, or invoke). Structural separation exists: the system prevents or records when the same party acts in two roles for the same artifact. Operator-level constraints cannot be overridden by user-level invocations. |
| **4 — Good** | Roles are documented. At least one structural gate exists for the most consequential role boundary (e.g., PR review requirement before deployment, owner-field validation). Role-conflation events are noted when they occur, even if not blocked. The operator/user boundary is respected in skill design. |
| **3 — Adequate** | Roles are named but not formally separated. The developer and evaluator roles are often the same person by default but this is recognized as a debt. Operator and user scopes are loosely distinguished in harness design but not consistently enforced. |
| **2 — Poor** | Developer and evaluator roles conflate regularly. There is no operator/user distinction in practice — any user can invoke any skill at any scope. Role separation is understood conceptually but produces no structural constraints. |
| **1 — Failing** | No role concept. Any party can author, approve, invoke, and modify any skill with no separation, no record, and no authority boundary. |

**Test**: can a user-level invocation override an operator-level constraint by rephrasing the prompt? If yes and there is no structural prevention or logging, this dimension scores 2 or lower.

---

### Dimension 4 — Audit Trail `[gate]`

What _non-code_ decisions are durably recorded — eval scores, overrides, and invocation failures?

**Scope note (independence from D1):** D1 (Change Control) covers code-artifact change history: who edited a file, when, and why. This dimension covers decisions that _leave no code artifact_ — an eval score assignment, an override grant, an exception approval. A system can score D1=5 (CHANGELOG is exemplary) and D4=1 (no eval record exists for any promotion decision). They are independent and should not be conflated.

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | All of: eval scores are persisted as durable, locatable artifacts (e.g., `reviews/` directory, not just conversation context); overrides are recorded with reason and authorizing party _before_ taking effect (not reconstructed afterward); invocation failures that deviate from expected behavior produce structured log entries. A decision that left no code artifact is independently locatable from artifacts alone in under 2 minutes. |
| **4 — Good** | Eval scores and override records exist. Override records may be informal (PR comment, description) but are present. Invocation failure logs exist but may not be structured. The record is locatable with moderate effort. |
| **3 — Adequate** | Eval records exist for recent skills but not historical ones. Overrides are not consistently recorded — some have records, some do not. Invocation failures are reproducible from existing logs only if you know where to look. |
| **2 — Poor** | Eval scores exist only in conversation context (lost after session). Override records are absent or inconsistent. A decision from six months ago is unlocatable without interviewing the people involved. |
| **1 — Failing** | No eval records, no override records, no invocation failure logs. The only non-code artifacts are the skills themselves. Post-incident reconstruction of any non-code decision is impossible from artifacts alone. |

**Test**: name a non-code decision made in the last 90 days — an eval score that justified a promotion, an override that was granted, a policy exception. Can you locate the record from artifacts alone in under 2 minutes without asking anyone? If no: D4 score is 2 or lower.

---

### Dimension 5 — Policy Encoding `[gate]`

Are behavioral constraints — what a skill can do, what tools it can invoke, what data it can access — expressed in a machine-verifiable form, not just in prose?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Skill scope constraints are expressed in structured manifest fields (skill.json) that gate validation scripts check. Tool permissions are explicit, not inferred. Sensitive-data access constraints are flagged in a machine-readable field. A pre-commit or CI gate enforces policy against the manifest; policy violations block merge. |
| **4 — Good** | Most constraints are in structured form. Some remain as prose in SKILL.md but are cross-referenced from the manifest. Validation scripts exist and run in CI, but coverage is partial. |
| **3 — Adequate** | Constraints are documented in SKILL.md prose. No structured manifest fields for scope. Validation scripts check metadata (name, description length) but not behavioral policy. Policy compliance is human-reviewed, not mechanized. |
| **2 — Poor** | Constraints exist only as prose, and prose is sometimes ambiguous. Validation is ad-hoc and pre-merge review rarely catches policy violations. The same constraint is expressed inconsistently across skills. |
| **1 — Failing** | Behavioral constraints are implicit — inferred from skill behavior or undocumented entirely. There is no manifest, no validation, and no systematic check. The system has no machine-readable statement of what any skill is allowed to do. |

**Test**: for the most sensitive skill in the library (highest tool access, broadest data scope), open its manifest. Can a script determine its authorized tool set, data access scope, and invocation constraints from the manifest alone — without reading SKILL.md prose?

---

### Dimension 6 — Override Authority `[gate]`

When the governed path fails or is too slow, who can override it, by what mechanism, under what conditions, and for how long?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Override authority is documented: named roles, named mechanisms, explicit expiry requirements. Every active override has a record: who granted it, when, why, and when it expires. Expired overrides are automatically flagged or revoked. Override scope is bounded — overrides apply to specific skills or specific invocations, not the entire system. No permanent overrides exist. |
| **4 — Good** | Override authority is documented. Most overrides are recorded. Expiry is expected but not automatically enforced. Override scope is usually bounded. One or two permanent overrides exist with documented rationale. |
| **3 — Adequate** | Override mechanism exists and is understood by practitioners. Records are informal (Slack message, PR comment). Expiry is not tracked. Some overrides have grown permanent without explicit decision to make them so. |
| **2 — Poor** | Overrides are used freely and undocumented. There is no named override authority. "Just bypass the gate for now" is the operational posture. The override surface is larger than anyone can enumerate. |
| **1 — Failing** | No override concept. Agents and practitioners bypass governance at will with no record, no authorization, and no expiry. The governed system and the actual system are irreconcilably diverged. |

**Test**: list all active overrides in the system. If you cannot produce this list from artifacts in under five minutes, the override governance is failing.

---

### Dimension 7 — Human Override of Agent Decisions `[review]`

During an active agent run, can a human interrupt, redirect, or abort a consequential action? Is that capability documented, tested, and actually reachable under failure conditions?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Interrupt/abort paths are named in the harness and per-skill SKILL.md for high-consequence skills. Human override is tested as part of skill validation (not just documented). Interrupt paths remain reachable even when the agent is mid-execution. Agents are designed to surface pending consequential actions before committing, not after. |
| **4 — Good** | Interrupt paths are documented. High-consequence skills surface confirmation gates. Override is reachable in normal operation but may not be tested under failure conditions. |
| **3 — Adequate** | Interrupt paths exist but are not named or documented — practitioners discover them through experience. Confirmation gates exist for some high-consequence operations. Override under failure is untested. |
| **2 — Poor** | No documented interrupt paths. Some skills commit consequential actions without confirmation. Human override requires killing the process — there is no in-flow mechanism. |
| **1 — Failing** | Agents cannot be interrupted without external process termination. Consequential actions are taken without confirmation. The system has no design for human override during execution. |

**Test**: for the highest-consequence skill in the library (the one with the most destructive or irreversible action), trace the human override path. How many steps does it take to stop a running invocation? Is that path reachable from the skill's output surface?

---

## §Anti-patterns

### AP-01 — The Implicit Owner (nobody owns it)

**Symptom**: Skills have no named owner. When something goes wrong, the question "who is responsible for this skill?" produces silence or a list of everyone who ever touched it. **Root cause**: Authorship is tracked (git blame) but ownership is never assigned. The distinction — authorship is historical, ownership is forward-looking — is never made explicit. **Correction**: Add an `owner` field to skill.json. Owner is the party responsible for correctness and updates going forward — may or may not be the original author. Populate it for every skill before the next version bump.

### AP-02 — Self-certifying Evals

**Symptom**: Eval scores are consistently high across the library. The author who wrote the skill also ran the eval. Promotion from draft to stable is fast and uncontested. **Root cause**: The evaluator and author roles are not separated, and no structural mechanism enforces separation. The author has every incentive to score their own work highly and no structural impediment to doing so. **Correction**: Require that the evaluator for a skill's promotion review is not the skill's primary author. Even informal peer review by a second practitioner provides structural separation. For critical skills, require adversarial evaluation (this skill's **critique** mode).

### AP-03 — Override Debt

**Symptom**: The team knows there are "a few" overrides in place but cannot enumerate them. Some overrides were added "temporarily" and have been active for months. **Root cause**: Overrides are added under pressure with no expiry and no tracking mechanism. The override surface grows asymptotically; nobody audits because nobody knows where to look. **Correction**: Maintain an OVERRIDES.md (or equivalent structured file) as a first-class governance artifact. Every override gets an entry: reason, authorizing party, expiry date. Add a quarterly review step. Expired overrides are removed by default, not extended by default.

### AP-04 — Prose-only Policy

**Symptom**: The policy says "skills should not invoke external APIs without user consent." The validation script checks description length and name formatting. The gap between policy and enforcement is permanent and invisible. **Root cause**: Policy is written by people who think in prose; enforcement is written by engineers who think in code. The two are never connected. Policies accumulate in documents; enforcement accumulates in scripts; neither references the other. **Correction**: For every prose policy, add a corresponding machine-verifiable field to the manifest. If it cannot be expressed in a field, it cannot be enforced — and if it cannot be enforced, it is a guideline, not a policy. Name the distinction explicitly.

### AP-05 — Governance Theater

**Symptom**: The process has all the artifacts — CHANGELOG, eval records, owner field, override log — but the artifacts are templated and never substantively filled. CHANGELOGs say "updated." Eval records say "passed review." Owner fields say "team." **Root cause**: Governance artifacts were added to satisfy a checklist, not to serve accountability. The people filling them out know they are performing compliance rather than practicing governance. **Correction**: Add at least one question to each artifact that cannot be answered with a template: "What failure mode does this rule prevent?" in CHANGELOG. "What would this skill need to do differently to score one point higher?" in eval records. Blank answers are a governance finding, not a pass.

### AP-06 — Role Collapse Under Pressure

**Symptom**: During incidents or deadlines, role separation is the first thing dropped. The author self-approves a hot fix. The evaluator skips the rubric and promotes based on "feels good." Post-incident, nobody restores the separation. **Root cause**: Role separation is treated as a process overhead rather than a safety mechanism. When overhead competes with urgency, overhead loses. The structural consequences of collapse are never made visible. **Correction**: Document the incident log entry every time role separation is bypassed. Even one sentence: "Author self-approved due to incident; post-incident review required." The accumulation of these entries makes the collapse pattern visible before it becomes chronic. Post-incident reviews explicitly ask: was role separation maintained? If not, what is the retroactive review?

---

## §Hard Tests

1. **The ownership test**: for any skill in the library, open skill.json. Is there a named owner? Is that owner a specific person or role — not "team" or "anyone"? If you emailed that person right now asking "is this skill still correct?", would they know which skill you meant?

2. **The eval-separation test**: for any skill marked stable, who ran the promotion eval? Was that person also the primary author? If the answer is "same person," the eval governance score is 2 or lower for that skill.

3. **The override enumeration test**: list every active override in the system from artifacts alone. If this takes more than five minutes or requires interviewing anyone, override governance is failing.

4. **The policy-enforcement gap test**: take any prose policy statement from AGENTS.md or a SKILL.md. Write a one-line check that mechanically verifies compliance. If you cannot, the policy is not enforced and should be labeled as a guideline.

5. **The post-incident reconstruction test**: a skill produced an unintended action three weeks ago. From artifacts alone — no conversation, no interviews — determine: which version was running, who last authorized a change, and whether any override was active. The number of gaps is your audit score.

6. **The role-collapse test**: look at the last three skill promotions (draft → stable). In how many did the same person author the skill and run the eval? The answer should be zero.

7. **The override expiry test**: look at the oldest active override in the system. When was it created? Is it still justified? Does an expiry exist? If "temporary" overrides are older than 90 days, override governance is failing.

8. **The human override test**: for the highest-consequence skill in the library, time how long it takes to interrupt a running invocation from the moment you decide to stop it. If the answer is "kill the process," document the interrupt-path gap as a governance finding.
