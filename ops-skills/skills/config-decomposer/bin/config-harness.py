#!/usr/bin/env python3
"""config-harness.py — the config-decomposer VALIDITY gate. Self-contained (stdlib only).

The VALIDITY axis (B1 parse · B2 schema · B3 plan) is mechanizable, but the validator is
tool-specific — `terraform validate`/`plan`, `kubeconform`, `hadolint`, `yamllint`, an app's own
`--check`. So this is a thin ADAPTER, not a bundled validator. It reads a tiny manifest of per-phase
commands, runs each one whose tool is actually on PATH, and normalizes the verdicts into a report
card. Like code-decomposer's execution-harness, the static logic (manifest parse + verdict normalize)
is proved by `selftest` with zero external deps; the live run fires only where the real tools exist —
**a missing tool is a SKIP, not a pass** (you have no evidence for that gate, not a green light).

The doctrine this enforces: the PLAN is the contract. A green `parse` proves syntax, nothing more;
the `plan` phase is where "valid config, wrong outcome / surprise destroy" is caught. A skipped plan
gate is reported as *no evidence*, never folded into a pass.

The `plan` verdict is TRI-STATE, because the doctrine's success case is non-zero by design — the
template recommends `terraform plan -detailed-exitcode` (exit 2 = changes present) and `kubectl diff`
(exit 1 = a diff): those are `changes-present` (pass-with-a-diff-to-READ), NOT a gate fail. `fail` is
reserved for a true error (terraform plan exit 1 or >2; kubectl diff exit >1).

Exit codes: 0 = PASS (all present gates green) · 1 = FAIL (a gate errored) · 2 = bad invocation/manifest
· 3 = INCOMPLETE (a decisive GATE was SKIPPED with no fails — NO EVIDENCE, so automation can't read it
as success).

Manifest (JSON) — each phase optional; `gate` defaults by phase (parse/schema/plan gate; lint/
policy advisory):
  {
    "tool": "terraform",
    "gates": {
      "parse":  { "cmd": "terraform fmt -check" },
      "schema": { "cmd": "terraform validate" },
      "plan":   { "cmd": "terraform plan -detailed-exitcode" },
      "lint":   { "cmd": "tflint", "gate": false },
      "policy": { "cmd": "checkov -d .", "gate": false }
    }
  }

  python3 bin/config-harness.py selftest
  python3 bin/config-harness.py template
  python3 bin/config-harness.py <manifest.json> [--cwd DIR]

Python 3.8+.
"""
import json
import os
import shlex
import shutil
import subprocess
import sys

PHASES = ["parse", "schema", "plan", "lint", "policy"]   # canonical run order
GATE_BY_DEFAULT = {"parse": True, "schema": True, "plan": True, "lint": False, "policy": False}


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


def verdict_of(exit_code, phase=None, cmd=""):
    """Normalize an exit code to a verdict — tri-state for the plan/diff phase.

    A `plan` phase is the doctrine's success case when it reports *changes present*, and the harness's
    own template recommends the very flag that signals that with a non-zero code:
      - `terraform plan -detailed-exitcode`: exit 0 = no changes, 2 = changes present (SUCCESS — a diff
        to READ), >2 = a real error.
      - `kubectl diff`: exit 0 = no diff, 1 = a diff present (SUCCESS — to READ), >1 = a real error.
    So for those, the "changes" code is `changes-present` (pass-with-diff, the intended outcome), NOT a
    gate fail. `fail` is reserved for a true error. Every other phase keeps the plain 0=pass / else=fail.
    """
    if exit_code == 0:
        return "pass"
    low = cmd.lower()
    is_kubectl_diff = "kubectl" in low and "diff" in low
    if phase == "plan":
        if is_kubectl_diff:
            return "changes-present" if exit_code == 1 else "fail"   # kubectl diff: 1 = diff, >1 = error
        # terraform/tofu plan -detailed-exitcode (the template default): 2 = changes, >2 = error, 1 = error
        return "changes-present" if exit_code == 2 else "fail"
    # a kubectl diff wired under any phase still means "diff present", not an error, at exit 1
    if is_kubectl_diff and exit_code == 1:
        return "changes-present"
    return "fail"


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
    res["verdict"] = verdict_of(proc.returncode, spec["phase"], spec["cmd"])
    if res["verdict"] == "changes-present":
        res["note"] = "exit %d — changes present, READ the diff (not a fail)" % proc.returncode
    else:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-1:] if proc.returncode else []
        res["note"] = tail[0][:160] if tail else ""
    return res


