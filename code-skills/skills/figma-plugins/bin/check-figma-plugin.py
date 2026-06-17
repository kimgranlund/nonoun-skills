#!/usr/bin/env python3
"""check-figma-plugin.py — static gate for a Figma plugin directory (stdlib only).

Mechanizes the §SelfAudit floor so it can't be skipped:
  - manifest.json parses; main (+ ui if present) point at files that exist; editorType is set;
    networkAccess is present and not an unjustified wildcard;
  - the sandbox file (manifest.main) is PURE — it calls no DOM/network/dynamic-import API
    (document./window./fetch(/new XMLHttpRequest/new WebSocket/localStorage/import()), with
    comments stripped first so a comment that NAMES those APIs (to say it avoids them) is ignored.

Usage:
  check-figma-plugin.py <plugin-dir>   # check a plugin; exit 0 pass / 1 findings
  check-figma-plugin.py selftest       # run fixtures; exit 0 pass
"""
import json
import os
import re
import sys
import tempfile

# Identifiers/calls that only exist in the iframe/browser, never in the sandbox VM.
SANDBOX_FORBIDDEN = re.compile(
    r"\bdocument\.|\bwindow\.|\bfetch\s*\(|new\s+XMLHttpRequest|new\s+WebSocket|\blocalStorage\b|\bimport\s*\("
)

# Web storage that Figma's plugin iframe can DENY (SecurityError) — an unguarded access at
# UI boot blanks the panel. Advisory, not a hard gate: guarded use (try/catch) is legitimate.
WEB_STORAGE = re.compile(r"\b(?:localStorage|sessionStorage|indexedDB)\b|\bdocument\.cookie\b")

# SYNC variable/node/style getters that THROW under documentAccess:"dynamic-page" (gotcha #2).
# The async variants have an `Async` between the name and the `(`, so `name\s*\(` matches the
# SYNC form only — the regex naturally excludes getLocalVariablesAsync(, getNodeByIdAsync(, …
SYNC_GETTERS = re.compile(
    r"\bget(?:LocalVariables|LocalVariableCollections|NodeById|LocalTextStyles|"
    r"LocalPaintStyles|LocalEffectStyles|LocalGridStyles)\s*\("
)
# Document-READ surfaces. Combined with non-'none' networkAccess this is the exfiltration
# trifecta (document → a remote) — advisory, since a trusted+essential remote is legitimate.
DOC_READ = re.compile(r"\bfigma\.(?:variables\b|currentPage\b|root\b|getNodeBy|getStyleBy|getLocalVariables)")


def strip_comments(src):
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)   # block comments
    src = re.sub(r"//[^\n]*", "", src)         # line comments
    return src


