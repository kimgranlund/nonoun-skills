# Changelog — goals-decomposer

Versioned independently of the `code-skills` plugin; the gate (`bin/check-skills.py`) must pass for any
release.

## 0.1.0 — draft

Initial release. Decompose / design / grade / cross-check a **goals / charter / PRD doc** — the
**OUTSIDE-IN** plane of planning a system, the peer to `architecture-decomposer`'s INSIDE-OUT — on two
crossing axes, scored separately with a gated rubric and the opposite-defect quadrant. The symmetric
half of the two-plane reasoning model (`HOWTO.md` §1): goals-decomposer grades *"are we aiming at the
right thing, and can we tell when we've hit it?"*; architecture-decomposer grades *"what structure holds
it up?"*.

- **The two-axis method** (`references/decomposition-method.md`): **A · AIM** (diagnosis → ranked
  *-ilities* → outcomes-not-outputs → coherence & non-goals → falsifiable success) × **B ·
  MEASURABILITY** (well-formed & ranked → goals measured → acceptance checkable → bounded → traceable),
  crossing at the individual goal; gates before reviews; the **vague-but-right** vs **precise-but-wrong**
  (Goodhart) quadrant; and the **charter-is-a-contract** doctrine.
- **The measurability gate** (`references/measurability-axis.md` + `bin/charter-check.py`): a stdlib-only
  linter over a `*.charter.json` card — `NO_DIAGNOSIS` · `UNRANKED` · `FLUFF` · `UNMEASURABLE_KPI` ·
  `VACUOUS_ACCEPTANCE` (gate fails) + `OUTPUT_NOT_OUTCOME` · `NO_NONGOALS` · `CONTRADICTION` ·
  `UNTRACED_GOAL` · `WELL_FORMED` (advisory/structural). `lint` · `selftest` · `--json`. Green (a
  governable checkout charter) / red (a fluffy "Platform v2") fixtures.
- **The AIM axis + the named canon** (`references/aim-axis.md`): Rumelt's **strategy kernel** (diagnosis
  → guiding policy → coherent action) and the four hallmarks of bad strategy; **outcomes over outputs**
  (Perri's build trap); the **architecture characteristics** ranked (Ford/Richards, *everything is a
  trade-off*); **SMART** + the **OEC** (Kohavi) for acceptance; and the adversarial **Goodhart/surrogate
  probe** for the *precise-but-wrong* quadrant.
- **The charter card** (`references/the-charter-schema.md`): the `*.charter.json` doc field-by-field,
  what "measured" means (a numeric threshold vs. falsifiable prose — a comparator/unit word), and the
  relationship to `architecture-decomposer`'s contract card.
- **Policy** (`references/policy.md`): the 10-point DoD, the **cross-check** seam to
  `architecture-decomposer` (every ranked characteristic → a structural mechanism; no architectural
  choice violates a principle), and the boundaries to `product-forge` (the *bet*, by taste),
  `code-decomposer`, `type-decomposer`, and the two-plane orchestrator (enforcement/isolation).
- A checked-in, sibling-collision-tested routing-eval corpus (`goals-decomposer.corpus.json`) and a
  worked `examples/walkthrough.md` (green→GOVERNABLE, red→both-defects, plus a Goodhart probe).

Sixth crossing-axis decomposer in `code-skills`; the OUTSIDE-IN peer that makes the two-plane model
symmetric.

### Defect fixes (pre-release hardening)

- **charter-check — VACUOUS_ACCEPTANCE substantive-word hole:** the acceptance check first treated any
  non-vague content word as "checkable," so `"the platform works well and feels snappy"` escaped (the
  nouns "platform"/"feels" rescued it). Reworked to judge by **measurement presence** (a number, a
  comparator word, or a unit) **plus a vague-domination ratio**, and broadened measurement detection so a
  real behavioral criterion ("ships a change in under a day") isn't falsely flagged. The degraded fixture's
  criterion is exactly the adjective-salad shape, locking the fix; the selftest carries the sound
  single-characteristic must-NOT-flag fixture and the malformed-input no-crash loop.
