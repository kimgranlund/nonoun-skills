#!/usr/bin/env python3
"""i18n-check.py — the i18n-verifier mechanism gate. Self-contained (stdlib only).

i18n-verifier owns the *locale* layer of a UI system. Two kinds of i18n defect matter, and they
are different in kind:

  - dir/lang presence and the existence of hardcoded (untranslated) string literals are MECHANICAL
    ATTRIBUTES of a surface — a surface either declares `dir`/`lang` or it does not; a string is
    either externalized or it is a literal in the markup. An LLM eyeballing "looks localized" misses
    a missing `dir` exactly where it matters, so these are ROUTED TO CODE (computation → code).
  - whether a *translation reads naturally*, whether the chosen line-height suits a script, whether
    a mirroring policy is the right one — those are JUDGMENT and stay a review in SKILL.md.

An "i18n surface card" is the small declarative artifact the skill emits (or re-derives when
auditing a UI). It lists the text-bearing surfaces and the system-wide locale posture:

  {
    "surfaces": [
      {"id": "header",  "has_lang": true,  "has_dir": true,  "hardcoded_strings": ["Save","Cancel"], "expansion_safe": false},
      {"id": "footer",  "has_lang": true,  "has_dir": true,  "hardcoded_strings": [],                 "expansion_safe": true}
    ],
    "rtl_supported": false,
    "locale_formats": {"dates": false, "numbers": true, "currency": false}
  }

Per surface (all keys optional except `id`):
  id                — a label for the report.
  has_lang          — surface (or a declared ancestor) carries `lang`. Absent/false on a text surface → MISSING_LANG.
  has_dir           — surface carries `dir`. Absent/false on a text surface → MISSING_DIR.
  hardcoded_strings — list of untranslated string literals found on the surface. Non-empty → HARDCODED_STRING.
  expansion_safe    — surface reserves text-expansion headroom (fluid / min-content / longest-locale). false → NO_EXPANSION_ROOM (advisory).
  text              — optional explicit flag. A surface is "text-bearing" if text:true, OR it declares
                      any of has_lang/has_dir/hardcoded_strings (the default — a surface that mentions
                      these is reasoning about text). Set text:false to mark a non-text surface (skips lang/dir).

Top-level posture (both optional):
  rtl_supported   — the system handles RTL/bidi (logical axes, dir flipping). false → NO_RTL (advisory; escalates if a
                    surface's has_dir handling implies RTL is in scope).
  locale_formats  — {dates, numbers, currency} each true if that family routes through Intl.*; any false → NO_LOCALE_FORMAT (advisory).

Flags:
  MISSING_LANG       (gate)      a text surface with has_lang false/absent — no declared language.
  MISSING_DIR        (gate)      a text surface with has_dir false/absent — no declared direction.
  HARDCODED_STRING   (gate)      a surface whose hardcoded_strings[] is non-empty — untranslated literals.
  NO_EXPANSION_ROOM  (advisory)  expansion_safe:false — DE/FI/RU run ~+35-100% longer; the surface may crop/overflow.
  NO_RTL             (advisory)  rtl_supported:false — escalated to a stronger advisory if any surface declares dir handling.
  NO_LOCALE_FORMAT   (advisory)  a locale_formats family is false — dates/numbers/currency not localized via Intl.*.

Absent data is SKIPPED, not silently passed: a card with no `surfaces`, no `rtl_supported`, and no
`locale_formats` reports each missing section as a skip (so an empty card is never a false "OK").
A malformed card (not an object, surfaces not a list, a surface not an object) yields a clear error,
not a crash. This gate is a PRE-FILTER, not an oracle: clearing it means dir/lang are present and no
hardcoded literals were declared — it does NOT prove the translations read naturally, the scripts are
metrically correct, or the bidi isolation is right. Confirm those in review.

  python3 bin/i18n-check.py selftest
  python3 bin/i18n-check.py <card.json | dir>
  python3 bin/i18n-check.py --json <card.json>

Python 3.8+.
"""
import json
import os
import sys

