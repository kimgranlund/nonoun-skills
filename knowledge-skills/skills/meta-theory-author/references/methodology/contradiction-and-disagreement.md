---
date: 2026-04-18
coverage: deep
peers:
  - ../methodology/theoretical-axes.md
  - ../methodology/paper-reading-protocol.md
  - ../methodology/author-canon-patterns.md
  - ../structure/paper-summary-template.md
primary_sources:
  - Pearl vs Rubin / Imbens exchange (causal inference, 2005-2020)
  - Replication crisis in psychology (Open Science Collaboration 2015, Nature 2020 Many Labs replications)
  - RCT-skepticism debates (Deaton & Cartwright 2018 vs Banerjee-Duflo 2007)
---

# Contradiction and disagreement

Theoretic fields are structured around disagreement. Different authors argue opposite conclusions from overlapping evidence. Empirical papers sometimes fail to replicate earlier findings. Methodological schools treat the same data differently. This file covers how meta-theory-author skills surface disagreement without taking sides.

## The problem

A produced theoretic-expert skill that presents the canon as consensus is subtly misleading. Real fields have:

- **Named disputes** (Pearl vs Rubin on potential-outcomes-vs-DAGs).
- **Failed replications** (most published psychology pre-2015 findings).
- **Interpretive multiplicity** (same data supporting opposite conclusions in economics).
- **Paradigm clashes** (frequentist vs Bayesian, functional vs structural in cog-sci).

SKILL.md's "unresolved debates" section is supposed to surface this. Without explicit protocol, it tends to produce a list of "two sides disagree" placeholders without real substance.

## Four kinds of disagreement

Each gets different treatment.

### 1. Methodological dispute

Same phenomenon, different methods, different conclusions.

**Example**: Observational vs RCT evidence for minimum-wage employment effects. Card-Krueger (1994) observational study showed negligible negative effect; Neumark et al. re-analyses showed larger negative effects; more recent Cengiz et al. (2019) using bunching estimator shows negligible.

**Treatment**: Each paper gets its own `findings/` or `methodologies/` file. A `debates/` file summarizes the methodological dispute explicitly — what does each method assume, where do they diverge, what's at stake.

Cross-link via `peers:` on all involved paper files.

### 2. Interpretive dispute

Same results, different conclusions drawn.

**Example**: Does fMRI activation during a task imply the region is necessary for the task? Activation implies involvement; only lesion studies imply necessity. Papers often over-interpret activation.

**Treatment**: The `debates/` file makes the interpretive distinction explicit. Individual paper files note the paper's interpretive stance in the "Limitations" section.

### 3. Paradigmatic dispute

Different frameworks yield different questions AND different answers.

**Example**: Pearl (do-calculus) vs Rubin (potential outcomes) in causal inference. The two frameworks are largely translatable, but each generates different research-question framings and different debates.

**Treatment**: Consider a `frameworks/` or `paradigms/` axis. Each paradigm gets a framing file; individual papers sit within their paradigm. `debates/` holds explicit cross-paradigm critiques.

### 4. Empirical failure to replicate

Paper A claims finding X; paper B attempts replication and fails.

**Example**: Amy Cuddy's power-poses effect (Carney, Cuddy, Yap 2010) vs Ranehill et al. (2015) failed replication.

**Treatment**: Both papers get their own files. The original's file has a prominent "Replication status" section flagging the failed replication. The failed-replication's file cross-links. SKILL.md's "replication status" section highlights.

## The disagreement-surface checklist

For every pair of papers in the skill that contradict, verify:

- [ ] Both papers have their own file with balanced summary.
- [ ] Each file's "Limitations" section notes the contradiction.
- [ ] Each file's `peers:` frontmatter cross-links the opposing paper.
- [ ] A `debates/` file exists if the dispute is methodological / paradigmatic, OR the contradiction is noted in SKILL.md's "Unresolved debates" section if it's narrower.
- [ ] No file claims one side "won" unless there's strong meta-analytic consensus (rare).

## The debates/ axis in detail

A debates/ file is a paper-summary file (one paper per file) where the paper IS the explicit engagement with the dispute.

Examples:

- `debates/imbens-2020-potential-outcomes-vs-dags.md` — Imbens's *Journal of Economic Perspectives* critique of DAGs.
- `debates/pearl-2018-response-to-imbens.md` — Pearl's response paper.
- `debates/deaton-cartwright-2018-understanding-rcts.md` — Deaton & Cartwright's RCT-skepticism.

Each is a normal paper-summary file. The distinguishing feature: they explicitly engage the dispute, so the summary emphasizes:

