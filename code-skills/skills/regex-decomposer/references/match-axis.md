# The MATCH axis — does it provably match, here?

The Match axis (B1–B5) grades *mechanism*, bottom-up: from "does this pattern even compile" to "does
it hold under Unicode and adversarial input." It is the **mechanizable** axis — route B1/B2/B3 to
`bin/regex-check.py` and **trust the tool, not the read-through**. An LLM cannot reliably tell by
reading whether a pattern compiles, matches a given string, or backtracks catastrophically; running
it is the only evidence.

## The ladder

| Level | Gate | The tool that proves it | The signal |
|---|---|---|---|
| **B1 Compiles** | `[gate]` | `re.compile` in the target engine | valid syntax: balanced groups, valid backrefs, no unsupported construct |
| **B2 Examples** | `[gate]` | the example set under the declared mode | matches ALL positives, rejects ALL negatives (the contract) |
| **B3 Safety** | `[gate]` | static ReDoS scan (tool) + a **manual** adversarial-input timing test | no catastrophic backtracking on a crafted string |
| **B4 Robustness** | review | wider inputs | Unicode, empty string, very long input, line endings |
| **B5 Readability** | review | the pattern itself | named groups, `x`/verbose mode, no needless cleverness |

The gates cascade: don't grade robustness (B4) for a pattern that won't compile (B1). A red gate
stops the axis — fix it before reviewing.

## The example set is the contract — run it as code

`bin/regex-check.py` reads a **pattern-spec card** and runs B1–B3 in one pass:

```json
{
  "name":      "iso-date",
  "pattern":   "\\d{4}-\\d{2}-\\d{2}",
  "flags":     ["i"],
  "engine":    "python-re",
  "mode":      "full",
  "positives": ["2026-06-16", "1999-01-01"],
  "negatives": ["2026/06/16", "26-6-16", "", "2026-06-16x", "9999-99-99"]
}
```

```sh
python3 bin/regex-check.py spec.json     # compile + examples (full/partial) + ReDoS scan; nonzero on any fail
python3 bin/regex-check.py selftest      # prove the checker over good/bad fixtures
```

The card is the contract of record. Read its report honestly:

- A **missed positive** (`positive NOT matched`) means the pattern is too narrow — it rejects a
  string the spec allows.
- A **matched negative** (`negative WRONGLY matched — accidental over-match`) means the pattern is
  too wide — it accepts a string the spec forbids. This is the over-match the anchoring decision
  (A2) is supposed to prevent.
- **An empty example set is not a pass** — it's a half-written contract. A card with no negatives has
  proved nothing about the language's boundary. The checker warns; treat it as a B2 incomplete.

## B1 — reading compile errors

The cheapest, highest-value gate. The pattern that won't compile is the LLM's most confident
failure. Common compile errors and what they mean:

- **`unbalanced parenthesis` / `missing ), unterminated subpattern`** — a stray or unescaped `(`.
- **`nothing to repeat`** — a quantifier with no atom before it (`*abc`, `(?:)+` on empty).
- **`invalid group reference` / `bad escape`** — a `\1` with no group 1, or a backref the engine
  doesn't support.
- **`look-behind requires fixed-width pattern`** (Python) — variable-length lookbehind, which Python
  forbids but PCRE/JS allow. A **dialect** signal, not a bug — see `dialects.md`.
- **`global flags not at the start`** (Python 3.11+) — inline `(?i)` mid-pattern; move it to the
  front or use the `flags` argument.

`bin/regex-check.py` reports the raw `re.error`. If your target engine is *not* Python, a Python
compile failure may be a dialect difference (the construct is valid in PCRE/JS) — verify in the real
engine before calling B1 red.

## B2 — the full/partial mode contract

`mode` is half the language (the other half being the classes). The checker uses:

- **`full`** → `re.fullmatch`: the entire string must be the language. The default. Negatives like
  trailing-character (`"2026-06-16x"`) and embedded-in-text only FAIL under `full` — which is exactly
  why a validator must declare it.
- **`partial`** → `re.search`: a match anywhere. Correct for tokenizers and extractors. Here a
  negative must contain *no* matching substring (`"@@@"` for `\w+`, not `"foo@bar"` which contains
  `\w+`).

Choosing `partial` when you meant `full` is the over-match in mechanized form — the checker turns the
A2 anchoring decision into a runnable assertion.

## B3 — safety (the gate that turns a regex into a DoS)

A pattern can compile and pass every example and still **hang the process** on a crafted input.
`bin/regex-check.py` runs a static **ReDoS-smell scan** flagging the three catastrophic-backtracking
families — nested quantifiers `(\w+)+` (incl. bounded-outer forms like `(.*a){10}`), overlapping
alternation `(a|ab)*`, quadratic `.*.*`. The scan is a **lossy pre-filter**: a clean result is
necessary but not sufficient (it can miss deeper nesting and over-flag), so confirm a suspicion with
a timing test. A flag is a **B3 gate failure** until cleared by an adversarial-input timing test —
which is a **manual** step the tool does not run (it is on the ROADMAP) — or a rewrite. The full
taxonomy, the why, and the fixes are in `redos-and-safety.md`.

## B4 Robustness & B5 Readability (reviews)

- **B4** — beyond the example set: **Unicode** (does `\w`/`\d` mean ASCII or Unicode here? do accented
  letters, combining marks, or emoji behave?), the **empty string** (does `*`/`?` make it match
  vacuously when it shouldn't?), **very long input** (the ReDoS surface), and **line endings**
  (`$` before `\n`, `\r\n`, the `m` flag). Test the inputs the example set is too polite to include.
- **B5** — a regex is read far more than written. Score up: **named groups** over numbered,
  **`x`/verbose mode** with comments for any non-trivial pattern, character classes over long
  alternations, and *no* cleverness that a comment can't rescue. Score down: a 200-character
  single-line pattern with five numbered captures.

The output of this axis is the **MATCH report card** — which gates ran, the example misses, and the
safety smells — handed alongside the pattern-spec card to the host (`code-decomposer`).
