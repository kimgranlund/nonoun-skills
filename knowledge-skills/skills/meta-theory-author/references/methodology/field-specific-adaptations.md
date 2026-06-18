---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/paper-reading-protocol.md
  - ../methodology/peer-review-verification.md
  - ../methodology/currency-and-recency.md
primary_sources:
  - Ioannidis, J.P.A. (2005). "Why most published research-survey findings are false." PLoS Medicine 2(8):e124.
  - Open Science Collaboration (2015). "Estimating the reproducibility of psychological science." Science 349(6251):aac4716.
  - Camerer et al. (2018). "Evaluating replicability of social science experiments in Nature and Science between 2010 and 2015." Nat Hum Behav 2:637-644.
---

# Field-specific adaptations

Different theoretical fields have different quality signals, different replication norms, different preprint cultures, and different retraction rates. The generic protocols in `paper-reading-protocol.md` and `peer-review-verification.md` apply everywhere; this file documents per-field adjustments.

## Biomedicine (including clinical medicine, epidemiology, cell biology, oncology)

### Quality signals

- **Preregistration** on ClinicalTrials.gov (RCTs) or PROSPERO (systematic reviews) — strong positive signal.
- **CONSORT-compliant reporting** for RCTs — standard quality frame.
- **PRISMA-compliant reporting** for systematic reviews/meta-analyses.
- **Reporting of CIs and effect sizes**, not just p-values.
- **Adequate statistical power calculations** pre-study.
- **Blinding** and concealment in RCTs.

### Weakness signals (higher vigilance required)

- **Retractions are common.** Cancer biology has documented retraction rates 10-20×higher than physics. Always check Retraction Watch.
- **Harking / p-hacking** especially common in observational studies.
- **Spin in abstracts** — abstract conclusions may not match results. Read the full results section.
- **Selective reporting of secondary outcomes** when primary outcome was null.
- **Investigator conflicts of interest** — industry-funded trials have known bias patterns.

### Sources and indexing

- **Primary index**: PubMed / MEDLINE.
- **Preprints**: bioRxiv (basic biology), medRxiv (clinical, from 2019).
- **Retraction watch**: particularly critical in this field.

### Refresh cadence

- 6-month standard. For fast-moving areas (oncology immunotherapy, new drug classes), 3-month is safer.

### Field-specific frontmatter additions

```yaml
preregistration: https://clinicaltrials.gov/study/NCT01234567  # if RCT
reporting_standard: CONSORT  # or PRISMA, STROBE, ARRIVE, etc.
conflicts_of_interest: disclosed  # or undisclosed / absent
power_analysis_reported: true
```

## Psychology and behavioral science

### Quality signals

- **Preregistration** on OSF or AsPredicted — critical post-replication-crisis.
- **Open data** and open materials.
- **Effect sizes with CIs**, not just p < .05.
- **Direct replication** in the paper or cited.
- **Registered Reports** (Stage 1 + Stage 2 peer review before data collection).

### Weakness signals

- **Small samples** (n < 50 per condition) — low power, high false-positive risk.
- **No preregistration** (especially post-2015).
- **Hypothesis phrased after analysis** (HARKing).
- **Underpowered effect sizes claimed as "robust."**
- **Dependence on single-item outcome measures.**
- **Lack of replication attempts cited.**

### Sources and indexing

- **Primary index**: PsycINFO (paywalled) / PsyArXiv (open).
- **Preprints**: PsyArXiv (OSF-hosted).
- **Replication trackers**: Reproducibility Project Psychology (2015), Many Labs projects (2014+), Registered Replication Reports.

### The replication-crisis context

Since 2011 (Diederik Stapel fraud, Open Science Collaboration 2015 reproducibility study), psychology has undergone substantial reform. Papers published pre-2015 are suspect by default unless independently replicated. Post-2015 papers with preregistration + open data are in a different epistemic class.

