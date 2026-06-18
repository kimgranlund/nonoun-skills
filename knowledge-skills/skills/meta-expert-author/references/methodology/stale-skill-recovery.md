---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/maintenance-and-evals.md
  - ../methodology/verification-discipline.md
  - ../methodology/cross-skill-dependencies.md
primary_sources:
  - 6-month refresh protocol (from maintenance-and-evals.md)
  - expert-dashboard/expert-color/expert-typography real-world refresh observations
---

# Stale-skill recovery

What to do when a skill has gone unmaintained for 12+ months and needs to be made useful again. Distinct from the 6-month refresh — this is triage, not cadence.

## Signals a skill is stale

- **Most recent `date:` frontmatter is > 12 months old.** Automated staleness signal.
- **User reports a confidently wrong claim.** Reactive signal.
- **Evals start failing** where they passed before. Regression signal.
- **A library the skill recommends was sunset** or acquired / rebranded.
- **A spec the skill cites got a new revision** (WCAG 2.3, React 21, etc.).
- **A product profiled in the skill no longer works that way** (UI redesigned, features removed).

Any one of these is a yellow flag. Three or more is a red flag — the skill is actively harmful.

## The triage decision

When a stale skill is flagged, decide:

1. **Refresh** — the skill's core is still sound; fix the stale claims.
2. **Partial refresh** — some axes are fine, others are rotten; rebuild just the rotten ones.
3. **Deprecate** — the domain has shifted enough that the skill's core premise is wrong.
4. **Fork** — split into two skills, one for legacy users, one for current state.

Default to **refresh**. Escalate only if the core premise is wrong.

## Full refresh protocol (for 12+ month-stale skills)

Heavier than the 6-month refresh. Five steps:

### Step 1: Staleness inventory

For every reference file, check `date:` frontmatter. Classify:

- **Fresh** (< 6 months) — skip.
- **Moderate** (6-12 months) — re-verify top-level claims only.
- **Stale** (> 12 months) — needs full re-verification.

A typical 12-month-stale skill has 60-80% of files in the "stale" bucket.

### Step 2: URL audit

Run through every `primary_sources` URL. Use a script to batch-curl them.

- **404 / gone** — find replacement or archive.org mirror.
- **Redirects to unrelated content** — find replacement.
- **Still live** — keep, note verification date.

Typical 12-month URL rot: 10-20% of non-archive URLs are dead. Higher for YouTube / personal blog / corporate press release sources.

### Step 3: Version-number and landscape audit

For each stale file, re-verify:

- Library versions (check npm, GitHub releases).
- Spec status (check W3C, IETF, MDN).
- Acquisition / partnership claims (check company pages, TechCrunch).
- Baseline / caniuse status for web platform features.

Log every correction in a working file — the CHANGELOG will cite these.

### Step 4: Re-run evals

If the skill has `evals/`, run them:

- **Trigger-accuracy** regressions? Usually the description is still fine.
- **Answer-quality** regressions? Usually correlated with stale content — fix the referenced files.
- **Regression evals** still passing? Good — don't break the fixes.

If no evals exist, this is the moment to add them (see `maintenance-and-evals.md` §evals).

### Step 5: Wave-style refresh

Don't try to refresh a 60-file skill in one session. Use a mini-wave structure:

- **Wave R1** — URL fixes across all files (parallelizable, 3-5 agents).
- **Wave R2** — version / landscape corrections per axis (5-8 agents, one per axis).
- **Wave R3** — content additions for new developments since last refresh (2-4 agents).

Each mini-wave gets a CHANGELOG entry. Bump version accordingly: `1.0.0 → 1.0.1` (Wave R1), `1.0.1 → 1.0.2` (Wave R2), `1.0.2 → 1.1.0` (Wave R3 adds content).

## Partial refresh

When only some axes are rotten, refresh those axes and leave the rest alone.

