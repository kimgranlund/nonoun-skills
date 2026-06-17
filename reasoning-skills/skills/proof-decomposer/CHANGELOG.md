# Changelog — proof-decomposer

Versioned independently of the `reasoning-skills` plugin; the gate (`bin/check-skills.py`) must pass
for any release.

## 0.1.0 — draft

Initial release. Decompose / design / grade a mathematical proof or deductive argument on the
**ARGUMENT × VERIFICATION** crossing axes, scored separately with a gated rubric and the opposite-
defect quadrant.

- **The two-axis method** (`references/decomposition-method.md`): Argument (claim → strategy → steps →
  coverage → rigor) × Verification (well-formed → acyclic → checks → robustness → reproducibility),
  crossing at the theorem statement; gates before reviews; the *valid-steps-proves-a-different-
  statement* vs *right-claim-invalid-or-circular-step* quadrant; and the **gate-where-you-can,
  adversarially-verify-where-you-can't** doctrine.
- **The structure check** (`references/structure-and-circularity.md` + `bin/proof-structure-check.py`):
  the centerpiece — a deterministic attack on circular reasoning and unsupported chains. Represents a
  proof as a skeleton (premises / axioms / steps with `from` citations / goal) and asserts no dangling
  citation, a DAG (no circular reasoning), and a reachable goal; flags off-path (irrelevant) steps.
  `selftest` proves valid / circular / dangling / unreachable / irrelevant fixtures with no deps.
- **The counterexample search** (`references/verification-axis.md` + `bin/numeric-spotcheck.py`):
  mechanizes B3 — searches a finite integer sample space for a counterexample to a parametric claim
  via a **safe** AST evaluator (no `eval`; only literals, declared vars, `+ - * // % **`, comparisons,
  `and/or/not`, parens). A counterexample is a disproof; "no counterexample in range" is corroboration,
  never a proof. `selftest` proves true/false claims and rejects code-injection attempts.
- **The ARGUMENT axis** (`references/argument-axis.md`): claim/quantifier precision, the "proves a
  different statement" neighbor table (converse, dropped hypothesis, quantifier swap, special case),
  strategy selection, and the fresh-context **adversarial claim probe**.
- **Proof methods** (`references/proof-methods.md`): direct · contrapositive · contradiction ·
  induction · construction · pigeonhole · cases/WLOG, each with its strategy-risk profile, decisive
  gate, and common misuse.
- **Policy** (`references/policy.md`): the 10-point definition-of-done, the proof-skeleton card +
  check-record shapes, and the handoff seams to a prose author, a proof assistant, and an ATP (which
  this skill is NOT).

First skill in the new `reasoning-skills` plugin.
