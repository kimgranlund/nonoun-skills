---
date: 2026-05-06
---

# Canonical layout reference

The full per-folder rationale for `apps/<name>/`. Read when confirming what each
folder is for, when an unusual app structure pushes back on the convention, or
when explaining the layout to a future reader.

## Source of truth

The decision is ratified in **ADR-0020** (chat-ui repo,
`.brain/adrs/0020-apps-and-component-demo-co-location.md`), specifically the
**2026-05-06 amendment**. Every claim in this reference file traces to that ADR.

## The full canonical structure

```
apps/<name>/
├── README.md                     ← entry, reading order, run instructions
├── PATTERNS.md                   ← non-obvious patterns ledger (optional)
├── CHANGELOG.md                  ← per-app changelog (optional, recommended)
│
├── skills/                       (Agent Skills v1 compliant skill bundles — REAL contract)
│   └── <name>-expert/
│       ├── SKILL.md              ← name + description (≤1024 chars) + body
│       ├── references/           ← extended reference docs
│       └── assets/               ← images, schemas, fixtures the skill cites
│
├── agents/                       (sub-agent definitions — markdown w/ frontmatter; convention)
├── commands/                     (slash commands — .md files; convention)
├── hooks/                        (lifecycle hooks — event JSON + handler scripts; convention)
├── monitors/                     (watchdog monitors — cron/event-driven; convention)
├── assets/                       (shared media — convention)
│   ├── screenshots/              ← visual smokes, dogfood-sweep artifacts
│   └── fixtures/                 ← test fixtures, seed data examples
├── bin/                          (executable scripts — convention)
│
├── spec/                         (AUGMENTATION — design axis)
│   ├── BRIEF.md                  ← PRD-NN-BRIEF, 3-page front-door
│   ├── ARCHITECTURE.md           ← PRD-NN-ARCH, decision defenses
│   ├── SPEC.md                   ← PRD-NN-SPEC, full implementation spec
│   ├── PRD.md                    ← schema-validated, only when plan-prd invoked
│   └── ARCHITECTURE-REVIEW.md    ← post-build review (optional)
│
├── plan/                         (AUGMENTATION — execution axis)
│   ├── ROADMAP.md                ← Now / Next / Later / Done
│   ├── MILESTONES.md             ← dated v1.0 / v1.1 / v2 scope cuts
│   └── PLAN.md                   ← current active cut (initially "no active initiative")
│
└── app/                          (AUGMENTATION — runnable source)
    ├── index.html                ← entry; per app-page-trio convention if applicable
    ├── *.html                    ← per-page shells
    ├── *.contents.html           ← per-page fragments (app-page-trio)
    ├── *.contents.js             ← per-page controllers (app-page-trio)
    ├── *.css                     ← page-shell styles
    └── (project-specific subtree)
```

## Per-folder rationale

### `skills/<name>-expert/` — the only real external contract

This is the only subtree that follows a published external contract: the
[Agent Skills v1 spec](https://agentskills.io/home). SKILL.md frontmatter is
required (`name` 1-64 chars, `description` ≤1024 chars). Optional fields:
`license`, `compatibility`, `metadata`, `allowed-tools`.

**Naming**: `<app-name>-expert` (e.g. `tasks-expert`, `chat-canvas-expert`).
The `-expert` suffix mirrors `meta-expert-author`'s convention.

**Mode**: scaffold the SKILL.md as a stub, then chain to `meta-expert-author`
to fill it in. That skill writes the references/ tree and skill.json under
this directory.

**Project-scoped vs global**: this skill lives **inside** the app, not in
`~/.claude/skills/`. It is intentionally opinionated toward this app's
architecture. The trade-off: it isn't auto-discovered by Claude Code's skill
loader; consumers reference it explicitly via `/plan-spec` or
`/arch-system`.

### `agents/` — convention; create on demand

Plugin spec defines this folder as the home for sub-agent definitions
(markdown files with frontmatter). Apps may not need any sub-agents at all.

**Don't pre-create.** If the user signals they want a sub-agent (e.g.,
"this app needs a `task-card-author` sub-agent"), create the folder + a
seed agent file at that point.

### `commands/` — convention; create on demand

Plugin spec defines this folder for slash commands. Apps may not need any
slash commands beyond what the host harness provides.

**Don't pre-create.** If the user signals "this app should ship `/<name>-demo-reset`",
create the folder + the `.md` file at that point.

### `hooks/` — convention; create on demand

Plugin spec defines this folder for lifecycle hooks (pre-commit, pre-render, etc.).
Useful when the app needs to enforce its own invariants beyond what the repo's
top-level hooks cover.

