---
name: regex-decomposer
description: >
  Decompose, design, and grade a regex on two crossing axes — LANGUAGE (target-set →
  anchoring → classes/quantifiers → groups → flags/dialect) and MATCH (compiles → examples → safety →
  robustness → readability) — scored separately so a pattern that matches the examples can't hide one
  that means the wrong language, nor a clever one hide that it won't run or ReDoS. MATCH routes
  to a self-tested checker (bin/regex-check.py): it compiles the pattern, asserts every positive
  matches and every negative does not, and runs a ReDoS scan (nested quantifiers, overlapping
  alternation). The wrong-language defect routes to an adversarial counter-example hunt. Backed by a
  gated rubric and a pattern-spec card {pattern, flags, engine, positives, negatives}. Use when
  designing a regex, grading one, hardening against ReDoS, or recovering what it matches. NOT for host
  code — a function graded on its spec (code-decomposer); a SQL query, its grain or performance
  (query-decomposer); or a UI layout into regions (layout-decomposer).
---

# regex-decomposer — grade a regular expression on two crossing axes

A regular expression is **correct on two independent axes that walk the same pattern in opposite
directions** — the decomposer seam the code-, layout-, and component-decomposers apply to a unit, to
space, and to a component, here applied to a single pattern:

- **Language · whole → part** grades the **intent**: the target-set the pattern *means* → its
  anchoring → its classes & quantifiers → its groups & captures → its flags & dialect. *"Is it the
  right language?"*
- **Match · part → whole** grades the **mechanism**: it compiles → matches the example set → is safe
  on adversarial input → is robust → is readable. *"Does it provably match, here?"*

They **cross at the pattern** — the regex text is *both* the claim (the language you mean: which
strings are in, which are out) and the executable matcher (what the engine actually runs). That
crossing is the whole technique: a pattern can be **matches the examples, means the wrong language**
(every positive passes, every negative fails, but it accidentally accepts strings the spec forbids —
overfit) or **right intent, won't run** (the target-set is exactly right, but the pattern won't
compile in the engine or catastrophically backtracks on a crafted input). Opposite defects, opposite
fixes — so you **score and report the two axes separately**, never averaged.

The reason this is outsized for an LLM author: the MATCH axis is exactly where models ship a
plausible-looking pattern that *won't compile* or *ReDoS-es* with total confidence — and it is
mechanizable, so the gate turns the worst failure into a caught error. And the **wrong-language**
quadrant — the one a passing example set hides — gets a dedicated attack: the example set is the
contract (run it as code), and "means the wrong language" is hunted with **adversarial
counter-examples**: strings the spec implies but the example set forgot.

## Quick Start

**You bring:** a pattern (a spec in words, an existing regex, a screenshot of one) and the question —
"write this", "is it right?", "will it ReDoS?", "what does this even match?". **You get:** a
pattern-spec card (target-set + pattern), a MATCH report card, and a two-axis grade with the defect
quadrant named.

> *"Match an ISO date like `2026-06-16`."* →
> 1. **Language — target-set first:** name the strings that MUST match (`2026-06-16`, `1999-01-01`)
>    and MUST NOT (`2026/06/16`, `26-6-16`, `99-99-99`, `2026-06-16x`) `[gate]`. Then **anchoring**:
>    a *full* match, not a substring — `2026-06-16x` and `x2026-06-16` MUST fail `[gate]`. This is the
>    #1 silent over-match.
> 2. **Match — run it, don't read it:** draft `\d{4}-\d{2}-\d{2}`; `bin/regex-check.py spec.json`
>    compiles it and runs the example set under `mode: "full"` `[gate, code]`, then scans for ReDoS
>    smells `[gate, code]`.
> 3. **Adversarial counter-example hunt:** in a fresh context, find a string the *spec* forbids that
>    the *pattern* still accepts (`9999-99-99`? `0000-00-00`?) — each is a missing **negative** that
>    proves the language is too wide. Add it; re-run.
> 4. **Review + report:** classes/quantifiers, groups, flags/dialect (A3–A5); robustness, readability
>    (B4/B5); then the two axis scores + the quadrant cell — gate failures first.

