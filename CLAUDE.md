# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

For the human-facing overview see [README.md](README.md); to author a new skill see [HOWTO.md](HOWTO.md); for the marketplace history see [CHANGELOG.md](CHANGELOG.md); for cross-cutting future work see [ROADMAP.md](ROADMAP.md) (per-skill roadmaps live in each `*/skills/<skill>/ROADMAP.md`).

## What this repo is

`nonoun-skills` is a **marketplace + home for general-purpose Claude Code skills** — domain-agnostic authoring aids kept separate from product plugins (which live in `nonoun-plugins`) so they don't bloat a plugin's standing context. Skills ship as **skill-bundle plugins**: a plugin that bundles *only* skills — no commands, agents, or MCP.

There is no application to run. The deliverable is the skill content itself; the repo's job is to keep it valid, self-contained, and installable. It currently holds **11 plugins / 37 skills**, and the spine through most of them is one technique: the **decomposer**.

## Layout & the chain

```
.claude-plugin/marketplace.json   # the marketplace — lists the 11 plugins
<plugin>/                         # design- · code- · data- · meta- · reasoning- · ops- · general- · knowledge- · manager- · skills- · plugins-skills
  .claude-plugin/plugin.json      #   plugin manifest (version lives here)
  skills/<skill>/                 #   each SKILL is a self-contained folder
bin/check-skills.py               # the one repo-wide gate (stdlib only)
.github/workflows/ci.yml          # runs the gate on push/PR
```

`marketplace.json` → `<plugin>/.claude-plugin/plugin.json` → `skills/*/skill.json` is the chain. **There is no central skill registry** — `bin/check-skills.py` discovers any dir matching `*/skills/*/` that contains a `skill.json`, so adding a skill to an existing plugin is just creating the folder. To add a *plugin*, create its `plugin.json` **and** add an entry to `marketplace.json`. (The gate validates skills independently of plugin manifests, so a skill passes before its plugin entry exists — but ship both, and refresh the plugin/marketplace `description` when a plugin gains a skill.)

## The decomposer method (the dominant pattern)

Most skills here are **decomposers**. A decomposer grades an artifact on **two independent axes that walk the same hierarchy in opposite directions**:

- an **intent axis** (whole → part) — *"is it the right thing?"* — where an LLM is strong.
- a **mechanism axis** (part → whole) — *"does it actually work / hold / render, here?"* — where an LLM fails silently, so it is **routed to a deterministic, self-tested `bin/` gate** (*computation routes to code, never inference*).

The two **cross at one seam**, their defects are **opposite** (so the axes are **scored separately, never averaged** — the quadrant), the rubric is **gated** (gate checks cascade and block the finer reviews), and where the dangerous axis can't be deterministically gated the method **adversarially verifies** it in a fresh context. Every decomposer runs three modes: **DECOMPOSE** / **CREATE-DESIGN** / **GRADE**. The 11 axis pairs (OUTSIDE-IN×INSIDE-OUT, SPEC×EXECUTION, MODEL×VALIDITY, …) are in the README table; the authoring recipe is in HOWTO.md.

**Canonical polarity + two planes (repo-wide, see HOWTO.md §1).** When a skill names its axes directionally, **OUTSIDE-IN = the intent axis** (whole→part, the goals / "what's good") and **INSIDE-OUT = the mechanism axis** (part→whole, the technical foundations) — never inverted (`layout-` and `brand-decomposer` follow this; `brand` carries a terminology note because its source corpus uses the words for reasoning-directions, the opposite polarity). Plan and review on **two planes in parallel**: OUTSIDE-IN (goals · -ilities · rubric) × INSIDE-OUT (SoC · DI · CLEAN · DDD · FP); they are orthogonal to intent/mechanism and form a 2×2 whose mechanizable cells route to `bin/`. The worked INSIDE-OUT canon (DDD bounded contexts, hexagonal/ports-and-adapters, CLEAN/Onion, Conway + inverse-Conway, connascence, fitness functions, SOLID, SoC/Parnas, ADRs/C4) lives in `architecture-decomposer`'s `references/architecture-knowledge.md`.

## Three skill vintages (this is the non-obvious part)

Skills here deliberately follow **three templates**, all valid — the gate enforces the hard contract on every skill equally and only **advises** on the skills-studio structural floor, so **don't "fix" a reference skill by bolting on `## Quick Start`**:

- **Decomposers** (the spine: `layout-/mermaid-/component-decomposer`, `code-/regex-/query-/type-decomposer`, `extraction-/routing-/proof-/config-decomposer`) — skills-studio template: `## Quick Start` · `§SelfAudit` · `## Verify Target`, two crossing axes, a gated rubric, a `bin/` mechanism gate.
- **Reference skills** (`color-science`, `typography-lettering`) — `## Invocation` + domain sections + a tiered `references/` corpus loaded on demand. They *answer and point at a peer for output*; they don't generate.
- **Domain build skill** (`figma-plugins`) — teaches how to build something specific, with its own `bin/` check; SKILL.md + references + bin shape, but not a two-axis grader.

## The contract every skill must satisfy (gate FAILs)

- `skill.json` parses and its `name` **exactly matches the directory name**
- `SKILL.md` has a frontmatter `description` ≤ **1024 chars** (the routing surface — write WHAT + WHEN + NOT, with quoted triggers and a `NOT for …` fence)
- every path in `skill.json` `files[]` **exists on disk** (and nothing on disk that should be listed is missing)
- relative `.md` links *inside the skill dir* resolve (a link escaping the dir is a cross-skill ref → WARN, not FAIL)
- each `bin/*.py` responds to a `selftest` subcommand and exits 0
- the Mermaid render-check, dogfooded over every skill's `references/`, passes its static keyword gate (so don't put a malformed ```mermaid block in any reference doc)
- the gate also **dogfoods `routing-eval` over every skill's `*.corpus.json`** and surfaces sibling-routing collisions as **advisory** WARNs (never a FAIL — the lexical-overlap proxy is an aid, not an oracle). A *new* collision warning after a description edit means you re-introduced sibling overlap; sharpen the `NOT for …` fence (see `routing-decomposer`)

Core principle: **skills are self-contained and computation routes to code, never to inference.** Deterministic checks live in a skill's `bin/` as selftested stdlib Python; `SKILL.md` stays a table-of-contents over `references/`.

## Gotchas to internalize (learned the hard way)

- **A mechanism gate is a lossy PRE-FILTER, not an oracle.** A clean run of a static linter (ReDoS smell, SQL smells, secret detection, groundedness) does **not** prove the artifact safe — these skills document their gate's limits on purpose. Don't reintroduce "trust the tool, a clean run = proof" overclaims; the honest framing is "necessary, not sufficient; confirm the dangerous case adversarially."
- **A green `selftest` is necessary, not sufficient.** Selftests must carry good **and** bad fixtures. An adversarial review found one-fixture-deep selftests hiding false-negatives in *every* new tool (a ReDoS bomb reported "clean", an invented value "grounded", `true` accepted for an int enum). When you touch a `bin/` tool, **add the adversarial input as a fixture** so the fix can't regress.
- **A harness bin treats a missing tool as no evidence.** `execution-harness` / `query-harness` / `config-harness` report a skipped *gate* (tool absent) as **INCOMPLETE / exit 3** — never a PASS. Preserve that; automation keys on the exit code.

## Commands

```sh
# The one gate — validate every skill, run all bin selftests, dogfood the render-check.
# A fresh clone proves itself with this alone (no external tooling). Currently: 37 skills, 26 selftests.
python3 bin/check-skills.py

# Any single bin tool exposes its self-test:
python3 <plugin>/skills/<skill>/bin/<tool>.py selftest

# mermaid-decomposer's render-check directly:
python3 design-skills/skills/mermaid-decomposer/bin/mermaid-render-check.py <file|dir>   # check a doc's ```mermaid blocks
```

The static keyword gate runs everywhere (stdlib only). The full Mermaid **render** gate (actual `mmdc` rendering) only fires where the mermaid CLI is installed; CI installs it but keeps that step **advisory** (`continue-on-error`) because the CLI's bundled mermaid version can drift from the 11.15.0 the reference targets.

`color-science` is the only skill with a build step (its `examples/` showcase dogfoods `src/`, the TS color library). The bundle is committed, so no build is needed for normal work; see `design-skills/skills/color-science/CLAUDE.md` for that skill's own notes.

## When editing

- Changing a skill's behavior surface means editing `SKILL.md`; changing *when it triggers* means editing the frontmatter `description` (and ideally the routing-eval corpus the ROADMAP tracks — `routing-decomposer` is the skill that grades this).
- Keep `skill.json` `files[]` in sync with disk — a stray or missing file FAILs the gate.
- After any change, run `python3 bin/check-skills.py` before committing. Update the skill's own `CHANGELOG.md`; update the root `CHANGELOG.md` for marketplace-level changes (a new skill/plugin, a cross-cutting fix).
- PDFs are gitignored (color-science archives ~236MB); reference files preserve archive.org source links instead.
