---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/prompt-steelmanning.md
  - ../methodology/concept-matching.md
  - ../methodology/scoping-survey.md
  - ../methodology/canon-curation-mode.md
  - ../agent-dispatch/wave-planning.md
primary_sources:
  - expert-dashboard v0.1.0 invocation (2026-04-18 transcript)
  - expert-typography v0.1.0 invocation
  - expert-color first-use conventions
---

# Invocation flow

The first-message experience. What the meta-skill should ask, answer, and decide before dispatching the scoping-survey agent. Most method failures come from skipping this step — agents run with wrong assumptions baked in.

## Full invocation phase (v1.4+)

Three operations run before the scoping survey dispatches. Each feeds the next.

1. **Prompt steelmanning** (`prompt-steelmanning.md`) — propose the stronger version of the user's prompt if warranted. Wait for confirmation.
2. **Four-question gate** (below) — confirm domain / mode / release / scale.
3. **Concept matching** (`concept-matching.md`) — inventory base-model coverage; propose axes + WebSearch budget. Wait for confirmation.
4. **Scoping survey** — dispatches with the calibrated plan.

The four-question gate is necessary but no longer sufficient. It catches ambiguity; steelmanning elicits latent intent; concept matching calibrates the execution plan.

Skip operations 1 and 3 when:
- The user's prompt is explicit, pre-scoped, and specifies a reference skill.
- The user has invoked this method many times and signals "proceed without questions."
- The skill is a micro-scale variant with obvious shape.

Run all three when:
- The prompt has any ambiguity (mode, scale, domain boundary).
- The user references "comprehensive" / "full" / "expert-level" without specifics.
- The domain's character might not match the user's implied shape.

## The four-question gate

Before dispatching the scoping survey, the main thread should have concrete answers to all four of these. Ask the user if the answers aren't clear from the prompt.

### 1. What's the domain?

Usually obvious from the prompt ("make me a `music-theory-expert`"). But verify the scope. "Music theory" is different from "music production" is different from "audio engineering."

Write one sentence framing. If the user can't recognize their domain from your one-sentence framing, you've misunderstood. Ask again.

### 2. Capability or canon-curation mode?

The single most consequential decision. Wrong mode = wrong output shape that's expensive to correct.

**Default to capability mode** unless the user explicitly references expert-color or the domain obviously has a deep authored canon. See `canon-curation-mode.md` § "When to pick canon-curation mode" for the four conditions.

When unclear, ask: "Is this domain more about comparing practitioner tools (like dashboards, fonts) or knowing the canon of named theorists / papers / books (like color theory, music theory)?"

### 3. Internal or public release?

- **Internal** (expert-typography, expert-dashboard): Skip publishing trappings. Ship to `~/.claude/skills/` for the team.
- **Public** (expert-color on agentskills.io): Add LICENSE / README / MAINTENANCE / ROADMAP / SECURITY / THIRD_PARTY_NOTICES / evals. See `publishing-trappings.md`.

Ask explicitly if not stated: "Is this for internal team use or are you planning to publish it (e.g., agentskills.io)?"

### 4. Scale expectation?

| Size | File count | Axes | Waves | Wallclock |
|---|---:|---:|---:|---|
| **Micro** | 10-25 | 3-5 | 2-3 | 1-2 hours |
| **Narrow** | 30-50 | 5-8 | 3-4 | 3-5 hours |
| **Medium** | 50-80 | 8-12 | 4-5 | 5-8 hours |
| **Comprehensive** | 80-120 | 10-15 | 5 | 8-12 hours |
| **Canon-curation** | 50-200 | 2-4 | 5 | varies — source-discovery-bound |

Default to **medium** if the user doesn't specify. Announce the scale estimate before dispatching the scoping survey so the user can redirect.

## Invocation-response template

When invoked, the main thread's first response should have this shape:

```
Got it — building a [domain]-expert skill.

**Mode**: [capability | canon-curation] — [one-sentence rationale].
**Release**: [internal | public].
**Scale**: [micro | narrow | medium | comprehensive | canon-curation] — estimated ~[N] files across [M] axes.

Next step: dispatch the scoping survey (1 agent, ~20-30 web queries, 8-15 min).

Want me to proceed, or redirect on any of the above?
```

