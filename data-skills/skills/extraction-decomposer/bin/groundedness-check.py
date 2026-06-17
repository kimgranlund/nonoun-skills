#!/usr/bin/env python3
"""groundedness-check.py — the extraction-decomposer FIDELITY gate. Self-contained (stdlib only).

This is the centerpiece. A schema validator proves an extraction is VALID; it is blind to the
extraction being INVENTED. The signature LLM failure here is schema-conformant JSON that contains a
hallucinated value the source never stated. Schema validation passes that failure straight through.

So this tool attacks the dangerous axis directly: it walks every SCALAR value in an extraction
(string / number — booleans are skipped, see below) and asserts that value is GROUNDED in the source
text. A value is grounded when the source supports it under one of four widening tests:

  EXACT        the value appears verbatim as a substring of the source
  NORMALIZED   it appears after case-folding + whitespace-collapse + punctuation-trim
  NUMERIC      a number appears digits-and-sign equal (12,000 / $12000 / 12000.0 all match "12000")
  DATE         a date appears in a common reformat (2026-06-16 <-> 06/16/2026 <-> June 16, 2026)

Anything that survives none of those is flagged as a LIKELY HALLUCINATION — an extracted value the
source does not support. Groundedness is NECESSARY, not sufficient: a grounded value can still be the
wrong span (see the failure taxonomy in references/groundedness.md). This tool catches the invented
value deterministically; the wrong-span / over-normalized cases route to the adversarial verifier.

Booleans are NOT grounded by this check: `true`/`false` rarely appear as literal source tokens (they
encode a judgment about the source), so flagging them would be all false positives. They are a
`[review]` item, not a gate — the adversarial verifier judges them.

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


def normalize(s):
    """Case-fold, collapse internal whitespace, strip edge punctuation/quotes."""
    s = _WS.sub(" ", str(s)).strip()
    s = _PUNCT_EDGE.sub("", s)
    return s.casefold()


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


def is_grounded(value, source, source_norm, source_nums, source_dates):
    """Return the grounding kind ('EXACT'|'NORMALIZED'|'NUMERIC'|'DATE') or None if ungrounded."""
    sval = str(value)
    if not sval.strip():
        return "EXACT"  # empty string is vacuously grounded (it asserts nothing about the source)

    # numbers: compare on the canonical numeric key, so 12,000 / $12000 / 12000.0 all ground "12000"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if _num_key(sval) in source_nums:
            return "NUMERIC"
        return None

    # strings — widen from exact to normalized
    if sval in source:
        return "EXACT"
    nval = normalize(sval)
    if nval and nval in source_norm:
        return "NORMALIZED"
    # a numeric-looking string ("12,000", "$5.50") grounds against source numbers
    if _NUM_TOKEN.search(sval) and _num_key(sval) in source_nums:
        return "NUMERIC"
    # a date-looking string grounds against any date the source expresses, in any common format
    vdates = _date_keys(sval)
    if vdates and (vdates & source_dates):
        return "DATE"
    return None


def check(extraction, source):
    """Return (findings, n_scalars). A finding is (path, value, 'UNGROUNDED')."""
    source_norm = normalize(source)
    source_nums = _source_num_keys(source)
    source_dates = _date_keys(source)
    findings, n = [], 0
    for path, value in scalar_values(extraction):
        n += 1
        if is_grounded(value, source, source_norm, source_nums, source_dates) is None:
            findings.append((path, value, "UNGROUNDED"))
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


def selftest():
    errs = []

    # 1. a fully faithful extraction has ZERO ungrounded findings.
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

    # 3. the normalization ladder — each rung grounds where exact-match would miss.
    src = "Total: $1,234.50 on 2026-01-02 for ACME  Corp."
    cases = [
        ("ACME Corp.", True),       # NORMALIZED (double-space collapse + edge punct)
        (1234.5, True),             # NUMERIC ($1,234.50 -> 1234.5)
        ("1,234.50", True),         # numeric string
        ("01/02/2026", True),       # DATE reformat of 2026-01-02
        ("Globex", False),          # absent -> ungrounded
        (9999, False),              # absent number -> ungrounded
    ]
    snorm, snums, sdates = normalize(src), _source_num_keys(src), _date_keys(src)
    for val, want_grounded in cases:
        got = is_grounded(val, src, snorm, snums, sdates) is not None
        if got != want_grounded:
            errs.append("grounding %r: got grounded=%s want %s" % (val, got, want_grounded))

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
    for path, value, _ in findings:
        v = repr(value)
        print("  UNGROUNDED  %-28s %s" % (path, v if len(v) <= 60 else v[:57] + "..."))
    if findings:
        sys.stderr.write("groundedness-check: FAIL — %d of %d scalar(s) not grounded in the source "
                         "(likely hallucination — verify each before shipping)\n" % (len(findings), n))
        return 1
    print("groundedness-check: OK — all %d scalar value(s) grounded in the source" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
