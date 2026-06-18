---
date: 2026-05-06
---

# Claude Code Integration

How to keep Claude Projects and Claude Code working as a coherent system rather than two disconnected tools.

---

## The Two-Layer Model

Claude Projects and Claude Code operate at different layers of the same project:

| Concern | Tool | Persistence |
|---|---|---|
| **What Claude knows** (domain, decisions, architecture) | Project Knowledge | Uploaded files, available across all project conversations |
| **How Claude behaves** (role, tone, format) | Project Instructions | Instructions field, applies to every project conversation |
| **How Claude executes** (build commands, style rules, file conventions) | CLAUDE.md | File in repo root, read at start of every Claude Code session |
| **What Claude can do** (tools, capabilities, integrations) | Skills + MCP servers | `.claude/skills/` directory and MCP configuration |

### The Boundary Rule

**Project Knowledge = understanding.** Things that are true about the project regardless of which tool is interacting with it. Domain knowledge, architectural decisions, business rules, terminology.

**CLAUDE.md = execution rules.** Things that only matter when writing, running, or testing code. Build commands, linting rules, file naming conventions, test patterns, commit message format.

**Project Instructions = behavioral role.** How Claude should present itself and respond. Tone, format preferences, standing constraints.

**The overlap danger:** When the same fact appears in both Project Knowledge and CLAUDE.md, they will eventually diverge. One gets updated, the other doesn't. Claude receives contradictory signals and either picks the wrong one or hedges.

**Resolution:** Keep facts in one place. Use cross-references for the other:

```markdown
# In CLAUDE.md
# Architecture
See the project knowledge base document `architecture.md` for the full
system map. Key points for code work:
- All new services go in /services
- Use the repository pattern for data access
- Event handlers live in /handlers, not in service files
```

---

## CLAUDE.md Structure

A well-structured CLAUDE.md covers these sections:

```markdown
# [Project Name]

## Build & Run
[Exact commands to build, test, run, deploy]

## Code Conventions
[Style rules, naming conventions, file organization]

## Workflow Rules
[PR process, branch naming, commit format, review requirements]

## Key Patterns
[Architectural patterns to follow when writing new code.
Reference project knowledge docs for the *why*.]

## Do Not
[Things Claude Code should never do in this codebase.
Specific enough to act on.]
```

### Worked Example: The Boundary in Practice

**In Project Knowledge (`architecture.md`):**
```markdown
## Event System
The platform uses an event-driven architecture for cross-service
communication. Events are published to an internal message bus.
Services subscribe to events they care about. This was chosen over
direct service-to-service calls to reduce coupling (see decisions.md,
"Event Bus Over Direct Calls").
```

**In CLAUDE.md:**
```markdown
## Event Handlers
- Event handlers go in `/src/handlers/`, one file per event type.
- Name pattern: `handle-{event-name}.ts` (e.g., `handle-patient-created.ts`).
- Every handler must be idempotent. Use the event ID for deduplication.
- Test handlers with: `npm run test:handlers`
```

The knowledge document explains *what the event system is and why it exists*. The CLAUDE.md explains *how to write code for it*. Neither duplicates the other.

---

## Skills Integration

Claude Code supports Skills — SKILL.md files in `.claude/skills/` that extend Claude's capabilities for specific tasks. Skills are the execution-layer equivalent of Project Knowledge documents.

**When to use a Skill vs. a Knowledge Document:**

| If the content is... | Put it in... |
|---|---|
| Facts about the domain or system | Project Knowledge |
| A repeatable workflow or procedure | A Skill |
| Decision rationale | Project Knowledge |
| How to generate a specific artifact type | A Skill |
| Terminology and glossary | Project Knowledge |
| Code generation patterns with templates | A Skill |

**Keeping Skills and Knowledge coherent:** Skills often encode domain knowledge implicitly in their instructions. When a Skill references domain facts, it should point to the Project Knowledge document rather than duplicating the facts:

```markdown
# In .claude/skills/api-endpoint/SKILL.md
## Context
Read the project's `api-rules.md` knowledge document for the full set
of API conventions. This skill applies those conventions to endpoint
generation.
```

---

## MCP Server Integration

For projects that use MCP (Model Context Protocol) servers, the knowledge base should document:

1. **What MCP servers are available** and what they provide
2. **When to use each server** (routing guidance)
3. **Authentication and configuration** requirements

This is especially important because MCP servers inject *capabilities* (tools) while knowledge documents inject *understanding* (context). Claude needs both to use an MCP server effectively.

Example knowledge document section:

```markdown
## Available MCP Servers

### adia-knowledge-graph
**Purpose:** Query the clinical knowledge graph for diagnostic relationships,
care pathways, and billing rules.
**When to use:** Any question about clinical logic, ICD-10/CPT relationships,
or care orchestration rules.
**Key tools:** `query_graph`, `get_pathway`, `validate_codes`

### agent-ui
**Purpose:** Generate UI components from A2UI schema definitions.
**When to use:** When building patient-facing or clinician-facing interfaces.
**Key tools:** `generate_component`, `validate_schema`
```

---

## Sync Checklist

When updating either the knowledge base or CLAUDE.md, verify:

- [ ] No fact is stated in both places (use cross-references instead)
- [ ] CLAUDE.md references knowledge docs by filename where relevant
- [ ] Skills reference knowledge docs for domain facts
- [ ] MCP servers are documented in the knowledge base
- [ ] Terminology is consistent between all layers
- [ ] If a decision changed in the knowledge base, execution rules in CLAUDE.md still align

---

## Signal: When Knowledge Should Be Authored

Watch for these patterns during Claude Code sessions — they indicate knowledge that should be captured:

- **Repeated corrections:** "No, we use PostgreSQL, not MySQL" — this belongs in architecture.md.
- **Re-explained context:** "Remember, this is a healthcare app so we need HIPAA compliance" — this belongs in rules.md.
- **Discovered patterns:** "Oh, I see all the services follow the repository pattern" — this belongs in architecture.md or a decision log entry.
- **Tribal knowledge:** "The reason we don't use GraphQL is..." — this belongs in decisions.md.

Surface these to the user: "I notice you've explained [X] a few times. Would you like me to draft a knowledge document so we capture this for future sessions?"
