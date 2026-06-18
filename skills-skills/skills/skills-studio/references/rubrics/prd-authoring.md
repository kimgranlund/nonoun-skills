---
title: PRD Authoring (Product Requirements Document for human teams)
key_question: Does the PRD establish shared product intent for the human team — problem, users, outcomes, scope boundaries, tradeoffs — without collapsing into a disguised implementation plan or a vague feature list?
layer: product-authoring
primary_critic: steve-yegge  # Platform-vs-product lens; PRDs are the alignment substrate for N+ stakeholders
companion_rubrics:
  - spec-authoring                       # SPEC = mechanizable counterpart; PRDs feed SPECs
  - context-engineering                  # PRDs are upstream context for downstream agentic execution
  - progressive-context-construction     # PRD → Design Spec → Technical SPEC → Agent Task SPEC is one such ladder
version: 0.1.0
status: empirically-derived
source: "/Users/kimba/Downloads/prd-vs-spec-agentic-coding-workflows.md (sections 2, 6, 10, 13.1)"
---

# PRD Authoring (for human-team product alignment)

## What this rubric measures

When an org produces a Product Requirements Document, does it create **shared product understanding** across product / design / engineering / leadership / QA / customer-success / operations — without overfitting to implementation or flattening into a vague feature list?

The failure mode this rubric defends against: **a PRD that reads like a feature checklist or a disguised technical spec**, leaving the team without the intentional frame (problem, users, outcomes, tradeoffs) that distinguishes product judgment from execution.

## Why this is its own rubric

Distinct from `spec-authoring` (which measures execution contracts for coding agents) and from `context-engineering` (which measures context delivery to any agent). A PRD optimizes for **human interpretation, strategic alignment, scope negotiation, product judgment**. Its readers are not coding agents; they are humans making prioritization and tradeoff calls. The rubric measures whether the document serves that audience.

PRDs and SPECs are not interchangeable. A PRD answers "what should exist, for whom, and why?" A SPEC answers "what exactly should change, where, under what constraints, and how will we know it is correct?" The PRD's job is to create **shared intent**; the SPEC's job is to create **reliable execution**. This rubric scores the first.

## Pipeline this rubric encodes

```
Problem awareness → Stakeholder alignment → Product intent → Scope negotiation
                    ↓
                    PRD authored (this rubric)
                    ↓
                    Design Spec → Technical SPEC → Agent Task SPEC (see spec-authoring rubric)
                    ↓
                    Implementation → Review → Merge
```

Without a strong PRD upstream, every downstream SPEC inherits ambiguity. Without a strong SPEC downstream, every agentic-execution loop fills the gap with its own assumptions.

## 8 scoring dimensions

| # | Dimension | Type | Question |
| --- | --- | --- | --- |
| D1 | Problem-statement clarity | gate | Is there a named root problem (user / business / system) that's distinguishable from a feature request? Can a stakeholder scan the first 200 words and articulate the problem? |
| D2 | Goals + Non-Goals balance | gate | For every named goal, is there a matched scope boundary (Non-Goal, deferred, out-of-scope)? An unbounded goal list is a non-PRD. |
| D3 | User / persona specificity | gate | Does the document name specific user types (role + context + needs) rather than "users" generically? |
| D4 | Success-metrics measurability | gate | Are outcomes stated as observable signals (numbers, percentages, behavior counts, sentiment shifts) rather than vague directionals ("better," "smoother")? |
| D5 | Implementation-prescription avoidance | gate | Does the PRD stay at the product layer? File paths, API schemas, framework choices, agent task decomposition should be absent EXCEPT where a technical constraint is genuinely a product constraint (offline, HIPAA, sub-100ms, accessibility compliance, etc.). |
| D6 | Tradeoff acknowledgment | review | Are major assumptions, constraints, and tradeoffs surfaced — or hidden behind smooth narrative? |
| D7 | Prioritization clarity | review | When stakeholders must choose, does the PRD name what wins? Or does it treat all requirements as equally important? |
| D8 | Outcome-orientation over feature-listing | review | Does the PRD describe what the product should _accomplish for the user_ — or just enumerate features the team has agreed to ship? |

**Gate dimensions** (D1–D5) — mechanically scoreable from the document structure + content. A reviewer can verify pass/fail by reading the headings + first paragraph of each section.

**Review dimensions** (D6–D8) — require human judgment of intent and honesty.

## 7 named anti-patterns

