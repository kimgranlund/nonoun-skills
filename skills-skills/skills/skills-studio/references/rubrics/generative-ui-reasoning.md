---
date: 2026-05-23
status: draft
version: "0.1.0"
---

# Generative UI Reasoning — Best Practices Rubric

**A generative UI plan is a decision surface specification, not a component list.** Generating UI without first establishing intent, domain, role, task, and decision produces outputs that are visually plausible but operationally useless — interfaces that look correct but do not serve any user's actual work.

The central failure mode: **premature rendering** — emitting components before the system has resolved what the user is trying to accomplish, what world the interface represents, and what decisions the interface must support.

This rubric evaluates whether an agentic UI generation system follows top-down reasoning from intent to output, maintains full traceability from task to component to binding to feedback state, and produces a plan that could be handed to an engineer and executed without guesswork.

**Companion docs:**

- `references/gen-ui-ladder/00-index.md` — source knowledge base for the reasoning ladder
- `references/gen-ui-ladder/30-anti-patterns.md` — named failure mode catalogue with before/after examples
- `references/gen-ui-ladder/42-eval-criteria.md` — tier scoring rubric and automated eval signals
- `agentic-coding.md` (this folder) — PEV loop, output contracts, and autonomy boundaries
- `prompt-control-modes.md` (this folder) — control mode selection for UI generation tasks
- `evaluation-workflows.md` (this folder) — how to test a generative UI system adversarially

---

## §The Problem

Generative UI systems fail in predictable ways when reasoning layers are skipped:

1. **Premature rendering** — the agent pattern-matches from prompt keywords to familiar component templates ("sales dashboard" → metric cards, chart, table) before establishing what the user is trying to do, what decisions they need to make, or what actions must be available. The output looks like a dashboard. It does not work like one.

2. **Generic Dashboard Syndrome** — metrics are displayed without supporting the decisions or actions those metrics imply. A KPI card showing average response time answers "what is true?" but not "which leads are at SLA risk right now and what do I do about it?" The interface is observational, not operational.

3. **Component-first thinking** — the agent reasons in component vocabulary ("what kind of components go in a dashboard?") rather than task vocabulary ("what does this user need to accomplish?"). Component libraries are libraries of answers; they do not contain the questions.

4. **Unbound specifications** — components are specified as visual artifacts with no data source, no query, no field map, and no refresh policy. An unbound component is a mockup. It cannot be made operational without a binding that the spec never established.

5. **Actionless interfaces** — an operational interface — one where the user's primary task is to act — contains no actions. The user can see what needs attention but cannot do anything about it. This is the decision layer left incomplete: decisions were specified but `possibleActions` was left empty.

6. **Role collapse** — a single interface is designed for multiple roles with incompatible goals, permissions, or primary tasks. Role differentiation defined in the role layer does not propagate to navigation, surface access, or component visibility. One interface serves all roles; it serves none well.

7. **Missing feedback states** — data-driven components are specified with no loading state, empty state, or error state. These are not UI polish — they are required operational model specifications. A component without a feedback model will flash, break, or go silent in real-world conditions.

---

## §First Principles

### 1. A UI is a decision surface over a domain, not a component tree

UI generation must begin with why the UI exists (intent), what world it represents (domain), who uses it (role), what they need to accomplish (task), and what they need to determine (decision). Only after these are resolved can the system determine which components are justified. Components are the output of reasoning, not the input.

### 2. Every component must be justified by a task or decision

A component is valid only if it can be traced to at least one task or decision in the upstream reasoning, has a data binding (if data-driven), and uses a component type appropriate to the task type. A component that cannot be traced to a task or decision has no justification and is a candidate for removal.

### 3. Validate upward before proceeding downward

When a system enters the reasoning ladder at any point below intent — from a PRD, a schema, a mockup, or a component request — it must derive all upstream layers before specifying downstream layers. If a component request contradicts the upstream reasoning, the component must change, not the reasoning. Upstream validation is not optional.

### 4. Metrics are inputs to decisions, not components

