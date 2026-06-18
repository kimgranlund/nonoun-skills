---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/academic-sourcing.md
  - ../methodology/currency-and-recency.md
  - ../structure/paper-summary-template.md
primary_sources:
  - https://retractionwatch.com/
  - https://www.crossref.org/services/crossmark/
  - https://doaj.org/
  - https://mjl.clarivate.com/home (Web of Science Master Journal List)
  - https://www.scopus.com/
---

# Peer-review verification

How to verify that a source is actually peer-reviewed, not retracted, and not from a predatory venue. Adds to meta-expert-author's verification discipline.

## The three checks

Every paper cited at tier 1-3 needs all three:

1. **Peer-review status**: is the venue actually peer-reviewed, and was this paper reviewed?
2. **Retraction status**: has this paper been retracted, corrected, or expressed-concern-of?
3. **Indexing status**: is it in a reputable index (WoS, Scopus, MEDLINE, DOAJ)?

Tier 4-5 (preprints, working papers) skip check 1 but still need 2 and 3 (preprint "retraction" = withdrawn).

## Check 1: peer-review status

### Default assumption

A paper published in a journal listed on the **Web of Science Master Journal List** OR **Scopus** OR **DOAJ** is peer-reviewed.

- Web of Science: mjl.clarivate.com/home (search by journal name).
- Scopus: scopus.com (requires free search account).
- DOAJ: doaj.org (open-access journals; curated list).

### Predatory-journal red flags

Some journals look legitimate but don't actually peer-review. Red flags:

- **Not in WoS, Scopus, or DOAJ.**
- **Publisher on Beall's list** (archived; successor maintained at beallslist.net).
- **Journal accepts manuscripts in <2 weeks.** Real peer review takes 1-6 months.
- **Article-processing charges (APCs) advertised prominently on submission page.** Legitimate OA journals charge APCs too, but predatory ones emphasize them.
- **Editor identities are suspicious.** Scholars with no real affiliation, or known scholars who deny being on the editorial board.
- **Venue overlaps with known predatory publishers**: OMICS, MedCrave, Bentham (some titles), Hilaris, Longdom.

If any of these flags, **do not cite the paper.** Or cite only if you can confirm it's also available as a preprint, and cite the preprint instead.

### Preprint → not peer-reviewed

A paper on arxiv, bioRxiv, SSRN, etc., is explicitly **not** peer-reviewed. This is fine — tier 4-5 sources are acceptable — but the frontmatter must reflect it:

```yaml
peer_review_status: "preprint-not-peer-reviewed"
preprint_version: "v2"
preprint_posted: "2024-11-15"
```

When citing a preprint, also check if it has since been published. See `currency-and-recency.md`.

## Check 2: retraction status

### Retraction Watch + Crossref

- **Retraction Watch**: retractionwatch.com/retraction-watch-database-user-guide/ (searchable database of retractions).
- **Crossref CrossMark**: embedded in most DOI resolutions; shows "correction", "retraction", "expression of concern" status.

Process:
1. Resolve the DOI via doi.org.
2. The landing page (from the publisher) should display retraction status via CrossMark widget if any.
3. Additionally search Retraction Watch by title and DOI.

### Retraction severities

| Status | Meaning | How to handle |
|---|---|---|
| **Retracted** | Paper withdrawn by publisher, typically for fabrication, fraud, or major error | Prominent ⚠️ RETRACTED banner in file. Note the retraction reason. Consider whether to keep the file at all. |
| **Correction issued** | Errata published; primary claims stand | Note the correction URL. Content usually still citable. |
| **Expression of concern** | Unresolved concern; investigation in progress | Label in file: "(expression of concern issued YYYY-MM)". Watch for resolution. |
| **Withdrawn** (preprint) | Authors withdrew preprint | If v1 existed and was influential, cite with caveat; prefer newer supersession. |

### The retraction-check protocol

