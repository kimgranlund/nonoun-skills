---
name: plugin-decomposer
description: >
  Decompose, design, and grade a Claude Code PLUGIN (a marketplace-distributed bundle of commands,
  agents, skills, MCP servers, hooks) on two crossing axes — BUNDLE (one job → components fit →
  cohesion → boundary → context cost) and MANIFEST (well-formed → name/version → marketplace resolves
  → paths legal → self-contained) — scored separately so a coherent idea that won't load and a
  kitchen-sink that loads fine get opposite fixes. MANIFEST routes to a self-tested checker
  (bin/plugin-check.py flags MANIFEST_INVALID, BAD_NAME, BAD_VERSION, ILLEGAL_PATH, KITCHEN_SINK). Use
  to author or review a plugin, or check a plugin.json + marketplace entry. Triggers: "is this plugin
  well-bundled", "review my plugin.json", "does this plugin install", "is this a kitchen-sink plugin",
  "what should NOT be in this plugin". The nonoun-native peer to the global plugins-factory. NOT for
  authoring a SKILL (skills-studio / skills-skills), a unit of code (code-decomposer), or an MCP tool
  perimeter (core-mcp-best-practices).
---

# plugin-decomposer — grade a Claude Code plugin on two crossing axes

A Claude Code plugin is **correct on two independent axes that walk the same hierarchy in opposite
directions** — the decomposer seam the code-, layout-, and component-decomposers apply to a unit of
code, to space, and to a component, here applied to a *plugin* (a marketplace-distributed bundle of
commands / agents / skills / MCP servers / hooks):

- **Bundle · whole → part** grades the **intent**: the one job the plugin does → the components that
  fit that job → its cohesion → its boundary (what it deliberately leaves out) → its standing-context
  cost. *"Is it the right plugin?"* — where an LLM is strong.
- **Manifest · part → whole** grades the **mechanism**: the `plugin.json` is well-formed → its
  name/version are valid → its marketplace entry resolves → its paths are legal → it is
  self-contained. *"Does it actually install & load, here?"* — where an LLM fails *silently*, so it
  routes to `bin/plugin-check.py`.

