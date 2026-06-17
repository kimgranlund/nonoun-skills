# The FIDELITY axis — is it the right data?

The Fidelity axis (A1–A5) grades *intent*, top-down: from "is everything the source provides
captured" to "can each value be traced to a span." This is the **dangerous** axis and the one the
cheap gate **cannot see** — a schema validator is silent on "this value was never in the source." It
is also exactly where an LLM fails with the most confidence: it produces a fluent, plausible,
schema-shaped value for a field, whether or not the source ever stated it. So this axis carries a
**deterministic groundedness check** *and* a **fresh-context adversarial verifier**, not just a
checklist.

## A1 · Completeness `[gate]`

Did the extraction capture every field the source *actually provides*? LLMs drop values silently —
the line item buried mid-paragraph, the second phone number, the date in the footer.

- Walk the **schema's fields against the source**: for each field, is the source's stated value
  present in the extraction? A field the source plainly provides but the extraction omits is a
  completeness failure.
- Distinguish a **drop** (source says it, extraction lost it — a fidelity gate failure) from an
  **absence** (source is silent, the field is correctly `null` or omitted — a B4 *robustness* matter,
  not a completeness failure). Completeness is about what the source *gives*, not what the schema
  *wants*.
- **Gate:** a dropped value means the extraction is incomplete regardless of how clean the rest is —
  every downstream consumer is missing data the source contained. Recover it before scoring below.

## A2 · Faithfulness `[gate]` — the no-invented-values discipline

This is the dangerous gate, the crossing seam with VALIDITY, and the reason the skill exists.

> **Every extracted value must be grounded in the source. No invented values, ever.** A value that is
> not supported by the source is a **hallucination**, even when it is plausible, well-typed, and
> schema-valid.

The discipline, in order:

1. **Run `bin/groundedness-check.py`** over the extraction + the source. It asserts every scalar is
   grounded — exact substring, normalized, numeric-key, or date-reformat match (see `groundedness.md`
   for the full ladder and the failure taxonomy). Any **ungrounded** scalar is a likely invented
   value and a gate failure until explained.
2. **Groundedness is necessary, not sufficient.** It catches the value that appears *nowhere* in the
   source (the cleanest hallucination). It cannot, by construction, catch a **wrong-span** value —
   one that *is* somewhere in the source but was attached to the wrong field (extracting the *ship-to*
   city into `bill_to.city`). That's what the adversarial verifier is for.
3. **Run the adversarial verifier** (below) for what groundedness can't see.

A faithfulness failure is corrected by **deleting the invented value and representing the field as
`null`** (see B4 and `validity-axis.md`) — never by inventing a *different* plausible value.

## A3 · Normalization `[review]`

Were values made consistent — units, dates, casing, number formats — **without distorting meaning**?

- **Faithful normalization** preserves the asserted fact: `"June 16, 2026" → "2026-06-16"`,
  `"$12,000.00" → 12000.0`, `"  Acme  Corp. " → "Acme Corp."`, `"EUR 50" → {amount: 50, currency:
  "EUR"}`. The groundedness check tolerates all of these (its normalized/numeric/date rungs).
- **Distorting normalization** is a *fidelity defect* in disguise: rounding `13,020 → 13,000`,
  coercing a `"~50"` estimate to an exact `50`, dropping a currency, snapping a fuzzy `"mid-June"` to
  a precise date the source never gave. If normalization changed what the source *asserts*, it's an
  A2/A3 failure, not a formatting nicety.
- Score by **meaning-preservation and consistency** across the document (every money field the same
  shape, every date ISO), not by how clever the transform is.

## A4 · Disambiguation `[review]`

When the source is **ambiguous**, did the extraction resolve to the **right** referent — or guess?

- **Entity ambiguity** — two people named "Lee", "the company" with three companies in scope, a bare
  "their account". Pick by what the source's local context supports; if it supports neither
  confidently, that's a `null` + a provenance note, not a coin flip.
- **Sense ambiguity** — "Apple" the vendor vs the fruit, "May" the month vs the name, "$" as USD vs
  another dollar. Resolve from the document's domain.
- **Co-reference** — a pronoun or "the above" pointing back. Resolve to the antecedent the source
  actually establishes; a mis-resolved co-reference produces a *grounded but wrong* value — the exact
  case groundedness can't catch.
- The defect to watch: a **confident guess presented as fact**. The right move on irreducible
  ambiguity is to surface it (null + provenance), not to manufacture certainty.

## A5 · Provenance `[review]`

Is each value **traceable to a specific source span** — a character offset, a line/page, or a quoted
snippet?

- Provenance is what makes A2 **auditable after the fact**: a reviewer (or `groundedness-check.py`)
  can confirm the value against its cited span instead of re-reading the whole document.
- For extraction at scale, a value with no provenance is a value you cannot verify cheaply — treat
  weak/absent provenance as a real review gap, not a nicety.
- The strongest extraction contracts carry provenance *in the schema* (`{value, source_span}` per
  field), turning A5 into a structural guarantee rather than a hope.

## The adversarial source cross-check (route A2/A4 to a skeptic, not the author)

The dangerous defects — *invented value* and *wrong-span / mis-resolved entity* — are not fully
gateable by groundedness. Verify them the way `deep-research` verifies claims: **in a fresh context,
adversarially, with the source in hand.**

Prompt a **separate** verifier (a fresh agent — not the one that produced or approved the extraction):

> *"Here is a source document and a structured extraction claimed to be drawn from it. For EACH
> extracted value, find the exact span of the source that supports it. Flag every value you cannot
> locate, every value attached to the wrong field, and every entity resolved to the wrong referent.
> Default to 'this value is unsupported' and try to prove support — do not assume good faith."*

- A verifier sharing the author's context inherits its blind spots and rubber-stamps the
  hallucination. **Separation is the point.**
- Feed any flagged value back as an **A2 faithfulness failure** (delete + `null`) or an **A4
  disambiguation failure** (re-resolve), and record its span as the missing **A5 provenance**.
- This is the half of fidelity that code can't reach. `groundedness-check.py` is the cheap,
  deterministic pre-filter; the adversarial cross-check is the verdict on what survives it.

The output of this axis feeds the **extraction-report card**'s `groundedness_findings[]` and
`adversarial_verdict` (see `policy.md`).