def check_plugin(d):
    errs = []
    mpath = os.path.join(d, "manifest.json")
    if not os.path.isfile(mpath):
        return ["no manifest.json in " + d]
    try:
        m = json.load(open(mpath, encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 - report any parse failure
        return ["manifest.json is invalid JSON: " + str(e)]

    main = m.get("main")
    if not main:
        errs.append("manifest.main missing (the sandbox file)")
    elif not os.path.isfile(os.path.join(d, main)):
        errs.append("manifest.main file not found: " + main)

    ui = m.get("ui")
    if ui and not os.path.isfile(os.path.join(d, ui)):
        errs.append("manifest.ui file not found: " + ui)

    et = m.get("editorType")
    if not isinstance(et, list) or not et:
        errs.append("manifest.editorType must be a non-empty array (e.g. [\"figma\"])")

    na = m.get("networkAccess")
    if na is None:
        errs.append('manifest.networkAccess missing (use {"allowedDomains":["none"]})')
    else:
        domains = na.get("allowedDomains") if isinstance(na, dict) else (["none"] if na == "none" else None)
        if domains is None or not isinstance(domains, list):
            errs.append("manifest.networkAccess malformed (want an object with allowedDomains[])")
        elif domains == ["*"] and not (isinstance(na, dict) and na.get("reasoning")):
            errs.append("networkAccess wildcard '*' needs a reasoning")

    if main and os.path.isfile(os.path.join(d, main)):
        code = strip_comments(open(os.path.join(d, main), encoding="utf-8").read())
        hit = SANDBOX_FORBIDDEN.search(code)
        if hit:
            errs.append("sandbox file calls a non-sandbox API: " + hit.group(0).strip())
        # gotcha #2: under documentAccess "dynamic-page" the SYNC getters throw — require async.
        if m.get("documentAccess") == "dynamic-page":
            sg = SYNC_GETTERS.search(code)
            if sg:
                errs.append("sandbox calls a SYNC getter under documentAccess 'dynamic-page' "
                            "(throws in Figma): " + sg.group(0).strip() + " — use the *Async variant")

    return errs


def exfil_warnings(d, m):
    """Advisory (non-failing): the exfiltration trifecta. A sandbox that READS the document AND
    has network access can ship the document to a remote. Keep those mutually exclusive unless the
    remote is essential + trusted (and never let untrusted imported content choose the URL)."""
    main = m.get("main")
    if not main or not os.path.isfile(os.path.join(d, main)):
        return []
    na = m.get("networkAccess")
    domains = na.get("allowedDomains") if isinstance(na, dict) else ([] if na == "none" else None)
    online = bool(domains) and domains != ["none"]
    if not online:
        return []
    code = strip_comments(open(os.path.join(d, main), encoding="utf-8").read())
    if DOC_READ.search(code):
        return ["sandbox both READS the document (figma.variables/currentPage/getNodeBy…) AND has "
                "network access (networkAccess ≠ none) — the exfiltration trifecta. Keep them mutually "
                "exclusive unless the remote is essential + trusted; never let imported content pick the URL."]
    return []


def storage_warnings(d, m):
    """Advisory (non-failing): ui.html web storage that looks unguarded.

    Figma's plugin iframe can DENY web storage — localStorage/sessionStorage throw a
    SecurityError, not return null, so an unguarded read at boot blanks the UI (works in a
    browser tab, blank inside Figma). Heuristic: flag only when ui.html touches web storage
    yet has NO try/catch anywhere — a guarded plugin (any `try {`) is assumed deliberate.
    """
    ui = m.get("ui")
    if not ui or not os.path.isfile(os.path.join(d, ui)):
        return []
    src = strip_comments(open(os.path.join(d, ui), encoding="utf-8").read())
    if WEB_STORAGE.search(src) and not re.search(r"\btry\s*\{", src):
        return [
            "ui.html uses web storage (localStorage/sessionStorage/…) with no try/catch anywhere — "
            "Figma's iframe can DENY it (SecurityError → blank UI). Guard every access, or persist via "
            "figma.clientStorage over the bridge."
        ]
    return []


def _write(d, manifest, code, ui=None):
    os.makedirs(d, exist_ok=True)
    json.dump(manifest, open(os.path.join(d, "manifest.json"), "w"))
    open(os.path.join(d, "code.js"), "w").write(code)
    if ui is not None:
        open(os.path.join(d, "ui.html"), "w").write(ui)


def selftest():
    fails = []
    with tempfile.TemporaryDirectory() as t:
        # GOOD — offline, files present, sandbox-pure, async getters.
        good = os.path.join(t, "good")
        _write(good,
               {"name": "g", "id": "g", "api": "1.0.0", "main": "code.js", "ui": "ui.html",
                "editorType": ["figma"], "documentAccess": "dynamic-page",
                "networkAccess": {"allowedDomains": ["none"]}},
               "figma.showUI(__html__);\nfigma.ui.onmessage = async (m) => { await figma.variables.getLocalVariablesAsync(); };",
               "<button>x</button>")
        e = check_plugin(good)
        if e:
            fails.append("good plugin flagged: " + str(e))

        # BAD — fetch in the sandbox, missing ui file, empty editorType, unjustified wildcard.
        bad = os.path.join(t, "bad")
        _write(bad,
               {"name": "b", "id": "b", "main": "code.js", "ui": "missing.html",
                "editorType": [], "networkAccess": {"allowedDomains": ["*"]}},
               "fetch('https://x').then(r => r.json());")
        e = check_plugin(bad)
        for want in ["sandbox file calls", "ui file not found", "editorType", "wildcard"]:
            if not any(want in x for x in e):
                fails.append("bad plugin: missed '" + want + "' in " + str(e))

        # COMMENT mentioning forbidden APIs must NOT trip sandbox purity.
        c = os.path.join(t, "c")
        _write(c,
               {"name": "c", "id": "c", "main": "code.js", "editorType": ["figma"], "networkAccess": "none"},
               "// no fetch, no document, no localStorage, no import() here\nfigma.notify('ok');")
        e = check_plugin(c)
        if any("sandbox file calls" in x for x in e):
            fails.append("a comment naming the APIs tripped sandbox purity: " + str(e))

        # UNGUARDED web storage in ui.html (no try/catch) → advisory warning.
        usg = os.path.join(t, "usg")
        gm = {"name": "u", "id": "u", "main": "code.js", "ui": "ui.html",
              "editorType": ["figma"], "networkAccess": "none"}
        _write(usg, gm, "figma.showUI(__html__);",
               "<script>var s=localStorage.getItem('k');</script>")
        if not storage_warnings(usg, gm):
            fails.append("unguarded localStorage in ui.html did not warn")
        if check_plugin(usg):  # storage is advisory only — must NOT fail the gate
            fails.append("unguarded ui.html storage wrongly failed the hard gate: " + str(check_plugin(usg)))

        # GUARDED web storage (try/catch present) → NO warning.
        gsg = os.path.join(t, "gsg")
        _write(gsg, gm, "figma.showUI(__html__);",
               "<script>try{var s=localStorage.getItem('k');}catch(e){}</script>")
        if storage_warnings(gsg, gm):
            fails.append("guarded localStorage in ui.html wrongly warned")

        # SYNC getter under documentAccess dynamic-page → HARD fail (gotcha #2).
        sg = os.path.join(t, "sg")
        _write(sg, {"name": "s", "id": "s", "main": "code.js", "editorType": ["figma"],
                    "documentAccess": "dynamic-page", "networkAccess": "none"},
               "const v = figma.variables.getLocalVariables();")
        if not any("SYNC getter" in x for x in check_plugin(sg)):
            fails.append("sync getter under dynamic-page did not fail: " + str(check_plugin(sg)))
        # the ASYNC variant must NOT trip it.
        ag = os.path.join(t, "ag")
        _write(ag, {"name": "a", "id": "a", "main": "code.js", "editorType": ["figma"],
                    "documentAccess": "dynamic-page", "networkAccess": "none"},
               "const v = await figma.variables.getLocalVariablesAsync();")
        if any("SYNC getter" in x for x in check_plugin(ag)):
            fails.append("async getter wrongly flagged as sync: " + str(check_plugin(ag)))

        # Exfiltration trifecta: doc-read + network → advisory WARN, NOT a hard fail.
        xm = {"name": "x", "id": "x", "main": "code.js", "editorType": ["figma"],
              "networkAccess": {"allowedDomains": ["api.example.com"]}}
        xf = os.path.join(t, "xf")
        _write(xf, xm, "const v = await figma.variables.getLocalVariablesAsync();")
        if not exfil_warnings(xf, xm):
            fails.append("doc-read + network did not warn (trifecta)")
        if check_plugin(xf):  # advisory only — must NOT fail the hard gate
            fails.append("trifecta wrongly failed the hard gate: " + str(check_plugin(xf)))
        # offline doc-read must NOT warn.
        om = {"name": "o", "id": "o", "main": "code.js", "editorType": ["figma"], "networkAccess": "none"}
        of = os.path.join(t, "of")
        _write(of, om, "const v = await figma.variables.getLocalVariablesAsync();")
        if exfil_warnings(of, om):
            fails.append("offline doc-read wrongly warned")

    return fails


def main(argv):
    if not argv or argv[0] == "selftest":
        fails = selftest()
        if fails:
            print("SELFTEST FAIL:")
            for f in fails:
                print("  -", f)
            return 1
        print("check-figma-plugin selftest: OK")
        return 0
    errs = check_plugin(argv[0])
    if errs:
        print("FAIL:", argv[0])
        for e in errs:
            print("  -", e)
        return 1
    # Advisory warnings never fail the gate — they flag a likely "blank in Figma" footgun.
    try:
        m = json.load(open(os.path.join(argv[0], "manifest.json"), encoding="utf-8"))
        for w in storage_warnings(argv[0], m) + exfil_warnings(argv[0], m):
            print("  WARN:", w)
    except Exception:  # noqa: BLE001 - manifest already validated above
        pass
    print("OK:", argv[0], "— manifest shape + sandbox purity + network surface")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
