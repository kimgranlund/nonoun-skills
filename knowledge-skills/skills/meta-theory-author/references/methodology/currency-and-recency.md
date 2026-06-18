---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/academic-sourcing.md
  - ../methodology/peer-review-verification.md
  - ../../meta-expert-author/references/methodology/maintenance-and-evals.md
primary_sources:
  - arxiv version-tracking conventions
  - Crossref version-of-record metadata
---

# Currency and recency

"Latest in peer-reviewed science" is a moving target. Preprints turn into published papers. Papers get corrected. New preprints supersede old ones. This file documents how meta-theory-author skills track that lifecycle.

## The preprint → publication lifecycle

A paper typically goes through these states:

| State | Identifier | Citation shape |
|---|---|---|
| Preprint v1 | arxiv:2024.01234v1 | Cite as preprint |
| Preprint v2, v3, … | arxiv:2024.01234v2 | Cite the specific version |
| Under peer review | (not public) | — |
| Accepted, in press | DOI registered but unpublished | Cite with "in press" |
| Published (version of record) | Full DOI | Cite the VoR |
| Corrected | DOI + correction DOI | Note correction |
| Retracted | DOI + retraction DOI | Flag in file |

The meta-skill tracks this: a file citing a preprint should check at refresh whether a published version now exists.

## Citing by state

### Preprint only (no published version yet)

```yaml
---
doi: not-issued
arxiv_id: 2401.12345v2
peer_review_status: preprint-not-peer-reviewed
preprint_version: v2
preprint_posted: 2024-11-15
venue: arxiv
retraction_status: clean
retraction_checked: 2026-04-18
superseded_by: null
---
```

Citation in-file:

> [Authors] (2024). *[Title]*. arxiv preprint v2 (posted 2024-11-15). https://arxiv.org/abs/2401.12345v2

### Preprint + published version

When a preprint has been published, the file can either (a) cite both with cross-reference or (b) migrate to cite only the published version. Recommended: (a).

```yaml
---
doi: 10.1038/s41586-025-12345-6
arxiv_id: 2401.12345v3
peer_review_status: peer-reviewed-published
venue: Nature
venue_indexed: [WoS, Scopus]
publication_date: 2025-06-10
preprint_version: v3
preprint_posted: 2024-11-15
retraction_status: clean
retraction_checked: 2026-04-18
---
```

In-file, explain if the preprint version differs materially:

> This paper was posted as arxiv preprint 2401.12345v3 on 2024-11-15 and subsequently published in Nature on 2025-06-10. The published version differs from the preprint in [sections affected], primarily due to reviewer-requested [changes].

### In-press

After acceptance but before publication:

```yaml
---
doi: 10.1038/s41586-025-12345-6  # DOI is registered but landing page may not be live
peer_review_status: in-press
venue: Nature
publication_date: null
acceptance_date: 2025-05-01
---
```

In-press is a short-lived state. Refresh after ~3 months to check if the DOI now resolves to a published version.

### Superseded

When a later paper by the same authors (or the community) explicitly supersedes an earlier paper:

```yaml
---
doi: 10.xxxx/older-paper
peer_review_status: peer-reviewed-published
superseded_by: 10.yyyy/newer-paper  # DOI of the superseding work
supersession_note: "The authors' [Year] follow-up refines the main theorem; cite the follow-up for current work."
---
```

Don't delete superseded papers — they're historically important. But flag them clearly.

## The refresh protocol (theoretic-expert additions)

Add to meta-expert-author's 6-month refresh protocol:

### Preprint → publication check

For every file with `peer_review_status: preprint-not-peer-reviewed` or `in-press`:

1. Search the authors + title in Google Scholar / Semantic Scholar / Crossref.
2. If a DOI-registered published version now exists:
   - Update frontmatter: `peer_review_status: peer-reviewed-published`.
   - Add `doi:`, `venue:`, `publication_date:`.
   - Compare published version to cited preprint version. Note material changes in-file.
3. If still only a preprint: update `retraction_checked:` date.

### Supersession check

For every file:

1. Check if newer work by the same authors (same topic) has been posted.
2. Check if the field has a new canonical paper on the same topic.
3. If found: add `superseded_by:` and note in-file.

### Version-of-record migration

If a paper went from preprint to published and the published version is materially different:

- Option 1: update the file to cite the published version, note the preprint history.
- Option 2: keep the original file as the preprint-era summary and author a new file for the published version with cross-reference.

Default to Option 1 unless the preprint version is historically important in its own right.

## Handling "latest" in SKILL.md

Claims like "latest theory of X" or "as of [date]" go stale fast in active fields. Conventions:

- **Date every such claim** with ISO date: "As of 2026-04, the leading account of X is [paper]."
- **Use relative phrasing when possible**: "recent work", "current consensus" rather than "the latest."
- **Re-date at each refresh**: update "As of 2026-04" to "As of 2026-10" (or whatever refresh date).

A skill whose SKILL.md has five-year-old "latest" claims is actively misleading. The refresh cadence has to catch these.

## Fast-moving vs slow-moving fields

Fields differ in how fast the state of the art changes. Adjust refresh cadence:

| Field pace | Example | Recommended refresh | What changes fastest |
|---|---|---|---|
| **Fast** | Deep learning, LLM scaling | 3-month | Preprint landscape; new scaling laws; new architectures |
| **Medium-fast** | Computational neuroscience, causal inference | 6-month | Empirical tests; meta-analyses |
| **Medium** | Most empirical science | 6-12 month | Canonical papers stable; meta-analyses shift |
| **Slow** | Pure mathematics, philosophy | 12-24 month | Canon stable; occasional new proofs or arguments |

For fast-moving fields, the meta-skill's default 6-month cadence may be too slow. Adjust in MAINTENANCE.md.

## The preprint-paper risk

Citing only preprints risks:

- **Peer review fails**: the preprint's claims are wrong in ways reviewers would catch.
- **Preprint withdrawn**: authors retract without a retraction notice in major retraction databases.
- **Superseded silently**: authors post v2 that changes conclusions.

Mitigations:

- Prefer published versions when available.
- For preprint-only citations, mark prominently and refresh frequently.
- Don't build load-bearing claims in SKILL.md on preprint-only sources — wait for peer review if the claim is core.

## The "bleeding edge" balance

A theoretic skill for an active field has to balance:

- **Currency**: covering the latest preprints shows the frontier.
- **Durability**: citing only peer-reviewed papers ensures long-term correctness.

Recommended mix:

- **SKILL.md "greatest hits"**: primarily peer-reviewed canon. Include at most 1-2 preprint citations, clearly labeled.
- **References/**: ~70% peer-reviewed, ~30% preprint / working-paper for fast-moving fields; closer to 90/10 for stable fields.

## Handling "this isn't published yet but everyone cites it"

Some preprints achieve canonical status before peer review (e.g., the original Transformer paper Vaswani et al. was a NeurIPS 2017 paper; others like RLHF papers have been canonical as preprints for years). Cite them normally with `peer_review_status: preprint-not-peer-reviewed` or the appropriate conference-proceedings status, and treat the community's canonization as a soft citation.

Don't let "everyone cites it" override the verification discipline. If a preprint gets retracted despite being canonical, the retraction is still the most important fact.
