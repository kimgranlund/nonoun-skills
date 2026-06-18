---
name: tool-stress
description: >
  Orchestrates a full multi-technique stress-test/eval CAMPAIGN against any system — code, library,
  API, pipeline, config, or artifact. Composes research-survey techniques (adversarial → ablation →
  sweep → hill-climb → autoresearch, with bisect as a regression safety net) into one campaign that
  builds a scoring harness, discovers bugs, removes dead weight, tunes parameters, and polishes to a
  target score. Use when the user says: "stress test this", "find everything wrong", "harden this",
  "evaluate quality", "break it and fix it", "run a full eval", "get this to 95%", "audit this
  codebase". NOT for running a SINGLE technique on its own (research-survey); NOT for designing or
  reviewing an MCP server's tool perimeter — schemas, permissions, tool-selection
  (core-mcp-best-practices); NOT for GRADING one fixed artifact against a rubric — code-decomposer
  (a function), regex-decomposer,
  query-decomposer, type-decomposer, config-decomposer; NOT for behavioral eval cases for a skill
  (skills-studio).
---

# Stress-Eval — Systematic Quality Campaign

Orchestrate a multi-technique evaluation session that discovers defects, removes waste,
optimizes parameters, and iterates to a target quality score. This skill composes individual
research-survey techniques into a coherent campaign with defined phases, scoring, and exit criteria.

This skill is **system-agnostic**. It works on any artifact that can be measured: a library,
an API, a UI, a pipeline, a prompt, a configuration, a model, or a process.

---


## Invocation

This is an **evaluation** skill. The user wants to stress-test a system — code, API, pipeline, or configuration. Decompose: (1) identify the failure modes, (2) design stress scenarios, (3) execute, (4) report degradation curves.

### Step 1 — Ingestion

Classify the target:
- "Stress-test my API" → latency + throughput under load; identify saturation points
- "Evaluate this pipeline" → bottleneck identification; back-pressure behavior
- "Test this config" → parameter-space exploration; find breaking points
- "Benchmark this library" → comparison against alternatives; variance analysis

### Step 2 — Decomposition

| Sub-task | Method |
|---|---|
| Baseline measurement | Stable-state performance before any stress |
| Load ramp | Gradual increase until degradation or failure |
| Spike test | Sudden burst; measure recovery time |
| Soak test | Sustained moderate load; detect memory leaks or drift |
| Chaos injection | Random failures; measure resilience |

### Step 3 — Execution routing

Every test produces a degradation curve: performance metric vs load. Report the inflection point (where performance stops being linear), the failure point (where the system errors), and the recovery behavior. Pair with `research-survey` for root-cause analysis of discovered failure modes.


## Prerequisites

This skill assumes access to a set of research-survey techniques. The user should provide a
reference to their research-survey skill or equivalent. The campaign uses up to six techniques:

| Technique    | Role in campaign                                    |
|-------------|-----------------------------------------------------|
| Adversarial  | Find what breaks (probing, edge cases, stress)      |
| Ablation     | Find what's unnecessary (component contribution)    |
| Sweep        | Find optimal values (parameter exploration)         |
| Hill Climb   | Find best combination (neighborhood search)         |
| Autoresearch | Polish to target (iterative single-change optimize) |
| Bisect       | Safety net (root-cause any regressions introduced)  |

If the user's research-survey skill has reference files for these techniques, read them before
executing the corresponding phase.

---

## Phase 0: Campaign Setup

Before running any technique, establish the campaign's foundation.

### Step 0.1 — Define the System

Identify what's being evaluated. Be specific:

```
System: {name and version}
Scope: {what's included — files, modules, endpoints, configs}
Boundary: {what's excluded — dependencies, infrastructure, external services}
```

### Step 0.2 — Define the Scorer

Every technique in the campaign shares a single scoring rubric. Without a scorer,
nothing is measurable and no technique can run.

Design a **weighted rubric** with 4-6 dimensions that cover the system's quality axes.
Each dimension gets a weight (total = 100) and a measurement method.

Template:

```
╔══════════════════════════════════════════════════════╗
║  SCORING RUBRIC                                      ║
╠══════════════════════════════════════════════════════╣
║  Dimension         Weight  Measurement                ║
║  ─────────         ──────  ───────────                ║
║  {dimension_1}     {w1}    {how to measure}           ║
║  {dimension_2}     {w2}    {how to measure}           ║
║  {dimension_3}     {w3}    {how to measure}           ║
║  {dimension_4}     {w4}    {how to measure}           ║
║  {dimension_5}     {w5}    {how to measure}           ║
║                                                      ║
║  Total: 100                                          ║
║  Target: {target_score}                              ║
╚══════════════════════════════════════════════════════╝
```

