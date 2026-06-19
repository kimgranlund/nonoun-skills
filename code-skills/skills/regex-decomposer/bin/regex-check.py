#!/usr/bin/env python3
"""regex-check.py — the regex-decomposer MATCH gate. Self-contained (stdlib only).

The MATCH axis (B1 compiles · B2 matches the example set · B3 is safe) is mechanizable: a regex is an
executable matcher, and the example set is its contract. This tool reads a tiny pattern-spec card and
proves all three in one pass — so the worst LLM failures ("matches the examples, means the wrong
language" and "plausible pattern that won't run or ReDoS") become caught errors, not opinions.

  B1 Compiles  — `re.compile(pattern, flags)` in the target engine (Python `re` here)
  B2 Examples  — every `positives[]` string matches, every `negatives[]` string does NOT, under the
                 declared match MODE (`full` = fullmatch / anchored, `partial` = search / unanchored)
  B3 Safety    — a STATIC ReDoS-smell scan over the regex's REAL parse tree (Python's stdlib
                 `sre_parse` / `re._parser`) flags the catastrophic-backtracking constructs: a nested
                 quantifier (star height >= 2 — a repeat whose body holds another repeat, incl. bounded
                 {m,n} outer repeats like (.*a){10}), an overlapping alternation under a quantifier
                 ((a|ab)*), or two consecutive unbounded repeats over overlapping content (.*.*). The
                 structural detection is PRECISE — it walks the AST, not a regex-on-regex heuristic —
                 but it is still a PRE-FILTER, not a proof for exotic cases: confirm a flagged pattern
                 with an adversarial-input timing test, by hand.

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
  python3 bin/regex-check.py [--json] <spec.json>   # machine-readable report

`--json` (additive reporting flag; parse-anywhere in argv) prints ONE machine-readable report object to
stdout and NOTHING else there — the shared schema every lint bin emits:
  {"tool": "regex-check", "ok": <bool>, "summary": "<one line>",
   "findings": [{"kind", "severity": fail|advisory, "location": "<spec name | null>", "message"}, ...]}
`ok` is true iff no FAIL (the exact condition that gives exit 0 in human mode). A blocking finding
(B1 won't-compile, a B2 example miss, a B3 ReDoS smell) maps to severity `fail`; an advisory warn
(no example set) to `advisory`. `location` is the spec's name (a regex card has no line). The exit code
is UNCHANGED by --json. Without --json, output + exit are byte-identical.

Python 3.8+.
"""
import json
import re
import sys

# Python's stdlib regex parser. It moved under `re._parser` in 3.11; `sre_parse` is the <=3.10 home
# (and a deprecated shim in 3.11+). We want the parser wherever it lives, stdlib-only, 3.8–3.13.
try:
    from re import _parser as sre_parse  # 3.11+
except ImportError:  # pragma: no cover - exercised on <=3.10
    import sre_parse  # type: ignore

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


# --- B3 static ReDoS-smell scan (AST-based) ----------------------------------------------------
# Catastrophic backtracking comes from AMBIGUITY: more than one way for the engine to match the same
# input, multiplied across a quantifier. We detect it on the regex's REAL parse tree — Python's stdlib
# `sre_parse.parse(pattern, flags)` returns a SubPattern, an iterable of (opcode, args) tuples — so the
# analysis is STRUCTURAL, not a regex-on-regex heuristic. Opcodes seen here (matched by NAME so we
# never hard-code the engine's numeric values):
#   MAX_REPEAT / MIN_REPEAT  args = (min, max, SubPattern)      a quantified body
#   BRANCH                   args = (None, [SubPattern, ...])   an alternation (a|b|…)
#   SUBPATTERN               args = (group, addflags, delflags, SubPattern)   a (…) group
#   IN / LITERAL / NOT_LITERAL / ANY / CATEGORY / RANGE / AT …  leaf-ish atoms
#
# Note `sre_parse` factors a common prefix out of an alternation: `(a|ab)` parses to
# LITERAL('a') + BRANCH([ [], [LITERAL('b')] ]) and `(a|a)` to LITERAL('a') + BRANCH([ [], [] ]) —
# so an EMPTY BRANCH ARM is the precise signal that one alternative was a prefix of another (the real
# overlap). And `(a|b|c)` is optimized into a single IN char class (no BRANCH at all), which is why a
# mutually-exclusive single-char alternation never trips the overlap check.
#
# Detection is PRECISE for the targeted families (star height, prefix-overlap, twin unbounded repeats)
# — but it remains a PRE-FILTER, not a decision procedure for every exotic blow-up. A clean scan is
# necessary, not sufficient; confirm any catastrophic suspicion with a manual timing test, and never
# treat a clean result as a safety proof.


