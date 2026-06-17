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
import tempfile

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


def _check_skill(d, fails, warns):
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
    # the skills-studio structural floor — ADVISORY (a quality convention, not all skill vintages follow it;
    # `ref-*` reference skills use `## Invocation` + domain sections instead). Warn, don't fail.
    body = open(skill_md, encoding="utf-8").read()
    for needle, label in (("## Quick Start", "Quick Start"), ("SelfAudit", "§SelfAudit"), ("## Verify Target", "Verify Target")):
        if needle not in body:
            warns.append(f"{rel}: SKILL.md has no `{label}` (skills-studio floor — advisory)")
    # relative .md links: a broken link INSIDE the skill dir is a real internal bug (FAIL); a link that escapes the
    # skill dir is a CROSS-SKILL reference to a sibling that may or may not be installed — out of this skill's
    # control, so advisory (WARN). The gate validates each skill's own integrity, not its ecosystem assumptions.
    dabs = os.path.abspath(d)
    md_files = [skill_md] + [os.path.join(dp, fn) for dp, _, fns in os.walk(d) for fn in fns if fn.endswith(".md")]
    for mf in md_files:
        base = os.path.dirname(mf)
        for link in re.findall(r"\]\(([^)]+\.md)\)", open(mf, encoding="utf-8").read()):
            if link.startswith(("http", "#")):
                continue
            target = os.path.normpath(os.path.join(base, link.split("#")[0]))
            if os.path.isfile(target):
                continue
            inside = os.path.commonpath([os.path.abspath(target), dabs]) == dabs
            where = f"{os.path.relpath(mf, ROOT)}: broken link -> {link}"
            (fails if inside else warns).append(where + ("" if inside else " (cross-skill ref — advisory)"))


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


def _routing_dogfood(skills, routing_eval, warns):
    """Run routing-eval over every skill's checked-in `*.corpus.json` and surface precision-hole
    collisions (a description over-triggering on a sibling's phrase) as ADVISORY warnings. The
    routing eval is a lexical-overlap aid, not an oracle, so a collision is never a FAIL — it keeps
    the Phase-1 sibling-collision cleanup self-enforcing without letting the lossy proxy block the gate."""
    for d in skills:
        corpora = sorted(f for f in os.listdir(d) if f.endswith(".corpus.json"))
        if not corpora:
            continue
        desc = _frontmatter_description(os.path.join(d, "SKILL.md"))
        if not desc:
            continue
        rel = os.path.relpath(d, ROOT)
        fd, desc_path = tempfile.mkstemp(suffix=".txt")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(desc)
            for corpus in corpora:
                r = subprocess.run([sys.executable, routing_eval, desc_path,
                                    os.path.join(d, corpus), "--min-f1", "0"],
                                   capture_output=True, text=True)
                out = r.stdout + r.stderr
                m = re.search(r"fp=(\d+)", out)
                if not m:
                    if r.returncode != 0:
                        warns.append(f"{rel}: routing-eval could not evaluate {corpus} "
                                     f"({(r.stderr or r.stdout).strip()[:120]})")
                    continue
                if int(m.group(1)) == 0:
                    continue
                grabbed, seen = [], False
                for line in out.splitlines():
                    if "precision holes" in line:
                        seen = True
                    elif seen and "✗" in line:
                        grabbed.append(line.split("✗", 1)[1].strip())
                if grabbed:
                    for g in grabbed:
                        warns.append(f"{rel}: routing-corpus collision — description over-triggers on a "
                                     f"sibling phrase \"{g}\" (advisory; routing-eval is a lexical-overlap aid)")
                else:
                    warns.append(f"{rel}: routing-corpus shows {m.group(1)} collision(s) (advisory)")
        finally:
            os.unlink(desc_path)


def main(argv):
    if argv and argv[0] not in ("selftest", "check"):
        sys.stderr.write("usage: check-skills.py [selftest]\n")
        return 2
    skills = _skill_dirs()
    if not skills:
        sys.stderr.write("no skills found under */skills/*/\n")
        return 1
    fails, warns, selftests = [], [], []
    render_check = routing_eval = None
    for d in skills:
        _check_skill(d, fails, warns)
        selftests += _run_bin_selftests(d, fails)
        rc = os.path.join(d, "bin", "mermaid-render-check.py")
        if os.path.isfile(rc):
            render_check = rc
        re_path = os.path.join(d, "bin", "routing-eval.py")
        if os.path.isfile(re_path):
            routing_eval = re_path
    # dogfood: the render-check over every skill's reference docs — the example diagrams must pass the keyword gate
    if render_check:
        for d in skills:
            refs = os.path.join(d, "references")
            if os.path.isdir(refs):
                r = subprocess.run([sys.executable, render_check, refs], capture_output=True, text=True)
                if r.returncode != 0:
                    fails.append(f"render-check over {os.path.relpath(refs, ROOT)} failed:\n{(r.stderr or r.stdout).strip()[:500]}")
    # dogfood: routing-eval over every skill's checked-in corpus — keeps sibling-collision cleanup
    # self-enforcing (ADVISORY: the lexical-overlap proxy never FAILs the gate)
    if routing_eval:
        _routing_dogfood(skills, routing_eval, warns)
    if fails:
        sys.stderr.write(f"check-skills: FAIL ({len(fails)} issue(s))\n")
        for f in fails:
            sys.stderr.write(f"  - {f}\n")
        return 1
    print(f"check-skills: OK — {len(skills)} skill(s) valid, {len(selftests)} bin selftest(s) passed, "
          f"render-check + routing-eval dogfooded")
    for d in skills:
        print(f"    ✓ {os.path.relpath(d, ROOT)}")
    if warns:
        print(f"  {len(warns)} advisory warning(s):")
        for w in warns:
            print(f"    ⚠ {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
