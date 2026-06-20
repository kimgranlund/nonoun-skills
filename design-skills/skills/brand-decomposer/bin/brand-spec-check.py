#!/usr/bin/env python3
"""brand-spec-check.py — the brand-decomposer OPERABILITY gate. Self-contained (stdlib only).

A brand-guidelines artifact reads as a *brand operating system*, not a logo rulebook. Most of grading
it is judgment (the INSIDE-OUT meaning axis — is the idea sharp, is the meaning chain coherent), and
that stays in SKILL.md. But the OUTSIDE-IN *operability* axis has joints that are arithmetic, not
taste — a vague prose deck "feels" complete but an agent cannot retrieve, cite, or trust it. Those are
routed here so a beautiful-but-unusable spec can't pass on looks:

  WELL_FORMED      required fields present, severities/confidences in range, token types known
  UNTRACED         a rule / token / example with no evidence[] (every non-obvious claim needs a source)
  LOW_CONFIDENCE   an inferred record at confidence < 0.75 not marked review (operational trust band)
  COLLAPSED_TRUTH  a record that fuses observed / inferred / proposed into one field
  CONTRAST_FAIL    a color role-pair below the WCAG AA floor (4.5 normal text / 3.0 large·ui) — the one
                   accessibility joint a deck almost never proves by hand
  BARE_TOKEN       a token with a value but no role + meaning (a palette, not a color *system*)
  GENERIC_IDEA     the brand idea is only interchangeable adjectives ("modern, bold, simple") — the
                   rubric's #1 weak signal: specific enough that a competitor couldn't copy-paste it
  INCOMPLETE       a rubric domain (mark · voice · color · type · expression · governance) with no
                   rule or token, or no surface coverage — the spec can't answer "how here?"

This is a PRE-FILTER, not an oracle: a clean run means the spec is well-formed, traced, accessible, and
complete *enough to operate* — it does NOT mean the brand idea is good or the meaning chain is right
(that is the INSIDE-OUT axis, judged + adversarially verified). A token table with a perfect contrast
score can still encode a generic, hollow brand.

  python3 bin/brand-spec-check.py lint <card.brand.json>     # the operability gate
  python3 bin/brand-spec-check.py contrast <fg> <bg> [large|ui]
  python3 bin/brand-spec-check.py selftest                    # green (DocuSign) / red (degraded) fixtures
  python3 bin/brand-spec-check.py lint <card> --json          # the shared {tool, ok, summary, findings} report

A *.brand.json card (the gradeable subset of the corpus schema — strategy + typed, evidence-linked
primitives):
  {"brand": "...",
   "strategy": {"brand_idea": "...", "meaning_chain": ["idea","voice","mark","color","type",...]},
   "domains": {"mark": {...}, "voice": {...}, "color": {...}, "type": {...}, "expression": {...},
               "governance": {...}},                       # each domain present = covered
   "tokens":  [{"id","type":"color|type|space|radius|motion","role","value","meaning",
                "evidence":[...], "confidence":0.0-1.0, "truth":"observed|inferred|proposed"}],
   "rules":   [{"id","domain","statement","severity":"must|should|may","evidence":[...],
                "confidence","truth"}],
   "examples":[{"id","surface","description","rules_demonstrated":[...],"evidence":[...]}],
   "surfaces":["homepage","product-ui","social","email","campaign","packaging", ...],
   "color_pairs":[{"name","fg":"#hex","bg":"#hex","size":"normal|large","role":"text|ui"}]}
Python 3.8+.
"""
import json
import re
import sys

DOMAINS = ["mark", "voice", "color", "type", "expression", "governance"]
# the corpus brand_domain enum (17 fine-grained values) rolled up to the 6 rubric-aligned domains, so a
# faithful corpus-shaped card normalizes instead of tripping warnings
DOMAIN_ALIASES = {"logo": "mark", "typography": "type", "layout": "expression",
                  "photography": "expression", "illustration": "expression", "motion": "expression",
                  "product": "expression", "marketing": "expression", "social": "expression",
                  "packaging": "expression", "environmental": "expression", "co_branding": "expression",
                  "data_visualization": "expression"}
