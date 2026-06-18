#!/usr/bin/env python3
"""refactor-scan.py — the mechanical spine of skills-refactor.

Library-level skill refactor (rename / merge / retire / split) is dangerous in two
ways this script gates:
  1. A bulk find-and-replace over an unbounded pattern silently corrupts skill names
     that are substrings of others (rename `report` → it rewrites `report-strategic`).
     → every match here is WORD-BOUNDARIED (core-foo never matches core-foobar).
  2. A destructive step (rm / overwrite) in a no-git repo is unrecoverable without a
     whole-library backup. → `check-backup` is the precondition a delete must pass.

Turns skills-refactor's §SelfAudit prose items into real checks.

Subcommands
  scan <old>                 Footprint map: every word-boundaried hit, classified by
                             file into LIVE (sweep) / MIXED (exclude+hand-edit) /
                             HISTORY (preserve). skill.json tag-only hits → NOT-A-REF.
  dry-run <old> <new>        The substitutions the in-place sweep WOULD make across
                             LIVE files. No writes — review before applying.
  check-backup [--since T]   Assert a whole-library backup tarball exists (mtime >= T,
             [--glob G]      epoch seconds; default: any). The precondition for a delete.
  verify <old>               Assert ZERO *dangling* live refs to <old> remain. Dated history
                             (MIXED) + retirement-marked provenance ("former/retired/absorbed/
                             merged X", "(retired) → Y") are allowed; a quoted "<old>" wiring
                             token or a dead <old>/ path still FAILs. The done-gate.
  selftest                   CI guard: word-boundary + classification + verify logic.

Exit 0 = ok/clean · 1 = a gate fails · 2 = bad invocation. Stdlib only (Python 3.9+).
"""
from __future__ import annotations
import argparse
import contextlib
import glob as globmod
import io
import json
import os
import re
import sys
import tempfile

# library root = three dirs up from this file (<root>/skills-refactor/scripts/refactor-scan.py)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCAN_EXT = (".md", ".json", ".py")
# files excluded from the auto-sweep: dated history (reviews) + MIXED (live row + historical log)
HISTORY_BASENAMES = {"CHANGELOG.md", "ROADMAP.md", "BACKLOG.md", "AGENTS.md", "README.md"}

# A *retired* skill legitimately leaves PROVENANCE mentions in live files — a SKILL.md
# "absorbed from the former X" note, a planning-table "(retired) → Y" redirect row, an
# eval-corpus provenance note, a re-baseline `reason` naming what was dropped. These name
# the old skill *as history*, not as a live pointer. verify must NOT fail on them — but it
# MUST still fail on a dangling pointer (a `peer_skills` element, a `use X` routing pointer,
# a dead `X/...` path). A line is provenance iff it carries a retirement marker; it is
# dangling-structural iff the old name appears as a quoted token or a path segment (those are
# wiring and break on delete regardless of any stray marker word on the same line).
PROVENANCE_MARKERS = re.compile(
    r"\b(former(ly)?|retired|absorb(ed|ing|s)|merged|fold(ed|s)|deprecat(ed|es)|renamed|"
    r"supersed(ed|es)|replaced|defunct|removed)\b|→|\(retired\)",
    re.IGNORECASE,
)


def _wordboundary(name: str) -> re.Pattern:
    """Match `name` only when not flanked by [\\w-] — so core-foo ∌ core-foobar / core-foo2."""
    return re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])")


def classify(relpath: str) -> str:
    """LIVE (rewire) / HISTORY (preserve, reviews) / MIXED (exclude from sweep, hand-edit)."""
    parts = relpath.split(os.sep)
    if "reviews" in parts:
        return "HISTORY"
    if os.path.basename(relpath) in HISTORY_BASENAMES:
        return "MIXED"
    return "LIVE"


