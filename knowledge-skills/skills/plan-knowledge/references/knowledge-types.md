---
date: 2026-05-06
---

# Knowledge Types Reference

Every knowledge base is composed of typed documents. Each type has a distinct structure
optimized for how it will be queried. Don't force all knowledge into the same shape —
type it, and the retrieval system rewards you with precision.

---

## Type 1: Orientation Document

**Purpose:** The entry point. Tells Claude (and humans) what this project *is*.

**When queried:** "What is this project?", "Who is this for?", "What problem does this solve?"

**Structure:**

```markdown
# [Project Name]

## What It Is
[2-3 sentences. What the project is and what it does.]

## Problem It Solves
[What pain point or need this addresses. Be specific.]

## Who It's For
[Target users/audience. Internal team? End users? Both?]

## Current Status
[Active development / Maintenance / Planning. What phase.]

## Key Links
[Repository, staging URL, production URL, design files — whatever is relevant.]
```

**Worked example:**

```markdown
# Adia Claims Intelligence

## What It Is
A module within the Adia clinical intelligence platform that automates
medical billing validation. It cross-references CPT codes against
ICD-10 diagnoses and flags mismatches before claim submission.

## Problem It Solves
Manual claims review is error-prone and slow. Clinics lose 3-8% of
revenue to preventable claim denials. This module catches errors at
the point of entry rather than after rejection.

## Who It's For
Billing coordinators and clinic administrators using the Adia platform.
The B2B API also serves partner clinic networks like Carbon Health.

## Current Status
Active development. Core validation engine is live. CPT-to-ICD-10
editing UI is in design (see architecture.md for the gap analysis).

## Key Links
- Repository: github.com/adia-health/claims-intelligence
- Staging: claims-staging.adia.ai
- Design: figma.com/file/xxx/claims-ui
```

**Sizing:** 50-150 lines. One per project.

---

## Type 2: System Map (Architecture)

**Purpose:** How the system is structured. Components, boundaries, data flow, patterns.

**When queried:** "How does X connect to Y?", "Where does this data live?", "What's the architecture?"

**Structure:**

```markdown
# [System/Component] Architecture

## System Overview
[High-level description. What are the major components and how do they relate?]

## Component: [Name]
**Responsibility:** [What it owns]
**Technology:** [Stack/framework]
**Communicates with:** [Other components, via what protocol]
**Data:** [What data it reads/writes, where stored]

[Repeat for each major component]

## Data Flow
[How data moves through the system. Key pathways.]

## Patterns & Conventions
[Architectural patterns in use: event-driven, REST, CQRS, etc.]

## Known Limitations
[Architectural constraints, tech debt, planned changes]
```

**Authoring guidance:**
- Name every component explicitly. "The backend" is not a component name.
- State the communication protocol between components (REST, gRPC, events, direct import).
- Include data ownership — which component is the source of truth for which data.

**Sizing:** 100-300 lines. Split into multiple documents if the system has >5 major components.

---

## Type 3: Decision Log

**Purpose:** Records what was decided and why. The most undervalued knowledge type — without rationale, Claude re-derives decisions from first principles and may reach different conclusions.

**When queried:** "Why did we choose X?", "What was decided about Y?", "Should we change Z?"

**Structure:**

```markdown
# Decision Log

## [Decision Title]
**Date:** [When decided]
**Status:** Active | Superseded by [link] | Under review
**Context:** [What situation prompted this decision]
**Decision:** [What was decided — stated as a clear, declarative sentence]
**Rationale:** [Why this option was chosen over alternatives]
**Alternatives considered:** [What else was on the table and why it was rejected]
**Consequences:** [What this decision implies for future work]
```

**Worked example:**

```markdown
## Custom Orchestration Over LangGraph
**Date:** 2025-03
**Status:** Active
**Context:** Needed an agent orchestration layer for the care planning pipeline.
LangGraph was the leading framework candidate.
**Decision:** Build a custom thin orchestration layer rather than adopting LangGraph.
**Rationale:** LangGraph's abstraction layer adds complexity we don't need —
our workflows are linear with branching, not cyclical graphs. The custom layer
is ~200 lines and fully transparent. We studied LangGraph's checkpointing model
as a reference for our own state management.
**Alternatives considered:** LangGraph (too abstract for our needs), CrewAI
(multi-agent model doesn't fit), raw function chaining (no state management).
**Consequences:** We own the orchestration code. Maintenance burden is ours.
Must build our own checkpointing if we need replay/recovery.
```

**Sizing:** 50-200 lines. One document per project, or split by domain if >15 decisions.

---

## Type 4: Rules Document (Constraints & Conventions)

