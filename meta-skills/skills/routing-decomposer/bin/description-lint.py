#!/usr/bin/env python3
"""description-lint.py — the routing-decomposer static description linter. Self-contained (stdlib only).

The routing eval (`routing-eval.py`) measures a description's precision/recall against a corpus. This
linter is the cheap STATIC pre-filter: before you spend a corpus on it, it checks the description has
the structural ingredients a routable description needs — the WHAT + WHEN + NOT-for shape the repo's
contract asks for — and flags the wording that reliably mis-routes (first-person voice, vagueness
words, no concrete trigger phrases). These are A-axis (INSTRUCTION) signals: a card that fails them
will almost always score badly on the eval too, so fix them first.

It parses the YAML frontmatter `description` (folded `>` block or inline), reconstructs it the same
way the repo gate does, and reports FAILs (hard contract / missing routing ingredient) and WARNs
(wording smells).

Checks:
  FAIL  description missing / > 1024 chars (the hard routing budget)
  FAIL  no WHAT signal      — no capability verb (decompose/grade/score/audit/design/build/...)
  FAIL  no WHEN/trigger signal — no "Triggers on" / "Use when" / quoted trigger phrases
  FAIL  fewer than N quoted concrete trigger phrases (default 3)
  WARN  no NOT-for fence    — no "NOT for" / "Does NOT" boundary that fences siblings
  WARN  first-person voice  — "I will", "we", "my skill" (a description is about the request, not the author)
  WARN  vagueness words     — "various", "powerful", "comprehensive", "etc.", "and more", "things", ...

  python3 bin/description-lint.py selftest
  python3 bin/description-lint.py <SKILL.md> [--min-triggers 3]

Python 3.8+.
"""
import os
import re
import sys

CAPABILITY_VERBS = (
    "decompose", "grade", "score", "audit", "design", "build", "generate", "create", "evaluate",
    "review", "analyze", "analyse", "measure", "convert", "extract", "author", "optimize", "optimise",
    "diagnose", "debug", "refactor", "plan", "compose", "verify", "check", "lint", "map", "produce",
    "render", "assess", "critique", "fix", "improve", "scaffold", "document", "model", "translate",
)
WHEN_MARKERS = ("trigger", "use when", "use this", "use whenever", "invoke", "reach for", "apply when")
NOT_MARKERS = ("not for", "not when", "does not", "doesn't", "do not trigger", "don't trigger", "never for")
VAGUE = (
    "various", "powerful", "comprehensive", "robust", "seamless", "flexible", "advanced",
    "cutting-edge", "state-of-the-art", "things", "stuff", "etc", "and more", "and so on",
    "all kinds", "any kind", "wide range", "world-class", "best-in-class", "leverage", "utilize",
)
FIRST_PERSON = (r"\bi will\b", r"\bi can\b", r"\bi'll\b", r"\bi'm\b", r"\bmy skill\b", r"\bwe will\b",
                r"\bwe can\b", r"\blet me\b", r"\ballows you to\b", r"\benables you to\b")


def extract_description(skill_md_text):
    """Same reconstruction the repo gate uses: folded `>` block joined to one line, or inline."""
    m = re.search(r"(?ms)^---\n(.*?)\n---", skill_md_text)
    if not m:
        return None
    fm = m.group(1)
    block = re.search(r"(?ms)^description:\s*>\s*\n((?:[ \t]+.*\n?)+)", fm)
    if block:
        return " ".join(l.strip() for l in block.group(1).splitlines() if l.strip())
    inline = re.search(r"(?m)^description:\s*(.+)$", fm)
    return inline.group(1).strip() if inline else None


def quoted_triggers(desc):
    """Concrete trigger phrases: anything in double quotes, or comma-separated items after a
    'Triggers on:' / 'Triggers include' marker (the two shapes real descriptions use)."""
    quoted = re.findall(r'"([^"]{3,})"', desc)
    if quoted:
        return [q.strip() for q in quoted if q.strip()]
    # marker-introduced list: "Triggers on: a, b, c. NOT for ..."
    mk = re.search(r"(?is)(?:triggers?\s+(?:on|include[s]?)|use when)\s*[:\-]?\s*(.+?)(?:\.\s+(?:not for|does not|do not)|$)", desc)
    if mk:
        chunk = mk.group(1)
        parts = re.split(r"[;,]| or | and ", chunk)
        return [p.strip(" .") for p in parts if len(p.strip(" .").split()) >= 2]
    return []


def _unquoted(desc):
    """The description with quoted trigger phrases removed — a quoted phrase is the USER's request
    wording, so first-person / vagueness inside it is not the author's voice and must not be flagged."""
    return re.sub(r'"[^"]*"', " ", desc)