At wave 1 authoring:
- For every paper added, run the Retraction Watch search.
- Flag any match in the file's frontmatter: `retraction_status: "retracted" | "corrected" | "concern" | "clean"`.

At every refresh:
- Re-run retraction checks on every paper in the skill. Retractions can happen years after publication.

### Known retraction-flagged domains

Some areas have higher retraction rates and deserve extra scrutiny:

- **Biomedicine** — particularly cancer biology, cell biology, clinical trials.
- **Psychology** — replication crisis has produced many retractions 2011+.
- **Computer science ML/AI** — ghost benchmarks, leaked test data; fewer formal retractions but many post-publication corrections.

Skill authors in these domains should budget 5-10% extra verification time.

## Check 3: indexing

### Why indexing matters

Indexed journals get:
- Citation-graph inclusion.
- Retraction tracking.
- Impact factor / SJR score (for venue ranking).
- Long-term URL stability.

Unindexed journals may be legitimate (especially new OA titles) but lack the durability guarantees.

### Indexes to check

- **Web of Science (Clarivate)** — Science Citation Index Expanded (SCIE), Social Sciences Citation Index (SSCI), Arts & Humanities Citation Index (AHCI).
- **Scopus (Elsevier)** — broader than WoS.
- **MEDLINE** — biomedical.
- **DOAJ (Directory of Open Access Journals)** — curated OA.
- **ERIC** — education.
- **MathSciNet / zbMATH** — mathematics.
- **INSPIRE-HEP** — high-energy physics.
- **Philpapers** — philosophy.
- **PsycINFO** — psychology.

Check 1-2 relevant indexes for each paper's venue.

## Frontmatter fields

Add to every paper-summary file:

```yaml
---
doi: 10.1038/nature12373
peer_review_status: peer-reviewed-published
venue: Nature
venue_indexed: [WoS, Scopus, MEDLINE]
retraction_status: clean  # clean | corrected | concern | retracted
retraction_checked: 2026-04-18
# If preprint:
# preprint_version: v3
# preprint_posted: 2024-11-15
# also_published_as: 10.1038/s41586-025-XXXXX-X
---
```

These fields are mandatory. Agent briefs must include them as required output.

## Agent-brief verification addition

Add to every meta-theory-author wave brief:

> **VERIFICATION DISCIPLINE (meta-theory-author additions):**
> For every paper you cite, verify and include in frontmatter:
> 1. `doi:` — resolve via doi.org, confirm it resolves to the paper.
> 2. `peer_review_status:` — confirm via venue's WoS/Scopus/DOAJ listing.
> 3. `retraction_status:` — check Retraction Watch by title + DOI.
> 4. `retraction_checked:` — today's ISO date.
> If any check fails, flag in your findings report. Do not silently include a paper you couldn't verify.

## Known corrections log (for this skill)

When an agent catches a fabrication or a missed retraction during a meta-theory-author run, log it here (or in the produced skill's `verification-discipline.md` extension).

_(No entries yet — this skill is v1.0.0.)_

## Citing retracted papers anyway

Sometimes a retracted paper is load-bearing in a field's history (e.g., the Macchiarini / Wakefield cases). Citing them:

1. Create the file with the normal paper template.
2. Prominent ⚠️ RETRACTED banner below the title.
3. Add a dedicated section: "Why this paper is cited despite retraction." Explain historical significance.
4. Link to the retraction notice DOI and Retraction Watch entry.
5. Update the CHANGELOG when the retraction becomes load-bearing to the skill.

Don't cite retracted papers invisibly. The retraction is the most important fact about them.

## When peer-review status is ambiguous

Some venues straddle the boundary (new journals, conferences with inconsistent review practices, invited contributions that skip review). Handle by:

- Labeling in frontmatter: `peer_review_status: "ambiguous"` with a note.
- Citing in-file: "This paper appeared in [venue]; the review process for invited contributions in this venue is unclear."
- Preferring a preprint or later peer-reviewed version if one exists.

Don't default to "peer-reviewed" when you're not sure. Ambiguous is honest.
