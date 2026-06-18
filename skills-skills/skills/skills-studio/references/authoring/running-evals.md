---
date: 2026-05-06
---

# Running and Evaluating Test Cases

The complete eval workflow from test case creation through viewer launch and feedback capture. This is one continuous sequence — don't stop partway through.

Put results in `<skill-name>-workspace/` as a sibling to the skill directory. Within the workspace, organize by iteration (`iteration-1/`, `iteration-2/`, etc.) and each test case gets a directory (`eval-0/`, `eval-1/`, etc.). Create directories as you go.

---

## Step 1: Spawn All Runs in the Same Turn

For each test case, spawn two subagents in the same turn — one with the skill, one without. Launch everything at once so it all finishes around the same time.

**With-skill run:**

```
Execute this task:
- Skill path: <path-to-skill>
- Task: <eval prompt>
- Input files: <eval files if any, or "none">
- Save outputs to: <workspace>/iteration-<N>/eval-<ID>/with_skill/outputs/
- Outputs to save: <what the user cares about — e.g., "the .docx file", "the final CSV">
```

**Baseline run** (same prompt, but the baseline depends on context):

- **Creating a new skill**: no skill at all. Same prompt, no skill path, save to `without_skill/outputs/`.
- **Improving an existing skill**: the old version. Before editing, snapshot the skill (`cp -r <skill-path> <workspace>/skill-snapshot/`), then point the baseline subagent at the snapshot. Save to `old_skill/outputs/`.

Write an `eval_metadata.json` for each test case. Give each eval a descriptive name based on what it's testing — not just "eval-0". If this iteration uses new or modified eval prompts, create fresh metadata files — don't assume they carry over.

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-here",
  "prompt": "The user's task prompt",
  "assertions": []
}
```

## Step 2: Draft Assertions While Runs Are In Progress

Don't wait for runs to finish. Draft quantitative assertions for each test case and explain them to the user. If assertions already exist in `evals/evals.json`, review them and explain what they check.

Good assertions are objectively verifiable and have descriptive names — they should read clearly in the benchmark viewer so someone glancing at results immediately understands what each one checks. Subjective skills (writing style, design quality) are better evaluated qualitatively — don't force assertions onto things that need human judgment.

Update `eval_metadata.json` and `evals/evals.json` with the assertions once drafted.

## Step 3: Capture Timing Data as Runs Complete

When each subagent task completes, the notification contains `total_tokens` and `duration_ms`. Save this immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This is the only opportunity to capture this data — it comes through the task notification and isn't persisted elsewhere.

## Step 4: Grade, Aggregate, and Launch the Viewer

Once all runs are done:

### 4a. Grade each run

Spawn a grader subagent (or grade inline) that reads `agents/grader.md` and evaluates each assertion against the outputs. Save results to `grading.json` in each run directory.

The `grading.json` expectations array must use the fields `text`, `passed`, and `evidence` (not `name`/`met`/`details` or other variants) — the viewer depends on these exact field names.

For assertions that can be checked programmatically, write and run a script rather than eyeballing it — scripts are faster, more reliable, and reusable across iterations.

### 4b. Aggregate into benchmark

Run the aggregation script from the `skills-studio` directory:

```bash
python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <n>
```

This produces `benchmark.json` and `benchmark.md` with pass_rate, time, and tokens for each configuration, with mean ± stddev and the delta. Put each `with_skill` version before its baseline counterpart.

If generating `benchmark.json` manually, see `references/schemas.md` for the exact schema the viewer expects.

### 4c. Analyst pass

Read the benchmark data and surface patterns the aggregate stats might hide. See `agents/analyzer.md` (the "Analyzing Benchmark Results" section) for what to look for:

- Assertions that always pass regardless of skill (non-discriminating)
- High-variance evals (possibly flaky)
- Time/token tradeoffs

### 4d. Launch the viewer

```bash
nohup python <ultraskill-path>/eval-viewer/generate_review.py \
  <workspace>/iteration-N \
  --skill-name "my-skill" \
  --benchmark <workspace>/iteration-N/benchmark.json \
  > /dev/null 2>&1 &
VIEWER_PID=$!
```

For iteration 2+, also pass `--previous-workspace <workspace>/iteration-<N-1>`.

Use `generate_review.py` to create the viewer — don't write custom HTML.

Tell the user something like: "I've opened the results in your browser. There are two tabs — 'Outputs' lets you click through each test case and leave feedback, 'Benchmark' shows the quantitative comparison. When you're done, come back here."

## What the User Sees in the Viewer

The "Outputs" tab shows one test case at a time:

- **Prompt**: the task that was given
- **Output**: the files the skill produced, rendered inline where possible
- **Previous Output** (iteration 2+): collapsed section showing last iteration's output
- **Formal Grades** (if grading was run): collapsed section showing assertion pass/fail
- **Feedback**: a textbox that auto-saves as they type
- **Previous Feedback** (iteration 2+): their comments from last time

The "Benchmark" tab shows stats: pass rates, timing, and token usage for each configuration, with per-eval breakdowns and analyst observations.

Navigation: prev/next buttons or arrow keys. When done, "Submit All Reviews" saves all feedback to `feedback.json`.

## Step 5: Read the Feedback

When the user tells you they're done, read `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback means the user thought it was fine. Focus improvements on test cases where the user had specific complaints.

Kill the viewer server when done:

```bash
kill $VIEWER_PID 2>/dev/null
```

When ready to improve the skill based on feedback, read `references/improving-skills.md`.

---

## Advanced: Blind Comparison

For rigorous comparison between two skill versions (e.g., "is the new version actually better?"), read `agents/comparator.md` and `agents/analyzer.md`. The basic idea: give two outputs to an independent agent without telling it which is which, and let it judge quality. Then analyze why the winner won.

This is optional, requires subagents, and most users won't need it. The human review loop is usually sufficient.

## How Skill Triggering Works (context for writing eval queries)

Skills appear in Claude's `available_skills` list with their name + description. Claude decides whether to consult a skill based on that description. Claude only consults skills for tasks it can't easily handle on its own — simple, one-step queries like "read this PDF" may not trigger a skill even if the description matches perfectly, because Claude can handle them directly.

This means eval queries should be substantive enough that Claude would actually benefit from consulting a skill. Simple queries like "read file X" are poor test cases — they won't trigger skills regardless of description quality.
