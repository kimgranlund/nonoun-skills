---
date: 2026-05-06
---

# Creating Skills

The full workflow from "I want a skill for X" to a complete draft ready for testing.

> **Build against the standard.** Before drafting, read `build-against-the-standard.md` — it maps each holistic dimension (D1–D10) to the **foundation** you build it from, the **rubric** it gets scored with, the **ship-gate**, and the **critic** who will red-team it. This skill scores and critiques against that same library, so build to it from the start rather than retrofitting after a failing scorecard. Pull the foundation for each dimension the skill actually has as you write that part (D7 from `../foundations/security-foundations.md`, D5 from `eval-foundations.md`, …).

---

## Step 1: Capture Intent

Start by understanding the user's intent. The current conversation might already contain a workflow the user wants to capture (e.g., "turn this into a skill"). If so, extract answers from the conversation history first — the tools used, the sequence of steps, corrections the user made, input/output formats observed.

Questions to answer (the user may need to fill gaps):

1. What should this skill enable Claude to do?
2. When should this skill trigger? (what user phrases/contexts)
3. What does a good output look like? (the shape — format, structure, quality bar)
4. **What does a bad output look like?** (the anti-patterns — what must never happen)
5. Should we set up test cases to verify the skill works?

Question 4 is critical. Anti-patterns drive the most useful instructions — they define the boundaries of acceptable behavior. "Never present a menu of options without a recommendation" is more useful than "be helpful." Ask this even if the user doesn't volunteer it: "What's the one thing this skill should absolutely never do?"

For question 5: skills with objectively verifiable outputs (file transforms, data extraction, code generation, fixed workflow steps) benefit from test cases. Skills with subjective outputs (writing style, art) often don't need them. Suggest the appropriate default based on the skill type, but let the user decide.

## Step 2: Interview and Research

Proactively ask questions about edge cases, input/output formats, example files, success criteria, and dependencies. Wait to write test prompts until you've got this part ironed out.

Check available MCPs — if useful for research-survey (searching docs, finding similar skills, looking up best practices), research-survey in parallel via subagents if available, otherwise inline.

### Domain Research (mandatory before writing)

Use web search to ground the skill in external knowledge. This is the single highest-leverage step in skill creation — do it even if the user doesn't ask.

1. **Search for prior art** — Has someone built a similar tool or methodology? What patterns exist in this domain? What do experts consider quality?
2. **Search for failure modes** — What goes wrong? Common mistakes, user complaints, known pitfalls the skill should prevent?
3. **Search for scoring approaches** — How do others measure quality? Existing rubrics, checklists, evaluation criteria that could inform assertions?
4. **Compile a reference sheet** — 3-5 authoritative sources. These inform the skill's instructions, examples, and opinionated defaults. Cite them in the skill or its changelog when a design choice is grounded in research-survey.

This phase typically takes 2-4 web searches and produces the foundational knowledge that separates a generic skill from an expert one.

## Step 3: Write the SKILL.md

Based on the interview, fill in the skill. Read `references/skill-template.md` for a concrete template with slots — copy it and fill it in rather than starting blank.

### Frontmatter

**Harness-read fields (required):**

- **name**: Skill identifier (kebab-case). Must match the directory name.
- **description**: When to trigger, what it does (max 1024 chars). This is the primary triggering mechanism — include both what the skill does AND specific contexts for when to use it. All "when to use" info goes here, not in the body.

  Claude has a tendency to "undertrigger" skills — to not use them when they'd be useful. To combat this, make descriptions a little "pushy." Instead of "How to build a dashboard," write "How to build a dashboard. Use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of data, even if they don't explicitly ask for a 'dashboard.'"

All other metadata lives in `skill.json` — see `references/skill-template.md` for the full template and field reference.

### Skill Anatomy

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description only)
│   └── Markdown instructions
├── skill.json (required — manifest with version, authors, tags, files)
├── CHANGELOG.md (required — version history)
├── ROADMAP.md (required — Planned / Deferred / Out of scope; may be empty)
└── Bundled Resources (optional)
    ├── scripts/    - Executable code for deterministic/repetitive tasks
    ├── references/ - Docs loaded into context as needed
    └── assets/     - Files used in output (templates, icons, fonts)
