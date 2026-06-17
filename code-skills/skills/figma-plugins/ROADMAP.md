# Roadmap — figma-plugins

Status: **0.1.2 draft** — a full 9-critic promote review ran 2026-06-17 (verdict **CONDITIONAL → stays
draft**). The cheap+correct findings were folded (see CHANGELOG 0.1.2); the items below are the explicit
gate to `stable`. Distilled from one real plugin (a design-token generator that writes Figma variable
collections); breadth beyond that surface is the main remaining gap.

## Validation owed before `stable` (the promote gate)

The 2026-06-17 9-critic council blocked stable on three Criticals; two were folded (Simon's `new Function`
self-contradiction → scoped to first-party in `testing.md`; Charity's unrecorded Verify Target → structured
-result/error-path documented). The residual gates:

- **Generalization (Elon, Karpathy).** A second plugin built *from this skill* (not the source plugin) —
  ideally the canvas/node-mutating one — to prove BUILD generalizes beyond the N=1 variables surface.
  Until then the description must not overclaim: it is honest about "variables" but "nodes" is sketched.
- **Measured routing F1 (Boris, Karpathy, Huyen).** Ship a routing-eval RUNNER that *executes*
  `evals/routing-corpus.json` through a scorer and records a real F1 — today the number is author-estimated,
  not measured (the corpus `_note` now says so). No baseline = every description edit is a vibes change.
- **Behavioral eval (Boris, Huyen, Elon).** ≥3 with-skill-vs-baseline cases on "scaffold a plugin that
  does X" — output quality, not just routing.
- **Mechanize the last prose gates (Wlaschin, Farley).** A `mock-figma.js` runnable fixture + a one-line CI
  invocation (TEST as mechanization, not advice); a bridge-envelope check (`parent.postMessage` payload
  missing `pluginMessage`) — the async-getter + exfiltration-trifecta checks landed in 0.1.2.

## Known gaps / next

- **Beyond variables.** The deepest reference is `variables-api.md` (the surface we built). Node
  creation/editing (`fills`, `createFrame`, layout, components), text + `loadFontAsync`, and styles are
  only sketched in `architecture.md`. Add a `nodes-api.md` from a second, canvas-mutating plugin.
- **D8 observability.** The `## Verify Target` now documents the structured-result + error-path pattern
  (0.1.2); still owed: `figma.notify` conventions + a dev-console checklist as a short "observability in a
  plugin" section.
- **`bin/` depth.** `check-figma-plugin.py` now gates manifest + sandbox purity + sync-getter-under-dynamic
  -page + (advisory) the exfiltration trifecta + UI storage. Still static-only: a `mock-figma.js` fixture +
  a runnable headless-apply harness would let the skill *run* a plugin's logic, not just lint it.
- **Manifest schema drift.** `networkAccess`/`documentAccess` forms have changed across API versions;
  pin the reference to a dated API version and note the migration from the string `networkAccess`.
- **Widgets / FigJam / Slides / Dev Mode.** Explicit non-goals today. If demand appears, a sibling
  skill (not a mode here) — the widget reactive model is different enough to mislead if merged.
