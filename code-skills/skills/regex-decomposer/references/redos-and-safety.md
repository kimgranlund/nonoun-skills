# ReDoS & safety — why a passing regex can hang the process

This is the centerpiece. The whole skill exists because an LLM (and a hurrying human) ships the
**right intent, won't run** quadrant — a pattern that compiles, matches every example, and then
**catastrophically backtracks** on one crafted input, pinning a CPU and turning a validator into a
denial-of-service. MATCH's B3 gate is "no catastrophic backtracking on adversarial input." This file
is the taxonomy, and `bin/regex-check.py`'s smell scan is its mechanized pre-filter.

## The one principle

> **Catastrophic backtracking comes from ambiguity multiplied across a quantifier.** When the engine
> has more than one way to match the same input, and that choice sits inside a repetition, the number
> of paths it must try before declaring "no match" grows exponentially (or quadratically) in the
> input length. The blow-up happens on the **failing** input — the string that *almost* matches and
> forces the engine to exhaust every path.

Two corollaries:

- **The danger is on non-matches, not matches.** A ReDoS pattern is usually fast on valid input and
  pathological on a string that matches a long prefix and then fails at the end. Your positives won't
  catch it; you need an adversarial near-miss.
- **A backtracking engine is the precondition.** PCRE, Python `re`, JS, Java, .NET, Ruby all use
  backtracking and are all exposed. **RE2** (Go's `regexp`, Rust's `regex`) uses a finite automaton
  and is **immune by construction** — no backreferences, linear time, always. The cheapest ReDoS fix
  is sometimes "change engines" (see `dialects.md`).

## The taxonomy (what `bin/regex-check.py` flags)

Static, cheap, deterministic — the pre-filter before a (costlier) adversarial timing test:

| Kind | Smell | Why it blows up |
|---|---|---|
| **NESTED_QUANTIFIER** | `(a+)+` · `(\w*)*` · `(a{1,3})+` | the inner and outer quantifier span the same characters; the engine can partition `aaaa` as `(aaaa)`, `(aaa)(a)`, `(aa)(aa)`, … — exponentially many ways, all retried on a failing tail |
| **OVERLAPPING_ALTERNATION** | `(a|a)*` · `(a|ab)*` · `(\d|\w)+` | two branches match the same input; every repetition can take either path, so the paths multiply per character |
| **QUADRATIC_WILDCARD** | `.*.*` · `.+\s*.+` · `.*a.*` | two unbounded greedy wildcards can trade characters at every split point — O(n²) work to find there's no match |

Run it: `python3 bin/regex-check.py spec.json` (the scan runs as part of B3). A flag is a **gate
failure** — the pattern is ReDoS until proven safe.

## Why the canonical examples explode

- **`^(\w+)+$` on `"aaaaaaaaaaaaaaaaaaaa!"`** — the `!` makes the overall match fail. To be sure,
  the engine tries every way to split the `a`s between the inner `\w+` and the outer `+`: 2^(n-1)
  partitions. Twenty `a`s and a `!` already takes noticeable time; thirty hangs.
- **`(a|ab)*c` on `"abababab…abX"`** — at each position the engine can match `a` then `b`, or `ab`;
  both consume the same text. On the failing `X`, it retries every combination of those choices.
- **`.*=.*;` on a long line with no `;`** — the first `.*` grabs everything, backs off one char at a
  time looking for `=`, and for each `=` the second `.*` does the same looking for `;`. Quadratic.

## How the example + adversarial sets *prove* safety

The static scan finds the *smell*; the **example set proves the cure**. The B3 gate is cleared two
ways, and the spec card carries the proof:

1. **An adversarial near-miss negative.** For any pattern over user input, add a negative that
   matches a long prefix and then fails — `"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!"` for a `\w`-based
   pattern, a long unterminated line for a `.*…` pattern. A safe pattern rejects it *fast*; a ReDoS
   pattern would hang. (The static scan is the cheap pre-filter; a wall-clock timing test on the
   adversarial negative is the proof — keep the negative in the card as a regression.)
2. **A rewrite that removes the ambiguity**, then re-run the whole example set to prove the language
   is unchanged. The rewrite must keep every positive matching and every negative rejected — the card
   is what guarantees the cure didn't change the meaning.

## The fixes (remove the ambiguity, keep the language)

- **Make the inner repetition unambiguous.** `(\w+)+` → `\w+`. The outer `+` added nothing — one
  `\w+` already matches the same language, with no nesting. This is the most common real fix: the
  nesting was never needed.
- **Anchor and bound.** Unbounded `+`/`*` over user input invites the blow-up; `{1,64}` caps the
  work and usually matches the real spec better anyway. Anchoring (`^…$`) removes the substring
  search that compounds it.
- **Atomic groups / possessive quantifiers** (PCRE, Java, .NET, PCRE2-backed Python via the `regex`
  module): `(?>\w+)` or `\w++` tell the engine "having matched these, never give them back" — killing
  the backtracking that the nesting feeds on. **Not** available in stock Python `re` or in JS.
- **Disjoint alternation.** Rewrite `(a|ab)` so branches can't both match the same input — e.g.
  `(ab?)` or order them so the longer comes first and the engine commits. Make the branches mutually
  exclusive by first character where you can.
- **Switch to RE2.** Go's `regexp`, Rust's `regex`, and RE2 itself run in guaranteed linear time and
  cannot ReDoS — at the cost of backreferences and lookaround. For any pattern fed untrusted input,
  "is RE2 an option?" is a first-class question, not a last resort.

## How this scores

B3 is **statically clean ∧ adversarially proven**:

- statically clean = `bin/regex-check.py`'s smell scan finds no NESTED_QUANTIFIER /
  OVERLAPPING_ALTERNATION / QUADRATIC_WILDCARD;
- adversarially proven = an adversarial near-miss negative is in the card and the pattern rejects it
  fast (or the pattern runs on an engine — RE2 — that cannot ReDoS).

A pattern that compiles and passes its positives but carries an unanswered smell is **not**
B3-passing — it's the *right intent, won't run* quadrant (it runs, until the day someone sends the
crafted input), and the corrective is on the **pattern** (remove the ambiguity), not the score.