| ID | Name | What it looks like |
| --- | --- | --- |
| AP-PRD-01 | **Feature-without-problem** | Document describes what to build (filters, dashboards, panels) without naming the user/business/system problem being solved. Reader can't tell why the feature matters. |
| AP-PRD-02 | **Goal-without-non-goal** | Goals section enumerated; no Non-Goals section, or Non-Goals are trivial ("we won't redesign the entire app"). Scope is effectively unbounded. |
| AP-PRD-03 | **Flat-priority list** | Every requirement is "must-have" or "important." When the team hits a tradeoff, the PRD provides no guidance for what wins. |
| AP-PRD-04 | **Hidden-assumption** | The PRD assumes specific technical capabilities, user behaviors, market conditions, or organizational support without stating them. When an assumption fails downstream, the failure looks like a surprise. |
| AP-PRD-05 | **Tradeoff-avoidance** | When two stakeholders want different things, the PRD includes both as goals rather than naming the tradeoff. Forces the conflict to recur in implementation. |
| AP-PRD-06 | **Vague-language** | Heavy use of "seamless," "intuitive," "smart," "delightful," "modern," "robust" without defining the behavior those words imply. Each reader interprets differently. |
| AP-PRD-07 | **Premature-implementation** | Collapses into describing the technical implementation — specific file paths, framework choices, API surfaces, code-shaped pseudocode. Belongs in a SPEC, not a PRD. |

## 5 hard tests

| # | Test | Verifies |
| --- | --- | --- |
| H1 | **Problem-statement scannable in 1 minute** | A stakeholder unfamiliar with the work can read the first 200 words and articulate the problem in their own words. |
| H2 | **Non-Goals section non-empty + non-trivial** | At least 3 substantive scope boundaries are named. "We won't ship a chat feature" beats "we won't redo the website." |
| H3 | **Success metrics are observable** | Every success metric maps to a number, percentage, behavior count, observable user signal, or qualitative survey instrument. No "better UX" or "improved satisfaction" without measurement. |
| H4 | **Persona specificity** | Personas name role + context + need (e.g., "billing admin reconciling end-of-month invoices") rather than "users" or "customers" generically. |
| H5 | **Implementation-detail absence** | No file paths, no API endpoint paths, no framework choices, no code blocks, no agent task decomposition. Exception: when a technical constraint is genuinely a product constraint (latency, accessibility, offline support, regulatory compliance). |

## 7-phase operating procedure

When authoring a PRD:

1. **Name the problem** → root-cause it. What user / business / system pain are we solving? Why now? Why us?
2. **Identify the users** → specific personas with role + context + decision pressure. Not "users."
3. **Define the outcome** → what should be true for the user when this ships? Frame in observable terms.
4. **Bound the scope** → list Non-Goals as explicitly as Goals. What is deferred? What is permanently out of scope?
5. **Surface tradeoffs** → name the assumptions, the constraints, the things you've decided NOT to spend the team's time on. Honest > smooth.
6. **Prioritize** → if the team must make tradeoffs mid-implementation, what wins? MVP vs P1 vs P2.
7. **Hand off** → link to (or anticipate) the downstream SPEC. Make clear what the PRD intentionally leaves to the SPEC author / coding agent.

## Recommended sections (per source doc §2.2 + §10)

| Section | Purpose |
| --- | --- |
| Title / Summary | Names the initiative and gives a concise description |
| Problem Statement | Explains the root problem or opportunity |
| Background / Context | Provides business, user, market, operational, or technical context |
| Goals | Defines what the initiative should accomplish |
| Non-Goals | Defines what the initiative will not attempt to solve |
| Users / Personas | Identifies the primary users and stakeholders |
| Use Cases | Describes the main situations the product must support |
| Product Requirements | Defines product-level capabilities and expected behaviors |
| Success Metrics | Establishes how impact will be measured |
| Scope / Phasing | Separates MVP, follow-up work, and future ideas |
| Dependencies | Identifies teams, systems, decisions, or data needed |
| Risks / Open Questions | Captures unresolved issues and decision points |
| Approval / Ownership | Clarifies responsible parties and sign-off expectations |

Not every PRD needs every section. The audit signal is whether **scope, outcomes, and tradeoffs** are unambiguous — not whether the template is complete.

## When to apply this rubric

- **Mandatorily**: any cross-functional initiative requiring alignment across product / design / engineering / ≥2 stakeholders
- **Before** authoring downstream SPECs (see `spec-authoring`)
- **As a review gate** before a PRD is committed for engineering planning
- **As a debugging frame**: when an initiative ships features but the team disagrees about whether the goal was met, walk D1 + D3 + D4 + D7 first — usually one of those was unbounded in the PRD

## What this rubric does NOT cover

- Technical execution contracts → see `spec-authoring`
- UI/interaction design discipline → see `agents-ux-wireframing-ascii`
- Implementation patterns (CSS composition, etc.) → see `composite-css-composition-discipline`
- Agent harness quality → see `harness-design`
- Context-delivery mechanics → see `context-engineering`

## Practical rule of thumb

> Use a **PRD** when the core risk is **human misalignment**.
>
> A good PRD should make the right thing obvious to the team.

The PRD's success test: stakeholders read it, agree on direction, and downstream SPECs can be derived without renegotiating intent.

## Citations

Source document: `/Users/kimba/Downloads/prd-vs-spec-agentic-coding-workflows.md` (sections 1, 2, 4, 6, 9, 10, 13.1, 14, 15).

Companion rubric: `spec-authoring.md` — the agentic-execution-contract counterpart that this rubric feeds.
