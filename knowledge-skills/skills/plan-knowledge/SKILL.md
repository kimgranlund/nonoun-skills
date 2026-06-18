---
name: plan-knowledge
description: "Use this skill to SET UP / bootstrap a retrieval-optimized Claude Project knowledge base: create foundational knowledge documents, structure project context into typed docs, write a README index and Project Instructions, and establish a knowledge-first workflow (or retrofit an existing base). Triggers: 'set up a Claude Project', onboarding Claude to a codebase/domain, 'help me organize what Claude needs to know', 'fix my knowledge base', 'make Claude useful for [domain]', reshaping or migrating existing docs into a knowledge base. Do NOT trigger for: applying structured mutations to an EXISTING base — UPSERT/DEDUPE/MERGE/SUPERSEDE/RECONCILE (ops-knowledge); authoring a distributable domain-expert or peer-reviewed theory SKILL via research waves (meta-expert-author / meta-theory-author); a repo brain with AGENTS.md, .brain, trip-wires, and CI (ops-repo); user-memory entries under ~/.claude (ops-memory); one standalone document not part of a knowledge base; or general project management or task planning."
---

# Claude Projects: Knowledge Architecture

A skill for helping users build retrieval-optimized, typed knowledge bases for Claude Projects — from first setup through living documentation.


## Invocation

This is a **document-authoring** skill. The user wants a Claude Project knowledge base. Decompose: (1) identify what Claude needs to know, (2) structure into foundational + reference docs, (3) establish the knowledge-first workflow.

### Step 1 — Ingestion

Classify the user's state:
- "Set up a Claude Project" → greenfield: create foundational docs, establish structure
- "Fix my knowledge base" → audit staleness, gaps, drift; reorganize
- "Make Claude know my project" → ingest existing docs; build reference index
- "Migrate docs to knowledge base" → restructure; split narrative from reference

### Step 2 — Decomposition

| Sub-task | Artifact |
|---|---|
| Foundational docs | PROJECT_OVERVIEW.md, ARCHITECTURE.md, DECISIONS.md |
| Reference docs | API surface, data models, deployment topology, runbooks |
| Human pointers | README.md, CHANGELOG.md, CONTRIBUTING.md |
| Workflow | Knowledge-first: update docs before asking Claude to code |

### Step 3 — Execution routing

Knowledge bases decay without maintenance. Every doc must be dated. The `ops-repo` skill audits for staleness. Foundational docs answer "what is this and why"; reference docs answer "how do I do X". Never mix the two in one file.


## When NOT to Use This Skill

- General project management or task planning (use a project management tool)
- Writing a single document that isn't part of a knowledge base
- Pure Claude Code setup with no Project Knowledge component (just write a CLAUDE.md directly)
- API documentation generation from code (use a docgen tool, then optionally import the output)

## First Principles

1. **Knowledge is infrastructure, not documentation.** A knowledge base isn't a wiki — it's the retrieval substrate that determines whether Claude can reason about your project or just guess. Every structural decision (heading density, statement granularity, document boundaries) directly affects retrieval accuracy. Write for the retrieval system, not for human readers.

2. **Typed knowledge retrieves better than generic knowledge.** A glossary, a decision log, a constraint set, and an architecture overview have fundamentally different structures. Documents typed to their knowledge category retrieve more accurately because their internal structure matches the shape of the queries that will fetch them.

3. **Conversations are volatile; knowledge is persistent.** Claude Projects have three layers: Project Instructions (behavioral), Project Knowledge (uploaded files), and Conversations (ephemeral). Anything valuable that surfaces in conversation must be authored back into knowledge files — otherwise it vanishes after the session.

4. **Context windows have an attention budget.** Every token in retrieved context competes for the model's attention. Smaller, focused documents with clear headings and declarative statements retrieve more precisely than large monolithic files. A 200-line document that answers one question well outperforms a 2,000-line document that answers twenty questions vaguely.

5. **The knowledge base is a living system.** Static uploads decay. Decisions change, terminology evolves, architecture shifts. The skill's job isn't just initial setup — it's establishing the habit of maintenance. If the knowledge base doesn't evolve with the project, it becomes noise.

