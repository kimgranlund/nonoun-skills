# The two-axis method — BUNDLE × MANIFEST

A Claude Code plugin is **correct on two independent axes that walk the same hierarchy in opposite
directions** — the decomposer seam the code-, layout-, and component-decomposers apply to a unit of
code, to space, and to a component, here applied to a *plugin* (a bundle of commands / agents /
skills / MCP servers / hooks shipped through a marketplace).

- **Bundle · whole → part** grades the **intent**: the one job the plugin does → the components that
  fit that job → its cohesion → its boundary (what it deliberately leaves out) → its standing-context
  cost. *"Is it the right plugin?"* — this is where an LLM is strong.
- **Manifest · part → whole** grades the **mechanism**: the `plugin.json` is well-formed → its name &
  version are valid → its marketplace entry resolves → its paths are legal → it is self-contained.
  *"Does it actually install & load, here?"* — this is where an LLM fails *silently* (a `Title Case`
  name, a `1.0` version, a `../shared` path all read fine and break at install), so it routes to
  `bin/plugin-check.py`.

They **cross at the manifest + structure** — the `plugin.json` (plus its marketplace entry and the
on-disk folder layout) is *both* the claim (this bundle does one job with these components) and the
mechanism (this is what the loader reads to discover and install them). A manifest that won't load is
a dead bundle; a manifest that loads fine but bundles ten unrelated things is dead weight in every
session's standing context.

That crossing is the whole technique. A plugin can be:

- **coherent idea, won't load** — a sharp single-job bundle with the right components, but a malformed
  manifest, an illegal `../` path, a non-semver version, or a marketplace name that doesn't resolve.
  The classic *correct-but-dead* failure: a good plugin nobody can install.
- **loads fine, kitchen-sink** — the manifest is valid and every path resolves, but it bundles a
  grab-bag of unrelated commands, agents, and MCP servers that don't serve one job — so it earns
  always-on context weight it can't justify. The classic LLM trap: a green install on an unfocused
  bundle.

Opposite defects, opposite fixes — so you **score and report the two axes separately, never
averaged.** An averaged score hides which one you have, and they need opposite work (fix the manifest
vs. split / trim the bundle).

## The leveled walk

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Bundle** | whole → part | **A1** One job `[gate]` → **A2** Components fit `[gate]` → **A3** Cohesion `[review]` → **A4** Boundary `[review]` → **A5** Standing-context cost `[review]` | "Is it the *right plugin*?" |
| **B · Manifest** | part → whole | **B1** Well-formed `[gate, code]` → **B2** Name/version valid `[gate, code]` → **B3** Marketplace resolves `[gate, code]` → **B4** Paths legal `[review, code]` → **B5** Self-contained `[review]` | "Does it *actually install & load*, here?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** — a failure cascades and BLOCKS the reviews below it on
that axis. `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable plugin is **≥4 on every review with
zero gate failures**, reported as two separate axis scores plus the quadrant cell.

### A · Bundle (whole → part)

- **A1 One job `[gate]`** — can you state what this plugin is *for* in one sentence, without "and"?
  No single job ⇒ everything under it is a guess about scope.
- **A2 Components fit `[gate]`** — does every bundled component (command / agent / skill / MCP / hook)
  serve that one job? A component that doesn't fit poisons cohesion and inflates context.
- **A3 Cohesion `[review]`** — the components reinforce one workflow; no kitchen-sink, no two plugins
  fused into one.
- **A4 Boundary `[review]`** — what is *deliberately NOT here* is explicit; the plugin doesn't reach
  into adjacent jobs that belong in a sibling plugin (or in a skill, a command, or an MCP).
- **A5 Standing-context cost `[review]`** — the always-on weight (skill descriptions, command names,
  agent definitions, MCP tool schemas the model carries every session) is *earned* by the job. A
  reference corpus loaded on demand is cheap; ten always-listed components are not.

### B · Manifest (part → whole)

- **B1 Well-formed `[gate, code]`** — `plugin.json` parses and carries the required fields (`name`,
  `version`). Routed to `bin/plugin-check.py` (`MANIFEST_INVALID`).
- **B2 Name/version valid `[gate, code]`** — `name` is kebab-case, `version` is semver. Routed
  (`BAD_NAME` / `BAD_VERSION`).
- **B3 Marketplace resolves `[gate, code]`** — the `marketplace.json` `plugins[]` entry exists, its
  `name` matches the manifest, and its `source` is a legal path. Routed (`MARKETPLACE_MISMATCH`).
- **B4 Paths legal `[review, code]`** — every declared component/source path is relative and stays
  inside the plugin dir (no absolute, no `..`). Routed (`ILLEGAL_PATH`). It's a `[review]` because a
  legal-path run is necessary but doesn't prove the path *content* is right.
- **B5 Self-contained `[review]`** — no undeclared dependency on another plugin, an external tool, or
  a path outside the bundle; the plugin works from a copy-alone install. The checker can flag illegal
  paths but **cannot** prove self-containment — that's a review.

## The opposite-defect quadrant

```
                  B · MANIFEST loads        B · MANIFEST won't load
