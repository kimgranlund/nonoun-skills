---
date: 2026-04-18
coverage: deep
peers:
  - ../methodology/axis-identification.md
  - ../methodology/verification-discipline.md
  - ../structure/skeleton-files.md
  - ../examples/color-expert-case-study.md
primary_sources:
  - expert-color (skill library, 148 files across 3 axes)
  - expert-typography (skill library, capability mode exemplar)
  - expert-dashboard (skill library, capability mode exemplar)
---

# Canon-curation mode

Expert skills come in two genres. This file distinguishes them and describes when to pick the second one.

## The two modes

| Dimension | **Capability mode** | **Canon-curation mode** |
|---|---|---|
| Exemplars | expert-typography, expert-dashboard | expert-color |
| What a file IS | One topic / task / decision | One authoritative source, summarized |
| Axis shape | Presentation / capability / substrate | Temporal / instrumental (history / current / tools) |
| SKILL.md role | Task→reference routing + cheat sheets | "Greatest hits" — corrections + non-obvious facts |
| Axis count | 8-15 | 2-4 |
| File count | 60-120 | 50-200 |
| Files per axis | 5-10 | 20-75 |
| SKILL.md length | 200-300 lines | 150-250 lines, denser |
| Primary-source pattern | Many URLs per file | One authoritative source per file |
| Research pattern | Synthesize topics across sources | Collect authoritative sources and summarize each |
| Domain example | Typography, SaaS dashboards, iOS development | Color theory, music theory, philosophy of mind |

Both modes use the same wave arc, agent-dispatch pattern, bookkeeping protocol, and verification discipline. They differ in **what a reference file is** and **how axes are organized**.

## When to pick canon-curation mode

Pick canon-curation when ALL of these are true:

1. **The domain has a deep canon** — named theorists, foundational papers, historical figures, canonical books, talks at established conferences. The practitioner's job is to know the canon.

2. **The base model already has strong priors.** A Claude-tier model already knows a lot about color theory, music theory, or cognitive science. The skill's job isn't to teach from scratch — it's to correct misconceptions, highlight non-obvious findings, and point at authoritative sources.

3. **Authoritative sources exist and are citable.** Papers on arxiv, books with DOIs, talks on YouTube with archive.org mirrors, academic preprints. If the domain's knowledge is mostly tribal / practitioner-folklore with no citable canon, canon-curation won't work.

4. **Topic-organized synthesis would duplicate the canon badly.** Writing "how to think about warm vs cool colors" as a synthesized topic file steals from Briggs, Ottosson, and Ostwald — better to summarize each directly.

Pick capability mode if any of:
- The domain is about **choosing and comparing practitioner tools** (fonts, dashboard components, web-component libraries).
- The canon is shallow or implicit (every SaaS product has its own conventions; there is no "canonical" dashboard thinker).
- The skill's primary question shape is "how do I do X?" or "which X for case Y?" not "what did X think?"

## Canonical axis model for canon-curation

