# Changelog — plugin-decomposer

Versioned independently of the `plugins-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.1.0 — draft

Initial release. Decompose / design / grade a Claude Code **plugin** (a marketplace-distributed bundle
of commands / agents / skills / MCP servers / hooks) on the **BUNDLE × MANIFEST** crossing axes, scored
separately with a gated rubric and the opposite-defect quadrant.

- **The two-axis method** (`references/decomposition-method.md`): Bundle (one job → components fit →
  cohesion → boundary → standing-context cost) × Manifest (well-formed → name/version → marketplace
  resolves → paths legal → self-contained), crossing at the manifest + structure; gates before
  reviews; the *coherent-idea-won't-load* vs *loads-fine-kitchen-sink* quadrant; and the
  **gate-where-you-can, adversarially-verify-where-you-can't** doctrine (manifest to code, the one-job
  bundle judgment to a fresh-context probe).
- **The MANIFEST checker** (`references/plugin-anatomy.md` + `bin/plugin-check.py`): the deterministic
  attack on the *coherent-idea-won't-load* quadrant. Reads a `plugin.json` (+ an optional
  `marketplace.json` entry) and flags MANIFEST_INVALID (missing/empty `name`/`version`), BAD_NAME
  (non-kebab), BAD_VERSION (non-semver), MARKETPLACE_MISMATCH (entry name doesn't resolve), and
  ILLEGAL_PATH (absolute or `..`-escaping component/source paths) as **gates**, plus KITCHEN_SINK (≥4
  distinct declared component kinds) as an **advisory** smell. `selftest` proves every code over
  must-flag and must-not-flag fixtures (clean minimal passes; missing name → MANIFEST_INVALID; `Foo
  Bar` → BAD_NAME; `1.0` → BAD_VERSION; `../x` → ILLEGAL_PATH; a focused 2-kind bundle does NOT trip
  KITCHEN_SINK), with no external deps.
- **Plugin anatomy** (`references/plugin-anatomy.md`): the manifest/marketplace/skills-discovery
  contract — `plugin.json` required fields, kebab/semver rules, how a marketplace entry resolves
  (name + source), path legality, self-containment, the skill-bundle special case, and how each
  checker finding maps onto the contract.

First skill in the new `plugins-skills` plugin. The nonoun-native peer to the global
`plugins-factory`.