1. **The claim under dispute** (stated in neutral terms).
2. **This paper's position**.
3. **What the paper's opponents hold** (referenced to their primary sources).
4. **What would resolve the dispute** (if anything).

Distinct from methodology or findings papers, which address topics without being primarily debate-engagements.

## The disagreement-surface in SKILL.md

Required section per `theoretical-axes.md` § "What goes in SKILL.md for theoretic skills":

```markdown
## Unresolved debates

[Enumerate the live disputes. Don't pick winners. Use hedges aggressively.]

1. **[Dispute name]** — [one-sentence statement of the dispute]. See:
   - `references/debates/[proponent-paper].md` — argues [position].
   - `references/debates/[opponent-paper].md` — argues [opposing position].
   
   Status: [contested / partial-consensus-on-X / widely-adopted-modus-vivendi / etc.]

2. **[Dispute name]** — ...
```

**Good** (from hypothetical causal-inference-expert):

> **Potential-outcomes vs DAGs** — whether causal inference is fundamentally a potential-outcomes problem (Rubin tradition) or a DAG-identification problem (Pearl tradition). See `references/debates/imbens-2020-potential-outcomes-vs-dags.md` and `references/debates/pearl-2018-response-to-imbens.md`. Status: partial-translation-possible, differing emphases remain; most applied work uses one framework without engaging the dispute.

**Bad**:

> **Potential outcomes vs DAGs** — some people prefer potential outcomes, others prefer DAGs.

The good version names the positions, cites papers, and characterizes the status honestly.

## Hedge discipline across disagreements

When summarizing a paper that's part of a dispute:

- In the paper's own file: **preserve its internal stance**. Pearl's file describes Pearl's argument as Pearl makes it.
- In the debates/ file: **name the dispute neutrally**. "There is disagreement about X" not "X is contested because some people are wrong."
- In SKILL.md: **characterize the dispute without adjudicating**. "A persistent dispute" not "the field is undecided because evidence is weak."

Never let the skill's overall posture reveal a side on a live dispute. The reader should be able to tell what the canon argues, without being told what to believe.

### When one side has clearly won

Some disputes have been resolved. Acknowledge resolution:

- **Phlogiston vs oxygen** — the dispute is historical. Skill can say "oxygen theory replaced phlogiston theory by ~1789."
- **Neural network capacity vs symbolic-AI** — largely empirically resolved for high-capacity perception/language tasks (neural won). Skill can note the empirical resolution while preserving nuance about domains where symbolic still applies.

Resolved disputes go in a **"Historical debates"** or **"Resolved disputes"** section, distinct from "Unresolved debates."

### When the dispute is actually about definitions

Sometimes "disagreement" reflects people talking past each other with different definitions of key terms. Surface this:

> **Pearl-Rubin equivalence debate** — at the formal level, do-calculus and potential outcomes have been proven equivalent for identification (Shpitser & Pearl 2008). The continuing dispute is largely about emphasis, notation, and what kinds of problems each framework makes easier. The dispute appears substantive but is primarily about research-program style, not about disagreement on mathematical content.

This hedging is more precise than "it's unresolved" or "it's resolved."

## Cross-paper contradiction at the claim level

Sometimes two papers in the skill don't explicitly debate each other but make contradictory claims about the same phenomenon.

**Example**: Paper A (fMRI study) claims region X is activated during task Y. Paper B (lesion study) shows region X damage doesn't impair task Y.

The two papers aren't in explicit dialogue — they're different methods with different inferences. But they contradict at the claim level.

**Treatment**:

- Both papers get their own files.
- Both files' "Key findings" sections accurately report the paper's claim.
- Both files' "Limitations" sections note the cross-study tension ("Lesion evidence — see `../findings/patient-xyz-lesion-study.md` — shows X may not be necessary for Y, suggesting fMRI activation here may reflect involvement rather than necessity").
- SKILL.md's "Key distinctions" section formalizes: "Activation ≠ necessity."

Don't create a `debates/` file for implicit contradictions. Surface them via cross-references and Limitations sections.

## Meta-analyses as dispute-resolution evidence

When a meta-analysis addresses a contested claim, it carries more weight in the disagreement surface:

- Its summary file explicitly notes which prior individual studies it synthesizes.
- SKILL.md's "Replication status" or "Unresolved debates" cites the meta-analysis.
- If the meta-analysis is conclusive, the dispute may be downgraded from "unresolved" to "partial-consensus."

**Example**: For a hypothetical `behavioral-economics-expert`, the Open Science Collaboration (2015) reproducibility project + subsequent meta-analyses shifted many claimed effects from "canonical" to "non-replicating." SKILL.md's replication-status section leans on these meta-analyses to characterize the field's post-2015 epistemic state.

