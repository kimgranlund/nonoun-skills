# Policy — definition-of-done, the card, and the handoff

The reusable artifacts and boundaries: what "done" means for a proof, the shape of the proof-skeleton
card the skill emits, and how this hands off to whatever writes or machine-checks the final proof
without overlapping it.

## Definition-of-done (a proof is shippable when…)

Gated items route to `bin/`; review items are 1–5 judgments. SHIPPABLE = the quadrant top-left.

1. **Right claim (A1)** — the proof targets the **exact** quantified statement (hypothesis,
   conclusion, every ∀/∃), not a converse / dropped-hypothesis / special-case neighbor; stated in one
   sentence with its quantifiers pinned.
2. **Sound strategy (A2)** — the method (direct / induction / contradiction / contrapositive /
   construction / pigeonhole) fits the claim and is structurally complete (base case present, ⊥
   actually derived, witness exhibited).
3. **Justified steps (A3)** — every step has a named justification (prior step / axiom / real theorem
   / definition); no "clearly" / "it follows" load-bearing leap (≥4).
4. **Full coverage (A4)** — all cases and all quantifiers discharged; no unproven lemma leaned on;
   no unexhibited witness (≥4).
5. **Rigorous (A5)** — definitions used as defined; degenerate/boundary cases addressed; no illegal
   move (division by possibly-zero, illegal limit swap) (≥4).
6. **Well-formed ∧ acyclic ∧ reachable (B1/B2)** — `proof-structure-check.py` finds no DANGLING
   citation, no CYCLE (circular reasoning), and the goal is reachable from the premises/axioms.
7. **Survives the checks (B3)** — `numeric-spotcheck.py` finds **no counterexample** over a
   representative sample space (and, where available, a proof assistant accepts it); a non-arithmetic
   claim with no assistant is a **SKIP**, recorded as such — never a silent pass.
8. **Robust (B4)** — boundary/degenerate instances hold (smallest n, empty/singleton, equality edge)
   (≥4).
9. **Reproducible (B5)** — a careful reader/checker can follow each step unaided; every cited result
   is real and applicable (≥4).
10. **Both axes ≥4, zero gate fails, SHIPPABLE quadrant** — reported as two scores, gate failures
    first, with the verified skeleton ready for handoff.

## The proof-skeleton card

The single artifact the skill emits (SPECIFY emits it, DECOMPOSE re-derives it) — it *is* the input to
`proof-structure-check.py`, plus the claim/strategy framing:

```json
{
  "claim": {
    "statement": "for every integer n >= 0, n(n+1) is even",
    "hypothesis": "n is an integer, n >= 0",
    "conclusion": "n(n+1) is even",
    "quantifiers": ["forall n in Z, n >= 0"]
  },
  "strategy": "cases (n even / n odd) — a direct argument per case",
  "steps": [
    {"id": "s1", "from": ["premise"], "statement": "either n is even or n is odd (case split)"},
    {"id": "s2", "from": ["s1"], "statement": "if n even, n=2k, n(n+1)=2k(n+1) is even"},
    {"id": "s3", "from": ["s1"], "statement": "if n odd, n+1 even, n+1=2k, n(n+1)=2nk is even"},
    {"id": "s4", "from": ["s2", "s3"], "statement": "in both cases n(n+1) is even"}
  ],
  "goal": "s4"
}
```

The accompanying **check record** (from the two tools + the adversarial probe):
```
check            tool                      verdict
structure        proof-structure-check     PASS (DAG, no dangling, goal reachable)
counterexample   numeric-spotcheck [0,100] PASS (no counterexample in 101 samples — corroborated)
claim probe      fresh-context skeptic     PASS (targets exactly the stated ∀n claim, no drift)
```

## Handoff — what this skill does NOT do

`proof-decomposer` owns **deductive-argument grading** — design-time + grade, argument-scoped — and
feeds the rest:

- **→ a prose author / a proof assistant**: receives the locked skeleton card and writes the final
  human-readable proof, or encodes it in Lean/Coq/Isabelle for a machine-checked certificate. This
  skill grades the argument's structure and claim; it does not emit the polished proof.
- **not a general theorem prover / decision procedure**: it does **not** search for a proof of an open
  conjecture, run SAT/SMT, or decide validity. It grades a **given** argument — is *this* chain valid,
  and does it prove the *stated* claim? Hand an open problem to an ATP, not here.
- **← a claim source** (a spec, a textbook, an upstream theorem): hands *in* the statement to prove.
  This skill grades a proof against its claim; it does not decide *which* theorem is worth proving.
- **distinct from `research-survey`**: that systematically explores/optimizes a system. This is
  argument validity (right + holds). A proof can be SHIPPABLE here and still leave open questions for
  exploration.

## Governance

- **Skeleton cards are checked in** next to the proof (or the lemma) as the contract of record; they
  version with the argument and are the first thing a reviewer reads.
- **The numeric range tracks the claim** — when the claim changes (a tighter bound, a new variable),
  widen/repin the `numeric-spotcheck` range so the search and the claim can't diverge; always probe
  the **boundary** values explicitly (n=0, n=1, the equality edge).
- **Proof-assistant budget** — encode the load-bearing lemmas in an assistant where the stakes justify
  it; the structure check + counterexample search are the cheap everywhere-gate, a machine-checked
  certificate the targeted proof.
