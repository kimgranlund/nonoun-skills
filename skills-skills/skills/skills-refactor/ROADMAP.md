# Roadmap

## Planned
- [DONE v0.3] ~~First tool-driven refactor~~ → **`arch-dogfood → arch-pattern`** merge run through `scan`→backup→`verify` (AGENTS v3.8.0). Graduation **1 of ≥3**.
- [DONE] ~~Second tool-driven refactor~~ → **`maintain-tokens-advanced → maintain-tokens`** (AGENTS v3.9.0) — an **investigation-driven merge** (the decision wasn't pre-made: read both forks, confirmed superset + consumer-asymmetry, then host-keeps-name/absorbs-better-content). `verify` returned 0 dangling refs cleanly on first run (the v0.3 provenance fix held). Graduation **2 of ≥3**.
- [DONE v0.3] ~~`verify` provenance-awareness~~ → the first tool-driven run surfaced a false positive: `verify` flagged 7 *provenance* mentions ("former/retired/absorbed/merged X", "(retired) → Y", the re-baseline `reason`) as dangling LIVE refs. Fixed — `verify` now separates a **dangling pointer** (quoted `"<old>"` token / dead `<old>/` path / unmarked prose → FAIL) from a **retirement-marked provenance mention** (kept); `PROVENANCE_MARKERS` + `_is_dangling`/`_is_structural_ref` + `--json` `provenance_allowed` bucket + 4 new selftest cases.
- [DONE v0.2] ~~Mechanize the footprint map + verify gate~~ → **`scripts/refactor-scan.py`** shipped: `scan` (LIVE/MIXED/HISTORY classification + tag-only NOT-A-REF), `dry-run` (word-boundaried, the C-S1 fix as a tool), `check-backup` (the MAJOR-S3 delete-precondition), `verify` (zero-live-refs done-gate), `selftest` (wired into `run-skill-gates.py`). Backup / map+dry-run / verify §SelfAudit items relabeled `[review]`→`[gate]`.
- [DONE v0.2] ~~`--reason` on re-baseline (MAJOR-W2)~~ → `score-routing.py --update-baseline --reason "<…>"` records the intentional change into `routing-baselines.json`.
- [DONE v0.2] ~~Routing F1 baseline~~ → scored **0.96**, committed.
- [v1.0] **Graduation criterion:** ≥3 refactors driven *by the skill* (`refactor-scan` scan→dry-run→verify in the loop), each landing the gate suite green on the first verify. **Progress: 2 of ≥3** — (1) arch-dogfood → arch-pattern (v0.3, which also *proved* the loop by finding + fixing the `verify` provenance bug on first real use); (2) maintain-tokens-advanced → maintain-tokens (investigation-driven; `verify` clean on first run). **1 more to graduate** from "faithful procedure capture + working toolset" to "proven end-to-end loop."
- [v0.x] A `split` worked example — the one operation of the four with **no** worked example behind it yet (rename ×3, merge ×3, retire ×2 are battle-tested this session; split is derived by symmetry).

## Deferred
- A `merge`-conflict resolver for when two skills being merged define the *same* reference filename or rubric — deferred because the campaign's merges had no such collision; revisit when one does.
- Cross-*library* refactor (moving a skill between `~/.claude/skills/` and a project's `.claude/skills/`) — deferred because the current contract is one library; `ops-repo` owns the project-repo side. Revisit if a real cross-library move comes up.

## Out of scope (by design)
- **Authoring or editing a skill's content** — `skills-studio` (author / edit / optimize). This skill changes a skill's name/boundaries/existence and the wiring around it, not its internal quality.
- **Deciding *whether* to refactor** (the quality judgment that a skill should be merged/retired) — that's a `skills-studio` critique/score output; this skill *executes* the decision.
- **Project-repo doc/skill hygiene** — `ops-repo` (`.brain`, AGENTS.md, project `.claude/skills/`).
- **Renaming symbols in source code** — ordinary code refactoring.
