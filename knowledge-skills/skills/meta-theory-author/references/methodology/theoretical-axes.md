---
date: 2026-04-18
coverage: expanded
peers:
  - ../../meta-expert-author/references/methodology/axis-identification.md
  - ../../meta-expert-author/references/methodology/canon-curation-mode.md
  - ../methodology/academic-sourcing.md
primary_sources:
  - Standard academic-field organizing conventions (observed across 2026 literature reviews)
---

# Theoretical axes

Domain-expert-author's axis model (presentation / capability / substrate for capability mode; temporal / instrumental for canon-curation) needs adjustment for theoretic-expert skills. Theoretical domains organize by different distinctions.

## Three primary axis models for theoretic domains

### Model A: Frame / empirical-test / meta-analysis

**Best for**: empirical sciences where theory proposes testable claims and papers differ in whether they propose, test, or synthesize.

- `theoretical-frame/` — papers proposing or refining theoretical frameworks.
- `empirical-test/` — papers empirically testing predictions from frames.
- `meta-analysis/` — papers systematically synthesizing empirical results.

Example: a `predictive-coding-expert` skill.
- `theoretical-frame/friston-2010-free-energy-principle.md`
- `empirical-test/yon-2021-sensory-prediction-error-replication.md`
- `meta-analysis/walsh-2020-predictive-coding-neural-evidence.md`

### Model B: Schools / figures / works

**Best for**: humanities and soft sciences with identifiable theoretical lineages.

- `schools/` — overview files of theoretical schools, their central commitments, their disputes.
- `figures/` — canonical figures, their key papers, their shifts over time.
- `works/` — specific canonical papers/books in depth.

Example: a `philosophy-of-mind-expert` skill.
- `schools/functionalism.md` (a school overview — but this is NOT one paper! See "mixed-mode footnote" below)
- `figures/chalmers-hard-problem-trajectory.md` (multi-paper trajectory for one author — but also multi-paper; see below)
- `works/chalmers-1995-facing-up-to-hard-problem.md` (one paper)

This model strains meta-theory-author's "one paper per file" rule. See "Mixed-mode for schools and figures" below.

### Model C: Methodologies / findings / debates

**Best for**: fields with contested methodology where "how we study X" is a central axis.

- `methodologies/` — papers establishing or critiquing methods.
- `findings/` — papers reporting empirical findings using established methods.
- `debates/` — papers explicitly engaging methodological or interpretive disputes.

Example: a `causal-inference-expert` skill.
- `methodologies/pearl-2009-causal-graph-identification.md`
- `findings/lalonde-1986-evaluating-econometric-methods-experimental-data.md`
- `debates/imbens-2019-potential-outcomes-vs-dags-imbens.md`

### Model D: Canonical split by sub-problem

**Best for**: fields with a clear decomposition into recognized sub-problems.

- Each axis is a named sub-problem of the field.
- Example: `machine-learning-theory-expert` with axes `generalization/`, `optimization/`, `approximation/`, `scaling-laws/`, `inductive-biases/`.

Every file within an axis is a paper treating that sub-problem.

## Mixed-mode for schools and figures

Model B (schools / figures / works) wants files that are NOT one paper per file:

- `schools/functionalism.md` — overview of the school across many papers. Not a single paper.
- `figures/chalmers-hard-problem-trajectory.md` — one author's work across multiple papers.

This is legitimate **mixed-mode**: the `works/` axis follows meta-theory-author's one-paper-per-file rule; `schools/` and `figures/` are capability-mode synthesis files.

Declare the axis mode in INDEX.md:

```markdown
## Axes

1. **schools/** (capability mode — synthesis across multiple sources per file)
2. **figures/** (capability mode — per-author trajectory synthesis)
3. **works/** (canon-curation — one paper per file; meta-theory-author core shape)
```

When an agent writes a `schools/` file, use meta-expert-author's capability-mode frontmatter and structure. When writing a `works/` file, use meta-theory-author's paper-summary template.

See `../../meta-expert-author/references/examples/mixed-mode-case-study.md` for the general mixed-mode pattern.

## Choosing the model

| Signal | Pick |
|---|---|
| Field has testable predictions and empirical tradition | Model A |
| Field has identifiable schools, lineages, and canonical figures | Model B (mixed-mode) |
| Field has active methodological disputes | Model C |
| Field has recognized sub-problem decomposition | Model D |

