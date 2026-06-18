# report-progress: RAG System

## Purpose

RAG (Red / Amber / Green) is a standardized status signaling system used in project
management to give stakeholders an immediate, scannable health read at every level —
project, milestone, work item, and blocker resolution. Its value comes entirely from
consistent, shared criteria. If different reporters or readers apply their own mental
models of what "Amber" means, the system breaks.

---

## RAG definitions for progress reports

### 🟢 Green — On track

**Criteria**:
- Scope, schedule, and quality are all within expected parameters
- No known issues that would prevent meeting the next milestone
- Any risks are being monitored; no active mitigation needed

**Common errors**:
- Green is not the default for "nothing on fire right now"
- Green does not mean "good" — it means on-track
- Green requires positive evidence of on-track status, not just absence of problems

---

### 🟡 Amber — At risk

**Criteria**:
- One or more parameters (scope, schedule, quality) degraded or trending negatively
- Known issues present; corrective action is in progress or being planned
- The next milestone may slip unless action is taken
- Confidence in meeting timeline is reduced but not gone

**Amber sub-types** (use in notes column):
- **Behind schedule**: Behind current plan but recovery plan in place
- **At risk**: Currently on plan but risk factors are elevated
- **Under-resourced**: Timeline may slip due to resourcing gap
- **Awaiting decision**: Blocked on a pending decision that hasn't crossed into hard blocker

**When to escalate Amber to Red**:
- Amber that has been open for 2+ status cycles without improvement
- Amber where the mitigation plan has been tried and isn't working
- Amber where the missed deadline would cause downstream cascade failures

---

### 🔴 Red — Off track

**Criteria**:
- A significant milestone has been missed or will be missed without immediate intervention
- A blocker is present with no clear resolution path
- Quality issues are severe enough to require rework that will delay delivery
- Escalation to leadership or external decision-makers is needed

**Red means action is required now**. A Red signal in a progress report with no
corresponding blocker entry, decision request, or path-forward item is incomplete.

**Never assign Red without**:
1. A named blocker or issue description
2. A resolution owner
3. An entry in Next Steps or a decision request

---

## Applying RAG consistently

### At the project level
The project-level RAG reflects the most critical single dimension. If any milestone
is Red, the project is at minimum Amber. If any active blocker has no clear resolution,
the project is likely Red.

Do not average signals. A project with four Green milestones and one Red milestone
is not Amber — it is Red, with four healthy areas noted.

### At the milestone level
Apply criteria to the specific milestone's delivery timeline and quality target.
A milestone due in 4 weeks is Green if it's on track for that date. It may become
Amber in week 3 if a blocker appears.

### At the work item level
Green: being actively worked, on track for estimated completion
Amber: delayed, but owner has a clear path forward
Red: blocked, no path forward without external help

---

## RAG change protocol

When a signal changes:
1. **Document the change** in the report: "Milestone 3 has changed from Green to Amber."
2. **Explain the change**: "Auth migration scope expanded by 2 new requirements (approved
   by [Name])."
3. **Name the consequence**: "This moves the M3 target from 2026-06-01 to 2026-06-15."

Stakeholders notice when a Green milestone silently becomes Red without an explanation.
Communicate signal changes proactively — don't let them discover it.

---

## Common misapplications

**Perpetual Amber**: A project that has been Amber for 3+ reporting periods without
either resolving to Green or escalating to Red. This signals that the issue isn't being
addressed. Perpetual Amber should trigger an honest conversation: is this project
actually Red?

**Optimistic Green**: Green assigned because the reporter wants to avoid difficult
conversations. This destroys trust when the milestone slips. Apply criteria rigorously.

**Punitive Red**: Red assigned not to signal a problem but to draw attention or apply
pressure. Red should describe reality, not be used as a management tool.

**Signal inflation**: If Red is used too frequently, stakeholders stop taking it seriously.
Reserve Red for genuinely critical situations. Amber is the right signal for "things
aren't great."
