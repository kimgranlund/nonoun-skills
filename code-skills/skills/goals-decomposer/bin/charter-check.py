#!/usr/bin/env python3
"""charter-check.py — the goals-decomposer MEASURABILITY gate. Self-contained (stdlib only).

A goals / charter / PRD doc is the OUTSIDE-IN plane: *what are we trying to do, and how do we know it's
good?* Most of grading it is judgment (the AIM axis — is the diagnosis real, are the goals the right
ones, ranked and coherent — Rumelt's strategy kernel), and that stays in SKILL.md. But the MEASURABILITY
axis has joints that are arithmetic, not taste — a fluffy charter "feels" ambitious but you cannot tell
when it's met. Those route here so a precise-but-wrong or a vague-but-right charter can't pass on looks:

  WELL_FORMED        required fields present, ranks/types in range
  NO_DIAGNOSIS       no stated problem/challenge — goals with no diagnosis is Rumelt's "bad strategy"
  UNRANKED           characteristics aren't a strict priority order (ties, esp. at the top — "if
                     everything is P0, nothing is")
  FLUFF              a characteristic / quality goal with no metric — "be scalable" with no number
  UNMEASURABLE_KPI   a goal with a metric but missing a threshold (or a window for a characteristic)
  VACUOUS_ACCEPTANCE an acceptance criterion that is only vague adjectives ("works well", "intuitive")
                     with no number or comparator — not a checkable predicate
  OUTPUT_NOT_OUTCOME a goal phrased as a build-output ("ship X", "add Y") not an outcome (a change in
                     user/system behavior) — Perri's build trap
  CONTRADICTION      a non-goal names a characteristic the charter also pursues (pursue-and-exclude)
  NO_NONGOALS        no explicit non-goals / scope boundary — unbounded scope

This is a PRE-FILTER, not an oracle: a clean run means the charter is well-formed, ranked, and
*falsifiable* — it does NOT mean the aims are the RIGHT ones or that a metric captures its outcome
(Goodhart). That is the AIM axis, judged + adversarially verified. A perfectly measurable charter can
optimize precisely the wrong thing.

  python3 bin/charter-check.py lint <charter.json>      # the measurability gate
  python3 bin/charter-check.py selftest                  # green (sound) / red (fluffy) fixtures
  python3 bin/charter-check.py lint <charter> --json     # the shared {tool, ok, summary, findings} report

A *.charter.json doc:
  {"title": "...",
   "diagnosis": "the problem/challenge actually being faced (what's wrong, not the goal)",
   "characteristics": [{"name","rank":int,"outcome","metric","threshold","window","rationale"}],
   "principles": ["the rules that shape choices", ...],
   "non_goals": ["explicit scope boundaries", ...],
   "acceptance": [{"criterion","metric","threshold"}]}
Python 3.8+.
"""
import json
import re
import sys

# quality adjectives that carry no measurement — an acceptance criterion made only of these is vacuous
VAGUE = {"works", "well", "good", "great", "fast", "slow", "robust", "reliable", "scalable", "intuitive",
         "easy", "simple", "nice", "clean", "modern", "better", "best", "seamless", "smooth", "snappy",
         "performant", "efficient", "secure", "flexible", "maintainable", "usable", "delightful",
         "powerful", "lightweight", "solid", "smart", "elegant", "quality", "high", "low"}
# a goal that starts with a build-verb is an output, not an outcome (the build trap)
BUILD_VERBS = {"ship", "build", "add", "implement", "create", "launch", "deliver", "release", "develop",
               "write", "make", "introduce", "integrate", "support", "enable", "provide"}
STOPWORDS = {"a", "an", "the", "is", "are", "be", "to", "of", "and", "or", "it", "in", "on", "with",
             "for", "that", "this", "should", "must", "will", "we", "our", "they", "their", "very"}


def _num(s):
    """A strict measurement — a digit or comparator symbol. Used for a threshold, which must be numeric."""
    return bool(re.search(r"\d|[<>≤≥%]", str(s or "")))


