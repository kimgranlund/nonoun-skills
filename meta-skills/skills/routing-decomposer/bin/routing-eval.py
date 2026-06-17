#!/usr/bin/env python3
"""routing-eval.py — the routing-decomposer ROUTING gate. Self-contained (stdlib only).

A skill's frontmatter `description` is a ROUTING CLASSIFIER, not prose: the model reads it to decide
whether a request belongs to this skill. You cannot eyeball its precision/recall — you must MEASURE
it against a labeled corpus of phrases that SHOULD trigger it (positives) and phrases that SHOULD NOT
(negatives, drawn adversarially from sibling skills and near-misses). This tool routes the B-axis
(B1 Fires / B2 Holds / B3 Boundary) to a TRANSPARENT, deterministic match model: a phrase "would
route here" iff its content-token overlap with the description clears a threshold. We then read
precision / recall / F1, and list the misses (positives the description fails to fire on — recall
holes) and the false positives (negatives it wrongly grabs — precision holes).

The match model is deliberately simple and inspectable — it is a *proxy* for a real model's routing,
calibrated to reward the same property a real description needs: concrete trigger phrases the request
language can land on. A description that scores well here (covers its positives, repels its negatives)
is one whose routing signal is legible; a description that misses obvious positives or grabs sibling
negatives is reported with the exact phrases so you can fix the wording, not the score.

Corpus (JSON):
  { "positives": ["decompose this skill's description", "grade the routing surface", ...],
    "negatives": ["author a whole new skill end to end", "score a UI layout", ...] }

  python3 bin/routing-eval.py selftest
  python3 bin/routing-eval.py <description.txt> <corpus.json> [--threshold 0.34] [--min-f1 0.7]

Exits nonzero if F1 is below --min-f1 (default 0.7). Python 3.8+.
"""
import json
import math
import os
import re
import sys

# Tokens with no routing signal — they appear in nearly every description and request, so counting
# them as "overlap" would let a vague description match everything. Stripping them is what makes the
# overlap score track *concrete* trigger signal rather than filler.
STOP = {
    "a", "an", "the", "and", "or", "of", "to", "for", "in", "on", "is", "it", "this", "that",
    "with", "as", "at", "by", "be", "are", "from", "into", "over", "your", "you", "i", "we",
    "do", "does", "not", "no", "use", "using", "used", "when", "what", "which", "how", "can",
    "should", "would", "will", "my", "our", "its", "their", "them", "these", "those", "any",
    "all", "some", "one", "two", "up", "out", "if", "so", "but", "than", "then", "also", "via",
    "per", "each", "etc", "eg", "ie", "vs", "across", "about", "more", "less", "new", "make",
}
# Light stemming so "routing" matches "route", "triggers" matches "trigger", etc. Order matters:
# longest suffix first.
_SUFFIXES = ("ization", "izations", "ingly", "ing", "ied", "ies", "ied", "ers", "er", "ed", "es", "s")


def _stem(tok):
    for suf in _SUFFIXES:
        if len(tok) > len(suf) + 2 and tok.endswith(suf):
            return tok[: -len(suf)]
    return tok


def tokenize(text):
    """Lowercase content tokens (stemmed, stopwords + sub-3-char noise removed)."""
    raw = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]*", text.lower())
    out = []
    for t in raw:
        t = t.strip("-_")
        if not t or t in STOP or len(t) < 3:
            continue
        out.append(_stem(t))
    return out


def description_tokens(description):
    """The set of content tokens the description offers as routing signal."""
    return set(tokenize(description))


def routes_here(phrase, desc_tokens, threshold):
    """Deterministic proxy for 'would the model route this phrase to this skill?'.

    Score = fraction of the PHRASE's content tokens that the description also carries. A request
    routes here iff that fraction clears the threshold — i.e. the description names enough of what
    the request is about. Returns (bool, score)."""
    pt = tokenize(phrase)
    if not pt:
        return (False, 0.0)
    hits = sum(1 for t in set(pt) if t in desc_tokens)
    score = hits / len(set(pt))
    return (score >= threshold, score)


