# The VERIFICATION axis — does the argument actually hold, mechanically?

The Verification axis (B1–B5) grades *mechanism*, bottom-up: from "does every step even cite
something real" to "can a checker reproduce the whole chain." It is the **mechanizable** axis — route
it to the structure check and the counterexample search, and **trust the graph and the
counterexample, not the read-through**. An LLM cannot reliably tell by reading whether a step is
circular or whether a "for all n" claim survives n=41; running the checks is the only evidence.

## The ladder

| Level | Gate | The tool that proves it | The signal |
|---|---|---|---|
| **B1 Well-formed** | `[gate, code]` | `proof-structure-check.py` | every `from` resolves; no dangling citation / undefined symbol; the statement parses |
| **B2 Acyclic** | `[gate, code]` | `proof-structure-check.py` | the citation graph is a **DAG** (no circular reasoning) **and** the goal is **reachable** from premises/axioms |
| **B3 Checks** | `[gate, code]` | `numeric-spotcheck.py` (+ a proof assistant if available) | the claim survives a counterexample search over a finite sample space |
| **B4 Robustness** | review | the claim at the boundary | degenerate/edge instances hold (smallest n, empty/singleton, equality edge) |
| **B5 Reproducibility** | review | a careful reader / a checker | each step is followable unaided; every cited result is real and applicable |

The gates cascade: don't grade robustness (B4) for a chain that cites a missing lemma (B1). A red gate
stops the axis — fix it before reviewing.

## B1/B2 — the structure check (the centerpiece)

`bin/proof-structure-check.py` is the load-bearing gate. You represent the proof as a **proof
skeleton** — premises, axioms, steps with `from` citations, and a `goal` — and it mechanically asserts
the three properties a valid deductive argument must have. The full discipline (how to model a proof
as cited steps, why each property matters, the dangling-citation and circular-lemma failures) is in
`structure-and-circularity.md`; the operational summary:

```json
{
  "premises": ["p1"],
  "axioms":   ["peano"],
  "steps": [
    {"id": "s1", "from": ["p1", "peano"], "statement": "..."},
    {"id": "s2", "from": ["s1"],          "statement": "..."}
  ],
  "goal": "s2"
}
```

```sh
python3 bin/proof-structure-check.py <skeleton.json>   # DANGLING / CYCLE / UNREACHABLE -> nonzero exit
```

- **DANGLING (B1)** — a `from` id that resolves to nothing: an undefined symbol, or a reference to a
  lemma that was never proven. The single most common "looks rigorous, isn't" defect.
- **CYCLE (B2)** — a back-edge in the citation graph: a step that (transitively) cites itself. This is
  **circular reasoning** made mechanical — assuming what you set out to prove.
- **UNREACHABLE (B2)** — the `goal` does not ground out in the premises/axioms. The chain may be a
  clean DAG locally and still float free of its foundations.
- **IRRELEVANT (advisory)** — a step off any path to the goal. Not a failure, but dead weight is often
  the residue of a copy-pasted or wandering argument; worth a look.

A clean structure check is **necessary, not sufficient**: it proves there's no circularity and the
goal is reached *as cited* — it does **not** prove each cited justification is valid (that's A3) or
that the goal is the right goal (that's A1).

## B3 — the counterexample search

`bin/numeric-spotcheck.py` is the cheap, decisive probe on the **claim** (and on key parametric
steps). A quantified claim that *reads* right can be false at one integer you didn't picture; a finite
search finds it:

```json
{"vars": ["n"], "expr": "n*(n+1) % 2 == 0", "range": [0, 100]}
```

```sh
python3 bin/numeric-spotcheck.py <claim.json>   # a counterexample -> nonzero exit (a DISPROOF)
```

It evaluates the claim over the Cartesian product of the integer range with a **safe AST evaluator**
(no `eval`; only literals, the declared vars, `+ - * // % **`, comparisons, `and/or/not`, parens). The
asymmetry is the whole point:

- **A counterexample is a proof of falsity** — the proof is *wrong*, stop and report. (The classic:
  "n² − n + 41 is prime for all n" survives n=0…40 and dies at n=41 — a search to range [0, 41] kills
  it; a sympathetic read does not.)
- **"No counterexample in range" is corroboration, NOT a proof** — it raises confidence and is exactly
  how to *catch* a false claim cheaply, but ∀ over an infinite domain is never settled by a finite
  sample. Report it as "survived N samples", never as "verified".

Where the claim is **not** arithmetic over integers (a topological statement, a claim about reals or
sets), the numeric check doesn't apply — fall to a **proof assistant** (Lean / Coq / Isabelle /
Agda) where one is available: a machine-checked proof is the strongest form of this gate. Absent
both, B3 is a **SKIP** (evidence incomplete), never a pass — like a skipped toolchain gate, a level
with no check has *no evidence* for it.

## B4 Robustness & B5 Reproducibility (reviews)

- **B4** — beyond "the general argument": do the **boundary and degenerate instances** hold? The
  smallest n (often n=0 or n=1, where induction base cases and "for large n" arguments quietly fail),
  the empty set, the singleton, the equality case of a strict inequality, the zero/identity element.
  Run `numeric-spotcheck.py` with the range pinned to the edges; a claim that fails at n=0 has a hole
  the prose skipped.
- **B5** — when a careful reader (or a proof checker) walks each step, can they fill it **unaided**?
  Every inference legible, every cited theorem real and its hypotheses met, no step that only the
  author can complete. A proof that can't be reproduced without the author's private intuition has a
  gap, even if every line "looks" fine.

The output of this axis is the **verification half** of the proof-skeleton card — the structure-check
verdict, the counterexample-search result, and the boundary/reproducibility notes — handed alongside
the claim/strategy half to whatever writes or machine-checks the final proof.
