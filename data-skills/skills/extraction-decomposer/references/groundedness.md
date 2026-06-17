# Groundedness — why a valid extraction is evidence of nothing

This is the centerpiece. The whole skill exists because an LLM (and a hurrying human) produces the
**valid JSON, invented values** quadrant — JSON that parses, conforms to the schema, satisfies every
constraint, and contains a value the source **never stated**. FIDELITY's A2 gate is "every value is
grounded in the source." This file is the grounding discipline, and `bin/groundedness-check.py` is its
mechanized core.

## The one principle

> **An extracted value pins the source, not the schema.** Its job is to be *traceable* to something
> the source actually says. A value that conforms to the schema but appears nowhere in the source is
> not data — it's a hallucination that happens to type-check.

Two corollaries:
- **Schema-valid is necessary, not sufficient.** The question is never "does it conform?" but "does
  the source *support* this value?"
- **The proof is grounding, not plausibility.** A value is right because the source says so, not
  because it reads like a value that field should have.

## What counts as "supported by the source"

`groundedness-check.py` walks every **scalar** in the extraction (strings and numbers — booleans and
nulls are skipped, see below) and asserts the value is grounded under one of four widening tests. The
ladder goes from strictest to most lenient; a value passes if **any** rung matches:

| Rung | Matches when… | Example (source → value) |
|---|---|---|
| **EXACT** | the value's **token sequence** appears as a contiguous run of whole source tokens (case-sensitive) | `Acme Robotics Inc.` → `"Acme Robotics Inc."` |
| **NORMALIZED** | the same **token-sequence** match after case-fold + edge-punctuation trim | `"  ACME  Corp. "` → `"Acme Corp."` |
| **NUMERIC** | a source number is digits-and-sign equal (commas, currency, trailing zeros ignored) | `$12,000.00` → `12000` |
| **DATE** | a source date appears in a common reformat (ISO ↔ slashed ↔ month-name, M/D and D/M both) | `June 16, 2026` → `"2026-06-16"` |

The string rungs (EXACT/NORMALIZED) are **token / word-boundary** matches, **not raw substring** tests.
This is deliberate, and it is the fix for a real false-negative class (below): a raw-substring test
grounds an invented `"Fran"` against `San Francisco` and `"Ware"` against `warehouse`. Tokenizing both
sides and requiring the value's tokens to appear as a contiguous run of *whole* source tokens closes
that — `fran` ≠ `francisco`, so the fragment no longer grounds. The four rungs are exactly the
**faithful normalizations** A3 permits — reformatting that preserves the asserted fact.

Two outcomes are **findings, not silent passes**:

- **WEAK_GROUNDING** — a very short value (one token, ≤3 chars) that *does* token-match. A short token
  is where a coincidental whole-token hit is most likely, so it is surfaced as `WEAK_GROUNDING — verify
  manually` rather than passed. (`"net"` against "net 30" is real, but cheap enough to warrant a look.)
- **EMPTY** — an empty / whitespace-only string. It asserts nothing about the source, but an empty value
  where the source has content is usually a B4 "had to put *something*" defect, so it is reported as a
  distinct `EMPTY` finding, not silently grounded.

Anything that survives none of the four rungs is **UNGROUNDED** and flagged as a likely hallucination.

One more outcome is an **advisory, not a gate failure** — it only fires when you opt in (see below):

- **WEAK_CONTEXT** — a value that *is* grounded (it passed a rung) but, given an opt-in per-field
  context cue, sits **far from any cue occurrence** in the source — a *possible* wrong-span. It is
  printed but does **not** change the exit code, because it only *approximates* role; role is confirmed
  by the adversarial verifier, never by this check.

### Why booleans and nulls are skipped

`true`/`false` and `null` are **judgments about the source, not copied tokens**. A `"paid": false`
encodes "I read the source and concluded unpaid"; the literal token `false` almost never appears in
the source, so grounding it would be all false positives. Booleans are an A4/B4 **review** matter
(judged by the adversarial verifier), not a deterministic gate. `null` is the *correct* representation
of absent data (B4) — there's nothing to ground.

## The groundedness check is necessary, not sufficient

`groundedness-check.py` catches the cleanest, most common hallucination: the value that appears
**nowhere** in the source, **plus** the substring-fragment class below (invented values that are mere
*fragments* of real source words). It **cannot**, by construction, catch a value that *is* a faithful
span of the source but was attached to the **wrong field** — because grounding is a containment test,
not an alignment test. That gap is exactly why A2 also carries the **adversarial verifier**
(`fidelity-axis.md`). The division of labor:

- **`groundedness-check.py`** — deterministic, cheap, runs everywhere; catches *invented* (absent)
  values and fragment hits. Its green is a floor, not a ceiling.
- **the adversarial cross-check** — judgment, fresh context; catches *wrong-span* and *mis-resolved*
  values that ground against the wrong part of the source.

## Wrong-span — the role the value plays

This is the gap the grounding rungs **cannot close**, and the honest center of this skill's design.

> Grounding proves a value is **PRESENT** in the source. It does **not** prove the value plays the
> **CLAIMED ROLE**. `"Acme"` extracted as `buyer` grounds cleanly even when the source has Acme as the
> `seller`. Presence is a containment fact; role is an *alignment* fact — and alignment is not
> decidable by token matching.

A deterministic stdlib checker **cannot** be a wrong-span oracle, and this tool does not pretend to be
one. What it offers instead is split into three honestly-named layers:

| Layer | Mechanism | Proves | Confidence |
|---|---|---|---|
| **Presence** | the four grounding rungs (code) | the value's tokens are *in* the source | deterministic |
| **Proximity** | the opt-in context-cue heuristic (code) | the value sits *near a field cue* in the source | heuristic — an *approximation* of role |
| **Role** | the **adversarial verify** step (fresh context) | the value plays *that* role, not a different one | judgment — the only real confirmation |

**Frame it this way: gate presence (code), gauge proximity (code, opt-in heuristic), confirm role
(adversarial verify).** Never read a clean proximity result as a confirmed role.

### The proximity heuristic (opt-in context cues)

If — and only if — the spec supplies a field one or more **context cues** (the field name and its
synonyms, e.g. `buyer → ["buyer","bill to","purchaser"]`), the check adds a proximity test for that
field:

- for a **grounded** scalar, find its nearest occurrence in the source and check whether it falls
  within a **token window** (default **~12 tokens**, configurable with `--window N`) of any cue
  occurrence;
- grounded but **no cue near any occurrence** → a **WEAK_CONTEXT** advisory: *"value is in the source
  but not near any '<field>' cue — possible wrong-span; verify the role."*

Crucial properties that keep it honest:

- **Opt-in, never a false positive on cue-less specs.** A field with no cues gets **no** proximity
  check and can never emit `WEAK_CONTEXT`. Existing behavior (token-boundary grounding + the
  weak-grounding floor) is **unchanged** when no cues are supplied.
- **Advisory, not a gate.** `WEAK_CONTEXT` is **printed but does not affect the exit code**. An
  ungrounded scalar still fails the gate (exit 1); a grounded-but-far value is *surfaced for a human or
  the adversarial verifier*, not blocked. It is a softer signal than `UNGROUNDED` by construction.
- **It approximates, it does not decide.** Proximity is a proxy for role: a value can sit next to its
  cue and still be the wrong entity (two "Acme"s), or sit far from its cue and be right (a table whose
  header is 40 tokens up). A near result is *reassuring*, not *proof*; a far result is *suspicious*,
  not a *verdict*. The real verdict comes only from the adversarial verifier below.

Cue format (CLI): a JSON object mapping each field's **leaf name** to a list of cue strings, passed as
an optional third argument:

```sh
python3 bin/groundedness-check.py extraction.json source.txt cues.json [--window N]
# cues.json: {"buyer": ["buyer","bill to","purchaser"], "seller": ["seller","sold by","vendor"]}
```

### The adversarial-verify step is what actually confirms role

Because proximity only approximates, **role confirmation is a separate, fresh-context adversarial
step** — never this gate, and never the agent that produced the extraction. Run a *skeptic* with the
source and the extraction in hand and ask it to attack the role of every value:

> *"Here is a source document and a structured extraction drawn from it. For EACH extracted field,
> confirm the value plays THAT role in the source, not a different one. Name any field whose value is
> real (it appears in the source) but **mis-attributed** — e.g. a seller's name placed in `buyer`, a
> ship-to city placed in `bill_to.city`, a pronoun resolved to the wrong antecedent. For each, quote
> the span that establishes the value's actual role. Default to 'this attribution is wrong' and try to
> prove the role; do not assume good faith."*

Feed any flagged field back as an **A2 faithfulness / A4 disambiguation** failure (re-extract from the
correct span; record the span as A5 provenance). This is the half of fidelity code cannot reach — the
proximity heuristic is a cheap pre-filter that *raises* the suspicious ones; the adversarial verifier
is the verdict on role.

### The substring-fragment false negative (now mitigated, worth naming)

