#!/usr/bin/env python3
"""budget-check.py — the perf-verifier performance-budget gate. Self-contained (stdlib only).

perf-verifier reasons about *perceived* latency — the judgment-heavy half (skeleton vs spinner,
streaming presentation, what feedback a surface owes the user) stays a review in SKILL.md. But one
half of the job is pure arithmetic: a measured number vs a budgeted number. *Computation routes to
code, never to inference* — so the budget comparison lives here, deterministic and self-tested.

A "performance budget card" pairs measured metrics with their budget:

  {
    "page": "/checkout",                         # optional label
    "metrics": {                                  # what was measured (any subset)
      "lcp_ms": 3200, "cls": 0.18, "inp_ms": 150, "tbt_ms": 420,
      "bundle_kb": 680, "image_kb": 1200, "requests": 95
    },
    "budget": {                                   # what was budgeted (any subset; CWV have defaults)
      "lcp_ms": 2500, "cls": 0.1, "inp_ms": 200, "tbt_ms": 300,
      "bundle_kb": 300, "image_kb": 500, "requests": 50
    }
  }

Per metric the gate compares measured vs effective-budget and classifies:

  - FAIL (gate)     — measured is over the CWV "poor" threshold (lcp>4000ms, cls>0.25, inp>500ms).
                      Poor is poor regardless of an indulgent local budget.
  - ADVISORY (warn) — over budget but not poor: a regression to watch, not a hard block.
  - OK              — within budget.
  - SKIPPED         — neither a measured value NOR an effective budget exists: nothing to compare.
                      Reported, never silently passed.

Core Web Vitals have canonical budgets, so a missing budget key for lcp/cls/inp/tbt falls back to a
default (lcp 2500ms, cls 0.1, inp 200ms, tbt 300ms). bundle_kb / image_kb / requests have no
universal "good" number, so they are only checked when the card supplies a budget for them.

  python3 bin/budget-check.py selftest
  python3 bin/budget-check.py <card.json | dir>

Python 3.8+.
"""
import json
import os
import sys

# Canonical Core-Web-Vitals "good" budgets — used when the card omits the key.
# (web.dev field thresholds: LCP 2.5s, CLS 0.1, INP 200ms; TBT lab proxy for INP at 300ms.)
CWV_DEFAULT_BUDGET = {"lcp_ms": 2500, "cls": 0.1, "inp_ms": 200, "tbt_ms": 300}

# CWV "poor" thresholds — over these is a gate FAIL regardless of the local budget.
# bundle/image/requests have no universal "poor" line, so over-budget there is only ever advisory.
POOR = {"lcp_ms": 4000, "cls": 0.25, "inp_ms": 500}

# Every metric the gate understands; bundle/image/requests are budget-only (no default).
KNOWN_METRICS = ["lcp_ms", "cls", "inp_ms", "tbt_ms", "bundle_kb", "image_kb", "requests"]

# "lower is better" is true for every metric here (latency, shift, weight, count).


def _num(v):
    """A finite real number, or None. Rejects bool — JSON true must not read as 1."""
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        f = float(v)
        if f != f or f in (float("inf"), float("-inf")):  # NaN / inf
            return None
        return f
    return None