def overall(results):
    """Report-card summary.

    Status precedence (M2 — a skipped GATE is NO EVIDENCE, never a silent pass):
      - FAIL       any gate phase truly failed (a real error);
      - INCOMPLETE no gate failed, but a gate phase was SKIPPED (tool absent) — the decisive evidence
                   is missing, so automation must NOT read this as green (exit non-zero);
      - PASS       every gate ran and passed (a plan that reports `changes-present` is a pass — a diff
                   to read, the doctrine's success case, not a fail).
    """
    gate_fails = [r for r in results if r["gate"] and r["verdict"] == "fail"]
    gate_skips = [r for r in results if r["gate"] and r["verdict"] == "skip"]
    gate_changes = [r for r in results if r["gate"] and r["verdict"] == "changes-present"]
    if gate_fails:
        status = "FAIL"
    elif gate_skips:
        status = "INCOMPLETE"
    else:
        status = "PASS"
    return {"status": status, "gate_fails": gate_fails, "gate_skips": gate_skips,
            "gate_changes": gate_changes}


TEMPLATE = {
    "tool": "terraform",
    "gates": {
        "parse":  {"cmd": "terraform fmt -check"},
        "schema": {"cmd": "terraform validate"},
        "plan":   {"cmd": "terraform plan -detailed-exitcode"},
        "lint":   {"cmd": "tflint", "gate": False},
        "policy": {"cmd": "checkov -d .", "gate": False},
    },
}


def selftest():
    errs = []
    # 1. tool_of + verdict_of (M1: the plan/diff verdict is tri-state)
    if tool_of("terraform plan -detailed-exitcode") != "terraform":
        errs.append("tool_of failed")
    if verdict_of(0) != "pass":
        errs.append("verdict_of(0) should be pass")
    # a non-plan phase keeps plain 0=pass / else=fail
    if verdict_of(2, "schema", "terraform validate") != "fail":
        errs.append("verdict_of: non-plan exit 2 should be fail")
    # terraform plan -detailed-exitcode: 2 = changes present (SUCCESS, a diff to read), not a fail
    if verdict_of(2, "plan", "terraform plan -detailed-exitcode") != "changes-present":
        errs.append("verdict_of: terraform plan exit 2 should be changes-present, not fail")
    if verdict_of(1, "plan", "terraform plan -detailed-exitcode") != "fail":
        errs.append("verdict_of: terraform plan exit 1 should be fail (real error)")
    if verdict_of(3, "plan", "terraform plan -detailed-exitcode") != "fail":
        errs.append("verdict_of: terraform plan exit >2 should be fail")
    # kubectl diff: exit 1 = a diff present (SUCCESS to read), >1 = error
    if verdict_of(1, "plan", "kubectl diff -f .") != "changes-present":
        errs.append("verdict_of: kubectl diff exit 1 should be changes-present")
    if verdict_of(2, "plan", "kubectl diff -f .") != "fail":
        errs.append("verdict_of: kubectl diff exit >1 should be fail")
    # 2. parse_manifest accepts a good manifest in canonical order
    specs = parse_manifest({"gates": {"plan": {"cmd": "terraform plan"}, "parse": {"cmd": "yamllint ."}}})
    if [s["phase"] for s in specs] != ["parse", "plan"]:
        errs.append("parse_manifest order wrong: %s" % [s["phase"] for s in specs])
    if specs[0]["gate"] is not True:
        errs.append("parse should gate by default")
    # 3. parse_manifest rejects malformed
    for bad in ({"gates": {"frobnicate": {"cmd": "x"}}}, {"gates": {"plan": {}}}, {"nope": 1}):
        try:
            parse_manifest(bad)
            errs.append("parse_manifest accepted malformed: %s" % bad)
        except ValueError:
            pass
    # 4. run_phase exercises the real subprocess path with no external deps (sys.executable always exists)
    ok = run_phase({"phase": "plan", "cmd": "%s -c \"import sys; sys.exit(0)\"" % shlex.quote(sys.executable), "gate": True})
    if not ok["ran"] or ok["verdict"] != "pass":
        errs.append("run_phase pass path failed: %s" % ok)
    bad = run_phase({"phase": "plan", "cmd": "%s -c \"import sys; sys.exit(5)\"" % shlex.quote(sys.executable), "gate": True})
    if not bad["ran"] or bad["verdict"] != "fail" or bad["exit"] != 5:
        errs.append("run_phase fail path failed: %s" % bad)
    skip = run_phase({"phase": "lint", "cmd": "definitely_not_a_real_tool_xyz check", "gate": False})
    if skip["ran"] or skip["verdict"] != "skip":
        errs.append("run_phase skip path failed: %s" % skip)
    # M1: a `plan` phase exiting 2 (the -detailed-exitcode "changes present" code) is changes-present, not a fail
    changes = run_phase({"phase": "plan", "cmd": "%s -c \"import sys; sys.exit(2)\"" % shlex.quote(sys.executable), "gate": True})
    if not changes["ran"] or changes["verdict"] != "changes-present":
        errs.append("run_phase plan exit-2 should be changes-present: %s" % changes)
    # 5. overall verdict logic
    if overall([ok, bad])["status"] != "FAIL":
        errs.append("overall should FAIL on a gate fail")
    if overall([ok])["status"] != "PASS":
        errs.append("overall should PASS when all gates pass")
    # a plan reporting changes-present is the doctrine's success case — a PASS (a diff to read), not a fail
    if overall([changes])["status"] != "PASS" or not overall([changes])["gate_changes"]:
        errs.append("overall should PASS on a changes-present gate and flag it: %s" % overall([changes]))
    # M2: a SKIPPED gate with no fails is INCOMPLETE (exit non-zero), never a silent PASS
    skip_gate = {**skip, "gate": True}
    if overall([skip_gate])["status"] != "INCOMPLETE" or not overall([skip_gate])["gate_skips"]:
        errs.append("overall: a skipped GATE should be INCOMPLETE, not PASS: %s" % overall([skip_gate]))
    # an advisory (non-gate) skip is fine — still PASS
    if overall([skip])["status"] != "PASS":
        errs.append("overall: an advisory skip should not block PASS: %s" % overall([skip]))
    # M2 (main path): --cwd with no value must not crash with IndexError; it returns a clean error code
    if main(["some-manifest.json", "--cwd"]) != 2:
        errs.append("main --cwd with no value should return 2, not raise IndexError")
    return errs


