# The charter card — the doc the gate consumes

`charter-check.py` grades a **`*.charter.json` card**: a typed, gradeable projection of a goals doc /
PRD. The prose PRD stays human-readable; the card is what the mechanism gate reads (the same
prose-vs-card split as `architecture-decomposer`'s contract card and `brand-decomposer`'s brand-spec card).

## The card

```json
{
  "title": "Checkout service",
  "diagnosis": "Cart abandonment spikes at peak because checkout p99 latency degrades under load and a single failure takes the whole flow down.",
  "characteristics": [
    { "name": "scalability", "rank": 1,
      "outcome": "checkout stays responsive under peak traffic",
      "metric": "p99 checkout latency", "threshold": "< 300ms", "window": "at 10x baseline load",
      "rationale": "abandonment tracks latency above 300ms (diagnosis)" },
    { "name": "resilience", "rank": 2, "outcome": "a downstream failure degrades, not collapses",
      "metric": "successful-checkout rate during a payment-provider outage", "threshold": "> 95%",
      "window": "during a single-provider outage", "rationale": "single failure took the flow down" }
  ],
  "principles": ["fail open to a queue, never to an error", "no synchronous calls on the hot path"],
  "non_goals": ["not multi-region in v1", "not a rewrite of the catalog service"],
  "acceptance": [
    { "criterion": "p99 checkout latency stays under 300ms at 10x load", "metric": "p99", "threshold": "300ms" },
    { "criterion": "checkout succeeds for >95% of carts during a simulated provider outage" }
  ]
}
```

## Field reference

| Field | Axis | Required | Notes |
|---|---|---|---|
| `title` | — | — | used in every finding |
| `diagnosis` | **A1 / B1** | yes | the challenge being faced; empty → `NO_DIAGNOSIS` (gate) |
| `characteristics[]` | **A2 / B2 / B3** | yes | the ranked *-ilities* |
| `characteristics[].name` | A2 | yes | the quality goal (scalability, resilience…) |
| `characteristics[].rank` | **B3** | yes | a distinct integer; ties → `UNRANKED` |
| `characteristics[].outcome` | A3 | — | the behavior change; a build-verb here → `OUTPUT_NOT_OUTCOME` |
| `characteristics[].metric` | **B2** | yes | the thing measured; absent → `FLUFF` |
| `characteristics[].threshold` | **B2** | yes | a **numeric** pass/fail bar; non-numeric → `UNMEASURABLE_KPI` |
| `characteristics[].window` | B2 | — | the condition (at N× load, over N days); absent → advisory |
| `characteristics[].rationale` | A1 | — | ties the goal to the diagnosis; absent → `UNTRACED_GOAL` (advisory) |
| `principles[]` | A4 | — | the rules that shape choices (carried to the cross-check) |
| `non_goals[]` | **B4** | — | scope boundary; empty → `NO_NONGOALS`; overlap with a characteristic → `CONTRADICTION` |
| `acceptance[]` | **A5 / B2** | — | `{criterion, metric?, threshold?}`; non-falsifiable criterion → `VACUOUS_ACCEPTANCE` |

## What "measured" means (the linter's test)

A **threshold** must be **numeric** (a digit or a comparator symbol: `< 300ms`, `> 95%`, `<= 1`). An
**acceptance criterion** is "measured" if it carries a number, a comparator word (under / over / within
/ at most…), or a unit (ms, requests, days, users…) — so *"ships a change in under a day"* counts, while
*"works well and feels snappy"* does not. This is deliberately lenient on prose (to avoid false
positives on real behavioral criteria) and strict on the per-characteristic KPI fields (which must carry
an actual number).

## Relationship to the architecture contract card

The charter is the **OUTSIDE-IN** doc; `architecture-decomposer`'s **contract card** (boundaries +
dependency graph) is the **INSIDE-OUT** doc. They are the two planes of one plan. The **cross-check**
(`references/policy.md`) reads both: every ranked characteristic in the charter should have a named
structural mechanism in the contract card; no architectural choice should violate a charter principle.
In the two-plane orchestrator (`nonoun-plugins`) these are the two cells of a lattice, the charter
upstream of the contract.