def _measured(s):
    """A broader 'is this falsifiable' test for acceptance prose — a number, a comparator word, or a
    unit (so 'ships a change in under a day' counts, but 'works well' does not)."""
    t = str(s or "").lower()
    if re.search(r"\d|[<>≤≥%]", t):
        return True
    if re.search(r"\b(under|over|within|below|above|least|most|fewer|exceeds?|per|each|before|after)\b", t):
        return True
    return bool(re.search(r"\b(ms|sec|secs|seconds?|mins?|minutes?|hours?|hrs?|days?|weeks?|months?"
                          r"|years?|requests?|users?|errors?|clicks?|steps?)\b", t))


def _words(s):
    return re.findall(r"[a-z']+", str(s or "").lower())


def check_charter(card):
    """Return (fails, warns), each a list of (kind, message)."""
    fails, warns = [], []

    def F(k, m):
        fails.append((k, m))

    def W(k, m):
        warns.append((k, m))

    if not isinstance(card, dict):
        F("WELL_FORMED", "charter is not a JSON object (got %s)" % type(card).__name__)
        return fails, warns
    title = card.get("title", "<charter>")

    if not (isinstance(card.get("diagnosis"), str) and card["diagnosis"].strip()):
        F("NO_DIAGNOSIS", "%s: NO_DIAGNOSIS — no stated problem/challenge; goals with no diagnosis is "
          "'bad strategy' (you can't tell what the goals are even FOR)" % title)

    chars = card.get("characteristics")
    if chars is None:
        chars = []
    elif not isinstance(chars, list):
        F("WELL_FORMED", "%s: characteristics is not a list" % title)
        chars = []
    chars = [c for c in chars if isinstance(c, dict)]

    # ranking: a strict priority order — duplicate ranks (especially the top) mean nothing is prioritized
    ranks = [c.get("rank") for c in chars if isinstance(c.get("rank"), int) and not isinstance(c.get("rank"), bool)]
    if chars and len(ranks) != len(chars):
        F("WELL_FORMED", "%s: every characteristic needs an integer rank" % title)
    elif ranks and len(set(ranks)) != len(ranks):
        F("UNRANKED", "%s: UNRANKED — characteristics share ranks %s; a charter must be a strict "
          "priority order ('if everything is P0, nothing is')"
          % (title, sorted({r for r in ranks if ranks.count(r) > 1})))

    char_names = set()
    for c in chars:
        name = c.get("name", "?")
        char_names.add(str(name).lower().strip())
        # FLUFF: a quality goal with no metric at all
        if not (c.get("metric") and str(c.get("metric")).strip()):
            F("FLUFF", "%s: FLUFF — characteristic '%s' has no metric (a quality goal you can't measure "
              "is fluff, not a goal)" % (title, name))
        else:
            # has a metric — but is it complete? threshold + window make it checkable
            if not (c.get("threshold") and _num(c.get("threshold"))):
                F("UNMEASURABLE_KPI", "%s: UNMEASURABLE_KPI — characteristic '%s' metric %r has no "
                  "numeric threshold (you can't pass/fail it)" % (title, name, c.get("metric")))
            if not (c.get("window") and str(c.get("window")).strip()):
                W("UNMEASURABLE_KPI", "%s: characteristic '%s' has no window/condition (under what load "
                  "/ over what period?)" % (title, name))
        # OUTPUT_NOT_OUTCOME: phrased as a build-output, not a change in behavior
        outcome = c.get("outcome") or c.get("name") or ""
        first = (_words(outcome) or [""])[0]
        if first in BUILD_VERBS:
            W("OUTPUT_NOT_OUTCOME", "%s: OUTPUT_NOT_OUTCOME — '%s' is phrased as an output (%r…), not "
              "an outcome (a measurable change in behavior/state)" % (title, name, first))
        # UNTRACED: a goal with no rationale tying it to the diagnosis
        if not (c.get("rationale") and str(c.get("rationale")).strip()):
            W("UNTRACED_GOAL", "%s: characteristic '%s' has no rationale tracing it to the diagnosis"
              % (title, name))

    # acceptance criteria must be checkable predicates, not vibes
    acc = card.get("acceptance") or []
    if isinstance(acc, list):
        for a in acc:
            if not isinstance(a, dict):
                F("WELL_FORMED", "%s: an acceptance entry is not an object" % title)
                continue
            crit = a.get("criterion", "")
            measured = _measured(crit) or _num(a.get("threshold")) or _num(a.get("metric"))
            content = [w for w in _words(crit) if w not in STOPWORDS and len(w) > 2]
            vague_dominated = content and sum(1 for w in content if w in VAGUE) / len(content) >= 0.5
            if not measured and (not content or vague_dominated):
                F("VACUOUS_ACCEPTANCE", "%s: VACUOUS_ACCEPTANCE — criterion %r has no measurable "
                  "predicate and is dominated by vague adjectives; not a checkable predicate"
                  % (title, crit))
            elif not measured:
                W("VACUOUS_ACCEPTANCE", "%s: acceptance %r has no number/comparator — is it really "
                  "falsifiable?" % (title, crit))

    # CONTRADICTION: a non-goal naming a characteristic the charter also pursues
    nongoals = card.get("non_goals") or []
    if not nongoals:
        W("NO_NONGOALS", "%s: NO_NONGOALS — no explicit non-goals; scope is unbounded (name what this "
          "is NOT)" % title)
    for ng in nongoals if isinstance(nongoals, list) else []:
        ng_words = set(_words(ng))
        hit = [n for n in char_names if n and n in ng_words]
        if hit:
            W("CONTRADICTION", "%s: CONTRADICTION — non-goal %r excludes %s, which the charter also "
              "pursues as a characteristic" % (title, ng, hit[0]))
    return fails, warns


