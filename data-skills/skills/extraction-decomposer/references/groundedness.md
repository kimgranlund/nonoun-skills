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
| **EXACT** | the value is a verbatim substring of the source | `Acme Robotics Inc.` → `"Acme Robotics Inc."` |
| **NORMALIZED** | matches after case-fold + whitespace-collapse + edge-punctuation trim | `"  ACME  Corp. "` → `"Acme Corp."` |
| **NUMERIC** | a source number is digits-and-sign equal (commas, currency, trailing zeros ignored) | `$12,000.00` → `12000` |
| **DATE** | a source date appears in a common reformat (ISO ↔ slashed ↔ month-name, M/D and D/M both) | `June 16, 2026` → `"2026-06-16"` |

These four rungs are exactly the **faithful normalizations** A3 permits — reformatting that preserves
the asserted fact. Anything that survives none of them is **UNGROUNDED** and flagged as a likely
hallucination. (Empty strings are vacuously grounded — they assert nothing about the source.)

### Why booleans and nulls are skipped

`true`/`false` and `null` are **judgments about the source, not copied tokens**. A `"paid": false`
encodes "I read the source and concluded unpaid"; the literal token `false` almost never appears in
the source, so grounding it would be all false positives. Booleans are an A4/B4 **review** matter
(judged by the adversarial verifier), not a deterministic gate. `null` is the *correct* representation
of absent data (B4) — there's nothing to ground.

## The groundedness check is necessary, not sufficient

`groundedness-check.py` catches the cleanest, most common hallucination: the value that appears
**nowhere** in the source. It **cannot**, by construction, catch a value that *is* in the source but
is **wrong** — because grounding is a containment test, not an alignment test. That gap is exactly why
A2 also carries the **adversarial verifier** (`fidelity-axis.md`). The division of labor:

- **`groundedness-check.py`** — deterministic, cheap, runs everywhere; catches *invented* (absent)
  values. Its green is a floor, not a ceiling.
- **the adversarial cross-check** — judgment, fresh context; catches *wrong-span* and *mis-resolved*
  values that ground against the wrong part of the source.

## The failure taxonomy

When grounding fails — or when the adversarial check fires — classify it; the class names the fix:

| Failure | What it looks like | How it's caught | The fix |
|---|---|---|---|
| **Invented value** | a name/number/date in the extraction that is in the source **nowhere** | `groundedness-check.py` flags it (UNGROUNDED) | delete it; represent the field as `null` |
| **Wrong-span** | a value that *is* in the source but copied from the wrong place (ship-to city into `bill_to.city`) | adversarial verifier (groundedness passes it) | re-extract from the correct span |
| **Over-normalized** | a transform that distorted the fact — `13,020 → 13,000`, `"~50" → 50`, currency dropped | `groundedness-check.py` flags it if the distorted value no longer matches; else the adversarial verifier | re-normalize without distorting; keep the qualifier |
| **Coerced-to-satisfy-required** | a `required` field the source omits, filled with a plausible guess | `groundedness-check.py` flags it (UNGROUNDED) **and** it's a B4 robustness defect | null the field; relax `required` in the schema (see `schema-design.md`) |

The first and last are deterministically caught; the middle two need the verifier. *Coerced-to-satisfy-
required* is the one the schema **manufactures** — the schema's own `required` keyword creates the
pressure to hallucinate (see `validity-axis.md` B4). It is the deepest reason VALIDITY and FIDELITY
must be scored separately.

## Running it

```sh
python3 bin/groundedness-check.py selftest                      # prove the ladder + the invented-value catch
python3 bin/groundedness-check.py extraction.json source.txt    # nonzero exit on any ungrounded scalar
```

The output lists every `UNGROUNDED` scalar with its JSON path and value. Read it honestly: an
ungrounded scalar is a **likely** hallucination — verify each against the source before shipping, and
classify it by the taxonomy above. A green run means every scalar is *locatable* in the source; it
does **not** mean every value is *correct* (run the adversarial cross-check for that). These findings
populate the report card's `groundedness_findings[]` (see `policy.md`).

## What a faithful extraction looks like

- Every scalar grounds against the source on the EXACT, NORMALIZED, NUMERIC, or DATE rung.
- Normalization **preserves the fact** (the date reformats, the money's value is unchanged, the
  currency survives).
- A field the source is silent on is `null`, not a plausible guess.
- Each value carries (or can be given) a **source span** for provenance (A5).
- It survives the **adversarial cross-check**: a fresh skeptic with the source can locate the exact
  span supporting every value, and finds no wrong-span or mis-resolved entity.
