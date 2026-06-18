#!/usr/bin/env python3
"""contrast-check.py — the color-verifier mechanism gate. Self-contained (stdlib only).

color-verifier owns the *how* of color: it derives OKLCH ramps and proves they behave.
Two things matter when judging a palette, and they are different in kind:

  - WCAG 2.x contrast is ARITHMETIC — sRGB → linearized relative luminance → (L1+0.05)/(L2+0.05).
    An LLM eyeballing "looks fine" fails silently here, so the contrast floor is ROUTED TO CODE:
    this gate computes the ratio and flags any pair under its AA floor. (computation → code.)
  - CVD safety and perceptual evenness are PERCEPTUAL JUDGMENT — they stay a review in SKILL.md.

A "color surface card" is the small declarative artifact the skill emits (or re-derives when
grading a palette) listing the foreground/background pairs that carry text or UI indication:

  {
    "pairs": [
      {"name": "body text",   "fg": "#1a1a1a", "bg": "#ffffff", "size": "normal", "role": "text"},
      {"name": "muted label", "fg": "#767676", "bg": "#ffffff", "size": "normal", "role": "text"},
      {"name": "card border",  "fg": "#949494", "bg": "#ffffff", "size": "normal", "role": "ui"}
    ]
  }

Per pair (all keys optional except fg + bg):
  name  — a label for the report (default "<pair>")
  fg/bg — the foreground and background colors. Accepts #rgb, #rrggbb, or rgb()/rgba(...).
          rgba alpha is IGNORED (contrast is judged on the opaque color; compositing is a review).
  size  — "normal" (default) | "large"   — large text is 18.66px bold or 24px+ regular.
  role  — "text" (default) | "ui"         — ui/non-text (borders, focus rings, icons, controls).

Flags (per the contrast floors in verification/contrast-pairs.json):
  CONTRAST_FAIL_AA  (gate)      text below 4.5 (normal) / 3.0 (large); ui/non-text below 3.0.
  CONTRAST_FAIL_AAA (advisory)  text below 7.0 (normal) / 4.5 (large) — only when AA already passes.

A malformed color (bad hex, out-of-range rgb, unparseable) yields a clear per-pair error, not a
crash. This gate is a PRE-FILTER, not an oracle: clearing it means the arithmetic floor holds — it
does NOT prove the palette CVD-safe or perceptually even. Confirm those in review.

  python3 bin/contrast-check.py selftest
  python3 bin/contrast-check.py <card.json | dir>
  python3 bin/contrast-check.py --json <card.json>

Python 3.8+.
"""
import json
import os
import re
import sys

# WCAG 2.x contrast floors --------------------------------------------------------------------
# keyed (role, size) -> (AA floor, AAA floor). ui/non-text has no separate large/AAA tier (1.4.11).
AA = {
    ("text", "normal"): 4.5,
    ("text", "large"):  3.0,
    ("ui",   "normal"): 3.0,
    ("ui",   "large"):  3.0,
}
AAA = {
    ("text", "normal"): 7.0,
    ("text", "large"):  4.5,
    # ui/non-text: 3.0 is the only graphical floor; AAA does not raise it -> no advisory tier.
    ("ui",   "normal"): None,
    ("ui",   "large"):  None,
}

_RGB_RE = re.compile(r"rgba?\(\s*([^)]*)\)", re.IGNORECASE)


class ColorError(ValueError):
    """A color string that cannot be parsed into an sRGB triple."""


