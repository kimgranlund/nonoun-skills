# Evidence, confidence & the three truths — the trust contract

The core object of a brand spec **is not "the brand." It is evidence.** A deck page says or shows
something; the spec captures that as raw text + slide metadata + a visual observation; extraction turns
it into typed claims, rules, tokens, and examples; the agent reasons over those records **while
preserving provenance.** Everything an agent retrieves or cites must trace back to a deck, slide, or
source. This file is the **B2 (traced & trusted)** contract — mechanized by `brand-spec-check.py`.

## The evidence model

Every extracted record carries an `evidence[]` array. Each entry points at where the claim came from:

```json
{
  "evidence": [
    {
      "deck_id": "docusign-2024",
      "slide_id": "docusign-2024-slide-007",
      "slide_number": 7,
      "source_url": "https://www.deck.gallery/docusign-brand-guidelines/",
      "extraction_method": "slide_alt_text",
      "confidence": 0.92
    }
  ]
}
```

- **`UNTRACED` (gate fail)** — any rule, token, or example with no `evidence[]`. An unsourced claim is
  indistinguishable from an invention; the corpus's quality bar is **Traceable: every non-obvious claim
  has source evidence.** The gate checks *presence*, not *truth* — a fabricated slide id passes the
  presence check, so confirm provenance out of band on high-stakes claims.
- **What is "non-obvious."** A literal restatement of a slide ("the logo is blue") and an
  industry-universal default need no source. An inferred rule, a normalized claim, an exact spec value,
  a prohibition, or an agency credit **always** needs one.

## Confidence as an operational signal

Confidence is not decoration — it is the **operational trust band** the agent uses to decide whether it
may act on a record. Store a confidence on every interpretation.

| Band | Meaning | Agent may… |
|---|---|---|
| `0.90–1.00` | **explicitly stated** by the deck | use directly, cite as a rule |
| `0.75–0.89` | **strongly supported** by repeated slide evidence | use, note as inferred |
| `0.50–0.74` | **plausible inference requiring review** | use only when `review`-flagged; surface the uncertainty |
| `<0.50` | **do not use** for critique or generation without human review | hold for human review |

- **`LOW_CONFIDENCE` (gate fail):** an `inferred` record below `0.75` that is **not** `review`-flagged.
  Presenting a `0.60` inference as a settled rule is the trust defect this band exists to prevent.
- **Uncertain where appropriate** is itself a quality bar: exact colors, type values, legal/trademark
  rules, and agency credits **must be verified** (or review-flagged) if the source does not explicitly
  state them. A spec that is falsely confident about an unverified hex is worse than one that flags it.

## The three truths — never collapse them

The spec preserves three different kinds of truth. Fusing them into one field destroys the reader's
ability to tell a documented rule from a guess from a recommendation.

- **Observed** — what the slide visibly says or shows. *(raw evidence; highest trust)*
- **Inferred** — what the system likely means, based on repeated evidence. *(interpretation; carries a
  confidence band)*
- **Proposed** — what the agent recommends for the designer's current work. *(a move, not a rule;
  belongs to CRITIQUE, never stored as a brand fact)*

> Never collapse those into one field.

- **`COLLAPSED_TRUTH` (gate fail):** a record whose `truth` is not exactly one of `observed` /
  `inferred` / `proposed`. A `truth: "guess"` is a collapsed truth — it hides whether the claim is
  documented or invented.
- **Why it matters operationally.** In CRITIQUE, the agent must separate *what the work is doing now*
  from *what the brand system says* from *what it proposes next* (`references/critique-mode.md`). If the
  spec itself collapses observed and inferred, the critique inherits the confusion and cites a guess as
  a rule.

## The QA checklist — what the gate enforces vs. what you must still check

`brand-spec-check.py` mechanizes the **claim/rule/token QA** that is arithmetic:

- Every typed record has `evidence[]` and a `confidence` in `[0,1]`. *(UNTRACED, range checks)*
- Inferred records below `0.75` are review-flagged. *(LOW_CONFIDENCE)*
- `truth` is one of the three. *(COLLAPSED_TRUTH)*
- Severity, token type in their enums; tokens have role + meaning. *(WELL_FORMED, BARE_TOKEN)*

It **cannot** mechanize the judgment QA — you must still confirm by reading:

- The claim is **not generic** unless the deck explicitly uses it. *(normalization must not erase
  nuance, nor invent it)*
- **Prohibitions are not invented from preferences** — a "we prefer X" is not a "never Y."
- **Raw evidence is separated from inference** — an inference must not be stored as observed evidence.
- **Meaning is source-supported** — a token's stated meaning traces to a slide, not to the extractor's
  imagination.

A green B2 gate means the *structure* of trust is intact; it does not certify the evidence is real or
the inference is sound. Necessary, not sufficient — the doctrine of every mechanism gate in this repo.
