# report-brief: Format Guide

## Section-by-section guidance

### 1. Classification / Header

```
SUBJECT: [Topic — specific, ≤ 12 words]
DATE: [YYYY-MM-DD]
AUTHOR: [Name or role]
FOR: [Audience — decision-maker, team, general]
```

Subject line standard: Be specific. "AI Vendor Landscape" → "Three AI Vendors Reaching
GPT-4 Parity by Q3: Competitive Assessment"

---

### 2. Bottom Line Up Front (BLUF)

Max 4 sentences. Structure:

**Sentence 1**: [Confidence level] + key assessment
> "We assess with high confidence that Anthropic will release a frontier multimodal model
> competitive with GPT-4o by Q2 2026."

**Sentence 2**: Why it matters for the reader's context
> "This accelerates the window for differentiation via model-specific features before
> the market homogenizes."

**Sentence 3** (optional): The strongest supporting evidence in a single clause
> "Assessment is based on disclosed compute investments, benchmark trajectory, and two
> confirmed lab recruitment events in the past 90 days."

**Sentence 4** (optional): Time-sensitive implication
> "Procurement decisions made before Q1 2026 should account for this shift."

**Anti-pattern**: Starting the BLUF with background or history. The BLUF is the
assessment, not the setup.

---

### 3. Key Judgments

3–7 bullets. Each bullet: [Confidence] + claim + brief rationale.

```
• [HIGH CONFIDENCE] [Claim]. Evidence: [1-sentence rationale].
• [MODERATE CONFIDENCE] [Claim]. Evidence: [1-sentence rationale].
• [LOW CONFIDENCE] [Claim]. Rationale: [Note inferential basis].
```

Ordering: most important judgment first, regardless of confidence level.

Changed judgments: Flag explicitly.
> "• [HIGH CONFIDENCE] [Claim]. ⚑ Assessment elevated from MODERATE since last brief
>   (March 2026) based on [new evidence]."

---

### 4. Background

1 paragraph maximum. Purpose: minimum prior knowledge for a reader without domain
context. Do not repeat the BLUF. Do not exceed one paragraph.

---

### 5. Evidence Summary

One table or structured list. For each key judgment, summarize the evidence:

| Judgment | Supporting evidence | Tier | Contradicting evidence |
|---|---|---|---|
| [Claim] | [Evidence summary] | Primary | [Any contrary evidence] |

If contradicting evidence is present, address it — don't omit it. Name why the
leading hypothesis is preferred despite the contradiction.

---

### 6. Competing Hypotheses

Use when any key judgment is rated moderate or low confidence, or when the evidence
supports more than one interpretation.

**Format**:
```
Hypothesis A: [Statement]
  Supporting evidence: [...]
  Contradicting evidence: [...]

Hypothesis B: [Statement]  
  Supporting evidence: [...]
  Contradicting evidence: [...]

Assessment: Hypothesis A is preferred because [evidence pattern]. We do not rule out
Hypothesis B; it would become more likely if [condition].
```

If confidence is high and alternatives are clearly ruled out, this section may be
omitted. State why briefly.

---

### 7. Intelligence Gaps

Bulleted list. Each gap: what is unknown + impact on assessment + how to fill it.

```
• [GAP]: We do not know [X].
  Impact: [How this changes the assessment if known].
  Collection: [What research or source would fill this gap].
  Severity: Critical / Significant / Informational
```

Minimum: always include at least one gap. A brief with no gaps claims perfect
information — and is therefore not credible.

---

### 8. Implications

Tailored to the reader's specific context. Generic implications ("this is an important
development") are not useful.

**Format for each implication**:
```
For [reader role / decision context]: [Specific implication]. 
Time-sensitive: [Is action needed now / soon / not urgent?]
```

---

### 9. Source Notes (optional)

Include when:
- A key judgment rests on a single source
- Sources have freshness caveats (e.g., data >12 months old)
- Source access or methods should be disclosed

Format: brief, factual. Not a full bibliography.

---

## Length norms

| Brief type | Length |
|---|---|
| Flash brief (urgent) | 1 page |
| Standard brief | 2–3 pages |
| Comprehensive briefing | 4–6 pages |

A brief longer than 6 pages should become a strategic report (use `report-strategic`).

---

## Signal density

Intelligence briefs are intentionally dense. Unlike strategic reports that build toward
conclusions, briefs assume the reader will tolerate high signal density in exchange
for brevity. This means:
- No throat-clearing sentences
- No "in conclusion" or "as we can see" transitions
- No summaries of sections you just wrote
- Findings directly followed by evidence, directly followed by implication
