# CLAUDE.md

This file provides guidance when working with code in this repository.

## Project Overview

This is an **agent skill** (compatible with Claude Code, Codex, Cursor, Copilot, OpenCode, and others via [agentskills.io](https://agentskills.io)). It contains a `SKILL.md` file that serves as a color expertise knowledge base, automatically loaded when the agent handles color-related tasks (naming, theory, spaces, accessibility, perception).

## Architecture

- `SKILL.md` — The skill definition with YAML frontmatter (`name`, `description`) and structured color knowledge. Loaded when color work is detected.
- `references/INDEX.md` — Master lookup table for 140+ deep reference files.
- `references/historical/` — Pre-digital color science (Ostwald, Helmholtz, ISCC-NBS, etc.)
- `references/contemporary/` — Modern color science (OKLAB, Briggs, CSA webinars, etc.)
- `references/techniques/` — Tools, libraries, methods (Spectral.js, Culori, APCA, palette generation, etc.)
- `src/` — Working TypeScript implementation: 24 color spaces (every one exports `toXYZ` + `fromXYZ`), gamut math, ΔE metrics, CVD simulation (Machado 2009), tone mapping (Reinhard / ACES), Kubelka-Munk pigment mixing, spectral integration (CIE 1931 CMF + illuminant SPDs), Bradford CAT, k-means quantization, Floyd-Steinberg dithering, cubehelix / spline interpolation.
- `examples/` — Static showcase site dogfooding `src/`. 54 live demos as classic HTML pages; 28 custom-element components; single IIFE bundle (`examples/lib/dist/refcolor.bundle.js`) so everything works directly over `file://`.

## Build

The reference content (`SKILL.md`, `references/`) needs no build — it's declarative. The TypeScript implementation does:

```bash
cd examples
./build.sh   # tsc (optional, if local) + esbuild → lib/dist/refcolor.bundle.js
```

`build.sh` falls back gracefully if no local `tsc` is present; it always runs `esbuild` to produce the IIFE bundle. CI is not required — the bundle is committed.

## Editing Guidelines

- Keep SKILL.md frontmatter `description` field accurate — it controls when the skill triggers.
- The skill is referenced by name (`color-science`).
- SKILL.md is the "greatest hits" — load-bearing color knowledge an agent needs frequently (color spaces lookup, gamut math, accessibility numbers, harmony rules, naming systems, recommended tools). Deep content lives in `references/`. Current size (~280 lines) reflects the breadth of color expertise the body carries; keep new content here only when it's frequently referenced — otherwise add to `references/`.
- Deep content goes in `references/` files, not in SKILL.md.
- PDFs are gitignored (~236MB); archive.org source links are preserved in every reference file.
