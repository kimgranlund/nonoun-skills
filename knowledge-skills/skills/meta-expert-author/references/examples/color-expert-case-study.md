---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/canon-curation-mode.md
  - ../methodology/axis-identification.md
  - ../methodology/verification-discipline.md
  - ./dashboard-expert-case-study.md
  - ./typography-expert-case-study.md
primary_sources:
  - expert-color/SKILL.md (skill library)
  - expert-color/CLAUDE.md
  - expert-color/references/INDEX.md
  - agentskills.io (publication target)
---

# Case study: expert-color

**Canon-curation exemplar.** 148 reference files across 3 axes. Single-genre skill that this meta-skill would previously have failed to produce. Studied here to document what `canon-curation-mode.md` covers.

## Scope

Domain: color theory, color science, color spaces, color definitions, palettes, ramps, gradients, conversions, accessibility, perceptual matching, pigment mixing, print-vs-screen color, CSS color syntax, historical color terminology.

## Axes (3)

1. `historical/` — Pre-digital color science. Ostwald, Helmholtz, Munsell, Albers, Itten, ISCC-NBS, Moses Harris, Ridgway, Birren, Cheskin, etc. ~40 files. Each file summarizes one historical figure / source.

2. `contemporary/` — Modern color science and theory. Björn Ottosson (OKLAB/OKLCH), David Briggs (CSA talks), Mark Fairchild (color appearance models), Schloss & Palmer (color combinations), Koenderink (warm/cool gestalt), plus philosophical sources (color subjectivism), plus nested sub-axes for specific canonical collections (`colorandcontrast/`, `huevaluechroma/`). ~70 files.

3. `techniques/` — Tools, libraries, methods. Culori, Spectral.js / Mixbox (pigment mixing), APCA, CIEDE2000, Kubelka-Munk, palette generation algorithms, Color Universal Design (CUD). ~40 files.

**Total: 148 files** across 3 axes = ~49 files per axis.

## What makes this canon-curation, not capability

1. **Each file summarizes ONE authoritative source.** File names encode the source: `historical/albers-interaction-of-color.md`, `contemporary/bjorn-ottosson-oklab-articles.md`, `contemporary/briggs-colours-objects-light.md`. Not "how-to" topics.

2. **Primary sources are the organizing principle.** The INDEX.md lists every file with a primary-source URL column. The file's value IS the summary of that source.

3. **Temporal/instrumental axis split.** Historical (pre-digital canon) / contemporary (current science) / techniques (tools). No "presentation" or "capability" axis because color doesn't have those — it has thinkers, findings, and implementations.

4. **SKILL.md doctrine: "greatest hits."** Color-expert's own CLAUDE.md says:
   > "SKILL.md should be concise 'greatest hits' (~200 lines) — the agent already has broad color knowledge; the skill should correct misconceptions, highlight non-obvious facts, and point to the right tools."

   SKILL.md contains:
   - Color Spaces decision table (11 rows — "what to use when")
   - HSL's limitations explained (what the base model gets wrong)
   - Named hue ranges (0-360° for red/orange/yellow/etc.)
   - Key distinctions: chroma vs saturation, lightness vs brightness
   - Implementation guidance (semantic layer)

   **No task→reference routing table.** The canon doesn't map to tasks cleanly.

5. **Rot-resistant sources.** Every file cites a durable URL when available — archive.org, Gutenberg, DOI, arxiv, or official institutional site. YouTube talks include archive.org mirrors. PDFs are downloaded locally and gitignored (~236MB) with URLs preserved.

## What would meta-expert-author v1.0 have produced instead?

Running meta-expert-author v1.0 on "expert-color" would have produced:

- SKILL.md with task→reference routing: "choosing a color space → X, building a palette → Y, accessibility → Z."
- 8-12 axes organized by task: `color-spaces/`, `palettes/`, `accessibility/`, `gradients/`, `pigment-mixing/`, `tools/`.
- 60-120 files each about a topic or decision: `color-spaces/oklch-vs-hsl.md`, `palettes/12-step-ramp-generation.md`.
- YAML frontmatter with full `date / coverage / peers / primary_sources` on every file.
- Task→reference routing in SKILL.md.

