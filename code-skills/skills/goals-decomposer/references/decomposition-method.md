# The goals-decomposer method — two crossing axes over a goals/charter doc

A goals / charter / PRD doc is the **OUTSIDE-IN plane** of planning a system: *what are we trying to do,
and how will we know it's good?* It is the peer of `architecture-decomposer` (the INSIDE-OUT plane) —
together they are the two planes you reason on when planning or reviewing any system (`HOWTO.md` §1).
This skill grades the **charter doc itself** — not the product idea's merit (that's taste, and
`product-forge`'s critic councils own it), but whether the doc is a *governable, falsifiable* statement
of intent that a downstream architecture can actually be held to.

Like every decomposer, a charter is **correct on two independent axes that walk the same hierarchy in
opposite directions** — the charter hierarchy being `diagnosis → ranked characteristics → principles &
non-goals → acceptance criteria`.

- **A · AIM · whole → part** grades the **intent**: is the diagnosis real, are these the *right* goals,
  strictly ranked, coherent, and bounded? *"Are we aiming at the right thing?"* Judgment — where an LLM
  is strong, and where it confidently rationalizes a goal set that doesn't face the actual challenge.
- **B · MEASURABILITY · part → whole** grades the **mechanism**: is every goal *falsifiable* — a metric
  with a threshold and a window, a checkable acceptance predicate, a strict priority order, no
  contradictions? *"Can you provably tell when it's met?"* This is arithmetic, not taste — so it is
  **routed to a deterministic, self-tested gate**, `bin/charter-check.py`.

## The crossing — and the quadrant

The two axes **cross at the individual goal** — a characteristic or acceptance criterion is *both* a
claim about what matters (the aim) and a checkable predicate (the measure). The two defects are
**opposite**:

- **Vague but right** (high A, low B): the right aims, expressed as fluff — *"be fast, be reliable, be
  scalable"* with no metric, no threshold, no rank. You agree with it and can't be held to any of it.
  Rumelt's *"a dog's dinner of goals."*
- **Precise but wrong** (high B, low A): a crisp, fully-measured KPI dashboard pointed at the **wrong
  outcome** — optimizing a surrogate metric, measuring outputs not outcomes, gaming what's easy to count
  (Goodhart's law). Every number is green while the thing that mattered rots.

Opposite fixes — sharpen-and-measure vs. re-diagnose-and-re-aim — so you **score the two axes
separately, never averaged**, and name the quadrant.

|  | **B low — unfalsifiable** | **B high — measurable** |
|---|---|---|
| **A high — right aim** | *vague but right* — give every goal a metric + threshold + rank | **GOVERNABLE** |
| **A low — wrong aim** | broken both ways — re-diagnose from the challenge | *precise but wrong* — the metric doesn't capture the outcome (Goodhart) |

## The doctrine — a charter is a contract, not a wish

- **Goals without a diagnosis is bad strategy** (Rumelt). A charter that lists aspirations but never
  names *the challenge being faced* gives the architecture nothing to be coherent against. `NO_DIAGNOSIS`
  is a gate fail.
- **If everything is a priority, nothing is.** The characteristics (the *-ilities*) must be a **strict
  order** — a real ranking forces the trade-offs the architecture will have to make. Ties, especially at
  the top, are `UNRANKED`. *Everything is a trade-off* — naming and ranking the trade-offs is the charter's job.
- **A goal you can't measure is fluff, not a goal.** Every characteristic needs a **metric + threshold +
  window**; every acceptance criterion a **checkable predicate**. `FLUFF` / `UNMEASURABLE_KPI` /
  `VACUOUS_ACCEPTANCE` route to `charter-check.py`.
- **Measurable is necessary, not sufficient — beware Goodhart.** A green gate proves the charter is
  *falsifiable*, never that the metric *captures the outcome*. The dangerous quadrant (*precise but
  wrong*) is on the AIM side and gets an **adversarial check in a fresh context**: for each top metric,
  could you move it without delivering the outcome? Is it a surrogate? Are you measuring an output
  ("ship X") instead of an outcome ("users do Y in half the time" — the build trap)?

## Staged isolation — this skill authors the OUTSIDE-IN doc *first*

In the two-plane workflow (`HOWTO.md` §1, and `nonoun-plugins`'s two-plane orchestrator), the charter is
produced and graded **before any architecture is in context** — so the goals can't be quietly bent to
fit a structure that doesn't exist yet. The charter then becomes the **read-only contract** the
INSIDE-OUT work (`architecture-decomposer`) honors; the **cross-check** — does the architecture serve
the ranked goals? — happens in a third fresh context. goals-decomposer owns the first stage and the
charter's half of that cross-check.

## The four modes

- **DECOMPOSE** — read an existing goals doc / PRD → extract a charter card → run `charter-check.py` →
  grade both axes. *"Is this PRD actually governable?"*
- **DESIGN** — author a charter top-down: name the diagnosis → rank the characteristics → set
  principles & non-goals → write falsifiable acceptance criteria → emit a charter card.
- **GRADE** — score both axes, gates before reviews, two scores + the quadrant, never averaged.
- **CROSS-CHECK** — given a *validated* charter and an `architecture-decomposer` blueprint, grade the
  seam: does each ranked characteristic have a structural mechanism, and does any architectural choice
  violate a principle? (See `references/policy.md`.)

Read `references/aim-axis.md` and `references/measurability-axis.md` next, `references/the-charter-schema.md`
for the card the gate consumes, and `references/policy.md` for the definition-of-done and the seams.
