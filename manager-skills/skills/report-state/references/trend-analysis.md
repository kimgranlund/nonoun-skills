# report-state: Trend Analysis

## What makes trend analysis valuable

A snapshot tells you where you are. Trend tells you where you're going. The combination
is what enables decisions. A system with degrading trend should prompt different action
than an identical system with improving trend — even if both are currently Amber.

The State of the Union report must answer: "Is the trajectory positive, stable, or
negative? How fast is it changing? What signals predict near-term change?"

---

## The three questions of trend analysis

### 1. Direction
Which way is this dimension moving — improving, stable, or deteriorating?

Compare the current period to the prior period. If this is the first assessment,
name what data you can use to infer recent trajectory (e.g., "incident rate over
the past 6 months has declined from 8/month to 3/month").

**Direction vocabulary**:
- **Improving (↑)**: Measurable positive change across the assessment period
- **Stable (↔)**: Within normal variation; no meaningful directional change
- **Deteriorating (↓)**: Measurable negative change across the assessment period

If a metric is too noisy to assign direction reliably, say so and assign ↔ with a
note — don't manufacture a direction you can't support.

---

### 2. Velocity
How fast is the change happening?

**Fast**: Changes are visible week-over-week or sprint-over-sprint. Requires attention
now; the situation may look materially different by the next assessment.

**Slow**: Changes visible quarter-over-quarter or year-over-year. The current assessment
is likely to hold until the next scheduled review.

Velocity matters for prioritization. A slow-deteriorating Green item may not need
immediate action. A fast-deteriorating Amber item may need escalation today.

---

### 3. Leading indicators
What signals typically precede a change in this dimension?

A leading indicator is observable now and predicts future state. Not all dimensions
have known leading indicators, but when they exist, they should be captured — they allow
for early intervention.

**Format**:
```
Leading indicator: [Observable metric or signal]
Historical relationship: [Has preceded X in N of M prior occurrences / observations]
Current reading: [What is this indicator showing right now]
Implication: [If the indicator is correct, we expect Y by Z date]
```

Example:
```
Leading indicator: API error rate (currently 0.3%)
Historical relationship: Error rate >0.5% preceded 2 of 3 reliability incidents in 2025
Current reading: 0.3% — within acceptable range but elevated from 0.1% baseline
Implication: Monitor weekly; if error rate crosses 0.5%, begin incident pre-flight
```

---

## Trend patterns and what they mean

### Improving trajectory from Red or Amber
Positive sign — but verify: is improvement due to corrective action (sustainable) or
external factors (may revert)? Name the cause of improvement.

### Stable trajectory at Green
Healthy. Note the factors keeping it stable — if those factors change, stability may break.

### Stable trajectory at Amber or Red
Most concerning pattern: stuck in a degraded state. Signals that monitoring is happening
but corrective action is not working (or not yet started).

### Deteriorating trajectory from Green
Early warning. Green with ↓ trend should be watched closely and may warrant Amber
treatment at the next assessment cycle.

### Fast-deteriorating trajectory at Amber
Approaching Red. If velocity is high, the next assessment may find this item Red. Consider
accelerating the assessment cycle for this dimension.

---

## Comparing to prior assessments

When a prior assessment exists, the trend section should include a comparison table:

| Dimension | Prior signal | Current signal | Change | Explanation |
|---|---|---|---|---|
| API reliability | 🟢 ↑ | 🟡 ↔ | Downgraded | Incident rate increased Q1 |
| Team velocity | 🟡 ↓ | 🟡 ↑ | Stable signal, improving trend | Sprint throughput recovering |

Key patterns to call out explicitly:
- **New Red items**: "X has degraded from Amber to Red since the last assessment."
- **Resolved items**: "Y has improved from Red to Green."
- **Persistent Amber**: "Z has been Amber for [N] assessments without improvement."
  Persistent Amber without resolution is a risk pattern that warrants escalation.

---

## Trend analysis for a first assessment

When there is no prior assessment to compare against, derive trend from available history:

1. **Metric time series**: If metrics exist (e.g., error rates, velocity points, NPS),
   plot them. The slope is the trend.

2. **Incident history**: If incidents are logged, count them by period. Increasing
   frequency = deteriorating.

3. **Qualitative trajectory**: If quantitative history is unavailable, interview or
   document stakeholder observations: "Was this better or worse 6 months ago? 1 year ago?"
   Qualitative trend is weaker evidence — note it as such.

4. **No trend data**: If genuinely no trend data exists, assign ↔ with a note:
   "Insufficient history to assess trend; baseline established in this assessment."
