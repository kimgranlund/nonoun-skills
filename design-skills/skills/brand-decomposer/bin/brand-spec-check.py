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
  THIN_EVIDENCE    an evidence[] entry present but with no deck_id/slide_id/source_url (points nowhere)
  DANGLING_REF     an example's rules_demonstrated names a rule id not in the card (broken retrieval, B5)
  WEAK_MANDATE     a 'must' (hard) rule at confidence < 0.90 — mandating what the deck didn't explicitly
                   state (band↔severity coherence)
  TRUTH_CONFIDENCE_MISMATCH  an 'observed' record at confidence < 0.90 — a direct observation you're
                   unsure of is really an inference (band↔truth coherence)

This is a PRE-FILTER, not an oracle: a clean run means the spec is well-formed, traced, accessible, and
complete *enough to operate* — it does NOT mean the brand idea is good or the meaning chain is right
(that is the INSIDE-OUT axis, judged + adversarially verified). A token table with a perfect contrast
score can still encode a generic, hollow brand.

  python3 bin/brand-spec-check.py lint <card.brand.json>     # the operability gate
  python3 bin/brand-spec-check.py contrast <fg> <bg> [large|ui]
  python3 bin/brand-spec-check.py selftest                    # green (DocuSign) / red (degraded) fixtures
  python3 bin/brand-spec-check.py lint <card> --json          # the shared {tool, ok, summary, findings} report
  python3 bin/brand-spec-check.py schema                      # print the formal card schema (to stdout)

