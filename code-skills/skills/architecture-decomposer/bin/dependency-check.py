#!/usr/bin/env python3
"""dependency-check.py — the architecture-decomposer INTEGRITY gate. Self-contained (stdlib only).

The STRUCTURE axis ("is it the right decomposition?") is where an LLM is strong and reads the design
top-down. The INTEGRITY axis ("does the structure actually HOLD, here?") is where an LLM fails
silently — it cannot reliably tell by eye whether a dependency graph is acyclic or whether every
edge respects the declared layering. So that axis is **routed to code**: this tool reads an
architecture *contract card* (the component dependency graph + the ordered layers) and flags the
mechanical defects deterministically.

Contract card (JSON):
  {
    "components": ["ui", "api", "domain", "db"],     # the nodes (modules / containers)
    "layers":     ["ui", "api", "domain", "db"],     # ORDERED top → bottom; a component in a higher
                                                     # layer may depend DOWN, never UP
    "layer_of":   {"ui": "ui", "api": "api", ...},   # optional: component -> layer name. If a
                                                     # component IS its own layer, this can be omitted
                                                     # and the component name is used as the layer.
    "edges":      [["ui", "api"], ["api", "domain"]] # an edge a->b means "a depends on b"
  }

Flags (gate failures BLOCK the finer reviews on the INTEGRITY axis):
  CYCLE            a dependency cycle (a transitively depends on itself) — Tarjan SCC. GATE (B2).
  LAYER_VIOLATION  an edge from a lower layer to a higher one (depends UP). GATE (B3).
Flags (advisory — surfaced for the review levels, never block):
  HIGH_COUPLING    a component whose fan-in or fan-out exceeds the threshold. REVIEW (B4).
  ORPHAN           a component with no edges in or out (dead / disconnected). REVIEW.

A clean DAG with no flags is INTEGRITY-sound on the mechanical levels (B1/B2/B3) — necessary, NOT
sufficient: a graph can be acyclic and layered yet have the WRONG boundaries (the STRUCTURE axis,
which this tool cannot see). Gate where you can; review the rest.

  python3 bin/dependency-check.py selftest
  python3 bin/dependency-check.py <card.json> [--max-fanin N] [--max-fanout N]
  python3 bin/dependency-check.py [--json] <card.json>   # machine-readable report
  python3 bin/dependency-check.py template

`--json` (additive reporting flag; parse-anywhere in argv) prints ONE machine-readable report object to
stdout and NOTHING else there — the shared schema every lint bin emits:
  {"tool": "dependency-check", "ok": <bool>, "summary": "<one line>",
   "findings": [{"kind", "severity": fail|advisory, "location": "<node/edge label>", "message"}, ...]}
`ok` is true iff no GATE finding (the exact condition that gives exit 0 in human mode). A gate flag
(CYCLE / LAYER_VIOLATION) maps to severity `fail`; an advisory one (HIGH_COUPLING / ORPHAN) to
`advisory`. The exit code is UNCHANGED by --json. Without --json, output + exit are byte-identical.

Python 3.8+.
"""
import json
import sys

DEFAULT_MAX_FANIN = 5
DEFAULT_MAX_FANOUT = 5

# Severity by flag kind: a gate blocks; advisory only informs.
GATE_KINDS = {"CYCLE", "LAYER_VIOLATION"}
ADVISORY_KINDS = {"HIGH_COUPLING", "ORPHAN"}


