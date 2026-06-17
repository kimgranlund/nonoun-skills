# Changelog — routing-decomposer

Versioned independently of the `meta-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

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