def _op_name(op):
    """An opcode's name, robustly: `op.name` if it's an enum, else `str(op)`."""
    return getattr(op, "name", None) or str(op)


def _is_repeat(name):
    return name in ("MAX_REPEAT", "MIN_REPEAT", "POSSESSIVE_REPEAT")


def _iter_subpatterns(args, name):
    """Yield the child SubPattern(s) reachable from a node's args, by opcode name.

    A SubPattern is itself iterable; SUBPATTERN nests one in args[3]; BRANCH holds a list in args[1];
    a REPEAT holds its body in args[2]. Everything else is a leaf (no sub-pattern to descend into).
    """
    if _is_repeat(name):
        yield args[2]
    elif name == "SUBPATTERN":
        yield args[3]
    elif name == "BRANCH":
        for arm in args[1]:
            yield arm


def _contains_repeat(subpattern):
    """True if `subpattern` contains a REPEAT anywhere in its subtree (its own star height >= 1).

    Descends through SUBPATTERN / BRANCH / concatenation — so the inner repeat in (a+), (.*a),
    ([^,]*,) , (a?) is found regardless of the wrapping group/alternation around it.
    """
    for op, args in subpattern:
        name = _op_name(op)
        if _is_repeat(name):
            return True
        for child in _iter_subpatterns(args, name):
            if _contains_repeat(child):
                return True
    return False


def _arm_tokens(arm):
    """A normalized, comparable token list for a branch arm (opcode-name + args repr per element)."""
    return [(_op_name(op), repr(args)) for op, args in arm]


def _branch_arms_overlap(arms):
    """True if two arms of a BRANCH can match the same leading input (a real, conservative overlap).

    The genuine overlap is "one alternative is a (possibly equal) PREFIX of another" — `(a|ab)`,
    `(a|a)` — so both can consume the same leading input, multiplying paths per repetition. Two
    precise, conservative signals (no first-char heuristic, which would over-flag mutually-exclusive
    arms like bar|baz that share only their first character):
      1. An EMPTY arm. `sre_parse` factors the shared leading prefix out of an alternation, so
         `(a|ab)` parses to LITERAL('a') + BRANCH([ [], [LITERAL('b')] ]) and `(a|a)` to
         LITERAL('a') + BRANCH([ [], [] ]). An empty arm is therefore the exact fingerprint of one
         alternative being a strict prefix of another.
      2. One arm's full token sequence is a prefix of another's (covers any arm the parser did not
         factor) — `bar` vs `baz` is NOT a prefix (they diverge at the 3rd token), so it stays clean.
    """
    toks = [_arm_tokens(arm) for arm in arms]
    if any(len(t) == 0 for t in toks):
        return True
    for i in range(len(toks)):
        for j in range(len(toks)):
            if i != j and toks[i] == toks[j][:len(toks[i])]:
                return True
    return False


def _find_overlap_branch(subpattern):
    """True if `subpattern` contains, anywhere, a BRANCH whose arms overlap (see _branch_arms_overlap)."""
    for op, args in subpattern:
        name = _op_name(op)
        if name == "BRANCH" and _branch_arms_overlap(args[1]):
            return True
        for child in _iter_subpatterns(args, name):
            if _find_overlap_branch(child):
                return True
    return False


def _is_unbounded_repeat(op, args):
    """True for a `*`/`+`/`{m,}` repeat — one whose upper bound is open (MAXREPEAT)."""
    return _is_repeat(_op_name(op)) and args[1] == getattr(sre_parse, "MAXREPEAT", None)