- **Pre-2015 paper, no replication cited**: hedge strongly. "The paper reported..." not "X is true."
- **Pre-2015 paper, direct replication succeeded**: treat as more credible.
- **Pre-2015 paper, direct replication failed**: cite the failed replication prominently.

### Refresh cadence

- 6-month. Replication-status section needs ongoing updates as new meta-analyses appear.

## Economics and econometrics

### Quality signals

- **Identification strategy made explicit** (RCT, natural experiment, instrumental variable, RDD, DiD).
- **Placebo tests** and falsification exercises.
- **Robustness tables** in appendix.
- **Working-paper series** (NBER, IZA, CEPR) — institutional review.
- **AEA's data and code availability policy** (2019+) for top journals.

### Weakness signals

- **Weak instruments** in IV estimation.
- **Parallel-trends assumption unjustified** in DiD.
- **Unobserved-confounder sensitivity analysis absent.**
- **Heterogeneity of treatment effects not examined.**

### Sources and indexing

- **Primary**: EconLit, RePEc/IDEAS.
- **Preprints**: SSRN, NBER working papers, IZA DP.
- **Top journals**: AER, QJE, Econometrica, Journal of Political Economy, Review of Economic Studies (the "Top 5").

### Working-paper culture

Economics has stronger working-paper culture than most sciences. An NBER WP is often cited for years before journal publication. Handle:

- Cite the NBER number + latest version.
- At refresh, check for journal publication and update.
- Don't treat working papers as lesser — field convention treats them as serious.

### Refresh cadence

- 12-month typically sufficient. Macroeconomic claims may need faster refresh around major events.

## Theoretical computer science

### Quality signals

- **Proofs checked via review** (venue rigor: STOC / FOCS / SODA / CCS / SIGCOMM / OSDI accepts).
- **Formal statements** of theorems with explicit hypotheses.
- **Prior-work section** situating contribution.

### Weakness signals

- **Incomplete proofs** (common in conference versions; full versions may exist as arxiv/journal submissions).
- **Non-standard models** without motivation.

### Sources and indexing

- **Primary**: DBLP, ACM Digital Library, IEEE Xplore.
- **Preprints**: arxiv (cs.*), Electronic Colloquium on Computational Complexity (ECCC).
- **No retraction culture to speak of** — rare.

### Conference vs journal

In CS, top-tier conferences (STOC, FOCS, NeurIPS, ICML, ACL, SIGCOMM, OSDI, CCS) are peer-reviewed and count as full publications. Journals (ACM Transactions, IEEE Transactions) are also valid but less central. Treat top-tier conference papers as tier 1-2.

### Refresh cadence

- 12-24 month typically fine. Proofs don't go stale; only framings do.

## Machine learning and AI

### Quality signals

- **Open code + pretrained models** — standard at top venues 2022+.
- **Ablation studies** across architecture and hyperparameters.
- **Comparison to strong baselines** (not just weak ones).
- **Multiple random seeds** with standard deviations.
- **Standardized benchmarks** (GLUE, SQuAD, ImageNet, etc.).

### Weakness signals

- **Benchmark overfitting** — tuning hyperparameters on test set.
- **Weak baselines** to inflate delta.
- **Single-seed runs** — variance not characterized.
- **Unreplicated scaling claims** — especially for expensive experiments.
- **Cherry-picked samples** in qualitative analyses.
- **Absent compute budget disclosure** — non-reproducible for resource-constrained readers.

### Sources and indexing

- **Primary**: arxiv (cs.LG, cs.CL, cs.CV, stat.ML).
- **Conferences**: NeurIPS, ICML, ICLR, ACL, EMNLP, CVPR, AAAI — all peer-reviewed, top-tier.
- **Preprint-culture**: extreme. Most ML papers live on arxiv for months before conference publication; many never get peer-reviewed at all.

### The arxiv-only reality

In ML, a large fraction of influential papers are arxiv-only (never submitted or still under review). The field's canonicalization happens via citation count + community discussion, not peer review. For meta-theory-author skills in ML:

