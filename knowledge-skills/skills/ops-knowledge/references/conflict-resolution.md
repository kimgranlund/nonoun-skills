# ops-knowledge: Conflict Resolution

When two sources disagree — file vs. file, chat vs. file, two entries in the same
file — auto-resolution is dangerous. This document specifies how to detect, classify,
and surface conflicts so the user always makes the final call.

---

## Conflict types

### Type 1: Direct contradiction

Two statements about the same fact, with incompatible content.

**Example**:
- `quickstart.md`: "Rate limit: 60 req/min"
- `limits.md`: "Rate limit: 100 req/min"

**Resolution path**: RECONCILE — surface both with their provenance; user picks
canonical.

---

### Type 2: Stale vs. current

One statement is correct as of an earlier point in time; another reflects the current
state.

**Example**:
- `api.md` (last updated 2025-03): "Database: PostgreSQL 14"
- User in chat: "We migrated to PG 16 in February."

**Resolution path**: If both are factual at their time, use SUPERSEDE (preserve
history). If the older one should not influence future readers, use UPSERT + provenance
note.

---

### Type 3: Scope mismatch (false conflict)

Two statements appear to conflict but cover different scopes.

**Example**:
- `api.md`: "Rate limit: 100 req/min"
- `internal-services.md`: "No rate limit for internal services"

**Resolution path**: Not a real conflict. Use APPEND on the first entry to add the
scope qualifier, or add a clarifying cross-reference.

---

### Type 4: Granularity mismatch

Two statements at different levels of specificity, where one is correct and the other
is technically wrong but practically useful.

**Example**:
- High-level docs: "We support OAuth 2.0"
- Detail docs: "We support OAuth 2.0 Authorization Code + PKCE; client credentials
  are deprecated as of 2026-Q1"

**Resolution path**: Not necessarily a conflict — the high-level statement is still
true. But verify the high-level statement doesn't mislead by omission. Consider
APPEND on the high-level for a "see [details]" pointer.

---

### Type 5: Conflicting interpretations

Two entries describe the same thing but use different mental models or framings.

**Example**:
- One entry treats the cache as "per-user"
- Another entry treats it as "per-session" (which is per-user-per-tab)

**Resolution path**: Often the deepest conflict — the framings shape what readers
think the system does. RECONCILE with a user discussion about which framing is
canonical, then NORMALIZE all references.

---

## The conflict-resolution protocol

### Step 1: Detect

Conflicts are detected during:
- UPSERT: when the new content contradicts the existing entry
- AUDIT: as a dedicated dimension
- RECONCILE: explicit detection on user request
- Cross-file search before any operation

### Step 2: Classify

Use the typology above. The type drives the resolution approach.

### Step 3: Surface

Present the conflict to the user with:
1. Both versions, verbatim, with their source (file + entry)
2. The provenance of each (date, prior changes if available)
3. Your classification (Type 1–5)
4. Your proposed resolution (RECONCILE, SUPERSEDE, APPEND, NORMALIZE)
5. Any third-party signals if available (e.g., external doc that supports one side)

**Never** present a conflict with a hidden preference. Show both sides equally.

### Step 4: Wait for the user

Do not proceed until the user picks. Acceptable user responses:
- "Use [A]" — apply RECONCILE or UPSERT with A as canonical
- "Use [B]" — same with B
- "Both are right" — likely Type 3 (scope mismatch); use APPEND to add qualifiers
- "Neither" — gather more information from the user
- "Defer" — log the conflict in provenance and move on without resolving

### Step 5: Apply + provenance

Whichever resolution wins, record:
- What the conflict was
- What was chosen
- Why (user's stated reason, or "user choice" if unstated)

Future audits can then revisit the decision with context.

---

## When conflicts cannot be resolved in the current session

If the user can't decide right now, log the conflict explicitly:

```markdown
> [!conflict] **Unresolved conflict** (logged 2026-05-15)
> - `api.md` says: Rate limit 100 req/min
> - `quickstart.md` says: Rate limit 60 req/min
> - Awaiting confirmation from engineering team.
```

This is preferable to silent state where two sources disagree without acknowledgment.
The next audit will surface it again until resolved.

---

## Chat-vs-file conflicts

A specific high-frequency case: the user makes a statement in chat that contradicts
the persisted knowledge base.

**Default treatment**: The file is canon until updated. Surface the conflict before
trusting the chat statement.

**Sample prompt**:
> "You mentioned the rate limit is 100 req/min, but `api.md` (last updated 2026-Q1)
> says 60 req/min. Has the limit been updated, or is the file out of date? I can
> RECONCILE either direction."

**Why this matters**: Without this check, every chat utterance silently overwrites
the file, and the knowledge base becomes a transcription of the latest conversation
rather than a curated record.

---

## Conflict-resolution anti-patterns

- **Picking the newer source automatically**: newer ≠ correct. The user just typed
  it doesn't mean the file is wrong.
- **Picking the more specific source automatically**: specificity ≠ correctness.
- **Picking the source with more provenance entries**: a heavily-edited entry isn't
  necessarily right.
- **Resolving by majority vote across sources**: if three files agree and one
  disagrees, the one may be the correct one. Always surface.
- **Marking a conflict as resolved without changing anything**: if no operation was
  applied, the conflict is still present. Either change something or log it as
  unresolved.

---

## Chains and cascades

Resolving one conflict often surfaces others:

1. RECONCILE the rate-limit conflict → 100 req/min wins
2. Quickstart now says 60 req/min, which is wrong → UPSERT or RETRACT
3. Search for other references to "60 req/min" → find 3 more
4. Decide: are they stale (UPSERT to 100), or about a different scope (qualify)?

Plan cascades explicitly. Don't apply a single RECONCILE and walk away if you've
created downstream conflicts.