def _repeat_body_can_overlap(args_a, args_b):
    """Conservative: can two sibling unbounded repeats compete for the same characters?

    True when either body is an ANY (`.`) — `.*` swallows anything, so `.*.*`, `.*\\w*` always overlap —
    or when the two bodies are structurally identical (`\\w*\\w*`, `a*a*`). Distinct concrete classes
    that cannot share a character (`\\d*\\D*`) are NOT flagged.
    """
    body_a, body_b = list(args_a[2]), list(args_b[2])
    if any(_op_name(op) == "ANY" for op, _ in body_a + body_b):
        return True
    norm = lambda body: [(_op_name(op), repr(a)) for op, a in body]
    return norm(body_a) == norm(body_b)


def _walk_for_smells(subpattern, finds):
    """Recurse `subpattern`, appending (kind, detail) findings. De-dups by kind in `redos_smells`."""
    items = list(subpattern)

    # 3. QUADRATIC — two consecutive unbounded repeats over overlapping content at the SAME level.
    for i in range(len(items) - 1):
        op_a, args_a = items[i]
        op_b, args_b = items[i + 1]
        if (_is_unbounded_repeat(op_a, args_a) and _is_unbounded_repeat(op_b, args_b)
                and _repeat_body_can_overlap(args_a, args_b)):
            finds.append(("QUADRATIC_WILDCARD",
                          "two consecutive unbounded greedy repeats can trade characters, e.g. .*.* / "
                          "\\w*\\w* — quadratic blow-up on long non-matching input"))

    for op, args in items:
        name = _op_name(op)
        if _is_repeat(name):
            body = args[2]
            # 1. NESTED_QUANTIFIER — star height >= 2: a repeat whose body holds another repeat
            #    (directly or through SUBPATTERN / BRANCH). Bounded {m,n} outer repeats count too.
            if _contains_repeat(body):
                finds.append(("NESTED_QUANTIFIER",
                              "a quantified group wraps another quantifier (star height >= 2), e.g. "
                              "(a+)+ / (\\w*)* / (.*a){10} / ([^,]*,){20} — exponential or polynomial "
                              "backtracking on a non-matching tail"))
            # 2. OVERLAPPING_ALTERNATION — a repeat whose body holds a BRANCH with overlapping arms.
            if _find_overlap_branch(body):
                finds.append(("OVERLAPPING_ALTERNATION",
                              "a quantified alternation has branches where one is a prefix of another, "
                              "e.g. (a|ab)* / (a|a)* — ambiguous paths multiply per repetition"))
        # descend into every child sub-pattern (group body, branch arm, repeat body)
        for child in _iter_subpatterns(args, name):
            _walk_for_smells(child, finds)


def redos_smells(pattern, flag_bits=0):
    """Static ReDoS-smell findings over the regex's parse tree: a list of (kind, detail), de-duped.

    AST-based and PRECISE for the targeted families (nested quantifier / overlapping alternation /
    quadratic twin-repeat) — but still a PRE-FILTER, not a decision procedure: confirm a catastrophic
    suspicion with a manual timing test (see redos-and-safety.md). A flag is a B3 gate failure until
    cleared by that test or a rewrite. A pattern that does not parse raises re.error (a B1 finding) —
    callers handle that; this function presumes a parseable pattern.
    """
    tree = sre_parse.parse(pattern, flag_bits)
    finds = []
    _walk_for_smells(tree, finds)
    # de-dup by kind, preserving first-seen order
    seen, out = set(), []
    for kind, detail in finds:
        if kind not in seen:
            seen.add(kind)
            out.append((kind, detail))
    return out


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
        # A pattern that won't compile won't parse either — there is no AST to analyze, so a
        # parse/compile failure is a B1 finding, NOT a ReDoS verdict (per the contract).
        fails.append("%s: B1 WONT COMPILE — %s" % (name, err))
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

        # B3 Safety — AST-based structural smell scan over the parse tree (needs a parseable pattern)
        smells = redos_smells(pattern, flag_bits)
        report["smells"] = smells
        for kind, detail in smells:
            fails.append("%s: B3 ReDoS-SMELL %s — %s (clear by a MANUAL adversarial-input timing test — "
                         "this tool does NOT run one — or a rewrite)" % (name, kind, detail))
    return report, fails, warns