Three axes by default (expert-color's model):

- **historical/** — Pre-digital / pre-current-state-of-the-art. The ancestors the canon cites.
- **contemporary/** — Current-state theory and science. Active researchers, recent papers, modern frameworks.
- **techniques/** — Tools, libraries, methods. The practical application layer.

Alternative axis splits (pick what fits the domain):

- **figures/ + schools/ + works/** — For philosophy or critical theory.
- **movements/ + composers/ + analyses/** — For music history.
- **papers/ + talks/ + books/** — Pure source-type organization.
- **canon/ + critiques/ + extensions/** — When the canon has well-documented critiques.

The rule: **the axis model should mirror how a practitioner in that domain would organize their own reading list.**

## File shape in canon-curation mode

A reference file in canon-curation mode is the skill's summary of one authoritative source. Structure:

```markdown
# [Source title — author or primary speaker]

**Source:** [URL, preferably rot-resistant — archive.org, Gutenberg, DOI, arxiv]
**Author / Speaker:** [name, role/affiliation]
**Date / Year:** [publication or recording date]
**Duration / Length:** [for videos / books]
**License:** [if relevant]

[Single-paragraph framing — what the source is, why it's in the canon, what makes it load-bearing.]

---

## 1. [Main claim / argument / finding]

[Dense summary of the section, with direct quotes for distinctive phrasings.]

### [Sub-topic]

[Sub-summary.]

## 2. [Next main claim]

...

## Key distinctions / corrections

[What this source corrects, contradicts, or sharpens vs the common priors the base model carries.]

## Cross-references

- [Other canon-file] — [how they relate]
- [Other canon-file] — ...

## Where to dig further

[Follow-up reading / primary material this source points at.]
```

Differences from capability-mode reference files:
- No decision tables — the file is **exposition of one source**, not synthesis.
- "Key distinctions / corrections" section is mandatory — this is where the skill's value lives.
- YAML frontmatter is OPTIONAL in strict canon-curation mode; inline `**Source:** / **Author:**` headers are also acceptable (expert-color's convention).
- Anti-patterns section is omitted (it's the source's job to critique, not this file's).

## SKILL.md doctrine: "greatest hits"

In canon-curation mode, SKILL.md is concise (150-250 lines) and structured around:

1. **Decision tables for picks the base model tends to get wrong.** Color spaces (OKLCH vs HSL), hue-to-degree mapping, chroma-vs-saturation distinction — all in expert-color's SKILL.md because Claude-the-base-model tends to default to HSL and conflate chroma/saturation.

2. **Corrections to common misconceptions.** "HSL isn't bad but here's what it can't do." Not tutorials — corrections.

3. **Pointers to the canon axes.** "For deeper work, see `references/historical/`, `references/contemporary/`, `references/techniques/` and INDEX.md for 148 files."

4. **No task→reference routing table.** The canon doesn't map to tasks cleanly. Instead use a SHORT anchor table (expert-color has a "Color Spaces — What to Use When" table with 11 rows, not a full task routing).

Capability mode's SKILL.md routes the user to the topic file; canon-curation mode's SKILL.md is itself the topic-level summary, with the canon as backing material.

## Waves in canon-curation mode

The 5-wave arc still applies but each wave's work is different:

| Wave | Capability mode | Canon-curation mode |
|---|---|---|
| Scoping | Axis list + topic file list | Canon survey: authoritative figures, papers, books, talks |
| W1 | Cross-axis foundations (shell, KPI, palette, etc.) | Foundational canon (Newton, Munsell, Albers, Helmholtz in color) |
| W2-4 | Axis depth | Batches of sources to summarize (15-25 sources per wave) |
| W5 | Phase-2 axes | Techniques/tools layer — the practical application |

Agents in canon-curation waves receive briefs like:
> "Author 3 reference files summarizing these authoritative sources: [source URL 1], [source URL 2], [source URL 3]. Each file summarizes one source per the template in `references/structure/reference-file-template.md` (canon-curation variant). Frontmatter: `Source: URL`, `Author: name`, `Date: YYYY`. Dense summary. Key distinctions / corrections section mandatory. If the source is a YouTube video, include archive.org backup URL when available."

Different from capability-mode briefs (which specify a topic and ask for synthesis).

## Primary-source durability: archive.org discipline

Canon-curation skills link to sources that must survive. Rules:

1. **Prefer rot-resistant URLs when they exist:** archive.org, Gutenberg, arxiv, DOI, official institutional sites with long-term commitments.
2. **Always include archive.org mirror for YouTube / blog / personal-site sources.** Add it at capture time — retrofitting after link-rot is hard.
3. **Download PDFs locally and gitignore them.** Commit the `references/` file with the citation; the PDF is a local cache.
4. **Test every URL in the INDEX at the end of each wave.** Dead links get marked and fixed before v1.0.0.

See `verification-discipline.md` § "Rot-resistant sources" for the full protocol.

## Mixing modes

A skill can be predominantly one mode with an axis in the other mode — expert-color's `techniques/` axis is more capability-mode (Culori, Spectral.js, APCA) than canon-curation. This is fine as long as each axis is internally consistent.

Don't mix modes within a single file. A file is either "summarize this source" or "synthesize this topic," not both.

## Publishing trappings

Canon-curation skills often target public publication (agentskills.io, GitHub). If so, add:

- `LICENSE` — MIT or CC-BY is typical.
- `README.md` — consumer-facing overview (distinct from SKILL.md).
- `MAINTENANCE.md` — how the skill is kept fresh.
- `ROADMAP.md` — what's next.
- `THIRD_PARTY_NOTICES.md` — license attributions for embedded quotes.
- `evals/` — test prompts that validate the skill triggers correctly.

These are NOT produced by the wave arc. Add them manually before public release. See `expert-color/` as exemplar.

## Anti-patterns specific to canon-curation mode

- **Writing a "topic" file in canon-curation mode.** If you find yourself writing "how OKLCH works" as a synthesis, stop — write a summary of Ottosson's OKLAB paper instead, and the synthesis lives in SKILL.md.
- **Over-synthesis in SKILL.md.** SKILL.md corrects and points; it doesn't re-derive the canon.
- **YouTube-only citations without archive.org.** Videos disappear. Mirror at capture time.
- **Padding with topics the canon doesn't cover.** If no authoritative source treats X, don't fake coverage — note the gap in `techniques/` or skip it.

## Validation: "would a domain practitioner recognize the canon here?"

The test: ask a person who's spent 10+ years in the domain whether the reference list covers the load-bearing canon. If they say "you're missing Briggs / Ottosson / Albers" for color, add those. If they say "this is the canon," you're done.

Capability mode's equivalent test is "can a practitioner answer their next 20 questions from this skill?" — different test, different shape.
