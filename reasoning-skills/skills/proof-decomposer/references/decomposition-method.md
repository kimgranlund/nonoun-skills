# The two-axis method — ARGUMENT × VERIFICATION

A proof is **correct on two independent axes that walk the same hierarchy in opposite directions** —
the decomposer seam the layout-, mermaid-, component-, and code-decomposers apply to space, diagrams,
components, and code, here applied to a deductive argument (a proof, or any rigorous chain of
inference).

- **Argument · whole → part** grades the **intent**: the claim it proves → its strategy → its steps →
  its case coverage → its rigor. *"Does it prove the right statement, soundly?"*
- **Verification · part → whole** grades the **mechanism**: every step is well-formed → the citation
  graph is acyclic and the goal is reachable → the claim survives numeric checks → it's robust at the
  boundary → a reader can reproduce it. *"Does the argument actually hold, mechanically?"*

They **cross at the theorem statement** — the statement is *both* the thing the Argument axis claims
(the exact quantified proposition) *and* the goal the Verification axis's checker must reach from the
premises and axioms. A claim with no reachable goal is hand-waving; a reachable goal that proves a
*different* claim is a proof of the wrong thing.

That crossing is the whole technique. A proof can be:

- **valid steps, proves a different (often weaker) statement** — the citation graph is a clean DAG,
  the goal is reached, every step follows — but it proved the **converse**, dropped a **hypothesis**,
  or let a **quantifier drift** (∀ became ∃, or "for some" was sold as "for all"). VERIFICATION
  passes, ARGUMENT fails. *The dangerous one — a correct-looking proof of a neighbor of the claim.*
