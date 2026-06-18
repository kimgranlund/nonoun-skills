---
date: 2026-04-18
coverage: deep
peers:
  - ../methodology/web-search-patterns.md
  - ../methodology/academic-sourcing.md
  - ../methodology/paper-reading-protocol.md
primary_sources:
  - https://scholar.google.com
  - https://www.semanticscholar.org/
  - https://openalex.org/
  - https://api.crossref.org/
  - https://arxiv.org/
  - https://unpaywall.org/
---

# Paper discovery

Where to look for peer-reviewed papers, preprints, and working papers. Operational surfaces with URL patterns, API endpoints, and when to prefer each.

## The five primary search surfaces

### 1. Semantic Scholar — best default for AI-aided discovery

- **URL pattern**: `https://www.semanticscholar.org/search?q=<query>`
- **API**: `https://api.semanticscholar.org/graph/v1/paper/search?query=<query>&limit=20&fields=title,authors,year,venue,abstract,citationCount,openAccessPdf,externalIds`
- **Why prefer**: semantic (not keyword) ranking; rich metadata; citation graph; free API with no key for moderate volumes.
- **Caveats**: coverage skewed toward CS / biomed; weaker in humanities.
- **Use for**: initial discovery; finding canonical papers by concept; citation-graph traversal.

### 2. Google Scholar — broadest coverage

- **URL pattern**: `https://scholar.google.com/scholar?q=<query>`
- **API**: none (blocks scraping; use only via browser or WebFetch sparingly).
- **Why prefer**: broadest index; well-ranked citation counts; finds grey literature.
- **Caveats**: no API, results not always stable, rate-limits aggressively.
- **Use for**: sanity-checking Semantic Scholar; finding papers in fields SS covers poorly.

### 3. OpenAlex — fully open, free, API-first

- **URL pattern**: `https://openalex.org/works?search=<query>`
- **API**: `https://api.openalex.org/works?search=<query>&per-page=25&filter=type:article`
- **Why prefer**: fully open, no key required, rich metadata (authors, institutions, concepts, OA status).
- **Caveats**: younger than competitors; concept tagging sometimes noisy.
- **Use for**: systematic retrieval; when you need structured JSON; when API rate limits matter.

### 4. Crossref — canonical for DOI resolution + metadata

- **URL pattern**: `https://search.crossref.org/?q=<query>`
- **API**: `https://api.crossref.org/works?query=<query>&rows=20`
- **Why prefer**: authoritative DOI source; most reliable for retraction/correction status via CrossMark; metadata for ~150M works.
- **Caveats**: query relevance weaker than Semantic Scholar; metadata richness varies.
- **Use for**: DOI-to-paper resolution; retraction checks; verifying metadata from other sources.

### 5. Unpaywall — legal open-access resolver

- **URL pattern**: `https://api.unpaywall.org/v2/<doi>?email=<your-email>`
- **API**: free, email required.
- **Why prefer**: surfaces legal OA versions of paywalled papers (preprint copies, author self-archives, green OA).
- **Caveats**: only resolves DOIs you already have.
- **Use for**: finding readable version of a paywalled paper; access-path discovery.

## Preprint-server-specific surfaces

### arxiv — CS, math, physics, stats, quant-bio, econ, q-fin

- **Search UI**: `https://arxiv.org/search/?searchtype=all&query=<query>`
- **Listing**: `https://arxiv.org/list/<category>/<year>-<month>` (e.g., `cs.LG/2024-11`).
- **Export API**: `http://export.arxiv.org/api/query?search_query=<query>&start=0&max_results=20`
- **Full text**: `https://arxiv.org/pdf/<paper-id>v<version>` (e.g., `2401.12345v3`).
- **HTML version (Oct 2023+)**: `https://arxiv.org/html/<paper-id>v<version>` — much easier for WebFetch.
- **Abstract page**: `https://arxiv.org/abs/<paper-id>` (landing page with DOI, citations, related).

