---
date: 2026-04-18
coverage: expanded
peers:
  - ../agent-dispatch/bookkeeping-protocol.md
  - ../methodology/coverage-tiers-and-frontmatter.md
primary_sources:
  - expert-dashboard/SKILL.md, skill.json, INDEX.md, CHANGELOG.md
  - expert-typography/SKILL.md, skill.json, INDEX.md, CHANGELOG.md
  - ~/.claude/skills/CLAUDE.md
---

# Skeleton file templates

The four files that land at v0.1.0, before any reference file is authored. Every skill uses the same four.

## 1. SKILL.md

The flat-prose entry point. Max 1024-char description in frontmatter. Body contains task→reference routing + cheat sheets + composition.

```markdown
---
name: [domain]-expert
description: >
  Use when working with [domain] at any level — [list 6-8 specific tasks].
  Use whenever a user is choosing, comparing, explaining, or specifying [domain] —
  even when they don't explicitly say "[domain]". Peers with [2-4 related skills].
---

# [domain]-expert

[One-sentence framing of the skill.]

## How to read this skill

This skill is structured as **flat-prose entry + tiered references**. This file gives you quick-lookup tables and orientation. Deep content lives in `references/` and loads on demand.

- **Start here** for task routing (table below) and quick reference tables.
- **Go to `references/INDEX.md`** for the full reference manifest with status markers.
- **Cross-reference peers**: [specify peer skills and which referenced file each covers].

## Invocation

Before answering, **ingest** the ask and **decompose** it into sub-questions. Dashboard-style skills almost always take composite questions — treating them as single lookups misses load-bearing parts.

### Step 1 — Ingest (what is actually being asked?)

[Domain-typical latent-intent patterns. Table of surface-prompt → watch-for → clarify-if-unclear. 3-5 rows.]

**Steelman rule**: if the literal prompt implies a narrower answer than the user's likely goal, propose the stronger framing and wait for confirmation.

**Concept-match rule**: [note which parts of the domain the base model covers densely vs thinly; flag low-confidence areas].

### Step 2 — Decompose (what sub-questions does this route to?)

Question-shape decomposition (Shape C in `meta-expert-author/references/methodology/task-decomposition.md`).

| Ask pattern | Typical sub-questions |
|---|---|
| [Pattern 1] | (1) ... (2) ... (3) ... |
| [Pattern 2] | (1) ... (2) ... (3) ... |

**Coverage check**: before answering, confirm every surfaced sub-question has a home (reference file, cheat sheet, or peer skill). Missing home = flag and don't fabricate.

### Step 3 — Route to references / peer skills

- **This SKILL.md's cheat tables** — [list which cheat sheets cover which sub-questions].
- **`references/<axis>/`** — per the Task → reference table below.
- **Peer skills** — [list the peers and what each provides].

### Step 4 — Answer + verify

- Name the decomposition explicitly if non-trivial.
- Flag sub-questions where evidence is thin.
- Don't answer beyond the decomposition.

## Task → reference

| You're doing… | Go to |
|---|---|
| [Task 1] | `references/[axis]/[file].md` |
| [Task 2] | `references/[axis]/[file].md` |
| ... | ... |

## [Cheat sheet #1 — canonical classification / archetype table]

| [Class / Archetype] | [Use for] | [Common pitfalls] |
|---|---|---|
| ... | ... | ... |

## [Cheat sheet #2 — comparative exemplars]

| [Exemplar] | [Known for] |
|---|---|
| ... | ... |

## Composition

This skill peers with:

- **[peer-skill-1]** — [purpose]
- **[peer-skill-2]** — [purpose]

And is consumed by:

- **[consumer-1]** — [purpose]

## Invariants

1. Answers, not generators — delegates computation to `composing-*` peer skills.
2. Flat-prose SKILL.md is the primary entry; references load on demand.
3. Every reference file is dated at the top so staleness is visible.
4. Coverage tiers declared up-front per file.
5. Every claim cites a source at file level; speculation labeled.
6. [Domain-specific invariants — e.g., product-reference profiles document **observable public patterns only**.]
```

