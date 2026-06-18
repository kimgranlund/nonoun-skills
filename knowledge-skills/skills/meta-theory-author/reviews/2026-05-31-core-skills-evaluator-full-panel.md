# meta-theory-author — Holistic 10-dim + 9-critic full panel (2026-05-31)

**Method:** two **fresh-context** subagents (blind) — `skills-holistic` v0.2.0 (D1–D10) + a 9-critic panel
— with an **inheritance probe**: this skill is defined as *overriding meta-expert-author's invariants*;
the parent just gained Invariant 12 (trust boundary) + 13 (evals required). Does the child inherit them?
All Criticals + the two code bugs **verified against the files.** **Target:** meta-theory-author v1.5.0
(`status: complete`).

## Verdict

**Overall 3 / 5 — and it confirms the root-cause pattern *plus* a new failure mode: broken inheritance.**
The child predates the parent's fix by 8 days and **re-enumerates the parent's invariants locally
(stopping at 10)** instead of a delta — so the parent's new safety invariants (12 trust boundary, 13
evals) are **silently excluded** ("inheritance-by-restatement is the bug"). It also **overloaded the
`§SelfAudit` token** (its Invariant 10 redefines it to mean "re-run verify_skill.py," a staleness check —
not the parent's injection guard). Clears the bar overwhelmingly: **~3 Criticals + ~7 Majors.** Genuine
strength: `tools/verify_skill.py` (D4=5, a real 567-line executable) — but it has two verified bugs that
make its headline checks not fire.

### Inheritance probe — FAILED (3 of 4 gaps)
- **Invariant 12 (trust boundary): not inherited.** Zero `injection`/`untrusted`/`trust boundary` hits
  anywhere (verified). The pipeline WebFetches arbitrary papers + landing pages + PDFs and writes files —
  the highest-WebFetch-exposure family in the library — with no guard. "What this skill produces" omits a
  `## §SelfAudit`. **D7=1, Critical.**
- **Invariant 13 (evals): not inherited.** No `evals/` dir; the produced-skill output contract omits it.
- **§SelfAudit: the skill has none** — the only mention (Invariant 10) is the overloaded staleness meaning.
- **Verify Target: the one that passes** — `verify_skill.py` closes on real Crossref/URL state.

## Holistic scorecard

| Dim | Name | Score | Finding |
|---|---|---|---|
| D1 `[review]` | Instructions & Harness | 4 | Minor — strong router + NOT-clause; **no real §SelfAudit** (token reused for staleness) |
| D2 `[review]` | Control Mode | 4 | Pass — mode-appropriate; rigid 12-section summary template is borderline over-proceduralized |
| D3 `[gate][review]` | Rubric Quality | 3 | **Major** — real `[hypothesis]`/`[established]` label discipline, but its output quality-checklist is unlabeled + uncalibrated |
| D4 `[gate]` | Mechanization | 5 | Pass — `tools/verify_skill.py` is a real 567-line executable (9 local + 4 network checks); but see BUG 1/2 below |
| D5 `[gate]` | Evaluation | 2 | **Major** — no `evals/`, no corpus/F1/baseline; teaches produced skills to omit `evals/` too |
| D6 `[review]` | Extensibility | 2 | **Major** — **template-only ROADMAP** while deferred scope lives in CHANGELOG + `verification-harness.md` (pollution) |
| D7 `[gate]` | **Security & Trust** | 1 | **Critical** — fetch-and-write over arbitrary academic URLs, zero injection guard / scope / §SelfAudit |
| D8 `[review]` | Observability | 3 | Minor — `verify_skill.py` exit codes/JSON are a real machine signal, but observe *form* not *correctness* |
| D9 `[review]` | Context Engineering | 4 | Pass — strong progressive disclosure + "load parent's refs, don't duplicate"; **no freshness check on the inherited parent** (the exact drift that happened) |
| D10 `[review]` | Plan Anatomy | 3 | Minor — wave plan has verifiable per-wave state (verify_skill.py checkpoint); orchestration spine leans on phase labels |

## Verified concrete bugs (in the skill's one mechanized strength)

- **[Critical · verified · FIXABLE] `verify_skill.py` gates on the stale parent name.** Line 377 checks
  `specializes != "theoretic-expert-author"`, but `skill.json` declares `specializes: "meta-expert-author"`
  (post-v0.2 rename). Every correctly-named produced skill trips the WARNING branch. The docstring + ~7
  references still say `theoretic-expert-author` — the v0.2.0 rename CHANGELOG claimed "all cross-refs
  updated"; the executable was not. *(Reproducibility broken at the rename boundary.)*
- **[Major · verified · FIXABLE] `REQUIRED_FIELDS` keys on a non-existent `works/` axis.** Line 90 keys the
  DOI/retraction/peer-review-status enforcement (the skill's *headline* discipline) on `"works"`, but the
  doctrine's actual paper-bearing axes (SKILL.md/INDEX) are `findings/` / `debates/` / `figures/`. A real
  produced skill's findings files hit `axis="unknown"` → the DOI/retraction checks **silently no-op.** The
  gate misses its own headline invariant.
- **[Major · verified] `status: complete` mislabel** — CHANGELOG/ROADMAP flag no live validation run ever
  occurred + the parent now mandates evals this skill lacks. → `stable`.
- **[Minor · verified] dashboard name disagreement** — CHANGELOG says `expert-dashboard`, SKILL.md says
  `ref-dashboard` (the skill that exists is `ref-dashboard`).

## Prioritized fixes (mostly parallel to the meta-expert-author v1.7.0 fix)
1. **Inherit the parent's safety invariants explicitly** — add Inv 12 (trust boundary + a real
   `## §SelfAudit` injection guard, distinct from the staleness invariant) + Inv 13 (evals required) to the
   produced-skill contract; give *this* skill a §SelfAudit. *(closes D7=1 + D5)*
2. **Replace the local invariant enumeration with a delta** ("inherit 1–13; override only §sourcing /
   §verification / §axis / §file-shape / §SKILL-section") to kill the numbering collision + the drift class,
   and add a freshness check on the inherited parent. *(Yegge / Wlaschin)*
3. **Fix the verifier:** read `specializes` from skill.json (or hardcode `meta-expert-author`); reconcile
   `works/` ↔ the real axis names so DOI/retraction checks fire; update the stale string refs. *(BUG 1+2)*
4. **`status: complete` → `stable`.**

## Disposition
Tracked in `meta-theory-author/ROADMAP.md` (Planned) + repo-root `BACKLOG.md`. The systemic lesson —
**inheritance-by-restatement silently drops parent updates** — is the cross-cutting note.