def _print_card(results, cwd):
    print("VALIDITY report card%s" % (" (cwd=%s)" % cwd if cwd else ""))
    print("  %-8s %-7s %-5s %-7s %s" % ("phase", "gate", "ran", "verdict", "note"))
    for r in results:
        print("  %-8s %-7s %-5s %-7s %s" % (
            r["phase"], "gate" if r["gate"] else "advise",
            "yes" if r["ran"] else "no", r["verdict"], r["note"]))


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("config-harness: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("config-harness: OK — manifest parse + tri-state plan verdict + run/skip/changes paths + "
              "INCOMPLETE-on-skipped-gate verified")
        return 0
    if argv[0] == "template":
        print(json.dumps(TEMPLATE, indent=2))
        return 0
    manifest, cwd = argv[0], None
    if "--cwd" in argv:
        i = argv.index("--cwd")
        if i + 1 >= len(argv):
            sys.stderr.write("config-harness: --cwd needs a directory argument\n")
            return 2
        cwd = argv[i + 1]
    try:
        doc = json.load(open(manifest, encoding="utf-8"))
        specs = parse_manifest(doc)
    except (OSError, json.JSONDecodeError, ValueError) as e:
        sys.stderr.write("config-harness: bad manifest — %s\n" % e)
        return 2
    results = [run_phase(s, cwd) for s in specs]
    _print_card(results, cwd)
    summary = overall(results)
    if summary["gate_changes"]:
        print("  → %d plan gate(s) report CHANGES PRESENT — READ the diff against the desired state: %s"
              % (len(summary["gate_changes"]), ", ".join(r["phase"] for r in summary["gate_changes"])))
    if summary["gate_skips"]:
        print("  ⚠ %d gate(s) skipped (tool absent) — NO EVIDENCE, not a pass: %s"
              % (len(summary["gate_skips"]), ", ".join(r["phase"] for r in summary["gate_skips"])))
    if summary["status"] == "FAIL":
        sys.stderr.write("config-harness: FAIL — %d gate(s) failed: %s\n"
                         % (len(summary["gate_fails"]), ", ".join(r["phase"] for r in summary["gate_fails"])))
        return 1
    if summary["status"] == "INCOMPLETE":
        sys.stderr.write("config-harness: INCOMPLETE — %d decisive gate(s) SKIPPED (tool absent), no fails: %s. "
                         "This is NO EVIDENCE, not a pass.\n"
                         % (len(summary["gate_skips"]), ", ".join(r["phase"] for r in summary["gate_skips"])))
        return 3
    print("config-harness: PASS — all present gates green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
