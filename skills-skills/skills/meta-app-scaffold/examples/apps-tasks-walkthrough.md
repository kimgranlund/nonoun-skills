# Worked example — `apps/tasks/`

The canonical example: `apps/tasks/` in chat-ui, scaffolded across three commits
on 2026-05-06 (`e9dc7d17` + `b7cec8aa` + `51e767ee`). This walkthrough shows
what `/meta-app-scaffold` would have produced if it had existed at the time.

## Original ask

> "Author a PRD for the **Tasks UI playground** at `apps/tasks/`. Research basis:
> `apps/tasks/skills/tasks-expert/` (v1.0.0, 68 reference files, 50,741 lines
> across 12 axes — Kanban / Gantt / List views; drag-drop; data schemas; state
> architecture; controller-and-service; sync engines; realtime collab;
> accessibility; creation/filters/views; foundations)."

This was a *post-hoc* foundation request — the skill bundle and runnable
implementation already existed when the spec work began. In a greenfield case,
`/meta-app-scaffold` would run before any of the chained skills.

## Greenfield walkthrough

### Step 1 — User invokes the skill

> "I want to scaffold a new reference app for a Tasks UI playground. Kanban
> default view, Gantt and List as alternates, drag-and-drop, schema-JSON
> document, in-memory only for v1. Build it like the existing reference apps."

### Step 2 — Skill confirms scope

This skill responds:

> "Scope check before I scaffold:
>
> 1. **App name**: `tasks` (kebab-case under `apps/`)
> 2. **One-line purpose**: "Reference app demonstrating task-management UI
>    patterns — Kanban, Gantt, List views with drag/drop and schema-JSON
>    document as source of truth"
> 3. **Repo**: `~/Projects/chat-ui` (auto-detected from cwd)
> 4. **Skill mode**: capability (default; broad reference coverage)
> 5. **Sibling apps to mirror**: none yet (this would be the first)
>
> Confirm? Or override any of (1)/(2)/(4)?"

User confirms.

### Step 3 — Pre-conditions

```bash
test -d apps                             # ✓ exists
test ! -e apps/tasks                     # ✓ doesn't exist
ls ~/.claude/skills/{meta-expert-author,plan-spec,plan-prd,meta-skill}/SKILL.md  # or ~/.agents/skills/...
                                         # ✓ all four sibling skills present
```

### Step 4 — Folder skeleton

```bash
mkdir -p apps/tasks/{skills/tasks-expert,assets/screenshots,spec,plan,app}
```

Result:

```
apps/tasks/
├── skills/tasks-expert/
├── assets/screenshots/
├── spec/
├── plan/
└── app/
```

### Step 5 — Seed each file

Per `references/templates.md`, write 10 files with the placeholders substituted:

- `<name>` → `tasks`
- `<Display Name>` → `Tasks UI Playground`
- `YYYY-MM-DD` → `2026-05-06`
- `<RELATIVE-ADR-PATH>` → `../../.brain/adrs/0020-apps-and-component-demo-co-location.md`
- `<one-line purpose>` → user-supplied

Files written:

```
apps/tasks/README.md                                   ← layout + reading order + run instructions
apps/tasks/PATTERNS.md                                 ← empty patterns ledger
apps/tasks/CHANGELOG.md                                ← Keep-a-Changelog header
apps/tasks/skills/tasks-expert/SKILL.md                ← stub frontmatter only
apps/tasks/spec/BRIEF.md                               ← PRD-01-BRIEF stub
apps/tasks/spec/ARCHITECTURE.md                        ← PRD-01-ARCH stub
apps/tasks/spec/SPEC.md                                ← PRD-01-SPEC stub
apps/tasks/plan/ROADMAP.md                             ← Now/Next/Later/Done
apps/tasks/plan/MILESTONES.md                          ← v1/v1.1/v2 placeholders
apps/tasks/plan/PLAN.md                                ← "no active initiative"
```

### Step 6 — Propose the chain

