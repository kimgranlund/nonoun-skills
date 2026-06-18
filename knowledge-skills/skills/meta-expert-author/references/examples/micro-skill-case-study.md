---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/invocation-flow.md
  - ../agent-dispatch/wave-planning.md
  - ../examples/typography-expert-case-study.md
primary_sources:
  - Hypothetical micro-skill scoping exercises (2026-04)
---

# Case study: micro-skills

**15-25 files across 3-5 axes, 2-3 waves.** The meta-skill's smallest coherent output. Not every domain wants to be a 100-file comprehensive skill — for tight, well-bounded domains, the micro variant is the right shape.

## When to pick micro

Pick micro when:

1. **The domain is narrow** — single well-bounded topic, not a sprawling discipline.
2. **The user wants quick turnaround** — 1-2 hours total, not 8-12.
3. **The question-space is focused** — practitioners ask 10-30 recurring questions, not hundreds.
4. **The canon is small** — one or two authoritative works, not a field.

Don't pick micro when:

- The user's prompt mentions breadth ("comprehensive", "cover everything", "like expert-dashboard").
- The scoping survey surfaces 50+ topic candidates.
- The domain has 5+ axes that each deserve 5+ files.

## Micro vs narrow vs medium

| Tier | Files | Axes | Waves | Agents per wave | Wallclock |
|---|---:|---:|---:|---:|---|
| **Micro** | 15-25 | 3-5 | 2-3 | 3-5 | 1-2 hours |
| Narrow | 30-50 | 5-8 | 3-4 | 5-7 | 3-5 hours |
| Medium | 50-80 | 8-12 | 4-5 | 5-8 | 5-8 hours |

The difference isn't just file count — it's the wave structure. Micro skips the full 5-wave arc.

## Micro wave structure

### Option A: 2 waves

- **Wave 1** (~10-15 files) — All foundation axes, 1-3 files per axis.
- **Wave 2** (~5-10 files) — Depth + edge cases + one product/exemplar axis if applicable.

### Option B: 3 waves

- **Wave 1** (~8-10 files) — Pure foundations.
- **Wave 2** (~5-8 files) — Axis completion.
- **Wave 3** (~3-5 files) — Polish + edge cases.

Prefer Option A for tight domains; Option B when the domain has 4-5 axes that each need their own focus.

## Micro can skip the scoping survey

If the domain is well-defined and the user clearly knows what they want, the scoping survey becomes overhead. Sample micro invocations that can skip scoping:

- "Make me an `apca-contrast-expert` — just APCA, the algorithm, its informative status in WCAG 3, tools that implement it, how to use it."
- "Build a `view-transitions-api-expert` focused only on the CSS View Transitions API — spec, browser support, patterns, gotchas."

In both cases the user has pre-scoped. The main thread's invocation response should confirm the axis list (3-5 axes) and file count (15-25) without a separate scoping agent.

**Still don't skip the scoping survey when:**
- The domain boundary is fuzzy ("something about CSS performance").
- The user asks "what should this cover?"
- Landscape verification is needed (libraries, versions, canonical sources).

## Micro SKILL.md shape

Tighter than capability or canon-curation defaults. Often one table + one cheat sheet + three cross-references is enough.

Example (hypothetical `apca-contrast-expert` SKILL.md structure):

```markdown
---
name: apca-contrast-expert
description: Use when working with APCA (Advanced Perceptual Contrast Algorithm)...
---

# apca-contrast-expert

APCA is the perceptual contrast algorithm defined by Myndex, informative in WCAG 3 Working Draft.

## When to use APCA vs WCAG 2.x contrast

| Task | Algorithm | Why |
|---|---|---|
| Current WCAG conformance | WCAG 2.x (4.5:1 text, 3:1 UI) | WCAG 2.2 is the Recommendation. |
| Informative perceptual comparison | APCA (Lc 60 for body text) | Perceptually uniform; designed for modern displays. |
| Design-system future-proofing | Both (compute and record each) | WCAG 3 trajectory is slow but headed this way. |

## Key distinctions

- **Lc ≠ contrast ratio.** APCA output is Lc (lightness contrast), not a ratio.
- **APCA thresholds are content-type specific.** Body text: Lc 60. Large headings: Lc 45.
- **APCA is NOT normative.** WCAG 3 is Working Draft as of 2026-04.

## Deeper references

- `references/algorithm/` — how APCA computes.
- `references/tooling/` — libraries and calculators.
- `references/comparison/` — APCA vs WCAG 2.x in practice.
```

~80-150 lines typical. Routing table is optional; if you have 20 files across 4 axes, a section-per-axis summary may work better than a table.

## Micro invocation-flow

Use the four-question gate from `invocation-flow.md`, but compressed:

**User**: "Make me an APCA expert — focused skill, not comprehensive."

**Main thread response**:
```
Got it — micro-scale APCA expert skill.

Scale: ~20 files across 4 axes (algorithm, tooling, comparison, WCAG-3-status).
Mode: capability (topic-organized, APCA's canon is small enough not to warrant canon-curation).
Release: [ask if unclear].
Waves: 2 (foundations + depth).

Skip the scoping survey — the domain is well-defined. Proceed to draft INDEX.md + SKILL.md skeleton?
```

Shorter than a full scoping-survey preamble. The user signs off; you draft the skeleton files and dispatch Wave 1.

## Micro bookkeeping

The bookkeeping protocol still applies but is lighter:

- INDEX.md update after each wave (2-3 total).
- skill.json version bumps: 0.1.0 (skeleton) → 0.2.0 (Wave 1) → 0.3.0 (Wave 2) → 1.0.0.
- CHANGELOG.md entry per wave.

No shortcut for bookkeeping. Even micro skills need the manifest discipline.

## Micro's place in the ecosystem

Micro skills often **pair with a larger skill** as an "extract." Example:

- `expert-color` (148 files) → could spawn `oklch-expert` (20 files) as a focused sub-skill.
- `expert-dashboard` (101 files) → could spawn `command-palette-expert` (15 files) just on cmdk + palette UX.

Extract-pattern triggers:
- A single topic within a large skill is getting 5+ questions per week.
- Users keep loading the whole skill to answer a narrow question.
- The narrow topic has its own coherent axis structure inside the parent skill.

The extract is effectively a re-packaging. The deep content stays in the parent; the micro skill becomes a fast path.

## Validation: "is this too small?"

Below 15 files, reconsider:
- Is this actually a typed skill? (One-shot tool with input/output schema → use `meta-skill-typed`.)
- Is this actually a cheat sheet? (Six tables, no deep content → write a memo and ship it as a doc.)
- Is this a snippet that belongs inside a bigger skill? (Add it as a file in an existing skill.)

Skills below 15 files often aren't skills — they're something else (tools, docs, snippets). Re-examine before committing.

## What v1.3 captures

v1.2's `invocation-flow.md` scale table mentioned micro (15-25 files, 3-5 axes, 2-3 waves) but didn't walk through what a micro run actually looks like. v1.3 provides the concrete walkthrough.

## Takeaways

- Narrow, well-bounded domains deserve micro skills, not padded medium skills.
- 2-3 waves is enough. 5-wave arc is overkill for micro.
- Skip the scoping survey when the domain is pre-scoped.
- Bookkeeping discipline doesn't relax for micro.
- Below 15 files, reconsider whether it's really a skill at all.