def parse_color(s):
    """Parse '#rgb' | '#rrggbb' | 'rgb(...)' | 'rgba(...)' into an (r, g, b) 0-255 int triple.

    Alpha (rgba 4th channel) is parsed-and-discarded — contrast is judged on the opaque color.
    Raises ColorError on anything malformed (so a bad card reports an error, never crashes)."""
    if not isinstance(s, str):
        raise ColorError("color must be a string, got %r" % (s,))
    t = s.strip()
    if t.startswith("#"):
        h = t[1:]
        if len(h) == 3:
            if not re.fullmatch(r"[0-9a-fA-F]{3}", h):
                raise ColorError("bad hex %r" % s)
            return tuple(int(c * 2, 16) for c in h)
        if len(h) == 6:
            if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
                raise ColorError("bad hex %r" % s)
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        raise ColorError("hex must be #rgb or #rrggbb, got %r" % s)
    m = _RGB_RE.fullmatch(t)
    if m:
        parts = [p.strip() for p in re.split(r"[,\s/]+", m.group(1).strip()) if p.strip()]
        if len(parts) not in (3, 4):
            raise ColorError("rgb() needs 3 or 4 components, got %r" % s)
        out = []
        for p in parts[:3]:
            if p.endswith("%"):
                v = float(p[:-1]) / 100.0 * 255.0
            else:
                v = float(p)
            if not (0 <= v <= 255):
                raise ColorError("rgb component out of range in %r" % s)
            out.append(int(round(v)))
        return tuple(out)
    raise ColorError("unrecognized color %r (use #rgb, #rrggbb, or rgb()/rgba())" % s)


