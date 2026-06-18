---
date: 2026-05-06
---

# File seed templates

Minimal seed content for each scaffolded file. Read in Step 4 of the SKILL.md
workflow. Each template:

- Fits on one screen.
- References ADR-0020 (where the convention lives).
- Points downstream readers to the sibling skill that fills it in substantively.
- Uses the `<name>` placeholder consistently — replace at scaffold time.

## `apps/<name>/README.md`

```markdown
# <Display Name>

<one-line purpose statement from user>

Status: **scaffolded** — see `./plan/ROADMAP.md` for the
multi-horizon plan and `./spec/SPEC.md` for the implementation
contract (both currently seed-only; populate via `/plan-spec` and
`/meta-expert-author`).

## Layout

This app borrows the [Claude Code plugin folder convention](https://docs.claude.com/en/docs/claude-code/plugin-reference)
as a structural shape (skills/, assets/, etc.) plus two project-specific
augmentations: `spec/` (design axis) and `plan/` (execution axis). The app is
**not a Claude Code plugin** — there is no `.claude-plugin/plugin.json` manifest.
Full rationale in [ADR-0020 (2026-05-06 amendment)](<RELATIVE-ADR-PATH>).

```
apps/<name>/
├── README.md                       ← you are here
├── PATTERNS.md                     ← non-obvious patterns ledger
├── CHANGELOG.md                    ← per-app changelog
│
├── skills/                         (Agent Skills v1 compliant)
│   └── <name>-expert/              ← project-scoped expert (research-survey basis)
│
├── assets/                         (shared media)
│   └── screenshots/                ← visual smokes
│
├── spec/                           (design axis)
│   ├── BRIEF.md                    ← PRD-01-BRIEF
│   ├── ARCHITECTURE.md             ← PRD-01-ARCH
│   └── SPEC.md                     ← PRD-01-SPEC
│
├── plan/                           (execution axis)
│   ├── ROADMAP.md                  ← Now / Next / Later / Done
│   ├── MILESTONES.md               ← v1 / v1.1 / v2 scope cuts
│   └── PLAN.md                     ← current active cut
│
└── app/                            (runnable implementation)
```

## Reading order

For product context:
1. `./spec/BRIEF.md` — 3-page elevator pitch.
2. `./spec/ARCHITECTURE.md` — decision rationale.
3. `./spec/SPEC.md` — implementation detail.

For status / what's next:
1. `./plan/ROADMAP.md` — multi-horizon view.
2. `./plan/MILESTONES.md` — dated scope cuts.

For research-survey basis:
1. `./skills/<name>-expert/SKILL.md`.

## Skill discoverability

The [`<name>-expert`](./skills/<name>-expert/) skill is project-scoped (lives
inside this app, not in `~/.claude/skills/`) and opinionated toward this app's
architecture. Reference it explicitly from `/plan-spec` or
`/arch-system` when authoring docs about this app.

## Running the app

(populate when `app/` source is authored)

## Authoring discipline

- Foundation scaffolded by `/meta-app-scaffold`.
- Skill authored via `/meta-expert-author` (capability mode).
- Spec authored via `/plan-spec` against the research-survey basis.
- Every reference file is dated, coverage-tiered, and cites primary sources.
- No fabricated bug IDs / RFC numbers / commit SHAs.
```

## `apps/<name>/PATTERNS.md`

```markdown
# <Display Name> — Patterns

Non-obvious patterns surfaced during the build of this app. Each entry should
answer "what would surprise a reader who hadn't built this?"

This ledger is initially empty — entries are added as the app is implemented.

## Cross-references

- **`spec/SPEC.md`** — the full type-driven contract this app was authored against
- **`spec/ARCHITECTURE.md`** — boundary contract sketches
- **`plan/MILESTONES.md`** — what's in v1 / v1.1 / v2 + decision rationale
- **`plan/ROADMAP.md`** — multi-horizon (Now / Next / Later / Done) view
```

## `apps/<name>/CHANGELOG.md`

```markdown
# Changelog

All notable changes to this app are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this app adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- Foundation scaffolded via `/meta-app-scaffold` per ADR-0020.

## [0.1.0] - YYYY-MM-DD

- Initial scaffold.
```

## `apps/<name>/skills/<name>-expert/SKILL.md`

