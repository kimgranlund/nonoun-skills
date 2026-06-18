---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/scoping-survey.md
  - ../methodology/wave-based-research.md
primary_sources:
  - expert-dashboard v1.0.0 axes (components, layouts, patterns, tables, data-viz, workflows, navigation, state-and-async, accessibility, products, ai-and-agents, architecture, performance, forms, feedback-and-copy)
  - expert-typography v1.0.0 axes (classifications, anatomy, metrics, pairing, legibility, scripts, fluid-type, libraries, css-techniques)
---

# Identifying the axes

An axis is a directory under `references/` that groups files which answer the same **kind** of question. Good axes make the skill navigable; bad axes make it sprawl. Most failures in this method trace back to poor axis choice.

## Three lenses for picking axes

A comprehensive skill usually needs at least one axis from each lens:

### 1. **Presentation** — what the thing LOOKS LIKE

What primitives, components, or artifacts does the practitioner work with?

- Dashboards: `components/` (KPI cards, drawers, palettes), `layouts/` (sidebar-first, bento), `patterns/` (inline editing, bulk actions).
- Typography: `anatomy/` (x-height, cap height, counters), `classifications/` (serif, sans, slab).

### 2. **Capability** — what the thing DOES

What capabilities / workflows / interactions does the domain support?

- Dashboards: `tables/`, `data-viz/`, `workflows/` (onboarding, billing, RBAC), `navigation/`, `state-and-async/`.
- Typography: `legibility/`, `pairing/`, `variable-fonts/`.

### 3. **Substrate** — what the thing SITS ON or INTEGRATES WITH

What cross-cutting concerns and integrations does the domain require?

- Dashboards: `accessibility/`, `architecture/` (multi-tenancy, real-time infra), `performance/`, `forms/`, `feedback-and-copy/`, `ai-and-agents/`.
- Typography: `css-techniques/`, `scripts/` (i18n), `libraries/`.

**Plus a distinctive axis**: `products/` in expert-dashboard makes "how does Linear vs Stripe do X?" tractable. Typography-expert has `techniques/` and `foundries/`. Every good expert skill has at least one axis that's **comparative** across named exemplars.

## Alternative lens model: temporal / instrumental (canon-curation mode)

The three-lens model above works for **capability-mode** skills (expert-typography, expert-dashboard). For **canon-curation-mode** skills, where each reference file summarizes one authoritative source rather than synthesizing a topic, use a different lens model.

**Temporal / instrumental lenses:**

1. **Historical** — Pre-current-state-of-the-art. The ancestors the canon cites. (expert-color: Ostwald, Helmholtz, Munsell, Albers, Itten.)
2. **Contemporary** — Current-state theory and science. Active researchers, recent papers. (expert-color: Ottosson, Briggs, Fairchild, Schloss-Palmer.)
3. **Techniques / instruments** — Tools, libraries, methods. (expert-color: Culori, Spectral.js, APCA, Kubelka-Munk.)

Alternative axis splits for canon-curation skills:

