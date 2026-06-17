# The ARGUMENT axis — does it prove the right statement, soundly?

The Argument axis (A1–A5) grades *intent*, top-down: from the proposition the proof must establish to
the rigor of its hardest step. This is the axis the structure check **cannot see** — a citation graph
is silent on "this proves the converse." It is also the axis LLMs fail silently on (confident,
plausible, *aimed at the wrong target*), so it carries an **adversarial claim probe**, not just a
checklist.

## A1 · Claim `[gate]`

Write the **exact** statement the proof must establish — *before* reading a single step — in the form:

> **Hypothesis** (what is assumed) ⟹ **Conclusion** (what is asserted), with **every quantifier**
> pinned (∀x∈S / ∃y / ∀ε>0 ∃δ>0 …) and the **domain** of each variable named.

Then ask: does the argument target *that*, or a **neighbor** it's easy to drift to? The neighbors —
the "proves a different statement" failure — are the whole reason this is a gate:

| Drift | What was proved instead | Tell |
|---|---|---|
| **Converse** | `Q ⟹ P` instead of `P ⟹ Q` | the proof "starts from the conclusion" |
| **Dropped hypothesis** | the theorem minus a premise — a *stronger, false* claim, or a *weaker, easier* one | a hypothesis named in A1 is never used in any step |
| **Quantifier swap** | ∃ where ∀ was claimed (or the order ∀∃ ↔ ∃∀ flipped) | "there is an x" doing the work of "for all x" |
| **Special case** | the claim at one value, sold as the general | a fixed n, a chosen witness, "without loss of generality" that *loses* generality |
| **Strengthened conclusion** | a claim the proof doesn't actually reach | the final step asserts more than the chain supports |

- A hypothesis that is **never used** is a red flag in both directions: either it was needed and the
  proof has a gap, or the theorem is true without it (a weaker claim was proved than stated).
- **Gate:** if the proof targets a neighbor, stop — every level below grades a proof of the wrong
  thing. Re-state the claim and re-decide whether the proof needs repair or the claim needs correcting.

## A2 · Strategy `[gate]`

The proof method must be **sound** and **fit the claim**. The catalogue and the fit rules live in
`proof-methods.md`; the gate here is structural:

- **Direct** — `P ⟹ Q` by a forward chain. Fits when the implication is constructive.
- **Contrapositive** — prove `¬Q ⟹ ¬P` (logically equivalent to `P ⟹ Q`). A *valid* substitution;
  not to be confused with the converse (a *different* statement — see A1).
- **Contradiction** — assume `P ∧ ¬Q`, derive ⊥. The gate: a contradiction proof must actually reach
  a contradiction (⊥), not merely something surprising.
- **Induction** — base case(s) **and** an inductive step that uses the hypothesis. The gate: a missing
  or wrong base case, or a step that doesn't invoke `P(k) ⟹ P(k+1)`, is broken before any algebra.
- **Construction** — exhibit the witness for an ∃, and prove it satisfies the property. The gate: the
  witness must be *exhibited*, not merely asserted to exist.

A misapplied method is an A2 gate failure independent of the steps' local validity: induction with no
base case, a contradiction that never derives ⊥, a "WLOG" that quietly drops cases.

## A3 · Steps `[review]`

Each step must **follow** from prior steps, axioms, or cited theorems, with a **named** justification:

- Every inference has a *reason*: a prior step-id, an axiom, a named theorem, or a definition. "It
  follows", "clearly", "obviously", and "it is easy to see" are **not** justifications — they are the
  places gaps hide. Score down each unjustified leap.
- A cited external theorem must be **real and applicable** (its hypotheses met here). A misremembered
  or misapplied theorem is a broken step that *reads* fine.
- The justification graph is what the Verification axis mechanizes (B1/B2) — A3 grades whether each
  *named* justification is actually *valid*, which the graph cannot.

## A4 · Coverage `[review]`

All cases and all quantifiers **discharged** — LLMs (and tired humans) leave the hard case implicit:

- **Case analysis** is exhaustive and the cases are genuinely covered (not "the rest are symmetric"
  when they aren't; not three of four cases of a parity argument).
- **Every ∀** ranges over its whole domain (including the boundary value); **every ∃** has an
  exhibited or constructed witness.
- **No unproven lemma** is leaned on — a "by a standard argument" or "one can show" that is load-
  bearing is a gap, not a step. Either prove it or cite a real result.

## A5 · Rigor `[review]`

The difference between *convincing* and *valid* — the degenerate cases and definition discipline:

- **Definitions are used as defined** — not a colloquial cousin (open vs closed, ≤ vs <, "limit" used
  loosely).
- **Degenerate / boundary instances** are addressed: n=0, the empty set, the singleton, equality in a
  strict inequality, the all-zero vector, the trivial group.
- **No illegal move**: division by a quantity that may be zero, a limit/sum/integral swap without
  justification, a "for large enough n" that hides a dependence, an `=` that should be `≤`.

## The adversarial CLAIM probe (route A1 to a skeptic, not the author)

The dangerous defect — *valid steps, proves a different statement* — lives here, and it is **not**
deterministically gateable (the structure check passes a proof of the converse). Verify it the way
`deep-research` verifies claims: **in a fresh context, adversarially.**

- Prompt a separate reviewer (not the one that wrote or read the proof with approval): *"Here is the
  claimed theorem (with its exact quantifiers) and the proof. Find a way the proof targets a*
  *NEIGHBOR of the claim — the converse, a dropped hypothesis, a quantifier swap, a special case sold*
  *as the general. Default to 'it proves a neighbor' and search for which one."*
- A verifier sharing the author's framing inherits its drift and rubber-stamps. Separation is the
  point: the structure check tells you the chain is sound; the skeptic tells you whether it ends at
  the right proposition.
- Feed any drift back as the A1 corrective: re-state the theorem to what was *actually* proved, then
  decide if that's the claim you wanted.

The output of this axis is the **claim + strategy** half of the proof-skeleton card — the artifact
GRADE re-derives and SPECIFY emits, and the thing the structure check's `goal` must reach.