A metric displayed without a decision that references it is an observation, not operational design. Every metric in the plan must trace to a decision that asks: what should the user determine from this metric, what signals do they need to determine it, and what actions follow once they've decided? Metrics mapped directly to components skip the decision layer.

### 5. Role collapse is a first-class error, not a rendering detail

Permissions, goals, and primary tasks defined in the role layer must propagate through navigation visibility, surface access, section visibility, and component-level controls. Role differentiation that does not carry through to the interface has no effect. Different roles over the same domain often require different interfaces.

### 6. Feedback states are part of the operational model

Loading, empty, error, stale, and permission states are not UI polish to be added later. They are required specifications. Every data-driven component must define at minimum: a loading state, an empty state, and an error state. A plan without feedback states specifies behavior only under ideal conditions.

### 7. An unbound component is a mockup

Data binding is not a detail. It defines what the component actually shows, how frequently it updates, and what states must be designed. A component without a `bindingId` and an explicit `fieldMap` is a visual placeholder, not a product specification.

### 8. The output contract enables handoff, not documentation

The plan's `ValidationResult` — with score, tier breakdown, issues, and checks — is not a summary of what was done. It is the evidence that the plan is complete enough to execute. A plan without a `ValidationResult` is a draft. A plan with a passing `ValidationResult` that cannot be handed to an engineer and executed directly has failed its output contract.

---

## §Reasoning Tiers

The 19-rung ladder groups into five tiers that can be validated independently. The rubric dimensions below map to these tiers.

| Tier                  | Rungs | Purpose                                 |
| --------------------- | ----- | --------------------------------------- |
| **Foundation**        | 0–1   | Input context, intent, success criteria |
| **Domain Reasoning**  | 2–5   | Domain model, roles, tasks, decisions   |
| **Structure**         | 6–9   | Posture, IA, shell, navigation          |
| **Surface Design**    | 10–13 | Surfaces, views, sections, components   |
| **Operational Model** | 14–17 | Bindings, actions, state, feedback      |
| **Output**            | 18–19 | Render plan, validation                 |

The failure modes in §The Problem each correspond to a skipped or short-circuited tier. The rubric dimensions below make these failures detectable and scoreable.

---

## §The Rubric

### Dimension 1 [gate] — Premature rendering avoidance

Does the plan establish intent, domain, task, and decision before any component is named?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | No component vocabulary (page, card, table, sidebar, modal, chart, widget) appears in intent, domain, task, or decision sections. All components appear at rung 13 or later. Every component can be traced to an upstream task or decision. |
| **4 — Good** | One or two incidental component references in upper tiers, easily removed without affecting the reasoning. Upstream reasoning is complete and independent of component vocabulary. |
| **3 — Adequate** | Some component vocabulary in task or decision sections, but the reasoning substance is present. The components mentioned could be derived from the upstream reasoning without changing it. |
| **2 — Poor** | Component selection precedes task and decision reasoning. The system names a table before it knows what decision the table supports. |
| **1 — Failing** | The plan begins with component vocabulary. Intent, domain, task, and decision are absent or post-hoc justifications for components already selected. AP-01 (Premature Rendering) or AP-03 (Component-First Thinking) is present. |

**Test**: search the intent, domain, task, and decision sections for: page, card, table, sidebar, nav, chart, modal, drawer, button, form, widget, dashboard. Each match is a premature rendering signal. Score 5 requires zero matches.

---

### Dimension 2 [gate] — Decision layer completeness

Does every critical decision support a user action, not just a user observation?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every critical decision has: a specific question, non-empty `requiredSignals` with `displayHints`, non-empty `possibleActions`, and an urgency rating. Every metric displayed in the plan is referenced by at least one decision as a required signal. |
| **4 — Good** | All critical decisions have actions. One or two secondary metrics lack decision references but are clearly informational. |
| **3 — Adequate** | Most decisions have actions. Some secondary decisions have empty `possibleActions`. No critical decision is missing an action. |
| **2 — Poor** | Several decisions have empty `possibleActions`. The user can identify the problem but cannot act. AP-05 (Actionless Interface) is present. |
| **1 — Failing** | Decision layer is absent or empty `possibleActions` throughout. Metrics are mapped directly to components without passing through a decision. AP-02 (Generic Dashboard Syndrome) is present. |

