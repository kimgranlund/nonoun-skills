---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/canon-curation-mode.md
  - ../methodology/axis-identification.md
  - ../examples/color-expert-case-study.md
primary_sources:
  - expert-color `techniques/` axis (mixed-mode exemplar in the wild)
  - expert-dashboard `products/` axis (mode-adjacent observation)
---

# Case study: mixed-mode skills

**When a single skill is partly capability, partly canon-curation.** Not a rare edge case — expert-color is the in-library exemplar, and most domains bigger than a single narrow topic run into it.

## The pattern

A skill can be **predominantly one mode with at least one axis in the other mode.** The whole skill picks a primary mode (capability OR canon-curation); individual axes can deviate when their content demands it.

Don't mix modes **within a single file**. A file is either "summarize this source" or "synthesize this topic," never both. Mode-mixing happens at the axis level.

## The exemplar: expert-color

**Primary mode**: canon-curation (historical/contemporary are pure canon-curation axes).
**Mixed-mode axis**: `techniques/`.

Files in expert-color's `techniques/` axis look different from `historical/` and `contemporary/`:

- `historical/albers-interaction-of-color.md` — summary of one book. One author. One source URL (archive.org).
- `contemporary/briggs-colours-objects-light.md` — summary of one talk. One speaker. One source URL (YouTube + archive.org mirror).
- `techniques/apca-contrast.md` — how to use APCA for contrast calculations. Multiple sources (Myndex docs, W3C WCAG 3 draft, practitioner writeups). Topic-synthesis.
- `techniques/culori-library.md` — how Culori works, its API, how to use it. Multiple sources (Culori GitHub, author blog, MDN CSS Color specs).

The first two are canon-curation. The second two are capability.

**Why the mix makes sense for color**: historical theorists are citable sources (one file per thinker). But "how to use APCA" isn't a single-source summary — it's a synthesis across docs, specs, practitioner experience. Forcing it into canon-curation shape would produce awkward "summary of the W3C WCAG 3 draft" files that don't answer the practitioner's real question.

## Signals you have a mixed-mode skill

You're probably mixed-mode if:

1. **One axis has ≥5 authoritative sources per topic**, and **another axis has 1 authoritative source per topic** that the file primarily summarizes.
2. **Some axes would produce "how to use X" files**, and **other axes would produce "what X said" files**.
3. **Some axes describe tools that evolve quickly** (Culori shipping new features monthly) alongside **axes describing static canonical sources** (Albers wrote his book in 1963, it doesn't update).

## The axis-level decision

Per axis, not per skill, pick one:

- **Canon-curation axis** — files are source summaries. Inline `**Source:**` headers acceptable. Archive.org mirrors required for tier 6+ URLs.
- **Capability axis** — files are topic syntheses. Full YAML frontmatter required. Multiple primary_sources per file.

Declare the axis's mode in INDEX.md next to the axis name:

```markdown
## Axes

1. **historical/** (canon-curation) — Pre-digital color science. One theorist / paper / book per file.
2. **contemporary/** (canon-curation) — Active researchers. One source per file.
3. **techniques/** (capability) — Tools and methods. Topic-synthesis per file.
```

This signals to contributors and consumers which file shape to expect in each axis.

## Wave planning for mixed-mode skills

Mixed-mode skills need wave briefs that match the axis's mode:

**Wave for a canon-curation axis**:
> "Author 3 reference files summarizing these authoritative sources: [URL 1], [URL 2], [URL 3]. Each file summarizes one source per the canon-curation template. Frontmatter: inline Source/Author headers OK. Primary_sources = the one URL + archive.org mirror."

**Wave for a capability axis** (same wave, different agents):
> "Author 3 reference files on these topics: [topic 1], [topic 2], [topic 3]. Each file synthesizes across 5-15 sources. Full YAML frontmatter required. Primary_sources = 10+ URLs per file."

Don't mix axis modes in a single agent brief. One agent = one axis mode.

## Mode-mixing anti-patterns

- **Mixing modes within a single file.** "Summary of Briggs + how to apply it to practical work" conflates two genres. Split into two files: `contemporary/briggs-talk.md` (canon) and `techniques/briggs-practical-applications.md` (capability).
- **Calling every axis mixed-mode "to be safe."** If an axis has only source-summary files, it's canon-curation. Declaring it mixed adds noise.
- **Inconsistent frontmatter within a mixed-mode axis.** Either all files in the axis use YAML (capability) or inline `**Source:**` headers (canon-curation). Not both.
- **Mixed-mode SKILL.md.** SKILL.md picks ONE doctrine (task-routing or "greatest hits"), not both. Color-expert's SKILL.md is "greatest hits" style even though `techniques/` is capability — because the whole skill's primary mode is canon-curation.

## Other candidate mixed-mode domains

- **music-theory-expert** — `figures/` (canon: Rameau, Schenker) + `techniques/` (capability: set-theory analysis, Neo-Riemannian transformations as tools).
- **philosophy-of-mind-expert** — `figures/` (canon) + `thought-experiments/` (capability: how Mary's Room is deployed, common objections, variant framings).
- **iOS-development-expert** — `apple-docs/` (canon) + `patterns/` (capability).
- **ml-research-expert** — `papers/` (canon: Transformers original, Attention is All You Need) + `techniques/` (capability: implementing attention from scratch).

In each, one axis is about what someone said, another is about what to do with it. The split is natural.

## When NOT to split into mixed-mode

If the user could plausibly reshape every file into one genre, don't split. Typography-expert could include a `typography-thinkers/` canon axis (Bringhurst, Lupton, Spiekermann) — it chose not to. The domain is practitioner-oriented enough that synthesizing across these thinkers per topic works better than summarizing each.

Dashboard-expert similarly: no `figures/` axis even though Shneiderman and Tufte exist. The skill is practitioner-oriented; quoting thinkers inline in topic-synthesis files suffices.

**Rule**: prefer single-mode if you can. Split only when one axis genuinely resists synthesis.

## What v1.3 captures

Before v1.3, `canon-curation-mode.md` mentioned mixing briefly in a "Mixing modes" section. v1.3 elevates that to a case study with concrete signals and anti-patterns. This closes the gap from v1.2's known-gaps list: "Mixed-mode skill case study."

## Takeaways

- Most large skills are mixed-mode to some degree. Plan for it rather than fighting it.
- Declare axis mode in INDEX.md so contributors know the shape.
- SKILL.md picks the overall primary mode (the mode of the majority of axes).
- Per-axis frontmatter conventions follow the axis mode, not the overall skill mode.
- When in doubt, single-mode wins — split only when one axis resists synthesis.
