#!/usr/bin/env python3
"""groundedness-check.py — the extraction-decomposer FIDELITY gate. Self-contained (stdlib only).

This is the centerpiece. A schema validator proves an extraction is VALID; it is blind to the
extraction being INVENTED. The signature LLM failure here is schema-conformant JSON that contains a
hallucinated value the source never stated. Schema validation passes that failure straight through.

So this tool attacks the dangerous axis directly: it walks every SCALAR value in an extraction
(string / number — booleans are skipped, see below) and asserts that value is GROUNDED in the source
text. A value is grounded when the source supports it under one of four widening tests:

  EXACT        the value's TOKEN SEQUENCE appears contiguously in the source token stream
  NORMALIZED   the same token-sequence match after case-folding + edge-punctuation trim
  NUMERIC      a number appears digits-and-sign equal (12,000 / $12000 / 12000.0 all match "12000")
  DATE         a date appears in a common reformat (2026-06-16 <-> 06/16/2026 <-> June 16, 2026)

The string tests are TOKEN/WORD-BOUNDARY matches, NOT raw substring tests. A raw-substring test is a
known false-negative trap: short invented values ground wholesale because each is a fragment of a real
word — "Fran" grounds against "San Francisco", "Ware" against "warehouse", and an invented "John Smith"
split into "John"+"Smith" grounds against "Johnson"/"Smithfield". Tokenizing both sides and requiring
the value's tokens to appear AS A CONTIGUOUS RUN of whole source tokens closes that trap (it mirrors
the numeric path, which already tokenizes). A short value below a token/length floor that DOES match is
not silently passed — it is surfaced as a distinct WEAK_GROUNDING finding ("verify manually"), because
a one-token, ≤3-char match is exactly where a coincidental fragment hit is most likely.

Anything that survives none of those is flagged as a LIKELY HALLUCINATION — an extracted value the
source does not support. This catches the value that appears nowhere AND the substring-fragment class
above; it does NOT catch a value that grounds against the WRONG span (see the failure taxonomy in
references/groundedness.md). This tool catches the invented value deterministically; the wrong-span /
over-normalized cases route to the adversarial verifier.

Booleans are NOT grounded by this check: `true`/`false` rarely appear as literal source tokens (they
encode a judgment about the source), so flagging them would be all false positives. They are a
`[review]` item, not a gate — the adversarial verifier judges them. An empty / whitespace-only string
is reported as a distinct EMPTY finding (it asserts nothing, but an empty value where the source has
content is usually a B4 "had to put something" defect, not silently grounded).

  python3 bin/groundedness-check.py selftest
  python3 bin/groundedness-check.py <extraction.json> <source.txt>   # nonzero exit on any ungrounded scalar

Python 3.8+.
"""
import json
import re
import sys

# --- normalization -----------------------------------------------------------------------------
_WS = re.compile(r"\s+")
_PUNCT_EDGE = re.compile(r"^[\s\"'`.,;:!?()\[\]{}<>\-–—]+|[\s\"'`.,;:!?()\[\]{}<>\-–—]+$")

# the weak-grounding floor: a string value whose ONLY grounding is a single short token is too cheap
# to coincidentally match (it is the fragment-hit zone). Surface it for manual review instead of
# passing it silently. Floors: < MIN_TOKENS whole tokens AND < MIN_CHARS characters → WEAK.
MIN_TOKENS = 2
MIN_CHARS = 4


def normalize(s):
    """Case-fold, collapse internal whitespace, strip edge punctuation/quotes."""
    s = _WS.sub(" ", str(s)).strip()
    s = _PUNCT_EDGE.sub("", s)
    return s.casefold()


# --- tokenization (the word-boundary core that replaces the raw-substring test) -----------------
# A token is a maximal run of word characters (letters/digits/underscore). Splitting on everything
# else means "Fran" tokenizes to ["fran"] and the source "San Francisco" to [..., "francisco", ...]
# — "fran" is NOT equal to "francisco", so the fragment no longer grounds. Numbers tokenize too, so
# the numeric path stays consistent with this one.
_TOKEN = re.compile(r"\w+", re.UNICODE)


def tokens(s, fold=True):
    """Word-tokens of a string. 'Acme Robotics Inc.' -> ['acme','robotics','inc'] (fold=True).

    fold=False keeps original case, so EXACT (case-sensitive) and NORMALIZED (case-folded) stay
    distinguishable rungs even though both are token-boundary matches."""
    return [(t.casefold() if fold else t) for t in _TOKEN.findall(str(s))]