Common dimension patterns by system type:

**For code/libraries:**
Correctness, Memory safety, Edge-case survival, Performance, Code minimality

**For APIs/services:**
Correctness, Error handling, Latency, Security, Contract compliance

**For prompts/AI systems:**
Accuracy, Consistency, Edge-case handling, Efficiency (tokens), Safety

**For configurations:**
Correctness, Robustness, Simplicity, Performance impact, Maintainability

**For pipelines:**
Throughput, Error recovery, Data integrity, Resource efficiency, Observability

### Step 0.3 — Build the Test Harness

Create an automated (or semi-automated) way to score the system. This is the most
important artifact of the campaign — every technique depends on it.

The harness should:
1. **Run fast** — You'll invoke it dozens of times. Keep it under 30 seconds.
2. **Be deterministic** — Same system state → same score. Flaky tests poison every technique.
3. **Cover every rubric dimension** — Each dimension needs at least one test.
4. **Output a structured score** — Not just pass/fail. Return the rubric breakdown.

Harness strategies by system type:

| System type | Harness approach |
|------------|-----------------|
| Code/library | Unit tests + stress tests + size check |
| API/service | Integration tests + load test + contract validator |
| Prompt/AI | Eval dataset + judge rubric + token counter |
| Config | Validation suite + performance benchmark |
| Pipeline | End-to-end test + chaos injection + throughput bench |
| UI | Browser automation + interaction probes (Depth 4+) + screenshot diff |

**For browser-based systems:** Build standalone HTML test files that import the system,
run a battery of tests, and print structured results to a `<pre>` element. This enables
automated scoring via browser preview tools.

### Step 0.4 — Score Baseline

Run the harness against the current system state. Record the baseline.

```
╔══════════════════════════════════════╗
║  BASELINE — Round 0                 ║
╠══════════════════════════════════════╣
║  Score: {score}/{max}               ║
║  Target: {target}                   ║
║  Weakest: {dimension} ({points})    ║
║                                     ║
║  Breakdown:                         ║
║    {dim1}: {score1}/{weight1}       ║
║    {dim2}: {score2}/{weight2}       ║
║    ...                              ║
╚══════════════════════════════════════╝
```

### Step 0.5 — Confirm with User

Present the rubric, harness, and baseline. Get confirmation before entering the campaign
loop. The user may want to adjust weights, add dimensions, or change the target.

---

## Phase 1: Campaign Loop

Execute techniques in a specific order. Each technique feeds the next.

```
┌─────────────────┐
│  1. ADVERSARIAL  │  Find defects. Fix them. Re-score.
│     (attack)     │
└────────┬────────┘
         │ defects fixed, score improved
         ▼
┌─────────────────┐
│  2. ABLATION     │  Find dead weight. Remove it. Re-score.
│     (simplify)   │
└────────┬────────┘
         │ waste removed, system leaner
         ▼
┌─────────────────┐
│  3. SWEEP        │  Find optimal parameters. Apply best. Re-score.
│     (explore)    │
└────────┬────────┘
         │ parameters tuned
         ▼
┌─────────────────┐
│  4. HILL CLIMB   │  Find best implementation. Apply winner. Re-score.
│     (optimize)   │  (Optional — only if multiple viable alternatives exist)
└────────┬────────┘
         │ best combination applied
         ▼
┌─────────────────┐
│  5. AUTORESEARCH │  Polish remaining weaknesses. One change at a time. Re-score.
│     (polish)     │
└────────┬────────┘
         │ target reached (or plateau)
         ▼
┌─────────────────┐
│  6. BISECT       │  Available throughout as regression safety net.
│     (diagnose)   │  Invoke if any technique introduces a failure.
└─────────────────┘
```

### Why This Order

1. **Adversarial first** — No point optimizing a broken system. Find and fix defects
   before measuring anything else. Defect fixes often improve multiple dimensions at once.

2. **Ablation second** — After fixing defects, check if the system has unnecessary
   complexity. Removing dead weight simplifies every subsequent technique (fewer parameters
   to sweep, fewer alternatives to climb, fewer things to polish).

