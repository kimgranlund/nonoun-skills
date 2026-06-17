# Structure & circularity — why a persuasive proof is evidence of nothing

This is the centerpiece. The whole skill exists because an LLM (and a hurrying human) produces
confidently-stated steps that are individually plausible but **assume what they prove** (circular
reasoning), **lean on a lemma that was never proven** (a dangling citation), or form a clean local
chain that **never actually reaches the goal** from the premises. None of these is visible to a
sympathetic read — all of them are visible to a graph. VERIFICATION's B1/B2 gate is "the citation
graph is well-formed and acyclic and the goal is reachable." This file is that discipline, and
`bin/proof-structure-check.py` is its mechanization.

## The one principle

> **A proof is a directed graph of cited steps, not a paragraph.** Each step is a node; each
> justification is an edge to a prior step, an axiom, or a premise. A valid deductive argument is a
> **DAG rooted in the premises/axioms with the goal reachable from them.** Persuasive prose can hide a
> back-edge (circularity) or a dangling edge (an unproven lemma); the graph cannot.

Two corollaries:
- **Reading it sympathetically is not checking it.** The question is never "is this convincing?" but
  "does every step cite something that exists, does nothing cite itself, and does the goal ground out
  in the premises?"
- **The proof is the structure check, not the inspection.** Build the skeleton and run it; a cycle or
  a dangling citation is mechanical, not a matter of taste.

## Modeling a proof as a skeleton

You convert the proof into a JSON **proof skeleton** — the input to `proof-structure-check.py` and the
core of the proof-skeleton card (`policy.md`):

```json
{
  "premises": ["p1", "p2"],
  "axioms":   ["peano", "ext"],
  "steps": [
    {"id": "s1", "from": ["p1", "peano"], "statement": "n+0 = n by the additive identity"},
    {"id": "s2", "from": ["s1"],          "statement": "..."},
    {"id": "s3", "from": ["s2", "p2"],    "statement": "the conclusion"}
  ],
  "goal": "s3"
}
```

- **premises / axioms** are the **roots** — the things granted without proof (the hypotheses of the
  theorem, the axioms of the theory, previously-established theorems you're allowed to cite).
- each **step** has a unique `id`, a `from` list of the ids it's derived from, and its `statement`.
- **goal** is the id of the step that *is* the conclusion — the theorem statement, the thing the
  Argument axis claims and the Verification axis must reach (the **crossing seam**).

Recovering this skeleton from prose **is** the decomposition: every "since … we have …", "by Lemma 3",
"therefore" becomes an edge; every "assume", "let", "by hypothesis" becomes a root or a step.

## The failure taxonomy (what `proof-structure-check.py` catches)

Static, cheap, deterministic — the structural defects a sympathetic read waves past:

| Kind | Smell | Why it's fatal |
|---|---|---|
| **DANGLING** | a `from` id resolves to nothing | the step cites an **undefined symbol** or an **unproven lemma** ("by Lemma L" — and L is never stated). The proof rests on a thing that isn't there. |
| **CYCLE** | a back-edge: `s1 from s2`, `s2 from s1` (or any loop) | **circular reasoning** — the step (transitively) assumes itself. "A because B, B because A" reads fine and proves nothing. |
| **UNREACHABLE** | the `goal` doesn't ground out in the roots | the chain floats free of the premises — a beautiful argument for a conclusion the hypotheses never reach. (A circular cluster is *also* unreachable: it never grounds.) |
| **IRRELEVANT** (advisory) | a step on no path to the goal | dead weight — often the residue of a wandering or copy-pasted argument; not fatal, but a tell. |

Run it: `python3 bin/proof-structure-check.py <skeleton.json>` — nonzero exit on any of the three
fatal kinds; the advisory IRRELEVANT is printed but does not fail.

### Why each property is exactly the right check

- **No dangling citation = the lemma exists.** The most common "rigorous-looking, isn't" defect is an
  appeal to an unproven intermediate ("it is well known that…", "by a standard result", "by Lemma 4"
  with no Lemma 4). In the skeleton it's a `from` id with no node — caught mechanically. *Either prove
  the lemma (add it as a step that grounds out) or cite a real, applicable theorem (add it as an
  axiom/root).*
- **Acyclic = no circular reasoning.** Assuming the conclusion is the oldest fallacy, and the hardest
  to see in prose because each local step looks valid. In the graph it's a back-edge — a step on a
  cycle can never ground out in the premises, which is *why* a cycle and an unreachable goal often fire
  together.
- **Goal reachable = the chain reaches the conclusion.** A proof can be a clean DAG and still not prove
  the theorem — if the goal step's dependencies don't trace back to the actual premises/axioms, it's a
  proof of something *not entailed by the hypotheses*. (This is the structural shadow of the A1 "proves
  a different statement" failure — but note: reachability alone does **not** catch A1, because the
  *wrong* goal can be perfectly reachable. See the cross-axis rule below.)

## The deeper smells (judgment, beyond the check)

The structure check catches the mechanical cases; these need the Argument axis's read:

- **The valid justification that's actually invalid.** `s3 from s2` with a clean edge — but s2 does
  *not* in fact imply s3 (a misapplied theorem, an illegal algebra step). The graph says "s3 cites
  s2"; only A3 says whether s2 ⟹ s3 *holds*. The check proves the *shape*, not the *soundness* of each
  link.
- **The right shape, wrong goal.** A DAG that grounds out and reaches `goal` — but `goal`'s statement
  is the *converse* of the claim, or a *special case*. The structure is impeccable; the proof is of a
  neighbor. This is the A1 gate's job — the structure check will happily pass it.
- **The "obviously" that hides a sub-proof.** A single step whose `from` is one premise but whose
  `statement` is a leap of three non-trivial inferences. The graph sees one edge; A3/A5 see a gap.
  Decompose suspicious steps into sub-steps until each edge is a single defensible inference.

## What a real (structurally sound) proof skeleton looks like

- Every `from` id resolves to a **defined** premise, axiom, or earlier step (no dangling).
- The graph is a **DAG** — no step transitively cites itself (no circular reasoning).
- The **goal grounds out** in the premises/axioms through the `from` edges (reachable).
- **No irrelevant steps** — every step is on some path to the goal (lean; nothing computed for show).
- Each edge is a **single defensible inference** — a step that needs three inferences is three steps.

## How this scores

B1/B2 is **well-formed ∧ acyclic ∧ reachable**:
- B1 = `proof-structure-check.py` finds **no DANGLING** citation (every step rests on something real);
- B2 = it finds **no CYCLE** (no circular reasoning) **and** the goal is **reachable** (the chain
  reaches the conclusion from the premises).

A proof whose prose is persuasive but whose skeleton has a cycle or a dangling lemma is **not**
B1/B2-passing — it's the *right claim, invalid/circular step* quadrant, and the corrective is on the
chain (prove the lemma, break the cycle), not the score. And remember the cross-axis rule: a **clean**
structure check is the floor, not the ceiling — A1 (right goal?) and A3 (each link valid?) are the
checks the graph cannot do for you.
