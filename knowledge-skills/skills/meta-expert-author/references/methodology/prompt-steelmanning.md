---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/invocation-flow.md
  - ../methodology/concept-matching.md
  - ../methodology/canon-curation-mode.md
primary_sources:
  - Internal observation — invocation-flow.md four-question gate doesn't elicit latent intent
  - Chalmers (2015) "Why Isn't There More Progress in Philosophy?" — steelmanning as epistemic practice
---

# Prompt steelmanning

The four-question gate in `invocation-flow.md` **clarifies** what the user said. Steelmanning goes further: it proposes **the stronger version of what they probably meant**, then asks whether to proceed with that version instead.

Without steelmanning, the meta-skill is a literal interpreter of prompts. With it, the meta-skill is a consultant that helps the user articulate what they actually want.

## What steelmanning IS

The dictionary definition applied to prompts: constructing the strongest plausible interpretation of a prompt before responding to it, especially when the literal interpretation would produce a weaker output than the user likely wants.

For prompt-ingestion specifically, three moves:

1. **Latent-intent detection** — what goal sits behind the literal request?
2. **Stronger-shape alternative** — is there a different output shape that better serves that goal?
3. **Scope recalibration** — does the prompt imply a scale mismatch with the optimal skill shape?

Steelmanning is NOT:
- **Rewriting the prompt silently** — always propose and wait for confirmation.
- **Scope creep** — not adding axes the user didn't ask for because "it would be more complete."
- **Second-guessing tone** — not "I notice you said X, but you probably meant Y."
- **Imagining latent intent that isn't there** — some prompts are exactly what the user meant; don't manufacture alternatives.

## The three steelman moves

### Move 1: Latent-intent detection

**Question**: what goal does the literal request serve? Is the literal output actually the best vehicle for that goal?

Examples:

| Literal prompt | Likely latent intent | Steelman proposal |
|---|---|---|
| "Make me a react-expert skill" | Help me answer React questions better | Narrower `react-hooks-expert` (reaches the questions faster) OR broader `frontend-framework-expert` covering React/Vue/Svelte comparatively (better for architect work). Ask which. |
| "Make an ML-theory-expert" (theoretic mode) | Know what the ML-theory canon says | Note: ML is arxiv-first + heavily blog-documented. Pure-theoretic mode misses half the field's working canon. Propose meta-expert-author mixed-mode instead. |
| "Build a skill for my team's design-system patterns" | Make Claude useful for our design system | This is a knowledge-base task → `plan-knowledge` skill, not a `[domain]-expert` skill. Different tool. |
| "A comprehensive css-animation-expert" | Have CSS-animation answers ready | Scope question: does "comprehensive" mean "every web-animation API" or "performance + accessibility + creative-patterns"? Prompt's "comprehensive" is ambiguous; propose the narrower version unless explicitly asked for breadth. |

### Move 2: Stronger-shape alternative

**Question**: is the output shape the user described the best shape for their goal?

Shape mismatches to watch for:

- **Expert skill vs typed tool**. If the domain is narrow and its outputs are structured (contrast calculations, color conversions), a typed tool might serve better than a knowledge-base skill.
- **Capability vs canon-curation mode**. If the prompt implies one but the domain's character implies the other, propose the alternative.
- **Micro vs comprehensive scale**. If the prompt says "comprehensive" but the domain is genuinely narrow (APCA has maybe 15 load-bearing concepts), propose micro-scale.
- **Standalone skill vs extension**. If the prompt is about a sub-topic of an existing skill in the library, propose extending rather than forking.

### Move 3: Scope recalibration

**Question**: does the prompt's implied scale match the domain's actual scale?

Signals of scale mismatch:

- Prompt mentions 1 domain + 1 sentence → user probably wants micro (15-25 files). Don't default to comprehensive.
- Prompt mentions "everything about X" → user wants comprehensive OR genuinely doesn't know the scale. Ask.
- Prompt references a comparable skill ("like expert-dashboard") → anchor to that skill's scale, but question the parallel (see anti-patterns below).
- Prompt mentions a specific deliverable ("I need to answer questions about X") → calibrate to the question-space size, which is usually smaller than the domain.

## When to steelman vs proceed

Heuristics for when steelmanning adds value:

| Prompt character | Steelman? |
|---|---|
| Pre-scoped, explicit about domain + mode + scale + release | **No** — proceed |
| Domain named, mode unclear | **Yes** — mode steelman |
| Vague domain ("something about X") | **Yes** — scope + mode steelman |
| References comparable skill ("like Y") | **Yes** — test the parallel |
| Contains buzzword ("comprehensive", "full", "complete", "expert-level") | **Yes** — scope recalibration |
| Narrow enough that the answer should be a different tool | **Yes** — genre recalibration |
| Explicitly says "proceed without questions" or similar | **No** — honor the override |
| User has invoked the meta-skill many times before | **Default: no** — assume they know what they want |
| User sounds frustrated or time-pressured | **No** — steelmanning slows them down |

**Default: steelman when the prompt has any ambiguity. Don't steelman when the user is explicit.**

## The propose-and-wait pattern

When you have a steelman to offer, propose it in a short, clearly-labeled format:

```
Got it — [one-sentence restatement of literal prompt].

[Steelman observation in one sentence. What's the stronger version?]

**Stronger version**: [the proposed alternative, 1-3 sentences].

Proceed with literal version, or with the stronger version?
```

Rules for the proposal:

- **One steelman per turn.** Don't list 3 alternatives. Pick the strongest, offer it, wait.
- **Explicit opt-out.** "Proceed with literal version" must always be an option.
- **Keep it short.** Total proposal ≤ 8 sentences. Longer feels like pushback.
- **Tone is collaborative, not corrective.** "The stronger version might be..." not "You actually want..."

