# Changelog — routing-decomposer

Versioned independently of the `meta-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.1.1 — draft (review pass)

Fixes from an adversarial review of the eval's own routing doctrine.

- **`routing-eval.py` — the fence now REPELS, not magnetizes (B1).** The proxy parses the `NOT for …`
  clause out of the positive routing tokens and treats the fenced sibling vocabulary as *negative*
  signal, so adding the doctrine's truthful sibling fence raises precision instead of grabbing the very
  siblings it disclaims. Pinned by paired fixtures (`FENCE_BASE_DESC` / `FENCE_WITH_DESC`).
- **The eval is reframed as a LEGIBILITY AID, not the proof (M2).** A green F1 no longer certifies a
  description — a grammarless keyword list echoing the corpus tokens scores F1 1.000 (new fixture). The
  pass condition, across all docs, is the `description-lint` pass + a human read of the named
  misses/grabs; `--min-f1` is a tripwire, not a verdict.
- **Stated plainly that the proxy is LEXICAL-OVERLAP ONLY and cannot grade B4 robustness (M1).** A low
  recall on a paraphrase/indirect positive may be a proxy artifact, not a defect.
- **Checked-in dogfood corpus (M3):** `routing-decomposer.corpus.json` (positives across phrasings;
  negatives from the in-repo `*-decomposer` siblings + the global peer skills-studio), added to
  `skill.json`. Eval of the skill's own description against it records F1 ≈ 0.86 (the named holes are
  paraphrase artifacts + adversarial-boundary grabs — the human-read material, not a defect list).
- **`skills-studio` repositioned as a global/external peer**, not an in-repo testable boundary; the B3
  boundary check and corpus negatives point at the real in-repo `*-decomposer` siblings.
- **`description-lint.py` minors:** clause-boundary fence detection (idiom "not for the faint of heart"
  no longer suppresses the missing-fence warn); whole-word capability-verb detection ("planetary" no
  longer matches "plan"); vague-category quotes ("various things", "routing tasks") no longer count as
  concrete triggers. Each pinned by a fixture.

## 0.1.0 — draft

Initial release. Decompose / write / grade a skill's **routing surface** — its frontmatter
`description` — on the **INSTRUCTION × ROUTING** crossing axes, scored separately with a gated rubric
and the opposite-defect quadrant.

- **The two-axis method** (`references/decomposition-method.md`): Instruction (capability → scope →
  triggers → disambiguation → economy) × Routing (fires → holds → boundary → robustness → stability),
  crossing at the description itself; gates before reviews; the *reads-well-mis-routes* vs
  *routes-accurately-but-misleads* quadrant; and the **measure-routing, gate-honesty-on-what-the-eval-
  can't-see** doctrine.
- **The routing eval** (`references/routing-axis.md` + `bin/routing-eval.py`): the centerpiece — a
  transparent, deterministic proxy for a model's routing (content-token overlap above a threshold)
  that scores precision / recall / F1 against a labeled corpus and lists the exact missed positives
  (recall holes) and grabbed negatives (precision holes). `selftest` proves a good description clears
  F1 ≥ 0.7 while a vague one under-triggers and a broad one over-triggers, with no external deps.
- **The eval corpus** (`references/eval-corpus.md`): how to build the labeled test — positives across
  the imperative / diagnostic / symptom / indirect families, and negatives drawn **adversarially**
  from sibling skills' own triggers + near-misses; the precision/recall/F1 read and the
  adversarial-negative discipline.
- **The description linter** (`bin/description-lint.py`): the A-axis static pre-filter — checks ≤1024,
  WHAT + WHEN/trigger + NOT-for signals, ≥N concrete quoted trigger phrases; flags first-person and
  vagueness words over good/bad fixtures.
- **The INSTRUCTION axis** (`references/instruction-axis.md`): capability honesty + no-overclaim, the
  NOT-for fence, disambiguating named siblings, and the ≤1024 economy — the honesty gates the eval
  cannot see.
- **Description craft** (`references/description-craft.md`): concrete before/after rewrites that move
  precision or recall (recall hole / precision hole / overclaim) and the trigger-phrase family
  patterns.
- **Policy** (`references/policy.md`): the 10-point definition-of-done, the corpus + scorecard shapes,
  and the handoff seam to `skills-studio` (whole-skill authoring) it defers to.

First skill in the new `meta-skills` plugin.
