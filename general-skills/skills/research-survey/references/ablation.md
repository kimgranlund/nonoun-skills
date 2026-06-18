---
date: 2026-05-06
---

# Ablation Study — Contribution Measurement by Removal

Systematically remove or disable components to measure their individual contribution. Answers: "What happens if we remove X?"

## Input

$ARGUMENTS — What to ablate. Can be:
- A system with multiple components (e.g., "the scoring checks", "the pipeline stages")
- A file with multiple independent parts
- A configuration with many options or flags
- A prompt or template with multiple rules or sections
- Default: identify the most complex multi-component configuration in the current working context

## Configuration

- **MAX_ROUNDS**: 100 (override with "max N rounds" in arguments)
- **BASELINE_RUNS**: 3 (run baseline N times and average for stability)

## Phase -1: Research (MANDATORY)

Before starting, use web search to gather authoritative references on the system being ablated. This ensures you understand the theoretical contribution of each component before measuring it empirically.

1. **Search for theory** — Which components of this type of system are considered most important by practitioners? What does the literature say about their relative value?
2. **Search for benchmarks** — What quality metrics or evaluation frameworks exist for this domain?
3. **Search for ablation studies** — Have others done similar component-removal studies? What did they find?
4. **Compile predictions** — Before running, predict which components are essential vs. inert based on research-survey. Compare predictions to results in the final report.

This phase prevents ablating blindly. External research-survey tells you what SHOULD matter; your ablation tells you what ACTUALLY matters.

## Phase 0: Inventory

1. **List all components** — Enumerate every removable piece. For a scorer: each check. For a prompt: each rule. For a config: each option. For a pipeline: each stage.
2. **Run baseline** — Score with everything enabled. Run BASELINE_RUNS times and average.
3. **Print inventory:**
   ```
   ╔══════════════════════════════════════╗
   ║  ABLATION STUDY — {system}          ║
   ╠══════════════════════════════════════╣
   ║  Components: {count}                ║
   ║  Baseline: {avg_score} (n={runs})   ║
   ╚══════════════════════════════════════╝
   ```

## Phase 1: Single Ablations

For each component (up to MAX_ROUNDS):

### Step 1 — Disable one component
Remove or disable a single component while keeping everything else unchanged.

### Step 2 — Score
Run the same scorer/test. Record the score.

### Step 3 — Calculate contribution
`contribution = baseline_score - ablated_score`
- Positive contribution → this component helps
- Zero contribution → this component is inert (candidate for removal)
- Negative contribution → this component hurts (removing it improves the score)

### Step 4 — Restore
Re-enable the component before the next iteration.

### Step 5 — Print result
```
Ablate {component}: {baseline} → {ablated} (contribution: {delta:+d})
  Verdict: {essential|helpful|inert|harmful}
```

## Phase 2: Interaction Effects (optional)

If time permits, test pairwise removals for the top 5 most impactful components to check for interaction effects (two components that individually help but together are redundant).

## Phase 3: Report

```
╔════════════════════════════════════════════════════╗
║  ABLATION STUDY COMPLETE                           ║
╠════════════════════════════════════════════════════╣
║  Essential (removing hurts >5%):                   ║
║    1. {component} — contribution: +{score}         ║
║  Helpful (removing hurts 1-5%):                    ║
║    1. {component} — contribution: +{score}         ║
║  Inert (no effect):                                ║
║    1. {component} — contribution: 0                ║
║  Harmful (removing helps):                         ║
║    1. {component} — contribution: -{score}         ║
╠════════════════════════════════════════════════════╣
║  Recommendation:                                   ║
║    Remove: {inert + harmful components}            ║
║    Keep: {essential + helpful components}           ║
║    Net improvement: +{projected_delta}             ║
╚════════════════════════════════════════════════════╝
```

## Rules

- **Disable ONE component per round** — never remove multiple simultaneously (that's Phase 2)
- **Always restore before next round** — ablation is non-destructive
- **Average baseline** — run baseline multiple times for stable comparison
- **Sort by impact** — present results from most impactful to least
- **Test interactions** — two "inert" components may be redundant with each other
- **Propose action** — don't just report; recommend what to remove
- **Web search on ambiguity** — When a component's contribution is near zero and you can't tell if it's truly inert or just hard to measure, use web search to research-survey whether that component is considered important in the industry. Let external evidence break the tie between "remove" and "keep".
