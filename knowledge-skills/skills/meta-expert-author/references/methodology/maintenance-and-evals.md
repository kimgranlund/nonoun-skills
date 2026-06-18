---
date: 2026-04-18
coverage: deep
peers:
  - ../methodology/verification-discipline.md
  - ../methodology/publishing-trappings.md
  - ../methodology/wave-based-research.md
primary_sources:
  - expert-color MAINTENANCE.md
  - meta-skill evals methodology (skill library)
---

# Maintenance and evals

A skill that shipped at v1.0.0 has a shelf life. Version numbers go stale, acquisitions change the landscape, URLs rot, new primitives ship. This file covers the post-v1.0 lifecycle and the eval protocol that catches regressions.

## Why this matters

Without a maintenance cadence:
- 6 months in: some React 19 claims are wrong (React 20 shipped).
- 12 months in: 15% of primary-source URLs 404.
- 18 months in: two `products/` profiles describe features that were removed.
- 24 months in: the skill is actively harmful — it confidently states wrong things.

A skill with a maintenance protocol stays useful for years. Without one, it rots in months.

## Refresh cadence

| Cadence | What to refresh | Time cost |
|---|---|---|
| **Continuous** (as you notice) | Broken URLs, obviously wrong claims | Minutes per fix |
| **6-month pass** | Version numbers, Baseline markers, acquisition claims, primary-source URL audit | 2-4 hours |
| **12-month pass** | All of the above + product profile deep-check + re-run evals | 4-8 hours |
| **24-month pass** | All of the above + axis re-evaluation (new axes? old axes obsolete?) | 1-2 days |
| **Event-driven** | Major release, acquisition, spec revision affecting the domain | As needed |

Default to **6-month passes** for active skills.

## The 6-month refresh protocol

### Step 1: URL audit

For every file in `primary_sources`:

- Fetch the URL.
- If it 404s or redirects to an unrelated page: replace with archive.org mirror or find a new primary source.
- If it redirects to a still-valid page: update the URL.

Tooling: a short script that reads all frontmatter `primary_sources:` lists and curls each URL.

### Step 2: Version-number audit

Grep the skill for version patterns (`v\d+\.\d+`, `\d+\.\d+\.\d+`, "React 19", "Chrome 125"). For each:

- Check the current version via npm / web / docs.
- If the stated version is stale by a minor release, note it. Stale by a major: fix.

Grep for dated claims (`as of 2026-04`, `2026 landscape`, `April 2026`) and verify each is still current.

### Step 3: Acquisition / landscape audit

For each product or library with an acquisition / partnership / status claim in the skill, fetch the official status page and check.

Examples of claims that go stale quickly:
- "PartyKit acquired by Cloudflare" (still true as of 2026-04, but Cloudflare could rebrand).
- "React 19 GA December 2024" (true; but "latest React" needs updating with each release).
- "Next.js PPR still experimental" (status flips as features stabilize).

### Step 4: Spec-revision audit

For standards the skill cites (WCAG, APG, RFC, CSS specs):

- Check the W3C "Updated" or "Publication History" field for the standard.
- If a revision shipped, verify any quoted normative text is still accurate.

### Step 5: Bump and log

- Bump `skill.json` version (`1.0.0` → `1.0.1` for refreshes, `1.1.0` if adding content).
- Update `date:` in refreshed reference files.
- Add a CHANGELOG entry summarizing what was refreshed.

## Event-driven refresh triggers

Some events require an out-of-cadence refresh:

- **Major domain release** — React 20 ships → refresh all React-related claims. WCAG 2.3 Rec → refresh all SC citations.
- **Canonical tool deprecation** — `react-virtualized` officially sunset → replace recommendations.
- **Acquisition affecting a profiled product** — Datadog acquires Mixpanel → revise profiles.
- **Key source disappearance** — A cited YouTube channel is deleted → replace with archive.org or alternative.
- **Domain-shifting event** — Interop 2027 focus areas announced → update Baseline status claims.

Treat these as "just enough refresh" — fix the affected claims, skip the full 6-month protocol unless it's been a while.

## Evals

Tests that validate the skill works. Two kinds.

### 1. Trigger-accuracy evals

Does the skill fire on prompts it should, and not on prompts it shouldn't?

File: `evals/trigger-accuracy.md`

```markdown
# Trigger accuracy

## Should trigger (20 prompts)

1. "Explain OKLCH vs HSL."
2. "Build me a color palette for a finance dashboard."
3. "Why does HSL fail for gradients?"
...
20. "What's the deal with Munsell's color system?"

## Should NOT trigger (20 prompts)

1. "Write me a Python script that sums a list."
2. "Plan my grocery run."
...
20. "What's the weather in Tokyo?"
```

