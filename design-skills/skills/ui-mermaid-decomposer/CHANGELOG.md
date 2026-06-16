# Changelog — ui-mermaid-decomposer

Format: [Keep a Changelog](https://keepachangelog.com/). Versioning: [SemVer](https://semver.org/).

## [0.1.0] — 2026-06-16

Initial cut. The two-axis diagram technique, modeled on [[ui-layout-decomposer]] and built on the advanced-Mermaid reference + rubric authored for the catalog corpus-reader (`mermaid@11.15.0`, `securityLevel:"strict"`).

### Added
- **The two-axis method** (`references/decomposition-method.md`) — INTENT (whole→atom: relationship → type →
  skeleton → elements → labels) × RENDER (atom→whole: keyword → syntax → strict-safety → legibility → portable),
  the gated walk (A1·A2 + B1·B2·B3 `[gate]`, the rest `[review]`), the "right-but-broken vs renders-but-wrong"
  framing, and the CREATE / DECOMPOSE / GRADE workflows — mapped level-by-level onto the rubric M1–M6.
- **The advanced-Mermaid reference** (`references/advanced-mermaid-reference.md`) — the reader-compatibility
  contract, the keyword/version matrix (every type is in 11.15.0; the `-beta` suffix is the trap), and per-type
  verbatim minimal syntax + gotchas for the 11 advanced types. Web-researched against the canonical mermaid.js.org
  docs + the mermaid-js/mermaid source/releases.
- **The diagram-quality rubric** (`references/mermaid-rubric.md`) — six dimensions (M1 type-fit · M2 syntax/version
  `[gate]` · M3 renders-in-target `[gate]` · M4 legibility · M5 accessibility · M6 portability) with score tables,
  anti-patterns, and hard tests.
- `SKILL.md` table-of-contents with Quick Start, the two-axis method table, the diagram-type-family selector,
  §SelfAudit (renderability-is-a-gate; right-type-first; strict-is-the-assumption; artifact-as-data; two-scores-
  never-one; start-from-the-verbatim-example), and a Verify Target.
