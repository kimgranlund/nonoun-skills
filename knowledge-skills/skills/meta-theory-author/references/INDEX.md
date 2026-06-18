---
date: 2026-05-06
---

# meta-theory-author — Reference Index

_Manifest for the `references/` tree. Inherits from `meta-expert-author` for anything not covered here._

## Axes

1. **methodology/** — academic-specific sourcing, verification, axis model, currency tracking, access/quoting.
2. **structure/** — the one-paper-per-file template.
3. **examples/** — worked example of a theoretic-expert skill.

## File manifest

| Status | Path | Purpose |
|---|---|---|
| | **methodology/** | |
| ✅ | `methodology/academic-sourcing.md` | Source ranking: DOI > peer-reviewed indexed > preprint > working paper > dissertation > conference > excluded. Preprint platforms (arxiv, bioRxiv, SSRN, NBER). What's excluded by policy. |
| ✅ | `methodology/peer-review-verification.md` | Verifying peer-review status. Retraction Watch + Crossref retraction checks. Predatory journal red flags. Indexing in WoS, Scopus, MEDLINE, DOAJ. |
| ✅ | `methodology/theoretical-axes.md` | Axis models for theoretical domains. Frame/empirical/meta-analysis split. Schools/figures/works split. Methodologies/findings/debates split. When each fits. |
| ✅ | `methodology/currency-and-recency.md` | Preprint → published timeline. Version supersession. Handling "latest" claims. Refresh-time preprint→publication check. |
| ✅ | `methodology/access-and-quoting.md` | Paywalled papers. Open-access alternatives (arxiv preprints, author copies, OA journals). Fair-use quote budgets. License-aware handling. |
| ✅ | `methodology/paper-discovery.md` | Where to find papers. Five primary search surfaces (Semantic Scholar, Google Scholar, OpenAlex, Crossref, Unpaywall) + preprint servers + field indexes. Search strategies per use case. Snowball search. |
| ✅ | `methodology/web-search-patterns.md` | WebSearch + WebFetch tool patterns for academic retrieval. Query formulation, JSON API endpoints (Semantic Scholar, arxiv, Crossref, OpenAlex, Unpaywall), rate limits, worked end-to-end flow. |
| ✅ | `methodology/paper-reading-protocol.md` | Keshav's three-pass method. Claim extraction by type. Weakness detection checklist. Hedge discipline. Paper-type-specific reading strategies. Epistemic humility principle. |
| ✅ | `methodology/author-canon-patterns.md` | Multi-paper author corpora (Pearl, Chomsky, Friston) via figures/ axis. When to add, figure-file shape, phase-structuring long trajectories, anti-patterns. |
| ✅ | `methodology/field-specific-adaptations.md` | Per-field quality signals, weakness signals, refresh cadence, retraction vigilance. Covers biomedicine, psychology, economics, CS, ML, philosophy, pure math, HEP/astro, clinical trials, meta-analyses. |
| ✅ | `methodology/contradiction-and-disagreement.md` | Four kinds of disagreement (methodological / interpretive / paradigmatic / replication-failure). debates/ axis file shape. SKILL.md "Unresolved debates" section template. Hedge discipline. Claim-level contradictions vs paper-level debates. Meta-analysis as dispute-resolution. Disputes-staleness refresh. |
| ✅ | `methodology/verification-harness.md` | Design + integration guide for the automated verification harness. Nine local checks + four network checks. Wave-end integration. When to run. Dealing with false positives. Architectural notes. Future extensions. |
| | **agent-dispatch/** | |
| ✅ | `agent-dispatch/theoretic-agent-brief-template.md` | Canonical agent brief specific to theoretic waves. Required WebSearch/WebFetch flow, full frontmatter spec, verification requirements, field-specific adaptations, failure modes. Use verbatim. |
| | **structure/** | |
| ✅ | `structure/paper-summary-template.md` | The one-paper-per-file template. Frontmatter: DOI, authors, venue, year, preprint-version, peer-review-status, retraction-status. Body structure: abstract, contribution, methods, findings, limitations, citing-works. |
| | **examples/** | |
| ✅ | `examples/sample-theoretic-skill.md` | Worked example: structure of a hypothetical `causal-inference-expert` skill. Axes, sample papers, SKILL.md sketch. |

## Executable tools (outside references/)

| Status | Path | Purpose |
|---|---|---|
| ✅ | `tools/verify_skill.py` | Python 3.9+ script. Walks a skill's references/, validates frontmatter + DOI resolution + retraction status + URL liveness. Run post-wave and at every refresh. ~580 lines, stdlib + optional PyYAML. |
| ✅ | `tools/README.md` | Usage guide for the verifier. Check inventory, exit codes, CI integration examples, limitations. |

## Inherited from meta-expert-author

For these concerns, load files from `../meta-expert-author/references/` instead of duplicating:

- Wave arc (`methodology/wave-based-research.md`)
- Scoping survey (`methodology/scoping-survey.md`)
- Coverage tiers + frontmatter base (`methodology/coverage-tiers-and-frontmatter.md`)
- Canon-curation mode (`methodology/canon-curation-mode.md`) — theoretic-expert is a stricter subtype of this
- Verification discipline base (`methodology/verification-discipline.md`) — overridden for academic-specific checks
- Invocation flow (`methodology/invocation-flow.md`)
- Publishing trappings (`methodology/publishing-trappings.md`)
- Maintenance and evals (`methodology/maintenance-and-evals.md`)
- Stale-skill recovery (`methodology/stale-skill-recovery.md`)
- Cross-skill dependencies (`methodology/cross-skill-dependencies.md`)
- Skeleton files (`structure/skeleton-files.md`) — SKILL.md uses "greatest hits" variant
- Reference file template base (`structure/reference-file-template.md`) — overridden by `paper-summary-template.md`
- Agent brief template (`agent-dispatch/agent-brief-template.md`) — needs theoretic-expert-specific adaptation (see `academic-sourcing.md` § agent briefs)
- Wave planning (`agent-dispatch/wave-planning.md`)
- Bookkeeping protocol (`agent-dispatch/bookkeeping-protocol.md`)

## Conventions

- Each reference file starts with YAML frontmatter (inherited from meta-expert-author).
- Primary sources cited at file level (inherited).
- **Added**: DOI or stablest-identifier in every paper summary's frontmatter.
- **Added**: Retraction status checked at authoring + refresh.
- Dates use ISO format.
