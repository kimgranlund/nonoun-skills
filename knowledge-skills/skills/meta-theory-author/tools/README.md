# tools/

Executable utilities for theoretic-expert-author-produced skills.

## verify_skill.py

Automated verification for a meta-theory-author skill. Validates the invariants documented in this meta-skill against an actual produced skill directory.

### Quick start

```bash
# Local checks only (fast, no network)
python3 verify_skill.py ~/.claude/skills/causal-inference-expert

# Full verification including DOI resolution + retraction checks + URL liveness
python3 verify_skill.py ~/.claude/skills/causal-inference-expert --network

# Verbose progress (prints DOI/arxiv checks to stderr)
python3 verify_skill.py ~/.claude/skills/causal-inference-expert --network --verbose

# JSON output (for CI / programmatic consumption)
python3 verify_skill.py ~/.claude/skills/causal-inference-expert --network --json
```

### Checks performed

#### Local (always run)

| Check | What it verifies |
|---|---|
| Frontmatter present | Every .md file in `references/` (except INDEX.md) has YAML frontmatter |
| Required fields | Per-axis required fields (works/ needs doi, authors, year, etc.) |
| Field values valid | `peer_review_status`, `retraction_status`, `paper_type`, `coverage` are in canonical sets |
| DOI or fallback | Every works/ file has a DOI, or a fallback identifier + doi_status flag |
| Date format | All date fields are ISO (YYYY-MM-DD) |
| Staleness | `retraction_checked` is ≤ 365 days old |
| Peer paths | Relative paths in `peers:` frontmatter resolve to existing files |
| Quote budget | No blockquote exceeds 100 words continuous |
| Retraction banner | `retraction_status: retracted` papers have a RETRACTED banner in body |

#### Network (requires `--network` flag)

| Check | What it verifies |
|---|---|
| DOI resolves | Crossref API confirms the DOI is registered |
| DOI retraction status | Crossref `update-to` field checked against declared `retraction_status` |
| arxiv ID exists | arxiv export API confirms the paper exists |
| URL liveness | First 5 primary_sources URLs per file return HTTP 200-399 |

### Dependencies

- **Required**: Python 3.9+
- **Optional**: PyYAML (`pip install pyyaml`) for robust frontmatter parsing. Falls back to naive regex parser if absent.

No other dependencies. Uses `urllib` from stdlib for HTTP.

### Network API usage

Free, no API key required:

- **Crossref REST API** — https://api.crossref.org/works/<doi>
- **arxiv Atom API** — http://export.arxiv.org/api/query?id_list=<id>
- URL liveness via HEAD / GET

Polite rate limits:
- Crossref: ~10 req/sec (we spacing-limit at 10/sec)
- arxiv: requested 3 seconds between queries (we enforce)
- General URLs: 0.1s spacing

Include `mailto:` in User-Agent for Crossref priority (edit USER_AGENT in script).

### Exit codes

| Code | Meaning |
|---|---|
| 0 | All checks passed |
| 1 | Non-network checks failed (frontmatter, validation) |
| 2 | Network checks failed (DOI, URLs, retractions) |
| 3 | Skill path not found or missing skill.json |

Use in CI:

```bash
# Fail CI on any error
python3 verify_skill.py ~/.claude/skills/my-skill --network
if [ $? -ne 0 ]; then exit 1; fi

# Only fail on content errors; tolerate network flakiness
python3 verify_skill.py ~/.claude/skills/my-skill
if [ $? -ne 0 ]; then exit 1; fi
```

### Example output (text mode)

```
=== Skill verification report ===
Skill: ~/.claude/skills/causal-inference-expert
Started: 2026-04-18T14:30:00+00:00

Files checked: 47
Files with errors: 3
Network checks: enabled

Summary:
  required_field_missing: 2
  stale_retraction_check: 1
  url_dead: 3

Errors by file:
  references/methodologies/pearl-1995-causal-diagrams.md:
    - missing required field: retraction_checked
  references/findings/lalonde-1986.md:
    - retraction_checked is 412 days old (threshold 365)
    - URL error (HTTPError): https://example.com/lalonde-original.html
  references/debates/imbens-2020.md:
    - missing required field: paper_type

❌ 3 file(s) have errors.
```

### Example output (JSON mode)

```json
{
  "skill_path": "~/.claude/skills/causal-inference-expert",
  "started_at": "2026-04-18T14:30:00+00:00",
  "files_checked": 47,
  "files_with_errors": 3,
  "network_checks_enabled": true,
  "summary": {
    "required_field_missing": 2,
    "stale_retraction_check": 1,
    "url_dead": 3,
    ...
  },
  "errors_by_file": {
    "references/methodologies/pearl-1995-causal-diagrams.md": [
      "missing required field: retraction_checked"
    ],
    ...
  },
  "finished_at": "2026-04-18T14:31:42+00:00"
}
```

### When to run

| Moment | Checks | Notes |
|---|---|---|
| After each wave | Local only | Fast; catches obvious mistakes before they pile up |
| Before v1.0.0 signoff | Full `--network` | Catches everything before shipping |
| At 6-month refresh | Full `--network` | Catches URL rot, new retractions, stale retraction_checked dates |
| In CI (on PR) | Local only | Too slow for network; gate on content discipline |
| Weekly cron (optional) | Full `--network` | Background URL-rot detection |

### Limitations

- **Venue indexing not checked** — WoS / Scopus / DOAJ aren't machine-queryable without paywalled keys. Trust the author's declared `venue_indexed` field.
- **Peer-review status not auto-verified** — can't programmatically determine if a paper was peer-reviewed. Trust the declared field.
- **Paper-type not auto-verified** — classification requires human judgment.
- **Hedge discipline not auto-verified** — faithfulness of the summary to the paper can't be checked programmatically.
- **Only first 5 primary_sources URLs checked** per file, to avoid slowness.

The harness catches mechanical errors. Content quality still needs human review.

### Extending the script

- Add new check functions following the pattern of `check_date_format`, `check_staleness`, etc.
- Register them in the main `verify_skill` loop.
- Add corresponding counter in `report["summary"]`.
- Update REQUIRED_FIELDS when frontmatter schema evolves.

### Known edge cases

- **Books / chapters** — DOI resolution works; some books lack CrossMark retraction metadata. Manual check required for book retractions (rare).
- **Preprints without DOIs** — frontmatter should use `arxiv_id`, `ssrn_id`, or `nber_wp` with `doi_status: not-issued`. Script accepts this.
- **Joint-author frontmatter** — `authors: [A, B, C]` works both as YAML list and comma-string. PyYAML handles both; fallback parser treats it as a string.
- **Mixed-mode figures/ files** — script recognizes the axis and applies figures-specific required fields (fewer than works/).
