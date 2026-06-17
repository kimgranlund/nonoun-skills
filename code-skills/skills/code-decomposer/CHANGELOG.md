# Changelog — code-decomposer

Versioned independently of the `code-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.2.0 — beta

Promoted to beta as part of the marketplace **v0.2.0** milestone (see the root CHANGELOG). This cycle the skill gained a checked-in, sibling-collision-tested routing-eval corpus, an adversarial-review hardening pass (fixes locked as selftest fixtures), and a worked `examples/walkthrough.md` (a red→green bin proof).

## 0.1.0 — draft

Initial release. Decompose / design / grade a unit of code on the **SPEC × EXECUTION** crossing axes,
scored separately with a gated rubric and the opposite-defect quadrant.

- **The two-axis method** (`references/decomposition-method.md`): Spec (problem → contract → cases →
  approach → fit) × Execution (compile → types/lint → test → robustness → observability), crossing at
  the contract; gates before reviews; the *correct-idea-won't-run* vs *green-but-wrong* quadrant; and
  the **gate-where-you-can, adversarially-verify-where-you-can't** doctrine.
- **The EXECUTION harness** (`references/execution-axis.md` + `bin/execution-harness.py`): a thin
  adapter that reads a per-project command manifest, runs each present gate (compile/typecheck/lint/
  test/mutation), and normalizes verdicts to a report card — a missing tool is a SKIP, not a pass.
  `selftest` proves the parse + normalize + run/skip logic with no external deps.
- **The test-vacuity linter** (`references/test-integrity.md` + `bin/test-vacuity-check.py`): the
  centerpiece — a deterministic attack on the *green but wrong* quadrant. Flags no-assert, tautology,
  mock-only, focused (`.only`), and skipped tests in Python (via `ast`) and JS/TS (regex + brace
  matching); optional `--unit` flags tests bound to the wrong subject.
- **The SPEC axis** (`references/spec-axis.md`): problem framing, contract design, case enumeration,
  approach/fit, and the fresh-context **adversarial spec probe**.
- **Unit families** (`references/unit-families.md`): pure · stateful · async · I/O · parser ·
  endpoint · glue, each with its spec-risk profile and execution emphasis.
- **Policy** (`references/policy.md`): the 10-point definition-of-done, the spec-card + execution-
  report shapes, the harness manifest, and the handoff seams to `/code-review`, `/verify`,
  `arch-system`, and `/simplify`.

First skill in the new `code-skills` plugin.
