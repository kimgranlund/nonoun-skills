#!/usr/bin/env python3
"""query-harness.py — the query-decomposer EXECUTION gate. Self-contained (stdlib only).

The EXECUTION axis (B1 parse · B2 bind · B3 plan/run) is mechanizable, but the engine is
project-specific — so this is a thin ADAPTER, not a bundled database. It reads a tiny manifest of
per-phase commands (each driving the real engine: psql / sqlite3 / bq / snowsql via EXPLAIN), runs
each one whose tool is actually on PATH, and normalizes the verdicts into a report card. Like the
code-decomposer execution-harness, the static logic (manifest parse + verdict normalize) is proved by
`selftest` with zero external deps; the live run fires only where the real engine exists (a missing
tool is a SKIP, not a failure).

Manifest (JSON) — each phase optional; `gate` defaults by phase (parse/bind/explain gate; run
advisory because it touches data):
  {
    "dialect": "postgres",
    "gates": {
      "parse":   { "cmd": "psql -d app -c \"PREPARE _q AS SELECT 1\"" },
      "bind":    { "cmd": "psql -d app -v ON_ERROR_STOP=1 -c \"EXPLAIN SELECT 1\"" },
      "explain": { "cmd": "psql -d app -c \"EXPLAIN SELECT 1\"" },
      "run":     { "cmd": "psql -d app -c \"EXPLAIN ANALYZE SELECT 1\"", "gate": false }
    }
  }

  python3 bin/query-harness.py selftest
  python3 bin/query-harness.py template
  python3 bin/query-harness.py <manifest.json> [--cwd DIR]

Python 3.8+.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys

PHASES = ["parse", "bind", "explain", "run"]   # canonical run order: parse -> bind -> plan -> run
GATE_BY_DEFAULT = {"parse": True, "bind": True, "explain": True, "run": False}


def tool_of(cmd):
    """The executable a command invokes (first shell token)."""
    parts = shlex.split(cmd)
    return parts[0] if parts else ""


def available(cmd):
    tool = tool_of(cmd)
    if not tool:
        return False
    if os.path.sep in tool:                      # an explicit path
        return os.path.isfile(tool) and os.access(tool, os.X_OK)
    return shutil.which(tool) is not None


def verdict_of(exit_code):
    return "pass" if exit_code == 0 else "fail"


def parse_manifest(doc):
    """Validate + normalize a manifest into an ordered list of phase specs. Raises ValueError."""
    if not isinstance(doc, dict) or "gates" not in doc or not isinstance(doc["gates"], dict):
        raise ValueError("manifest must be an object with a 'gates' object")
    specs = []
    for name, spec in doc["gates"].items():
        if name not in PHASES:
            raise ValueError("unknown phase %r (expected one of %s)" % (name, ", ".join(PHASES)))
        if not isinstance(spec, dict) or not spec.get("cmd"):
            raise ValueError("phase %r needs a non-empty 'cmd'" % name)
        specs.append({
            "phase": name,
            "cmd": spec["cmd"],
            "gate": bool(spec.get("gate", GATE_BY_DEFAULT[name])),
        })
    specs.sort(key=lambda s: PHASES.index(s["phase"]))
    return specs


def run_phase(spec, cwd=None):
    """Run one phase if its tool is present; return a normalized result dict."""
    res = {"phase": spec["phase"], "cmd": spec["cmd"], "gate": spec["gate"],
           "ran": False, "exit": None, "verdict": "skip", "note": ""}
    if not available(spec["cmd"]):
        res["note"] = "%s not on PATH" % tool_of(spec["cmd"])
        return res
    try:
        proc = subprocess.run(shlex.split(spec["cmd"]), cwd=cwd, capture_output=True, text=True)
    except OSError as e:
        res["note"] = "could not run (%s)" % e
        return res
    res["ran"] = True
    res["exit"] = proc.returncode
    res["verdict"] = verdict_of(proc.returncode)
    tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-1:] if proc.returncode else []
    res["note"] = tail[0][:160] if tail else ""
    return res


def overall(results):
    """Report-card summary over the GATE phases only (advisory phases never decide the verdict):
      - any gate FAILED                         -> FAIL
      - no gate failed but some gate was SKIPPED -> INCOMPLETE (no engine ran it; NOT a pass)
      - every gate ran green                     -> PASS
    A fully-skipped run (the common no-engine-on-PATH case) is INCOMPLETE, not PASS — a skipped gate
    is missing evidence, and a missing tool is a SKIP, never a pass."""
    gate_results = [r for r in results if r["gate"]]
    gate_fails = [r for r in gate_results if r["verdict"] == "fail"]
    gate_skips = [r for r in gate_results if r["verdict"] == "skip"]
    gate_passes = [r for r in gate_results if r["verdict"] == "pass"]
    if gate_fails:
        status = "FAIL"
    elif gate_skips or not gate_passes:
        # some gate was skipped, OR no gate ran green at all (an empty / advisory-only manifest):
        # either way there is no positive gate evidence — this is NOT a pass.
        status = "INCOMPLETE"
    else:
        status = "PASS"
    return {"status": status, "gate_fails": gate_fails, "gate_skips": gate_skips}


TEMPLATE = {
    "dialect": "postgres",
    "gates": {
        "parse":   {"cmd": "psql -d app -c \"PREPARE _q AS SELECT 1\""},
        # bind without executing: EXPLAIN binds every identifier against the schema but never runs
        # the query (a real idiom — psql has no --dry-run flag).
        "bind":    {"cmd": "psql -d app -v ON_ERROR_STOP=1 -c \"EXPLAIN SELECT 1\""},
        "explain": {"cmd": "psql -d app -c \"EXPLAIN SELECT 1\""},
        "run":     {"cmd": "psql -d app -c \"EXPLAIN ANALYZE SELECT 1\"", "gate": False},
    },
}


def selftest():
    errs = []
    # 1. tool_of + verdict_of
    if tool_of("psql -d app -c \"EXPLAIN SELECT 1\"") != "psql":
        errs.append("tool_of failed")
    if verdict_of(0) != "pass" or verdict_of(2) != "fail":
        errs.append("verdict_of failed")
    # 2. parse_manifest accepts a good manifest in canonical order (out-of-order input)
    specs = parse_manifest({"gates": {"explain": {"cmd": "psql"}, "parse": {"cmd": "psql"}}})
    if [s["phase"] for s in specs] != ["parse", "explain"]:
        errs.append("parse_manifest order wrong: %s" % [s["phase"] for s in specs])
    if specs[0]["gate"] is not True:
        errs.append("parse should gate by default")
    # the `run` phase must be advisory by default
    run_spec = parse_manifest({"gates": {"run": {"cmd": "psql"}}})[0]
    if run_spec["gate"] is not False:
        errs.append("run should be advisory by default")
    # 3. parse_manifest rejects malformed
    for bad in ({"gates": {"frobnicate": {"cmd": "x"}}}, {"gates": {"parse": {}}}, {"nope": 1}):
        try:
            parse_manifest(bad)
            errs.append("parse_manifest accepted malformed: %s" % bad)
        except ValueError:
            pass
    # 4. run_phase exercises the real subprocess path with no external deps (sys.executable always exists)
    ok = run_phase({"phase": "parse", "cmd": "%s -c \"import sys; sys.exit(0)\"" % shlex.quote(sys.executable), "gate": True})
    if not ok["ran"] or ok["verdict"] != "pass":
        errs.append("run_phase pass path failed: %s" % ok)
    bad = run_phase({"phase": "bind", "cmd": "%s -c \"import sys; sys.exit(5)\"" % shlex.quote(sys.executable), "gate": True})
    if not bad["ran"] or bad["verdict"] != "fail" or bad["exit"] != 5:
        errs.append("run_phase fail path failed: %s" % bad)
    skip = run_phase({"phase": "explain", "cmd": "definitely_not_a_real_engine_xyz -c EXPLAIN", "gate": True})
    if skip["ran"] or skip["verdict"] != "skip":
        errs.append("run_phase skip path failed: %s" % skip)
    # 5. overall verdict logic — three statuses (PASS / FAIL / INCOMPLETE)
    if overall([ok, bad])["status"] != "FAIL":
        errs.append("overall should FAIL on a gate fail")
    if overall([ok])["status"] != "PASS":
        errs.append("overall should PASS when all gates pass")
    # an all-skip GATE run is INCOMPLETE (was wrongly PASS) — a missing engine is NOT a pass
    if overall([skip])["status"] != "INCOMPLETE" or not overall([skip])["gate_skips"]:
        errs.append("overall should be INCOMPLETE on an all-skip gate run: %s" % overall([skip]))
    # a gate fail beats an INCOMPLETE skip (FAIL dominates)
    if overall([bad, skip])["status"] != "FAIL":
        errs.append("overall should FAIL when a gate fails even if another gate skipped")
    # a green gate alongside a skipped ADVISORY (non-gate) phase stays PASS — advisory never decides
    adv_skip = {**skip, "gate": False}
    if overall([ok, adv_skip])["status"] != "PASS":
        errs.append("overall should PASS when only an advisory phase skipped: %s" % overall([ok, adv_skip]))
    # an empty manifest (no gate ran at all) is INCOMPLETE, not PASS
    if overall([])["status"] != "INCOMPLETE":
        errs.append("overall on an empty manifest should be INCOMPLETE, got %s" % overall([])["status"])
    # an advisory-only manifest (a passing advisory phase, no gate) is also INCOMPLETE — no gate evidence
    if overall([{**ok, "gate": False}])["status"] != "INCOMPLETE":
        errs.append("overall on an advisory-only manifest should be INCOMPLETE")
    return errs


def _print_card(results, cwd, dialect):
    print("PLAN report card%s%s" % (
        " (dialect=%s)" % dialect if dialect else "",
        " (cwd=%s)" % cwd if cwd else ""))
    print("  %-10s %-7s %-5s %-7s %s" % ("phase", "gate", "ran", "verdict", "note"))
    for r in results:
        print("  %-10s %-7s %-5s %-7s %s" % (
            r["phase"], "gate" if r["gate"] else "advise",
            "yes" if r["ran"] else "no", r["verdict"], r["note"]))


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("query-harness: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("query-harness: OK — manifest parse + verdict normalize + run/skip paths + "
              "PASS/FAIL/INCOMPLETE verdict logic verified")
        return 0
    if argv[0] == "template":
        print(json.dumps(TEMPLATE, indent=2))
        return 0
    manifest, cwd = argv[0], None
    if "--cwd" in argv:
        cwd = argv[argv.index("--cwd") + 1]
    try:
        doc = json.load(open(manifest, encoding="utf-8"))
        specs = parse_manifest(doc)
    except (OSError, json.JSONDecodeError, ValueError) as e:
        sys.stderr.write("query-harness: bad manifest — %s\n" % e)
        return 2
    results = [run_phase(s, cwd) for s in specs]
    _print_card(results, cwd, doc.get("dialect"))
    summary = overall(results)
    if summary["gate_skips"]:
        print("  ⚠ %d gate(s) skipped (engine absent) — evidence incomplete: %s"
              % (len(summary["gate_skips"]), ", ".join(r["phase"] for r in summary["gate_skips"])))
    if summary["status"] == "FAIL":
        sys.stderr.write("query-harness: FAIL — %d gate(s) failed: %s\n"
                         % (len(summary["gate_fails"]), ", ".join(r["phase"] for r in summary["gate_fails"])))
        return 1
    if summary["status"] == "INCOMPLETE":
        # no gate ran green (the common no-engine-on-PATH case, or an empty/advisory-only manifest).
        # A skipped gate reported as a pass would be NOT-done — so this exits NON-ZERO, never PASS.
        n = len(summary["gate_skips"])
        why = ("%d gate(s) had no engine" % n) if n else "no gate ran (empty/advisory-only manifest)"
        sys.stderr.write("query-harness: INCOMPLETE — %s; this is NOT a pass "
                         "(provide the engine on PATH and re-run; a skipped gate is missing evidence)\n"
                         % why)
        return 3
    print("query-harness: PASS — all present gates green (grain check is separate — see grain-and-joins.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
