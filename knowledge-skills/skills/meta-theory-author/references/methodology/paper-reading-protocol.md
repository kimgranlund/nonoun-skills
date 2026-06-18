---
date: 2026-04-18
coverage: deep
peers:
  - ../methodology/web-search-patterns.md
  - ../methodology/paper-discovery.md
  - ../structure/paper-summary-template.md
primary_sources:
  - Keshav, S. (2007). "How to read a paper." ACM SIGCOMM CCR 37(3):83-84. https://doi.org/10.1145/1273445.1273458
  - Loseke, D. (2017). Methodological Thinking. Sage.
  - Ioannidis, J.P.A. (2005). "Why most published research-survey findings are false." PLoS Medicine 2(8):e124. https://doi.org/10.1371/journal.pmed.0020124
---

# Paper-reading protocol

How to read a paper well enough to summarize it faithfully. Operational discipline so meta-theory-author skills don't accumulate over-confident paraphrases.

## The three-pass method (Keshav 2007)

Canonical. Every meta-theory-author summary is based on at least pass 1 + pass 2; deep-coverage files require pass 3.

### Pass 1 — scan (5-10 minutes)

Read:
- Title, abstract, introduction.
- Section and sub-section headings.
- Conclusion.
- References (scan for familiar citations).

After pass 1, answer:

1. **Category**: What type of paper? (Empirical study? Theoretical proof? Position paper? Systematic review? Methodology paper?)
2. **Context**: What related papers are cited?
3. **Correctness**: Do the assumptions look valid?
4. **Contributions**: What's the main contribution? (In the paper's own words, from the intro.)
5. **Clarity**: Is the paper well-written?

If any answer is "unclear after pass 1," the paper may be poorly structured — proceed carefully.

### Pass 2 — read for content (~1 hour)

Read the paper carefully but skip heavy math / proofs. Focus on:
- Figures, tables, and their captions — often where the core empirical claims live.
- Methods section — the actual design of the study.
- Results section — the actual numbers, not just the prose summary.
- Limitations section — what the authors themselves acknowledge.

After pass 2, you should be able to:
- State the main claim to someone else in 1-2 sentences.
- Describe the methods in enough detail that someone could replicate (at least in principle).
- List the paper's main limitations.

If a paper fails pass 2 — you still can't summarize it after an hour of reading — the paper may be genuinely unclear, or you're missing prerequisites. For meta-theory-author purposes, **don't write a summary you couldn't explain to someone else**.

### Pass 3 — virtual re-implementation (~2-5 hours)

Read to challenge the paper:
- Mentally re-derive the theorems / re-run the experiments.
- Spot assumptions that aren't justified.
- Identify what's novel vs what's borrowed from prior work.
- Notice where the authors might have cherry-picked results.
- Look up references for claims that seem surprising.

After pass 3, you have near-expert knowledge of the paper — including its weaknesses.

Pass 3 is needed for `coverage: deep` files. Optional for `coverage: expanded` or `foundational`.

## Claim extraction

Every paper makes multiple kinds of claims. The summary file distinguishes them.

### Claim types

| Type | Example | How to cite |
|---|---|---|
| **Primary claim** | "Transformers outperform LSTMs on machine translation." | In "Key findings" with specific numbers + effect size |
| **Secondary claim** | "This suggests attention is useful for sequence modeling broadly." | In discussion; label as "suggestive" |
| **Methodological claim** | "We introduce multi-head attention." | In "Methods" |
| **Theoretical claim** | "Attention is a case of kernel regression." | In "Contribution" with caveat if not fully proven |
| **Speculative claim** | "Future work should explore X." | Briefly noted; not the paper's contribution |

Don't conflate speculative claims with primary results. Authors often include "future work" speculations that shouldn't be cited as findings.

### Claim verification

For each primary claim:

- **Check the effect size** — not just statistical significance.
- **Check the sample size** — small-N studies have high variance.
- **Check the control condition** — what's the baseline?
- **Check confidence intervals** — if not reported, flag the paper.
- **Check for preregistration** — if preregistered, claims are more credible.

If the paper's claims are reported vaguely ("significant improvement" without numbers), the summary should reflect that vagueness — don't manufacture concreteness the paper lacks.

## Weakness-detection checklist

