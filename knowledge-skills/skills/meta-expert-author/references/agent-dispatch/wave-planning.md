---
date: 2026-04-18
coverage: expanded
peers:
  - ../agent-dispatch/agent-brief-template.md
  - ../agent-dispatch/bookkeeping-protocol.md
  - ../methodology/wave-based-research.md
primary_sources:
  - expert-dashboard Wave 1-5 plans
  - expert-typography Wave 1-5 plans
---

# Wave planning

Each wave is an ensemble of files authored by 5-8 parallel agents. Picking the right ensemble is load-bearing — bad wave planning produces uneven coverage and wasted agents.

## Sizing a wave

| Parameter | Typical | Floor | Ceiling |
|---|---:|---:|---:|
| Files per wave | 15-25 | 10 | 27 |
| Agents per wave | 5-8 | 4 | 8 |
| Files per agent | 2-3 | 1 | 4 |
| Wave duration (wallclock) | 10-20 min | 5 | 30 |

Below floor: merge with the next wave. Above ceiling: split.

## Balance rules

Every wave should have:

1. **A foundations agent** (Wave 1) OR **an axis-completion agent** (Waves 2-4). Not drifting between axes.
2. **At most one "new axis" agent**. Opening too many new axes per wave fragments coverage.
3. **Product-reference agents grouped**. Three products per agent is normal (e.g., "products batch B-1: Datadog + Intercom + Slack").
4. **No overlap between agents**. Two agents authoring related files that cross-reference each other is OK (forward-refs) but two agents touching the same file is a bug.

## Pairing files within an agent

Files within one agent should be **closely related by topic** so the agent can reuse context. Good pairings:

- `tables/ag-grid.md` + `tables/column-management.md` + `tables/selection-and-bulk.md` (all AG Grid / table APIs).
- `products/datadog.md` + `products/intercom.md` + `products/slack.md` (three products, same research-survey substrate).
- `accessibility/screen-reader-for-dashboards.md` + `accessibility/keyboard-traversal.md` (related a11y domains).

Bad pairings:
- `tables/tanstack-table.md` + `data-viz/chart-library-landscape.md` (different axes, different primary sources).
- `accessibility/wcag-2-2.md` + `patterns/bulk-actions.md` (different specialties).

## The scoping → wave mapping

After the scoping survey, you have 65-120 planned files across 8-15 axes. Map them to waves like this:

### Wave 1 (foundations) — 12-16 files

Goal: one anchor per foundation axis + an anchor exemplar. Every subsequent wave will cross-reference Wave 1 files.

Pick **one file per axis** for axes that will carry the skill's voice. Examples from expert-dashboard Wave 1:
- `components/app-shell.md` (components axis)
- `components/command-palette.md` (components axis; second file because palette is cross-cutting)
- `layouts/sidebar-first-vs-topbar.md` (layouts axis)
- `navigation/sidebar-ia.md` (navigation axis)
- `tables/tanstack-table.md` (tables axis)
- `tables/virtualization.md` (tables axis; second because scaling is foundational)
- `data-viz/chart-library-landscape.md` (data-viz axis)
- `data-viz/chart-type-selection.md` (data-viz axis; second because selection is foundational)
- `state-and-async/loading-empty-error-success.md` (state-and-async axis)
- `accessibility/wcag-2-2-for-dashboards.md` (accessibility axis)
- `accessibility/apg-patterns.md` (accessibility axis; second because APG is foundational)
- `products/linear.md` (anchor exemplar)

12 files landed in Wave 1 → 8 agents (each with 1-2 files).

### Waves 2-4 (axis depth) — 15-25 files each

Goal: complete partial axes + open new axes.

Pattern: **six focus agents**, each owning one domain.
- Agent A: finish tables (3-4 files).
- Agent B: finish data-viz (3-4 files).
- Agent C: open a new axis (3-4 files, e.g., AI/agents).
- Agent D: product batch (3 products in one file each, or one joint profile).
- Agent E: cross-cutting axis (3-4 files, e.g., workflows batch).
- Agent F: a focused-scope agent (1-2 files, short).

### Wave 5 (phase-2) — 10-15 files

Goal: add adjacent axes elevated from "nice to have."

Pattern: **one agent per new axis**, 3-5 files each. 3 axes × 1 agent each = 3 agents OR split each into two agents if files exceed 4.

From expert-dashboard Wave 5:
- Performance: 5 files → 2 agents (3+2).
- Forms: 5 files → 2 agents (3+2).
- Feedback-and-copy: 5 files → 2 agents (3+2).
- Total: 6 agents, 15 files.

## The proposal-proceed rhythm

Every wave is proposed to the user in a short message:

```
## Wave N proposal (X files, Y parallel agents)

| Agent | Files | Focus |
|---|---|---|
| A | [file 1, file 2, file 3] | [topic] |
| B | [file 4, file 5] | [topic] |
...

After Wave N: [total] files projected complete.

Say **proceed** to dispatch Wave N.
```

User says `proceed` → dispatch in a single message → wait for completion notifications.

## Never skip the proposal step

The proposal-proceed rhythm is non-negotiable. Dispatching a wave without user approval breaks the pacing and the user loses the ability to redirect before 8 agents spend 15 minutes of compute on the wrong files.

Exception: `/loop` or similar autonomous mode, where the user has pre-authorized the pattern.

## Wave-level failure modes

### Wave too big (27+ files)

Split along the natural fault line (axes, product batches). Two waves is always better than one too-big wave.

### Wave too small (< 10 files)

Merge with the next wave's plan. Small waves waste the overhead of proposal + bookkeeping.

### Wave unfocused (agents touching 4+ axes)

Re-group agents by axis. Each agent should feel like a coherent expert in one corner.

### Mid-wave discovery

If Wave N discovers a new axis is needed, note it in the CHANGELOG under "known gaps" and plan it for Wave N+1. Never retroactively add files to Wave N.

## When to call v1.0.0

v1.0.0 lands when:
- Every ⬜ in the original INDEX plan is ✅.
- All Phase-2 axes (if any) are complete.
- Status in skill.json flips to `complete`.
- CHANGELOG has a v1.0.0 entry summarizing all 5 waves.

If the skill feels complete but has 2-3 deferred files, consider them out-of-scope and ship v1.0.0 anyway — those files can land in v1.1.0 or later.
