# report-state: Health Signals

## The RAG system

RAG (Red / Amber / Green) is the standard health signal vocabulary for state assessments.
It works because it gives readers an immediate, color-coded orientation before they read
the detail. But it only works if the criteria are defined and applied consistently.

**The cardinal rule**: Define your RAG criteria before you apply them. Never apply RAG
signals and then define criteria later (readers will assume their own definitions).

---

## Default RAG criteria

These defaults work for most technical, operational, and organizational assessments.
Override them per-domain when the domain has its own standards, but state the override.

### 🟢 Green — Healthy
**Criteria**:
- Operating within expected parameters for all key dimensions
- No known issues requiring active intervention
- Trend is stable or improving
- Confidence in the assessment is moderate or high

**Common mistakes when assigning Green**:
- Green is not the default for "nothing dramatically wrong"
- Green is not "unknown" — unknown is ⚫
- Green does not mean "improving" — that's the Trend, not the Signal
- Green is not "not Red" — it requires positive evidence of health

---

### 🟡 Amber — At Risk
**Criteria**:
- One or more key dimensions operating outside expected parameters
- Known issues present; monitoring or corrective action is underway
- Performance declining or inconsistent without clear recovery trajectory
- Confidence in the assessment may be low (uncertainty itself warrants Amber)

**Amber sub-types** (use in notes/evidence column, not as separate signals):
- **Degraded**: Performance below expected but stable
- **At risk**: Currently meeting parameters but risk of degradation is real
- **Recovering**: Was Red; improvement underway but not yet Green
- **Uncertain**: Insufficient visibility to assess; more likely negative than positive

---

### 🔴 Red — Critical
**Criteria**:
- Critical failure or blocking issue present
- Requires immediate escalation or intervention
- Impact to other components, users, or delivery already occurring
- No credible recovery plan currently in place

**Red is a call to action**. A Red signal without an action item in the Path Forward
section is incomplete.

**Common mistakes when assigning Red**:
- Do not use Red for "I'm concerned about this" — that's Amber
- Red means something is broken or blocking right now, not "could become a problem"
- A single Red item should not pull the entire report to Red without explanation

---

### ⚫ Unknown — Insufficient information
**Criteria**:
- Insufficient visibility to make a health assessment
- The absence of a signal is itself informative (document it as a gap)

**Never omit Unknown**. If you don't know the state of something in scope, assign ⚫
and document the gap. Pretending you know, or simply leaving things off the matrix,
is worse.

---

## Trend signals

Trend and health signal are independent. A Red item can be trending upward (recovering).
A Green item can be trending downward (early warning sign).

| Symbol | Meaning |
|---|---|
| ↑ | Improving over the assessment period |
| ↔ | Stable — no meaningful change |
| ↓ | Deteriorating over the assessment period |
| — | No trend data (for Unknown items) |

**Velocity** (optional — use in evidence column):
- Fast: change occurring over days to weeks
- Slow: change occurring over months or quarters

---

## Domain-specific criteria overrides

When a domain has its own health standards, use those — but define them explicitly.

**Software reliability example**:
```
Green: P99 latency ≤ 200ms; error rate < 0.1%; uptime > 99.9% over 30 days
Amber: Any metric outside Green range; or known issues being investigated
Red: Error rate > 1%; or P99 > 500ms; or any incident open > 2 hours
```

**Team health example**:
```
Green: Velocity stable; attrition rate < 10% annually; no open critical blockers
Amber: Velocity declining; 1–2 critical blockers; attrition elevated but manageable
Red: Velocity significantly degraded; 3+ critical blockers; key departure risk
```

**Compliance example**:
```
Green: All controls passing; no open audit findings
Amber: 1–2 minor findings open; no critical gaps
Red: Critical findings open; or audit imminently at risk
```

---

## Evidence requirements per signal level

The credibility of a health signal depends entirely on its evidence. Minimum evidence
requirements:

| Signal | Minimum evidence |
|---|---|
| 🟢 Green | Specific metric(s) within expected range + trend confirmation |
| 🟡 Amber | Named issue(s) with observable impact + owner or monitoring status |
| 🔴 Red | Specific failure mode + current impact + escalation status |
| ⚫ Unknown | Statement of what is unknown + collection gap description |

A signal without evidence is an assertion. Assertions are opinions, not assessments.
