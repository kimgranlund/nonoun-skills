# Roadmap — routing-decomposer

Ships its core in 0.1.0 (the two axes, the routing eval, the description linter, the corpus +
scorecard protocol, the craft rewrites). Everything below is additive.

## Fixed in 0.1.1 (review pass)

- **B1 fence inversion** — `routing-eval.py` now parses the `NOT for …` clause OUT of the positive
  routing tokens and makes the fenced vocabulary *repel* (lower a phrase's score), so adding the
  doctrine's truthful sibling fence improves precision instead of magnetizing the very siblings it
  disclaims. Pinned by paired selftest fixtures (`FENCE_BASE_DESC` / `FENCE_WITH_DESC`).
- **Eval demoted from "the proof" to a legibility AID** (M2) — a green F1 no longer certifies a
  description (a keyword list echoing the corpus scores F1 1.000, now a selftest fixture); the pass
  condition across SKILL.md / policy.md / routing-axis.md / decomposition-method.md / eval-corpus.md is
  `description-lint` clean + a human read of the named misses/grabs.
- **Lexical-overlap-only / can't-grade-B4** (M1) stated plainly in the docs — a low recall on a
  paraphrase may be a proxy artifact, not a defect; B4 robustness is the human's call.
- **Checked-in dogfood corpus** (M3) — `routing-decomposer.corpus.json` added and listed in
  `skill.json`; eval of the skill's own description against it records F1 ≈ 0.86.
- **skills-studio repositioned as a global/external peer**, not an in-repo testable boundary;
  corpus negatives + B3 now point at the real in-repo `*-decomposer` siblings (B2).
- **description-lint minors** — fence detection at clause boundary (idiom "not for the faint of heart"
  no longer suppresses the missing-fence warn); whole-word capability-verb detection ("planetary" no
  longer matches "plan"); vague-category quotes ("various things", "routing tasks") no longer count as
  concrete triggers. Each pinned by a fixture.

## Deferred / known limitations

- **The proxy is lexical-overlap only.** It cannot measure paraphrase/synonym routing (B4) or true
  model behavior. The `--vs sibling-desc.txt` boundary mode and a non-overlap match model (below) would
  reduce, not eliminate, this. Until then the docs are explicit that the human read is the proof.
- **No automated harvest of live sibling descriptions** for the corpus — negatives are curated by hand
  (the corpus-builder helper below would close this).

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
