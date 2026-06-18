#!/usr/bin/env python3
"""focus-check.py — the focus-verifier mechanism gate. Self-contained (stdlib only).

A "focus order card" is the small declarative artifact the skill emits (or re-derives when grading
an existing UI) to describe the keyboard-focus structure of a view: the focusable elements with
their tabindex / focus-visibility, the DOM source order, and any open modal's focus story. This
linter routes the MECHANIZABLE facts of focus management to code — does a *positive* tabindex
override natural order? does a focusable element paint a visible focus indicator? does the DOM
order survive the tab sequence? is an open modal trapped and does it restore focus on close? —
while the judgment-heavy review (is the *order* sensible? does the sequence match reading order
and task flow?) stays in SKILL.md. A tabindex value, a `trap:false`, a missing visible-focus flag
are mechanical; whether the resulting walk makes *sense* is a human read.

Focus order card shape (all top-level keys optional; report — never silently pass — when absent):
  {
    "elements": [
      {"id": "skip-link", "tabindex": 0,  "focusable": true, "visible_focus": true},
      {"id": "hero-cta",  "tabindex": 3,  "focusable": true, "visible_focus": false},
      {"id": "decorative","tabindex": -1, "focusable": false}
    ],
    "dom_order": ["skip-link", "nav", "hero-cta", "footer"],
    "modal": {"open": true, "trap": false, "restore_focus": false}
  }

Per-element keys:
  id            — stable identifier (string). Used to correlate dom_order with elements.
  tabindex      — the tabindex attribute value (int). 0 = natural order; -1 = programmatic only;
                  >0 = EXPLICIT positive index (the anti-pattern — overrides DOM order globally).
  focusable     — whether the element takes keyboard focus at all (bool).
  visible_focus — whether the element paints a visible focus indicator when focused (bool).

Checks (gate = a hard FAIL; advisory = a WARN that surfaces a risk for human review):
  POSITIVE_TABINDEX  (gate)     — any element with tabindex > 0. A positive tabindex yanks the
                                  element out of DOM order and ahead of every tabindex:0 element on
                                  the page — the canonical focus-order anti-pattern.
  NO_VISIBLE_FOCUS   (gate)     — a focusable element with visible_focus:false. A focusable element
                                  with no visible indicator strands keyboard users (WCAG 2.4.7).
  ORDER_MISMATCH     (advisory) — when explicit tabindex>0 values are present, the resulting tab
                                  order (positive-tabindex elements first, ascending, then the
                                  tabindex:0 elements in DOM order) diverges from dom_order. Surfaces
                                  the exact reorder the positive tabindex caused.
  MODAL_NO_TRAP      (gate)     — an OPEN modal with trap:false. Focus can escape the dialog to the
                                  page behind it — a keyboard user is lost. (Gate only while open;
                                  a closed modal's trap setting is not exercised.)
  MODAL_NO_RESTORE   (advisory) — an OPEN modal with restore_focus:false. On close, focus will not
                                  return to the trigger — recoverable, so advisory, not a gate.

A check whose data is absent is SKIPPED and reported as a skip (no silent pass): no elements[] ->
the element-level checks can't run; no dom_order -> ORDER_MISMATCH can't run; no modal -> the modal
checks can't run. A malformed card yields a clear error, not a traceback.

  python3 bin/focus-check.py selftest
  python3 bin/focus-check.py <card.json | dir>

Python 3.8+.
"""
import json
import os
import sys


def _tab_order(elements):
    """The browser tab sequence: positive-tabindex elements first (ascending tabindex, ties by DOM
    appearance), THEN the tabindex:0 / natural-order elements in their elements[] (DOM) appearance.
    Elements that are not keyboard-focusable (tabindex < 0 or focusable:false) take no part."""
    positives, naturals = [], []
    for i, el in enumerate(elements):
        if not isinstance(el, dict):
            continue
        ti = el.get("tabindex", 0)
        if not isinstance(ti, int) or isinstance(ti, bool):
            continue  # malformed tabindex handled by the validity pass; not orderable here
        focusable = el.get("focusable", True)
        if ti > 0:
            positives.append((ti, i, el.get("id")))
        elif ti == 0 and focusable:
            naturals.append(el.get("id"))
    positives.sort(key=lambda t: (t[0], t[1]))
    return [pid for _, _, pid in positives] + naturals