**Don't pre-create.** Most apps don't need bespoke hooks.

### `monitors/` — convention; create on demand

Plugin spec defines this folder for watchdog monitors (cron-driven, event-driven).
Rare for reference apps.

**Don't pre-create.**

### `assets/` — pre-create `assets/screenshots/`

This is where shared media lives — screenshots, fixtures, schemas, fonts, etc.
**Always pre-create `assets/screenshots/`** because visual smoke output is
universal: every app benefits from a Playwright-driven screenshot harness, and
having the folder ready avoids the "screenshots/ at root" antipattern (the very
thing the 2026-05-06 amendment fixes for `apps/tasks/`).

Other subfolders under `assets/` (`fixtures/`, `data/`, `fonts/`) are created
on demand.

### `bin/` — convention; create on demand

Plugin spec defines this folder for executable scripts. If the app has its own
CLI tools or one-off scripts, they live here. Otherwise skip.

### `spec/` — pre-create with seed BRIEF / ARCHITECTURE / SPEC

The design axis: PRD, BRIEF, ARCHITECTURE, SPEC. Doc IDs use the `PRD-NN-`
prefix already used in `apps/tasks/spec/PRD-01-BRIEF.md` etc.

**Why seed three docs (not one)**: each answers a different question:
- **BRIEF.md** — the 3-page elevator pitch. Read by anyone wanting context fast.
- **ARCHITECTURE.md** — decision defenses. Read by reviewers and future maintainers.
- **SPEC.md** — the full implementation contract. Read by the implementer.

These can converge into one doc (`PRD.md`) if the app is small or if `plan-prd`
is being used for schema-validated PRD output. Default: keep them separate.

**ARCHITECTURE-REVIEW.md** is a post-build artifact — independent type-driven
review of the spec set. Created when an architecture review is run (often via
`arch-system`); not pre-seeded.

### `plan/` — pre-create with seed ROADMAP / MILESTONES / PLAN

The execution axis. Mirrors the repo-wide `docs/ROADMAP.md` + `docs/PLAN.md`
shape, scoped to one app.

- **ROADMAP.md** — multi-horizon: Now / Next / Later / Done. The source of
  truth for "what's the long-term picture for this app?"
- **MILESTONES.md** — dated cut log: v1.0.0, v1.1.0, v2.0.0 with explicit
  scope cuts and out-of-scope items.
- **PLAN.md** — current active cut. Initially "no active initiative —
  promote a v1.0 candidate from ROADMAP `## Next` to start work."

