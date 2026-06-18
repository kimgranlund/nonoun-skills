#!/usr/bin/env python3
"""Quick validation script for skills.

Default mode: structural minimums (frontmatter + name + description).
--strict mode: adds §SelfAudit checks (routing corpus, Verify Target, Quick Start).

Used by package_skill.py before packaging. Run manually:
    python scripts/quick_validate.py <skill-dir>          # structural only
    python scripts/quick_validate.py <skill-dir> --strict  # full §SelfAudit
"""

import sys
import os
import re
import yaml
from pathlib import Path


def _check_selfaudit(skill_path: Path) -> list[str]:
    """Returns a list of §SelfAudit warning strings (empty = all pass)."""
    warnings = []
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text() if skill_md.exists() else ""
    lines = content.splitlines()

    # Routing eval corpus
    corpus = skill_path / "evals" / "routing-corpus.json"
    if not corpus.exists():
        warnings.append("⚠  evals/routing-corpus.json missing — routing accuracy is unknown")

    # Verify Target (anywhere in SKILL.md)
    if not re.search(r'^##\s+Verify Target', content, re.MULTILINE):
        warnings.append("⚠  ## Verify Target section missing — no external signal for 'done'")

    # Quick Start within first 50 lines
    first_50 = "\n".join(lines[:50])
    if not re.search(r'^##\s+Quick Start', first_50, re.MULTILINE):
        warnings.append("⚠  ## Quick Start section missing (or beyond line 50) — cold-start D1 gate FAIL")

    # ROADMAP.md
    roadmap = skill_path / "ROADMAP.md"
    if not roadmap.exists():
        warnings.append("⚠  ROADMAP.md missing — deferred scope has no canonical home")

    # Label coverage: every "### Dimension N" heading must carry `[gate]`, `[review]`, or `[hypothesis]`
    # A labeled dimension looks like: ### Dimension 3 — Title `[gate]`
    # An unlabeled one looks like:    ### Dimension 3 — Title
    dim_headings = re.findall(r'^### Dimension \d+[^\n]*', content, re.MULTILINE)
    unlabeled = [d for d in dim_headings if not re.search(r'`\[(gate|review|hypothesis)\]`', d)]
    if unlabeled:
        ex = unlabeled[0][:70]
        warnings.append(
            f"⚠  {len(unlabeled)} dimension heading(s) missing `[gate]`/`[review]`/`[hypothesis]` label "
            f"(e.g. '{ex}') — consumers cannot tell which are mechanical vs judgment-based"
        )

    return warnings


def validate_skill(skill_path, strict: bool = False):
    """Basic validation of a skill"""
    skill_path = Path(skill_path)

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Define allowed properties
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata', 'compatibility'}

    # Check for unexpected properties (excluding nested keys under metadata)
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    if name:
        # Check naming convention (kebab-case: lowercase with hyphens)
        if not re.match(r'^[a-z0-9-]+$', name):
            return False, f"Name '{name}' should be kebab-case (lowercase letters, digits, and hyphens only)"
        if name.startswith('-') or name.endswith('-') or '--' in name:
            return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
        # Check name length (max 64 characters per spec)
        if len(name) > 64:
            return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    if description:
        # Check for angle brackets
        if '<' in description or '>' in description:
            return False, "Description cannot contain angle brackets (< or >)"
        # Check description length (max 1024 characters per spec)
        if len(description) > 1024:
            return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."

    # Validate compatibility field if present (optional)
    compatibility = frontmatter.get('compatibility', '')
    if compatibility:
        if not isinstance(compatibility, str):
            return False, f"Compatibility must be a string, got {type(compatibility).__name__}"
        if len(compatibility) > 500:
            return False, f"Compatibility is too long ({len(compatibility)} characters). Maximum is 500 characters."

    # §SelfAudit checks (--strict mode or always-warn)
    warnings = _check_selfaudit(skill_path)
    for w in warnings:
        print(w)

    if strict and warnings:
        return False, f"Skill has {len(warnings)} §SelfAudit gap(s) — run without --strict to see them as warnings"

    return True, "Skill is valid!" + (f" ({len(warnings)} §SelfAudit warning(s))" if warnings else "")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    strict = "--strict" in sys.argv

    if not args:
        print("Usage: python quick_validate.py <skill_directory> [--strict]")
        print("  --strict  Treat §SelfAudit warnings as failures (routing corpus, Verify Target, Quick Start)")
        sys.exit(1)

    valid, message = validate_skill(args[0], strict=strict)
    print(message)
    sys.exit(0 if valid else 1)