LOCALE_FORMAT_FAMILIES = ("dates", "numbers", "currency")


def _is_text_surface(surface):
    """A surface is text-bearing unless it explicitly says text:false. A surface that declares any of
    has_lang / has_dir / hardcoded_strings is reasoning about text, so it defaults to text-bearing."""
    if "text" in surface:
        return bool(surface.get("text"))
    return any(k in surface for k in ("has_lang", "has_dir", "hardcoded_strings"))


def check_card(card):
    """Return (fails, warns, skips) for one i18n surface card.

    fails  — gate violations (MISSING_LANG / MISSING_DIR / HARDCODED_STRING).
    warns  — advisories (NO_EXPANSION_ROOM / NO_RTL / NO_LOCALE_FORMAT).
    skips  — sections absent from the card (reported, never silently passed).
    """
    fails, warns, skips = [], [], []

    if not isinstance(card, dict):
        fails.append("<card>: card is not an object (got %s)" % type(card).__name__)
        return fails, warns, skips

    # --- surfaces ---------------------------------------------------------------------------
    surfaces = card.get("surfaces")
    any_dir_handling = False
    if surfaces is None:
        skips.append("no surfaces[] — per-surface lang/dir/hardcoded-string checks skipped")
    elif not isinstance(surfaces, list):
        fails.append("surfaces: must be a list (got %s)" % type(surfaces).__name__)
    elif not surfaces:
        skips.append("surfaces[] is empty — per-surface checks skipped")
    else:
        for i, surface in enumerate(surfaces):
            if not isinstance(surface, dict):
                fails.append("surfaces[%d]: must be an object (got %s)" % (i, type(surface).__name__))
                continue
            sid = surface.get("id", "surface[%d]" % i)

            hardcoded = surface.get("hardcoded_strings")
            if hardcoded is not None and not isinstance(hardcoded, list):
                fails.append("%s: hardcoded_strings must be a list (got %s)"
                             % (sid, type(hardcoded).__name__))
                hardcoded = None

            text = _is_text_surface(surface)

            # --- gate: a text surface must declare lang + dir (mechanical attributes) ---
            if text:
                if not surface.get("has_lang"):
                    fails.append("%s: MISSING_LANG — text surface declares no `lang` "
                                 "(direction is declared, not inferred)" % sid)
                if not surface.get("has_dir"):
                    fails.append("%s: MISSING_DIR — text surface declares no `dir` "
                                 "(direction is declared, not inferred)" % sid)
            if surface.get("has_dir"):
                any_dir_handling = True

            # --- gate: hardcoded (untranslated) string literals ---
            if hardcoded:
                fails.append("%s: HARDCODED_STRING — %d untranslated literal(s) %s — externalize for "
                             "translation (don't concatenate; use ICU MessageFormat)"
                             % (sid, len(hardcoded), list(hardcoded)))

            # --- advisory: text-expansion headroom ---
            if text and "expansion_safe" in surface and not surface.get("expansion_safe"):
                warns.append("%s: NO_EXPANSION_ROOM — reserves no expansion headroom; DE/FI ~+35%%, "
                             "RU ~+100%% — fluid width or longest-locale sizing, no silent truncation" % sid)

    # --- top-level: RTL posture -------------------------------------------------------------
    if "rtl_supported" not in card:
        skips.append("no rtl_supported — RTL/bidi posture check skipped")
    elif not card.get("rtl_supported"):
        if any_dir_handling:
            warns.append("NO_RTL — rtl_supported:false, yet a surface declares `dir` handling "
                         "(RTL appears in scope) — logical axes + dir flipping needed")
        else:
            warns.append("NO_RTL — rtl_supported:false — RTL/bidi (Arabic/Hebrew/Persian/Urdu) "
                         "not handled; logical axes keep this cheap if added later")

    # --- top-level: locale formatting -------------------------------------------------------
    lf = card.get("locale_formats")
    if lf is None:
        skips.append("no locale_formats — number/date/currency Intl-formatting check skipped")
    elif not isinstance(lf, dict):
        fails.append("locale_formats: must be an object (got %s)" % type(lf).__name__)
    else:
        for fam in LOCALE_FORMAT_FAMILIES:
            if fam not in lf:
                skips.append("locale_formats.%s absent — %s formatting check skipped" % (fam, fam))
            elif not lf.get(fam):
                warns.append("NO_LOCALE_FORMAT — %s not localized; route through Intl.* "
                             "(Intl.NumberFormat / DateTimeFormat) — not hardcoded/concatenated" % fam)

    return fails, warns, skips


