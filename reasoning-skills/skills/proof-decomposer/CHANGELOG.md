# Changelog — proof-decomposer

Versioned independently of the `reasoning-skills` plugin; the gate (`bin/check-skills.py`) must pass
for any release.

## 0.2.1 — beta

Deepened `bin/numeric-spotcheck.py` with a **modular / divisibility / primality** claim shape (the ROADMAP modular item). Beside the existing boolean `expr` claim, the tool now takes a single-variable function `f(n)` asserted to satisfy a number-theory predicate — `is prime`, `k | f(n)` / `divisible by k`, or `≡ r (mod m)` — accepted as a JSON object **or** a natural-language sentence (`^` normalised to `**`, var defaults to `n`).

- **Safe-eval preserved.** `f(n)` is evaluated by the **same** AST-whitelist evaluator (`compile_expr` + `eval_node`) — no `eval()` — so every existing guard (the `**` exponent cap, the result-bit-size magnitude cap, the wall-clock backstop) is inherited unchanged. The only new code is a **bounded trial-division** primality test (capped at ~10¹²; a larger `|f(n)|` is *rejected*, never computed) and a per-n predicate; the search returns the **smallest** counterexample.
- **The Euler polynomial is now a real fixture.** `n²−n+41 is prime for all n ≥ 0` → COUNTEREXAMPLE at **n=41**, `f(41)=1681=41²`, reported with the **modular witness** `f(41) ≡ 0 (mod 41)` — the constant term 41 divides it. The misleading "primality is OUT OF SCOPE / motivation only" framing in `references/verification-axis.md` and the source is replaced.
- **Fixtures lock both directions** (the adversarial-selftest discipline): a found counterexample (Euler n=41 with the mod-41 witness; `n²+1` divisible by 2 failing at n=2 with remainder 1; `n ≡ 0 (mod 3)` failing at n=1) **and** true claims that yield none (the *bounded* Euler window `0 ≤ n ≤ 39`; `n³−n` divisible by 6; `2n ≡ 0 (mod 2)`), plus a primality-over-a-huge-value **DoS rejection** and a `**`-bomb rejection inside a predicate claim. `is_prime` itself is checked against known primes/composites. All existing fixtures (true/false boolean claims, false algebraic identity, POW_BOMB, chained comparisons, parse rejections) are intact.

## 0.2.0 — beta

Promoted to beta as part of the marketplace **v0.2.0** milestone (see the root CHANGELOG). This cycle the skill gained a checked-in, sibling-collision-tested routing-eval corpus, an adversarial-review hardening pass (fixes locked as selftest fixtures), and a worked `examples/walkthrough.md` (a red→green bin proof).

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
