---
date: 2026-04-18
coverage: deep
peers:
  - ../methodology/theoretical-axes.md
  - ../../meta-expert-author/references/examples/mixed-mode-case-study.md
  - ../structure/paper-summary-template.md
primary_sources:
  - Judea Pearl corpus (30+ papers across causal inference, 1988-2024)
  - Noam Chomsky corpus (60+ books + hundreds of papers, 1957-2024)
  - Karl Friston corpus (400+ papers across computational neuroscience)
---

# Author canon patterns

Some theoretical canon is organized by author trajectories, not by individual papers. Pearl's causal-inference corpus spans 30+ papers over 35 years; Chomsky has shifted his theoretical position five times across 60+ books. Summarizing paper-by-paper misses the arc.

This file covers how meta-theory-author skills handle multi-paper programs of research-survey without violating the one-paper-per-file invariant.

## The tension

**One-paper-per-file invariant** (from v1.0): every reference file summarizes exactly one paper.

**Author-canon reality**: some authors shift positions, refine ideas, or elaborate a single framework across a decades-long corpus. The individual-paper view loses the trajectory.

Resolution: **mixed-mode within the skill.** The `works/` axis keeps one-paper-per-file. A separate `figures/` or `trajectories/` axis holds **author-canon synthesis files** that span multiple papers — these files are capability-mode (synthesis), not canon-curation (one source).

See `../../meta-expert-author/references/examples/mixed-mode-case-study.md` for the general pattern. This file covers the theoretic-expert-specific application.

## When to add a figures/ axis

Add when:

1. **One author has ≥10 canonical papers in the skill's scope.** Below 10, cross-references among the paper files suffice.
2. **The author's position has shifted.** A trajectory file can make the shift legible — e.g., Chomsky's Standard Theory → Government and Binding → Minimalist Program.
3. **The author is itself a subject of study.** Philosophy of mind discusses Chalmers-the-thinker, not just individual Chalmers papers.
4. **Readers routinely ask "what did X say?" not "what does paper Y argue?"** — a signal that author-level abstraction is load-bearing.

Don't add when:

- The author has 3-5 papers in scope. Use cross-references instead.
- The author is one of many in a field without distinctive trajectory. "Everyone cites them" doesn't justify a figure file.
- Their corpus is monolithic (every paper argues the same thing). The first paper summarizes the whole.

## Figures/ file shape

A figure file is NOT a paper summary. It's a **capability-mode synthesis** (per meta-expert-author) with these sections:

```markdown
---
date: 2026-04-18
coverage: deep
figure: Judea Pearl
canonical_papers:
  - ../works/pearl-1988-probabilistic-reasoning.md
  - ../works/pearl-1995-causal-diagrams-biometrika.md
  - ../works/pearl-2009-causality-2nd-ed.md
  - ../works/pearl-2018-book-of-why.md
peers:
  - ../works/rubin-1974-potential-outcomes.md
  - ../works/imbens-2020-potential-outcomes-vs-dags.md
primary_sources:
  - https://doi.org/... (each paper's DOI)
---

# Judea Pearl — causal inference trajectory

## Biographical frame

[Position, affiliation, major shifts in field role. ~1 paragraph.]

## Theoretical trajectory

### Phase 1: [Years] — [Phase label]

[What was Pearl's position? Key paper(s). Summary of stance.]

- ../works/pearl-1988-probabilistic-reasoning.md — Bayesian networks formalism.

### Phase 2: [Years] — [Phase label]

[Position shift if any. New papers. How they build on or depart from Phase 1.]

- ../works/pearl-1995-causal-diagrams-biometrika.md — DAG causal interpretation.

### Phase 3: [Years] — [Phase label]

...

## Methodological commitments

[What does this author consistently endorse across their corpus? Statistical approaches, formalisms, epistemic positions.]

## Points of contention

[What has this author been publicly opposed on? Who opposes them? Link to the `../debates/` axis.]

- Disputes with Rubin / Imbens / Holland (potential-outcomes camp) — see `../debates/imbens-2020-potential-outcomes-vs-dags.md`.
- Critique of "model-free" statistical approaches — see `../debates/pearl-2018-model-blind-ml-limitations.md`.

## Influence

[Who does this author's work influence? Which subsequent research-survey programs, empirical fields, or applied domains cite them as foundational?]

## Reception

[What's the current standing of the author's position? Broadly accepted? Contested? In decline? Cite review papers or retrospectives if available.]

## Canonical-paper reading order

[For someone entering the author's corpus cold, which 3-5 papers should they read first?]

1. `../works/pearl-2009-causality-ch1-ch3.md` — the compact framework statement.
2. `../works/pearl-1995-causal-diagrams-biometrika.md` — the DAG paper that grounds everything.
3. `../works/pearl-2018-book-of-why.md` — the accessible trade-book overview.

## Key distinctions this author introduces or sharpens

[Vocabulary the author contributed to the field.]

- **do(X)** — intervention operator.
- **Ladder of causation** — observation / intervention / counterfactual.
- **Causal hierarchy theorem** — what each level can and cannot answer.

## What NOT to fold into the trajectory

[Scope guardrails. What papers by this author are out of scope for this skill, and why?]

- Pearl's work on belief revision (1990s) is outside the causal-inference scope.
- Pearl's co-authored applied-medicine papers are in `../works/` individually but not central to the trajectory.
```