Based on Ioannidis 2005 + replication-crisis lessons. Every paper-summary author should scan for these:

### Empirical weakness signals

- **Low statistical power** — small samples for effects the authors claim are robust.
- **Post-hoc analysis framed as pre-specified** — look for phrases like "we decided to examine" without preregistration.
- **Arbitrary cutoffs** — "we defined X as above Y" without justification for Y.
- **Multiple comparisons without correction** — many tests, one significant result.
- **Selective reporting** — results hinted at but not fully reported; supplementary material with additional tests.
- **Small effect sizes called "robust"** — be skeptical.
- **Replications not attempted** — common in novel findings; not fatal but worth noting.

### Theoretical / methodological weakness signals

- **Undefined key terms** — if the paper introduces a new concept without a precise definition, it's a red flag.
- **Unjustified assumptions** — every model has assumptions; papers that don't foreground them are hiding something.
- **Circular reasoning** — definition of the phenomenon implies the conclusion.
- **Citation padding** — citing your own or in-group papers excessively.
- **Strawman opponents** — if the paper critiques "common approaches" without citing specific examples.

### Venue / review signals

- **Predatory journal** (see `peer-review-verification.md`).
- **Conference-only with no journal version** — for fields where journal publication is the norm, this is a weakness signal.
- **No preregistration** — in fields that have adopted preregistration, absence is noted.

### Retraction / concern signals

- **Expression of concern** — documented concerns about integrity.
- **Author under investigation** — check retraction-tracker indices.
- **Paper replicated and failed** — cite the failed replication.

## Summary faithfulness

The summary file must not claim more than the paper does.

### Faithful summary

