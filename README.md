# nonoun-skills

A home for **general-purpose Claude Code skills** — domain-agnostic authoring aids that aren't tied to any one plugin's job. Versioned, validated, and installable as a marketplace, kept separate from the product plugins (which live in [`claude-plugins`](https://github.com/kimgranlund/claude-plugins)) so the skills don't bloat a plugin's standing context or stretch its scope.

The marketplace `name` is `nonoun-skills`; the repo is `nonoun-skills`. Skills are distributed as cohesive **skill-bundle plugins** (a plugin that bundles only skills — no commands, agents, or MCP).

## Plugins

### `design-skills` — design-domain skills

Four skills. Two are paired **"decomposers"** on the same technique (two independent axes that walk the same hierarchy in opposite directions, scored separately so opposite defects don't average out); two are deep **reference** skills (perceptual color, typography):

| Skill | What it does | Carries |
| --- | --- | --- |
| **layout-decomposer** | read / grade / design a UI on OUTSIDE-IN (frame → regions → cards → atoms) × INSIDE-OUT (actions → bindings → feedback → coherence) | a gated rubric + a four-archetype ASCII-wireframe library (productivity-shell · saas-dashboard · marketing-site · mobile-app) |
| **mermaid-decomposer** | create / grade advanced Mermaid diagrams on INTENT (relationship → type → skeleton → labels) × RENDER (keyword → syntax → strict-safety → legibility) | a verbatim 11-type syntax catalog, a gated M1–M6 rubric, and a **mechanized render-check** (`bin/mermaid-render-check.py`) |
| **color-science** | answer perceptual-color questions — spaces, gamut math, contrast/APCA, harmony, CVD, pigment mixing, color naming | a TypeScript color library (`src/`, 24 spaces) + 54 interactive `examples/` demos + a deep references corpus (historical · contemporary · techniques) |
| **typography-lettering** | answer typography questions — anatomy, classification, metrics, world scripts, accessibility, and the modern CSS text surface | a tiered references corpus by axis (history · classification · metrics · scripts · techniques · science) |

The two **decomposers** run `DECOMPOSE` / `CREATE` / `GRADE` — gates before reviews, two axes reported separately. The two **reference** skills *answer* (they explain and point at the right peer for output); they don't generate.

## Install

```text
/plugin marketplace add kimgranlund/nonoun-skills
/plugin install design-skills@nonoun-skills
```

…or for local development, point Claude Code at the skills directly (they're standard skill folders):

```sh
# symlink each into your user skills (kept in sync with the repo)
for s in design-skills/skills/*/; do ln -s "$PWD/$s" ~/.claude/skills/; done
```

## Develop

Skills are markdown + (optionally) stdlib Python. The repo is **self-contained and clean-checkout-true** — one gate proves it:

```sh
python3 bin/check-skills.py                                    # validate every skill + run bin selftests + dogfood the render-check
python3 design-skills/skills/mermaid-decomposer/bin/mermaid-render-check.py selftest    # the static keyword gate
python3 design-skills/skills/mermaid-decomposer/bin/mermaid-render-check.py <file|dir>  # check a doc's ```mermaid blocks (mmdc renders when installed)
```

`bin/check-skills.py` asserts, per skill (FAIL): `skill.json` parses and its `name` matches the dir; the SKILL.md `description` is ≤ 1024 chars; every `files[]` path exists; relative `.md` links resolve. It then runs each skill's `bin/*.py selftest` and dogfoods the Mermaid render-check over the reference docs. The skills-studio structural floor (`## Quick Start` · `§SelfAudit` · `## Verify Target`) is **advisory** (a WARN, not a FAIL) — the two `decomposer` skills carry it; the `ref-*`-derived reference skills use `## Invocation` + domain sections instead. CI (`.github/workflows/ci.yml`) runs the gate on every push/PR.

The full Mermaid **render** gate (`mmdc` actually rendering each block) fires only where the mermaid CLI is installed; CI installs it so the M3 render gate runs there, while the static keyword gate runs everywhere.

## Layout

```
nonoun-skills/
  .claude-plugin/marketplace.json      # the marketplace (one plugin: design-skills)
  design-skills/
    .claude-plugin/plugin.json
    skills/
      layout-decomposer/            # SKILL.md · skill.json · CHANGELOG · ROADMAP · references/
      mermaid-decomposer/           # … + bin/mermaid-render-check.py
      color-science/                   # SKILL.md · references/ · src/ (TS color lib) · examples/ (54 demos)
      typography-lettering/            # SKILL.md · references/ (tiered by axis)
  bin/check-skills.py                  # the self-contained CI gate
  .github/workflows/ci.yml
```

## Conventions

- **Skills are self-contained.** A skill names its `files[]` in `skill.json`, keeps SKILL.md a table-of-contents over `references/` loaded on demand, and routes deterministic checks to `bin/` (stdlib, selftested) — *computation routes to code, never to inference*.
- **The description is the routing surface** — ≤ 1024 chars, with WHAT + WHEN + NOT. A routing-eval corpus (scored trigger/adversarial phrases) is the next maturity step for each skill (tracked in its ROADMAP).
- **Mixed vintages are fine.** The two `decomposer` skills follow the skills-studio template (Quick Start · §SelfAudit · Verify Target); `color-science` + `typography-lettering` are reference skills (`## Invocation` + domain sections) — both valid; the gate enforces the hard contract and only advises on the template.
- Authored and red-teamed with **skills-studio**; the decomposers were extracted from the dev-factory cockpit + the catalog corpus-reader's Mermaid work, and `color-science`/`typography-lettering` adapt `meodai/skill.ref-color`'s flat-SKILL + tiered-references shape.
