# B · The MEASURABILITY axis — can you provably tell when it's met?

The MEASURABILITY axis grades the **mechanism**, bottom-up: from each individual goal (does it carry a
checkable predicate?) up to the charter as a whole (is it strictly ranked, non-contradictory, bounded?).
This is exactly where a charter *feels* ambitious but can't be held to anything — so its gates are
**routed to a deterministic, self-tested tool, `bin/charter-check.py`**, and a clean run is **necessary,
not sufficient.** This is where the **vague-but-right** defect lives: the right aims, expressed as fluff.

You walk it **part → whole**. The per-goal checks are gates; the whole-charter coherence checks are
reviews. Run `charter-check.py lint <charter.json>` — don't certify falsifiability by reading.

## B1 · Diagnosis present `[gate]` — mechanized

`NO_DIAGNOSIS` — the charter has no stated problem/challenge. The cheapest mechanizable proxy for
Rumelt's "mistaking goals for strategy": a charter that is all goals and no diagnosis. (Whether the
diagnosis is *correct* is AIM/A1; that it *exists* is here.)

## B2 · Every goal carries a measure `[gate]` — mechanized

The core of the axis: a goal you can't measure is fluff.

- **`FLUFF`** — a characteristic with **no metric** at all ("be scalable", "be reliable"). A quality
  word is not a goal until it has a number attached.
- **`UNMEASURABLE_KPI`** — a characteristic with a metric but **no numeric threshold** (metric "uptime",
  threshold blank — you can't pass/fail it) — or no **window/condition** (under what load, over what
  period). A complete KPI is **metric + threshold + window**: "p99 checkout latency < 300ms at 10× load."
- **`VACUOUS_ACCEPTANCE`** — an acceptance criterion with **no measurable predicate** that is dominated
  by vague adjectives ("the platform works well and feels snappy"). The linter checks for a number, a
  comparator (`<`, under, within…), or a unit (ms, requests, days); a criterion made only of quality
  adjectives is not falsifiable. (A *concrete-but-unnumbered* criterion — "a new contributor ships a
  change without asking for help" — drops to an advisory, not a hard fail: is it really checkable?)

## B3 · The charter is a strict order `[gate]` — mechanized

`UNRANKED` — the characteristics share ranks (especially at the top). A strict priority order is what
makes the trade-offs decidable downstream; the linter requires every characteristic to carry a distinct
integer rank. (`WELL_FORMED` fires if a rank is missing or non-integer.)

## B4 · Coherence & scope `[review]` — mechanized smells + judgment

- **`CONTRADICTION`** (mechanized, narrow) — a non-goal that *names* a characteristic the charter also
  pursues (you can't both pursue and exclude X). The linter catches the literal overlap; the *semantic*
  contradictions (two -ilities that can't co-maximize without a ranking) are A4 judgment.
- **`NO_NONGOALS`** (mechanized) — no explicit scope boundary. Unbounded scope is ungovernable.
- **`OUTPUT_NOT_OUTCOME`** (mechanized smell) — a goal starting with a build-verb (ship/add/build/…).
  Surfaced here as a smell; judged on A3.

## What the gate enforces vs. what you must still check

`charter-check.py` mechanizes the *arithmetic* of falsifiability — presence of a diagnosis, a metric +
numeric threshold per goal, a checkable acceptance predicate, a strict ranking, literal contradictions,
scope bounds. It **cannot** mechanize:

- whether a metric **captures its outcome** (Goodhart) — that's the AIM-axis adversarial probe;
- whether the ranking reflects the **real** trade-offs (you can rank wrong, strictly);
- whether the diagnosis is **true**;
- whether an acceptance criterion, though numbered, measures the **right** number.

So a green run means the charter is *well-formed, ranked, and falsifiable* — **governable**. It does not
mean the aims are right. That is the AIM axis (`references/aim-axis.md`), judged and adversarially
verified. A perfectly measurable charter can hold you precisely accountable to the wrong thing.