def _lin(c):
    """sRGB 8-bit channel -> linear-light component (WCAG 2.x transfer)."""
    cs = c / 255.0
    return cs / 12.92 if cs <= 0.03928 else ((cs + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb):
    r, g, b = rgb
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast_ratio(fg, bg):
    """WCAG 2.x contrast ratio of two sRGB triples: (Llight + 0.05) / (Ldark + 0.05) ∈ [1, 21]."""
    l1, l2 = relative_luminance(fg), relative_luminance(bg)
    hi, lo = (l1, l2) if l1 >= l2 else (l2, l1)
    return (hi + 0.05) / (lo + 0.05)


def check_pair(pair):
    """Return (fails, warns) for one pair card. fails = AA gate + parse errors; warns = AAA advisory."""
    fails, warns = [], []
    name = pair.get("name", "<pair>")
    role = (pair.get("role") or "text").lower()
    size = (pair.get("size") or "normal").lower()
    if role not in ("text", "ui"):
        fails.append("%s: role %r not in {text, ui}" % (name, role))
        role = "text"
    if size not in ("normal", "large"):
        fails.append("%s: size %r not in {normal, large}" % (name, size))
        size = "normal"

    try:
        fg = parse_color(pair.get("fg"))
        bg = parse_color(pair.get("bg"))
    except ColorError as e:
        fails.append("%s: %s" % (name, e))
        return fails, warns

    ratio = contrast_ratio(fg, bg)
    aa = AA[(role, size)]
    if ratio < aa:
        fails.append("CONTRAST_FAIL_AA — %s: %.2f:1 (%s, %s) below AA floor %.1f:1"
                     % (name, ratio, role, size, aa))
        return fails, warns  # already an AA fail; AAA advisory only applies once AA passes

    aaa = AAA[(role, size)]
    if aaa is not None and ratio < aaa:
        warns.append("CONTRAST_FAIL_AAA — %s: %.2f:1 (%s %s) passes AA %.1f but below AAA floor %.1f:1"
                     % (name, ratio, role, size, aa, aaa))
    return fails, warns


def check_card(card):
    """Return (fails, warns, n) for a surface card ({"pairs": [...]}) or a bare pair list."""
    if isinstance(card, dict) and "pairs" in card:
        pairs = card["pairs"]
    elif isinstance(card, list):
        pairs = card
    elif isinstance(card, dict):
        pairs = [card]  # a single bare pair card
    else:
        return ["card is not an object or list"], [], 0
    if not isinstance(pairs, list):
        return ["'pairs' must be a list"], [], 0
    fails, warns = [], []
    for p in pairs:
        if not isinstance(p, dict):
            fails.append("pair entry is not an object: %r" % (p,))
            continue
        f, w = check_pair(p)
        fails += f
        warns += w
    return fails, warns, len(pairs)


# --- selftest fixtures -------------------------------------------------------------------------
# must-FLAG (AA gate fails)
BAD_777 = {"pairs": [{"name": "muted", "fg": "#777", "bg": "#fff", "size": "normal", "role": "text"}]}  # ~4.48 < 4.5
BAD_3TO1_AS_TEXT = {"pairs": [{"name": "thin text", "fg": "#949494", "bg": "#ffffff",
                               "size": "normal", "role": "text"}]}                                       # ~3.03 < 4.5
# must-NOT-flag (AA passes)
OK_DARK = {"pairs": [{"name": "body", "fg": "#111", "bg": "#fff", "size": "normal", "role": "text"}]}    # ~18.88
OK_767676 = {"pairs": [{"name": "label", "fg": "#767676", "bg": "#ffffff",
                        "size": "normal", "role": "text"}]}                                              # ~4.54 >= 4.5
OK_3TO1_LARGE = {"pairs": [{"name": "big head", "fg": "#949494", "bg": "#ffffff",
                            "size": "large", "role": "text"}]}                                           # ~3.03 >= 3.0
OK_3TO1_UI = {"pairs": [{"name": "border", "fg": "#949494", "bg": "#ffffff", "role": "ui"}]}             # ~3.03 >= 3.0
# AAA advisory (passes AA, below AAA) — a WARN, never a FAIL
AAA_ADVISORY = {"pairs": [{"name": "label", "fg": "#767676", "bg": "#fff", "size": "normal", "role": "text"}]}
# malformed color -> a clear error, not a crash
BAD_COLOR = {"pairs": [{"name": "typo", "fg": "#gggggg", "bg": "#fff"}]}
BAD_RGB_RANGE = {"pairs": [{"name": "oob", "fg": "rgb(300, 0, 0)", "bg": "#fff"}]}
# rgb()/rgba() accepted; alpha ignored
OK_RGB = {"pairs": [{"name": "rgb body", "fg": "rgb(17,17,17)", "bg": "rgba(255,255,255,0.5)",
                     "size": "normal", "role": "text"}]}


def selftest():
    errs = []

    # --- 1. ratio math is correct against a known value -------------------------------------
    r_777 = contrast_ratio((0x77, 0x77, 0x77), (0xff, 0xff, 0xff))
    if not (4.47 < r_777 < 4.49):
        errs.append("ratio #777/#fff = %.4f, expected ~4.48" % r_777)
    r_767 = contrast_ratio((0x76, 0x76, 0x76), (0xff, 0xff, 0xff))
    if not (4.53 < r_767 < 4.55):
        errs.append("ratio #767676/#fff = %.4f, expected ~4.54" % r_767)
    if abs(contrast_ratio((0, 0, 0), (255, 255, 255)) - 21.0) > 0.01:
        errs.append("black-on-white must be 21:1")
    if abs(contrast_ratio((255, 255, 255), (255, 255, 255)) - 1.0) > 1e-9:
        errs.append("white-on-white must be 1:1")
    # order-independent (max/min in numerator/denominator)
    if abs(contrast_ratio((0x77,)*3, (0xff,)*3) - contrast_ratio((0xff,)*3, (0x77,)*3)) > 1e-9:
        errs.append("ratio must be symmetric in fg/bg")

    def fails_of(c):
        return check_card(c)[0]

    def warns_of(c):
        return check_card(c)[1]

    # --- 2. must-FLAG --------------------------------------------------------------------------
    if not any("CONTRAST_FAIL_AA" in f for f in fails_of(BAD_777)):
        errs.append("#777 on #fff (~4.48) as normal text not flagged AA-fail")
    if not any("CONTRAST_FAIL_AA" in f for f in fails_of(BAD_3TO1_AS_TEXT)):
        errs.append("3:1 pair as normal text not flagged AA-fail")

    # --- 3. must-NOT-flag ----------------------------------------------------------------------
    if fails_of(OK_DARK):
        errs.append("#111 on #fff wrongly flagged: %s" % fails_of(OK_DARK))
    if fails_of(OK_767676):
        errs.append("#767676 on #fff (~4.54) wrongly flagged AA-fail: %s" % fails_of(OK_767676))
    if warns_of(OK_767676):  # ~4.54 also clears... no: 4.54 < 7.0 so it SHOULD warn AAA — checked below
        pass
    if fails_of(OK_3TO1_LARGE):
        errs.append("3:1 pair as LARGE text wrongly flagged: %s" % fails_of(OK_3TO1_LARGE))
    if fails_of(OK_3TO1_UI):
        errs.append("3:1 pair as UI role wrongly flagged: %s" % fails_of(OK_3TO1_UI))

    # --- 4. AAA advisory is a WARN, never a FAIL ----------------------------------------------
    if fails_of(AAA_ADVISORY):
        errs.append("AAA-only shortfall produced a FAIL (must be advisory): %s" % fails_of(AAA_ADVISORY))
    if not any("CONTRAST_FAIL_AAA" in w for w in warns_of(AAA_ADVISORY)):
        errs.append("#767676 on #fff (~4.54, < AAA 7.0) not warned AAA")
    # a UI-role pass must NOT emit an AAA advisory (no AAA tier for graphics)
    if warns_of(OK_3TO1_UI):
        errs.append("UI-role pass wrongly emitted an AAA advisory: %s" % warns_of(OK_3TO1_UI))
    # a deep-contrast pass clears BOTH AA and AAA — no warn at all
    if warns_of(OK_DARK):
        errs.append("#111 on #fff (>AAA) wrongly emitted an AAA advisory: %s" % warns_of(OK_DARK))

    # --- 5. malformed colors -> clear error, not a crash --------------------------------------
    if not any("typo" in f for f in fails_of(BAD_COLOR)):
        errs.append("malformed hex not reported as an error")
    if not any("oob" in f for f in fails_of(BAD_RGB_RANGE)):
        errs.append("out-of-range rgb() not reported as an error")

    # --- 6. rgb()/rgba() parsing (alpha ignored) ----------------------------------------------
    if fails_of(OK_RGB):
        errs.append("rgb()/rgba() body text wrongly flagged: %s" % fails_of(OK_RGB))
    if parse_color("#abc") != (0xaa, 0xbb, 0xcc):
        errs.append("#abc shorthand expansion wrong")
    if parse_color("rgb(50%, 0%, 100%)") != (128, 0, 255):
        errs.append("percentage rgb() parse wrong: %r" % (parse_color("rgb(50%, 0%, 100%)"),))

    return errs


def _iter_cards(path):
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            for fn in sorted(fns):
                if fn.endswith(".surface.json") or fn.endswith(".contrast.json"):
                    yield os.path.join(dp, fn)
    else:
        yield path


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("contrast-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("contrast-check: OK — WCAG ratio math + AA gate + AAA advisory verified over good/bad fixtures")
        return 0

    as_json = False
    args = list(argv)
    if args and args[0] == "--json":
        as_json = True
        args = args[1:]
    if not args:
        sys.stderr.write("usage: contrast-check.py [--json] <card.json | dir>\n")
        return 2

    fails, warns, n = [], [], 0
    for fp in _iter_cards(args[0]):
        try:
            doc = json.load(open(fp, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            fails.append("%s: unreadable (%s)" % (fp, e))
            continue
        for card in (doc if isinstance(doc, list) else [doc]):
            f, w, c = check_card(card)
            fails += f
            warns += w
            n += c

    if as_json:
        out = {"pairs_checked": n, "fails": fails, "warns": warns,
               "status": "FAIL" if fails else "OK"}
        print(json.dumps(out, indent=2))
        return 1 if fails else 0

    for w in warns:
        print("  ⚠ %s" % w)
    if fails:
        sys.stderr.write("contrast-check: FAIL (%d)\n" % len(fails))
        for f in fails:
            sys.stderr.write("  - %s\n" % f)
        return 1
    print("contrast-check: OK — %d pair(s) clear the AA contrast floor" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
