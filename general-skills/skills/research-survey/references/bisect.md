---
date: 2026-05-06
---

# Bisect — Binary Search for Root Cause

Find the exact change that introduced a regression or behavior change. Split the search space in half each round — logarithmic convergence.

## Input

$ARGUMENTS — What to bisect. Can be:
- A regression description (e.g., "output quality dropped after last week's changes")
- A version range (e.g., "v2.1..HEAD", "commit abc..def")
- A file with a known-bad state (e.g., "this config stopped working after the refactor")
- A behavior change (e.g., "the API returns errors that it didn't before")
- Default: diff between current state and the last known-good state

## Configuration

- **MAX_ROUNDS**: 100 (override with "max N rounds" in arguments)
- **MODE**: "git" | "code" | "config" (auto-detected from arguments)

## Phase -1: Research (MANDATORY)

Before bisecting, use web search to gather context on the regression class. This often reveals the root cause faster than blind binary search.

1. **Search for the symptom** — What does this error message or behavior change typically indicate? What are known causes?
2. **Search for known bugs** — Has anyone reported this regression in the tools, libraries, or platforms involved?
3. **Search for the pattern** — What class of change typically introduces this kind of regression? (e.g., dependency updates, config changes, API contract changes)
4. **Form a hypothesis** — Based on research-survey, predict the likely cause before bisecting. This lets you prioritize which half to test first and may eliminate the need for bisection entirely.

This phase can shortcut the entire process. If the web search reveals the exact bug pattern, you can jump straight to the fix.

## Phase 0: Establish Bounds

1. **Identify GOOD state** — The last known working version. Can be:
   - A version control commit, tag, or branch
   - A backup or snapshot
   - A code snippet or config that works
   - "It worked on {date}" → check history for the boundary
2. **Identify BAD state** — The current broken state.
3. **Define the test** — How to tell good from bad:
   - A test that passes/fails
   - A visual or behavioral check
   - A scorer threshold
   - A specific assertion ("endpoint returns 200")
4. **Count the search space** — How many changes/commits/steps between good and bad?

```
╔══════════════════════════════════════╗
║  BISECT — {description}             ║
╠══════════════════════════════════════╣
║  Good: {good_ref}                   ║
║  Bad:  {bad_ref}                    ║
║  Space: {count} steps               ║
║  Est. rounds: {ceil(log2(count))}   ║
╚══════════════════════════════════════╝
```

## Phase 1: Loop

### Git Mode
Use `git bisect` or manual checkout to test the midpoint.

### Code Mode
For a single file with many changes:
1. Start with the full diff between good and bad
2. Apply half the hunks
3. Test
4. If good → the bug is in the other half
5. If bad → the bug is in this half
6. Repeat on the narrowing half

### Config Mode
For configurations with many options:
1. Start with all options at their "bad" values
2. Flip half of them back to "good"
3. Test
4. Narrow to the half containing the regression

### Each Round:
```
Round {n}: testing midpoint ({remaining} candidates left)
  Midpoint: {description}
  Result: {good|bad}
  Narrowed to: {remaining/2} candidates
```

## Phase 2: Report

```
╔══════════════════════════════════════════════════╗
║  BISECT COMPLETE                                 ║
╠══════════════════════════════════════════════════╣
║  Root cause: {exact change/commit/line}          ║
║  Rounds: {n} (of {max possible})                 ║
║  Introduced by: {commit/change description}      ║
║  Fix: {proposed fix}                             ║
╚══════════════════════════════════════════════════╝
```

## Rules

- **Always halve the space** — never test randomly; always pick the midpoint
- **One test per round** — test the midpoint, then narrow
- **Preserve the test** — use the exact same test at every midpoint
- **Log the path** — record every midpoint tested and its result (good/bad)
- **Don't fix during bisect** — find the cause first, fix second
- **Clean state** — ensure each midpoint test starts from a clean state (no leftover artifacts)
- **Web search on inconclusive results** — When a midpoint test is ambiguous (neither clearly good nor bad), or the regression appears intermittent, STOP and use web search to look up the error message or symptom. Known bugs, timing issues, or platform-specific behavior often explain "sometimes fails" results better than more bisecting.