**Test**: for each metric or KPI in the plan, trace backward to a decision that references it as a required signal. For each decision, verify `possibleActions` is non-empty. Count decisions with empty `possibleActions`. Any critical decision failing this check is Score 2 or lower.

---

### Dimension 3 [gate] — Component traceability

Can every component be fully traced from task or decision through to data binding?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every component has non-empty `taskIds` or `decisionIds`. Every data-driven component has a `bindingId` with an explicit `fieldMap`. A complete traceability matrix (task → decision → signal → component → binding) can be built with no gaps. |
| **4 — Good** | All critical components are traced. One or two non-critical components have thin justification but can be removed without breaking the operational model. |
| **3 — Adequate** | Most components are traced. Some have `bindingId` but no `fieldMap` (implicit field matching). The traceability matrix has gaps but the plan is largely executable. |
| **2 — Poor** | Several components have empty `taskIds` and `decisionIds`. Bindings are present but `fieldMaps` are absent. The traceability matrix cannot be built without inference. |
| **1 — Failing** | Components are listed with no task or decision references. Bindings are absent. AP-04 (Unbound UI) is present. The plan is a mockup. |

**Test**: build the traceability matrix using the template in `references/gen-ui-ladder/42-eval-criteria.md`. A gap in any `taskId`/`decisionId` column is a warning. A gap in any `bindingId` column for a data-driven component is an error.

---

### Dimension 4 [gate] — Operational model completeness

Are the plan's actions and data-driven components specified to the level required for implementation?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Every action has `permission` and `errorPath`. Every data-driven component has loading, empty, and error feedback states with specific (non-generic) messages and `suggestedActions`. Derived state is not stored. Optimistic updates have rollback paths. |
| **4 — Good** | All actions have permissions and error paths. Feedback states are present but some empty-state messages are generic. Derived state rule is followed. |
| **3 — Adequate** | Most actions have permissions. Minor actions may lack error paths. Feedback states exist for primary components but not all secondary ones. |
| **2 — Poor** | Actions lack permissions or error paths. Feedback states are present in some components but absent in others. |
| **1 — Failing** | Actions have no permissions or error paths. Feedback states are absent. AP-06 (Missing Feedback States) is present. The plan cannot be executed without significant specification work. |

**Test**: list every `ActionSpec`; count those missing `permission` (error) and those missing `errorPath` (error). List every data-driven component; count those missing a loading, empty, or error state (warning each). The automated eval signals in `references/gen-ui-ladder/42-eval-criteria.md §Operational Model` define the exact checks.

---

### Dimension 5 [review] — Role differentiation propagation

Does the role layer's differentiation carry through to the actual interface?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | Each role's `uiDifferentiators` are non-empty and carry through to: navigation item visibility (role-gated items), surface access control, section-level visibility, and component-level permission checks. Role collapse check passes: no two roles with incompatible goals see identical navigation and surfaces. |
| **4 — Good** | Role differentiation carries through to navigation and surface access. Component-level gating may be incomplete for edge cases, but primary role differences are enforced. |
| **3 — Adequate** | Some role differentiation carries through. Navigation is partially role-gated. The plan does not fully prevent a role from seeing surfaces they cannot use. |
| **2 — Poor** | Multiple roles are defined with `uiDifferentiators`, but the differentiation does not appear in navigation, surfaces, or component specs. The same interface is produced for all roles. |
| **1 — Failing** | `uiDifferentiators` are empty for multiple roles. AP-07 (Role Collapse) is present. |

**Test**: extract navigation items visible to each role. If all roles with incompatible goals see identical navigation, role collapse is present. For each `uiDifferentiator` entry, find where in the surface or component spec it is enforced. Missing enforcement for a stated differentiator is a gap.

---

### Dimension 6 [review] — Entry point handling

