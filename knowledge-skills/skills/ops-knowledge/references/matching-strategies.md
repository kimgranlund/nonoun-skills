# ops-knowledge: Matching Strategies

How to identify the existing entry that an operation should target. Most knowledge-base
drift comes from a UPSERT landing on the wrong entry (or no entry, silently creating a
duplicate). Identity resolution is the most failure-prone step in any operation.

---

## The three matching strategies

### 1. Key match (strongest)

**Use when**: The file has explicit identifiers — frontmatter keys, headings that
function as unique IDs, anchor labels, or structured fields.

**How**: Look for an exact match on the identifier.

**Examples**:
- Markdown heading: `## Rate Limits` — match on heading text
- Frontmatter key: `slug: rate-limits` — match on slug
- JSON object: `"id": "rate-limits"` — match on id field
- Table row with a primary-key column

**Failure mode**: The identifier has been changed (RENAME drift) but you're looking
for the old name. Mitigation: also check recent SUPERSEDE notes and RENAME provenance
entries.

**Confidence**: High. If a key match succeeds, proceed with the operation.

---

### 2. Heading or path match (medium-strong)

**Use when**: No explicit keys, but the document has clear hierarchical structure with
distinctive headings or path-like fragments.

**How**: Walk the heading hierarchy and match by path. E.g., `"API > Rate Limits >
Per-endpoint limit"` is a more precise locator than just `"Per-endpoint limit"`.

**Examples**:
- `## Architecture > ### Database > #### Connection Pooling`
- A glossary entry by exact term + context

**Failure mode**: Two sections at different paths use the same heading (e.g., two
"Examples" sub-sections under different parents). Always include the parent path to
disambiguate.

**Confidence**: Medium-high. Verify with a content read before operating.

---

### 3. Fuzzy or semantic match (weakest)

**Use when**: The file lacks structural identifiers and headings are descriptive prose
rather than labels.

**How**:
- Tokenize the incoming statement and the candidate entries
- Score by overlap (tokens, n-grams) and by semantic similarity if available
- Rank candidates and pick the top one only if it exceeds a confidence threshold

**Examples**:
- User says "the rate limit thing" → search for entries mentioning "rate limit"
- User says "what we said about the database" → scan for database-related entries

**Failure mode**: Multiple plausible matches; semantic match picks the wrong one.

**Confidence**: Low to medium. **Always confirm with the user** before applying an
operation matched only by fuzzy/semantic strategy.

---

## The escalation ladder

When operating, try strategies in order from strongest to weakest:

1. Try **key match** first.
2. If no key, try **heading/path match**.
3. If still no match, try **fuzzy/semantic match**.
4. If no match exceeds the confidence threshold, treat as "no existing entry" and
   propose INSERT (for UPSERT) or surface ambiguity (for other operations).

**Never skip to fuzzy match if a key strategy is available.** Fuzzy match is the
last resort, not a shortcut.

---

## Ambiguity protocol

When more than one entry matches (any strategy):

1. **Stop.** Do not pick one silently.
2. **List candidates** to the user with file path + heading path + first line of
   content.
3. **Ask** which one is the target — or whether the change should be applied to all,
   or whether the apparent duplication is the actual problem (use DEDUPE instead).
4. **Wait** for explicit confirmation before proceeding.

**Sample ambiguity prompt**:
> "I found 3 entries that could match 'rate limit':
>
> 1. `api.md > ## Rate Limits` — Per-endpoint sustained rate limit
> 2. `limits.md > ## API Limits` — Aggregate rate + burst limits
> 3. `quickstart.md > ## Getting Started > Limits` — Quickstart summary
>
> Which is the target for this update? Or should I DEDUPE these first?"

---

## Identity drift signals

Watch for these signals that an entry's identity may be unstable:

- **Frequent RENAMEs** in provenance → the entry's name is contested; use content
  match in addition to key match
- **Multiple SUPERSEDE chains** → recent revisions; verify you're targeting the
  current version, not a superseded one
- **Same content in multiple files** → DEDUPE candidate; don't UPSERT all of them
- **Heading change between sessions** → the chat may reference an old name; map to
  current name explicitly

---

## When the entry genuinely doesn't exist

If no match is found, the operation determines what happens:

| Operation | If no match |
|---|---|
| **UPSERT** | Insert as a new entry (this is the "U" half) |
| **APPEND** | Surface as error: cannot append to nothing. Suggest UPSERT. |
| **DEDUPE** | No-op — nothing to deduplicate |
| **MERGE** | Surface as error: need at least 2 entries to merge |
| **SUPERSEDE** | Surface as error: cannot supersede nothing. Suggest UPSERT. |
| **RETRACT** | No-op — nothing to retract |
| **RENAME** | Surface as error: source name not found |
| **RECONCILE** | No conflict — but flag that one party of the "conflict" doesn't exist |
| **NORMALIZE** | No-op for that entry |
| **EXTRACT** | Surface as error: source content not found |

---

## Cross-file identity

Some entries are referenced across files. When operating on one:

1. Search the full knowledge base for references to the entry (links, mentions,
   anchor references).
2. If references exist, include them in the operation plan:
   - UPSERT: references may still resolve (content changed, location same)
   - RENAME: references must be updated
   - RETRACT: references will break — surface as part of the diff
   - EXTRACT: references must point to the new file

3. Re-verify after the operation: search for the old reference pattern and confirm
   zero results.

---

## Implementation checklist

For every operation, before applying:

- [ ] Have I identified the target entry by the strongest available strategy?
- [ ] If fuzzy/semantic match, have I confirmed with the user?
- [ ] Have I checked for ambiguity (multiple matches)?
- [ ] Have I searched for cross-file references that need to follow this change?
- [ ] Have I noted the identity in the provenance (heading path, key, or content
      snippet for searchability)?
