# Definition-of-done, the cross-check, and the seams

This is the handoff contract — when a charter is *done*, how it cross-checks against the architecture,
and the boundaries to the neighbours. Load it in GRADE to close out, or when deciding "is this someone
else's job?".

## The 10-point definition-of-done

A charter is **GOVERNABLE** when all ten hold (gate failures are zeros, not deductions):

**AIM (intent) — axis A:**

1. **A diagnosis that faces the challenge** — not a goal list (A1 gate; `NO_DIAGNOSIS` clean).
2. **Characteristics strictly ranked** — a real priority order that forces the trade-offs (A2 gate;
   `UNRANKED` clean).
3. **Outcomes, not outputs** — every goal is a behavior change, not a feature shipped (A3 ≥ 4;
   `OUTPUT_NOT_OUTCOME` clean).
4. **Coherent and bounded** — goals don't fight; non-goals are explicit (A4 ≥ 4; `CONTRADICTION` /
   `NO_NONGOALS` clean).
5. **Falsifiable success** — acceptance criteria are a real definition-of-done that capture the goals
   (A5 ≥ 4).

**MEASURABILITY (mechanism) — axis B (gated by `charter-check.py`):**

6. **Diagnosis present** (B1 gate).
7. **Every goal carries a metric + numeric threshold + window** (B2 gate; `FLUFF` / `UNMEASURABLE_KPI`
   / `VACUOUS_ACCEPTANCE` clean).
8. **A strict integer ranking** (B3 gate; `UNRANKED` clean).
9. **Scope bounded, no literal contradictions** (B4 ≥ 4).

**Both axes:**

10. **Two scores, never one; Goodhart-probed.** Axis A and axis B reported separately with the quadrant
    named; the top metrics **survived a fresh-context surrogate/Goodhart probe** (*precise-but-wrong*
    ruled out).

**NOT done** when: the goals are right but unmeasurable (*vague but right*); or crisply measured but
aimed at the wrong outcome / a surrogate metric (*precise but wrong*); or a gate was skipped (linter not
run) and reported as a pass; or one blended score is reported.

## The cross-check — the seam to architecture-decomposer

The charter is the OUTSIDE-IN doc; `architecture-decomposer`'s contract card is the INSIDE-OUT doc. The
**cross-check** (run in a *third* fresh context — neither author grades the seam) asks the one question
neither plane can ask itself:

- **Coverage:** every *ranked* characteristic has a **named structural mechanism** in the architecture (a
  rank-1 scalability goal → a stated bottleneck + an independent scale path; a security goal → a trust
  boundary). An unserved high-rank goal is a seam finding routed to the **architecture**.
- **Contradiction:** no architectural choice violates a charter **principle** (a "no synchronous calls
  on the hot path" principle vs. a synchronous dependency in the contract). Routed to the **architecture**.
- **Infeasibility:** if a goal can't be met by any structure, that's routed *back to the charter* (the
  aim was wrong or unrankable) — never patched silently at the seam.

This is the 2×2's GOVERNABLE/SHIPPABLE cell. In the `nonoun-plugins` two-plane orchestrator
(`docs/designs/two-plane-orchestrator.md`) the cross-check is a gate, and a charter change marks the
architecture **stale** (regenerate + re-cross-check).

## The seams — what is *not* this skill

| When the job is… | It belongs to | Not here because |
|---|---|---|
| design the **technical structure** that meets the goals | `architecture-decomposer` | that's the INSIDE-OUT plane; this skill grades the goals the structure is held to |
| **judge the product idea's merit / strategy** by expert taste | `product-forge` (council, methodology) | this skill grades whether the charter is *governable & falsifiable*, not whether the bet is *good* (Marty C./Teresa T./Rumelt-as-critic live there) |
| grade a **single unit of code** against its spec | `code-decomposer` | the charter is upstream of code — the goals of the whole, not one function's contract |
| **make illegal states unrepresentable** in the data model | `type-decomposer` | the charter sets the goals; the model is one INSIDE-OUT realization |
| **orchestrate** the two planes in isolated contexts + maintain the docs over time | the two-plane orchestrator (`nonoun-plugins`) | orchestration/isolation is an agent property; a skill teaches the method, an agent enforces it |

The clean test: if the question is **"is this a governable, falsifiable statement of what we're trying to
do and how we'll know it's good?"** it's this skill. If it's **"is this the right bet?"** it's
`product-forge`. If it's **"what structure meets it?"** it's `architecture-decomposer`.