- Accept arxiv-only papers as tier 4-5, but flag status carefully.
- Check for subsequent peer-reviewed version at each refresh.
- Weight peer-reviewed papers (NeurIPS/ICML/ICLR/ACL) higher for SKILL.md's "greatest hits" claims.

### Refresh cadence

- **3-month** for fast-moving areas (LLM scaling, new architectures). 6-month otherwise.

## Philosophy

### Quality signals

- **Rigorous argument structure** with explicit premises and conclusion.
- **Engagement with contemporary literature** (not just founders).
- **Publication in ranked journals** (Mind, Philosophical Review, Journal of Philosophy, Nous, Analysis, etc.).
- **Book publication** with major academic presses (Oxford UP, Cambridge UP, Harvard UP).

### Weakness signals

- **Strawman opponents** without citing specific positions.
- **Key terms undefined** or used ambiguously.
- **Empirical claims unbacked** (philosophers sometimes make empirical-sounding claims).

### Sources and indexing

- **Primary**: PhilPapers (comprehensive), JSTOR, ProQuest Philosophy Documentation.
- **Preprints**: PhilPapers hosts preprints; less centralized than arxiv.
- **Books are a major unit** — Cambridge Companions, Oxford Handbooks, monographs.

### Refresh cadence

- **24-month** typically. Canon stable; occasional new arguments.

### Author-canon pattern