def check_card(card):
    """Return (fails, advisories, skipped, oks) for one budget card.

    Each list holds human-readable strings. Raises ValueError on a malformed card so the caller
    can report a clean error rather than crash.
    """
    if not isinstance(card, dict):
        raise ValueError("budget card must be a JSON object, got %s" % type(card).__name__)
    metrics = card.get("metrics", {})
    budget = card.get("budget", {})
    if not isinstance(metrics, dict):
        raise ValueError("'metrics' must be an object")
    if not isinstance(budget, dict):
        raise ValueError("'budget' must be an object")

    label = card.get("page") or card.get("label") or "<card>"
    # surface any key the card used that the gate doesn't model — a typo'd metric would otherwise
    # vanish silently (no measured + no budget => skipped, but the user thinks it was checked).
    unknown = sorted((set(metrics) | set(budget)) - set(KNOWN_METRICS))

    fails, advisories, skipped, oks = [], [], [], []
    for m in KNOWN_METRICS:
        measured = _num(metrics.get(m))
        # validate a present-but-non-numeric value rather than treating it as absent
        if m in metrics and measured is None:
            raise ValueError("%s: metric '%s' is not a number: %r" % (label, m, metrics.get(m)))
        bud = _num(budget.get(m))
        if m in budget and bud is None:
            raise ValueError("%s: budget '%s' is not a number: %r" % (label, m, budget.get(m)))

        # effective budget: explicit budget wins; else the CWV default; else none (skip-eligible).
        eff = bud if bud is not None else CWV_DEFAULT_BUDGET.get(m)

        if measured is None and eff is None:
            skipped.append("%s: '%s' — no measured value and no budget; nothing to compare" % (label, m))
            continue
        if measured is None:
            skipped.append("%s: '%s' — budget %s set but no measured value" % (label, m, eff))
            continue
        if eff is None:
            skipped.append("%s: '%s' = %s — no budget (no universal default); supply one to check"
                           % (label, m, _fmt(measured)))
            continue

        src = "" if m in budget else " (CWV default)"
        if m in POOR and measured > POOR[m]:
            fails.append("%s: '%s' = %s over POOR threshold %s (budget %s%s) — gate FAIL"
                         % (label, m, _fmt(measured), _fmt(POOR[m]), _fmt(eff), src))
        elif measured > eff:
            advisories.append("%s: '%s' = %s OVER_BUDGET %s%s (not yet 'poor') — advisory"
                              % (label, m, _fmt(measured), _fmt(eff), src))
        else:
            oks.append("%s: '%s' = %s within budget %s%s" % (label, m, _fmt(measured), _fmt(eff), src))

    for u in unknown:
        skipped.append("%s: unknown metric '%s' — not modeled by this gate; ignored" % (label, u))
    return fails, advisories, skipped, oks


def _fmt(n):
    """Print 0.18 not 0.18000000001, and 3200 not 3200.0."""
    if n == int(n):
        return str(int(n))
    return ("%.4f" % n).rstrip("0").rstrip(".")


# --- selftest fixtures -------------------------------------------------------------------------
# must-FLAG: lcp over-budget (advisory), cls over the POOR line (FAIL), bundle over-budget (advisory)
FLAG = {
    "page": "/checkout",
    "metrics": {"lcp_ms": 3200, "cls": 0.3, "inp_ms": 150, "tbt_ms": 420,
                "bundle_kb": 680, "image_kb": 1200, "requests": 95},
    "budget":  {"lcp_ms": 2500, "cls": 0.1, "inp_ms": 200, "tbt_ms": 300,
                "bundle_kb": 300, "image_kb": 500, "requests": 50},
}
# must-NOT-flag: every metric within budget
CLEAN = {
    "page": "/home",
    "metrics": {"lcp_ms": 1800, "cls": 0.05, "inp_ms": 120, "tbt_ms": 150,
                "bundle_kb": 240, "image_kb": 380, "requests": 32},
    "budget":  {"lcp_ms": 2500, "cls": 0.1, "inp_ms": 200, "tbt_ms": 300,
                "bundle_kb": 300, "image_kb": 500, "requests": 50},
}
# must-NOT-flag: bundle present with no budget + no default -> skipped, reported, not flagged
SKIP = {"page": "/x", "metrics": {"bundle_kb": 999}}
# CWV default kicks in: cls 0.3 with NO budget key still FAILs on the poor line (default 0.1 < 0.3)
DEFAULT_FAIL = {"page": "/y", "metrics": {"cls": 0.3}}
# CWV default: lcp 2600 with no budget -> over the 2500 default but under poor 4000 -> advisory
DEFAULT_ADVISORY = {"page": "/z", "metrics": {"lcp_ms": 2600}}
# empty-ish card: no metrics, no budget -> everything skipped, no fail/advisory, no crash
EMPTY = {"page": "/empty"}
BAD_TYPE = {"metrics": {"lcp_ms": True}}            # bool must not read as 1 -> ValueError
BAD_SHAPE = {"metrics": [1, 2, 3]}                   # metrics not an object -> ValueError


