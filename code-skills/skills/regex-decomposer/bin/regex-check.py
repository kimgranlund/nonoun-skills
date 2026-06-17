#!/usr/bin/env python3
"""regex-check.py — the regex-decomposer MATCH gate. Self-contained (stdlib only).

The MATCH axis (B1 compiles · B2 matches the example set · B3 is safe) is mechanizable: a regex is an
executable matcher, and the example set is its contract. This tool reads a tiny pattern-spec card and
proves all three in one pass — so the worst LLM failures ("matches the examples, means the wrong
language" and "plausible pattern that won't run or ReDoS") become caught errors, not opinions.

  B1 Compiles  — `re.compile(pattern, flags)` in the target engine (Python `re` here)
  B2 Examples  — every `positives[]` string matches, every `negatives[]` string does NOT, under the
                 declared match MODE (`full` = fullmatch / anchored, `partial` = search / unanchored)
  B3 Safety    — a STATIC ReDoS-smell scan flags the catastrophic-backtracking constructs (nested
                 quantifiers, overlapping alternation under a quantifier, an unbounded `.*` pile-up)

A pattern-spec card (JSON):
  {
    "name":      "iso-date",
    "pattern":   "\\\\d{4}-\\\\d{2}-\\\\d{2}",
    "flags":     ["i"],              # optional: any of i m s x a u l  (re.I/M/S/X/A/U/L)
    "engine":    "python-re",        # advisory label — this tool runs Python `re`
    "mode":      "full",             # "full" (fullmatch) | "partial" (search). default: full
    "positives": ["2026-06-16"],     # MUST match
    "negatives": ["2026/06/16", ""]  # MUST NOT match
  }

  python3 bin/regex-check.py selftest          # good/bad fixtures: a passing spec, a missed positive,
                                               # a matched negative, and a ReDoS-smell pattern
  python3 bin/regex-check.py <spec.json>       # validate a card; report card; NONZERO on any failure

Python 3.8+.
"""
import json
import re
import sys

# --- flag letters -> re flags ------------------------------------------------------------------
FLAG_MAP = {
    "i": re.I, "m": re.M, "s": re.S, "x": re.X, "a": re.A, "u": re.U, "l": re.L,
}


def flags_of(letters):
    """Combine a list/str of single-letter flags into an `re` flag int. Raises ValueError on unknown."""
    bits = 0
    for ch in (letters or []):
        ch = ch.strip().lower()
        if not ch:
            continue
        if ch not in FLAG_MAP:
            raise ValueError("unknown flag %r (use any of %s)" % (ch, " ".join(sorted(FLAG_MAP))))
        bits |= FLAG_MAP[ch]
    return bits


# --- B1 compile / B2 examples ------------------------------------------------------------------
def compile_pattern(pattern, flag_bits):
    """B1: compile in the target engine. Returns (regex_or_None, error_str_or_None)."""
    try:
        return re.compile(pattern, flag_bits), None
    except re.error as e:
        return None, str(e)


def matches(rx, text, mode):
    """Does `text` match under the declared mode? full = fullmatch (anchored), partial = search."""
    if mode == "full":
        return rx.fullmatch(text) is not None
    return rx.search(text) is not None


def check_examples(rx, positives, negatives, mode):
    """B2: every positive must match, every negative must not. Returns a list of mismatch strings."""
    misses = []
    for s in positives:
        if not matches(rx, s, mode):
            misses.append("positive NOT matched (mode=%s): %r" % (mode, s))
    for s in negatives:
        if matches(rx, s, mode):
            misses.append("negative WRONGLY matched (mode=%s): %r — accidental over-match" % (mode, s))
    return misses


# --- B3 static ReDoS-smell scan ----------------------------------------------------------------
# Catastrophic backtracking comes from AMBIGUITY: more than one way for the engine to match the same
# input, multiplied across a quantifier. These three families cover the classic exponential/quadratic
# blowups. The scan is intentionally conservative (false positives over false negatives) — a flagged
# pattern needs an adversarial-input proof (see redos-and-safety.md), not an automatic reject.
_GROUP_OPEN = r"\((?:\?[:=!<][^)]*?|\?<[^>]+>|\?P<[^>]+>|\?P=[^)]+|\?#[^)]*|)"  # ( with optional (?: (?= (?<name> etc.

# 1. NESTED QUANTIFIER — a quantified atom inside a quantified group: (a+)+ , (\w*)* , (a{1,3})+
#    The inner and outer quantifier both span the same characters -> exponential paths.
_NESTED_QUANT = re.compile(
    r"\([^()]*[+*]\)[+*]"           # (….+….)+  or (….*….)*   — quantifier inside, quantifier outside
    r"|\([^()]*[+*]\)\{"            # (….+….){m,n}
    r"|\([^()]*\{\d+,?\d*\}[^()]*\)[+*{]"  # (….{m,n}….)+ — bounded inner, quantified outer
)

