---
name: proof-decomposer
description: >
  Decompose, design, and grade a mathematical proof or rigorous deductive argument on two crossing
  axes — ARGUMENT (claim → strategy → steps → coverage → rigor) and VERIFICATION
  (well-formed → acyclic → checks → robustness → reproducibility) — scored separately so a valid-
  looking chain can't hide that it proves a different (often weaker) statement, nor a right claim
  hide an invalid or circular step. VERIFICATION routes to a self-tested structure check
  (bin/proof-structure-check.py: dangling-citation, circular-reasoning/DAG, goal-reachability) and a
  safe counterexample search. Backed by a gated rubric, a proof-skeleton
  card, and proof-method playbooks (induction, contradiction, contrapositive). Use when planning a
  proof, checking whether an argument is valid, or grading one — it only ever grades a GIVEN
  argument, never invents one. NOT for a function or unit of code against its spec
  (→ code-decomposer). NOT a theorem prover: does not search for or produce a proof, nor discover
  one for an open conjecture.
---

# proof-decomposer — grade a deductive argument on two crossing axes

A proof is **correct on two independent axes that walk the same hierarchy in opposite directions** —
the decomposer seam the layout-, mermaid-, component-, and code-decomposers apply to space, diagrams,
components, and code, here applied to a mathematical proof / deductive argument:

- **Argument · whole → part** grades the **intent**: the claim it proves → its strategy → its steps →
  its case coverage → its rigor. *"Does it prove the right statement, soundly?"*
- **Verification · part → whole** grades the **mechanism**: every step is well-formed → the citation
  graph is acyclic and the goal is reachable → the claim survives counterexample search → it's robust
  at the boundary → a reader can reproduce it. *"Does the argument actually hold, mechanically?"*