TOKEN_TYPES = {"color", "type", "space", "radius", "motion", "elevation"}
SEVERITIES = {"must", "should", "may"}  # the corpus enum (RFC-2119); must=hard rule, may=flexible range
TRUTHS = {"observed", "inferred", "proposed"}


def _norm_domain(d):
    return DOMAIN_ALIASES.get(d, d)
CONFIDENCE_REVIEW = 0.75
# the rubric's "voice is only adjectives" trap — a brand idea that is JUST these is interchangeable
GENERIC = {"modern", "bold", "simple", "innovative", "trusted", "clean", "friendly", "premium",
           "playful", "minimal", "approachable", "dynamic", "human", "authentic", "fresh", "sleek"}
# stopwords don't count as substantive — else "modern, bold, AND simple" reads as non-generic
STOPWORDS = {"and", "the", "a", "an", "of", "to", "is", "are", "be", "with", "for", "or", "that",
             "this", "it", "as", "our", "we", "you", "your", "but", "yet", "so", "in", "on", "at"}


# --- WCAG contrast (shared with color-verifier's contrast-check) -------------------------------
def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _hex(s):
    s = str(s).strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6 or any(ch not in "0123456789abcdefABCDEF" for ch in s):
        raise ValueError("bad color %r" % s)
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def contrast(fg, bg):
    rf, gf, bf = _hex(fg)
    rb, gb, bb = _hex(bg)
    lf = 0.2126 * _lin(rf) + 0.7152 * _lin(gf) + 0.0722 * _lin(bf)
    lb = 0.2126 * _lin(rb) + 0.7152 * _lin(gb) + 0.0722 * _lin(bb)
    hi, lo = max(lf, lb), min(lf, lb)
    return (hi + 0.05) / (lo + 0.05)


def _aa_floor(size, role):
    return 3.0 if (size == "large" or role == "ui") else 4.5


