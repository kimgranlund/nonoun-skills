---
name: safety-verifier
description: Reason about and verify blast radius, reversibility, and friction for every destructive or high-consequence action a UI exposes — undo over confirm, type-to-confirm for irreversible, bulk preview/dry-run, audit-trail UX, recall windows, re-auth, scoped permissions, and destructive-default posture. Use when checking or auditing destructive actions that are under-specified, when confirm dialogs have proliferated (confirmation fatigue), or when undo/recovery is missing. NOT for text/background contrast, palette, or color-blind safety (color-verifier); NOT for focus order, keyboard nav, hit-targets, or focus rings (focus-verifier); NOT for RTL/bidi, locale Intl formatting, or text-expansion (i18n-verifier); NOT for loading skeleton/spinner, CLS, or perceived-latency budgets (perf-verifier); NOT for color-space theory or palette math (color-science); NOT for prompt-injection/agent security or back-end authz model design; NOT for building a confirm-dialog or undo-toast component (component-decomposer).
---

# safety-verifier

Reasoning skill that owns the *trust* layer of ui-dev. Every action has a blast radius and a reversibility; this skill names those primitives and emits the invariants every destructive or high-consequence surface must satisfy. Upstream: UISchema, `ui-compose-interaction` (destructive confirmation in state transitions), `ui-compose-voice` (destructive copy). Downstream: component libraries, `ui-audit-quality`.


## Invocation

This is a **constraint** decomposition skill. The user needs friction rules for destructive or high-consequence actions. Decompose: (1) map blast radius, (2) determine reversibility, (3) choose undo vs confirm vs type-to-confirm, (4) specify audit trail surface.

### Step 1 — Ingestion

Classify the ask surface:
- "Destructive actions under-specified" → enumerate every high-consequence action
- "Too many confirm dialogs" → replace with undo where reversible
- "Undo missing" → audit action set for reversibility gaps
- "Irreversible needs more friction" → type-to-confirm escalation ladder

### Step 2 — Decomposition

| Sub-ask | Rule |
|---|---|
| Blast radius mapping | Data scope (row, user, org, account) × recoverability (restorable from backup, re-creatable, permanent) |
| Undo over confirm | Default to undo for any reversible action within 30 seconds |
| Type-to-confirm | Name the object (best) → scoped phrase → "DELETE" (worst) → none for truly irreversible |
| Audit trail | Every destructive action emits a structured event (who, what, when, before-state, after-state) |
| Scoped permissions | Check permission at point of action, not just gate; time-bound elevation for sensitive ops |
| Tense discipline | Present-continuous during ("Deleting…"), past after success ("Deleted"), past+reason on failure |

### Step 3 — Execution routing

Every action with blast radius ≥ "user-visible data loss" must have a documented recovery path or an explicit "not recoverable" flag. `ui-compose-interaction` consumes the safety constraints as state-machine transitions (pending → undoable → committed). The audit surface is declarative: events logged, not behavior implemented.


## When to use

- Destructive confirmations have proliferated on low-stakes actions (confirmation fatigue).
- A destructive action lacks recovery (delete without undo, send without recall window).
- Bulk actions happen silently — no preview, no count, no dry-run.
- Audit-trail UX is missing — users can't see what they changed or who did it.
- Permissions are implicit and changes silently succeed or silently fail.
- A new high-stakes feature is being designed and the team wants blast-radius analysis *before* UI.

## When NOT to use

- Routine single-user actions with reversible state — undo is sufficient, this skill is overkill.
- Back-end authorization model design — this skill consumes the model, does not define it.
- Legal / compliance disclosures authoring — owned by legal; this skill constrains *presentation*.

## Rate-limiting factor

**Every action has a (blast radius, reversibility) coordinate.** The irreducible operation is: before attaching a UI affordance to an action, locate the action on the blast/reversibility plane. UI treatment (confirmation, type-to-confirm, undo window, audit event, permission gate) is a function of coordinate. A UI that treats "delete one of my drafts" the same as "delete the org's customer database" is either over-confirming (fatigue) or under-protecting (data loss).

## First principles