Philosophy is the paradigm field for figures/ axis. Most sub-fields organize around named positions attached to named philosophers (Chalmers's hard problem, Quine's naturalism, Kripke's rigid designation). See `author-canon-patterns.md`.

## Pure mathematics

### Quality signals

- **Complete proofs** — unlike applied fields, math papers typically include full proofs.
- **Publication in peer-reviewed journals** (Annals of Mathematics, Inventiones, Acta, etc.).
- **Citation by subsequent papers** working in the same framework.

### Weakness signals

- **Undeclared assumptions.**
- **Gaps in proofs** not acknowledged.

### Sources and indexing

- **Primary**: MathSciNet (paywalled), zbMATH (open).
- **Preprints**: arxiv (math.*).

### Retraction culture

- Rare. Math papers mostly stand or fall on proof-checking, not retraction.

### Refresh cadence

- **24-month** typically. Math results are durable; refresh mainly for new proofs.

## High-energy physics / quantum physics / astrophysics

### Quality signals

- **Experimental confirmation** in large collaborations (LIGO, LHC, IceCube).
- **Publication in PRL, PRD, JHEP, Nature Physics.**
- **Independent replication** in different experimental facilities.

### Weakness signals

- **Individual-experiment claims** without replication.
- **Anomaly papers** — especially common in hep-ph.
- **Exaggerated significance** (3σ presented as discovery).

### Sources and indexing

- **Primary**: INSPIRE-HEP, NASA ADS.
- **Preprints**: arxiv (hep-*, astro-ph, gr-qc, quant-ph, cond-mat).
- **Preprint-culture**: extreme; almost all physics papers live on arxiv.

### Refresh cadence

- **12-month** typically. Exceptions: during major experimental runs (LHC Run 3, JWST campaigns), 6-month.

## Clinical trials (specific notes)

### Required fields

Beyond the standard peer-review frontmatter, clinical trial summaries add:

```yaml
trial_registration: NCT01234567
trial_phase: 3             # 1/2/3/4
primary_outcome: "Overall survival"
sample_size: 450
effect_size: "HR 0.82 (95% CI 0.68-0.99)"
funding_source: "NIH R01 ..."
conflicts_of_interest: "disclosed"
```

### Special considerations

- **Phase 1-2 vs Phase 3** — different epistemic weight. Phase 3 is confirmatory; earlier phases are exploratory.
- **Surrogate vs clinical endpoints** — progression-free survival vs overall survival are not equivalent.
- **Industry-funded vs independent** — disclose in summary.

## Meta-analyses and systematic reviews

### Quality signals

- **PRISMA-compliant search and reporting.**
- **Preregistration** on PROSPERO.
- **Assessment of study quality** (Cochrane risk of bias, GRADE, etc.).
- **Tests for publication bias** (funnel plots, Egger's test).
- **Heterogeneity analysis** (I², random-effects vs fixed-effects).

### Special template addition

Meta-analysis files need:

```yaml
meta_analysis: true
included_studies_count: 47
pooled_effect_size: "SMD 0.34 (95% CI 0.21-0.47)"
heterogeneity_I2: 62
publication_bias_assessed: "funnel plot + Egger's test"
prospero_registration: CRD42024123456
```

### Weakness signals

- **Studies in low-quality journals dominate the pool.**
- **Unassessed publication bias.**
- **High heterogeneity without subgroup justification.**
- **Narrative synthesis without meta-analysis when quantitative would be feasible.**

## Cross-field comparison table

| Field | Canon style | Preprint culture | Retraction rate | Refresh cadence | Figures axis? |
|---|---|---|---|---|---|
| Biomedicine | Paper-level | Moderate (bio/medRxiv) | High | 3-6 month | Sometimes |
| Psychology | Paper-level + replication tracking | Moderate | Moderate-high | 6 month | Rarely |
| Economics | Paper-level | Strong (WPs) | Low | 12 month | Sometimes |
| Theoretical CS | Paper-level | Strong (arxiv) | Very low | 12-24 month | Rarely |
| Machine learning | Paper-level (arxiv-first) | Extreme | Low (but ghost-benchmarks common) | 3-6 month | Sometimes |
| Philosophy | Author-level | Weak | Very low | 24 month | Almost always |
| Pure math | Paper-level | Strong (arxiv) | Very low | 24 month | Rarely |
| HEP / astro | Paper-level | Extreme | Low | 12 month | Rarely |

## Agent-brief adaptations

When dispatching waves for field-specific theoretic skills, adjust the brief:

> **Field-specific brief** (biomedicine example):
> - Check trial registration for every RCT cited.
> - Verify retraction status thoroughly; biomedicine has high retraction rates.
> - Use PubMed as the primary search index in addition to Semantic Scholar.
> - Extract effect sizes with CIs, not just p-values.
> - Flag CoI disclosures in frontmatter.
> - Note reporting standard (CONSORT, PRISMA, STROBE) where applicable.

> **Field-specific brief** (machine learning example):
> - arxiv is often the primary venue; accept arxiv-only as tier 4 with flagging.
> - Check for subsequent conference publication (NeurIPS, ICML, ICLR, ACL).
> - Verify benchmark claims — check if baselines were strong.
> - Note whether code + models are released.
> - Flag compute-budget-dependence of results.

> **Field-specific brief** (philosophy example):
> - Consider figures/ axis for named philosophical positions.
> - Preprint culture weak; rely on peer-reviewed journals + books.
> - Engage with the argument structure; don't paraphrase positions without citing.

## Picking the right adaptation

For each new theoretic-expert skill:

1. Identify the field (or primary field if interdisciplinary).
2. Review the adaptations above for that field.
3. Incorporate into:
   - `paper-summary-template.md` frontmatter (field-specific fields).
   - Agent-brief template (field-specific verification).
   - Refresh cadence in MAINTENANCE.md.
   - `paper-reading-protocol.md` expectations (replication emphasis, etc.).

## When the domain spans multiple fields

Many theoretic skills span fields (computational neuroscience spans CS + biology; econometrics spans econ + statistics). Pick the stricter adaptation for each dimension:

- **Retraction vigilance**: take the stricter field (e.g., if biomedicine is involved, check Retraction Watch aggressively).
- **Replication tracking**: if psychology-adjacent, track replications.
- **Refresh cadence**: the shorter of the two.
- **Frontmatter fields**: union of the two.

Document the choice in the skill's MAINTENANCE.md.
