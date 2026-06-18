---
date: 2026-05-06
---

# Environment-Specific Guides

Adaptations for environments that differ from the default Claude Code workflow. Read this when you detect you're in Claude.ai or Cowork, then apply the relevant overrides to the standard workflow from the other reference files.

---

## Claude.ai

In Claude.ai, the core workflow is the same (draft → test → review → improve → repeat), but some mechanics change because Claude.ai doesn't have subagents.

### Running test cases

No subagents means no parallel execution. For each test case, read the skill's SKILL.md, then follow its instructions to accomplish the test prompt yourself. Do them one at a time. This is less rigorous than independent subagents (you wrote the skill and you're also running it, so you have full context), but it's a useful sanity check — and the human review step compensates.

Skip baseline runs — just use the skill to complete the task as requested.

### Reviewing results

If you can't open a browser (no display, remote server), skip the browser reviewer entirely. Instead, present results directly in the conversation. For each test case, show the prompt and the output. If the output is a file (docx, xlsx, etc.), save it to the filesystem and tell them where to download and inspect it.

Ask for feedback inline: "How does this look? Anything you'd change?"

### Benchmarking

Skip quantitative benchmarking — it relies on baseline comparisons which aren't meaningful without subagents. Focus on qualitative feedback.

### The iteration loop

Same as before — improve the skill, rerun test cases, ask for feedback — just without the browser reviewer. You can still organize results into iteration directories.

### Description optimization

Requires `claude -p` (CLI tool), only available in Claude Code. Skip it in Claude.ai.

### Blind comparison

Requires subagents. Skip it.

### Packaging

The `package_skill.py` script works anywhere with Python and a filesystem. On Claude.ai, run it and the user can download the resulting `.skill` file.

### Updating an existing skill

The user might ask you to update an existing skill, not create a new one. In this case:

- **Preserve the original name.** Note the skill's directory name, `name` frontmatter field, and `name` in skill.json — all three must stay in sync.
- **Bump the version.** Update `version` in skill.json and add a CHANGELOG.md entry for the changes. Update the `files` array if files were added/removed.
- **Copy to a writeable location before editing.** The installed skill path may be read-only. Copy to `/tmp/skill-name/`, edit there, package from the copy.
- **If packaging manually, stage in `/tmp/` first**, then copy to the output directory — direct writes may fail due to permissions.

---

## Cowork

If you're in Cowork, the main things to know:

### What works

- You have subagents, so the main workflow (spawn test cases in parallel, run baselines, grade, etc.) all works. If you run into severe timeout problems, run test prompts in series rather than parallel.
- `package_skill.py` works — just needs Python and a filesystem.
- Description optimization (`run_loop.py` / `run_eval.py`) should work since it uses `claude -p` via subprocess. Save it until the skill is fully finished and the user agrees it's in good shape.

### What's different

- No browser or display. When generating the eval viewer, use `--static <output_path>` to write a standalone HTML file instead of starting a server. Then share the link so the user can open it in their browser.
- Feedback works differently: the viewer's "Submit All Reviews" button downloads `feedback.json` as a file. Read it from the Downloads folder (you may need to request access first).

### Critical reminder

Generate the eval viewer using `generate_review.py` BEFORE evaluating outputs yourself. Get results in front of the human ASAP. Don't skip this step — it's the most important part of the feedback loop. Use `generate_review.py`, not custom HTML.

### Updating an existing skill

Same guidance as Claude.ai above — preserve the original name and copy to a writeable location before editing.
