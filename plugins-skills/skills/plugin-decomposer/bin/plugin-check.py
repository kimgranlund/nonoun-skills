#!/usr/bin/env python3
"""plugin-check.py — the plugin-decomposer MANIFEST gate. Self-contained (stdlib only).

The MANIFEST axis ("does it actually install & load?") is exactly where an LLM author hallucinates
with confidence — a plausible-looking plugin.json with a `Title Case` name, a `1.0` version, or a
`../shared/hooks` path reads fine but fails at install. So that axis routes to code, not inference:
this reads a plugin.json (and OPTIONALLY its marketplace.json `plugins[]` entry) and flags the
load-blocking defects deterministically.

Findings (GATE blocks the BUNDLE reviews below it; ADVISORY is a review signal, never a block):
  MANIFEST_INVALID  [gate]  not an object, or a required field (name / version) missing/empty/wrong-type
  BAD_NAME          [gate]  name not kebab-ish (lowercase letters/digits/hyphens, no leading/trailing/double -)
  BAD_VERSION       [gate]  version not semver-ish (MAJOR.MINOR.PATCH[-pre][+build])
  ILLEGAL_PATH      [gate]  a declared component/source path that is absolute or escapes the plugin dir (`../`)
  MARKETPLACE_MISMATCH [gate] a marketplace entry was supplied but its name != the manifest name (won't resolve)
  KITCHEN_SINK      [advisory] many DISPARATE component kinds bundled — an unfocused, hard-to-justify bundle

This is a LOSSY PRE-FILTER, not an oracle. A clean run proves the manifest is well-FORMED and the
paths are legal; it cannot prove the plugin does ONE job, that its components actually serve that job,
or that a referenced path exists with the right content. KITCHEN_SINK is a smell (count of disparate
component types), not a verdict — a focused multi-component plugin is legitimate. Confirm the BUNDLE
axis (A1–A5) by review, adversarially.

  python3 bin/plugin-check.py selftest
  python3 bin/plugin-check.py template
  python3 bin/plugin-check.py <plugin.json> [--marketplace <marketplace.json>] [--entry NAME]
  python3 bin/plugin-check.py [--json] <plugin.json> [--marketplace ...] [--entry ...]

`--json` (additive reporting flag; parse-anywhere in argv) prints ONE machine-readable report object to
stdout and NOTHING else there — the shared schema every lint bin emits:
  {"tool": "plugin-check", "ok": <bool>, "summary": "<one line>",
   "findings": [{"kind", "severity": fail|advisory, "location": "<plugin label | null>", "message"}, ...]}
`ok` is true iff no GATE finding (the exact condition that gives exit 0 in human mode). A gate finding
(MANIFEST_INVALID / BAD_NAME / BAD_VERSION / ILLEGAL_PATH / MARKETPLACE_MISMATCH) maps to severity
`fail`; the KITCHEN_SINK advisory to `advisory`. The exit code is UNCHANGED by --json. Without --json,
output + exit are byte-identical.

Python 3.8+.
"""
import json
import os
import re
import sys

# A plugin.json's REQUIRED fields for a loadable manifest. `name` + `version` are the hard floor;
# the rest (description, author, homepage, license, keywords) are conventional, not load-blocking.
REQUIRED = ("name", "version")

# Kebab: lowercase alnum tokens joined by single hyphens — no leading/trailing/double hyphen, no _,
# no uppercase, no spaces. (`Foo Bar`, `Foo_Bar`, `-x`, `x-`, `x--y` all fail.)
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Semver-ish: MAJOR.MINOR.PATCH with optional -prerelease and +build (the subset npm/Claude accept).
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)

# The declared-component fields a plugin.json / marketplace entry may carry that hold a PATH into the
# bundle. Each must stay inside the plugin dir (relative, no `..`) and never be absolute.
PATH_FIELDS = ("commands", "agents", "hooks", "mcpServers", "skills", "source")

# Component KINDS that count toward the kitchen-sink smell. A plugin that declares many DISTINCT kinds
# is doing many jobs; the threshold is a smell, not a hard fail.
COMPONENT_KINDS = ("commands", "agents", "hooks", "mcpServers", "skills")
KITCHEN_SINK_THRESHOLD = 4   # 4+ distinct declared component kinds = advisory smell