# --- the operability checks --------------------------------------------------------------------
def check_card(card):
    """Return (fails, warns) for one brand-spec card."""
    fails, warns = [], []
    brand = card.get("brand", "<card>")

    strat = card.get("strategy") or {}
    idea = (strat.get("brand_idea") or "").strip()
    if not idea:
        fails.append("%s: no strategy.brand_idea — the spec has no core to propagate (A1 gate)" % brand)
    else:
        words = re.findall(r"[a-z']+", idea.lower())
        nongeneric = [w for w in words if w not in GENERIC and w not in STOPWORDS and len(w) > 2]
        if words and not nongeneric:
            fails.append("%s: GENERIC_IDEA — brand_idea is only interchangeable adjectives (%r); a "
                         "competitor could copy-paste it (rubric weak signal #1)" % (brand, idea))

    chain = strat.get("meaning_chain") or []
    if idea and len(chain) < 4:
        warns.append("%s: meaning_chain has %d links — the idea isn't propagated to the primitives "
                     "(idea→voice→mark→color→type→…)" % (brand, len(chain)))

    # provenance + truth + value on every typed record
    def _provenance(rec, kind, label):
        rid = rec.get("id", label)
        if not rec.get("evidence"):
            fails.append("%s: UNTRACED — %s '%s' has no evidence[] (every non-obvious claim needs a "
                         "source)" % (brand, kind, rid))
        conf = rec.get("confidence")
        if conf is None:
            fails.append("%s: %s '%s' has no confidence" % (brand, kind, rid))
        elif isinstance(conf, bool) or not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
            fails.append("%s: %s '%s' confidence %r not in [0,1]" % (brand, kind, rid, conf))
        elif conf < CONFIDENCE_REVIEW and rec.get("truth") == "inferred" and not rec.get("review"):
            warns.append("%s: LOW_CONFIDENCE — inferred %s '%s' at %.2f (< %.2f) not marked review"
                         % (brand, kind, rid, conf, CONFIDENCE_REVIEW))
        t = rec.get("truth")
        if t is not None and t not in TRUTHS:
            warns.append("%s: COLLAPSED_TRUTH — %s '%s' truth %r not one of observed/inferred/proposed"
                         % (brand, kind, rid, t))

    for r in card.get("rules") or []:
        _provenance(r, "rule", "rule")
        if r.get("severity") not in SEVERITIES:
            fails.append("%s: rule '%s' severity %r not in %s" % (brand, r.get("id", "?"),
                                                                  r.get("severity"), sorted(SEVERITIES)))
        if _norm_domain(r.get("domain")) not in DOMAINS:
            warns.append("%s: rule '%s' domain %r not a known brand domain" % (brand, r.get("id", "?"),
                                                                               r.get("domain")))
    for tok in card.get("tokens") or []:
        _provenance(tok, "token", "token")
        if tok.get("type") not in TOKEN_TYPES:
            warns.append("%s: token '%s' type %r unknown" % (brand, tok.get("id", "?"), tok.get("type")))
        if tok.get("value") and not (tok.get("role") and tok.get("meaning")):
            warns.append("%s: BARE_TOKEN — '%s' has a value but no role+meaning (a palette, not a "
                         "system)" % (brand, tok.get("id", "?")))
    for ex in card.get("examples") or []:
        if not ex.get("evidence"):
            warns.append("%s: example '%s' has no evidence[]" % (brand, ex.get("id", "?")))

    # contrast — the one accessibility joint a deck rarely proves by hand
    for p in card.get("color_pairs") or []:
        try:
            ratio = contrast(p["fg"], p["bg"])
        except (KeyError, ValueError) as e:
            warns.append("%s: color_pair %r unreadable (%s)" % (brand, p.get("name", "?"), e))
            continue
        floor = _aa_floor(p.get("size", "normal"), p.get("role", "text"))
        if ratio < floor:
            fails.append("%s: CONTRAST_FAIL — pair '%s' %.2f:1 below AA %.1f (the color system isn't "
                         "accessible here)" % (brand, p.get("name", "?"), ratio, floor))

    # completeness — every domain covered by at least one rule or token; surfaces present
    domains_present = {_norm_domain(d) for d in (card.get("domains") or {})}
    rule_domains = {_norm_domain(r.get("domain")) for r in card.get("rules") or []}
    tok_domains = set()
    for t in card.get("tokens") or []:
        tt = t.get("type")
        tok_domains.add({"color": "color", "type": "type", "space": "expression", "radius": "expression",
                         "motion": "expression", "elevation": "expression"}.get(tt, tt))
    have = domains_present | rule_domains | tok_domains
    missing = [d for d in DOMAINS if d not in have]
    if missing:
        warns.append("%s: INCOMPLETE — domains with no rule/token: %s (the spec can't answer 'how here?'"
                     " for them)" % (brand, ", ".join(missing)))
    if not card.get("surfaces"):
        warns.append("%s: INCOMPLETE — no surfaces[] (an OUTSIDE-IN spec must say where the brand "
                     "shows up)" % brand)
    return fails, warns


