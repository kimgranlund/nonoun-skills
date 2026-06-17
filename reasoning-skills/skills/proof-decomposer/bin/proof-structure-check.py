#!/usr/bin/env python3
"""proof-structure-check.py — the proof-decomposer structure gate. Self-contained (stdlib only).

The defining failure of a confidently-stated proof is a step that *cites itself* (circular
reasoning), *cites a step that does not exist* (a dangling citation / undefined lemma), or a chain
that never actually *reaches the goal* from the premises and axioms. None of these is visible to a
sympathetic read — they are visible to a graph. This is the centerpiece: it represents a proof as a
directed graph of cited steps and mechanically asserts the structural properties a valid deductive
argument must have, so VERIFICATION routes to a check instead of to inference.

Skeleton (JSON) — premises/axioms are the roots; each step cites prior ids via `from`; `goal` is the
id that must be reached:
  {
    "premises": ["p1"],
    "axioms":   ["peano"],
    "steps": [
      {"id": "s1", "from": ["p1", "peano"], "statement": "..."},
      {"id": "s2", "from": ["s1"],          "statement": "..."}
    ],
    "goal": "s2"
  }

It asserts four structural properties, each a FAIL on violation:
  DANGLING     every id in any `from` resolves to a premise, axiom, or earlier-defined step
  CYCLE        the dependency graph is a DAG — no step (transitively) depends on itself
  UNREACHABLE  the `goal` is reachable from premises/axioms through `from` edges
  IRRELEVANT   (advisory) a step that is not on any path to the goal — dead weight, often a tell

  python3 bin/proof-structure-check.py selftest
  python3 bin/proof-structure-check.py <skeleton.json>

Python 3.8+.
"""
import json
import sys


def _roots(doc):
    return set(doc.get("premises", []) or []) | set(doc.get("axioms", []) or [])


def parse_skeleton(doc):
    """Validate shape + normalize. Returns (roots:set, steps:list-of-dict, goal:str). Raises ValueError."""
    if not isinstance(doc, dict):
        raise ValueError("skeleton must be a JSON object")
    if not isinstance(doc.get("steps"), list) or not doc["steps"]:
        raise ValueError("skeleton needs a non-empty 'steps' list")
    roots = _roots(doc)
    if not isinstance(doc.get("premises", []), list) or not isinstance(doc.get("axioms", []), list):
        raise ValueError("'premises' and 'axioms' must be lists")
    steps, seen = [], set()
    for i, s in enumerate(doc["steps"]):
        if not isinstance(s, dict) or not s.get("id"):
            raise ValueError("step %d needs a non-empty 'id'" % i)
        sid = s["id"]
        if sid in seen or sid in roots:
            raise ValueError("duplicate id %r (ids must be unique across premises/axioms/steps)" % sid)
        seen.add(sid)
        frm = s.get("from", []) or []
        if not isinstance(frm, list):
            raise ValueError("step %r 'from' must be a list of ids" % sid)
        steps.append({"id": sid, "from": list(frm), "statement": s.get("statement", "")})
    goal = doc.get("goal")
    if not goal:
        raise ValueError("skeleton needs a 'goal' id")
    if goal not in seen and goal not in roots:
        raise ValueError("'goal' %r is not a defined step, premise, or axiom" % goal)
    return roots, steps, goal


def find_dangling(roots, steps):
    """Cited ids that resolve to nothing — undefined symbol / nonexistent lemma. Returns list of (step, id)."""
    known = set(roots)
    dangling = []
    for s in steps:
        for cited in s["from"]:
            if cited not in known and cited not in {t["id"] for t in steps}:
                dangling.append((s["id"], cited))
        known.add(s["id"])
    return dangling