def _is_illegal_path(p):
    """A path is illegal in a portable bundle if it is absolute or escapes the plugin dir (`..`)."""
    if not isinstance(p, str) or not p:
        return False
    if os.path.isabs(p) or p.startswith("~") or re.match(r"^[A-Za-z]:[\\/]", p):  # /x, ~/x, C:\x
        return True
    # Normalise with forward slashes and look for any `..` segment (escape) — covers `../x`, `a/../../b`.
    norm = p.replace("\\", "/")
    return any(seg == ".." for seg in norm.split("/"))


def _collect_paths(obj):
    """Yield every string path declared under a PATH_FIELDS key (string, list, or dict-of-strings)."""
    for field in PATH_FIELDS:
        val = obj.get(field)
        if isinstance(val, str):
            yield field, val
        elif isinstance(val, list):
            for v in val:
                if isinstance(v, str):
                    yield field, v
        elif isinstance(val, dict):
            for v in val.values():
                if isinstance(v, str):
                    yield field, v


def _declared_kinds(obj):
    """The set of component kinds the manifest actually declares (truthy value present)."""
    kinds = set()
    for kind in COMPONENT_KINDS:
        v = obj.get(kind)
        if v:                      # non-empty list / dict / string
            kinds.add(kind)
    return kinds


def check(manifest, market_entry=None):
    """Return a list of (severity, code, detail) findings. severity ∈ {'gate','advisory'}.

    `manifest` is the parsed plugin.json. `market_entry` (optional) is the parsed marketplace.json
    `plugins[]` entry for B3 (does the marketplace reference resolve to this plugin?)."""
    finds = []
    if not isinstance(manifest, dict):
        return [("gate", "MANIFEST_INVALID", "plugin.json must be a JSON object")]

    # B1 · required fields well-formed
    for field in REQUIRED:
        if field not in manifest:
            finds.append(("gate", "MANIFEST_INVALID", "missing required field %r" % field))
        elif not isinstance(manifest[field], str) or not manifest[field].strip():
            finds.append(("gate", "MANIFEST_INVALID", "field %r must be a non-empty string" % field))

    # B2 · name / version valid (only meaningful if the field is a present string)
    name = manifest.get("name")
    if isinstance(name, str) and name.strip() and not KEBAB_RE.match(name):
        finds.append(("gate", "BAD_NAME",
                      "name %r is not kebab-case (lowercase letters/digits/hyphens, no spaces/_/caps)" % name))
    version = manifest.get("version")
    if isinstance(version, str) and version.strip() and not SEMVER_RE.match(version):
        finds.append(("gate", "BAD_VERSION", "version %r is not semver (MAJOR.MINOR.PATCH)" % version))

    # B4 · declared paths legal (no absolute, no `..` escape) — in the manifest AND the market entry
    for src, (field, p) in (
        [("manifest", fp) for fp in _collect_paths(manifest)]
        + ([("marketplace", fp) for fp in _collect_paths(market_entry)] if isinstance(market_entry, dict) else [])
    ):
        if _is_illegal_path(p):
            finds.append(("gate", "ILLEGAL_PATH",
                          "%s.%s path %r is absolute or escapes the plugin dir" % (src, field, p)))

    # B3 · marketplace reference resolves (name must match) — only if an entry was supplied
    if isinstance(market_entry, dict):
        ename = market_entry.get("name")
        if ename != name:
            finds.append(("gate", "MARKETPLACE_MISMATCH",
                          "marketplace entry name %r != plugin name %r — will not resolve" % (ename, name)))

    # A3/A4 · kitchen-sink smell (advisory): many disparate component kinds = an unfocused bundle
    kinds = _declared_kinds(manifest)
    if len(kinds) >= KITCHEN_SINK_THRESHOLD:
        finds.append(("advisory", "KITCHEN_SINK",
                      "declares %d distinct component kinds (%s) — confirm it does ONE job"
                      % (len(kinds), ", ".join(sorted(kinds)))))
    return finds


