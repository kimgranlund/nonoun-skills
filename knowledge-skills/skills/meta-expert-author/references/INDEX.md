---
date: 2026-05-06
---

# meta-expert-author — Reference Index

_Manifest of files that ship with this meta-skill. Every reference file here should be loaded only when the task at hand maps to its purpose line._

## Axes

1. **methodology/** — the research-wave method, scoping, axes, coverage tiers, verification.
2. **structure/** — templates for the four skeleton files + individual reference files.
3. **agent-dispatch/** — brief template, wave planning, post-wave bookkeeping.
4. **examples/** — real skills produced by this method, as case studies.

## File manifest

| Status | Path | Purpose |
|---|---|---|
| | **methodology/** | |
| ✅ | `methodology/wave-based-research.md` | The 5-wave arc: scoping → W1 foundations → W2-4 expansions → W5 phase-2 → v1.0.0. |
| ✅ | `methodology/scoping-survey.md` | How to run the single-agent scoping survey that produces the axis list + file plan. |
| ✅ | `methodology/axis-identification.md` | Decomposing a domain into axes; how typography and dashboards map. |
| ✅ | `methodology/coverage-tiers-and-frontmatter.md` | foundational / expanded / deep + YAML frontmatter spec. |
| ✅ | `methodology/verification-discipline.md` | No-fabrication rules, primary-source obligations, rot-resistant sourcing, observable-public-only posture. |
| ✅ | `methodology/canon-curation-mode.md` | The alternate genre: source-organized files, temporal axes, "greatest hits" SKILL.md. Decision framework for capability vs canon-curation mode. |
| ✅ | `methodology/invocation-flow.md` | The first-message experience: four-question gate, clarifying questions, bail-out points. Orchestrates steelmanning + concept-matching. How to avoid dispatching scoping on vague prompts. |
| ✅ | `methodology/prompt-steelmanning.md` | Three steelman moves (latent-intent / stronger-shape / scope-recalibration). Propose-and-wait pattern. When to steelman vs proceed. Worked examples. Anti-patterns (scope creep, condescension, post-proceed steelmanning). |
| ✅ | `methodology/concept-matching.md` | Introspective inventory of base-model coverage before WebSearch. Five-step protocol (list 15-25 concepts / rate confidence / cluster / temporal / axis proposal). Calibrates WebSearch budget + hedge level + axis shape. Worked causal-inference example. |
| ✅ | `methodology/task-decomposition.md` | Break ingested asks into covering, non-overlapping, individually-tractable sub-asks. Three decomposition shapes (axis / task / question). 6-step protocol (restate / seams / name / coverage-check / ordering / propose). Three worked examples (meta-skill, produced-skill, narrow refactor). Completes the ingestion → decomposition → execution triad. |
| ✅ | `methodology/publishing-trappings.md` | Files a skill needs for public release (LICENSE / README / MAINTENANCE / ROADMAP / SECURITY / THIRD_PARTY_NOTICES / evals / .gitignore). agentskills.io checklist. |
| ✅ | `methodology/maintenance-and-evals.md` | Post-v1.0 lifecycle: refresh cadence, event-driven triggers, URL/version/acquisition audits. Trigger-accuracy and answer-quality evals. Version semantics post-1.0. Deprecation. |
| ✅ | `methodology/stale-skill-recovery.md` | Triage for 12+ month-stale skills: refresh / partial / fork / deprecate. Wave-style mini-refresh structure. Refresh-wave agent brief template. |
| ✅ | `methodology/cross-skill-dependencies.md` | Four dependency kinds (mention / peer / file-path / hard). Peer-refresh propagation semantics (pull model). Shared-vocabulary drift. Version-compatibility matrices. Breaking-change etiquette. |
| | **structure/** | |
| ✅ | `structure/skeleton-files.md` | Templates for SKILL.md, skill.json, INDEX.md, CHANGELOG.md. |
| ✅ | `structure/reference-file-template.md` | Template for an individual reference file. |
| | **agent-dispatch/** | |
| ✅ | `agent-dispatch/agent-brief-template.md` | Canonical prompt template for a wave's parallel agents. |
| ✅ | `agent-dispatch/wave-planning.md` | How to size, balance, and pair files within a wave. |
| ✅ | `agent-dispatch/bookkeeping-protocol.md` | Post-wave INDEX / skill.json / CHANGELOG protocol. Includes sed-accident warning. |
| | **examples/** | |
| ✅ | `examples/dashboard-expert-case-study.md` | 101 files / 15 axes / 5 waves / ~57k lines. Big-domain exemplar. |
| ✅ | `examples/typography-expert-case-study.md` | 59 files / 5 waves. Narrower-domain capability exemplar. |
| ✅ | `examples/color-expert-case-study.md` | 148 files / 3 axes. Canon-curation exemplar, published publicly on agentskills.io. |
| ✅ | `examples/mixed-mode-case-study.md` | Skills that are partly capability + partly canon-curation. expert-color's `techniques/` axis as exemplar. Signals, anti-patterns, per-axis mode declaration. |
| ✅ | `examples/micro-skill-case-study.md` | 15-25 file / 3-5 axis / 2-3 wave micro variant. When to pick, how to compress the wave arc, skipping scoping survey, validation that it's not too small. |

## Conventions mirrored in produced skills

- YAML frontmatter per reference file: `date`, `coverage`, `peers`, `primary_sources`.
- Coverage tiers declared up-front.
- Primary sources cited at file level.
- Dates use ISO format.
- Product references = observable public only.