When the plan enters the ladder mid-rung, does it derive upstream layers correctly before proceeding?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | The plan correctly identifies its entry rung. All upstream layers are derived before downstream layers are specified. Inferred claims are marked as inferred, not stated as known. Missing upstream items appear in `InputContext.missing` with explicit assumptions. If input components contradict derived reasoning, the components are adjusted, not the reasoning. |
| **4 — Good** | Entry point identified. Upstream derivation is mostly complete. One or two inferred claims stated without marking, but they are low-risk. |
| **3 — Adequate** | Upstream layers are present but thin. Some inferred claims treated as known. The plan proceeds without fully validating the upstream reasoning. |
| **2 — Poor** | Entry point not identified. Upstream layers derived partially or not at all. Inferred claims stated as facts. The plan jumps from the entry rung to component specification. |
| **1 — Failing** | Mid-ladder entry treated as top-level. No upward validation. Component requests accepted at face value without deriving intent and task. |

**Test**: identify the `InputContext.entryPoint`. List all claims in the intent, domain, and role sections. For each: is it marked `known` (explicitly stated in the input) or `inferred`? If the input entered mid-ladder and upstream claims are marked `known` rather than `inferred`, the plan has treated derived reasoning as given fact.

---

### Dimension 7 [review] — Output contract quality

Does the plan's `ValidationResult` make it reviewable, executable, and handoff-safe?

| Score | Evidence |
| --- | --- |
| **5 — Excellent** | `ValidationResult` is present with: `passed` boolean, numeric score (0–100), tier breakdown, `issues[]` with severity and suggested fixes, and `checks[]` array covering all standard checks. Score ≥ 75 overall. No individual tier below 60% of its max. The result can be handed to an engineer and executed without reading the full plan. |
| **4 — Good** | `ValidationResult` present with score and issues. One or two standard checks missing from `checks[]`. Score ≥ 75. |
| **3 — Adequate** | `ValidationResult` present but shallow: a passed boolean and prose summary, not a structured issues list. Score may be present but not broken down by tier. |
| **2 — Poor** | `ValidationResult` is a prose paragraph. Issues are mentioned but not categorized by severity or tier. Not machine-readable. |
| **1 — Failing** | No `ValidationResult`. The plan declares completion when components are specified. There is no verification step. |

**Test**: can a different agent, given only the `ValidationResult`, determine: what was verified, which tier had the highest-risk issues, what the most critical open issue is, and what the next required step is? If not, the output contract is insufficient.

---

## §Anti-patterns

### AP-01 — Premature rendering

**Symptom**: the plan begins with component vocabulary; reasoning about intent, task, and decision is absent or follows component selection rather than preceding it. **Root cause**: the system pattern-matched from prompt keywords to familiar component templates without reasoning through the ladder. **Correction**: enforce the reasoning ladder as a pre-condition for component generation. See `references/gen-ui-ladder/30-anti-patterns.md` AP-01.

### AP-02 — Generic Dashboard Syndrome

**Symptom**: metrics are displayed with no decision layer; the interface is observational, not operational; there is no path from metric to decision to action. **Root cause**: decision layer (rung 5) skipped; metrics mapped directly to components. **Correction**: for every metric in the plan, derive the decision it supports before specifying the component. See `references/gen-ui-ladder/30-anti-patterns.md` AP-02.

### AP-03 — Metric without decision

**Symptom**: a KPI card or chart has empty `decisionIds`; the metric answers "what is true?" but not "what do I do?" **Root cause**: decision layer underspecified; metrics derived from the domain model and placed in components without establishing a decision that references them. **Correction**: every metric must trace to at least one decision as a required signal. See `references/gen-ui-ladder/30-anti-patterns.md` AP-08.

### AP-04 — Role differentiation without propagation

**Symptom**: multiple roles defined with goals and permissions; identical navigation and surfaces produced for all roles. **Root cause**: the role layer produced `uiDifferentiators` that were not carried forward to navigation visibility, surface access, or component-level permission checks. **Correction**: trace each `uiDifferentiator` entry to its enforcement point in navigation, surface, or component specs. See `references/gen-ui-ladder/30-anti-patterns.md` AP-07.