# --- machine-readable report (--json) ----------------------------------------------------------
# ONE shared schema across every lint bin: {tool, ok, summary, findings:[{kind, severity, location,
# message}]}. `ok` is true iff no blocking finding (the same condition that gives exit 0 in human mode).
# Printed via json.dumps(indent=2); nothing else goes to stdout under --json.
def _report_json(tool, ok, summary, findings):
    """Emit the shared report object to stdout (and nothing else). `findings` is a list of dicts already
    in {kind, severity, location, message} shape. Returns the dict so callers/selftests can reuse it."""
    report = {"tool": tool, "ok": ok, "summary": summary, "findings": findings}
    print(json.dumps(report, indent=2))
    return report


def build_report(specs):
    """Build the JSON report over one or more pattern-spec cards. A blocking finding (B1 won't-compile,
    a B2 example miss, a B3 ReDoS smell) maps to severity `fail`; an advisory warn (no example set) to
    `advisory`. `ok` is true iff no fail — the exact exit-0 condition of `main`. `location` is the
    spec's name (a regex card has no line number)."""
    out, blocking = [], 0
    for spec in specs:
        report, fails, warns = validate_spec(spec)
        name = report.get("name", "<spec>")
        if not report.get("compiled"):
            blocking += 1
            # surface the compile error from the fail string (the only place it lives)
            msg = next((f for f in fails if "WONT COMPILE" in f), "%s: B1 won't compile" % name)
            out.append({"kind": "WONT_COMPILE", "severity": "fail", "location": name, "message": msg})
        for miss in report.get("example_misses", []):
            blocking += 1
            out.append({"kind": "EXAMPLE_MISS", "severity": "fail", "location": name, "message": miss})
        for kind, detail in report.get("smells", []):
            blocking += 1
            out.append({"kind": kind, "severity": "fail", "location": name, "message": detail})
        for w in warns:
            out.append({"kind": "NO_EXAMPLES", "severity": "advisory", "location": name, "message": w})
    ok = blocking == 0
    if not out:
        summary = "%d spec(s): compile + examples + safety clean" % len(specs)
    else:
        summary = ("%d finding(s) (%d blocking, %d advisory) across %d spec(s) — confirm a flagged "
                   "ReDoS with a manual timing test" % (len(out), blocking, len(out) - blocking, len(specs)))
    return {"tool": "regex-check", "ok": ok, "summary": summary, "findings": out}


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

# Adversarial MUST-FLAG patterns — the exponential/polynomial families the AST scan must catch.
# Star height >= 2 (a repeat whose body holds another repeat) covers the whole nested family, incl.
# the bounded-{m,n}-outer polynomial cases the old regex-on-regex heuristic missed.
REDOS_MUST_FLAG = (
    r"(.*a){10}",       # NESTED: bounded-outer repeat over a `.*` inner -> polynomial blow-up
    r"(a?){20}a{20}",   # NESTED: bounded-outer repeat over an `a?` inner -> exponential blow-up
    r"([^,]*,){20}",    # NESTED: the classic CSV-field polynomial ReDoS
    r"(a*)*",           # NESTED: star-outer over star-inner (the floor case)
    r"(a|ab)*",         # OVERLAPPING_ALTERNATION (one branch a prefix of another)
    r".*.*x",           # QUADRATIC_WILDCARD (twin unbounded `.` repeats)
    r"^(\w+)+@\w+$",    # NESTED: a quantified group under `+`
)