```markdown
---
name: <name>-expert
description: >
  Project-scoped expert knowledge for the <Display Name> app at `apps/<name>/`.
  Use when designing, specifying, or implementing this app's features or
  architecture. Stub created by `/meta-app-scaffold`; substantive content
  to be authored via `/meta-expert-author` (capability mode by default).
metadata:
  status: stub
  scope: project-local
  project_root: apps/<name>
  authored_via: /meta-app-scaffold
  next_step: /meta-expert-author --target apps/<name>/skills/<name>-expert/
---

# <name>-expert

**Status: STUB.** This SKILL.md was scaffolded by `/meta-app-scaffold`.
Substantive content (references/, cheat sheets, task→reference routing) will be
authored by `/meta-expert-author`.

To populate this skill:

```
/meta-expert-author --target apps/<name>/skills/<name>-expert/ --mode capability
```

Until that runs, this skill is a placeholder. Don't reference it from the spec
docs as if it carries content — it doesn't yet.
```

## `apps/<name>/spec/BRIEF.md`

```markdown
# <Display Name> — Brief

**Document:** PRD-01-BRIEF
**Version:** 0.1.0
**Date:** YYYY-MM-DD
**Status:** Stub — to be authored by `/plan-spec`
**Audience:** Product, engineering, design

---

## How to Read This Document

This brief will be the 3-page front-door once authored. Until then, see
`./ARCHITECTURE.md` for decision defenses and
`./SPEC.md` for the implementation contract. For execution-axis
context, see `../plan/ROADMAP.md` and
`../plan/MILESTONES.md`. Research basis at
[`../skills/<name>-expert/`](../skills/<name>-expert/).

Sections marked 📐 are spec detail; 💡 are reasoning; ⚠️ are open decisions.

---

## 1. What This Is

(one sentence — what the app does)

## 2. Why It Exists

(the problem this app solves; tie to user need)

## 3. First Principles

(2-4 engineering principles; populate via /plan-spec)

## 4. Core Architecture

(diagram or paragraph; populate via /plan-spec)

## 5. Open Decisions

(track unresolved questions with options + tradeoffs)

---

**Authoring next step**: `/plan-spec` against the research-survey basis at
`../skills/<name>-expert/`.
```

## `apps/<name>/spec/ARCHITECTURE.md`

```markdown
# <Display Name> — Architecture

**Document:** PRD-01-ARCH
**Version:** 0.1.0
**Date:** YYYY-MM-DD
**Status:** Stub — to be authored by `/plan-spec`

---

This document defends each architectural choice. Until authored, the
architecture is undecided.

For the 3-page summary, see `./BRIEF.md`. For implementation detail,
see `./SPEC.md`. For version-by-version scope, see
`../plan/MILESTONES.md`.

## Sections (to be populated)

- Boundaries
- Type architecture
- Domain primitives
- Boundary contracts
- State machines
- Composition patterns

**Next document**: `./SPEC.md` — full implementation contract.
```

## `apps/<name>/spec/SPEC.md`

```markdown
# <Display Name> — Specification

**Document:** PRD-01-SPEC
**Version:** 0.1.0
**Date:** YYYY-MM-DD
**Status:** Stub — to be authored by `/plan-spec`

---

The full implementation contract for this app. Until authored, the
specification is undefined.

For orientation, see `./BRIEF.md`. For decision defenses, see
`./ARCHITECTURE.md`. For scope by version, see
`../plan/MILESTONES.md`. The research-survey basis is at
[`../skills/<name>-expert/`](../skills/<name>-expert/).

## Layout

```
apps/<name>/
├── README.md
├── skills/<name>-expert/
├── spec/  (design axis)
├── plan/  (execution axis)
└── app/   (runnable implementation)
```

## Sections (to be populated)

- R1. Component contracts
- R2. State architecture
- R3. Service / controller / command boundaries
- R4. Data schema
- R5. Accessibility model
- R6. Persistence
- R7. Open issues

---

**Authoring next step**: `/plan-spec --target apps/<name>/spec/` against the
research-survey basis at `../skills/<name>-expert/`.
```

## `apps/<name>/plan/ROADMAP.md`

