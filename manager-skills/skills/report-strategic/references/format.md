# report-strategic: Format Guide

## Section-by-section guidance

### 1. Cover / Title Block

Keep this minimal. Include:
- Title (should name the specific subject, not just "Strategic Report")
- Subject scope (1 sentence bounding statement)
- Author, date (YYYY-MM-DD), version (v1.0, v1.1...)
- Audience and distribution if it matters for how the reader engages

Bad title: "AI Strategy Report"
Good title: "AI Investment Priorities for the Payments Platform: 2026–2027"

---

### 2. Executive Summary

Write this **last**. Max 1 page. Four elements:

**Situation** (1–2 sentences): What is the context that makes this report necessary?
> "The payments platform serves 4M monthly users across 12 markets, but three competing
> AI vendors have launched feature-equivalent capabilities at 40% lower cost since Q3 2025."

**Key findings** (3–5 bullets): Self-contained facts. Assume the reader reads only these.
- Each bullet: one finding + the evidence in parentheses or em-dash
- Order: most important first
- No jargon without prior definition

**Primary recommendation** (1–2 sentences): The single most important action.
> "We recommend a 6-month vendor consolidation beginning Q3 2026, expected to reduce
> AI infrastructure costs by $2.4M annually."

---

### 3. Glossary / Terminology

Build this **before writing findings**. Three categories:

**Domain terms**: Technical or industry vocabulary that a non-specialist reader may not know.
Format: `**Term**: Definition. Source if applicable.`

**Contested terms**: Words that mean different things to different communities.
Format: `**Term**: [In this report, this means X. Note: Y community uses this to mean Z.]`

**Abbreviations**: Any abbreviation used in the report.
Format: `**API**: Application Programming Interface`

Keep definitions to 1–3 sentences. Link to authoritative sources if citing a standard.

---

### 4. Context & Background

Three paragraphs maximum:

1. **Why now**: The forcing function. What event, trend, or decision deadline makes this
   topic timely?

2. **History**: Brief. What trajectory has brought us here? What prior decisions are
   relevant?

3. **Scope**: What is in scope and what is explicitly out of scope. Scope statements
   prevent readers from holding you accountable for things you didn't cover.

> "This report covers AI capabilities in the payments vertical only. Adjacent investments
> in the fraud platform and KYC pipeline are out of scope."

---

### 5. Methodology

Short (1–2 paragraphs or a brief table). Answer:
- What sources were consulted? (Categorize: primary research / industry reports / internal data / expert interviews)
- What is the data time window?
- What are the known limitations?

**Source reliability tiers** (use these labels consistently):
| Tier | Description |
|---|---|
| Primary | Direct observation, primary documents, first-party data |
| Secondary | Analysis of primary sources; industry reports; reviewed research |
| Estimated | Inference, extrapolation, or expert judgment with no direct source |

---

### 6. Findings

Each finding follows this structure:

```
**Finding [N]: [Headline — a specific, falsifiable claim]**

Evidence: [Data, quote, or citation supporting the claim. Source tier in brackets.]

Significance: [Why this matters for the reader's situation or decision.]
```

Rules:
- Findings should be specific, not general. "Costs are rising" → "Vendor X costs have
  increased 23% YoY, from $1.2M to $1.47M (Primary: internal procurement data, Q1 2026)"
- Mark speculative findings: add "(Estimated)" after the headline
- Use tables to present comparative data across multiple items
- Use viz-2x2 for positioning or trade-off analysis

**Table template for comparisons:**
| Dimension | Option A | Option B | Source |
|---|---|---|---|
| Cost | $X | $Y | Primary |
| ...  | ... | ... | ... |

---

### 7. Strategic Implications

Two sub-sections:

**Risk surface**: Name each risk as: Risk statement | Likelihood (H/M/L) | Impact (H/M/L)
> "If Vendor X exits the market before our contract expires, we face a 6-month migration
> risk with no tested fallback. Likelihood: Low. Impact: High."

**Opportunity surface**: Name each opportunity as: Opportunity | Condition required | Payoff
> "If we consolidate vendors by Q3, we can renegotiate at scale and achieve estimated
> $2.4M annual savings. Condition: exec approval by end of Q2."

---

### 8. Recommendations

Format each recommendation as a numbered item:

```
**[N]. [Action verb phrase]**
- Owner: [Name or role]
- Success condition: [How we know this is done / done well]
- Timeline: [Target date or trigger condition]
- Dependencies: [What must happen first, if any]
```

Order by priority, not chronology. If there's only one recommendation, say so and name why.

---

### 9. Appendices

Only include if:
- There is data too detailed for the findings section but necessary for verification
- Alternative analyses were considered and rejected (name them and why)
- Methodology requires more than 2 paragraphs to document properly

Label each appendix (A, B, C) and reference them from the findings or methodology sections.

---

### 10. References

List all sources cited in the report.

Format:
```
[Author/Org] — [Title or description]. [Date]. [Tier: Primary/Secondary/Estimated]
```

Example:
```
Stripe, Inc. — "Payments Infrastructure Benchmark Report 2025." March 2025. [Secondary]
Internal Procurement — "Vendor Cost Summary FY2025." Q1 2026 export. [Primary]
```

---

## Length norms

| Report type | Approximate length |
|---|---|
| Executive brief | 2–4 pages |
| Standard strategic report | 6–12 pages |
| Comprehensive analysis | 12–20 pages + appendices |

Always calibrate to audience: executives want 2–4 pages; technical implementers may need 10+.
