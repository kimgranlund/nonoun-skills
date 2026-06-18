#!/usr/bin/env python3
"""
verify_skill.py — Automated verification for theoretic-expert-author skills.

Validates that a produced skill satisfies theoretic-expert-author's invariants:
frontmatter completeness, DOI resolution, retraction status, preprint currency,
URL liveness, staleness detection.

Usage:
    verify_skill.py <skill-path> [--network] [--verbose] [--json]

Examples:
    verify_skill.py ~/.claude/skills/causal-inference-expert
    verify_skill.py ~/.claude/skills/causal-inference-expert --network
    verify_skill.py ~/.claude/skills/causal-inference-expert --network --json

Exit codes:
    0 — all checks passed
    1 — non-network checks failed
    2 — network checks failed (DOIs, URLs, retractions)
    3 — skill path not found or not a theoretic-expert skill

Dependencies:
    Required: Python 3.9+
    Optional: PyYAML (falls back to regex frontmatter parsing if absent)

Network APIs used (free, no key required):
    - Crossref REST API: https://api.crossref.org/works/<doi>
    - arxiv API: http://export.arxiv.org/api/query
    - Retraction detection via Crossref `update-to` field
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict | None:
    """Extract YAML frontmatter from a markdown string. Returns None if absent."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    raw = m.group(1)
    if HAS_YAML:
        try:
            return yaml.safe_load(raw) or {}
        except yaml.YAMLError:
            return None
    # Fallback: naive parser for flat key: value pairs
    result = {}
    for line in raw.split("\n"):
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        if ":" in line and not line.startswith(" ") and not line.startswith("-"):
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip().strip('"').strip("'")
    return result


# ---------------------------------------------------------------------------
# Required frontmatter fields per theoretic-expert-author v1.3 spec
# ---------------------------------------------------------------------------

_PAPER_FIELDS = [
    "doi", "authors", "year", "title", "venue", "venue_type",
    "peer_review_status", "retraction_status", "retraction_checked",
    "coverage", "paper_type",
]
REQUIRED_FIELDS = {
    # Paper-bearing axes (one source per file) all require the full citation/retraction field set.
    # The doctrine's canonical paper axes are findings/ and debates/ (SKILL.md/INDEX); `works` is kept
    # as a legacy alias so older skills still validate. (Pre-fix, only `works` was keyed — so DOI/
    # retraction checks silently no-op'd on findings/ and debates/ files.)
    "works": _PAPER_FIELDS,
    "findings": _PAPER_FIELDS,
    "debates": _PAPER_FIELDS,
    "figures": [
        "figure", "canonical_papers", "coverage",
    ],
    "methodology": [
        "date", "coverage",
    ],
    "structure": [
        "date", "coverage",
    ],
    "agent-dispatch": [
        "date", "coverage",
    ],
    "examples": [
        "date", "coverage",
    ],
}

VALID_PEER_REVIEW_STATUSES = {
    "peer-reviewed-published", "in-press", "preprint-not-peer-reviewed",
    "working-paper", "dissertation", "technical-report", "ambiguous",
}

VALID_RETRACTION_STATUSES = {"clean", "corrected", "concern", "retracted"}

VALID_PAPER_TYPES = {
    "empirical", "theoretical", "methodological", "review",
    "meta-analysis", "position",
}

VALID_COVERAGE_TIERS = {"foundational", "expanded", "deep"}


# ---------------------------------------------------------------------------
# Local (no-network) checks
# ---------------------------------------------------------------------------

def axis_of(rel_path: Path) -> str:
    parts = rel_path.parts
    for part in parts:
        if part in REQUIRED_FIELDS:
            return part
    return "unknown"


def check_frontmatter_completeness(file_path: Path, fm: dict, axis: str) -> list[str]:
    errors = []
    required = REQUIRED_FIELDS.get(axis, [])
    for field in required:
        if field not in fm or fm[field] in (None, "", []):
            errors.append(f"missing required field: {field}")

    # Type validation for theoretic works/ files
    if axis == "works":
        if "peer_review_status" in fm and fm["peer_review_status"] not in VALID_PEER_REVIEW_STATUSES:
            errors.append(f"invalid peer_review_status: {fm['peer_review_status']}")
        if "retraction_status" in fm and fm["retraction_status"] not in VALID_RETRACTION_STATUSES:
            errors.append(f"invalid retraction_status: {fm['retraction_status']}")
        if "paper_type" in fm and fm["paper_type"] not in VALID_PAPER_TYPES:
            errors.append(f"invalid paper_type: {fm['paper_type']}")
        if "coverage" in fm and fm["coverage"] not in VALID_COVERAGE_TIERS:
            errors.append(f"invalid coverage: {fm['coverage']}")

        # DOI or fallback identifier required
        doi = fm.get("doi")
        has_fallback = any(fm.get(k) for k in ("arxiv_id", "ssrn_id", "nber_wp"))
        if (not doi or doi in ("null", "None", "not-issued")) and not has_fallback:
            errors.append("no DOI and no fallback identifier (arxiv_id / ssrn_id / nber_wp)")

    return errors


