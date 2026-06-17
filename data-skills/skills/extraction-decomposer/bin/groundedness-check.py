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
  DATE         a date appears in a common reformat (2026-06-16 <-> 06/16/2026 <-> June 16, 2026; an
               ambiguous slashed/dotted date keys both D/M/Y and M/D/Y, so a European 02.01.2026
               grounds 2026-01-02 too — but an unambiguous day>12 drops the impossible reading)

Non-ASCII digit scripts (Arabic-Indic ٠١٢…, Eastern-Arabic/Persian ۰۱۲…, Devanagari ०१२…, fullwidth
０１２…) are folded to ASCII before numeric/date key extraction, on both the source and the value, so a
number or date written in a non-ASCII script grounds an ASCII extraction. An all-ASCII source/value is
unchanged.

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

WRONG-SPAN, AND WHY THIS TOOL ONLY APPROXIMATES IT
--------------------------------------------------
Grounding proves a value is PRESENT in the source; it cannot prove the value plays the CLAIMED ROLE.
"Acme" extracted as `buyer` grounds cleanly even when the source has Acme as the `seller` — a
*wrong-span* defect. A deterministic checker cannot confirm role; that needs a fresh-context
ADVERSARIAL-VERIFY step (the verifier prompt lives in references/fidelity-axis.md). What a stdlib
checker CAN do is APPROXIMATE proximity: an OPTIONAL per-field "context cue" signal. If the spec gives
a field one or more cue strings (e.g. buyer -> ["buyer","bill to","purchaser"]), then for a grounded
scalar we check whether its nearest source occurrence falls within a token window (default ~12,
configurable) of a cue occurrence. Grounded but NO cue near ANY occurrence -> a WEAK_CONTEXT ADVISORY
("in the source but not near any '<field>' cue — possible wrong-span; verify the role"). This is a
HEURISTIC, not an oracle: it is opt-in (no cues -> no WEAK_CONTEXT, never a false positive on cue-less
specs), and it is ADVISORY — it does NOT affect exit code. Framing: gate PRESENCE (code), gauge
PROXIMITY (code, opt-in heuristic), confirm ROLE (adversarial verify). Do not read a clean proximity
result as a role confirmation.

Booleans are NOT grounded by this check: `true`/`false` rarely appear as literal source tokens (they
encode a judgment about the source), so flagging them would be all false positives. They are a
`[review]` item, not a gate — the adversarial verifier judges them. An empty / whitespace-only string
is reported as a distinct EMPTY finding (it asserts nothing, but an empty value where the source has
content is usually a B4 "had to put something" defect, not silently grounded).

  python3 bin/groundedness-check.py selftest
  python3 bin/groundedness-check.py <extraction.json> <source.txt>             # nonzero exit on any ungrounded scalar
  python3 bin/groundedness-check.py <extraction.json> <source.txt> [cues.json] [--window N]
                                                                               # opt-in proximity (WEAK_CONTEXT advisory)
  python3 bin/groundedness-check.py <extraction.json> <source.txt> [...] [--spans]
                                                                               # ALSO emit A5 provenance per grounded scalar
  python3 bin/groundedness-check.py <extraction.json> <source.txt> [...] [--min-tokens N] [--min-chars N]
                                                                               # tune the WEAK_GROUNDING floor (defaults 2 / 4)

`cues.json` (optional) is a JSON object mapping a field's LEAF NAME to a list of cue strings, e.g.
`{"buyer": ["buyer","bill to","purchaser"], "seller": ["seller","sold by","vendor"]}`. Only fields
present in this map get the proximity check; everything else behaves exactly as before. --window sets
the cue token window (default 12). WEAK_CONTEXT is ADVISORY: it is printed but does NOT change the exit
code (presence/grounding failures still do).

--spans (ADDITIVE, OPT-IN, A5 provenance): for each GROUNDED scalar, additionally emit the SOURCE span
that grounded it — the character offset and a short ±20-char snippet of the source where the grounding
match occurred. A green run then produces provenance, not just pass/fail. A value grounding at multiple
spans emits the FIRST and notes the count. Without --spans, output and exit are EXACTLY as before.

