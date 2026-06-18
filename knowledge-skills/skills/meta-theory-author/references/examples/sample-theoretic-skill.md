---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/theoretical-axes.md
  - ../methodology/academic-sourcing.md
  - ../structure/paper-summary-template.md
primary_sources:
  - Causal inference field conventions (observational)
---

# Worked example: causal-inference-expert

A hypothetical `causal-inference-expert` skill to show what meta-theory-author produces. Not built — used as a design example.

## Invocation

**User**: "Build me a causal-inference-expert skill, meta-theory-author style. Focus on the peer-reviewed canon — Pearl, Rubin, Imbens, VanderWeele, plus recent meta-analyses."

**Four-question gate:**

| Question | Answer |
|---|---|
| Domain | Causal inference in statistics, econometrics, epidemiology |
| Mode | Canon-curation (theoretic) — one paper per file |
| Release | Internal (not publishing to agentskills.io initially) |
| Scale | Medium — ~45-60 papers across 3 axes, 3-4 waves |

## Axis choice

**Model C** (methodologies / findings / debates) — best fit for causal inference because:
- The field has active methodological disputes (DAGs vs potential outcomes).
- Empirical papers use established methods.
- Debates are a distinct category from methods and findings.

Axes:
1. **`methodologies/`** — foundational method papers.
2. **`findings/`** — empirical papers applying causal-inference methods.
3. **`debates/`** — explicit methodological / interpretive disputes.

## Scoping survey output (abbreviated)

### Canonical methodology papers

- **Rubin (1974)** — Estimating causal effects of treatments in randomized and nonrandomized studies. *J. Ed. Psych.* — potential-outcomes framework origin.
- **Pearl (1995)** — Causal diagrams for empirical research-survey. *Biometrika* — DAG formalism.
- **Pearl (2009)** — *Causality* (2nd ed., book) — comprehensive DAG treatment.
- **Imbens & Rubin (2015)** — *Causal Inference for Statistics, Social, and Biomedical Sciences* (book) — potential-outcomes comprehensive.
- **VanderWeele (2015)** — *Explanation in Causal Inference* (book) — mediation analysis.
- **Angrist, Imbens, Rubin (1996)** — Identification of causal effects using instrumental variables. *JASA*.
- **Holland (1986)** — Statistics and causal inference. *JASA* — no-causation-without-manipulation critique.
- **Rosenbaum & Rubin (1983)** — The central role of the propensity score. *Biometrika*.
- **Hernán & Robins (2020)** — *Causal Inference: What If* (book, free PDF online) — g-methods.

### Canonical empirical / findings papers

- **LaLonde (1986)** — Evaluating econometric evaluations. *Am. Econ. Rev.* — observational vs experimental benchmarking.
- **Card & Krueger (1994)** — Minimum wages and employment in NJ/PA. *Am. Econ. Rev.* — natural experiment canonical.
- **Angrist (1990)** — Lifetime earnings and the Vietnam lottery. *Am. Econ. Rev.* — instrumental variables canonical.
- **Dehejia & Wahba (1999, 2002)** — propensity score revisits of LaLonde. *JASA*.

### Canonical debate papers

- **Imbens (2020)** — Potential outcomes and directed acyclic graphs. *Journal of Economic Perspectives* — vs-DAGs argument.
- **Pearl (2018)** — Response to Imbens critique (Book of Why + various). — counter-response.
- **Deaton & Cartwright (2018)** — Understanding and misunderstanding randomized controlled trials. *Soc. Sci. Med.* — RCT skepticism.
- **Rubin (2005)** — Causal inference using potential outcomes. *JASA*.

## Sample reference file: `methodologies/pearl-2009-causality-ch3.md`

