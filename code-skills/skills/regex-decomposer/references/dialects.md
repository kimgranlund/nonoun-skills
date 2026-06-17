# Dialects — what's portable and what isn't

A regex is not one language; it is a family of dialects that disagree on syntax *and* on what's
expressible. The same pattern can mean different things — or fail to compile — across engines. Pin
the **engine** in the spec card (A5), because a pattern that's correct in PCRE can be a compile error
in RE2 and a silent over-match in JS. `bin/regex-check.py` runs **Python `re`**; for any other
target, treat its compile + example run as a sanity check and cross-verify the dialect-specific
constructs in the real engine.

## The engines you'll meet

| Engine | Used by | Type | ReDoS-able? |
|---|---|---|---|
| **PCRE / PCRE2** | PHP, nginx, many CLI tools (`grep -P`), Perl | backtracking | yes |
| **JS (ECMAScript)** | browsers, Node | backtracking | yes |
| **Python `re`** | Python stdlib | backtracking | yes |
| **Java / .NET** | JVM, CLR | backtracking | yes |
| **RE2** | Go `regexp`, Rust `regex`, ripgrep, CodeSearch | finite automaton | **no — linear time, immune by construction** |

The first division is **backtracking vs automaton**. Backtracking engines are more expressive
(backreferences, lookaround) but can ReDoS. Automaton engines (RE2) are linear-time and DoS-proof but
**drop** backreferences and (mostly) lookaround. For untrusted input, that trade often favors RE2.

## The portability table

| Construct | PCRE | JS | Python `re` | RE2 / Go |
|---|---|---|---|---|
| Named group **definition** | `(?<n>…)` / `(?P<n>…)` | `(?<n>…)` (ES2018+) | `(?P<n>…)` | `(?P<n>…)` |
| Named **backreference** | `\k<n>` / `(?P=n)` | `\k<n>` | `(?P=n)` | — (no backrefs) |
| Numbered **backreference** | `\1` | `\1` | `\1` | **— unsupported** |
| **Lookahead** `(?=…)` `(?!…)` | yes | yes | yes | **— unsupported** |
| **Lookbehind** `(?<=…)` `(?<!…)` | yes (variable-width) | yes (ES2018+) | yes (**fixed-width only**) | **— unsupported** |
| **Atomic group** `(?>…)` | yes | **no** | **no** (stock `re`; the `regex` module has it) | n/a |
| **Possessive** `a++` `a*+` | yes | **no** | **no** (stock `re`) | n/a |
| **Inline flags** `(?i)` | anywhere | scoped `(?i:…)` (ES2025) | start-only (3.11+) | yes |
| **Unicode property** `\p{L}` | yes | with `u` flag | **— use the `regex` module** (stock `re` lacks `\p`) | yes |
| `\d` `\w` default scope | ASCII (Unicode opt-in) | ASCII (`u` for full Unicode) | **Unicode by default** (`a` flag → ASCII) | Unicode |

Read the table as a **gate list**: a backreference or lookaround in a pattern targeting Go/RE2 is a
**B1 compile failure**, not a portability nicety. A `\p{L}` in stock Python `re` won't compile. A
variable-width lookbehind compiles in PCRE/JS and is a Python compile error.

## The portability traps that bite quietly

- **`\d`/`\w` scope flips by engine.** In Python `re`, `\d` matches Unicode digits (`٣`, `४`) by
  default — pass the `a` flag for ASCII-only. In JS and PCRE, `\d` is ASCII unless you opt in. A
  "digits only" pattern can accept characters you never intended *because the engine's default
  differs from the engine you tested in*. This is a frequent **wrong-language** defect — add a
  Unicode-digit string to your negatives and let the example set catch it.
- **`$` and the trailing newline.** In Python `re` (without `m`), `$` matches at end-of-string **or
  just before a final `\n`** — so `^\d+$` accepts `"123\n"`. Use `\Z` (Python) / `\z` for a strict
  end. JS `$` does not have this quirk by default.
- **`.` and newlines.** `.` excludes `\n` everywhere by default; the dotall flag is `s` (PCRE,
  Python, JS via `s` in ES2018+). Multiline input + `.*` + no `s` silently stops at the first line.
- **Named-group syntax differs.** `(?P<n>…)` is Python/RE2; `(?<n>…)` is PCRE/JS. Copy a Python
  pattern into JS and the `(?P<…>)` is a compile error.
- **Inline-flag placement.** Python 3.11+ rejects `(?i)` anywhere but the start; older Python and
  PCRE allow it mid-pattern. Prefer the engine's flags argument over inline flags for portability.

## What's actually portable (the safe core)

If you need one pattern to run everywhere, stay inside this subset:

- Character classes `[…]`, `\d \w \s` (but **declare the ASCII/Unicode scope explicitly** via flags),
  the dot, anchors `^ $`, word boundary `\b`.
- Quantifiers `* + ? {m,n}` and lazy variants `*? +?`.
- Non-capturing `(?:…)` and capturing `(…)` groups, ordered alternation `(a|b)`.
- The `i`, `m`, `s` flags via the engine's flags argument (not inline).

Avoid for portability: backreferences, lookbehind (and variable-width lookahead), atomic/possessive
quantifiers, `\p{…}` Unicode properties, named groups (or pick the syntax for the *narrowest* engine
you target and note it). When the spec card's `engine` is RE2/Go, the smell scan in
`bin/regex-check.py` matters less (RE2 can't ReDoS) but the **unsupported-construct** gate matters
more — backrefs and lookaround simply won't compile there.

## The decision

Ask, in order: **(1) Is the input untrusted?** → strongly prefer RE2 (linear, DoS-proof) and live
without backrefs/lookaround. **(2) Which engine actually runs this in production?** → pin it in the
card; that, not Python `re`, is the B1 authority. **(3) Does the pattern use a non-portable
construct?** → either confirm the target supports it, or rewrite to the portable core.
