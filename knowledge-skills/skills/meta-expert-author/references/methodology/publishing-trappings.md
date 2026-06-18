---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/canon-curation-mode.md
  - ../methodology/maintenance-and-evals.md
primary_sources:
  - expert-color skill library (LICENSE, README, MAINTENANCE, ROADMAP, SECURITY, THIRD_PARTY_NOTICES, evals/)
  - agentskills.io publication conventions
---

# Publishing trappings

Files a skill needs when shipping publicly (agentskills.io, GitHub, skill registries) that aren't needed for internal team use. Not produced by the wave arc — added manually after v1.0.0 when a skill targets release.

## When to add publishing trappings

- **Internal skill** (expert-typography, expert-dashboard): Skip the *publishing* files below. **Note: `evals/` is NOT a publishing trapping** — it is a core requirement for any reusable skill (Invariant 13), internal or public. Do not skip it.
- **Public skill** (expert-color): Add all of the below before shipping.
- **Borderline**: If the user might ever share the skill outside their org, add LICENSE + README at minimum.

## The eight trappings files

| File | Required for public? | Purpose |
|---|:-:|---|
| `LICENSE` | ✅ | Legal grant. |
| `README.md` | ✅ | Consumer-facing overview (different from SKILL.md). |
| `MAINTENANCE.md` | ✅ | How the skill is kept fresh. |
| `ROADMAP.md` | optional | What's next. |
| `SECURITY.md` | optional | Vulnerability reporting policy. |
| `THIRD_PARTY_NOTICES.md` | if embedding quotes | License attribution for embedded third-party material. |
| `evals/` | **core requirement (not a publishing trapping)** | Routing corpus (≥10 trigger + ≥5 adversarial) + ≥1 behavioral/answer-quality check, with a recorded baseline. **Required for any reusable skill, internal or public** (Invariant 13) — listed here only because authors look here for it. |
| `.gitignore` | ✅ | Exclude cached PDFs, local notes, secrets. |

## LICENSE

Pick one:

- **MIT** — Permissive. Most common for skills. Drop in the standard 21-line template.
- **Apache-2.0** — Permissive + patent grant.
- **CC-BY-4.0** — If the skill is primarily curated prose / quotations (canon-curation).
- **CC0** — Public domain dedication. For reference material with no opinionated content.

**Don't use GPL for a skill.** The skill is a knowledge artifact consumed by many agents; viral copyleft creates friction.

Stub:

```
MIT License

Copyright (c) YYYY [Author]

Permission is hereby granted, free of charge, ...
[standard MIT text]
```

## README.md

Different audience from SKILL.md:

- **SKILL.md** = agent-facing, triggers on description match, gets loaded into context.
- **README.md** = human-facing, shown on GitHub / agentskills.io listing, explains what the skill is and how to install.

Structure:

```markdown
# [skill-name]

One-sentence pitch.

## What it does

2-3 paragraphs of human-facing description. What questions does the skill answer? Who's the audience? What does it assume the user/agent already knows?

## Installation

### Claude Code

```bash
# Copy into ~/.claude/skills/
git clone https://github.com/[author]/[skill-name] ~/.claude/skills/[skill-name]
```

### Other agent harnesses

[If compatible with Codex, Cursor, etc.]

## Structure

- `SKILL.md` — the skill definition (auto-loaded).
- `references/` — deep content; loaded on demand.
- `evals/` — test prompts.

## Acknowledgments

[Attribution for canonical sources, inspirations.]

## License

[MIT / Apache-2.0 / CC-BY-4.0 — pick one]
```

Keep under 200 lines. Link to SKILL.md for the agent-facing content.

## MAINTENANCE.md

The skill's staleness contract. Covers:

- **Refresh cadence** — "Every 6 months, re-verify version numbers, acquisition claims, and Baseline markers."
- **Source-rot protocol** — "Test all `primary_sources` URLs at each refresh; replace dead links."
- **Domain-shift triggers** — Events that force an out-of-cadence refresh (major release, acquisition, spec revision).
- **How to update** — Step-by-step for contributors.
- **Owner contact** — Who to notify for major updates.

