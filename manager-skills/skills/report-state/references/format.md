# report-state: Format Guide

## Section-by-section guidance

### 1. Cover / Header

```
STATE OF: [Subject — specific name of system, domain, or initiative]
Period: [Date range or "as of YYYY-MM-DD"]
Author: [Name or role]
Audience: [Who this is for]
```

---

### 2. Executive Summary (≤ 1 page)

Four elements, in order:

**Overall health signal**: One line: `Overall: 🟡 AMBER — [1-sentence rationale]`

**Key observations** (3–5 bullets):
- Each bullet: a specific, self-contained observation
- Order: most critical first
- Mix of positive and negative — do not only surface problems

**Overall trajectory**: One line: `Trajectory: Improving | Stable | Deteriorating`
- Improving: the trend across multiple dimensions is positive
- Stable: no meaningful change this period
- Deteriorating: the trend is negative

**Immediate attention items** (0–2 only):
- Reserve for genuinely urgent Red items
- If nothing is urgent, say "No items require immediate attention this period"

---

### 3. Scope & Inventory

**Scope statement**: Two explicit sentences.
> "This assessment covers [X, Y, Z]. It does not cover [A, B] — see [reference] for those."

**Inventory table**: Complete list of everything assessed.

| # | Name | Category | Coverage confidence |
|---|---|---|---|
| 1 | [Component] | [Category] | Full / Partial / Estimated |
| ... | ... | ... | ... |

Coverage confidence:
- **Full**: Deep visibility; high-quality data
- **Partial**: Some visibility; known gaps in understanding
- **Estimated**: Little direct visibility; based on inference

---

### 4. Health Signal Matrix

One row per component. Keep it scannable.

| Component | Status | Trend | Confidence | Key evidence |
|---|---|---|---|---|
| [Name] | 🟢 Green | ↑ | High | [1-sentence evidence] |
| [Name] | 🟡 Amber | ↔ | Moderate | [1-sentence evidence] |
| [Name] | 🔴 Red | ↓ | High | [1-sentence evidence] |
| [Name] | ⚫ Unknown | — | — | [Gap description] |

**Mandate**: Every signal must have evidence in the key evidence column.
An unsubstantiated signal is an opinion, not an assessment.

**Health signal criteria** (define these in a footnote or sidebar):
```
Green: Operating within expected parameters; no known issues requiring intervention
Amber: Degraded or at risk; known issues present; monitoring or action in progress  
Red: Critical issues present; requires immediate attention or is blocking progress
Unknown: Insufficient information to assess
```

Trend: ↑ Improving | ↔ Stable | ↓ Deteriorating
Confidence: High / Moderate / Low (from evidence quality, not the health signal itself)

---

### 5. Domain Deep-Dives

One section per domain, or one per Red/Amber item at minimum.

**Structure per domain**:

```
## [Domain Name]  Status: [Signal] Trend: [↑/↔/↓]

### Current state
[1–3 paragraphs or bullet list describing what exists]

### What's working
[Specific, evidence-backed items]

### What isn't working  
[Specific, evidence-backed items — be honest]

### Root causes (for Amber/Red items)
[Contributing factors, not blame]

### Evidence
[Sources, data points, observations supporting the above]
```

**Depth calibration**:
- Green items: 1–2 paragraphs suffice
- Amber items: Full structure with root causes
- Red items: Full structure with root causes + immediate action needed

---

### 6. Trend Analysis

| Dimension | Direction | Velocity | Leading indicators |
|---|---|---|---|
| [Dimension] | ↑/↔/↓ | Fast/Slow | [What predicts near-term change] |

**Velocity**: How fast is change happening in this dimension?
- **Fast**: Noticeable change within weeks
- **Slow**: Change visible only over months or quarters

**Leading indicators**: Observable signals that typically precede changes in this dimension.
> "New API error rate (currently 0.3%) — has preceded reliability degradations in 2 of
> 3 prior incidents."

**Comparison to prior assessment** (if applicable):
> "In the March 2026 assessment, overall trajectory was Improving. This assessment
> downgrades to Stable based on slowdown in [dimension]."

---

### 7. Gap Map

| Gap | Severity | Owner | Path to close |
|---|---|---|---|
| [What is unknown/missing] | Critical/Significant/Informational | [Name or role] | [Action or research needed] |

Severity:
- **Critical**: Blocking a health assessment or a key decision
- **Significant**: Limits confidence; would meaningfully improve the picture
- **Informational**: Would be useful; doesn't change the overall view

Every gap must have an owner. "No owner" is itself a gap to be called out.

---

### 8. Path Forward

**Mark clearly** as forward-looking. This section does not describe current state.

Format: ordered action items.

| Priority | Action | Owner | Target date | Dependency |
|---|---|---|---|---|
| 1 | [Action] | [Owner] | [Date] | [Prerequisite] |

"What good looks like" at the next assessment:
> "At the next assessment (target: Q3 2026), we expect: [Green items]; [Amber items
> resolved]; [gap X filled]."

---

## Length norms

| Scope | Length |
|---|---|
| Single system (3–5 components) | 4–6 pages |
| Domain portfolio (6–15 components) | 8–12 pages |
| Large portfolio (15+ components) | 12–20 pages + appendix |

One health signal matrix row per component; only Red and Amber items get deep-dives.
