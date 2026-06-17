# The LANGUAGE axis — is it the right language?

The Language axis (A1–A5) grades *intent*, top-down: from the set of strings the pattern is *supposed
to* describe down to the dialect detail of how it's written. This is the axis the engine **cannot
see** — a compiler is silent on "this pattern means a different language than you intended." It is
also the axis an LLM fails silently on (a pattern that fits the three examples it was shown, by
accident), so it carries an **adversarial counter-example hunt**, not just a checklist.

## A1 · Target-set `[gate]`

A regex *is* a formal language: a (usually infinite) **set of strings**. Before writing or reading
one character of pattern, name that set as two concrete lists:

- **IN** — strings that MUST match. The positives.
- **OUT** — strings that MUST NOT match. The negatives — and these are where the real work is.

The trap is that **the IN set is easy and the OUT set is the contract.** Anyone can list a few
strings that should match. The language is *defined by its boundary* — the strings that look almost
right but must be rejected. "Match an email" is not a target-set; "match `a@b.co` but reject
`a@b`, `@b.co`, `a@@b.co`, `a b@c.co`" is the beginning of one.

- Write the target-set in the user's terms first (*"a US ZIP, 5 digits, optionally +4"*), then turn
  each clause into at least one positive and one negative.
- The **near-misses** are the highest-value negatives: one digit too many, the right shape with a
  forbidden character, the empty string, leading/trailing whitespace.
- **Gate:** if the target-set is wrong or fuzzy, stop — every level below polishes a pattern for the
  wrong language. This is the artifact you hand to the host code and to a reviewer.

## A2 · Anchoring `[gate]`

The single most common silent defect. A regex matches a **substring** by default — so an unanchored
pattern is answering a different question than you think:

- **Full match** (`^…$`, or `re.fullmatch`, or `\A…\z`): the *whole* string must be the language.
  `^\d{4}$` means "exactly four digits."
- **Partial match** (`re.search`, unanchored): *somewhere in* the string. `\d{4}` means "contains
  four consecutive digits" — it matches `abc2026def`, `20267`, `99999`.

The classic over-match: a validator written with `\d{4}-\d{2}-\d{2}` and run with `search` accepts
`garbage 2026-06-16 more garbage` and `2026-06-16-07-08`. The pattern looks right; the **mode** is
wrong.

- Decide full-vs-partial **before** the character classes — it changes what every class means.
- `\b` (word boundary) is the middle ground for tokenizing: match a whole word inside a larger text.
- Encode the decision in the spec card's `mode` field (`full` / `partial`) so `bin/regex-check.py`
  enforces it — a negative like `"2026-06-16x"` only fails under `full`, and that's the point.
- **Gate:** a pattern whose anchoring was never decided is ungraded. A missing `^…$` (when full is
  meant) or a stray anchor (when partial is meant) is a gate failure, not a style note.

## A3 · Classes & quantifiers `[review]`

The width of the language, character by character:

- **Class width** — `.` matches almost anything (and not newlines, unless `s`); `\w` includes `_`
  and (with `u`) Unicode letters; `[a-z]` is ASCII-only. The wrong class is the wrong language: `\w+`
  for "a word" silently allows `___`.
- **Greedy vs lazy** — `.*` grabs as much as possible and backtracks; `.*?` grabs as little. In
  `<(.*)>` vs `<(.*?)>` over `<a><b>`, the first captures `a><b`, the second `a`. Wrong greediness is
  a wrong capture, not just a perf note.
- **Bounded vs unbounded** — prefer `{m,n}` to `+`/`*` when the spec has a real bound (a year is
  `\d{4}`, not `\d+`). Bounds tighten the language *and* defang ReDoS.

## A4 · Groups & captures `[review]`

- **Capture vs non-capture** — `(…)` captures (costs a numbered slot, used downstream); `(?:…)` only
  groups. Don't capture what nothing reads; renumbering captures is a classic refactor bug.
- **Named groups** — `(?P<year>\d{4})` (Python) / `(?<year>\d{4})` (JS/PCRE) — readable extraction,
  stable under reordering.
- **Backreferences** — `(["'])…\1` matches a balanced quote. Powerful, but backrefs make the engine
  backtracking (and are unsupported in RE2/Go — a dialect gate).
- **Alternation** — `(a|b|c)`. Order matters in backtracking engines (first match wins for the
  overall greedy walk); **overlapping** branches under a quantifier — `(a|ab)*` — are a ReDoS smell
  (see `redos-and-safety.md`).

## A5 · Flags & dialect `[review]`

Flags change the language; the dialect changes what's even expressible.

- **`i`** ignorecase — folds the alphabet; with `u`, folds Unicode (`ß`, `İ`). **`m`** multiline —
  `^`/`$` match at every line, not just string ends (a frequent surprise). **`s`** dotall — `.` now
  matches newlines. **`x`** verbose — whitespace ignored, `#` comments allowed (the readability
  flag). **`u`** unicode — `\w`, `\d`, `\b` become Unicode-aware.
- **Dialect** — PCRE / JS / Python / RE2 / Go differ on lookbehind, named-group syntax, possessive
  quantifiers, atomic groups, backrefs, and Unicode properties. Pin the engine in the spec card; see
  `dialects.md`. `bin/regex-check.py` runs Python `re` — for a JS or PCRE target, treat its compile
  as a sanity check and cross-verify the dialect-specific constructs in the real engine.

## The adversarial counter-example hunt (route A1 to a skeptic, not the author)

The dangerous defect — *matches the examples, means the wrong language* — lives here, and it is **not
caught by passing the example set** (an overfit pattern passes its own examples by construction). So
verify it the way `deep-research` verifies claims: **in a fresh context, adversarially.**

- Prompt a separate reviewer (a fresh agent, not the one that wrote the pattern): *"Here is the
  target-set in words and the pattern. Find one string the SPEC implies but the example set does not
  list — a forbidden string the pattern still ACCEPTS, or an allowed string it REJECTS. Default to 'a
  counterexample exists' and search for it."*
- The richest seams to attack: the **anchoring** (does a trailing newline / surrounding text slip
  through?), the **class width** (does `\d` accept a Unicode digit `٣`? does `.` swallow a newline?),
  the **quantifier bounds** (`9999-99-99` for a "date"? `00000` for a "ZIP"?), and **alternation
  order**.
- Feed every counterexample back as a new **negative** (or positive) in the spec card. Re-run
  `bin/regex-check.py` — the new negative should now FAIL the pattern (proving the bug), and the fix
  makes it pass. A pattern is only as correct as its negatives are mean.

The output of this axis is the **pattern-spec card** — the target-set as positives[] + negatives[] —
the artifact GRADE re-derives and SPECIFY emits, and the thing you hand to the host code.
