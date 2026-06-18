---
date: 2026-05-06
---

# Autoresearch — Iterative Single-Change Optimization

Run → score → identify weakest dimension → change ONE thing → re-run → keep if better, revert if worse → repeat.

Based on Andrej Karpathy's autoresearch pattern: let the agent experiment autonomously, keeping only changes that improve the score. One change per round, measured impact, and a changelog of what worked.

## Input

$ARGUMENTS — What to optimize. Can be:
- A file path to the artifact being improved
- A benchmark or test identifier
- A prompt describing the optimization target
- A test command to measure quality
- Default: the most recently edited file or the artifact identified in problem analysis

## Configuration

- **MAX_ROUNDS**: 100 (override with "max N rounds" in arguments)
- **TARGET_SCORE**: 95 (override with "target N" in arguments)
- **CONSECUTIVE_PASSES**: 2 (stop after hitting target N times in a row)

## Phase -1: Research (MANDATORY)

Before touching anything, use web search to gather authoritative references on the domain being optimized. This grounds every subsequent decision in established knowledge, not guesses.

1. **Search for best practices** — What does the industry consider quality in this domain? What are the accepted standards and guidelines?
2. **Search for known issues** — What are common pitfalls, bugs, or failure patterns in this type of system?
3. **Search for prior art** — How have others solved similar optimization problems? What scoring rubrics or quality metrics exist?
4. **Compile a reference sheet** — 3-5 authoritative sources that inform the optimization strategy. Cite them in the changelog when a change is inspired by external knowledge.

This phase ensures you're not optimizing in a vacuum.

## Phase 0: Baseline

1. **Identify the artifact** — What are we optimizing? A file, a test suite, a configuration, a prompt, a model, a process?
2. **Identify the scorer** — How do we measure quality? Options:
   - An existing test suite (pass rate)
   - A benchmark command (numeric score)
   - A custom metric (lines of code, latency, bundle size, accuracy, etc.)
   - A manual checklist (if no automated scorer, define 5-10 yes/no checks)
   - An LLM-as-judge rubric (for subjective quality)
3. **Run the scorer** — Record the baseline score, breakdown, and any failing checks.
4. **Print baseline card:**
   ```
   ╔══════════════════════════════════════╗
   ║  AUTORESEARCH — Round 0 (Baseline)  ║
   ╠══════════════════════════════════════╣
   ║  Score: {score}/{max}               ║
   ║  Target: {target}                   ║
   ║  Weakest: {check} ({points} pts)    ║
   ╚══════════════════════════════════════╝
   ```

## Phase 1: Loop

For each round (1 to MAX_ROUNDS):

### Step 1 — Identify weakest dimension
Look at the score breakdown. Find the check with the lowest score (or the first failing check). This is the focus for this round.

### Step 2 — Propose ONE change
Based on the weakest check, propose a single, targeted change. Be specific:
- Name the exact thing being changed and how
- State the expected impact on the weak dimension
- Bad: "improve quality" — Good: "add input validation for empty strings in the parse function"

### Step 3 — Apply the change
Make the edit. Keep it minimal — one concept per round.

### Step 4 — Re-score
Run the same scorer. Record the new score.

### Step 5 — Keep or revert
- **If score improved or stayed the same** → KEEP the change. Log it.
- **If score dropped** → REVERT the change. Log the revert. Try a different approach next round.

### Step 6 — Check exit conditions
- Score ≥ TARGET_SCORE for CONSECUTIVE_PASSES rounds → **stop (target reached)**
- Round = MAX_ROUNDS → **stop (max rounds)**
- Score = max possible → **stop (perfect)**
- 5 consecutive reverts → **stop (stuck)** — report what was tried

### Step 7 — Print round card
```
Round {n}: {prev_score} → {new_score} ({delta:+d})
  Change: {description}
  Status: {kept|reverted}
  Weakest remaining: {check}
```

## Phase 2: Report

After the loop ends, print the final report:

```
╔══════════════════════════════════════════════════╗
║  AUTORESEARCH COMPLETE                           ║
╠══════════════════════════════════════════════════╣
║  Baseline: {baseline_score}                      ║
║  Final:    {final_score} ({delta:+d})            ║
║  Rounds:   {total_rounds}                        ║
║  Kept:     {kept_count}                          ║
║  Reverted: {reverted_count}                      ║
╠══════════════════════════════════════════════════╣
║  Changes that stuck:                             ║
║    1. {change_description} (+{delta})            ║
║    2. {change_description} (+{delta})            ║
║  Reverted (didn't help):                         ║
║    1. {change_description} ({delta})             ║
╚══════════════════════════════════════════════════╝
```

## Rules

- **ONE change per round** — never batch multiple fixes
- **Always measure** — never assume a change helped without scoring
- **Revert immediately** — if the score drops, undo before the next round
- **Log everything** — every round's change, score, and keep/revert decision
- **Don't repeat** — if a change was reverted, try a different approach, not the same thing again
- **Be specific** — vague changes ("improve quality") are not actionable
- **Stop when stuck** — 5 consecutive reverts means the approach needs rethinking, not more rounds
- **Web search on poor signal** — When the score is flat, multiple changes tie, you're unsure which check to target next, or you've reverted 2+ times in a row, STOP and use web search to research-survey the specific problem. Let external knowledge break the tie before burning more rounds guessing.
