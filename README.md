# nonoun-skills

A home for **general-purpose Claude Code skills** — domain-agnostic authoring aids that aren't tied to any one plugin's job. Versioned, validated, and installable as a marketplace, kept separate from the product plugins (which live in [`claude-plugins`](https://github.com/kimgranlund/claude-plugins)) so the skills don't bloat a plugin's standing context or stretch its scope.

The marketplace `name` is `nonoun-skills`; the repo is `nonoun-skills`. Skills are distributed as cohesive **skill-bundle plugins** (a plugin that bundles only skills — no commands, agents, or MCP).

## Plugins

### `ui-decomposers` — read a visual artifact on two crossing axes

Two paired "decomposer" skills built on the same technique — **two independent axes that walk the same hierarchy in opposite directions**, scored separately so opposite defects don't average out:

| Skill | Technique | Carries |
| --- | --- | --- |
| **ui-layout-decomposer** | OUTSIDE-IN (macro→micro: frame → regions → cards → atoms) × INSIDE-OUT (core→whole: actions → bindings → feedback → coherence) | a gated rubric + a four-archetype ASCII-wireframe library (productivity-shell · saas-dashboard · marketing-site · mobile-app) |
| **ui-mermaid-decomposer** | INTENT (whole→atom: relationship → type → skeleton → labels) × RENDER (atom→whole: keyword → syntax → strict-safety → legibility) | a verbatim syntax catalog for the 11 advanced Mermaid types, a gated M1–M6 rubric, and a **mechanized render-check** (`bin/mermaid-render-check.py`) |

Each is a `DECOMPOSE` / `CREATE`(or DESIGN) / `GRADE` skill: read an artifact and grade it, design a new one, or score one against the rubric — gates before reviews, two axes reported separately.

## Install

```text
/plugin marketplace add kimgranlund/nonoun-skills
/plugin install ui-decomposers@nonoun-skills
```

…or for local development, point Claude Code at the skills directly (they're standard skill folders):

```sh
# symlink into your user skills (kept in sync with the repo)
ln -s "$PWD/ui-decomposers/skills/ui-layout-decomposer"  ~/.claude/skills/
ln -s "$PWD/ui-decomposers/skills/ui-mermaid-decomposer" ~/.claude/skills/
```

## Develop

Skills are markdown + (optionally) stdlib Python. The repo is **self-contained and clean-checkout-true** — one gate proves it:

```sh
python3 bin/check-skills.py                                   # validate every skill + run bin selftests + dogfood the render-check
python3 ui-decomposers/skills/ui-mermaid-decomposer/bin/mermaid-render-check.py selftest   # the static keyword gate
python3 ui-decomposers/skills/ui-mermaid-decomposer/bin/mermaid-render-check.py <file|dir> # check a doc's ```mermaid blocks (mmdc renders when installed)
```

`bin/check-skills.py` asserts, per skill: `skill.json` parses and its `name` matches the dir; the SKILL.md `description` is ≤ 1024 chars; every `files[]` path exists; relative `.md` links resolve; the SKILL.md carries `## Quick Start`, a `§SelfAudit`, and a `## Verify Target`. It then runs each skill's `bin/*.py selftest` and dogfoods the Mermaid render-check over the reference docs. CI (`.github/workflows/ci.yml`) runs it on every push/PR.

The full Mermaid **render** gate (`mmdc` actually rendering each block) fires only where the mermaid CLI is installed; CI installs it so the M3 render gate runs there, while the static keyword gate runs everywhere.

## Layout

```
nonoun-skills/
  .claude-plugin/marketplace.json      # the marketplace (one plugin: ui-decomposers)
  ui-decomposers/
    .claude-plugin/plugin.json
    skills/
      ui-layout-decomposer/            # SKILL.md · skill.json · CHANGELOG · ROADMAP · references/
      ui-mermaid-decomposer/           # … + bin/mermaid-render-check.py
  bin/check-skills.py                  # the self-contained CI gate
  .github/workflows/ci.yml
```

## Conventions

- **Skills are self-contained.** A skill names its `files[]` in `skill.json`, keeps SKILL.md a thin table-of-contents (≤ ~100 lines), and pushes depth into `references/` loaded on demand. Deterministic checks live in `bin/` (stdlib, selftested) — *computation routes to code, never to inference*.
- **The description is the routing surface** — ≤ 1024 chars, with WHAT + WHEN + NOT. A routing-eval corpus (scored trigger/adversarial phrases) is the next maturity step for each skill (tracked in its ROADMAP).
- Authored and red-teamed with **skills-studio** (the skill-lifecycle tool); these two were extracted from the dev-factory cockpit + the catalog corpus-reader's Mermaid work.