- **right claim, an invalid or circular step** — it targets exactly the stated theorem, but a step
  **cites itself** (assumes what it's proving), **cites a lemma never proven**, or the **goal isn't
  reachable** from the premises. ARGUMENT passes, VERIFICATION fails. *Plausible prose, broken chain.*

Opposite defects, opposite fixes — so you **score and report the two axes separately, never
averaged.** An averaged "3/5" hides which one you have, and they need opposite work (re-state and
re-quantify the claim, vs repair the inference chain).

## The leveled walk

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Argument** | whole → part | **A1** Claim `[gate]` → **A2** Strategy `[gate]` → **A3** Steps → **A4** Coverage → **A5** Rigor | "Does it prove the *right statement*, soundly?" |
| **B · Verification** | part → whole | **B1** Well-formed `[gate, code]` → **B2** Acyclic `[gate, code]` → **B3** Checks `[gate, code — integer-arithmetic claims; else SKIP / proof-assistant]` → **B4** Robustness → **B5** Reproducibility | "Does the argument *actually hold*, mechanically?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** — a failure cascades and BLOCKS the reviews below it on
that axis (you can't grade the steps of a proof of the wrong claim, or the rigor of a chain that
cites a missing lemma). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable proof is **≥4 on every
review with zero gate failures**, reported as two separate axis scores plus the quadrant cell.

These gates route to code, never to a sympathetic read:
- **B1/B2 structure** → `bin/proof-structure-check.py` (dangling citation, cycle, goal-reachability).
  Always applies. See `structure-and-circularity.md`.
- **B3 checks** → `bin/numeric-spotcheck.py` (counterexample search over the claim) — **only for
  parametric integer-arithmetic claims**. Most real proofs (topology, reals/sets, non-arithmetic
  logic) cannot use it, so B3 is *usually a recorded SKIP* (or a proof-assistant gate where one is
  installed) — a SKIP is "no evidence", never a failure. See `verification-axis.md`.

### A · Argument (whole → part)

- **A1 Claim `[gate]`** — does the proof target the **exact** statement, correctly quantified? Name
  the hypothesis, the conclusion, and every ∀/∃ *before* reading the steps. The #1 silent failure is
  proving a neighbor: the converse, the contrapositive sold as the original, a special case sold as
  the general, a dropped hypothesis. Wrong claim ⇒ everything below is a proof of the wrong thing.
- **A2 Strategy `[gate]`** — is the method **sound and fitting**: direct, induction, contradiction,
  contrapositive, construction, pigeonhole? A method misapplied (induction with no base case, a
  contradiction that never derives ⊥) is structurally broken before any step. See `proof-methods.md`.
- **A3 Steps `[review]`** — does each step follow from prior steps, axioms, or cited theorems, with a
  *named* justification? No step asserted by intimidation ("clearly", "obviously", "it follows").
- **A4 Coverage `[review]`** — are **all cases** and **all quantifiers** discharged? No unhandled
  case, no unproven lemma leaned on, no "the other case is symmetric" that isn't, no ∃-witness left
  unexhibited.
- **A5 Rigor `[review]`** — are definitions used **as defined**; are degenerate / boundary / edge
  instances (n=0, the empty set, equality in a strict inequality) addressed; is there no division by a
  possibly-zero quantity, no illegal limit swap, no hand-wave at the hard step?

### B · Verification (part → whole)

- **B1 Well-formed `[gate, code]`** — does every step **cite** prior step-ids / axioms (no undefined
  symbol, no dangling reference to a lemma that doesn't exist), and does the statement parse? Routed
  to `bin/proof-structure-check.py`.
- **B2 Acyclic `[gate, code]`** — is the citation graph a **DAG** (no circular reasoning — no step
  that, transitively, assumes itself), and is the **goal reachable** from the premises/axioms through
  the citation edges? Routed to `bin/proof-structure-check.py`.
- **B3 Checks `[gate, code]`** — *for parametric integer-arithmetic claims:* does the claim (and its
  key steps, where parametric) **survive a counterexample search** over a finite sample space, via
  `bin/numeric-spotcheck.py`? For any non-arithmetic claim this tool does not apply — B3 is a recorded
  **SKIP** (or a proof-assistant gate: Lean / Coq / Isabelle, the stronger form where available),
  which is the common case and not a failure.
- **B4 Robustness `[review]`** — do **boundary and degenerate instances** of the claim hold (the
  smallest n, the empty/singleton case, the equality edge)? A claim that fails at n=0 has a hole the
  prose may have skipped.
- **B5 Reproducibility `[review]`** — can a careful reader (or a checker) follow **each step unaided**,
  with every inference legible and every cited result real? A step only the author can fill is a gap.

## The opposite-defect quadrant

```
                  B · VERIFICATION passes    B · VERIFICATION fails
A · ARGUMENT  ┌────────────────────────┬────────────────────────┐
   passes     │      SHIPPABLE         │  right claim, an        │
              │  (≥4 every review,     │  invalid or circular    │
              │   zero gate fails)     │  step — proves the      │
              │                        │  exact statement, but a │
              │                        │  step cites itself / a  │
              │                        │  missing lemma / goal   │
              │                        │  unreachable            │
              ├────────────────────────┼────────────────────────┤
A · ARGUMENT  │ valid steps, proves a  │       REBUILD           │
   fails      │ DIFFERENT / weaker     │                         │
              │ statement — clean DAG, │                         │
              │ goal reached, but the  │                         │
              │ converse / a dropped   │                         │
              │ hypothesis / quantifier│                         │
              │ drift                  │                         │
              └────────────────────────┴────────────────────────┘
```

The quadrant **names the fix**: top-right needs the inference chain repaired (a missing lemma proven,
a cycle broken); bottom-left needs the **claim** re-stated and re-quantified — work the structure
check **cannot see**, because the graph is clean; it just terminates at the wrong proposition. Report
the cell, not an average.

## The doctrine — an argument's persuasiveness is not its validity

This is why the skill earns its place (and why it's outsized for an LLM author):

- **You cannot certify a proof by reading it sympathetically.** Confidently-stated, individually-
  plausible steps are exactly the LLM failure mode, and exactly what a sympathetic read rubber-stamps.
  Route VERIFICATION to a **structure check** (citation integrity + acyclicity + goal-reachability)
  and a **numeric counterexample search** — `trust the graph and the counterexample, not the prose`.
- **"Proves a different statement" is NOT deterministically gateable.** It lives on the ARGUMENT side:
  the steps are valid and the goal is reached, but the *target* is a neighbor of the claim. The
  structure check passes a proof of the converse just as happily as a proof of the theorem — so probe
  the **claim adversarially**: in a fresh context, ask *"does this prove EXACTLY the quantified
  statement, or a weaker/converse/special-case neighbor?"* A verifier sharing the author's framing
  inherits its drift (the `deep-research` adversarial-verify move).
- **A clean DAG is necessary, not sufficient.** B2 proves there's no circular reasoning and the goal
  is reached *as cited* — it does not prove each cited justification is actually valid (that's A3) or
  that the goal is the right goal (that's A1). Gate first, then read for soundness.

## Modes

- **SPECIFY** (before proving) — state the **claim** precisely (hypothesis, conclusion, every ∀/∃),
  pick a fitting **strategy**, and plan the **proof skeleton** (the steps + their intended citations +
  the goal). Emit a proof-skeleton card.
- **DECOMPOSE** (an existing proof) — recover the claim + strategy (A1/A2), build the skeleton, run
  `proof-structure-check.py` (B1/B2) and `numeric-spotcheck.py` (B3), then score the reviews. Emit the
  skeleton card + a gap list (e.g. *"clean DAG, but the claim is the converse"* or *"right claim, but
  s4 cites lemma-L which is never proven"*).
- **GRADE** — score both axes, gates first (run both checks + the adversarial claim probe), place in
  the quadrant, name one corrective per failure.

## Walk order (do not skip)

1. **A1 Claim / A2 Strategy** — write the exact quantified statement and name the method. Wrong claim
   or unfit strategy ⇒ stop, re-spec; do not grade steps of a proof of the wrong thing.
2. **B1/B2 Structure** — build the skeleton, run `proof-structure-check.py`. A dangling citation,
   a cycle, or an unreachable goal ⇒ fix the chain before reviewing (you can't grade rigor of a chain
   that cites a missing lemma).
3. **B3 Checks** — run `numeric-spotcheck.py` over the claim (and key parametric steps). A
   counterexample is a **disproof** — the proof is wrong, stop. (A proof assistant is the stronger
   gate where available.)
4. **A1 adversarial probe** — in a fresh context, try to show the proof targets a *neighbor* of the
   claim (converse, dropped hypothesis, quantifier drift). Any drift is an A1 failure.
5. **Reviews** — A3–A5 then B4–B5, 1–5 each. Below 4 ⇒ name the single corrective.
6. **Report** — two axis scores, the quadrant cell, gate failures first; hand the verified skeleton
   to the consumer (a peer that writes the final proof prose, or a proof assistant).