# --- fixtures ----------------------------------------------------------------------------------
_EV = [{"deck_id": "docusign-2024", "slide_id": "docusign-2024-slide-007", "confidence": 0.92}]
GREEN = {
    "brand": "DocuSign",
    "strategy": {
        "brand_idea": "Agreements are dynamic moments of connection, not static documents — make the "
                      "moment of agreement feel like forward progress.",
        "meaning_chain": ["idea", "voice", "mark", "color", "type", "layout", "imagery", "apps"],
    },
    "domains": {d: {} for d in DOMAINS},
    "tokens": [
        {"id": "color.ink", "type": "color", "role": "text", "value": "#130032",
         "meaning": "primary ink for body and headlines", "evidence": _EV, "confidence": 0.95,
         "truth": "observed"},
        {"id": "color.surface", "type": "color", "role": "background", "value": "#ffffff",
         "meaning": "default light surface", "evidence": _EV, "confidence": 0.95, "truth": "observed"},
        {"id": "type.display", "type": "type", "role": "display", "value": "DS Indigo / 48-72px",
         "meaning": "expressive headline voice", "evidence": _EV, "confidence": 0.9, "truth": "observed"},
    ],
    "rules": [
        {"id": "mark.clearspace", "domain": "mark", "statement": "Maintain clearspace = the height of "
         "the logomark on all sides.", "severity": "must", "evidence": _EV, "confidence": 0.95,
         "truth": "observed"},
        {"id": "voice.active", "domain": "voice", "statement": "Write agreements as active progress, "
         "never static 'document management'.", "severity": "should", "evidence": _EV,
         "confidence": 0.85, "truth": "inferred"},
        {"id": "color.activation", "domain": "color", "statement": "Use the primary as an activation "
         "accent, not a full-field background.", "severity": "should", "evidence": _EV,
         "confidence": 0.8, "truth": "inferred"},
        {"id": "type.scale", "domain": "type", "statement": "Use the modular display/body scale; never "
         "set display below 32px.", "severity": "should", "evidence": _EV, "confidence": 0.9,
         "truth": "observed"},
        {"id": "expr.grid", "domain": "expression", "statement": "8pt grid; imagery is product-true, "
         "not stock.", "severity": "should", "evidence": _EV, "confidence": 0.8, "truth": "inferred"},
        {"id": "gov.partner", "domain": "governance", "statement": "Partner lockups require brand-team "
         "approval.", "severity": "must", "evidence": _EV, "confidence": 0.9, "truth": "observed"},
    ],
    "examples": [
        {"id": "ex.ui", "surface": "product-ui", "description": "A high-trust signing moment: neutral "
         "system carries the base, primary only as the activation CTA.", "rules_demonstrated":
         ["color.activation"], "evidence": _EV}],
    "surfaces": ["homepage", "product-ui", "social", "email", "campaign"],
    "color_pairs": [{"name": "ink on surface", "fg": "#130032", "bg": "#ffffff", "size": "normal",
                     "role": "text"}],
}
# RED — the corpus's failure modes: generic idea, an untraced rule, a sub-0.75 inferred rule unflagged,
# a contrast fail, a bare token, missing domains, collapsed truth.
RED = {
    "brand": "Acme",
    "strategy": {"brand_idea": "Modern, bold, and simple.", "meaning_chain": ["idea", "color"]},
    "domains": {"color": {}, "type": {}},
    "tokens": [{"id": "color.brand", "type": "color", "value": "#9aa0a6", "evidence": [], "confidence": 0.6}],
    "rules": [
        {"id": "r1", "domain": "color", "statement": "Use the brand grey.", "severity": "should",
         "evidence": [], "confidence": 0.6, "truth": "inferred"},
        {"id": "r2", "domain": "voice", "statement": "Be bold.", "severity": "loud", "evidence": _EV,
         "confidence": 0.55, "truth": "guess"}],
    "examples": [],
    "surfaces": [],
    "color_pairs": [{"name": "grey on white", "fg": "#9aa0a6", "bg": "#ffffff", "size": "normal",
                     "role": "text"}],
}