def _is_structural_ref(line: str, old: str) -> bool:
    """True if `old` appears as live WIRING on this line — a quoted token ("old" as a
    peer_skills/files element or a JSON key) or a path segment (old/...). Such a ref dangles
    when the skill is deleted, so it FAILs verify even if a retirement word shares the line."""
    return bool(re.search(r'"' + re.escape(old) + r'"', line)) or \
        bool(re.search(r"(?<![\w-])" + re.escape(old) + r"/", line))


def _is_dangling(line: str, old: str) -> bool:
    """A remaining LIVE-file occurrence is a dangling ref (FAIL) if it's structural wiring,
    or if it's bare prose with no retirement marker. It's allowed (provenance) only when a
    retirement marker is present AND it isn't structural wiring."""
    if _is_structural_ref(line, old):
        return True
    return not PROVENANCE_MARKERS.search(line)


def _iter_files(root: str):
    for dp, dirs, fns in os.walk(root):
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules") and not d.startswith(".backup")]
        for fn in fns:
            if fn.endswith(SCAN_EXT):
                yield os.path.relpath(os.path.join(dp, fn), root)


def _tag_only(root: str, relpath: str, pat: re.Pattern) -> bool:
    """True if a skill.json's only matches are inside its `tags` array (a category, not a ref)."""
    if os.path.basename(relpath) != "skill.json":
        return False
    try:
        data = json.load(open(os.path.join(root, relpath), encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    tags = data.get("tags", [])
    in_tags = any(pat.search(t) for t in tags if isinstance(t, str))
    # any match outside the tags array? serialize the doc without tags and test.
    rest = dict(data)
    rest.pop("tags", None)
    in_rest = bool(pat.search(json.dumps(rest)))
    return in_tags and not in_rest


def find_hits(root: str, old: str):
    """Return {relpath: (class, [ (lineno, line) ])} for word-boundaried matches; tag-only → 'NOT-A-REF'."""
    pat = _wordboundary(old)
    hits: dict[str, tuple] = {}
    for rel in _iter_files(root):
        try:
            lines = open(os.path.join(root, rel), encoding="utf-8").read().splitlines()
        except OSError:
            continue
        matched = [(i + 1, ln.strip()) for i, ln in enumerate(lines) if pat.search(ln)]
        if not matched:
            continue
        cls = "NOT-A-REF" if _tag_only(root, rel, pat) else classify(rel)
        hits[rel] = (cls, matched)
    return hits


def cmd_scan(root: str, old: str, as_json: bool) -> int:
    hits = find_hits(root, old)
    buckets: dict[str, list] = {"LIVE": [], "MIXED": [], "HISTORY": [], "NOT-A-REF": []}
    for rel, (cls, _m) in sorted(hits.items()):
        buckets[cls].append(rel)
    if as_json:
        print(json.dumps({"old": old, "files": {k: v for k, v in buckets.items()}}, indent=2))
        return 0
    print(f"footprint of '{old}' — {len(hits)} files\n")
    print("LIVE (sweep old→new):")
    for f in buckets["LIVE"]:
        print(f"  {f}  ({len(hits[f][1])} hit{'s' if len(hits[f][1]) > 1 else ''})")
    print("\nMIXED (exclude from auto-sweep; hand-edit the live row/title, keep the dated log):")
    for f in buckets["MIXED"]:
        print(f"  {f}")
    print("\nHISTORY (preserve verbatim):")
    for f in buckets["HISTORY"]:
        print(f"  {f}")
    if buckets["NOT-A-REF"]:
        print("\nNOT-A-REF (skill.json tag-only — a category, not a pointer; leave):")
        for f in buckets["NOT-A-REF"]:
            print(f"  {f}")
    print(f"\n→ sweep the {len(buckets['LIVE'])} LIVE files; hand-edit the {len(buckets['MIXED'])} MIXED; "
          f"leave {len(buckets['HISTORY'])} HISTORY + {len(buckets['NOT-A-REF'])} tag-only.")
    return 0


def cmd_dry_run(root: str, old: str, new: str) -> int:
    pat = _wordboundary(old)
    hits = find_hits(root, old)
    live = {f: m for f, (c, m) in hits.items() if c == "LIVE"}
    if not live:
        print(f"no LIVE word-boundaried matches for '{old}' — nothing to sweep.")
        return 0
    print(f"DRY-RUN: '{old}' → '{new}' across {len(live)} LIVE files (no files changed)\n")
    for f in sorted(live):
        for lineno, line in live[f]:
            print(f"  {f}:{lineno}")
            print(f"    - {line}")
            print(f"    + {pat.sub(new, line)}")
    print("\nReview the above, then apply the word-boundaried in-place sweep (see references/operations.md).")
    return 0


def cmd_check_backup(since: float, glob_pat: str) -> int:
    matches = globmod.glob(os.path.expanduser(glob_pat))
    fresh = [m for m in matches if os.path.getmtime(m) >= since]
    if not fresh:
        print(f"FAIL: no backup tarball matching {glob_pat}" + (f" newer than {since}" if since else "")
              + " — back up the whole library before any delete/overwrite.", file=sys.stderr)
        return 1
    newest = max(fresh, key=os.path.getmtime)
    print(f"OK: backup present — {newest}")
    return 0


def cmd_verify(root: str, old: str, as_json: bool) -> int:
    hits = find_hits(root, old)
    mixed = {f: m for f, (c, m) in hits.items() if c == "MIXED"}
    # split each LIVE file's matches per-line: dangling wiring (FAIL) vs provenance mention (OK)
    dangling: dict[str, list] = {}
    provenance: dict[str, list] = {}
    for f, (c, matched) in hits.items():
        if c != "LIVE":
            continue
        d = [(ln, txt) for ln, txt in matched if _is_dangling(txt, old)]
        p = [(ln, txt) for ln, txt in matched if not _is_dangling(txt, old)]
        if d:
            dangling[f] = d
        if p:
            provenance[f] = p
    ok = not dangling
    if as_json:
        print(json.dumps({"old": old,
                          "live_refs_remaining": sorted(dangling),
                          "provenance_allowed": sorted(provenance),
                          "mixed_review": sorted(mixed), "ok": ok}, indent=2))
        return 0 if ok else 1
    if dangling:
        print(f"FAIL: {sum(len(v) for v in dangling.values())} dangling LIVE reference(s) to '{old}' "
              f"remain — these name a deleted skill as if it still exists; rewire them:")
        for f in sorted(dangling):
            for lineno, line in dangling[f]:
                print(f"  {f}:{lineno}: {line}")
    else:
        print(f"OK: zero dangling LIVE references to '{old}'.")
    if provenance:
        print(f"\n(allowed) {sum(len(v) for v in provenance.values())} provenance mention(s) of '{old}' in "
              f"{len(provenance)} live file(s) — retirement-marked ('former/retired/absorbed/merged/→'), "
              f"naming it as history, not as a live pointer; kept:")
        for f in sorted(provenance):
            for lineno, line in provenance[f]:
                print(f"  {f}:{lineno}: {line[:100]}")
    if mixed:
        print(f"\n(review) {len(mixed)} MIXED file(s) still mention '{old}' — confirm each is a historical/log "
              f"line, not a live row that needs the new name: {', '.join(sorted(mixed))}")
    return 0 if ok else 1


def cmd_selftest() -> int:
    """Prove word-boundary + classification + verify on a temp fixture."""
    fails = []
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "core-foo"))
        os.makedirs(os.path.join(d, "core-foobar"))
        os.makedirs(os.path.join(d, "core-foo", "reviews"))
        # a LIVE ref to core-foo + a substring trap (core-foobar) in another skill's SKILL.md
        open(os.path.join(d, "core-foobar", "SKILL.md"), "w").write(
            "peer: core-foo\nunrelated: core-foobar is its own skill\n")
        # a skill.json whose ONLY core-foo hit is a tag (NOT-A-REF)
        json.dump({"name": "x", "tags": ["core-foo", "meta"], "files": ["SKILL.md"]},
                  open(os.path.join(d, "core-foobar", "skill.json"), "w"))
        # dated history that legitimately mentions core-foo
        open(os.path.join(d, "core-foo", "reviews", "2026-01-01-x.md"), "w").write("reviewed core-foo\n")

        hits = find_hits(d, "core-foo")
        # 1. word-boundary: the "core-foobar is its own skill" line must NOT count as a core-foo hit
        sk = hits.get(os.path.join("core-foobar", "SKILL.md"))
        if not sk or any("its own skill" in ln for _, ln in sk[1]):
            fails.append("word-boundary: core-foo matched inside core-foobar")
        # 2. the review file is HISTORY
        rv = hits.get(os.path.join("core-foo", "reviews", "2026-01-01-x.md"))
        if not rv or rv[0] != "HISTORY":
            fails.append("classification: review file not HISTORY")
        # 3. the tag-only skill.json is NOT-A-REF
        sj = hits.get(os.path.join("core-foobar", "skill.json"))
        if not sj or sj[0] != "NOT-A-REF":
            fails.append("tag-only skill.json not flagged NOT-A-REF")
        # 4. verify FAILS (a live ref — the SKILL.md peer line — exists)
        with contextlib.redirect_stdout(io.StringIO()):
            r_before = cmd_verify(d, "core-foo", as_json=True)
        if r_before == 0:
            fails.append("verify passed despite a live ref")
        # 5. after rewiring the live ref, a PROVENANCE mention in a live file is allowed:
        #    verify PASSES even though "core-foo" still appears (named as history, not wiring).
        open(os.path.join(d, "core-foobar", "SKILL.md"), "w").write(
            "peer: foo\nNote: absorbed from the former core-foo skill.\n"
            "unrelated: core-foobar is its own skill\n")
        with contextlib.redirect_stdout(io.StringIO()):
            r_after = cmd_verify(d, "core-foo", as_json=True)
        if r_after != 0:
            fails.append("verify failed on an allowed provenance mention ('former core-foo')")
    # 6. provenance vs dangling discrimination (the v0.3 fix) — direct on the classifier:
    if _is_dangling("absorbed from the former core-foo skill", "core-foo"):
        fails.append("provenance prose wrongly flagged dangling")
    if not _is_dangling('  "core-foo",  (now merged)', "core-foo"):
        fails.append("structural quoted token not flagged dangling despite a marker word")
    if not _is_dangling("see core-foo/SKILL.md for details", "core-foo"):
        fails.append("dead path ref not flagged dangling")
    if not _is_dangling("peer: core-foo", "core-foo"):
        fails.append("bare unmarked pointer not flagged dangling")
    if fails:
        print("SELFTEST FAIL:\n  - " + "\n  - ".join(fails), file=sys.stderr)
        return 1
    print("SELFTEST PASS — word-boundary, classification, tag-detection, and verify all correct.")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="refactor-scan.py", description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output (scan/verify)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("scan").add_argument("old")
    dr = sub.add_parser("dry-run"); dr.add_argument("old"); dr.add_argument("new")
    cb = sub.add_parser("check-backup")
    cb.add_argument("--since", type=float, default=0.0, help="epoch seconds; backup must be newer")
    cb.add_argument("--glob", default="~/.claude/*backup*.tgz",
                    help="backup tarball glob (default ~/.claude/*backup*.tgz)")
    sub.add_parser("verify").add_argument("old")
    sub.add_parser("selftest")
    args = ap.parse_args(argv)

    if args.cmd == "scan":
        return cmd_scan(ROOT, args.old, args.json)
    if args.cmd == "dry-run":
        return cmd_dry_run(ROOT, args.old, args.new)
    if args.cmd == "check-backup":
        return cmd_check_backup(args.since, args.glob)
    if args.cmd == "verify":
        return cmd_verify(ROOT, args.old, args.json)
    if args.cmd == "selftest":
        return cmd_selftest()
    return 2


if __name__ == "__main__":
    sys.exit(main())
