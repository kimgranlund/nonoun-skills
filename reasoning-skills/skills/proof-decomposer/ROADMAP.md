# Roadmap — proof-decomposer

Ships its core in 0.1.0 (the two axes, the structure check, the counterexample search, the proof-
skeleton card, the proof-method playbooks). Everything below is additive.

## `bin/proof-structure-check.py`

- [x] **UNJUSTIFIED gate** (landed) — a non-root step with empty `from` grounded vacuously
      (`all([])` is True); now a FAIL with a "move to premises/axioms if assumed" hint, plus a
      must-flag fixture. Forward references stay valid (a skeleton is a DAG, not a sequential program).
- [ ] **Per-step inference typing** — tag each edge with its rule (modus ponens, ∀-elim, induction
      step) and check the rule's arity/shape, narrowing the gap between "shape valid" (today) and
      "inference valid" (A3 — still a human read).
- [ ] **Sub-step expansion hints** — flag a step whose `statement` is long / multi-clause relative to
      its single `from` edge (a likely "obviously" hiding a sub-proof) for decomposition.
- [ ] Emit a machine-readable report (JSON) so GRADE can fold the structure verdict into the check
      record, and a Graphviz/DOT export of the citation graph for inspection.

## `bin/numeric-spotcheck.py`

- [x] **Result-magnitude guard + wall-clock budget** (landed) — `**` is composable, so a per-exponent
      cap let `((n**64)**64)**64` build a ~500k-digit integer and hang; now each power's predicted
      bit-size (`base.bit_length() * exp`) is checked against `MAX_BITS` before computing, with a
      `WALLCLOCK_BUDGET_S` backstop across the loop. POW_BOMB fixture must be REJECTED. Primality is
      explicitly OUT OF SCOPE (no primality predicate); a false-algebraic-identity fixture replaced the
      misleading "Euler prime" one — number-theory/primality claims route to a proof assistant.
- [x] **Modular / divisibility / primality predicate claims** (landed, 0.2.1) — a second claim
      shape beside the boolean `expr`: a single-var `f(n)` asserted to satisfy a number-theory
      predicate (`is prime`, `k | f(n)` / `divisible by k`, `≡ r (mod m)`), accepted as JSON or a
      natural-language sentence. `f(n)` reuses the SAME safe AST evaluator (all `**` magnitude/exponent
      guards + wall-clock backstop inherited); the only additions are a bounded trial-division
      primality test (capped at ~10¹², a larger `|f(n)|` rejected not hung) and a per-n predicate. The
      Euler polynomial `n²−n+41` is now a real fixture: COUNTEREXAMPLE at n=41 with the **modular
      witness** `f(41)=1681 ≡ 0 (mod 41) = 41²` (the constant term divides it). Fixtures lock a true
      bounded Euler window (no false-positive), true/false divisibility + congruence, and a primality
      DoS rejection.
- [ ] **Rationals & wider domains** — exact rationals (`fractions`), and a real-sampling mode (grid +
      random) with a tolerance.
- [ ] **Randomized / smart sampling** — beyond the dense Cartesian product: random sampling for wide
      multi-var ranges, and boundary-biased sampling (always test lo, hi, 0, ±1) so the cheap edges
      that break induction base cases are never missed.
- [ ] **Witness search** for ∃-claims — given `exists`-shaped expr, search for a satisfying witness
      (the dual of counterexample search) to support construction proofs at B3.

## Method & corpus

- [ ] A **routing-eval corpus** (the maturity step the repo ROADMAP tracks) — especially the
      boundaries with a general theorem prover / ATP (this skill grades a *given* argument), with
      `research-survey` (exploration), and with `deep-research` (whose adversarial-verify move the
      claim probe borrows) — the likely mis-routes.
- [ ] A worked **end-to-end transcript** (a SPECIFY → prove → DECOMPOSE → GRADE on a real theorem),
      with the skeleton card, both check records, and a caught "proves-the-converse" drift checked in
      and dogfooded.
- [ ] An **adversarial-probe template** (the fresh-context skeptic prompt for the claim) as a reusable
      reference, shared in shape with `deep-research`'s verify step.
- [ ] A **proof-assistant adapter** (the stronger B3) — a thin manifest like the code-decomposer
      harness that shells out to Lean / Coq / Isabelle where installed, recording a machine-checked
      certificate (and a SKIP where absent), kept advisory because the toolchain is project-specific.

## Plugin

- [ ] As `reasoning-skills` grows, candidate siblings from the same ARGUMENT/VERIFICATION lineage: a
      `logic-decomposer` (propositional/predicate validity: form × truth-table/SAT) and an
      `estimation-decomposer` (Fermi estimates: assumptions × sensitivity bounds) — both with
      deterministic checks.