--min-tokens N / --min-chars N (ADDITIVE, OPT-IN): the WEAK_GROUNDING floor — a string value whose only
grounding is below BOTH floors (< N tokens AND < N chars) is surfaced as WEAK_GROUNDING rather than
passed. Defaults are unchanged (2 tokens, 4 chars), so a call without these flags behaves exactly as
before; a high-recall corpus can tighten or loosen the band. Python 3.8+.
"""
import json
import re
import sys
import unicodedata

# --- non-ASCII digit folding (ADDITIVE; ASCII text is untouched) -------------------------------
# Numeric and date grounding read ASCII digits. A source that writes a number or date in a non-ASCII
# digit script — Arabic-Indic (٠١٢…), Eastern-Arabic/Persian (۰۱۲…), Devanagari (०१२…), fullwidth
# (０１２…) — would key under those code points and never match an extraction normalized to ASCII
# (`١٢٣٤` keyed as "١٢٣٤" ≠ "1234"). `_ascii_digits` rewrites any character carrying a Unicode digit
# value to its ASCII equivalent BEFORE key extraction, on BOTH the source and the value side. It is
# strictly additive: a character with no digit value (every ASCII letter/digit/punct) is left as-is,
# so an all-ASCII source is byte-for-byte unchanged and no existing grounding moves.
def _ascii_digits(s):
    """Map any Unicode-digit character to its ASCII 0-9; leave everything else untouched."""
    s = str(s)
    if s.isascii():
        return s  # fast path: nothing to fold, behaviour identical to before
    out = []
    for ch in s:
        if ch.isascii():
            out.append(ch)
            continue
        d = unicodedata.digit(ch, None)
        out.append(str(d) if d is not None else ch)
    return "".join(out)


# --- normalization -----------------------------------------------------------------------------
_WS = re.compile(r"\s+")
_PUNCT_EDGE = re.compile(r"^[\s\"'`.,;:!?()\[\]{}<>\-–—]+|[\s\"'`.,;:!?()\[\]{}<>\-–—]+$")

# the weak-grounding floor: a string value whose ONLY grounding is a single short token is too cheap
# to coincidentally match (it is the fragment-hit zone). Surface it for manual review instead of
# passing it silently. Floors: < MIN_TOKENS whole tokens AND < MIN_CHARS characters → WEAK.
MIN_TOKENS = 2
MIN_CHARS = 4

DEFAULT_CUE_WINDOW = 12  # tokens of gap allowed between a value occurrence and the nearest cue


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


def token_spans(s, fold=True):
    """Like tokens(), but each token carries its CHARACTER span in `s`: (token, char_start, char_end).

    Provenance (--spans) threads the source character offset back from a token match. The token strings
    are IDENTICAL to tokens(s, fold)'s output (same casefold), so a token index into one is the same
    index into the other — the spans line up with the lists is_grounded already matches against."""
    return [((m.group(0).casefold() if fold else m.group(0)), m.start(), m.end())
            for m in _TOKEN.finditer(str(s))]


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


def _occurrence_spans(needle, haystack):
    """All (start, end) token-index spans where `needle` appears as a contiguous run in `haystack`.

    Indices are into `haystack`'s token list; `end` is exclusive. Empty list if no occurrence."""
    spans = []
    if not needle:
        return spans
    n, h = len(needle), len(haystack)
    if n > h:
        return spans
    first = needle[0]
    for i in range(h - n + 1):
        if haystack[i] == first and haystack[i:i + n] == needle:
            spans.append((i, i + n))
    return spans


# --- A5 provenance: locate the SOURCE span that grounded a value (OPT-IN, --spans) ------------------
SNIPPET_PAD = 20  # chars of context shown on each side of the grounding offset in the emitted snippet


def _snippet(source, start, end, pad=SNIPPET_PAD):
    """A short ±pad-char window of `source` around the [start, end) char span, whitespace-collapsed.

    Elision markers (…) mark a clipped edge so the snippet is not mistaken for a document boundary."""
    lo = max(0, start - pad)
    hi = min(len(source), end + pad)
    frag = _WS.sub(" ", source[lo:hi]).strip()
    return ("…" if lo > 0 else "") + frag + ("…" if hi < len(source) else "")


def _token_run_offsets(needle_tokens, source_spans):
    """Char offsets (start) of every place `needle_tokens` runs contiguously through `source_spans`.

    `source_spans` is token_spans() output [(tok, cstart, cend), ...]; the match is on the token strings
    (index-aligned with the token list is_grounded already matched), and the returned offset is the
    char start of the run's FIRST token — the exact source character where the grounding begins."""
    toks = [t for t, _, _ in source_spans]
    spans = _occurrence_spans(needle_tokens, toks)
    return [source_spans[i][1] for i, _ in spans]


def _leaf_field(path):
    """The trailing field name of a JSON path: '$.contact.buyer' -> 'buyer', '$.items[2]' -> 'items'.

    Cues are keyed by leaf field name, so a value at any depth/position under that field is checked."""
    last = path.rsplit(".", 1)[-1]
    return last.split("[", 1)[0]


def _gap(span_a, span_b):
    """Token gap between two [start, end) spans: 0 if they touch/overlap, else the tokens between."""
    a0, a1 = span_a
    b0, b1 = span_b
    if a1 <= b0:
        return b0 - a1
    if b1 <= a0:
        return a0 - b1
    return 0


def near_a_cue(value, cues_for_field, source_norm_tokens, window):
    """True iff a NORMALIZED occurrence of `value` sits within `window` tokens of a cue occurrence.

    Both the value and every cue are matched as contiguous whole-token runs in the case-folded source
    (the same word-boundary discipline grounding uses), so a fragment can never satisfy proximity.
    Returns True if EITHER the value has no locatable occurrence (the proximity question is moot — a
    truly absent value is an UNGROUNDED matter, not a WEAK_CONTEXT one) OR no cue is configured."""
    if not cues_for_field:
        return True  # opt-in: no cue for this field -> never a WEAK_CONTEXT finding
    val_spans = _occurrence_spans(tokens(value), source_norm_tokens)
    if not val_spans:
        return True  # not locatable here -> grounding/UNGROUNDED owns this, not proximity
    cue_spans = []
    for cue in cues_for_field:
        cue_spans += _occurrence_spans(tokens(cue), source_norm_tokens)
    if not cue_spans:
        return True  # the cue itself never appears in the source -> cannot judge proximity; stay quiet
    for vs in val_spans:
        for cs in cue_spans:
            if _gap(vs, cs) <= window:
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


_EU_NUM = re.compile(r"[-+]?\d{1,3}(?:\.\d{3})+,\d+")       # 1.234,56  ·  1.234.567,89   (EU format)
_SCI_NUM = re.compile(r"[-+]?\d+(?:\.\d+)?[eE][-+]?\d+")    # 1.5e3  ·  2E-4              (scientific)


def _locale_num_keys(source):
    """Extra source-side keys for EU-format (1.234,56) and scientific (1.5e3) numbers, so a faithful
    extraction normalized to a plain number (1234.56 / 1500) still grounds. ADDITIVE — never removes a
    US-format key. The EU pattern REQUIRES a ',\\d+' decimal tail, which disambiguates it from US
    thousands (a bare '1.234' stays US), so this adds no spurious groundings."""
    keys = set()
    for t in _EU_NUM.findall(source):
        k = _num_key(t.replace(".", "").replace(",", "."))
        if k:
            keys.add(k)
    for t in _SCI_NUM.findall(source):
        try:
            v = float(t)
        except ValueError:
            continue
        k = _num_key(str(int(v)) if v == int(v) else repr(v))
        if k:
            keys.add(k)
    return keys


