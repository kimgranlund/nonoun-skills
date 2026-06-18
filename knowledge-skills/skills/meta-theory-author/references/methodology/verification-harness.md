---
date: 2026-04-18
coverage: expanded
peers:
  - ../../tools/verify_skill.py
  - ../../tools/README.md
  - ../methodology/peer-review-verification.md
  - ../methodology/currency-and-recency.md
primary_sources:
  - https://api.crossref.org/swagger-ui/index.html
  - https://info.arxiv.org/help/api/index.html
  - https://unpaywall.org/products/api
---

# Verification harness

Automated verification for theoretic-expert-author-produced skills. Where `peer-review-verification.md` documents what humans check, this file documents what the machine checks — and how the two overlap.

## What the harness is

**`tools/verify_skill.py`** — a Python 3.9+ script that validates a theoretic-expert skill against the invariants documented in this meta-skill. Run it post-wave, pre-v1.0 signoff, and at every 6-month refresh.

The harness is NOT a replacement for human verification. It's a floor — it catches mechanical errors (missing fields, broken DOIs, dead URLs, stale retraction-checks) so humans can spend their attention on content quality (hedge discipline, claim accuracy, axis coherence).

## What it verifies

### Local checks (no network)

1. **Frontmatter presence**: every reference file has YAML frontmatter.
2. **Required fields per axis**: works/ files need doi + authors + year + venue + peer_review_status + retraction_status + retraction_checked + paper_type + coverage. Other axes have lighter requirements.
3. **Valid field values**: `peer_review_status`, `retraction_status`, `paper_type`, `coverage` are in canonical sets.
4. **DOI-or-fallback rule**: every works/ file has a DOI, or a labeled fallback identifier (arxiv_id / ssrn_id / nber_wp).
5. **Date format**: all date fields are ISO (YYYY-MM-DD).
6. **Staleness**: `retraction_checked` is ≤ 365 days old.
7. **Peer path resolution**: relative `peers:` paths resolve to existing files.
8. **Quote budget**: no single blockquote exceeds 100 words continuous (fair-use guardrail).
9. **Retraction banner**: files with `retraction_status: retracted` have a visible RETRACTED banner in the first 500 chars.

### Network checks (with `--network`)

10. **DOI resolves**: Crossref API confirms the DOI is registered.
11. **Retraction alignment**: Crossref `update-to` field cross-checked against declared `retraction_status`. Mismatch = flag.
12. **arxiv ID validity**: arxiv export API confirms the paper exists.
13. **URL liveness**: first 5 `primary_sources` URLs per file return HTTP 200-399.

### What the harness does NOT verify

- **Peer-review status** — no programmatic way to confirm a venue is in WoS/Scopus. Trust the author's declared field.
- **Paper-type classification** — requires reading the paper. Human judgment.
- **Hedge discipline** — faithfulness of summary to paper. Human judgment.
- **Axis coherence** — whether a file belongs in methodologies/ or findings/. Human judgment.
- **Cross-reference meaningfulness** — whether a `peers:` link is substantively relevant. Human judgment.

The harness catches **form**; humans catch **substance**.

## When to run it

| Moment | Flags | Why |
|---|---|---|
| **After each wave** | local only | Catch frontmatter drift before it accumulates |
| **Before v1.0.0 signoff** | `--network` | Ensure every DOI resolves + no stale retractions + URLs live |
| **At 6-month refresh** | `--network` | Catch URL rot + new retractions + stale retraction_checked dates |
| **In CI on PRs** | local only | Network checks too slow; gate on content discipline |
| **Weekly cron (optional)** | `--network --json` | Background URL-rot surveillance |

## Integration into the wave bookkeeping protocol

Update `meta-expert-author/references/agent-dispatch/bookkeeping-protocol.md` for meta-theory-author skills: after Step 5 (CHANGELOG entry), add:

> **Step 6 (theoretic-expert skills only)**: run `tools/verify_skill.py <skill-path>` locally. If any non-network errors: fix before proposing next wave. Network checks can be deferred to next natural refresh.

At v1.0.0 signoff: always run with `--network`. If any errors: fix before flipping status to `complete`.

## Sample wave-end integration

```bash
# After Wave 3 of a theoretic-expert skill
cd ~/.claude/skills/meta-theory-author/tools

# Quick check
python3 verify_skill.py ~/.claude/skills/causal-inference-expert
# Exit 0: proceed
# Exit 1: fix content errors before next wave

# At v1.0.0 signoff
python3 verify_skill.py ~/.claude/skills/causal-inference-expert --network --verbose
# Exit 0: ship it
# Exit 1: content errors — fix
# Exit 2: network errors (DOI / URL) — fix DOIs, replace dead URLs with archive.org
```

## Dealing with false positives

### Network flakiness