- **figures/ + schools/ + works/** — philosophy or critical theory.
- **movements/ + composers/ + analyses/** — music history.
- **papers/ + talks/ + books/** — pure source-type organization.
- **canon/ + critiques/ + extensions/** — when the canon has well-documented critiques.

**Use temporal/instrumental lenses when:**
- The domain has a deep canon of named sources (theorists, papers, books, talks).
- The base model already has strong priors — the skill's value is corrections + authoritative-source pointers, not synthesis.
- Axes would mirror a domain practitioner's reading list, not their task list.

**Exemplar**: expert-color uses 3 axes (`historical/`, `contemporary/`, `techniques/`) with ~49 files per axis. Capability-mode skills have 8-15 axes with ~7 files per axis. Canon-curation = fewer axes, denser per axis.

See `canon-curation-mode.md` for the full decision framework and file-shape conventions.

## Tests for a good axis

1. **Can you articulate a 3-sentence purpose for it** that doesn't overlap with any other axis?
2. **Are there 3+ distinct file-sized topics** inside it?
3. **Does every file name inside it end in the same part of speech** (all nouns, all pattern-names)?
4. **Is it on the landing-page routing table** in SKILL.md without being ambiguous?

If "yes" to all four, it's probably a real axis.

## Tests for a BAD axis

- **Single-file axis** — usually belongs inside another axis as a regular file.
- **Overlapping purpose** — files could sensibly go in two places; pick one, deprecate the other.
- **Mood-based axis** — "advanced/" or "gotchas/" aren't axes, they're tags.
- **Library-soup axis** — `libraries/` can work (expert-typography has one) but often masks what the files actually teach; prefer topic-based axes.

## Naming axes

- **Short** (≤ 2 words, usually 1).
- **Directory-safe** (no spaces, lowercase, hyphens).
- **Noun or noun-phrase**.
- **Plural when the directory contains multiple files of the same kind** (`patterns/`, `layouts/`, `components/`).
- **Singular when the directory contains facets of one thing** (`accessibility/`).

## Axis count sweet spot

- **6-8 axes** for narrow-domain skills.
- **10-12 axes** for medium-domain skills.
- **13-15 axes** for comprehensive-domain skills.

Beyond 15, the SKILL.md routing table stops fitting on a screen and the skill feels incoherent.

## How to split an axis that's too big

If one axis threatens to hold 20+ files, split by sub-dimension:

- Dashboards: initially `references/` had one `data-viz/` axis. At 9 files it was still OK; had it grown to 15, the split would have been `data-viz/charts/` and `data-viz/dashboards/` or by chart category.
- Typography: `techniques/` split into `techniques/` (CSS) and `opentype-features/` (font-level).

## How to merge axes that are too small

If two axes each have 2-3 files and the purposes are adjacent, merge them. Example: early `expert-dashboard` had both `state-and-async/` and `real-time/` as separate axes; the two merged into one.

## The product-reference axis

Skills benefit enormously from a `products/` axis with per-exemplar profiles. The rule:

- **Observable public patterns only**. No speculation about internals.
- **One file per canonical product**, or **joint profiles** when three products share a category (`products/ramp-brex-mercury.md`, `products/mixpanel-amplitude.md`).
- **7-15 products total** is typical — below 7 and the axis feels shallow, above 15 and profile depth suffers.
- **Pick products with distinctive UX DNA**, not the biggest logos.

## Worked examples

### expert-dashboard axes (15)

| # | Axis | Lens | Files | Notes |
|---:|---|---|---:|---|
| 1 | components | Presentation | 8 | Primitives: shell, palette, KPI card, drawer, object inspector, empty state, skeleton, toast. |
| 2 | layouts | Presentation | 8 | Page archetypes: sidebar-first, three-pane, bento, density, container queries, responsive tables, mobile, modern CSS. |
| 3 | patterns | Presentation | 9 | Interactions: keyboard-first, multiplayer presence, view plurality, progressive disclosure, master-detail, inline editing, bulk actions, confirmation, activity. |
| 4 | navigation | Capability | 5 | IA: sidebar, palette-deeper, top-nav, breadcrumbs, tabs. |
| 5 | tables | Capability | 8 | Data surface at scale. |
| 6 | data-viz | Capability | 9 | Charts + KPIs. |
| 7 | workflows | Capability | 8 | Multi-step operator flows (RBAC, onboarding, billing, audit, flags, import/export). |
| 8 | state-and-async | Capability | 4 | Loading/error, real-time, optimistic, offline. |
| 9 | accessibility | Substrate | 6 | WCAG, APG, contrast for data, SR, keyboard, reduced motion. |
| 10 | products | Comparative | 13 | Linear, Stripe, Vercel, Notion, Figma, Datadog, Intercom, Slack, Mixpanel/Amplitude, HubSpot, Retool, Airtable/Attio, Ramp/Brex/Mercury. |
| 11 | ai-and-agents | Capability | 5 | Copilot sidebar, approval UIs, prompt bars, streaming, operator-ready. |
| 12 | architecture | Substrate | 4 | Multi-tenancy, real-time infra, analytics/telemetry, flag integration. |
| 13 | performance | Substrate | 5 | Bundle, virtualization, render, cache, image/icon. |
| 14 | forms | Substrate | 5 | Complex, wizards, validation, upload, autosave. |
| 15 | feedback-and-copy | Substrate | 5 | Errors, microcopy, help, confirmation, empty-state. |

### expert-typography axes (~9)

- `classifications/` (presentation: what the shapes are called)
- `anatomy/` (presentation: parts of a glyph)
- `metrics/` (capability: what the numbers mean)
- `pairing/` (capability: how families combine)
- `legibility/` (substrate: reading research-survey)
- `scripts/` (substrate: non-Latin)
- `variable-fonts/` (capability: axes + wiring)
- `techniques/` (substrate: CSS properties)
- `libraries/` (substrate: what's shipping)

The point: every comprehensive expert skill mixes presentation, capability, and substrate, and usually has at least one comparative axis (products/, foundries/, exemplars/).