def _source_num_keys(source):
    source = _ascii_digits(source)  # ADDITIVE: fold non-ASCII digits so a source written in
    # Arabic-Indic/Devanagari/fullwidth digits keys under ASCII; an all-ASCII source is unchanged.
    return ({_num_key(t) for t in _NUM_TOKEN.findall(source)} | _locale_num_keys(source)) - {None}


def _num_offsets(source, want_key):
    """Char offsets where a source number canonicalizes to `want_key` (for --spans provenance).

    `_ascii_digits` is a per-character fold, so the folded string is the same length as `source` and a
    match offset in it is the same offset in the original. Plain US tokens and EU/scientific tokens are
    both scanned, mirroring the keys _source_num_keys emits; returns offsets in document order."""
    folded = _ascii_digits(source)
    offs = []
    for m in _NUM_TOKEN.finditer(folded):
        if _num_key(m.group(0)) == want_key:
            offs.append(m.start())
    for m in _EU_NUM.finditer(folded):
        if _num_key(m.group(0).replace(".", "").replace(",", ".")) == want_key:
            offs.append(m.start())
    for m in _SCI_NUM.finditer(folded):
        try:
            v = float(m.group(0))
        except ValueError:
            continue
        k = _num_key(str(int(v)) if v == int(v) else repr(v))
        if k == want_key:
            offs.append(m.start())
    return sorted(set(offs))


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


def _valid_ymd(y, m, d):
    """True iff (y, m, d) is a month/day-plausible key (1-12 / 1-31). Guards the ambiguous-date
    reading: a slashed `25/12/2026` is unambiguously D/M/Y (day 25 > 12), so the M/D/Y reading would
    be month 25 — an IMPOSSIBLE key. Dropping it is purely additive: an impossible key can never match
    a real extraction, so no existing grounding is lost, and a clearly-unambiguous date no longer emits
    a phantom reading. Day range is the loose 1-31 (we are matching keys, not validating calendars)."""
    return 1 <= m <= 12 and 1 <= d <= 31


def _date_keys(text):
    """All (year, month, day) keys a string yields — both M/D and D/M readings of a slashed date.

    Slashed/dotted dates are ambiguous, so BOTH the M/D/Y and D/M/Y readings are emitted (accepting
    either is correct for a fidelity AID): `02.01.2026` grounds `2026-01-02` (D/M/Y) and `02/01/2026`
    still grounds `2026-02-01` (M/D/Y). Impossible readings (month/day out of range) are filtered by
    `_valid_ymd`, so `25/12/2026` yields only the D/M/Y key, not an impossible month-25 M/D/Y one."""
    text = _ascii_digits(text)  # ADDITIVE: a date written in a non-ASCII digit script keys under ASCII
    keys = set()
    for y, m, d in _ISO.findall(text):
        if _valid_ymd(int(y), int(m), int(d)):
            keys.add((int(y), int(m), int(d)))
    for a, b, y in _SLASH.findall(text):
        if _valid_ymd(int(y), int(a), int(b)):
            keys.add((int(y), int(a), int(b)))   # M/D/Y
        if _valid_ymd(int(y), int(b), int(a)):
            keys.add((int(y), int(b), int(a)))   # D/M/Y
    for mon, d, y in _NAMED.findall(text):
        mi = _MONTHS.get(mon.casefold())
        if mi and _valid_ymd(int(y), mi, int(d)):
            keys.add((int(y), mi, int(d)))
    for d, mon, y in _NAMED2.findall(text):
        mi = _MONTHS.get(mon.casefold())
        if mi and _valid_ymd(int(y), mi, int(d)):
            keys.add((int(y), mi, int(d)))
    return keys


def _date_offsets(source, want_keys):
    """Char offsets where a source date expresses any key in `want_keys` (for --spans provenance).

    Same per-character-fold offset invariance as _num_offsets. A slashed/dotted date yields both the
    M/D/Y and D/M/Y readings (matching _date_keys), so it matches if EITHER reading is wanted; a named
    date is matched by its single valid reading. Returns offsets in document order."""
    folded = _ascii_digits(source)
    offs = []
    for m in _ISO.finditer(folded):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if _valid_ymd(y, mo, d) and (y, mo, d) in want_keys:
            offs.append(m.start())
    for m in _SLASH.finditer(folded):
        a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if ((_valid_ymd(y, a, b) and (y, a, b) in want_keys) or
                (_valid_ymd(y, b, a) and (y, b, a) in want_keys)):
            offs.append(m.start())
    for m in _NAMED.finditer(folded):
        mi = _MONTHS.get(m.group(1).casefold())
        d, y = int(m.group(2)), int(m.group(3))
        if mi and _valid_ymd(y, mi, d) and (y, mi, d) in want_keys:
            offs.append(m.start())
    for m in _NAMED2.finditer(folded):
        mi = _MONTHS.get(m.group(2).casefold())
        d, y = int(m.group(1)), int(m.group(3))
        if mi and _valid_ymd(y, mi, d) and (y, mi, d) in want_keys:
            offs.append(m.start())
    return sorted(set(offs))


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

# WEAK_CONTEXT is the opt-in proximity advisory. A value can be GROUNDED (it passed a rung above) yet
# sit nowhere near its field's cue — a possible wrong-span. It is reported but does NOT change the exit
# code (it is a heuristic that only APPROXIMATES role; true role confirmation is the adversarial verify
# step). So it is deliberately NOT in _FAIL_KINDS.
WEAK_CONTEXT = "WEAK_CONTEXT"


