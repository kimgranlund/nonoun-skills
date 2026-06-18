---
date: 2026-04-18
coverage: foundational
peers:
  - ../methodology/coverage-tiers-and-frontmatter.md
  - ../methodology/verification-discipline.md
primary_sources:
  - expert-dashboard reference files (typical exemplars)
  - expert-typography reference files
---

# Reference file template

Every reference file follows the same structure. Agents are briefed with this template so output is consistent across the skill.

## Template

```markdown
---
date: 2026-04-18
coverage: <foundational | expanded | deep>
peers:
  - ../[axis]/[peer-1].md
  - ../[axis]/[peer-2].md
primary_sources:
  - <URL or citation>
  - <URL or citation>
---

# [Title — title case, noun phrase]

[One or two sentences framing the file. Who it's for, what question it answers, what it does NOT cover. End the opener with a sentence pointing to the peer file for adjacent concerns.]

## [Section 1 — usually "The [concept]" or "Decision framework"]

[Dense prose. Numbered or bulleted lists when they help; prose paragraphs otherwise.]

## [Section 2 — typically a decision table or matrix]

| [Column 1] | [Column 2] | [Column 3] |
|---|---|---|
| [Row] | [Row] | [Row] |

## [Section 3-7 — topical sub-sections appropriate to the file]

### Sub-topic

Prose.

## Anti-patterns

- **Name the anti-pattern.** One-line description. Why it fails. What to do instead.
- **Anti-pattern.** ...

## Accessibility / compliance [if applicable]

[WCAG 2.2 SC citations, APG pattern references, regulatory obligations. Normative text quoted verbatim from primary sources.]

## Library landscape [if applicable]

| Library | Version as of 2026-04 | Status | Notes |
|---|---|---|---|
| ... | ... | ... | ... |

## Exemplars

[Named products/projects that demonstrate the pattern well. Observable-public-only.]

- **[Product]** — [specific observable behavior, 1-3 sentences]
- **[Product]** — [specific observable behavior, 1-3 sentences]

## Primary sources

[A footer repeating the frontmatter `primary_sources` with inline annotation of what each source backs. Optional but often helpful.]
```

## Section guidelines

### Title

- Noun phrase, title case, short.
- No "How to X" framings — the skill is an answer, not a tutorial.
- Match the file name (converted from kebab-case).

### Opener

Two sentences, not more. First sentence: what the file covers. Second sentence: what it does NOT cover + pointer to the peer file that does.

Good:
> "This file covers real-time UX at the transport and presentation layers — WebSocket / SSE choices, presence indicators, degradation strategies. For the pure async state machine, see `state-and-async/loading-empty-error-success.md`; for chart-specific streaming, see `data-viz/real-time-streaming.md`."

Bad:
> "In this file we will explore the fascinating topic of real-time UX. Dashboards today often need to handle real-time updates…"

### Numbered sections

Sections numbered starting at 1. Each section has a clear topical scope. 7-15 sections is typical for expanded/deep files.

### Tables vs prose

- **Table** when comparison is the primary purpose (4+ items, 3+ dimensions).
- **Bulleted list** when enumeration is the primary purpose.
- **Prose** otherwise.

Don't mix: a paragraph explaining a table is fine; a table embedded mid-paragraph is bad.

### Anti-patterns section

Every file should have one. Format:

> **Anti-pattern name in bold.** One-line description. _Why it fails._ What to do instead.

### Accessibility section

If the file touches any accessibility-relevant concern, include it. Quote WCAG SC text verbatim from `w3.org/TR/WCAG22/`. Cite APG patterns with full URL.

### Primary sources

Every URL the file draws on goes in the frontmatter `primary_sources` list. A footer "Primary sources" section in the body is optional but helpful for longer files.

## Length

| Coverage tier | Typical lines |
|---|---|
| foundational | 250-400 |
| expanded | 400-600 |
| deep | 600-900 |

Files ≥ 900 lines need a table of contents at the top. Files < 250 lines are suspect — consider whether they're really expanded-tier or whether content is missing.

## Tone

- **Dense, factual prose.** No marketing. No filler.
- **Cite everything.** A claim without a URL is a speculation.
- **Use inline code** for keyboard shortcuts, CSS properties, file paths, small identifiers.
- **Avoid emojis.** Only if the user explicitly requests them.
- **Second person for the reader** ("you") is rare; prefer imperative or declarative.
- **Date claims with contemporary context** ("as of 2026-04") for anything time-sensitive.

## Cross-references

When referring to another file in the same skill, use a relative path inline:

> "See `../accessibility/wcag-2-2-for-dashboards.md` for the normative SC quotations."

Or inline link syntax for readability:

> See `../accessibility/wcag-2-2-for-dashboards.md` for normative SC quotations.

When referring to a peer skill, use the skill name + relative path:

> "See `../../ui-sys-typography/references/type-scale.md`."

## Checklist before promoting ⬜ → ✅ in INDEX.md

- [ ] YAML frontmatter complete and correct.
- [ ] `date` is ISO-format.
- [ ] `coverage` tier declared.
- [ ] `peers` paths resolve.
- [ ] `primary_sources` lists ≥ 5 URLs for foundational, ≥ 10 for expanded, ≥ 20 for deep.
- [ ] Title matches file name.
- [ ] Opener has the two-sentence framing.
- [ ] At least one decision table or comparison matrix.
- [ ] Anti-patterns section present.
- [ ] All claims cite primary sources.
- [ ] No fabricated bug IDs, RFC numbers, or commit SHAs.
- [ ] No speculation about product internals (if profiling a product).
