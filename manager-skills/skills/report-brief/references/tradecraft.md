# report-brief: CIA Analytical Tradecraft

## What is analytical tradecraft?

Analytical tradecraft is the set of practices that intelligence analysts use to produce
assessments that are honest, evidence-based, calibrated, and useful to decision-makers.
The CIA formalized many of these practices in the "Tradecraft Primer" and Richards Heuer's
"Psychology of Intelligence Analysis." The principles are domain-agnostic and apply to
any domain where evidence is incomplete and uncertainty must be communicated clearly.

---

## Core principles

### 1. Bottom Line Up Front (BLUF)
Intelligence consumers are busy decision-makers. The first thing they read must be the
key assessment. Supporting evidence follows. This is the reverse of academic writing,
where conclusions come last.

**In practice**: Write the BLUF before you research the body. Revise it after. If you
can't write a BLUF before researching, you don't yet know what question you're answering.

---

### 2. Key judgments
Key judgments are the 3–7 most important assessments in the brief. They are:
- **Specific**: Not "AI is evolving rapidly" but "We assess that three competing LLM vendors
  will reach feature parity with GPT-4o by Q3 2026."
- **Confidence-annotated**: Every key judgment carries a confidence level.
- **Ordered**: Most important judgment first.
- **Change-flagged**: If a judgment has changed since the last assessment, say so.

---

### 3. Confidence levels
Confidence levels are not hedging — they are data. They tell the reader how much weight
to give a judgment when making decisions. See `confidence-lexicon.md` for full vocabulary.

**The three-tier system**:
- **High confidence**: Multiple independent sources corroborate; strong logical chain
- **Moderate confidence**: Credible evidence with gaps; or single-source without corroboration
- **Low confidence**: Indirect evidence; significant inferential leaps; single source unreliable

**Never omit a confidence level**. A judgment without a confidence level forces the reader
to guess — and they will guess wrong.

---

### 4. Source discipline
Sources are not all equal. The reliability of a source must be communicated to the reader.

**Source tiers**:
| Tier | Examples | Use |
|---|---|---|
| Primary | First-party data, direct observation, primary documents | Full weight |
| Secondary | Industry reports, reviewed research, expert synthesis | Weight with noted caveats |
| Estimated | Extrapolation, inference, analogy | Mark clearly; low confidence default |

**Source assessment**: For each major claim, note the source tier. If a claim rests
on a single secondary source, say so — the reader can evaluate accordingly.

---

### 5. Structured Analytic Techniques (SATs)

SATs are formal methods for overcoming cognitive biases in analysis. Two are most
applicable to domain knowledge briefs:

#### Analysis of Competing Hypotheses (ACH)
**When to use**: When the evidence supports more than one interpretation.
**How**: List all plausible hypotheses. For each piece of evidence, ask: "Is this
consistent or inconsistent with each hypothesis?" The surviving hypothesis is the
one least contradicted by evidence — not most supported.

**Common ACH error**: Selecting the hypothesis with the most supporting evidence
rather than eliminating hypotheses via contradicting evidence.

#### Key assumptions check
**When to use**: On any brief where conclusions depend on unstated premises.
**How**: List every assumption the analysis depends on. For each: "How confident are
we this is true? What happens to the conclusion if this assumption is wrong?"

---

### 6. Intelligence gaps
Gaps are things you don't know that matter for the assessment. They are not admissions
of failure — they are guidance to the reader and the next analyst.

**Gap format**:
> "We do not know [X]. If [X] were true, it would [change/confirm/overturn] our assessment
> of [Y]. This gap could be filled by [collection method or research action]."

**Gap severity tiers**:
- **Critical**: If the unknown fact changes the key judgment, it's a critical gap.
- **Significant**: Changes confidence level but not the direction of the judgment.
- **Informational**: Would be useful but doesn't affect the key judgment.

---

### 7. Cognitive bias awareness

The most common biases in rapid briefing contexts:

**Anchoring**: The first number or assessment encountered pulls subsequent estimates
toward it. Mitigation: Form your initial assessment independently before researching.

**Confirmation bias**: Seeking evidence that supports an existing view. Mitigation:
Actively search for disconfirming evidence; run ACH.

**Availability bias**: Overweighting recent or easily recalled events. Mitigation:
Explicitly check whether the evidence represents a pattern or an outlier.

**Mirror imaging**: Assuming others think like you do. Mitigation: Explicitly ask
"how might this look from a different vantage point?"

---

## The analytic standard

A brief that meets the analytic standard:
1. States the key judgment with confidence level in the first paragraph
2. Provides the evidence, including contradicting evidence
3. Addresses alternative hypotheses
4. Names intelligence gaps explicitly
5. Derives implications specific to the reader's context
6. Does not overclaim certainty or underclaim in false modesty

The standard is violated when:
- Confidence language is omitted to appear more decisive
- Contradicting evidence is footnoted or omitted
- Gaps are not named (they exist; naming them is honest)
- Implications are generic rather than tailored to the reader