def _contiguous_sublist(needle, haystack):
    """True iff the token list `needle` appears as a contiguous run inside `haystack`."""
    if not needle:
        return False
    n, h = len(needle), len(haystack)
    if n > h:
        return False
    first = needle[0]
    for i in range(h - n + 1):
        if haystack[i] == first and haystack[i:i + n] == needle:
            return True
    return False


# --- numeric grounding -------------------------------------------------------------------------
_NUM_TOKEN = re.compile(r"[-+]?\d[\d,_ ]*(?:\.\d+)?")


def _num_key(text):
    """Canonical numeric key: sign + digits, trailing-zero-insensitive after the point.

    '12,000' -> '12000'; '$12000.00' -> '12000'; '-5.50' -> '-5.5'; '3.0' -> '3'."""
    m = re.search(r"[-+]?\d[\d,_ ]*(?:\.\d+)?", str(text))
    if not m:
        return None
    raw = m.group(0).replace(",", "").replace("_", "").replace(" ", "")
    neg = raw.startswith("-")
    raw = raw.lstrip("+-")
    if "." in raw:
        intpart, frac = raw.split(".", 1)
        frac = frac.rstrip("0")
        raw = intpart if not frac else intpart + "." + frac
    raw = raw.lstrip("0") or "0"
    return ("-" if neg and raw != "0" else "") + raw


def _source_num_keys(source):
    return {_num_key(t) for t in _NUM_TOKEN.findall(source)} - {None}


# the ENTIRE trimmed string must be one number token to take the numeric back door. This closes the
# M1 trap: "12 Nonexistent Street" and "12-FAKE-ID-9999" merely START with a number; without this
# anchor their leading "12" would ground them via _num_key (which reads only the first match). A
# string that is wholly numeric ("12,000", "$5.50", "-5.5", "3.0") still grounds; a string that only
# leads with a digit does NOT.
_WHOLE_NUM = re.compile(r"^[\s$€£¥]*[-+]?\d[\d,_ ]*(?:\.\d+)?[\s%]*$")


def _is_whole_number_string(s):
    """True iff the entire trimmed string is a single numeric token (optional currency/percent/sign)."""
    return bool(_WHOLE_NUM.match(str(s).strip()))


# --- date grounding ----------------------------------------------------------------------------
_MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], start=1)}
_MONTHS.update({m[:3]: i for m, i in list(_MONTHS.items())})

# the three date shapes we read: ISO (Y-M-D), slashed (M/D/Y or D/M/Y — both keyed), month-name.
_ISO = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
_SLASH = re.compile(r"\b(\d{1,2})[/.](\d{1,2})[/.](\d{4})\b")
_NAMED = re.compile(r"\b([A-Za-z]{3,9})\.?\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b")
_NAMED2 = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]{3,9})\.?,?\s+(\d{4})\b")


def _date_keys(text):
    """All (year, month, day) keys a string yields — both M/D and D/M readings of a slashed date."""
    keys = set()
    for y, m, d in _ISO.findall(text):
        keys.add((int(y), int(m), int(d)))
    for a, b, y in _SLASH.findall(text):
        keys.add((int(y), int(a), int(b)))   # M/D/Y
        keys.add((int(y), int(b), int(a)))   # D/M/Y
    for mon, d, y in _NAMED.findall(text):
        mi = _MONTHS.get(mon.casefold())
        if mi:
            keys.add((int(y), mi, int(d)))
    for d, mon, y in _NAMED2.findall(text):
        mi = _MONTHS.get(mon.casefold())
        if mi:
            keys.add((int(y), mi, int(d)))
    return keys


