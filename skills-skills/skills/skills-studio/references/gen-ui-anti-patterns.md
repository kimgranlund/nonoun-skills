---
date: 2026-05-19
source: ref-gen-ui-systems/references/anti-patterns.md (copied into skills-studio for self-containment)
---

# Anti-Pattern Catalogue

## 10 Named Failure Modes in Generative UI

Use this catalogue for critique, validation, and for catching failure modes before they are built. Each entry names the pattern, describes its symptoms, identifies the root cause (which rung was skipped), and provides a before/after correction.

---

## Quick Reference

| ID | Name | Skipped rung | Severity | Primary symptom |
| --- | --- | --- | --- | --- |
| AP-01 | Premature Rendering | 0–5 | Critical | Output begins with component vocabulary |
| AP-02 | Generic Dashboard Syndrome | 5 (Decision) | Critical | Metrics shown with no actions |
| AP-03 | Component-First Thinking | 1–5 | High | Reasoning starts with component names |
| AP-04 | Unbound UI | 14 (Binding) | High | Components have no data source |
| AP-05 | Actionless Interface | 15 (Interaction) | High | Operational surface with no actions |
| AP-06 | Missing Feedback States | 17 (Feedback) | High | No loading, empty, or error states |
| AP-07 | Role Collapse | 3 (Role) | High | One interface for incompatible roles |
| AP-08 | Metric Without Decision | 5 (Decision) | Medium | KPI card with empty decisionIds |
| AP-09 | Surface Without Task | 10 (Surface) | Medium | Surface with empty taskIds |
| AP-10 | State Without Owner | 16 (State) | Medium | State entries with no owner or lifetime |

---

## AP-01: Premature Rendering

**Symptoms:** Output begins with component vocabulary ("header," "card," "table," "sidebar"). No intent, role, task, or decision is stated. The interface looks correct but is structurally wrong.

**Root cause:** Bypassed the reasoning ladder entirely. Started at the output layer (Rung 13+) instead of the foundation layer (Rungs 0–5).

**Before:**

```txt
Prompt: Build a dashboard for sales leads.
Output: Dashboard → KPI Cards (Total, Converted, Revenue) → Bar Chart
        (Leads by Month) → Table (All Leads)
```

**After:**

```txt
Prompt: Build a dashboard for sales leads.

Ladder execution:
1. Intent: Help a sales team monitor and act on incoming leads.
2. Domain: Lead, Owner, Source, Activity, SLA.
3. Roles: Sales Manager (monitoring + acting), SDR (acting).
4. Tasks: Triage leads, assign leads, inspect SLA risk.
5. Decisions: Which leads need action now? Which are at SLA risk?
6. Posture: Monitoring primary, acting secondary. Realtime.
...
Output: Priority lead queue, SLA risk panel, rep workload — with
        bindings, actions, state, and feedback for each.
```

**Correction:** No component may be emitted before Rungs 0–5 are resolved.

---

## AP-02: Generic Dashboard Syndrome

**Symptoms:** KPI cards showing totals with no drill-down. Charts displaying trends with no filter or action. A table listing all records with no prioritization or action affordance. No visible path from interface to user's next step.

**Root cause:** Decision layer (Rung 5) was skipped. Metrics were mapped to components without establishing what decisions they support.

**The specific error:** Conflating metric with decision. "Average response time is 43 minutes" is a metric. "Which leads are at risk of missing the SLA?" is a decision. The decision requires signals, thresholds, and a consequent action. A dashboard showing the metric without the decision is observational, not operational.

**Before:**

```yaml
components:
  - type: kpi_card
    props: { label: Total Leads, value: "{{total_leads}}" }
  - type: kpi_card
    props: { label: Conversion Rate, value: "{{conversion_rate}}" }
  - type: data_table
    props: { label: All Leads, columns: [name, email, status, date] }
```

**After:**

```yaml
components:
  - type: kpi_card
    props:
      label: At SLA Risk
      value: "{{sla_risk_count}}"
      alertThreshold: 1
    actionIds: [open_sla_filtered_queue]
    decisionIds: [which_leads_are_at_sla_risk]

  - type: data_table
    props:
      label: Priority Leads
      density: compact
      defaultSort: { field: priorityScore, direction: desc }
      columns: [name, score, sla_deadline, owner, status, age]
    actionIds: [assign_lead, open_lead_detail, mark_qualified]
    decisionIds: [which_leads_need_action_now]
```

