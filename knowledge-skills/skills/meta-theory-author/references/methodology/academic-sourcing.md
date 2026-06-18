---
date: 2026-04-18
coverage: deep
peers:
  - ../methodology/peer-review-verification.md
  - ../methodology/currency-and-recency.md
  - ../methodology/access-and-quoting.md
primary_sources:
  - https://www.doi.org/
  - https://arxiv.org/help/policies
  - https://www.biorxiv.org/about-biorxiv
  - https://www.ssrn.com/index.cfm/en/about-us/
  - https://www.nber.org/
---

# Academic sourcing

What counts as a primary source in a theoretic-expert skill, how to rank them, and what's excluded by policy.

## The source-durability ranking

Stricter than meta-expert-author's generic ranking. For meta-theory-author:

| Tier | Source type | Example | Why this tier |
|---|---|---|---|
| **1** | Peer-reviewed journal article with DOI | Nature, Science, JASA, PRL, PNAS, PLOS ONE | Indexed, retraction-tracked, version-stable |
| **2** | Peer-reviewed conference paper with DOI | NeurIPS, ICML, ACL, CHI, STOC | Indexed, venue-reviewed |
| **3** | Book from academic publisher with DOI / ISBN | Cambridge, MIT Press, Springer monograph | Editorially reviewed |
| **4** | Preprint on recognized server | arxiv, bioRxiv, medRxiv, SSRN, PsyArXiv | Version-stable identifier; may or may not be later peer-reviewed |
| **5** | Working paper on recognized series | NBER, IZA, CEPR, CESifo | Institutionally vetted |
| **6** | Dissertation / thesis from accredited institution | ProQuest, institutional repository | Committee-reviewed |
| **7** | Technical report from recognized lab | Microsoft Research, MILA, Allen Institute | Author-attributed but not peer-reviewed |
| **8** | Conference proceedings (workshop, poster) | NeurIPS workshops, ICML workshops | Lightly reviewed, inclusion-rate high |
| — | **Excluded** | Blog posts, Substack, company research-survey blogs, podcast transcripts, YouTube except recorded conference talks, Wikipedia | Not peer-reviewed, no citation-stability guarantee |

Tier 1-3 are canonical. Tier 4-6 are acceptable with explicit labeling. Tier 7-8 are used sparingly and labeled. Everything below is excluded.

## What about the gray zone?

### Company research-survey blogs (DeepMind, OpenAI, Anthropic, Google Research)

- **Excluded by default.** These are not peer-reviewed, and company blogs can be revised or removed silently.
- **Exception**: if a company research-survey blog post has an accompanying paper on arxiv, cite the arxiv paper instead. The blog is commentary; the paper is the record.

### Textbooks