def check_card(card):
    """Return (fails, warns, skips) for one focus order card.

    Raises ValueError on a structurally malformed card (caller turns it into a clean error)."""
    if not isinstance(card, dict):
        raise ValueError("card must be a JSON object")
    fails, warns, skips = [], [], []
    name = card.get("id") or card.get("view") or card.get("name") or "<card>"

    # --- validity pass: a malformed element shape is an error, not a silent skip ---
    elements = card.get("elements")
    if elements is not None and not isinstance(elements, list):
        raise ValueError("%s: 'elements' must be a list" % name)
    if isinstance(elements, list):
        for i, el in enumerate(elements):
            if not isinstance(el, dict):
                raise ValueError("%s: elements[%d] must be an object" % (name, i))
            ti = el.get("tabindex", 0)
            if isinstance(ti, bool) or not isinstance(ti, int):
                raise ValueError("%s: element %r has non-integer tabindex %r"
                                 % (name, el.get("id", i), ti))

    # --- POSITIVE_TABINDEX (gate) + NO_VISIBLE_FOCUS (gate), per element ---
    if isinstance(elements, list) and elements:
        for el in elements:
            eid = el.get("id", "<el>")
            ti = el.get("tabindex", 0)
            if ti > 0:
                fails.append("%s: element '%s' has POSITIVE_TABINDEX (tabindex=%d) — a positive "
                             "tabindex overrides DOM order and jumps ahead of every tabindex:0 "
                             "element; use 0 (natural) or -1 (programmatic), never >0" % (name, eid, ti))
            # a focusable element that explicitly declares no visible focus indicator
            if el.get("focusable", True) and el.get("visible_focus") is False:
                fails.append("%s: focusable element '%s' has NO_VISIBLE_FOCUS (visible_focus:false) "
                             "— a focusable element must paint a visible focus indicator (WCAG 2.4.7); "
                             "don't `outline:none` without a replacement" % (name, eid))
    else:
        skips.append("%s: no elements[] — POSITIVE_TABINDEX / NO_VISIBLE_FOCUS checks skipped" % name)

    # --- ORDER_MISMATCH (advisory): only meaningful when explicit positive tabindex is present ---
    dom_order = card.get("dom_order")
    if dom_order is not None and not isinstance(dom_order, list):
        raise ValueError("%s: 'dom_order' must be a list" % name)
    has_positive = isinstance(elements, list) and any(
        isinstance(e, dict) and isinstance(e.get("tabindex", 0), int)
        and not isinstance(e.get("tabindex", 0), bool) and e.get("tabindex", 0) > 0
        for e in elements)
    if not isinstance(elements, list) or not elements:
        pass  # already reported the elements[] skip above
    elif not dom_order:
        skips.append("%s: no dom_order — ORDER_MISMATCH check skipped" % name)
    elif not has_positive:
        skips.append("%s: no positive tabindex present — ORDER_MISMATCH not applicable (tab order "
                     "follows DOM order)" % name)
    else:
        tab = _tab_order(elements)
        # compare the resulting tab walk to the DOM order, restricted to the ids that participate
        dom_focusable = [d for d in dom_order if d in set(tab)]
        if tab != dom_focusable:
            warns.append("%s: ORDER_MISMATCH — positive tabindex reorders the tab walk %s away from "
                         "DOM order %s; is this sequence intended? (review)" % (name, tab, dom_focusable))

    # --- modal focus story: MODAL_NO_TRAP (gate, only while open) + MODAL_NO_RESTORE (advisory) ---
    modal = card.get("modal")
    if modal is None:
        skips.append("%s: no modal — MODAL_NO_TRAP / MODAL_NO_RESTORE checks skipped" % name)
    elif not isinstance(modal, dict):
        raise ValueError("%s: 'modal' must be an object" % name)
    elif not modal.get("open"):
        skips.append("%s: modal not open — trap/restore not exercised, checks skipped" % name)
    else:
        if modal.get("trap") is not True:
            fails.append("%s: MODAL_NO_TRAP — an OPEN modal with trap:%r — focus can escape to the "
                         "page behind the dialog; trap Tab/Shift+Tab inside the modal while open"
                         % (name, modal.get("trap")))
        if modal.get("restore_focus") is not True:
            warns.append("%s: MODAL_NO_RESTORE — an open modal with restore_focus:%r — on close, "
                         "focus won't return to the element that opened it (review)"
                         % (name, modal.get("restore_focus")))

    return fails, warns, skips


# --- selftest fixtures -------------------------------------------------------------------------
# must-FLAG: a positive tabindex, a no-visible-focus element, AND an open untrapped modal.
BAD = {
    "id": "hero-view",
    "elements": [
        {"id": "skip-link", "tabindex": 0, "focusable": True, "visible_focus": True},
        {"id": "hero-cta", "tabindex": 3, "focusable": True, "visible_focus": False},
        {"id": "decoration", "tabindex": -1, "focusable": False},
    ],
    "dom_order": ["skip-link", "hero-cta"],
    "modal": {"open": True, "trap": False, "restore_focus": False},
}
# must-NOT-flag: all tabindex 0/-1, every focusable element visible, modal trapped + restoring.
GOOD = {
    "id": "settings-view",
    "elements": [
        {"id": "skip-link", "tabindex": 0, "focusable": True, "visible_focus": True},
        {"id": "name-input", "tabindex": 0, "focusable": True, "visible_focus": True},
        {"id": "avatar", "tabindex": -1, "focusable": False},
    ],
    "dom_order": ["skip-link", "name-input"],
    "modal": {"open": True, "trap": True, "restore_focus": True},
}
# a closed modal with trap:false must NOT fire MODAL_NO_TRAP (the trap isn't exercised while closed).
CLOSED_MODAL = {"id": "x", "elements": [{"id": "a", "tabindex": 0, "focusable": True, "visible_focus": True}],
                "dom_order": ["a"], "modal": {"open": False, "trap": False, "restore_focus": False}}