# --- machine-readable report (--json) ----------------------------------------------------------
# ONE shared schema across every lint bin: {tool, ok, summary, findings:[{kind, severity, location,
# message}]}. `ok` is true iff no GATE finding (the same condition that gives exit 0 in human mode).
# Printed via json.dumps(indent=2); nothing else goes to stdout under --json.
def _report_json(tool, ok, summary, findings):
    """Emit the shared report object to stdout (and nothing else). `findings` is a list of dicts already
    in {kind, severity, location, message} shape. Returns the dict so callers/selftests can reuse it."""
    report = {"tool": tool, "ok": ok, "summary": summary, "findings": findings}
    print(json.dumps(report, indent=2))
    return report


def build_report(finds, label=None):
    """Build the JSON report from check()'s (severity, code, detail) findings. A gate finding → severity
    `fail`; the KITCHEN_SINK advisory → `advisory`. `ok` is true iff no gate finding — the exact exit-0
    condition of `_run`. `location` is the plugin name when known (manifest findings are plugin-scoped),
    else null."""
    out, gates = [], 0
    for sev, code, detail in finds:
        if sev == "gate":
            gates += 1
        out.append({"kind": code, "severity": "fail" if sev == "gate" else "advisory",
                    "location": label, "message": detail})
    ok = gates == 0
    if not out:
        summary = "manifest well-formed, paths legal — no load-blocking defects"
    else:
        summary = ("%d finding(s) (%d gate, %d advisory) — confirm the BUNDLE axis by review"
                   % (len(out), gates, len(out) - gates))
    return {"tool": "plugin-check", "ok": ok, "summary": summary, "findings": out}


TEMPLATE = {
    "name": "my-plugin",
    "version": "0.1.0",
    "description": "One job, stated in one sentence.",
    "author": {"name": "you", "email": "you@example.com"},
    "homepage": "https://github.com/you/my-plugin",
    "license": "MIT",
    "keywords": ["example"],
}


# --- selftest fixtures (must-FLAG and must-NOT-flag) -------------------------------------------
CLEAN = {"name": "my-plugin", "version": "0.1.0", "description": "does one thing"}
CLEAN_FOCUSED_MULTI = {  # legitimate: a few related component kinds, under threshold
    "name": "good-bundle", "version": "1.2.3",
    "commands": ["./commands/a.md"], "agents": ["./agents/b.md"],
}
MISSING_NAME = {"version": "0.1.0"}
MISSING_VERSION = {"name": "my-plugin"}
EMPTY_NAME = {"name": "  ", "version": "0.1.0"}
BAD_NAME_SPACE = {"name": "Foo Bar", "version": "0.1.0"}
BAD_NAME_UNDERSCORE = {"name": "foo_bar", "version": "0.1.0"}
BAD_NAME_DOUBLE = {"name": "foo--bar", "version": "0.1.0"}
BAD_VERSION = {"name": "ok", "version": "1.0"}
BAD_VERSION_V = {"name": "ok", "version": "v1.0.0"}
ESCAPE_PATH = {"name": "ok", "version": "0.1.0", "hooks": ["../x/hook.json"]}
ABS_PATH = {"name": "ok", "version": "0.1.0", "commands": ["/etc/passwd"]}
NESTED_ESCAPE = {"name": "ok", "version": "0.1.0", "agents": {"a": "agents/../../b.md"}}
KITCHEN = {  # 5 distinct component kinds = smell
    "name": "everything", "version": "0.1.0",
    "commands": ["./c.md"], "agents": ["./a.md"], "hooks": ["./h.json"],
    "mcpServers": {"x": "./m.json"}, "skills": ["./skills/s"],
}