3. **Sweep third** — With a clean, minimal system, explore parameter values. The sweep
   maps the scoring landscape and identifies which knobs actually matter.

4. **Hill climb fourth** (optional) — If the sweep reveals multiple viable alternatives
   (not just parameter values but structural choices), hill climb finds the best
   combination. Skip this if the system has no meaningful structural alternatives.

5. **Autoresearch last** — The final polish. The system is now correct, minimal, and
   well-tuned. Autoresearch targets the weakest remaining dimension one change at a time,
   iterating toward the target score.

6. **Bisect on demand** — If any technique introduces a regression (score drops on a
   previously-passing dimension), stop and bisect to find the exact change that caused it.

### Between Each Technique

After each technique completes:

1. **Snapshot** — Save the current system state (git commit, file copy, checkpoint).
   This enables bisection if a later technique introduces a regression.

2. **Re-score** — Run the full harness. Record the score.

3. **Print transition card:**
   ```
   ╔══════════════════════════════════════════════╗
   ║  {TECHNIQUE} → {NEXT_TECHNIQUE}              ║
   ╠══════════════════════════════════════════════╣
   ║  Score: {prev} → {current} ({delta:+d})      ║
   ║  Changes: {count} kept, {count} reverted      ║
   ║  Snapshot: {reference}                        ║
   ╚══════════════════════════════════════════════╝
   ```

4. **Check exit conditions:**
   - Score ≥ target → **exit campaign** (target reached)
   - Score decreased → **invoke bisect** before continuing
   - User requests stop → **exit campaign** (user halt)

5. **Confirm next technique** — Tell the user which technique is next and why.
   Let them skip, reorder, or repeat if they want.

---

## Phase 2: Technique Execution

Each technique follows the protocol defined in the research-survey skill's reference files.
This section provides campaign-specific guidance for how to scope each technique.

### 1. Adversarial

**Goal:** Maximize the Edge-case survival dimension. Side-effect: often improves
Correctness and Memory safety too.

**Scoping the attack surface:**

Start by categorizing the system's inputs, states, and boundaries:

```
Attack Surface Inventory:
  Inputs:      {list all entry points — API params, user actions, config values}
  States:      {list lifecycle states — init, running, error, cleanup, idle}
  Boundaries:  {list module boundaries — where data crosses from one domain to another}
  Resources:   {list finite resources — memory, connections, file handles, DOM nodes}
  Timing:      {list timing-sensitive operations — async, concurrent, batched}
```

For each category, design probes that target the edges:

| Category | Probe pattern |
|----------|--------------|
| Inputs | Empty, null, max-length, wrong type, special chars, injection |
| States | Invalid transitions, interrupted operations, rapid cycling |
| Boundaries | Type confusion at interfaces, contract violations, missing fields |
| Resources | Leak detection (create/destroy cycles), exhaustion (volume tests) |
| Timing | Race conditions, rapid sequential calls, out-of-order delivery |

**Building probe files:**

Create standalone test files (one per category or one combined) that:
1. Import/instantiate the system under test
2. Execute a battery of probes
3. Classify each result: CRASH / CORRUPT / DEGRADE / SURVIVE
4. Print structured results

**Probe depth levels — the Static vs. Interactive trap:**

Every probe must be classified by depth. A common failure mode is marking a feature
as passing based on shallow checks when the actual bug is in the interaction layer.

```
DEPTH 1 — Existence:  "Does the element exist in the DOM?"
DEPTH 2 — Content:    "Does it have the right text/attributes/children?"
DEPTH 3 — Wiring:     "Is the JS connected? Are event listeners attached?"
DEPTH 4 — Interaction: "When I click/type/hover, does the expected thing happen?"
DEPTH 5 — Round-trip:  "Does the full user flow work? (action → state change → DOM update)"
```

**MANDATORY RULE: Never mark an interactive feature as passing based on Depth 1-2 alone.**

If a page has buttons, inputs, toggles, or any interactive element, the probe MUST
include at least one Depth 4 check: trigger the interaction and assert the outcome.

Examples of the trap:
- Page loads, button exists, text is correct → DEPTH 2 PASS, but clicking does nothing (wiring bug)
- Setup module runs without error, trait connects → DEPTH 3 PASS, but uses wrong API (contract bug)
- Counter shows "0" → DEPTH 2 PASS, but clicking "→ 100" doesn't animate (event dispatch bug)

