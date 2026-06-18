---
date: 2026-04-18
coverage: expanded
peers:
  - ../methodology/wave-based-research.md
  - ../methodology/verification-discipline.md
  - ./dashboard-expert-case-study.md
primary_sources:
  - expert-typography/CHANGELOG.md (v0.1.0 through v1.0.0)
  - expert-typography/skill.json v1.0.0
  - expert-typography/references/INDEX.md v1.0.0
---

# Case study: expert-typography

**Medium-domain exemplar.** 59 reference files, ~5 waves. Authored in a prior session 2026-04-18. The first skill produced by this method and the origin of the verification-discipline lessons.

## Scope

Domain statement: typography as a knowledge domain — font classifications, anatomy, metrics, variable-font axes, pairing, legibility research-survey, non-Latin scripts, CSS typography techniques (text-wrap, text-box, initial-letter, leading-trim, font-size-adjust, metric overrides), OpenType features, fallback stacks.

## Axes (~9)

1. `classifications/` — Serif, sans, slab, display, mono, script. Historical taxonomy (Vox-ATypI, humanist / transitional / modern / etc.).
2. `anatomy/` — x-height, cap height, ascender, descender, counter, aperture, terminal.
3. `metrics/` — Font metrics the code uses: UPM, hhea vs OS/2, line-gap, cap-height %.
4. `pairing/` — Family pairings. Metric-compatibility. Voice-complement logic.
5. `legibility/` — Reading research-survey. Measure (line length) bounds. Hyphenation.
6. `scripts/` — Non-Latin: Arabic, CJK, Devanagari, Hebrew, Greek, Cyrillic, Thai, Hangul, Ethiopic.
7. `variable-fonts/` — Axis taxonomy (wght / wdth / ital / slnt / opsz + custom). Wiring to CSS.
8. `techniques/` — CSS text-* properties. 2024-2026 Baseline capabilities.
9. `libraries/` + `foundries/` — Google Fonts, Adobe Fonts, open-source foundries, Commercial. Licensing.

## Waves executed

Wave 1 established classifications + anatomy + metrics + legibility + pairing foundations. Waves 2-5 completed scripts, variable fonts, techniques, libraries, and foundry profiles.

Final size: 59 files at v1.0.0.

## What worked

1. **Axis clarity.** Typography has well-established sub-domains (anatomy, metrics, pairing) that map cleanly to axes. The scoping survey was fast.
2. **Primary-source discipline.** Typography has strong canonical sources (Ellen Lupton's *Thinking with Type*, Robert Bringhurst's *Elements of Typographic Style*, foundry docs) that agents could cite directly.
3. **CSS-landscape dating.** Every technique file carried "as of 2026-04" Baseline notes with caniuse verification.

## What went wrong — the WebKit Bug 241691 incident

During Wave 2 authoring, an agent fabricated "WebKit Bug 241691" as a citation for a Safari text-wrapping issue. The bug ID looked plausible — right format, right tracker — but the bug didn't exist.

The fabrication wasn't caught until post-v1.0.0 audit. Fix: the file was edited to state the observed behavior without the tracker ID.

**Lesson**: the agent had access to WebSearch but produced the citation from priors instead of verifying. Agent briefs for subsequent skills (expert-dashboard onward) included explicit "Past fabrication lesson: do not invent tracker IDs (WebKit Bug 241691)" language. This language reliably makes agents more careful.

## Size comparison to expert-dashboard

| Metric | expert-typography | expert-dashboard |
|---|---:|---:|
| Files | 59 | 101 |
| Axes | ~9 | 15 |
| Waves | 5 | 5 |
| Products/exemplars axis | foundries (deferred to v1.x) | 13 products |
| Lines (approx) | ~30-35k | ~57k |

Typography is a **well-bounded domain** — the scope is inherently narrower than dashboards. That's why typography landed at 59 files while dashboards landed at 101. Neither was padded or truncated to hit a target; the domains simply have different natural sizes.

## Takeaways for method consumers

- Medium-domain skills (60-ish files) are a cleaner shape than the "comprehensive" 100+ skills — faster to complete, tighter to navigate.
- Product/exemplar axes are less necessary for well-canonized domains (typography's canon is books and foundries, not UX products) but still help.
- Fabrications are easier to catch early (agent findings stage) than late (post-v1.0 audit). Treat suspicious citations as suspicious immediately.
- The 5-wave arc worked for both skill sizes. Don't assume small domains need fewer waves — use the wave structure even for 30-file skills; it spreads the verification checkpoints evenly.

## Pattern transferability

The expert-typography → expert-dashboard jump proved the method generalizes. Same wave arc, same bookkeeping protocol, same agent-brief structure, two very different domains. Both landed at v1.0.0 with coherent axis structure, dated claims, and primary-source citations.

That's the reason this meta-skill (`meta-expert-author`) exists: the pattern is repeatable. Any domain with distinct sub-dimensions, an established canon, and a practitioner body of knowledge is a candidate.
