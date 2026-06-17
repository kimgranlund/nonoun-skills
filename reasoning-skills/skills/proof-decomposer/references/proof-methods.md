# Proof methods — pick by the shape of the claim

Proofs aren't uniform: a `∀n` claim, an existence claim, and a "no such object" claim fail in
different ways and need different methods. This is the "archetype library" — match the method to the
claim's shape, then the two axes get a **strategy-risk profile** (where A2/A3 defects hide for that
method) and a **decisive check** (which gate is the cheapest place to catch them). One proof can chain
methods (induction whose step is a direct argument); take the union of the emphases.

| Method | Fits a claim shaped like… | Strategy-risk (where A2/A3 defects hide) | Decisive check (cheapest catch) |
|---|---|---|---|
| **Direct** | `P ⟹ Q` (constructive implication) | a step that doesn't follow; a hidden case split treated as one case | A3 each link; B1/B2 the chain is well-formed and grounds out |
| **Contrapositive** | `P ⟹ Q`, easier from `¬Q` | **confusing it with the converse** (`Q ⟹ P` — a *different* claim, A1); mis-negating Q | A1 (is `¬Q ⟹ ¬P` really the contrapositive, not the converse?) |
| **Contradiction** | `P` is impossible to violate; "no such object exists" | the proof **never derives ⊥** (it derives "surprising", not "absurd"); assuming `¬P` wrong | A2 (a real ⊥ is reached); B3 (the assumed object's properties are numerically inconsistent) |
| **Induction** (weak/strong) | `∀n ≥ n₀, P(n)` | **missing/wrong base case**; a step that doesn't **use** `P(k)`; strong induction needed but weak used | B4 the **base case** (run `numeric-spotcheck` at n=n₀); A4 the step invokes the hypothesis |
| **Construction** | `∃x, P(x)` | the witness is **asserted to exist, not exhibited**; the exhibited witness doesn't satisfy `P` | A4 (witness exhibited); B3 (the witness *numerically* satisfies `P`) |
| **Pigeonhole** | `∃` a collision among more items than boxes | miscounting items vs boxes; the boxes aren't exhaustive/disjoint | A4 (the counting is exact); B3 (a small instance collides as claimed) |
| **Cases / WLOG** | claim splits into a finite partition | a **non-exhaustive** partition; a "WLOG" that actually **loses generality** | A4 (the cases cover the whole domain; the symmetry the WLOG claims is real) |

## How a method shifts the walk

- **Where the gate bites.** Induction lives or dies on the **base case** (B4 / `numeric-spotcheck` at
  n₀) and on the step *using* the hypothesis (A4); a construction on the **witness** (exhibited at A4,
  checked at B3); a contradiction on actually reaching **⊥** (A2). Spend the verification budget there.
- **Where the claim probe aims.** Contrapositive proofs attract the **converse confusion** (A1) —
  point the adversarial claim probe at "is `¬Q ⟹ ¬P` the contrapositive or did it slide to `Q ⟹ P`?".
  Cases/WLOG proofs attract the **dropped-case / lost-generality** drift (A4).
- **Which structural defect dominates.** "By a standard result" and "it is well known" — the
  **DANGLING** citation — cluster in proofs that lean on background theorems (analysis, algebra). A
  proof that "reduces P to P′" and then "reduces P′ to P" is the textbook **CYCLE**. Point
  `proof-structure-check.py` accordingly.

## Common misuse to flag at A2

- **Induction with no base case** — the step `P(k) ⟹ P(k+1)` can be perfectly valid and prove
  *nothing* without a true base; "all horses are the same color" is exactly this. A2 gate failure.
- **A "contradiction" that isn't** — assuming `¬Q`, deriving something false-*looking* but not ⊥, then
  declaring victory. The contradiction must be an actual `X ∧ ¬X`.
- **Affirming the converse** — proving `Q ⟹ P` and calling it a proof of `P ⟹ Q`. The single most
  common "valid steps, different statement" defect; it passes the structure check and fails A1.
- **WLOG that loses generality** — "without loss of generality assume x < y" when the case x = y (or
  the asymmetric case) behaves differently and is never handled. A4 coverage failure.
- **Vacuous / trivial proof mistaken for general** — proving `P ⟹ Q` only in the case P is false (or Q
  always true), then claiming the general implication. A1/A4.

## The cross-method rule

Whatever the method, the **theorem statement** (A1) is the crossing seam and the **goal** the
structure check must reach. The method only tells you **where the defect is most likely to hide** and
**which gate is the cheapest place to catch it** — it doesn't change the two-axis method, it focuses
it: pick the method (A2), build the skeleton, run the structure check (B1/B2), search for a
counterexample (B3), and probe the claim adversarially (A1).