def is_grounded(value, source, source_tokens, source_norm_tokens, source_nums, source_dates,
                min_tokens=MIN_TOKENS, min_chars=MIN_CHARS):
    """Return the outcome kind for a scalar value.

    Grounding (PASS):  'EXACT' | 'NORMALIZED' | 'NUMERIC' | 'DATE'
    Findings (FAIL):   'WEAK_GROUNDING' (matched, but below the floor — verify manually)
                       'EMPTY'          (empty / whitespace-only value)
                       'UNGROUNDED'     (no rung matched — likely hallucination)

    `min_tokens`/`min_chars` are the WEAK_GROUNDING floor (a token-match below BOTH is surfaced as
    WEAK rather than passed). They default to the module constants, so every existing caller is
    byte-for-byte unchanged; --min-tokens / --min-chars thread alternates through here."""
    sval = str(value)
    if not sval.strip():
        return "EMPTY"  # empty string asserts nothing; an empty value where the source has content
        # is usually a B4 "had to put something" defect, so surface it rather than pass it silently.

    # ADDITIVE: fold non-ASCII digits in the value for the NUMERIC paths only (a value written
    # "١٢٣٤" must key as "1234"). The token-match paths below keep the ORIGINAL sval — folding a name
    # is unnecessary (names have no digit chars) and the source side is already ASCII-folded, so an
    # all-ASCII value is byte-identical and no existing grounding moves.
    nval = _ascii_digits(sval)

    # numbers: compare on the canonical numeric key, so 12,000 / $12000 / 12000.0 all ground "12000"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if _num_key(nval) in source_nums:
            return "NUMERIC"
        return "UNGROUNDED"

    # a STRING that is WHOLLY a number takes the numeric path (M1: a string that merely STARTS with a
    # digit must NOT — "12 Nonexistent Street" / "12-FAKE-ID-9999" fall through to the token test).
    if _is_whole_number_string(nval):
        if _num_key(nval) in source_nums:
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
        # lives — do not pass it silently; surface it for manual verification. The floors are
        # configurable (--min-tokens / --min-chars); defaults reproduce the historical behaviour.
        if len(vtoks) < min_tokens and len(sval.strip()) < min_chars:
            return "WEAK_GROUNDING"
        return matched
    return "UNGROUNDED"


def grounded_span(value, kind, source, source_spans_cs, source_spans_norm, source_dates):
    """A5 provenance: for an already-GROUNDED value of `kind`, return (offset, snippet, count).

    `offset` is the char position in `source` where the FIRST grounding occurrence begins; `snippet`
    is a short ±SNIPPET_PAD-char window of the source around it; `count` is how many spans grounded
    the value (>1 means the value is ambiguous — surfaced for the adversarial verifier, see ROADMAP).
    Returns None if no concrete span can be located (defensive — `kind` should already be a PASS).

    `source_spans_cs` / `source_spans_norm` are token_spans(source, fold=False/True) — passed in so
    check() builds them once. This function performs NO grounding decision; it only RE-LOCATES the
    span for a value the grounding ladder already accepted, so it cannot change any pass/fail."""
    sval = str(value)
    nval = _ascii_digits(sval)
    if kind == "NUMERIC":
        offs = _num_offsets(source, _num_key(nval))
    elif kind == "DATE":
        offs = _date_offsets(source, _date_keys(sval))
    elif kind == "EXACT":
        offs = _token_run_offsets(tokens(sval, fold=False), source_spans_cs)
    elif kind == "NORMALIZED":
        offs = _token_run_offsets(tokens(sval), source_spans_norm)
    else:
        return None
    if not offs:
        return None
    start = offs[0]
    return start, _snippet(source, start, start + len(sval) if start + len(sval) <= len(source)
                           else len(source)), len(offs)


def check(extraction, source, cues=None, window=DEFAULT_CUE_WINDOW,
          min_tokens=MIN_TOKENS, min_chars=MIN_CHARS, spans=False, provenance_out=None):
    """Return (findings, n_scalars). A finding is (path, value, kind) for a non-grounding outcome.

    `cues` (optional) maps a field's LEAF NAME to a list of cue strings. When provided for a field, a
    GROUNDED scalar whose nearest source occurrence is not within `window` tokens of any cue occurrence
    yields a WEAK_CONTEXT advisory (possible wrong-span). Fields absent from `cues` are unaffected — the
    signal is strictly opt-in, so a cue-less call behaves exactly as before. WEAK_CONTEXT is advisory
    and does NOT enter the exit-affecting _FAIL_KINDS set.

    `min_tokens`/`min_chars` configure the WEAK_GROUNDING floor (defaults reproduce historical
    behaviour). `spans` (A5 provenance, OPT-IN): when True, `provenance_out` (if given) is appended
    with one (path, kind, offset, snippet, count) per GROUNDED scalar — the source span that grounded
    it. The (findings, n) return value is UNCHANGED whether or not spans is set, so every existing
    caller is byte-for-byte unaffected; provenance is a side-channel, never folded into findings."""
    cues = cues or {}
    source_tokens = tokens(source, fold=False)   # case-sensitive, for the EXACT rung
    source_norm_tokens = tokens(source)           # case-folded, for the NORMALIZED rung
    source_nums = _source_num_keys(source)
    source_dates = _date_keys(source)
    # token_spans() is built ONLY when --spans is requested (no cost on the default path).
    source_spans_cs = token_spans(source, fold=False) if spans else None
    source_spans_norm = token_spans(source) if spans else None
    findings, n = [], 0
    for path, value in scalar_values(extraction):
        n += 1
        kind = is_grounded(value, source, source_tokens, source_norm_tokens, source_nums, source_dates,
                           min_tokens=min_tokens, min_chars=min_chars)
        if kind in _FAIL_KINDS:
            findings.append((path, value, kind))
            continue
        # the value is GROUNDED (a PASS rung). Emit A5 provenance (opt-in) before the proximity check.
        if spans and provenance_out is not None:
            prov = grounded_span(value, kind, source, source_spans_cs, source_spans_norm, source_dates)
            if prov is not None:
                offset, snippet, count = prov
                provenance_out.append((path, kind, offset, snippet, count))
        # Only now does proximity apply, and only if the field has cues. A grounded value far from
        # every cue occurrence is a possible wrong-span -> WEAK_CONTEXT.
        cues_for_field = cues.get(_leaf_field(path))
        if cues_for_field and not near_a_cue(value, cues_for_field, source_norm_tokens, window):
            findings.append((path, value, WEAK_CONTEXT))
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