```

### Progressive Disclosure

Skills use a three-level loading system:

1. **Metadata** (name + description) — Always in context (~100 words)
2. **SKILL.md body** — In context whenever skill triggers (<500 lines ideal)
3. **Bundled resources** — As needed (unlimited, scripts execute without loading)

Keep SKILL.md under 500 lines. If approaching this limit, add a reference file layer with clear pointers about where the model should go next.

**Domain organization**: When a skill supports multiple domains/frameworks, organize by variant and read only the relevant reference file:

```
cloud-deploy/
├── SKILL.md (workflow + selection)
└── references/
    ├── aws.md
    ├── gcp.md
    └── azure.md
```

## Writing Guide

### Voice and Style

Prefer the imperative form in instructions. Explain to the model _why_ things are important rather than using heavy-handed MUSTs. Use theory of mind and try to make the skill general, not super-narrow to specific examples. Start by writing a draft and then look at it with fresh eyes and improve it.

### Structural Elements That Make Skills Great

Not every skill needs all of these, but consider each when drafting:

**First Principles section (strongly recommended).** 3-5 foundational truths that govern the skill. These are the "why" behind every instruction. When a model encounters an ambiguous situation, first principles give it a framework for reasoning rather than a rule to memorize. Write them as opinionated statements with explanations, not bland "best practices."

Good: "Constraints before creativity. Every design decision is a response to a constraint. If you don't know the constraints, you're decorating, not designing."

Bad: "Always follow best practices and industry standards."

**When NOT to use section (recommended for complex skills).** Explicitly tell the model when to back off. The description should be pushy (to prevent under-triggering), but the body should know its limits. This builds trust and prevents the skill from being invoked for tasks it handles poorly.

**Worked example (recommended for non-obvious workflows).** A condensed walkthrough showing the skill's full pipeline on a concrete case. Not a toy example — a realistic scenario that demonstrates real complexity, including edge cases and decision points. Worked examples are the single largest teachability multiplier.

**Opinionated defaults (recommended).** Skills that make recommendations outperform skills that present menus. When the skill has to choose between approaches, state a default and the reasoning. Users can override, but they should have to justify it.

**Output format templates.** If the skill produces a structured output, include a concrete template with slots rather than describing the format in prose. The consuming agent copies the template and fills it in — zero inference required.

**Anti-patterns section.** Explicitly state what the skill must never do. These negative examples often teach more effectively than positive ones because they define the boundary between acceptable and unacceptable behavior.

### When to Extract Reference Files

Reference files (`references/*.md`) are for content that:

- Is too long for SKILL.md (which should stay under 500 lines)
- Is domain-specific and only needed for certain branches of the skill's logic
- Contains catalogs, taxonomies, decision trees, or lookup tables
- Would clutter the main instruction flow if inline

**Rule of thumb:** If a section of SKILL.md is > 60 lines and is only relevant to one sub-task, it's a reference file. Point to it with: "Read `references/X.md` for the full Y."

Reference files can be long (200-600 lines) because they're loaded on demand. Include a table of contents if > 300 lines.

Common reference file types:

- Decision trees (pattern selection, technology choice)
- Catalogs (violation types, gap classifications, drift taxonomy)
- Templates (output formats, scoring rubrics, report structures)
- Domain knowledge (API references, standards, best practices compilations)
- Worked examples (if the example is > 40 lines)

### Defining Output Formats

```markdown
## Report structure
ALWAYS use this exact template:
# [Title]
## Executive summary
## Key findings
## Recommendations
```

### Examples Pattern

Include concrete examples. Format them clearly:

```markdown
## Commit message format
**Example 1:**
Input: Added user authentication with JWT tokens
Output: feat(auth): implement JWT-based authentication
```

### Principle of Lack of Surprise

Skills must not contain malware, exploit code, or any content that could compromise system security. A skill's contents should not surprise the user in their intent if described. Don't create misleading skills or skills designed to facilitate unauthorized access, data exfiltration, or other malicious activities.

## Step 4: Write Test Cases

After writing the skill draft, come up with 2-3 realistic test prompts — the kind of thing a real user would actually say. Share them with the user: "Here are a few test cases I'd like to try. Do these look right, or do you want to add more?"

Save test cases to `evals/evals.json`. Don't write assertions yet — just the prompts. You'll draft assertions later while runs are in progress.

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

See `references/schemas.md` for the full schema (including the `assertions` field).

When ready to run the test cases, read `references/running-evals.md`.