# --- selftest fixtures -------------------------------------------------------------------------
GOOD = {
    "surfaces": [
        {"id": "header", "has_lang": True, "has_dir": True, "hardcoded_strings": [], "expansion_safe": True},
        {"id": "footer", "has_lang": True, "has_dir": True, "hardcoded_strings": [], "expansion_safe": True},
    ],
    "rtl_supported": True,
    "locale_formats": {"dates": True, "numbers": True, "currency": True},
}
BAD_MISSING_LANG = {
    "surfaces": [{"id": "banner", "has_lang": False, "has_dir": True, "hardcoded_strings": []}],
    "rtl_supported": True,
    "locale_formats": {"dates": True, "numbers": True, "currency": True},
}
BAD_HARDCODED = {
    "surfaces": [{"id": "toolbar", "has_lang": True, "has_dir": True,
                  "hardcoded_strings": ["Save", "Cancel"], "expansion_safe": True}],
    "rtl_supported": True,
    "locale_formats": {"dates": True, "numbers": True, "currency": True},
}
WARN_EXPANSION = dict(GOOD, surfaces=[{"id": "label", "has_lang": True, "has_dir": True,
                                       "hardcoded_strings": [], "expansion_safe": False}])
WARN_NO_RTL = dict(GOOD, rtl_supported=False)
WARN_NO_RTL_SCOPED = {  # rtl false BUT a surface declares dir handling -> escalated advisory
    "surfaces": [{"id": "rtl-pane", "has_lang": True, "has_dir": True, "hardcoded_strings": []}],
    "rtl_supported": False,
    "locale_formats": {"dates": True, "numbers": True, "currency": True},
}
WARN_NO_LOCALE_FORMAT = dict(GOOD, locale_formats={"dates": False, "numbers": True, "currency": False})
EMPTY = {}  # all sections absent -> all skipped, never a false OK
NON_TEXT = {  # a surface explicitly not text-bearing skips the lang/dir gate
    "surfaces": [{"id": "spacer", "text": False}],
    "rtl_supported": True,
    "locale_formats": {"dates": True, "numbers": True, "currency": True},
}
MALFORMED_CARD = ["not", "an", "object"]
MALFORMED_SURFACE = {"surfaces": "header,footer"}
MALFORMED_HARDCODED = {"surfaces": [{"id": "x", "has_lang": True, "has_dir": True, "hardcoded_strings": "Save"}]}