def find_cycle(roots, steps):
    """Detect a cycle in the citation graph (steps depend on what they cite). Returns a cycle path or None."""
    adj = {s["id"]: [c for c in s["from"] if c not in roots] for s in steps}
    WHITE, GREY, BLACK = 0, 1, 2
    color = {sid: WHITE for sid in adj}
    stack = []

    def visit(u):
        color[u] = GREY
        stack.append(u)
        for v in adj.get(u, []):
            if v not in color:           # cites a root or unknown — not a step edge
                continue
            if color[v] == GREY:         # back-edge -> cycle
                return stack[stack.index(v):] + [v]
            if color[v] == WHITE:
                got = visit(v)
                if got:
                    return got
        color[u] = BLACK
        stack.pop()
        return None

    for sid in adj:
        if color[sid] == WHITE:
            got = visit(sid)
            if got:
                return got
    return None


def reachable_from_roots(roots, steps):
    """The set of step ids whose every dependency chain bottoms out at premises/axioms.

    A step is GROUNDED iff all of its `from` ids are roots or already-grounded steps. Iterate to a
    fixpoint. A circular or root-less cluster never grounds — which is exactly an unreachable goal.
    """
    by_id = {s["id"]: s for s in steps}
    grounded = set(roots)
    changed = True
    while changed:
        changed = False
        for s in steps:
            if s["id"] in grounded:
                continue
            if all(c in grounded for c in s["from"]):
                grounded.add(s["id"])
                changed = True
    return {sid for sid in by_id if sid in grounded}


def find_irrelevant(roots, steps, goal):
    """Steps that are NOT on any path to the goal (the goal does not transitively cite them)."""
    by_id = {s["id"]: s for s in steps}
    needed, frontier = set(), [goal]
    while frontier:
        cur = frontier.pop()
        if cur in needed or cur in roots:
            continue
        needed.add(cur)
        for c in by_id.get(cur, {"from": []})["from"]:
            frontier.append(c)
    return [s["id"] for s in steps if s["id"] not in needed]


def check(doc):
    """Run all structural checks. Returns (ok:bool, report:dict)."""
    roots, steps, goal = parse_skeleton(doc)
    dangling = find_dangling(roots, steps)
    cycle = find_cycle(roots, steps)
    grounded = reachable_from_roots(roots, steps)
    goal_reachable = goal in roots or goal in grounded
    irrelevant = find_irrelevant(roots, steps, goal) if goal_reachable and not cycle else []
    fails = []
    if dangling:
        fails.append("DANGLING: " + ", ".join("%s cites missing %s" % (s, c) for s, c in dangling))
    if cycle:
        fails.append("CYCLE: circular reasoning " + " -> ".join(cycle))
    if not goal_reachable:
        fails.append("UNREACHABLE: goal %r is not grounded in the premises/axioms" % goal)
    report = {
        "roots": sorted(roots), "n_steps": len(steps), "goal": goal,
        "dangling": dangling, "cycle": cycle, "goal_reachable": goal_reachable,
        "irrelevant": irrelevant, "fails": fails,
    }
    return (not fails), report


# --- selftest fixtures -------------------------------------------------------------------------
VALID = {
    "premises": ["p1"], "axioms": ["A"],
    "steps": [
        {"id": "s1", "from": ["p1", "A"], "statement": "from p1 and axiom A"},
        {"id": "s2", "from": ["s1"], "statement": "from s1"},
        {"id": "s3", "from": ["s2", "A"], "statement": "the goal"},
    ],
    "goal": "s3",
}
CIRCULAR = {   # s1 from s2, s2 from s1 — neither grounds; also a cycle
    "premises": ["p1"], "axioms": [],
    "steps": [
        {"id": "s1", "from": ["s2"], "statement": "A because B"},
        {"id": "s2", "from": ["s1"], "statement": "B because A"},
    ],
    "goal": "s2",
}
DANGLING = {   # s2 cites lemmaX which is never defined
    "premises": ["p1"], "axioms": [],
    "steps": [
        {"id": "s1", "from": ["p1"], "statement": "ok"},
        {"id": "s2", "from": ["s1", "lemmaX"], "statement": "by the (unproven) lemma X"},
    ],
    "goal": "s2",
}
UNREACHABLE = {   # goal step cites only itself's sibling that never grounds; goal cites nothing rooted
    "premises": ["p1"], "axioms": [],
    "steps": [
        {"id": "s1", "from": ["p1"], "statement": "grounded"},
        {"id": "g", "from": ["s2"], "statement": "goal"},
        {"id": "s2", "from": ["s2"], "statement": "self-loop, never grounds"},
    ],
    "goal": "g",
}
IRRELEVANT = {   # valid + reaches goal, but s_dead is off any path to the goal
    "premises": ["p1"], "axioms": [],
    "steps": [
        {"id": "s1", "from": ["p1"], "statement": "used"},
        {"id": "s_dead", "from": ["p1"], "statement": "computed but never cited toward the goal"},
        {"id": "s2", "from": ["s1"], "statement": "goal"},
    ],
    "goal": "s2",
}


