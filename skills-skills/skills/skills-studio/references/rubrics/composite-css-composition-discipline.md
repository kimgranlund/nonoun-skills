---
title: Composite CSS Composition Discipline
key_question: When an agent composes UI from primitives + composites with their own @scope CSS, does it respect the layered contracts (composition grammars, intrinsic display, slot vocabularies) or override them in ways that silently break the child's intrinsic layout?
layer: gen-ui-authoring
primary_critic: boris-cherny  # PEV loop / harness quality — the audit-gate vs visual-review gap is exactly this layer
companion_rubrics:
  - agents-ux-wireframing-ascii  # wireframing prevents premature visual collapse; this rubric prevents post-wireframe composition-grammar bypasses
  - generative-ui-reasoning      # the 19-rung ladder; this rubric operates at Rungs 12-13 (Section/Component)
version: 0.1.0
status: empirically-derived
source_incidents:
  - "2026-05-24 billing-overview CSS-illiteracy postmortem (substrate-side; chat-ui)"
  - "2026-05-24 8-demo grandfather-elimination cycle (4 cross-composite fixes observed)"
---

# Composite CSS Composition Discipline

## What this rubric measures

When an agent authors or composes UI from a design system with primitives + composites that each ship their own `@scope` CSS contracts, does the agent respect those contracts as load-bearing — or treat them as conveniences to be overridden?

The failure mode this rubric defends against: **agents read each component's API surface (attributes, slots, events) but skip its CSS, then write parent CSS that silently clobbers the child's intrinsic layout, OR re-implement composition grammar the parent already provides.** The result is markup that passes structural audits but renders visually broken.

## Why this is its own rubric

Distinct from the wireframing rubric (which prevents premature visual collapse at the design stage) and the reasoning-ladder rubric (which sequences the conceptual steps). This rubric operates at Rungs 12-13 (Section / Component) of the gen-ui ladder: **AFTER the wireframe is correct and BEFORE rendering**. The trap is structural at the CSS-layer boundary, not at the design layer.

Empirically derived from a 2026-05-24 incident where one composite's bypass + four cross-composite display-override bugs all passed every structural audit the codebase had, while shipping broken visuals. Five distinct patterns recur; four generalize to any design-system-driven gen-ui pipeline.

## Pipeline this rubric encodes

```
Intent → Wireframe → Component Selection
                     ↓
                     Component Literacy (CSS read for each picked primitive)  ← THIS RUBRIC
                     ↓
                     Composition Sketch (using each primitive's grammar)      ← THIS RUBRIC
                     ↓
                     Author Markup
                     ↓
                     Verify: structural audit + visual proportion check       ← THIS RUBRIC
```

Without this discipline, the steps from selection through verify all execute without anyone reading the primitives' CSS contracts. The agent treats `<X-ui>` as a black box whose attribute API is the whole API. CSS is implementation detail. **For visual outcomes, CSS IS the contract** — attributes only tune it.

## 8 scoring dimensions

| # | Dimension | Type | Question |
| --- | --- | --- | --- |
| D1 | Composition-grammar respect | gate | When the agent uses primitive `<X-ui>` that ships a composition grammar (e.g., `<header>` + slot vocabulary), does the markup actually use that grammar — or stamp arbitrary children that bypass it? |
| D2 | Parent/child display boundary | gate | When parent CSS toggles visibility of an embedded primitive, does it use `:not([state])` to preserve the child's intrinsic display — or override with `display: block` and silently flatten the child's layout? |
| D3 | Control-group size consistency | gate | When the agent composes multiple form/control primitives in the same visual row, do all share the same `size` attribute — or do defaults diverge into mismatched baselines? |
| D4 | Container-query/grid alignment | gate | When the layout has `@container` queries collapsing column count at breakpoints, does the grid use plain `repeat(N, 1fr)` — or `minmax(<min>, 1fr)` that fights the breakpoints? |
| D5 | Default-vs-contract distinction | review | Does the agent treat each primitive's defaults (display, size, columns) as starting points to be overridden when context demands — or as contracts that must not be clobbered? |
| D6 | Slot-vocabulary use over re-invention | gate | When stamping into composites with named slots (`slot="icon"`, `slot="heading"`, etc.), does the agent use the slot names — or invent parallel `[data-*]` attribute conventions and re-implement positioning? |
| D7 | Embedded-composite visual-debt acknowledgment | review | When an embedded composite has known visual debt (e.g., proportions that don't match the consumer's design intent), does the consumer surface it as accepted debt (with a fix-scope note) — or silently inherit and hope it looks OK? |
| D8 | Wrapper-primitive attribute forwarding | review | When a wrapper primitive (e.g., search-ui wrapping input-ui) doesn't forward consumer-passed attributes like `size` to its inner control, does the agent file an upstream fix — or work around by reaching into wrapper internals? |

**Gate dimensions** (D1, D2, D3, D4, D6) — mechanically scoreable. Each has at least one detector pattern (existing or forward-work) that can flag in CI.

**Review dimensions** (D5, D7, D8) — require human / agent judgment of intent + scope.

## 4 hard tests

| # | Test | Verifies |
| --- | --- | --- |
| H1 | Composition-grammar bypass scan | For each composite stamped/composed, does the markup follow its grammar? (e.g., `audit:card-structure` for card-ui, similar audits forward-work for avatar-ui/alert-ui/drawer-ui.) |
| H2 | Parent display-override scan | For each `[state] > [child]` rule that sets `display: block` (or any non-`none` display), is the child a composite with `:scope { display: flex \| grid }` that this would override? Visual-review gap until audited. |
| H3 | Control-group height parity | Per visual row of form controls, do all controls render at the same height? Playwright measure: `getBoundingClientRect().height` should be uniform across siblings in a toolbar / button-cluster. |
| H4 | minmax-vs-container-query scan | Any grid using `repeat(N, minmax(<min>, 1fr))` AND `@container` queries on column count = fighting. Flag at code review. |