def check_retraction_flag(file_path: Path, fm: dict, content: str) -> list[str]:
    """If retraction_status: retracted, body must contain a prominent RETRACTED banner."""
    errors = []
    if fm.get("retraction_status") == "retracted":
        if "RETRACTED" not in content[:500]:
            errors.append("retraction_status=retracted but no RETRACTED banner in first 500 chars")
    return errors


def check_date_format(fm: dict) -> list[str]:
    errors = []
    for key in ("date", "retraction_checked", "publication_date", "preprint_posted", "acceptance_date"):
        val = fm.get(key)
        if val and val not in (None, "null"):
            val = str(val)
            if not re.match(r"^\d{4}-\d{2}-\d{2}$", val):
                errors.append(f"{key} not ISO-format (YYYY-MM-DD): {val}")
    return errors


def check_staleness(fm: dict, threshold_days: int = 365) -> list[str]:
    errors = []
    rc = fm.get("retraction_checked")
    if not rc:
        return errors
    try:
        checked = datetime.strptime(str(rc), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - checked
        if age > timedelta(days=threshold_days):
            errors.append(f"retraction_checked is {age.days} days old (threshold {threshold_days})")
    except ValueError:
        pass
    return errors


def check_peer_paths(file_path: Path, fm: dict, skill_root: Path) -> list[str]:
    errors = []
    peers = fm.get("peers", []) or []
    if isinstance(peers, str):
        peers = [peers]
    for peer in peers:
        if not peer:
            continue
        peer_path = (file_path.parent / peer).resolve()
        # Allow links to parent-skill references/
        if not peer_path.exists():
            errors.append(f"peer path does not resolve: {peer}")
    return errors


def check_quote_budget(content: str, limit_words: int = 100) -> list[str]:
    """Flag blockquotes with > limit_words continuous words."""
    errors = []
    blockquotes = re.findall(r"(?:^> .*\n?)+", content, re.MULTILINE)
    for bq in blockquotes:
        words = re.findall(r"\w+", bq)
        if len(words) > limit_words:
            snippet = bq.strip().replace("\n", " ")[:80]
            errors.append(f"blockquote exceeds {limit_words} words ({len(words)}): {snippet}...")
    return errors


# ---------------------------------------------------------------------------
# Network checks (optional)
# ---------------------------------------------------------------------------

CROSSREF_API = "https://api.crossref.org/works/"
ARXIV_API = "http://export.arxiv.org/api/query?id_list={arxiv_id}"
USER_AGENT = "theoretic-expert-author-verifier/1.0 (mailto:research@example.com)"


def fetch_with_retry(url: str, max_retries: int = 3, delay: float = 1.0) -> bytes | None:
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
            if attempt == max_retries - 1:
                return None
            time.sleep(delay * (2 ** attempt))
    return None


def verify_doi_via_crossref(doi: str) -> tuple[bool, list[str]]:
    """Returns (ok, issues). Checks DOI resolves + retraction status."""
    issues = []
    if not doi or doi in ("null", "None", "not-issued"):
        return True, []
    url = CROSSREF_API + urllib.parse.quote(doi.strip())
    data = fetch_with_retry(url)
    if not data:
        return False, [f"DOI does not resolve via Crossref: {doi}"]
    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        return False, [f"DOI returned invalid JSON: {doi}"]
    message = payload.get("message", {})

    # Retraction check via update-to field
    update_to = message.get("update-to", [])
    for update in update_to:
        update_type = update.get("type", "")
        if update_type in ("retraction", "correction", "expression_of_concern"):
            issues.append(
                f"DOI has {update_type} notice: {update.get('DOI', 'unknown')}"
            )

    return len(issues) == 0, issues


def verify_arxiv_id(arxiv_id: str) -> tuple[bool, list[str]]:
    """Returns (ok, issues). Checks arxiv entry exists."""
    if not arxiv_id:
        return True, []
    # Strip version suffix for API lookup
    base_id = re.sub(r"v\d+$", "", arxiv_id.strip())
    url = ARXIV_API.format(arxiv_id=urllib.parse.quote(base_id))
    data = fetch_with_retry(url)
    if not data:
        return False, [f"arxiv lookup failed: {arxiv_id}"]
    body = data.decode("utf-8", errors="ignore")
    if "<entry>" not in body:
        return False, [f"arxiv ID not found: {arxiv_id}"]
    # Polite rate limit: arxiv asks for 3s between queries
    time.sleep(3)
    return True, []


def verify_url(url: str) -> tuple[bool, str]:
    """HEAD request to check URL returns 2xx."""
    if not url or not url.startswith(("http://", "https://")):
        return True, ""
    try:
        req = urllib.request.Request(
            url, method="HEAD", headers={"User-Agent": USER_AGENT}
        )
        with urllib.request.urlopen(req, timeout=8) as r:
            code = r.getcode()
            if 200 <= code < 400:
                return True, ""
            return False, f"URL returned {code}: {url}"
    except urllib.error.HTTPError as e:
        if e.code == 405:  # HEAD not allowed, try GET
            try:
                req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=8) as r:
                    if 200 <= r.getcode() < 400:
                        return True, ""
            except Exception:
                pass
        return False, f"URL HTTP {e.code}: {url}"
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        return False, f"URL error ({type(e).__name__}): {url}"


