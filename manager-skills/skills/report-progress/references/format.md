# report-progress: Format Guide

## Section-by-section guidance

### 1. Header

```
PROJECT: [Name]
REPORT PERIOD: [Week of YYYY-MM-DD | Sprint N | Q[N] YYYY]
AUTHOR: [Name or role]
DATE: [YYYY-MM-DD]
DISTRIBUTION: [Recipients]
OVERALL STATUS: [🟢 GREEN | 🟡 AMBER | 🔴 RED] — [1-sentence rationale]
```

The overall status line is the first thing stakeholders see. Make the rationale specific.

Bad: `🟡 AMBER — Some concerns`
Good: `🟡 AMBER — Auth migration is 2 weeks behind schedule; mitigation plan in place`

---

### 2. Executive Summary (3–6 bullets)

```
• Completed: [What was accomplished this period — specific, not "made progress"]
• Status: [Overall health with brief rationale]  
• Top blocker: [Most critical blocker and owner, if any]
• Next milestone: [Name] — [Target date]
• Risk: [Most significant open risk, if any]
```

If there are no blockers or risks, say so explicitly: "No active blockers." This
is reassuring — omitting it makes readers wonder.

---

### 3. Scope Summary

Three sub-elements:

**Current agreed scope** (bullet list or 1–2 sentences):
What is in scope for this project/sprint/initiative as currently defined.

**Scope changes this period** (table, only if changes occurred):
| Change | Type | Approved by | Impact |
|---|---|---|---|
| [Item added/removed] | Addition/Removal/Deferral | [Name] | [Schedule/cost impact] |

If no scope changes: "No scope changes this period."

**Explicit out-of-scope** (only if confusion arose this period):
"[Item X] was raised as a potential addition and is explicitly out of scope pending [decision]."

---

### 4. Milestone Tracker

| Milestone | Target date | Revised date | Status | Notes |
|---|---|---|---|---|
| [Name] | [Original date] | [If changed] | 🟢/🟡/🔴 | [Key info] |

- List all milestones for the project, not just current-period ones
- Highlight any date changes in the "Revised date" column
- Flag milestones that are at risk even if not yet late

---

### 5. Work Completed This Period

Punch list format. Be specific — "completed login flow" not "made progress on auth."

```
✅ [Item] — [Owner] [date completed if notable]
✅ [Item] — [Owner]
```

Flag items that closed blockers or risks:
```
✅ [Item] — [Owner] ← Resolves Blocker #3
```

---

### 6. Work In Progress

| Item | Owner | Est. completion | Status | Notes |
|---|---|---|---|---|
| [Item] | [Name] | [Date] | 🟢/🟡/🔴 | [Current state] |

Status per item:
- Green: On track for stated completion date
- Amber: At risk; may slip or needs additional support
- Red: Behind; will slip without intervention

---

### 7. Blockers

**Definition**: A blocker is a specific item that is preventing another item from
proceeding. Slow items are not blockers. Items you'd like help with are not blockers.

| # | Blocker | Impact | Owner | Date raised | Needed by |
|---|---|---|---|---|---|
| B1 | [Specific blocking item] | [What is blocked] | [Owner] | [Date] | [Deadline] |

Every blocker entry must answer: who is responsible for resolving this?

"Waiting on approvals" is not a blocker entry. "Waiting on [Name] to approve [specific
decision] — blocking [X] — needed by [date]" is a blocker entry.

---

### 8. Risks

| # | Risk | Likelihood | Impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|
| R1 | [Risk statement] | H/M/L | H/M/L | [Action being taken] | [Owner] | Open/Monitoring/Mitigated |

Likelihood × Impact:
- High × High = Escalate now
- High × Medium or Medium × High = Active mitigation required
- Others = Monitor

Risk vs. issue distinction:
- **Risk**: Something that might happen (future-tense)
- **Issue / Blocker**: Something that has happened (present-tense, use Blockers section)

---

### 9. Decisions Log

| Decision | Outcome | Owner | Date | Impact |
|---|---|---|---|---|
| [Decision needed/made] | [Outcome or "Pending"] | [Decision owner] | [Date] | [What it unblocked] |

Pending decisions: highlight these — they often become blockers if not resolved.

---

### 10. Next Steps

Ordered list. Every item must have an owner and a date.

```
1. [Action] — [Owner] — by [date]
2. [Action] — [Owner] — by [date]
   ↳ Depends on: [Item #1 or Blocker B1]
```

Flag dependencies between next steps where they exist.

---

### 11. Metrics (optional)

Include when the project has established metrics that stakeholders track.

| Metric | Current | Prior period | Target | Trend |
|---|---|---|---|---|
| [Metric] | [Value] | [Prior value] | [Target] | ↑/↔/↓ |

---

## Length norms

| Report type | Length |
|---|---|
| Weekly team update | 1–2 pages |
| Sprint review | 2–3 pages |
| Monthly executive status | 2–4 pages |
| Quarterly project review | 4–8 pages |

Tables dominate — prose is minimal. A stakeholder should be able to scan this in
3–5 minutes and know exactly where things stand.
