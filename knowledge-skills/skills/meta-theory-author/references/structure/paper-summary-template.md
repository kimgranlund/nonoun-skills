---
date: 2026-04-18
coverage: deep
peers:
  - ../../meta-expert-author/references/structure/reference-file-template.md
  - ../methodology/academic-sourcing.md
  - ../methodology/peer-review-verification.md
  - ../methodology/access-and-quoting.md
primary_sources:
  - expert-color reference file conventions (inline Source/Author headers)
  - Academic paper-summary best practices (observational)
---

# Paper summary template

The file shape for one paper per reference file. Overrides meta-expert-author's generic `reference-file-template.md` with academic-specific frontmatter and structure.

## Frontmatter

Required fields. Anything the wave agent can't fill in must be explicitly null or flagged.

```yaml
---
# Identifiers
doi: 10.1038/nature12373
arxiv_id: 2401.12345v3       # if preprint or has preprint version
ssrn_id: null
nber_wp: null
# Bibliographic
authors:
  - Pearl, Judea
year: 2009
title: "Causality: Models, Reasoning, and Inference (2nd edition)"
venue: Cambridge University Press
venue_type: book             # journal | conference | book | preprint | working-paper | dissertation | technical-report
# Peer-review state
peer_review_status: peer-reviewed-published   # peer-reviewed-published | in-press | preprint-not-peer-reviewed | working-paper | dissertation | technical-report
venue_indexed: [WoS, Scopus]
publication_date: 2009-09-01
# Preprint lineage (if applicable)
preprint_version: null
preprint_posted: null
# Retraction / supersession
retraction_status: clean     # clean | corrected | concern | retracted
retraction_checked: 2026-04-18
superseded_by: null
# Access
license: copyright-all-rights-reserved
access_paths:
  - doi: https://doi.org/10.1017/CBO9780511803161
  - author_copy: http://bayes.cs.ucla.edu/BOOK-2K/
# Skill-internal
coverage: deep               # foundational | expanded | deep
paper_type: theoretical      # empirical | theoretical | methodological | review | meta-analysis | position
peers:
  - ../findings/lalonde-1986-evaluating-econometric-methods.md
  - ../debates/pearl-2018-critique-response.md
primary_sources:
  - https://doi.org/10.1017/CBO9780511803161
  - http://bayes.cs.ucla.edu/BOOK-2K/
---
```

## Title

Use the paper's title verbatim as the H1 heading. Don't paraphrase.

```markdown
# Causality: Models, Reasoning, and Inference (Pearl 2009, 2nd ed.)
```

Include the author-year in parens for scannability. Filename uses author-year-short-title slug: `pearl-2009-causality.md`.

## Body structure

```markdown
# [Title] ([Author] [Year])

**DOI**: https://doi.org/10.1038/nature12373
**Authors**: Judea Pearl
**Year**: 2009
**Venue**: Cambridge University Press (2nd ed.)
**Status**: peer-reviewed-published; not retracted (checked 2026-04-18)

[One-paragraph framing. What is this paper/book/chapter? Why is it in this skill's canon? What question does it primarily answer?]

## Abstract

[Verbatim abstract from the paper. Abstracts are typically OK to reproduce (check journal policy if uncertain — most are explicitly permissive). If the abstract exceeds 250 words, paraphrase and cite.]

## Contribution

[What does this paper do that prior work didn't? 2-4 sentences. Use paraphrase, not quotation.]

## Methods

[What methods does the paper use? Brief description. Important distinctions: experimental, observational, mathematical, simulation-based, meta-analytic.]

## Key findings

[Bulleted list of the paper's main findings or claims.]

- [Finding 1]
- [Finding 2]
- [Finding 3]

## Key distinctions

[Terms the paper introduces, refines, or conflates with others in the field. Essential for "greatest hits" SKILL.md content.]

- **[Term]** — [precise definition as used in this paper]
- **[Term]** — [definition]

## Notable quotations

[Up to 1-2 direct quotations, 50-100 words each. Full attribution + page. For critical commentary only.]

> "In a causal graph, a path is said to be blocked by a conditioning set Z if..." (Pearl 2009, p. 78)

## Limitations

[What the paper itself acknowledges as limitations, and what later work has flagged. Often the most useful section of a summary — the base model doesn't know these by default.]

## Replication / empirical status

[For empirical papers only. Has the finding replicated? What's the meta-analytic status? Cite any relevant replications or failure-to-replicate papers, cross-linked to their own summary files in the skill.]

- [Replication 1] — [summary + cross-ref]
- [Failed replication] — [summary + cross-ref]

## Citing / cited works in this skill

[Cross-references. What other files in this skill cite this paper or are cited by it?]

- Cites: [../methodologies/rubin-1974-potential-outcomes.md]
- Cited by: [../debates/imbens-2020-potential-outcomes-vs-dags.md]

## Where to dig further

[Follow-up papers, review articles, canonical critiques. Link to their summary files in this skill or external DOIs for papers not yet summarized.]

- [Pearl & Mackenzie 2018 *Book of Why*] — [doi]
- [Morgan & Winship 2015 *Counterfactuals and Causal Inference*] — [doi]

## Access

[DOI link + any legal OA alternatives. Explicit if paywalled.]

- DOI: https://doi.org/10.1017/CBO9780511803161
- Author's website (sample chapters): http://bayes.cs.ucla.edu/BOOK-2K/
- Paywalled via publisher. Many university libraries have access.
```

