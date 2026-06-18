---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/wave-based-research.md
  - ../agent-dispatch/wave-planning.md
primary_sources:
  - expert-dashboard/CHANGELOG.md (v0.1.0 through v1.0.0)
  - expert-dashboard/skill.json v1.0.0
  - expert-dashboard/references/INDEX.md v1.0.0
---

# Case study: expert-dashboard

**Comprehensive-domain exemplar.** 101 reference files, 15 axes, 5 research-survey waves, ~57,390 lines. Authored 2026-04-18 over 5 proposal-proceed cycles.

## Scope

Domain statement: "comprehensive SaaS dashboard knowledge base spanning components, layouts, patterns, tables, data-viz, workflows, navigation, state-and-async, accessibility, AI copilots, 13 canonical SaaS product profiles, multi-tenant architecture, real-time infrastructure, analytics/telemetry pipelines, performance, forms, and feedback-and-copy voice invariants."

Trigger prompt: "next skill: 'expert-dashboard' expert in all things SaaS dashboards, and every component, module, pattern, layout, workflow, etc."

## Axes (15)

1. `components/` (8 files) — Presentation primitives.
2. `layouts/` (8) — Page archetypes + layout primitives.
3. `patterns/` (9) — Recurring interactions.
4. `navigation/` (5) — IA, palette deep, breadcrumbs, tabs, top-nav.
5. `tables/` (8) — TanStack / AG Grid / virtualization / column / selection / pagination / spreadsheet-as-DB / a11y.
6. `data-viz/` (9) — Library landscape / chart selection / KPIs / time-series / perception / anti-patterns / CVD / grammar-of-graphics / real-time.
7. `workflows/` (8) — RBAC / onboarding / billing / metering / invites-SSO / audit / flags / import-export.
8. `state-and-async/` (4) — LESR / real-time / optimistic / offline.
9. `accessibility/` (6) — WCAG 2.2 / APG / contrast for data / SR / keyboard / reduced motion.
10. `products/` (13) — Linear / Stripe / Vercel / Notion / Figma / Datadog / Intercom / Slack / Mixpanel-Amplitude / HubSpot / Retool / Airtable-Attio / Ramp-Brex-Mercury.
11. `ai-and-agents/` (5) — Copilot sidebar / approval UIs / prompt bars / streaming surfaces / operator-ready.
12. `architecture/` (4) — Flag integration / multi-tenancy / real-time infra / analytics-telemetry.
13. `performance/` (5) — Bundle / virtualization-deep / render / cache / image-icon.
14. `forms/` (5) — Complex patterns / wizards / validation / upload / autosave.
15. `feedback-and-copy/` (5) — Errors / microcopy / help / confirmation / empty-state.

## Wave plan executed

| Wave | Files | Agents | Focus |
|---:|---:|---:|---|
| Scoping | 0 | 1 | Axis list + file plan (~12 research-survey areas, ~32 queries). Identified `ai-and-agents/` as 15th axis. |
| Skeleton | 4 | 0 | SKILL.md + skill.json v0.1.0 + CHANGELOG v0.1.0 + INDEX.md v0.1.0. |
| **Wave 1** | 16 | 8 | Foundations: components/app-shell + palette + KPI + empty + skeleton; layouts/sidebar-first; navigation/sidebar-ia; tables/tanstack + virtualization; data-viz/chart-library-landscape + chart-type-selection + KPIs; state-and-async/loading-empty-error-success; accessibility/WCAG-2-2 + APG; products/linear. |
| **Wave 2** | 20 | 8 | Tables advanced (6) + data-viz advanced (6) + ai-and-agents (5) + products A (Stripe + Vercel + Notion + Figma). |
| **Wave 3** | 27 | 8 | Layouts (7) + patterns (9) + workflows (8) + drawers + object-inspector + first architecture file. |
| **Wave 4** | 23 | 8 | Navigation (4) + state-and-async completion (3) + accessibility completion (4) + products B (8) + architecture (3) + toast. |
| **Wave 5** | 15 | 6 | Performance (5) + forms (5) + feedback-and-copy (5). |
| **v1.0.0** | — | — | 101 files, all axes at 100%. |

Total: 101 files, ~57,390 lines, 38 agents across 5 waves.

## What worked

1. **Parallel dispatch at ~8 agents per wave**. Each agent owned 2-4 related files. Wallclock per wave: 10-20 min.
2. **Agent findings reports.** Each agent returned 3-5 notable findings with primary-source URLs. These became the CHANGELOG's "Notable findings" section verbatim (lightly edited).
3. **Forward-reference tolerance.** Wave 3 files referenced Wave 4 files; labeled "forward-ref"; resolved by Wave 4.
4. **Product-reference axis as differentiator.** 13 per-product profiles made "how does X do Y vs how does Z do Y" tractable. Joint profiles (`ramp-brex-mercury.md`) worked well for category-peers.
5. **Late-wave axis additions.** Performance, forms, and feedback-and-copy were not in the original scoping but surfaced during Wave 2-3 as "should really be in here." Added cleanly in Wave 5.