A DOI "not resolving" might be a transient Crossref blip. If the same DOI resolves in a browser, retry the script.

Temporary workaround: run without `--network` to confirm content is clean; re-run with `--network` later.

### Valid fallback identifiers flagged

If a paper has no DOI but does have an arxiv_id, the script accepts it. If the script flags "no DOI and no fallback identifier," the frontmatter's fallback field is missing or mistyped.

### Fair-use quotations legitimately over 100 words

Rare but possible for heavily discussed quotes or normative standards text (WCAG SCs quoted verbatim, legal text). If legitimately necessary, quote in multiple blockquotes separated by commentary (each under 100 words).

The script doesn't currently accept a per-file override. Add an explicit `quote_budget_override: true` to frontmatter as a v1.5 extension.

### arxiv rate limiting

arxiv enforces 3-second spacing between queries. A skill with 100 arxiv IDs takes ~5 minutes just for arxiv. Budget accordingly — run during a coffee break.

## Architectural notes

### Why Crossref + arxiv APIs, not commercial ones

Free, no key required, polite rate limits. Semantic Scholar has a richer API but occasionally requires API keys for heavy use. Crossref + arxiv cover 95% of what the harness needs.

For deeper verification (citation counts, influence scores, open-access status), add Semantic Scholar or OpenAlex queries. See `web-search-patterns.md` for their endpoints.

### Why Python

Stdlib suffices (urllib, json, re, pathlib). One optional dep (PyYAML). Runs on any developer's machine without environment setup.

A Node.js or Deno version is feasible; Python is chosen for accessibility.

### Why check only first 5 URLs per file

Primary_sources arrays can be long; checking 30 URLs per file × 50 files = 1500 URL fetches per refresh. Too slow. The first 5 are almost always the load-bearing ones (DOIs, arxiv, main references); others tend to be supporting material.

To check all: modify the slice in the script. Or run a separate URL-audit pass monthly.

## What the harness enables

### 1. Consistent shipping discipline

Every skill shipped with a verify-clean record. No more "I forgot to set retraction_checked" errors shipping to production.

### 2. Automated staleness detection

The staleness check means a skill's `retraction_checked` fields can't silently age past a year. The script surfaces stale files before they become wrong files.

### 3. CI integration

`--json` output + non-zero exit codes make the harness drop-in for GitHub Actions, GitLab CI, etc. Example:

```yaml
# .github/workflows/verify.yml
name: Verify skill
on: [pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install pyyaml
      - run: python3 ../meta-theory-author/tools/verify_skill.py . --network --json
```

### 4. Refresh-wave prioritization

Run with `--network --json`, pipe to `jq`, get a prioritized list of files needing attention (dead URLs / retracted DOIs / stale checks). Feed that list into the next refresh wave's agent brief.

## Limitations and future work

### Current v1.0 of the harness

- Single-threaded network requests. Could parallelize.
- No caching of API responses. Repeated runs re-fetch.
- No `--fix` mode. Errors must be fixed by hand.
- No handling of non-Crossref DOIs (e.g., DataCite registry for datasets).
- No cross-skill verification (if skill A cites skill B's files, broken links in B aren't detected by running A's verifier).

### Candidate v1.1 additions

- **Caching** — store Crossref responses in `~/.cache/theoretic-verifier/` keyed by DOI. Skip re-fetch within 24h.
- **Parallel network checks** — use `concurrent.futures` to parallelize DOI / arxiv / URL fetches within politeness limits.
- **`--fix` mode** — for mechanical fixes (date format correction, missing `doi_status` flag), offer automated correction.
- **DataCite DOI support** — for dataset-backed papers.
- **Preprint → published supersession detection** — query Semantic Scholar for published version of each arxiv preprint.
- **Cross-skill dependency graph** — walk `peer[]` from skill.json, verify linked skills also pass their verification.

## What this v1.4 closes

v1.3 noted: "Automated verification harness — requires implementation, not just spec."

v1.4 delivers the implementation. The script is ~550 lines of Python, stdlib + optional PyYAML only, free APIs only. Ships as part of this meta-skill (`tools/verify_skill.py`). Documented in `tools/README.md`.

The skill is now genuinely end-to-end: doctrine says what to do; the harness mechanically checks that it was done.

## What's still execution-gated

- **Live validation runs** (causal-inference-expert, ML-theory-expert, philosophy-of-mind-expert) still require dispatching waves. The harness validates the *output* of such runs; it doesn't dispatch them.
- **Content quality audits** still need human review. Hedge discipline, axis coherence, claim faithfulness are judgment calls. The harness clears the mechanical-error floor; humans clear the judgment floor.

The meta-skill is as complete as pure doctrine + automatable mechanics allow. Beyond this is either live field-testing or content-judgment work.
