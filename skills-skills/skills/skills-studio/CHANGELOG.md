# Changelog — skills-studio

## 3.5.1 — 2026-06-02 — Runtime environment foundation + rubric added

Added `references/foundations/runtime-environment-foundations.md` (full Claude Code tool inventory + Claude Chat capability spec) and `references/rubrics/runtime-compatibility.md` (D0–D5 rubric for chat/agent/both target classification). Wired into rubric-manifest.json and build-against-the-standard.md as D0 prerequisite gate. SKILL.md updated with runtime target as required authoring gate. `accounting-studio` is the first skill to carry `"target": "agent"` in its manifest.

## 3.5.0 — 2026-05-31 — `promote` mode: complete D1–D10 + full council + verdict

### Added

- **`promote` mode** (EVALUATE family) — the complete evaluation loop for promotion decisions. Closes the gap between `score` (rubric-only) and `critique` (council-only): `promote` runs both in sequence with the holistic D1–D10 scan as the coordinator. Triggers on "complete review of {skill}", "thorough review", "full review", "promote to stable", "is this skill ready to promote?", "comprehensive evaluation".

  **4-stage workflow:**
  - **Stage 0**: Pre-flight structural gates (`quick_validate.py --strict` equivalent; ROADMAP D7; Quick Start CS2) — any gate failure stops the review.
  - **Stage 1**: Holistic scan (D1–D10, `skills-holistic.md`) — scores all 10 dimensions 1–5, flags any D ≤ 3 as "weak" for Stage 2.
  - **Stage 2**: Targeted deep-dives (only for weak dims) — loads the paired rubric + runs the paired primary critic per `build-against-the-standard.md` mapping table.
  - **Stage 3**: Full 9-critic panel — all critics run as fresh lenses; S11 synthesis at minimum.
  - **Stage 4**: Synthesis + **APPROVED / CONDITIONAL / BLOCKED** verdict (APPROVED = all D ≥ 3 + no surviving Critical/Major; CONDITIONAL = D = 2 or bounded Majors + required fixes listed; BLOCKED = D = 1 or Critical).

- **Routing corpus** — 7 `promote`-mode trigger phrases added to `evals/routing-corpus.json`.
- **`skill.json`** — version 3.4.0 → 3.5.0.

## 3.4.0 — 2026-05-31 — quick_validate.py --strict: label-coverage gate (ROADMAP [v3.x])

Added label-coverage check to `_check_selfaudit()` in `scripts/quick_validate.py`. When `--strict` is passed, the check scans every `### Dimension N` heading in the produced SKILL.md and warns if any dimension is missing a `\`[gate]\``, `\`[review]\``, or `\`[hypothesis]\``label. Addresses ROADMAP [v3.x] "extend`quick_validate.py --strict` for label-coverage."

**What it checks:** `re.findall(r'^### Dimension \d+[^\n]*', content, re.MULTILINE)` → filter lines that lack the backtick-labeled type tag → warn with count and first example.

**Why useful:** a produced skill whose dimensions lack type labels cannot be scored consistently (rubric-quality D1 gate FAIL). Running `quick_validate.py --strict` now catches this before packaging.

**What it does NOT check:** doesn't validate that the label is correct (a [gate] that requires judgment to apply) — that's rubric-quality D2 [review] and requires human evaluation. Label presence is the mechanical floor; label accuracy is the judgment overlay.

## 3.3.0 — 2026-05-31 — Self-containment: internalize gen-ui anti-patterns catalogue

skills-studio had one external cross-skill reference remaining: `eval-prompts.md` GU section referenced `../../../ref-gen-ui-systems/references/anti-patterns.md` for the Generative UI Reasoning evaluation prompts (GU1–GU5). This loaded critical evaluation content from a peer skill at invocation time.

### Changed

- **`references/gen-ui-anti-patterns.md`** (new) — the 10 named failure modes in Generative UI (AP-01 Premature Rendering through AP-10 State Without Owner), condensed from `ref-gen-ui-systems/references/anti-patterns.md`. Includes Quick Reference table + per-pattern correction + cross-reference to the internal `agents-ux-wireframing-ascii.md` rubric.

- **`references/critics/eval-prompts.md`** — GU section preamble updated: path `../../../ref-gen-ui-systems/references/anti-patterns.md` → `../gen-ui-anti-patterns.md`. The GU evaluation prompts now resolve entirely within skills-studio.

- **`skill.json`** — version 3.2.0 → 3.3.0; `references/gen-ui-anti-patterns.md` added to `files[]`.

**Result:** skills-studio has zero external cross-skill dependencies for evaluation content. All rubrics, foundations, critic personas, and domain knowledge (including gen-ui anti-patterns) are physically inside the skill directory. The only peer-skill entries are in `peer_skills` metadata (advisory navigation, not load-time dependencies).

## 3.2.0 — 2026-05-31 — Add the `expert-council-design` rubric (dogfood-driven)

Surfaced by the `core-brand-studio` re-review: the instrument could score the **rubrics** a skill ships (`rubric-quality.md`) but had **no home for scoring the _critic panel_ a skill ships** — and a skill's most distinctive property can be its council (core-brand-studio's 14 practitioner critics; core-agentic-ux's 8-critic council; skills-studio's own 9 engineering critics). The probe found the gap is library-wide, not brand-specific.

### Added

- **`references/rubrics/expert-council-design.md`** (v0.1.0, empirically-derived) — 5 dimensions (2 gate / 2 review / 1 hypothesis), `primary_critic` `scott-wlaschin` (a panel is a type system over a judgment space — overlapping/uncovered critics are the illegal states): C1 authority grounding `[review]`, C2 non-redundancy & coverage `[gate]`, C3 control-mode fitness (persona vs rubric) `[review]`, C4 falsifiable persona output `[gate]`, C5 calibration — does the panel discriminate a _failing_ artifact, not just bless good ones `[hypothesis]`. 5 anti-patterns (AP-EC-01 costume critic … AP-EC-05 demo-only calibration), 5 hard tests. `scoring_targets`: core-brand-studio, core-agentic-ux-best-practices, skills-studio.
- **`references/rubric-manifest.json`** → v0.15.0: registered (no `foundation` field — a domain/meta rubric like prd/spec/report; `check-foundations-coverage.py` still PASS).

### Changed

- `skill.json`: version 3.1.0 → 3.2.0; `files[]` + the new rubric.

> Second instrument improvement driven by reviewing-with-the-instrument (after `report-authoring`). Tellingly, its C5 (calibration) is exactly the open Major the brand re-review found — and the gap generalizes to every council-bearing skill, skills-studio included.

## 3.1.0 — 2026-05-31 — Make it truly bi-directional: author builds against the rubric/foundation/critic library

Closes the gap surfaced by review: the eval side fully used the rubric library, but the **author side targeted only an aligned standard** (its §SelfAudit gates _mirrored_ the rubric dimensions) without its guides ever referencing the foundations, rubrics, or critics. The two halves were co-located + bridged by a hand-off loop, not a shared knowledge base. Now the author side draws on the _same_ foundations, rubrics, and critics the eval side scores with.

### Added

