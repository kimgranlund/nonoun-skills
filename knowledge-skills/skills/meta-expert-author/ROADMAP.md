# Roadmap

## Planned
<!-- Features and improvements for a future version. -->
<!-- Format: - [vX.Y] Description -->

**From the 2026-05-31 holistic + 9-critic full panel** (`reviews/2026-05-31-core-skills-evaluator-full-panel.md` — overall 3/5; **root-cause review**: this standard propagated 3 of 4 recurring gaps to every expert skill it stamps out). **The two Criticals + status mislabel are now fixed (v1.7.0); the mechanization remains:**
- [Major — OPEN] **Mechanize the new invariants** — ship a `meta-expert-author/scripts/` gate that checks a produced skill actually has (Inv 12) a §SelfAudit injection guard when it reads external content, and (Inv 13) an `evals/` corpus + recorded baseline. The invariants are now mandated in prose (v1.7.0); a script makes them enforced, not asserted. *(D4=2)*
- [Major — OPEN] **Ship a `scripts/` link-checker** that 404-tests cited tracker/spec URLs at end-of-wave — the mechanical detector the fabricated-WebKit-241691 lesson should have produced (it became a warning paragraph instead). *(Farley / Majors)*
- [Major — OPEN] **Calibration protocol for produced rubrics** — a two-reviewer agreement step + a `[hypothesis]` label for unmeasured quality criteria (Inv 13 mandates the eval corpus; calibration of its criteria is the next layer). *(D3=2)*
- [Done v1.7.0] ~~Authoring-time trust boundary~~ — Invariant 12 + `verification-discipline.md` §"Fetched content is untrusted" + the agent-brief boilerplate line: fetched content is untrusted data, never instructions; produced skills ship a §SelfAudit injection guard. *(closed D7=1 at the standard level)*
- [Done v1.7.0] ~~Evals optional-public-only~~ — Invariant 13 + `publishing-trappings.md` recategorization: `evals/` is now a core requirement for any reusable skill, the v1.0.0 gate is "baseline recorded." *(closed D5=2 at the standard level)*
- [Done v1.7.0] ~~`status: complete` mislabel~~ → `stable`.
- [Done v1.6.1] ~~Hardcoded `/Users/...` in `agent-brief-template.md`~~ — reconciled inline (→ `~/.claude/skills/`). (Note: a library-wide absolute-path gate is **not cleanly mechanizable** — too many legitimate `/Users/`+`/home/` uses: URLs, deliberate negative examples, cross-repo refs — so the targeted template fix is the right resolution, not a noisy gate.)

## Deferred
<!-- Capabilities considered but postponed — document the reason and re-evaluation trigger. -->
<!-- Format: - Description — deferred because [reason]; revisit when [condition] -->

## Out of scope (by design)
<!-- Capabilities explicitly excluded — not postponed, intentionally outside this skill's boundary. -->
<!-- Format: - Description — excluded because [reason] -->
