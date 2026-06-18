# report-progress: Risk Register

## Risk vs. issue distinction

**Risk**: A future uncertainty that may negatively affect the project if it materializes.
Risk management is forward-looking. (Example: "If the vendor API changes in Q3, we will
need to rebuild the integration.")

**Issue / Blocker**: A present reality already affecting the project. Issues go in the
Blockers section, not the risk register. (Example: "The vendor API changed last week;
the integration is broken.")

A risk that has materialized becomes an issue. Move it to Blockers when it does.

---

## Risk register format

| # | Risk | Likelihood | Impact | Score | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|
| R1 | [Risk statement] | H/M/L | H/M/L | [H×I] | [Action being taken] | [Owner] | [Status] |

**Risk statement format**: "[If/When condition], then [negative consequence]."
> "If Q3 infrastructure migration is delayed, then our October launch will be blocked
> by unresolved dependency on the new data layer."

---

## Likelihood and impact

Rate each dimension independently as High / Medium / Low.

### Likelihood
| Level | Meaning |
|---|---|
| **High** | More likely than not to materialize this project cycle |
| **Medium** | Real possibility; monitoring warranted |
| **Low** | Possible but unlikely; worth noting |

### Impact
| Level | Meaning |
|---|---|
| **High** | Causes milestone miss, budget overrun >10%, or significant quality degradation |
| **Medium** | Delays delivery, reduces scope, or requires unplanned work |
| **Low** | Manageable; minor scope or timeline adjustment only |

---

## Risk score matrix

Use this to prioritize mitigation effort:

|  | **High impact** | **Med impact** | **Low impact** |
|---|---|---|---|
| **High likelihood** | 🔴 Escalate | 🟡 Active mitigation | 🟡 Monitor closely |
| **Med likelihood** | 🟡 Active mitigation | 🟡 Monitor closely | 🟢 Monitor |
| **Low likelihood** | 🟡 Monitor closely | 🟢 Monitor | 🟢 Log only |

**Escalate**: Needs leadership visibility; may require resource or timeline decision
**Active mitigation**: Owner has a specific mitigation action in progress
**Monitor closely**: Check status each reporting period; ready to escalate
**Monitor**: Review each period; no action needed now
**Log only**: Noted for record; no action expected

---

## Mitigation strategies

When documenting mitigations, be specific. "Monitoring the situation" is not mitigation.

**Avoidance**: Eliminate the risk by changing the plan.
> "We will not use the vendor API for the critical path; we'll build an internal
> abstraction layer that can swap the underlying vendor."

**Reduction**: Reduce likelihood or impact.
> "We've booked weekly syncs with the vendor team to surface API changes 4 weeks early
> rather than learning at integration time."

**Transfer**: Move the risk to another party.
> "We've added an SLA to the vendor contract that compensates us for integration delays
> caused by undocumented API changes."

**Acceptance**: Acknowledge the risk and accept the consequences if it materializes.
> "We accept the risk of minor API changes and have budgeted 2 sprints of rework
> contingency in the Q4 plan."

**Contingency**: Plan for the risk if it materializes.
> "If the vendor API changes, we have a fallback to the previous API version available
> for 90 days. Contingency plan is documented in [reference]."

---

## Risk register maintenance

Risks should be reviewed every reporting period:

| Status | Meaning |
|---|---|
| **Open** | Risk is present; monitoring or mitigation active |
| **Monitoring** | Risk acknowledged; no active mitigation yet; watch for triggers |
| **Mitigated** | Mitigation is in place and working; risk level reduced |
| **Closed** | Risk has passed (event window over) or been fully eliminated |
| **Materialized** | Risk occurred; move to Blockers section |

When a risk moves to Closed or Materialized:
- Note the date and outcome in the register
- Keep the closed row for one additional period for the record
- Remove after that

---

## Common risk categories

For software/product projects:

| Category | Common risks |
|---|---|
| **Schedule** | Scope creep, under-estimation, dependency delay |
| **Scope** | Requirements change, stakeholder expectation drift |
| **Technical** | Architecture assumptions invalid, integration failures, tooling instability |
| **Resource** | Key person risk, attrition, hiring delay |
| **External** | Vendor changes, regulatory change, market shift |
| **Quality** | Insufficient testing time, debt accumulation, rework required |

Ensure at least one risk in the register comes from each high-likelihood category
for the project at hand.
