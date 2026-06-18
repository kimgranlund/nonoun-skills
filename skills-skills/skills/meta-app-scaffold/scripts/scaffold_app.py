#!/usr/bin/env python3
"""Scaffold an apps/{name}/ directory tree with seeded stub files.

Mechanizes Steps 2–4 of the meta-app-scaffold SKILL.md workflow:
- Pre-condition checks (name validation, collision detection)
- Create 5 required folders
- Seed 10 stub files from embedded templates

Idempotent: skips existing files by default; use --force to overwrite.
Dry-run: lists what would be created without touching the filesystem.

Usage:
    python3 scaffold_app.py --name billing-demo --purpose "Reference app for Stripe integration"
    python3 scaffold_app.py --name tasks --dry-run
    python3 scaffold_app.py --name chat-canvas --json
    python3 scaffold_app.py --help

Exit 0 = success; 1 = error (name conflict, invalid args, write failure).
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

TODAY = date.today().isoformat()

# ─── Template library ─────────────────────────────────────────────────────────
# Each value is a callable(name, display, purpose) → str  OR  a plain str.
# Substitution rules (from references/templates.md §Substitution rules):
#   {name}         → kebab-case app name
#   {display}      → display name (title-case of name if not specified)
#   {purpose}      → one-line purpose statement
#   {today}        → YYYY-MM-DD

TEMPLATES: dict[str, str] = {
    "README.md": """\
# {display}

{purpose}

Status: **scaffolded** — see [`plan/ROADMAP.md`](./plan/ROADMAP.md) for the
multi-horizon plan and [`spec/SPEC.md`](./spec/SPEC.md) for the implementation
contract (both currently seed-only; populate via `plan-spec` and
`meta-expert-author`).

## Layout

This app borrows the Claude Code plugin folder convention as a structural shape
(skills/, assets/, etc.) plus two project-specific augmentations: `spec/`
(design axis) and `plan/` (execution axis). The app is **not a Claude Code
plugin** — there is no `.claude-plugin/plugin.json` manifest.

```
apps/{name}/
├── README.md                       ← you are here
├── PATTERNS.md                     ← non-obvious patterns ledger
├── CHANGELOG.md                    ← per-app changelog
│
├── skills/                         (Agent Skills v1 compliant)
│   └── {name}-expert/              ← project-scoped expert (research-survey basis)
│
├── assets/                         (shared media)
│   └── screenshots/                ← visual smokes
│
├── spec/                           (design axis)
│   ├── BRIEF.md                    ← PRD-01-BRIEF
│   ├── ARCHITECTURE.md             ← PRD-01-ARCH
│   └── SPEC.md                     ← PRD-01-SPEC
│
├── plan/                           (execution axis)
│   ├── ROADMAP.md                  ← Now / Next / Later / Done
│   ├── MILESTONES.md               ← v1 / v1.1 / v2 scope cuts
│   └── PLAN.md                     ← current active cut
│
└── app/                            (runnable implementation)
```

## Reading order

For product context: `spec/BRIEF.md` → `spec/ARCHITECTURE.md` → `spec/SPEC.md`.
For execution status: `plan/ROADMAP.md` → `plan/MILESTONES.md`.
For research basis: `skills/{name}-expert/SKILL.md`.

## Running the app

(populate when `app/` source is authored)

## Authoring discipline

- Foundation scaffolded by `meta-app-scaffold`.
- Skill authored via `meta-expert-author` (capability mode).
- Spec authored via `plan-spec` against the research-survey basis.
- No fabricated bug IDs / RFC numbers / commit SHAs.
""",

    "PATTERNS.md": """\
# {display} — Patterns

Non-obvious patterns surfaced during the build of this app. Each entry should
answer "what would surprise a reader who hadn't built this?"

This ledger is initially empty — entries are added as the app is implemented.

## Cross-references

- **`spec/SPEC.md`** — the full type-driven contract
- **`spec/ARCHITECTURE.md`** — boundary contract sketches
- **`plan/MILESTONES.md`** — what's in v1 / v1.1 / v2
- **`plan/ROADMAP.md`** — multi-horizon view
""",

    "CHANGELOG.md": """\
# Changelog

