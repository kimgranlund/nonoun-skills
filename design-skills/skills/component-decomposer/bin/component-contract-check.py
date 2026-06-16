#!/usr/bin/env python3
"""component-contract-check.py — the component-decomposer contract linter. Self-contained (stdlib only).

A "contract card" is the small declarative artifact the skill emits for a component before it is
built (and re-derives when grading one that exists). This linter routes the MECHANIZABLE gates of
the COMPOSE x REALIZE rubric to code — the judgment-heavy reviews stay in SKILL.md. It checks one
or more contract cards (JSON) and reports FAILs (gate violations) and WARNs (policy advisories).

Contract card shape (all keys optional except `component`):
  {
    "component": "x-select",            # custom-element tag — MUST contain a hyphen
    "layer": "component",               # token | primitive | component | pattern
    "form_associated": true,            # FACE: participates in forms via ElementInternals
    "replaces_native": true,            # stands in for a native control (input/button/select/...)
    "role": "combobox",                 # ARIA role (required for interactive components)
    "parts": ["trigger","value","listbox","option","indicator"],
    "props": ["size","variant","disabled","invalid"],
    "boolean_props": ["disabled","invalid","open","required","loading","readonly"],
    "slots": ["option"],
    "states": ["open","disabled","invalid"],
    "keyboard": ["ArrowDown","ArrowUp","Enter","Escape","Home","End"],
    "forced_colors": true,              # ships @media (forced-colors: active)
    "owns_outer_margin": false,         # a component must NOT set its own outer margin
    "validity": true                    # form controls declare a setValidity story
  }

  python3 bin/component-contract-check.py selftest
  python3 bin/component-contract-check.py <card.json | dir>

Python 3.8+.
"""
import json
import os
import sys

LAYERS = {"token", "primitive", "component", "pattern"}

# APG keyboard minimums per role — the subset a contract MUST declare to clear the interaction gate.
APG_MIN = {
    "button":            ["Enter", "Space"],
    "checkbox":          ["Space"],
    "switch":            ["Space"],
    "radio":             ["ArrowDown", "ArrowUp"],
    "radiogroup":        ["ArrowDown", "ArrowUp"],
    "listbox":           ["ArrowDown", "ArrowUp", "Home", "End"],
    "option":            ["ArrowDown", "ArrowUp"],
    "combobox":          ["ArrowDown", "Escape", "Enter"],
    "menu":              ["ArrowDown", "ArrowUp", "Escape"],
    "menuitem":          ["ArrowDown", "ArrowUp"],
    "tab":               ["ArrowLeft", "ArrowRight"],
    "tablist":           ["ArrowLeft", "ArrowRight"],
    "slider":            ["ArrowLeft", "ArrowRight", "Home", "End"],
    "dialog":            ["Escape"],
    "tooltip":           [],  # never focusable; dismiss on Escape is a review, not a gate
}
# roles that stand in for a native form control — these MUST be form-associated + own forced-colors.
NATIVE_REPLACING = {"button", "checkbox", "switch", "radio", "combobox", "listbox", "slider", "textbox", "spinbutton"}
BOOLEAN_PROP_WARN = 6  # more independent booleans than this -> compose, don't configure


def check_card(card):
    """Return (fails, warns) for one contract card."""
    fails, warns = [], []
    name = card.get("component", "<card>")

    # --- A2/B2 gate: a custom element tag must contain a hyphen ---
    if "-" not in str(name):
        fails.append("%s: component tag must contain a hyphen (custom-element requirement)" % name)

    # --- A1 gate: layer must be one of the four tiers ---
    layer = card.get("layer")
    if layer is not None and layer not in LAYERS:
        fails.append("%s: layer %r not in {token, primitive, component, pattern}" % (name, layer))

    role = card.get("role")
    interactive = bool(role) or card.get("form_associated") or card.get("keyboard") or card.get("replaces_native")

    # --- A2 gate: an interactive component needs named parts and a role ---
    if interactive and not card.get("parts"):
        warns.append("%s: interactive component declares no parts[] (anatomy) — name its parts" % name)
    if interactive and not role:
        fails.append("%s: interactive component declares no role (set via ElementInternals)" % name)

    # --- B2 gate: a form control must be form-associated, with value + validity story ---
    replaces = card.get("replaces_native") or (role in NATIVE_REPLACING)
    is_control = card.get("form_associated") or (role in NATIVE_REPLACING and role not in {"button"})
    if is_control and not card.get("form_associated"):
        fails.append("%s: control with role %r must be form-associated (FACE/ElementInternals)" % (name, role))
    if card.get("form_associated") and role not in {"button"} and not card.get("validity"):
        warns.append("%s: form-associated control declares no validity story (setValidity)" % name)

    # --- B3 gate: APG keyboard minimum for the role ---
    if role in APG_MIN:
        have = set(card.get("keyboard", []))
        missing = [k for k in APG_MIN[role] if k not in have]
        if missing:
            (fails if card.get("keyboard") else warns).append(
                "%s: role %r missing APG keys %s%s" % (name, role, missing,
                                                       "" if card.get("keyboard") else " (no keyboard[] declared)"))

    # --- B4 gate: anything replacing a native control must ship forced-colors styles ---
    if replaces and not card.get("forced_colors"):
        fails.append("%s: replaces a native control but declares no forced-colors styles "
                     "(@media (forced-colors: active)) — it will vanish in Windows High Contrast" % name)

    # --- A3/A4 policy reviews (advisory) ---
    bools = card.get("boolean_props") or [p for p in card.get("props", []) if p in (card.get("boolean_props") or [])]
    if len(card.get("boolean_props", [])) > BOOLEAN_PROP_WARN:
        warns.append("%s: %d boolean props (> %d) — likely a variant enum or composition is hiding "
                     "(boolean-prop explosion)" % (name, len(card["boolean_props"]), BOOLEAN_PROP_WARN))
    if card.get("owns_outer_margin"):
        warns.append("%s: declares its own outer margin — components don't set outer margin; "
                     "spacing is the parent's job (gap on a layout primitive)" % name)
    return fails, warns


