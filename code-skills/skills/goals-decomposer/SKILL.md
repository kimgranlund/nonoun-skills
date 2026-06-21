---
name: goals-decomposer
description: >
  Decompose, design, grade, or cross-check a goals / charter / PRD doc — the OUTSIDE-IN peer to
  architecture-decomposer — on two crossing axes: AIM (diagnosis → ranked -ilities →
  principles/non-goals → falsifiable acceptance; Rumelt's kernel, outcomes over outputs) and
  MEASURABILITY (every goal has a metric+threshold+window, a strict priority order, no contradictions),
  scored separately so a vague-but-right charter can't hide a precise-but-wrong one. Doctrine: a charter
  is a CONTRACT, not a wish — goals with no diagnosis is bad strategy; if everything is P0, nothing is;
  an unmeasurable goal is fluff. MEASURABILITY routes to bin/charter-check.py (diagnosis · ranked · FLUFF
  · UNMEASURABLE_KPI · VACUOUS_ACCEPTANCE); the precise-but-wrong quadrant (Goodhart — the metric misses
  the outcome) is adversarially verified. NOT for judging the product bet by taste (product-forge), the
  structure that meets them (architecture-decomposer), a unit of code vs its spec (code-decomposer), or
  the data model (type-decomposer).
---

# goals-decomposer — grade a goals/charter doc on two crossing axes

A goals / charter / PRD doc is the **OUTSIDE-IN plane** of planning a system — *what are we trying to do,
and how will we know it's good?* — the peer of `architecture-decomposer` (the INSIDE-OUT plane). This
skill grades the **charter itself**: not whether the bet is *good* (that's taste — `product-forge`'s
councils), but whether the doc is a **governable, falsifiable contract** a downstream architecture can be
held to. Like every decomposer, a charter is **correct on two independent axes that walk the same
hierarchy** (`diagnosis → ranked characteristics → principles & non-goals → acceptance`) **in opposite
directions:**

- **AIM · whole → part** grades the **intent**: is the diagnosis real, are these the *right* goals,
  strictly ranked, coherent, bounded? *"Are we aiming at the right thing?"* Judgment — where an LLM is
  strong, and where it rationalizes a goal set that never faces the challenge.
- **MEASURABILITY · part → whole** grades the **mechanism**: is every goal *falsifiable* — a metric with
  a threshold and a window, a checkable acceptance predicate, a strict priority order, no contradictions?
  *"Can you provably tell when it's met?"* Arithmetic, not taste — so it routes to a deterministic gate,
  `bin/charter-check.py`.

They **cross at the individual goal** — a characteristic is *both* a claim about what matters and a
checkable predicate. The two defects are **opposite**: **vague but right** (the right aims as fluff —
"be fast, be reliable", no metric, no rank) or **precise but wrong** (a crisp KPI dashboard pointed at
the wrong outcome — a surrogate metric, Goodhart's law). Opposite fixes — so you **score the two axes
separately, never averaged**, and name the quadrant.

## Quick Start

**You bring:** a goals doc / PRD (or a planning request) and the question — "design this", "is this PRD
governable?", "grade these goals", "do these goals match the architecture?". **You get:** a charter card
(diagnosis + ranked characteristics + acceptance), a measurability report from the bin, and a two-axis
grade with the defect quadrant named.

> *"Is this PRD ready to hand to engineering?"* →
> 1. **AIM — diagnosis → ranked goals:** is there a real diagnosis (not just goals) `[gate]`; are the
>    *-ilities* a strict priority order `[gate]`. Then A3 outcomes-not-outputs, A4 coherence & scope,
>    A5 falsifiable success.
> 2. **MEASURABILITY — measure it, don't read it:** `bin/charter-check.py lint charter.json` runs
>    well-formed+ranked `[gate]` + every-goal-measured `[gate]` + acceptance-checkable `[gate]`.
> 3. **Attack the dangerous quadrant:** a skeptic in a fresh context tries to break each top metric —
>    could you move it *without* delivering the outcome (Goodhart)? is "success" an output renamed?
> 4. **Report:** two axis scores + the quadrant cell, gate failures first.

**Modes:** **DECOMPOSE** (read a PRD → extract a charter → run the gate → grade) · **DESIGN** (name the
diagnosis → rank the -ilities → set principles/non-goals → write falsifiable acceptance) · **GRADE**
(score both axes, gates before reviews) · **CROSS-CHECK** (a *validated* charter vs an
`architecture-decomposer` blueprint — does the structure serve the ranked goals?).

## The two axes (the method)

Load `references/decomposition-method.md` first. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · AIM** | whole → part | **A1** Diagnosis `[gate]` → **A2** Ranked characteristics `[gate]` → **A3** Outcomes not outputs `[review]` → **A4** Coherence & scope `[review]` → **A5** Falsifiable success `[review]` | "Are we aiming at the *right thing*?" |
| **B · MEASURABILITY** | part → whole | **B1** Well-formed & ranked `[gate]` → **B2** Goals measured `[gate]` → **B3** Acceptance checkable `[gate]` → **B4** Bounded & coherent `[review]` → **B5** Traceable `[review]` | "Can you *provably tell* when it's met?" |

`A1·A2` and `B1·B2·B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on that
axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A charter is **GOVERNABLE** at **≥4 on every review
with zero gate failures**, reported as two scores plus the quadrant. The B gates route to
**`bin/charter-check.py`**; the A reviews are judged + the top metrics adversarially Goodhart-probed.

This is the OUTSIDE-IN half of the **two-plane** method (`HOWTO.md` §1): plan/review the goals here, the
structure in `architecture-decomposer`, and cross-check the seam in a third fresh context. The charter is
authored **first, with no architecture in context** (staged isolation), then handed down read-only.

## The doctrine — a charter is a contract, not a wish

- **Goals with no diagnosis is bad strategy** (Rumelt). `NO_DIAGNOSIS` is a gate fail — a goal list with
  no challenge to answer gives the architecture nothing to be coherent against.
- **If everything is a priority, nothing is.** The *-ilities* must be a **strict order** — the rank is
  what forces the trade-off the architecture has to make. Ties → `UNRANKED`. *Everything is a trade-off.*
- **A goal you can't measure is fluff.** Metric + threshold + window per goal; a checkable predicate per
  acceptance criterion. `FLUFF` / `UNMEASURABLE_KPI` / `VACUOUS_ACCEPTANCE` route to the bin.
- **Measurable is necessary, not sufficient — beware Goodhart.** A green gate proves *falsifiable*, never
  that the metric *captures the outcome*. The *precise-but-wrong* quadrant is on the AIM side, caught by a
  fresh-context surrogate probe and the outputs-not-outcomes smell (the build trap).

## §SelfAudit

- **Measurability is the gate the LLM fails silently.** Run `charter-check.py`; don't certify "it's
  measurable / ranked / falsifiable" from reading. An unrun gate is *no evidence*, not a pass.
- **A green gate is a pre-filter, not an oracle.** It proves the charter is *falsifiable* — not that the
  aims are right or the metric captures its outcome. Confirm the outcome out of band.
- **The dangerous defect is invisible to the gate — Goodhart-probe the metrics.** *Precise but wrong*
  needs a skeptic: could you move each top metric without delivering the outcome? is it a surrogate? is
  "success" an output renamed? Default to "surrogate" until it survives.
- **Strict ranking, always.** A charter with five rank-1 goals has made no decision. If you can't name
  the trade-off between the top two and which wins, they aren't ranked.
- **Two scores, never one.** *Vague-but-right* and *precise-but-wrong* need opposite fixes (measure it vs
  re-diagnose & re-aim). Report both axes and name the quadrant; never average.
- **Grade the charter; don't make the bet or build the structure.** The product bet is `product-forge`;
  the structure is `architecture-decomposer`. Hand off; don't overlap.

## Verify Target

A charter is **done** when: the diagnosis faces the challenge (A1, `NO_DIAGNOSIS` clean) and the *-ilities*
are strictly ranked (A2, `UNRANKED` clean); goals are outcomes not outputs, coherent and bounded with
falsifiable acceptance (A3–A5 ≥ 4); the bin's well-formed + measured + checkable gates ran **green**
(B1–B3 — no `FLUFF`/`UNMEASURABLE_KPI`/`VACUOUS_ACCEPTANCE`); scope is bounded and goals trace to the
diagnosis (B4–B5); the top metrics **survived a fresh-context Goodhart probe**; and both axes score ≥4
with zero gate failures, landing in **GOVERNABLE** — ready to hand down as the read-only contract for
`architecture-decomposer`. **NOT done** when: the goals are right but unmeasurable (*vague but right*);
crisply measured but aimed at a surrogate / the wrong outcome (*precise but wrong*); a gate was skipped
and reported as a pass; or one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (AIM × MEASURABILITY), the leveled walk with gates, the quadrant, the charter-is-a-contract doctrine, staged isolation, and the four modes |
| `references/aim-axis.md` | **the AIM axis** — diagnosis (Rumelt's kernel) → ranked *-ilities* → outcomes-not-outputs (the build trap) → coherence & non-goals → falsifiable success (SMART/OEC); the adversarial Goodhart probe; where **precise-but-wrong** lives |
| `references/measurability-axis.md` | **the MEASURABILITY axis** — well-formed+ranked → goals-measured → acceptance-checkable → bounded → traceable; what the gate enforces vs. what you must still check; mechanized by `bin/charter-check.py`; where **vague-but-right** lives |
| `references/the-charter-schema.md` | **the `*.charter.json` card** — field-by-field, what "measured" means (numeric threshold vs. falsifiable prose), and the relationship to the architecture contract card |
| `references/policy.md` | **definition-of-done / handoff** — the 10-point DoD, the **cross-check** seam to `architecture-decomposer`, and the boundaries to `product-forge`, `code-decomposer`, `type-decomposer`, and the two-plane orchestrator |
| `bin/charter-check.py` | **mechanizes the B axis** — `lint <charter.json>` (WELL_FORMED · NO_DIAGNOSIS · UNRANKED · FLUFF · UNMEASURABLE_KPI · VACUOUS_ACCEPTANCE · OUTPUT_NOT_OUTCOME · CONTRADICTION · NO_NONGOALS · UNTRACED_GOAL) · `selftest` · `--json` |