A · BUNDLE   ┌────────────────────────┬────────────────────────┐
  focused    │      SHIPPABLE         │  coherent idea, won't   │
             │                        │  load — one sharp job & │
             │                        │  the right components,  │
             │                        │  but a malformed manifest,│
             │                        │  illegal path, bad name/  │
             │                        │  version, or unresolved   │
             │                        │  marketplace entry        │
             ├────────────────────────┼────────────────────────┤
A · BUNDLE   │ loads fine, kitchen-   │       REBUILD           │
  unfocused  │ sink — valid manifest, │                         │
             │ legal paths, but a     │                         │
             │ grab-bag of unrelated  │                         │
             │ components earning     │                         │
             │ context it can't justify│                        │
             └────────────────────────┴────────────────────────┘
```

The quadrant **names the fix**: top-right needs manifest work (`plugin-check.py` tells you exactly
which gate); bottom-left needs *bundle* work the checker **cannot see** — split the plugin, drop the
components that don't fit, or sharpen the one-job statement.

## The doctrine — gate where you can, adversarially verify where you can't

This is why the skill earns its place (and why it's outsized for an LLM author):

- The MANIFEST gates (B1–B4) are the **cheap, deterministic** axis — route them to
  `bin/plugin-check.py` and **trust the tool, not the read-through.** An LLM cannot reliably tell by
  reading whether a name is kebab-legal, a version is semver, or a path escapes the bundle; the
  checker can. It catches *coherent-idea-won't-load* outright.
- But the **dangerous** axis ("loads fine, kitchen-sink") lives on the BUNDLE side and is **not
  deterministically gateable.** `KITCHEN_SINK` is a *count-of-disparate-component-kinds* smell — a
  lossy pre-filter, never a verdict (a focused multi-component plugin is legitimate; a single-skill
  bundle that smuggles in two jobs trips nothing). Route the real judgment two ways:
  - **A1/A2 by review**: state the one job in a sentence with no "and"; check each component against
    it. A component you can't tie to the job is the defect.
  - **A fresh-context adversarial probe**: a skeptic asked *"what two jobs is this plugin really
    doing?"* and *"which component would a user disable, and why is it still here?"* A reviewer who
    shares the author's framing rubber-stamps the bundle — separate the context (the `deep-research`
    adversarial-verify move). The global `plugins-factory:plugin-critique` 9-critic council is the
    heavyweight version of this probe.
- **Be honest about the checker's reach.** A clean `plugin-check.py` run proves the manifest is
  well-FORMED and the paths are LEGAL. It does **not** prove the declared paths *exist with the right
  content*, that the bundle is self-contained (B5), or that it does one job (A1) — those stay on the
  review side. Don't read a green run as "the plugin is good."

## Modes

- **DESIGN** (before authoring) — walk Bundle-down: name the one job (A1), pick only the components
  that serve it (A2), state the boundary (A4), estimate the standing-context cost (A5); then draft the
  manifest and run `plugin-check.py` to keep the MANIFEST axis green from the first commit.
- **DECOMPOSE** (an existing plugin) — recover the one-job statement (A1) and map each component to it
  (A2/A3); run `plugin-check.py` over the `plugin.json` (+ `--marketplace`) for B1–B4; report the
  bundle map + a gap list (e.g. *"loads clean, but the `hooks` component serves a second job — split
  it"*).
- **GRADE** — score both axes, gates first (run `plugin-check.py`, then the adversarial one-job
  probe), place in the quadrant, name one corrective per failure.

## Walk order (do not skip)

1. **A1 One job / A2 Components fit** — state the job in one sentence; tie every component to it.
   Can't ⇒ stop, split or trim before grading anything else.
2. **B1–B4 Manifest** — run `plugin-check.py <plugin.json> [--marketplace marketplace.json]`. A gate
   finding (MANIFEST_INVALID / BAD_NAME / BAD_VERSION / MARKETPLACE_MISMATCH / ILLEGAL_PATH) ⇒ fix
   before reviewing the bundle (you can't ship a plugin that won't install).
3. **A1/A2 adversarial probe** — in a fresh context, hunt the second job and the disable-me component.
   Any hit is a cohesion/boundary defect the checker's KITCHEN_SINK smell may have missed.
4. **Reviews** — A3–A5 then B4–B5, 1–5 each. Below 4 ⇒ name the single corrective.
5. **Report** — two axis scores, the quadrant cell, gate failures first; hand off to
   `skills-studio` (for a skill it bundles), `plugins-factory` (the global plugin-lifecycle peer), or
   `plugins-factory:plugin-critique` (the 9-critic council) as appropriate.