1. **Blast radius is a number, not an adjective.** Count the affected entities and observers. `self, 1` ≠ `org, 10k`.
2. **Reversibility is a duration, not a boolean.** `reversible within 30 days`, `reversible within session`, `irreversible` — each drives different UX.
3. **Undo > confirm.** For reversible low-stakes actions, ship undo instead of a confirmation dialog.
4. **Type-to-confirm for irreversible, high-blast actions.** The friction must match the blast radius.
5. **Preview before bulk.** Every bulk action shows the count and a sampled preview before executing.
6. **Dry-run when possible.** For actions over APIs, offer a dry-run that reports what *would* happen.
7. **Audit events are user-facing.** Users see what they changed, when, and can export the log.
8. **Permission failures explain.** Silent failure refused; permission errors name what's missing and how to request it.
9. **Sensitive-action re-auth.** High-blast actions re-prompt for authentication within a time window.
10. **Destructive defaults are refused.** The default button in a destructive confirmation is Cancel.

## Procedure

### Step 1 — Enumerate actions
List every action the product exposes. For each, record:

```ts
type Action = {
  id: string;
  verb: string;                        // create / update / delete / send / publish / invite / revoke
  blastRadius: {
    scope: "self" | "workspace" | "org" | "public";
    count: number | "1" | "N" | "all"; // how many entities
    observers: number;                 // humans who will notice
  };
  reversibility: "instant" | "session" | "minutes" | "days" | "irreversible";
  sensitivity: "low" | "medium" | "high" | "critical";
};
```

### Step 2 — Place on the blast/reversibility plane
Classify each action into one of the treatments:

| blast × reversibility | treatment |
|---|---|
| low × instant        | silent action + undo toast |
| low × session        | silent action + undo toast (session-scoped) |
| medium × instant     | undo + toast (confirm-on-modify-of-shared-item only) |
| medium × days        | undo; no confirm |
| medium × irreversible| confirm with named consequence |
| high × days          | confirm with named consequence + audit event |
| high × irreversible  | type-to-confirm + re-auth + audit event |
| critical × any       | type-to-confirm + re-auth + 2-person approval + audit event |

### Step 3 — Design the friction
For each treatment, wire the specific friction:

- **Undo toast**: ≥ 6s visible, undo CTA focusable, `aria-live="polite"`. For destructive sessions (bulk delete), extend to 12–30s.
- **Confirm dialog**: names the consequence; destructive CTA is *not* the default; destructive styling; dismissable by Escape.
- **Type-to-confirm**: user types the resource name exactly; CTA disabled until match. Label shows the resource name in a `<code>` element.
- **Re-auth**: password / WebAuthn / SSO re-prompt; valid for ≤ 15 minutes within the session.
- **2-person approval**: initiator proposes; second approver resolves; both are recorded.

### Step 4 — Preview and dry-run
For any action affecting > 1 entity:

- Render a count ("Delete 42 items").
- Show a sampled preview of up to 10 affected entities.
- Where APIs allow, offer a "Dry run" that reports would-be changes without executing.

### Step 5 — Audit events
Every action at `high` blast or `irreversible` reversibility emits a user-visible audit event:

```ts
type AuditEvent = {
  id: string;
  actor: { id: string; displayName: string };
  verb: string;
  target: { type: string; id: string; displayName: string };
  at: string;                    // ISO timestamp
  before?: unknown;              // redacted where sensitive
  after?: unknown;
  recoverable: boolean;
  recoveryDeadline?: string;     // ISO timestamp; null if irreversible
};
```

Users can filter, search, and export the log.

### Step 6 — Permission UX
When an action is forbidden:

- Render a permission error with `subject + diagnosis + remedy` (see `ui-compose-voice`).
- Name the missing permission, the role that holds it, and a request-access CTA.
- Never silently disable an affordance without explanation.

### Step 7 — Default posture
Every destructive confirmation:

- Default focus: Cancel (not the destructive action).
- Destructive button uses semantic danger color token + a non-color cue (weight / icon).
- Escape always closes the dialog without executing.
- Enter does not execute unless focused on the destructive CTA intentionally.