**Common mistake**: filing MILESTONES under `spec/`. It's tempting because
"milestones reference architecture decisions" — but the question MILESTONES
answers (what's done by when?) is execution, not design. Resist.

### `app/` — pre-create empty (or seed per stack)

**Standalone shape** (single set of top-level files):

```
app/
├── <name>.html              ← shell
├── <name>.contents.html     ← fragment
└── <name>.contents.js       ← controller (page-trio per ADR-0021)
```

**Rollup shape** (multiple sub-experiences under sub-directories):

```
app/
├── <sub-1>/
│   ├── <sub-1>.html
│   ├── <sub-1>.contents.html
│   └── <sub-1>.contents.js   ← optional; omit for declarative pages
├── <sub-2>/
│   └── ...
└── <sub-3>/
    └── ...
```

Rollup mode shares ONE foundation (one README, one PATTERNS, one CHANGELOG,
one skill, one spec set, one plan set) covering N sub-pages. Each sub-page
has its own `<sub>.html` + `<sub>.contents.html`; controllers
(`<sub>.contents.js`) are optional — purely declarative pages skip them
(page-DUO instead of page-TRIO). Examples in the chat-ui repo:
- `apps/errors/` — 3 sub-pages (404 / 500 / maintenance), all declarative
- `apps/genui/` — 7 playgrounds, mixed declarative + controller
- `apps/saas/` — multiple admin sub-experiences
- `apps/user-flow/` — auth + registration + onboarding sub-flows

The SPEC for a rollup includes per-sub-page tables (one row per sub-page
× per-surface column) rather than re-explaining the shared chrome N times.

**Fragments-only / corpus-source shape** (sub-directories with ONLY a
fragment, no shells, no controllers):

```
app/
├── <sub-1>/
│   └── <sub-1>.contents.html    ← chunk-marker fragment ONLY
├── <sub-2>/
│   └── <sub-2>.contents.html
└── <sub-3>/
    └── <sub-3>.contents.html
```

Used when the rollup's value is **input to a content/training pipeline**,
not runnable demos. Each fragment carries chunk markers
(`<article data-chunk="X" data-chunk-kind="page">` with
`<section data-chunk-slot="...">` children), and a tool harvests them
into JSON or some other captured artifact.

Properties of this shape:
- No `<sub>.html` shells, no `<sub>.contents.js` controllers, no CSS files
- Inline `style="..."` may be intentionally permitted (preserves layout
  intent as training signal) — verify against the project's exemplar-
  style ban
- Captured artifacts live under `packages/<consumer>/...`; the
  `apps/<name>/` tree is the editable source-of-truth
- The pipeline's `captured_at` timestamp is the staleness signal —
  re-running extraction is manual / opt-in
- "Run the demo" is N/A; previewing requires injecting the fragment
  into another shell

Example in the chat-ui repo:
- `apps/generic-shells/` — 5 page-shaped chunks (editor, error, form,
  marketing, settings) feeding the gen-UI compose-from-chunks engine.
  Captured to `packages/a2ui/corpus/chunks/<name>-page-shell.json`.

The SPEC for a fragments-only rollup describes (a) the per-fragment
contract (slots, primary tag, components used), (b) the captured-
artifact JSON shape, (c) the chunk-marker contract, (d) the capture
lifecycle (one-way: fragment → tool → artifact).

**Mixed-shape rollup** (some sub-pages page-DUO, some fragments-only):

```
app/
├── <sub-1>/
│   ├── <sub-1>.html              ← page-DUO (with shell)
│   └── <sub-1>.contents.html
├── <sub-2>/
│   ├── <sub-2>.html              ← page-DUO (with shell)
│   └── <sub-2>.contents.html
└── <sub-3>/
    └── <sub-3>.contents.html      ← fragments-only (no shell)
```

A rollup can mix shapes per sub-page when the constituent patterns
have different runnability needs. Common case: most sub-pages stand
alone (ship a shell) but some are designed for embedding in a parent
flex container (no shell because a shell would force a wrapper that
distorts the use case).

Properties of mixed-shape rollups:
- Each sub-page declares its own shape; no rollup-level uniformity
  required
- Tooling that assumes uniform shape (e.g. visual-smokes that hit
  every shell URL) needs a shape-per-sub-page lookup, not a
  rollup-level rule
- Inline `style="..."` is permitted on the fragments-only sub-pages
  (per fragments-only rules); page-DUO sub-pages keep the project's
  default no-inline-style convention

Example in the chat-ui repo:
- `apps/patterns/` — 11 page-DUO patterns + 2 fragments-only patterns
  (editor-code-pane, editor-preview-pane) in one rollup. The 2
  fragments-only patterns are designed for embedding in a parent
  shell (e.g. the editor-page archetype from generic-shells).



The runnable source tree. Stack-agnostic. Could be:
- Static HTML/JS (chat-ui's `apps/tasks/` style — uses app-page-trio convention)
- React + Vite
- Next.js
- Plain Node script
- Anything else

**Don't speculate the stack.** Leave `app/` empty unless the user explicitly says
"web-components" / "React" / etc. If they do, seed `app/index.html` with a
minimal shell pointing at the chosen stack's conventions.

For chat-ui's app-page-trio convention specifically: see
[ADR-0021](https://github.com/adiahealth/gen-ui-kit/blob/main/.brain/adrs/0021-app-page-trio.md).

## What's deliberately NOT in the canonical structure

These folders/files exist in the Claude Code plugin spec but are **not** part
of an `apps/<name>/` foundation by default:

- **`.claude-plugin/plugin.json`** — declares plugin status. Apps are not
  plugins. Add only if the user explicitly asks to distribute this app as a
  Claude Code plugin.
- **`.mcp.json`** — declares MCP servers. Most apps don't ship MCP servers.
- **`.lsp.json`** — declares LSP servers. Claude Code-specific; Hermes/Pi
  don't honor it.
- **`settings.json`** — user-editable plugin defaults. Apps don't have
  plugin-shaped settings.

If an app later genuinely needs any of these, add them then — the layout
already accommodates them. **Don't pre-create them.**

## Repo-shape assumptions

This skill assumes the target repo has:

- A top-level `apps/` directory (or is willing to have one created).
- A `git` working tree (so file creations can be tracked).
- Optional but useful: `scripts/check-links.mjs` (chat-ui-style intra-repo
  link checker) for verifying seeded link references.

If the target repo deviates from these (e.g., uses `examples/` instead of
`apps/`, or `pkgs/` instead of `apps/`), confirm with the user before
proceeding. Don't auto-rename the convention; instead, either:
- Adapt the skill output to the repo's existing convention, OR
- Surface the friction and ask whether to introduce `apps/` as a new
  top-level directory.
