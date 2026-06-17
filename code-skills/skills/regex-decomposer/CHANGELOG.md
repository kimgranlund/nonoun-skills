# Changelog — regex-decomposer

Versioned independently of the `code-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.1.0 — draft

Initial release. Decompose / design / grade a regular expression on the **LANGUAGE × MATCH** crossing
axes, scored separately with a gated rubric and the opposite-defect quadrant.

- **The two-axis method** (`references/decomposition-method.md`): Language (target-set → anchoring →
  classes/quantifiers → groups → flags/dialect) × Match (compiles → examples → safety → robustness →
  readability), crossing at the pattern; gates before reviews; the *matches-the-examples-means-the-
  wrong-language* vs *right-intent-won't-run* quadrant; and the **example-set-is-the-contract**
  doctrine with the adversarial counter-example hunt.
- **The MATCH checker** (`references/match-axis.md` + `bin/regex-check.py`): reads a pattern-spec card,
  compiles the pattern (Python `re`), asserts every positive matches and every negative does NOT under
  the declared full/partial `mode`, and runs a static ReDoS-smell scan. `selftest` proves the
  compile + example + scan logic over good/bad fixtures (a passing spec, a missed positive, a matched
  negative, a nested-quantifier ReDoS smell) with no external deps; the file-path mode exits nonzero
  on any gate failure.
- **The LANGUAGE axis** (`references/language-axis.md`): target-set discipline (the OUT set is the
  contract), the anchoring traps (full vs partial, the substring over-match), and the fresh-context
  **adversarial counter-example hunt** for "means the wrong language."
- **ReDoS & safety** (`references/redos-and-safety.md`): the centerpiece — the catastrophic-
  backtracking taxonomy (nested quantifiers, overlapping alternation, quadratic `.*`), why each
  blows up, how the example + adversarial sets prove safety, and the atomic-group / possessive / RE2
  fixes.
- **Dialects** (`references/dialects.md`): PCRE · JS · Python · RE2/Go portability — the
  backtracking-vs-automaton split, the construct table (backrefs, lookaround, atomic groups, Unicode
  scope), the quiet `\d`/`$`/`.` traps, and the safe portable core.
- **Policy** (`references/policy.md`): the 9-point definition-of-done, the pattern-spec card shape
  `{pattern, flags, engine, positives[], negatives[]}`, and the handoff seams to `code-decomposer`,
  `query-decomposer`, and `/verify`.

Second skill in the `code-skills` plugin (after `code-decomposer`).
