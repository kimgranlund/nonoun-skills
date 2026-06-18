---
date: 2026-04-18
coverage: deep
peers:
  - ../methodology/scoping-survey.md
  - ../methodology/axis-identification.md
  - ../agent-dispatch/wave-planning.md
  - ../agent-dispatch/bookkeeping-protocol.md
primary_sources:
  - expert-dashboard v1.0.0 run (2026-04-18, 101 files, 5 waves)
  - expert-typography v1.0.0 run (2026-04-18, 59 files, 5 waves)
---

# Wave-based research-survey

The method is a **5-wave arc from skeleton to v1.0.0**, with a single-agent scoping survey front-loaded before Wave 1. Each wave dispatches 5-8 parallel agents, each authoring 2-4 files. Per-wave bookkeeping (INDEX / skill.json / CHANGELOG) happens before the next wave starts.

## Why waves?

Three reasons:

1. **Parallelism**: 6 agents writing 20 files concurrently is ~10-20× faster than sequential.
2. **Context economy**: the main thread stays uncluttered — agents return ~200-word findings reports, not raw file content.
3. **Verification checkpointing**: after each wave, the main thread sees notable findings, can correct course, and catches fabrication drift before it compounds.

## The arc

| Stage | Agents | Files | Output |
|---|---:|---:|---|
| **Scoping survey** | 1 | 0 | Axis list, file plan (65-120 files), scoping findings. |
| **Skeleton** (no wave) | 0 | 4 | `SKILL.md`, `skill.json`, `CHANGELOG.md`, `references/INDEX.md`. |
| **Wave 1 — foundations** | 5-8 | 12-20 | Highest-leverage cross-axis files; one anchor per foundation axis. |
| **Wave 2 — axis depth A** | 5-8 | 15-25 | Second tier: advanced tables, advanced data-viz, etc. |
| **Wave 3 — axis depth B** | 5-8 | 15-27 | Third tier: layouts, patterns, workflows. |
| **Wave 4 — axis completion** | 5-8 | 15-25 | Finish original axes; add first product-reference batches. |
| **Wave 5 — phase-2 axes** (optional) | 5-6 | 10-15 | Add 2-3 adjacent axes elevated from "nice to have." |
| **v1.0.0** | 0 | 0 | Bookkeeping only. Status flips to `complete`. |

Scoping → 5 waves → v1.0.0 is ~6-8 sub-sessions if the user paces `proceed`-per-wave.

## Wave 1 — foundations

Pick the axes whose absence would make the skill feel incomplete in the first question. For `expert-dashboard`, that was: components, layouts, navigation, tables, data-viz, state-and-async, accessibility, and one anchor product profile (Linear). For `expert-typography`: classifications, anatomy, metrics, legibility, pairing, variable fonts.

Rule of thumb: **one file per foundation axis + one anchor exemplar**. Usually 12-16 files.

Wave 1 agents use the coverage tier **`deep`** more than later waves because these files will be cited by every file that follows.

## Waves 2-4 — expansion

Each expansion wave picks an ensemble that:

- **Completes a partial axis** (e.g., Wave 2 finishes tables + data-viz).
- **Opens a new axis or product batch** (e.g., Wave 2 opens the `ai-and-agents/` axis and adds Stripe/Vercel/Notion/Figma product profiles).
- **Avoids overloading a single agent** (3-4 files per agent max; more risks hitting context or degrading quality).

When a wave exceeds ~27 files across 8 agents, split across two waves. When it falls below ~12 files across 5 agents, consider combining with the next wave.

## Wave 5 — phase-2 axes (optional)

Wave 5 is reserved for axes that the scoping survey flagged as "nice to have" but would otherwise defer. If during Waves 2-4 you uncover new axes, plant them here.

Typical Wave 5 axes: performance, forms, feedback-and-copy (from expert-dashboard) — each ~5 files.

## Per-wave rhythm

Every wave follows the same script in the main thread:

1. **Propose the wave** to the user: files, agent split, focus per agent. Wait for "proceed".
2. **Dispatch N agents in parallel** (all in one message, `run_in_background=true`).
3. **Receive completion notifications** as each agent finishes (typically spaced over 8-15 minutes).
4. **Consolidate**: flip INDEX markers, bump skill.json, prepend CHANGELOG entry with file table and notable findings.
5. **Report the wave outcome** to the user + propose the next wave.

See `../agent-dispatch/bookkeeping-protocol.md` for the mechanics of step 4.

## Verification checkpointing

Agent completion reports are the key verification surface. Each agent must return:

- **Line counts per file** — catches suspiciously short or bloated files.
- **3-5 notable findings** — the main thread cites these in the CHANGELOG.
- **Verification corrections** — any claims in the scoping brief the agent couldn't verify and corrected or omitted.

If an agent reports claims without citations, or cites URLs you can't verify, treat the output as suspect and re-read the files before CHANGELOG promotion.

## Pacing and session boundaries

One wave per conversation is the natural unit, but strong agents can do two waves in one session if the user paces `proceed` quickly. Between waves is the only safe place to pause the work and resume later — mid-wave is not resumable cleanly because background agents may still be running.

If context gets tight within a wave, consolidate bookkeeping immediately (write the CHANGELOG entry incrementally as agents complete) rather than batching at the end.

## When the scoping is wrong

If Wave 1 reveals the scoping survey missed a load-bearing axis, add it to Wave 2's plan rather than backfilling into Wave 1. Keep waves forward-flowing — re-opening a "complete" wave breaks the bookkeeping invariant.

Scoping failures that justify adding a new axis:
- A whole category of questions the skill can't answer (e.g., "dashboards need an AI-copilots axis I didn't scope").
- A library/standard that turns out to be load-bearing across 3+ axes.

Scoping failures that do NOT justify adding a new axis:
- A single missing file within an existing axis — just add it to the next wave.
- A deprecated topic that's smaller than expected — note in the CHANGELOG, move on.
