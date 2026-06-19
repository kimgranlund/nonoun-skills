# Behavioral evaluation — does a skill measurably improve the output?

The gate (`bin/check-skills.py`) proves a skill is well-formed and that its `bin/` gates work (good +
bad fixtures). The routing corpora prove it *fires* on the right requests. Neither measures the thing
that matters most: **when the skill is invoked, is the produced artifact actually better than without
it?** This file is the method for measuring that, plus two worked pilots.

It is the marketplace-level [ROADMAP](ROADMAP.md) "behavioral-eval layer" item — **piloted and
templated here**, not yet automated.

## The template

For one skill, on a representative task:

1. **Task** — a realistic prompt the skill is meant to help with.
2. **With-skill run** — an agent that reads + applies the skill (and runs its `bin/` if it routes there).
3. **Baseline run** — the same task with the skill **suppressed** (see constraint #1).
4. **Score** — both outputs against a **per-skill metric** (constraint #2), grounded in the skill's own
   `bin/` where possible. Blind-judge for rigor; repeat over N runs for variance.
5. **Read** — does with-skill beat baseline on the metric, and by how much?

## Three design constraints (learned the hard way in the pilots)

### 1. Installed skills auto-route — the baseline MUST suppress them
The first pilot's "baseline" agent silently invoked the skill anyway (it *ran the skill's `bin/`*),
because a button-design task **triggers** the installed skill regardless of the prompt. So a
behavioral eval of an installed skill must explicitly suppress it — *"from first principles only; do
not read files, invoke any skill / plugin / methodology, or run any tool"* — or run the baseline in a
skill-absent environment. Without this, with-skill ≈ baseline and the eval measures nothing.

### 2. Choose the metric by the base model's competence at the task
A skill's *measurable value* depends on whether the task sits inside or outside the base model's
reliable knowledge — and the metric must match, or the eval reads "the skill barely helped":

| Task vs base competence | What the skill adds | The right metric |
|---|---|---|
| **OUTSIDE** (e.g. exact component geometry) | raw correctness — the base model *guesses*; the skill *derives + verifies* | output correctness, checked by the skill's `bin/` |
| **INSIDE** (e.g. k8s config security) | verification · structure · provenance · discipline — the base model already knows the issues | verification-rate · structure · false-positive-rate — **NOT raw recall** (the baseline matches it) |

### 3. Ground the metric in the skill's `bin/` where possible
For a skill with a deterministic gate, the `bin/` is objective ground truth — no subjective judge
needed for the mechanizable axis. The eval doubles as a **bin stress test** (pilot B surfaced a real
`config-lint` false-negative). Reproducibility across N skill-runs is a free quality signal: a good
deterministic skill produces **low-variance** output.

## Pilot A — component-decomposer (OUTSIDE competence: exact geometry)

Task: *"design a button across XS–2XL with icon/label/caret; give the spec."* With-skill vs a
suppressed first-principles baseline.

| Dimension | With-skill | Baseline (suppressed) |
|---|---|---|
| Padding | every value = `(h−glyph)/2`, **computed + bin-verified** | eyeballed heuristic (`H×0.34`, "snapped by hand") |
| Consistency | one law unifies icon-only · icon-leading · caret | inconsistent — icon-only pad (11) ≠ icon-leading pad (12) |
| Verification | ran `geometry-check` + `contract-check` (green) | none — *"I'd trust the model more than the exact integers"* |
| Structure | two-axis gated grade + named quadrant | flat "strengths / weaknesses / B+" |

**Result:** the skill materially lifts correctness on its target dimension — it routes the geometry to
a derived, verified law, eliminating the eyeballing the baseline names as *its own* top weakness. A
clean win because the task is **outside** the base model's reliable knowledge.

## Pilot B — config-decomposer (INSIDE competence: config security)

Task: *"review this k8s manifest for safety issues."* Ground truth = `config-lint.py` (5 findings; it
**misses** the `API_KEY` plaintext secret hidden in k8s `env:[{name,value}]` format).

- **The suppressed baseline was strong** — it caught all 5 bin findings **and the API-key the bin
  misses**, plus ~8 more (securityContext hardening, seccomp, probes, namespace, least-privilege DB
  user). k8s security is well within the base model's knowledge, so **raw recall did not separate
  them** — the baseline arguably found *more* raw issues.
- **The skill's value showed up elsewhere:** it **ran the bin** (its 5 findings are *verified*, not
  asserted), **labelled provenance** (`[linter, FAIL]` vs `[manual]`), produced the **two-axis
  INTENT × VALIDITY gated grade** with the quadrant + a SHIPPABLE verdict, honored the harness
  discipline (**B1–B3 = NO EVIDENCE, not PASS** — `kubeconform`/`kubectl` were absent), and *named the
  bin's blind spot as a blind spot* (then flagged it as a maintainer fixture).

**Result:** on an **inside**-competence task the skill's value is **verification + provenance +
structure + discipline**, not raw recall — exactly what constraint #2 predicts. *Byproduct:* a real
`config-lint` false-negative (k8s `env`-list secrets) is now on config-decomposer's ROADMAP.

## Running one (the agent prompts)

- **With-skill:** *"Do `<task>` using the `<skill>` skill: read `<skill>/SKILL.md` and apply it (run
  its `bin/` if it routes there). `<task input>`."*
- **Baseline (suppressed):** *"Do `<task>` from your own knowledge only. Do NOT read files, invoke any
  skill / plugin / methodology (esp. `*-decomposer`), or run any tool. `<task input>`."*
- **Score:** for an out-of-competence task, diff each output's findings against the `bin/` ground
  truth (recall / precision); for an in-competence task, score verification-rate, structure, and
  false-positives. Blind-judge + N-run variance for rigor.

## What's still a project (not done here)

Automating this — a runnable harness that fans out with-skill / baseline / judge and aggregates
variance — is the remaining work; `skills-skills/skills-studio`'s `eval` mode is the closest existing
engine. This file is the **method + two proofs**; wiring it into CI per skill is the open item.