# 2. OVERLAPPING ALTERNATION under a quantifier — (a|a)* , (a|ab)* , (\d|\w)+ : branches that can
#    match the same text give the engine multiple equivalent paths per repetition.
_ALT_QUANT = re.compile(r"\([^()]*\|[^()]*\)[+*]|\([^()]*\|[^()]*\)\{\d*,\d*\}")

# 3. QUADRATIC `.*` PILE-UP — two or more unbounded greedy wildcards that can trade characters:
#    `.*.*` , `.*\s*.*` , `.+.+` . Each split point doubles the work.
_QUADRATIC = re.compile(r"(?:\.[*+]).{0,8}?(?:\.[*+])")


def _has_overlapping_alternation(group_body):
    """True if a `(a|b|…)` body has branches that can match the same first input (a real overlap)."""
    branches = group_body.split("|")
    if len(branches) < 2:
        return False
    # crude but effective: a branch that is a prefix of (or equal to) another, or two branches that
    # share an identical leading char class / literal, can both consume the same input.
    seen = []
    for b in branches:
        b = b.strip()
        for prev in seen:
            if b and prev and (b.startswith(prev) or prev.startswith(b) or b[0:1] == prev[0:1]):
                return True
        seen.append(b)
    return False


def redos_smells(pattern):
    """Static ReDoS-smell findings: a list of (kind, detail). Empty = no static smell found."""
    finds = []
    if _NESTED_QUANT.search(pattern):
        finds.append(("NESTED_QUANTIFIER",
                      "a quantified group wraps a quantified atom, e.g. (a+)+ / (\\w*)* — "
                      "exponential backtracking on a non-matching tail"))
    # overlapping alternation under a quantifier: find each (…|…)[+*{] and test the body for overlap
    for m in re.finditer(r"\(([^()]*\|[^()]*)\)\s*(?:[+*]|\{\d*,\d*\})", pattern):
        if _has_overlapping_alternation(m.group(1)):
            finds.append(("OVERLAPPING_ALTERNATION",
                          "a quantified alternation has branches that match the same input, e.g. "
                          "(a|ab)* / (\\d|\\w)+ — ambiguous paths multiply per repetition"))
            break
    if _QUADRATIC.search(pattern):
        finds.append(("QUADRATIC_WILDCARD",
                      "two or more unbounded greedy wildcards can trade characters, e.g. .*.* — "
                      "quadratic blow-up on long non-matching input"))
    return finds


# --- the card validator ------------------------------------------------------------------------
def validate_spec(spec):
    """Run B1/B2/B3 over one pattern-spec card. Returns (report_dict, fails:list, warns:list)."""
    fails, warns = [], []
    name = spec.get("name", "<spec>")
    pattern = spec.get("pattern")
    mode = spec.get("mode", "full")
    if not isinstance(spec, dict) or pattern is None:
        return {"name": name}, ["%s: card has no 'pattern'" % name], warns
    if mode not in ("full", "partial"):
        fails.append("%s: mode %r must be 'full' or 'partial'" % (name, mode))
        mode = "full"
    try:
        flag_bits = flags_of(spec.get("flags", []))
    except ValueError as e:
        fails.append("%s: %s" % (name, e))
        flag_bits = 0
    report = {"name": name, "mode": mode, "compiled": False,
              "positives": len(spec.get("positives", [])), "negatives": len(spec.get("negatives", [])),
              "example_misses": [], "smells": []}

    # B1 Compiles
    rx, err = compile_pattern(pattern, flag_bits)
    if rx is None:
        fails.append("%s: B1 WONT COMPILE — %s" % (name, err))
        # can't run examples on an uncompilable pattern; still run the static smell scan below
    else:
        report["compiled"] = True
        # B2 Examples
        misses = check_examples(rx, spec.get("positives", []), spec.get("negatives", []), mode)
        report["example_misses"] = misses
        for m in misses:
            fails.append("%s: B2 %s" % (name, m))
        if not spec.get("positives") and not spec.get("negatives"):
            warns.append("%s: B2 has no examples — the example set IS the contract; add positives + negatives"
                         % name)

    # B3 Safety (static smell scan — runs regardless of compile, on the raw pattern)
    smells = redos_smells(pattern)
    report["smells"] = smells
    for kind, detail in smells:
        fails.append("%s: B3 ReDoS-SMELL %s — %s (prove safe with an adversarial-input timing test)"
                     % (name, kind, detail))
    return report, fails, warns


