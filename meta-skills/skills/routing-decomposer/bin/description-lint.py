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
# Fence markers must be matched at a CLAUSE boundary, not anywhere in prose: "not for the faint of
# heart" is idiom, not a NOT-for fence. A real fence opens a clause — it follows sentence start or a
# clause separator (. ; , : — | or a newline) — so we anchor each marker to one of those.
NOT_MARKERS = ("not for", "not when", "does not", "doesn't", "do not trigger", "don't trigger", "never for")
_FENCE_PATTERNS = tuple(
    re.compile(r"(?im)(?:^|[.;:,—|]|\n)\s*%s\b" % re.escape(mk)) for mk in NOT_MARKERS
)


def has_fence(desc):
    """True iff the description carries a NOT-for fence at a CLAUSE boundary (not idiom in prose)."""
    return any(p.search(desc) for p in _FENCE_PATTERNS)


def found_capability_verbs(desc):
    """Capability verbs present as a WHOLE WORD or a normal inflection (grade/grades/grading/graded),
    but NOT as a coincidental prefix of an unrelated word ('plan' must not match 'planetary',
    'map' must not match 'mapping a galaxy'… 'mapping' IS allowed since it's the verb inflected).
    We bound each verb with \\b on both sides, allowing only the common verb suffixes between."""
    low = desc.lower()
    hits = []
    for v in CAPABILITY_VERBS:
        # verb + optional inflection (s, es, d, ed, ing) + word boundary — 'plan\b' won't hit 'planetary'
        if re.search(r"\b%s(?:e?s|e?d|ing|)\b" % re.escape(v), low):
            hits.append(v)
    return hits


def has_capability_verb(desc):
    return bool(found_capability_verbs(desc))
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


# A quoted phrase is only a CONCRETE trigger if it gives the classifier something to land on. A vague
# category ("various things", "routing tasks", "all kinds of stuff") is not a landing point — it's the
# same filler the VAGUE list flags, just in quotes. We reject a quoted phrase that is purely vague:
# it carries no content word beyond a vague category term.
_VAGUE_CATEGORY = (
    "various", "things", "stuff", "tasks", "items", "kinds", "all kinds", "any kind", "anything",
    "everything", "and more", "etc", "and so on", "wide range", "miscellaneous", "general",
)


def _is_concrete_trigger(phrase):
    """A trigger phrase is CONCRETE if it names a real request the classifier can land on — not a
    vague category. Rejected: < 2 words; or a phrase whose only content is a vague-category term
    ('various things'); or a bare noun-category with no action signal ('routing tasks', 'all kinds of
    stuff'). Accepted: a phrase with a capability verb ('grade this description') or a demonstrative
    pointing at a concrete object ('this description — does it over-trigger')."""
    p = phrase.strip(" .").lower()
    words = re.findall(r"[a-z0-9'-]+", p)
    if len(words) < 2:
        return False
    vague_words = set()
    for cat in _VAGUE_CATEGORY:
        if " " in cat:
            if cat in p:
                vague_words.update(cat.split())
        elif cat in words:
            vague_words.add(cat)
    filler = {"the", "a", "an", "this", "that", "my", "your", "of", "to", "for", "on", "in", "and",
              "or", "with", "some", "any", "do", "it"}
    content = [w for w in words if w not in vague_words and w not in filler]
    if not content:
        return False  # only vague terms + filler — pure category, no landing point
    # A phrase whose content words include a vague-category head and NO action signal (no capability
    # verb, no demonstrative pointing at an object) is a bare category like "routing tasks" — reject.
    has_action = has_capability_verb(p) or bool(re.search(r"\b(this|these|my|your)\b", p))
    if vague_words and not has_action:
        return False
    return True


def quoted_triggers(desc):
    """Concrete trigger phrases: anything in double quotes, or comma-separated items after a
    'Triggers on:' / 'Triggers include' marker (the two shapes real descriptions use). Vague-category
    quotes ('various things', 'routing tasks') are rejected — a category is not a landing point."""
    quoted = re.findall(r'"([^"]{3,})"', desc)
    if quoted:
        return [q.strip() for q in quoted if q.strip() and _is_concrete_trigger(q)]
    # marker-introduced list: "Triggers on: a, b, c. NOT for ..."
    mk = re.search(r"(?is)(?:triggers?\s+(?:on|include[s]?)|use when)\s*[:\-]?\s*(.+?)(?:\.\s+(?:not for|does not|do not)|$)", desc)
    if mk:
        chunk = mk.group(1)
        parts = re.split(r"[;,]| or | and ", chunk)
        return [p.strip(" .") for p in parts if _is_concrete_trigger(p)]
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

    if not has_capability_verb(desc):
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

    if not has_fence(desc):
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

