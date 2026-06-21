# Walkthrough — grading two charters, then the Goodhart probe

Two cards ship with the skill: `checkout.green.charter.json` (a governable charter) and
`platform.red.charter.json` (a fluffy one). Both are the bin's own fixtures, written to disk so you can
run every command.

## 1 · GRADE the green charter — Checkout service

### Measurability (run the gate first)

```sh
python3 bin/charter-check.py lint examples/checkout.green.charter.json
# charter-check: OK — measurability gates clear (diagnosis, ranked, falsifiable);
#                the AIM axis (are these the RIGHT aims?) is judged separately
```

B-axis green: there's a diagnosis; the three characteristics carry distinct ranks (1, 2, 3); each has a
metric + numeric threshold + window (`p99 checkout latency < 300ms at 10x baseline load`); the acceptance
criteria carry numbers; non-goals are explicit. **Axis B = GOVERNABLE.**

### Aim (judge, then Goodhart-probe)

- **A1 diagnosis** — *"cart abandonment spikes at peak because checkout p99 degrades under load and a
  single failure takes the whole flow down."* It faces a real challenge; the goals answer it. **Gate clear.**
- **A2 ranked** — scalability(1) > resilience(2) > evolvability(3). A strict order — you can name the
  trade-off (under a partial outage, keep the *successful-checkout rate* up even if latency slips).
- **A3–A5** — outcomes not outputs ("checkout stays responsive", not "build a cache"); coherent; bounded.
- **Goodhart probe** (fresh context): *could you move "p99 < 300ms at 10× load" without delivering the
  outcome (fewer abandoned carts)?* Not easily — it's close to the outcome, with a window. **Survives.**

**Verdict:** AIM ≥ 4, MEASURABILITY green → **GOVERNABLE**. Two scores, never averaged.

## 2 · GRADE the red charter — Platform v2 (vague but right, and unranked)

```sh
python3 bin/charter-check.py lint examples/platform.red.charter.json
# charter-check: FAIL (5)
#   - Platform v2: NO_DIAGNOSIS — no stated problem/challenge …
#   - Platform v2: UNRANKED — characteristics share ranks [1]; a charter must be a strict priority order …
#   - Platform v2: FLUFF — characteristic 'fast' has no metric …
#   - Platform v2: UNMEASURABLE_KPI — characteristic 'reliable' metric 'uptime' has no numeric threshold …
#   - Platform v2: VACUOUS_ACCEPTANCE — criterion 'the platform works well and feels snappy' … not checkable
#   ⚠ OUTPUT_NOT_OUTCOME ('make…', 'ship…') · NO_NONGOALS · no window · no rationale
```

Every measurability defect at once: no diagnosis, two rank-1 characteristics (no priority), a metric-less
"fast", an "uptime" KPI with no threshold, and a "works well and feels snappy" acceptance criterion. The
charter *reads* ambitious and you can't be held to a single line of it — **vague but right** (the aims
aren't wrong, they're just fluff). **Axis B = 1.** Fix: give every goal a metric + threshold + window and
a strict rank, and write a diagnosis.

## 3 · The dangerous quadrant — precise but wrong (Goodhart)

The gate can't catch the *opposite* defect. Imagine a charter that passes the bin cleanly — diagnosis,
strict ranks, every goal a crisp KPI — whose rank-1 metric is **"average session length > 8 min."** It is
perfectly measurable and **aimed at the wrong outcome**: session length goes *up* when users are lost and
hunting, not when they succeed. That's the **precise-but-wrong** quadrant, and only the AIM-axis
Goodhart probe catches it:

> *Could you move "average session length" without delivering the outcome it stands for?* Yes — confusion
> inflates it. It's a **surrogate**. Replace it with a metric closer to the outcome ("task completed in <
> 2 min", with a guardrail on error rate). 

A green `charter-check` run means the charter is **falsifiable** — never that the metric **captures the
outcome**. Necessary, not sufficient: that is why the two axes are scored separately, and why the top
metrics always get a fresh-context probe.