## Length

Paper summaries are typically **250-500 lines**. Not shorter (less than 250 lines suggests under-coverage); not longer (over 500 suggests it should be split).

For very dense books (e.g., Pearl 2009 is a 400-page book), summarize chapter-by-chapter in SEPARATE files:

- `pearl-2009-causality-chapter-1.md`
- `pearl-2009-causality-chapter-3.md`
- etc.

Each chapter-file is a standalone summary. Cross-reference via `peers:` frontmatter.

## Retracted paper variant

If the paper is retracted, the file starts with a prominent banner:

```markdown
# [Title] ([Author] [Year])

> ⚠️ **RETRACTED** (YYYY-MM-DD)
> 
> Reason: [brief description of retraction reason]
> Retraction notice DOI: [DOI]
> Retraction Watch entry: [URL]
> 
> This paper is cited here despite retraction because [reason — historical significance, influence before retraction, etc.].

[Rest of the summary follows normal template, but every claim is framed as "the retracted paper claimed..." rather than "X is true."]
```

## Preprint-only variant

Frontmatter has `peer_review_status: preprint-not-peer-reviewed` and includes version tracking. Body should have an explicit note:

```markdown
**Preprint status**: posted as arxiv 2401.12345v3 on 2024-11-15. Not yet peer-reviewed at time of this summary (2026-04-18). Next refresh will check for published version.
```

## Multi-paper-program footnote

If a paper is part of a series (e.g., Pearl has written 30+ causal-inference papers over decades), don't merge them into one file. Keep one file per paper, and use `peers:` frontmatter to link them.

For navigation, a **schools/** or **figures/** file can summarize the author's overall trajectory across many papers (capability-mode) — but each individual paper still gets its own one-paper-per-file treatment.

See `theoretical-axes.md` § "Mixed-mode for schools and figures."

## When the paper has multiple main results

Summarize all of them. The "Key findings" section can have 5-10 bullets if warranted. Don't artificially reduce to "the one main result" — that loses information.

## When the paper is a replication

Label it clearly:

```markdown
# [Title]: a replication of [Original Author Year]

This paper is an explicit replication attempt of [original paper]. Summary below focuses on the replication outcome, not re-derivation of the original theory.

## Replication design

[How the replication was conducted.]

## Replication outcome

[Did the finding replicate? Effect size comparison. Statistical power. Etc.]

## Implications for the original

[What this says about the original paper's claim. Supports it? Weakens it? Inconclusive?]
```

Replication papers are load-bearing for the skill's "replication status" SKILL.md section.

## Paper-type typology

The `paper_type:` frontmatter field classifies the paper's genre. This helps readers and subsequent files know what KIND of claim is being summarized, which constrains how it can be cited.

| Value | Meaning | Example |
|---|---|---|
| `empirical` | Reports empirical findings from new data collection | RCT, observational study, experiment |
| `theoretical` | Proposes a theoretical framework, formalism, or proof | Pearl 2009 *Causality*, Friston 2010 free-energy principle |
| `methodological` | Introduces or critiques a method | Angrist-Imbens-Rubin 1996 IV method paper |
| `review` | Non-systematic review of a literature | Narrative review, annual review article |
| `meta-analysis` | Systematic quantitative synthesis | Cochrane review, PRISMA-compliant meta-analysis |
| `position` | Argues a stance without primary empirical claims | Philosophical position paper, vision paper, critical commentary |

### Mixed-type papers

Some papers combine types (e.g., introduce a method AND apply it to new data). Pick the primary type:

- If the methodological contribution is the novelty → `methodological`.
- If the empirical finding is the novelty → `empirical`.

Note the combination in the body (e.g., "This paper introduces [method] and applies it to [question]."). The `paper_type:` field reflects the primary contribution.

### Why this matters

Different paper types carry different epistemic weight:

- **Empirical** claims need replication tracking.
- **Theoretical** claims need assumption-explicitness.
- **Methodological** claims need comparison-to-prior-methods.
- **Review** claims are secondary synthesis — don't cite as primary.
- **Meta-analysis** claims aggregate primary studies — note the pool.
- **Position** claims are arguments, not findings — "argued" not "established."

The SKILL.md's "greatest hits" section should weight paper-type when citing. A `position` paper arguing X is different evidence than an `empirical` paper reporting X.

## Quality checklist

Before promoting a paper-summary file to ✅ in INDEX.md:

- [ ] DOI resolves (or explicit null with justification).
- [ ] Peer-review status declared, verified via WoS/Scopus/DOAJ.
- [ ] Retraction checked, `retraction_checked` date set.
- [ ] Authors, year, venue in frontmatter.
- [ ] `paper_type:` field set (empirical / theoretical / methodological / review / meta-analysis / position).
- [ ] Abstract included verbatim or paraphrased + cited.
- [ ] Contribution, methods, key findings sections present.
- [ ] Key distinctions section identifies terms the base model conflates.
- [ ] Limitations section present.
- [ ] Quotations within fair-use budget (≤ 100 words continuous, attributed).
- [ ] Cross-references to other files in the skill via `peers:`.
- [ ] Access paths listed for legal OA or DOI.
