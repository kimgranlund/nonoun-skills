# Roadmap

## Planned
- [~~v1.13~~ DONE 1.13.0] Routing corpus recall improvement — description rewritten with specific vocabulary ("directory tree", "folder skeleton", "spec/ plan/ app/ axes", "playground app", "clone-and-run demo app") and NOT clauses for skill authoring + repo auditing. F1 0.64 → 0.74, R 0.58 → 0.83. Proxy ceiling for "scaffold" vocabulary ambiguity; live router handles better via context. Baseline committed.
- [~~v1.14~~ DONE 1.13.0] Scaffold script — `scripts/scaffold_app.py` ships with `--name`, `--display-name`, `--purpose`, `--base-dir`, `--mode greenfield|reverse-engineering`, `--dry-run`, `--force`, `--json`. Deterministic: 5 folders + 10 seeded stub files. Idempotent: skips existing files by default. JSON manifest output for CI integration. Smoke-tested: dry-run produces the correct 5+10 manifest.
- [v1.x] Mode commitment artifact — after Step 1 mode selection, write a one-line marker to a working file (e.g. `.scaffold-mode`) so subsequent steps can verify mode mechanically rather than relying on §SelfAudit's [gate] introspection claim. (Wlaschin Major from promote-mode council.)

## Deferred
<!-- Capabilities considered but postponed — document the reason and re-evaluation trigger. -->
<!-- Format: - Description — deferred because [reason]; revisit when [condition] -->

## Out of scope (by design)
- Creating distributable Claude Code plugins with `.claude-plugin/plugin.json` manifests — apps borrow the plugin folder layout but are not plugins; plugin creation has a different contract
- Authoring substantive spec or PRD content — this skill seeds minimal stubs; substantive content arrives via plan-spec, plan-prd, meta-expert-author
- Auditing or repairing existing app foundations — use ops-repo for drift detection and in-place audits
- Single-file demos with no skill/spec/plan story — these belong under site/pages/playground/, not apps/
- Web-component primitives — those live under packages/ with their own convention
