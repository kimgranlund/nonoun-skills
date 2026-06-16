#!/usr/bin/env python3
"""mermaid-render-check.py — mechanize the M2/M3 gates: do the ```mermaid blocks in a doc actually render?

Two layers, so the high-value check runs everywhere and the full check runs where the engine is installed:

  1. STATIC keyword gate (always, stdlib-only, no engine) — extract every ```mermaid fenced block and assert its
     first line is a known diagram keyword with the CORRECT `-beta` suffix. This catches the single most common
     failure the reference documents — a bare `sankey`/`architecture`/`venn`/`ishikawa`/`wardley`/`treeView`,
     which is a hard syntax error in mermaid 11.x (the engine needs the `-beta` form). Deterministic; mints the
     verdict from the source text, never from inference.
  2. RENDER check (only if `mmdc`, the @mermaid-js/mermaid-cli, is on PATH) — render each block under
     securityLevel:strict and mint pass/fail from the engine's EXIT STATUS. The real M3 test. If `mmdc` is absent
     it SKIPs with an install hint and does NOT fail — the static gate still ran.

    python3 mermaid-render-check.py <file.md | dir>     # check every ```mermaid block (recurses a dir)
    python3 mermaid-render-check.py -                   # read markdown from stdin
    python3 mermaid-render-check.py selftest            # prove the static gate (no engine needed)

Exit 1 if any block fails a layer that ran; 0 otherwise. Python 3.8+, stdlib only.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

# The diagram keywords valid in mermaid@11.15.0. The `-beta` set is load-bearing: the bare form is a syntax error.
BETA_REQUIRED = {"sankey", "architecture", "venn", "ishikawa", "wardley", "treeView"}  # → must be `<name>-beta`
NO_SUFFIX = {
    "flowchart", "graph", "sequenceDiagram", "classDiagram", "stateDiagram", "stateDiagram-v2",
    "erDiagram", "journey", "gantt", "pie", "quadrantChart", "requirementDiagram", "gitGraph",
    "mindmap", "timeline", "xychart-beta", "xyChart", "block", "block-beta", "packet", "packet-beta",
    "radar", "c4", "C4Context", "C4Container", "C4Component", "C4Dynamic", "C4Deployment",
    "zenuml", "treemap", "kanban", "eventmodeling", "info",
}
BETA_OK = {f"{k}-beta" for k in BETA_REQUIRED} | {"xychart-beta", "block-beta", "packet-beta"}


def extract_blocks(md):
    """Return [(line_no, code)] for each ```mermaid fenced block. Tolerates ~~~ fences and a language tag with
    trailing whitespace; ignores nested fences inside a ```markdown example block by tracking the opening fence."""
    blocks, lines = [], md.splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r"^(\s*)(`{3,}|~{3,})\s*mermaid\s*$", lines[i])
        if m:
            fence = m.group(2)[0] * 3
            start = i + 1
            j = start
            while j < len(lines) and not re.match(rf"^\s*{re.escape(fence[0])}{{3,}}\s*$", lines[j]):
                j += 1
            blocks.append((start + 1, "\n".join(lines[start:j])))
            i = j + 1
        else:
            i += 1
    return blocks


def first_keyword(code):
    """The diagram keyword = the first token of the first content line, skipping YAML frontmatter, `%%{init}%%`
    directives, blank lines, and `%%` comments. Returns (keyword, first_line) or (None, None)."""
    lines = code.splitlines()
    i = 0
    if i < len(lines) and lines[i].strip() == "---":          # YAML frontmatter
        i += 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    while i < len(lines):
        s = lines[i].strip()
        if not s or s.startswith("%%"):                        # blank / directive / comment
            i += 1
            continue
        return s.split()[0].rstrip(";"), s
    return None, None


def static_check(code):
    """(ok, reason) — the keyword gate, no engine. Flags a bare beta keyword (the #1 failure) and an unknown one."""
    kw, line = first_keyword(code)
    if kw is None:
        return False, "empty diagram (no keyword line)"
    if kw in BETA_REQUIRED:
        return False, f"`{kw}` needs the `-beta` suffix — write `{kw}-beta` (bare `{kw}` is a syntax error in 11.x)"
    if kw in NO_SUFFIX or kw in BETA_OK:
        return True, f"keyword `{kw}` OK"
    # an unknown keyword may still be valid (a type we don't enumerate) — warn, don't hard-fail the static layer
    return True, f"keyword `{kw}` not in the known set — verify it renders (warn)"


def _mmdc():
    return shutil.which("mmdc")


def render_check(code, mmdc):
    """(ok, reason) — render the block via mmdc under securityLevel:strict; verdict from EXIT STATUS."""
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "d.mmd")
        out = os.path.join(td, "d.svg")
        with open(src, "w", encoding="utf-8") as f:
            f.write(code + "\n")
        try:
            p = subprocess.run([mmdc, "-i", src, "-o", out, "-q"],
                               capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError) as e:
            return False, f"mmdc could not run: {e}"
        if p.returncode == 0 and os.path.exists(out):
            return True, "rendered"
        err = (p.stderr or p.stdout or "").strip().splitlines()
        return False, "render failed: " + (err[-1] if err else f"exit {p.returncode}")


