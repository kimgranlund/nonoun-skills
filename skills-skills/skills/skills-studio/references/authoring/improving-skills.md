---
date: 2026-05-06
---

# Improving Skills

How to think about improvements, the iteration loop, self-improvement, and adversarial hardening.

---

## How to Think About Improvements

1. **Generalize from the feedback.** You're iterating on a few examples to move fast, but the skill will be used across many different prompts. If the skill only works for the test cases, it's useless. Rather than fiddly overfitting changes or oppressively constrictive MUSTs, try branching out with different metaphors or recommending different patterns of working. It's cheap to experiment.

2. **Keep the prompt lean.** Remove things that aren't pulling their weight. Read the transcripts, not just the final outputs — if the skill is making the model waste time on unproductive steps, cut those parts and see what happens.

3. **Explain the why.** Try hard to explain the **why** behind everything. Today's LLMs have good theory of mind and when given a good harness can go beyond rote instructions. Even if the user's feedback is terse or frustrated, understand the task and why they wrote what they wrote, then transmit this understanding into the instructions. If you're writing ALWAYS or NEVER in all caps, that's a yellow flag — reframe and explain the reasoning so the model understands why it matters.

4. **Look for repeated work across test cases.** Read the transcripts from test runs and notice if the subagents all independently wrote similar helper scripts or took the same multi-step approach. If all 3 test cases resulted in the subagent writing a `create_docx.py` or a `build_chart.py`, that's a strong signal the skill should bundle that script. Write it once, put it in `scripts/`, and tell the skill to use it.

Take your time. Write a draft revision, then look at it with fresh eyes and improve it. Get into the head of the user and understand what they want and need.

## The Iteration Loop

After improving the skill:

1. Apply your improvements
2. Rerun all test cases into a new `iteration-<N+1>/` directory, including baseline runs. If creating a new skill, the baseline is always `without_skill` (no skill) — that stays the same across iterations. If improving an existing skill, use your judgment on what makes sense as the baseline.
3. Launch the reviewer with `--previous-workspace` pointing at the previous iteration
4. Wait for the user to review
5. Read the new feedback, improve again, repeat

Keep going until:

- The user says they're happy
- The feedback is all empty (everything looks good)
- You're not making meaningful progress

After each meaningful improvement round, bump the `version` in `skill.json` (minor for new capabilities, patch for fixes) and add a CHANGELOG.md entry. Update the `files` array in skill.json if any files were added or removed.

## Optional: Self-Improve with Autoresearch

After the user feedback loop converges, you can optionally run a scored self-improvement pass on the skill itself. This uses the autoresearch pattern: score → identify weakest dimension → change one thing → re-score → keep or revert.

Read `references/self-improvement.md` for the full rubric, scoring formula, loop protocol, adversarial probe categories, and CHANGELOG format.

**When to offer this:** When the skill is "good enough" but the user wants it to be great. Or when you notice quality dimensions the user hasn't explicitly addressed (composability, parsimony, teachability).

### Quick summary of the rubric dimensions:

1. **Clarity** (weight 3): Every step unambiguous on first read
2. **Completeness** (weight 3): Every decision point covered
3. **Parsimony** (weight 2): Every sentence earning its place
4. **Opinionatedness** (weight 2): Makes recommendations, not menus
5. **Teachability** (weight 2): Accessible to someone new to the domain
6. **Composability** (weight 1): Integrates cleanly with other skills/tools

Score each 1-5. Composite = weighted average normalized to 0-100. Target: 85/100.

### The autoresearch loop:

1. Score the baseline
2. Identify weakest dimension
3. Propose ONE targeted change
4. Apply and re-score
5. Keep if improved, revert if regressed
6. Repeat (one change per round, stop at target or after 5 consecutive reverts)

This loop typically produces +10 to +30 points of improvement in 3-5 rounds.

## Build-time red-team — summon the critics on your own draft

Before declaring an `author`/`edit` job done, run **`critique`** on the draft you just wrote — the same 9-critic panel `skills-studio` uses to evaluate other skills, turned on your own output. This is the build-side half of the bi-directional loop (see `build-against-the-standard.md`).

- **Floor (every skill, before ship):** `critique single-critic simon` (trust boundary — the most recurring Critical across the library's review campaign) **+** `single-critic wlaschin` (structure, labels, illegal states). Two cheap passes that catch the two highest-frequency failure classes.
- **Escalate to `critique full-panel`** for: pre-v1.0 / `stable` promotion; any skill that **ingests untrusted content** (Simon's lens compounds, and for an orchestrator the fan-out amplifies an injection); or a multi-agent skill.
- **Targeted edit?** Run just the critic(s) who own the dimension you touched (the "Red-team lens" column in `build-against-the-standard.md`).

Self-review relaxes the cold-read rule, but not the adversarial bar: push for ≥1 Critical or document why none exists. **Fold surviving Critical/Major findings back into the draft** before packaging — that is the loop closing on itself.

## Optional: Adversarial-probe categories

After the critic pass, also stress-test the routing surface for failure modes. See `self-improvement.md` for the full probe categories and report format.

Quick summary of probe categories:

- **Trigger confusion:** Prompts that should trigger but might not (indirect phrasing, synonyms, multi-intent requests)
- **Trigger hijack:** Prompts that should NOT trigger but superficially match (adjacent domains, keyword collisions)
- **Instruction ambiguity:** Where could instructions be read two different ways?
- **Dependency failure:** What happens if a referenced file/tool/resource is unavailable? Add fallback instructions.
- **Edge case inputs:** Empty input, extremely long input, wrong format, wrong language

For each failure found: either fix the skill or add it as a documented limitation. New failure modes can become new test cases in evals.json.