## Agent-brief additions for disagreement handling

Add to meta-theory-author wave briefs when authoring files that touch contested topics:

> **Disagreement-handling** (from `../methodology/contradiction-and-disagreement.md`):
> - If the paper you're summarizing is part of a named dispute, note the dispute in the "Limitations" section and cross-link opposing paper files via `peers:`.
> - If the paper explicitly engages a dispute (debates/ axis), structure the summary around: claim under dispute / this paper's position / opposing positions / resolution path.
> - Preserve hedge discipline: do not pick sides in your summary. Describe what the paper argues, not whether it's right.
> - Report in your findings: any contested claims you noticed that should be surfaced in SKILL.md's "Unresolved debates" section.

## Staleness of disputes

Disputes evolve. A dispute that was "live" in 2015 may have been largely resolved by 2025 through meta-analysis, replication, or paradigm-shift.

Refresh protocol (adds to `currency-and-recency.md`):

- At 6-month refresh: review SKILL.md's "Unresolved debates" section. For each listed dispute:
  - Has a meta-analysis or replication study appeared that shifts the status?
  - Has the dispute been officially acknowledged resolved by both sides?
  - Has the dispute become obsolete (field moved on)?
- Update status accordingly; move resolved disputes to "Historical debates."

## Worked example: SKILL.md "Unresolved debates" for causal-inference-expert

```markdown
## Unresolved debates

1. **Potential outcomes vs DAGs (Pearl vs Rubin traditions)** — whether causal inference should center on potential-outcomes algebra or DAG-based identification. Formally largely equivalent for identification (Shpitser & Pearl 2008); emphasis and accessibility differ.
   - `references/debates/imbens-2020-potential-outcomes-vs-dags.md`
   - `references/debates/pearl-2018-book-of-why.md`
   - Status: **partial-translation-possible**; applied work typically picks one without engaging the dispute.

2. **RCT epistemic primacy (Deaton-Cartwright vs Banerjee-Duflo-Kremer)** — do RCTs deserve the privileged status they hold in empirical policy research-survey?
   - `references/debates/deaton-cartwright-2018-understanding-rcts.md` — critiques.
   - `references/findings/banerjee-duflo-2009-economic-lives-of-the-poor.md` — representative RCT program.
   - Status: **contested**; Nobel Prize 2019 to Banerjee/Duflo/Kremer signals mainstream endorsement, but Deaton's critiques remain cited.

3. **Heterogeneity estimation methods (HTE / CATE)** — many methods for estimating treatment-effect heterogeneity; no consensus on preferred approach.
   - `references/methodologies/athey-wager-2019-causal-forest.md`
   - `references/methodologies/chernozhukov-et-al-2018-double-ml.md`
   - Status: **methodological proliferation**; method-choice often application-dependent.

4. **Observational causal "deep-learning" methods** — growing literature; contested rigor.
   - `references/debates/pearl-2018-model-blind-limitations.md` — skeptical.
   - `references/methodologies/louizos-et-al-2017-causal-effect-inference.md` — affirmative.
   - Status: **contested**; active research-survey area.

## Resolved debates

- **Observational methods sufficient without experimental baseline** — LaLonde (1986) showed observational methods often mis-recover experimental estimates. While refined propensity methods (Dehejia-Wahba 1999) partially recover accuracy, the field largely agrees observational-only causal inference is unreliable absent strong identification assumptions. See `references/findings/lalonde-1986-evaluating-econometric-methods.md`.
```

## What this closes from v1.2's known gaps

v1.2 CHANGELOG noted: "Cross-figure / cross-paper contradiction detection — implicitly via `debates/` axis; could formalize."

This file formalizes:
- Four kinds of disagreement and how each is surfaced.
- Debates/-axis file shape vs cross-reference notes.
- SKILL.md "Unresolved debates" section template.
- Hedge discipline across disagreements.
- Claim-level contradiction handling (distinct from paper-level debates).
- Meta-analysis as dispute-resolution evidence.
- Staleness protocol for disputes.
- Worked SKILL.md example.

## Still deferred after this file

- **Automated verification harness** — auto-checking DOIs + retraction status + version supersession at scale. Requires implementation (not just documentation). Candidate for separate skill or CI integration.
- **Live validation runs** — dispatching an actual meta-theory-author wave to produce a real skill like causal-inference-expert. Requires execution.

These are genuinely execution-gated rather than doctrine-gated. The skill's doctrine layer is complete.