The historical weakness of a naive grounding check is the **raw-substring test**: it asks "does this
value appear *anywhere* as a substring?" and so grounds an invented value that is merely a *fragment*
of a real source word — `"Fran"` against `San Francisco`, `"Ware"` against `warehouse`, an invented
`"John Smith"` split into `"John"`/`"Smith"` against `Johnson`/`Smithfield`. Every value is invented,
every value is a substring of something real, and a substring check reports them all grounded — a
silent **false negative** of exactly the class this skill exists to catch. The current check **mitigates
this** with **token / word-boundary matching** (require the value's whole tokens to appear as a
contiguous run of whole source tokens) plus a **weak-grounding floor** (a one-token, ≤3-char match is
surfaced for manual review, not passed). The class is not *eliminated* — a value that happens to be a
real multi-token span of the source, copied into the wrong field, still grounds — but the cheap
fragment hit no longer slips through. Read a green run accordingly: it means every scalar is *locatable
as whole tokens*, not that every value is *correct*.

## The failure taxonomy

When grounding fails — or when the adversarial check fires — classify it; the class names the fix:

| Failure | What it looks like | How it's caught | The fix |
|---|---|---|---|
| **Invented value** | a name/number/date in the extraction the source never states — absent entirely, **or** a mere fragment of a real source word (`"Fran"` from "Francisco") | `groundedness-check.py` flags it (UNGROUNDED; a short fragment that token-matches → WEAK_GROUNDING) | delete it; represent the field as `null` |
| **Wrong-span** | a value that *is* in the source but copied from the wrong place (ship-to city into `bill_to.city`; a seller's name in `buyer`) | **adversarial verifier** confirms it; the opt-in **proximity heuristic** can *pre-flag* it as `WEAK_CONTEXT` when cues are supplied (groundedness alone passes it) | re-extract from the correct span |
| **Over-normalized** | a transform that distorted the fact — `13,020 → 13,000`, `"~50" → 50`, currency dropped | `groundedness-check.py` flags it if the distorted value no longer matches; else the adversarial verifier | re-normalize without distorting; keep the qualifier |
| **Coerced-to-satisfy-required** | a `required` field the source omits, filled with a plausible guess | `groundedness-check.py` flags it (UNGROUNDED) **and** it's a B4 robustness defect | null the field; relax `required` in the schema (see `schema-design.md`) |

The first and last are deterministically caught; the middle two need the verifier. *Coerced-to-satisfy-
required* is the one the schema **manufactures** — the schema's own `required` keyword creates the
pressure to hallucinate (see `validity-axis.md` B4). It is the deepest reason VALIDITY and FIDELITY
must be scored separately.

## Running it

```sh
python3 bin/groundedness-check.py selftest                                 # prove the ladder + the invented-value catch
python3 bin/groundedness-check.py extraction.json source.txt               # nonzero exit on any ungrounded scalar
python3 bin/groundedness-check.py extraction.json source.txt cues.json [--window N]
                                                                           # + opt-in proximity (WEAK_CONTEXT advisory)
```

The output lists every finding with its kind, JSON path, and value: `UNGROUNDED` (no rung matched —
a likely hallucination), `WEAK_GROUNDING` (a short value that token-matched — verify manually),
`EMPTY` (an empty/whitespace value), and — only when cues are supplied — `WEAK_CONTEXT` (grounded but
not near its field cue — a *possible* wrong-span). The first three **fail the gate** (exit 1);
`WEAK_CONTEXT` is **advisory** and does **not** affect the exit code. Read it honestly: an ungrounded
scalar is a **likely**, not certain, hallucination — a locale or scientific-notation number can also be
a false positive — so verify each against the source before shipping, and classify it by the taxonomy
above. A green run means every scalar is *locatable as whole tokens* in the source; it does **not** mean
every value is *correct*, nor that a wrong-span value was caught — a clean run (even with cues) is a
*presence* (and, with cues, *proximity*) result, not a *role* confirmation; run the adversarial
cross-check for that. These findings populate the report card's `groundedness_findings[]` (see
`policy.md`).

## What a faithful extraction looks like

- Every scalar grounds against the source on the EXACT, NORMALIZED, NUMERIC, or DATE rung.
- Normalization **preserves the fact** (the date reformats, the money's value is unchanged, the
  currency survives).
- A field the source is silent on is `null`, not a plausible guess.
- Each value carries (or can be given) a **source span** for provenance (A5).
- It survives the **adversarial cross-check**: a fresh skeptic with the source can locate the exact
  span supporting every value, and finds no wrong-span or mis-resolved entity.