# --- minor-fix fixtures ------------------------------------------------------------------------
# m1: a description with NO real fence but the idiom "not for the faint of heart" in prose. The old
# substring check saw "not for" and SUPPRESSED the missing-fence warn. The clause-boundary check must
# still raise it (the idiom is mid-clause, not at a clause opening).
IDIOM_NO_FENCE_MD = '''---
name: idiom-skill
description: >
  Grade and decompose a skill's frontmatter description — routing work not for the faint of heart.
  Triggers on: "grade this description", "score the routing", "build a routing corpus".
---
# body
'''
# m2: a description whose ONLY 'verb-looking' token is 'planetary' (contains 'plan'). The old
# substring check saw 'plan' and PASSED the WHAT gate; whole-word detection must FAIL it.
PLAN_SUBSTRING_MD = '''---
name: astro-skill
description: >
  A planetary catalogue of frontmatter metadata for interstellar discoverability.
  Triggers on: "list the planets", "show the catalogue", "open the atlas".
---
# body
'''
# m3: a description whose quoted "triggers" are vague categories ("various things", "routing tasks",
# "all kinds of stuff"). The old quote-counter counted them as concrete; they must NOT count, so the
# too-few-concrete-triggers fail must fire.
VAGUE_QUOTES_MD = '''---
name: vague-quotes-skill
description: >
  Grade a skill's frontmatter description for routing. Triggers on: "various things", "routing tasks",
  "all kinds of stuff".
---
# body
'''


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

    # 6. m1 — the prose idiom "not for the faint of heart" must NOT suppress the missing-fence warn
    #    (it is mid-clause, not a clause-opening NOT-for fence).
    if has_fence("routing work not for the faint of heart"):
        errs.append("m1: idiom 'not for the faint of heart' wrongly counted as a fence")
    if not has_fence("Grade the description. NOT for authoring a whole skill (skills-studio)."):
        errs.append("m1: a real clause-opening 'NOT for …' fence was not detected")
    im = extract_description(IDIOM_NO_FENCE_MD)
    _, iw = lint(im)
    if not any("NOT-for" in w for w in iw):
        errs.append("m1: idiom-only description did not raise the missing-fence warn: %s" % iw)

    # 7. m2 — capability-verb detection is whole-word: 'planetary' must NOT satisfy the WHAT gate via
    #    the substring 'plan', so the no-WHAT fail must fire.
    if has_capability_verb("a planetary catalogue of interstellar metadata"):
        errs.append("m2: 'planetary' wrongly matched the capability verb 'plan' (substring bug)")
    if not has_capability_verb("we will plan the migration"):
        errs.append("m2: the real verb 'plan' (whole word) was not detected")
    if not has_capability_verb("grades and scores the routing"):  # inflections still match
        errs.append("m2: inflected verbs 'grades'/'scores' not detected")
    pm = extract_description(PLAN_SUBSTRING_MD)
    pf, _ = lint(pm)
    if not any("WHAT" in f for f in pf):
        errs.append("m2: 'planetary'-only description did not raise the no-WHAT fail: %s" % pf)

    # 8. m3 — vague-category quotes are not concrete triggers; the too-few-triggers fail must fire.
    if _is_concrete_trigger("various things") or _is_concrete_trigger("routing tasks"):
        errs.append("m3: a vague-category quote was wrongly counted as a concrete trigger")
    if not _is_concrete_trigger("grade this description"):
        errs.append("m3: a genuinely concrete trigger was wrongly rejected")
    vq = extract_description(VAGUE_QUOTES_MD)
    if len(quoted_triggers(vq)) >= 3:
        errs.append("m3: vague-category quotes counted toward the concrete-trigger total: %s"
                    % quoted_triggers(vq))
    vf, _ = lint(vq)
    if not any("concrete trigger" in f for f in vf):
        errs.append("m3: vague-quotes description did not raise the too-few-concrete-triggers fail: %s" % vf)
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