```markdown
---
doi: 10.1017/CBO9780511803161
authors:
  - Pearl, Judea
year: 2009
title: "Causality: Models, Reasoning, and Inference, Chapter 3: Causal Diagrams and the Identification of Causal Effects"
venue: Cambridge University Press
venue_type: book
peer_review_status: peer-reviewed-published
venue_indexed: [WoS, Scopus]
publication_date: 2009-09-01
retraction_status: clean
retraction_checked: 2026-04-18
license: copyright-all-rights-reserved
access_paths:
  - doi: https://doi.org/10.1017/CBO9780511803161
  - author_copy: http://bayes.cs.ucla.edu/BOOK-2K/
coverage: deep
peers:
  - ../methodologies/rubin-1974-potential-outcomes.md
  - ../debates/imbens-2020-potential-outcomes-vs-dags.md
primary_sources:
  - https://doi.org/10.1017/CBO9780511803161
  - http://bayes.cs.ucla.edu/BOOK-2K/
---

# Causality, Chapter 3 (Pearl 2009)

**DOI**: https://doi.org/10.1017/CBO9780511803161
**Author**: Judea Pearl
**Venue**: Cambridge University Press (2nd ed.)
**Status**: peer-reviewed book chapter; not retracted (checked 2026-04-18)

Chapter 3 of Pearl's *Causality* introduces the graphical formalism for causal identification — DAGs, d-separation, the back-door criterion, the front-door criterion, and do-calculus. Foundational for graph-based causal inference.

## Contribution

Formalizes identification — the question of which causal effects can be estimated from observational data given a DAG — into three calculus rules (do-calculus). Provides the back-door criterion as a sufficient condition for confounding control, and the front-door criterion as an alternative when back-door doesn't hold.

## Methods

Mathematical. Chapter proves theorems via graph algorithms; no empirical data.

## Key findings

- **Back-door criterion**: controlling for a variable set Z identifies P(Y | do(X)) if Z blocks all back-door paths and no variable in Z is a descendant of X.
- **Front-door criterion**: identifies P(Y | do(X)) via a mediator M even when back-door adjustment is impossible.
- **do-calculus**: three rules that enable systematic identification reasoning.
- **Every identifiable effect** from observational data under a given DAG can be derived via do-calculus.

## Key distinctions

- **do(X)** — intervention (setting X by external action), distinct from **conditioning on X** (observing X).
- **d-separation** — graphical criterion for conditional independence given a DAG.
- **Back-door path** — path from X to Y beginning with an arrow into X (source of confounding).
- **Identification** — the theoretical question of whether a causal quantity can be estimated from data, separate from **estimation** (how to do it).

## Notable quotations

> "The back-door criterion provides a simple graphical test of sufficient conditions for adjustment" (Pearl 2009, p. 79).

## Limitations

- Assumes the DAG is correct; model misspecification not treated in depth in Ch. 3.
- Discrete intervention model; continuous-valued treatments handled in later chapters.
- Critiqued (see `../debates/imbens-2020-potential-outcomes-vs-dags.md`) for assuming the researcher has access to the true DAG.

## Citing / cited works in this skill

- Cites: `../methodologies/rubin-1974-potential-outcomes.md` (contrasts with potential-outcomes framework).
- Cited by: `../debates/imbens-2020-potential-outcomes-vs-dags.md` (Imbens critiques the DAG approach).

## Access

- DOI: https://doi.org/10.1017/CBO9780511803161
- Sample chapters + preface: http://bayes.cs.ucla.edu/BOOK-2K/
- Full book paywalled; academic-library access typical.
```

## SKILL.md sketch

