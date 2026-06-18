---
date: 2026-05-06
---

# Sweep — Parameter Space Exploration

Systematically explore a range of values for one or more parameters. Map the scoring landscape to find optimal settings and understand sensitivity.

## Input

$ARGUMENTS — What to sweep. Can be:
- A parameter and range (e.g., "timeout values 100ms-5000ms")
- Multiple parameters (e.g., "batch size 8-64 and learning rate 0.001-0.1")
- A configuration knob (e.g., "retry count 1-10")
- A design or tuning variable (e.g., "temperature 0.0-1.0 for the generation prompt")
- Default: identify tunable parameters in the most recently edited file or configuration

## Configuration

- **MAX_ROUNDS**: 100 (override with "max N rounds" in arguments)
- **GRID_RESOLUTION**: 5 (number of steps per parameter dimension)
- **TOP_K**: 3 (report the top K configurations)

## Phase -1: Research (MANDATORY)

Before defining the parameter space, use web search to gather authoritative references on optimal values. Don't sweep blindly — know what the established ranges are first.

1. **Search for standards** — What do industry guidelines, specifications, or RFCs recommend for these parameter values?
2. **Search for research-survey** — Are there studies, benchmarks, or papers on the effect of these parameters? What ranges did they test?
3. **Search for what others ship** — What default values do popular frameworks, libraries, or products use? What ranges do they expose to users?
4. **Narrow the range** — Use research-survey to set informed min/max bounds. Don't sweep 1-10000 when research-survey says 10-100 covers 95% of useful values.

This phase makes your sweep efficient. External knowledge narrows the parameter space so you test meaningful values, not noise.

## Phase 0: Define Parameter Space

1. **List parameters** — What are we sweeping? Each needs:
   - Name (e.g., "batch_size")
   - Range (e.g., 8-128)
   - Step size (e.g., power of 2) or discrete values (e.g., [8, 16, 32, 64, 128])
   - Unit/type (e.g., "count", "milliseconds", "ratio")
2. **Calculate grid size** — Total combinations = product of steps per parameter. If > MAX_ROUNDS, sample randomly.
3. **Run baseline** — Score with current values.

```
╔══════════════════════════════════════════════╗
║  SWEEP — {description}                       ║
╠══════════════════════════════════════════════╣
║  Parameters: {count}                         ║
║  Grid size: {total_combinations}             ║
║  Rounds: {min(grid_size, MAX_ROUNDS)}        ║
║  Baseline: {score} at {current_values}       ║
╚══════════════════════════════════════════════╝
```

## Phase 1: Single-Parameter Sweeps

For each parameter independently:

### Step 1 — Hold others constant
Keep all other parameters at their baseline values.

### Step 2 — Iterate through range
For each value in the parameter's range:
1. Set the parameter to this value
2. Score
3. Record (value, score)
4. Restore to baseline

### Step 3 — Print sweep curve
```
Parameter: {name} (range: {min}-{max}, step: {step})
  {value1}: ████████████░░░░ {score1}
  {value2}: █████████████░░░ {score2}
  {value3}: ████████████████ {score3}  ← best
  {value4}: ██████████░░░░░░ {score4}
  Optimal: {best_value} ({best_score})
  Sensitivity: {low|medium|high}
```

## Phase 2: Multi-Parameter Grid (if 2+ parameters)

Test combinations of the top 3 values for each parameter:

```
              param_b=X  param_b=Y  param_b=Z
param_a=X:     82         88         85
param_a=Y:     85         94         91    ← sweet spot
param_a=Z:     83         90         88
```

## Phase 3: Report

```
╔══════════════════════════════════════════════════╗
║  SWEEP COMPLETE                                  ║
╠══════════════════════════════════════════════════╣
║  Baseline: {score} at {baseline_values}          ║
║  Best: {score} at {best_values} (+{delta})       ║
║                                                  ║
║  Top {K} configurations:                         ║
║    1. {values} → {score}                         ║
║    2. {values} → {score}                         ║
║    3. {values} → {score}                         ║
║                                                  ║
║  Sensitivity analysis:                           ║
║    {param1}: HIGH (±{range} → ±{score_range})    ║
║    {param2}: LOW (±{range} → ±{score_range})     ║
║                                                  ║
║  Recommendation: set {param}={value}             ║
╚══════════════════════════════════════════════════╝
```

## Rules

- **One parameter at a time first** — understand individual effects before testing combinations
- **Always restore** — each test point starts from baseline (no accumulation)
- **Sample if too large** — if grid > MAX_ROUNDS, use random sampling (Latin hypercube or similar)
- **Report sensitivity** — which parameters matter most? Which are flat?
- **Visualize** — use ASCII bar charts for sweep curves
- **Apply the winner** — after the sweep, offer to apply the optimal configuration
- **Web search on surprising results** — When a parameter has an unexpected sweet spot, the curve is non-monotonic, or the optimal value contradicts intuition, STOP and use web search to research-survey why. Understanding WHY a value is optimal is as valuable as knowing WHAT it is.
