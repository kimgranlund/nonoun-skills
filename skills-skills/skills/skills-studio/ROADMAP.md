# Roadmap

v3.1.0 (2026-05-31) made it **bi-directional** — the author side now builds against the same foundations/rubrics/critics the eval side scores with (`references/authoring/build-against-the-standard.md` + a build-time red-team gate). v3.0.1 renamed `skills-critique` → `skills-studio`; v3.0.0 folded in `meta-skill` and retired `meta-skill-typed`; v2.0.0 merged the two evaluators. **`skills-studio`** is the full skill lifecycle tool. See CHANGELOG.

## Planned

- [DONE v3.0.1] ~~Rename so the name stops under-describing the skill~~ → **`skills-studio`** (a studio creates _and_ critiques; establishes the `*-studio` convention with `core-brand-studio`).
- [v3.x] **Graduation from draft to stable** — exit criteria per family: **author** needs ≥3 skills produced end-to-end that pass `quick_validate.py --strict` on first try; **score** needs ≥3 empirical applications per rubric with demonstrated catches; **critique** needs ≥3 adversarial evals whose Critical/Major findings demonstrably improved the target.
- [v3.x] **Measure the routing corpus.** `evals/routing-corpus.json` now exists and is CI-scored by `score-routing.py` (the v2.x gap — closed). The model-executed F1 (vs the IDF proxy) remains the operational frontier.
- [v3.x] **Mechanize more author gates** — `quick_validate.py --strict` checks routing-corpus/Verify-Target/Quick-Start/§SelfAudit presence; extend to label-coverage and the "doesn't-exempt-itself" check. (`check-foundations-coverage.py` is the foundations↔rubrics gate already in CI.)

## Deferred

- **Cross-rubric dependency enforcement** — validating a skill meets a dependency rubric's minimum before scoring dependent rubrics; deferred because scoring is human-driven and the ceremony is premature at ~0 empirical applications.
- **A dedicated self-improving-systems / extensibility critic seat** — partially resolved (the SI1–SI5 topical section + synthesis prompt S10 compose existing voices). A standalone seat remains deferred (candidate: Neal Ford / Rebecca Parsons). Tracked in `BACKLOG.md`.
- **A UX/product critic seat** — deferred until the panel shows a gap it would fill. (`core-agentic-ux-best-practices` owns the operator-seat UX lens for _workflows_; keep in sync, don't merge.)
- **Pruning the inherited eval machinery** — the `eval-viewer/`, `aggregate_benchmark.py`, and `generate_report.py` came in wholesale with the meta-skill fold; revisit whether all of it earns its keep once the `eval` mode has real usage.

## Out of scope (by design)

- **Authoring a comprehensive [domain]-expert knowledge skill** (research-wave reference skills like ref-dashboard) — `meta-expert-author`; or a **peer-reviewed-source theory skill** — `meta-theory-author`. skills-critique authors _general_ skills; these two specialized authors stay separate.
- **Code review of non-skill artifacts** (PRs, general codebases) — the rubrics and critic personas are calibrated for agent skills and agentic systems, not general code quality.