# --- the groundedness test ---------------------------------------------------------------------
def scalar_values(obj, path="$"):
    """Yield (json-path, value) for every scalar leaf. Lists index by [i]; objects by .key.

    Booleans and nulls are skipped — null is the *correct* representation of absent data (B4), and a
    boolean encodes a judgment, not a copied source token."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from scalar_values(v, "%s.%s" % (path, k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from scalar_values(v, "%s[%d]" % (path, i))
    elif isinstance(obj, bool) or obj is None:
        return
    elif isinstance(obj, (str, int, float)):
        yield path, obj


# Finding kinds the gate treats as FAILures (a non-grounding outcome the consumer must look at).
# A grounding kind ('EXACT'|'NORMALIZED'|'NUMERIC'|'DATE') is a PASS; these are not.
_FAIL_KINDS = ("UNGROUNDED", "WEAK_GROUNDING", "EMPTY")


def is_grounded(value, source, source_tokens, source_norm_tokens, source_nums, source_dates):
    """Return the outcome kind for a scalar value.

    Grounding (PASS):  'EXACT' | 'NORMALIZED' | 'NUMERIC' | 'DATE'
    Findings (FAIL):   'WEAK_GROUNDING' (matched, but below the floor — verify manually)
                       'EMPTY'          (empty / whitespace-only value)
                       'UNGROUNDED'     (no rung matched — likely hallucination)
    """
    sval = str(value)
    if not sval.strip():
        return "EMPTY"  # empty string asserts nothing; an empty value where the source has content
        # is usually a B4 "had to put something" defect, so surface it rather than pass it silently.

    # numbers: compare on the canonical numeric key, so 12,000 / $12000 / 12000.0 all ground "12000"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if _num_key(sval) in source_nums:
            return "NUMERIC"
        return "UNGROUNDED"

    # a STRING that is WHOLLY a number takes the numeric path (M1: a string that merely STARTS with a
    # digit must NOT — "12 Nonexistent Street" / "12-FAKE-ID-9999" fall through to the token test).
    if _is_whole_number_string(sval):
        if _num_key(sval) in source_nums:
            return "NUMERIC"
        return "UNGROUNDED"

    # a date-looking string grounds against any date the source expresses, in any common format
    vdates = _date_keys(sval)
    if vdates and (vdates & source_dates):
        return "DATE"

    # strings — TOKEN/WORD-BOUNDARY match (not raw substring). Require the value's token sequence to
    # appear as a contiguous run of whole source tokens. EXACT keeps original case; NORMALIZED folds.
    vtoks = tokens(sval)                       # case-folded
    matched = None
    if vtoks:
        if _contiguous_sublist(tokens(sval, fold=False), source_tokens):
            matched = "EXACT"
        elif _contiguous_sublist(vtoks, source_norm_tokens):
            matched = "NORMALIZED"
    if matched:
        # the weak-grounding floor: a 1-token, ≤3-char hit is where a coincidental fragment match
        # lives — do not pass it silently; surface it for manual verification.
        if len(vtoks) < MIN_TOKENS and len(sval.strip()) < MIN_CHARS:
            return "WEAK_GROUNDING"
        return matched
    return "UNGROUNDED"


def check(extraction, source):
    """Return (findings, n_scalars). A finding is (path, value, kind) for a non-grounding outcome."""
    source_tokens = tokens(source, fold=False)   # case-sensitive, for the EXACT rung
    source_norm_tokens = tokens(source)           # case-folded, for the NORMALIZED rung
    source_nums = _source_num_keys(source)
    source_dates = _date_keys(source)
    findings, n = [], 0
    for path, value in scalar_values(extraction):
        n += 1
        kind = is_grounded(value, source, source_tokens, source_norm_tokens, source_nums, source_dates)
        if kind in _FAIL_KINDS:
            findings.append((path, value, kind))
    return findings, n


# --- selftest fixtures -------------------------------------------------------------------------
SOURCE = """\
INVOICE

Bill to: Acme Robotics Inc.
Invoice #: INV-2026-0042
Issued: June 16, 2026
Due: 07/16/2026