# --- selftest fixtures -------------------------------------------------------------------------
GOOD = {
    "component": "x-select", "layer": "component", "form_associated": True, "replaces_native": True,
    "role": "combobox", "parts": ["trigger", "value", "listbox", "option", "indicator"],
    "props": ["size", "variant", "disabled", "invalid"], "boolean_props": ["disabled", "invalid", "open"],
    "slots": ["option"], "states": ["open", "disabled", "invalid"],
    "keyboard": ["ArrowDown", "ArrowUp", "Enter", "Escape", "Home", "End"],
    "forced_colors": True, "owns_outer_margin": False, "validity": True,
}
BAD_NO_HYPHEN = {"component": "select", "role": "combobox", "keyboard": ["ArrowDown", "Escape", "Enter"],
                 "form_associated": True, "replaces_native": True, "forced_colors": True, "parts": ["x"]}
BAD_NO_FORCED = {"component": "x-checkbox", "layer": "component", "role": "checkbox", "form_associated": True,
                 "replaces_native": True, "keyboard": ["Space"], "parts": ["box"], "forced_colors": False}
BAD_NOT_FACE = {"component": "x-radio", "role": "radio", "replaces_native": True, "forced_colors": True,
                "keyboard": ["ArrowDown", "ArrowUp"], "parts": ["dot"]}
WARN_BOOLS = dict(GOOD, component="x-btn", role="button", form_associated=False, replaces_native=False,
                  keyboard=["Enter", "Space"], validity=False,
                  boolean_props=["a", "b", "c", "d", "e", "f", "g"])


def selftest():
    errs = []

    def fails_of(card):
        return check_card(card)[0]

    def warns_of(card):
        return check_card(card)[1]

    if fails_of(GOOD):
        errs.append("GOOD card produced fails: %s" % fails_of(GOOD))
    if not any("hyphen" in f for f in fails_of(BAD_NO_HYPHEN)):
        errs.append("missing-hyphen not caught")
    if not any("forced-colors" in f for f in fails_of(BAD_NO_FORCED)):
        errs.append("missing forced-colors not caught")
    if not any("form-associated" in f for f in fails_of(BAD_NOT_FACE)):
        errs.append("non-FACE control not caught")
    if not any("boolean" in w for w in warns_of(WARN_BOOLS)):
        errs.append("boolean-prop explosion not warned")
    # a button is NOT required to be form-associated and has no validity warning
    if any("form-associated" in f for f in fails_of({"component": "x-button", "role": "button",
                                                     "keyboard": ["Enter", "Space"], "parts": ["label"],
                                                     "replaces_native": True, "forced_colors": True})):
        errs.append("button wrongly required to be form-associated")
    return errs


def _iter_cards(path):
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            for fn in sorted(fns):
                if fn.endswith(".contract.json"):
                    yield os.path.join(dp, fn)
    else:
        yield path


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("contract-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("contract-check: OK — gate + policy checks verified over good/bad fixtures")
        return 0
    fails, warns, n = [], [], 0
    for fp in _iter_cards(argv[0]):
        try:
            doc = json.load(open(fp, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            fails.append("%s: unreadable (%s)" % (fp, e))
            continue
        for card in (doc if isinstance(doc, list) else [doc]):
            n += 1
            f, w = check_card(card)
            fails += f
            warns += w
    for w in warns:
        print("  ⚠ %s" % w)
    if fails:
        sys.stderr.write("contract-check: FAIL (%d)\n" % len(fails))
        for f in fails:
            sys.stderr.write("  - %s\n" % f)
        return 1
    print("contract-check: OK — %d card(s) clear the gates" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