def selftest():
    errs = []

    def codes(finds):
        return {c for _, c, _ in finds}

    def expect_clean(label, manifest, entry=None):
        f = check(manifest, entry)
        gates = [c for sev, c, _ in f if sev == "gate"]
        if gates:
            errs.append("%s: expected NO gate finding, got %s" % (label, gates))

    def expect_code(label, manifest, code, entry=None):
        if code not in codes(check(manifest, entry)):
            errs.append("%s: expected %s, got %s" % (label, code, sorted(codes(check(manifest, entry)))))

    # must-NOT-flag (clean)
    expect_clean("clean-minimal", CLEAN)
    expect_clean("clean-focused-multi", CLEAN_FOCUSED_MULTI)
    # a clean manifest WITH a matching marketplace entry: still no gate
    expect_clean("clean+matching-market", CLEAN, {"name": "my-plugin", "source": "./my-plugin"})
    # CLEAN must not trip the advisory smell either
    if "KITCHEN_SINK" in codes(check(CLEAN)):
        errs.append("clean-minimal: false KITCHEN_SINK")
    if "KITCHEN_SINK" in codes(check(CLEAN_FOCUSED_MULTI)):
        errs.append("clean-focused-multi (2 kinds): false KITCHEN_SINK")

    # must-FLAG (gates)
    expect_code("not-an-object", [], "MANIFEST_INVALID")
    expect_code("missing-name", MISSING_NAME, "MANIFEST_INVALID")
    expect_code("missing-version", MISSING_VERSION, "MANIFEST_INVALID")
    expect_code("empty-name", EMPTY_NAME, "MANIFEST_INVALID")
    expect_code("name-with-space", BAD_NAME_SPACE, "BAD_NAME")
    expect_code("name-underscore", BAD_NAME_UNDERSCORE, "BAD_NAME")
    expect_code("name-double-hyphen", BAD_NAME_DOUBLE, "BAD_NAME")
    expect_code("version-two-part", BAD_VERSION, "BAD_VERSION")
    expect_code("version-v-prefix", BAD_VERSION_V, "BAD_VERSION")
    expect_code("escape-path", ESCAPE_PATH, "ILLEGAL_PATH")
    expect_code("absolute-path", ABS_PATH, "ILLEGAL_PATH")
    expect_code("nested-escape-in-dict", NESTED_ESCAPE, "ILLEGAL_PATH")
    # marketplace mismatch (name doesn't resolve)
    expect_code("market-name-mismatch", CLEAN, "MARKETPLACE_MISMATCH",
                {"name": "other-name", "source": "./my-plugin"})
    # an illegal `source` in the marketplace entry is caught too
    expect_code("market-escape-source", CLEAN, "ILLEGAL_PATH",
                {"name": "my-plugin", "source": "../my-plugin"})

    # must-FLAG (advisory)
    if "KITCHEN_SINK" not in codes(check(KITCHEN)):
        errs.append("kitchen-sink: expected KITCHEN_SINK advisory, got %s" % sorted(codes(check(KITCHEN))))
    # KITCHEN_SINK must be ADVISORY, never a gate (an unfocused bundle still installs)
    for sev, c, _ in check(KITCHEN):
        if c == "KITCHEN_SINK" and sev != "advisory":
            errs.append("KITCHEN_SINK must be advisory, got severity %r" % sev)

    # a valid plugin name with a single hyphen is fine (regression guard against an over-strict regex)
    if "BAD_NAME" in codes(check({"name": "plugin-decomposer", "version": "0.1.0"})):
        errs.append("false BAD_NAME on a valid kebab name")
    # a prerelease/build semver is valid
    if "BAD_VERSION" in codes(check({"name": "ok", "version": "1.0.0-rc.1+build.5"})):
        errs.append("false BAD_VERSION on a valid prerelease semver")

    # --- --json report selftest (the shared schema) -------------------------------------------
    import io
    import contextlib

    def _capture_report(report_obj):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _report_json(report_obj["tool"], report_obj["ok"], report_obj["summary"],
                         report_obj["findings"])
        return json.loads(buf.getvalue())

    def _assert_report(rep, want_ok, want_nonempty, label):
        if not isinstance(rep, dict):
            errs.append("--json %s: report is not a dict" % label); return
        if rep.get("tool") != "plugin-check":
            errs.append("--json %s: tool=%r, want 'plugin-check'" % (label, rep.get("tool")))
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

    # dirty manifest (BAD_NAME_SPACE ⇒ gate BAD_NAME): tool right, ok false, findings non-empty
    dirty_rep = _capture_report(build_report(check(BAD_NAME_SPACE), BAD_NAME_SPACE.get("name")))
    _assert_report(dirty_rep, False, True, "dirty")
    if not any(fd["kind"] == "BAD_NAME" and fd["severity"] == "fail" for fd in dirty_rep["findings"]):
        errs.append("--json dirty: BAD_NAME should map to severity 'fail'")
    # advisory-only manifest (KITCHEN_SINK, no gate) keeps ok TRUE
    adv_rep = _capture_report(build_report(check(KITCHEN), KITCHEN.get("name")))
    _assert_report(adv_rep, True, True, "advisory-only")
    if not any(fd["kind"] == "KITCHEN_SINK" and fd["severity"] == "advisory" for fd in adv_rep["findings"]):
        errs.append("--json advisory-only: KITCHEN_SINK should map to severity 'advisory'")
    # clean manifest ⇒ ok true, findings []
    _assert_report(_capture_report(build_report(check(CLEAN), CLEAN.get("name"))), True, False, "clean")

    return errs