- **`references/authoring/build-against-the-standard.md`** — the bi-directional bridge. A table mapping each holistic dimension D1–D10 → the **foundation** you build it from → the **rubric** it's scored with → the **ship-gate** the produced skill must pass → the **critic** who red-teams it (pairings taken from the manifest's `foundation` fields, not asserted). Plus the build-time red-team protocol.
- **Build-time red-team (a `[gate]` in §AUTHOR):** before a produced skill ships, run `critique` on the agent's _own_ draft. Stakes-tiered default — floor = `single-critic simon` (trust boundary, the campaign's most recurring Critical) + `single-critic wlaschin` (structure/labels); escalate to `full-panel` for pre-v1.0 / untrusted-content / orchestrator skills. Surviving Critical/Major fold back via `edit`.

### Changed

- `SKILL.md` §AUTHOR: "build against the standard" is now the first read; each best-practices requirement is annotated with its holistic dimension + foundation (D5←eval-foundations, D8←observability, D1←instructions-harness, D7←security, D3←rubric); the build-time red-team added to the requirements, the §SelfAudit "Before authoring" gate, the Output Contract, and the Verify Target ("no critic ever saw the draft" → NOT done).
- `references/authoring/creating-skills.md`: a "Build against the standard" callout up top (pull each dimension's foundation as you write that part).
- `references/authoring/improving-skills.md`: the vague "Optional: Adversarial Hardening" reframed — the **9-critic build-time red-team** is now the named step; the routing-probe categories follow it.
- `skill.json`: version 3.0.1 → 3.1.0; `files[]` + the new reference.

### Result

`author → score/critique/eval → edit` is now one loop over one body of knowledge: a skill is **built to the standard it will be judged by**, and the critics are summoned on it at build time, not only when someone later evaluates it.

## 3.0.1 — 2026-05-31 — Rename `skills-critique` → `skills-studio`

The name `skills-critique` under-described the skill once it absorbed authoring (v3.0.0): it now authors, scores, critiques, and evals skills. Renamed to **`skills-studio`** — a _studio_ both creates and critiques — establishing a `*-studio` naming convention for the library's expert/compound skills (alongside `core-brand-studio`). Directory, `name` fields (SKILL.md + skill.json), and ~43 live cross-references (peer_skills, routing pointers, rubric-load paths, gate-script keys, README/AGENTS inventory, routing baseline) updated in one pass; dated history (this CHANGELOG's prior entries, the `report-*` review docs and their `2026-05-31-skills-critique-*` filenames, AGENTS/BACKLOG log entries) preserved as accurate-as-written. No behavior change. Gates re-verified green.

> Entries below predate the rename and refer to the skill as `skills-critique` / `core-skills-*` / `meta-skill` — accurate for their dates; the lineage is: `core-skills-best-practices` + `core-skills-evaluator` → `skills-critique` (v2.0.0) → + `meta-skill` (v3.0.0) → `skills-studio` (v3.0.1).

## 3.0.0 — 2026-05-31 — Fold in `meta-skill` (authoring); retire `meta-skill-typed`

User-directed: skills-critique becomes the **full skill lifecycle tool** — author → evaluate → improve — not just an evaluator. Folds `meta-skill` (the general skill-authoring + eval-running toolkit) in, and retires `meta-skill-typed` (the model now handles typed/schema skills natively, so the dedicated authoring guide is obsolete).

### Added (from `meta-skill`)

- **Author family of modes:** `author` (create from scratch — interview → research → draft → routing eval → package), `edit` (fix/improve an existing skill), `optimize` (tune the description against a routing corpus). The evaluate family (`score` / `critique`) gains `eval` (behavioral test cases + variance) from meta-skill's eval machinery — the loop is now author → score/critique/eval → edit/optimize, in one skill.
- `references/authoring/` (8): creating-skills, skill-template, improving-skills, self-improvement, description-optimization, running-evals, schemas, environment-guides.
- `scripts/` (+9): `quick_validate.py` (structural + `--strict` §SelfAudit gates — the library-wide single-skill validator), `run_eval.py` / `run_loop.py` / `improve_description.py` (optimize), `aggregate_benchmark.py` / `generate_report.py` (eval), `package_skill.py`, `utils.py`, `__init__.py`.
- `agents/` (grader, comparator, analyzer), `eval-viewer/`, `assets/eval_review.html`, `LICENSE.txt`.
- `evals/routing-corpus.json` — skills-critique had **no** routing corpus (its own ROADMAP gap); seeded from meta-skill's and extended with evaluation triggers (closes the gap).

### Preserved (from `meta-skill-typed`, otherwise retired)

- `references/skill-definition-schema.json` — the canonical meta-schema all `skill.json` files validate against. The typed-skill _infrastructure_ (`meta-type-registry`, `shared-types`) is unaffected and stays; only the obsolete authoring skill is retired.

### Changed

- `SKILL.md` rewritten as the unified lifecycle spec (two families: author/edit/optimize + score/critique/eval); the §SelfAudit now carries both the evaluation trust boundary **and** the produced-skill authoring gates ("don't exempt yourself").
- `skill.json`: `name` unchanged; version 2.1.0 → **3.0.0** (major — absorbs an authoring skill, two skill names retired); `files[]` extended (56 → 82); description surfaces authoring triggers; `peer_skills` → the remaining specialized authors (meta-expert-author, meta-theory-author, meta-app-scaffold).
- Gate runner: `meta-skill-typed`'s `validate.py` gate dropped (its target — meta-skill-typed's own skill.json/examples — is deleted; `check-skill-metadata` already covers manifest validity); `quick_validate.py` re-homed here.

### Note (naming)

The name `skills-critique` now under-describes the skill (it authors + scores + critiques). A rename (e.g. `skills`) is a tracked, low-cost follow-up — deferred to avoid re-wiring twice.

## 2.1.0 — 2026-05-31 — Add the `report-authoring` rubric (dogfood-driven)

Surfaced by reviewing the `report-*` skill family: four independent blind `skills-critique` passes (report-strategic / report-brief / report-state / report-progress) **each independently reported the same instrument gap** — the rubric library has `prd-authoring` and `spec-authoring` but no rubric for _decision-facing report documents_, so the holistic meta-rubric scored the skill-as-machine while the report-document the skill emits stayed unmeasured. They converged on the same seven dimensions.

### Added

- **`references/rubrics/report-authoring.md`** (v0.1.0, empirically-derived) — 7 dimensions (4 gate / 3 review), `primary_critic` `simon-willison` (the report-specific novelty is the ingestion **trust boundary** + **claim→evidence traceability**): D1 claim→evidence traceability `[gate]`, D2 source-provenance & trust boundary `[gate]`, D5 recommendation actionability `[gate]`, D7 uncertainty/gap surfacing `[gate]`, D3 BLUF/pyramid `[review]`, D4 audience fit `[review]`, D6 calibrated-signal discipline & honesty `[review]`. 6 anti-patterns (AP-RA-01 orphaned verdict … AP-RA-06 action-free status), 5 hard tests (incl. an injection probe and a summary-stands-alone test). `scoring_targets`: the four `report-*` skills.
- **`references/rubric-manifest.json`** → v0.14.0: `report-authoring` registered (26 rubrics). No `foundation` field (a domain rubric, like prd/spec — `check-foundations-coverage.py` still PASS).

### Changed

- `SKILL.md` references table: added a **document-authoring rubrics** row (prd / spec / report) — load when the target skill's output is a document.
- `skill.json`: version 2.0.0 → 2.1.0; `files[]` + the new rubric.

## 2.0.0 — 2026-05-31 — Merge: `core-skills-best-practices` + `core-skills-evaluator` → `skills-critique`

