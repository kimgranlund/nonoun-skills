# Roadmap

## Planned
<!-- Format: - [vX.Y] Description -->
- [v1.2] Operation-recall eval — feed past `ops-ledger.jsonl` lines (op + input) back and check the skill re-selects the same verb on the same input (the ledger's own self-test; see `references/operation-ledger.md`).
- [v1.2] Score `evals/routing-corpus.json` for an F1 baseline (the cross-library theme-5 "label `[gate]` only if a check runs it" frontier).

## Done (v1.1.0 — 2026-05-30)
- Addressed the 2026-05-30 core-skills-evaluator 9-critic review (`reviews/2026-05-30-core-skills-evaluator-full-panel.md`): **vocabulary justified** (UPSERT/APPEND, MERGE/DEDUPE, SUPERSEDE/RETRACT distinctions surfaced into SKILL.md); **operation ledger** added (`references/operation-ledger.md`); **file list single-sourced** to `skill.json`; **routing eval corpus** added; **external-doc injection guard** added (in §SelfAudit). Plus §SelfAudit + Verify Target for full family uniformity. First Principles promoted into the shared `.docs/ops-family-shape.md` template.

## Deferred
<!-- Capabilities considered but postponed — document the reason and re-evaluation trigger. -->
<!-- Format: - Description — deferred because [reason]; revisit when [condition] -->

## Out of scope (by design)
<!-- Capabilities explicitly excluded — not postponed, intentionally outside this skill's boundary. -->
<!-- Format: - Description — excluded because [reason] -->