def evaluate(description, corpus, threshold=0.34):
    """Run the routing proxy over the corpus; return a metrics + diagnostics dict."""
    dt = description_tokens(description)
    pos = corpus.get("positives", []) or []
    neg = corpus.get("negatives", []) or []
    tp, fn, missed = 0, 0, []
    for p in pos:
        ok, sc = routes_here(p, dt, threshold)
        if ok:
            tp += 1
        else:
            fn += 1
            missed.append((p, round(sc, 2)))
    fp, tn, grabbed = 0, 0, []
    for n in neg:
        ok, sc = routes_here(n, dt, threshold)
        if ok:
            fp += 1
            grabbed.append((n, round(sc, 2)))
        else:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return {
        "n_pos": len(pos), "n_neg": len(neg),
        "tp": tp, "fn": fn, "fp": fp, "tn": tn,
        "precision": round(precision, 3), "recall": round(recall, 3), "f1": round(f1, 3),
        "missed_positives": missed,      # recall holes — under-trigger
        "grabbed_negatives": grabbed,    # precision holes — over-trigger
        "threshold": threshold,
        "desc_token_count": len(dt),
    }


# --- selftest fixtures -------------------------------------------------------------------------
# A well-built description: names its capability (grade/decompose a skill's description/routing),
# its scope (precision/recall, the eval corpus), and concrete triggers — and is fenced against the
# sibling (whole-skill authoring).
GOOD_DESC = (
    "Grade and decompose the routing surface of a skill — its frontmatter description — measuring "
    "whether it fires on the right requests and holds against the wrong ones. Run a routing eval "
    "over a labeled corpus of trigger phrases to score precision, recall, and F1, then fix the "
    "wording that mis-routes (under-trigger or over-trigger). Triggers on: grade this description, "
    "is this description routing correctly, why does my skill not fire, why does it over-trigger, "
    "score the routing, build a routing corpus. NOT for authoring a whole skill end to end "
    "(skills-studio)."
)
GOOD_CORPUS = {
    "positives": [
        "grade this skill's description",
        "is my description routing correctly",
        "why does my skill never fire on real requests",
        "this skill over-triggers and grabs the wrong requests",
        "score the precision and recall of this routing surface",
        "build a routing corpus for my skill",
        "measure whether this description fires on the right phrases",
        "fix the wording that mis-routes",
    ],
    "negatives": [
        "author a whole new skill from scratch end to end",
        "run the adversarial critic panel on my plugin",
        "decompose this UI layout into regions",
        "grade a unit of code against its contract",
        "convert design tokens between formats",
        "write the CSS for this component",
    ],
}
# A description that READS well but MIS-ROUTES: it describes the capability in abstract,
# capability-honest prose but names none of the concrete trigger words the requests use, so it
# under-triggers (low recall). This is the "reads well, mis-routes" quadrant — the eval must catch it.
MISROUTING_DESC = (
    "An instrument for the qualitative appraisal of textual metadata pertaining to the "
    "discoverability of capabilities within an agentic context, emphasizing rhetorical clarity and "
    "the felicitous selection of lexical signifiers."
)
# A description so broad it grabs the sibling negatives too — over-trigger (low precision).
OVERBROAD_DESC = (
    "Grade, score, decompose, review, audit, evaluate, check, measure, analyze, and improve any "
    "skill, description, layout, component, code, token, corpus, plugin, routing, UI, and contract "
    "for quality, correctness, fit, and coherence across every axis and dimension."
)