### AP-05 — Shallow specification theater

**Symptom**: the plan has all required sections but fields are thin — one sentence, no specifics, generic messages. Passes structural checks but fails shallowness detection. **Root cause**: the system satisfied the presence check without satisfying the content check. `successCriteria` is aspirational not testable. `requiredInformation` lists entity names not field+purpose pairs. Empty states say "No data available." **Correction**: apply the shallowness tests from `references/gen-ui-ladder/42-eval-criteria.md` §Distinguishing Shallow-But-Correct from Deep-But-Wrong.

### AP-06 — False validation pass

**Symptom**: `ValidationResult.passed = true` with a high score, but the plan is fundamentally wrong — intent drift, domain without use, or component-decision mismatch. **Root cause**: validation checked structural completeness but not reasoning correctness; all fields present, but the intent model does not match the actual use case. **Correction**: build the traceability matrix and run it end-to-end. A mismatch at any join (task → decision → signal → component column) is a structural error that completeness scores miss. See `references/gen-ui-ladder/42-eval-criteria.md` §False positive: high score, wrong plan.

---

## §Hard Tests

1. **The vocabulary test**: search the intent, domain, task, and decision sections for component names (page, card, table, sidebar, modal, chart, button, form, widget). Count matches. Score 5 requires zero matches in these sections. Each match is evidence of premature rendering.

2. **The metric trace test**: pick any metric displayed in the plan. Trace backward: is it referenced as a `requiredSignal` in a `DecisionModel`? Does that decision have `possibleActions`? Does an `ActionSpec` exist for each listed action? If any step in the chain is missing, the metric is not operational.

3. **The traceability matrix test**: build the full matrix using the template in `references/gen-ui-ladder/42-eval-criteria.md`. Count gaps. A missing `taskId`/`decisionId` for any component is a warning. A missing `bindingId` for any data-driven component is an error.

4. **The role isolation test**: extract the navigation and surfaces visible to each role. For a system with multiple roles that have incompatible goals: are the interfaces functionally distinct? If two roles with incompatible permissions see identical navigation, role collapse is confirmed.

5. **The entry point test**: identify the `InputContext.entryPoint`. For each claim in the intent, domain, and role sections: is it `known` (explicitly stated in the input) or `inferred`? If the plan entered mid-ladder and upstream claims are marked `known` rather than `inferred`, it has treated derived reasoning as given fact.

6. **The dead component test**: pick any component in the plan. Remove it from the spec. Does the traceability matrix still hold? Do the decision's `possibleActions` still have implementations? If removing the component breaks nothing in the task and decision layers, the component was unjustified.

7. **The feedback completeness test**: list all data-driven components (any with a `bindingId`). For each: are loading, empty, and error states present? Are empty-state messages specific to the surface context, or generic ("No data available")? Score 5 requires all three states and non-generic messages for every data-driven component.

8. **The continuation test**: hand only the `ValidationResult` to a new agent. Can it identify: what was verified, which tier had the most critical issues, what the most severe open issue is, and what the next required step is? If the new agent cannot answer these questions from the `ValidationResult` alone, the output contract is insufficient.

---

## §Known coverage gaps

Two critics on the eval panel are not fully served by this rubric's current dimensions. These gaps are labeled as `[hypothesis]` in the manifest and should be addressed as real applications accumulate:

**Charity Majors (post-deploy observability):** This rubric evaluates the plan that goes in, not what comes out in production. It has no dimension covering whether the generated UI plan specifies action telemetry hooks, error boundary instrumentation, or rollback triggers tied to production error rates. A generated plan that passes all seven dimensions here may still produce a UI that ships invisibly.

**Simon Willison (trust boundaries):** The rubric covers action permission scoping (D4) but does not address: whether sensitive-field access generates an audit event, whether component generation from untrusted schemas can embed malicious component requests, or whether the plan's generated actions are scoped to minimum necessary privilege in the application's permission model. Both gaps require extending the gen-ui-ladder source material before they can be rubric dimensions.
