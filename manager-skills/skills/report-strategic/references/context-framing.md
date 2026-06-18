# report-strategic: Context Framing Technique

## The problem this solves

Strategic reports fail when readers bring incompatible mental models to the findings.
A finding like "our NPS has declined 8 points" lands differently depending on whether
the reader knows what NPS is, what our baseline was, and whether 8 points is catastrophic
or noise. Context framing prevents that divergence.

## The three layers of context

### Layer 1: Vocabulary alignment (Glossary)

**Purpose**: Ensure every reader decodes the same meaning from the same word.

**Process**:
1. Write your findings section first (rough draft).
2. Highlight every term that could be misread by a non-specialist.
3. For each term: write the definition you are using, flag if it's contested.
4. Move the glossary to Section 3 — before findings, after the executive summary.

**Anti-pattern**: Defining terms inline (in parentheses) as you use them. This interrupts
reading flow and creates inconsistency when the same term appears in multiple places.

**Anti-pattern**: Defining terms in a footnote at the end. Readers won't look.

---

### Layer 2: Mental model setup (Context & Background)

**Purpose**: Give readers the minimum prior knowledge needed to interpret findings correctly.

**The "prior knowledge test"**: For each finding, ask: "What would a reader need to already
know to find this surprising, concerning, or interesting?" Supply that in Context & Background.

**What to include**:
- The status quo before this report's time window
- Key metrics at baseline (so readers can interpret changes)
- The decision or event that makes this topic timely
- What others in the field are doing (if relevant for comparison)

**What to exclude**:
- History that is genuinely irrelevant to the current findings
- Background that assumes reader familiarity with internal jargon
- Background that duplicates what's in the executive summary

---

### Layer 3: Scope declaration

**Purpose**: Prevent the reader from holding the report accountable for questions it
didn't set out to answer.

**Format**: Two explicit statements.

**In scope**: "[This report covers] X, Y, and Z."
**Out of scope**: "[This report does not cover] A, B, or C — see [reference] for those."

**Why this matters**: Without scope boundaries, an executive reading findings about
Platform A will immediately ask about Platforms B and C. Addressing that question upfront
prevents it from derailing the presentation.

---

## Contested terminology guide

Some terms are frequently misread in strategic contexts. Pre-define these if you use them:

| Term | Common misreads | Clarify by stating |
|---|---|---|
| **Strategy** | Vision; plan; roadmap | "In this report, strategy means a choice of where to play and how to win (after Porter)" |
| **ROI** | Gross return; net return; payback period | "ROI here is defined as net return / total invested capital over 24 months" |
| **AI** | LLMs only; all ML; automation broadly | "AI in this report means large language model capabilities (LLMs and their derivatives)" |
| **Platform** | Product; infrastructure; both | Define which meaning on first use |
| **Customer** | End user; buyer; both | "Customer refers to the paying entity (typically B2B buyer), not the end user" |
| **North Star metric** | Primary KPI; aspirational goal | "North Star metric = the single metric that best captures delivered value to customers" |

---

## Framing for different audiences

**Executive audience**: Lead with "why now" and "so what." They don't need full background
— they need to understand why you're putting this in front of them today.

**Technical audience**: Lead with scope and methodology. They need to assess your evidence
before they trust your findings. Consider moving methodology earlier in the document.

**Mixed audience**: Follow the standard structure. Executives stop at the executive summary;
technical readers continue into findings. Both audiences see the glossary and context.

**External audience**: Maximize context. External readers have no access to your internal
jargon, org structure, or history. Assume zero prior knowledge.

---

## The context budget

Context should occupy roughly 10–20% of a strategic report. More than 20% signals that
findings and recommendations are under-developed. Less than 10% risks alienating
non-specialist readers.

For a 10-page report: glossary (½ page) + context/background (1 page) + methodology
(½ page) = ~20% context, ~80% analysis and recommendation.
