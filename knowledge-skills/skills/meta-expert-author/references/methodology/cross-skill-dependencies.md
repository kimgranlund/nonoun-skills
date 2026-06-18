---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/maintenance-and-evals.md
  - ../structure/skeleton-files.md
primary_sources:
  - expert-typography ↔ ui-sys-typography peer relationship
  - expert-dashboard ↔ expert-color peer declaration
  - ~/.claude/skills/CLAUDE.md peer convention
---

# Cross-skill dependencies

Skills reference each other. When one refreshes or breaks, the others need to know. This file covers what `"peer"`, `"consumed_by"`, and file-path cross-references actually commit to — and what happens when they drift.

## Dependency kinds

Four kinds of cross-skill dependency, in increasing strength:

| Kind | Declared where | Breakage cost |
|---|---|---|
| **Descriptive mention** | Prose in SKILL.md or reference files | Low — stale name just reads wrong |
| **Peer declaration** | `skill.json → composition.peer[]` | Medium — consumers assume conceptual adjacency |
| **File-path cross-reference** | Inline link in a reference file | High — broken link rots the skill |
| **Hard functional dependency** | Typed skill contract, shared types | Critical — produced output fails without it |

This meta-skill's outputs use the first three; typed skills (`meta-skill-typed`, `meta-type-registry`) use the fourth.

## What `peer` commits to

Declaring `"peer": ["expert-typography"]` in `skill.json` commits to:

1. **Conceptual adjacency** — the two skills cover related domains and reinforce each other.
2. **Non-overlap in scope** — the peers have distinct primary domains, not competing coverage.
3. **Consistent conventions** — both use the same structural invariants (flat-prose SKILL.md, YAML frontmatter, wave-based authoring) where applicable.
4. **Soft compatibility** — if you load both skills in the same conversation, they shouldn't contradict each other.

`peer` does NOT commit to:

- Synchronized versioning.
- Mutual awareness (peer A can refresh without peer B knowing).
- Bidirectional declaration (peer A can list peer B; peer B doesn't have to list A).

## What `consumed_by` commits to

Declaring `"consumed_by": ["ui-audit-quality"]` in `skill.json` commits to:

1. **Known consumer** — this skill's output is used by the consumer.
2. **Breaking-change responsibility** — if you break invariants or restructure, notify the consumer.
3. **Version-bump awareness** — major version bumps (2.0.0) warn consumers.

`consumed_by` DOES commit to:

- Preserving the output shape across minor versions (1.0.0 → 1.x.x).
- Announcing breaking changes in CHANGELOG prominently.
- A grace period before deprecation takes effect.

## File-path cross-references

Inline references like `` `../expert-typography/references/techniques/measure.md` `` are load-bearing. They:

- Assume a specific directory layout.
- Assume the target file still exists at that path.
- Break silently if the peer skill reorganizes.

**Rules for cross-skill file paths:**

1. **Use relative paths, never absolute.** `../expert-typography/...` not `/Users/.../expert-typography/...`.
2. **Test the path resolves before committing.** A 3-second verification saves hours of debugging later.
3. **Cite the target's SKILL.md first, specific files second.** SKILL.md is stable; internal file paths aren't.
4. **When in doubt, describe instead of linking.** "See `expert-typography` for measure-width calculations" is more rot-resistant than a deep file link.

## Peer-refresh propagation

When skill A refreshes (6-month cadence, see `maintenance-and-evals.md`), what happens to peer B?

### Default: nothing automatically

Skills don't sync. Refreshing `expert-typography` doesn't trigger a refresh of `expert-dashboard` even though they peer.

### Manual: "refresh-fanout" at peer's next refresh cycle

When peer B hits its own 6-month refresh, one of the steps is:

- For each skill in `peer[]` and `consumed_by[]`, check whether their most recent CHANGELOG version is newer than your last refresh.
- If yes: read their CHANGELOG "Notable findings" section and check for claims that affect shared vocabulary or cross-referenced content.
- Update or fix as needed.

This is a **pull model** — peer B refreshes itself and pulls from peers' CHANGELOGs. Skill A doesn't push.

### Event-driven: when a peer deprecates or breaks

If skill A publishes a deprecation (`"status": "deprecated"`) or bumps to a major version (2.0.0), peers that reference it should:

1. Check each file-path cross-reference to A.
2. If the path still resolves and the content still matches the citation, no action.
3. If not, fix the citation or remove it.

Out-of-cadence — do this when you see the deprecation, not 6 months later.

## Declaring cross-skill dependencies in skill.json

Full shape:

```json
{
  "composition": {
    "peer": [
      "expert-typography",
      "expert-color"
    ],
    "consumed_by": [
      "ui-audit-quality"
    ],
    "depends_on": [
      "meta-type-registry"
    ]
  }
}
```

- `peer[]` — same-tier skills with adjacent scope.
- `consumed_by[]` — skills that use this one's output.
- `depends_on[]` — (optional, typed skills) hard dependencies — fail if absent.

For skills produced by `meta-expert-author`, `depends_on[]` is rarely needed. Peer + consumed_by is typical.

## Shared-vocabulary drift

The most common cross-skill failure: two skills develop divergent vocabulary for the same concept.

Example: `expert-typography` uses "measure" (typographic term for line width). `ui-sys-responsive` uses "max-width" for the same idea. A user loading both gets conflicting prescriptions.

**Mitigation**: at 6-month refresh, skim peers' vocabulary. If a peer has started using a term you've avoided, either adopt it or add a cross-reference note: "`expert-typography` calls this 'measure'; we use 'max-width' because we treat it as a CSS property."

Don't fork vocabulary silently. The user notices.

## Version-compatibility matrices

For skills with active consumers, maintain a compatibility matrix in SKILL.md or a dedicated `COMPATIBILITY.md`:

```markdown
## Compatibility

| This skill version | Works with ui-audit-quality | Works with ui-sys-typography |
|---|---|---|
| 1.0.x | ≥1.0.0 | ≥1.0.0 |
| 1.1.x | ≥1.1.0 | ≥1.0.0 |
| 2.0.x | ≥2.0.0 (breaking) | ≥1.5.0 |
```

Only needed for skills with actual multi-version deployment. For most internal skills, `skill.json composition.peer[]` suffices.

## Peer-skill agent brief

When a wave adds a file that cross-references a peer skill:

> "This file should cross-reference `../expert-typography/SKILL.md` and (if applicable) specific reference files under `../expert-typography/references/`. Verify the paths resolve. If expert-typography has a SKILL.md section that covers your topic, link to it; don't re-derive. Peer skills: expert-typography (classifications, anatomy), ui-sys-typography (tokens from brand)."

Agents need to know which peers exist and what shape they have. Without that context, agents invent peer paths that don't resolve.

## Breaking changes to peers

If you break a peer-facing invariant — rename an axis, remove a reference file, change SKILL.md's cheat sheet format — the protocol:

1. **Before breaking**: search the skill library for cross-references to the affected path (`grep -r "old-path" ~/.claude/skills/`).
2. **At the break**: bump to a major version (2.0.0).
3. **In the CHANGELOG**: prominent "**Breaking changes affecting peer skills**" section listing what moved where.
4. **Notify peer owners**: via commit message, PR, or direct ping.

The `expert-dashboard` Wave 3 sed-disaster (INDEX corruption) was self-contained — no peer skill referenced INDEX internals. Had it been a SKILL.md reorganization, peers would need the announcement.

## When cross-skill references decay

Inventory cross-references at 12-month refresh (not 6-month — catching drift at the yearly mark):

1. Grep the skill for `../other-skill/` paths.
2. For each, verify the file exists and the content matches your citation.
3. Fix what's broken. Demote broken deep-file references to shallow SKILL.md references.

## Cross-reference fatigue

If your skill cross-references 10+ peers and most paths break at every refresh, you've over-coupled. Reduce by:

- Citing peer SKILL.md only (stable) instead of deep files (unstable).
- Describing the peer in prose instead of linking.
- Merging adjacent content into your own skill if the peer is rotting faster than you can patch.

Loose coupling to peers is more durable than tight coupling. A skill that depends on 10 peers' internal file paths is fragile.

## What v1.3 captures

v1.2's known-gaps list flagged "cross-skill dependency / sync protocol." v1.3 provides:

- The four dependency kinds and what each commits to.
- Peer-refresh propagation semantics (pull model, not push).
- Shared-vocabulary drift mitigation.
- Version-compatibility matrices (for skills that need them).
- Breaking-change protocol for peers.

## Takeaways

- Skills don't sync automatically. Use the 6-month refresh to pull from peers' CHANGELOGs.
- Cite peer SKILL.md files first; deep file paths are load-bearing and rot-prone.
- Declare peers and consumers explicitly in skill.json; don't rely on prose mentions.
- Loose coupling wins over tight coupling. Keep cross-references shallow.
- Breaking changes affecting peers require a major version bump + CHANGELOG announcement + direct notification.