A *.brand.json card (the gradeable subset of the corpus schema — strategy + typed, evidence-linked
primitives). The formal, declarative contract is ../schema/brand-spec.schema.json (the selftest
drift-guards it against this file's enums); validate an arbitrary card against it with type-decomposer's
instance-check.py. Shape:
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
import os
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
CONFIDENCE_REVIEW = 0.75    # below this an inferred record must be review-flagged
CONFIDENCE_EXPLICIT = 0.90  # the "explicitly stated by the deck" band — a must-rule / observed claim
#                             below it is a coherence smell (mandating/observing on non-explicit evidence)
# the rubric's "voice is only adjectives" trap — a brand idea that is JUST these is interchangeable
GENERIC = {"modern", "bold", "simple", "innovative", "trusted", "clean", "friendly", "premium",
           "playful", "minimal", "approachable", "dynamic", "human", "authentic", "fresh", "sleek"}
# stopwords don't count as substantive — else "modern, bold, AND simple" reads as non-generic
STOPWORDS = {"and", "the", "a", "an", "of", "to", "is", "are", "be", "with", "for", "or", "that",
             "this", "it", "as", "our", "we", "you", "your", "but", "yet", "so", "in", "on", "at"}
# generic filler nouns don't rescue adjective-salad either — "modern, bold, simple SOLUTIONS" is still
# interchangeable. A real idea names a concrete subject (agreements, signing, tax), not a category word.
GENERIC_NOUNS = {"solutions", "solution", "products", "product", "experiences", "experience", "platform",
                 "platforms", "tools", "services", "service", "brands", "brand", "company", "business",
                 "results", "value", "values", "innovation", "technology", "things", "stuff", "design",
                 "designs", "ideas", "world", "future", "way", "ways", "people"}


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
    """Return (fails, warns), each a list of (kind, message) — so --json carries a real kind, and a
    malformed card produces a graded FAIL rather than a traceback."""
    fails, warns = [], []

    def F(kind, msg):
        fails.append((kind, msg))

    def W(kind, msg):
        warns.append((kind, msg))

    if not isinstance(card, dict):
        F("WELL_FORMED", "card is not a JSON object (got %s)" % type(card).__name__)
        return fails, warns
    brand = card.get("brand", "<card>")

    strat = card.get("strategy")
    if strat is None:
        strat = {}
    elif not isinstance(strat, dict):
        F("WELL_FORMED", "%s: strategy is not an object" % brand)
        strat = {}
    idea = (strat.get("brand_idea") or "").strip()
    if not idea:
        F("WELL_FORMED", "%s: no strategy.brand_idea — the spec has no core to propagate (A1 gate)" % brand)
    else:
        words = re.findall(r"[a-z']+", idea.lower())
        nongeneric = [w for w in words if w not in GENERIC and w not in STOPWORDS
                      and w not in GENERIC_NOUNS and len(w) > 2]
        if words and not nongeneric:
            F("GENERIC_IDEA", "%s: GENERIC_IDEA — brand_idea is only interchangeable adjectives/filler "
              "(%r); a competitor could copy-paste it (rubric weak signal #1)" % (brand, idea))

    chain = strat.get("meaning_chain") or []
    if idea and len(chain) < 4:
        W("MEANING_CHAIN", "%s: meaning_chain has %d links — the idea isn't propagated to the "
          "primitives (idea→voice→mark→color→type→…)" % (brand, len(chain)))

    # provenance + truth + value on every typed record. LOW_CONFIDENCE and COLLAPSED_TRUTH are B2 GATE
    # failures (the trust contract), not advisories — an unflagged weak inference or a collapsed truth
    # reads as a settled rule, the exact defect the three-truths model exists to stop.
    def _provenance(rec, kind, rid):
        ev = rec.get("evidence")
        if not ev:
            F("UNTRACED", "%s: UNTRACED — %s '%s' has no evidence[] (every non-obvious claim needs a "
              "source)" % (brand, kind, rid))
        elif isinstance(ev, list) and any(
                isinstance(e, dict) and not (e.get("deck_id") or e.get("slide_id") or e.get("source_url"))
                for e in ev):
            # present but pointing nowhere — a structural strengthening of the presence-only check (it
            # still can't prove the deck_id is REAL; confirm that out of band)
            W("THIN_EVIDENCE", "%s: THIN_EVIDENCE — %s '%s' has an evidence entry with no "
              "deck_id/slide_id/source_url (it points nowhere)" % (brand, kind, rid))
        conf = rec.get("confidence")
        is_num = isinstance(conf, (int, float)) and not isinstance(conf, bool)
        if conf is None:
            F("WELL_FORMED", "%s: %s '%s' has no confidence" % (brand, kind, rid))
        elif not is_num or not 0 <= conf <= 1:
            F("WELL_FORMED", "%s: %s '%s' confidence %r not in [0,1]" % (brand, kind, rid, conf))
        elif conf < CONFIDENCE_REVIEW and rec.get("truth") == "inferred" and not rec.get("review"):
            F("LOW_CONFIDENCE", "%s: LOW_CONFIDENCE — inferred %s '%s' at %.2f (< %.2f) not marked "
              "review (B2 gate — an unflagged weak inference reads as settled)"
              % (brand, kind, rid, conf, CONFIDENCE_REVIEW))
        t = rec.get("truth")
        if t is not None and t not in TRUTHS:
            F("COLLAPSED_TRUTH", "%s: COLLAPSED_TRUTH — %s '%s' truth %r not one of "
              "observed/inferred/proposed (B2 gate)" % (brand, kind, rid, t))
        # coherence: an 'observed' claim you're not ~certain of is really an inference (band↔truth)
        if t == "observed" and is_num and conf < CONFIDENCE_EXPLICIT:
            W("TRUTH_CONFIDENCE_MISMATCH", "%s: TRUTH_CONFIDENCE_MISMATCH — %s '%s' is 'observed' at "
              "%.2f (< %.2f explicit); a direct observation you're unsure of is an inference"
              % (brand, kind, rid, conf, CONFIDENCE_EXPLICIT))

    def _records(key):
        recs = card.get(key) or []
        if not isinstance(recs, list):
            F("WELL_FORMED", "%s: %s is not a list" % (brand, key))
            return []
        out = []
        for i, rec in enumerate(recs):
            if isinstance(rec, dict):
                out.append(rec)
            else:
                F("WELL_FORMED", "%s: %s[%d] is not an object" % (brand, key, i))
        return out

    rule_ids = set()
    for r in _records("rules"):
        rid = r.get("id", "?")
        rule_ids.add(r.get("id"))
        _provenance(r, "rule", rid)
        sev = r.get("severity")
        if sev not in SEVERITIES:
            F("WELL_FORMED", "%s: rule '%s' severity %r not in %s" % (brand, rid, sev,
                                                                      sorted(SEVERITIES)))
        if _norm_domain(r.get("domain")) not in DOMAINS:
            W("UNKNOWN_DOMAIN", "%s: rule '%s' domain %r not a known brand domain"
              % (brand, rid, r.get("domain")))
        # coherence: a 'must' (hard) rule on non-explicit evidence — don't mandate what wasn't stated
        rc = r.get("confidence")
        if sev == "must" and isinstance(rc, (int, float)) and not isinstance(rc, bool) \
                and rc < CONFIDENCE_EXPLICIT:
            W("WEAK_MANDATE", "%s: WEAK_MANDATE — rule '%s' is 'must' (hard) at confidence %.2f "
              "(< %.2f explicit); don't hard-mandate what the source didn't explicitly state"
              % (brand, rid, rc, CONFIDENCE_EXPLICIT))
    for tok in _records("tokens"):
        tid = tok.get("id", "?")
        _provenance(tok, "token", tid)
        if tok.get("type") not in TOKEN_TYPES:
            W("UNKNOWN_TYPE", "%s: token '%s' type %r unknown" % (brand, tid, tok.get("type")))
        if "value" in tok and not (tok.get("role") and tok.get("meaning")):
            W("BARE_TOKEN", "%s: BARE_TOKEN — '%s' has a value but no role+meaning (a palette, not a "
              "system)" % (brand, tid))
    for ex in _records("examples"):
        eid = ex.get("id", "?")
        if not ex.get("evidence"):
            W("UNTRACED_EXAMPLE", "%s: example '%s' has no evidence[]" % (brand, eid))
        for ref in ex.get("rules_demonstrated") or []:
            if ref not in rule_ids:
                W("DANGLING_REF", "%s: DANGLING_REF — example '%s' demonstrates rule '%s', which is "
                  "not in the card (a broken retrieval link — B5)" % (brand, eid, ref))

    # contrast — the one accessibility joint a deck rarely proves by hand
    for p in _records("color_pairs"):
        try:
            ratio = contrast(p["fg"], p["bg"])
        except (KeyError, ValueError, TypeError) as e:
            W("BAD_PAIR", "%s: color_pair %r unreadable (%s)" % (brand, p.get("name", "?"), e))
            continue
        floor = _aa_floor(p.get("size", "normal"), p.get("role", "text"))
        if ratio < floor:
            F("CONTRAST_FAIL", "%s: CONTRAST_FAIL — pair '%s' %.2f:1 below AA %.1f (the color system "
              "isn't accessible here)" % (brand, p.get("name", "?"), ratio, floor))

    # completeness — every domain covered by at least one rule or token; surfaces present
    domains_obj = card.get("domains") or {}
    domains_present = {_norm_domain(d) for d in domains_obj} if isinstance(domains_obj, dict) else set()
    rule_domains = {_norm_domain(r.get("domain")) for r in (card.get("rules") or []) if isinstance(r, dict)}
    tok_domains = set()
    for t in (card.get("tokens") or []):
        if not isinstance(t, dict):
            continue
        tt = t.get("type")
        tok_domains.add({"color": "color", "type": "type", "space": "expression", "radius": "expression",
                         "motion": "expression", "elevation": "expression"}.get(tt, tt))
    have = domains_present | rule_domains | tok_domains
    missing = [d for d in DOMAINS if d not in have]
    if missing:
        W("INCOMPLETE", "%s: INCOMPLETE — domains with no rule/token: %s (the spec can't answer "
          "'how here?' for them)" % (brand, ", ".join(missing)))
    if not card.get("surfaces"):
        W("INCOMPLETE", "%s: INCOMPLETE — no surfaces[] (an OUTSIDE-IN spec must say where the brand "
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


# --- the formal schema artifact (declarative contract) + a drift guard ------------------------
def _schema_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "schema",
                        "brand-spec.schema.json")


def _schema_coherence():
    """The formal schema (schema/brand-spec.schema.json) and this gate must not silently diverge.
    Assert the enums agree and the GREEN fixture meets the schema's required-field contract. This is a
    bounded coherence check, NOT a general JSON-Schema validator — validate an arbitrary card against
    the schema with type-decomposer's instance-check.py or any JSON-Schema tool."""
    errs = []
    try:
        sch = json.load(open(_schema_path(), encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return ["schema/brand-spec.schema.json unreadable (%s)" % e]
    defs = sch.get("$defs", {})
    try:
        enum_checks = [
            ("rule.severity", set(defs["rule"]["properties"]["severity"]["enum"]), SEVERITIES),
            ("truth", set(defs["truth"]["enum"]), TRUTHS),
            ("token.type", set(defs["token"]["properties"]["type"]["enum"]), TOKEN_TYPES),
            ("rule.domain", set(defs["rule"]["properties"]["domain"]["enum"]),
             set(DOMAINS) | set(DOMAIN_ALIASES)),
        ]
    except KeyError as e:
        return ["schema shape changed — missing %s (schema/bin drift)" % e]
    for name, in_schema, in_bin in enum_checks:
        if in_schema != in_bin:
            errs.append("schema/bin enum drift on %s: schema=%s bin=%s"
                        % (name, sorted(in_schema), sorted(in_bin)))

    def _need(obj, where, reqd):
        for k in reqd:
            if not isinstance(obj, dict) or k not in obj:
                errs.append("GREEN fixture violates schema-required %s.%s" % (where, k))

    _need(GREEN, "card", sch.get("required", []))
    _need(GREEN.get("strategy", {}), "strategy", sch["properties"]["strategy"].get("required", []))
    for r in GREEN.get("rules", []):
        _need(r, "rule[%s]" % r.get("id"), defs["rule"].get("required", []))
    for t in GREEN.get("tokens", []):
        _need(t, "token[%s]" % t.get("id"), defs["token"].get("required", []))
    for ex in GREEN.get("examples", []):
        _need(ex, "example[%s]" % ex.get("id"), defs["example"].get("required", []))
    for p in GREEN.get("color_pairs", []):
        _need(p, "color_pair", defs["color_pair"].get("required", []))
    return errs


def selftest():
    errs = []
    errs += _schema_coherence()
    gf, gw = check_card(GREEN)
    if gf:
        errs.append("GREEN (DocuSign) card produced FAILs: %s" % gf)
    if gw:  # a complete, traced, accessible card must be clean of WARNs too (no false positives)
        errs.append("GREEN (DocuSign) card produced false-positive WARNs: %s" % gw)
    rf, rw = check_card(RED)
    rk = {k for k, _ in rf}
    # LOW_CONFIDENCE and COLLAPSED_TRUTH are GATE FAILS (B2), not advisories — assert they're in fails
    for kind in ["GENERIC_IDEA", "UNTRACED", "CONTRAST_FAIL", "LOW_CONFIDENCE", "COLLAPSED_TRUTH"]:
        if kind not in rk:
            errs.append("RED card missed gate-fail %s (fail kinds=%s)" % (kind, sorted(rk)))
    if not any("severity" in m for _k, m in rf):
        errs.append("RED card: bad severity 'loud' not caught")
    if not any(k == "BARE_TOKEN" for k, _ in rw):
        errs.append("RED card: BARE_TOKEN not warned")
    # contrast math sanity (shared with contrast-check)
    if not (abs(contrast("#000", "#fff") - 21.0) < 0.01 and contrast("#9aa0a6", "#ffffff") < 4.5):
        errs.append("contrast math wrong")
    # adversarial: a bool confidence must NOT pass as a valid number (the "true accepted for an int" trap)
    bf, _ = check_card({"brand": "B", "strategy": {"brand_idea": "A specific forcing idea about X."},
                        "tokens": [{"id": "t", "type": "color", "role": "text", "value": "#000",
                                    "meaning": "ink", "evidence": _EV, "confidence": True}]})
    if not any("confidence True not in [0,1]" in m for _k, m in bf):
        errs.append("bool confidence (True) accepted as a valid number (fails=%s)" % bf)
    # adversarial: GENERIC_IDEA must NOT be evaded by one filler noun…
    ef, _ = check_card({"strategy": {"brand_idea": "Modern, bold, simple solutions."}})
    if not any(k == "GENERIC_IDEA" for k, _ in ef):
        errs.append("GENERIC_IDEA evaded by a filler noun ('…simple solutions')")
    # …but must NOT false-positive on a real, specific idea naming a concrete subject
    rf2, _ = check_card({"strategy": {"brand_idea": "Agreements are dynamic moments of connection."}})
    if any(k == "GENERIC_IDEA" for k, _ in rf2):
        errs.append("GENERIC_IDEA false-positive on a real, specific idea")
    # adversarial: malformed inputs must FAIL cleanly, never raise (the --json contract must hold)
    for bad in [[], None, "txt", {"strategy": "txt"}, {"rules": "oops"}, {"color_pairs": ["#000"]}]:
        try:
            mfails, _mw = check_card(bad)
        except Exception as exc:  # noqa: BLE001 — the whole point is "no uncaught exception"
            errs.append("check_card crashed on %r (%s)" % (bad, exc))
            continue
        if not mfails:
            errs.append("malformed card %r produced no FAIL" % (bad,))
    # coherence smells (must-flag): a 'must' rule + an 'observed' token, both at 0.80 (< 0.90 explicit,
    # but >= 0.75 so LOW_CONFIDENCE stays quiet — isolating the two coherence checks)
    coh, cw = check_card({"strategy": {"brand_idea": "Agreements are dynamic moments of connection."},
                          "rules": [{"id": "m", "domain": "mark", "statement": "x", "severity": "must",
                                     "evidence": _EV, "confidence": 0.80, "truth": "inferred"}],
                          "tokens": [{"id": "tk", "type": "color", "role": "text", "value": "#000",
                                      "meaning": "ink", "evidence": _EV, "confidence": 0.80,
                                      "truth": "observed"}]})
    ck = {k for k, _ in cw}
    for kind in ["WEAK_MANDATE", "TRUTH_CONFIDENCE_MISMATCH"]:
        if kind not in ck:
            errs.append("coherence smell %s not raised (warn kinds=%s)" % (kind, sorted(ck)))
    # …must-NOT-flag: a 'should' rule and an 'inferred' record at the same 0.80 are coherent
    _ok, okw = check_card({"strategy": {"brand_idea": "Agreements are dynamic moments of connection."},
                           "rules": [{"id": "s", "domain": "mark", "statement": "x", "severity": "should",
                                      "evidence": _EV, "confidence": 0.80, "truth": "inferred"}]})
    if any(k in ("WEAK_MANDATE", "TRUTH_CONFIDENCE_MISMATCH") for k, _ in okw):
        errs.append("coherence smell false-positive on a should/inferred record (warns=%s)" % okw)
    # evidence integrity (must-flag): a dangling rules_demonstrated ref + a pointer-less evidence entry
    _ef2, ew2 = check_card({"strategy": {"brand_idea": "Agreements are dynamic moments of connection."},
                            "rules": [{"id": "real", "domain": "mark", "statement": "x",
                                       "severity": "should", "evidence": [{"note": "trust me"}],
                                       "confidence": 0.80, "truth": "inferred"}],
                            "examples": [{"id": "e", "surface": "web", "description": "d",
                                          "rules_demonstrated": ["ghost"], "evidence": _EV}]})
    ek = {k for k, _ in ew2}
    for kind in ["DANGLING_REF", "THIN_EVIDENCE"]:
        if kind not in ek:
            errs.append("evidence-integrity %s not raised (warn kinds=%s)" % (kind, sorted(ek)))
    return errs


def _report(card, fails, warns, as_json):
    brand = card.get("brand", "<card>") if isinstance(card, dict) else "<card>"
    if as_json:
        find = [{"kind": k, "severity": "fail", "location": brand, "message": m} for k, m in fails]
        find += [{"kind": k, "severity": "advisory", "location": brand, "message": m} for k, m in warns]
        print(json.dumps({"tool": "brand-spec-check", "ok": not fails,
                          "summary": "%d fail, %d advisory" % (len(fails), len(warns)),
                          "findings": find}, indent=2))
        return 1 if fails else 0
    for _k, w in warns:
        print("  ⚠ %s" % w)
    if fails:
        sys.stderr.write("brand-spec-check: FAIL (%d)\n" % len(fails))
        for _k, f in fails:
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
    if argv[0] == "schema":
        try:
            sys.stdout.write(open(_schema_path(), encoding="utf-8").read())
        except OSError as e:
            sys.stderr.write("brand-spec-check: schema unreadable (%s)\n" % e)
            return 2
        return 0
    if argv[0] == "lint":
        try:
            card = json.load(open(argv[1], encoding="utf-8"))
        except (OSError, IndexError, json.JSONDecodeError) as e:
            sys.stderr.write("brand-spec-check: unreadable card (%s)\n" % e)
            return 2
        fails, warns = check_card(card)
        return _report(card, fails, warns, as_json)
    sys.stderr.write("usage: brand-spec-check.py lint <card> | contrast <fg> <bg> | schema | "
                     "selftest [--json]\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