They **cross at the manifest + structure** — the `plugin.json` (plus its marketplace entry and the
on-disk layout) is *both* the claim (one job, these components) and the mechanism (what the loader
reads to discover and install them). That crossing is the whole technique: a plugin can be **coherent
idea, won't load** (one sharp job and the right components, but a malformed manifest, an illegal `../`
path, a non-semver version, or a marketplace name that doesn't resolve) or **loads fine, kitchen-sink**
(valid manifest, legal paths, but a grab-bag of unrelated components earning always-on context it
can't justify). Opposite defects, opposite fixes — so you **score and report the two axes separately,
never averaged.**

The reason this is outsized for an LLM author: MANIFEST is exactly where models hallucinate with the
most confidence (`Title Case` names, `1.0` versions, `../shared` paths) *and* it is mechanizable — so
the gate converts the worst failure into a caught error. And the **kitchen-sink** quadrant — the one a
green install hides — gets a dedicated attack: a component-count smell plus a fresh-context one-job
probe.

## Quick Start

**You bring:** a plugin (an idea, an existing `plugin.json` + folder, a marketplace entry) and the
question — "design this bundle", "is this well-bundled?", "does it install?", "what shouldn't be
here?". **You get:** a one-job statement + component map, a manifest report card, and a two-axis grade
with the defect quadrant named.

> *"Is my `db-toolkit` plugin well-bundled?"* →
> 1. **Bundle — one job → components fit:** state it in a sentence with no "and" — "manage local
>    Postgres for dev" `[gate]`; tie each component to it: a `db-up` command (fits), a `migrate` agent
>    (fits), a `slack-notify` hook (*doesn't* — second job) `[gate]`.
> 2. **Manifest — run it, don't read it:** `bin/plugin-check.py plugin.json --marketplace
>    marketplace.json` checks well-formed + name/version + marketplace-resolves + paths-legal `[gate]`.
>    Green? Now the bundle is the question.
> 3. **Adversarial one-job probe:** in a fresh context, ask *"what two jobs is this really doing, and
>    which component would a user disable?"* — the `slack-notify` hook is the second job; split it.
> 4. **Review + report:** cohesion/boundary/cost (A3–A5), paths/self-contained (B4–B5), then the two
>    axis scores + the quadrant cell — gate failures first — handed to `skills-studio` (for a bundled
>    skill) or `plugins-factory` / `plugins-factory:plugin-critique` (the global peer + its council).

**Modes:** **DESIGN** (Bundle-down → name the one job, pick only fitting components → draft the
manifest, keep `plugin-check.py` green) · **DECOMPOSE** (read a plugin → recover the one-job statement
→ map components → run the manifest checker → grade) · **GRADE** (score both axes, gates before
reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Bundle** | whole → part | **A1** One job → **A2** Components fit → **A3** Cohesion → **A4** Boundary → **A5** Standing-context cost | "Is it the *right plugin*?" |
| **B · Manifest** | part → whole | **B1** Well-formed → **B2** Name/version → **B3** Marketplace resolves → **B4** Paths legal → **B5** Self-contained | "Does it *actually install & load*, here?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on
that axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable plugin is **≥4 on every review with
zero gate failures**, reported as two separate axis scores plus the defect quadrant.

## The doctrine — gate where you can, adversarially verify where you can't

The non-obvious core, and the reason it earns a skill:

- **MANIFEST is the cheap, deterministic axis** — route B1–B4 to `bin/plugin-check.py` and **trust the
  tool, not the read-through.** An LLM cannot reliably tell by reading whether a name is kebab-legal,
  a version is semver, or a path escapes the bundle. It catches *coherent-idea-won't-load* outright.
- **"Loads fine, kitchen-sink" is NOT deterministically gateable** — it lives on the BUNDLE side.
  `KITCHEN_SINK` is a *count-of-disparate-component-kinds* smell (a lossy pre-filter, never a verdict:
  a focused multi-component plugin is legitimate; a single-skill bundle smuggling in two jobs trips
  nothing). Route the real judgment two ways: **A1/A2 by review** (state the one job with no "and";
  tie every component to it), and a **fresh-context adversarial probe** (*"what two jobs is this
  really doing? which component would a user disable, and why is it still here?"*). A reviewer sharing
  the author's framing rubber-stamps the bundle — separate the context (the `deep-research` move). The
  global `plugins-factory:plugin-critique` 9-critic council is the heavyweight version of this probe.

## §SelfAudit

- **The manifest is the gate the LLM fails silently.** Run `plugin-check.py`; do not certify "it
  installs / the name is fine / the path is legal" from reading. An unrun checker is *no evidence*,
  not a pass.
- **A clean checker run is necessary, not sufficient.** It proves the manifest is well-FORMED and the
  paths are LEGAL — not that the declared paths *exist with the right content*, that the bundle is
  self-contained (B5), or that it does one job (A1). Those stay on the review side; never read green
  as "the plugin is good."
- **The dangerous defect is invisible to the tool — probe the bundle adversarially in a fresh
  context.** "Loads fine, kitchen-sink" needs a skeptic hunting the second job, not the author's
  confidence. `KITCHEN_SINK` is a smell, not the verdict.
- **Gates before reviews, always.** Don't grade cohesion for a plugin that won't load, or
  standing-context cost for a bundle whose one job you can't state. Stop each axis at its first failed
  gate.
- **Two scores, never one.** *Coherent-idea-won't-load* and *loads-fine-kitchen-sink* need opposite
  fixes (fix the manifest vs. split/trim the bundle). Report both axes and name the quadrant cell;
  never average.
- **Decompose & grade, don't author the components.** This skill locks the one-job statement, the
  manifest verdict, and the grade — it does not write the bundled skill (`skills-studio` /
  `skills-skills`), the unit of code in a command (`code-decomposer`), or the MCP tool perimeter
  (`core-mcp-best-practices`). Hand off; don't overlap. It is the nonoun-native peer to the global
  `plugins-factory`.

## Verify Target

A plugin is **done** when: you can state its one job in a sentence with no "and" (A1) and every
component serves it (A2); cohesion/boundary/standing-context cost ≥4 (A3–A5); `plugin-check.py` ran
**green** on the `plugin.json` (+ `--marketplace`) — well-formed, valid name/version, marketplace
resolves, paths legal (B1–B4); self-containment confirmed by review (B5 ≥4); and both axes score ≥4
with zero gate failures, landing in the **SHIPPABLE** quadrant. **NOT done** when: it installs cleanly
but bundles unrelated components you can't tie to one job (*loads fine, kitchen-sink*); or the bundle
is sharp but the manifest is malformed, the name/version invalid, the marketplace entry unresolved, or
a path escapes the dir (*coherent idea, won't load*); or the checker was skipped and read as a pass; or
one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Bundle × Manifest), the leveled walk with gates, the quadrant, the gate-vs-adversarial-verify doctrine, and the DESIGN / DECOMPOSE / GRADE workflows |
| `references/plugin-anatomy.md` | **the Manifest axis** — the manifest/marketplace/skills-discovery contract: `plugin.json` required fields, kebab/semver rules, how a marketplace entry resolves, path legality, self-containment, the skill-bundle special case, and how each `plugin-check.py` finding maps onto it |
| `bin/plugin-check.py` | **mechanizes B1–B4** — reads a `plugin.json` (+ optional marketplace entry) and flags MANIFEST_INVALID · BAD_NAME · BAD_VERSION · MARKETPLACE_MISMATCH · ILLEGAL_PATH (gates) + KITCHEN_SINK (advisory). `<plugin.json> [--marketplace M] [--entry NAME]` · `template` · `selftest` |
