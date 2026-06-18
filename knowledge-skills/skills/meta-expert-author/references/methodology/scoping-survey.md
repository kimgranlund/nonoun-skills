---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/wave-based-research.md
  - ../methodology/axis-identification.md
primary_sources:
  - expert-dashboard v0.1.0 scoping survey (2026-04-18)
  - expert-typography v0.1.0 scoping survey
---

# The scoping survey

One agent, 20-30 web queries, 8-12 research-survey areas. Produces the axis list, the file plan (typically 65-120 files), and a findings report that the main thread uses to draft the INDEX.md and seed the SKILL.md cheat sheets.

## Brief the scoping agent with

- **Domain statement** from the user's prompt, expanded into 2-3 sentences.
- **Comparable skills** already in the library (expert-typography, expert-dashboard) so the agent mirrors voice and structure.
- **Research areas to cover**: libraries, standards, canonical exemplars, recent landscape shifts, academic foundations, adjacent disciplines, failure modes.
- **Output shape**: axis list with 3-sentence rationales, per-axis file list, landscape-shift bullets for the CHANGELOG, flagged uncertainties.

## Standard research-survey areas

Adjust to the domain, but the scoping agent should always touch:

1. **Libraries / tools / ecosystem** — what practitioners use, which are 2024-2026 leaders, which are in sunset.
2. **Standards and specs** — W3C, IETF, ISO, academic consensus, regulatory (WCAG, EAA, etc.).
3. **Canonical exemplars** — products, brands, or projects the domain treats as reference.
4. **Landscape shifts 2023-2026** — acquisitions, deprecations, new primitives, reversed positions.
5. **Academic / historical foundations** — the cited papers and the people who wrote them.
6. **Failure modes and anti-patterns** — what the domain gets wrong, common mistakes.
7. **Adjacent disciplines** — neighboring skills that this one should peer or not overlap.
8. **Accessibility / compliance dimensions** — the inclusion floor for the domain.
9. **Tooling maturity** — which claims are production-ready, which are speculative.
10. **Naming conventions** — the vocabulary drift across products and how to document it.

## Agent prompt template

```
You are running the scoping survey for a new `[domain]-expert` skill in the style of expert-typography and expert-dashboard.

Goal: produce an axis list + file plan that the main thread will use to seed INDEX.md and SKILL.md, then inform 5 research-survey waves.

Research areas to cover (run 20-30 web queries total, spread across these):
1. Libraries / tools / ecosystem
2. Standards and specs
3. Canonical exemplars
4. Landscape shifts 2023-2026 (acquisitions, deprecations, reversed positions)
5. Academic / historical foundations
6. Failure modes and anti-patterns
7. Adjacent disciplines / peer skills
8. Accessibility / compliance (if relevant)
9. Tooling maturity (production vs experimental)
10. Naming conventions and vocabulary drift

Domain statement:
[2-3 sentences from the user's prompt]

Comparable skills in this library:
- expert-typography: classifications, anatomy, metrics, pairing, legibility, scripts, fluid-type, libraries
- expert-dashboard: components, layouts, patterns, tables, data-viz, workflows, navigation, state-and-async, accessibility, products, AI-agents, architecture, performance, forms, feedback-and-copy

Deliver a findings report structured as:

## Axes (proposed, 8-15)
For each axis: name (directory-safe), 3-sentence purpose, 3-10 planned reference file names.

## Landscape shifts (2023-2026)
Bulleted with dates and sources. These become CHANGELOG "notable findings" for the eventual Wave 1 entry.

## Canonical references
Products / libraries / standards to anchor the skill.

## Peer skills
Which existing skills this should peer with or explicitly avoid overlapping.

## Flagged uncertainties
Claims the survey couldn't verify against primary sources — flag for the main thread to resolve.

## File count estimate
Total planned across all axes, with split by wave.

No speculative internals. Every claim needs a URL. If a claim is uncertain, label it.

Respond in ~1500-2500 words.
```

## What the main thread does with the output

1. **Drafts `references/INDEX.md`** with axes + file list in the manifest, all ⬜.
2. **Drafts `SKILL.md`** with the task→reference table and cheat sheets based on axes.
3. **Drafts `skill.json`** with tags derived from axes + canonical exemplars.
4. **Seeds `CHANGELOG.md` v0.1.0** with the scoping-survey findings.
5. **Plans Wave 1** based on axis prioritization + file-count budget.

## Pitfalls

- **Scoping too narrow** — results in a 30-file skill. Usually fixable by adding a products/ axis or splitting a big axis into two.
- **Scoping too broad** — 150+ files. Usually fixable by grouping related topics into "joint profile" files (e.g., `products/ramp-brex-mercury.md` for three finance products).
- **Axis confusion** — two axes that would produce overlapping files. Merge them before Wave 1 or separate the responsibilities sharply.
- **Canonical-exemplar list drifts** — the agent proposes 30 products, you pick 12-15. Cull early.

## Time budget

A scoping agent typically runs 8-15 minutes. It's the only agent in this phase, so no parallelism here — but don't try to do it inline in the main thread; the main thread should receive a report, not raw web-search output.

## Calibrating file count

| Skill size | Total files | Axes | Waves |
|---|---:|---:|---:|
| Narrow expert | 30-50 | 5-8 | 3-4 |
| Medium expert | 50-80 | 8-12 | 4-5 |
| Comprehensive | 80-120 | 10-15 | 5 |

Typography-expert landed ~60 (medium). Dashboard-expert landed 101 (comprehensive). The domain determines the size — don't pad to hit a count.
