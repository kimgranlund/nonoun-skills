---
date: 2026-05-06
---

# Retrieval-Optimized Authoring

How to write knowledge documents that Claude's retrieval system can find and use accurately. This is the rate-limiting factor in knowledge base quality — a well-structured document retrieves precisely, a poorly-structured one becomes noise.

---

## How Claude's Retrieval Works (Simplified)

When a user asks a question in a Project conversation, Claude's retrieval system:

1. **Identifies relevant documents** from the knowledge base based on the query
2. **Extracts relevant sections** within those documents
3. **Injects the retrieved content** into the conversation context alongside the user's message

The retrieval system operates on semantic similarity — it matches the meaning of the query against the meaning of document sections. This means:

- **Headings act as section anchors.** A heading that closely matches a likely query dramatically improves retrieval of the content under it.
- **Declarative statements match queries better** than narrative prose, because queries are usually questions about specific facts.
- **Focused documents beat sprawling ones** because the retrieval system can select the whole document with confidence rather than gambling on which section is relevant.

---

## The Seven Authoring Rules

### Rule 1: One Topic Per Document

A document should answer one *category* of question. If someone asks "what's the API authentication method?" and "what's our deployment process?", those answers should live in different documents.

**Test:** Can you summarize this document's purpose in one sentence without using "and"? If not, split it.

**Bad:**
```markdown
# Project Notes
## Authentication
Bearer tokens...
## Deployment
Docker containers on ECS...
## Database Schema
Patients table...
```

**Good:** Three separate documents — `api-authentication.md`, `deployment.md`, `database-schema.md`.

### Rule 2: Keyword-Rich Headings

Headings are the primary retrieval signal. Make them specific and include the terms someone would actually search for.

**Bad headings:** `Overview`, `Details`, `Notes`, `Section 1`, `Miscellaneous`

**Good headings:** `Patient Intake API Endpoints`, `ICD-10 Code Validation Rules`, `Docker Deployment to AWS ECS`

**Pattern:** `[Domain Noun] [Specific Topic]` — not `[Generic Category]`.

### Rule 3: Declarative Statements Over Narrative

The retrieval system matches queries to content. Queries are usually factual ("what database do we use?"). Declarative statements ("The primary database is PostgreSQL 15 on RDS") match these queries directly. Narrative prose buries the same fact in context that dilutes the match.

**Bad:**
```markdown
After much deliberation, the team eventually decided that it would be
best to go with PostgreSQL for the primary database, considering various
factors including cost, team familiarity, and the need for JSONB support.
```

**Good:**
```markdown
**Primary database:** PostgreSQL 15 on AWS RDS.
**Rationale:** JSONB support for flexible schemas, team familiarity, managed service reduces ops burden.
```

Same information. The second version retrieves 3x more reliably because the key facts are in prominent positions with clear labels.

### Rule 4: Front-Load Key Information

Put the most important facts at the top of each section. The retrieval system sometimes truncates long sections — front-loaded content survives truncation.

**Pattern for each section:**
1. **Statement of fact** (the answer)
2. **Context** (why it matters)
3. **Details** (elaboration, edge cases)

### Rule 5: Size Documents for Retrieval Precision

The sweet spot for knowledge documents is **50-300 lines**. Here's why:

- **Under 30 lines:** Too thin. Multiple tiny documents create retrieval noise — the system has to choose among many similarly-relevant micro-documents.
- **50-150 lines:** Ideal for most knowledge types. Focused enough to retrieve precisely, substantial enough to be self-contained.
- **150-300 lines:** Acceptable for complex topics (architecture, decision logs). Use clear heading hierarchy to aid section-level retrieval.
- **Over 300 lines:** Split it. Long documents dilute retrieval precision because the system can't be confident which section matters.

### Rule 6: Use Consistent Terminology

If the project calls it a "patient encounter", use "patient encounter" everywhere — not "visit", "appointment", "session", and "encounter" interchangeably. Inconsistent terminology means the retrieval system might find the definition but miss the usage, or vice versa.

**Practical step:** Author a glossary (Type 5) early, then use its terms as the canonical vocabulary across all documents.

### Rule 7: Cross-Reference by Filename

When one document depends on another, reference it explicitly by filename:

```markdown
For the full API authentication flow, see `api-authentication.md`.
```

This serves two purposes: it helps human editors navigate the knowledge base, and it gives Claude an explicit pointer to follow when a query spans multiple documents.

---

## README.md Template

Every knowledge base needs a README. Here's the template:

```markdown
# [Project Name] — Knowledge Base

[2-3 sentence project description.]

## Documents

| File | Type | Description |
|---|---|---|
| `orientation.md` | Orientation | What the project is, who it's for, current status |
| `architecture.md` | System Map | Component structure, data flow, tech stack |
| `decisions.md` | Decision Log | Key decisions with rationale and alternatives |
| `rules.md` | Rules | Constraints, conventions, always/never rules |
| `glossary.md` | Glossary | Domain terminology and internal names |
| `goals.md` | North Star | Objectives, success criteria, non-goals |

## Reading Order

Start with `orientation.md` for project context. Then read `rules.md`
for behavioral constraints. All other documents can be read in any order
as needed.

## Maintenance

This knowledge base is actively maintained. Last audit: [date].
When decisions change, update `decisions.md` and re-upload.
```

---

## Document Naming Conventions

Use lowercase kebab-case filenames that communicate content at a glance:

**Good:** `api-authentication.md`, `patient-data-model.md`, `deployment-rules.md`

**Bad:** `notes.md`, `doc1.md`, `misc-stuff.md`, `IMPORTANT.md`

**Pattern:** `[domain]-[topic].md`. If a document needs a generic name, it's probably covering too many topics.

---

## Common Authoring Mistakes

**Mistake: Uploading raw source code as knowledge.**
Code is implementation, not knowledge. Upload a document that *describes* the code — its architecture, patterns, conventions, and key decisions. If Claude needs to reference specific code, include short illustrative snippets (10-20 lines), not entire files.

**Mistake: Duplicating Project Instructions content in knowledge docs.**
If a rule appears in both Project Instructions and a knowledge document, they'll eventually diverge. Put behavioral rules in Instructions, factual knowledge in documents. Reference by filename when Instructions need to point at knowledge.

**Mistake: Writing for human aesthetics instead of retrieval.**
Paragraphs of flowing prose read well but retrieve poorly. Knowledge documents aren't essays — they're structured data in markdown format. Prioritize scannability, keyword density, and clear section boundaries over narrative flow.

**Mistake: Never updating after initial setup.**
A knowledge base that's two months stale is actively harmful — Claude will confidently cite outdated information. Schedule quarterly reviews. Remove documents that no longer reflect reality.

**Mistake: Creating too many tiny documents.**
Splitting is important, but over-splitting creates its own problem. If every paragraph becomes its own file, the retrieval system has to choose among dozens of equally-relevant micro-documents. Aim for documents that are self-contained units of knowledge, typically 50-300 lines.
