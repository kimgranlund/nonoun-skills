---
date: 2026-04-18
coverage: deep
peers:
  - ../agent-dispatch/wave-planning.md
  - ../agent-dispatch/agent-brief-template.md
  - ../structure/skeleton-files.md
primary_sources:
  - expert-dashboard Wave 3 sed-accident incident (2026-04-18, INDEX.md recovery)
  - expert-dashboard per-wave CHANGELOG entries (5 waves)
---

# Post-wave bookkeeping protocol

After every wave, three files update: `references/INDEX.md`, `skill.json`, `CHANGELOG.md`. This is the rhythm that keeps the skill coherent across waves.

**Do this before proposing the next wave.** Never carry unbooked files into a new wave.

## The three updates

### 1. `references/INDEX.md` — flip markers

For every file that landed in the wave, flip its row from `⬜` to `✅`. Nothing else.

**Use Edit with exact old-string / new-string.** One Edit call per row, OR rewrite the whole file with Write if you've read the current state.

### 2. `skill.json` — version bump + files list

- Bump `version`: `0.1.0` → `0.2.0` (Wave 1) → `0.3.0` (Wave 2) → ... → `1.0.0` (final).
- Flip `status`: `skeleton` → `wave-1-complete` → ... → `complete`.
- Append new files to `files[]` array.
- Extend `tags[]` with new domain-specific tags from the wave's findings.
- Update `description` if the wave materially expanded the skill's scope.

### 3. `CHANGELOG.md` — prepend new entry

Prepend (not append) a new version entry above the previous wave's entry.

```markdown
## [0.N.0] — [ISO date] — Wave N references

### Added

N reference files across M parallel web-research agents — [axis breakdown with counts]. Wave N total: **~X lines**. Cumulative: **A/B files (C%), ~D lines**.

| File | Lines |
|---|---|
| `[path]` | [count] |
| ... | ... |

### Notable findings

**[Theme 1, e.g., "Navigation deepening"]:**
- **[Finding 1 with verified claim + primary source]**
- **[Finding 2]**
...

**[Theme 2]:**
- ...

### Bumped

- `skill.json` → v0.N.0, status `[prev]` → `[current]`, `files[]` lists N references + SKILL.md + CHANGELOG.md + references/INDEX.md ([total] total).
- `tags[]` extended: [list new tags].
- `description` [if changed] updated to reflect [new scope].
- `references/INDEX.md` — flipped ⬜ → ✅ on N Wave N rows.

### Known gaps

- [Files forward-referenced by Wave N but not yet landed.]
- [Axes considered but deferred.]
```

## DO NOT use sed to flip INDEX.md markers

**This is the single most important lesson from past runs.** During expert-dashboard Wave 3, a bulk sed command to flip 27 ⬜→✅ markers concatenated 27 replacement stubs onto every line of the 316-line INDEX.md, bloating the file to 370KB of corrupted content. The backup was deleted in the same command chain. Recovery required rewriting the entire INDEX.

**Always use:**
- `Edit` with exact `old_string`/`new_string`, one row at a time, OR
- `Write` with a complete rebuilt file content.

**Never use:**
- `sed -i` with stacked substitutions.
- `sed -i` with `&& rm .bak` in the same chain.
- Bash one-liners that batch-modify many lines at once.

If you catch yourself about to run a sed batch on INDEX.md, stop and use Edit or Write instead.

## Order of operations

1. **All agents complete.** Every agent has returned a findings report.
2. **Tally the wave.** Line counts per file + notable findings per agent.
3. **Update INDEX.md.** Flip ⬜→✅.
4. **Update skill.json.** Version + files[] + tags.
5. **Prepend CHANGELOG entry.** File table + notable findings + bumped + known gaps.
6. **Propose next wave** (or announce v1.0.0 if this was the final wave).

Parallel updates to INDEX, skill.json, CHANGELOG are fine — they're independent files. But all three should happen in the same turn, not spread across turns.

## Write vs Edit for each file

| File | Typical approach |
|---|---|
| `INDEX.md` | Edit per-row, OR Write with full rebuild. |
| `skill.json` | Write with full content (JSON is easier to rewrite than patch). |
| `CHANGELOG.md` | Edit, inserting new entry at the top (`old_string: "# Changelog\n\n## [PREV]"` → `new_string: "# Changelog\n\n## [NEW]\n\n...\n\n---\n\n## [PREV]"`). |

## Tagging conventions for skill.json

Tags derive from:
- Axis names (`navigation`, `accessibility`).
- Canonical exemplar names (`linear`, `stripe`, `datadog`).
- Library names (`tanstack`, `ag-grid`, `recharts`).
- Technique names (`wcag`, `apg`, `virtualization`).

Keep tags lowercase, kebab-case, singular. Aim for 30-100 tags total by v1.0.0 — they drive skill discoverability.

## Version semantics

This method uses versions as **wave markers**, not traditional semver:

- `0.1.0` — Skeleton only.
- `0.2.0` — Wave 1 complete.
- `0.3.0` — Wave 2 complete.
- `0.4.0` — Wave 3 complete.
- `0.5.0` — Wave 4 complete.
- `1.0.0` — All waves complete.

Post-v1.0.0 maintenance:
- `1.0.1` — Date-stamp refresh, version-number updates.
- `1.1.0` — New reference files added (e.g., a new product profile).
- `2.0.0` — Major axis restructure or breaking change to invariants.

## Known-gaps discipline

Every CHANGELOG entry should have a "known gaps" section. This lists:

- **Dangling cross-refs** — files Wave N references that land in Wave N+1.
- **Deferred files** — files considered but not yet scheduled.
- **Open axis questions** — whether to split, merge, or add axes.

Dangling cross-refs are fine short-term; they must resolve by v1.0.0. Grep the final INDEX for `⬜` rows — all should be gone before flipping to `status: "complete"`.

## Findings-to-CHANGELOG pipeline

Agents return 3-5 notable findings per wave. The main thread promotes these verbatim (lightly edited for tone) into the CHANGELOG's "Notable findings" section, grouped by theme.

The CHANGELOG becomes the skill's primary audit trail — a reader can understand **what's in the skill and why** by reading the CHANGELOG alone. Treat the findings as the skill's public-facing justification.

## Checklist after every wave

- [ ] Every ⬜ for Wave N's files flipped to ✅ in INDEX.md.
- [ ] skill.json `version` bumped, `status` flipped, `files[]` extended, `tags[]` extended.
- [ ] CHANGELOG.md has a new entry with the Wave N file table, notable findings, bumped, and known gaps.
- [ ] No `sed` commands were used on INDEX.md.
- [ ] Dangling cross-refs noted in "known gaps".
- [ ] Propose next wave to user (or announce v1.0.0).