**Modes:** **SPECIFY** (target-set down → draft the pattern → emit a spec card) · **DECOMPOSE** (read
a pattern → recover its target-set → run the example set → grade) · **GRADE** (score both axes, gates
before reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Language** | whole → part | **A1** Target-set → **A2** Anchoring → **A3** Classes/quantifiers → **A4** Groups/captures → **A5** Flags/dialect | "Is it the *right language*?" |
| **B · Match** | part → whole | **B1** Compiles → **B2** Examples → **B3** Safety → **B4** Robustness → **B5** Readability | "Does it *provably match*, here?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on
that axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable pattern is **≥4 on every review
with zero gate failures**, reported as two separate axis scores plus the defect quadrant. The whole
B-gate ladder — **B1 compile · B2 examples · B3 safety** — routes to code: `bin/regex-check.py`.

## The doctrine — the example set is the contract; the spec is wider than its examples

The non-obvious core, and the reason it earns a skill:

- **The MATCH axis is the cheap, deterministic axis** — route B1/B2/B3 to `bin/regex-check.py` and
  **trust the tool, not the read-through**. An LLM cannot reliably tell by reading whether a pattern
  compiles, matches a given string, or backtracks catastrophically. The example set — every
  `positives[]` and `negatives[]` — is the pattern's contract; run it.
- **"Means the wrong language" is NOT a B failure** — a pattern that passes every example can still
  accept strings the spec forbids (an over-wide language). The example set proves the pattern matches
  *its examples*; it does **not** prove the pattern means the *spec's* language. Close that gap with
  an **adversarial counter-example hunt**: a fresh-context skeptic generates strings the spec implies
  but the example set forgot, and each accepted-but-forbidden string is a new negative. A pattern is
  only as correct as its negatives are mean.

## §SelfAudit

- **Anchoring is the silent over-match — check it first, after the target-set.** An unanchored
  pattern matches a *substring*; `\d{4}` "matches" `abc2026def`. Decide full-vs-partial **before**
  the character classes, and make `bin/regex-check.py` enforce it via the `mode` field. A missing
  `^…$` / `\b` is a gate failure, not a stylistic note.
- **Compile and run the example set; never certify a match from reading.** B1/B2/B3 are
  `bin/regex-check.py`, not inspection. An LLM ships patterns that don't compile or that quietly
  over-match with full confidence. An unrun gate is *no evidence*, not a pass.
- **A passing example set is evidence of nothing about the language until you've hunted
  counter-examples.** The dangerous defect — *matches the examples, means the wrong language* — is
  invisible to the example set by construction. Hunt the forbidden-but-accepted string in a fresh
  context; the author's examples inherit the author's blind spots.
- **Nested quantifiers and overlapping alternation are ReDoS until proven safe.** `(\w+)+`, `(a|a)*`,
  `(.*a){10}`, `.*.*` are catastrophic-backtracking smells. `bin/regex-check.py` flags them
  statically — but that scan is a **lossy pre-filter** (necessary, not sufficient: it can miss deeper
  nesting and over-flag), so clear a flag with a **manual** adversarial-input timing test (the tool
  does not run one — it is on the ROADMAP) or a rewrite (atomic groups / possessive / RE2), never by
  ignoring it.
- **Gates before reviews, always.** Don't grade groups or readability for a pattern that won't
  compile, or classes for one whose target-set is wrong. Stop each axis at its first failed gate.
- **Two scores, never one — and design/grade only, don't write the surrounding code.** *Wrong
  language* and *won't-run/ReDoS* need opposite fixes (re-spec the negatives vs rewrite the matcher).
  Report both axes and name the quadrant; never average. This skill locks the pattern-spec card and
  the grade; the host code that *calls* the regex is `code-decomposer`'s.

## Verify Target

A pattern is **done** when: its target-set is explicit (the strings that must match and must not,
A1); anchoring/full-vs-partial is decided and enforced (A2); classes/quantifiers, groups, and
flags/dialect score ≥4 (A3–A5); `bin/regex-check.py` ran and the **compile + example + safety** gates
are green (B1–B3); an adversarial counter-example hunt found no forbidden-but-accepted string (or the
ones it found are now negatives in the card); robustness + readability ≥4 (B4/B5); and both axes
score ≥4 with zero gate failures, landing in the **SHIPPABLE** quadrant — with the pattern-spec card
ready for the host (`code-decomposer`). **NOT done** when: it matches every example but accepts a
string the spec forbids (*matches the examples, means the wrong language*); or the target-set is
right but it won't compile in the engine or ReDoS-es on a crafted input (*right intent, won't run*);
or the example set has no negatives (the contract is half-written); or anchoring was never decided;
or one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Language × Match), the leveled walk (A1–A5 × B1–B5) with gates, the defect quadrant, the example-set-is-the-contract doctrine, and the SPECIFY / DECOMPOSE / GRADE workflows |
| `references/language-axis.md` | **the Language axis** — target-set discipline (the in/out sets you actually mean), the anchoring traps (full vs partial, `^ $ \b`, the substring over-match), and the **adversarial counter-example hunt** for "means the wrong language" |
| `references/match-axis.md` | **the Match axis** — the compile → example → safety ladder, how to read each engine's compile errors, the full/partial `mode` contract, and the robustness/readability reviews; mechanized by `bin/regex-check.py` |
| `references/redos-and-safety.md` | **any "will it ReDoS?" / safety question** — the centerpiece: the catastrophic-backtracking taxonomy (nested quantifiers, overlapping alternation, quadratic `.*`), why it blows up, and how the example + adversarial sets *prove* safety; the atomic-group / possessive / RE2 fixes |
| `references/dialects.md` | **any portability / engine question** — PCRE · JS · Python · RE2 · Go differences, what's portable and what isn't (lookbehind, backrefs, named groups, Unicode), and which engine kills ReDoS by construction |
| `references/policy.md` | **definition-of-done / handoff** — the pattern-spec card shape `{pattern, flags, engine, positives[], negatives[]}`, the 9-point DoD, and the seams to `code-decomposer`, `query-decomposer`, and `/verify` |
| `bin/regex-check.py` | **mechanizes B1–B3** — reads a pattern-spec card, compiles the pattern (Python `re`), asserts every positive matches and every negative does NOT under the `full`/`partial` mode, and runs a static ReDoS-smell scan (nested quantifier · overlapping alternation · quadratic wildcard). That scan is a **lossy pre-filter** — necessary, not sufficient; it can miss deeper nesting and over-flag, and it does **not** run a timing test (that step is manual). `<spec.json>` · `selftest` |