Keep SKILL.md under ~250 lines. The routing table and 2-3 cheat sheets are the core; body prose is minimal.

### Variant: "greatest hits" SKILL.md (canon-curation mode)

For **canon-curation mode** skills (see `../methodology/canon-curation-mode.md`), the SKILL.md serves a different role: not a routing table but a **corrections layer** on top of the base model's priors. The domain has a deep canon, the base model knows a lot, and the skill's job is to sharpen misconceptions and point at the canon.

Structure:

```markdown
---
name: [domain]-expert
description: >
  Use when working with [domain] at any level — [list specific tasks]. Use whenever
  a user is choosing, comparing, generating, naming, converting, or explaining [domain],
  even if they do not explicitly ask for "[domain theory]."
---

# [Domain] Expert

A comprehensive knowledge base for [domain]-related work. See `references/INDEX.md` for [N]+ detailed reference files; this skill file contains the essential knowledge to answer most questions directly.

## [Canonical decision table — the one thing the base model tends to get wrong]

| Task | Use | Why |
|---|---|---|
| [Task 1] | **[Canonical answer]** | [Why it's right] |
| [Task 2] | **[Canonical answer]** | [Why it's right] |
| ... | ... | ... |

## [Misconception correction #1]

[2-3 paragraphs explaining what the base model tends to think vs what the canon actually says. Example: expert-color's "HSL isn't bad but here's what it can't do" section.]

## [Named-range / quick-reference table]

[Tight, scannable reference. Example: expert-color's named-hue degree ranges.]

## [Key distinctions the base model conflates]

- **[Term A]** = [precise definition]
- **[Term B]** = [precise definition]
- **[Term C]** = [precise definition]
- [Term A] ≠ [Term B]. They are different dimensions.

## Implementation guidance

[Pseudocode or pattern-level guidance that survives across codebases. Not a tutorial — a decision-structure the agent should preserve regardless of target stack.]

## Where to dig deeper

For [sub-topic X], see `references/historical/` — [what's there, 1 line].
For [sub-topic Y], see `references/contemporary/` — [what's there].
For [sub-topic Z], see `references/techniques/` — [what's there].

Full 148-file manifest: `references/INDEX.md`.
```

