#!/usr/bin/env python3
"""composition-check.py — the COMPOSITION card gate (component-decomposer's COMPOSE A4 / A5).

This is the multi-component *composition card* gate — the complement to component-contract-check.py
(the single-component contract card). Where contract-check lints ONE component's anatomy/API/FACE,
this lints how components NEST and WIRE up the tier ladder (primitive → component → module). The
composition rubric is mostly judgment (the COMPOSE A4 Composition / A5 Coherence rungs in SKILL.md),
but a few joints are arithmetic, not taste, and are routed here so a clean-looking composition card
can't hide a mis-cut boundary or a seamless component:

  • tier-consistency  — a primitive composes nothing; a component composes >=1 piece AND has a seam;
                        a module arranges >=2 components and does not tier-skip to a raw primitive
                        (the A4 tier ladder).
  • the SEAM gate      — a component MUST expose a seam: named slots, or an overflow mechanism. A
                        seamless component is "boxed but inert" (A4 — the cross-component slot/state
                        seam, which folds into REALIZE B3/B4 as a cross-component note).
  • overflow-declared  — a capacity-constrained axis carrying many action-primitives MUST declare an
                        overflow mechanism (A4 / the cross-component interaction note on B4).
  • god-component fanout — a component composing > 7 pieces smells like a mis-cut module (A4).
  • no self-margin     — a piece must not set its own outer margin; spacing BETWEEN pieces is the
                        parent composition's gap / region grid (A5 — the same no-outer-margin rule
                        component-contract-check warns on for a single component).

And one generator — the slot-presence -> grid-columns mapping: the deterministic layout the
slot-presence grid rests on, where an ABSENT slot leaves NO phantom column. The MODULE → app-shell
boundary hands UP to layout-decomposer (this gate stops at the module; the page / region grid it sits
in is layout-decomposer's).

Usage:
  composition-check.py lint <card.composition.json>     # the A4 / A5 composition-card linter
  composition-check.py slot-grid <comma,slots>          # slot-presence -> grid-template-columns
  composition-check.py selftest                          # good / bad fixtures (the law, proven)

A *.composition.json card:
  {"name":"toolbar","tier":"component",
   "contains":[{"name":"x-button","tier":"primitive","role":"action"}, ...],
   "slots":["actions"],"axis":"horizontal","overflow":"priority-menu","selfMargin":false}
"""
import json
import sys

TIERS = ("primitive", "component", "module")
# the canonical content slot gets `1fr`; every other present slot gets an `auto` column.
CONTENT_SLOTS = ("content", "body", "label")
# a component composing more than this many pieces smells like a module / god-component (A4).
GOD_COMPONENT_FANOUT = 7


def lint(card):
    """Return (errors, warnings) for a composition descriptor (COMPOSE A4 / A5)."""
    errs, warns = [], []
    tier = card.get("tier")
    if tier not in TIERS:
        return ([f"tier {tier!r} is not one of {TIERS} (A4 tier ladder)"], [])

    contains = card.get("contains", []) or []
    slots = card.get("slots", []) or []
    overflow = card.get("overflow")
    axis = card.get("axis", "none")
    has_seam = bool(slots) or bool(overflow)

    # A5 — no self-owned outer margin
    if card.get("selfMargin"):
        errs.append("selfMargin: true — a piece must not set its own outer margin; spacing BETWEEN "
                    "pieces is the parent's gap / region grid (A5)")

    if tier == "primitive":
        if contains:
            errs.append(f"a primitive composes {len(contains)} piece(s); a primitive is an atom "
                        "(the leaf — its own contract card) — re-tier to 'component' (A4)")
    elif tier == "component":
        if not contains:
            errs.append("a component composes no pieces — it is a primitive, or its children are missing (A4)")
        if not has_seam:
            errs.append("SEAM gate: a component exposes no slots and no overflow — 'boxed but inert'; "
                        "give it named slots or an overflow mechanism (A4 / REALIZE B3 seam)")
        if len(contains) > GOD_COMPONENT_FANOUT:
            warns.append(f"a component composes {len(contains)} pieces (> {GOD_COMPONENT_FANOUT}) — "
                         "possible god-component; is this really a module? (A4)")
    elif tier == "module":
        comp_children = [c for c in contains if c.get("tier") == "component"]
        if len(comp_children) < 2:
            errs.append(f"a module arranges {len(comp_children)} component(s); a module needs >=2 components "
                        "in regions with cross-component state — else it is a component (A4)")
        skips = [c.get("name") for c in contains if c.get("tier") == "primitive"]
        if skips:
            warns.append(f"a module nests raw primitive(s) {skips} with no component between (tier-skip) — "
                         "wrap them in a component, or mark the exception (A4). The module's app shell "
                         "hands UP to layout-decomposer.")

    # A4 / REALIZE B4 — overflow on a capacity-constrained axis carrying many actions
    actions = [c for c in contains if c.get("role") == "action"]
    if axis in ("horizontal", "vertical") and len(actions) >= 4 and not overflow:
        errs.append(f"a {axis} axis carries {len(actions)} actions but declares no overflow mechanism — "
                    "it will clip or wrap; declare a priority-overflow seam (A4 / REALIZE B4)")

    return (errs, warns)


