# ops-knowledge: Operation Catalog

Full semantics, edge cases, and worked examples for each operation in the vocabulary.

---

## UPSERT

**Definition**: Update an entry if it exists; insert it if it doesn't.

**Idempotent**: Yes — running UPSERT with the same payload twice produces the same
state. This makes it the safest default for "I want this fact represented in the file."

**When to use**:
- A topic exists and new information about it has emerged
- A topic may exist (uncertain) and you want to ensure it's represented
- The user says "make sure X is in the file" without saying whether X is new or update

**Identity strategy required**: UPSERT depends entirely on correctly identifying whether
the entry already exists. See `matching-strategies.md`.

**Worked example**:

> User: "Our API rate limit is now 100 req/min, not 60."
>
> 1. Search the file for an existing rate-limit entry.
> 2. Found: "Rate limit: 60 req/min (as of 2025-Q3)"
> 3. UPSERT replaces with: "Rate limit: 100 req/min (updated 2026-05-15)"
> 4. Provenance: "Updated per user statement 2026-05-15; prior value 60 req/min."

**Edge case — ambiguous identity**: If two entries plausibly match (e.g., one in
`api.md` and one in `limits.md`), do not UPSERT both. Surface the ambiguity:
> "I found rate-limit entries in both `api.md` and `limits.md`. Which is canonical?"

**Edge case — partial match**: If the existing entry covers a related but distinct
fact (e.g., entry is about "burst rate limit" not "sustained rate limit"), prefer
APPEND or insert as a sibling, not UPSERT.

---

## APPEND

**Definition**: Add new content to an existing entry, preserving prior content.

**Idempotent**: No — appending the same content twice creates duplication. Check
before appending.

**When to use**:
- Additive update: new sub-point, new example, new caveat
- The new content does not contradict prior content
- The existing entry should grow, not be replaced

**When NOT to use**:
- Prior content has been falsified (use SUPERSEDE or RETRACT)
- The new content is essentially a rewording (use UPSERT to consolidate)

**Worked example**:

> User: "Also, the rate limit doesn't apply to internal services."
>
> 1. Find the rate-limit entry.
> 2. APPEND a sub-bullet: "- Note: limit does not apply to internal services."
> 3. Provenance: "Appended internal-services exception 2026-05-15."

**Edge case — duplicate prevention**: Before appending, scan for similar content
already present. If found, surface: "The entry already contains a similar note — want
to update the existing one instead?"

---

## DEDUPE

**Definition**: Find duplicate entries covering the same topic; consolidate to one
canonical form.

**Idempotent**: Yes — after DEDUPE there are no duplicates to remove on a second pass.

**When to use**:
- The file has accumulated entries that cover the same topic
- The user says "this is documented in three places" or "find duplicates"
- A periodic audit found duplicates

**Three duplicate categories**:
1. **Exact duplicates**: same content, possibly different wording. Pick one canonical
   form; delete the others.
2. **Near duplicates**: overlapping content. MERGE the unique elements; pick canonical
   form for shared elements.
3. **Conflicting duplicates**: same topic, contradictory content. Surface the conflict
   to the user — do not silently choose.

**Worked example**:

> AUDIT pass finds:
> - `api.md`: "Rate limit: 100 req/min"
> - `limits.md`: "Rate limit: 100 req/min (per endpoint)"
> - `quickstart.md`: "API limit: 60 req/min"
>
> 1. Exact + near: `api.md` and `limits.md` overlap; `limits.md` is more specific.
> 2. Conflict: `quickstart.md` says 60, others say 100.
> 3. Action: Surface to user. Suggest: keep `limits.md` as canonical, RETRACT
>    `api.md`'s version, and ask about `quickstart.md` (is it stale, or about a
>    different limit?).

**Edge case — references**: Before removing a duplicate, search for inbound references
to it. If found, redirect them to the canonical form (or use RENAME semantics).

---

## MERGE

**Definition**: Combine two or more distinct entries (or files) into one.

**Idempotent**: Yes — once merged, a second MERGE finds nothing to combine.

