# The brand-spec card — the gradeable subset of the corpus schema

`brand-spec-check.py` grades a **`*.brand.json` card**: a flattened, gradeable subset of the full
`brand_guideline_corpus.schema.json`. The full corpus schema is an *ingestion* schema (decks → slides →
evidence spans → typed records → brand systems); the card keeps only what the **two axes** need — the
strategy (axis A) and the typed, evidence-linked primitives (axis B) — in one self-contained object.

> **The machine-readable contract is [`schema/brand-spec.schema.json`](../schema/brand-spec.schema.json)**
> (JSON Schema, Draft 2020-12) — this page is its prose companion. Print it with
> `bin/brand-spec-check.py schema`; the bin's selftest **drift-guards** it against the gate's enums
> (`severity`, `truth`, token `type`, `domain`) so the two can't silently diverge. The schema is the
> *declarative* B1 contract (structure, types, enums, required fields); the *semantic* gates (UNTRACED
> provenance, LOW_CONFIDENCE, COLLAPSED_TRUTH, CONTRAST_FAIL, GENERIC_IDEA, INCOMPLETE) are not
> expressible in JSON Schema and live in the bin with domain-meaningful finding kinds. To validate an
> arbitrary card against the schema, pipe it through `type-decomposer`'s `instance-check.py` — wire the
> schema plus your card(s) into its `{schema, legal[], illegal[]}` spec and run it:
>
> ```sh
> # spec = {"schema": <brand-spec.schema.json>, "legal": [<good cards>], "illegal": [<bad cards>]}
> python3 …/type-decomposer/bin/instance-check.py spec.json
> # instance-check: OK — 2 legal validate, 1 illegal rejected (illegal states unrepresentable)
> ```
>
> *Verified:* the `docusign.green` and `empower.hollow` cards validate against the schema, and
> `acme.red` (with `severity:"loud"`, `truth:"guess"`) is rejected — so the schema, the bin, and
> instance-check agree on what is well-formed.

## The card

```json
{
  "brand": "DocuSign",
  "strategy": {
    "brand_idea": "Agreements are dynamic moments of connection, not static documents — make the moment of agreement feel like forward progress.",
    "meaning_chain": ["idea", "voice", "mark", "color", "type", "layout", "imagery", "apps"]
  },
  "domains": { "mark": {}, "voice": {}, "color": {}, "type": {}, "expression": {}, "governance": {} },
  "tokens": [
    { "id": "color.ink", "type": "color", "role": "text", "value": "#130032",
      "meaning": "primary ink for body and headlines",
      "evidence": [{ "deck_id": "docusign-2024", "slide_id": "docusign-2024-slide-007", "confidence": 0.92 }],
      "confidence": 0.95, "truth": "observed" }
  ],
  "rules": [
    { "id": "mark.clearspace", "domain": "mark",
      "statement": "Maintain clearspace = the height of the logomark on all sides.",
      "severity": "must", "evidence": [ … ], "confidence": 0.95, "truth": "observed" }
  ],
  "examples": [
    { "id": "ex.ui", "surface": "product-ui",
      "description": "A high-trust signing moment: neutral system carries the base, primary only as the activation CTA.",
      "rules_demonstrated": ["color.activation"], "evidence": [ … ] }
  ],
  "surfaces": ["homepage", "product-ui", "social", "email", "campaign"],
  "color_pairs": [
    { "name": "ink on surface", "fg": "#130032", "bg": "#ffffff", "size": "normal", "role": "text" }
  ]
}
```

## Field reference

| Field | Axis | Required | Notes |
|---|---|---|---|
| `brand` | — | yes | the brand name (used in every finding) |
| `strategy.brand_idea` | **A1** | yes | the core; `GENERIC_IDEA` fails if it is only interchangeable adjectives |
| `strategy.meaning_chain` | **A2** | yes | `idea→voice→mark→color→type→…`; < 4 links warns (idea not propagated) |
| `domains` | **B4** | — | a presence map; a key present = that domain is claimed covered |
| `tokens[]` | **B1·B2·B3** | — | `{id, type, role, value, meaning, evidence[], confidence, truth}`; `BARE_TOKEN` if value without role+meaning |
| `rules[]` | **B1·B2** | — | `{id, domain, statement, severity, evidence[], confidence, truth}` |
| `examples[]` | **A4·B4** | — | `{id, surface, description, rules_demonstrated[], evidence[]}`; evidence-linked, not a screenshot |
| `surfaces[]` | **B4** | — | where the brand lives; empty = `INCOMPLETE` |
| `color_pairs[]` | **B3** | — | `{name, fg, bg, size:normal\|large, role:text\|ui}`; each checked against the WCAG AA floor |

## Enumerations (faithful to the corpus schema)

- **`severity`** ∈ `{must, should, may}` — the corpus's RFC-2119 enum. `must` = a hard rule, `may` = a
  flexible range; this is the corpus's "distinguish hard rules from flexible expression."
- **`truth`** ∈ `{observed, inferred, proposed}` — the three truths, never collapsed
  (`references/evidence-and-confidence.md`).
- **token `type`** ∈ `{color, type, space, radius, motion, elevation}`.
- **`domain`** — the six rubric-aligned domains `{mark, voice, color, type, expression, governance}`.
  The full corpus `brand_domain` enum is finer (17 values); the card **normalizes** them:
  `logo→mark`, `typography→type`, and `layout / photography / illustration / motion / product /
  marketing / social / packaging / environmental / co_branding / data_visualization → expression`.
  `strategy` is not a domain — it is the brand idea (A1). So a card authored against the full corpus
  schema grades without modification.

## How the card relates to the full corpus schema

| Corpus `$def` | In the card | Why flattened |
|---|---|---|
| `brand_system.strategy` | `strategy` | the idea + chain are all the A axis needs |
| `brand_claim` | folded into `strategy.brand_idea` | the claim that decides the grade is the central idea |
| `brand_rule` | `rules[]` (+ a `truth` field) | drops `rule_type` / `rationale` / `context` from the *required* subset — `context` is graded as B5 judgment, not a gate |
| `brand_token` *(lives inside `visual_identity`)* | `tokens[]` | lifted to the top level so every primitive is checkable in one place |
| `brand_example` | `examples[]` | keeps `surface`, `description`, `rules_demonstrated`, `evidence` |
| `text_evidence` / `visual_observation` | the `truth` field | the corpus separates observed evidence from inferred records *structurally*; the card carries `truth` per-record so the three-truths separation is checkable in the flattened form |
| `evidence_ref` | `evidence[]` entries | unchanged — `{deck_id, slide_id, slide_number, source_url, extraction_method, confidence}` |

The card is **deliberately lossy**: it is the grading projection, not the archive. Produce it from a
full corpus by projection (DECOMPOSE), or author it directly (DESIGN). Either way the gate reads the
same fields.
