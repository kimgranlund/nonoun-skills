---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/invocation-flow.md
  - ../methodology/prompt-steelmanning.md
  - ../methodology/concept-matching.md
  - ../methodology/axis-identification.md
  - ../agent-dispatch/wave-planning.md
primary_sources:
  - Internal observation — ingestion (steelman + concept-match) clarifies the ask but doesn't execute it; without decomposition the main thread jumps straight from "I understand" to "I'm doing" with no intermediate plan
  - Polya (1945) "How to Solve It" — understand → plan → execute → look back
  - Kepner-Tregoe problem analysis — separating problem from solution via structured breakdown
---

# Task decomposition

Ingestion (steelmanning + concept-matching) tells the skill **what the user is actually asking for**. Decomposition tells it **how to break that ask into sub-asks that can each be executed**.

Without decomposition, the main thread goes from "I understand the ask" straight to "I'm executing" — skipping the plan. The symptoms are predictable: monolithic dispatches, missed sub-asks, parallel work that turns out sequential, and retroactive recomposition when a sub-ask gets forgotten.

**The discipline is: no ask executes monolithically. Every non-trivial ask is decomposed into named, scope-bounded sub-asks — each of which is individually executable, verifiable, and composable.**

## What decomposition IS

The operation of splitting an understood ask into the **smallest set of sub-asks that together cover the whole ask, with no sub-ask overlapping another**.

Three properties of a good decomposition:

1. **Covering** — union of sub-asks = the whole ask. Nothing important slips between seams.
2. **Non-overlapping** — sub-asks don't duplicate each other's work. Each has a distinct scope.
3. **Individually tractable** — each sub-ask is small enough to be executed (by an agent, by the main thread, or by a reference-file lookup) without further decomposition.

Decomposition is NOT:
- **Restating the ask with numbers.** "1. Do the thing. 2. Do it well." is not decomposition.
- **Free-form brainstorming.** A messy list of 15 loosely-related bullets isn't a decomposition; it's a dump.
- **Planning in the absence of ingestion.** Decomposing a misunderstood ask produces a well-structured wrong answer.
- **Over-fragmentation.** Breaking an atomic 2-minute task into 6 sub-asks with 4 hand-offs wastes coordination cost.

## Why it matters — three failure modes decomposition prevents

### Failure 1: monolithic dispatch

Main thread reads an ask → dispatches one big agent with "do all of X". Agent returns a sprawling result that's partially right, partially wrong, and hard to verify because there's no sub-structure to check.

With decomposition: the ask becomes 4 sub-asks → 4 agents → each result is scoped and verifiable.

### Failure 2: silent omission

Ask mentions three things A, B, C. Main thread notices A and B; C slips through. Executes A + B. User redirects: "what about C?" — but by then the work is shaped around A + B and retrofitting C is painful.

With decomposition: A, B, C each become a named sub-ask. The decomposition step surfaces C before execution. Missing it requires actively dropping it, not passively forgetting.

### Failure 3: false parallelism

Ask has a hidden dependency chain (B needs A's output; C needs B's output). Main thread dispatches A, B, C in parallel because they sounded independent. B and C produce garbage because their inputs were wrong.

With decomposition: dependencies are explicit. The decomposition step forces the question "which sub-asks can run in parallel?" and "which must run sequentially?". Hidden dependencies surface here instead of at execution time.

## Three kinds of decomposition

Different asks decompose differently. Three recurring shapes:

### Shape A: Axis decomposition (for domains)

Break a domain into 3-7 cross-cutting dimensions. Each axis is a lens on the whole domain, not a slice of it.

**Used for**: scoping a skill, organizing references/, structuring a PRD.

**Example**: typography domain → `foundations/` / `systems/` / `product-references/` / `history/` / `techniques/`. Each axis touches the whole domain from a different angle.

**Detailed in**: `axis-identification.md` (for skill-authoring specifically).

### Shape B: Task decomposition (for execution)

Break an execution task into sub-tasks that run in sequence or parallel. Each sub-task has a clear input, output, and success criterion.

**Used for**: wave planning, agent dispatch, multi-step implementation, complex refactors.

**Example**: "produce a 60-file skill on X" → Wave 1 foundations (15 files) → Wave 2 expansion (15 files) → Wave 3 expansion (15 files) → Wave 4 phase-2 (10 files) → Wave 5 polish (5 files).

**Detailed in**: `wave-planning.md` (for the 5-wave arc specifically).

### Shape C: Question decomposition (for answering)

Break a user's question into sub-questions that route to specific reference files or tool invocations. Each sub-question is independently answerable.

**Used for**: produced skills answering practitioner questions, router skills.

**Example**: user asks "is this color pair accessible?" → (1) what's the contrast ratio? (2) what's the WCAG 2 AA threshold for this text size? (3) what's the APCA Lc? (4) how do WCAG 2 vs APCA disagree here? → each routes to a different reference file.

**Detailed in**: produced skills document this per-skill via their SKILL.md "Invocation" section.

## When to decompose vs proceed