**When to use**:
- Two entries that grew up separately actually belong together
- Two files cover overlapping topics with no clear boundary
- The user says "consolidate these into one place"

**Difference from DEDUPE**: MERGE assumes the source entries are distinct (no
duplication); DEDUPE assumes they are duplicative. Use MERGE when 1+1=2 (both parts
remain); use DEDUPE when 1+1=1 (the parts collapse).

**Worked example**:

> File has two entries:
> - "Authentication: OAuth 2.0 with PKCE"
> - "API Keys: Used for service-to-service calls"
>
> User: "Merge these into one auth section."
>
> 1. Create unified "Authentication" section.
> 2. Sub-section: "User Auth: OAuth 2.0 with PKCE"
> 3. Sub-section: "Service Auth: API Keys"
> 4. Provenance: "Merged authentication entries 2026-05-15."
> 5. Search for references to either original entry; update.

---

## SUPERSEDE

**Definition**: Mark an old entry as replaced by a new one. Preserve a link from old
to new so historical context remains visible.

**Idempotent**: Yes — supersession is a one-way link; re-applying produces no change.

**Difference from UPSERT**: UPSERT replaces in place (old content gone). SUPERSEDE
keeps both, with the old marked as historical and pointing to the new.

**When to use**:
- A revision is significant enough that historical context matters
- Readers may need to understand what the prior version said and why it changed
- An ADR-style change where the decision history is part of the record

**Worked example**:

> Old entry: "**Database**: PostgreSQL 14 — chosen for JSON support and maturity."
>
> User: "We moved to PostgreSQL 16 last month for the JSON_TABLE features."
>
> 1. New entry: "**Database**: PostgreSQL 16 — chosen for JSON_TABLE support
>    (added in PG 16). Supersedes 2025 PG 14 decision."
> 2. Old entry: keep, but add: "Superseded 2026-05-15. See current entry."
> 3. Provenance: "Superseded prior PG 14 decision; reason: JSON_TABLE requirement."

---

## RETRACT

**Definition**: Remove an entry because it is wrong, obsolete, or no longer relevant.

**Idempotent**: Yes — once retracted, there is nothing to retract again.

**Difference from SUPERSEDE**: RETRACT removes; SUPERSEDE keeps with a pointer. Use
RETRACT when the old information is harmful (false, misleading, or pollutes context)
or genuinely irrelevant.

**Default behavior**: Soft retract — replace content with a brief tombstone noting why
it was retracted. Hard delete (no tombstone) only on explicit user request.

**Worked example**:

> Old entry: "**Caching**: Use Memcached for session state."
>
> User: "We never actually used Memcached — we used Redis the whole time."
>
> 1. Replace entry with tombstone: "_Retracted 2026-05-15: This entry was incorrect;
>    sessions have always been in Redis._"
> 2. Provenance: "Retracted incorrect Memcached entry; correct entry under 'Redis'."
> 3. Search for references to Memcached in other files; surface or update.

---

## RENAME

**Definition**: Change the key or heading of an entry, plus update all cross-references.

**Idempotent**: Yes — after RENAME, the old name no longer exists; running again is a
no-op.

**Why this is its own operation**: Renaming a section without updating references
breaks the knowledge base. RENAME bundles the heading change with the reference scan.

**Workflow**:
1. Identify all references to the old name (search across all files in scope).
2. Show the user the list of references that will change.
3. Apply the heading change + all reference updates as a single atomic operation.
4. Verify no references to the old name remain.

**Worked example**:

> User: "Rename the 'Quick Start' section to 'Getting Started'."
>
> 1. Find "## Quick Start" in the target file.
> 2. Search all files for "Quick Start" and `#quick-start` anchors.
>    Found: 3 references across 2 files.
> 3. Present diff: heading change + 3 reference updates.
> 4. Apply.
> 5. Verify: 0 references to "Quick Start" remain.

---

## RECONCILE

**Definition**: Resolve a conflict between two sources, two entries, or chat-vs-file
state.

**Idempotent**: Yes — once reconciled, no conflict remains to resolve.

