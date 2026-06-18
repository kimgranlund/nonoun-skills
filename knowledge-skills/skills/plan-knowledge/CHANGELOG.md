# CHANGELOG — plan-knowledge

## 1.0.0 — 2026-05-07 — Naming Convention Rename

- Renamed from `knowledge-author` to `plan-knowledge` per the `plan-` domain/phase convention.
- All cross-references in downstream/upstream skills updated.

## Optimization Summary

| Metric | Value |
|---|---|
| Baseline score | 51/100 |
| Final score | 88/100 (+37) |
| Method | Full decomposition + rewrite (not incremental) |
| Research sources | 4 |
| Reference files added | 3 |
| Adversarial probes | 7 |
| Survived | 3 |
| Fixed | 4 |

## Research Sources
1. Claude Projects best practices guides (multiple 2025-2026 sources) — informed knowledge base sizing, RAG behavior, retrieval patterns
2. RAG chunking strategy research-survey (Weaviate, Snowflake, Firecrawl) — informed document sizing rules and heading-as-anchor pattern
3. Context engineering literature (Aurimas Griciūnas 2026, Tobi Lütke framework) — informed attention budget principle and context window awareness
4. Claude Code documentation — informed Skills/MCP integration guidance and CLAUDE.md boundary rule

## Root Cause Analysis (Pre-Rewrite)

Eight structural deficiencies identified:

1. **No first principles** — skill was purely procedural with no reasoning framework
2. **No knowledge typing** — all documents treated identically despite different retrieval patterns
3. **No retrieval-aware authoring** — "write for retrieval" was a one-liner, not actionable guidance
4. **Zero worked examples** — teachability near zero
5. **Implicit phase transitions** — no entry/exit criteria between phases
6. **No anti-patterns** — most common failure modes undocumented
7. **No context engineering awareness** — no mention of token budgets, retrieval mechanics, or sizing
8. **Thin composability** — Claude Code got 4 lines; MCP/Skills unmentioned

## Design Decisions

### Full rewrite vs. incremental improvement
The baseline had structural problems (missing first principles, no typing system, no reference files) that couldn't be fixed incrementally. A full rewrite with modular architecture was more honest than pretending to iterate on a fundamentally different structure.

### Three reference files, not zero
The original was a single 147-line file. The rewrite uses SKILL.md (~180 lines) as a routing layer with three reference files (~150-200 lines each) loaded on demand. This follows the meta-skill's progressive disclosure principle: SKILL.md gives the workflow, reference files give the depth.

### Knowledge typing as a first-class concept
The six knowledge domains in the original were a flat list. The rewrite promotes them to typed documents with distinct structures, templates, and worked examples. This is the single highest-leverage change — it converts "write some docs about your project" into "author typed knowledge artifacts optimized for retrieval."

### Retrieval mechanics as first principle
The original said "write for retrieval" without explaining what retrieval is or how it works. The rewrite includes a simplified model of Claude's retrieval system and derives all authoring rules from it. This means Claude can reason about novel situations ("should I split this document?") by reasoning from the retrieval model, not by memorizing rules.

### Anti-patterns section
Added the six most common failure modes observed across Claude Projects usage. Anti-patterns teach more effectively than positive instructions because they define the boundary between acceptable and unacceptable behavior.

### Claude Code boundary rule
The original said "keep in sync." The rewrite defines a clear boundary rule (understanding vs. execution vs. behavior), a worked example showing the same topic handled across both layers, and a sync checklist. Also added Skills and MCP integration guidance.

## Adversarial Probes

### Probe 1: indirect-context-request
- **Category:** trigger (under-trigger)
- **Input:** "I keep re-explaining my project to Claude every time I start a new chat"
- **Result:** SURVIVE — description covers this pattern
- **Action:** none

### Probe 2: existing-docs-reshape
- **Category:** trigger (under-trigger)
- **Input:** "I have markdown files from my old wiki, can you help organize them for Claude?"
- **Result:** DEGRADE → FIXED
- **Action:** Added "reshape, reorganize, or migrate existing documentation" to description

### Probe 3: general-project-management
- **Category:** trigger (over-trigger / hijack)
- **Input:** "Help me plan my home renovation project timeline"
- **Result:** RISK → FIXED
- **Action:** Narrowed "set up a project" to "set up a Claude project", added "When NOT to use" section, added explicit exclusion in description

### Probe 4: phase-2-without-reference-file
- **Category:** dependency
- **Input:** What if references/knowledge-types.md can't be loaded?
- **Result:** BREAK → FIXED
- **Action:** Added fallback guidance: "use the priority table below" with minimal inline authoring pattern

### Probe 5: non-technical-project
- **Category:** instruction (incompleteness)
- **Input:** "Set up a knowledge base for my content marketing workflow"
- **Result:** DEGRADE → FIXED
- **Action:** Added "Adapting for Non-Technical Projects" section to knowledge-types.md with domain translation table

### Probe 6: existing-messy-knowledge-base
- **Category:** edge case
- **Input:** "I already have a knowledge base but it's a mess. Help me fix it."
- **Result:** DEGRADE → FIXED
- **Action:** Added "Retrofitting an Existing Knowledge Base" section to SKILL.md with 4-step audit workflow

### Probe 7: claude-code-only
- **Category:** trigger
- **Input:** "Help me write a good CLAUDE.md for my repo"
- **Result:** SURVIVE — description includes "making a CLAUDE.md"
- **Action:** none