```markdown
---
name: causal-inference-expert
description: Use when working with causal inference — potential outcomes, DAGs, identification, confounding, instrumental variables, regression discontinuity, difference-in-differences, mediation analysis, sensitivity analysis, g-methods, or comparing methodologies across the Pearl / Rubin / Imbens / VanderWeele traditions.
---

# causal-inference-expert

Peer-reviewed canon of causal inference: potential outcomes, DAGs, identification, estimation. See `references/INDEX.md` for the 45-60 paper corpus.

## Methodology quick-pick

| Task | Method | Seminal paper |
|---|---|---|
| Estimate ATE from RCT | Difference in means | — (standard) |
| Observational, know the DAG | Back-door adjustment | Pearl (1995, 2009) |
| Observational, hidden confounders with instrument | IV | Angrist, Imbens, Rubin (1996) |
| Observational, only a running variable | RDD | Hahn, Todd, van der Klaauw (2001) |
| Observational, panel data with shock | DID | Card & Krueger (1994); Goodman-Bacon (2021) |
| Want to decompose total effect | Mediation | VanderWeele (2015) |
| Time-varying confounders | g-methods | Robins (1986, 2000); Hernán & Robins (2020) |

## Unresolved debates

1. **Potential outcomes vs. DAGs** — mostly a notation / emphasis dispute, but real differences in how treatments-with-time and non-manipulable causes are handled. See `debates/imbens-2020-potential-outcomes-vs-dags.md`.
2. **RCT epistemic primacy** — Deaton & Cartwright (2018) vs. the Banerjee-Duflo-Kremer tradition. Do RCTs deserve the canonical status they have?
3. **Heterogeneity estimation** — CATE / HTE estimation methods proliferate; no consensus on preferred approach.
4. **Observational "deep-learning" causal methods** — growing literature, contested rigor.

## Replication status

- **LaLonde (1986)** benchmark — observational methods sometimes recover experimental estimates (Dehejia & Wahba 1999) and sometimes don't (Smith & Todd 2005). Field-canonical unsettled question.
- **Minimum wage employment effects** — Card-Krueger (1994) replicated in several state-level settings; Cengiz et al. (2019) extends. General DID approach now considered robust.

## Key distinctions the base model conflates

- **Causation vs. correlation** — distinct despite the field being about quantifying the gap.
- **do(X) vs. conditioning on X** — the whole point of DAGs vs. plain regression.
- **Identification vs. estimation** — mathematical vs. statistical question.
- **ATE vs. ATT vs. CATE** — different estimands, different assumptions.

## Where to dig deeper

- `references/methodologies/` — ~15 foundational method papers.
- `references/findings/` — ~20 empirical applications.
- `references/debates/` — ~10 methodological disputes.

Full 45+ paper manifest: `references/INDEX.md`.
```

## Wave plan

Given ~45 papers, 3 axes, medium scale:

- **Wave 1** — 15 methodology files (Pearl DAG chapters, Rubin potential outcomes, Angrist-Imbens-Rubin IV, Rosenbaum-Rubin propensity, Holland critique). 5 agents.
- **Wave 2** — 20 findings files (LaLonde, Card-Krueger, Angrist Vietnam, Dehejia-Wahba, etc.). 5-6 agents.
- **Wave 3** — 10 debates files (Imbens-Pearl exchange, Deaton-Cartwright, Rubin-Pearl responses). 3-4 agents.

Total wallclock: ~6-8 hours across 3 sessions.

## What makes this a meta-theory-author skill, not meta-expert-author

Every file cites one peer-reviewed paper. No blog posts, no tutorials, no software docs. The `debates/` axis explicitly surfaces methodological disputes from the published record. Retraction status tracked (a few high-profile causal-inference retractions exist in applied work). Preprint handling applies to recent methods papers (e.g., double machine learning has many arxiv preprints before journal publication).

Contrast with a hypothetical `causal-inference-practitioner-expert` (meta-expert-author mixed-mode): would include R package docs (DoubleML, MatchIt), stan-based Bayesian guides, econometrics blog posts, tutorial YouTube videos. Different source discipline, different output shape.

## Takeaways

- Theoretic-expert-author produces skills where **the citation graph IS the skill**.
- Model C (methods/findings/debates) fits empirical theoretical fields cleanly.
- The `debates/` axis is distinctively valuable — it surfaces what the field is still arguing about, which is what SKILL.md's "unresolved debates" section quotes from.
- Paper-level summaries are the unit. Author-level or school-level summaries require mixed-mode (capability-mode synthesis files in a separate axis).