# --- selftest fixtures -------------------------------------------------------------------------
SPEC_GOOD = {
    "name": "iso-date",
    "pattern": r"\d{4}-\d{2}-\d{2}",
    "mode": "full",
    "positives": ["2026-06-16", "1999-01-01"],
    "negatives": ["2026/06/16", "26-6-16", "", "2026-06-16 ", "x2026-06-16"],
}
SPEC_MISSES_POSITIVE = {
    # claims to match a dotted version too, but the pattern only allows '-' -> positive "1.2.3" is missed
    "name": "version",
    "pattern": r"\d+-\d+-\d+",
    "mode": "full",
    "positives": ["1-2-3", "1.2.3"],   # second positive is NOT matched -> B2 fail
    "negatives": ["abc"],
}
SPEC_MATCHES_NEGATIVE = {
    # the #1 silent over-match: unanchored 'partial' search means the negative "foo@bar" still
    # contains a matching substring -> the negative is WRONGLY matched
    "name": "loose-word",
    "pattern": r"\w+",
    "mode": "partial",
    "positives": ["hello"],
    "negatives": ["@@@", "foo@bar"],   # "foo@bar" contains \w+ -> wrongly matched -> B2 fail
}
SPEC_REDOS = {
    "name": "redos-email-ish",
    "pattern": r"^(\w+)+@\w+$",        # nested quantifier (\w+)+ -> catastrophic backtracking
    "mode": "full",
    "positives": ["a@b"],
    "negatives": ["nope"],
}


def selftest():
    errs = []

    # 1. the GOOD spec passes clean (compiles, examples match, no smell)
    rep, fails, warns = validate_spec(SPEC_GOOD)
    if fails:
        errs.append("good spec produced failures: %s" % fails)
    if not rep["compiled"]:
        errs.append("good spec did not compile")

    # 2. a MISSED POSITIVE is a B2 failure
    _, fails, _ = validate_spec(SPEC_MISSES_POSITIVE)
    if not any("B2" in f and "positive NOT matched" in f for f in fails):
        errs.append("missed-positive spec was not flagged: %s" % fails)

    # 3. a MATCHED NEGATIVE is a B2 failure (the over-match)
    _, fails, _ = validate_spec(SPEC_MATCHES_NEGATIVE)
    if not any("B2" in f and "negative WRONGLY matched" in f for f in fails):
        errs.append("matched-negative spec was not flagged: %s" % fails)

    # 4. a ReDoS-smell pattern is a B3 failure with the NESTED_QUANTIFIER kind
    _, fails, _ = validate_spec(SPEC_REDOS)
    if not any("NESTED_QUANTIFIER" in f for f in fails):
        errs.append("ReDoS nested-quantifier spec was not flagged: %s" % fails)

    # 5. the smell scan recognizes each family and stays quiet on safe patterns
    if not any(k == "NESTED_QUANTIFIER" for k, _ in redos_smells(r"(a*)*")):
        errs.append("redos_smells missed (a*)*")
    if not any(k == "OVERLAPPING_ALTERNATION" for k, _ in redos_smells(r"(a|ab)*")):
        errs.append("redos_smells missed (a|ab)* overlapping alternation")
    if not any(k == "QUADRATIC_WILDCARD" for k, _ in redos_smells(r".*.*x")):
        errs.append("redos_smells missed .*.* quadratic wildcard")
    for safe in (r"\d{4}-\d{2}-\d{2}", r"[a-z]+@[a-z]+\.[a-z]+", r"(?:abc|def)g", r"a+b+c+"):
        if redos_smells(safe):
            errs.append("redos_smells false-positive on safe pattern %r: %s" % (safe, redos_smells(safe)))

    # 6. flags_of parses + rejects
    if flags_of(["i", "m"]) != (re.I | re.M):
        errs.append("flags_of i,m wrong")
    try:
        flags_of(["z"])
        errs.append("flags_of accepted unknown flag")
    except ValueError:
        pass

    # 7. mode semantics: fullmatch vs search
    rx, _ = compile_pattern(r"\d+", 0)
    if matches(rx, "a12b", "full"):
        errs.append("full mode should not match 'a12b' against \\d+")
    if not matches(rx, "a12b", "partial"):
        errs.append("partial mode should find \\d+ in 'a12b'")
    return errs


def _print_card(report):
    print("MATCH report card — %s" % report["name"])
    print("  B1 compile : %s" % ("ok" if report["compiled"] else "FAILED"))
    print("  B2 examples: mode=%s  positives=%d  negatives=%d  misses=%d"
          % (report["mode"], report["positives"], report["negatives"], len(report["example_misses"])))
    for m in report["example_misses"]:
        print("       ✗ %s" % m)
    print("  B3 safety  : %s" % ("clean" if not report["smells"] else "%d smell(s)" % len(report["smells"])))
    for kind, detail in report["smells"]:
        print("       ⚠ %s — %s" % (kind, detail))


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("regex-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("regex-check: OK — compile + example-set (full/partial) + ReDoS-smell scan verified "
              "over good/bad fixtures")
        return 0
    try:
        doc = json.load(open(argv[0], encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write("regex-check: bad spec — %s\n" % e)
        return 2
    specs = doc if isinstance(doc, list) else [doc]
    all_fails, all_warns = [], []
    for spec in specs:
        report, fails, warns = validate_spec(spec)
        _print_card(report)
        all_fails += fails
        all_warns += warns
    for w in all_warns:
        print("  ⚠ %s" % w)
    if all_fails:
        sys.stderr.write("regex-check: FAIL (%d issue(s))\n" % len(all_fails))
        for f in all_fails:
            sys.stderr.write("  - %s\n" % f)
        return 1
    print("regex-check: PASS — %d spec(s): compile + examples + safety clean" % len(specs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