See `maintenance-and-evals.md` for the full lifecycle. MAINTENANCE.md is the consumer-facing TL;DR of that protocol.

## ROADMAP.md

What's next. Optional but useful:

```markdown
# Roadmap

## v1.1 — [target date]
- Add [product/profile/axis].
- Refresh [axis] for 2026-Q4 state.

## v1.2 — [target date]
- [planned change].

## Under consideration
- [floated ideas that may or may not land].

## Won't do
- [explicit out-of-scope decisions].
```

## SECURITY.md

Boilerplate. For skills that don't execute code, a simple policy suffices:

```markdown
# Security Policy

This skill is declarative content (Markdown + JSON). It doesn't execute code or network requests at skill-load time. However, primary-source URLs cited in references/ may be fetched by agents that consume this skill.

## Reporting a vulnerability

Email [contact] or open a private GitHub security advisory. Typical response within 7 days.

## Scope

- Incorrect claims in the knowledge base.
- Broken or malicious `primary_sources` URLs.
- Prompt-injection payloads embedded in quoted material.

## Out of scope

- Disagreements about canonical interpretation.
- Stale version numbers (report as regular issues).
```

## THIRD_PARTY_NOTICES.md

Required if the skill embeds quotes, transcripts, or content from sources with license requirements (e.g., CC-BY material, academic papers, foundry marketing copy).

Structure:

```markdown
# Third-Party Notices

## [Source 1]

**License**: [CC-BY-4.0 / MIT / fair use / etc.]
**Source**: [URL]
**Used in**: [which references/ files embed this]
**Attribution**: [required attribution text]

## [Source 2]

...
```

For color-expert-style skills that transcribe CSA talks and Color Nerd Shorts, this file is load-bearing.

## evals/

Test prompts that validate the skill works. Directory structure:

```
evals/
├── trigger-accuracy.md
├── answer-quality.md
└── regressions.md
```

See `maintenance-and-evals.md` for the full eval design.

Minimum viable eval: 10-20 prompts that should trigger the skill + 10-20 that shouldn't, with expected-answer snippets for the triggering prompts. Run manually or via a harness; keep pass/fail log per version.

## .gitignore

Standard exclusions:

```
# Local PDF cache
references/*.pdf
references/**/*.pdf

# Editor artifacts
.DS_Store
.vscode/
.idea/

# Local notes (not committed)
SCRATCH.md
local-notes/

# Secrets
.env
.env.local
```

The PDF exclusion matters for canon-curation skills that download source PDFs locally. Keep the references but not the files.

## When to add each

| Moment | Add |
|---|---|
| Planning public release | LICENSE, README.md |
| v1.0.0 signoff for public release | MAINTENANCE.md, SECURITY.md, .gitignore |
| First refresh pass | ROADMAP.md |
| First external contribution request | THIRD_PARTY_NOTICES.md |
| First regression report | evals/ |

Don't add them preemptively for internal skills. Overhead without benefit.

## agentskills.io publication checklist

Per expert-color's launch:

- [ ] LICENSE present and compatible with agentskills.io policy.
- [ ] README.md explains install + scope in under 200 lines.
- [ ] MAINTENANCE.md promises a refresh cadence you'll honor.
- [ ] skill.json `status: "complete"` + `version: "1.0.0"` or higher.
- [ ] evals/ has at least trigger-accuracy tests.
- [ ] Every URL in primary_sources resolves (run the two-minute test on a sample).
- [ ] No absolute paths in any file.
- [ ] No secrets in any file.
- [ ] `.gitignore` excludes local caches.
- [ ] Attribution complete if embedding quoted canon material.

## Internal-only shortcut

For internal team skills that don't need publishing:

- Skip everything in this file.
- Use `~/.claude/skills/CLAUDE.md` team-shared conventions instead.
- Treat the skill as a living document with rolling updates; no release ceremony.
