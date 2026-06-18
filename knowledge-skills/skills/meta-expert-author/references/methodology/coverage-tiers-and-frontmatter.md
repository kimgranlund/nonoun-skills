---
date: 2026-04-18
coverage: foundational
peers:
  - ../structure/reference-file-template.md
  - ../methodology/verification-discipline.md
primary_sources:
  - expert-dashboard per-file frontmatter audit (2026-04)
  - expert-typography per-file frontmatter audit
---

# Coverage tiers and frontmatter

Every reference file in a produced skill starts with YAML frontmatter. No exceptions. This is the single most load-bearing convention — it makes staleness visible, depth claims honest, and cross-links machine-verifiable.

## The frontmatter

```yaml
---
date: 2026-04-18
coverage: <foundational | expanded | deep>
peers:
  - <relative path to peer file>
  - <relative path to peer file>
primary_sources:
  - <URL or full citation>
  - <URL or full citation>
---
```

### Fields

| Field | Required | Purpose |
|---|:-:|---|
| `date` | ✅ | ISO-format date this file was authored or last updated. Staleness is visible at a glance. |
| `coverage` | ✅ | One of `foundational` / `expanded` / `deep`. Sets reader expectation for depth. |
| `peers` | ✅ | Relative paths to sibling files that cross-reference this one. Must resolve. |
| `primary_sources` | ✅ | URLs or full citations for every factual claim-family in the file. |
| `product` | product profiles | Name of the SaaS/library/brand profiled. |
| `product_url` | product profiles | Canonical URL. |
| `observation_note` | product profiles | "Observable public patterns only; no speculative internals." |

## Coverage tiers

Each tier signals the expected **depth and structure** of the file. Tiers are declared at author time, not assigned retroactively — write to the tier you've chosen.

### `foundational`

- 250-400 lines of dense prose.
- One primary topic, cleanly defined.
- 2-4 canonical exemplars or techniques.
- Decision table or cheat sheet toward the end.
- Primary sources: 5-10 authoritative URLs.

Use for: first-encounter overviews, definitional material, cornerstone concepts the skill doesn't want to restate everywhere.

Example: `methodology/coverage-tiers-and-frontmatter.md` (this file).

### `expanded`

- 400-600 lines.
- One primary topic with 3-6 sub-dimensions or related topics folded in.
- 5-8 canonical exemplars.
- Decision tables, library comparison matrices, anti-pattern callouts.
- Primary sources: 10-20 URLs.

Use for: the workhorse majority of reference files.

Example: `data-viz/chart-type-selection.md` in expert-dashboard.

### `deep`

- 600-900 lines (occasionally more).
- One primary topic with exhaustive sub-dimensions.
- 10+ canonical exemplars including direct quotations or specific measurements.
- Multiple decision tables, full decision trees, normative-text quotations for standards.
- Primary sources: 20+ URLs, often with full citations.
- APG pattern mappings, normative WCAG SC quotations, etc.

Use for: files the skill will be **evaluated by** — foundational a11y content, the single most important file per axis, standards-grounded content.

Example: `accessibility/screen-reader-for-dashboards.md` (890 lines), `tables/accessibility.md` (789 lines).

## Tier selection guide

| Content type | Tier |
|---|---|
| Narrow technique | foundational |
| Single-product profile | expanded |
| Multi-product joint profile | deep |
| Standards / normative coverage | deep |
| Anti-patterns + exemplars | expanded |
| Comparison (library landscape) | deep |
| Quick reference / cheat sheet | foundational |
| Architectural decision table | expanded |

## Dates

Always ISO format: `2026-04-18`. No month names, no abbreviations, no American-style `4/18/2026`. Dates must be parseable.

Update the `date:` when you materially revise the content. Don't update it for typo fixes — staleness detectors should surface real drift, not cosmetic churn.

## Peer paths

Peers use **relative paths from the file**, not absolute.

```yaml
peers:
  - ../components/command-palette.md
  - ../patterns/keyboard-first.md
```

Not:

```yaml
peers:
  - /Users/kimba/.claude/skills/expert-dashboard/references/components/command-palette.md  # ❌
  - components/command-palette.md  # ❌ (needs `../` prefix when in a sibling dir)
```

Paths must resolve. If a peer file doesn't exist yet (Wave 2 file referenced from Wave 1), label it a forward-reference and note in the Wave 1 CHANGELOG "known gaps / dangling cross-refs" section.

## Primary sources

Every factual claim-family needs a URL or full citation. Claim-families are:

- **Version numbers / release dates** (e.g., "React 19 GA December 5, 2024").
- **Acquisition / partnership claims** (e.g., "PartyKit acquired by Cloudflare April 2024").
- **Standards text** (e.g., "WCAG 2.2 SC 2.5.8").
- **Academic citations** (e.g., "Cleveland & McGill 1984, JASA 79(387)").
- **Product-specific claims** (e.g., "Linear sidebar-collapse shortcut `[`").

URLs go in the `primary_sources` list. Inline citations in the prose refer back. If a claim can't be verified against a primary source, **omit it or mark it speculative** — see `verification-discipline.md`.

## Product profile extra fields

For files in `products/`:

```yaml
---
date: 2026-04-18
coverage: deep
product: Linear
product_url: https://linear.app
observation_note: "Observable public patterns only; no speculative internals."
peers:
  - ../patterns/keyboard-first.md
  - ../components/command-palette.md
primary_sources:
  - https://linear.app/changelog
  - https://linear.app/docs
---
```

The `observation_note` is load-bearing: it's the contract that prevents speculative-internals drift.

## Frontmatter is mandatory

A reference file without frontmatter is a bug. Fix it before promoting the file to ✅ in INDEX.md.