---

## Workflow: Five Phases

### Phase 1 — Orient

Before writing anything, understand the project's shape:

1. **Name the project specifically.** The name should communicate domain and purpose at a glance. Good: `Acme API Redesign – v2 Backend`. Bad: `Dev Work`.

2. **Identify the knowledge audience.** Who will use this project? A solo developer needs different knowledge than a team of five. An engineering project needs different knowledge than a content workflow. This determines which knowledge types to prioritize and how much elicitation depth to invest.

3. **Survey existing materials.** Ask: "Do you have existing docs, specs, READMEs, or past conversations that capture project knowledge?" Existing materials accelerate Phase 2 dramatically — import and reshape rather than elicit from scratch.

### Phase 2 — Elicit & Type

Read `references/knowledge-types.md` for the full taxonomy of knowledge types, their structures, and authoring rules. If the reference file is unavailable, use the priority table below — each type has a distinct structure, and the worked examples in the reference file can be approximated by following the structural pattern: heading → declarative statements → context → details.

Work through these knowledge categories in priority order. Each category has a distinct document type with its own structure — don't force all knowledge into the same shape.

| Priority | Knowledge Type | Document Type | When to Skip |
|---|---|---|---|
| 1 | **Project Overview** | Orientation doc | Never skip |
| 2 | **Architecture & Structure** | System map | Skip for non-technical projects |
| 3 | **Decisions & Rationale** | Decision log | Skip if project is brand new |
| 4 | **Constraints & Conventions** | Rules doc | Never skip |
| 5 | **Terminology & Glossary** | Glossary | Skip if domain is general |
| 6 | **Goals & Success Criteria** | North star doc | Skip if purely operational |

**Entry criteria for Phase 3:** You have at least an Orientation doc and a Rules doc. Everything else can be added incrementally.

### Phase 3 — Author & Structure

Read `references/retrieval-authoring.md` for retrieval-optimized writing patterns, document sizing, heading strategies, and structural templates.

Core authoring rules (the full guide expands these with examples):

- **One topic per document.** If a document covers two unrelated domains, split it. Retrieval precision depends on document focus.
- **Headings are retrieval anchors.** Use specific, keyword-rich headings — not "Overview" but "Patient Intake Workflow Overview". The retrieval system uses headings to locate relevant content.
- **Declarative statements over prose.** "The API uses REST with JSON payloads, authenticated via Bearer tokens" retrieves better than a paragraph that buries the same facts in narrative.
- **Markdown only.** Token-efficient, well-structured, easy to update. HTML occupies roughly 2x the knowledge base space due to tag overhead.

**README.md is mandatory.** It serves as the knowledge base index:
- 2–3 sentence project description
- List of every knowledge document with a one-line description
- Reading order if documents have dependencies

Generate all documents as downloadable files so the user can review and edit before uploading.

### Phase 4 — Write Project Instructions

Project Instructions are separate from the knowledge base — they live in the instructions field, not as an uploaded file. They define Claude's behavioral configuration for every conversation in the project.

Project Instructions should cover:
- Claude's role (e.g., "You are a senior backend engineer familiar with this codebase")
- Output format preferences
- Tone and formality level
- Standing constraints (things Claude should always or never do)
- Pointers to key knowledge documents ("Always check architecture.md before proposing structural changes")

**Key distinction:** Knowledge documents encode *what Claude knows*. Project Instructions encode *how Claude behaves*. Don't duplicate knowledge in instructions — reference it by filename instead. A good heuristic: if the content would be true regardless of Claude's role, it's knowledge. If it only matters because of Claude's role, it's an instruction.

Optimal length: 200–500 words. Shorter is too vague; longer and Claude starts losing pieces in long conversations.

### Phase 5 — Maintain

The knowledge base is a living system. Establish these habits with the user:

- **Decision changes → update the relevant doc, re-upload.** Stale decisions are worse than no decisions — they cause Claude to confidently give outdated guidance.
- **Repeated explanations in conversation → author into knowledge.** If you've explained the same thing three times across conversations, it belongs in a file.
- **New patterns from Claude Code → author back in.** Solutions discovered during implementation are knowledge. Capture them.
- **Quarterly audit.** Review every document. Remove outdated ones. Split documents that have grown too large. Merge documents that overlap.

**Deriving new documents:** The knowledge base is also a generative foundation. Use existing docs to produce onboarding guides, API references, implementation checklists, and decision summaries. Generate as downloadable files for team review before adding to the knowledge base.

---

## Anti-Patterns

These are the most common ways knowledge bases fail. Watch for them and surface them to the user:

1. **The monolith.** One 3,000-line document with everything. Retrieval becomes imprecise because every query partially matches. Split ruthlessly.

2. **The code dump.** Uploading entire source files as "knowledge." Code is not knowledge — it's implementation. Instead, author documents that *describe* the code's architecture, patterns, and conventions.

3. **The duplicate.** Same facts stated in Project Instructions and in a knowledge document. When one gets updated and the other doesn't, Claude receives contradictory signals.

4. **The orphan conversation.** Valuable context lives in conversation history that was never authored into a file. When the conversation scrolls out of context, the knowledge vanishes.

5. **The stale base.** Knowledge uploaded once and never updated. After two months of development, the knowledge base describes a project that no longer exists.

6. **The vague heading.** Using "Overview", "Notes", "Misc" as headings. The retrieval system can't distinguish these from any other document's "Overview". Use specific, keyword-rich headings.

---

## Retrofitting an Existing Knowledge Base

When the user already has a knowledge base that isn't working well, don't start from scratch. Audit and reshape:

1. **Inventory.** List every document with its line count, topic, and type (using the six knowledge types). Identify: monoliths (>300 lines), orphans (no clear type), duplicates (overlapping content).

2. **Triage.** For each document, decide: keep as-is, split, merge, rewrite, or remove. Priority: split monoliths first (biggest retrieval win), then rewrite vague headings, then remove stale content.

3. **Retype.** Reshape documents to match the knowledge type templates. A "notes" document usually contains fragments of 2-3 different types — extract them into properly typed documents.

4. **Re-index.** Update or create the README.md to reflect the new structure.

This is the same workflow as greenfield setup, just starting from Phase 3 (Author & Structure) with existing raw material instead of Phase 2 (Elicit).

---

## Claude Code Integration

Read `references/claude-code-integration.md` for the full guide on keeping Project Knowledge and CLAUDE.md coherent.

Quick summary: Claude Projects and Claude Code serve complementary roles.

| Layer | Tool | What belongs |
|---|---|---|
| **Thinking & Knowledge** | Claude Projects | Decisions, rationale, domain knowledge, goals, architecture, terminology |
| **Execution & Rules** | Claude Code + `CLAUDE.md` | Build/test commands, code style rules, file structure, workflow rules |

CLAUDE.md is the Claude Code equivalent of Project Instructions. They should not contradict each other. When working in Claude Code, anything explained repeatedly or corrected frequently is a signal it belongs in the knowledge base.

---

## Output Checklist

When completing a knowledge base setup, verify:

- [ ] Project named specifically (domain + purpose)
- [ ] README.md exists and indexes all documents
- [ ] Each knowledge type has at least one dedicated, focused document
- [ ] Documents follow retrieval-optimized authoring patterns (see references)
- [ ] Project Instructions written and saved (separate from knowledge base)
- [ ] Instructions reference knowledge docs by filename, don't duplicate them
- [ ] All files uploaded to Project Knowledge
- [ ] User understands the living-document expectation and audit cadence
- [ ] If Claude Code is used: CLAUDE.md and Project Instructions are coherent

---

## Reference Files

Load these on demand based on what the user needs:

- `references/knowledge-types.md` — Full taxonomy of knowledge types with structures, templates, and worked examples
- `references/retrieval-authoring.md` — Retrieval-optimized writing patterns, document sizing, heading strategies, and anti-patterns
- `references/claude-code-integration.md` — Keeping Project Knowledge and CLAUDE.md coherent, with worked examples of the boundary between them