### bioRxiv / medRxiv — biology / medicine preprints

- **Search**: `https://www.biorxiv.org/search/<query>` or `medrxiv.org/search`.
- **API**: `https://api.biorxiv.org/details/biorxiv/<DOI>` (for specific papers).
- **PDFs**: downloadable from each paper's page.

### SSRN — social sciences, law, finance, economics

- **Search**: `https://www.ssrn.com/index.cfm/en/scholarly-papers-and-eJournals/search/?txtKey_Words=<query>`
- **API**: limited.
- **Caveats**: some papers paywalled; preprint "versions" tracked.

### NBER — economics working papers

- **Search**: `https://www.nber.org/papers?page=1&q=<query>`
- **Listing**: by working-paper number (`nber.org/papers/w<nnnn>`).
- **Download**: PDF free after 18-month embargo; free for academics immediately.

### PsyArXiv / SocArXiv / others — field-specific OSF preprints

- **PsyArXiv**: `https://psyarxiv.com/search?q=<query>`
- **SocArXiv**: `https://osf.io/preprints/socarxiv/discover?q=<query>`
- **Other OSF preprints**: `https://osf.io/preprints/` (ChemRxiv, engrXiv, LawArXiv, etc.).

## Field-specialized indexes

| Field | Index | URL |
|---|---|---|
| Biomedicine | PubMed / MEDLINE | https://pubmed.ncbi.nlm.nih.gov/ |
| High-energy physics | INSPIRE-HEP | https://inspirehep.net/ |
| Mathematics | zbMATH | https://zbmath.org/ |
| Mathematics (alt) | MathSciNet | https://mathscinet.ams.org/ (paywalled) |
| Philosophy | PhilPapers | https://philpapers.org/ |
| Psychology | PsycINFO | https://www.apa.org/pubs/databases/psycinfo (paywalled) |
| Education | ERIC | https://eric.ed.gov/ |
| Engineering | IEEE Xplore | https://ieeexplore.ieee.org/ |
| CS | DBLP | https://dblp.org/ |
| Economics | RePEc / IDEAS | https://ideas.repec.org/ |
| Climate / earth sci | NASA ADS | https://ui.adsabs.harvard.edu/ |

## Search strategies by use case

### Use case 1: "find canonical papers in [field / sub-field]"

1. **Semantic Scholar**: search by field name + "review" or "introduction" — review papers cite the canon.
2. **Google Scholar**: search `<field>` sorted by citations — top 20 results usually include most canonical papers.
3. **Textbook references**: find an established textbook (Cambridge / MIT Press / Springer) — its bibliography lists the canon.
4. **Award lists**: ACL Lifetime Achievement, Turing Award citations, Nobel lectures — field canons often align with award recognitions.

### Use case 2: "find latest papers on [specific topic]"

1. **arxiv listing by category + time range**: `arxiv.org/list/cs.LG/2024-11` gives Nov 2024 ML papers.
2. **Google Scholar with year filter**: `scholar.google.com/scholar?q=<topic>&as_ylo=2024`.
3. **Semantic Scholar API with year filter**: include `year:2024-2026` in query.
4. **Twitter/X** — surprisingly useful for pointer-to-paper even though Twitter itself is excluded as a source.

### Use case 3: "find the follow-up / critique of [paper]"

1. **Semantic Scholar "Cited By" view** — `semanticscholar.org/paper/<paper-id>` has a Cited By tab.
2. **OpenAlex citation relations**: `api.openalex.org/works/<work-id>?select=referenced_works,related_works`.
3. **Google Scholar "Cited by" link** — on any Scholar result.
4. **Connected Papers** (connectedpapers.com) — visual graph of related work.

### Use case 4: "find all papers by [author]"

