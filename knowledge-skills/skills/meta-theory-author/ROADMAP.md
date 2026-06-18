# Roadmap

## Planned
<!-- Features and improvements for a future version. -->
<!-- Format: - [vX.Y] Description -->

**From the 2026-05-31 holistic + 9-critic full panel** (`reviews/2026-05-31-core-skills-evaluator-full-panel.md` — overall 3/5). The Criticals + verifier bugs are fixed (v1.6.0); remaining:
- [Major — OPEN] **Replace the local invariant enumeration with a true delta** ("inherit 1–13; override only §sourcing/§verification/§axis/§file-shape/§SKILL-section") + add a freshness check on the inherited parent, so the inheritance-by-restatement drift class can't recur. (v1.6.0 made the safety invariants explicit + stated full 1–13 inheritance; the structural delta-only refactor remains.)
- [Major — OPEN] **Calibration for produced rubrics** — label the output quality-checklist `[gate]`/`[review]` + a two-reviewer agreement step. *(D3=3)*
- [Major — OPEN] **`evals/` for this skill itself** + a behavioral corpus runner — Invariant 12 now mandates it for produced skills; the meta-skill should model it. *(D5=2)*
- [Minor — OPEN] Reconcile `works/` vs `findings/`/`debates/` axis naming in the doctrine (the verifier now accepts all three; the doctrine should pick one canonical). Reconcile `expert-dashboard` vs `ref-dashboard` in CHANGELOG/SKILL.md.
- [Minor — OPEN · surfaced by the now-working verifier] **8 broken peer-paths in the skill's own reference files** — they cite the parent as `../../meta-expert-author/...` (2 levels) but the correct depth from `references/<axis>/` is `../../../meta-expert-author/...` (3 levels). The BUG 1 fix made `verify_skill.py` actually run, which immediately caught these; fix the depth in the cross-refs.
- [Done v1.6.0] ~~Trust boundary not inherited (D7=1)~~ → Invariant 11 + agent-brief clause + produced-skill §SelfAudit requirement.
- [Done v1.6.0] ~~Evals not inherited (D5)~~ → Invariant 12 + "What this skill produces."
- [Done v1.6.0] ~~verify_skill.py stale parent name (BUG 1) + `works/`-axis no-op (BUG 2)~~ → both fixed; headline DOI/retraction checks now fire.
- [Done v1.6.0] ~~`status: complete` mislabel~~ → `stable`. ~~§SelfAudit token collision~~ → Invariant 10 reworded.

## Deferred
<!-- Capabilities considered but postponed — document the reason and re-evaluation trigger. -->
<!-- Format: - Description — deferred because [reason]; revisit when [condition] -->

## Out of scope (by design)
<!-- Capabilities explicitly excluded — not postponed, intentionally outside this skill's boundary. -->
<!-- Format: - Description — excluded because [reason] -->