# --- fixtures ----------------------------------------------------------------------------------
GREEN = {
    "title": "Checkout service",
    "diagnosis": "Cart abandonment spikes at peak because checkout p99 latency degrades under load and "
                 "a single failure takes the whole flow down.",
    "characteristics": [
        {"name": "scalability", "rank": 1, "outcome": "checkout stays responsive under peak traffic",
         "metric": "p99 checkout latency", "threshold": "< 300ms", "window": "at 10x baseline load",
         "rationale": "abandonment tracks latency above 300ms (diagnosis)"},
        {"name": "resilience", "rank": 2, "outcome": "a downstream failure degrades, not collapses",
         "metric": "successful-checkout rate during a payment-provider outage", "threshold": "> 95%",
         "window": "during a single-provider outage", "rationale": "single failure took the flow down"},
        {"name": "evolvability", "rank": 3, "outcome": "a pricing change ships without touching checkout",
         "metric": "modules touched by a pricing-rule change", "threshold": "<= 1", "window": "per change",
         "rationale": "pricing churn must not destabilize the hot path"},
    ],
    "principles": ["fail open to a queue, never to an error", "no synchronous calls on the hot path"],
    "non_goals": ["not multi-region in v1", "not a rewrite of the catalog service"],
    "acceptance": [
        {"criterion": "p99 checkout latency stays under 300ms at 10x load", "metric": "p99", "threshold": "300ms"},
        {"criterion": "checkout succeeds for >95% of carts during a simulated provider outage"},
    ],
}
# RED — the charter's failure modes: no diagnosis, tied ranks, a fluffy metric-less goal, an
# unmeasurable KPI, a vacuous acceptance criterion, an output-not-outcome, a contradiction, no non-goals.
RED = {
    "title": "Platform v2",
    "characteristics": [
        {"name": "fast", "rank": 1, "outcome": "make it fast"},
        {"name": "reliable", "rank": 1, "outcome": "ship the new reliability layer",
         "metric": "uptime"},
    ],
    "principles": ["be modern"],
    "non_goals": [],
    "acceptance": [{"criterion": "the platform works well and feels snappy"}],
}


