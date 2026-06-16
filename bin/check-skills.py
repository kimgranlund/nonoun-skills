#!/usr/bin/env python3
"""check-skills.py — the nonoun-skills CI gate. Self-contained (stdlib only), clean-checkout-true.

Validates every bundled skill structurally, runs each skill's own `bin/*.py selftest`, and dogfoods the mermaid
render-check over the repo's markdown — so a fresh clone proves itself with no external tooling.

  python3 bin/check-skills.py            # validate all skills under */skills/*/
  python3 bin/check-skills.py selftest   # alias for the above (the repo's one gate)

Per skill it asserts: skill.json parses + `name` matches the dir; the SKILL.md YAML `description` is <= 1024 chars;
every path in skill.json `files[]` exists on disk; relative `.md` links in SKILL.md + references resolve; and a
SKILL.md carries `## Quick Start`, a `§SelfAudit`, and `## Verify Target` (the skills-studio structural floor).
Exit 1 on any failure. Python 3.8+.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _skill_dirs():
    out = []
    for dp, dns, fns in os.walk(ROOT):
        if ".git" in dp or "__pycache__" in dp:
            continue
        if os.path.basename(os.path.dirname(dp)) == "skills" and "skill.json" in fns:
            out.append(dp)
    return sorted(out)


def _frontmatter_description(skill_md):
    """The YAML `description:` (supports a folded `>` block or an inline value)."""
    t = open(skill_md, encoding="utf-8").read()
    m = re.search(r"(?ms)^---\n(.*?)\n---", t)
    if not m:
        return None
    fm = m.group(1)
    block = re.search(r"(?ms)^description:\s*>\s*\n((?:[ \t]+.*\n?)+)", fm)
    if block:
        return " ".join(l.strip() for l in block.group(1).splitlines() if l.strip())
    inline = re.search(r"(?m)^description:\s*(.+)$", fm)
    return inline.group(1).strip() if inline else None


def _check_skill(d, fails):
    name = os.path.basename(d)
    rel = os.path.relpath(d, ROOT)
    try:
        man = json.load(open(os.path.join(d, "skill.json"), encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        fails.append(f"{rel}: skill.json unreadable ({e})")
        return
    if man.get("name") != name:
        fails.append(f"{rel}: skill.json name {man.get('name')!r} != dir {name!r}")
    skill_md = os.path.join(d, "SKILL.md")
    if not os.path.isfile(skill_md):
        fails.append(f"{rel}: SKILL.md missing")
        return
    desc = _frontmatter_description(skill_md)
    if not desc:
        fails.append(f"{rel}: SKILL.md has no frontmatter description")
    elif len(desc) > 1024:
        fails.append(f"{rel}: SKILL.md description is {len(desc)} chars (> 1024)")
    for f in man.get("files", []):
        if not os.path.isfile(os.path.join(d, f)):
            fails.append(f"{rel}: skill.json files[] lists {f} — not on disk")
    # the skills-studio structural floor
    body = open(skill_md, encoding="utf-8").read()
    for needle, label in (("## Quick Start", "Quick Start"), ("SelfAudit", "§SelfAudit"), ("## Verify Target", "Verify Target")):
        if needle not in body:
            fails.append(f"{rel}: SKILL.md missing `{label}`")
    # relative .md links resolve (SKILL.md + every references/*.md)
    md_files = [skill_md] + [os.path.join(dp, fn) for dp, _, fns in os.walk(d) for fn in fns if fn.endswith(".md")]
    for mf in md_files:
        base = os.path.dirname(mf)
        for link in re.findall(r"\]\(([^)]+\.md)\)", open(mf, encoding="utf-8").read()):
            if link.startswith(("http", "#")):
                continue
            target = os.path.normpath(os.path.join(base, link.split("#")[0]))
            if not os.path.isfile(target):
                fails.append(f"{os.path.relpath(mf, ROOT)}: broken link -> {link}")


def _run_bin_selftests(d, fails):
    bindir = os.path.join(d, "bin")
    if not os.path.isdir(bindir):
        return []
    ran = []
    for fn in sorted(os.listdir(bindir)):
        if not fn.endswith(".py"):
            continue
        p = os.path.join(bindir, fn)
        r = subprocess.run([sys.executable, p, "selftest"], capture_output=True, text=True)
        ran.append((os.path.relpath(p, ROOT), r.returncode))
        if r.returncode != 0:
            fails.append(f"{os.path.relpath(p, ROOT)} selftest failed:\n{(r.stderr or r.stdout).strip()[:500]}")
    return ran


def main(argv):
    if argv and argv[0] not in ("selftest", "check"):
        sys.stderr.write("usage: check-skills.py [selftest]\n")
        return 2
    skills = _skill_dirs()
    if not skills:
        sys.stderr.write("no skills found under */skills/*/\n")
        return 1
    fails, selftests = [], []
    render_check = None
    for d in skills:
        _check_skill(d, fails)
        selftests += _run_bin_selftests(d, fails)
        rc = os.path.join(d, "bin", "mermaid-render-check.py")
        if os.path.isfile(rc):
            render_check = rc
    # dogfood: the render-check over every skill's reference docs — the example diagrams must pass the keyword gate
    if render_check:
        for d in skills:
            refs = os.path.join(d, "references")
            if os.path.isdir(refs):
                r = subprocess.run([sys.executable, render_check, refs], capture_output=True, text=True)
                if r.returncode != 0:
                    fails.append(f"render-check over {os.path.relpath(refs, ROOT)} failed:\n{(r.stderr or r.stdout).strip()[:500]}")
    if fails:
        sys.stderr.write(f"check-skills: FAIL ({len(fails)} issue(s))\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print(f"check-skills: OK — {len(skills)} skill(s) valid, {len(selftests)} bin selftest(s) passed, render-check dogfooded")
    for d in skills:
        print(f"    ✓ {os.path.relpath(d, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