- **Tier 3** if from an academic publisher (Cambridge UP, MIT Press, Springer, Elsevier academic imprints).
- **Tier 7** for technical books from trade publishers (O'Reilly, Manning) — useful but not peer-reviewed.
- **Excluded** for self-published technical books without peer review.

### Lecture notes

- **Tier 7** for faculty-authored course notes posted on .edu sites with identifiable authorship and stable URLs.
- **Excluded** for student-authored summaries, review sites, tutorial pages.

### Wikipedia

- **Excluded as a primary source.** Acceptable only as a starting-point reference in "See also" footers, never in the primary_sources frontmatter.
- Reason: editable, no stable citation, no peer review.

### Talks / podcasts / interviews

- **Excluded as primary sources even if the speaker is a canonical figure.** A Geoffrey Hinton podcast interview is not a primary source for his theories — cite his papers instead.
- **Exception**: recorded conference talks at ranked venues (NeurIPS invited, AAAI Turing lecture, Nobel Prize lecture) may be tier 8, with the DOI of the associated paper preferred when available.

### Preregistration documents

- **Tier 4-5** if posted on recognized registries (AsPredicted, OSF, ClinicalTrials.gov).
- Useful for tracking the theoretical commitments of a paper before data collection.

## Preprint platforms

| Platform | Fields | DOI? | Versioning | Withdrawal policy |
|---|---|---|---|---|
| **arxiv.org** | Physics, CS, math, stats, quant-bio, q-fin, econ | Yes (since ~2020, rolled out gradually) | v1, v2, … explicit versions | Authors can withdraw; earlier versions preserved |
| **bioRxiv / medRxiv** | Biology / medicine | Yes | Explicit versions | Authors can withdraw |
| **SSRN** | Social sciences, law, economics | Has SSRN ID; DOI varies | Version-tracked | Withdrawals happen; platform keeps record |
| **PsyArXiv** | Psychology | Yes (via OSF) | Version-tracked | OSF retention |
| **ChemRxiv** | Chemistry | Yes | Version-tracked | |
| **ResearchGate preprints** | Various | Sometimes | Not always version-tracked | NOT RELIABLE — prefer original platform |

Citing a preprint means citing a specific version. Never cite "the preprint" — cite v2 or v3 by its URL-with-version (arxiv URLs include the version: `arxiv.org/abs/2103.00020v1`).

## Working-paper series

- **NBER** (National Bureau of Economic Research) — economics and econometrics. Every paper has an NBER WP number. Often later published in journals.
- **IZA Institute of Labor Economics** — labor economics. IZA DP number.
- **CEPR** (Centre for Economic Policy Research) — European economics. CEPR DP number.
- **CESifo** (Munich) — public economics.
- **SSRN** — cross-field, but especially law and finance.

Working papers are tier 5 — higher than preprints in some fields because they undergo an institutional review. Cite by series name + paper number + DOI if available.

## What DOI gives you

- **Persistent identifier**: the URL `https://doi.org/<doi>` resolves to the current canonical location even if the publisher moves or renames URLs.
- **Citation-graph inclusion**: DOI is what Semantic Scholar, Google Scholar, Crossref, OpenAlex index against.
- **Retraction tracking**: retractions are logged against DOIs.

**No DOI = no file** unless an explicit fallback identifier is used AND the frontmatter flags the DOI absence with `doi_status: "not-issued"` or `doi_status: "pending"`.

## Search surfaces

Where to find papers to cite:

| Surface | Scope | Rank-by |
|---|---|---|
| **Google Scholar** | Broad, multidisciplinary | Citation count |
| **Semantic Scholar** | Broad, AI-aided | Semantic match + influence |
| **OpenAlex** | Broad, fully open | Metadata richness |
| **Crossref** | Metadata for DOIs | Registered works |
| **PubMed / MEDLINE** | Biomedicine | Medical indexing |
| **arxiv listing** | CS / physics / stats | Daily updates |
| **SSRN** | Social sciences | Recent submissions |
| **INSPIRE-HEP** | High-energy physics | Specialized |
| **zbMATH** | Mathematics | Specialized |
| **Philpapers** | Philosophy | Specialized |

Agents doing scoping surveys should use Google Scholar or Semantic Scholar for breadth, then verify each candidate via Crossref for DOI resolution.

## Agent-brief adaptations

When dispatching wave agents for a theoretic-expert skill, the brief should include this paragraph:

> **SOURCE DISCIPLINE** (meta-theory-author override):
> - Primary sources MUST be tier 1-5 from `academic-sourcing.md` (peer-reviewed journals, conference papers, academic books, preprints, working papers).
> - Every file's frontmatter includes a `doi:` field. If no DOI, use `arxiv_id:`, `ssrn_id:`, or `nber_wp:` and add `doi_status: "not-issued"`.
> - Exclude blog posts, company research-survey blogs (cite the arxiv version instead), YouTube non-conference, Wikipedia, podcast transcripts, Medium, Substack.
> - For each paper, verify peer-review status and retraction status via Crossref or Retraction Watch (see `peer-review-verification.md`).
> - Report any paper whose primary source you couldn't cleanly place in tiers 1-5; the main thread will adjudicate.

## Fallback when a claim has no academic source

If a claim you want to make has no peer-reviewed source:

1. **Check preprint servers** — maybe a working paper exists.
2. **Check dissertations** — ProQuest or institutional repositories.
3. **Check technical reports** — tier 7 but acceptable with labeling.
4. **If still nothing**: omit the claim, or explicitly label it "(not yet treated in peer-reviewed literature; cited here from [identifier])."

Don't import blog posts to fill gaps. The skill's value is source discipline — compromising it for one claim erodes the whole.

## Common rookie mistakes

- **Citing a news article that reports on a paper.** Cite the paper directly.
- **Citing a thread by a paper's author on Twitter/X explaining the paper.** Cite the paper.
- **Citing an author's blog where they informally summarize their own work.** Cite the paper.
- **Citing a tutorial that implements a paper's method.** Cite the paper.
- **Citing a Wikipedia article that summarizes the field.** Cite the primary sources Wikipedia cites.

The pattern: when a secondary source summarizes a primary source, cite the primary source. The secondary is for finding the primary, not for the claim itself.