Many fields fit multiple models. Typical combination:

- Physics → Model D (by sub-problem: GR, QFT, statistical mechanics, …).
- Economics → Model A or C (frames + empirical tests, or methods + findings + debates).
- Psychology → Model A (replication crisis made frames/tests/meta-analyses the natural split).
- Philosophy → Model B (schools + figures + works).
- CS theory → Model D (by sub-problem: complexity, algorithms, logic, …).
- Cognitive science → often Model A + Model B hybrid.

## Axis count for theoretic skills

Narrower than capability-mode:

- **Narrow theoretic** — 3 axes, 20-40 files.
- **Medium theoretic** — 3-4 axes, 40-80 files.
- **Comprehensive theoretic** — 4-5 axes, 80-150 files.

Don't exceed 5 axes in a theoretic skill. Theoretical domains don't usually need more — the structure is in the paper-citation graph, not in many axis names.

## Anti-patterns

- **Axis per journal.** `nature-papers/`, `science-papers/` — bad; journals aren't conceptual axes.
- **Axis per decade.** `1990s-papers/`, `2000s-papers/` — temporal splits usually don't carry meaning in theoretic work. Exception: fields with clear paradigm breaks (pre-/post-transformers, pre-/post-replication-crisis).
- **Axis per author.** `pearl/`, `rubin/` — bias toward canonical figures overshoots; use schools or methodologies instead.
- **"Theory" and "practice" axes.** Too vague. Use specific sub-problems instead.
- **"Classic" and "modern" axes.** Similar to per-decade; usually not load-bearing.

## Worked example: causal-inference-expert

Three axes (Model C):

1. **`methodologies/`** (~15 files) — each file = one paper establishing or critiquing a method.
   - `pearl-2009-causality-chapter-3.md`
   - `imbens-rubin-2015-causal-inference-introduction.md`
   - `vanderweele-2015-explanation-in-causal-inference.md`
   - ...

2. **`findings/`** (~20 files) — each file = one paper reporting empirical causal findings using established methods.
   - `lalonde-1986-evaluating-econometric-methods-experimental-data.md`
   - `card-krueger-1994-minimum-wage-new-jersey.md`
   - ...

3. **`debates/`** (~10 files) — each file = one paper explicitly engaging a dispute.
   - `pearl-2018-book-of-why-critique-response.md`
   - `imbens-2020-potential-outcomes-vs-dags.md`
   - ...

Total: ~45 files across 3 axes. A medium theoretic skill.

SKILL.md would use the "greatest hits" shape: decision table on when to use DAGs vs potential outcomes, quick reference on identification strategies, pointers to canonical methodological papers.

## Worked example: deep-learning-theory-expert

Four axes (Model D):

1. **`generalization/`** — VC dimension, Rademacher complexity, double descent, implicit bias.
2. **`optimization/`** — SGD convergence, loss-landscape geometry, neural tangent kernel.
3. **`scaling-laws/`** — Chinchilla, Kaplan, emergent abilities.
4. **`inductive-biases/`** — architecture priors, symmetry, transformer circuits, mechanistic interpretability.

~20-30 files per axis. Comprehensive theoretic skill.

## What goes in SKILL.md for theoretic skills

Required sections (meta-theory-author override):

1. **Decision / orientation table** — "which sub-problem / school / method is relevant to a given question?"
2. **Key distinctions** — the vocabulary the base model conflates in this field.
3. **Unresolved debates** — the live controversies. Not "who's right" but "what's still contested."
4. **Replication status** — for empirical fields, a summary of which big findings have replicated and which haven't.
5. **Canon pointers** — which papers in `references/` are the starting points.

The "unresolved debates" and "replication status" sections are load-bearing. They convey what the field KNOWS vs. what it's still ARGUING about — which is where the skill adds value beyond the base model's summarization.

## Footnote: when the field is purely theoretical

Some fields don't have an empirical-test axis because the claims are mathematical or conceptual (set theory, model theory, metaphysics). Model B or a modified Model D works:

- **Theorems / proofs / conjectures** as axes for mathematics.
- **Positions / arguments / responses** as axes for analytic philosophy.

Adjust the axis model to the field's actual internal structure, not a generic template.