Example: `expert-dashboard` 18 months post-v1.0. The `products/` axis is stale (products shipped redesigns, some acquisitions). `accessibility/` is fine (WCAG 2.2 didn't change). `tables/` is borderline (TanStack v9 shipped).

Partial refresh:
- Products axis: mini-wave, 8-10 file updates.
- Tables axis: mini-wave, 3-4 file updates.
- Skip accessibility + everything else.

Version bump: `1.0.0 → 1.1.0`. CHANGELOG entry notes which axes were refreshed and which were verified-unchanged.

## Deprecation

When the domain has shifted so much that the skill's premise is wrong:

1. Announce in CHANGELOG with rationale.
2. Add `DEPRECATED.md` to the skill root:
   ```markdown
   # Deprecated
   
   This skill was retired 2027-04-18. The domain has shifted such that [specific reason].
   
   **Use instead**: [successor skill if one exists, or alternative approach].
   
   The content remains for historical reference but is no longer maintained.
   ```
3. In `skill.json`: `"status": "deprecated"`, add `"deprecated_date": "ISO date"`, add `"successor": "skill-name"` if one exists.
4. In SKILL.md frontmatter: prepend "⚠️ DEPRECATED [date]" to the description so the skill doesn't silently trigger.
5. Notify peers (via `consumed_by[]` and `peer[]`).
6. Keep the skill installed for 6-12 months as historical reference, then archive.

Don't silently delete a deprecated skill. Deprecation is a public event with downstream impact.

## Fork

Rare but legitimate: the domain bifurcated. Part of the original skill is still accurate for the legacy context; part needs rebuilding for the new state.

Example: a hypothetical `react-server-components-expert` from 2024 that covered experimental PPR. By 2027 RSCs are stable but PPR was renamed and restructured. Fork into:

- `react-server-components-legacy-expert` — covers 2024-2026 state, marked deprecated.
- `react-server-components-expert` — fresh, covers 2027+ state.

Forks are expensive. Only do this when downstream consumers can't upgrade immediately.

## Dealing with fabrication found during refresh

If refresh surfaces a fabricated claim (an invented bug ID, a wrong citation):

1. Remove or correct the claim.
2. Log it in `verification-discipline.md` § "Known corrections log" as a pattern-lesson.
3. Check whether similar fabrications slipped through elsewhere — grep for the class of claim (tracker IDs, version numbers, acquisition claims).
4. Add an eval (`evals/regressions.md`) that would have caught this.

Fabrications during refresh are more concerning than fabrications during authoring — they mean the original author's verification failed AND the 6-month refresh missed it.

## Agent briefs for refresh waves

Refresh waves differ from new-authoring waves:

> **Refresh wave brief template:**
> "Refresh the following N files in `[skill-name]`: [file paths]. Per file: re-verify every `primary_sources` URL (replace dead links with archive.org mirrors or alternatives). Re-verify every version number, acquisition claim, and spec citation against 2027-04 web snapshots. Update `date:` frontmatter. Do NOT restructure files. Do NOT add new content unless a claim is so outdated it needs rewriting. Report: per-file changes + list of corrections."

The emphasis on "do NOT restructure" is critical. Refresh waves fix claims in place. Restructuring is a separate operation (major version bump).

## When to just let a skill die

Not every stale skill deserves refresh.

- **Abandoned project** — no one uses the skill anymore. Don't refresh; archive.
- **Superseded by a better skill** — newer skill covers the same ground better. Point at successor, archive original.
- **Domain deprecated** — e.g., a `flash-animation-expert`. Archive.

Refresh cost is real. Only skills with active consumers earn refresh effort.

## What v1.3 captures

v1.2's `maintenance-and-evals.md` covered the 6-month refresh but had a thin section on "what if a skill goes way past its refresh window." v1.3 expands that into the full stale-skill-recovery triage, partial refresh patterns, fork decisions, and refresh-wave agent briefs.

## Takeaways

- A skill flagged stale gets triaged: refresh / partial / deprecate / fork.
- 12+ month-stale skills use wave-style mini-refreshes, not one-shot fixes.
- URL rot typically hits 10-20% at 12 months; budget accordingly.
- Fabrications found during refresh are a yellow flag — run the verification discipline more aggressively.
- Refresh waves fix claims in place; restructuring is a separate operation requiring a major version bump.
- Not every stale skill deserves refresh. Archive unused ones.