**Never silent**: RECONCILE always surfaces the conflict to the user with both
versions visible. The user picks; the skill applies.

**When to use**:
- The user makes a statement that contradicts the file
- An AUDIT finds two entries that disagree
- An external source disagrees with the file

**Worked example**:

> User: "Our SLA is 99.95% uptime."
> File: "SLA: 99.9% uptime."
>
> 1. Detect conflict.
> 2. Present: "The file says SLA is 99.9%; you mentioned 99.95%. Which is correct?
>    Has it been updated?"
> 3. User: "It was updated last month to 99.95%."
> 4. UPSERT with new value; provenance: "Reconciled chat-vs-file conflict; user
>    confirmed SLA updated to 99.95% last month."

---

## NORMALIZE

**Definition**: Standardize the format or structure of entries that have drifted.

**Idempotent**: Yes — after NORMALIZE, entries already match the canonical shape.

**When to use**:
- The knowledge base has grown organically and entries follow different patterns
- A new structural standard has been adopted
- An audit reveals format inconsistency

**Always show diffs**: Aesthetic changes are still changes. Show the user every
entry that will be modified before applying.

**Worked example**:

> Audit finds 12 API endpoint entries; 8 use the format `**GET /foo**: description`
> and 4 use `**GET /foo** — description`. User chooses `**GET /foo**: description`
> as canonical.
>
> 1. List the 4 entries to be changed.
> 2. Show side-by-side diff for each.
> 3. Apply on confirmation.
> 4. Provenance: "Normalized 4 endpoint entries to colon-separator format."

---

## EXTRACT

**Definition**: Move a section out of one file and into its own file.

**Idempotent**: Yes — once extracted, running again finds nothing to move.

**When to use**:
- A section has grown large enough to deserve its own file
- A section is logically distinct from the file's main topic
- The user wants to share a section without sharing the whole file

**Workflow**:
1. Identify the section to extract and its inbound references.
2. Create the new file with the extracted content + appropriate frontmatter/header.
3. Replace the original section with a brief stub + link to the new file (or remove
   entirely if the user prefers).
4. Update all inbound references to point to the new file.
5. Verify cross-references resolve.

**Worked example**:

> The `api.md` file has grown to 800 lines, with a 200-line section on webhooks.
>
> User: "Pull the webhooks section into its own file."
>
> 1. Create `webhooks.md` with the section content + standard header.
> 2. Replace section in `api.md` with: "See `./webhooks.md` for webhook
>    details."
> 3. Update 5 inbound references to point to `webhooks.md`.

---

## AUDIT

**Definition**: Survey the knowledge base for staleness, conflicts, duplicates, gaps,
or orphans. Produces a report; does not modify files.

**Idempotent**: Yes (read-only operation).

**When to use**:
- Periodic health check (monthly, quarterly)
- After a major project change that may have invalidated content
- When the user senses the knowledge base has drifted

**Audit dimensions**:
1. **Staleness**: dates, versions, references to deprecated systems
2. **Duplicates**: entries covering the same topic in multiple places
3. **Conflicts**: entries that contradict each other
4. **Gaps**: topics referenced but not defined; broken cross-references
5. **Orphans**: entries that are never referenced and no longer relevant
6. **Format drift**: entries that don't match the file's dominant pattern

**Output**: a structured report listing each finding with recommended operation
(UPSERT / DEDUPE / RETRACT / RECONCILE / etc.). The user then chooses which to apply.

---

## Operation selection cheat sheet

| Scenario | Operation |
|---|---|
| "Update this fact" / "this changed" | UPSERT |
| "Add this detail to the existing entry" | APPEND |
| "These are documented in multiple places" | DEDUPE |
| "Combine these two sections" | MERGE |
| "Replace X with Y, but preserve the history" | SUPERSEDE |
| "Remove this — it's wrong" | RETRACT |
| "Rename this section" | RENAME |
| "These two sources disagree" | RECONCILE |
| "Make these entries follow the same pattern" | NORMALIZE |
| "Move this into its own file" | EXTRACT |
| "Check the health of the knowledge base" | AUDIT |
