#!/usr/bin/env python3
"""geometry-check.py — the component-decomposer geometry engine. Self-contained (stdlib only).

The button is the base unit of the system (input, select, menu-item, badge, tag, and container
insets all derive from it). Its box model is governed by ONE law:

    edge padding for any glyph = (height - glyph) / 2

i.e. every glyph (icon or caret) is centered in a SQUARE cell of side = the button height. Two
consequences fall straight out of that law and are the engine's reason to exist:

  1. an icon-only (or caret-only) button is exactly SQUARE — width == height;
  2. the asymmetric inline padding (icon side vs caret side) is NOT a free design value — it is
     forced by icon != caret size. The icon side gets (h-icon)/2, the caret side gets (h-caret)/2.

So the only FREE per-size values are: height, icon, caret, font, spacer. Everything else is computed.
This script holds the canonical XS..2XL ramp, computes the derived geometry, lays out any
slot permutation, validates a component's declared geometry against the ramp, and proves the law
against the hand-authored source table in `selftest`.

  python3 bin/geometry-check.py selftest                  # prove the law + permutations round-trip
  python3 bin/geometry-check.py ramp                       # print the full computed ramp
  python3 bin/geometry-check.py layout XL icon,label,caret # box-model segments for one permutation
  python3 bin/geometry-check.py validate spec.json         # check a declared geometry against the ramp

Python 3.8+.
"""
import json
import sys

SIZES = ["2XL", "XL", "LG", "MD", "SM", "XS"]

# --- the only free per-size design values (height, icon, caret, font, spacer) ------------------
# spacer is the gap flanking the label and between adjacent glyphs. Larger tiers use 8, tight
# tiers use 4 (the split lands at height >= 36 / font >= 16).
FREE = {
    "2XL": {"height": 64, "icon": 28, "caret": 18, "font": 20, "spacer": 8},
    "XL":  {"height": 48, "icon": 24, "caret": 16, "font": 18, "spacer": 8},
    "LG":  {"height": 36, "icon": 20, "caret": 14, "font": 16, "spacer": 8},
    "MD":  {"height": 28, "icon": 18, "caret": 14, "font": 14, "spacer": 4},
    "SM":  {"height": 24, "icon": 16, "caret": 12, "font": 13, "spacer": 4},
    "XS":  {"height": 20, "icon": 14, "caret": 12, "font": 12, "spacer": 4},
}

# the hand-authored source table — the ground truth `selftest` proves the derived paddings against.
# (left = icon-side padding, right = caret-side padding, as given in the design spec.)
SOURCE_PADDING = {
    "2XL": {"pad_icon": 18, "pad_caret": 23},
    "XL":  {"pad_icon": 12, "pad_caret": 16},
    "LG":  {"pad_icon": 8,  "pad_caret": 11},
    "MD":  {"pad_icon": 5,  "pad_caret": 7},
    "SM":  {"pad_icon": 4,  "pad_caret": 6},
    "XS":  {"pad_icon": 3,  "pad_caret": 4},
}

GLYPH = {"icon", "caret"}


def edge_pad(height, glyph):
    """The law: a glyph centers in a square cell of side = height -> padding = (height-glyph)/2.

    Exact (integer) at every canonical size because heights and glyph sizes share parity."""
    return (height - glyph) / 2


def geometry(size):
    """The full computed geometry for a size — free values + derived paddings + radii."""
    f = FREE[size]
    h, icon, caret = f["height"], f["icon"], f["caret"]
    pad_icon = edge_pad(h, icon)        # icon-side inline padding (icon-only button is square)
    pad_caret = edge_pad(h, caret)      # caret-side inline padding (caret-only button is square)
    return {
        "size": size,
        "height": h,
        "icon": icon,
        "caret": caret,
        "font": f["font"],
        "spacer": f["spacer"],
        "pad_icon": _int(pad_icon),     # = (h - icon)/2
        "pad_caret": _int(pad_caret),   # = (h - caret)/2
        "pad_label": _int(pad_caret),   # text at an edge takes the generous (caret-side) padding
        "radius_pill": _int(h / 2),     # fully-rounded = height/2 (the geometric default)
        "inset": _int(pad_caret),       # container/section inner padding == button caret-side pad
        "gap": f["spacer"],             # gap between contained/gridded items == the spacer
    }


def _int(x):
    """Render a whole-number float as int (the ramp is integer at every canonical size)."""
    return int(x) if float(x).is_integer() else x


def pad_for(geo, slot):
    """Edge padding contributed by whichever slot sits at an edge."""
    return {"icon": geo["pad_icon"], "caret": geo["pad_caret"], "label": geo["pad_label"]}[slot]


