# Roadmap

Planned work for the skill beyond reference collection and curation.

**Recently shipped (v1.13–v1.20):** a working TypeScript implementation in `src/` — 24 color spaces (each with `toXYZ`/`fromXYZ`), gamut math (cusp, peak C/L, CSS Color 4 mapping), ΔE metrics (76/94/2000/ok/HyAB), CVD simulation (Machado 2009), tone mapping (Reinhard/ACES), Kubelka-Munk pigment mixing, spectral integration (CIE 1931 CMF + D65/D50/A/F2/E SPDs), Bradford CAT, k-means quantization, Floyd-Steinberg dithering, cubehelix interpolation — plus an `examples/` showcase site (54 live demos, 28 custom elements, single `file://`-safe IIFE bundle). The original palette-naming and contrast-matrix roadmap items are subsumed by that implementation.

## Planned
<!-- Features and improvements for a future version. -->
<!-- Format: - [vX.Y] Description -->
Small deterministic helper scripts under `scripts/` that **wrap** the repo's recommendations (never compete with them), in likely build order:
- Palette naming helper — nearest names from one or more dictionaries (default: color.pizza `bestOf`); switchable to a preferred naming system; transparent about which dictionary produced each name.
- Contrast matrix helper — pairwise WCAG (and, if simple, APCA) contrast over a palette, easy to inspect useful text/background pairs.
- Duplicate / near-duplicate detector — perceptual (not raw-hex) detection of palette steps that collapse visually.
- Perceptual sorting helper — a wrapper over `colorsort-js` (already recommended) that preserves explainable metadata.
- Ramp / scale wrapper — call a recommended generator and emit the **reproducible recipe** (tool, anchors, options, space) alongside the output.

## Deferred
<!-- Capabilities considered but postponed — document the reason and re-evaluation trigger. -->
- All five `scripts/` helpers above — deferred because the skill is a **knowledge resource first**; build a helper only once a real, repeated agent need makes it worth the maintenance. Revisit when a given helper would be invoked often enough to justify shipping it.

## Out of scope (by design)
<!-- Capabilities explicitly excluded — not postponed, intentionally outside this skill's boundary. -->
- Reimplementing color libraries the skill already recommends — `scripts/` helpers wrap/support recommendations, they do not replace them.
- Growing the repo into a large application framework — any helper stays small, deterministic, clear-I/O, and reproducible so the skill remains a knowledge resource, not a framework.
