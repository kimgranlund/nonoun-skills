---
date: 2026-05-06
---

# Skill Template

Copy this template when starting a new skill. Fill in the slots marked with `{SLOT}`. Delete any optional sections that don't apply. This template embodies the prescriptive-first-with-embedded-knowledge pattern — directives come first, knowledge is embedded as justification.

---

## Template

```markdown
---
name: {skill-name-kebab-case}
description: >
  {What this skill does — 1-2 sentences.} Use whenever the user {specific trigger
  phrases and contexts — be pushy to prevent under-triggering}. Also trigger when
  {indirect phrasings, synonyms, adjacent use cases that should activate this skill}.
  Even partial requests like "{example fragment}" should trigger this skill.
---

# {Skill Display Name}

{1-2 sentence summary of what this skill does and why it exists. Ground it in the
problem it solves, not just the mechanics.}

## First Principles

1. **{Principle name}.** {Opinionated statement explaining a foundational truth that
   governs this skill. Not a bland "best practice" — a specific claim about how the
   domain works and why it matters for the agent's behavior.}

2. **{Principle name}.** {Another foundational truth. 3-5 principles total.}

3. **{Principle name}.** {Each principle should help the agent resolve ambiguous
   situations by reasoning from first principles rather than memorizing rules.}

## When NOT to Use This Skill

- **{Adjacent task the skill shouldn't handle}** — use `{other-skill}` instead.
  {Brief explanation of why the boundary exists.}
- **{Another boundary case}** — {what to do instead}.

## Workflow

### Step 1: {First major phase}

{Prescriptive instructions in imperative voice. Tell the agent what to DO, not
what exists. Embed knowledge as justification for each directive.}

### Step 2: {Second major phase}

{Continue the workflow. Each step should be self-contained enough that the agent
can execute it without reading ahead.}

### Step 3: {Third major phase}

{For complex steps, break into sub-steps. If a sub-task needs > 60 lines of
instruction, extract it to `references/{subtask}.md` and point to it here:
"Read `references/{subtask}.md` for the full {description}."}

## Output Format

{If the skill produces structured output, include a concrete template with slots.
The agent copies this and fills it in — zero inference required.}

```

{Literal template with {SLOT} markers that the agent fills in}

```

## Anti-Patterns (What This Skill Must Never Do)

- **Never {specific failure mode}.** {Why this is bad and what to do instead.}
- **Never {another failure mode}.** {Explanation grounded in first principles.}

## Estimation / Defaults

{Opinionated defaults the skill uses when the user doesn't specify. State the
default and the reasoning. The user can override, but they should have to
justify it — not make the initial choice.}
```

---

## skill.json Template

Every skill must include a `skill.json` manifest alongside SKILL.md. Create this file in the skill root directory:

```json
{
  "name": "{skill-name-kebab-case}",
  "version": "1.0.0",
  "description": "{One-line summary — shorter than SKILL.md description, for catalogs}",
  "status": "draft",
  "authors": ["{your-name}"],
  "codeowners": [],
  "tags": ["{domain-tags}"],
  "depends_on": [],
  "peer_skills": [],
  "files": [
    "SKILL.md",
    "CHANGELOG.md",
    "ROADMAP.md"
  ]
}
```

**Required fields:** `name`, `version`, `description`, `status`, `authors`, `tags`, `files`.

**Optional fields:** `codeowners`, `depends_on`, `peer_skills`, `classification`, `lineage`, `approved_by`, `approved_date`, `pilot`.

**Rules:**

- `name` must match the directory name and SKILL.md `name` field — three-way consistency.
- `files` must list every file in the skill directory (relative paths). Update it whenever you add or remove a file.
- `version` uses semver: patch for typos, minor for new capabilities, major for breaking changes. Must match the latest CHANGELOG.md entry.
- `lineage` should be set when forking a skill (e.g. `"arch-pattern"`).

---

## Checklist Before Finalizing

After filling in the template, verify:

- [ ] **Description is pushy enough.** Would Claude trigger this skill for indirect phrasings and synonyms? If someone asked for the skill's output without naming it, would the description match?
- [ ] **First principles are opinionated.** Each one makes a specific claim, not a generic "best practice." They help resolve ambiguous situations.
- [ ] **Instructions are imperative.** The voice is "Do X" not "X is done" or "You might want to consider X."
- [ ] **Knowledge is embedded, not separate.** Directives include their reasoning inline, not in a separate "Background" section the agent might skip.
- [ ] **Anti-patterns are specific.** Each names a concrete failure mode, not a vague "don't be bad."
- [ ] **SKILL.md is under 500 lines.** Long content is extracted to reference files with clear pointers.
- [ ] **Output format has a template.** If the skill produces structured output, there's a literal template to copy — not just a prose description.
- [ ] **skill.json exists and is consistent.** `name` matches across directory, SKILL.md, and skill.json. `files` array lists all actual files. `version` matches the latest CHANGELOG.md entry.
- [ ] **ROADMAP.md exists** with Planned / Deferred / Out of scope sections. Populate any known out-of-scope decisions now — empty sections are fine, missing file is not.
