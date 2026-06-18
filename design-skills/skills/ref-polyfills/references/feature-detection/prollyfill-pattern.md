---
date: 2026-04-27
coverage: advisory
peers:
  - ../feature-detection/ponyfill-pattern.md
  - ../feature-detection/progressive-enhancement.md
  - ../meta/glossary.md
  - ../meta/decision-tree.md
  - ../js-language-status/shadowrealm.md
  - ../js-language-status/pipeline-operator.md
  - ../js-language-status/decorators.md
  - ../landscape-shifts/interop-2026-priorities.md
primary_sources:
  - https://www.oreilly.com/library/view/building-polyfills/9781449370725/ch07.html — Brian Kardell, "Building Your First Prollyfill" (Building Polyfills, O'Reilly)
  - https://github.com/bkardell/selectors-L4-link-prollyfills — Kardell's CSS Selectors Level 4 prollyfill
  - https://w3ctag.github.io/polyfills/ — W3C TAG, "Polyfills and the evolution of the Web" (covers speculative-polyfill / prollyfill)
  - https://kikobeats.com/polyfill-ponyfill-and-prollyfill/ — concise three-way comparison
  - https://infrequently.org/about-me/ — Alex Russell, Extensible Web Manifesto co-author
  - https://github.com/extensibleweb/manifesto — Extensible Web Manifesto (the philosophical container for prollyfills)
---

# Prollyfill pattern

A speculative implementation of a pre-spec or in-flux feature, shipped before the spec is finalized. The "prolly" is a contraction of "probably-fill" — the implementation is *probably* what the spec will land on, but it might not be.

## The term