Don't dispatch until the user confirms or corrects. Spending 10 minutes of agent compute on the wrong scoping is worse than waiting 30 seconds for user signoff.

## Clarifying questions (only when needed)

Ask these only if the gate-four answers aren't clear:

- **Domain ambiguity**: "Just to confirm — by [X] you mean [narrow framing] or [broader framing]?"
- **Mode ambiguity**: "This domain could go either way — do you want topic-organized files (how-to) or source-organized files (who-said-what)?"
- **Release ambiguity**: "Is this for your team or are you planning to publish it?"
- **Scale ambiguity**: "How deep should this go — a focused 25-file reference or a comprehensive 100-file skill?"

Limit to 2-3 questions max. If more context is needed, run the scoping survey and let the findings resolve it.

## When the user provides a reference skill

Common pattern: "make me a skill like expert-dashboard for X." Use it.

- **"Like expert-dashboard"** → capability mode, comprehensive scale, 8-15 axes.
- **"Like expert-typography"** → capability mode, medium scale, 8-12 axes.
- **"Like expert-color"** → canon-curation mode, temporal axes, publishing trappings.

Echo back: "Mirroring [reference skill]'s shape: [mode], [scale], [~N files across M axes]. Proceed?"

## When the user provides existing notes

User has a pile of markdown files, transcripts, or documents and wants them shaped into a skill.

Different starting point than from-scratch. Skip the scoping survey; instead:

1. **Inventory the existing material.** Read or `find`. Classify each piece: what axis would it belong to?
2. **Propose axes from the material.** Instead of web-search-driven axes, the user's notes suggest them.
3. **Then run a coverage-gap scoping agent** to find what's missing from the canon that the user's notes don't cover.

Detect this case by looking for language like "I have some notes", "organize these docs", "turn this into a skill", or when the user attaches files.

## When the user invokes with just "make an expert skill"

Under-specified prompt. Ask:
- Domain?
- Mode?
- Release?
- Scale?

Don't guess. Don't dispatch the scoping survey on a vague prompt — you'll produce a plausible-but-wrong skill and waste the user's time.

## When to push back on the scope

If the four-question gate reveals something that will fail the method, say so before dispatching.

- **Domain too narrow for this method**: "An 'npm-install-expert' skill probably wants to be a single-file skill or a typed tool, not a 60-file knowledge base. Use `meta-skill` instead?"
- **Domain too broad**: "'Software engineering expert' is too broad — the scoping survey would produce 300+ files. Want to narrow to a sub-domain first?"
- **Domain where canon doesn't exist**: "'TikTok-trends-expert' doesn't have a durable citable canon — everything rots in 3 months. The method will produce a skill that's stale before it ships. Reconsider?"

The meta-skill is not obligated to produce a bad skill. Decline with a reason.

## Progress transparency

During a wave, the main thread should surface:
- Wave proposal with file list + agent split (before dispatch).
- Confirmation that N agents are running in background (after dispatch).
- Completion notifications as each agent finishes (narrated briefly — "Agent 4B complete, 3 files, 1220 lines").
- Wave completion summary with findings (after all agents complete, before next proposal).

Don't narrate internal deliberation. Don't run silently for 15 minutes. One-sentence updates at state transitions.

## Bail-out points

The user can abort at any wave boundary:

- Between scoping-survey report and Wave 1 dispatch.
- Between wave N completion and wave N+1 proposal.

Honor these. If the user says "stop" or "wait", freeze the current state, ensure bookkeeping is complete for the last completed wave, and don't dispatch further.

## Invocation checklist

Before dispatching the scoping survey, confirm:

- [ ] Domain framed in one sentence.
- [ ] Mode decided (capability or canon-curation).
- [ ] Release path decided (internal or public).
- [ ] Scale estimated (~N files across M axes).
- [ ] User has confirmed or corrected the plan.

Without all five, don't dispatch. Ask.