## Worked examples

### Example A: scope recalibration

**User**: "Make a comprehensive typescript-expert skill."

**Steelmanned response**:

> Got it — a typescript-expert skill.
>
> **Observation**: "Comprehensive TypeScript" could mean 60+ files spanning generics, utility types, narrowing, config, migration, library-authoring, meta-programming — a full comprehensive-scale skill. But TypeScript's most-asked questions concentrate in ~20 topics. A narrow 25-file skill might answer 80% of questions at 30% of the authoring time.
>
> **Stronger version**: narrow-scale typescript-expert (~25 files) focused on the high-traffic question-space, with the option to expand if specific axes turn out thin.
>
> Proceed with comprehensive or narrow?

### Example B: mode steelman

**User**: "Build me a theoretic-expert for deep learning."

**Steelmanned response**:

> Got it — a theoretic-expert for deep learning (peer-reviewed only).
>
> **Observation**: Deep learning is arxiv-first. ~60% of the field's canonical papers are arxiv-only (NeurIPS papers have DOIs but many high-impact works never go to peer review). A pure-theoretic skill restricted to peer-reviewed sources would exclude a lot of what practitioners cite.
>
> **Stronger version**: meta-expert-author in mixed-mode — a `peer-reviewed/` axis for the formal canon + a `preprints/` axis explicitly labeling arxiv-only work as tier-4 sources. Preserves source discipline but matches the field's actual shape.
>
> Proceed with strict theoretic or mixed-mode?

### Example C: genre recalibration

**User**: "Make me an apca-contrast-expert with all the formulas and thresholds."

**Steelmanned response**:

> Got it — APCA expert with formulas and thresholds.
>
> **Observation**: APCA is narrow enough that the practitioner's typical question is "what's the Lc for this pair?" — a computation, not a knowledge lookup. A typed tool that computes Lc given two colors might serve the goal better than a 20-file skill.
>
> **Stronger version**: a `meta-skill-typed` that takes two colors + content-type and returns Lc + pass/fail threshold. With a short reference section for context.
>
> Proceed with knowledge-base skill, typed tool, or both?

### Example D: no steelman warranted

**User**: "Make a narrow 20-file skill specifically about APCA color contrast algorithm and its status in WCAG 3. Capability mode. Internal use."

**Response**:

> Got it — narrow-scale APCA-contrast-expert, capability mode, internal. ~20 files across 4 axes.
>
> Proposed axes: algorithm / tooling / comparison-with-wcag-2 / wcag-3-status.
>
> Proceed to skeleton?

No steelman — the user has pre-scoped everything. Steelmanning here would feel condescending.

## Anti-patterns

### Scope creep disguised as steelmanning

**Bad**: "You asked for a 20-file skill. Here's a 60-file version with three more axes you didn't ask for."

User didn't ask for that. This isn't a stronger interpretation; it's a bigger skill.

### Condescending framing

**Bad**: "I notice you said X. You probably didn't realize that Y would be better."

**Better**: "Observation: the stronger version might be Y. Want that, or X as asked?"

The difference is tone. Steelmanning is a collaborative offer; condescension is unilateral correction.

### Multiple parallel steelmans

**Bad**: "Here are four alternative interpretations..."

Four options is more work for the user than one option. Pick the strongest steelman; offer it; wait.

### Steelmanning into mode-drift

**Bad**: User asked for capability mode. Steelman pushes toward canon-curation because "the domain has a canon."

If the user explicitly chose a mode, don't reverse that choice via steelman. The user picked for a reason.

### Post-proceed steelmanning

**Bad**: User said "proceed." You reply "proceeding, but also consider X, Y, Z first."

Proceed means proceed. If you had a steelman, it was the time to offer it; the time passed.

### Latent-intent projection

**Bad**: User said "X-expert." You imagine they really want "something that solves Y" and propose Y.

Unless the user's prompt contains signals of an underlying goal different from the literal request, don't invent one.

### Steelmanning an already-strong prompt

**Bad**: User gave a precise, well-scoped, mode-explicit prompt. You still propose an alternative out of habit.

If there's nothing to steelman, proceed. The user did the work; honor it.

## Composition with concept-matching

Steelmanning tells you **what shape the skill should have**. Concept-matching (see `concept-matching.md`) tells you **how much the base model already knows about the domain**, which calibrates:

- How much WebSearch the scoping survey needs (dense corpus → less; sparse → more).
- Where in the produced skill to flag uncertainty ("limited base-model coverage; heavy reliance on WebSearch").
- Which axes to propose (concept-matching surfaces the natural decomposition).

Typical flow in the invocation phase:

1. Read the user's prompt.
2. **Steelman** it → propose stronger shape if warranted.
3. After user confirms shape: **concept-match** against training corpus → calibrate certainty.
4. Present the plan (shape + axes + WebSearch budget) → user confirms.
5. Dispatch scoping survey.

The two operations compose: steelmanning decides the target; concept-matching decides how to get there.

## Measuring whether steelmanning helped

After a skill ships, ask yourself:

- Was the steelman proposal accepted? (If yes: it was useful.)
- Was it rejected? (If yes: note why — overreach? Misread the prompt?)
- Did the user have to redirect mid-wave because the initial framing was wrong? (If yes: steelmanning could have caught it.)

Track these over time. If your steelman acceptance rate is < 30%, you're probably overreaching. If the mid-wave-redirect rate is > 20%, you're probably under-steelmanning.

## One short invariant

**Steelman when the prompt is ambiguous; proceed when it's explicit; never rewrite silently.**