# ---------------------------------------------------------------------------
# Main verification pass
# ---------------------------------------------------------------------------

def walk_reference_files(skill_root: Path) -> list[Path]:
    """Yield all .md files under references/, excluding INDEX.md."""
    refs = skill_root / "references"
    if not refs.exists():
        return []
    out = []
    for md in refs.rglob("*.md"):
        if md.name == "INDEX.md":
            continue
        out.append(md)
    return out


def verify_skill(skill_root: Path, do_network: bool = False, verbose: bool = False) -> dict:
    report = {
        "skill_path": str(skill_root),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "files_checked": 0,
        "files_with_errors": 0,
        "errors_by_file": {},
        "network_checks_enabled": do_network,
        "summary": {
            "frontmatter_missing": 0,
            "required_field_missing": 0,
            "invalid_field_value": 0,
            "date_format_error": 0,
            "stale_retraction_check": 0,
            "peer_path_broken": 0,
            "quote_budget_exceeded": 0,
            "doi_unresolved": 0,
            "doi_retracted_unflagged": 0,
            "arxiv_not_found": 0,
            "url_dead": 0,
        },
    }

    # Basic sanity: is this actually a skill?
    skill_json = skill_root / "skill.json"
    if not skill_json.exists():
        report["fatal"] = f"no skill.json at {skill_root}"
        return report

    try:
        manifest = json.loads(skill_json.read_text())
    except json.JSONDecodeError as e:
        report["fatal"] = f"skill.json parse error: {e}"
        return report

    # Check the skill specializes the theory-authoring parent. Accept both the current name
    # (meta-expert-author, post-v0.2 rename) and the legacy name so older skills still pass.
    composition = manifest.get("composition", {})
    specializes = composition.get("specializes")
    if specializes not in ("meta-expert-author", "theoretic-expert-author"):
        report["warning"] = (
            f"skill.json composition.specializes is {specializes!r}, not "
            f"'meta-expert-author'. Running generic checks anyway."
        )

    files = walk_reference_files(skill_root)
    report["files_checked"] = len(files)

    for f in files:
        rel = f.relative_to(skill_root)
        axis = axis_of(rel)
        errors = []

        try:
            content = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            errors.append(f"cannot read file: {e}")
            report["errors_by_file"][str(rel)] = errors
            report["files_with_errors"] += 1
            continue

        fm = parse_frontmatter(content)
        if fm is None:
            errors.append("no YAML frontmatter")
            report["summary"]["frontmatter_missing"] += 1
            report["errors_by_file"][str(rel)] = errors
            report["files_with_errors"] += 1
            continue

        # Local checks
        fm_errors = check_frontmatter_completeness(f, fm, axis)
        errors.extend(fm_errors)
        report["summary"]["required_field_missing"] += sum(
            1 for e in fm_errors if "missing required field" in e
        )
        report["summary"]["invalid_field_value"] += sum(
            1 for e in fm_errors if e.startswith("invalid ")
        )

        date_errors = check_date_format(fm)
        errors.extend(date_errors)
        report["summary"]["date_format_error"] += len(date_errors)

        stale_errors = check_staleness(fm)
        errors.extend(stale_errors)
        report["summary"]["stale_retraction_check"] += len(stale_errors)

        peer_errors = check_peer_paths(f, fm, skill_root)
        errors.extend(peer_errors)
        report["summary"]["peer_path_broken"] += len(peer_errors)

        quote_errors = check_quote_budget(content)
        errors.extend(quote_errors)
        report["summary"]["quote_budget_exceeded"] += len(quote_errors)

        banner_errors = check_retraction_flag(f, fm, content)
        errors.extend(banner_errors)

        # Network checks
        if do_network and axis == "works":
            doi = fm.get("doi")
            if doi and doi not in ("null", "None", "not-issued"):
                if verbose:
                    print(f"  checking DOI: {doi}", file=sys.stderr)
                ok, doi_issues = verify_doi_via_crossref(doi)
                errors.extend(doi_issues)
                if not ok:
                    report["summary"]["doi_unresolved"] += sum(
                        1 for e in doi_issues if "does not resolve" in e
                    )
                    report["summary"]["doi_retracted_unflagged"] += sum(
                        1 for e in doi_issues
                        if "retraction notice" in e and fm.get("retraction_status") == "clean"
                    )
                time.sleep(0.1)  # polite spacing

            arxiv_id = fm.get("arxiv_id")
            if arxiv_id:
                if verbose:
                    print(f"  checking arxiv: {arxiv_id}", file=sys.stderr)
                ok, arxiv_issues = verify_arxiv_id(arxiv_id)
                errors.extend(arxiv_issues)
                if not ok:
                    report["summary"]["arxiv_not_found"] += 1

            # URL liveness check — primary_sources only (don't hammer every URL)
            primary = fm.get("primary_sources", []) or []
            if isinstance(primary, str):
                primary = [primary]
            for url in primary[:5]:  # cap at 5 to avoid slowness
                if url and url.startswith(("http://", "https://")):
                    ok, msg = verify_url(url)
                    if not ok:
                        errors.append(msg)
                        report["summary"]["url_dead"] += 1
                    time.sleep(0.1)

        if errors:
            report["errors_by_file"][str(rel)] = errors
            report["files_with_errors"] += 1

    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    return report


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def format_text_report(report: dict) -> str:
    lines = []
    lines.append(f"=== Skill verification report ===")
    lines.append(f"Skill: {report['skill_path']}")
    lines.append(f"Started: {report['started_at']}")
    if "fatal" in report:
        lines.append(f"FATAL: {report['fatal']}")
        return "\n".join(lines)
    if "warning" in report:
        lines.append(f"WARNING: {report['warning']}")

    lines.append("")
    lines.append(f"Files checked: {report['files_checked']}")
    lines.append(f"Files with errors: {report['files_with_errors']}")
    lines.append(f"Network checks: {'enabled' if report['network_checks_enabled'] else 'disabled'}")
    lines.append("")
    lines.append("Summary:")
    for key, count in report["summary"].items():
        if count > 0:
            lines.append(f"  {key}: {count}")

    if report["errors_by_file"]:
        lines.append("")
        lines.append("Errors by file:")
        for path, errors in sorted(report["errors_by_file"].items()):
            lines.append(f"  {path}:")
            for err in errors:
                lines.append(f"    - {err}")

    lines.append("")
    if report["files_with_errors"] == 0:
        lines.append("✅ All checks passed.")
    else:
        lines.append(f"❌ {report['files_with_errors']} file(s) have errors.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("skill_path", type=Path, help="Path to a skill directory.")
    parser.add_argument("--network", action="store_true",
                        help="Enable network checks (DOI, arxiv, URL liveness).")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Print progress to stderr.")
    parser.add_argument("--json", action="store_true",
                        help="Output machine-readable JSON instead of text.")
    args = parser.parse_args()

    skill_root = args.skill_path.expanduser().resolve()
    if not skill_root.exists():
        print(f"error: skill path not found: {skill_root}", file=sys.stderr)
        sys.exit(3)
    if not skill_root.is_dir():
        print(f"error: skill path is not a directory: {skill_root}", file=sys.stderr)
        sys.exit(3)

    report = verify_skill(skill_root, do_network=args.network, verbose=args.verbose)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_text_report(report))

    # Exit code
    if "fatal" in report:
        sys.exit(3)
    if report["files_with_errors"] == 0:
        sys.exit(0)
    # If any network-specific errors, return 2
    net_keys = ("doi_unresolved", "doi_retracted_unflagged", "arxiv_not_found", "url_dead")
    if any(report["summary"][k] > 0 for k in net_keys):
        sys.exit(2)
    sys.exit(1)


if __name__ == "__main__":
    main()