def selftest():
    errs = []

    def run(card):
        return check_card(card)

    # --- FLAG card -----------------------------------------------------------------------------
    f, a, s, o = run(FLAG)
    if not any("cls" in x and "POOR" in x for x in f):
        errs.append("FLAG: cls 0.3 should be a POOR/FAIL")
    if not any("lcp_ms" in x and "OVER_BUDGET" in x for x in a):
        errs.append("FLAG: lcp 3200 vs 2500 should be an over-budget advisory")
    if not any("bundle_kb" in x and "OVER_BUDGET" in x for x in a):
        errs.append("FLAG: bundle 680 vs 300 should be an over-budget advisory")
    if any("cls" in x for x in a):
        errs.append("FLAG: cls (a FAIL) leaked into advisories")
    if any("lcp_ms" in x for x in f):
        errs.append("FLAG: lcp 3200 (under poor 4000) wrongly classified as FAIL")

    # --- CLEAN card: zero fails, zero advisories ----------------------------------------------
    f, a, s, o = run(CLEAN)
    if f or a:
        errs.append("CLEAN card produced fails/advisories: %s %s" % (f, a))
    if len(o) != len(KNOWN_METRICS):
        errs.append("CLEAN card should pass all %d metrics, got %d OK" % (len(KNOWN_METRICS), len(o)))

    # --- SKIP card: bundle with no budget/default is reported-skipped, never flagged -----------
    f, a, s, o = run(SKIP)
    if f or a:
        errs.append("SKIP: bundle with no budget must not be flagged, got %s %s" % (f, a))
    if not any("bundle_kb" in x and "no budget" in x for x in s):
        errs.append("SKIP: bundle-with-no-budget should be reported as skipped (no silent pass)")

    # --- CWV defaults --------------------------------------------------------------------------
    f, a, s, o = run(DEFAULT_FAIL)
    if not any("cls" in x and "POOR" in x for x in f):
        errs.append("DEFAULT_FAIL: cls 0.3 with no budget should FAIL via the CWV default")
    f, a, s, o = run(DEFAULT_ADVISORY)
    if not any("lcp_ms" in x and "OVER_BUDGET" in x for x in a):
        errs.append("DEFAULT_ADVISORY: lcp 2600 with no budget should be advisory via CWV default")
    if any("lcp_ms" in x for x in f):
        errs.append("DEFAULT_ADVISORY: lcp 2600 (under poor 4000) wrongly a FAIL")

    # --- EMPTY card: all skipped, no crash, no fail/advisory ----------------------------------
    f, a, s, o = run(EMPTY)
    if f or a or o:
        errs.append("EMPTY card should produce no fails/advisories/oks, got %s %s %s" % (f, a, o))
    if not s:
        errs.append("EMPTY card should report skipped metrics, not silently pass")

    # --- malformed cards raise ValueError, not a crash ----------------------------------------
    for label, bad in (("BAD_TYPE (bool-as-number)", BAD_TYPE), ("BAD_SHAPE (metrics not object)", BAD_SHAPE)):
        try:
            run(bad)
            errs.append("%s should have raised ValueError" % label)
        except ValueError:
            pass
        except Exception as e:  # any other exception = a crash, not a clean error
            errs.append("%s raised %s, not ValueError" % (label, type(e).__name__))

    return errs


def _iter_cards(path):
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            for fn in sorted(fns):
                if fn.endswith(".budget.json"):
                    yield os.path.join(dp, fn)
    else:
        yield path


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("budget-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("budget-check: OK — budget comparison verified over good/bad fixtures")
        return 0

    fails, advisories, skipped, oks, n = [], [], [], [], 0
    for fp in _iter_cards(argv[0]):
        try:
            doc = json.load(open(fp, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            fails.append("%s: unreadable (%s)" % (fp, e))
            continue
        for card in (doc if isinstance(doc, list) else [doc]):
            n += 1
            try:
                f, a, s, o = check_card(card)
            except ValueError as e:
                fails.append("%s: malformed card — %s" % (fp, e))
                continue
            fails += f
            advisories += a
            skipped += s
            oks += o

    for x in skipped:
        print("  · SKIP %s" % x)
    for x in advisories:
        print("  ⚠ %s" % x)
    if fails:
        sys.stderr.write("budget-check: FAIL (%d)\n" % len(fails))
        for x in fails:
            sys.stderr.write("  - %s\n" % x)
        return 1
    print("budget-check: OK — %d card(s); %d metric(s) within budget, %d advisory, %d skipped"
          % (n, len(oks), len(advisories), len(skipped)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
