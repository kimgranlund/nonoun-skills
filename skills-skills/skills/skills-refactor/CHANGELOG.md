# Changelog — skills-refactor

## 0.3.0 — 2026-05-31 — First tool-driven refactor (graduation 1/3) + provenance-aware `verify`

The skill's **first refactor driven by its own tooling** end-to-end: the long-deferred `arch-dogfood → arch-pattern` merge (fold the DOGFOOD phase back as a conditional Component-Library Mode + retire the fork). Ran the loop as designed — `refactor-scan.py scan arch-dogfood` (footprint: 11 LIVE / 8 MIXED / 1 HISTORY), whole-library backup + `check-backup` asserted before the delete, additive build, then `verify` as the done-gate — and it **surfaced a real limitation in `verify`**, which this release fixes.

### The dogfooding find (and fix)
- **`verify` couldn't tell a dangling pointer from a provenance mention.** Its first real run **failed** on 7 occurrences that were all *intentional history* — a SKILL.md "Absorbed from the **former** arch-dogfood skill" note, a planning-table "`(retired)` → arch-pattern" redirect row, eval-corpus provenance notes, and the `score-routing` re-baseline `reason` naming what was dropped. None was live wiring (no `peer_skills` element, no `use X` pointer, no dead path), and the metadata/gate/routing checks were all green — so this was a false positive, not a broken merge. A retire **legitimately** leaves the old name in live files *as history*.
- **Fix:** `verify` now classifies each remaining LIVE-file occurrence per-line. A **dangling ref (FAIL)** is structural wiring — a quoted `"<old>"` token (peer_skills/files element or JSON key) or a dead `<old>/…` path — **or** bare prose with no retirement marker. A **provenance mention (allowed)** carries a retirement marker (`former`/`retired`/`absorbed`/`merged`/`folded`/`deprecated`/`renamed`/`superseded`/`→`/`(retired)`) and isn't structural. Structural wiring still FAILs even if a marker word shares the line (a quoted token / dead path breaks on delete regardless). New `PROVENANCE_MARKERS` + `_is_structural_ref` / `_is_dangling` helpers; the `--json` output gains a `provenance_allowed` bucket; the human output separates "dangling (FAIL)" from "provenance (kept)".
- **`selftest` extended** with the discrimination cases: provenance prose is allowed; a quoted token, a dead path, and a bare unmarked pointer each still FAIL. (Gate #12 stays green.)

### Result
- `arch-pattern` v0.3.0 absorbed the DOGFOOD phase; `arch-dogfood` retired. `verify arch-dogfood` → **0 dangling LIVE refs** (7 provenance mentions kept); `check-skill-metadata` **71/71 · 0 errors**, `run-skill-gates` **12/12**, `score-routing` **PASS**. Backup at `~/.claude/skills-backup-arch-merge.tgz`.
- **Graduation: 1 of ≥3 tool-driven refactors done.** The procedure-capture is now also a *proven* loop (it found and fixed a tool bug on first real use). `skill.json` 0.2.0 → 0.3.0; `files[]` unchanged.

## 0.2.0 — 2026-05-31 — Mechanize the gates: `scripts/refactor-scan.py` (closes the 2 deferred red-team Majors)

Turns the §SelfAudit prose discipline into running checks — the v0.2 ROADMAP work, and the two red-team Majors (S3 backup-precondition, W2 re-baseline-reason) that v0.1.0 deferred.

### Added
- **`scripts/refactor-scan.py`** (stdlib-only) — the mechanical spine: `scan <old>` (footprint map, classified LIVE / MIXED / HISTORY, with skill.json tag-only hits flagged NOT-A-REF — so the live-vs-history split isn't done by eye), `dry-run <old> <new>` (the word-boundaried substitutions the sweep *would* make, no writes), `check-backup --since` (asserts a whole-library backup tarball exists — the precondition a delete must pass, **MAJOR-S3**), `verify <old>` (asserts **zero LIVE refs** remain — the done-gate), and `selftest` (proves the word-boundary `core-foo ∌ core-foobar`, the classification, and verify pass/fail). Registered in `run-skill-gates.py` (selftest).
- **`score-routing.py --reason`** (in repo `scripts/`) — `--update-baseline --reason "<intentional change>"` records *why* into `routing-baselines.json`, so a legitimate re-baseline is structurally distinguishable from editing a gate to pass (**MAJOR-W2** — makes First Principle 4 a discriminant, not a plea).

### Changed
- §SelfAudit: **backup**, **map+dry-run**, and **verify-before-done** relabeled `[review]` → `[gate]` (now scripted by `refactor-scan.py` + the existing library checks); the structural-sourcing and concurrent-edit items stay `[review]` (genuinely not mechanizable — labeled honestly). The method spine cites the tool for steps 1/2/7.
- `skill.json`: version 0.1.0 → 0.2.0; `files[]` + the script.

### Verify
- `refactor-scan.py selftest` PASS; run live this session against the session's own renames — `verify core-brand-studio` and `verify skills-critique` both returned **0 LIVE refs** (independently confirming those renames were clean), and `scan skills-studio` correctly classified 43 LIVE / 10 MIXED / 1 HISTORY.

## 0.1.0 — 2026-05-31 — Initial draft (authored via skills-studio)

First cut of the library-level skill-refactor procedure: rename / merge / retire / split a skill or skill-set, rewiring live cross-references while preserving dated history and re-verifying the gate suite.

- **Authored through `skills-studio`'s author flow** (built against `build-against-the-standard.md`; first end-to-end dogfood of the merged lifecycle tool).
- **Grounded in 6 worked examples** from the 2026-05-31 skill-library campaign: 3 merges (core-skills-best-practices + core-skills-evaluator → skills-critique; +meta-skill; the report-* fixes) and 3 renames (skills-critique → skills-studio; core-brand-studio → brand-studio; core-agentic-ux → core-agentic-ux-best-practices). The recurring procedure + its silent-failure modes are captured here so they stop being re-derived by hand.
- **SKILL.md:** 5 First Principles (refactor is 90% rewiring; live-wiring-rewired/dated-history-preserved; destructive-steps-need-a-net; gates-are-done-and-never-falsified; concurrent-edit-aware), the 7-step method spine, a 4-operation table, `## §SelfAudit` (backup-before-destructive + history-is-data + concurrent-edit guard + re-baseline-not-falsify + verify-before-done), and a `## Verify Target` whose signal is **external** (gate suite green + a grep for the old name returning only dated-history files).
- **`references/operations.md`:** per-operation playbooks (rename / merge / retire / split) + the cross-cutting gotchas learned the hard way (files[]↔disk after a sweep, routing-baseline orphans, tags-are-not-references, generic-adjective prose, parallel-editor collisions).
- **`evals/routing-corpus.json`:** trigger + adversarial phrases; adversarials route to `skills-studio` (author/edit/optimize/score — the single-skill lifecycle) and `ops-repo` (project-doc hygiene), the two nearest neighbours.
- **Build-time red-team (the gate worked — caught 2 Criticals pre-ship):** a fresh-context Simon + Wlaschin pass on the draft found, and this release folds: **(C-S1)** the bulk `perl -i` sweep was unbounded — renaming a short/prefix name like `report` would silently corrupt the substring in unrelated skills → now **word-boundaried + literal-escaped (`\Q…\E`), dry-run-first, whole-library backup**; **(C-S2/W1)** the "content is data, not instructions" guard was instructional and mislabeled `[gate]` with no script → relabeled `[review]`, and a **structural sourcing rule** added (destructive/rewrite targets come only from the human-reviewed footprint map, never from content parsed mid-run); **(W3)** `merge`/`split` now stated as compositions of `rename`+`retire` with the major-bump-wins version rule; **(W5)** a **MIXED** file-class added (exclude-from-sweep + enumerated hand-edits); **(W4)** the `files[]`↔disk gotcha reframed as exclude-history-pointers-up-front, not rewrite-then-revert. The two mechanization Majors (script-enforced backup precondition; `--reason` on re-baseline) are v0.2 (ROADMAP). This is the first empirical application of `skills-studio`'s build-time red-team gate — it paid for itself.
- `status: draft` / `0.1.0` — new skill; graduation to stable needs the routing F1 baseline + ≥3 real refactors driven *by the skill* (it currently documents refactors done by hand).