> ```
> ✅ Scaffolded apps/tasks/
>
> Folders created:
>   apps/tasks/{skills/tasks-expert,assets/screenshots,spec,plan,app}
>
> Files seeded (10):
>   apps/tasks/README.md
>   apps/tasks/PATTERNS.md
>   apps/tasks/CHANGELOG.md
>   apps/tasks/skills/tasks-expert/SKILL.md
>   apps/tasks/spec/{BRIEF,ARCHITECTURE,SPEC}.md
>   apps/tasks/plan/{ROADMAP,MILESTONES,PLAN}.md
>
> Plugin manifest: not created (default).
> ADR alignment: ADR-0020 (2026-05-06 amendment).
>
> Proposed follow-ups:
>   1. /meta-expert-author --target apps/tasks/skills/tasks-expert/ --mode capability
>   2. /plan-spec --target apps/tasks/spec/ --research apps/tasks/skills/tasks-expert/
>   3. (optional) /meta-skill if the app needs sub-skills
>
> Suggested commit:
>   scaffold(apps): apps/tasks/ foundation per ADR-0020
>
> Want me to invoke (1) now?"
> ```

User says "yes — meta-expert-author next".

### Step 7 — Chain to `/meta-expert-author`

This skill exits; control passes to `/meta-expert-author` with the suggested
arguments. That skill's loop runs (typically 5 waves over hours/days, with
parallel agent dispatches) and fills in:

- `apps/tasks/skills/tasks-expert/SKILL.md` (replaces the stub with full content)
- `apps/tasks/skills/tasks-expert/references/{12 axes}/*.md` (~68 files, ~50K lines)
- `apps/tasks/skills/tasks-expert/CHANGELOG.md`
- `apps/tasks/skills/tasks-expert/skill.json`

### Step 8 — Chain to `/plan-spec`

Once `meta-expert-author` finishes Wave 1+ (or all 5 waves), invoke
`/plan-spec` to fill in the spec docs:

- `apps/tasks/spec/BRIEF.md` (PRD-01-BRIEF, 3-page front-door)
- `apps/tasks/spec/ARCHITECTURE.md` (PRD-01-ARCH, decision defenses)
- `apps/tasks/spec/SPEC.md` (PRD-01-SPEC, full implementation contract)

The seeds are replaced with substantive content drawn from the expert skill's
research-survey basis.

### Step 9 — Implementation begins

User picks the stack — for this app, vanilla web components + AdiaUI primitives
+ signal()-based reactivity + Traits-based DnD. The implementer fills `app/`:

- `app/index.html` (entry shell)
- `app/tasks-playground.js` (boot)
- `app/tasks.css`
- `app/seed-data.js`
- `app/components/` (playground-local custom elements)
- `app/controller/` + `app/service/`
- `app/visual-test.mjs` (Playwright smoke)

`apps/tasks/plan/PLAN.md` activates with the v1.0 initiative; ROADMAP.md
populates Now/Next/Later/Done; MILESTONES.md grows as cuts ship.

### Step 10 — Post-build polish

When v1.0 ships:

- `apps/tasks/spec/ARCHITECTURE-REVIEW.md` is authored as an independent
  type-driven review (often via `/arch-system`).
- `apps/tasks/PATTERNS.md` accumulates non-obvious patterns surfaced during the
  build.
- `apps/tasks/assets/screenshots/` fills with visual smoke output.
- `apps/tasks/plan/PLAN.md` resets to "no active initiative" and v1.0 promotes
  into MILESTONES.md.

This is the steady-state shape captured in the actual `apps/tasks/` after the
2026-05-06 cleanup.

## Comparison to the actual 2026-05-06 work

The actual 2026-05-06 work was three commits:

1. `e9dc7d17` — initial migration: established the layout, included a
   `.claude-plugin/plugin.json` manifest (later removed).
2. `b7cec8aa` — recorded the rename-source deletes for screenshots/.
3. `51e767ee` — reframed: dropped the manifest, clarified "borrow not claim",
   added the Follow-ups section to ADR-0020.

`/meta-app-scaffold` codifies the **post-51e767ee** state — borrow the
plugin layout as a convention, no manifest by default, opt-in for distribution.

Future apps invoking this skill skip the reframing detour and land at the
correct layout immediately.

## What this walkthrough demonstrates

- **The skill scaffolds, the chain authors.** This skill writes 10 small
  template files; `/meta-expert-author` writes 68 reference files of
  research-backed content. Different jobs, different skills.
- **Composition, not consolidation.** Tempting to roll all the authoring into
  one mega-skill — but each chained skill has its own user-loop semantics
  (waves, research-survey protocol, validation passes). Keeping them separate keeps
  each one tractable.
- **Seeds reference the chain.** Each scaffolded file points at the skill that
  fills it in, so a future reader who finds a stub knows what to do next.
