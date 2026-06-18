---
date: 2026-05-06
---

# Hill Climb — Greedy Local Optimization

Explore the neighborhood of the current solution. Try every possible single-step change, pick the best one, move there, repeat. Unlike autoresearch (which fixes the weakest check), hill climbing tries ALL options and picks the winner.

## Input

$ARGUMENTS — What to optimize. Can be:
- A file to refactor or improve
- A configuration to tune
- A design or layout to iterate
- A parameter space with discrete alternatives to compare
- Default: the most recently edited file or artifact

## Configuration

- **MAX_ROUNDS**: 100 (override with "max N rounds" in arguments)
- **PLATEAU_LIMIT**: 3 (stop after N rounds with no improvement)
- **NEIGHBORHOOD_SIZE**: 5 (try up to N alternatives per round)

## Phase -1: Research (MANDATORY)

Before starting, use web search to gather authoritative references on the optimization domain. This expands your neighborhood — you can only propose changes you know about.

1. **Search for alternatives** — What approaches exist for this type of problem? What are the trade-offs between them?
2. **Search for patterns** — What do established frameworks, guidelines, or standards recommend?
3. **Search for state of the art** — What are the highest-quality examples in this domain? What makes them good?
4. **Build a moves catalog** — List possible optimizations informed by research-survey. This becomes your neighborhood generator for Phase 1.

This phase ensures your hill climb explores informed moves, not random tweaks. The best local optimum is only as good as your move vocabulary.

## Phase 0: Baseline

1. **Identify the artifact** and **scorer** (same as autoresearch).
2. **Run baseline score.**
3. **Enumerate the move space** — What are the possible single-step changes? Examples:
   - For code: refactor a function, change an algorithm, adjust a threshold
   - For a prompt: add a rule, remove a rule, strengthen a rule, add an example
   - For a config: toggle a flag, change a threshold, swap an implementation
   - For a structure: rearrange sections, change hierarchy, swap approaches

## Phase 1: Loop

For each round (1 to MAX_ROUNDS):

### Step 1 — Generate neighborhood
Propose NEIGHBORHOOD_SIZE different single-step changes. Each must be independent (not building on each other).

### Step 2 — Try each neighbor
For each proposed change:
1. Apply the change
2. Score
3. Record the score
4. Revert

### Step 3 — Pick the best
Select the neighbor with the highest score. If no neighbor improves on the current score, this is a **plateau**.

### Step 4 — Apply the winner
If the best neighbor improved the score, apply it permanently. If plateau, increment plateau counter.

### Step 5 — Check exit conditions
- Plateau counter ≥ PLATEAU_LIMIT → **stop (local optimum reached)**
- Score ≥ target → **stop (target reached)**
- Round = MAX_ROUNDS → **stop (max rounds)**

### Step 6 — Print round card
```
Round {n}: tried {count} neighbors
  Best: "{description}" → {score} (+{delta})
  Others: "{desc}" ({score}), "{desc}" ({score}), ...
  Status: {applied|plateau {count}/{limit}}
```

## Phase 2: Report

```
╔══════════════════════════════════════════════════╗
║  HILL CLIMB COMPLETE                             ║
╠══════════════════════════════════════════════════╣
║  Baseline: {baseline}                            ║
║  Final: {final} (+{total_delta})                 ║
║  Rounds: {rounds} ({total_neighbors} tried)      ║
║  Path:                                           ║
║    R1: {change} (+{d})                           ║
║    R2: {change} (+{d})                           ║
║    R3: plateau (local optimum)                   ║
╚══════════════════════════════════════════════════╝
```

## Rules

- **Try multiple alternatives per round** — this is the key difference from autoresearch
- **Always revert between neighbors** — each is tested against the same baseline
- **Apply only the winner** — not the second-best, not a combination
- **Track what was tried** — the rejected neighbors inform future rounds
- **Stop at plateaus** — if 3 rounds find no improvement, you're at a local optimum
- **Consider restarts** — if stuck, try a random larger change to escape the local optimum
- **Web search on plateaus** — When all neighbors score the same, you can't think of new moves, or multiple alternatives tie, STOP and use web search to research-survey novel approaches to the specific problem. External knowledge generates new neighbors you wouldn't have thought of. Search before restarting randomly.