The fix: for every page with interactive elements, write at least one probe that:
1. Triggers the primary interaction (click, type, dispatch event)
2. Waits for the expected async result (animation, fetch, state change)
3. Asserts the DOM changed as expected

**For browser-based UI systems specifically:**

When testing a batch of N pages (e.g., 44 trait demos), don't just sweep for
"does it load." Build a per-page interaction spec:

```js
// Per-page interaction probes
{
  page: '/traits/count-up',
  interactions: [
    { action: 'click', selector: '#to100' },
    { wait: 1500 },
    { assert: { selector: '#counter', textContent: '100' } }
  ]
}
```

If writing per-page specs for every page is too expensive, at minimum:
- **Categorize pages** by interaction type (click-to-trigger, form-input, hover-effect, auto-animate)
- **Sample test** at least 1 page per category at Depth 4+
- **Flag untested pages** as "Depth 2 only" in the report — never claim 100% if interaction wasn't verified

**Fix-as-you-go:** When a probe finds a bug at medium severity or above, fix it before
continuing. Re-run the probe to verify. This keeps the system in a testable state.

**Multiple rounds:** If Round 1 finds and fixes bugs, run Round 2 with deeper probes
that target the areas around the fixes. New fixes often expose adjacent weaknesses.

### 2. Ablation

**Goal:** Maximize the Code minimality dimension (or equivalent). Confirm every component
earns its place.

**Inventory strategy:**

List every removable component. The granularity depends on the system:

| System type | Component granularity |
|------------|----------------------|
| Code | Functions, branches, error handlers, utility helpers |
| Config | Flags, options, rules, middleware entries |
| Prompt | Rules, examples, persona instructions, format constraints |
| Pipeline | Stages, filters, transformers, validators |

**For each component:**
1. Disable it (comment out, set to no-op, remove from config)
2. Run the harness
3. Record: `contribution = baseline_score - ablated_score`
4. Restore it

**Classify results:**
- **Essential** (contribution > 5%): Keep. Cannot remove.
- **Helpful** (contribution 1-5%): Keep. Contributes meaningfully.
- **Inert** (contribution ~0%): Candidate for removal.
- **Harmful** (contribution < 0): Remove immediately — it's hurting the score.

**Decision:** Remove inert and harmful components. The system gets smaller and every
remaining component is justified.

### 3. Sweep

**Goal:** Improve Performance and Correctness by finding optimal parameter values.

**Identify sweepable parameters:**

Look for values that are currently hardcoded or defaulted but could be different:
- Thresholds, limits, timeouts, buffer sizes
- Algorithm choices (sort strategy, hash function, cache policy)
- Scheduling strategies (immediate vs batched vs deferred)
- Resource allocation (pool size, concurrency limit, retry count)

