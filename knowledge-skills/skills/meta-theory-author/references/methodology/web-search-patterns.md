---
date: 2026-04-18
coverage: deep
peers:
  - ../methodology/paper-discovery.md
  - ../methodology/paper-reading-protocol.md
  - ../methodology/academic-sourcing.md
primary_sources:
  - Claude Code WebSearch / WebFetch tool behavior (observed 2026-04)
  - Semantic Scholar API documentation (https://api.semanticscholar.org/api-docs/)
  - arxiv API documentation (https://info.arxiv.org/help/api/index.html)
  - Crossref REST API (https://api.crossref.org/swagger-ui/index.html)
---

# Web-search patterns for academic retrieval

Operational patterns for using WebSearch and WebFetch (Claude Code tools) to find and retrieve peer-reviewed papers. The meta-theory-author method requires these tools to work — this file documents how to use them effectively.

## Tools and what they give you

### WebSearch

- **Input**: a search query string.
- **Output**: a ranked list of URLs with titles and snippets.
- **Behavior**: hits a general-purpose search engine (typically Google-like).
- **Best for**: initial discovery, finding canonical papers by concept, finding the right DOI or landing page.
- **Limits**: no structured data; ranking is general-purpose, not academic-first.

### WebFetch

- **Input**: a specific URL + an extraction prompt.
- **Output**: extracted content from the page.
- **Behavior**: fetches the URL, converts HTML to markdown, runs the extraction prompt against it.
- **Best for**: reading a specific paper's landing page, extracting abstract/authors/DOI from a paper page, consuming the arxiv HTML version of a paper, hitting JSON API endpoints.
- **Limits**: single URL per call; paywalled content returns landing-page metadata only.

## The WebSearch → WebFetch flow

Standard pattern for finding and reading one paper:

1. **WebSearch**: `"<paper concept>" site:arxiv.org OR site:semanticscholar.org` — get candidate URLs.
2. **WebFetch** the top 2-3 landing pages — extract metadata (title, authors, DOI, abstract).
3. Decide which is the right paper.
4. **WebFetch** the selected paper's full HTML/PDF-alternative URL — extract the paper content.
5. Optionally **WebFetch** Semantic Scholar's API for citation graph context.

## WebSearch query patterns

### Pattern 1: Concept search with site filter

Find papers about a specific concept on preferred platforms:

```
"counterfactual reasoning" site:arxiv.org
"propensity score matching" site:semanticscholar.org
"scaling laws neural networks" site:openreview.net
```

Site filter dramatically improves signal-to-noise because you're pre-constraining to academic domains.

### Pattern 2: Author + concept

Find specific author's work on a topic:

```
"judea pearl" causal inference arxiv
"daphne koller" graphical models site:cs.stanford.edu
```

### Pattern 3: Exact title

When you know the title:

```
"Attention Is All You Need" vaswani
"Causal Inference: What If" hernan robins
```

Exact-quote the title. Add author name to disambiguate.

### Pattern 4: Recent + field + topic

For latest-work queries:

```
"large language model scaling" 2025 arxiv
"replication crisis psychology" 2024 meta-analysis
```

Year explicit in query helps recent ranking.

### Pattern 5: Cited-by walks

After finding a seminal paper:

```
"cited by: Attention Is All You Need" survey transformer architectures
```

Or use Semantic Scholar's "Cited By" tab directly (WebFetch `semanticscholar.org/paper/<id>/citations`).

### Pattern 6: Field-specific venue + year

When you know the venue:

```
"NeurIPS 2024" "in-context learning"
"Nature 2024" "transformer interpretability"
"JASA 2023" "causal inference"
```

Venue quotes help narrow to peer-reviewed proceedings.

### Pattern 7: Reviewing / synthesis signals

To find review papers and meta-analyses:

```
"systematic review" "<topic>" site:ncbi.nlm.nih.gov
"<field>" "review" OR "meta-analysis" 2023 OR 2024
"tutorial" OR "introduction" "<topic>" PDF
```

Review papers are gold for scoping-survey agents — they cite canonical works.

## WebFetch patterns for paper landing pages

### Pattern A: arxiv abstract page

```
WebFetch(
  url: "https://arxiv.org/abs/2401.12345",
  prompt: "Extract: title, authors, submission date, abstract, subject categories, DOI if any, list of sections in the paper, and any comments about replaced or updated versions."
)
```

### Pattern B: arxiv HTML full paper

```
WebFetch(
  url: "https://arxiv.org/html/2401.12345v3",
  prompt: "Extract: all section headings, the main theorems or claims, the experimental setup if any, and the conclusion. Note page or section numbers for key quotations."
)
```

arxiv's HTML version (introduced 2023-Oct) is much better for WebFetch than PDF.

### Pattern C: DOI landing page

```
WebFetch(
  url: "https://doi.org/10.1038/nature12373",
  prompt: "Extract: title, authors, journal, year, abstract, any retraction or correction notice visible, open-access status."
)
```

DOI resolution gives the publisher's landing page — usually has abstract and metadata even if full text is paywalled.

### Pattern D: Semantic Scholar paper page

```
WebFetch(
  url: "https://www.semanticscholar.org/paper/<paper-id>",
  prompt: "Extract: title, authors, venue, year, abstract, citation count, references (first 10 listed), citing works (first 10 listed), open-access PDF URL if present."
)
```

### Pattern E: PubMed entry

```
WebFetch(
  url: "https://pubmed.ncbi.nlm.nih.gov/<pmid>/",
  prompt: "Extract: title, authors, journal, year, abstract, DOI, publication type (e.g., randomized controlled trial, meta-analysis), any retraction status."
)
```

### Pattern F: Crossref API for DOI metadata

```
WebFetch(
  url: "https://api.crossref.org/works/10.1038/nature12373",
  prompt: "Return the JSON as parsed fields: DOI, title, authors, published-print date, journal, publisher, type (journal-article / book-chapter / etc.), is-referenced-by-count, references array length, any retraction metadata."
)
```

### Pattern G: Unpaywall OA resolver

```
WebFetch(
  url: "https://api.unpaywall.org/v2/10.1038/nature12373?email=research-survey@example.com",
  prompt: "Return: is_oa (boolean), best_oa_location (URL if OA copy available), oa_status (green/gold/bronze/closed), any license info."
)
```

Replace email with a real contact per Unpaywall's policy.

## JSON API endpoints (structured retrieval)

These return JSON — WebFetch against them gets structured results without HTML parsing:

### Semantic Scholar

```
# Paper search
https://api.semanticscholar.org/graph/v1/paper/search?query=<query>&limit=20&fields=title,authors,year,venue,abstract,citationCount,openAccessPdf,externalIds

# Specific paper (by S2 ID or DOI)
https://api.semanticscholar.org/graph/v1/paper/DOI:10.1038/nature12373?fields=title,authors,year,venue,abstract,references,citations,openAccessPdf

# Paper citations
https://api.semanticscholar.org/graph/v1/paper/DOI:10.1038/nature12373/citations?limit=50&fields=title,year,venue

# Paper references
https://api.semanticscholar.org/graph/v1/paper/DOI:10.1038/nature12373/references?limit=50&fields=title,year,venue
```

### arxiv Atom API

```
http://export.arxiv.org/api/query?search_query=ti:%22attention+is+all+you+need%22&start=0&max_results=5
```

Returns Atom XML. WebFetch with a prompt like "Extract each entry's title, authors, summary (abstract), arxiv id, published date."

### Crossref

```
# Search
https://api.crossref.org/works?query=<query>&rows=20

# DOI lookup
https://api.crossref.org/works/10.1038/nature12373

# Filter by type + date
https://api.crossref.org/works?query=<query>&filter=type:journal-article,from-pub-date:2024-01-01&rows=20
```

### OpenAlex

```
# Search
https://api.openalex.org/works?search=<query>&per-page=25

# Filter by concept + year
https://api.openalex.org/works?search=<query>&filter=concept.id:C41008148,publication_year:2024

# Specific work
https://api.openalex.org/works/doi:10.1038/nature12373
```

### Retraction Watch (via Crossref)

Retractions register in Crossref. To check a specific paper:

```
https://api.crossref.org/works/10.1038/nature12373
```

Look for `update-to` array — presence indicates a correction or retraction referring to this DOI.

For proactive retraction search (all retractions in a field):

```
https://api.crossref.org/works?filter=update-type:retraction,from-update-date:2024-01-01&rows=50
```

## Query refinement when results are bad

### Too many results, mostly irrelevant

- Add field-specific terms.
- Add year constraint.
- Add `site:arxiv.org` or `site:semanticscholar.org`.
- Switch to Semantic Scholar API with structured field filters.

### Too few results / all tangential

- Broaden the query: drop the most specific term.
- Try synonymous phrasings.
- Search for review papers; then follow their bibliographies.
- Try the topic in the author's own words (find a known author's paper and search their terminology).

### Search surface returning irrelevant or gamed results

- Switch surface. If Google Scholar is full of SEO noise, try Semantic Scholar or OpenAlex.
- Use Crossref for pure metadata (no content ranking).
- For very recent preprints, go directly to arxiv's listing.

## Rate limits and ethics

| Surface | Rate limit (free tier) | Notes |
|---|---|---|
| Semantic Scholar API | ~1 req/sec, higher with API key | Request API key for heavy use |
| arxiv API | "be respectful"; ~1 query every 3 seconds | No hard cap but abusers get blocked |
| Crossref API | 50 req/sec polite, "mailto:" header required for priority | Include contact in requests |
| OpenAlex API | 10 req/sec; email header for faster | |
| Unpaywall | 100K req/day with email | Requires email in URL |
| Google Scholar | aggressive CAPTCHAs on automated requests | Use browser / infrequent WebFetch |

For wave-level work (one wave = tens of searches, possibly hundreds of WebFetches), stay within polite rate limits. An agent running too fast gets temporarily blocked.

## WebFetch-specific tips

- **Prompt specificity matters**: a generic prompt like "summarize this paper" returns a generic summary. Specific prompts like "extract the exact statement of Theorem 3.2 including assumptions" get specific extractions.
- **JSON APIs are cheaper than HTML**: the Semantic Scholar API returns structured JSON that WebFetch can pass through; the web UI has more noise.
- **PDF vs HTML**: prefer HTML (arxiv HTML, journal web pages). PDFs are extractable but slower and lose structure.
- **Landing pages vs full-text**: most verification (DOI, authors, year, abstract) needs the landing page, not full text.
- **Batch similar queries**: if authoring 5 files about Pearl papers, cache author metadata once, don't re-fetch per paper.

## When WebSearch and WebFetch aren't enough

- **Paywalled full-text**: use Unpaywall for OA alternatives; ILL / direct request if no OA exists.
- **Books**: WebFetch the publisher's page for metadata; for content, use the author's sample chapters or ILL.
- **Non-indexed preprints**: some fields (pure math, old CS papers) live on author websites. Google-level WebSearch finds them; WebFetch the PDF.
- **Very recent papers (hours/days old)**: may not be indexed anywhere yet. Check arxiv new listings directly.

## Agent-brief requirement

Every meta-theory-author wave agent brief includes (abbreviated):

> **Required tooling**: WebSearch and WebFetch. You MUST use them. Don't summarize papers from prior knowledge alone — every paper's claims, abstract, and methods must be verified by fetching the paper or its landing page.
> 
> **Search patterns**: see `../methodology/web-search-patterns.md` for canonical query patterns, API endpoints, and fallback strategies.
> 
> **Per paper, minimum tooling**:
> - WebSearch to find the landing page (DOI, arxiv URL, Semantic Scholar URL).
> - WebFetch the landing page for metadata + abstract.
> - WebFetch the full text (arxiv HTML preferred) to verify claims.
> - WebFetch Crossref / Retraction Watch for retraction status.
> 
> If any step fails (paywalled full text, etc.), report the gap in your findings; do not invent content.

## Common failure modes

- **Hallucinating content from abstract alone** — abstract is a summary; actual paper often contains critical caveats not in the abstract. Don't summarize the paper from the abstract unless explicitly labeled.
- **Fetching a review and citing it as primary** — reviews summarize primary work; cite the primary work.
- **Fetching the landing page but not the paper** — abstract + methods section is what you need, not just metadata.
- **Conflating preprint and published versions** — different DOIs, different texts, different peer-review status. Always check which version you have.
- **Trusting citation counts without reading** — highly cited can mean "widely debunked" too.

## Worked flow: find and summarize "Vaswani et al. 2017 Attention Is All You Need"

1. **WebSearch**: `"Attention Is All You Need" Vaswani 2017` → top result arxiv.
2. **WebFetch** `https://arxiv.org/abs/1706.03762` → extract title, authors, date, DOI (if any), abstract.
3. Note: paper was accepted at NeurIPS 2017 as well. **WebFetch** `https://papers.nips.cc/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html` for the conference-proceedings version.
4. **WebFetch** `https://arxiv.org/html/1706.03762v7` → extract architecture description, training setup, results tables.
5. **WebFetch** Semantic Scholar API: `https://api.semanticscholar.org/graph/v1/paper/arXiv:1706.03762?fields=citationCount,influentialCitationCount,references` → get citation-graph context.
6. **WebFetch** Crossref (if DOI registered): check retraction/correction status.
7. Write the paper-summary file using `structure/paper-summary-template.md`.

Total: ~5 WebFetch calls + 1 WebSearch. 3-5 minutes wallclock. Produces a verified, cited summary.