```markdown
# <Display Name> — Roadmap

**Document:** plan-roadmap
**Updated:** YYYY-MM-DD
**Audience:** Implementers, future agents

This roadmap is the multi-horizon view. For dated scope cuts, see
`./MILESTONES.md`. For the active cut's plan, see
`./PLAN.md`. For design-axis docs, see [`../spec/`](../spec/).

---

## Now (in flight)

_No active initiative._

## Next (queued)

_(populate as v1.0 work surfaces)_

## Later (deferred)

_(populate as longer-horizon ideas surface)_

## Done

_(populate as cuts ship)_

---

## Relationship to repo-wide ROADMAP

If this monorepo has a `docs/ROADMAP.md`, it should carry a 1-line summary of
this app's status. This per-app roadmap is the source of truth.
```

## `apps/<name>/plan/MILESTONES.md`

```markdown
# <Display Name> — Milestones

**Document:** PRD-01-MS
**Version:** 0.1.0
**Date:** YYYY-MM-DD
**Status:** Stub — to be populated as scope is committed

---

## How to Read This Document

Each milestone has a target outcome, a feature list, and a definition of done.
Out-of-scope items are listed last and are not promises — they're documented
exclusions.

For the architectural rationale, see `../spec/ARCHITECTURE.md`.
For implementation detail, see `../spec/SPEC.md`.
For multi-horizon view, see `./ROADMAP.md`.

---

## Milestone Map

| Milestone | Target | Outcome |
|---|---|---|
| **v1.0.0** | First demonstrable cut | (populate) |
| **v1.1.0** | Polish + missing surfaces | (populate) |
| **v2.0.0** | (populate) | (populate) |

---

## v1.0.0 — (Title)

### Outcome

(what works at v1.0?)

### Definition of done

- [ ] (populate)
- [ ] (populate)

## v1.1.0 — (Title)

### Outcome

(what's added in v1.1?)

## v2.0.0 — (Title)

### Outcome

(what's the major-bump goal?)

---

## Out of scope

(items intentionally excluded; not promises)
```

## `apps/<name>/plan/PLAN.md`

```markdown
# <Display Name> — Active Plan

**Document:** plan-active
**Updated:** YYYY-MM-DD
**Audience:** Anyone working on this app today

---

## Status

**No active initiative.** Promote a v1.0 candidate from
`./ROADMAP.md` `## Next` to `## In flight` here when starting work.

---

## When to activate this plan

Promote a candidate from `./ROADMAP.md` by replacing this
section with:

```markdown
## <initiative title>

_Started: YYYY-MM-DD_
_Spec: ../spec/SPEC.md §<section>_

### Objective
<what + why>

### Work items
- [ ] item 1
- [ ] item 2

### Findings / decisions
<as work progresses>

### Next steps
<rolling action list>
```

---

## Archive policy

When an initiative ships, this PLAN gets reset to "no active initiative" and
the dated entry promotes into `./MILESTONES.md`. Older PLAN
content is captured in commit history — there is no separate plan archive
directory at app scope.
```

## Substitution rules

When materializing each template:

1. **Replace `<name>`** with the kebab-case app name (e.g., `tasks`,
   `chat-canvas`).
2. **Replace `<Display Name>`** with the user's preferred display name (often
   title-case of `<name>`, but the user may pick differently — e.g., `tasks` →
   "Tasks UI Playground").
3. **Replace `YYYY-MM-DD`** with today's date.
4. **Replace `<RELATIVE-ADR-PATH>`** in README with the relative path from
   `apps/<name>/README.md` to the ADR. For chat-ui this is
   `../../.brain/adrs/0020-apps-and-component-demo-co-location.md`. If the
   target repo doesn't have this ADR, drop the link entirely (don't fabricate).
5. **Replace `<one-line purpose statement>`** in README and BRIEF §1 with the
   user-provided purpose.

## What this skill does NOT seed

These files are intentionally NOT pre-created — they're either authored via
chained skills or surface organically:

- `apps/<name>/spec/PRD.md` — created by `/plan-prd` if invoked (schema-validated)
- `apps/<name>/spec/ARCHITECTURE-REVIEW.md` — created post-build by an
  independent reviewer (often `/arch-system`)
- `apps/<name>/skills/<name>-expert/references/*` — created by `/meta-expert-author`
- `apps/<name>/skills/<name>-expert/skill.json` — created by `/meta-expert-author`
- `apps/<name>/skills/<name>-expert/CHANGELOG.md` — created by `/meta-expert-author`
- `apps/<name>/app/*` — left to the implementer's stack choice
- `apps/<name>/agents/*`, `commands/*`, `hooks/*`, `monitors/*`, `bin/*` —
  created on demand when the app needs them