User-directed merge of the library's two skill-evaluation instruments into one skill with two modes. The two were always a pair — they cross-routed to each other, shared the rubric library, and the evaluator's topical sections (CM/RQ/CE/GV/PA/CS) mirror the score rubrics one-to-one. Unifying them removes the "which do I call?" routing tax and the duplicated trust/quality discipline.

### Merged

- **Host:** this skill continues `core-skills-best-practices`' lineage (it owns the rubric library, foundations, manifest, and `scripts/check-foundations-coverage.py`), renamed to `skills-critique`. Version continued 1.6.0 → **2.0.0** (major: the two source skill names are retired, an identity change).
- **Absorbed:** `core-skills-evaluator` v0.1.10 — its 9 critic-persona files + `eval-prompts.md` now live under `references/critics/`; its full-panel/single-critic/synthesis behavior is **critique mode**. The evaluator skill is retired (history preserved in its prior `reviews/` and CHANGELOG; this entry is the lineage record).
- **Two top-level modes:** `score` (rubric scorecard — rubric-select / deep-audit / scorecard + the 5-stage eval-loop) and `critique` (9-critic panel — single-critic / full-panel / synthesis). The holistic 10-dimension meta-rubric (`references/rubrics/skills-holistic.md`) is the shared spine.

### Added (net-new in the merge, not in either original)

