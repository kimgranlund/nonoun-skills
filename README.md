# nonoun-skills

A home + marketplace for **general-purpose Claude Code skills** — domain-agnostic authoring aids that aren't tied to any one plugin's job. Versioned, validated, and installable, kept separate from the product plugins (which live in [`nonoun-plugins`](https://github.com/kimgranlund/nonoun-plugins)) so the skills don't bloat a plugin's standing context or stretch its scope.

Skills ship as cohesive **skill-bundle plugins** — a plugin that bundles only skills (no commands, agents, or MCP). The repo holds **11 plugins / 38 skills**, and the spine running through most of them is one technique: the **decomposer**.

→ Building a skill? See **[HOWTO.md](HOWTO.md)**. Repo history: **[CHANGELOG.md](CHANGELOG.md)**. What's next: **[ROADMAP.md](ROADMAP.md)**.

## The decomposer method (the spine)

Most skills here are **decomposers**. A decomposer grades an artifact on **two independent axes that walk the same hierarchy in opposite directions**, and the whole technique is that the two are **scored separately, never averaged**:

- an **intent axis** (whole → part) — *"is it the right thing?"* — naming, structure, the claim it makes. This is where an LLM is strong.
- a **mechanism axis** (part → whole) — *"does it actually work / hold / render, here?"* — the thing that compiles, validates, renders, executes. This is where an LLM fails silently, so it is **routed to a deterministic, self-tested `bin/` gate** — *computation routes to code, never inference.*

They **cross at one seam** (the artifact that is both the claim and the mechanism), the defects on the two axes are **opposite** (a clean intent can't hide a broken mechanism, and vice versa), and the rubric is **gated**: gate-level checks cascade and block the finer reviews. Where the dangerous axis can't be deterministically gated, the method **adversarially verifies** it in a fresh context. Every decomposer runs the same three modes: **DECOMPOSE** (read & grade), **CREATE/DESIGN** (author), **GRADE** (score against the rubric).

The same shape, specialized per domain — the axis pair is the skill's fingerprint:

| Skill | Plugin | Intent axis × mechanism axis | Mechanized gate (`bin/`) |
| --- | --- | --- | --- |
| **layout-decomposer** | design | OUTSIDE-IN × INSIDE-OUT | — (ASCII-wireframe archetype library) |
| **mermaid-decomposer** | design | INTENT × RENDER | `mermaid-render-check.py` (keyword gate + `mmdc`) |
| **component-decomposer** | design | COMPOSE × REALIZE | `geometry-check.py` (the (h−glyph)/2 law) · `component-contract-check.py` |
| **brand-decomposer** | design | MEANING × OPERABILITY | `brand-spec-check.py` (schema/provenance/WCAG-contrast/completeness) |
| **code-decomposer** | code | SPEC × EXECUTION | `execution-harness.py` · `test-vacuity-check.py` |
| **regex-decomposer** | code | LANGUAGE × MATCH | `regex-check.py` (example-set + ReDoS smell) |
| **query-decomposer** | code | SEMANTICS × EXECUTION | `sql-lint.py` · `query-harness.py` (EXPLAIN/dry-run) |
| **type-decomposer** | code | MODEL × VALIDITY | `instance-check.py` (legal/illegal instance sets) · `model-smells.py` |
| **architecture-decomposer** | code | STRUCTURE × INTEGRITY | `dependency-check.py` (acyclicity / layering / coupling) |
| **extraction-decomposer** | data | FIDELITY × VALIDITY | `groundedness-check.py` · `schema-check.py` |
| **routing-decomposer** | meta | INSTRUCTION × ROUTING | `routing-eval.py` (precision/recall) · `description-lint.py` |
| **proof-decomposer** | reasoning | ARGUMENT × VERIFICATION | `proof-structure-check.py` (DAG) · `numeric-spotcheck.py` |
| **config-decomposer** | ops | INTENT × VALIDITY | `config-lint.py` · `config-harness.py` (validate/plan) |

The non-decomposer skills follow two other vintages: deep **reference** skills that *answer and point at a peer for output* (they don't generate), and a **domain build** skill.

## Plugins

| Plugin | Domain | Skills |
| --- | --- | --- |
| **design-skills** | UI / visual | decomposers `layout-` · `mermaid-` · `component-` · `brand-decomposer` · reference `color-science` · `typography-lettering` · `ref-polyfills` · verifiers `color-` · `focus-` · `i18n-` · `perf-` · `safety-verifier` |
| **code-skills** | engineering | `code-` · `regex-` · `query-` · `type-` · `architecture-decomposer` (decomposers) · `figma-plugins` (domain build) |
| **data-skills** | structured data | `extraction-decomposer` |
| **meta-skills** | skills about skills | `routing-decomposer` |
| **reasoning-skills** | deductive argument | `proof-decomposer` |
| **ops-skills** | config / infra-as-code | `config-decomposer` |
| **general-skills** | domain-agnostic methods | `research-survey` · `viz-2x2` · `tool-stress` |
| **knowledge-skills** | knowledge bases | `meta-expert-author` · `meta-theory-author` · `plan-knowledge` · `ops-knowledge` |
| **manager-skills** | exec writing & reporting | `report-brief` · `-progress` · `-state` · `-strategic` · `resume-author` |
| **skills-skills** | authoring skills | `skills-studio` · `skills-refactor` · `meta-app-scaffold` |
| **plugins-skills** | authoring plugins | `plugin-decomposer` |

What each carries:

- **design-skills** — `layout-decomposer` (read/grade/design a UI, with a four-archetype ASCII-wireframe library) · `mermaid-decomposer` (advanced Mermaid on a verbatim 11-type syntax catalog + a mechanized render-check) · `component-decomposer` (a zero-dependency web component *and* how components compose — nest/wire — up to the module, with a deterministic geometry engine — every glyph centered in a square cell, so edge padding = (height − glyph)/2 — plus a composition-card linter; hands the app shell up to layout-decomposer) · `brand-decomposer` (a brand-guidelines spec graded as an *operating system* — INSIDE-OUT meaning × OUTSIDE-IN operability — with a 100-pt rubric, an evidence/confidence/three-truths trust model, a stdlib operability gate (schema/provenance/WCAG-contrast/completeness), and a CRITIQUE mode that grounds work-critique in a validated spec) · `color-science` (perceptual color + a TypeScript color library + 54 interactive demos) · `typography-lettering` (type anatomy → world scripts → the modern CSS text surface) · `ref-polyfills` (CSS/JS feature support, polyfills, the Baseline landscape) · the **verifiers** `color-`/`focus-`/`i18n-`/`perf-`/`safety-verifier` (gate a UI surface on contrast, focus order, i18n, perf budgets, and safety — each a card-based `bin/` check).
- **code-skills** — `code-decomposer` (a unit of code: right + provably runs, with an execution harness and a test-vacuity linter that attacks the "green but wrong" quadrant) · `regex-decomposer` (a pattern that means the right language and won't ReDoS) · `query-decomposer` (a SQL query at the right grain that actually plans) · `type-decomposer` (make illegal states unrepresentable, proven by legal/illegal instance sets) · `architecture-decomposer` (a system on STRUCTURE × INTEGRITY, with an acyclicity/layering/coupling checker) · `figma-plugins` (build/test Figma plugins across the sandbox↔iframe message bridge).
- **data-skills** — `extraction-decomposer` (is a structured extraction both schema-valid *and* true to its source — the instructive inversion where the cheap gate isn't the dangerous axis).
- **meta-skills** — `routing-decomposer` (does a skill's frontmatter description fire on the right requests and hold against the wrong ones — graded by a mechanized routing eval).
- **reasoning-skills** — `proof-decomposer` (are the steps valid *and* do they prove the stated claim — a proof-structure DAG check catches circular reasoning + a numeric counterexample search).
- **ops-skills** — `config-decomposer` (does a config declare the right desired-state *and* validate/plan cleanly — the plan is the contract; a safety linter catches plaintext secrets, `:latest`, wide-open permissions).
- **general-skills** — `research-survey` (systematic investigation & optimization: bisect, ablation, hill-climb, sweep) · `viz-2x2` (build/critique a 2×2 matrix) · `tool-stress` (stress-test a tool / MCP interface). *Domain-agnostic, reusable anywhere.*
- **knowledge-skills** — `meta-expert-author` · `meta-theory-author` · `plan-knowledge` · `ops-knowledge` (build and maintain knowledge bases and reference corpora).
- **manager-skills** — the `report-brief`/`-progress`/`-state`/`-strategic` family + `resume-author` (executive writing & reporting tools).
- **skills-skills** — `skills-studio` (the skill lifecycle: author/score/critique/eval) · `skills-refactor` · `meta-app-scaffold` (the meta-tooling for authoring Claude Code skills).
- **plugins-skills** — `plugin-decomposer` (a plugin on BUNDLE × MANIFEST — the right components for one job *and* it actually loads, with a manifest linter; the nonoun-native peer to plugins-factory).

## Install

```text
/plugin marketplace add kimgranlund/nonoun-skills
/plugin install design-skills@nonoun-skills      # …and/or code-skills, data-skills, meta-skills, reasoning-skills, ops-skills
```

…or for local development, point Claude Code at the skills directly (they're standard skill folders):

```sh
# symlink every skill into your user skills (kept in sync with the repo)
for s in */skills/*/; do ln -s "$PWD/$s" ~/.claude/skills/; done
```

## Develop

Skills are markdown + (optionally) stdlib Python. The repo is **self-contained and clean-checkout-true** — one gate proves it:

```sh
python3 bin/check-skills.py     # validate every skill, run all bin selftests, dogfood the render-check
```

`bin/check-skills.py` discovers any `*/skills/*/` containing a `skill.json` and asserts, per skill (**FAIL**): `skill.json` parses and its `name` matches the dir; the SKILL.md frontmatter `description` is ≤ 1024 chars; every `files[]` path exists; relative `.md` links resolve; each `bin/*.py` answers a `selftest` subcommand and exits 0; the Mermaid render-check passes its static keyword gate over every skill's `references/`. It also **dogfoods `routing-eval` over each skill's checked-in `*.corpus.json`** and surfaces sibling-routing collisions as advisories (the lexical-overlap proxy never FAILs the gate). The skills-studio structural floor (`## Quick Start` · `§SelfAudit` · `## Verify Target`) is **advisory** (a WARN) — decomposers carry it; the `ref-*`-derived reference skills use `## Invocation` + domain sections instead. CI (`.github/workflows/ci.yml`) runs the gate on every push/PR.

The full Mermaid **render** gate (`mmdc` actually rendering each block) fires only where the mermaid CLI is installed; CI installs it, so the render gate runs there while the static keyword gate runs everywhere.

## Layout

```
nonoun-skills/
  .claude-plugin/marketplace.json      # the marketplace (11 plugins)
  <plugin>/                            # design- · code- · data- · meta- · reasoning- · ops-skills
    .claude-plugin/plugin.json
    skills/<skill>/
      SKILL.md · skill.json · CHANGELOG.md · ROADMAP.md
      references/                      # loaded on demand; decomposition-method.md is always first
      bin/*.py                         # stdlib, selftested — the mechanism gate
  bin/check-skills.py                  # the one self-contained CI gate
  .github/workflows/ci.yml
  HOWTO.md · CHANGELOG.md · README.md
```

## Conventions

- **Skills are self-contained.** A skill names its `files[]` in `skill.json`, keeps SKILL.md a table-of-contents over `references/` loaded on demand, and routes deterministic checks to `bin/` (stdlib, selftested) — *computation routes to code, never to inference.*
- **The description is the routing surface** — ≤ 1024 chars, WHAT + WHEN + NOT. (`routing-decomposer` is the skill that grades this property; a routing-eval corpus is the next maturity step tracked in each skill's ROADMAP.)
- **The mechanism axis is gated where it can be, adversarially verified where it can't.** A deterministic gate is cheap but lossy — a static linter is a *pre-filter*, not a complete oracle. The hard, LLM-silent defects (a hallucinated value, an illegal state, a circular proof) get a deterministic gate *and* a fresh-context adversarial check; the skills document the gate's limits rather than overclaiming them.
- **Three vintages, all valid.** Decomposers follow the skills-studio template (Quick Start · §SelfAudit · Verify Target); `color-science` + `typography-lettering` are reference skills (`## Invocation` + domain sections); `figma-plugins` is a domain build skill. The gate enforces the hard contract on all equally and only *advises* on the template.