The term **"prollyfill"** is most directly associated with **Brian Kardell**, who chaired the W3C Extensible Web Community Group and authored the chapter ["Building Your First Prollyfill"](https://www.oreilly.com/library/view/building-polyfills/9781449370725/ch07.html) in the O'Reilly book *Building Polyfills*. Kardell's [`selectors-L4-link-prollyfills`](https://github.com/bkardell/selectors-L4-link-prollyfills) repo is an early canonical example, and his Hitch.js project (a "prollyfill engine" for CSS selectors, ~2013) operationalized the pattern.

The Extensible Web Manifesto (https://github.com/extensibleweb/manifesto) is the philosophical container — the idea that low-level primitives plus userland prollyfills can shape standards faster than committee-driven specs alone. **Alex Russell** (https://infrequently.org/, co-author of the Extensible Web Manifesto) is closely associated with this movement and uses the term in writing about it, but the term itself is most commonly traced to Kardell and the Extensible Web community circa 2013–2014.

The W3C TAG document on polyfill evolution (https://w3ctag.github.io/polyfills/) discusses speculative polyfills as a category — Kardell contributed to that working group's thinking on the subject.

For the curious, the term is sometimes spelled "probablyfill" in older writing; "prollyfill" became the canonical compression.

## Definition

**Prollyfill**: a feature shim that targets a *proposed* or *in-flux* spec — typically pre-Stage-3, sometimes pre-Stage-2 — and exists to (a) let developers experiment with the proposal, (b) provide implementation feedback to spec authors, and (c) bridge the gap until native support arrives.

Compare:

| Term | Spec stage | Risk profile |
|---|---|---|
| Polyfill | Finalized (typically Stage 4 / shipped in spec; native partial) | Low — spec is stable, only browser support varies |
| Ponyfill | Finalized (delivery model, not stage signal) | Low — same as polyfill |
| **Prollyfill** | **Pre-spec or in-flux (Stage 1 / 2 / early 2.7)** | **High — spec may change, implementations break** |

A prollyfill is identifiable not by its delivery (it can be a polyfill or a ponyfill in shape) but by the *maturity of the underlying spec*.

## Historical examples

**Container queries** before the spec landed. The original "element queries" prollyfill (EQCSS, by Tommy Hodgins; CSS Element Queries by Mariusz Nowak) shipped speculative semantics that later differed from the final `@container` syntax. Code written against the prollyfill needed migration when CSS Containment Module Level 3 stabilized.

**CSS Custom Properties** (then-named "CSS Variables"). Prollyfilled in early 2010s under multiple names with different syntaxes — the final spec settled on `--property-name` syntax, which broke earlier prollyfilled code.

**Web Components v0**. The original Polymer 0.5 / 1.0 era shipped a `<template>`, `<element>`, `HTMLImports`, and Shadow DOM v0 stack that was almost entirely replaced by v1 specs in 2016. Code written against v0 prollyfills required complete rewrites.

**Decorators (Stage 2 / 2.7 era)**. Multiple TC39 decorators proposals — "legacy" (TypeScript / `experimentalDecorators`), "Stage 2" (~2017), "Stage 3 2022-03", "Stage 3 2023-11" — each broke code written against the previous. Babel and TypeScript both prollyfilled decorators for years; the final ES2025 form differs from every interim. See `../js-language-status/decorators.md`.

**Scroll-driven animations** before Chromium shipped. The `flackr/scroll-timeline` polyfill (which is also a prollyfill — the spec was in flux) tracked spec changes and required code updates.

**Pipeline operator (`|>`)**. Babel's pipeline-operator plugin offered three different proposals (Hack, F#, smart-mix) at various points; users could opt into one. The spec stalled at Stage 2 with no progress in 2025; any code using the prollyfilled syntax is at version-lock risk. See `../js-language-status/pipeline-operator.md`.

## The risk

A prollyfill commits the consumer to:

1. **Migrating when the spec changes.** If the spec removes a method, renames a property, or changes evaluation order, every call site must be updated. Migration is non-mechanical when semantics change.
2. **Maintaining a dependency on the prollyfill author.** The library must stay current with spec churn or be abandoned. Users either follow the maintainer or fork the prollyfill.
3. **Encoding a guess.** Production code shipping a prollyfill is encoding a bet that the spec will land in roughly the prollyfilled form. Stages 1–2 proposals fail or change semantics frequently enough that this bet often loses.

The Records & Tuples proposal is a recent cautionary example. Prollyfilled libraries shipped immutable record/tuple types based on the Stage 2 proposal; Records & Tuples was withdrawn at the April 2025 TC39 plenary, and Composites (its successor) has different semantics. See `../js-language-status/withdrawn-records-tuples.md`. Every prollyfilled-Records codebase needs migration.

## At our baseline: skip prollyfills for production

The recommended posture for the modern baseline:

- **Don't ship prollyfills to production users.** The risk profile is wrong for production code — feature might be removed, semantics might change, and your migration is forced rather than scheduled.
- **Use prollyfills in experimentation, exploration, and feedback loops.** Test the developer experience of a Stage 2 proposal, then file feedback on tc39/proposals or the relevant CSSWG issue. Don't ship the prollyfilled artifact to end users.
- **Watch for the "Stage 4 but unshipped" exception.** When a proposal is at Stage 4 (spec finalized) and just hasn't shipped yet in the engines you target, the "prollyfill" is essentially a polyfill — the spec won't change. Iterator helpers and Set methods both passed through this state in 2024–2025. The risk profile collapses to a normal polyfill.

The threshold worth caring about is **Stage 3 → Stage 4**:

| Stage | Posture |
|---|---|
| 0 / 1 / 2 | Don't ship to production. Experiment locally, file feedback. |
| 2.7 | Prollyfill OK behind a flag with explicit rip-out plan. |
| 3 | Polyfill is reasonable; prep for native. Spec is stable. |
| 4 | Polyfill is normal. Just remove it when targets hit native. |

See `../js-language-status/` per-feature files for current TC39 stages.

## When a prollyfill becomes a polyfill

OddBird's `popover-polyfill` is a good example of the transition. Started as a prollyfill in the WICG-draft era (when popover semantics were unstable); became a polyfill once the API stabilized in HTML and shipped in Chrome, then Safari, then Firefox. The same package, the same import; the *spec maturity* is what changed.

The same arc happened with the `@oddbird/css-anchor-positioning` polyfill — it began life as a prollyfill against a draft CSS Anchor Positioning spec, stabilized as the spec moved to CR / shipping, and is now a normal polyfill for the Firefox 129–146 gap (see `../css-polyfills-and-shims/anchor-positioning-polyfill.md`).

## Prollyfill as feedback loop

The Extensible Web argument for prollyfills isn't that you should ship them — it's that *implementing them surfaces issues with the spec*. A prollyfill author who tries to build, ship, and use a feature against a draft spec discovers ambiguities, missing edge cases, and ergonomic problems that committee review can't predict. That feedback flows into spec iteration.

This is the *good* use of prollyfills: as instruments for spec maturation, not as production artifacts.

## When you might still ship one

Three scenarios where a production prollyfill is defensible:

1. **The spec is at Stage 2.7 / Stage 3 and you have a rip-out plan.** Use a feature flag, contain the prollyfill to a single module, and commit to migration when the native version ships.
2. **The feature is internal-only.** A team-internal tool that you control end-to-end; spec churn means you migrate the tool, not 100K external users.
3. **You're the prollyfill maintainer.** You're shipping the spec drift yourself; cost of churn is amortized across your maintenance budget.

For everything else: stick with PE (`progressive-enhancement.md`), ponyfills (`ponyfill-pattern.md`), or polyfills of finalized features (`../runtime-polyfills/`, `../css-polyfills-and-shims/`).

## Anti-patterns

### "It works in Chrome behind a flag, so it's fine to prollyfill"

Chrome flags expose pre-stable implementations. The flag is there because the spec might change. Prollyfilling a flagged feature into production code is a double bet — bet on the flag becoming default, and bet on the semantics not shifting. Both happen, neither happens reliably.

### "We've been shipping the prollyfill for 2 years, it's stable"

Stability of the prollyfill is not stability of the spec. The Records & Tuples prollyfills had years of stability before the proposal was withdrawn. Spec age ≠ spec finality.

### "We'll just freeze the prollyfill version"

Possible, but you've now committed to maintaining a hand-rolled fork forever. The cost is asymmetric — small until something breaks (a security advisory, a transitive dependency change, a TC39 decision), then enormous.

## Cross-references

- `ponyfill-pattern.md` — the production-grade alternative for finalized specs.
- `progressive-enhancement.md` — the production-grade alternative for missing-feature degradation.
- `../meta/glossary.md` — concise definitions of polyfill / ponyfill / shim / prollyfill.
- `../meta/decision-tree.md` — the do-I-need-a-polyfill flow (prollyfills branch off at the "is the spec stable?" check).
- `../js-language-status/decorators.md` — exemplar of long-running spec churn.
- `../js-language-status/pipeline-operator.md` — exemplar of stalled-Stage-2 prollyfill risk.
- `../js-language-status/shadowrealm.md` — exemplar of Stage 2.7 (NOT Stage 3) prollyfill judgment call.
- `../js-language-status/withdrawn-records-tuples.md` — the Records & Tuples cautionary tale.
- `../landscape-shifts/interop-2026-priorities.md` — what's likely to mature in 2026 (and worth tracking before prollyfilling).