def parse_card(doc):
    """Validate + normalize a contract card. Raises ValueError on a malformed card."""
    if not isinstance(doc, dict):
        raise ValueError("card must be a JSON object")
    comps = doc.get("components")
    if not isinstance(comps, list) or not comps or not all(isinstance(c, str) for c in comps):
        raise ValueError("'components' must be a non-empty list of strings")
    compset = set(comps)
    if len(compset) != len(comps):
        raise ValueError("'components' has duplicates")

    layers = doc.get("layers", [])
    if not isinstance(layers, list) or not all(isinstance(l, str) for l in layers):
        raise ValueError("'layers' must be a list of strings")
    if len(set(layers)) != len(layers):
        raise ValueError("'layers' has duplicates")

    layer_of = doc.get("layer_of", {})
    if not isinstance(layer_of, dict):
        raise ValueError("'layer_of' must be an object (component -> layer)")
    for c, l in layer_of.items():
        if c not in compset:
            raise ValueError("layer_of references unknown component %r" % c)
        if layers and l not in layers:
            raise ValueError("layer_of maps %r to unknown layer %r" % (c, l))

    edges = doc.get("edges", [])
    if not isinstance(edges, list):
        raise ValueError("'edges' must be a list of [from, to] pairs")
    norm_edges = []
    for e in edges:
        if not (isinstance(e, list) and len(e) == 2 and all(isinstance(x, str) for x in e)):
            raise ValueError("each edge must be a [from, to] pair of strings, got %r" % (e,))
        a, b = e
        if a not in compset or b not in compset:
            raise ValueError("edge %r references an unknown component" % (e,))
        norm_edges.append((a, b))

    return {"components": comps, "layers": layers, "layer_of": layer_of, "edges": norm_edges}


def _adjacency(card):
    adj = {c: [] for c in card["components"]}
    for a, b in card["edges"]:
        adj[a].append(b)
    return adj