That would be a **valid** expert-color. It would cover the same use cases. But it would:
- **Duplicate the canon** — writing a "chroma vs saturation" topic file synthesizes from Briggs without citing him directly.
- **Miss the canon-curation value** — the distinctive thing expert-color does is summarize Briggs + Ottosson + Albers + Munsell in their own terms.
- **Shape the skill differently** — task-oriented vs source-oriented.

Both shapes are legitimate. Canon-curation mode exists to enable the second shape.

## Publishing trappings

Color-expert ships publicly on agentskills.io, so it has extra files that capability-mode internal skills don't need:

- `LICENSE` — MIT.
- `README.md` — consumer-facing.
- `MAINTENANCE.md` — keeping it fresh.
- `ROADMAP.md` — what's next.
- `SECURITY.md` — vulnerability reporting.
- `THIRD_PARTY_NOTICES.md` — attributions.
- `evals/` — directory of test prompts.

These are outside the scope of what meta-expert-author produces automatically. Add manually before public release.

## Source-preservation discipline

The canon-curation pattern makes source rot an existential risk. Color-expert's discipline:

- **YouTube Shorts from Color Nerd** (primary channel for many historical summaries) are also saved locally and mirrored to archive.org where possible.
- **CSA (Color Science Association) talks** — 40-90 minute YouTube talks — are transcribed locally; the YouTube URL is the citation but the transcript is the local cache.
- **Historical books** — Moses Harris, Birren, Albers — cited via Gutenberg, archive.org, or Gale scans.
- **Academic papers** — DOI or arxiv; DOI is load-bearing because arxiv versions can be withdrawn.
- **Blog posts and personal sites** — Björn Ottosson's articles, Peter Donahue's visualizations — mirrored to archive.org at capture time.

None of this is exotic. All of it is pattern-transferable to music theory, philosophy, cognitive science, or any domain where the canon is online-fragile.

## Size comparison

| Metric | expert-color | expert-typography | expert-dashboard |
|---|---:|---:|---:|
| Mode | canon-curation | capability | capability |
| Files | 148 | 59 | 101 |
| Axes | 3 | ~9 | 15 |
| Files/axis | ~49 | ~7 | ~7 |
| SKILL.md style | greatest hits | task routing | task routing |
| Each file summarizes | one source | one topic | one topic |
| Publishing | agentskills.io (public) | internal | internal |

Canon-curation skills are **fewer axes, denser per axis**. Capability skills are **more axes, sparser per axis**.

## Takeaways for method consumers

- Domain has a deep canon + the base model knows a lot → **canon-curation mode**.
- Domain has distinct sub-dimensions + practitioner-comparison questions → **capability mode**.
- Domain has both → split by axis: expert-color's `techniques/` axis is partly capability-mode; `historical/` and `contemporary/` are strict canon-curation.
- Publishing publicly → add LICENSE / README / MAINTENANCE / evals/ after v1.0.0.
- Source rot is real → archive.org discipline from wave 1, not post-hoc.

## What this case study adds to the meta-skill

Before v1.1.0, `meta-expert-author` would have produced expert-color in capability mode — missing the canon-curation genre entirely. The addition of `methodology/canon-curation-mode.md` (v1.1.0) and the temporal/instrumental axis model in `axis-identification.md` closes this gap.

Test for the extension: given the prompt "make me a `music-theory-expert` like expert-color," meta-expert-author v1.1 should now:
1. Detect canon-curation genre from the "like expert-color" cue.
2. Propose temporal/instrumental axes (historical theorists, contemporary analysts, techniques).
3. Produce source-summary files, not topic-synthesis files.
4. Write a "greatest hits" SKILL.md, not a task-routing one.
5. Enforce archive.org discipline from Wave 1.

That's what v1.1.0 adds.
