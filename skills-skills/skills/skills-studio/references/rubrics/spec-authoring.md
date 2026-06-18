---
title: SPEC Authoring (Specification Document for agentic coding workflows)
key_question: Does the SPEC define an execution contract bounded enough for a coding agent to implement, verify, and stop safely — or does it leave ambiguity that the agent fills with its own assumptions, producing over-edits, under-implementations, or unsafe refactors?
layer: agent-coding
primary_critic: boris-cherny  # PEV loop / verifiability lens — SPECs are the V's input contract
companion_rubrics:
  - prd-authoring                           # Upstream alignment doc that this rubric's input flows from
  - agents-ux-wireframing-ascii             # When SPEC involves UI, wireframing is upstream of UI/Component Contracts section
  - composite-css-composition-discipline    # When SPEC involves composite UI, this rubric covers Rungs 12-13
  - context-engineering                     # SPECs ARE structured context objects in agentic harnesses
  - harness-design                          # SPEC consumed by the harness; harness quality affects whether the SPEC is honored
version: 0.1.0
status: empirically-derived
source: "/Users/kimba/Downloads/prd-vs-spec-agentic-coding-workflows.md (sections 3, 7, 8, 11, 13.2)"
---

# SPEC Authoring (for agentic coding workflows)

## What this rubric measures

When an org produces a Specification Document for downstream agentic coding execution, does the SPEC **convert product intent into a structured, typed, implementation-ready contract** the agent can read, plan against, edit, test, and stop safely from — or does it leave the ambiguity that produces over-edits, under-implementations, scope creep, and silent failures?

The failure mode this rubric defends against: **a SPEC that reads like a PRD with technical details appended**, leaving the coding agent to fill behavioral, structural, and verification gaps with its own (often wrong) assumptions.

## Why this is its own rubric

