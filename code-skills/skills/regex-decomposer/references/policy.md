# Policy — definition-of-done, the card, and the handoff

The reusable artifacts and boundaries: what "done" means, the shape of the pattern-spec card the
skill emits, and how this hands off to the rest of the code-tooling fleet without overlapping it.

## Definition-of-done (a pattern is shippable when…)

Gated items route to `bin/regex-check.py`; review items are 1–5 judgments. SHIPPABLE = the quadrant
top-left.

1. **Explicit target-set (A1)** — the IN and OUT string sets are named, with the boundary near-misses
   listed as negatives. Stated as one sentence + the two lists.
2. **Anchoring decided (A2)** — full vs partial is chosen and encoded in the card's `mode`; the
   relevant trailing-character / embedded-text negatives are present.
3. **Right classes & quantifiers (A3)** — class width matches the spec; greediness intended; bounds
   used where the spec has them (≥4).
4. **Sound groups & captures (A4)** — captures only what's consumed, named where it aids reading,
   alternation non-overlapping; backrefs only on a backtracking engine (≥4).
5. **Flags & dialect pinned (A5)** — engine + flags declared; no non-portable construct for the
   target engine (≥4).
6. **Compiles (B1)** — `bin/regex-check.py` compiled it; for a non-Python engine, the dialect-specific
   constructs are cross-verified there.
7. **Examples green (B2)** — every positive matched and every negative rejected under the declared
   mode; the negative list is non-empty (the contract has a boundary).
8. **Safe (B3)** — the ReDoS-smell scan is clean **and** an adversarial near-miss negative is in the
   card and rejected fast (or the engine is RE2/linear and cannot ReDoS).
9. **Both axes ≥4, zero gate fails, SHIPPABLE quadrant** — reported as two scores, gate failures
   first, with B4 robustness + B5 readability ≥4 and the pattern-spec card ready for handoff.

## The pattern-spec card

The card is the contract of record — checked in next to the pattern (or its test), the diff a
reviewer reads first, and the input `bin/regex-check.py` validates. Shape:

```json
{
  "name":      "iso-date",
  "pattern":   "\\d{4}-\\d{2}-\\d{2}",
  "flags":     ["a"],
  "engine":    "python-re",
  "mode":      "full",
  "positives": ["2026-06-16", "1999-01-01"],
  "negatives": ["2026/06/16", "26-6-16", "", "2026-06-16x", "x2026-06-16",
                "9999-99-99", "٢٠٢٦-٠٦-١٦",
                "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!"]
}
```

- **`pattern`** — the regex, JSON-escaped (`\\d` for `\d`).
- **`flags`** — single letters from `i m s x a u l` (map to `re.I/M/S/X/A/U/L`).
- **`engine`** — the production engine label (`python-re`, `js`, `pcre`, `re2-go`). Advisory to the
  checker (which runs Python `re`) but **load-bearing for B1/A5** — it's the real compile authority.
- **`mode`** — `full` (fullmatch / whole-string) or `partial` (search / substring). Encodes the A2
  anchoring decision so the checker enforces it.
- **`positives` / `negatives`** — the example set, which IS the target-set's concrete contract. The
  negatives carry the weight: boundary near-misses, the empty string, a Unicode-scope probe, and an
  **adversarial ReDoS near-miss** (a long almost-match) belong here.

## The two report cards the skill produces

- **MATCH report card** (`bin/regex-check.py`): B1 compile · B2 example misses (positive/negative,
  with the offending string) · B3 safety (the smell kinds). Nonzero exit on any gate failure.
- **The two-axis grade**: A score (1–5 per review, gates pass/fail) and B score, reported separately,
  with the quadrant cell named (SHIPPABLE · matches-the-examples-means-the-wrong-language ·
  right-intent-won't-run · REBUILD) and one corrective per failure.

## Handoff — what this skill does NOT do

`regex-decomposer` owns **regex design and grading** and feeds the others; it does not write the code
around the pattern.

- **→ `code-decomposer`**: the host that *calls* the regex — the function that uses it, the error
  handling, the tests around it. This skill hands over the locked pattern-spec card; `code-decomposer`
  grades the unit that embeds it. A regex can be SHIPPABLE here and the function around it still be
  *green but wrong*.
- **→ `query-decomposer`** (sibling): structured query languages (SQL) — a different language ×
  execution crossing. A `LIKE`/`SIMILAR TO`/`~` pattern *inside* SQL is a regex; the surrounding
  query is `query-decomposer`'s.
- **not `/verify`**: that runs the whole app to confirm end-to-end behavior. This skill proves the
  *pattern* means the right language and matches; `/verify` proves the *system* behaves.
- **not the production engine's authority**: `bin/regex-check.py` runs Python `re`. For a JS / PCRE /
  RE2 target, it's a sanity check — the engine pinned in the card is the B1/A5 authority, and
  dialect-specific constructs must be cross-verified there (see `dialects.md`).

## Governance

- **The card is checked in** next to the pattern as the contract of record; it versions with the
  code and is the diff a reviewer reads first.
- **Every counterexample found becomes a negative** — the adversarial hunt and any production
  over-match incident add to the card's `negatives[]`, so the bug can never silently return.
- **The adversarial ReDoS near-miss stays in the card** as a regression: the long almost-match that
  would hang an unsafe pattern proves, on every run, that the current one is fast.
