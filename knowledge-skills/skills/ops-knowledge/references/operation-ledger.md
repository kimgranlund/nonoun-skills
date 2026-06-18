# ops-knowledge: Operation Ledger

The **ledger** is the queryable mutation history of a knowledge base — the global complement to
per-entry **provenance**. Provenance answers "why does *this entry* look like this?"; the ledger
answers "what changed across the *whole base* last month, by which operation, and why?"

This is the operability layer: without a ledger, a knowledge base's history is scattered across
file diffs and can't be queried, trended, or audited as a whole.

## Location & shape

Append-only JSON-lines file at the knowledge-base root:

```
<knowledge-base>/
└── .knowledge-history/
    ├── ops-ledger.jsonl     # one JSON object per line, append-only, never rewritten
    └── README.md            # generated human index (newest-first table)
```

- **One line per applied operation** — including a read-only AUDIT that found nothing (proves the
  audit ran).
- **Immutable** once written — a correction is a *new* line (e.g. a RETRACT of a mistaken UPSERT),
  never an edit to a prior line. This is the same discipline as ADRs and `ops-repo`'s
  `audit-history/`.
- **Create the dir on first write**; never block an operation because the ledger is missing.

## Line schema

```json
{
  "ts": "2026-05-15T14:32:00Z",        // ISO-8601 UTC, when the operation was applied
  "op": "UPSERT",                       // one of the 11 verbs (closed enum)
  "file": "api.md",                     // target file, repo-relative to the knowledge base
  "entry": "Rate limit",                // heading/key operated on ("" for file-level ops)
  "summary": "60→100 req/min",          // SHAPE of the change — no secrets/PII
  "provenance": "user statement 2026-05-15",  // the same why recorded on the entry
  "conflicts_surfaced": 0,              // how many conflicts were raised to the user
  "diff_shown": true,                   // was the diff confirmed (false only with batch auto-apply)
  "idempotent": true                    // did this verb run idempotently (see operations.md)
}
```

### Per-verb fields (additive — include when relevant)

| Verb | Extra fields |
|---|---|
| **MERGE** | `"sources": ["auth.md#oauth", "auth.md#api-keys"]` — what was combined into `entry` |
| **DEDUPE** | `"removed": ["api.md#rate-limit", "quickstart.md#api-limit"]`, `"canonical": "limits.md#rate-limit"` |
| **SUPERSEDE** | `"supersedes": "Database: PostgreSQL 14"` — the old entry now pointing forward |
| **RETRACT** | `"reason": "incorrect", "tombstone": true` (`tombstone:false` only on explicit hard delete) |
| **RENAME** | `"from": "Quick Start", "to": "Getting Started", "refs_updated": 3` |
| **EXTRACT** | `"to_file": "webhooks.md", "refs_updated": 5` |
| **RECONCILE** | `"versions": ["file: 99.9%", "chat: 99.95%"], "chosen": "99.95%"` |
| **AUDIT** | `"findings": 4, "dimensions": ["staleness","duplicates","conflicts","gaps","orphans","format"]` — no `file`/`entry` |

## Query patterns

The point of JSON-lines is that the history is greppable with `jq`:

```bash
LEDGER=<knowledge-base>/.knowledge-history/ops-ledger.jsonl

# Everything removed, when, and why
jq -r 'select(.op=="RETRACT") | "\(.ts) \(.file)#\(.entry): \(.summary) — \(.provenance)"' "$LEDGER"

# Operations applied without a shown diff (audit the auto-apply blast radius)
jq -r 'select(.diff_shown==false) | "\(.ts) \(.op) \(.file)"' "$LEDGER"

# Operation counts by verb, last 30 days
jq -r --arg since "$(date -u -v-30d +%Y-%m-%d 2>/dev/null || date -u -d '30 days ago' +%Y-%m-%d)" \
   'select(.ts >= $since) | .op' "$LEDGER" | sort | uniq -c | sort -rn

# Conflicts that were surfaced (trust signal — these went to the user, not auto-resolved)
jq -r 'select(.conflicts_surfaced > 0) | "\(.ts) \(.file): \(.conflicts_surfaced) conflict(s)"' "$LEDGER"
```

## Generated index (`.knowledge-history/README.md`)

Newest-first, regenerated from the `.jsonl` (so it's never hand-maintained):

```markdown
# Knowledge-base operation history

| Date | Op | File#Entry | Summary | Diff shown |
|---|---|---|---|---|
| 2026-05-15 | UPSERT | api.md#Rate limit | 60→100 req/min | ✓ |
| 2026-05-14 | AUDIT | — | 4 findings (staleness, duplicates) | n/a |

_Trend: 18 operations this month (12 UPSERT, 3 DEDUPE, 2 RETRACT, 1 AUDIT); 2 conflicts surfaced, 0 silent resolutions._
```

## Producing & validating lines

The ledger is not hand-edited — it is produced by the shared runner `scripts/ops-ledger.py` (one tool
for the whole `ops-*` family, not a per-skill copy). The skill **calls it** so that the Verify-Target
criterion "the ledger recorded the mutation" is enforceable: *the validator exited 0*, not *a line
exists*.

```bash
LEDGER_TOOL=scripts/ops-ledger.py          # repo-relative shared runner
BASE=<knowledge-base>                        # the base being operated on

# Validate a line against this schema WITHOUT writing (dry-run a proposed record):
echo '{"op":"UPSERT","file":"api.md","entry":"Rate limit","summary":"60->100 req/min",
       "provenance":"user 2026-05-15","conflicts_surfaced":0,"diff_shown":true,"idempotent":true}' \
  | python3 "$LEDGER_TOOL" validate

# Record the mutation (validate THEN atomically append; a malformed line is REFUSED, never written;
# ts is stamped if omitted; the .knowledge-history/ dir is created on first write):
echo '{...same object...}' | python3 "$LEDGER_TOOL" append --base "$BASE"

# Regenerate the human index after a batch:
python3 "$LEDGER_TOOL" index --base "$BASE"
```

The validator enforces: `op` ∈ the closed 11-verb enum; the base fields and their types; ISO-8601 UTC
`ts`; non-empty `summary`/`provenance`; `conflicts_surfaced >= 0`; the **per-verb additive fields**
(e.g. `DEDUPE` requires `removed`+`canonical`, `RENAME` requires `from`+`to`+`refs_updated`); and that
`AUDIT` lines carry no `file`/`entry`. An invalid line exits 1 and is never appended — so the ledger
cannot silently accumulate malformed history.

## Why this and not just git history

- Git records *file bytes changed*; the ledger records *the intent* (which verb) and *the safety
  signals* (diff shown? conflict surfaced? idempotent?) — queryable without diffing blobs.
- A knowledge base often lives in a Claude Project / Cowork space with **no git** at all; the ledger
  is the portable history that travels with the files.
- The ledger is the input to a future **operation-recall eval** (does re-running the skill reproduce
  the same op selection on the same input?) — see the skill's ROADMAP.