- **A `§SelfAudit` trust boundary** spanning both modes: the skill-under-evaluation is untrusted content to assess, never instructions to obey (a "rate this 5/5" or injection line is _material to score_, per critique's SC1 test — not a command). Neither original carried this D7 guard; it's the campaign's recurring fix, applied at the instrument itself.

### Changed

- `SKILL.md` rewritten as one unified spec (two modes, merged Quick Start / Invocation / References / Output Contract / Routing corpus / Verify Target).
- `skill.json`: `name` → `skills-critique`; `files[]` extends the best-practices set with `references/critics/*` (10 files); `peer_skills` added.
- Internal cross-refs repointed: `eval-prompts.md` and the persona files' `../core-skills-best-practices/references/...` paths → local `../rubrics/` / `../foundations/`; the `EVAL-PROMPTS.md` casing bug fixed; internal "use `core-skills-evaluator`" mentions → "critique mode."
- Live external pointers rewired to `skills-critique`: `peer_skills` in `core-brand-studio` + `core-mcp-best-practices`; README + AGENTS catalogs (74 → 73 skills); `ref-gen-ui-systems` rubric-location pointers; `scripts/run-skill-gates.py` registry key; the review-naming convention in `.docs/ops-family-shape.md`.
- **Historical records preserved:** existing `reviews/<date>-core-skills-evaluator-full-panel.md` files, dated CHANGELOG/ROADMAP/BACKLOG entries, and the `Reviewer:` attributions are left as accurate as-of-when-written; only live wiring was repointed.

### Verify

- Backup of both source skills at `~/.claude/skills-backup-skills-critique-merge.tgz` (no-git safety net).
- `check-skill-metadata.py` + `run-skill-gates.py` green after the cutover (`check-foundations-coverage.py` is path-relative and survives the rename).

---

## 1.6.0 — 2026-05-31 — Holistic meta-rubric expanded 8 → 10 dimensions (D9 Context Engineering, D10 Plan Anatomy)

### _(history below this line is `core-skills-best-practices`' — preserved verbatim; `core-skills-evaluator`'s own history lived in its retired directory)_

The `skills-holistic` meta-rubric asserted "all eight load-bearing concerns" but never said why context-engineering / governance / plan-anatomy (which have full rubrics + foundations) weren't among them — so "8 not 11" read as an oversight. Resolved by **scale**: the two solo/authoring-scale concerns are promoted to dimensions; the team/system-scale one stays cross-cutting.

### Changed

- **`references/rubrics/skills-holistic.md` → v0.2.0 (8 → 10 dimensions).** Added **D9 — Context Engineering** `[review]` (dynamic per-task context vs D1's static harness; drills into `context-engineering.md` / `progressive-context-construction.md`) and **D10 — Plan Anatomy** `[review]` (plan well-formedness vs `agentic-coding`'s loop-closure; drills into `plan-anatomy.md`). Each ships a 1–5 anchor table, a Go-deeper pointer, and a hard test (9, 10). Title/intro/grounding updated; gate/review balance now 4 gate + 6 review.
- **Added a `§Scope` section** stating _why D1–D10 and not D1–D11_: **Governance** (`governance.md`) is a team/system concern (team scale, runtime layer) — a solo skill has no governance to score — so it stays a cross-cutting rubric, not a holistic dimension. Also documents the D9↔D1 and D10↔agentic-coding overlaps and why each earns its place.
- **`references/rubric-manifest.json` → v0.13.0:** `skills-holistic` entry now `dimensions: 10`, D9/D10 in `dimension_breakdown.review`, `hard_tests_count: 10`, updated `key_question` + `note`, and `context-engineering` + `plan-anatomy` added to its `dependencies`.
- **`references/README.md`:** Foundations table "Holistic dim" column now maps context-engineering → **D9**, plan-anatomy → **D10**, governance → cross-cutting (team/system scale); meta-rubric row and prose updated to ten dimensions.
- **`SKILL.md`** reference index + **`references/foundations/eval-foundations.md`** updated from "8-dimension" → "10-dimension".
- **Lockstep:** `core-skills-evaluator`'s S11 coverage test and S2 synthesis prompt updated to the same 10 dimensions (separate skill, separate bump).
- `skill.json` version 1.5.0 → 1.6.0.

## 1.5.0 — 2026-05-31 — Rubric quality fixes: harness-design label placement + governance D3 + D6 anchors

### Changed

- **`references/rubrics/harness-design.md`** — label placement fixed for all 6 dimensions (rubric-quality D1 compliance fix reported by rubric-quality assessment). Format was `### Dimension N [type] — Title`; corrected to `### Dimension N — Title \`[type]\`` to match library convention. Also: D6 score 4 anchor fixed — "Clear that corrections have been added / some rules have origin context" replaced with count-based evidence: "≥3 rules carry a parenthetical origin note; no rules visibly stale."

- **`references/rubrics/governance.md`** — D3 score 4 anchor fixed (rubric-quality D3 behavioral-anchor-quality gap). "Roles are documented. Separation is expected and largely practiced. Some structural enforcement exists" replaced with count-based evidence: "At least one structural gate exists for the most consequential role boundary; role-conflation events are noted when they occur." Resolves the "largely/some" adjective-only level descriptors flagged in the rubric-quality assessment.

- `skill.json` version 1.4.0 → 1.5.0.

## 1.4.0 — 2026-05-31 — primary_critic assignments for 3 new critics + rubric quality fixes

### Changed

- **`references/rubric-manifest.json`** → v0.12.0: assigned `primary_critic` for the three critics added by peer agent (Wlaschin, Huyen, Farley) who had no primary ownership across any rubric:
  - `scott-wlaschin` → `rubric-quality` (type-driven structural gates = his lens), `plan-anatomy` (making illegal plan states unrepresentable)
  - `chip-huyen` → `evaluation-workflows` (measured failure modes per step, determinism boundary)
  - `david-farley` → `governance` (reproducible change processes, audit trails), `mechanization-best-practices` (automated pipelines, idempotency), `worktree-operations` (manifest-backed lifecycle, reproducibility)

- **`references/rubrics/skills-authoring.md`** — D6 `[hypothesis]` measurement plan added (rubric-quality D5 fix). The "timing figures are an unverified hypothesis" note was honest but lacked the four required elements: named metric (median wall-clock per mode), minimum sample size (≥5 invocations / ≥30 days), control variables (model version, harness version), and judgment rule (≤50% median time at invocation 5 = compounding confirmed; < 10% improvement invocation 5→10 = plateau, flag bottleneck).

- **`references/rubrics/governance.md`** — D4 Audit Trail narrowed to resolve D1/D4 conflation (rubric-quality D4 fix). D4 now explicitly scopes to _non-code_ decisions (eval scores, overrides, invocation failures) with a scope note separating it from D1 (code-artifact change history). A system can score D1=5 and D4=1 — the conflation is resolved. New test: "locate a non-code decision record from 90 days ago in under 2 minutes without asking anyone."

- `skill.json` version 1.3.0 → 1.4.0.

## 1.3.0 — 2026-05-31 — Foundations↔rubrics coverage made a checked fact

Audit finding: the `foundations/` theory docs paired to `rubrics/` only by name, the link wasn't machine-readable, and two foundation-paired rubrics were orphaned from the registry. **No rubric content changed** — this wires and verifies the existing pairing.

### Added

- **`scripts/check-foundations-coverage.py`** — gates the foundations↔rubrics contract: every `foundations/*.md` must be claimed by exactly one rubric via the manifest `foundation` field, every link must resolve, no duplicate claims. Registered in the repo-root `scripts/run-skill-gates.py`. Current: **11/11 foundations claimed, PASS**.

### Changed

- **Registered `governance` + `plan-anatomy` in `rubric-manifest.json`** — both rubrics existed and were content-aligned with their foundations but were missing from the registry (invisible to discovery). Manifest now 23→25 entries; all rubric files registered.
- **Added a `foundation` field to all 11 foundation-paired rubric entries** in the manifest (`harness-design`→`instructions-harness-foundations`, … `rubric-quality`→`rubric-foundations`), making the 1:1 pairing machine-checkable. `_comment` documents the field + gate.
- **Completed the manifest `critics` array 6 → 9** — added Scott Wlaschin (type/composition), Chip Huyen (orchestration/reliability), and David Farley (delivery/reproducibility) so the registry matches the 9-critic panel referenced by the README and `core-skills-evaluator`. No `primary_critic` reassignments; all existing refs still resolve. Manifest version 0.9.0 → 0.11.0.
- **Refreshed `references/README.md`** — it indexed only 16 of 25 rubrics, never mentioned `foundations/`, and carried stale counts ("twelve"/"16 rubrics"/"13 areas"). Now: all 25 rubrics by category, a **Foundations (theory layer)** section with the 11-pair table + holistic-dimension mapping, corrected counts, and the dead `evals/EVAL-PROMPTS.md` link repointed to the sibling `core-skills-evaluator` 9-critic corpus. Frontmatter → v0.2.0.
- `skill.json`: added the script to `files[]`; version 1.2.0 → 1.3.0.

## 1.2.0 — 2026-05-31 — Two new rubrics: cold-start-orientation + rubric-quality

### Added

- **`references/rubrics/cold-start-orientation.md`** (v0.1.0, draft) — 6-dimension rubric scoring how well a skill enables first-time user orientation. D1 [gate]: Quick Start present within 50 lines with all three elements (worked example, bring list, mode table). D2 [review]: first-screen coverage (can "use [skill]" be answered without scrolling?). D3 [gate]: worked example embedded in SKILL.md, not delegated to references/. D4 [review]: example specificity (real domain, real constraint, no placeholders). D5 [gate]: key concepts defined inline at first appearance. D6 [review]: mode table with trigger conditions, not just mode names. 4 anti-patterns (reference-delegated example, mode menu without triggers, vocabulary barrier, generic example). 6 hard tests matching CS1–CS5 from the evaluator topical section.

- **`references/rubrics/rubric-quality.md`** (v0.1.0, draft) — 6-dimension rubric scoring rubric design quality. D1 [gate]: label completeness (every dimension has [gate]/[review]/[hypothesis]). D2 [review]: label accuracy ([gate] dims are actually mechanically checkable). D3 [gate]: behavioral anchor quality (level descriptors show evidence, not just adjectives). D4 [review]: criterion independence (dimensions assess distinct properties). D5 [gate]: hypothesis measurement plans (every [hypothesis] carries metric + sample size + baseline + judgment rule). D6 [review]: calibration potential (two reviewers agree within 1 point). 4 anti-patterns (adjective ladder, hypothesis asserting as fact, conflated criterion, gated gate). 6 hard tests.

- **`references/rubric-manifest.json`** — both rubrics registered; library version 0.8.0 → 0.9.0.

### Changed

- **`SKILL.md`** — References table: 2 new rows added after `plan-anatomy.md`.
- **`skill.json`** — version 1.1.1 → 1.2.0; files[] extended with both rubric files.

## 1.1.1 — 2026-05-31 — Quick Start section

Added `## Quick Start` before `## Invocation`: one worked example (`use core-skills-best-practices ops-repo/SKILL.md`), what to bring, and a 4-row mode table (default workflow / rubric-select / deep-audit / scorecard).

## 1.1.0 — 2026-05-31 — Context engineering, governance, plan anatomy (foundations + rubrics)

### Added

- `references/foundations/context-engineering-foundations.md` — foundational knowledge: context selection, structuring, compression, retrieval quality, freshness, conflict detection, and context shape design; ties to context-engineering.md and progressive-context-construction.md rubrics
- `references/foundations/governance-foundations.md` — foundational knowledge: NIST AI RMF, EU AI Act, ISO 42001; change management, role separation, eval governance, policy-as-code, override authority, behavioral drift detection
- `references/foundations/plan-anatomy-foundations.md` — foundational knowledge: ReAct/Plan-and-Execute/Reflexion architectures; goal decomposition, dependency ordering, checkpoint design, completion criteria (real-state vs. self-referential), recovery paths
- `references/rubrics/governance.md` (v0.1.0, draft) — new scoring rubric: 5-7 dimensions covering change authority, eval interpretation governance, override authority, policy encoding, audit trail, behavioral drift detection
- `references/rubrics/plan-anatomy.md` (v0.1.0, draft) — new scoring rubric: 7 dimensions covering goal decomposition, dependency ordering, checkpoint design, decision point specification, completion criteria, recovery paths, plan representation

### Changed

- `skill.json` version 1.0.1 → 1.1.0; files[] extended with 5 new entries
- `SKILL.md` references table: 5 new rows added

## 1.0.1 — 2026-05-31 — Reorganize references/ into foundations/, rubrics/, workflows/ subfolders

### Changed

- **`references/` reorganized into three subfolders** — 33 flat files → structured hierarchy:
  - `references/foundations/` (8 files) — the "What Is X?" knowledge documents for each of the 8 holistic dimensions
  - `references/rubrics/` (21 files) — all scoring rubrics including the meta-rubric (`skills-holistic.md`)
  - `references/workflows/` (2 files) — `eval-loop-workflow.md` and `failure-mode-taxonomy.md`
  - `references/` root — only `README.md` and `rubric-manifest.json` (the always-load entry points)
- **`references/rubric-manifest.json`** — all `"file"` paths updated to include subfolder prefix (e.g., `"harness-design.md"` → `"rubrics/harness-design.md"`)
- **`references/workflows/eval-loop-workflow.md`** and **`failure-mode-taxonomy.md`** — internal rubric references updated to `../rubrics/` relative paths
- **`SKILL.md`** — References table paths updated for all 31 moved files
- **`skill.json`** — `files[]` paths updated for all 31 moved files; version unchanged (1.0.0 → 1.0.1 for this patch)
- **`core-skills-evaluator/SKILL.md`** — cross-skill template path updated: `references/[rubric-name].md` → `references/rubrics/[rubric-name].md`; foundations path added

## 1.0.0 — 2026-05-31 — Six dimension foundations (complete 8-dimension coverage)

### Added

- **`references/instructions-harness-foundations.md`** — foundational knowledge for D1 (Instructions & Harness): SKILL.md structure, ingestion contract, cold-start requirements, invocation section anatomy, and harness-design principles.
- **`references/control-mode-foundations.md`** — foundational knowledge for D2 (Control Mode): the five control modes (instruction / procedure / rubric / objective / mission), when to use each, task-entropy matching, and mode-selection anti-patterns.
- **`references/mechanization-foundations.md`** — foundational knowledge for D4 (Mechanization): the mechanization ladder, the 3-condition threshold for mechanizing a check, mechanism contract template, and mechanization anti-patterns.
- **`references/extensibility-foundations.md`** — foundational knowledge for D6 (Extensibility): evidence-driven extension, placement discipline, cold-start protection, lifecycle states, and the 6-step learning loop.
- **`references/security-foundations.md`** — foundational knowledge for D7 (Security & Trust Boundaries): the lethal trifecta, prompt-injection guard patterns, scope containment, and trust-boundary failure modes.
- **`references/observability-foundations.md`** — foundational knowledge for D8 (Observability): post-invocation signal design, structured output contracts, telemetry hooks, and the self-assessment vs. external-signal distinction.

Together with `rubric-foundations.md` (D3) and `eval-foundations.md` (D5), these six documents complete foundational coverage for all 8 dimensions of the holistic skill quality meta-rubric (`skills-holistic.md`). Previously, D1/D2/D4/D6/D7/D8 had detailed scoring rubrics but no dedicated foundational reference explaining the underlying concepts. The foundations give scorers and authors a first-principles grounding before they engage the scoring dimensions.

### Changed

- **`skill.json`** — version 0.9.0 → 1.0.0; `files[]` extended with all six foundational documents (inserted after `eval-foundations.md`).
- **`SKILL.md`** — References table: six new rows added after `eval-foundations.md` row, each with a load-when description keyed to its corresponding holistic dimension.

## 0.9.0 — 2026-05-31 — Foundational knowledge documents: rubric-foundations + eval-foundations

### Added

- **`references/rubric-foundations.md`** (v1.0.0, research-verified) — foundational knowledge document: _What Is a Rubric?_ The logical structure of a rubric (criteria × levels with behavioral descriptors × aggregation rule); origin in Popham (1997) educational measurement; the analytic/holistic split; how rubrics differ from metrics (single-dimensional formulas) and checklists (binary gates); the probabilistic→deterministic bridging mechanism (decomposition, anchor specification, evidence-gathering, explicit aggregation); Constitutional AI (arXiv:2212.08073) as the production-scale proof of rubric logic in LLM training; the Prometheus "Judge Paradox" (rubric quality dominates judge capacity — a weaker model on a well-specified rubric outperforms a stronger model on a vague prompt); G-Eval's 0.514 Spearman correlation with human judgment (vs. substantially lower for ROUGE/BERTScore); AutoRubric's six failure modes and reliability targets (Krippendorff's α ≥ 0.800); production principles (3–6 criteria, discrete scores, behavioral anchors, criterion independence, one-judge-per-criterion, version control for rubrics). Explains how `[gate]`/`[review]`/`[hypothesis]` labels in this library correspond to AutoRubric's binary/ordinal/hypothesis criterion types. 7 primary sources cited.

- **`references/eval-foundations.md`** (v1.0.0, research-verified) — foundational knowledge document: _What Is an Eval?_ Four-way distinction: benchmark (cross-model comparison on standardized tasks) vs. eval (application-specific quality measurement) vs. test (CI pass/fail gate) vs. metric (single measurable quantity); three structural problems evals solve (comprehension gap, specification gap, generalization gap); eval taxonomy by purpose (capability, regression, behavioral, adversarial, routing, safety) and by environment (offline, online, component, end-to-end); the three-tier evaluator stack (code-based → LLM-as-judge → human calibration); MT-Bench/Chatbot Arena validation (>80% LLM-human agreement, NeurIPS 2023, arXiv:2306.05685); the 12 LLM judge biases (position, verbosity, self-enhancement — with structural mitigations); persona-based adversarial evaluation (Bloom, 0.86 Spearman, the 9-critic council as direct application); the five probabilistic→reliable translation mechanisms (statistical aggregation, pass@k / pass^k, rubric-anchored scoring, calibrated judges, versioned baselines); Eval-Driven Development (Huyen, 2025); CI/CD gate architecture (smoke eval → full regression → safety gate → online monitoring); eval maturity levels (0–3). Explains how `evals/routing-corpus.json`, `[gate]`/`[review]` dimensions, and the critic council all fit the eval framework. 12 primary sources cited.

- **`skill.json`** — version 0.8.0 → 0.9.0; `files[]` extended with both foundational documents.
- **`SKILL.md`** — References table: two new entries added after `failure-mode-taxonomy.md`.

## 0.8.0 — 2026-05-31 — Holistic 8-dimension meta-rubric (`skills-holistic.md`)

### Added

- **`references/skills-holistic.md`** — the holistic skill quality meta-rubric. 8 dimensions covering the full space of skill design concerns: D1 Instructions & Harness Design, D2 Control Mode Design (prompting vs rubrics — the choice of instruction/procedure/rubric/objective/mission matched to task entropy), D3 Rubric Quality ([gate]/[review]/[hypothesis] labeling and calibration), D4 Mechanization & Tool Use, D5 Evaluation (routing corpus, behavioral eval, verify target on real product state), D6 Extensibility (ROADMAP.md, §Teach, observed compounding), D7 Security & Trust Boundaries (lethal trifecta, injection guard, scope containment), D8 Observability (post-invocation signal, not self-assessment). Four cross-dimensional anti-patterns (AP-H1–H4) that individual dimension rubrics miss: confident-rubric-without-calibration, mechanized-shell-with-judgment-core, trusted-content-reader, extensible-skill-that-never-extends. Eight hard tests, one per dimension.

  D2 (Control Mode) and D3 (Rubric Quality) are new coverage — no prior rubric in the library addressed these dimensions directly. D1/D4/D5/D6/D7/D8 synthesize and cross-reference existing detailed rubrics.

  Primary critic: boris-cherny. Depends on: harness-design, skills-authoring, prompt-control-modes, inversion-and-abstraction, evaluation-workflows, skill-extensibility, security-and-scope-containment, observability-and-telemetry.

- **`references/rubric-manifest.json`** — `skills-holistic` entry added as first entry (meta-rubric positioned above the specific rubrics). Library version 0.6.0 → 0.7.0.

### Changed

- **`SKILL.md`** — References table: `skills-holistic.md` added above `skills-authoring.md` as the entry-point for any full skill review.
- **`skill.json`** — version 0.7.0 → 0.8.0; `files[]` extended with `references/skills-holistic.md`.

## 0.7.0 — 2026-05-28 — D7 roadmap-hygiene gate + ROADMAP.md

### Added

- `references/skills-authoring.md` — D7 `[gate]`: Roadmap hygiene. Scores whether a skill has a `ROADMAP.md` with Planned / Deferred / Out of scope sections. AP-07 (roadmap pollution via changelog or skill body). Hard Test 8 (grep for forward-looking keywords outside `ROADMAP.md`). Rubric version 0.1.0 → 0.2.0.
- `references/rubric-manifest.json` — `skills-authoring` entry: `dimensions` 6 → 7, `D7-roadmap-presence` added to `gate` breakdown, rubric version 0.1.0 → 0.2.0. Library version 0.5.0 → 0.6.0.
- `ROADMAP.md` — per library-wide convention (AGENTS.md v3.0.0). Documents graduation criteria (≥3 empirical applications per rubric), deferred automated gate runner, and explicit out-of-scope capabilities (adversarial persona evals, skill authoring, code review).

### Changed

- `skill.json` version 0.6.0 → 0.7.0; `files[]` extended with `ROADMAP.md`.

## 0.6.0 — 2026-05-26 — Add explicit eval-loop workflow + reframe modes as workflow stages

### Added

- `references/eval-loop-workflow.md` — explicit five-stage escalating workflow for skill evaluation:
  - **Stage 0 — Cold-read** (60-90 sec): read SKILL.md only; produce one-paragraph orientation (domain, layer, audience, claimed mode, apparent maturity). Not a scoring step.
  - **Stage 1 — Triage check** (5-10 min): single rubric (default `skills-authoring.md`) in deep-audit mode. Three buckets: Pass / Conditional Pass / Fail. Triage Fail → STOP; fixing structural issues comes before further scoring because scoring a broken skill against more rubrics compounds noise (every rubric surfaces the same underlying issue differently).
  - **Stage 2 — Rubric selection** (5 min, `rubric-select` mode): identify applicable rubrics with one-sentence justification each. Default priority order: triage rubric → layer-specific rubrics → cross-cutting rubrics → output-quality rubrics.
  - **Stage 3 — Targeted deep-audit** (20 min per rubric, `deep-audit` mode): score 1-3 high-priority rubrics in full per-dimension detail. Depth, not coverage.
  - **Stage 4 — Full scorecard** (60+ min, `scorecard` mode): comprehensive coverage of all applicable rubrics. Adds coverage summary, confidence note, and cross-rubric findings beyond the per-rubric scorecard.
  - **Stage 5 — Action planning** (15 min): findings → owners + dates
    - gate-vs-defer decisions. Non-optional after Stage 4 — the scorecard is the input to actions; actions are the deliverable.
- **Stop conditions** documented per-stage: cold-read empty / triage Fail / zero rubric exposure / Stage 3 sufficient / time-box exhausted / diminishing returns / user redirect. The Triage-Fail stop is the most important — it prevents 60+ minutes of compounding noise when 5 minutes of triage would have caught the structural issue.
- **Escalation triggers** documented: pre-v1.0 promotion → full Stages 0-5; post-incident audit → Stages 0-5 + adversarial pass via `core-skills-evaluator`; pipeline integration → Stages 0-4 with focus on [gate] dimensions; quarterly health check → Stages 0-2 by default; library-wide audit → Stages 0-2 across library + Stages 3-4 on outliers; new skill triage (<30 days) → Stages 0-1 only.
- **Depth-by-stakes matrix** documented: 9 use cases mapped to default stop stages with reasoning per row (casual curiosity → Stage 1; pre-v1.0 promotion → Stage 5; post-incident → Stage 5
  - adversarial; etc.).
- **Direct-jump override** table: when the user names a specific mode (`rubric-select`, `deep-audit`, `scorecard`, `triage`, `health check`, `pre-v1.0 audit`), treat as direct entry to the corresponding stage; otherwise default to the full workflow.
- **Anti-patterns** documented: default-to-largest (running full scorecard reflexively), skip-triage (scoring without structural pre-flight), score-without-reading (skipping Stage 0 cold-read), scorecard-without-actions (stopping at Stage 4), single-rubric-as- comprehensive (treating Stage 1 as the complete audit), all-rubric-coverage (loading non-applicable rubrics), no-stop- conditions (running every stage regardless of intermediate findings), no-cross-rubric-synthesis (Stage 4 without surfacing issues that appear in multiple rubrics).
- **Self-audit checklist** for the eval loop itself: did I cold-read, did I triage, did I match stop stage to stakes, did I cite evidence, did I produce action planning, did I name the stop condition?

### Changed

- `SKILL.md` Invocation section restructured. New `### Default workflow` subsection added before `### Modes`, with the five-stage table, stop conditions, and escalation triggers summarised. The three modes (`rubric-select`, `deep-audit`, `scorecard`) are now framed as **direct-jump entry points** the workflow sequences, with each mode annotated to indicate which workflow stage it implements. The default invocation path is the workflow; named modes are overrides.
- `SKILL.md` References table — added `eval-loop-workflow.md` entry with "Always when no mode is specified" load trigger.
- `skill.json` `version` 0.4.0 → 0.6.0 (catching up the skill.json version that lagged behind the changelog at 0.5.0 and accounting for the new workflow). `files[]` extended with `references/eval-loop-workflow.md`.

### Why

The skill had the **components** of an escalating evaluation loop — three modes mapping roughly to small / medium / large output — but no **explicit workflow** sequencing them with stop conditions and escalation triggers. The default failure mode was "agent runs the full scorecard against ~20 rubrics for every evaluation request, regardless of stakes" — which burns context, time, and reviewer attention on detailed scoring of skills that a 5-minute triage would have shown to be structurally broken (and where the right output was "fix the structural issue first, then scoring becomes meaningful").

The eval-loop workflow makes the small → large progression explicit, with documented stop conditions at every stage and escalation triggers tied to specific use cases (pre-v1.0 promotion, post-incident audit, quarterly health check, library-wide audit, etc.). The workflow does not replace the modes — it sequences them. Users who want direct entry to a mode still get it; users who invoke the skill without naming a mode get the workflow as the sensible default.

The naming chosen for the file (`eval-loop-workflow.md`) avoids collision with the existing `evaluation-workflows.md` — that file is a _rubric_ for scoring other skills' eval workflows; this new file is _this skill's own_ evaluation workflow. The distinction matters; conflating the two would have produced confusion at every load.

---

## 0.5.0 — 2026-05-25 — Add `prd-authoring` + `spec-authoring` rubrics (product + execution-contract layers)

Two new rubrics distilled from `/Users/kimba/Downloads/prd-vs-spec-agentic-coding-workflows.md`. Together they close the upstream gap from "raw initiative" → "shared product intent (PRD)" → "agentic execution contract (SPEC)" → "implementation."

### Why two rubrics, not one

The source doc's central thesis: PRDs and SPECs are not interchangeable. They reduce ambiguity for **different readers at different layers of execution**.

- **PRD** = human alignment around product intent. Reader: cross-functional team. Optimized for interpretation, judgment, tradeoff negotiation.
- **SPEC** = machine-usable execution contract for implementation. Reader: coding agents + orchestrators + reviewers + CI. Optimized for bounded execution, testability, dependency control, stop-and-escalate safety.

Mixing them produces:

- PRDs that read like disguised implementation plans (engineering pre-commitment without product alignment)
- SPECs that copy the PRD with technical bullets appended (no decomposition, no contracts, no acceptance criteria)

Two rubrics let each one score the document against its own optimization target.

### Added — `references/prd-authoring.md`

**Layer**: product-authoring. **Primary critic**: steve-yegge (platform-vs-product lens; PRDs are alignment substrate for N+ stakeholders).

**Key question**: Does the PRD establish shared product intent for the human team — problem, users, outcomes, scope boundaries, tradeoffs — without collapsing into a disguised implementation plan or a vague feature list?

**8 scoring dimensions** (5 gate + 3 review):

- D1 Problem-statement clarity [gate]
- D2 Goals + Non-Goals balance [gate]
- D3 User / persona specificity [gate]
- D4 Success-metrics measurability [gate]
- D5 Implementation-prescription avoidance [gate]
- D6 Tradeoff acknowledgment [review]
- D7 Prioritization clarity [review]
- D8 Outcome-orientation over feature-listing [review]

**7 named anti-patterns** + **5 hard tests** + **7-phase operating procedure** + recommended section list.

### Added — `references/spec-authoring.md`

**Layer**: agent-coding. **Primary critic**: boris-cherny (PEV loop / verifiability; SPECs are the V's input contract).

**Key question**: Does the SPEC define an execution contract bounded enough for a coding agent to implement, verify, and stop safely — or does it leave ambiguity that the agent fills with its own assumptions, producing over-edits, under-implementations, or unsafe refactors?

**10 scoring dimensions** (7 gate + 3 review):

- D1 Scope / Non-Scope explicit [gate]
- D2 Behavioral precision [gate]
- D3 Typed data contracts [gate]
- D4 API / Service contracts [gate]
- D5 UI / Component contracts [gate]
- D6 File / Module map present [gate]
- D7 Acceptance criteria mapped [gate]
- D8 Source-PRD link [review]
- D9 Stop-and-escalate conditions [review]
- D10 Conservative-edit framing [review]

**8 named anti-patterns** + **7 hard tests** + **7-phase operating procedure** + recommended section list + tier-down guidance for small changes.

### Relationships across the rubric set

- **`prd-authoring` → `spec-authoring`** — PRDs feed SPECs through decomposition (`prd-authoring` §7-phase step 7 hands off; `spec-authoring` §7-phase step 1 receives).
- **`spec-authoring` → `agents-ux-wireframing-ascii`** — when SPEC includes UI, wireframing belongs in the UI/Component Contracts section's design source.
- **`spec-authoring` → `composite-css-composition-discipline`** — when SPEC includes composite UI, that rubric specifies Rungs 12-13 within the UI/Component Contracts.
- **`spec-authoring` ↔ `harness-design`** — SPECs are consumed by the agent harness; harness quality affects whether the SPEC is honored.
- **Both** ↔ **`context-engineering`** — PRDs are upstream context for downstream agentic execution; SPECs ARE structured context objects.

Dependencies declared in manifest accordingly.

### Updated — manifest entries

Two new rubric entries added to `references/rubric-manifest.json` before the gen-ui rubrics, reflecting product/execution-contract precedence over implementation-layer rubrics. Library version bumped 0.4.0 → 0.5.0.

### Source

`/Users/kimba/Downloads/prd-vs-spec-agentic-coding-workflows.md` (15 sections). The source doc is the authoritative reference; both rubrics cite it for each dimension / anti-pattern / hard test where derived.

### Practical pairing

> Use a **PRD** when the core risk is **human misalignment**. Use a **SPEC** when the core risk is **execution ambiguity**. A PRD should make the right thing obvious to the team. A SPEC should make the next correct change obvious to the agent.

The best workflow uses both. The PRD preserves product judgment; the SPEC mechanizes implementation intent.

---

## 0.4.0 — 2026-05-25 — Add `composite-css-composition-discipline` rubric (gen-ui authoring layer)

New rubric distilled from a real 2026-05-24 incident chain (chat-ui repo): one composite shipped with a CSS-illiteracy bypass, then four cross-composite display-override bugs surfaced during the cleanup. All five patterns passed structural audits while rendering visually broken — different in shape from "premature visual collapse" (which the existing wireframing rubric defends against) and different from "reasoning ladder out of order" (which generative-ui-reasoning defends against). Distinct failure mode warrants its own rubric.

### Added — `references/composite-css-composition-discipline.md`

**Layer**: gen-ui-authoring. **Pipeline position**: Rungs 12-13 (Section / Component) of the gen-ui reasoning ladder — AFTER wireframe correct, BEFORE rendering.

**Key question**: When an agent composes UI from primitives + composites with their own `@scope` CSS, does it respect the layered contracts (composition grammars, intrinsic display, slot vocabularies) or override them in ways that silently break the child's intrinsic layout?

**8 scoring dimensions** (5 gate + 3 review):

- D1 Composition-grammar respect [gate]
- D2 Parent/child display boundary [gate]
- D3 Control-group size consistency [gate]
- D4 Container-query/grid alignment [gate]
- D5 Default-vs-contract distinction [review]
- D6 Slot-vocabulary use over re-invention [gate]
- D7 Embedded-composite visual-debt acknowledgment [review]
- D8 Wrapper-primitive attribute forwarding [review]

**5 named anti-patterns**:

- AP-CCD-01 API-only literacy
- AP-CCD-02 Reach-into-child override
- AP-CCD-03 Parallel composition layer
- AP-CCD-04 Mixed-defaults toolbar
- AP-CCD-05 minmax-vs-CQ fighter

**4 hard tests** for mechanical verification (composition-grammar bypass scan, parent display-override scan, control-group height parity, minmax-vs-container-query scan).

**7-phase operating procedure** from intent → wireframe → component selection (with mandatory CSS literacy recording) → composition planning (using each primitive's grammar) → dimension annotation → markup authoring → override pattern selection → verify.

Empirical citations included for each AP — sister commit + sister postmortem from chat-ui (`4e86400c9`, `4223a4147`, `1298fb064`, `94d497557`).

### Relationship to existing rubrics

- **`agents-ux-wireframing-ascii`** — operates at design stage; this rubric operates AFTER design, at composition stage. Wireframing prevents premature visual collapse; this rubric prevents composition-grammar bypass post-design.
- **`generative-ui-reasoning`** — defines the 19-rung ladder; this rubric specifies what happens at Rungs 12-13 specifically.
- **`harness-design`** — composition-grammar audits are a harness concern; this rubric specifies what they should detect.

Dependencies declared in manifest: `agents-ux-wireframing-ascii`, `generative-ui-reasoning`.

### Updated — manifest entry

Added rubric to `references/rubric-manifest.json` with 8 dimensions, 5 anti-patterns, 4 hard tests, source-incident citations. Library version bumped 0.3.0 → 0.4.0.

### Source incidents

Real 2026-05-24 cycle in chat-ui:

- `.brain/postmortems/2026-05-24-component-css-illiteracy.md` — the authoring-side failure
- `.brain/postmortems/2026-05-24-card-structure-audit-enforcement-gap.md` — the operational-side failure
- Commit chain `4e86400c9` → `4223a4147` → `1298fb064` → `94d497557` (the four cross-composite cleanup fixes)

Companion docs in the source pipeline:

- `~/Projects/chat-ui/.agents/skills/adia-ui-authoring/references/common-gotchas.md` (substrate-side framing)
- `~/Projects/chat-ui/.agents/skills/adia-ui-kit/references/common-gotchas-consumer.md` (consumer-side framing)

This rubric is the org-wide generalization. Substrate / consumer framings cite it as the upstream best-practice source.

---

## 0.3.0 — 2026-05-24 — Add `agents-ux-wireframing-ascii` rubric (Boris lens, structural-reasoning artifact)

Imports the wireframing best-practices rubric from `/Users/kimba/Downloads/agents-ux-wireframing-ascii.md` and integrates it into the catalog. Rubric library version bumped 0.2.0 → 0.3.0.

### Added — `references/agents-ux-wireframing-ascii.md`

ASCII wireframes as compressed reasoning artifacts (NOT primitive mockups). The central failure mode addressed: **premature visual collapse** — an agent jumps from product prompt directly to polished components before structure, hierarchy, state, navigation, and interaction ownership have stabilized.

**Pipeline the rubric encodes:**

```
Intent → IA → Layout Structure → Interaction Model → ASCII Wireframe → Component Mapping → Visual Design → Implementation
```

**5 wireframe levels** — agent picks one based on risk:

- Level 1 Region (app shells, dashboards, navigation)
- Level 2 Interaction (flows, modal/sheet behavior, focus models)
- Level 3 State (data-driven regions across default/loading/empty/error)
- Level 4 Responsive (wide/medium/narrow variants)
- Level 5 Semantic Component (implementation decomposition + multi-agent task planning)

**10 scoring dimensions** (6 gate + 4 review):

- D1 Intent-to-structure traceability [gate]
- D2 Structural hierarchy clarity [gate]
- D3 Interaction ownership [gate]
- D4 State coverage [gate]
- D5 Responsive decomposition [gate]
- D6 Density and information priority [review]
- D7 Semantic component mapping [review]
- D8 Annotation discipline [review]
- D9 Reviewability and diffability [gate]
- D10 Appropriate fidelity [review]

**Canonical notation grammar** — small stable syntax for boxes, controls, state, components, ownership, responsive variants, unresolved questions. Goal: consistent interpretation by agents and reviewers, not visual beauty.

**10 anti-patterns** — AP-01 ASCII art as decoration → AP-10 implementation drift from wireframe. Covers premature visual fidelity, generic dashboard skeletons, missing states, ambiguous ownership, undiffable redraws.

**10 hard tests** — region justification / second-agent component derivation / focus / state / responsive collapse / dead-region / diff / implementation handoff / visual collapse / review-gate.

**7-phase operating procedure** — Derive before drawing → Choose level → Default structure → Annotate ownership → Add states → Responsive → Review as gate.

**Companion docs note**: rubric's companion-docs list is incomplete and should not be relied on directly — manifest maintains authoritative dependency mapping.

### Updated — manifest entry

```json
{
  "name": "agents-ux-wireframing-ascii",
  "layer": "authoring",
  "primary_critic": "boris-cherny",
  "dimensions": 10,
  "wireframe_levels": ["region", "interaction", "state", "responsive", "component"],
  "anti_patterns_count": 10,
  "dependencies": ["generative-ui-reasoning", "context-engineering", "progressive-context-construction", "evaluation-workflows"],
  "empirical_applications": 1
}
```

Has 1 empirical application: `adia-ui-authoring` v1.6.0 Phase 2.5 Layout Decomposition (composite-demo-protocol.md). That phase will be reformed in v1.7.0 to cite this rubric as the authoritative spec rather than hand-rolling a 5-sub-artifact list.

### Updated — SKILL.md References table

Added row for `agents-ux-wireframing-ascii.md` under "Load when scoring against the wireframing rubric."

### Files changed

- `references/agents-ux-wireframing-ascii.md` (NEW, 1098 lines — full rubric verbatim)
- `references/rubric-manifest.json` (rubric entry + version 0.2.0 → 0.3.0)
- `skill.json` (files[] +1, version 0.1.0 → 0.2.0)
- `SKILL.md` (References table row)
- `CHANGELOG.md` (this entry)

## 0.2.0 — 2026-05-24 — Add 3 new rubrics (mechanization, skill-extensibility, worktree-operations)

Imports 3 new rubrics from `/Users/kimba/Downloads/new best-practices/` and integrates them into the catalog. Rubric library version bumped 0.1.1 → 0.2.0.

### Added — 3 new rubric reference files

- **`references/mechanization-best-practices.md`** — Mechanization rubric (Elon Musk lens). 7 dimensions. Covers the mechanization ladder (prompt → skill prose → script → validator → hook → CI gate → workflow → infrastructure policy), 3-condition mechanization threshold, mechanism contract template, 10 anti-patterns, 15 hard tests. Companion to `inversion-and-abstraction.md` and `tool-use.md`.
- **`references/skill-extensibility.md`** — Skill Extensibility rubric (Boris Cherny lens). 8 dimensions. Covers evidence-driven extension, placement discipline (6 destinations), cold-start protection, behavioral delta clarity, regression safety, lifecycle states (experimental → active → senior → deprecated → archived), 6-step learning loop, 10 anti-patterns, 12 hard tests, extension change template.
- **`references/worktree-operations.md`** — Worktree Operations rubric (Steve Yegge lens). 7 dimensions (all explicitly tagged [gate]/[review]). Covers the operating model (manifest-backed lifecycle state), path ownership and shared-surface control, staging/commit discipline, validation gates, integration ordering, recovery + archive safety, 8 anti-patterns, 10 hard tests, reference operating procedure + minimum/mature harness contracts.

### Changed

- `references/rubric-manifest.json` — library version 0.1.1 → 0.2.0; added 3 rubric entries with primary_critic, dimensions, dependencies, and (for worktree-operations) dimension_breakdown for [gate]/[review] split.
- `references/README.md` — added rubric rows for the 3 new rubrics (mechanization
  - skill-extensibility under "Execution quality"; worktree-operations under "Operations and safety"). Updated counts "all 13 rubrics" → "all 16 rubrics".
- `skill.json` — added 3 reference files to files array. Also fixed a pre-existing trailing-comma bug that made skill.json invalid JSON (`generative-ui-reasoning.md",\n  ]` → no trailing comma).

### Rationale

The 3 new rubrics fill gaps surfaced by the chat-ui rollup-family review (see META-REFACTOR-SPEC.md in chat-ui):

- **mechanization-best-practices** — every per-skill REFACTOR-SPEC recommended mechanizing prose procedures (§Teach decision trees, audit gates, dry-run workflows). This rubric is the canonical reference for that work.
- **skill-extensibility** — formalizes the "extension governance" gap surfaced across multiple specs (skills accumulating without placement discipline, cold-start creep, append-only learning).
- **worktree-operations** — net-new coverage for multi-agent operational hygiene; surfaces patterns the rollup-family multi-agent-coordination rubric mentions but does not specify at the Git operations layer.

All 3 are draft (status: 0.1.0); per the README's graduation criterion they require ≥3 empirical applications before promotion to stable.

## 0.1.0 — 2026-05-23 — Initial draft

- Created skill for scoring skills against the best-practices rubric library
- Modes: rubric-select, deep-audit [rubric-name], scorecard
- Reads rubric-manifest.json at ingestion to identify applicable rubrics
- [gate] dimensions scored mechanically; [review] dimensions scored with cited evidence
- Output contract: per-dimension scorecard entries + scorecard summary with top issues
- References rubrics on-demand (not preloaded at cold-start)
- Routing eval corpus: 12 trigger phrases + 5 adversarial phrases
- Differentiates from core-skills-evaluator: scoring vs. adversarial critique
