# Roadmap — regex-decomposer

Ships its core in 0.1.0 (the two axes, the MATCH checker, the ReDoS-smell scan, the pattern-spec
card, the dialect table). Everything below is additive.

## `bin/regex-check.py`

- [ ] **A wall-clock ReDoS timing test** — beyond the static smell scan, run the pattern against the
      adversarial near-miss negative with a hard timeout (subprocess + `SIGALRM`) and FAIL if it
      doesn't reject fast. Turns B3's "smell" into a measured proof.
- [ ] **Multi-engine compile** — shell out to `node`, `pcre2grep`, or Go `regexp` (where present) so
      B1 is checked in the *declared* engine, not only Python `re` (a missing engine is a SKIP, like
      the execution-harness pattern).
- [ ] **Smell-scan precision** — the static scan is conservative (false positives over false
      negatives). Add an AST-ish parse of the pattern to cut false positives on safe nesting like
      `(?:ab)+` and to catch deeper nesting the regex-based scan misses.
- [ ] Emit a machine-readable report (JSON) so GRADE can fold the example misses + smells into the
      two-axis grade automatically.

## Method & corpus

- [ ] A **routing-eval corpus** (the maturity step the repo ROADMAP tracks) — especially the
      boundaries with `code-decomposer` (the host code), `query-decomposer` (SQL), and `/verify`
      (app-time), which are the likely mis-routes.
- [ ] A worked **end-to-end transcript** (an email or URL pattern: SPECIFY the target-set → draft →
      DECOMPOSE → find the over-match via the adversarial hunt → GRADE), with the pattern-spec card,
      the MATCH report, and the ReDoS near-miss checked in and dogfooded.
- [ ] An **adversarial-hunt template** (the fresh-context skeptic prompt) as a reusable reference,
      shared in shape with `code-decomposer`'s spec probe and `deep-research`'s verify step.
- [ ] A **pattern-family playbook** (like `code-decomposer`'s unit-families) — validator vs extractor
      vs tokenizer vs sanitizer, each with where the LANGUAGE defect hides and which gate is decisive
      — if the single method proves too thin per family.

## Plugin

- [ ] As `code-skills` grows, the sibling from the same lineage is `query-decomposer` (SQL: semantics
      × execution), tracked in `code-decomposer`'s ROADMAP — both share the deterministic example-set
      gate this skill mechanizes.
