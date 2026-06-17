# Worked example — "matches the examples, but ReDoS" on LANGUAGE × MATCH

A complete DECOMPOSE → fix → GRADE for one email pattern, showing the **B3 safety gate** catching
catastrophic backtracking on a pattern whose example set is *green* — the signature failure
`regex-decomposer` exists to catch. The two spec cards here are checked in and the checker actually
flags / clears them.

## The artifact

An email validator. The author tests it against a handful of addresses, all pass, all junk rejected —
ship it?

```
pattern: (\w+)+@\w+\.\w+
positives: alice@example.com, bob@mail.org
negatives: no-at-sign, @example.com
```

## DECOMPOSE

**A · Language** (target-set → anchoring → classes/quantifiers)
- **Target set** — "a local part, `@`, a domain with a dot." ✓
- **Anchoring** — `mode: full` (fullmatch), so no unanchored over-match. ✓
- **Classes/quantifiers** `[B3 risk]` — the local part is written `(\w+)+`: a `+` quantifier wrapping
  a `\w+`. *Claim:* it's just "one or more word chars." Prove it's safe (B3).

**B · Match** (compiles → examples → safety)
- **B1 Compiles / B2 Examples** `[gate]` — run the checker on the card (`examples/email.red.json`):

```
$ python3 bin/regex-check.py examples/email.red.json
regex-check: FAIL (1 issue(s))
  - email-naive: B3 ReDoS-SMELL NESTED_QUANTIFIER — a quantified group wraps another quantifier (star height >= 2) ...
MATCH report card — email-naive
  B1 compile : ok
  B2 examples: mode=full  positives=2  negatives=2  misses=0
  B3 safety  : 1 smell(s)
       ⚠ NESTED_QUANTIFIER — a quantified group wraps another quantifier (star height >= 2) ...
```

**B1 and B2 are green** — it compiles, every positive matches, every negative is rejected, `misses=0`.
A sympathetic read stops here and ships. But **B3 fails**: the AST scan finds `(\w+)+` is a nested
quantifier (star height ≥ 2) — exponential backtracking on a long non-matching tail like
`"aaaaaaaaaaaaaaaaaaaa!"`. The examples never exercised that input, so green told you nothing about
safety. This is the *matches the examples, but ReDoS* quadrant, proven on the parse tree.

## Fix

The outer `+` adds no expressive power — collapse the nesting to a single character class
(`examples/email.green.json`: `[\w.]+@\w+\.\w+`, which also admits the dotted local part), keeping the
exact same example set:

```
$ python3 bin/regex-check.py examples/email.green.json
MATCH report card — email-safe
  B1 compile : ok
  B2 examples: mode=full  positives=2  negatives=2  misses=0
  B3 safety  : clean
regex-check: PASS — 1 spec(s): compile + examples + safety clean
```

Same examples, still green — and now the parse tree has star height 1, so there's no ambiguity for the
engine to backtrack through. The red→green transition is the proof that B3 holds. (For an exotic
flag the checker is a pre-filter; confirm with a manual adversarial-input timing test.)

## GRADE — two scores, never averaged

- **Language: 5/5** — right target set, anchored, classes now linear (no nested quantifier).
- **Match: B3 gate-fail → (after fix) 5/5** — compiles, examples green ∧ the safety scan is clean.

**Quadrant:** the red card sat in **"green examples, unsafe pattern"** (Match's B1/B2 looked green but
B3 was catastrophic) — *the example set passing on the wrong property*. The fix is removing the nested
quantifier, not adding more examples. After it: **SHIPPABLE**.

The lesson: "do the examples pass?" is the wrong question for safety; "can a crafted input make this
backtrack?" is the right one — and the structure that causes it is detectable on the AST, not by
eyeballing the pattern.