Contact: Dana Lee (dana.lee@acme.example)
Subtotal: $12,000.00
Tax (8.5%): $1,020.00
Total due: $13,020.00
Status: unpaid
"""

# Every scalar here is grounded in the source (verbatim, normalized, numeric, or a date reformat).
FAITHFUL = {
    "vendor": "Acme Robotics Inc.",
    "invoice_number": "INV-2026-0042",
    "issued": "2026-06-16",          # source says "June 16, 2026" — DATE reformat
    "due": "2026-07-16",             # source says "07/16/2026" — DATE reformat
    "contact": {"name": "Dana Lee", "email": "dana.lee@acme.example"},
    "subtotal": 12000,               # source "$12,000.00" — NUMERIC key match
    "tax": 1020.0,                   # "$1,020.00" — NUMERIC
    "total": 13020,                  # "$13,020.00" — NUMERIC
    "tax_rate": "8.5%",              # "(8.5%)" — NORMALIZED (edge-punct trimmed)
    "paid": False,                   # boolean — skipped, not grounded by this check
    "notes": None,                   # null — skipped
}

# The signature failure: VALID, schema-conformant JSON with INVENTED values absent from the source.
INVENTED = dict(FAITHFUL,
                contact={"name": "John Smith",            # invented person — not in source
                         "email": "dana.lee@acme.example"},
                total=99999,                              # invented total — source says 13,020
                po_number="PO-7788")                      # invented field value entirely

# --- adversarial fixtures: the substring-fragment / numeric-back-door false-negative class --------
# B1: a raw-substring test grounds every one of these (each is a FRAGMENT of a real source word), yet
# every value is invented. A token/word-boundary match must FLAG them all.
FRAGMENT_SOURCE = "San Francisco warehouse Delivery net 30. Johnson Smithfield Corporation."
FRAGMENT_INVENTED = {
    "buyer": "Fran",      # fragment of "Francisco"  — must FLAG (WEAK or UNGROUNDED, never PASS)
    "seller": "Ware",     # fragment of "warehouse"  — must FLAG
    "agent": "Del",       # fragment of "Delivery"   — must FLAG
    "first": "John",      # fragment of "Johnson"    — must FLAG
    "last": "Smith",      # fragment of "Smithfield" — must FLAG
}
# M1: a string that merely STARTS with a grounded number must NOT ground via the numeric back door.
NUM_LEADING_SOURCE = "Quantity: 12 boxes. Year 2026."
NUM_LEADING_INVENTED = {
    "addr": "12 Nonexistent Street",   # leads with grounded "12" but is an invented address — FLAG
    "id": "12-FAKE-ID-9999",           # leads with grounded "12" but is an invented id        — FLAG
}


def selftest():
    errs = []

    def _kind(val, src):
        """Single-value grounding outcome under the same artifacts check() builds."""
        return is_grounded(val, src, tokens(src, fold=False), tokens(src),
                           _source_num_keys(src), _date_keys(src))

    # 1. a fully faithful extraction has ZERO findings.
    finds, n = check(FAITHFUL, SOURCE)
    if finds:
        errs.append("faithful extraction flagged %d value(s): %s" % (len(finds), finds))
    if n < 9:
        errs.append("faithful walk visited only %d scalars (booleans/null must be skipped, rest counted)" % n)

    # 2. the invented extraction is flagged on EXACTLY the invented scalars, and nothing else.
    finds, _ = check(INVENTED, SOURCE)
    flagged = {p for p, _, _ in finds}
    for want in ("$.contact.name", "$.total", "$.po_number"):
        if want not in flagged:
            errs.append("invented value at %s NOT flagged (got %s)" % (want, sorted(flagged)))
    for safe in ("$.vendor", "$.invoice_number", "$.issued", "$.due", "$.subtotal", "$.tax_rate"):
        if safe in flagged:
            errs.append("grounded value at %s wrongly flagged" % safe)

    # 2b. B1 — the substring-fragment class: every fragment value must be FLAGGED, never passed.
    finds, n = check(FRAGMENT_INVENTED, FRAGMENT_SOURCE)
    flagged = {p for p, _, _ in finds}
    for k in FRAGMENT_INVENTED:
        if "$.%s" % k not in flagged:
            errs.append("B1 substring-fragment %r NOT flagged — raw-substring false negative survives "
                        "(got %s)" % (k, sorted(flagged)))
    if len(flagged) != n:
        errs.append("B1 — expected ALL %d fragment values flagged, only %d were" % (n, len(flagged)))

    # 2c. M1 — a numeric-leading invented string must NOT ground via the numeric back door.
    finds, n = check(NUM_LEADING_INVENTED, NUM_LEADING_SOURCE)
    flagged = {p for p, _, _ in finds}
    for k in NUM_LEADING_INVENTED:
        if "$.%s" % k not in flagged:
            errs.append("M1 numeric-leading invented %r NOT flagged — leading-digit back door survives "
                        "(got %s)" % (k, sorted(flagged)))
    # and the bare grounded number itself STILL grounds (no over-correction)
    if _kind("12", NUM_LEADING_SOURCE) != "NUMERIC":
        errs.append("M1 over-corrected: a wholly-numeric string '12' should still ground NUMERIC")

    # 2d. WEAK_GROUNDING — a short value that DOES token-match the source is surfaced, not passed.
    #     "net" is a whole source token in FRAGMENT_SOURCE, but it is below the weak floor (1 token,
    #     3 chars) — it must report WEAK_GROUNDING (verify manually), not a silent grounding kind.
    if _kind("net", FRAGMENT_SOURCE) != "WEAK_GROUNDING":
        errs.append("WEAK floor: short whole-token 'net' should report WEAK_GROUNDING, got %r"
                    % _kind("net", FRAGMENT_SOURCE))
    # a longer multi-token whole match is NOT weak (the floor is for the fragment-hit zone only)
    if _kind("San Francisco", FRAGMENT_SOURCE) != "EXACT":
        errs.append("WEAK floor too wide: 'San Francisco' should ground EXACT, got %r"
                    % _kind("San Francisco", FRAGMENT_SOURCE))

    # 2e. EMPTY — an empty / whitespace-only string is a distinct finding, not a silent grounding.
    finds, _ = check({"blank": "", "spaces": "   "}, SOURCE)
    kinds = {p: k for p, _, k in finds}
    for p in ("$.blank", "$.spaces"):
        if kinds.get(p) != "EMPTY":
            errs.append("empty value at %s should report EMPTY, got %r" % (p, kinds.get(p)))

    # 3. the normalization ladder — each rung grounds where exact-match would miss.
    src = "Total: $1,234.50 on 2026-01-02 for ACME  Corp."
    cases = [
        ("ACME Corp.", True),       # NORMALIZED (case-fold token match)
        (1234.5, True),             # NUMERIC ($1,234.50 -> 1234.5)
        ("1,234.50", True),         # numeric string
        ("01/02/2026", True),       # DATE reformat of 2026-01-02
        ("Globex", False),          # absent -> ungrounded
        (9999, False),              # absent number -> ungrounded
    ]
    for val, want_grounded in cases:
        got = _kind(val, src) not in _FAIL_KINDS
        if got != want_grounded:
            errs.append("grounding %r: got grounded=%s want %s (kind=%r)"
                        % (val, got, want_grounded, _kind(val, src)))

    # 4. booleans/null are skipped by the scalar walk (never grounded, never flagged).
    paths = {p for p, _ in scalar_values({"a": True, "b": None, "c": "x"})}
    if paths != {"$.c"}:
        errs.append("scalar walk should yield only $.c, got %s" % sorted(paths))

    # 5. numeric key canonicalization
    for a, b in [("12,000", "12000"), ("$12000.00", "12000"), ("3.0", "3"), ("-5.50", "-5.5")]:
        if _num_key(a) != _num_key(b):
            errs.append("num_key(%r)=%r != num_key(%r)=%r" % (a, _num_key(a), b, _num_key(b)))
    return errs


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("groundedness-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("groundedness-check: OK — faithful extraction clean, invented values flagged, "
              "normalize/numeric/date ladder verified")
        return 0
    if len(argv) < 2:
        sys.stderr.write("usage: groundedness-check.py <extraction.json> <source.txt>\n")
        return 2
    try:
        extraction = json.load(open(argv[0], encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write("cannot read extraction: %s\n" % e)
        return 2
    try:
        source = open(argv[1], encoding="utf-8").read()
    except OSError as e:
        sys.stderr.write("cannot read source: %s\n" % e)
        return 2
    findings, n = check(extraction, source)
    for path, value, kind in findings:
        v = repr(value)
        note = {"UNGROUNDED": "", "WEAK_GROUNDING": "  (short match — verify manually)",
                "EMPTY": "  (empty value)"}.get(kind, "")
        print("  %-14s %-28s %s%s" % (kind, path, v if len(v) <= 50 else v[:47] + "...", note))
    if findings:
        # honest wording (m1): some of these are FALSE POSITIVES (a locale/scientific-notation value,
        # an over-normalization that nonetheless preserves meaning). Say "verify", do not assert.
        sys.stderr.write("groundedness-check: FAIL — %d of %d scalar(s) not cleanly grounded in the "
                         "source — verify each against the source before shipping (an ungrounded "
                         "scalar is a LIKELY but not certain hallucination)\n" % (len(findings), n))
        return 1
    print("groundedness-check: OK — all %d scalar value(s) grounded in the source" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
