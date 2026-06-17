# Worked example — "right claim, circular justification" on ARGUMENT × VERIFICATION

A complete DECOMPOSE → fix → GRADE for one proof, showing the **B2 acyclicity gate** catching a step
that justifies itself in a circle — a defect invisible to a sympathetic read, visible to a graph. The
two skeletons here are checked in and the structure engine actually fails / passes them.

## The artifact

The claim `∀n∈ℤ, n≥0 ⟹ n(n+1) is even` — true, and the right thing to prove. An LLM offers two
confidently-stated steps (`examples/even-sum.red.json`):

- **s1**: "n(n+1) is even *because* the product of consecutive integers is even"
- **s2**: "the product of consecutive integers is even *because* n(n+1) is even"

Each sentence reads as a plausible justification. Ship it?

## DECOMPOSE

**A · Argument** (whole → part) — *the right statement, soundly?*
- **A1 Claim** `[gate]` — `∀n∈ℤ, n≥0 ⟹ n(n+1) even`. Exactly the theorem; no quantifier drift. ✓
- **A2 Strategy** `[gate]` — a case split on n's parity is sound and fitting. ✓

**B · Verification** (part → whole) — *does the argument actually hold?*
- **B1 Well-formed** `[gate]` — premises/axioms/steps shapes parse. ✓
- **B2 Acyclic** `[gate, code]` — model the proof as a citation DAG and run the engine on the spec:

```
$ python3 bin/proof-structure-check.py examples/even-sum.red.json
PROOF structure check — 2 step(s), goal=s2, roots={n_int, n_nonneg, parity}
  dangling     none
  unjustified  none
  cycle        s1 -> s2 -> s1
  goal         UNREACHABLE
  irrelevant   none
proof-structure-check: FAIL — CYCLE: circular reasoning s1 -> s2 -> s1; UNREACHABLE: goal 's2' is not grounded in the premises/axioms
```

**B2 fails.** s1 cites s2 and s2 cites s1 — neither bottoms out at a premise or axiom, so the "goal"
is reachable only *through the cycle*: it is grounded in nothing. The two sentences each look like a
reason, but together they assume what they set out to prove. A failed `[gate]` blocks the B-axis
reviews (B3–B5): no point spot-checking or grading robustness on a chain that never grounds.

## Fix

Re-derive each step from premises/axioms/earlier steps, never from a later one
(`examples/even-sum.green.json`): split on parity from the `parity` axiom, prove each case lands on a
multiple of 2, and let the goal cite the two cases. The graph is now a DAG that flows roots → goal:

```
$ python3 bin/proof-structure-check.py examples/even-sum.green.json
PROOF structure check — 4 step(s), goal=goal, roots={n_int, n_nonneg, parity}
  dangling     none
  unjustified  none
  cycle        none (DAG)
  goal         reachable
  irrelevant   none
proof-structure-check: PASS — citation graph is a DAG, no dangling refs, goal reachable
```

No cycle, no dangling lemma, no off-path step, and the goal grounds in the premises/axioms — the
red→green transition is the proof that the chain holds *as cited*.

## GRADE — two scores, never averaged

- **Argument: 5/5** — right claim, fitting strategy; the steps were the *justification* that was
  broken, not the *aim*.
- **Verification: B2 gate-fail → (after fix) 5/5** — B2 was the only blocker; with the cycle gone,
  the goal is reachable and B3 (numeric spot-check over a range) / B4 / B5 can proceed.

**Quadrant:** the red proof sat in **"right claim, an invalid or circular step"** (Argument passed —
it aimed at exactly the theorem — but Verification's B2 found the chain assumes itself) — *designed
right, built wrong*. The fix is the chain, not the claim. After it: **SHIPPABLE**.

The lesson: "does each step read like a reason?" is the wrong question; "does the chain ground in the
premises without citing itself?" is the right one — and you can't eyeball acyclicity, you build the
graph and watch the gate find the back-edge.