- States the paper's primary claim in the paper's own framing.
- Reports effect sizes + sample sizes + confidence intervals where the paper reports them.
- Notes limitations the paper itself acknowledges.
- Notes weaknesses YOU identified (clearly labeled as your commentary, not the paper's).
- Cross-references replication attempts, critiques, follow-ups.

### Unfaithful summary (avoid)

- "Pearl proved that causality requires DAGs" — Pearl did not prove this. He developed a framework. Don't overclaim.
- "This study showed X works" — if the study measured a correlated outcome in one population, don't generalize.
- "Smith (2023) established that Y" — if Smith's paper is a single study, "established" is too strong. Use "argued," "reported," "suggested."
- Omitting the paper's caveats — if the paper says "we found X, but only under conditions Y," the summary must include Y.

### Hedge discipline

When in doubt, hedge. Good hedges:

- "The paper argues..."
- "This study reported..."
- "The authors claim..."
- "Under the assumptions of..."

Bad (over-confident) phrasings:

- "X is true because..."
- "This proves..."
- "The fact that..."

Academic citations always carry epistemic caveats. Preserve them.

## Reading for critical sections

Some sections deserve disproportionate attention:

### Methods

- **For empirical papers**: the most important section. Vague methods = unreproducible results.
- **For theoretical papers**: the assumptions and setup define what's proven.
- **Red flag**: vague descriptions of data, preprocessing, or exclusion criteria.

### Tables

- Contain the actual results. Prose summaries simplify; tables reveal.
- Check sample sizes per cell, confidence intervals, significance levels.
- Check if the "headline" result is one row out of many reported.

### Figures

- Often the paper's argument in compressed form.
- Check axis labels, error bars, log vs. linear scales.
- Check that figure captions describe what's shown, not what the authors wish were shown.

### Limitations section

- The paper's own acknowledged weaknesses.
- Often at the end of the discussion; sometimes a dedicated "Limitations" header.
- If there's no limitations section, the paper is incomplete — note this in your summary.

### References

- Who does this paper cite? Who doesn't it cite? (Omissions are often tellable.)
- Are key prior works included?
- Are there citation patterns suggesting an in-group?

## Distinguishing paper types

Different paper types have different reading strategies:

### Empirical paper (RCT, observational study, experiment)

- Focus: methods + results + tables.
- Critical: sample size, controls, effect sizes, preregistration.
- Risk: p-hacking, post-hoc framing, selective reporting.

### Theoretical paper (proof, framework, definition)

- Focus: definitions + theorems + assumptions.
- Critical: precise definitions, explicit assumptions, novel vs. restated.
- Risk: vague key terms, circular arguments, conflation with prior work.

### Methodology paper (new method, comparison, algorithm)

- Focus: algorithm description + evaluation + baselines.
- Critical: what's the baseline, what's the improvement, how general is the method.
- Risk: weak baselines, cherry-picked benchmarks, narrow applicability.

### Review / meta-analysis

- Focus: search strategy + inclusion criteria + synthesis.
- Critical: was the search systematic, were studies pre-registered, is there meta-analytic technique.
- Risk: biased selection, narrative synthesis without weighting, outdated corpus.

### Position / theory paper

- Focus: thesis + argument structure + engagement with opposing views.
- Critical: is the position new, does it address known counters, is it falsifiable.
- Risk: strawman opponents, untestable claims, style over substance.

## When you can't read the paper

Several scenarios:

### Paywalled

See `access-and-quoting.md`. Use Unpaywall, preprint, ILL, or author request. Don't cite without reading.

### In a language you can't read

- Get a translation (Google Translate for gist; professional translation for critical use).
- If translation quality is doubtful, flag the summary as "partial; based on translated version of abstract."
- Don't cite as if you've read it thoroughly.

### Too technically specialized

If the paper is genuinely beyond your background (e.g., a deep-learning person reading a category-theory proof):

- Read the abstract, introduction, and conclusion at minimum.
- Find a secondary source (review, textbook chapter) that contextualizes it.
- Summary should be labeled "coverage: foundational" and note the limitation.
- Don't fake technical depth. Stay at the level you actually understand.

## Agent-brief requirement

Every meta-theory-author wave agent brief must include:

> **Paper-reading protocol** (from `../methodology/paper-reading-protocol.md`):
> - Do at least pass 1 + pass 2 (Keshav 2007) on every paper before summarizing.
> - For `coverage: deep` files, pass 3 is required.
> - Extract primary claims, methods, results with specifics (effect sizes, sample sizes, CIs).
> - Flag weakness signals: low power, post-hoc framing, multiple comparisons, strawman arguments, vague definitions.
> - Hedge discipline: preserve the paper's epistemic level ("argued" not "proved" unless the paper actually proved it).
> - Summary faithfulness: summary must not claim more than the paper.
> - If you cannot read the paper (paywall unresolved, language barrier, specialized technique), REPORT the gap; do NOT fake the summary from the abstract.

## Worked example: how to read a transformer paper

Vaswani et al. 2017 "Attention Is All You Need" — what the three passes would look like.

### Pass 1 (5-10 min)

- **Category**: methodology paper — introduces new architecture.
- **Context**: cites RNN/LSTM baselines; seq2seq literature.
- **Correctness**: well-established ML venue (NeurIPS 2017).
- **Contributions**: "We propose the Transformer, a model architecture eschewing recurrence and relying entirely on attention mechanisms..." (paper's own framing).
- **Clarity**: clean prose; diagrams support text.

### Pass 2 (~1 hour)

- Methods: attention mechanism, multi-head attention, positional encoding, encoder-decoder structure.
- Results tables: Table 2 shows BLEU scores on WMT 2014 En-De (28.4) and En-Fr (41.0); baselines in range 26.3-28.1.
- Limitations: the paper doesn't explicitly discuss limitations; scaling behavior is noted for En-De but not rigorously.

### Pass 3 (~3-5 hours)

- Re-derive attention formula; notice dot-product vs additive choice and why.
- Question: why does the paper not report standard deviations across training runs?
- Question: the positional encoding choice (sinusoidal) is novel — is this justified empirically or just ablated?
- Check the subsequent literature: many transformer papers use learned positional encodings instead. Worth noting in the summary.

A paper-summary file based on this reading protocol would cite specific BLEU numbers, note the limited limitations section, and cross-reference follow-up papers (e.g., Devlin et al. 2018 BERT) via the skill's own file manifest.

## The epistemic humility principle

Summarizing papers is an act of trust. The reader of your summary will cite your summary instead of reading the paper. If your summary overclaims, the overconfidence propagates.

The rule: **the summary should be at most as confident as the paper itself.** If the paper says "suggests," the summary says "suggests." If the paper says "proves under assumptions A, B, C," the summary preserves those assumptions.

When in doubt, read the paper again. Two hours of re-reading is cheaper than a skill that misleads consumers for years.