## Frontmatter distinctions

Figures files use capability-mode frontmatter:

- `coverage:` — usually `deep` (trajectory files are load-bearing).
- `figure:` — the author's full name.
- `canonical_papers:` — relative paths to 3-10 works/ files that anchor the trajectory.
- `peers:` — related figures + contested-claim papers.
- `primary_sources:` — URLs (often many, including the DOIs of canonical papers).

**NO** `doi:`, `peer_review_status:`, `retraction_status:`, etc. — those live in the per-paper works/ files.

## Cross-linking discipline

Every figures/ file cross-references the individual works/ files it synthesizes. Every works/ file by an author with a figures/ entry links back to that entry:

```yaml
# In works/pearl-2009-causality-2nd-ed.md:
peers:
  - ../figures/pearl-judea.md
  - ../works/pearl-1995-causal-diagrams-biometrika.md
```

This produces a navigable two-level structure: reader can drill from figure → works, or from works → figure for context.

## Sizing

| Author corpus size | Figure file length | Works files |
|---|---|---|
| 10-15 papers in scope | 400-500 lines | 10-15 files |
| 15-30 papers in scope | 500-700 lines | 15-30 files (possibly split by phase) |
| 30+ papers | 700-900 lines | 30+ files; figures/ file becomes phase-subdivided |

For 50+ paper corpora (rare but real — Chomsky, Friston), consider splitting the figure file itself by phase:

- `figures/chomsky-noam-aspects-era.md` (1957-1975)
- `figures/chomsky-noam-principles-and-parameters.md` (1975-1993)
- `figures/chomsky-noam-minimalist-program.md` (1993-present)

Treat these as a figure-series.

## Anti-patterns

### Figure file that's a bibliography

A figures/ file that just lists the author's papers with one-sentence descriptions isn't a trajectory — it's a citation list. Add synthesis: what's the arc? What's the theoretical commitment? What's the influence?

If you can't write synthesis, the author may not warrant a figures/ file — they may just be a prolific-but-incoherent researcher whose individual papers should stand alone.

### Figure file that duplicates the works/ summaries

Don't re-summarize papers in the figure file. Link to the works/ files. The figure file adds trajectory, not content.

### Figure file that overclaims consistency

Authors shift. Don't pretend Pearl-1988 and Pearl-2018 argue the same thing if they don't. Phase-structure the trajectory to make shifts explicit.

### Author-as-axis

Don't create axes named after authors: `pearl/`, `rubin/`, `chomsky/`. That's overshoot. Use figures/ as a single axis holding all figure files.

### Quoting the author as a substitute for citing papers

"Pearl (2009) argues X" is fine. "Pearl argues X" without a paper anchor is an unverifiable author-level claim. Always tie the argument to a specific paper.