def selftest():
    errs = []
    # 1. tokenize strips stopwords / short noise / stems
    toks = set(tokenize("Grade the ROUTING of a skill's descriptions"))
    if "the" in toks or "of" in toks:
        errs.append("tokenize did not strip stopwords: %s" % sorted(toks))
    if "rout" not in toks and "route" not in toks and "routing" not in toks:
        errs.append("tokenize lost the 'routing' signal: %s" % sorted(toks))
    if "description" not in toks and "descript" not in toks:
        errs.append("tokenize/stem dropped 'descriptions': %s" % sorted(toks))

    # 2. the GOOD description scores well — high F1, fires on its positives, holds its negatives
    g = evaluate(GOOD_DESC, GOOD_CORPUS)
    if g["f1"] < 0.7:
        errs.append("GOOD description scored F1=%.2f (< 0.7); missed=%s grabbed=%s"
                    % (g["f1"], g["missed_positives"], g["grabbed_negatives"]))
    if g["recall"] < 0.7:
        errs.append("GOOD description recall too low: %.2f (missed %s)" % (g["recall"], g["missed_positives"]))
    if g["precision"] < 0.7:
        errs.append("GOOD description precision too low: %.2f (grabbed %s)" % (g["precision"], g["grabbed_negatives"]))

    # 3. the MIS-ROUTING (reads-well-but-vague) description under-triggers: it must MISS positives
    m = evaluate(MISROUTING_DESC, GOOD_CORPUS)
    if not m["missed_positives"]:
        errs.append("mis-routing description wrongly fired on every positive (recall=%.2f)" % m["recall"])
    if m["recall"] >= g["recall"]:
        errs.append("mis-routing description should have LOWER recall than GOOD (%.2f vs %.2f)"
                    % (m["recall"], g["recall"]))

    # 4. the OVER-BROAD description over-triggers: it must GRAB negatives (precision hole)
    o = evaluate(OVERBROAD_DESC, GOOD_CORPUS)
    if not o["grabbed_negatives"]:
        errs.append("over-broad description wrongly held all negatives (precision=%.2f)" % o["precision"])
    if o["precision"] >= g["precision"]:
        errs.append("over-broad description should have LOWER precision than GOOD (%.2f vs %.2f)"
                    % (o["precision"], g["precision"]))

    # 5. routes_here is monotone in overlap and empty-safe
    dt = description_tokens(GOOD_DESC)
    if routes_here("", dt, 0.34)[0]:
        errs.append("empty phrase wrongly routed")
    on, son = routes_here("grade this skill's description routing", dt, 0.34)
    off, soff = routes_here("xyzzy plugh quux frobnitz", dt, 0.34)
    if not on or off:
        errs.append("routes_here on/off-target wrong: on=%s(%.2f) off=%s(%.2f)" % (on, son, off, soff))
    return errs


def _fmt_metrics(m):
    print("routing-eval — %d positive(s), %d negative(s), threshold %.2f, %d description token(s)"
          % (m["n_pos"], m["n_neg"], m["threshold"], m["desc_token_count"]))
    print("  precision %.3f   recall %.3f   F1 %.3f   (tp=%d fp=%d fn=%d tn=%d)"
          % (m["precision"], m["recall"], m["f1"], m["tp"], m["fp"], m["fn"], m["tn"]))
    if m["missed_positives"]:
        print("  recall holes — positives that do NOT route here (under-trigger):")
        for p, sc in m["missed_positives"]:
            print("    ✗ %.2f  %s" % (sc, p))
    if m["grabbed_negatives"]:
        print("  precision holes — negatives this WRONGLY grabs (over-trigger):")
        for n, sc in m["grabbed_negatives"]:
            print("    ✗ %.2f  %s" % (sc, n))
    if not m["missed_positives"] and not m["grabbed_negatives"]:
        print("  ✓ every positive fires and every negative holds")


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("routing-eval: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("routing-eval: OK — tokenizer + precision/recall/F1 + under/over-trigger detection verified")
        return 0
    if len(argv) < 2:
        sys.stderr.write("usage: routing-eval.py <description.txt> <corpus.json> [--threshold T] [--min-f1 F]\n")
        return 2
    desc_path, corpus_path = argv[0], argv[1]
    threshold = float(argv[argv.index("--threshold") + 1]) if "--threshold" in argv else 0.34
    min_f1 = float(argv[argv.index("--min-f1") + 1]) if "--min-f1" in argv else 0.7
    try:
        description = open(desc_path, encoding="utf-8").read()
        corpus = json.load(open(corpus_path, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write("routing-eval: bad input — %s\n" % e)
        return 2
    if not isinstance(corpus, dict) or not (corpus.get("positives") or corpus.get("negatives")):
        sys.stderr.write("routing-eval: corpus must be {\"positives\":[...], \"negatives\":[...]}\n")
        return 2
    m = evaluate(description, corpus, threshold)
    _fmt_metrics(m)
    if m["f1"] < min_f1:
        sys.stderr.write("routing-eval: FAIL — F1 %.3f below --min-f1 %.2f. "
                         "Fix the wording, not the corpus: add trigger words for the missed positives; "
                         "tighten scope / add a NOT-for fence for the grabbed negatives.\n"
                         % (m["f1"], min_f1))
        return 1
    print("routing-eval: OK — F1 %.3f >= %.2f" % (m["f1"], min_f1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