def lint(desc, min_triggers=3):
    """Return (fails, warns) for a reconstructed description string."""
    fails, warns = [], []
    low = desc.lower()
    prose = _unquoted(desc).lower()   # author's own words, with user-quoted triggers stripped

    if len(desc) > 1024:
        fails.append("description is %d chars (> 1024 routing budget)" % len(desc))

    if not any(v in low for v in CAPABILITY_VERBS):
        fails.append("no WHAT signal — names no capability verb "
                     "(decompose/grade/score/audit/design/build/…); the model can't tell what it does")

    has_when = any(mk in low for mk in WHEN_MARKERS) or bool(re.search(r'"[^"]{3,}"', desc))
    if not has_when:
        fails.append("no WHEN/trigger signal — no 'Triggers on' / 'Use when' marker and no quoted "
                     "trigger phrases; the model has nothing to match a request against")

    triggers = quoted_triggers(desc)
    if len(triggers) < min_triggers:
        fails.append("only %d concrete trigger phrase(s) (need >= %d) — one phrasing under-triggers; "
                     "cover the real invocation space" % (len(triggers), min_triggers))

    if not any(mk in low for mk in NOT_MARKERS):
        warns.append("no NOT-for fence — add an explicit 'NOT for …' that names the sibling(s) this "
                     "could be confused with, or it will over-trigger onto their territory")

    for pat in FIRST_PERSON:
        if re.search(pat, prose):
            warns.append("first-person / author voice (%s) — a description is about the request, "
                         "not the author; write WHAT + WHEN, not 'I will'" % pat.strip(r"\b"))
            break

    hit_vague = [v for v in VAGUE if re.search(r"\b%s\b" % re.escape(v), prose)]
    if hit_vague:
        warns.append("vagueness words carry no routing signal: %s — replace with concrete capability "
                     "+ trigger phrases" % ", ".join(sorted(set(hit_vague))))
    return fails, warns


# --- selftest fixtures -------------------------------------------------------------------------
GOOD_MD = '''---
name: routing-decomposer
description: >
  Grade and decompose the routing surface of a skill — its frontmatter description — measuring
  whether it fires on the right requests and holds against the wrong ones. Triggers on: "grade this
  description", "is my skill routing correctly", "why does my skill never fire", "this skill
  over-triggers", "score the precision and recall of this description", "build a routing corpus".
  NOT for authoring a whole skill end to end (skills-studio).
---
# body
'''
# Bad: first person, vague, no NOT-for, no concrete quoted triggers, no trigger marker.
BAD_MD = '''---
name: vague-skill
description: >
  I will help you with various powerful and comprehensive tasks. My skill leverages cutting-edge
  techniques to handle all kinds of things and more for you, seamlessly and robustly.
---
# body
'''
# Bad: over the 1024 budget.
LONG_DESC = "Grade this. " + ('"do a thing" ' * 3) + ("Triggers on stuff. " * 120)
LONG_MD = "---\nname: x\ndescription: >\n" + "".join("  %s\n" % w for w in [LONG_DESC]) + "---\n"


def selftest():
    errs = []
    # 1. extraction round-trips the folded block to the same string the repo gate builds
    d = extract_description(GOOD_MD)
    if not d or "Triggers on" not in d or len(d) > 1024:
        errs.append("extraction wrong: %r" % (d and d[:60]))

    # 2. the GOOD description passes clean (no fails)
    gf, gw = lint(d)
    if gf:
        errs.append("GOOD description produced fails: %s" % gf)
    # GOOD quotes "is my skill routing correctly" — "my skill" is the USER's wording, not author
    # voice, so the first-person warn must NOT fire on a quoted trigger.
    if any("first-person" in w for w in gw):
        errs.append("GOOD: first-person warn falsely fired on a quoted trigger phrase: %s" % gw)

    # 3. the BAD description trips the wording fails + warns
    bd = extract_description(BAD_MD)
    bf, bw = lint(bd)
    if not any("WHEN" in f or "trigger" in f.lower() for f in bf):
        errs.append("BAD: missing-trigger fail not raised: %s" % bf)
    if not any("concrete trigger" in f for f in bf):
        errs.append("BAD: too-few-triggers fail not raised: %s" % bf)
    if not any("NOT-for" in w for w in bw):
        errs.append("BAD: missing NOT-for warn not raised: %s" % bw)
    if not any("first-person" in w for w in bw):
        errs.append("BAD: first-person warn not raised: %s" % bw)
    if not any("vagueness" in w for w in bw):
        errs.append("BAD: vagueness warn not raised: %s" % bw)

    # 4. the over-budget description trips the length fail
    ld = extract_description(LONG_MD)
    lf, _ = lint(ld)
    if not any("1024" in f for f in lf):
        errs.append("over-budget description not flagged (len=%s): %s" % (ld and len(ld), lf))

    # 5. quoted_triggers reads both shapes (quoted, and marker-list)
    q = quoted_triggers('Triggers on: "grade this", "score that", "fix the other"')
    if len(q) != 3:
        errs.append("quoted_triggers (quoted) wrong: %s" % q)
    ml = quoted_triggers("Use when you want to grade a description, score the routing, build a corpus.")
    if len(ml) < 2:
        errs.append("quoted_triggers (marker-list) wrong: %s" % ml)
    return errs


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("description-lint: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("description-lint: OK — extraction + WHAT/WHEN/NOT + trigger-count + smell checks verified")
        return 0
    min_triggers = int(argv[argv.index("--min-triggers") + 1]) if "--min-triggers" in argv else 3
    path = argv[0]
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        sys.stderr.write("description-lint: cannot read %s (%s)\n" % (path, e))
        return 2
    desc = extract_description(text)
    if not desc:
        sys.stderr.write("description-lint: no frontmatter `description` found in %s\n" % path)
        return 2
    fails, warns = lint(desc, min_triggers)
    print("description-lint — %d chars, %d concrete trigger phrase(s)"
          % (len(desc), len(quoted_triggers(desc))))
    for w in warns:
        print("  ⚠ %s" % w)
    if fails:
        sys.stderr.write("description-lint: FAIL (%d)\n" % len(fails))
        for f in fails:
            sys.stderr.write("  - %s\n" % f)
        return 1
    print("description-lint: OK — WHAT + WHEN + concrete triggers present, within budget")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