Distinct from `prd-authoring` (which measures human-team alignment) and from `harness-design` (which measures the agent's _environment_). A SPEC optimizes for **agent task execution, behavioral precision, testability, dependency control, repeatable implementation**. Its readers are coding agents + orchestrator agents + reviewer agents + CI + human reviewers — operating through constrained context windows, tool calls, file edits, and local reasoning loops.

The PRD answers "what should exist, for whom, and why?" The SPEC answers "what exactly should change, where, under what constraints, and how will we know it is correct?" This rubric scores the second.

In an agentic harness, the SPEC is **part of the operational substrate** — an intentional context object, not just a prose document. The rubric measures whether the document is designed for that role.

## Pipeline this rubric encodes

```
PRD (see prd-authoring rubric)
  ↓
  Decompose intent → behaviors → contracts → tasks
  ↓
  SPEC authored (this rubric)
  ↓
  Agent task plan → File edits → Tests → Acceptance check → Stop or escalate
  ↓
  Review → Merge
```

Without a strong SPEC, every step from "task plan" through "stop or escalate" inherits ambiguity. The agent fills gaps with priors; priors are often wrong; over-edit / under-implement / opportunistic-refactor follows.

## 10 scoring dimensions

| # | Dimension | Type | Question |
| --- | --- | --- | --- |
| D1 | Scope / Non-Scope explicit | gate | Does the SPEC name what the agent MAY change AND what it MUST NOT touch? Both sections non-trivial. |
| D2 | Behavioral precision | gate | For each user flow / feature, are required states enumerated (loading / empty / error / success / disabled / permission / edge)? |
| D3 | Typed data contracts | gate | Every data field declared with type. Enums enumerate values. Validation rules stated. Persistence behavior explicit. |
| D4 | API / Service contracts | gate | Every endpoint / method named with request shape, response shape, error shape, permission model. |
| D5 | UI / Component contracts | gate | If UI is in scope: components named with props / attributes / states / slots / variants / accessibility requirements / responsive behavior. |
| D6 | File / Module map present | gate | SPEC identifies likely files / directories / packages the agent will inspect or modify. Specific paths, not categories. |
| D7 | Acceptance criteria mapped | gate | Every requirement maps to at least one observable, verifiable check (test, manual verification step, or CI gate). |
| D8 | Source-PRD link | review | SPEC links back to (or summarizes) the PRD / product intent it implements. Agent has access to the why, not just the what. |
| D9 | Stop-and-escalate conditions | review | SPEC names conditions where the agent must halt and ask for review rather than proceeding (missing data, ambiguous case, scope edge). |
| D10 | Conservative-edit framing | review | SPEC explicitly tells the agent NOT to refactor adjacent unrelated code, NOT to opportunistically "improve" things outside scope. |

**Gate dimensions** (D1–D7) — mechanically scoreable. A reviewer (or an audit script) can verify pass/fail by section-presence + content-checks.

**Review dimensions** (D8–D10) — require judgment about completeness + safety.

## 8 named anti-patterns

| ID | Name | What it looks like |
| --- | --- | --- |
| AP-SPEC-01 | **PRD-copy-paste-with-tech-bottom** | SPEC is the PRD body with an "Implementation Notes" section appended. No decomposition into behaviors → contracts → tasks. |
| AP-SPEC-02 | **Missing-file-boundaries** | "Scope" describes capabilities; no file/module/directory list. Agent guesses where to look. |
| AP-SPEC-03 | **Untyped-data-fields** | Data described in prose ("the lead has a status, a source, an owner, a priority") without types, enums, validation. Agent invents shapes. |
| AP-SPEC-04 | **Missing-states** | UI requirements without loading / empty / error / permission states. Agent ships happy-path only; production surfaces broken edge cases. |
| AP-SPEC-05 | **Acceptance-criteria-absent** | Requirements stated; no observable verification gates. Agent can't tell when the work is done. |
| AP-SPEC-06 | **License-to-clean-up** | SPEC includes language like "while you're in there, also fix..." or "feel free to refactor." Opens unbounded edit scope. |
| AP-SPEC-07 | **Test-expectation-omitted** | No test plan, no manual verification steps, no CI gates. Acceptance criteria exist but aren't mechanically checkable. |
| AP-SPEC-08 | **No-escalation-criteria** | SPEC doesn't say when the agent should stop and ask for review. Agent guesses; guesses produce out-of-scope edits or worse, fabrications. |

## 7 hard tests

| # | Test | Verifies |
| --- | --- | --- |
| H1 | **Every requirement has acceptance criterion** | Walk the requirements list; each must map to at least one named verification (test name, command, observable check). |
| H2 | **Every data field has a type** | Walk the data contracts; no field is "the name (string-ish)" or "a config object with various properties." |
| H3 | **Every UI region has full state coverage** | For UI-in-scope SPECs: loading / empty / error / success states enumerated per region. Permission states if relevant. |
| H4 | **Scope + Non-Scope both substantive** | Both sections present + non-trivial. Non-Scope "we won't redo authentication" beats "we won't rewrite the codebase." |
| H5 | **At least one escalation criterion** | SPEC names at least one "stop and ask" trigger (missing data, ambiguous case, scope edge, permission gap, schema mismatch). |
| H6 | **File/Module map is specific** | Paths, not categories. "packages/web-modules/billing/invoice-history/invoice-history.class.js" beats "the billing module." |
| H7 | **Source PRD linked or summarized** | The SPEC connects back to product intent — either via direct PRD link or a 1-paragraph "Source Intent" summary. |

## 7-phase operating procedure

When authoring a SPEC from a PRD:

1. **Extract product intent** → from the PRD, identify problem / goal / user outcome / non-goals. Reproduce as a 1-paragraph "Source Intent" section.
2. **Convert goals into behaviors** → translate product requirements into specific states, flows, conditions, and rules. Per requirement, enumerate the edge cases.
3. **Map behaviors to system surfaces** → identify components / APIs / data models / routes / services / jobs / permissions / integrations that must change.
4. **Define contracts** → make implicit structures explicit. Typed data fields. Request/response payloads. Events. State machines. Validation rules. Component APIs (props/slots/states).
5. **Set boundaries** → enumerate what the agent may modify (Scope), what must remain untouched (Non-Scope), what requires escalation (Stop-and-Ask conditions).
6. **Decompose tasks** → break work into units that can be implemented, reviewed, tested, and merged independently. Each task has its own acceptance criteria.
7. **Define verification** → convert each requirement into acceptance criteria + test plan + review checklist. Mechanical wherever possible.

## Recommended sections (per source doc §3.2 + §11)

| Section | Purpose |
| --- | --- |
| Objective | Defines the implementation outcome in one paragraph |
| Source PRD / Intent Link | Connects the work back to human product intent |
| Scope | Defines what the agent may change |
| Non-Scope | Defines what the agent must not touch |
| Current System Context | Summarizes relevant existing architecture / patterns / conventions |
| Target Behavior | Defines required behavior in detail |
| User Flows / Interaction Rules | Specifies step-by-step behavior |
| Data Contracts | Defines types, schemas, fields, enums, validation, persistence rules |
| API / Service Contracts | Defines endpoints, service methods, events, integrations |
| UI / Component Contracts | Defines component behavior, props, attributes, states, slots, variants, accessibility |
| File / Module Map | Identifies likely files, directories, or packages involved |
| Constraints | Lists technical, architectural, performance, security, and design constraints |
| Agent Instructions | Defines how agents should approach the task (read-before-edit, minimal-diff, stop-and-escalate triggers) |
| Task Breakdown | Decomposes work into implementation units |
| Acceptance Criteria | Defines what must be true when complete |
| Test Plan | Defines required unit, integration, E2E, visual, or manual checks |
| Review Checklist | Defines what reviewers or orchestrator agents must inspect |
| Open Questions | Captures unresolved issues that block or affect execution |

Not every SPEC needs every section. The audit signal is whether **scope, contracts, and verification** are unambiguous — not whether the template is complete.

## When to apply this rubric

- **Mandatorily**: any agentic coding task targeting non-trivial code change (multi-file edits, new features, schema changes, API contract changes)
- **After** the PRD is committed (see `prd-authoring`)
- **As a review gate** before the SPEC is handed to a coding agent or orchestrator
- **As a debugging frame**: when an agent over-edits / under-implements / opportunistically refactors, walk D1 + D5 + D7 + D10 first — usually one was missing in the SPEC
- **As a context-quality probe**: when running a multi-agent workflow, score each SPEC fed to coding agents. Low scores correlate with low completion rates.

## SPEC tier-down for small changes

A small change (low-risk, localized, easy to verify) can use a combined lightweight PRD/SPEC:

```md
# Feature Brief

## Intent
## Scope
## Requirements
## Implementation Notes
## Acceptance Criteria
```

Acceptable when scope is < ~5 files AND change is reversible AND verification is local.

Anything beyond that should separate the PRD and SPEC.

## What this rubric does NOT cover

- Upstream product alignment → see `prd-authoring`
- UI design discipline → see `agents-ux-wireframing-ascii`
- CSS composition discipline for composite UIs → see `composite-css-composition-discipline`
- Agent harness quality (the environment that consumes SPECs) → see `harness-design`
- Context delivery mechanics → see `context-engineering`
- Multi-agent coordination → see `multi-agent-coordination`

## Practical rule of thumb

> Use a **SPEC** when the core risk is **execution ambiguity**.
>
> A good SPEC should make the next correct change obvious to the agent.

The SPEC's success test: a coding agent reads it, plans the implementation, executes within scope, verifies via acceptance criteria, and either ships or stops at an escalation criterion — without inferring intent the SPEC failed to declare.

## Citations

Source document: `/Users/kimba/Downloads/prd-vs-spec-agentic-coding-workflows.md` (sections 1, 3, 4, 5, 7, 8, 9, 11, 13.2, 14, 15).

Companion rubrics:

- `prd-authoring.md` — upstream alignment doc that feeds this rubric's input
- `agents-ux-wireframing-ascii.md` — when SPEC includes UI, wireframing belongs in the UI/Component Contracts section's design source
- `composite-css-composition-discipline.md` — when SPEC includes composite UI, the rubric specifies Rungs 12-13 within the UI/Component Contracts