They **cross at the theorem statement** — the statement is *both* the thing the Argument axis claims
(the exact quantified proposition) *and* the goal the Verification axis's checker must reach from the
premises and axioms. That crossing is the whole technique: a proof can be **valid steps, proves a
different (often weaker) statement** (a clean DAG that reaches the goal — but the converse, a dropped
hypothesis, or quantifier drift) or **right claim, an invalid or circular step** (it targets exactly
the theorem, but a step cites itself, cites a missing lemma, or the goal isn't reachable). Opposite
defects, opposite fixes — so you **score and report the two axes separately**, never averaged.

The reason this is outsized for an LLM author: an argument's **persuasiveness is not its validity** —
confidently-stated, individually-plausible steps are exactly the failure a sympathetic read rubber-
stamps. So VERIFICATION is routed to a *structure check* (citation integrity + acyclicity + goal-
reachability) and a *numeric counterexample search*, both mechanizable; and the dangerous **proves-a-
neighbor** quadrant — the one a clean structure check passes happily — gets a dedicated attack: a
fresh-context adversarial probe of the CLAIM.

## Quick Start

**You bring:** a claim + a proof (a sketch, a textbook argument, an existing proof) and the question —
"state and plan this", "is this proof valid?", "does it prove what it claims?", "is it rigorous?".
**You get:** a proof-skeleton card (the claim + strategy + cited steps + goal), a check record, and a
two-axis grade with the defect quadrant named.

> *"Is this proof that `n(n+1)` is even for all n ≥ 0 valid?"* →
> 1. **Argument — claim → strategy:** the claim is `∀n∈ℤ, n≥0 ⟹ n(n+1) even` `[gate]`; the strategy
>    is a case split on n's parity — sound and fitting `[gate]`.
> 2. **Verification — check it, don't read it:** build the skeleton (steps + `from` citations + goal)
>    and run `bin/proof-structure-check.py` — DAG, no dangling lemma, goal reachable `[gate]`. Then
>    `bin/numeric-spotcheck.py {"vars":["n"],"expr":"n*(n+1)%2==0","range":[0,100]}` — no
>    counterexample `[gate]`.
> 3. **Adversarial claim probe:** in a fresh context, hunt for drift — does it prove a *neighbor*
>    (the converse? a dropped hypothesis? ∃ doing ∀'s work)? Any drift is an A1 failure.
> 4. **Review + report:** steps/coverage/rigor (A3–A5), robustness/reproducibility (B4–B5), then the
>    two axis scores + the quadrant cell — gate failures first — handed to a prose author or a proof
>    assistant.

**Modes:** **SPECIFY** (state the claim + quantifiers → pick a strategy → plan the proof skeleton) ·
**DECOMPOSE** (read a proof → recover claim + strategy → run the structure/numeric checks → grade) ·
**GRADE** (score both axes, gates before reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Argument** | whole → part | **A1** Claim → **A2** Strategy → **A3** Steps → **A4** Coverage → **A5** Rigor | "Does it prove the *right statement*, soundly?" |
| **B · Verification** | part → whole | **B1** Well-formed → **B2** Acyclic → **B3** Checks *(integer-arithmetic claims; else SKIP / proof-assistant)* → **B4** Robustness → **B5** Reproducibility | "Does the argument *actually hold*, mechanically?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on
that axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable proof is **≥4 on every review with
zero gate failures**, reported as two separate axis scores plus the defect quadrant. The gates route
to code: **B1/B2 structure** → `bin/proof-structure-check.py` (always); **B3 checks** →
`bin/numeric-spotcheck.py` — but B3 **applies only to parametric integer-arithmetic claims**; for any
other claim B3 is a recorded **SKIP** (or a proof-assistant gate where available), which is the common
case, *not* a failure.

## The doctrine — gate where you can, adversarially verify where you can't

The non-obvious core, and the reason it earns a skill:

- **VERIFICATION is the cheap, deterministic axis** — route B1/B2 to `bin/proof-structure-check.py`
  (the citation graph is a DAG, no dangling lemma, goal reachable) and B3 to `bin/numeric-spotcheck.py`
  (a counterexample search), and **trust the graph and the counterexample, not the read-through**. A
  counterexample is a *disproof*; a clean structure check catches *circular / invalid-chain* outright.
- **"Proves a different statement" is NOT deterministically gateable** — it lives on the ARGUMENT side
  (the steps are valid and the goal is reached, but the *target* is a neighbor of the claim). The
  structure check passes a proof of the converse just as happily as a proof of the theorem. Route it
  to a **fresh-context adversarial probe** of the claim: a verifier sharing the author's framing
  inherits its drift — separate the context (the `deep-research` move).

## The proof methods (pick by the shape of the claim)

Each method tells you **where the strategy/step defect hides** and **which gate is the cheapest place
to catch it** — it focuses the method, doesn't change it. Full table in `references/proof-methods.md`.

| Method | Decisive gate / failure to hunt |
|---|---|
| direct · contrapositive | A1 confusing contrapositive with the **converse** (a different claim) |
| induction | B4 the **base case** (`numeric-spotcheck` at n₀) + A4 the step *uses* the hypothesis |
| contradiction | A2 a real **⊥** is actually derived, not merely "surprising" |
| construction · pigeonhole | A4 the witness is **exhibited** + B3 it numerically satisfies the property |
| cases / WLOG | A4 the partition is **exhaustive**; the "WLOG" doesn't lose generality |

## §SelfAudit

- **Persuasiveness is not validity.** Do not certify a proof by reading it sympathetically — run
  `proof-structure-check.py` and `numeric-spotcheck.py`. An unrun check is *no evidence*, not a pass.
- **A clean DAG is evidence of nothing about the claim.** B1/B2 prove there's no circular reasoning
  and the goal is reached *as cited* — they do **not** prove the goal is the *right* goal (A1) or that
  each cited justification is *valid* (A3). Gate first, then read for soundness and aim.
- **The dangerous defect is invisible to the tools — probe the claim adversarially in a fresh
  context.** "Proves a neighbor" needs a skeptic hunting the converse / dropped hypothesis / quantifier
  drift, not the author's confidence.
- **A counterexample is a disproof; "no counterexample in range" is not a proof.** A finite search
  over ℤ corroborates and cheaply *catches* a false ∀-claim — it never settles an infinite domain.
  Report "survived N samples", never "verified".
- **Gates before reviews, always.** Don't grade the steps of a proof of the wrong claim, or the rigor
  of a chain that cites a missing lemma. Stop each axis at its first failed gate.
- **Two scores, never one.** *Valid-steps-wrong-statement* and *right-claim-broken-step* need opposite
  fixes (re-state and re-quantify the claim vs repair the chain). Report both axes and name the
  quadrant cell; never average.
- **Argument, not theorem-proving.** This skill grades a *given* argument and emits the skeleton card —
  it does not search for a proof of an open conjecture, run an ATP/SMT solver, or write the polished
  prose. Hand the verified skeleton to a prose author or a proof assistant; hand an open problem
  elsewhere.

## Verify Target

A proof is **done** when: it targets the right quantified claim with a fitting, complete strategy
(A1/A2); steps/coverage/rigor ≥4; `proof-structure-check.py` reports a DAG with no dangling citation
and a reachable goal (B1/B2); `numeric-spotcheck.py` finds no counterexample over a representative
range (B3) (or a proof assistant accepts it — a non-checkable claim is a recorded SKIP, not a pass);
robustness + reproducibility ≥4; and both axes score ≥4 with zero gate failures, landing in the
**SHIPPABLE** quadrant — with the skeleton card + check record ready for a prose author or a proof
assistant. **NOT done** when: the chain is a clean DAG that reaches its goal but the goal is the
converse, a special case, or a dropped-hypothesis weakening of the claim (*valid steps, proves a
different statement*); or it targets the exact claim but a step cites itself / a missing lemma or the
goal is unreachable (*right claim, an invalid or circular step*); or a check was skipped (no
tool/assistant) and reported as a pass; or one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Argument × Verification), the leveled walk with gates, the quadrant, the gate-vs-adversarial-verify doctrine, and the SPECIFY / DECOMPOSE / GRADE workflows |
| `references/argument-axis.md` | **the Argument axis** — claim/quantifier precision and the "proves a different statement" neighbor table, strategy selection, step justification, coverage, rigor, and the **adversarial claim probe** |
| `references/verification-axis.md` | **the Verification axis** — the structural ladder, the structure check, the counterexample search and its asymmetry, when a proof assistant helps, and the boundary/reproducibility reviews; mechanized by both `bin/` tools |
| `references/structure-and-circularity.md` | **any "is this chain valid?" question** — the centerpiece: modeling a proof as a DAG of cited steps, the dangling-citation / circular-reasoning / unreachable-goal failures, why a clean structure check is necessary-not-sufficient; mechanized by `bin/proof-structure-check.py` |
| `references/proof-methods.md` | **picking/grading a method** — direct · induction · contradiction · contrapositive · construction · pigeonhole · cases/WLOG, each with its strategy-risk profile, decisive gate, and common misuse |
| `references/policy.md` | **definition-of-done / handoff** — the 10-point DoD, the proof-skeleton card + check-record shapes, and the seams to a prose author, a proof assistant, and an ATP (which this skill is NOT) |
| `bin/proof-structure-check.py` | **mechanizes B1/B2** — reads a proof skeleton (premises/axioms/steps+`from`/goal); asserts no dangling citation, a DAG (no circular reasoning), and a reachable goal; flags off-path (irrelevant) steps. `<skeleton.json>` · `[--json]` machine-readable report (shared schema) · `selftest` |
| `bin/numeric-spotcheck.py` | **mechanizes B3** — searches a finite integer sample space for a counterexample to a parametric claim via a **safe** AST evaluator (no `eval`); a counterexample is a disproof. Two claim shapes: a boolean `expr`, and a **modular / divisibility / primality** predicate over `f(n)` (`is prime`, `k \| f(n)`, `≡ r (mod m)`) — e.g. `n²−n+41 is prime` dies at n=41 with the mod-41 witness. `<claim.json>` · `"<NL claim>"` · `selftest` |