# sparse card: only a single clean element — every absent section reports a SKIP, no fail, no warn.
SPARSE = {"id": "frag", "elements": [{"id": "a", "tabindex": 0, "focusable": True, "visible_focus": True}]}
# order-mismatch fixture: a positive tabindex pulls 'late' ahead of 'early' — advisory WARN, no fail
# beyond the POSITIVE_TABINDEX gate itself.
REORDER = {"id": "reorder", "elements": [
    {"id": "early", "tabindex": 0, "focusable": True, "visible_focus": True},
    {"id": "late", "tabindex": 1, "focusable": True, "visible_focus": True}],
    "dom_order": ["early", "late"]}
# malformed: a non-integer tabindex (true) must raise, not crash or silently pass.
MALFORMED = {"id": "bad", "elements": [{"id": "a", "tabindex": True, "focusable": True}]}


def selftest():
    errs = []

    def of(card):
        return check_card(card)

    bf, bw, _ = of(BAD)
    if not any("POSITIVE_TABINDEX" in f for f in bf):
        errs.append("positive tabindex (tabindex:3) not flagged")
    if not any("NO_VISIBLE_FOCUS" in f for f in bf):
        errs.append("focusable element with visible_focus:false not flagged")
    if not any("MODAL_NO_TRAP" in f for f in bf):
        errs.append("open modal with trap:false not flagged")
    if not any("MODAL_NO_RESTORE" in w for w in bw):
        errs.append("open modal with restore_focus:false not warned")
    if not any("ORDER_MISMATCH" in w for w in bw):
        errs.append("positive-tabindex reorder did not surface ORDER_MISMATCH")

    gf, gw, gs = of(GOOD)
    if gf:
        errs.append("clean card produced fails: %s" % gf)
    if gw:
        errs.append("clean card produced warns: %s" % gw)
    # the GOOD card supplies every section, so the element + modal checks all RUN (no skip). The
    # only legitimate skip is ORDER_MISMATCH being "not applicable" (a clean card has no positive
    # tabindex to reorder anything) — anything else means a present section was silently skipped.
    bad_skips = [s for s in gs if "not applicable" not in s]
    if bad_skips:
        errs.append("fully-populated clean card silently skipped a present section: %s" % bad_skips)

    cf, _, cs = of(CLOSED_MODAL)
    if any("MODAL_NO_TRAP" in f for f in cf):
        errs.append("closed modal wrongly fired MODAL_NO_TRAP")
    if not any("modal not open" in s for s in cs):
        errs.append("closed modal did not report a skip")

    sf, sw, ss = of(SPARSE)
    if sf or sw:
        errs.append("sparse clean card produced fails/warns: %s / %s" % (sf, sw))
    if not (any("no dom_order" in s for s in ss) and any("no modal" in s for s in ss)):
        errs.append("sparse card did not report dom_order/modal skips (silent pass?)")

    rf, rw, _ = of(REORDER)
    if not any("POSITIVE_TABINDEX" in f for f in rf):
        errs.append("reorder fixture's tabindex:1 not flagged as positive")
    if not any("ORDER_MISMATCH" in w for w in rw):
        errs.append("reorder fixture did not surface ORDER_MISMATCH")

    try:
        of(MALFORMED)
        errs.append("malformed card (tabindex:true) did not raise")
    except ValueError:
        pass

    return errs


def _iter_cards(path):
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            for fn in sorted(fns):
                if fn.endswith(".focus.json"):
                    yield os.path.join(dp, fn)
    else:
        yield path


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("focus-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("focus-check: OK — gate + advisory checks verified over good/bad/sparse/malformed fixtures")
        return 0
    fails, warns, skips, n = [], [], [], 0
    for fp in _iter_cards(argv[0]):
        try:
            doc = json.load(open(fp, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            fails.append("%s: unreadable (%s)" % (fp, e))
            continue
        for card in (doc if isinstance(doc, list) else [doc]):
            n += 1
            try:
                f, w, s = check_card(card)
            except ValueError as e:
                fails.append("%s: malformed card (%s)" % (fp, e))
                continue
            fails += f
            warns += w
            skips += s
    for s in skips:
        print("  - (skip) %s" % s)
    for w in warns:
        print("  ! %s" % w)
    if fails:
        sys.stderr.write("focus-check: FAIL (%d)\n" % len(fails))
        for f in fails:
            sys.stderr.write("  - %s\n" % f)
        return 1
    print("focus-check: OK — %d card(s) clear the focus gates" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