### Step 8 — Declare recall windows
For actions with a recall window (send, publish, invite):

- Render a transient countdown ("Undo send (10s)").
- Allow recall without re-confirmation.
- Declare the window in seconds per action type.

### Step 9 — Emit the SafetySchema

```ts
type SafetySchema = {
  actions: Action[];
  treatments: Record<ActionId, Treatment>;
  recallWindows: Record<ActionId, number>;        // seconds
  reauthPolicy: { requiredFor: ActionId[]; windowMinutes: number };
  auditEvents: { emittedFor: ActionId[]; retentionDays: number; exportFormat: "csv" | "json" };
};
```

## Invariants

1. Every action has a (blastRadius, reversibility, sensitivity) triple. Unclassified actions refused.
2. Reversible low-stakes actions use undo — not confirmation.
3. Irreversible high-blast actions use type-to-confirm + re-auth + audit event.
4. Bulk actions preview the count and sample before execution.
5. Destructive dialogs default focus to Cancel and name the consequence.
6. Permission failures explain the missing role and a remedy.
7. Every `high` blast or `irreversible` action emits a user-visible audit event.
8. Recall-window countdowns are non-blocking and cancelable.
9. Sensitive-action re-auth is scoped to a declared time window.
10. Destructive copy resolves via `destructive-confirmation-*` slots (no literal strings).


- **INV-SAF-001** — Every proof cites specific schema paths or CSS rules it evaluates (enforcement: convention)
- **INV-SAF-002** — Remediation suggestions are scoped to the schema/artifact that can fix them (enforcement: convention)

## Typed Interface

**Domain:** `ui-design`

**Consumes:** Relevant schemas and artifacts.

**Produces:** `SafetyAndDestructiveAffordancesProof` — constraint-satisfaction proof or violation report.

**Invariants:** Evaluations cite schema paths or CSS rules; remediation suggestions scoped to fixable artifact.

**Downstream:** `ui-audit-quality`.

## Anti-patterns this skill refuses

- Confirm dialog on every mutation, including harmless edits — confirmation fatigue.
- Silent irreversible delete ("Delete", no confirm, no undo).
- Destructive dialog with Delete as default-focused button.
- "Are you sure?" as a universal confirm prompt — names neither consequence nor resource.
- Bulk delete without count + preview — users can't tell what they're doing.
- Silent permission failure (disabled button with no tooltip / error).
- Undo toast that dismisses in < 3s — unusable on touch / screen-reader.
- Audit events stored but never surfaced to the user.
- Type-to-confirm using the user's *email* (trivially known) instead of the resource name.
- Re-auth scoped to the entire session (defeats the purpose).
- Stacked confirmations ("Are you sure?" → "Are you really sure?") — fix the default.
- Destructive copy in `action-label` slot without a `destructive-confirmation-*` wrapper.

## Handoff

- `ui-compose-interaction` consumes destructive-back and optimistic-rollback semantics; surfaces the state machine for type-to-confirm.
- `ui-compose-voice` supplies `destructive-confirmation-{title,body,cta}` and `inline-error-banner` slots; enforces "name the consequence".
- `focus-verifier` enforces Cancel-as-default-focus and Escape handling.
- `ui-compose-forms` consumes type-to-confirm as a FieldContract variant.
- `ui-compose-nav` consumes destructive-back intercepts for unsaved-work flows.
- `ui-audit-quality` runs safety checks: blast/reversibility coverage, undo over confirm, type-to-confirm for irreversible, preview on bulk, default-Cancel, audit-event visibility, permission UX.

## Bundled reference files

- `blast-reversibility/matrix.json` — the canonical (blast × reversibility) → treatment table.
- `friction/recipes.json` — undo toast, confirm, type-to-confirm, re-auth, 2-person approval recipes.
- `recall/windows.json` — canonical recall-window durations per action type (send, publish, invite, etc.).
- `audit/event-schema.json` — AuditEvent schema and user-visibility requirements.
- `permissions/error-ux.json` — permission-failure copy + affordance pattern.
- `defaults/confirm-posture.json` — destructive-confirm default posture (focus, keyboard, styling).