def slot_grid(present):
    """The deterministic slot-presence -> grid-template-columns mapping (an absent slot => no column)."""
    cols = ["1fr" if s in CONTENT_SLOTS else "auto" for s in present]
    return " ".join(cols) if cols else "(none — no slots present)"


# ── fixtures: the law, proven by construction ───────────────────────────────────────────────
def _actions(n):
    return [{"name": "ui-button", "tier": "primitive", "role": "action"} for _ in range(n)]


FIXTURES = [
    ("GOOD toolbar+overflow", {"name": "toolbar", "tier": "component", "contains": _actions(6),
                               "slots": ["actions"], "axis": "horizontal", "overflow": "priority-menu",
                               "selfMargin": False}, False),
    ("seamless component (B2)", {"name": "card", "tier": "component",
                                 "contains": [{"name": "div", "tier": "primitive"}],
                                 "slots": [], "overflow": None, "selfMargin": False}, True),
    ("missing overflow (B2/B4)", {"name": "toolbar", "tier": "component", "contains": _actions(6),
                                  "slots": ["actions"], "axis": "horizontal", "overflow": None,
                                  "selfMargin": False}, True),
    ("self-margin (A5)", {"name": "card", "tier": "component",
                          "contains": [{"name": "ui-heading", "tier": "primitive"}],
                          "slots": ["header", "body"], "selfMargin": True}, True),
    ("module with 1 component (A1)", {"name": "settings", "tier": "module",
                                      "contains": [{"name": "ui-nav", "tier": "component"}],
                                      "selfMargin": False}, True),
    ("primitive that composes (A1)", {"name": "button", "tier": "primitive",
                                      "contains": [{"name": "ui-menu", "tier": "primitive"}],
                                      "selfMargin": False}, True),
]


def selftest():
    ok = True
    for label, card, want_err in FIXTURES:
        errs, warns = lint(card)
        passed = bool(errs) == want_err
        ok = ok and passed
        tag = "errors" if errs else "clean"
        print(f"  {'PASS' if passed else 'FAIL'} · {label}: {tag}" + (f" — {errs[0]}" if errs else ""))
    assert slot_grid(["icon", "content", "caret"]) == "auto 1fr auto"
    assert slot_grid(["content", "caret"]) == "1fr auto"
    assert slot_grid(["content"]) == "1fr"
    print("  PASS · slot-grid: icon,content,caret -> auto 1fr auto ; content,caret -> 1fr auto ; content -> 1fr")
    print("selftest:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "selftest":
        return selftest()
    if cmd == "slot-grid":
        present = [s.strip() for s in argv[2].split(",") if s.strip()] if len(argv) > 2 else []
        print(slot_grid(present))
        return 0
    if cmd == "lint":
        with open(argv[2]) as fh:
            card = json.load(fh)
        errs, warns = lint(card)
        for w in warns:
            print(f"  WARN  {w}")
        for e in errs:
            print(f"  ERROR {e}")
        print(f"\n{card.get('name', '?')} ({card.get('tier', '?')}): {len(errs)} error(s), {len(warns)} warning(s)")
        return 1 if errs else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
