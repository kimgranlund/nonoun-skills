# Roadmap — routing-decomposer

Ships its core in 0.1.0 (the two axes, the routing eval, the description linter, the corpus +
scorecard protocol, the craft rewrites). Everything below is additive.

## `bin/routing-eval.py`

- [ ] **Two-description boundary mode** (`--vs sibling-desc.txt`) — mechanize the B3 Boundary gate:
      score each boundary phrase against *both* descriptions and assert the sibling wins, instead of
      leaving it to a manual two-run comparison.
- [ ] **Better match models behind a flag** — the token-overlap proxy is transparent but coarse; add
      an optional TF-IDF / embedding-free n-gram model (still stdlib) and report the spread so a
      score isn't an artifact of one proxy.
- [ ] **Per-phrase score table + `--json`** so GRADE can fold the routing metrics into the scorecard
      and a CI step can gate a description change on no recall/precision regression.
- [ ] **Threshold sweep** (`--sweep`) — print precision/recall across thresholds (a mini ROC) so the
      calibration is visible rather than asserted.

## `bin/description-lint.py`

- [ ] **Read the live skill neighbourhood** — given a marketplace/plugin root, harvest sibling
      descriptions and warn when this description shares too many content tokens with a sibling (a
      structural over-trigger risk) before any corpus exists.
- [ ] **Overclaim heuristics** — flag capability verbs ("automatically", "optimizes", "fixes") whose
      object the skill's own `bin/`/modes don't support (best-effort; the honesty call stays human).
- [ ] Quoted-trigger **family coverage** check — warn when all triggers are one phrasing family
      (e.g. all imperative), the most common recall hole.

## Method & corpus

- [ ] A **corpus-builder helper** that, given a skill + its siblings, scaffolds a starter
      `*.corpus.json` (positives across families, negatives seeded from sibling triggers) for the
      author to harden.
- [ ] A worked **end-to-end transcript** (a SPECIFY → measure → fix-the-misses → GRADE on a real
      mis-routing description), with the corpus, the before/after metrics, and the wording diff
      checked in and dogfooded.
- [ ] **Dogfood across the marketplace** — run the eval over every shipped skill's description with
      its corpus as a periodic routing-health check (the maturity step the repo ROADMAP tracks).

## Plugin

- [ ] As `meta-skills` grows, candidate siblings from the same INSTRUCTION/ROUTING lineage about
      *meta* surfaces: a `command-decomposer` (slash-command name/description routing) and an
      `agent-decomposer` (subagent description selection) — both with the same adversarial-corpus eval.