**Purpose:** What Claude should always or never do in this project context. The behavioral boundary.

**When queried:** "How should I handle X?", "What's the convention for Y?", "Am I allowed to Z?"

**Structure:**

```markdown
# [Domain] Rules & Conventions

## Always
- [Declarative rule]. [Brief rationale.]
- [Declarative rule]. [Brief rationale.]

## Never
- [Declarative rule]. [Brief rationale.]
- [Declarative rule]. [Brief rationale.]

## Conventions
### [Category]
- [Convention with specific example]

### [Category]
- [Convention with specific example]
```

**Worked example:**

```markdown
# API Design Rules

## Always
- Use kebab-case for URL paths. Consistency with existing 200+ endpoints.
- Return 404 for missing resources, not empty 200. Clients depend on status codes.
- Include pagination for any list endpoint returning >10 items.

## Never
- Never return stack traces in production error responses. Security risk.
- Never use query parameters for write operations. REST semantics.

## Conventions
### Authentication
- All endpoints require Bearer token via Authorization header.
- Token validation happens in middleware, not in individual handlers.

### Naming
- Resource names are plural: /patients, /claims, /encounters.
- Nested resources use the parent path: /patients/{id}/encounters.
```

**Authoring guidance:**
- Every rule gets a rationale, even if brief. Claude generalizes better from reasoned rules than from bare commands.
- Be specific enough to act on. "Follow best practices" is not a rule.

**Sizing:** 50-150 lines. Split by domain if the project has >30 rules.

---

## Type 5: Glossary

**Purpose:** Domain-specific terminology, acronyms, and internal names that Claude wouldn't know from training data.

**When queried:** "What is X?", "What does Y mean?", any query containing domain jargon.

**Structure:**

```markdown
# Glossary

| Term | Definition |
|---|---|
| **[Term]** | [Precise definition in project context. Not the Wikipedia definition — the *project's* definition.] |
```

**Authoring guidance:**
- Include terms that have project-specific meanings, even if they're common words. If "encounter" means something specific in your project, define it.
- Include acronyms, internal codenames, and team-specific shorthand.
- Alphabetize. Retrieval doesn't care about order, but human editors do.

**Sizing:** 20-100 lines. One per project.

---

## Type 6: North Star Document (Goals & Success Criteria)

**Purpose:** What "done" looks like. Keeps Claude aligned with project objectives rather than local optimizations.

**When queried:** "What are we trying to achieve?", "Is this the right approach?", "What should we prioritize?"

**Structure:**

```markdown
# Goals & Success Criteria

## North Star
[One sentence: the ultimate outcome this project exists to achieve.]

## Goals (Priority Order)
1. **[Goal]** — [Measurable criterion]. [Current status.]
2. **[Goal]** — [Measurable criterion]. [Current status.]

## Non-Goals
- [Thing that is explicitly out of scope and why.]

## Success Metrics
| Metric | Target | Current |
|---|---|---|
| [Name] | [Target value] | [Current value or "not yet measured"] |
```

**Authoring guidance:**
- Non-goals are as important as goals. They prevent Claude from optimizing for things you don't care about.
- Success criteria should be measurable. "Better UX" is not a criterion. "Task completion time <30 seconds" is.

**Sizing:** 30-80 lines. One per project.

---

## Choosing What to Write First

Not every project needs all six types on day one. Here's the minimum viable knowledge base:

**Always start with:**
1. Orientation doc (Type 1) — Claude needs to know what the project *is*
2. Rules doc (Type 4) — Claude needs to know the behavioral boundaries

**Add next based on project type:**
- **Engineering project:** Architecture (Type 2) + Decision log (Type 3)
- **Content/workflow project:** Goals (Type 6) + Glossary (Type 5)
- **Domain-heavy project:** Glossary (Type 5) + Architecture (Type 2)

**Add the rest incrementally** as they become relevant. A knowledge base that grows with the project is better than one that tries to be complete on day one and ends up stale.

---

## Adapting for Non-Technical Projects

The types above use engineering examples, but the structure works for any domain. The key adaptation is renaming while keeping the structural pattern:

| Engineering Type | Content/Marketing Equivalent | Operations Equivalent |
|---|---|---|
| System Map | Channel Map (platforms, workflows, audiences) | Process Map (stages, handoffs, tools) |
| Decision Log | Strategy Log (campaign choices, brand decisions) | Policy Log (process changes, tool selections) |
| Rules Doc | Style Guide + Brand Voice Rules | SOP + Compliance Rules |
| Glossary | Brand Terminology + Audience Segments | Internal Terminology + Role Definitions |

The structural templates (heading patterns, declarative statements, sizing) apply identically regardless of domain.