# --- proximity fixtures: WEAK_CONTEXT (wrong-span APPROXIMATION via opt-in cues) -------------------
# Acme is the SELLER in this source; a buyer field carrying "Acme" is a wrong-span defect that grounds
# cleanly (Acme is present) — only proximity to a "buyer" cue can hint at it. The buyer ("Globex") and
# the seller ("Acme") each sit next to their own cue word; cross-attribute them and they sit far away.
ROLE_SOURCE = (
    "Purchase Order. Bill to: Globex Industries, 5 Market St. "
    "A long stretch of boilerplate terms and conditions follows here for many tokens so that the two "
    "parties are well separated in the document and a token window cannot bridge them by accident. "
    "Sold by: Acme Robotics, the supplier of record for this order."
)
ROLE_CUES = {
    "buyer": ["buyer", "bill to", "purchaser"],
    "seller": ["seller", "sold by", "vendor", "supplier"],
}
# (a) WRONG-SPAN with cues: buyer="Acme Robotics" is GROUNDED (Acme is in the source) but far from any
#     buyer cue (it sits by "Sold by") -> WEAK_CONTEXT. seller="Acme Robotics" sits next to "Sold by"
#     -> NOT flagged. This is the discriminating pair.
ROLE_WRONG = {"buyer": "Acme Robotics", "seller": "Acme Robotics"}
# (b) RIGHT roles with the SAME values+cues: each value is near its own cue -> NEITHER flagged.
ROLE_RIGHT = {"buyer": "Globex Industries", "seller": "Acme Robotics"}
# (c) cue-less spec: the SAME wrong-span extraction with NO cues passed -> NO WEAK_CONTEXT at all
#     (the existing behavior is untouched — opt-in means silent when unused).


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

    # 2f. WEAK_CONTEXT (a) — wrong-span WITH cues: buyer="Acme Robotics" is grounded but far from any
    #     buyer cue -> flagged WEAK_CONTEXT; the same value as seller sits by "Sold by" -> NOT flagged.
    finds, _ = check(ROLE_WRONG, ROLE_SOURCE, cues=ROLE_CUES)
    wc = {p for p, _, k in finds if k == WEAK_CONTEXT}
    if "$.buyer" not in wc:
        errs.append("(a) wrong-span buyer='Acme Robotics' (grounded, far from a buyer cue) should be "
                    "WEAK_CONTEXT, got findings %s" % sorted(finds))
    if "$.seller" in wc:
        errs.append("(a) seller='Acme Robotics' sits next to its 'Sold by' cue — must NOT be WEAK_CONTEXT")
    # and WEAK_CONTEXT must never enter the exit-affecting set
    if any(k in _FAIL_KINDS for _, _, k in finds):
        errs.append("(a) WEAK_CONTEXT leaked into a FAIL kind — it must stay advisory")

    # 2g. WEAK_CONTEXT (b) — same values+cues but the RIGHT roles: each value is near its own cue, so
    #     NEITHER is flagged. Proves a nearby cue suppresses the advisory (no false positive on good data).
    finds, _ = check(ROLE_RIGHT, ROLE_SOURCE, cues=ROLE_CUES)
    wc = {p for p, _, k in finds if k == WEAK_CONTEXT}
    if wc:
        errs.append("(b) correctly-attributed values each near their own cue should NOT be WEAK_CONTEXT, "
                    "got %s" % sorted(wc))

    # 2h. WEAK_CONTEXT (c) — the SAME wrong-span extraction but NO cues passed: opt-in means the signal
    #     is silent. NO WEAK_CONTEXT at all (no regression / no false positive on a cue-less spec).
    finds, _ = check(ROLE_WRONG, ROLE_SOURCE)            # cues omitted
    if any(k == WEAK_CONTEXT for _, _, k in finds):
        errs.append("(c) cue-less spec must emit NO WEAK_CONTEXT (opt-in), got %s" % sorted(finds))
    # belt-and-suspenders: an empty cue map is also cue-less for every field
    finds, _ = check(ROLE_WRONG, ROLE_SOURCE, cues={})
    if any(k == WEAK_CONTEXT for _, _, k in finds):
        errs.append("(c) empty cue map must emit NO WEAK_CONTEXT, got %s" % sorted(finds))

    # 2i. proximity must not perturb existing grounding outcomes: the faithful extraction stays clean
    #     even when irrelevant cues are supplied for fields whose values ARE near them.
    finds, _ = check(FAITHFUL, SOURCE, cues={"vendor": ["bill to"]})
    if finds:
        errs.append("(opt-in) faithful extraction with a satisfiable cue should stay clean, got %s"
                    % sorted(finds))
    # and a wider window relaxes the heuristic: with a window spanning the whole doc, even the wrong-span
    # buyer is "near" the buyer cue, so the advisory is suppressed (tunable, as documented).
    finds, _ = check(ROLE_WRONG, ROLE_SOURCE, cues=ROLE_CUES, window=1000)
    if any(k == WEAK_CONTEXT for _, _, k in finds):
        errs.append("window tunable: a huge window should suppress WEAK_CONTEXT, got %s" % sorted(finds))

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

    # 3b. locale-aware numeric grounding: a faithful value normalized from an EU-format or scientific
    # source number still grounds; a bare US '1.234' stays US (no EU mis-read); an invented value does not.
    locale_src = "Revenue 1.234,56 EUR, yield 1.5e3 units, ratio 1.234, count 2E-4."
    for val, want_grounded in [(1234.56, True), (1500, True), (0.0002, True),
                               ("1.234", True), (9999.99, False)]:
        got = _kind(val, locale_src) not in _FAIL_KINDS
        if got != want_grounded:
            errs.append("locale grounding %r: got grounded=%s want %s (kind=%r)"
                        % (val, got, want_grounded, _kind(val, locale_src)))

    # 3c. DD.MM.YYYY-dominant dates (0.2.2): an ambiguous slashed/dotted source date keys under BOTH
    # the D/M/Y and M/D/Y readings, so a European source grounds an ISO extraction either way — while
    # an unambiguous date (day > 12) emits ONLY the valid reading (no impossible month-25 phantom key),
    # and an absent date stays ungrounded.
    #   must-GROUND
    if _kind("2026-01-02", "Fällig am 02.01.2026") != "DATE":            # D/M/Y: 2 Jan 2026
        errs.append("DD.MM date: '2026-01-02' should ground DATE against 'Fällig am 02.01.2026', got %r"
                    % _kind("2026-01-02", "Fällig am 02.01.2026"))
    if _kind("2026-12-25", "Lieferung 25/12/2026") != "DATE":           # day 25 > 12 -> D/M/Y only
        errs.append("DD/MM date: '2026-12-25' should ground DATE against '25/12/2026', got %r"
                    % _kind("2026-12-25", "Lieferung 25/12/2026"))
    if _kind("2026-02-01", "Dated 02/01/2026") != "DATE":               # M/D/Y reading still accepted
        errs.append("MDY still accepted: '2026-02-01' should ground DATE against '02/01/2026', got %r"
                    % _kind("2026-02-01", "Dated 02/01/2026"))
    #   guard: the unambiguous date must NOT emit the impossible month-25 (M/D/Y) key
    if (2026, 25, 12) in _date_keys("25/12/2026"):
        errs.append("date guard: '25/12/2026' must NOT emit the impossible month-25 M/D/Y key")
    #   must-NOT-GROUND: an absent date stays ungrounded
    if _kind("2026-07-04", "Fällig am 02.01.2026") == "DATE":
        errs.append("absent date '2026-07-04' must NOT ground against a source with no such date")

    # 3d. non-ASCII digits (0.2.2): Arabic-Indic / Eastern-Arabic / Devanagari / fullwidth digits in
    # the SOURCE (or the value) are folded to ASCII before numeric/date key extraction, so a number or
    # date written in a non-ASCII script grounds an ASCII extraction. Folding must NOT over-match (a
    # different number stays ungrounded).
    #   must-GROUND: number in a non-ASCII source; fullwidth source; non-ASCII date
    if _kind(1234, "Total ١٢٣٤") != "NUMERIC":                          # Arabic-Indic 1234
        errs.append("non-ASCII digit: 1234 should ground NUMERIC against 'Total ١٢٣٤', got %r"
                    % _kind(1234, "Total ١٢٣٤"))
    if _kind(2026, "２０２６") != "NUMERIC":                               # fullwidth 2026
        errs.append("fullwidth digit: 2026 should ground NUMERIC against '２０２６', got %r"
                    % _kind(2026, "２０２６"))
    if _kind("2026-01-02", "٢٠٢٦-٠١-٠٢") != "DATE":                      # Arabic-Indic ISO date
        errs.append("non-ASCII date: '2026-01-02' should ground DATE against '٢٠٢٦-٠١-٠٢', got %r"
                    % _kind("2026-01-02", "٢٠٢٦-٠١-٠٢"))
    if _kind(123, "रकम १२३") != "NUMERIC":                              # Devanagari 123
        errs.append("devanagari digit: 123 should ground NUMERIC against 'रकम १२३', got %r"
                    % _kind(123, "रकम १२३"))
    #   a value written in non-ASCII digits also folds for grounding against an ASCII source
    if _kind("١٢٣٤", "Total 1234") != "NUMERIC":
        errs.append("non-ASCII value: '١٢٣٤' should ground NUMERIC against 'Total 1234', got %r"
                    % _kind("١٢٣٤", "Total 1234"))
    #   must-NOT-GROUND (FP guard): a DIFFERENT number must not over-match through folding
    if _kind(5678, "Total ١٢٣٤") == "NUMERIC":
        errs.append("digit-normalize over-match: 5678 must NOT ground against 'Total ١٢٣٤'")
    #   and an all-ASCII source/value is byte-identical (no perturbation of existing behaviour)
    if _ascii_digits("Plain ASCII 1234.") != "Plain ASCII 1234.":
        errs.append("_ascii_digits perturbed an all-ASCII string")

    # 3e. SPAN EMISSION (0.2.3) — A5 provenance: --spans emits, per GROUNDED scalar, the SOURCE char
    #     offset + snippet that grounded it. The offset must point AT the real occurrence, a multi-span
    #     value must note count>1, and --spans must NOT alter the (findings, n) the gate already returns.
    prov = []
    finds_s, n_s = check(FAITHFUL, SOURCE, spans=True, provenance_out=prov)
    # (i) spans never perturb the gate: findings/n are byte-identical to the default run.
    finds_d, n_d = check(FAITHFUL, SOURCE)
    if finds_s != finds_d or n_s != n_d:
        errs.append("spans perturbed the gate: (%s,%d) != default (%s,%d)"
                    % (finds_s, n_s, finds_d, n_d))
    # (ii) every grounded scalar got a provenance row; each offset really points at its value in SOURCE.
    by_path = {p: (kind, off, snip, cnt) for p, kind, off, snip, cnt in prov}
    if "$.vendor" not in by_path:
        errs.append("spans: grounded $.vendor produced no provenance row (got %s)" % sorted(by_path))
    else:
        _, voff, vsnip, _ = by_path["$.vendor"]
        # the offset must be the literal position of "Acme Robotics Inc." in the source text
        if SOURCE.find("Acme Robotics Inc.") != voff:
            errs.append("spans: $.vendor offset %d does not point at the real 'Acme Robotics Inc.' "
                        "occurrence (expected %d)" % (voff, SOURCE.find("Acme Robotics Inc.")))
        if "Acme Robotics Inc" not in vsnip:
            errs.append("spans: $.vendor snippet %r does not contain the grounding text" % vsnip)
    # a NUMERIC offset must point at the digits in the source ("$12,000.00" -> the '1' of 12,000)
    if "$.subtotal" in by_path:
        _, soff, _, _ = by_path["$.subtotal"]
        if SOURCE[soff:soff + 2] != "12":
            errs.append("spans: $.subtotal NUMERIC offset %d should point at '12' (got %r)"
                        % (soff, SOURCE[soff:soff + 2]))
    # a DATE offset must point at the source's date span ("June 16, 2026")
    if "$.issued" in by_path:
        _, ioff, isnip, _ = by_path["$.issued"]
        if SOURCE.find("June 16, 2026") != ioff:
            errs.append("spans: $.issued DATE offset %d should point at 'June 16, 2026' (expected %d)"
                        % (ioff, SOURCE.find("June 16, 2026")))
    # (iii) a value grounding at MULTIPLE spans notes count>1 (and still emits the FIRST offset).
    multi_src = "Acme paid Acme. Acme."
    mprov = []
    check({"who": "Acme"}, multi_src, spans=True, provenance_out=mprov)
    mrow = next((r for r in mprov if r[0] == "$.who"), None)
    if not mrow:
        errs.append("spans multi: grounded $.who produced no provenance row")
    else:
        _, _, moff, _, mcount = mrow
        if mcount != 3:
            errs.append("spans multi: 'Acme' occurs 3x but count noted %d" % mcount)
        if moff != multi_src.find("Acme"):
            errs.append("spans multi: first offset %d should be the first 'Acme' at %d"
                        % (moff, multi_src.find("Acme")))
    # (iv) without --spans, the provenance_out is left untouched (no side-effect leaks into the default).
    untouched = []
    check(FAITHFUL, SOURCE, provenance_out=untouched)            # spans defaults False
    if untouched:
        errs.append("spans off: provenance_out must stay empty when spans is not set, got %s" % untouched)

    # 3f. CONFIGURABLE WEAK-GROUNDING FLOOR (0.2.3) — --min-tokens / --min-chars move the WEAK band.
    #     "Lee" is a single 3-char whole source token in SOURCE ("Dana Lee"): at the DEFAULT floor
    #     (2 tokens / 4 chars) it is below both -> WEAK_GROUNDING; raising --min-chars does nothing to
    #     it (already weak), but a value that is clean at default must FLIP to weak when the floor rises.
    #     "Dana" is a 4-char single token: at default (chars 4 is NOT < 4) it grounds clean (EXACT);
    #     with --min-chars 6 it now falls below the char floor -> WEAK_GROUNDING. That flip proves the
    #     flag changes the band.
    def _kindf(val, src, mt=MIN_TOKENS, mc=MIN_CHARS):
        return is_grounded(val, src, tokens(src, fold=False), tokens(src),
                           _source_num_keys(src), _date_keys(src), min_tokens=mt, min_chars=mc)
    # default floor: "Dana" (4 chars, 1 token) grounds clean — 4 is NOT < 4, so the char floor misses it
    if _kindf("Dana", SOURCE) != "EXACT":
        errs.append("floor default: 'Dana' (4 chars) should ground EXACT at the default floor, got %r"
                    % _kindf("Dana", SOURCE))
    # raise the char floor to 6: "Dana" now falls below BOTH floors (1<2 tokens AND 4<6 chars) -> WEAK
    if _kindf("Dana", SOURCE, mc=6) != "WEAK_GROUNDING":
        errs.append("floor --min-chars 6: 'Dana' should flip to WEAK_GROUNDING, got %r"
                    % _kindf("Dana", SOURCE, mc=6))
    # and the flip is reachable through the public check() API via its min_chars kwarg
    finds_floor, _ = check({"first": "Dana"}, SOURCE, min_chars=6)
    if {p: k for p, _, k in finds_floor}.get("$.first") != "WEAK_GROUNDING":
        errs.append("floor via check(min_chars=6): $.first 'Dana' should be WEAK_GROUNDING, got %s"
                    % finds_floor)
    # the DEFAULT (no flag) is byte-identical to before: 'Dana' clean, the existing WEAK case unchanged
    if check({"first": "Dana"}, SOURCE)[0]:
        errs.append("floor default regression: 'Dana' must stay clean with no flag, got %s"
                    % check({"first": "Dana"}, SOURCE)[0])
    if _kindf("net", FRAGMENT_SOURCE) != "WEAK_GROUNDING":   # the 0.2.0 WEAK case still weak at default
        errs.append("floor default regression: 'net' must stay WEAK at the default floor, got %r"
                    % _kindf("net", FRAGMENT_SOURCE))
    # lowering the floor can RECLASSIFY a default-weak hit as a clean grounding (the opposite direction).
    # "net" appears verbatim (case-sensitive) in FRAGMENT_SOURCE, so the clean rung is EXACT.
    if _kindf("net", FRAGMENT_SOURCE, mt=1, mc=1) != "EXACT":
        errs.append("floor --min-tokens 1 --min-chars 1: 'net' should now ground clean (EXACT), got %r"
                    % _kindf("net", FRAGMENT_SOURCE, mt=1, mc=1))

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
              "normalize/numeric/date ladder verified (EU/sci + DD.MM dates + non-ASCII digits), "
              "proximity cues opt-in (WEAK_CONTEXT advisory)")
        return 0

    # parse args: <extraction.json> <source.txt> [cues.json] [--window N] [--spans]
    #             [--min-tokens N] [--min-chars N] — order-flexible for the flags.
    window = DEFAULT_CUE_WINDOW
    min_tokens = MIN_TOKENS
    min_chars = MIN_CHARS
    spans = False
    positional = []
    # integer-valued flags share one parser (both --flag N and --flag=N forms); --spans is a bare bool.
    _int_flags = {"--window": "window", "--min-tokens": "min_tokens", "--min-chars": "min_chars"}
    int_vals = {"window": window, "min_tokens": min_tokens, "min_chars": min_chars}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--spans":
            spans = True
        elif a in _int_flags:
            i += 1
            if i >= len(argv) or not argv[i].lstrip("-").isdigit():
                sys.stderr.write("%s needs an integer\n" % a)
                return 2
            int_vals[_int_flags[a]] = int(argv[i])
        elif "=" in a and a.split("=", 1)[0] in _int_flags:
            name, v = a.split("=", 1)
            if not v.lstrip("-").isdigit():
                sys.stderr.write("%s needs an integer\n" % name)
                return 2
            int_vals[_int_flags[name]] = int(v)
        else:
            positional.append(a)
        i += 1
    window, min_tokens, min_chars = int_vals["window"], int_vals["min_tokens"], int_vals["min_chars"]

    if len(positional) < 2:
        sys.stderr.write("usage: groundedness-check.py <extraction.json> <source.txt> "
                         "[cues.json] [--window N] [--spans] [--min-tokens N] [--min-chars N]\n")
        return 2
    try:
        extraction = json.load(open(positional[0], encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write("cannot read extraction: %s\n" % e)
        return 2
    try:
        source = open(positional[1], encoding="utf-8").read()
    except OSError as e:
        sys.stderr.write("cannot read source: %s\n" % e)
        return 2
    cues = None
    if len(positional) >= 3:
        try:
            cues = json.load(open(positional[2], encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            sys.stderr.write("cannot read cues: %s\n" % e)
            return 2
        if not isinstance(cues, dict):
            sys.stderr.write("cues.json must be an object: {\"field\": [\"cue\", ...], ...}\n")
            return 2

    provenance = [] if spans else None
    findings, n = check(extraction, source, cues=cues, window=window,
                        min_tokens=min_tokens, min_chars=min_chars,
                        spans=spans, provenance_out=provenance)
    for path, value, kind in findings:
        v = repr(value)
        note = {"UNGROUNDED": "", "WEAK_GROUNDING": "  (short match — verify manually)",
                "EMPTY": "  (empty value)",
                WEAK_CONTEXT: "  (grounded but not near a '%s' cue — possible wrong-span; verify the "
                              "role via adversarial cross-check)" % _leaf_field(path)}.get(kind, "")
        print("  %-14s %-28s %s%s" % (kind, path, v if len(v) <= 50 else v[:47] + "...", note))

    # A5 PROVENANCE (--spans): for each GROUNDED scalar, print the source span that grounded it. This is
    # additive output — it appears ONLY under --spans and does NOT change the exit code or the findings.
    if spans and provenance:
        print("  --- provenance (--spans): %d grounded scalar(s) located in the source ---"
              % len(provenance))
        for path, kind, offset, snippet, count in provenance:
            multi = "  (%d spans — ambiguous; the adversarial verifier should disambiguate)" % count \
                if count > 1 else ""
            snip = snippet if len(snippet) <= 60 else snippet[:57] + "…"
            print("  %-12s %-26s @%-7d %r%s" % (kind, path, offset, snip, multi))

    # WEAK_CONTEXT is ADVISORY: it does NOT affect the exit code (it only APPROXIMATES wrong-span; role
    # is confirmed by the adversarial verifier, not this gate). The exit is driven by _FAIL_KINDS only.
    fails = [f for f in findings if f[2] in _FAIL_KINDS]
    advisories = [f for f in findings if f[2] == WEAK_CONTEXT]
    if fails:
        # honest wording (m1): some of these are FALSE POSITIVES (a locale/scientific-notation value,
        # an over-normalization that nonetheless preserves meaning). Say "verify", do not assert.
        extra = (" (+%d WEAK_CONTEXT advisory — possible wrong-span, does not affect exit)"
                 % len(advisories)) if advisories else ""
        sys.stderr.write("groundedness-check: FAIL — %d of %d scalar(s) not cleanly grounded in the "
                         "source — verify each against the source before shipping (an ungrounded "
                         "scalar is a LIKELY but not certain hallucination)%s\n"
                         % (len(fails), n, extra))
        return 1
    if advisories:
        # grounded, but proximity is suspicious — pass the gate, but say so clearly.
        print("groundedness-check: OK — all %d scalar value(s) grounded in the source; %d WEAK_CONTEXT "
              "advisory (grounded but not near its field cue — possible wrong-span; confirm the role "
              "with the adversarial verifier, see references/fidelity-axis.md)" % (n, len(advisories)))
        return 0
    print("groundedness-check: OK — all %d scalar value(s) grounded in the source" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