Not every ask warrants decomposition. Heuristics:

| Ask character | Decompose? |
|---|---|
| Single-file edit, clear target | **No** — execute |
| Single-question answer (answerer skill) | **Yes** — decompose into sub-questions so routing is explicit |
| Multi-step task with obvious ordering | **Light** — name the steps, note ordering, execute |
| Multi-step with parallelism opportunity | **Yes** — explicit parallel/sequential call-out |
| Multi-file refactor | **Yes** — by file or by concern |
| Skill-authoring (meta) | **Always** — wave + axis decomposition is mandatory |
| User explicitly says "just do X" and X is atomic | **No** — honor the directness |
| User asks for something you don't fully understand | **STOP** — ingest first, then decompose |

**Default: decompose when the ask has ≥ 2 seams. Proceed when it's atomic.**

A seam = a natural joint where the ask could be split. If you can describe the ask in a single sentence without a conjunction, it's probably atomic.

## The decomposition protocol

When decomposition is warranted:

### Step 1: Restate the ask in your own language

Say what you think the ask is, in one sentence. If you can't, you haven't ingested yet — go back to steelmanning + concept-matching.

### Step 2: Identify the seams

Seams are natural joints. Look for:
- Conjunctions in the ask ("A and B").
- Multiple deliverables ("a file and a test and a README").
- Multiple phases ("first X, then Y, then Z").
- Multiple axes of variation ("across all components" → each component is a seam).
- Dependencies ("Y uses X's output" → X and Y are separate).

### Step 3: Name the sub-asks

Aim for **3-7 sub-asks** for most decompositions. Fewer than 3 = probably atomic; more than 7 = probably over-decomposed and should be grouped.