def check_text(md, label):
    blocks = extract_blocks(md)
    if not blocks:
        return 0, 0, []  # nothing to check
    mmdc = _mmdc()
    fails = []
    for ln, code in blocks:
        ok, reason = static_check(code)
        if not ok:
            fails.append((label, ln, "static", reason))
            continue
        if mmdc:
            rok, rreason = render_check(code, mmdc)
            if not rok:
                fails.append((label, ln, "render", rreason))
    return len(blocks), (1 if mmdc else 0), fails


def run(paths):
    targets = []
    for path in paths:
        if path == "-":
            targets.append(("<stdin>", sys.stdin.read()))
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for fn in files:
                    if fn.endswith((".md", ".markdown", ".mmd")):
                        fp = os.path.join(root, fn)
                        targets.append((fp, open(fp, encoding="utf-8").read()))
        elif os.path.isfile(path):
            targets.append((path, open(path, encoding="utf-8").read()))
        else:
            sys.stderr.write(f"not found: {path}\n")
            return 2
    total_blocks, any_render, all_fails = 0, 0, []
    for label, md in targets:
        nb, rendered, fails = check_text(md, label)
        total_blocks += nb
        any_render = any_render or rendered
        all_fails.extend(fails)
    engine = "mmdc render + static keyword gate" if _mmdc() else "static keyword gate only (mmdc not on PATH — `npm i -g @mermaid-js/mermaid-cli` to mechanize the M3 render gate)"
    if all_fails:
        sys.stderr.write(f"mermaid-render-check: FAIL — {len(all_fails)} block(s) ({engine})\n")
        for lbl, ln, layer, reason in all_fails:
            sys.stderr.write(f"  {lbl}:{ln} [{layer}] {reason}\n")
        return 1
    print(f"mermaid-render-check: OK — {total_blocks} block(s) pass ({engine})")
    return 0


def selftest():
    """Prove the static keyword gate without the engine: the bare beta keywords FAIL, the correct forms PASS."""
    fails = []
    cases = [
        ("sankey-beta\nA,B,1", True, "sankey-beta accepted"),
        ("sankey\nA,B,1", False, "bare sankey caught (must be -beta)"),
        ("architecture\n  group a(cloud)[A]", False, "bare architecture caught"),
        ("architecture-beta\n  group a(cloud)[A]", True, "architecture-beta accepted"),
        ("flowchart TD\n A-->B", True, "flowchart accepted"),
        ("erDiagram\n A ||--o{ B : x", True, "erDiagram accepted (no suffix)"),
        ("venn\n set A", False, "bare venn caught"),
        ("wardley-beta\ntitle X", True, "wardley-beta accepted"),
        ("---\nconfig:\n  theme: dark\n---\ngantt\n title T", True, "keyword found past YAML frontmatter"),
        ("%%{init: {'theme':'dark'}}%%\nsankey\nA,B,1", False, "bare sankey caught past a directive"),
    ]
    for code, want_ok, desc in cases:
        ok, reason = static_check(code)
        if ok != want_ok:
            fails.append(f"{desc}: expected ok={want_ok}, got {ok} ({reason})")
    # extraction: a ```markdown block that merely SHOWS a mermaid fence is not itself extracted as a diagram
    md = "# doc\n\n```mermaid\nflowchart TD\n A-->B\n```\n\ntext\n\n```mermaid\nsankey\nA,B,1\n```\n"
    blocks = extract_blocks(md)
    if len(blocks) != 2:
        fails.append(f"extraction: expected 2 mermaid blocks, got {len(blocks)}")
    _, _, dfails = check_text(md, "x")          # the 2nd block (bare sankey) must be a static failure
    if not any(layer == "static" for _, _, layer, _ in dfails):
        fails.append("end-to-end: the bare-sankey block was not caught by the static gate")
    if fails:
        sys.stderr.write("mermaid-render-check selftest: FAIL\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    engine = "mmdc present" if _mmdc() else "mmdc absent (static gate only)"
    print(f"mermaid-render-check selftest: OK (static keyword gate catches bare-beta + unknown; {engine})")
    return 0


def main(argv):
    if not argv:
        sys.stderr.write(__doc__.splitlines()[0] + "\nusage: mermaid-render-check.py <file|dir|-> | selftest\n")
        return 2
    if argv[0] == "selftest":
        return selftest()
    return run(argv)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