## Field-by-field fit

Some fields have strong author-trajectory canons; others don't.

| Field | Typical author-canon pattern | Figures axis warranted? |
|---|---|---|
| Philosophy | Strong; named positions attached to named philosophers | Yes, almost always |
| Economics | Moderate; some figures (Rubin, Imbens, Angrist) have named methods | Sometimes |
| Theoretical physics | Weak; individual papers more than trajectories | Rarely |
| Theoretical CS | Weak; papers stand more than authors | Rarely |
| Deep-learning theory | Moderate; some figures (Hinton, LeCun, Bengio) are canon | Sometimes |
| Cognitive science | Strong; named frameworks attached to authors | Yes |
| Epidemiology | Strong; named methods attached to authors (Robins, Hernán, VanderWeele) | Yes |
| Clinical trial methods | Moderate | Sometimes |
| Formal logic | Weak-moderate; ideas outlive individual careers | Rarely |
| Ethics / political philosophy | Strong | Yes |

When unsure, start without a figures/ axis. If cross-references between works/ files become unwieldy (one author cited in 8+ other files without a central anchor), introduce a figures/ file at that author.

## Adding figures/ mid-project

If you realize mid-wave that a figures/ axis is warranted:

1. Finish the current wave without adding the axis.
2. Between waves, announce in the CHANGELOG: "Adding `figures/` axis for author-canon trajectories."
3. Add the axis to INDEX.md with ⬜ markers for planned files.
4. Schedule a dedicated wave for figures/ files (typically 3-5 figure files for Pearl / Rubin / Imbens / VanderWeele in a causal-inference-expert skill).
5. Retrofit cross-references in existing works/ files.

Don't try to add figures/ to the current wave — it disrupts bookkeeping.

## Worked example: Pearl figures/ file in causal-inference-expert

Expected structure:

```markdown
# Judea Pearl — causal inference trajectory

## Biographical frame
UCLA CS professor; Turing Award 2011 for Bayesian networks and causal inference.

## Theoretical trajectory

### Phase 1: 1988-1994 — Bayesian networks as probabilistic reasoning
Pearl (1988) *Probabilistic Reasoning* establishes the computational formalism for Bayesian networks. At this stage, Pearl does NOT claim causal interpretation — BNs are probabilistic tools.

### Phase 2: 1995-2000 — Causal diagrams
Pearl (1995) reinterprets BNs as causal. Introduces the do-operator and intervention semantics. *Biometrika* paper is the canonical reference.

### Phase 3: 2000-2009 — Causality book and back-door / front-door formalism
Pearl (2000, 2009) *Causality* consolidates the framework. Theorem: do-calculus is complete for identification.

### Phase 4: 2010-2024 — Popularization and contested reception
Pearl (2018) *Book of Why* brings framework to general audiences. Imbens (2020), Rubin (2005), Holland (1986) offer alternative potential-outcomes framings. Pearl responds publicly.

## Methodological commitments
- Structural causal models as primary.
- Graph-based reasoning over algebraic manipulation.
- Opposition to "model-free" statistics; critique of ML-without-causal-structure.

## Points of contention
- Pearl vs Rubin on potential-outcomes equivalence. See `../debates/imbens-2020-potential-outcomes-vs-dags.md`.
- Pearl's critique of ML interpretability. See `../debates/pearl-2018-model-blind-limitations.md`.

## Canonical reading order
1. Pearl (1995) — compact DAG statement.
2. Pearl (2009) Chapter 1 + 3 — framework + identification.
3. Pearl (2018) *Book of Why* — accessible synthesis.

## Key distinctions
- **do(X) vs conditioning** — intervention vs observation.
- **Back-door criterion** — graphical sufficient condition for adjustment.
- **Ladder of causation** — observation / intervention / counterfactual.

## What's out of scope
Pearl's belief-revision work (1980s-early 90s) outside causal focus.
```

Full figure file: ~500-600 lines. Anchored to 4-5 canonical works/ files.
