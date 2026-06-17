# The two-axis method — LANGUAGE × MATCH

A regular expression is **correct on two independent axes that walk the same pattern in opposite
directions** — the decomposer seam the code-, layout-, and component-decomposers apply to a unit, to
space, and to a component, here applied to a single pattern.

- **Language · whole → part** grades the **intent**: the target-set the pattern *means* → its
  anchoring → its classes & quantifiers → its groups & captures → its flags & dialect. *"Is it the
  right language?"*
- **Match · part → whole** grades the **mechanism**: it compiles → matches the example set → is safe
  on adversarial input → is robust → is readable. *"Does it provably match, here?"*

They **cross at the pattern** — the regex text is *both* the claim (the formal language you mean:
which strings are in the set, which are out) and the executable matcher (what the engine actually
runs). A target-set with no runnable pattern is a wish; a pattern with no stated target-set is
"matches the examples, means the wrong language" waiting to happen.

That crossing is the whole technique. A pattern can be:

- **right intent, won't run** — the target-set is exactly right, but the pattern won't compile in the
  engine (an unsupported construct, an unbalanced group, a bad backreference) or **catastrophically
  backtracks** on a crafted input. The classic LLM failure: a plausible-looking pattern that doesn't
  execute, or ReDoS-es.
- **matches the examples, means the wrong language** — compiles, matches every positive, rejects
  every negative — but it accidentally accepts strings the spec forbids (an over-wide language) or
  rejects strings the spec allows (an over-narrow one). The classic LLM trap: a pattern overfit to
  the handful of examples it was shown, fitting them by accident, not by meaning the right set.

Opposite defects, opposite fixes — so you **score and report the two axes separately, never
averaged.** An averaged score hides which one you have, and they need opposite work: re-spec the
negatives (Language) vs rewrite the matcher (Match).

## The leveled walk

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Language** | whole → part | **A1** Target-set `[gate]` → **A2** Anchoring `[gate]` → **A3** Classes/quantifiers → **A4** Groups/captures → **A5** Flags/dialect | "Is it the *right language*?" |
| **B · Match** | part → whole | **B1** Compiles `[gate, code]` → **B2** Examples `[gate, code]` → **B3** Safety `[gate, code]` → **B4** Robustness → **B5** Readability | "Does it *provably match*, here?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** — a failure cascades and BLOCKS the reviews below it on
that axis. `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable pattern is **≥4 on every review
with zero gate failures**, reported as two separate axis scores plus the quadrant cell.

### A · Language (whole → part)

- **A1 Target-set `[gate]`** — the formal language you mean: the set of strings that MUST match and
  the set that MUST NOT. This is the contract, and the example set is its concrete proof. A wrong or
  fuzzy target-set makes everything below moot — you'll polish a pattern for the wrong language.
- **A2 Anchoring `[gate]`** — full match vs partial (substring) match; `^`, `$`, `\b`, `\A`, `\z`.
  This is the **#1 silent over-match**: an unanchored `\d{4}` "matches" `abc2026def`. Decide it
  before the character classes, because it changes what every class below means.
- **A3 Classes & quantifiers `[review]`** — character classes (`[a-z]`, `\d`, `\w`, `.`), greedy vs
  lazy (`*` vs `*?`), bounded vs unbounded (`{2,4}` vs `+`). Right class width, right greediness.
- **A4 Groups & captures `[review]`** — capturing vs non-capturing (`(…)` vs `(?:…)`), named groups,
  backreferences, alternation `(a|b)`. Captures only what's consumed downstream; alternation ordered
  and non-overlapping.
- **A5 Flags & dialect `[review]`** — `i` (ignorecase), `m` (multiline), `s` (dotall), `x` (verbose),
  `u` (unicode); and the **engine**: PCRE vs JS vs Python vs RE2/Go. The flags change the language;
  the dialect changes what's even expressible (see `dialects.md`).

### B · Match (part → whole)

- **B1 Compiles `[gate, code]`** — valid syntax in the **target engine**: balanced groups, valid
  backreferences, no unsupported construct. Routed to `bin/regex-check.py` (Python `re`); cross-check
  the real engine for dialect-specific constructs.
- **B2 Examples `[gate, code]`** — matches **ALL** positives and rejects **ALL** negatives, under the
  declared full/partial **mode**. The example set is the contract; run it, don't eyeball it.
- **B3 Safety `[gate, code]`** — no catastrophic backtracking (ReDoS) on adversarial input. The
  static smell scan flags the constructs; an adversarial-input timing test proves it (see
  `redos-and-safety.md`).
- **B4 Robustness `[review]`** — Unicode (accented letters, surrogate pairs, normalization), the
  empty string, very long input, mixed line endings. Holds beyond the example set.
- **B5 Readability `[review]`** — named groups over numbered, `x`/verbose mode with comments for any
  non-trivial pattern, no needless cleverness. A regex is read far more often than written.

## The opposite-defect quadrant

```
                 B · MATCH passes          B · MATCH fails