# SAFE patterns the scan must NOT flag (regression fixtures). (foo|bar|baz)* is the classic false
# positive: mutually-exclusive branches that merely share a first char are linear-safe, not an overlap
# (and `sre_parse` factors no empty arm out of them, so the AST signal stays silent).
REDOS_MUST_NOT_FLAG = (
    r"(foo|bar|baz)*",            # mutually-exclusive alternation under `*` — linear-safe
    r"\d{4}-\d{2}-\d{2}",
    r"[a-z]+@[a-z]+\.[a-z]+",
    r"(?:abc|def)g",
    r"a+b+c+",                    # sibling repeats, not nested — star height 1
    r"(?:foo)*",                  # non-capturing group, no inner quantifier — `?:` is not a quant
    r"(a|b|c)+",                  # single-char branches — `sre_parse` folds them into one IN class
    r"(abc){3}",                  # bounded repeat over a literal — no inner quantifier
    r"^\w+$",                     # a single anchored repeat — star height 1
)


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

    # 5. the AST scan flags EVERY MUST-FLAG pattern (the exponential/polynomial families) and stays
    #    quiet on EVERY MUST-NOT-FLAG safe pattern. Both sets are wired in as assertions.
    for bad in REDOS_MUST_FLAG:
        if not redos_smells(bad):
            errs.append("redos_smells MISSED catastrophic pattern %r (must flag)" % bad)
    # the bounded-{m,n}-outer polynomial family must land specifically on NESTED_QUANTIFIER
    for poly in (r"(.*a){10}", r"(a?){20}a{20}", r"([^,]*,){20}"):
        if not any(k == "NESTED_QUANTIFIER" for k, _ in redos_smells(poly)):
            errs.append("redos_smells did not flag %r as NESTED_QUANTIFIER" % poly)
    if not any(k == "OVERLAPPING_ALTERNATION" for k, _ in redos_smells(r"(a|ab)*")):
        errs.append("redos_smells missed (a|ab)* overlapping alternation")
    if not any(k == "QUADRATIC_WILDCARD" for k, _ in redos_smells(r".*.*x")):
        errs.append("redos_smells missed .*.* quadratic wildcard")
    for safe in REDOS_MUST_NOT_FLAG:
        if redos_smells(safe):
            errs.append("redos_smells false-positive on safe pattern %r: %s" % (safe, redos_smells(safe)))

    # 5b. an unparseable pattern must surface as a B1 compile finding, never a ReDoS verdict
    _, fails, _ = validate_spec({"name": "broken", "pattern": r"(a+", "mode": "full",
                                 "positives": [], "negatives": []})
    if not any("B1 WONT COMPILE" in f for f in fails):
        errs.append("unparseable pattern '(a+' was not reported as a B1 compile finding: %s" % fails)
    if any("ReDoS-SMELL" in f for f in fails):
        errs.append("unparseable pattern '(a+' wrongly produced a ReDoS verdict: %s" % fails)

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
        if rep.get("tool") != "regex-check":
            errs.append("--json %s: tool=%r, want 'regex-check'" % (label, rep.get("tool")))
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

    # dirty fixture (SPEC_REDOS ⇒ a B3 NESTED_QUANTIFIER fail): tool right, ok false, findings non-empty
    dirty_rep = _capture_report(build_report([SPEC_REDOS]))
    _assert_report(dirty_rep, False, True, "dirty")
    if not any(fd["kind"] == "NESTED_QUANTIFIER" and fd["severity"] == "fail" for fd in dirty_rep["findings"]):
        errs.append("--json dirty: NESTED_QUANTIFIER should map to severity 'fail'")
    # advisory-only spec (a compiling, example-free, safe pattern) keeps ok TRUE — only a NO_EXAMPLES warn
    adv_rep = _capture_report(build_report([{"name": "no-ex", "pattern": r"\d+", "mode": "full"}]))
    _assert_report(adv_rep, True, True, "advisory-only")
    if not any(fd["kind"] == "NO_EXAMPLES" and fd["severity"] == "advisory" for fd in adv_rep["findings"]):
        errs.append("--json advisory-only: NO_EXAMPLES should map to severity 'advisory'")
    # clean fixture ⇒ ok true, findings []
    _assert_report(_capture_report(build_report([SPEC_GOOD])), True, False, "clean")

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
        print("regex-check: OK — compile + example-set (full/partial) + AST-based ReDoS scan verified "
              "over good/bad fixtures (must-flag all flag; must-not-flag none flag)")
        return 0
    # --json is a parse-anywhere reporting flag — strip it out, remember it, leave everything else.
    as_json = "--json" in argv
    if as_json:
        argv = [a for a in argv if a != "--json"]
        if not argv:
            sys.stderr.write("usage: regex-check.py [--json] <spec.json>\n")
            return 2
    try:
        doc = json.load(open(argv[0], encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write("regex-check: bad spec — %s\n" % e)
        return 2
    specs = doc if isinstance(doc, list) else [doc]
    if as_json:
        rep = build_report(specs)
        _report_json(rep["tool"], rep["ok"], rep["summary"], rep["findings"])
        return 0 if rep["ok"] else 1
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