Run these through the skill's harness. Expected:
- 100% triggering on the "should trigger" list.
- < 5% false-positive rate on the "should NOT trigger" list.

A skill that fails trigger accuracy has a broken `description` field. Fix and re-eval.

### 2. Answer-quality evals

Given the skill is loaded, does the agent answer correctly?

File: `evals/answer-quality.md`

```markdown
# Answer quality

## Prompt: "What color space should I use for a CSS gradient from red to blue?"

Expected: mentions OKLCH or OKLAB (not HSL or RGB). Mentions mid-gradient darkening problem. Cites `components-specific-work` references or the SKILL.md gradient section.

Pass criteria: OKLCH or OKLAB present, HSL not recommended, no fabricated claims.

## Prompt: "Is APCA required for WCAG 3?"

Expected: states WCAG 3 is Working Draft (not Recommendation). APCA is informative only. WCAG 2.2 is the conformance target.

Pass criteria: doesn't claim APCA is normative. References WCAG 2.2 as the current Rec.

...
```

Run 10-30 answer-quality prompts. Review answers manually or with a judge model. Track pass rate per version.

### 3. Regression evals

Record prompts where the skill gave a wrong answer in the past. Every refresh must pass these.

File: `evals/regressions.md`

```markdown
# Regression evals

## Regression: [date] — [issue]

**Prompt**: [the prompt that revealed the bug]
**What went wrong**: [brief description]
**Fix**: [what was changed]
**Expected now**: [specific answer criteria]

## Regression: 2026-Q2 — stale TanStack version

**Prompt**: "What's the current TanStack Table version?"
**What went wrong**: skill claimed v8.x after v9 was Widely Available.
**Fix**: Refreshed `tables/tanstack-table.md` 2026-05-15.
**Expected now**: mentions v9.x current, notes date of last verification.
```

### Running evals

Manually: paste prompts into a fresh conversation with the skill loaded, compare to expected.

Programmatically: wire to `meta-skill`'s eval harness if you have it; otherwise a simple shell script + judge model works.

**Cadence**: run evals after every refresh. Run trigger-accuracy + regression evals monthly if the skill is in active use.

## Version semantics post-v1.0

| Change | Bump |
|---|---|
| Typo fix, broken-link fix | No bump |
| Date-stamp refresh, version-number refresh, no content change | `1.0.0 → 1.0.1` |
| Content refresh (claims updated, new findings) | `1.0.1 → 1.1.0` |
| New reference files added | `1.0.x → 1.1.0` |
| Major axis restructure | `1.x.x → 2.0.0` |
| Breaking change to invariants | `1.x.x → 2.0.0` |

Semver for skills is loose compared to software — adopt the spirit, not the strict letter.

## Maintenance record

Every refresh gets a CHANGELOG entry. Template:

```markdown
## [1.0.1] — 2026-10-18 — 6-month refresh

### Refreshed

- Version numbers across `performance/`, `forms/`, `tables/`: [summary of updates].
- [N] primary-source URLs replaced (dead links): [list].
- React 19.2 → 19.3 references updated.

### Verified (no change needed)

- All WCAG 2.2 SC citations current.
- All product-profile acquisition claims current.

### Caught by evals

- [Regression] Stale TanStack Table version claim — fixed in `tables/tanstack-table.md`.

### Next refresh

Target: 2027-04-18.
```

## Staleness detection

Two signals that a skill needs refresh:

1. **User feedback** — a report that a claim is wrong. Treat as urgent.
2. **Calendar** — 6 months since last refresh date in any reference file.

A skill whose most recent `date:` frontmatter is > 12 months old should carry a banner in SKILL.md: "⚠️ Last refreshed [date]; some claims may be stale."

## Retiring a skill

When the domain shifts so much that the skill is net-harmful:

1. Mark `skill.json` with `"status": "deprecated"`.
2. Add a DEPRECATED.md explaining what to use instead.
3. If there's a successor skill, reference it.
4. Keep the skill installed for 6-12 months (it's still useful as a historical reference).
5. After that grace period, archive.

Don't silently delete — skill consumers build cross-references. Deprecation is a public event.

## When maintenance isn't worth it

- **One-shot skill** produced for a specific project, never reused. Don't set up MAINTENANCE.md; just let it rot naturally.
- **Internal skill** for a topic the team no longer works in. Archive; don't refresh.
- **Experimental skill** that didn't find its audience. Delete or park.

Only skills that earn refresh effort deserve it. Most skills don't — and that's fine.
