---
date: 2026-05-06
---

# Description Optimization

The description field in SKILL.md frontmatter is the primary mechanism that determines whether Claude invokes a skill. After creating or improving a skill, offer to optimize the description for better triggering accuracy.

This step requires the `claude` CLI tool (`claude -p`), which is only available in Claude Code. Skip it in Claude.ai.

---

## Step 1: Generate Trigger Eval Queries

Create 20 eval queries — a mix of should-trigger and should-not-trigger. Save as JSON:

```json
[
  {"query": "the user prompt", "should_trigger": true},
  {"query": "another prompt", "should_trigger": false}
]
```

The queries must be realistic — concrete, specific, with detail a real user would include: file paths, personal context, column names, company names, URLs, backstory. Mix lengths. Focus on edge cases rather than clear-cut examples.

Bad: `"Format this data"`, `"Extract text from PDF"`, `"Create a chart"`

Good: `"ok so my boss just sent me this xlsx file (its in my downloads, called something like 'Q4 sales final FINAL v2.xlsx') and she wants me to add a column that shows the profit margin as a percentage. The revenue is in column C and costs are in column D i think"`

### Should-trigger queries (8-10)

Think about coverage. Different phrasings of the same intent — some formal, some casual. Include cases where the user doesn't explicitly name the skill or file type but clearly needs it. Uncommon use cases. Cases where this skill competes with another but should win.

### Should-not-trigger queries (8-10)

The most valuable ones are near-misses — queries that share keywords or concepts with the skill but actually need something different. Adjacent domains, ambiguous phrasing where a naive keyword match would trigger but shouldn't.

Don't make negatives obviously irrelevant. "Write a fibonacci function" as a negative for a PDF skill is too easy. The negative cases should be genuinely tricky.

## Step 2: Review with User

Present the eval set using the HTML template:

1. Read the template from `assets/eval_review.html`
2. Replace placeholders:
   - `__EVAL_DATA_PLACEHOLDER__` → the JSON array (no quotes — JS variable assignment)
   - `__SKILL_NAME_PLACEHOLDER__` → the skill's name
   - `__SKILL_DESCRIPTION_PLACEHOLDER__` → the skill's current description
3. Write to a temp file (e.g., `/tmp/eval_review_<skill-name>.html`) and open it
4. The user can edit queries, toggle should-trigger, add/remove entries, then click "Export Eval Set"
5. The file downloads to `~/Downloads/eval_set.json` — check for the most recent version in case there are multiple

This step matters — bad eval queries lead to bad descriptions.

## Step 3: Run the Optimization Loop

Tell the user: "This will take some time — I'll run the optimization loop in the background and check on it periodically."

Save the eval set to the workspace, then run in the background:

```bash
python -m scripts.run_loop \
  --eval-set <path-to-trigger-eval.json> \
  --skill-path <path-to-skill> \
  --model <model-id-powering-this-session> \
  --max-iterations 5 \
  --verbose
```

Use the model ID from your system prompt so the triggering test matches what the user actually experiences.

While it runs, periodically tail the output to give the user updates on which iteration it's on and what the scores look like.

The loop automatically: splits eval set into 60% train / 40% held-out test, evaluates the current description (3 runs per query for reliable trigger rate), calls Claude to propose improvements based on failures, re-evaluates on both train and test, iterates up to 5 times. It selects `best_description` by test score (not train) to avoid overfitting.

## Step 4: Apply the Result

Take `best_description` from the JSON output and update the skill's SKILL.md frontmatter. Show the user before/after and report the scores.