def selftest():
    errs = []
    gf, gw = check_charter(GREEN)
    if gf:
        errs.append("GREEN charter produced FAILs: %s" % gf)
    if gw:
        errs.append("GREEN charter produced false-positive WARNs: %s" % gw)
    rf, rw = check_charter(RED)
    rk = {k for k, _ in rf}
    rwk = {k for k, _ in rw}
    for kind in ["NO_DIAGNOSIS", "UNRANKED", "FLUFF", "UNMEASURABLE_KPI", "VACUOUS_ACCEPTANCE"]:
        if kind not in rk:
            errs.append("RED charter missed gate-fail %s (fails=%s)" % (kind, sorted(rk)))
    for kind in ["NO_NONGOALS", "OUTPUT_NOT_OUTCOME"]:
        if kind not in rwk:
            errs.append("RED charter missed warn %s (warns=%s)" % (kind, sorted(rwk)))
    # _num: a measurement is a digit or a comparator, not an adjective
    if not (_num("< 300ms") and _num("p99") and not _num("very fast") and not _num("robust")):
        errs.append("_num measurement detection wrong")
    # adversarial: a strict-ranked, fully-measured characteristic must NOT trip FLUFF/UNRANKED
    okf, _ = check_charter({"diagnosis": "x", "characteristics": [
        {"name": "a", "rank": 1, "metric": "m", "threshold": "< 5ms", "window": "at load", "rationale": "r"}],
        "non_goals": ["y"], "acceptance": [{"criterion": "m stays < 5ms at load"}]})
    if any(k in ("FLUFF", "UNRANKED", "UNMEASURABLE_KPI", "VACUOUS_ACCEPTANCE") for k, _ in okf):
        errs.append("false-positive on a sound single-characteristic charter: %s" % okf)
    # malformed inputs must FAIL cleanly, never raise
    for bad in [[], None, "txt", {"characteristics": "oops"}, {"acceptance": [1]}]:
        try:
            mf, _mw = check_charter(bad)
        except Exception as exc:  # noqa: BLE001
            errs.append("check_charter crashed on %r (%s)" % (bad, exc))
    return errs


def _report(card, fails, warns, as_json):
    title = card.get("title", "<charter>") if isinstance(card, dict) else "<charter>"
    if as_json:
        find = [{"kind": k, "severity": "fail", "location": title, "message": m} for k, m in fails]
        find += [{"kind": k, "severity": "advisory", "location": title, "message": m} for k, m in warns]
        print(json.dumps({"tool": "charter-check", "ok": not fails,
                          "summary": "%d fail, %d advisory" % (len(fails), len(warns)),
                          "findings": find}, indent=2))
        return 1 if fails else 0
    for _k, w in warns:
        print("  ⚠ %s" % w)
    if fails:
        sys.stderr.write("charter-check: FAIL (%d)\n" % len(fails))
        for _k, f in fails:
            sys.stderr.write("  - %s\n" % f)
        return 1
    print("charter-check: OK — measurability gates clear (diagnosis, ranked, falsifiable); the AIM axis "
          "(are these the RIGHT aims?) is judged separately")
    return 0


def main(argv):
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("charter-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("charter-check: OK — green (sound) clean, red (fluffy) caught; measurement detection verified")
        return 0
    if argv[0] == "lint":
        try:
            card = json.load(open(argv[1], encoding="utf-8"))
        except (OSError, IndexError, json.JSONDecodeError) as e:
            sys.stderr.write("charter-check: unreadable charter (%s)\n" % e)
            return 2
        fails, warns = check_charter(card)
        return _report(card, fails, warns, as_json)
    sys.stderr.write("usage: charter-check.py lint <charter.json> | selftest [--json]\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