All notable changes to this app are documented here.

## [Unreleased]

- Foundation scaffolded via `meta-app-scaffold`.

## [0.1.0] - {today}

- Initial scaffold.
""",

    "skills/{name}-expert/SKILL.md": """\
---
name: {name}-expert
description: >
  Project-scoped expert knowledge for the {display} app at `apps/{name}/`.
  Use when designing, specifying, or implementing this app's features or
  architecture. Stub created by `meta-app-scaffold`; substantive content
  to be authored via `meta-expert-author` (capability mode by default).
metadata:
  status: stub
  scope: project-local
  project_root: apps/{name}
  authored_via: meta-app-scaffold
  next_step: meta-expert-author --target apps/{name}/skills/{name}-expert/
---

# {name}-expert

**Status: STUB.** This SKILL.md was scaffolded by `meta-app-scaffold`.
Substantive content (references/, cheat sheets, task→reference routing) will be
authored by `meta-expert-author`.

To populate this skill:

```
use meta-expert-author — target apps/{name}/skills/{name}-expert/ mode capability
```

Until that runs, this skill is a placeholder — don't reference it from spec
docs as if it carries content.
""",

    "spec/BRIEF.md": """\
# {display} — Brief

**Document:** PRD-01-BRIEF
**Version:** 0.1.0
**Date:** {today}
**Status:** Stub — to be authored by `plan-spec`
**Audience:** Product, engineering, design

---

## How to Read This Document

This brief will be the 3-page front-door once authored. Until then, see
[`ARCHITECTURE.md`](./ARCHITECTURE.md) for decision defenses and
[`SPEC.md`](./SPEC.md) for the implementation contract. For execution-axis
context, see [`../plan/ROADMAP.md`](../plan/ROADMAP.md). Research basis at
[`../skills/{name}-expert/`](../skills/{name}-expert/).

## 1. What This Is

{purpose}

## 2. Why It Exists

(populate via plan-spec)

## 3. First Principles

(populate via plan-spec)

## 4. Core Architecture

(populate via plan-spec)

## 5. Open Decisions

(track unresolved questions with options + tradeoffs)

---

**Authoring next step**: `plan-spec` against the research-survey basis at
`../skills/{name}-expert/`.
""",

    "spec/ARCHITECTURE.md": """\
# {display} — Architecture

**Document:** PRD-01-ARCH
**Version:** 0.1.0
**Date:** {today}
**Status:** Stub — to be authored by `plan-spec`

---

This document defends each architectural choice. Until authored, the
architecture is undecided.

For the 3-page summary, see [`BRIEF.md`](./BRIEF.md). For implementation
detail, see [`SPEC.md`](./SPEC.md). For version-by-version scope, see
[`../plan/MILESTONES.md`](../plan/MILESTONES.md).

## Sections (to be populated)

- Boundaries
- Type architecture
- Domain primitives
- Boundary contracts
- State machines
- Composition patterns

**Next document**: [`SPEC.md`](./SPEC.md) — full implementation contract.
""",

    "spec/SPEC.md": """\
# {display} — Specification

**Document:** PRD-01-SPEC
**Version:** 0.1.0
**Date:** {today}
**Status:** Stub — to be authored by `plan-spec`

---

The full implementation contract for this app. Until authored, the
specification is undefined.

For orientation, see [`BRIEF.md`](./BRIEF.md). For decision defenses, see
[`ARCHITECTURE.md`](./ARCHITECTURE.md). The research-survey basis is at
[`../skills/{name}-expert/`](../skills/{name}-expert/).

## Sections (to be populated)

- R1. Component contracts
- R2. State architecture
- R3. Service / controller / command boundaries
- R4. Data schema
- R5. Accessibility model
- R6. Persistence
- R7. Open issues

---

**Authoring next step**: `plan-spec --target apps/{name}/spec/` against the
research-survey basis at `../skills/{name}-expert/`.
""",

    "plan/ROADMAP.md": """\
# {display} — Roadmap

**Document:** plan-roadmap
**Updated:** {today}
**Audience:** Implementers, future agents

Multi-horizon view. For dated scope cuts, see [`MILESTONES.md`](./MILESTONES.md).
For the active cut's plan, see [`PLAN.md`](./PLAN.md). For design-axis docs,
see [`../spec/`](../spec/).