def label_justify(slots):
    """How the label's TEXT aligns under `justify-content: space-between`, by what flanks it.

    flanked both sides -> center; only-left neighbour -> end; only-right -> start; alone/absent -> center."""
    if "label" not in slots:
        return "center"  # single glyph -> centered in a square
    i = slots.index("label")
    left = i > 0
    right = i < len(slots) - 1
    if left and right:
        return "center"
    if left:
        return "end"
    if right:
        return "start"
    return "center"


def layout(size, slots):
    """Box model for a (size, ordered-slots) permutation.

    Returns the ordered segments left->right, the label justification, whether it is square
    (single glyph), and the fixed (non-label) width. Layout is `display:flex` + space-between with
    a `spacer` gap flanking the label and between adjacent glyphs."""
    if size not in FREE:
        raise ValueError("unknown size %r (use one of %s)" % (size, ", ".join(SIZES)))
    for s in slots:
        if s not in ("icon", "caret", "label"):
            raise ValueError("unknown slot %r (use icon, caret, label)" % s)
    geo = geometry(size)
    square = len(slots) == 1 and slots[0] in GLYPH

    if square:
        # icon-only / caret-only: square, glyph centered, padding symmetric = (h - glyph)/2
        glyph = slots[0]
        side = geo["height"]
        pad = _int(edge_pad(side, geo[glyph]))
        segs = [("pad", pad), (glyph, geo[glyph]), ("pad", pad)]
        return {"size": size, "slots": list(slots), "square": True, "width": side,
                "height": side, "justify": "center", "segments": segs, "fixed_width": side}

    segs = [("pad", pad_for(geo, slots[0]))]
    for idx, s in enumerate(slots):
        if idx > 0:
            segs.append(("spacer", geo["spacer"]))
        segs.append(("label", "fill") if s == "label" else (s, geo[s]))
    segs.append(("pad", pad_for(geo, slots[-1])))

    fixed = sum(w for role, w in segs if role != "label")
    return {"size": size, "slots": list(slots), "square": False, "width": "fill" if "label" in slots else fixed,
            "height": geo["height"], "justify": label_justify(slots), "segments": segs, "fixed_width": fixed}


# --- validation of a declared component geometry against the ramp ------------------------------
def validate_spec(spec):
    """Check a declared geometry dict against the canonical ramp. Returns (fails, warns)."""
    fails, warns = [], []
    name = spec.get("component", "<spec>")
    size = spec.get("size")
    if size not in FREE:
        fails.append("%s: size %r is not one of %s" % (name, size, ", ".join(SIZES)))
        return fails, warns
    geo = geometry(size)
    for key in ("height", "icon", "caret", "font", "spacer"):
        if key in spec and spec[key] != geo[key]:
            fails.append("%s[%s]: %s=%s, ramp says %s" % (name, size, key, spec[key], geo[key]))
    slots = spec.get("slots")
    if slots:
        lay = layout(size, slots)
        if "pad_lead" in spec and spec["pad_lead"] != lay["segments"][0][1]:
            fails.append("%s[%s]: pad_lead=%s, law gives %s" % (name, size, spec["pad_lead"], lay["segments"][0][1]))
        if "pad_trail" in spec and spec["pad_trail"] != lay["segments"][-1][1]:
            fails.append("%s[%s]: pad_trail=%s, law gives %s" % (name, size, spec["pad_trail"], lay["segments"][-1][1]))
        if "justify" in spec and spec["justify"] != lay["justify"]:
            fails.append("%s[%s]: justify=%r, layout gives %r" % (name, size, spec["justify"], lay["justify"]))
        if spec.get("square") is not None and bool(spec["square"]) != lay["square"]:
            fails.append("%s[%s]: square=%s, layout gives %s" % (name, size, spec["square"], lay["square"]))
        if lay["square"] and "width" in spec and spec["width"] != geo["height"]:
            fails.append("%s[%s]: icon/caret-only must be square (width==height==%s), got %s"
                         % (name, size, geo["height"], spec["width"]))
    if spec.get("radius") == "pill" and "radius_px" in spec and spec["radius_px"] != geo["radius_pill"]:
        warns.append("%s[%s]: pill radius should be %s (height/2), got %s"
                     % (name, size, geo["radius_pill"], spec["radius_px"]))
    return fails, warns