**Correction:** For every metric, ask: what decision does this support? What action follows? If no action follows, the metric may not belong in an operational interface.

---

## AP-03: Component-First Thinking

**Symptoms:** The reasoning document begins: "The page will have a sidebar, a filter bar, cards, and a table." Components are named before tasks are identified.

**Root cause:** The system started from component library vocabulary rather than reasoning vocabulary. Component libraries are libraries of answers; they do not contain the questions.

**Before (wrong reasoning process):**

```txt
1. What kind of page is this? → Dashboard
2. What components go in a dashboard? → Cards, charts, tables, filter bar
3. What data do the cards show? → Totals and rates
```

**After (correct reasoning process):**

```txt
1. What is the user trying to accomplish? → Triage incoming leads
2. What decisions must they make? → Which leads need action? Which are at SLA risk?
3. What signals do they need? → Priority score, SLA deadline, owner, status, age
4. What actions must be available? → Assign, qualify, reject, open detail
5. What component types serve these signals and actions? → Priority table, KPI cards, action menu
```

**Correction:** Replace "what components do we need?" with "what tasks must be supported?" Components are the output of reasoning, not the input.

---

## AP-04: Unbound UI

**Symptoms:** Component specs list props but no `bindingId`. Components display placeholder values or hardcoded content. No refresh policy.

**Root cause:** Data binding layer (Rung 14) was skipped. Components were generated as visual artifacts without connecting them to the domain model.

**Correction:** Apply the data binding layer to every data-driven component. A component without a `bindingId` is an incomplete specification.

---

## AP-05: Actionless Interface

**Symptoms:** A queue, list, or triage surface with no buttons or affordances. Decisions are supported by signals but no actions follow. The user can identify what needs to be done but cannot do anything.

**Root cause:** Interaction layer (Rung 15) was skipped. Decision layer partially completed (signals specified) but `possibleActions` is empty.

**Correction:** Every decision must have non-empty `possibleActions` before the spec is complete.

---

## AP-06: Missing Feedback States

**Symptoms:** Component specs contain no `feedbackModel` entries. No specification of what happens while data loads, when results are empty, or when the data source is unavailable.

**Root cause:** Feedback layer (Rung 17) was skipped or treated as a detail to handle later.

**The three required states:** Loading (request pending), Empty (0 results), Error (request failed).

**Correction:** Apply the completeness rule: every data-driven component requires loading, empty, and error states. Not optional.

---

## AP-07: Role Collapse

**Symptoms:** Single navigation serves all user types. Some users see metrics they cannot act on. Others see controls they cannot use. Permission errors during normal workflows.

**Root cause:** Role layer (Rung 3) was underspecified. Multiple roles identified but `uiDifferentiators` was empty.

**Correction:** Populate `uiDifferentiators` for each role. Carry those differences through navigation, surfaces, sections, and component permission checks.

---

## AP-08: Metric Without Decision

**Symptoms:** KPI cards showing totals and averages. No decision references these metrics. No action follows.

**Correction:** For every metric component, verify at least one `DecisionModel` references it as a required signal.

---

## AP-09: Surface Without Task

**Symptoms:** A page, panel, or modal exists with empty `taskIds`. No clear reason for the user to navigate to or open this surface.

**Correction:** Every surface must have at least one `taskId`. If a surface cannot be associated with a task, remove it.

---

## AP-10: State Without Owner

**Symptoms:** Component behavior changes based on values that are never explicitly modeled. Derived values stored as local state and become stale.

**Root cause:** State layer (Rung 16) was skipped or reduced to listing variable names without specifying ownership or reset conditions.

**Correction:** Categorize every state entry by owner. Apply derived state rule without exception. Every optimistic entry must have a failure rollback.

---

## Wireframing Anti-Pattern Cross-Reference

The 10 anti-patterns above cover the full ladder. For the SPECIFIC failure modes of the wireframing tier, see `references/rubrics/agents-ux-wireframing-ascii.md` in this skill. Its 10 anti-patterns are the wireframe-artifact-specific analogs of the ladder-spanning failure modes catalogued here.