**Length target: 150-250 lines, dense.** No task→reference routing table (the canon doesn't map cleanly to tasks). No archetype list. Lead with the one decision table that captures the domain's "what do I reach for" question.

**When to use this variant:**
- The domain has a deep canon (named theorists, foundational papers, canonical books).
- The base model already has strong priors on the domain — the skill corrects, doesn't teach from scratch.
- File → source mapping is 1:1 rather than file → topic.

**When to use the task-routing variant (default):**
- The domain is about choosing and comparing practitioner tools (fonts, dashboard components, libraries).
- The skill's primary question shape is "how do I do X?" or "which X for case Y?"

See `../examples/color-expert-case-study.md` for the canon-curation SKILL.md in practice.

## 2. skill.json

The machine-readable manifest. Required fields per `~/.claude/skills/CLAUDE.md`.

```json
{
  "name": "[domain]-expert",
  "version": "0.1.0",
  "description": "[expanded description; mirrors SKILL.md frontmatter but can be longer]",
  "status": "skeleton",
  "authors": ["[author-handle]"],
  "tags": [
    "[domain]",
    "[7-15 tags derived from axes + canonical exemplars]"
  ],
  "files": [
    "SKILL.md",
    "CHANGELOG.md",
    "references/INDEX.md"
  ],
  "composition": {
    "peer": [
      "[peer-skill-1]",
      "[peer-skill-2]"
    ],
    "consumed_by": [
      "[consumer-1]"
    ]
  },
  "invariants": [
    "[5-8 invariant statements from SKILL.md]"
  ],
  "notes": "[optional free-form context about the skill's design]"
}
```

Version progression: `0.1.0` (skeleton) → `0.2.0` (Wave 1) → ... → `1.0.0` (complete). `status` flips `skeleton` → `wave-1-complete` → ... → `complete`.

## 3. CHANGELOG.md

Seed with a v0.1.0 entry.

```markdown
# Changelog

## [0.1.0] — [ISO date] — Skeleton

### Added

- Directory scaffold: `[skill-name]/` with N `references/` subdirectories ([list axes]).
- `SKILL.md` — flat-prose entry file with frontmatter, task→reference routing table, [cheat sheets].
- `skill.json` — v0.1.0 manifest. Status `skeleton`. Composition declares peers ([list]) and consumers ([list]). Invariants declared.
- `references/INDEX.md` — full reference manifest with planned files across N axes, status markers (✅ present, ⬜ planned), coverage tiers, per-file purpose statements.

### Scoping-survey findings ([ISO date])

[Condensed summary of scoping agent output. Bullet per finding category: landscape shifts, canonical exemplars, library landscape, dated API / spec capability claims, axes shifted since baseline, file-count plan.]

### What's next (Phase 2)

Wave 1 (first parallel dispatch, N agents producing M files): highest-leverage cross-axis foundations.

[List file pairs or agent assignments.]

See `references/INDEX.md` § Wave Plan for Waves 2–5.
```

Subsequent wave entries prepend above v0.1.0. Each wave entry contains: file table (path + coverage + lines), "notable findings" section, "bumped" section (version + tags + INDEX updates), "known gaps" section.

## 4. references/INDEX.md

The manifest. Every planned file listed, status marker per row.

```markdown
# [domain]-expert — Reference Index

_Manifest for the `references/` tree. Authoritative: every file listed here is either present (✅) or planned (⬜). If you add a file, add it here first. If you remove a file, update this index and note it in the top-level `CHANGELOG.md`._

_Status as of [ISO date]: **M/N files landed**._

## Axes

1. **[axis-1]/** — [3-sentence purpose, including key topics]
2. **[axis-2]/** — [3-sentence purpose]
...

## File manifest

| Status | Path |
|---|---|
| | **[axis-1]/** |
| ⬜ | `[axis-1]/[file-1].md` |
| ⬜ | `[axis-1]/[file-2].md` |
| | **[axis-2]/** |
| ⬜ | `[axis-2]/[file-3].md` |
...

## Wave plan

- **Wave 1** (planned) — N files: [scope].
- **Wave 2** (planned) — N files: [scope].
...

## Open questions / deferred

- [Files considered but not yet scheduled.]
- [Split-or-merge questions that will be resolved during authoring.]

## Conventions

- Each reference file starts with YAML frontmatter: `date`, `coverage` tier (foundational/expanded/deep), `peers`, `primary_sources`.
- Every factual claim cites a source at the file level. Speculation is labeled.
- Product-reference profiles document observable public patterns only — no speculative internals.
- Dates use ISO format ([today]).
```

## Writing order at v0.1.0

1. **Scoping survey agent** (separate step, see `../methodology/scoping-survey.md`).
2. **Draft INDEX.md** from scoping output — this becomes the source of truth.
3. **Draft SKILL.md** with cheat sheets derived from axes and exemplars.
4. **Draft skill.json** with tags from axes + canonical exemplars.
5. **Seed CHANGELOG.md v0.1.0** with scoping findings.

All four files written before Wave 1 dispatches.

## Validation checklist before Wave 1

- [ ] Every file path in SKILL.md routing table resolves to an entry in INDEX.md.
- [ ] Every file in INDEX.md has a ⬜ or ✅ marker.
- [ ] skill.json `files[]` matches INDEX.md (both refer to the same set plus SKILL.md + CHANGELOG.md + INDEX.md itself).
- [ ] skill.json `name` matches directory name and SKILL.md frontmatter `name`.
- [ ] skill.json description under 1024 characters.
- [ ] CHANGELOG.md has a v0.1.0 entry.
- [ ] No hardcoded absolute paths anywhere.

## After each wave

See `../agent-dispatch/bookkeeping-protocol.md` for the post-wave update to these four files.