A · LANGUAGE ┌────────────────────────┬────────────────────────┐
  passes     │      SHIPPABLE         │  right intent, won't    │
             │                        │  run — target-set is    │
             │                        │  right, but it won't    │
             │                        │  compile in the engine  │
             │                        │  or ReDoS-es on a       │
             │                        │  crafted input          │
             ├────────────────────────┼────────────────────────┤
A · LANGUAGE │ matches the examples,  │       REBUILD           │
  fails      │ means the wrong        │                         │
             │ language — compiles &  │                         │
             │ passes every example,  │                         │
             │ but accepts a string   │                         │
             │ the spec forbids       │                         │
             └────────────────────────┴────────────────────────┘
```

The quadrant **names the fix**: top-right needs matcher work (rewrite the pattern, kill the
backtracking); bottom-left needs *language* work the example set **cannot see** — a meaner set of
negatives, found by an adversarial hunt.

## The doctrine — the example set is the contract; the spec is wider than its examples

This is why the skill earns its place (and why it's outsized for an LLM author):

- The MATCH gates (B1/B2/B3) are the **cheap** axis — run `bin/regex-check.py` and **trust the tool,
  not the read-through**. An LLM cannot reliably tell by reading whether a pattern compiles, matches
  a given string, or backtracks catastrophically. The example set — every `positives[]` and
  `negatives[]` — is the pattern's concrete contract; run it as code.
- But the **dangerous** defect ("means the wrong language") is on the LANGUAGE side and **not** caught
  by passing the example set — by construction, a pattern overfit to its examples passes them. Route
  it with an **adversarial counter-example hunt**: a *fresh-context* skeptic asked to find one string
  the **spec** implies but the **example set forgot** — a forbidden string the pattern still accepts,
  or an allowed string it rejects. Each one becomes a new negative (or positive) in the card, and a
  pattern is only as correct as its negatives are mean. A verifier sharing the author's examples
  inherits the author's blind spots — separate the context (the `deep-research` adversarial-verify
  move).

## Modes

- **SPECIFY** (before writing) — walk Language-down: name the target-set (the in/out string sets),
  decide anchoring (full vs partial), choose classes/quantifiers/groups, fix the engine + flags;
  draft the pattern; emit a **pattern-spec card** with positives[] and negatives[].
- **DECOMPOSE** (existing pattern) — *recover* the target-set from the pattern (read it as a language:
  what's in, what's out), run the example set (B1–B3 via `bin/regex-check.py`), score the reviews;
  emit the spec card + a gap list (e.g. *"compiles & passes the examples, but accepts `9999-99-99`
  which the spec forbids — the language is too wide"*).
- **GRADE** — score both axes, gates first (run the checker, run the adversarial hunt), place in the
  quadrant, name one corrective per failure.

## Walk order (do not skip)

1. **A1 Target-set / A2 Anchoring** — name the in/out string sets and decide full-vs-partial. Wrong
   ⇒ stop, re-spec (re-spec, don't tweak the classes).
2. **B1/B2/B3 Match** — run `bin/regex-check.py spec.json`. Won't-compile / a missed positive / a
   matched negative / a ReDoS smell ⇒ fix before reviewing (you can't grade groups for a pattern that
   won't compile).
3. **A1 adversarial counter-example hunt** — in a fresh context, find a string the spec forbids that
   the pattern accepts (or allows that it rejects). Add each as a negative/positive; re-run B2.
4. **Reviews** — A3–A5 then B4–B5, 1–5 each. Below 4 ⇒ name the single corrective.
5. **Report** — two axis scores, the quadrant cell, gate failures first; hand the verified
   pattern-spec card to the host (`code-decomposer`).
