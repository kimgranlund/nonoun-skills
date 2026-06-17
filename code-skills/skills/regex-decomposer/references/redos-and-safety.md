# ReDoS & safety — why a passing regex can hang the process

This is the centerpiece. The whole skill exists because an LLM (and a hurrying human) ships the
**right intent, won't run** quadrant — a pattern that compiles, matches every example, and then
**catastrophically backtracks** on one crafted input, pinning a CPU and turning a validator into a
denial-of-service. MATCH's B3 gate is "no catastrophic backtracking on adversarial input." This file
is the taxonomy, and `bin/regex-check.py`'s smell scan is its mechanized pre-filter.

> **The scan is AST-based structural analysis, and a PRE-FILTER, not a verdict.** It no longer reads
> the pattern with a regex; it walks the regex's **real parse tree** (Python's stdlib `sre_parse` /
> `re._parser`), so the targeted families — *star height ≥ 2* (a repeat whose body holds another
> repeat), *prefix-overlapping alternation* under a quantifier, *twin unbounded repeats* over
> overlapping content — are detected **precisely**, not by a lossy regex-on-regex heuristic. It is
> still a pre-filter, not a full decision procedure: a clean scan is **necessary but not sufficient**
> for exotic blow-ups outside those families, so a flag is a suspicion, not a proof. Confirm any
> catastrophic suspicion with a **timing test** — and note the timing test is a **manual** step the
> tool does **not** perform (mechanizing it is on the ROADMAP).

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

Structural, cheap, deterministic — computed on the parse tree, the pre-filter before a (costlier)
**manual** adversarial timing test (the tool flags the smell; it does not time the pattern):

| Kind | Smell | AST signal (how the tree reveals it) | Why it blows up |
|---|---|---|---|
| **NESTED_QUANTIFIER** | `(a+)+` · `(\w*)*` · `(.*a){10}` · `([^,]*,){20}` | **star height ≥ 2**: a `MAX_REPEAT`/`MIN_REPEAT` whose body subtree (through `SUBPATTERN`/`BRANCH`/concatenation) contains another repeat. A bounded `{m,n}` outer repeat counts as a repeat too. | the inner and outer quantifier span the same characters; the engine can partition `aaaa` as `(aaaa)`, `(aaa)(a)`, `(aa)(aa)`, … — exponentially (or polynomially) many ways, all retried on a failing tail |
| **OVERLAPPING_ALTERNATION** | `(a|a)*` · `(a|ab)*` | a repeat whose body holds a `BRANCH` with an **empty arm** (`sre_parse` factors a shared prefix out, so `(a|ab)` → `LITERAL('a')` + `BRANCH([[], [LITERAL('b')]])` — the empty arm is the exact fingerprint of one alternative being a prefix of another) or an arm whose token sequence is a prefix of another's. | two branches match the same input; every repetition can take either path, so the paths multiply per character |
| **QUADRATIC_WILDCARD** | `.*.*` · `.+\s*.+` (`\w*\w*`) | two **consecutive unbounded repeats** (`max == MAXREPEAT`) at the same sequence level whose bodies can overlap (either body is `ANY`, or the two bodies are structurally identical). | two unbounded greedy wildcards can trade characters at every split point — O(n²) work to find there's no match |

Because detection is structural, mutually-exclusive alternations are *not* false-flagged:
`(foo|bar|baz)*` keeps no empty arm (and `bar`/`baz` are not prefixes of one another), `(a|b|c)+`
is folded by `sre_parse` into a single `IN` char class with no `BRANCH` at all, and sibling repeats
like `a+b+c+` are star height 1 (no repeat *inside* a repeat).

Run it: `python3 bin/regex-check.py spec.json` (the scan runs as part of B3). A flag is a **gate
failure** — the pattern is ReDoS until proven safe. A pattern that does not parse is a **B1 compile
finding**, not a ReDoS verdict (there is no tree to analyze).

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
   adversarial negative is the proof — but **you run that timing test by hand**: `regex-check.py`
   does not time patterns, so it cannot clear a B3 smell for you. Keep the negative in the card as a
   regression.)
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

- statically clean = `bin/regex-check.py`'s AST scan finds no NESTED_QUANTIFIER /
  OVERLAPPING_ALTERNATION / QUADRATIC_WILDCARD (precise for those families, but still a pre-filter —
  necessary, not sufficient for exotic blow-ups; see the caveat up top);
- adversarially proven = an adversarial near-miss negative is in the card and the pattern rejects it
  fast under a **manual** timing test you run yourself (or the pattern runs on an engine — RE2 — that
  cannot ReDoS). The tool does not perform this timing test.

A pattern that compiles and passes its positives but carries an unanswered smell is **not**
B3-passing — it's the *right intent, won't run* quadrant (it runs, until the day someone sends the
crafted input), and the corrective is on the **pattern** (remove the ambiguity), not the score.
