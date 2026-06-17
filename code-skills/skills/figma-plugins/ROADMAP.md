# Roadmap — figma-plugins

Status: **0.1.0 draft**. Distilled from one real plugin (a design-token generator that writes Figma
variable collections). Breadth beyond that surface is the main gap.

## Known gaps / next

- **Beyond variables.** The deepest reference is `variables-api.md` (the surface we built). Node
  creation/editing (`fills`, `createFrame`, layout, components), text + `loadFontAsync`, and styles are
  only sketched in `architecture.md`. Add a `nodes-api.md` from a second, canvas-mutating plugin.
- **D8 observability.** The `## Verify Target` is honest (one human import-and-run) but there is no
  in-Figma telemetry pattern documented (e.g. `figma.notify` conventions, error surfacing to the UI,
  a dev-console checklist). Add a short "observability in a plugin" section.
- **`bin/` depth.** `check-figma-plugin.py` is static-only (manifest + sandbox purity). A
  `mock-figma.js` fixture + a runnable headless-apply harness (the `testing.md` pattern as code) would
  let the skill *run* a plugin's logic, not just lint it — moving TEST from advice to mechanization.
- **Manifest schema drift.** `networkAccess`/`documentAccess` forms have changed across API versions;
  pin the reference to a dated API version and note the migration from the string `networkAccess`.
- **Widgets / FigJam / Slides / Dev Mode.** Explicit non-goals today. If demand appears, a sibling
  skill (not a mode here) — the widget reactive model is different enough to mislead if merged.

## Validation owed before `stable`

- A second plugin built *from this skill* (not the source plugin) to prove the BUILD mode generalizes.
- `eval` behavioral cases (with-skill vs. baseline) on "scaffold a plugin that does X" tasks.
- Re-run `critique full-panel` (only Simon + Wlaschin ran at 0.1.0).