def _run(plugin_path, market_path=None, entry_name=None, as_json=False):
    try:
        manifest = json.load(open(plugin_path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write("plugin-check: cannot read %s — %s\n" % (plugin_path, e))
        return 2
    label = manifest.get("name") if isinstance(manifest, dict) else None
    entry = None
    if market_path:
        try:
            market = json.load(open(market_path, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            sys.stderr.write("plugin-check: cannot read marketplace %s — %s\n" % (market_path, e))
            return 2
        plugins = market.get("plugins", []) if isinstance(market, dict) else []
        want = entry_name or (manifest.get("name") if isinstance(manifest, dict) else None)
        entry = next((p for p in plugins if isinstance(p, dict) and p.get("name") == want), None)
        if entry is None:
            # No matching entry at all — the marketplace doesn't list this plugin (a B3 gate failure).
            msg = "no plugins[] entry named %r in %s" % (want, market_path)
            if as_json:
                rep = build_report([("gate", "MARKETPLACE_MISMATCH", msg)], label)
                _report_json(rep["tool"], rep["ok"], rep["summary"], rep["findings"])
                return 1
            print("plugin-check: MANIFEST report — %s" % plugin_path)
            print("  [gate] MARKETPLACE_MISMATCH  %s" % msg)
            return 1
    finds = check(manifest, entry)
    if as_json:
        rep = build_report(finds, label)
        _report_json(rep["tool"], rep["ok"], rep["summary"], rep["findings"])
        return 1 if [f for f in finds if f[0] == "gate"] else 0
    print("plugin-check: MANIFEST report — %s%s" % (plugin_path, " + marketplace" if entry else ""))
    gate_fails = [f for f in finds if f[0] == "gate"]
    for sev, code, detail in finds:
        print("  [%s] %-20s %s" % (sev, code, detail))
    if not finds:
        print("  (no findings — manifest is well-formed and paths are legal)")
    if gate_fails:
        sys.stderr.write("plugin-check: FAIL — %d gate finding(s); the manifest will not load cleanly\n"
                         % len(gate_fails))
        return 1
    advisories = [f for f in finds if f[0] == "advisory"]
    if advisories:
        print("plugin-check: PASS (manifest well-formed) with %d advisory smell(s) — confirm the "
              "BUNDLE axis (does it do ONE job?) by review" % len(advisories))
    else:
        print("plugin-check: PASS — manifest well-formed, paths legal. NOTE: a clean run does not "
              "prove the bundle is FOCUSED — verify the BUNDLE axis (A1–A5) by review.")
    return 0


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("plugin-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("plugin-check: OK — manifest/name/version/path/marketplace checks verified over "
              "must-flag and must-not-flag fixtures")
        return 0
    # --json is a parse-anywhere reporting flag — strip it out, remember it, leave everything else.
    as_json = "--json" in argv
    if as_json:
        argv = [a for a in argv if a != "--json"]
        if not argv:
            sys.stderr.write("usage: plugin-check.py [--json] <plugin.json> [--marketplace ...] [--entry ...]\n")
            return 2
    if argv[0] == "template":
        print(json.dumps(TEMPLATE, indent=2))
        return 0
    plugin_path = argv[0]
    market_path = argv[argv.index("--marketplace") + 1] if "--marketplace" in argv else None
    entry_name = argv[argv.index("--entry") + 1] if "--entry" in argv else None
    return _run(plugin_path, market_path, entry_name, as_json)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