# --- selftest: prove the law and the permutation logic ----------------------------------------
PERMUTATIONS = [
    (["icon", "label", "caret"], "center"),
    (["icon", "label"],          "end"),
    (["label", "caret"],         "start"),
    (["label"],                  "center"),
    (["icon"],                   "center"),
    (["caret"],                  "center"),
    (["caret", "label"],         "end"),
    (["caret", "label", "icon"], "center"),
]


def selftest():
    errs = []
    # 1. the padding law reproduces the hand-authored source table exactly, at every size.
    for size in SIZES:
        geo = geometry(size)
        src = SOURCE_PADDING[size]
        if geo["pad_icon"] != src["pad_icon"]:
            errs.append("%s: (h-icon)/2=%s != source pad_icon %s" % (size, geo["pad_icon"], src["pad_icon"]))
        if geo["pad_caret"] != src["pad_caret"]:
            errs.append("%s: (h-caret)/2=%s != source pad_caret %s" % (size, geo["pad_caret"], src["pad_caret"]))
    # 2. the canonical icon|label|caret box model matches the spec'd pattern at 2XL
    #    | 18 pad | icon | 8 spacer | label fill | 8 spacer | caret | 23 pad |
    xl2 = layout("2XL", ["icon", "label", "caret"])
    expect = [("pad", 18), ("icon", 28), ("spacer", 8), ("label", "fill"),
              ("spacer", 8), ("caret", 18), ("pad", 23)]
    if xl2["segments"] != expect:
        errs.append("2XL icon|label|caret segments %s != %s" % (xl2["segments"], expect))
    # 3. permutation -> label justification matches the documented 8 patterns
    for slots, want in PERMUTATIONS:
        got = label_justify(slots)
        if got != want:
            errs.append("justify %s: got %r want %r" % (slots, got, want))
    # 4. icon-only and caret-only are square (width == height) at every size
    for size in SIZES:
        for g in ("icon", "caret"):
            lay = layout(size, [g])
            if not lay["square"] or lay["width"] != geometry(size)["height"]:
                errs.append("%s %s-only not square: %s" % (size, g, lay))
    # 5. validate_spec accepts a correct spec and rejects a wrong one
    ok = {"component": "x-button", "size": "XL", "slots": ["icon", "label", "caret"],
          "height": 48, "icon": 24, "caret": 16, "pad_lead": 12, "pad_trail": 16, "justify": "center"}
    f, _ = validate_spec(ok)
    if f:
        errs.append("validate_spec rejected a correct spec: %s" % f)
    bad = dict(ok, pad_trail=12)  # caret side must be (48-16)/2 = 16, not 12
    f, _ = validate_spec(bad)
    if not f:
        errs.append("validate_spec accepted a wrong pad_trail")
    return errs


def _print_ramp():
    cols = ["size", "height", "icon", "caret", "font", "spacer", "pad_icon", "pad_caret",
            "radius_pill", "inset", "gap"]
    print("  ".join("%-10s" % c for c in cols))
    for size in SIZES:
        g = geometry(size)
        print("  ".join("%-10s" % g[c] for c in cols))


def _print_layout(size, slots):
    lay = layout(size, slots)
    print("%s  [%s]  square=%s  justify=%s  height=%s  fixed_width=%s"
          % (size, ",".join(slots), lay["square"], lay["justify"], lay["height"], lay["fixed_width"]))
    print("  " + " | ".join("%s:%s" % (r, w) for r, w in lay["segments"]))


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("geometry-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("geometry-check: OK — padding law verified against source table, "
              "8 permutations + square-glyph rule + validate round-trip pass")
        return 0
    cmd = argv[0]
    if cmd == "ramp":
        _print_ramp()
        return 0
    if cmd == "layout" and len(argv) >= 3:
        _print_layout(argv[1], [s.strip() for s in argv[2].split(",") if s.strip()])
        return 0
    if cmd == "validate" and len(argv) >= 2:
        try:
            spec = json.load(open(argv[1], encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            sys.stderr.write("cannot read spec: %s\n" % e)
            return 2
        specs = spec if isinstance(spec, list) else [spec]
        fails, warns = [], []
        for s in specs:
            f, w = validate_spec(s)
            fails += f
            warns += w
        for w in warns:
            print("  ⚠ %s" % w)
        if fails:
            sys.stderr.write("geometry-check: FAIL (%d)\n" % len(fails))
            for f in fails:
                sys.stderr.write("  - %s\n" % f)
            return 1
        print("geometry-check: OK — %d spec(s) match the ramp" % len(specs))
        return 0
    sys.stderr.write("usage: geometry-check.py [selftest|ramp|layout <SIZE> <slots>|validate <file>]\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