Each sub-ask needs:
- **Input**: what does it consume? (The original ask, a prior sub-ask's output, a file, etc.)
- **Output**: what does it produce? Be concrete — a file, a set of files, a decision, a verification report.
- **Success criterion**: how do you know it's done? Something observable, not "looks good".

### Step 4: Verify coverage + independence

Two checks:

- **Coverage check**: if you executed all sub-asks and nothing else, would the whole ask be done? If not, there's a missing sub-ask.
- **Overlap check**: do any two sub-asks do the same work? If so, merge or re-scope.

### Step 5: Declare ordering

For each sub-ask, declare:
- **Runs in parallel with**: [list of other sub-asks]
- **Must run after**: [sub-ask whose output this needs]
- **Blocks**: [sub-asks that need this one's output]

This step is where false parallelism gets caught. If you find yourself saying "B depends on A but can run parallel", you haven't understood the dependency.

### Step 6 (optional): Propose to user

For asks where the decomposition implies non-trivial commitment (a 5-wave skill, a 20-file refactor), surface the decomposition as a proposal before executing. For smaller asks, proceed.

## Worked example A: meta-skill decomposition (skill-authoring)

**Ask**: "Build a causal-inference-expert skill."

**Decomposition** (Shape A — axis + Shape B — waves):

Axis decomposition first (Shape A):
- `methodologies/` — Pearl, Rubin, Imbens, Robins methods.
- `findings/` — landmark empirical papers.
- `debates/` — Pearl vs Imbens, RCT epistemology.
- `recent/` — post-2023 developments.

Then wave decomposition (Shape B):
- **Wave 1** (foundations, 10 files): methodologies/ — core of Pearl + Rubin canon.
- **Wave 2** (parallel-safe): findings/ (8 files) + debates/ (5 files) — no dependencies on Wave 1 beyond axis names.
- **Wave 3**: recent/ (10 files) — depends on Wave 1 for context-referencing ("this extends Pearl's do-calculus by..."), must run after Wave 1.
- **Wave 4**: cross-axis synthesis in SKILL.md's "Unresolved debates" — depends on Waves 1-3.
- **Wave 5**: polish + publishing trappings.

Dependencies declared. Wave 2 parallel-safe. Wave 3 sequential after Wave 1. Wave 4 sequential after 1-3.

## Worked example B: produced-skill question decomposition (answerer)

**Ask** (to expert-dashboard, a produced skill): "How should I handle an empty state in a revenue chart?"

**Decomposition** (Shape C — sub-questions):

- (1) What's the category of empty state? (no-data-yet / loading / no-matches / error)
- (2) What are the visual conventions for each category?
- (3) What are the copy conventions? (tone, length, CTA presence)
- (4) What are revenue-specific considerations? (zero vs null distinction; placeholder vs blank)

Each sub-question routes to a reference file:
- (1) → `references/empty-states/taxonomy.md`
- (2) → `references/empty-states/visual-patterns.md`
- (3) → `references/empty-states/copy-patterns.md`
- (4) → `references/charts/revenue-specifics.md`

Main thread synthesizes answer from the four sources.

**Why this matters**: without decomposition, the main thread might answer from memory + one reference file → misses the revenue-specific considerations because empty-states/taxonomy.md doesn't cover them.

## Worked example C: narrow task decomposition (refactor)

**Ask**: "Refactor app-shell.templates.css so iframes fill available space."

**Decomposition** (Shape B — task, small-scale):

- (1) **Inventory** the current iframe rules. Output: list of existing selectors + their behaviors.
- (2) **Identify the seams**: where does prose layout end and iframe-fill-mode begin? Output: named conditions ("body contains only iframe" vs "body contains prose content").
- (3) **Design the conditional selector**: `:has()` vs explicit attribute opt-in. Output: CSS rule draft.
- (4) **Apply** the rule and verify it doesn't regress prose layout. Output: edited file.
- (5) **Smoke test** in a real browser context. Output: observed behavior report.

Sequential: 1 → 2 → 3 → 4 → 5. No parallelism opportunity. Coverage check: all of 1-5 together = "refactor complete + verified" ✅.

## Anti-patterns

### Decomposition theater

**Bad**: "Step 1: Understand the problem. Step 2: Think about it. Step 3: Solve it."

These aren't sub-asks; they're a restatement with numbers. A real decomposition has sub-asks each with concrete input/output/success criterion.

### Over-decomposition

**Bad**: an atomic 5-line edit decomposed into 8 sub-asks with 6 hand-offs.

If the sub-ask count exceeds the line count of the change, you're over-decomposing. Coordination cost exceeds the value. Just do the edit.

### Under-decomposition

**Bad**: "Build the skill" as a single sub-ask for a 60-file skill.

Big monolithic sub-asks hide dependencies, obscure parallel opportunities, and produce single massive agent results that are hard to verify. Break it down.

### Decomposition before ingestion

**Bad**: user sends ambiguous prompt → main thread skips steelmanning + concept-matching, jumps straight to "let me decompose this into 5 sub-asks".

The decomposition will be beautifully structured — and aimed at the wrong target. Ingest first. Then decompose.

### Fake parallelism

**Bad**: "Sub-asks A, B, C all run in parallel" — but B's input is A's output.

If B needs A's output, they're sequential, not parallel. Don't call it parallel because it looks more impressive in the plan. Hidden sequential dependencies cause cascading failures.

### Decomposition without coverage check

**Bad**: propose sub-asks A, B, C, D → execute → discover 3 turns later that an aspect of the ask wasn't covered.

The coverage check (step 4) is cheap. Always do it. "If I execute all sub-asks and nothing else, is the ask complete?"

### Decomposition inflation

**Bad**: propose a 5-wave, 12-sub-ask decomposition for what turns out to be a 30-minute task.

The decomposition should match the ask's real scale, which depends on ingestion. If the ask is a 30-minute job, the decomposition is 2-4 sub-asks with clear ordering. Not 12.

### Silent re-decomposition mid-execution

**Bad**: announce a decomposition → start executing → realize mid-way the decomposition was wrong → silently re-decompose without telling the user.

If the decomposition needs revision, say so. "The initial decomposition missed X; revised plan: ...". The user should see the updated plan, not discover it from the output.

## Composition with ingestion

Full invocation phase for a non-trivial ask:

1. **Steelman** the prompt → is there a stronger shape?
2. User confirms shape.
3. **Concept-match** the confirmed domain → what does the base model know?
4. User confirms the shape + calibration.
5. **Decompose** the confirmed ask into sub-asks with ordering + success criteria.
6. User confirms (for non-trivial asks) or proceed (for smaller ones).
7. Execute.

Four reads on the ask, each building on the prior:

- **Steelmanning** = what shape should the output have?
- **Concept-matching** = what do I already know about that shape's content?
- **Decomposition** = how do I split the execution into tractable parts?
- **Execution** = do the parts, compose the whole.

Every skill in this library — meta-skills, produced skills, typed tools, utility skills — does all four. The ingestion-decomposition-execution triad is **the invocation contract**, not a meta-skill ornament.

## Decomposition in skills that don't produce more skills

For **produced skills** (expert-dashboard, expert-typography, expert-color), decomposition takes Shape C — question decomposition. Each skill's SKILL.md should include an **Invocation** section that documents:

- How the skill decomposes incoming questions into sub-questions.
- Which sub-questions route to which reference files.
- What the synthesis pattern is across reference files.

This makes the skill's routing logic legible to the user (and to future-you reading the skill in 6 months) instead of implicit in the main thread's judgment.

For **typed skills** (meta-skill-typed, ui-build-tokens, ui-decomp-legacy), decomposition is encoded in the schema — the input schema's fields ARE the decomposition of what the skill needs to know. The SKILL.md's Invocation section documents how the typed invocation maps to the schema.

For **utility skills** (viz-2x2, token-cleanup), decomposition is Shape B — task decomposition — and should be documented as a sub-ask list in the skill's main body.

**Rule**: every skill's SKILL.md has an Invocation section that makes its ingestion + decomposition discipline explicit. See `../structure/skeleton-files.md` for the template.

## One short invariant

**Ingest before decomposing; decompose before executing; verify coverage; declare ordering; don't fake parallelism; don't decompose what's atomic.**