1. **Semantic Scholar author page**: `semanticscholar.org/author/<author-name>`.
2. **Google Scholar profile**: `scholar.google.com/citations?user=<profile-id>`.
3. **OpenAlex author**: `api.openalex.org/authors?search=<name>`.
4. **ORCID**: `orcid.org/<0000-xxxx-xxxx-xxxx>` — author's own-maintained list.

### Use case 5: "resolve DOI to full text"

1. `doi.org/<doi>` — resolves to publisher landing page (may be paywalled).
2. **Unpaywall** API — surfaces legal OA version.
3. Author's website / ResearchGate — check manually.
4. **arxiv ID from the paper's metadata** — if DOI paper exists on arxiv, preprint is OA.

## Snowball search

When you have one canonical paper and need to find related work:

### Forward snowball (what came after)

- Semantic Scholar "Cited By" list.
- Filter by year to get recent citations.
- Look for highly cited follow-ups + critiques.

### Backward snowball (what it cites)

- The paper's own reference list.
- Semantic Scholar "References" tab gives structured access.
- Often reveals the canon that the paper itself builds on.

### Sideways snowball (co-citation)

- Connected Papers — visual graph.
- Semantic Scholar "Related Papers" tab.
- Papers frequently co-cited with yours suggest topic-adjacent work.

## Coverage gaps to know about

- **Books**: most of the above surfaces prioritize articles. For books, use OpenLibrary, Google Books, WorldCat, or publisher catalogs.
- **Non-English literature**: Semantic Scholar and Google Scholar have incomplete non-English coverage. CNKI for Chinese, CiNii for Japanese, SciELO for Latin American.
- **Dissertations**: ProQuest Dissertations & Theses (paywalled), OpenThesis, DART-Europe.
- **Grey literature**: government reports, think-tank papers, institutional working papers — Google is often best.
- **Very recent preprints (<48 hours)**: arxiv homepage listings; sometimes haven't indexed yet.

## Quantity discipline

For a wave's scoping survey:

- Run 15-30 queries across 3-5 surfaces.
- Don't stop at one query per topic — search the same concept with different phrasings.
- Capture DOIs, arxiv IDs, and landing-page URLs for every candidate paper.
- Target ~2-3x the file count of the planned skill (e.g., 100 candidate papers for a 45-paper skill).
- Filter candidates via peer-review + retraction check before adding to INDEX.

## What NOT to do

- **Don't rely only on one surface.** Semantic Scholar + one other minimum.
- **Don't trust citation counts alone.** Influential papers get cited for wrong reasons too.
- **Don't skip retraction checks.** Every candidate gets verified (see `peer-review-verification.md`).
- **Don't use Sci-Hub.** Unpaywall + preprints + author-website + ILL cover ~95% of what you need legally.
- **Don't cite from summaries.** Summary found the paper — go read the paper itself before citing.

## Agent-brief guidance

Every meta-theory-author wave agent brief must include:

> **Paper-discovery protocol:**
> - Use WebSearch AND WebFetch liberally. WebSearch for initial discovery (Semantic Scholar, Google Scholar, arxiv, OpenAlex, Crossref). WebFetch for specific paper landing pages.
> - Search at least 2 surfaces per topic. Don't rely on one.
> - Capture DOI, arxiv ID, authors, year, venue for every candidate.
> - Verify peer-review status via Crossref / WoS / Scopus / DOAJ before adding to file manifest.
> - Check retraction status via Retraction Watch.
> - See `../methodology/web-search-patterns.md` for specific query patterns.

## When a paper seems important but has no findable version

Rare but happens. Protocol:

1. Check author's ORCID page for a self-archived copy.
2. Check author's affiliation's institutional repository.
3. Email the corresponding author (polite one-line request — most authors share).
4. If still unobtainable, document the gap in the skill's CHANGELOG and skip the paper.

**Do not** cite a paper you haven't read based on its abstract alone — unless the file is explicitly labeled "abstract-only summary" and the abstract is quoted verbatim.