## 5 named anti-patterns

| ID | Name | What it looks like |
| --- | --- | --- |
| AP-CCD-01 | **API-only literacy** | Agent reads the component's `.yaml` + `.d.ts` (props, events, slots) but never opens its `.css`. Stamps `<X-ui>` with attributes, never inspects how X-ui's `@scope` rules render its children. |
| AP-CCD-02 | **Reach-into-child override** | Parent CSS sets `display: block` (or any non-toggle display) on an embedded primitive to "make it visible." Beats the child's `:scope { display: flex \| grid }` from its own `@scope` by specificity. |
| AP-CCD-03 | **Parallel composition layer** | Agent stamps `<div data-foo>` + `<div data-bar>` + `<div data-baz>` inside a composite that ships its own grammar (e.g., `<header>` + slot vocabulary), then re-implements the grid layout via custom `@scope` rules. |
| AP-CCD-04 | **Mixed-defaults toolbar** | Agent composes a button cluster relying on each primitive's defaults without setting a common `size`. Buttons default `md`, inputs default differently, wrapper primitives don't forward size — three control heights in one row. |
| AP-CCD-05 | **minmax-vs-CQ fighter** | Agent writes `repeat(N, minmax(<min>, 1fr))` plus `@container` queries for responsive collapse. The minmax floor causes overflow BEFORE the breakpoint reduces N. |

## 7-phase operating procedure

When composing UI from a design system with `@scope` CSS primitives:

1. **Derive intent** → wireframe (use `agents-ux-wireframing-ascii` rubric)
2. **Component selection** → for each picked primitive, RECORD the CSS literacy facts (default render, slot grammar, exposed tokens, embed gotchas). Reading is mandatory; recording is the proof of reading.
3. **Composition planning** → for each primitive, plan child structure following its grammar. If a primitive's grammar is unfamiliar, re-read its `.css` before planning the markup.
4. **Annotate dimensions** → from CSS literacy facts, annotate the wireframe with real dimensions (px / rem). Catches D4 (minmax-vs-CQ) and D7 (visual debt) at design time.
5. **Author markup** → follow each primitive's slot grammar (D1, D6). Set consistent sizes on form-control groups (D3). Use `:not([state])` for visibility toggles, never `display: block` override (D2).
6. **Author CSS overrides** → for any rule targeting an embedded composite element, ask: does this override a property the composite sets in its `@scope`? If yes, choose a non-clobbering pattern (consumer-extension tokens like `--card-bg`, slot composition, etc.).
7. **Verify** → run composition-grammar audits (forward work for most primitives); measure rendered heights of control groups via Playwright; visual-review for D5/D7/D8 judgment calls.

## What detectors exist today (substrate-side reference)

These detector citations are specific to `~/Projects/chat-ui` (AdiaUI repo) — pattern generalizes to any design-system repo with similar audits.

| Dimension | Detector | Status |
| --- | --- | --- |
| D1 (card-ui specifically) | `scripts/audit/audit-card-structure.mjs` | ✓ wired; scans HTML + JS (2026-05-24) |
| D1 (avatar-ui, alert-ui, drawer-ui, aside-ui) | — | ⏳ forward work |
| D2 | — | ⏳ forward work (only visual review today) |
| D3 | — | ⏳ forward work (only visual review today) |
| D4 | — | ⏳ forward work (code-review pattern only) |
| D5–D8 | — | reviewer-only (no mechanical detector planned) |

The forward work on detectors is enumerated in chat-ui's `.brain/handoffs/2026-05-25-session-handoff.md` (items 12-15 of the "next 20").

## When to apply this rubric

- **Mandatorily**: any time an agent generates UI by composing primitives that ship their own `@scope` CSS contracts
- **At Rungs 12-13** of the gen-ui reasoning ladder (Section / Component)
- **As a precondition** for declaring a generative-UI surface "verified" or "shipped"
- **As a debugging frame**: when an audit passes but the rendered output looks wrong, walk D1-D4 first; one of them covers most cases

## What this rubric does NOT cover

- Wireframing discipline → see `agents-ux-wireframing-ascii`
- General reasoning-ladder sequencing → see `generative-ui-reasoning`
- Design-token contract validity (raw color values, etc.) → typically covered by repo-specific lint
- Accessibility, performance, visual-hierarchy critique → orthogonal concerns

## Citations & source incidents

The four cross-composite patterns this rubric encodes were empirically observed and fixed in `~/Projects/chat-ui`:

| Pattern | Sister commit | Sister postmortem |
| --- | --- | --- |
| D1 / AP-CCD-03 (composition-grammar bypass) | `4e86400c9` (payment-method-list rewrite) | `2026-05-24-component-css-illiteracy.md` |
| D2 / AP-CCD-02 (parent display override) | `4223a4147` (4 billing composites simultaneously) | (within session handover) |
| D3 / AP-CCD-04 (mixed control sizes) | `1298fb064` (search-ui forwarding + toolbar size) | (within session handover) |
| D4 / AP-CCD-05 (minmax vs container queries) | `94d497557` (dashboard-layout KPI grid) | (within session handover) |

Companion documents from the source pipeline (`adia-ui-authoring` skill):

- `references/common-gotchas.md` (substrate-side framing of the 5 gotchas)
- `references/composite-demo-protocol.md` §Phase 2.5a (Pre-flight Component Literacy gate)
- `references/component-literacy.md` (sister skill `adia-ui-kit` consumer-side framing of pre-flight)
- `references/common-gotchas-consumer.md` (sister skill `adia-ui-kit` consumer-side framing of these 4 patterns)
