# ops-knowledge: Provenance

Every change should record what changed, why, and when. Without provenance, the
knowledge base accumulates anonymous edits that can't be reviewed, audited, or rolled
back. This document specifies the format and conventions.

---

## What provenance answers

Three questions about every change:

1. **What changed?** — content delta, structural change, or both
2. **Why?** — source of the new information, reason for the change
3. **When?** — date (ISO 8601: YYYY-MM-DD)

A fourth question is optional but valuable:

4. **By whom or on whose authority?** — chat session, external doc, user statement,
   AUDIT pass

---

## Provenance formats

### Inline provenance (default for small changes)

A single italicized line appended to the entry:

```markdown
## Rate Limits

The API enforces a rate limit of 100 requests per minute per API key.

_Updated 2026-05-15: limit raised from 60 to 100 req/min per engineering decision._
```

**Use for**: UPSERT, APPEND, RENAME, NORMALIZE — changes that don't fundamentally
restructure the entry.

---

### Provenance block (for significant changes)

A dedicated block at the end of the entry:

```markdown
## Rate Limits

[content]

---
**Provenance**
- 2026-05-15: Updated limit to 100 req/min (user statement, engineering)
- 2026-02-10: Added burst-limit clause (per design doc v3)
- 2025-09-22: Initial entry (from API design spec)
```

**Use for**: entries with significant edit history, ADR-style decisions, or any entry
where the history is part of the value.

---

### Tombstone (for RETRACT)

A short note that replaces the retracted content:

```markdown
## Memcached

_Retracted 2026-05-15: This entry was incorrect; sessions have always been stored
in Redis, never Memcached. See [Redis](#redis)._
```

**Use for**: RETRACT operations where readers might look for the old entry by name.

---

### Supersession pointer (for SUPERSEDE)

A note at the end of the superseded entry pointing forward:

```markdown
## Database (legacy)

[old content]

_Superseded 2026-05-15 by [Database](#database). Reason: migrated to PostgreSQL 16
for JSON_TABLE support._
```

And at the start of the new entry:

```markdown
## Database

[new content]

_Supersedes the 2025 PG 14 selection; see [Database (legacy)](#database-legacy)._
```

---

### Conflict log (for unresolved RECONCILE)

A callout block for conflicts that can't be resolved in the current session:

```markdown
> [!conflict] **Unresolved: Rate limit value**
> - `api.md`: 100 req/min
> - `quickstart.md`: 60 req/min
> - Logged 2026-05-15; awaiting engineering confirmation.
```

---

## Date conventions

- **Always ISO 8601**: `2026-05-15`, never `5/15/26` or `May 15, 2026`
- **Date, not timestamp**: the day-level resolution is sufficient and stable across
  timezones
- **Use the date of the change, not the date of the underlying event**: if the user
  tells you on 2026-05-15 that something changed in 2026-02, the provenance date is
  2026-05-15, and the prose can note "(change effective 2026-02)"

---

## Reason conventions

Be specific. Avoid empty reasons:

| Bad | Good |
|---|---|
| _Updated 2026-05-15._ | _Updated 2026-05-15: rate limit raised to 100 req/min per engineering._ |
| _Cleaned up._ | _Updated 2026-05-15: removed duplicate paragraph; consolidated with parent entry._ |
| _Per user._ | _Updated 2026-05-15: user confirmed PG 16 migration completed in February._ |

Specificity in provenance compounds over time. Future audits depend on it.

---

## What to omit from provenance

- **Internal reasoning**: "I noticed the entry seemed off" — irrelevant to readers
- **Author identity** (in shared projects): unless the project explicitly tracks
  authorship, the reason matters more than the author
- **Speculation about future changes**: provenance is about what just happened, not
  what may happen
- **The full diff**: provenance summarizes; the file's version history (git, etc.) is
  where the diff lives

---

## Provenance vs. version control

If the knowledge base lives in a version-controlled environment (git, etc.), the
commit history captures every change. So why duplicate that in inline provenance?

**Three reasons**:

1. **Provenance lives with the content**. Readers don't run `git log` to understand
   why an entry says what it says.

2. **Granularity differs**. A commit may contain 12 entries' worth of changes;
   provenance is per-entry.

3. **Knowledge bases often don't have version control**. Claude Projects, Cowork
   project files, and similar environments may have no git equivalent. Inline
   provenance is the only audit trail.

When git is available, use it for *what changed at the byte level* and use inline
provenance for *why this entry says what it says*. They are complementary.

---

## Provenance for batch operations

When an operation applies to many entries (e.g., a NORMALIZE pass across 40 entries),
inline provenance on each one creates noise. Use a batch provenance block at the top
or bottom of the file:

```markdown
---

## Batch operation log

- 2026-05-15: NORMALIZE pass — converted 40 endpoint entries to colon-separator
  format. Affected entries: all under `## API Endpoints`.
```

Then inline provenance on individual entries is optional.

---

## Implementation checklist

For every change, before saving:

- [ ] Is there a provenance entry for this change?
- [ ] Is the date ISO 8601?
- [ ] Is the reason specific (not "updated" or "cleaned up")?
- [ ] If this is a chain (SUPERSEDE, RENAME, RECONCILE), is the link to the prior
      version present?
- [ ] If this is a batch operation, is the batch log entry sufficient (or should
      individual entries also carry provenance)?