## Lessons learned

### Sed disaster in Wave 3

During Wave 3 bookkeeping, a `sed -i.bak -E` one-liner with 27 stacked substitutions to flip ⬜→✅ in INDEX.md corrupted the file to 370KB — every line got 27 concatenated replacement stubs prepended. Backup was deleted in the same chain.

Recovery: rewrote the full INDEX.md from memory + skill.json `files[]`.

Lesson captured in `../agent-dispatch/bookkeeping-protocol.md`: **never sed-batch INDEX.md**. Use Edit per-row or Write full-rebuild.

### Scoping corrections

The scoping brief had several plausible-looking but wrong claims that agents caught by verifying against primary sources:
- "Airtable founded 2013" → actually 2012, public launch 2015-03.
- "TanStack + AG Grid partnership August 2024" → actually June 2022.
- "Linear sidebar-collapse shortcut Cmd+\" → actually `[` (Cmd+\ is VS Code).
- "Tremor acquisition, unspecified date" → actually Vercel January 2025.

Pattern: scoping briefs carry unverified plausibility. Agents that verify catch them.

### Agent fabrication

No fabrication caught in expert-dashboard waves (unlike expert-typography Wave 2 "WebKit Bug 241691" incident). Agent briefs explicitly cited the expert-typography fabrication as a warning — and expert-dashboard agents were noticeably more careful.

## Sample Wave 4 brief

From Wave 4A (navigation deepening) — abridged:

```
You are authoring 4 reference files for the `expert-dashboard` skill at
`~/.claude/skills/expert-dashboard/references/navigation/`.

Files to author (all new):
1. navigation/command-palette-deeper.md — IA patterns for palettes BEYOND
   component-anatomy file. Command taxonomy (actions vs navigation vs search
   vs help), ranking/relevance (recency, fuzzy matching, frequency), stale
   invalidation, context-aware commands. Exemplars: Linear, Raycast, Superhuman.
   Library: cmdk.
2. navigation/top-nav-patterns.md — [scope].
3. navigation/breadcrumb-patterns.md — [scope]. Cite APG breadcrumb pattern.
4. navigation/tabs-and-segmented.md — Tabs vs segmented. APG tabs (manual vs
   automatic). Cite APG exhaustively.

Frontmatter: [standard YAML block]

Length: 400-700 lines each.

VERIFICATION DISCIPLINE — ABSOLUTELY NON-NEGOTIABLE:
- Use WebSearch / WebFetch liberally.
- Never fabricate bug IDs or tracker numbers.
- Product references: observable public patterns only.
- Past fabrication lesson: do not invent tracker IDs (WebKit Bug 241691).

Context — existing files to cross-reference:
- references/components/command-palette.md (exists)
- references/patterns/keyboard-first.md (exists)
- references/accessibility/apg-patterns.md (exists)

Today's date: 2026-04-18. WCAG 2.2 Rec 2023-10-05.

Write all 4 files with Write. Do not update INDEX.md or skill.json.
Respond with: line counts, 3-5 notable findings.
```

Output: 4 files, 365 / 266 / 338 / 390 lines. Six notable findings including "Segmented control is not a tablist" (Primer guidance), "Vercel moved off top-nav to sidebar Feb 2026" (changelog cited), "cmdk v1.1.1 no multi-step native" (source-code verified), "APG breadcrumb example uses CSS-only separators" (APG HTML examined).

## Files per axis (final)

| Axis | Files | Avg lines/file |
|---|---:|---:|
| components | 8 | ~490 |
| layouts | 8 | ~617 |
| patterns | 9 | ~522 |
| navigation | 5 | ~362 |
| tables | 8 | ~610 |
| data-viz | 9 | ~687 |
| workflows | 8 | ~484 |
| state-and-async | 4 | ~446 |
| accessibility | 6 | ~710 |
| products | 13 | ~545 |
| ai-and-agents | 5 | ~556 |
| architecture | 4 | ~505 |
| performance | 5 | ~583 |
| forms | 5 | ~556 |
| feedback-and-copy | 5 | ~552 |
| **Total** | **101** | **~568** |

## Takeaways for method consumers

- Comprehensive-domain skills are feasible in a single day with 5 proposal-proceed cycles.
- ~6-8 agents per wave is the sweet spot.
- Bookkeeping discipline (no sed) matters more than brief-writing excellence.
- Product-reference axis is a disproportionate value-add.
- Late-wave axis additions (Wave 5 phase-2) are legitimate; plan for them.