def selftest():
    errs = []
    gf, gw = check_card(GREEN)
    if gf:
        errs.append("GREEN (DocuSign) card produced FAILs: %s" % gf)
    if gw:  # a complete, traced, accessible card must be clean of WARNs too (no false positives)
        errs.append("GREEN (DocuSign) card produced false-positive WARNs: %s" % gw)
    rf, rw = check_card(RED)
    need = ["GENERIC_IDEA", "UNTRACED", "CONTRAST_FAIL"]
    for kind in need:
        if not any(kind in f for f in rf):
            errs.append("RED card missed %s (fails=%s)" % (kind, rf))
    if not any("severity" in f for f in rf):
        errs.append("RED card: bad severity 'loud' not caught")
    if not any("BARE_TOKEN" in w for w in rw):
        errs.append("RED card: BARE_TOKEN not warned")
    if not any("LOW_CONFIDENCE" in w for w in rw):
        errs.append("RED card: sub-0.75 inferred rule not flagged")
    if not any("COLLAPSED_TRUTH" in w for w in rw):
        errs.append("RED card: truth 'guess' not caught")
    # contrast math sanity (shared with contrast-check)
    if not (abs(contrast("#000", "#fff") - 21.0) < 0.01 and contrast("#9aa0a6", "#ffffff") < 4.5):
        errs.append("contrast math wrong")
    # adversarial: a bool confidence must NOT pass as a valid number (the "true accepted for an int" trap)
    bf, _ = check_card({"brand": "B", "strategy": {"brand_idea": "A specific forcing idea about X."},
                        "tokens": [{"id": "t", "type": "color", "role": "text", "value": "#000",
                                    "meaning": "ink", "evidence": _EV, "confidence": True}]})
    if not any("confidence True not in [0,1]" in f for f in bf):
        errs.append("bool confidence (True) accepted as a valid number (fails=%s)" % bf)
    return errs


def _report(card, fails, warns, as_json):
    if as_json:
        find = [{"kind": f.split(":")[1].strip().split(" ")[0] if "—" in f or ":" in f else "FAIL",
                 "severity": "fail", "location": card.get("brand"), "message": f} for f in fails]
        find += [{"kind": w.split(":")[1].strip().split(" ")[0], "severity": "advisory",
                  "location": card.get("brand"), "message": w} for w in warns]
        print(json.dumps({"tool": "brand-spec-check", "ok": not fails,
                          "summary": "%d fail, %d advisory" % (len(fails), len(warns)),
                          "findings": find}, indent=2))
        return 1 if fails else 0
    for w in warns:
        print("  ⚠ %s" % w)
    if fails:
        sys.stderr.write("brand-spec-check: FAIL (%d)\n" % len(fails))
        for f in fails:
            sys.stderr.write("  - %s\n" % f)
        return 1
    print("brand-spec-check: OK — operability gates clear (well-formed, traced, accessible, complete); "
          "the meaning axis is judged separately")
    return 0


def main(argv):
    as_json = "--json" in argv
    argv = [a for a in argv if a != "--json"]
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("brand-spec-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("brand-spec-check: OK — green (DocuSign) clean, red (degraded) caught; contrast math verified")
        return 0
    if argv[0] == "contrast":
        try:
            r = contrast(argv[1], argv[2])
        except (IndexError, ValueError) as e:
            sys.stderr.write("usage: contrast <fg> <bg> [large|ui]  (%s)\n" % e)
            return 2
        size = argv[3] if len(argv) > 3 else "normal"
        floor = _aa_floor("large" if size == "large" else "normal", "ui" if size == "ui" else "text")
        print("  %.2f:1  (AA floor %.1f — %s)" % (r, floor, "PASS" if r >= floor else "FAIL"))
        return 0 if r >= floor else 1
    if argv[0] == "lint":
        try:
            card = json.load(open(argv[1], encoding="utf-8"))
        except (OSError, IndexError, json.JSONDecodeError) as e:
            sys.stderr.write("brand-spec-check: unreadable card (%s)\n" % e)
            return 2
        fails, warns = check_card(card)
        return _report(card, fails, warns, as_json)
    sys.stderr.write("usage: brand-spec-check.py lint <card> | contrast <fg> <bg> | selftest [--json]\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
