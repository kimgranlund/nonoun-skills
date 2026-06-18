---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/academic-sourcing.md
  - ../structure/paper-summary-template.md
primary_sources:
  - https://www.copyright.gov/title17/92chap1.html#107 (17 USC §107 fair use)
  - https://www.nature.com/articles/d41586-019-02038-0 (Plan S overview)
  - https://www.coalition-s.org/
  - https://creativecommons.org/licenses/
---

# Access and quoting

Peer-reviewed papers are often paywalled. Finding legal access and handling fair-use quoting so the skill doesn't become a copyright problem.

## Access hierarchy

Prefer in this order:

1. **Open-access version of record** — CC-BY or CC-BY-NC journal, directly downloadable.
2. **Author-deposited preprint** — arxiv, bioRxiv, SSRN, institutional repository.
3. **Author website copy** — "green OA" self-archived versions.
4. **Institutional access** — via university library.
5. **Interlibrary loan** — slower but legal.
6. **Direct author request** — most authors share gladly; ResearchGate and email both work.
7. **Paywalled access via subscription** — acceptable for reading, not for redistributing.

Excluded: Sci-Hub, Library Genesis, and similar shadow libraries. Legal and policy risk not worth it.

## What the skill can and cannot redistribute

Even after obtaining legal access to a paper, the skill has limits on what it can include:

### Can include (under fair use, US 17 USC §107):

- **Summary / paraphrase** — your own words summarizing claims.
- **Short quotations** — ~100 words continuous, or ~10% of a very short paper, for comment/criticism.
- **Factual data** — a reported statistic (e.g., "N = 450 participants") isn't copyrightable.
- **Titles, authors, abstracts** — usually OK to reproduce (abstracts sometimes have their own license; check).
- **Tables of metadata** — author lists, citation counts.

### Cannot include:

- **Full text of the paper** — copyright violation.
- **Figures from the paper** unless CC-licensed.
- **Long verbatim passages** — beyond ~100 words continuous is risky.
- **Entire sections** — "here is the methods section" not OK.

### License-specific rules:

- **CC-BY**: attribution required, otherwise free to reuse.
- **CC-BY-SA**: attribution + derivative works must carry the same license.
- **CC-BY-NC**: attribution + non-commercial only.
- **CC-BY-ND**: attribution + no derivatives; summaries generally OK, modifications not.
- **CC0 / public domain**: no restrictions.
- **Traditional copyright** (most paywalled papers): fair use only.

Include the license in frontmatter when known:

```yaml
license: CC-BY-4.0
license_url: https://creativecommons.org/licenses/by/4.0/
```

## Quote budgets

Per reference file, recommend:

- **Zero to one quotation** of 50-100 words from each cited paper.
- **No quotations over 100 words** without explicit license permission.
- **No quotation of figures** unless license permits.

If the paper has a short critical passage (a definition, a theorem statement, a canonical formulation) that deserves direct quotation, use it sparingly. Paraphrase everything else.

### Quote format

Always include:
- Author attribution.
- Year.
- Page / section if the source is paginated.
- Inline citation.

Example:

> "We introduce the free-energy principle, which states that biological systems resist disorder by minimizing a bound on surprise" (Friston, 2010, p. 127). This formulation grounds the paper's central claim that …

Not:

> "The free-energy principle states that systems minimize surprise." This is a great claim.

The first quotes, attributes, and cites. The second paraphrases without clear attribution — which is worse because it obscures the source.

## Paywall navigation

When an agent is running scoping-survey or wave-authoring and hits a paywall:

1. **Search for an open preprint.** Use the paper title in arxiv, SSRN, institutional repository searches.
2. **Check the author's website.** Many authors self-archive.
3. **Use Unpaywall** (https://unpaywall.org/) — browser extension or API; surfaces legal OA copies.
4. **Check the DOAJ** if the journal might be OA.
5. **Request via ILL or direct email.** Slower, not suitable for wave-bound work.
6. **If still inaccessible**: cite the paper from its abstract and metadata only. Don't summarize content you haven't read.

Never use Sci-Hub. Skills shipping with Sci-Hub-sourced content create legal problems for consumers.

## Handling "we read the paper but can't redistribute it"

The scenario: agent has legal access (via institutional subscription), reads the paper, summarizes it in the reference file. But the skill will ship publicly — users without subscription access can't read the original.

This is fine. The skill is a summary, not a redistribution. Users who want the full paper can:

- Access via their own institution.
- Request from authors.
- Find the preprint.

The skill's value is the summary, not the source. As long as:
- Quote budgets are respected.
- Attribution is complete.
- Links point to the DOI / legal access paths, not pirate sites.

## Open-access policy landscape (2026-04)

- **Plan S** (European cOAlition S): requires full OA for funded research-survey.
- **US OSTP Nelson Memo** (2022): all federally funded US research-survey must be OA by 2026.
- **UKRI OA Policy** (2022): full OA required for UK-funded research-survey.

By 2026-04, a large and growing fraction of recent papers are OA by policy. Older papers remain mostly paywalled.

## When the paper is behind a "free to read but can't download" softwall

Some publishers (Science, Nature occasionally) offer free web reading but not PDF download. Summarize from the web version; cite the DOI normally. This is legal — you read it, you summarized it.

## Fair use is jurisdictional

The US §107 four-factor fair-use test (purpose, nature, amount, market effect) doesn't directly apply in the UK (fair dealing), EU (InfoSoc Directive exceptions), etc. A skill that ships globally should:

- Default to conservative quote budgets (works under most jurisdictions).
- Include full attribution and licensing metadata.
- Link to original papers for full access (don't substitute).

If the skill's author has jurisdiction-specific concerns, consult local fair-use / fair-dealing guidance.

## Attribution in frontmatter

Every paper-summary file includes:

```yaml
---
authors: [Pearl, J.]  # or multiple
year: 2009
title: Causality (2nd ed.)
venue: Cambridge University Press
doi: 10.1017/CBO9780511803161
license: copyright-all-rights-reserved  # or CC-BY-4.0 or similar
access_paths:
  - doi: https://doi.org/10.1017/CBO9780511803161
  - preprint: null
  - author_copy: http://bayes.cs.ucla.edu/BOOK-2K/
---
```

The `access_paths` field helps users find legal copies without you redistributing.

## What NOT to do

- **Don't scan-and-embed paywalled papers.** Even locally for the skill's own use during authoring.
- **Don't transcribe substantial sections verbatim.** Summary and short quote only.
- **Don't use Sci-Hub or LibGen.** Replace with legal preprint / ILL / author-request paths.
- **Don't claim a paper is OA when it isn't.** Inaccurate license metadata is worse than no metadata.

## When the license is ambiguous

Some older papers or unusual journals have unclear licensing. If you can't determine the license:

- Treat as traditional copyright (most restrictive).
- Quote minimally (50 words max).
- Link to DOI for full access.
- Note in frontmatter: `license: unclear`.

## Image and figure reproduction

Reproducing a figure from a paper requires one of:

- The figure is CC-BY (or similar permissive license).
- The skill obtains explicit permission from the rights-holder.
- The use clearly falls under fair use (parody, critical commentary on the figure itself).

Generally: **don't reproduce figures in theoretic-expert skills.** Describe the figure instead. Link to the paper for the actual image.