def find_cycles(card):
    """All cycles via Tarjan's strongly-connected-components. An SCC with >1 node, or a single node
    with a self-loop, is a cycle. Returns a list of node-lists (one per cyclic SCC)."""
    adj = _adjacency(card)
    index_counter = [0]
    stack = []
    lowlink = {}
    index = {}
    on_stack = {}
    sccs = []
    self_loops = {a for a, b in card["edges"] if a == b}

    # iterative Tarjan to avoid recursion-depth limits on large graphs
    def strongconnect(root):
        work = [(root, 0)]
        while work:
            v, pi = work[-1]
            if pi == 0:
                index[v] = lowlink[v] = index_counter[0]
                index_counter[0] += 1
                stack.append(v)
                on_stack[v] = True
            recurse = False
            i = pi
            while i < len(adj[v]):
                w = adj[v][i]
                if w not in index:
                    work[-1] = (v, i + 1)
                    work.append((w, 0))
                    recurse = True
                    break
                elif on_stack.get(w):
                    lowlink[v] = min(lowlink[v], index[w])
                i += 1
            if recurse:
                continue
            if lowlink[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    comp.append(w)
                    if w == v:
                        break
                if len(comp) > 1 or comp[0] in self_loops:
                    sccs.append(comp)
            work.pop()
            if work:
                parent = work[-1][0]
                lowlink[parent] = min(lowlink[parent], lowlink[v])

    for v in card["components"]:
        if v not in index:
            strongconnect(v)
    return sccs


def _layer_index(card):
    """component -> its layer's position in the ordered `layers` list. A component with no mapping
    and a name that IS a declared layer maps to that layer; otherwise it has no layer position."""
    order = {l: i for i, l in enumerate(card["layers"])}
    pos = {}
    for c in card["components"]:
        layer = card["layer_of"].get(c, c)  # default: the component is its own layer
        if layer in order:
            pos[c] = order[layer]
    return pos


def find_layer_violations(card):
    """An edge a->b (a depends on b) violates layering when b sits in a HIGHER layer than a.
    Layers are ordered top→bottom, so a higher layer has a SMALLER index. Depending up (b's index <
    a's index) is the violation. Same-layer edges are allowed (caught as cycles if circular)."""
    pos = _layer_index(card)
    violations = []
    for a, b in card["edges"]:
        if a in pos and b in pos and pos[b] < pos[a]:
            violations.append({
                "from": a, "from_layer": card["layers"][pos[a]],
                "to": b, "to_layer": card["layers"][pos[b]],
            })
    return violations


def coupling(card, max_fanin=DEFAULT_MAX_FANIN, max_fanout=DEFAULT_MAX_FANOUT):
    """Fan-in (incoming deps) and fan-out (outgoing deps) per component; flag those over threshold."""
    fanin = {c: 0 for c in card["components"]}
    fanout = {c: 0 for c in card["components"]}
    for a, b in card["edges"]:
        if a != b:
            fanout[a] += 1
            fanin[b] += 1
    hot = []
    for c in card["components"]:
        if fanin[c] > max_fanin or fanout[c] > max_fanout:
            hot.append({"component": c, "fanin": fanin[c], "fanout": fanout[c]})
    return {"fanin": fanin, "fanout": fanout, "high_coupling": hot}


def find_orphans(card):
    """Components with zero edges in OR out (ignoring self-loops) — disconnected from the graph."""
    touched = set()
    for a, b in card["edges"]:
        if a != b:
            touched.add(a)
            touched.add(b)
    return [c for c in card["components"] if c not in touched]


def analyze(card, max_fanin=DEFAULT_MAX_FANIN, max_fanout=DEFAULT_MAX_FANOUT):
    """Run every check; return findings + an overall verdict (a gate flag -> FAIL)."""
    findings = []
    for scc in find_cycles(card):
        findings.append({"kind": "CYCLE", "gate": True,
                         "loc": " -> ".join(scc + [scc[0]]),
                         "detail": "cycle among: %s" % " -> ".join(scc + [scc[0]])})
    for v in find_layer_violations(card):
        findings.append({"kind": "LAYER_VIOLATION", "gate": True,
                         "loc": "%s -> %s" % (v["from"], v["to"]),
                         "detail": "%s (%s) depends UP on %s (%s)"
                         % (v["from"], v["from_layer"], v["to"], v["to_layer"])})
    coup = coupling(card, max_fanin, max_fanout)
    for h in coup["high_coupling"]:
        findings.append({"kind": "HIGH_COUPLING", "gate": False,
                         "loc": h["component"],
                         "detail": "%s has fan-in=%d fan-out=%d (max in=%d out=%d)"
                         % (h["component"], h["fanin"], h["fanout"], max_fanin, max_fanout)})
    for o in find_orphans(card):
        findings.append({"kind": "ORPHAN", "gate": False,
                         "loc": o,
                         "detail": "%s has no dependencies in or out" % o})
    gate_fails = [f for f in findings if f["gate"]]
    return {"status": "FAIL" if gate_fails else "PASS",
            "findings": findings, "gate_fails": gate_fails, "coupling": coup}


# --- machine-readable report (--json) ----------------------------------------------------------
# ONE shared schema across every lint bin: {tool, ok, summary, findings:[{kind, severity, location,
# message}]}. `ok` is true iff no blocking finding (the same condition that gives exit 0 in human mode).
# Printed via json.dumps(indent=2); nothing else goes to stdout under --json.
def _report_json(tool, ok, summary, findings):
    """Emit the shared report object to stdout (and nothing else). `findings` is a list of dicts already
    in {kind, severity, location, message} shape. Returns the dict so callers/selftests can reuse it."""
    report = {"tool": tool, "ok": ok, "summary": summary, "findings": findings}
    print(json.dumps(report, indent=2))
    return report


def build_report(res):
    """Build the JSON report from analyze()'s result. A gate flag (CYCLE / LAYER_VIOLATION) → severity
    `fail`; an advisory one (HIGH_COUPLING / ORPHAN) → `advisory`. `ok` is true iff no gate flag — the
    exact PASS/exit-0 condition of analyze()."""
    out, gates = [], 0
    for f in res["findings"]:
        if f["gate"]:
            gates += 1
        out.append({"kind": f["kind"], "severity": "fail" if f["gate"] else "advisory",
                    "location": f["loc"], "message": f["detail"]})
    ok = gates == 0
    if not out:
        summary = "acyclic + layered + bounded — no mechanical defects"
    else:
        summary = ("%d finding(s) (%d gate, %d advisory) — confirm boundaries by review"
                   % (len(out), gates, len(out) - gates))
    return {"tool": "dependency-check", "ok": ok, "summary": summary, "findings": out}


TEMPLATE = {
    "components": ["ui", "api", "domain", "db"],
    "layers": ["ui", "api", "domain", "db"],
    "layer_of": {"ui": "ui", "api": "api", "domain": "domain", "db": "db"},
    "edges": [["ui", "api"], ["api", "domain"], ["domain", "db"]],
}


def selftest():
    errs = []

    # --- parse_card: rejects malformed cards (lock the input contract) ---
    for bad in (
        [],                                                   # not an object
        {"components": []},                                   # empty components
        {"components": ["a", "a"]},                           # duplicate component
        {"components": ["a"], "edges": [["a", "ghost"]]},     # edge to unknown node
        {"components": ["a"], "edges": [["a"]]},              # malformed edge
        {"components": ["a"], "layers": ["x", "x"]},          # duplicate layer
        {"components": ["a"], "layer_of": {"a": "nope"}, "layers": ["x"]},  # unknown layer
        {"components": ["a"], "layer_of": {"ghost": "x"}, "layers": ["x"]},  # unknown comp in map
    ):
        try:
            parse_card(bad)
            errs.append("parse_card accepted malformed: %r" % (bad,))
        except ValueError:
            pass

    # --- MUST-NOT-FLAG: a clean DAG passes, no findings at all ---
    clean = parse_card({
        "components": ["ui", "api", "domain", "db"],
        "layers": ["ui", "api", "domain", "db"],
        "edges": [["ui", "api"], ["api", "domain"], ["domain", "db"], ["ui", "domain"]],
    })
    res = analyze(clean)
    if res["status"] != "PASS":
        errs.append("clean DAG should PASS, got %s" % res["status"])
    if res["findings"]:
        errs.append("clean DAG should have zero findings, got %r" % res["findings"])

    # --- MUST-FLAG CYCLE: a 2-cycle a<->b ---
    two_cycle = parse_card({"components": ["a", "b"], "edges": [["a", "b"], ["b", "a"]]})
    res = analyze(two_cycle)
    cyc = [f for f in res["findings"] if f["kind"] == "CYCLE"]
    if not cyc:
        errs.append("2-cycle should flag CYCLE, got %r" % res["findings"])
    if res["status"] != "FAIL":
        errs.append("a cycle must FAIL the gate, got %s" % res["status"])

    # MUST-NOT-FLAG (cycle false-positive guard): a diamond is acyclic, must NOT flag CYCLE
    diamond = parse_card({"components": ["a", "b", "c", "d"],
                          "edges": [["a", "b"], ["a", "c"], ["b", "d"], ["c", "d"]]})
    if [f for f in analyze(diamond)["findings"] if f["kind"] == "CYCLE"]:
        errs.append("a diamond (shared dependency, no cycle) must NOT flag CYCLE")

    # self-loop is a cycle of one
    selfloop = parse_card({"components": ["a", "b"], "edges": [["a", "a"], ["a", "b"]]})
    if not [f for f in analyze(selfloop)["findings"] if f["kind"] == "CYCLE"]:
        errs.append("a self-loop should flag CYCLE")

    # a longer 3-cycle a->b->c->a
    three = parse_card({"components": ["a", "b", "c"],
                        "edges": [["a", "b"], ["b", "c"], ["c", "a"]]})
    if analyze(three)["status"] != "FAIL":
        errs.append("a 3-cycle must FAIL")

    # --- MUST-FLAG LAYER_VIOLATION: a lower layer depends UP on a higher one ---
    layered = parse_card({
        "components": ["ui", "domain"],
        "layers": ["ui", "domain"],            # ui is higher (index 0), domain lower (index 1)
        "edges": [["domain", "ui"]],           # domain (lower) depends UP on ui (higher) -> violation
    })
    res = analyze(layered)
    lv = [f for f in res["findings"] if f["kind"] == "LAYER_VIOLATION"]
    if not lv:
        errs.append("a lower->higher edge should flag LAYER_VIOLATION, got %r" % res["findings"])
    if res["status"] != "FAIL":
        errs.append("a layer violation must FAIL the gate, got %s" % res["status"])

    # MUST-NOT-FLAG (layer false-positive guard): the SAME graph depending DOWN is legal
    legal = parse_card({
        "components": ["ui", "domain"],
        "layers": ["ui", "domain"],
        "edges": [["ui", "domain"]],           # ui (higher) depends DOWN on domain (lower) -> OK
    })
    if [f for f in analyze(legal)["findings"] if f["kind"] == "LAYER_VIOLATION"]:
        errs.append("a higher->lower (down) edge must NOT flag LAYER_VIOLATION")

    # same-layer edge is not a layer violation (it's a cycle only if circular)
    same = parse_card({
        "components": ["a", "b"], "layers": ["L"],
        "layer_of": {"a": "L", "b": "L"}, "edges": [["a", "b"]],
    })
    if [f for f in analyze(same)["findings"] if f["kind"] == "LAYER_VIOLATION"]:
        errs.append("a same-layer edge must NOT flag LAYER_VIOLATION")

    # --- MUST-FLAG HIGH_COUPLING: a hub exceeding the fan-out threshold ---
    hub_edges = [["hub", t] for t in ["a", "b", "c", "d", "e", "f"]]
    hub = parse_card({"components": ["hub", "a", "b", "c", "d", "e", "f"], "edges": hub_edges})
    res = analyze(hub, max_fanout=5)
    hc = [f for f in res["findings"] if f["kind"] == "HIGH_COUPLING"]
    if not hc or "hub" not in hc[0]["detail"]:
        errs.append("a hub (fan-out 6 > 5) should flag HIGH_COUPLING, got %r" % res["findings"])
    if res["status"] != "PASS":
        errs.append("HIGH_COUPLING is advisory — must NOT FAIL the gate, got %s" % res["status"])

    # MUST-NOT-FLAG: under-threshold fan-out is clean
    small = parse_card({"components": ["h", "a", "b"], "edges": [["h", "a"], ["h", "b"]]})
    if [f for f in analyze(small, max_fanout=5)["findings"] if f["kind"] == "HIGH_COUPLING"]:
        errs.append("fan-out 2 (<5) must NOT flag HIGH_COUPLING")

    # --- MUST-FLAG ORPHAN: a node with no edges in or out ---
    orphaned = parse_card({"components": ["a", "b", "lonely"], "edges": [["a", "b"]]})
    res = analyze(orphaned)
    orf = [f for f in res["findings"] if f["kind"] == "ORPHAN"]
    if not orf or "lonely" not in orf[0]["detail"]:
        errs.append("a node with no edges should flag ORPHAN, got %r" % res["findings"])
    if res["status"] != "PASS":
        errs.append("ORPHAN is advisory — must NOT FAIL the gate, got %s" % res["status"])

    # MUST-NOT-FLAG: a connected node is not an orphan
    if [f for f in analyze(parse_card({"components": ["a", "b"], "edges": [["a", "b"]]}))["findings"]
            if f["kind"] == "ORPHAN"]:
        errs.append("a connected node must NOT flag ORPHAN")

    # --- --json report selftest (the shared schema) -------------------------------------------
    import io
    import contextlib

    def _capture_report(report_obj):
        """Round-trip a report dict through _report_json's stdout path and json.loads it back, asserting
        nothing but the JSON object lands on stdout."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _report_json(report_obj["tool"], report_obj["ok"], report_obj["summary"],
                         report_obj["findings"])
        return json.loads(buf.getvalue())

    def _assert_report(rep, want_ok, want_nonempty, label):
        if not isinstance(rep, dict):
            errs.append("--json %s: report is not a dict" % label); return
        if rep.get("tool") != "dependency-check":
            errs.append("--json %s: tool=%r, want 'dependency-check'" % (label, rep.get("tool")))
        if rep.get("ok") is not want_ok:
            errs.append("--json %s: ok=%r, want %r" % (label, rep.get("ok"), want_ok))
        if not isinstance(rep.get("summary"), str) or not rep["summary"]:
            errs.append("--json %s: summary missing/empty" % label)
        f = rep.get("findings")
        if not isinstance(f, list):
            errs.append("--json %s: findings not a list" % label); return
        if want_nonempty and not f:
            errs.append("--json %s: findings should be non-empty" % label)
        if not want_nonempty and f:
            errs.append("--json %s: findings should be [] on clean input, got %s" % (label, f))
        for fd in f:
            if not isinstance(fd, dict) or any(k not in fd for k in ("kind", "severity", "location", "message")):
                errs.append("--json %s: a finding is missing a required key: %r" % (label, fd))
            elif fd["severity"] not in ("fail", "warn", "advisory"):
                errs.append("--json %s: bad severity %r" % (label, fd["severity"]))

    # dirty fixture (a 2-cycle ⇒ CYCLE gate): parses, tool right, ok false, findings non-empty
    dirty_rep = _capture_report(build_report(analyze(two_cycle)))
    _assert_report(dirty_rep, False, True, "dirty")
    if not any(fd["kind"] == "CYCLE" and fd["severity"] == "fail" for fd in dirty_rep["findings"]):
        errs.append("--json dirty: CYCLE should map to severity 'fail'")
    # advisory-only (a hub) keeps ok TRUE — HIGH_COUPLING does not block
    adv_rep = _capture_report(build_report(analyze(hub, max_fanout=5)))
    _assert_report(adv_rep, True, True, "advisory-only")
    if not any(fd["kind"] == "HIGH_COUPLING" and fd["severity"] == "advisory" for fd in adv_rep["findings"]):
        errs.append("--json advisory-only: HIGH_COUPLING should map to severity 'advisory'")
    # clean fixture ⇒ ok true, findings []
    _assert_report(_capture_report(build_report(analyze(clean))), True, False, "clean")

    return errs


def _print_report(card, res):
    print("INTEGRITY report — %d component(s), %d edge(s)"
          % (len(card["components"]), len(card["edges"])))
    if not res["findings"]:
        print("  (clean) acyclic + layered + bounded — no mechanical defects found")
    for f in res["findings"]:
        print("  %-16s %-7s %s" % (f["kind"], "GATE" if f["gate"] else "advise", f["detail"]))
    print("  status: %s" % res["status"])


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("dependency-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("dependency-check: OK — cycle + layering + coupling + orphan checks verified "
              "(must-flag and must-not-flag fixtures)")
        return 0
    # --json is a parse-anywhere reporting flag — strip it out, remember it, leave everything else.
    as_json = "--json" in argv
    if as_json:
        argv = [a for a in argv if a != "--json"]
        if not argv:
            sys.stderr.write("usage: dependency-check.py [--json] <card.json>\n")
            return 2
    if argv[0] == "template":
        print(json.dumps(TEMPLATE, indent=2))
        return 0

    path = argv[0]
    max_fanin, max_fanout = DEFAULT_MAX_FANIN, DEFAULT_MAX_FANOUT
    if "--max-fanin" in argv:
        max_fanin = int(argv[argv.index("--max-fanin") + 1])
    if "--max-fanout" in argv:
        max_fanout = int(argv[argv.index("--max-fanout") + 1])
    try:
        doc = json.load(open(path, encoding="utf-8"))
        card = parse_card(doc)
    except (OSError, json.JSONDecodeError, ValueError) as e:
        sys.stderr.write("dependency-check: bad card — %s\n" % e)
        return 2
    res = analyze(card, max_fanin, max_fanout)
    if as_json:
        rep = build_report(res)
        _report_json(rep["tool"], rep["ok"], rep["summary"], rep["findings"])
        return 0 if rep["ok"] else 1
    _print_report(card, res)
    if res["status"] == "FAIL":
        sys.stderr.write("dependency-check: FAIL — %d gate flag(s): %s\n"
                         % (len(res["gate_fails"]),
                            ", ".join(sorted({f["kind"] for f in res["gate_fails"]}))))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