def selftest():
    errs = []

    def fails_of(c):
        return check_card(c)[0]

    def warns_of(c):
        return check_card(c)[1]

    def skips_of(c):
        return check_card(c)[2]

    # must-NOT-flag: the clean card raises no gate fails and no advisories
    if fails_of(GOOD):
        errs.append("GOOD card produced fails: %s" % fails_of(GOOD))
    if warns_of(GOOD):
        errs.append("GOOD card produced warns: %s" % warns_of(GOOD))

    # must-FLAG: gate fails
    if not any("MISSING_LANG" in f for f in fails_of(BAD_MISSING_LANG)):
        errs.append("has_lang:false not caught as MISSING_LANG")
    if not any("HARDCODED_STRING" in f for f in fails_of(BAD_HARDCODED)):
        errs.append("non-empty hardcoded_strings not caught as HARDCODED_STRING")
    # a missing has_dir (absent, not just false) is also a gate fail
    if not any("MISSING_DIR" in f for f in fails_of(
            {"surfaces": [{"id": "n", "has_lang": True, "hardcoded_strings": []}]})):
        errs.append("absent has_dir not caught as MISSING_DIR")

    # advisories
    if not any("NO_EXPANSION_ROOM" in w for w in warns_of(WARN_EXPANSION)):
        errs.append("expansion_safe:false not warned as NO_EXPANSION_ROOM")
    if fails_of(WARN_EXPANSION):
        errs.append("NO_EXPANSION_ROOM wrongly escalated to a gate fail")
    if not any("NO_RTL" in w for w in warns_of(WARN_NO_RTL)):
        errs.append("rtl_supported:false not warned as NO_RTL")
    if not any("appears in scope" in w for w in warns_of(WARN_NO_RTL_SCOPED)):
        errs.append("NO_RTL not escalated when a surface declares dir handling")
    if not any("NO_LOCALE_FORMAT" in w for w in warns_of(WARN_NO_LOCALE_FORMAT)):
        errs.append("a false locale_formats family not warned as NO_LOCALE_FORMAT")
    # exactly two families are false -> exactly two NO_LOCALE_FORMAT advisories
    if sum("NO_LOCALE_FORMAT" in w for w in warns_of(WARN_NO_LOCALE_FORMAT)) != 2:
        errs.append("NO_LOCALE_FORMAT count != 2 false families")

    # skip-don't-silently-pass: an empty card reports skips and never a clean OK
    if fails_of(EMPTY) or warns_of(EMPTY):
        errs.append("empty card produced fails/warns instead of skips")
    if len(skips_of(EMPTY)) < 3:
        errs.append("empty card did not skip all 3 sections (surfaces, rtl, locale_formats)")

    # a non-text surface skips the lang/dir gate
    if fails_of(NON_TEXT):
        errs.append("non-text surface (text:false) wrongly hit the lang/dir gate")

    # malformed input -> clean error, not a crash
    if not any("not an object" in f for f in fails_of(MALFORMED_CARD)):
        errs.append("malformed card (a list) not reported as a clean error")
    if not any("surfaces" in f and "list" in f for f in fails_of(MALFORMED_SURFACE)):
        errs.append("surfaces-not-a-list not reported as a clean error")
    if not any("hardcoded_strings must be a list" in f for f in fails_of(MALFORMED_HARDCODED)):
        errs.append("hardcoded_strings-not-a-list not reported as a clean error")

    return errs


def _iter_cards(path):
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            for fn in sorted(fns):
                if fn.endswith(".i18n.json"):
                    yield os.path.join(dp, fn)
    else:
        yield path


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("i18n-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("i18n-check: OK — gate + advisory + skip checks verified over good/bad fixtures")
        return 0

    as_json = False
    if argv and argv[0] == "--json":
        as_json = True
        argv = argv[1:]
    if not argv:
        sys.stderr.write("usage: i18n-check.py [--json] <card.json | dir>\n")
        return 2

    fails, warns, skips, n = [], [], [], 0
    for fp in _iter_cards(argv[0]):
        try:
            doc = json.load(open(fp, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            fails.append("%s: unreadable (%s)" % (fp, e))
            continue
        for card in (doc if isinstance(doc, list) else [doc]):
            n += 1
            f, w, s = check_card(card)
            fails += f
            warns += w
            skips += s

    if as_json:
        print(json.dumps({"cards": n, "pass": not fails, "fails": fails,
                          "warns": warns, "skips": skips}, indent=2))
        return 1 if fails else 0

    for s in skips:
        print("  · skip: %s" % s)
    for w in warns:
        print("  ⚠ %s" % w)
    if fails:
        sys.stderr.write("i18n-check: FAIL (%d)\n" % len(fails))
        for f in fails:
            sys.stderr.write("  - %s\n" % f)
        return 1
    print("i18n-check: OK — %d card(s) clear the gates" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