---

## Now (in flight)

_No active initiative._

## Next (queued)

_(populate as v1.0 work surfaces)_

## Later (deferred)

_(populate as longer-horizon ideas surface)_

## Done

_(populate as cuts ship)_
""",

    "plan/MILESTONES.md": """\
# {display} — Milestones

**Document:** PRD-01-MS
**Version:** 0.1.0
**Date:** {today}
**Status:** Stub — to be populated as scope is committed

---

## Milestone Map

| Milestone | Target | Outcome |
|---|---|---|
| **v1.0.0** | First demonstrable cut | (populate) |
| **v1.1.0** | Polish + missing surfaces | (populate) |
| **v2.0.0** | (populate) | (populate) |

---

## v1.0.0 — (Title)

### Outcome

(what works at v1.0?)

### Definition of done

- [ ] (populate)

## Out of scope

(items intentionally excluded; not promises)
""",

    "plan/PLAN.md": """\
# {display} — Active Plan

**Document:** plan-active
**Updated:** {today}
**Audience:** Anyone working on this app today

---

## Status

**No active initiative.** Promote a v1.0 candidate from
[`ROADMAP.md`](./ROADMAP.md) `## Next` to `## In flight` here when starting
work.

---

## Archive policy

When an initiative ships, this PLAN gets reset to "no active initiative" and
the dated entry promotes into [`MILESTONES.md`](./MILESTONES.md). Older PLAN
content is captured in commit history.
""",
}

REQUIRED_DIRS = [
    "skills/{name}-expert",
    "assets/screenshots",
    "spec",
    "plan",
    "app",
]


def to_display(name: str) -> str:
    """kebab-case → Title Case (e.g. 'billing-demo' → 'Billing Demo')."""
    return " ".join(word.capitalize() for word in name.split("-"))


def validate_name(name: str) -> str | None:
    """Return an error string if name is invalid, else None."""
    if not re.match(r"^[a-z0-9][a-z0-9\-]*$", name):
        return f"Name '{name}' must be kebab-case: lowercase letters, digits, and hyphens only"
    if name.startswith("-") or name.endswith("-") or "--" in name:
        return f"Name '{name}' cannot start/end with a hyphen or contain consecutive hyphens"
    if len(name) > 64:
        return f"Name '{name}' is too long ({len(name)} chars, max 64)"
    return None


def render(template: str, name: str, display: str, purpose: str) -> str:
    return (
        template
        .replace("{name}", name)
        .replace("{display}", display)
        .replace("{purpose}", purpose)
        .replace("{today}", TODAY)
    )


def scaffold(
    name: str,
    display: str,
    purpose: str,
    base_dir: Path,
    mode: str,
    dry_run: bool,
    force: bool,
) -> tuple[list[str], list[str], list[str]]:
    """Returns (created, skipped, errors)."""
    app_root = base_dir / "apps" / name
    created: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []

    # Folders
    for d_tpl in REQUIRED_DIRS:
        d = app_root / d_tpl.replace("{name}", name)
        rel = str(d.relative_to(base_dir))
        if d.exists():
            skipped.append(f"  [skip] {rel}/ (already exists)")
        elif dry_run:
            created.append(f"  [dry]  {rel}/")
        else:
            try:
                d.mkdir(parents=True, exist_ok=True)
                created.append(f"  [dir]  {rel}/")
            except OSError as e:
                errors.append(f"  [err]  {rel}/: {e}")

    # Files
    for file_tpl, content_tpl in TEMPLATES.items():
        rel_file = file_tpl.replace("{name}", name)
        dest = app_root / rel_file
        rel = str(dest.relative_to(base_dir))
        content = render(content_tpl, name, display, purpose)

        if dest.exists() and not force:
            skipped.append(f"  [skip] {rel} (exists; use --force to overwrite)")
            continue

        if dry_run:
            created.append(f"  [dry]  {rel}")
            continue

        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(content, encoding="utf-8")
            action = "[over]" if dest.exists() else "[new] "
            created.append(f"  {action} {rel}")
        except OSError as e:
            errors.append(f"  [err]  {rel}: {e}")

    return created, skipped, errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="scaffold_app.py",
        description="Scaffold an apps/{name}/ directory tree with seeded stub files.",
        epilog="Exit 0 = success; 1 = error.",
    )
    ap.add_argument("--name", required=True, help="Kebab-case app name (e.g. billing-demo)")
    ap.add_argument("--display-name", default="", dest="display",
                    help="Display name (default: Title Case of --name)")
    ap.add_argument("--purpose", default="(purpose not specified)",
                    help="One-line purpose statement for README and BRIEF")
    ap.add_argument("--base-dir", default=".", dest="base_dir",
                    help="Root of the monorepo (apps/ will be created here)")
    ap.add_argument("--mode", choices=["greenfield", "reverse-engineering"],
                    default="greenfield", help="Scaffold mode (default: greenfield)")
    ap.add_argument("--dry-run", action="store_true",
                    help="List what would be created without touching the filesystem")
    ap.add_argument("--force", action="store_true",
                    help="Overwrite existing seed files (dangerous; preserves non-seed files)")
    ap.add_argument("--json", action="store_true", dest="json_out",
                    help="Emit a machine-readable JSON manifest instead of human output")
    args = ap.parse_args(argv)

    # Validate name
    err = validate_name(args.name)
    if err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1

    name = args.name
    display = args.display or to_display(name)
    base_dir = Path(args.base_dir).resolve()
    app_root = base_dir / "apps" / name

    # Collision check (non-dry-run only)
    if not args.dry_run and app_root.exists() and not args.force:
        existing = list(app_root.iterdir())
        if existing:
            print(
                f"ERROR: apps/{name}/ already exists and is non-empty.\n"
                f"Options:\n"
                f"  (a) pick a different name\n"
                f"  (b) use --force to complete any missing seed files\n"
                f"  (c) git mv apps/{name} apps/<old-name> and start fresh",
                file=sys.stderr,
            )
            return 1

    # Reverse-engineering mode note
    if args.mode == "reverse-engineering":
        if not args.json_out:
            print(
                "\n⚠  REVERSE-ENGINEERING MODE: Step 4.5 pre-pass required.\n"
                "   Before authoring any spec content, complete the verified-surface\n"
                "   inventory (grep imports → read component yaml → read source end-to-end\n"
                "   → build verified-surface table). See references/reverse-engineering.md.\n"
            )

    created, skipped, errors = scaffold(
        name=name,
        display=display,
        purpose=args.purpose,
        base_dir=base_dir,
        mode=args.mode,
        dry_run=args.dry_run,
        force=args.force,
    )

    if args.json_out:
        manifest = {
            "skill": "meta-app-scaffold",
            "name": name,
            "display": display,
            "purpose": args.purpose,
            "mode": args.mode,
            "base_dir": str(base_dir),
            "app_root": str(app_root),
            "dry_run": args.dry_run,
            "created": [s.strip() for s in created],
            "skipped": [s.strip() for s in skipped],
            "errors": [s.strip() for s in errors],
            "ok": len(errors) == 0,
        }
        print(json.dumps(manifest, indent=2))
        return 0 if not errors else 1

    # Human output
    verb = "Would create" if args.dry_run else "Created"
    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Scaffolding apps/{name}/\n")

    if created:
        print(f"{verb}:")
        print("\n".join(created))
    if skipped:
        print(f"\nSkipped ({len(skipped)}):")
        print("\n".join(skipped))
    if errors:
        print(f"\nErrors ({len(errors)}):", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    if not args.dry_run:
        print(f"\n✓ Scaffolded apps/{name}/ ({len(created)} items)")
        print(f"\nProposed follow-ups (run in order or skip per priority):")
        print(f"  1. meta-expert-author → apps/{name}/skills/{name}-expert/ (capability mode)")
        print(f"  2. plan-spec → apps/{name}/spec/ (BRIEF + ARCHITECTURE + SPEC)")
        print(f"  3. (optional) plan-prd → apps/{name}/spec/PRD.md (schema-validated)")
        print(f"  4. (optional) skills-studio author → app-private slash commands or secondary skills")
    return 0


if __name__ == "__main__":
    sys.exit(main())