def selftest():
    errs = []
    ok, rep = check(VALID)
    if not ok:
        errs.append("VALID should pass, got fails=%s" % rep["fails"])
    if rep["irrelevant"]:
        errs.append("VALID should have no irrelevant steps, got %s" % rep["irrelevant"])

    ok, rep = check(CIRCULAR)
    if ok or not rep["cycle"]:
        errs.append("CIRCULAR should fail with a cycle, got %s" % rep["fails"])

    ok, rep = check(DANGLING)
    if ok or not rep["dangling"]:
        errs.append("DANGLING should fail with a dangling citation, got %s" % rep["fails"])

    ok, rep = check(UNREACHABLE)
    if ok or rep["goal_reachable"]:
        errs.append("UNREACHABLE should fail (goal not grounded), got %s" % rep["fails"])

    ok, rep = check(IRRELEVANT)
    if not ok:
        errs.append("IRRELEVANT skeleton should still PASS the gates, got fails=%s" % rep["fails"])
    if "s_dead" not in rep["irrelevant"]:
        errs.append("IRRELEVANT should flag s_dead as off-path, got %s" % rep["irrelevant"])

    # parse_skeleton rejects malformed shapes
    for bad in ({}, {"steps": []}, {"steps": [{"from": []}]}, {"steps": [{"id": "a"}], "goal": "zzz"},
                {"steps": [{"id": "a"}, {"id": "a"}], "goal": "a"}):
        try:
            parse_skeleton(bad)
            errs.append("parse_skeleton accepted malformed: %s" % bad)
        except ValueError:
            pass
    return errs


def _print_report(rep):
    print("PROOF structure check — %d step(s), goal=%s, roots={%s}"
          % (rep["n_steps"], rep["goal"], ", ".join(rep["roots"])))
    print("  %-12s %s" % ("dangling", "none" if not rep["dangling"]
          else ", ".join("%s->%s" % (s, c) for s, c in rep["dangling"])))
    print("  %-12s %s" % ("cycle", "none (DAG)" if not rep["cycle"] else " -> ".join(rep["cycle"])))
    print("  %-12s %s" % ("goal", "reachable" if rep["goal_reachable"] else "UNREACHABLE"))
    print("  %-12s %s" % ("irrelevant", "none" if not rep["irrelevant"] else ", ".join(rep["irrelevant"])))


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("proof-structure-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("proof-structure-check: OK — dangling / cycle / reachability / irrelevance verified over fixtures")
        return 0
    try:
        doc = json.load(open(argv[0], encoding="utf-8"))
        ok, rep = check(doc)
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write("proof-structure-check: bad skeleton — %s\n" % e)
        return 2
    except ValueError as e:
        sys.stderr.write("proof-structure-check: invalid skeleton — %s\n" % e)
        return 2
    _print_report(rep)
    if rep["irrelevant"]:
        print("  ⚠ %d irrelevant step(s) off any path to the goal (advisory): %s"
              % (len(rep["irrelevant"]), ", ".join(rep["irrelevant"])))
    if not ok:
        sys.stderr.write("proof-structure-check: FAIL — %s\n" % "; ".join(rep["fails"]))
        return 1
    print("proof-structure-check: PASS — citation graph is a DAG, no dangling refs, goal reachable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