**For each parameter:**
1. Define a range informed by research-survey (don't sweep blindly)
2. Hold all other parameters at baseline
3. Test each value in the range
4. Record (value, score)
5. Identify the optimal value and sensitivity

**Apply:** Set each parameter to its optimal value. Re-score to confirm the
combination is better than baseline (interactions between parameters can surprise).

### 4. Hill Climb (Optional)

**Goal:** Find the best structural combination when multiple viable implementations exist.

**Skip this technique if:**
- The system has no meaningful structural alternatives
- The sweep already found the optimum
- Time is limited and autoresearch will suffice

**When to use:**
- Multiple algorithms could solve the same problem
- Multiple architectural patterns are viable
- The system has design choices (not just parameter values) that could go either way

### 5. Autoresearch

**Goal:** Reach the target score by fixing the weakest dimension one change at a time.

**Entry condition:** The system is correct, minimal, and well-tuned. This is the final
polish pass — not the place for structural changes.

**Round structure:**
1. Score → identify weakest dimension → propose ONE change → apply → re-score
2. If score improved: keep. If dropped: revert.
3. Repeat until target or plateau.

**Exit conditions:**
- Score ≥ target for 2 consecutive rounds
- 5 consecutive reverts (stuck — the approach needs rethinking)
- All dimensions are within 2 points of their maximum

### 6. Bisect (On Demand)

**Goal:** Isolate the exact change that caused a regression.

**Invoke when:**
- A score dimension drops after a technique completes
- A previously-passing test now fails
- The system behaves differently than expected after changes

**Requires:** Snapshots from Phase 1's between-technique checkpoints.

---

## Phase 3: Campaign Report

After the campaign loop exits (target reached, plateau, or user halt), produce the
final report.

```
╔══════════════════════════════════════════════════════════════╗
║  STRESS-EVAL CAMPAIGN COMPLETE                               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  System: {name}                                              ║
║  Techniques executed: {count}/{total}                        ║
║                                                              ║
║  SCORING                                                     ║
║    Baseline:  {baseline_score}/100                           ║
║    Final:     {final_score}/100 (+{delta})                   ║
║    Target:    {target} — {reached|not reached}               ║
║                                                              ║
║  DIMENSION BREAKDOWN                                         ║
║    {dim1}:  {before} → {after} ({delta:+d})                  ║
║    {dim2}:  {before} → {after} ({delta:+d})                  ║
║    {dim3}:  {before} → {after} ({delta:+d})                  ║
║    ...                                                       ║
║                                                              ║
║  TECHNIQUE RESULTS                                           ║
║    Adversarial: {probes_run} probes, {bugs_found} bugs fixed ║
║    Ablation:    {components} tested, {removed} removed       ║
║    Sweep:       {parameters} swept, {applied} optimized      ║
║    Hill Climb:  {rounds} rounds, {moves} moves applied       ║
║    Autoresearch: {rounds} rounds, {kept}/{total} kept        ║
║    Bisect:      {invocations} (regression safety)            ║
║                                                              ║
║  CHANGES SUMMARY                                             ║
║    Defects fixed:        {count}                             ║
║    Dead code removed:    {count} lines                       ║
║    Parameters optimized: {count}                             ║
║    Structural changes:   {count}                             ║
║    Polish changes:       {count}                             ║
║                                                              ║
║  REMAINING GAPS                                              ║
║    {gap_1}: {why it wasn't fixed} — {severity}               ║
║    {gap_2}: {why it wasn't fixed} — {severity}               ║
║                                                              ║
║  ARTIFACTS                                                   ║
║    Test harness: {location}                                  ║
║    Stress tests: {location}                                  ║
║    Snapshots:    {locations}                                 ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Principles

These apply across all techniques and all system types:

1. **Measure before and after every change.** No change is "obviously" good. The scorer
   is the only source of truth.

2. **One variable at a time.** Within each technique, isolate changes to attribute cause.
   Between techniques, snapshot to enable bisection.

3. **Fix before optimizing.** Adversarial and ablation come before sweep and hill climb.
   Don't tune a broken or bloated system.

4. **The harness is the most important artifact.** A campaign is only as good as its
   scorer. Invest in the harness early — every technique depends on it.

5. **Research before guessing.** Each technique's reference file mandates a research-survey
   phase. Use web search to ground every decision in prior art. The best probes come
   from studying real-world failures, not random fuzzing.

6. **Stop when stuck.** Repeated failures or plateaus mean the approach needs rethinking,
   not more rounds. Surface this to the user.

7. **Log everything.** Every probe, every score, every keep/revert decision. The campaign
   log is the artifact that makes the work reproducible and auditable.

8. **The user decides.** Present findings and recommendations. Confirm before applying
   changes. Never auto-chain techniques without consent.

9. **Test at the interaction layer, not just the existence layer.** A page that loads
   is not a page that works. If the system under test has interactive elements (buttons,
   inputs, animations, event-driven behaviors), probes MUST trigger the interaction and
   assert the outcome. Checking that a button exists and has the right label is Depth 2.
   Clicking the button and verifying the result is Depth 4. Never report a passing score
   for interactive features based on Depth 1-2 checks alone. When sweeping N pages,
   either test every page at Depth 4+ or explicitly flag which pages were only checked
   at Depth 2 — never claim full coverage from existence checks.

10. **Read the source before writing the probe.** When testing generated code (setup
    modules, adapters, glue code), read both the source file AND the API it calls.
    A setup module can execute without error yet use the wrong API entirely (e.g.,
    setting a data attribute when the trait expects a CustomEvent). The probe must
    verify the contract between caller and callee, not just that the caller runs.

---

## Quick Start

If the user says "stress test this" or "run a full eval" without further context:

1. Ask: "What's the system?" (if not obvious from context)
2. Ask: "What does quality mean for this system?" (to inform the rubric)
3. Ask: "What's your target score?" (default: 95/100)
4. Build the rubric and harness
5. Score baseline
6. Present the campaign plan
7. Execute on confirmation

If the user provides a reference to their research-survey skill:
- Read the skill's reference files for each technique before executing that phase
- Follow the technique's protocol exactly, scoped by this campaign's rubric and harness
