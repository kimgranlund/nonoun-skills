# Changelog — config-decomposer

Versioned independently of the `ops-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.1.0 — draft

Initial release. Decompose / design / grade a configuration / infrastructure-as-code artifact on the
**INTENT × VALIDITY** crossing axes, scored separately with a gated rubric and the opposite-defect
quadrant.

- **The two-axis method** (`references/decomposition-method.md`): Intent (desired-state → contract →
  cases → drift & idempotency → fit) × Validity (parse → schema → plan → safety → observability),
  crossing at the config-measured-against-the-tool's-schema/state; gates before reviews; the
  *right-intent-won't-validate* vs *valid-but-wrong* quadrant; and the **plan-is-the-contract**
  doctrine (a missing tool is a SKIP, not a pass).
- **The VALIDITY harness** (`references/validity-axis.md` + `bin/config-harness.py`): a thin adapter
  modeled on code-decomposer's execution-harness — reads a per-tool command manifest, runs each
  present gate (parse/schema/plan/lint/policy), and normalizes verdicts to a report card; a missing
  tool is a SKIP flagged as `NO EVIDENCE`, never a pass. `selftest` proves the parse + normalize +
  run/skip logic with no external deps; `template` prints a starter manifest.
- **The plan-and-drift centerpiece** (`references/plan-and-drift.md`): the *plan-is-the-contract*
  principle, idempotency as a fixed point, the four failure shapes (surprise destroy, silent default,
  wrong scope, non-idempotent churn), the discipline of reading a plan diff against the desired state,
  and why a green parse proves nothing.
- **The safety linter** (`references/secrets-and-safety.md` + `bin/config-lint.py`): a static
  smell detector across YAML/JSON/HCL/Dockerfile/TOML (treated as text, one detector per format) —
  plaintext secrets, `:latest`/unpinned, `0.0.0.0/0`/`::/0`, wildcard `"*"` grants, missing k8s
  resource limits — with a reference/placeholder false-positive guard. `selftest` over good/bad
  fixtures.
- **The INTENT axis** (`references/intent-axis.md`): desired-state framing, the config contract (the
  dependency surface other configs read), case enumeration, drift & idempotency, fit, and recovering
  intent from an existing config — where the *valid-but-wrong* defect lives.
- **Policy** (`references/policy.md`): the 10-point definition-of-done, the config-spec card
  `{desired_state, contract, plan_verdict, safety_findings[]}`, the harness adapter manifest, and the
  handoff seams to `code-decomposer`, `/verify`, `arch-system`, and `/simplify`.

First skill in the new `ops-skills` plugin.
