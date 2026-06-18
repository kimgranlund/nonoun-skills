---
date: 2026-05-06
---

# Composition with sibling skills

How to chain `/meta-app-scaffold` with the substantive authoring skills.
Read in Step 5 of the SKILL.md workflow.

## Composition principle

This skill scaffolds *folders + minimal seeds*. Substantive content arrives
via four sibling skills, each with its own user-loop semantics:

| Sibling | Owns | Output |
|---|---|---|
| `/meta-expert-author` | `apps/<name>/skills/<name>-expert/` | SKILL.md body + references/* + skill.json + CHANGELOG.md |
| `/plan-spec` | `apps/<name>/spec/{BRIEF,ARCHITECTURE,SPEC,ARCHITECTURE-REVIEW}.md` | Multi-doc spec set, dual-readability |
| `/plan-prd` | `apps/<name>/spec/PRD.md` (+ JSON corpus) | Schema-validated PRD against project-schema-2026.json |
| `/meta-skill` | Any app-private skill beyond the primary `<name>-expert` | New SKILL.md + references + skill.json + CHANGELOG |

## When to invoke which

### Always invoke first: `/meta-expert-author`

The expert skill provides the research-survey basis that downstream skills (plan-spec,
plan-prd) consume. **Skipping this step is the most common failure mode** — a
spec authored without a research-survey basis is shallow; a PRD without research-survey is
ungrounded.

**Default arguments**:

```
/meta-expert-author <<EOF
Author the project-scoped expert skill for apps/<name>/.

- Target directory: apps/<name>/skills/<name>-expert/
- Mode: capability (broad reference coverage; mirrors tasks-expert)
  [or canon-curation if the domain has deep canonical sources]
- Domain: <user-supplied 1-line description>
- Sibling exemplars to mirror in style: tasks-expert, expert-dashboard
- Project-scoped (NOT global) — it lives inside the app, opinionated toward
  this app's architecture.
- Coverage tiers: foundational / expanded / deep per file
- Every reference file: dated YAML frontmatter, primary-source citations.
- Skill.md: flat-prose entry + task→reference routing tables + cheat sheets
- references/: organized by axis (e.g., views-* / interaction-* / data-* /
  state-* / accessibility-* / foundations-*) — pick axes that fit the domain
- 3-5 research-survey waves, each dispatching parallel agents.

Stop after the SKILL.md is drafted (post-Wave 1) so I can review the axis
breakdown before committing to the full wave plan.
EOF
```

**Stop point**: explicitly tell meta-expert-author to stop after Wave 1
(SKILL.md + axis breakdown). Don't let it run all 5 waves before the user
sees the structure.

### Invoke second (after expert skill is mature): `/plan-spec`

Once the expert skill has at least Wave 1's references, the spec docs can
draw on them.

**Default arguments**:

```
/plan-spec <<EOF
Author the spec set for apps/<name>/.

- Target directory: apps/<name>/spec/
- Existing seeds (replace, don't append):
  - apps/<name>/spec/BRIEF.md (PRD-01-BRIEF)
  - apps/<name>/spec/ARCHITECTURE.md (PRD-01-ARCH)
  - apps/<name>/spec/SPEC.md (PRD-01-SPEC)
- Spec type: Hybrid Brief + Spec (reads as a 3-page brief AND an implementer-
  facing reference). Doc IDs use the PRD-NN- prefix.
- Research basis: apps/<name>/skills/<name>-expert/ (project knowledge)
- Audience: implementers, reviewers, future agents
- Use the dual-readability markers: 📐 (spec detail), 💡 (reasoning),
  ⚠️ (open decisions)
- Cross-link to plan/MILESTONES.md and plan/ROADMAP.md for execution-axis
  context.

Phase 1 — search the project knowledge first (the expert skill's references).
Only web-search for gaps the expert skill doesn't cover.
EOF
```

### Invoke (opt-in): `/plan-prd`

Use only when the user wants a **schema-validated** PRD against Adia's
project-schema-2026.json. Most apps don't need this — `/plan-spec`'s
hybrid Brief + Spec is enough for ad-hoc projects.

**Default arguments**:

```
/plan-prd <<EOF
Author a schema-validated PRD for apps/<name>/.

- Target directory: apps/<name>/spec/
- PRD ID: PRD-NN-<title-slug>
- Schema: project-schema-2026.json
- Existing context: apps/<name>/skills/<name>-expert/ (research-survey) +
  apps/<name>/spec/{BRIEF,ARCHITECTURE,SPEC}.md (if /plan-spec has run)
- Output: spec/PRD.md (root JSON or markdown), supporting spec files,
  PROJECT.md (top-level summary), file manifest
- Mechanically validate every output against the schema before declaring done.
EOF
```

`/plan-prd` and `/plan-spec` are NOT redundant: `/plan-spec` produces a
prose-first hybrid doc; `/plan-prd` produces a JSON-validated artifact. Pick
based on whether downstream tooling needs the schema-validated form.

### Invoke (opt-in): `/meta-skill`

Use when the app needs an additional skill beyond `<name>-expert`. Examples:

- `apps/tasks/skills/task-card-author/` — sub-skill that authors task-card
  variants (specialized, smaller scope than tasks-expert)
- `apps/chat-canvas/skills/canvas-shortcut-mapper/` — sub-skill that maps
  keyboard shortcuts to canvas operations

**Default arguments**:

```
/meta-skill <<EOF
Create a new skill at apps/<name>/skills/<sub-skill-name>/.

- Project-scoped (lives inside the app, not in ~/.claude/skills/)
- Description: <user-supplied 1-line>
- Triggers: <user-supplied phrases>
- Composition with parent expert: this skill complements <name>-expert by
  handling <specific narrower scope>; refers back to it for general domain
  knowledge.
- Output structure: SKILL.md (≤500 lines) + skill.json + CHANGELOG.md +
  optional references/ subfolder
EOF
```

## Composition order

The dependency graph:

```
                ┌─ /plan-spec ────► spec/{BRIEF,ARCH,SPEC}.md
                │
/meta-expert-author ──► skills/<name>-expert/
                │
                └─ /plan-prd (opt-in) ──► spec/PRD.md
                │
                └─ /meta-skill (opt-in) ──► skills/<sub-skill>/
```

Order:

1. `/meta-app-scaffold` (this skill) — scaffolds the folders + seeds.
2. `/meta-expert-author` — first wave of references; SKILL.md content.
3. `/plan-spec` — drafts BRIEF, ARCHITECTURE, SPEC against the expert
   skill's research-survey.
4. (opt-in) `/plan-prd` — schema-validated PRD if needed.
5. (opt-in) `/meta-skill` — sub-skills as the app grows.
6. (continuous) `/meta-expert-author` waves 2-5 — fills in remaining
   references. Can run in parallel with plan-spec once Wave 1's references
   are in place.

## Don't auto-invoke

Each chained skill is a long-running authoring loop. Don't auto-invoke
without explicit user confirmation. Surface the chain as proposals:

> "Foundation laid. Three follow-ups, run in order or skip per priority:
>
>  1. `/meta-expert-author` for `apps/<name>/skills/<name>-expert/`
>  2. `/plan-spec` for `apps/<name>/spec/`
>  3. (optional) `/plan-prd` for schema-validated PRD
>
> Want me to invoke (1) now?"

## Re-running scaffold against an evolving app

Apps evolve. The user might later want:

- An `agents/` folder added (because they're authoring a sub-agent now).
- A `commands/` folder added (because they're shipping a slash command).
- A `bin/` folder added (because they need executable scripts).

For these, **don't re-run the full scaffold**. Just create the folder and seed
its initial file. Re-running the full scaffold risks overwriting authored
content.

If the user asks for a "scaffold update" (rare), confirm what specifically
they want, then add only the missing pieces — never overwrite an existing
SKILL.md or spec file.

## Sanity-checking after the chain

Once 2-3 chained skills have completed, run a sanity check:

```bash
# All folders present
test -d apps/<name>/{skills/<name>-expert,spec,plan,assets,app}

# Skill is no longer a stub (meta-expert-author ran)
grep -q "STUB" apps/<name>/skills/<name>-expert/SKILL.md && echo "STILL A STUB" || echo "✓ skill populated"

# Spec docs are no longer stubs (plan-spec ran)
grep -q "Stub — to be authored" apps/<name>/spec/SPEC.md && echo "STILL A STUB" || echo "✓ spec populated"

# Links resolve (chat-ui)
[ -f scripts/check-links.mjs ] && node scripts/check-links.mjs apps/<name>/

# README's relative ADR link works
test -f $(grep -oE 'plugin\)\]\(([^)]+)' apps/<name>/README.md | sed 's/.*](//;s/)$//')
```

If any check fails, surface the gap to the user before declaring the foundation
complete.
