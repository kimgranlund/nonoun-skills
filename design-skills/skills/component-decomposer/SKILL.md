---
name: component-decomposer
description: >
  Decompose, design, and grade a zero-dependency web component (Custom Elements, FACE, no native form
  elements) AND how components nest + wire (compose) up to the module, on two crossing axes — COMPOSE
  (layer → anatomy → API → composition → coherence: the primitive → component → module tier ladder +
  seams/slots/overflow) and REALIZE (geometry → element → semantics → interaction → fidelity) — scored
  separately (the defect quadrant) so a clean API can't hide an inert composition. Backed by a gated
  rubric, the (height-glyph)/2 geometry engine, a contract-card linter, and a composition-card linter
  (tier · seam · overflow · slot-presence). Use when
  designing, nesting, or grading a component or composition, fixing geometry/parts/API, building a
  no-native-form-element control, or spotting a god-component. NOT for a function (code-decomposer), a
  proof (proof-decomposer), code (ui-build-components), an app shell / page region grid / archetype
  (layout-decomposer), or tokens (ui-build-tokens).
---

# component-decomposer — design a component on two crossing axes

A building-block component is **correct on two independent axes that walk the same hierarchy in
opposite directions** — the same outside-in / inside-out seam the [layout-decomposer](../layout-decomposer/SKILL.md)
applies to space and the [mermaid-decomposer](../mermaid-decomposer/SKILL.md) applies to a diagram,
here applied to a zero-dependency web component:

- **Compose · whole → part** grades the **abstraction**: the layer → its anatomy (named parts) → its
  API surface → **how it composes upward** (the primitive → component → module tier ladder: the seam,
  slots, overflow, and cross-component state that wire components into modules) → its coherence with
  the library.
- **Realize · part → whole** grades the **embodiment**: its exact geometry → the custom element → its
  platform semantics (ARIA/FACE) → its interaction contract (incl. the cross-component seam) → its
  rendered fidelity.

They **cross at the component contract** — a named part with an API that is *also* a real box with
exact pixels, an `ElementInternals`-bearing element, and a keyboard map. That crossing is the whole
technique: a component can be **designed right, built wrong** (clean layer + API, but off-ramp
pixels, no FACE, or dead in forced-colors) or **built right, designed wrong** (pixel-exact and
accessible, but a boolean-prop explosion or a self-owned margin that rots the library). Opposite
defects, opposite fixes — so you **score and report the two axes separately**, never averaged.

The Realize axis rests on a **deterministic geometry foundation**: one law — *every glyph centers in
a square cell of side = the button height, so edge padding = (height − glyph)/2* — from which the
square icon-only button, the asymmetric icon/caret padding, the pill radius, and composed container
insets are all **computed and machine-checked**, never guessed.

## Quick Start

**You bring:** a component (a screenshot, a spec, existing code) and the question — "design this",
"what are its parts/API?", "are the pixels right?", "is it production-ready?". **You get:** a
contract card, a geometry spec on the ramp, and a two-axis grade with the defect quadrant named.

> *"Design our button — icon, label, and a caret, across sizes."* →
> 1. **Compose — layer → anatomy:** it's a **component** `[gate]`; anatomy is `[ icon? · label? ·
>    caret? ]` with eight permutations `[gate]`. The button is also a select trigger / menu item /
>    modal action — design the anatomy to **nest**.
> 2. **Realize — geometry first:** run `bin/geometry-check.py`. Height/icon/caret/font/spacer come
>    from the XS–2XL ramp; **paddings are derived** by `(height − glyph)/2` `[gate]`; icon-only is
>    **square**; container insets **compose**. Then **element** (autonomous, signals-reactive,
>    light DOM) `[gate]` and **semantics** (role via `ElementInternals`; a value-bearing control is
>    FACE) `[gate]`.
> 3. **Interaction + fidelity:** APG keyboard (Enter + Space), the **native-parity budget** (focus
>    ring, forced-colors, mobile picker) `[review]`; SSR/theming/icon strategy `[review]`.
> 4. **Verify + report:** `bin/component-contract-check.py` over the contract card, then the two axis
>    scores + the quadrant cell — gate failures first.

For a **composition** — how components nest + wire up to the module — Compose's A4/A5 carry the
tier ladder, and the second `bin/` gate is the **composition card**:

> *"Build a toolbar with primary actions and an overflow menu."* →
> 1. **Compose — A4 tier + seam:** it's a **component** on the **primitive → component → module**
>    ladder — it composes primitive `x-button`s + an `x-menu` and adds a **seam** `[gate]`; its
>    boundary is *one* toolbar, not a loose button row. The seam is a **priority + overflow**
>    mechanism: actions render inline until they don't fit, then collapse *lowest-priority-first* into
>    the overflow menu (the *same* actions, one source of truth — never authored twice). Containment:
>    `toolbar → [ action-group · spacer · overflow-trigger → menu(items) ]`.
> 2. **Realize — cite the leaves, then the cross-component notes:** the leaf `x-button` / `x-menu`
>    contracts are the single-component REALIZE concern — **cite them, don't re-derive**. The
>    cross-component **state** (the overflowed set, derived from width) folds into B3; the reflow
>    folds into B4.
> 3. **A5 coherence + the up-handoff `[review]`:** zero outer margin (spacing between pieces is the
>    parent's gap); the *module* it sits in hands the **app shell / page region grid UP to
>    [layout-decomposer](../layout-decomposer/SKILL.md)** — this skill stops at "does the module
>    cohere and fit the slot the shell hands it".
> 4. **Verify + report:** `bin/composition-check.py` over the `*.composition.json` card
>    (tier-consistency · the seam gate · overflow-declared · the slot-presence → grid generator · no
>    self-margin), then the two axis scores + the quadrant — a beautifully-bounded toolbar with a fake
>    overflow is **built right, designed wrong** at A4.

**Modes:** **DESIGN** (Compose-down → Realize-up → reconcile at the contract → hand off to a code
peer; the app shell hands up to layout-decomposer) · **DECOMPOSE** (read a component or composition →
layer/tier + anatomy + realization walk + grade) · **GRADE** (score both axes against the rubric,
gates before reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Compose** | whole → part | **A1** Layer → **A2** Anatomy → **A3** API → **A4** Composition *(the primitive → component → module tier ladder: seam · slots · overflow)* → **A5** Coherence | "Is it the *right component*, shaped to compose?" |
| **B · Realize** | part → whole | **B1** Geometry → **B2** Element → **B3** Semantics *(+ cross-component state)* → **B4** Interaction *(+ cross-component reflow)* → **B5** Fidelity | "Does it *render exact and work*, here, with no native control?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on
that axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5) — **except A4's tier/seam joints, which are a
mechanizable gate** (a seamless component or a mis-cut tier blocks A4 just as B1 blocks Realize). A
shippable component is **≥4 on every review with zero gate failures**, reported as two separate axis
scores plus the defect quadrant. **Three** gates route to code: **B1 geometry** →
`bin/geometry-check.py`; **A1/A2/B2/B3/B4 contract** (the single-component card) →
`bin/component-contract-check.py`; **A4/A5 composition** (the multi-component card — tier-consistency
· seam · overflow · slot-presence grid · no self-margin) → `bin/composition-check.py`.

## The doctrine — geometry is computed, not guessed

The dimensional law — *every glyph centers in a square cell of side = the button height, so edge
padding = (height − glyph)/2* — is the one part of this skill that is **arithmetic, not judgment**, so
it is routed to `bin/geometry-check.py` and **machine-checked, never eyeballed**: the derived paddings,
the square glyph-only button, the pill radius, and the composed insets all fall out of the ramp + the
law. Everything else — the layer, the anatomy, the API surface, the platform-semantics contract — is
*judged*. The discipline is the same one the code-family siblings share: **route the mechanizable gate
to code, judge the rest** — a clean API can't hide off-ramp pixels, and exact pixels can't hide a
prop-exploded API, because the two axes are scored separately and only B1 is delegated to the engine.

## The geometry foundation (the Realize axis's first gate)

One law governs the whole dimensional system — `bin/geometry-check.py` is its source of truth:

> **Edge padding for any glyph = (height − glyph) / 2** — every glyph centers in a square cell of
> side = the button height.

The only **free** per-size values are five — **height, icon, caret, font, spacer** (the XS–2XL
ramp). Everything else is derived: the asymmetric icon-side vs caret-side padding (forced by icon ≠
caret), the **square** icon-only/caret-only button, the **pill** radius (`height/2`), and the
**composed** inner padding that containers and lists reuse for nested sections. Badges and tags are
the same system at a smaller scale. Full ramp, permutations, and CSS idiom in
`references/geometry-system.md`.

## The component families (pick by what the component does)

The family files are the recipe library — anatomy · states · ARIA role · keyboard · embodiment ·
geometry, per pattern. They share one geometry (the button box) and one platform contract (FACE +
APG + the top layer).

| Family | Members | Reference |
|---|---|---|
| **Controls** (form-associated, native-replacing) | button · custom select/combobox · checkbox · switch · radio · textarea-like | `references/family-controls.md` |
| **Overlays** (top-layer surfaces) | modal card (header+body+actions) · menu · popover · drawer/panel · tooltip · toast | `references/family-overlays.md` |

(Disclosure — tabs/accordion/command-palette — and Primitives — box/stack/cluster/grid/card — are
tracked in ROADMAP; their geometry is already covered by `geometry-system.md`'s composed-padding and
square-glyph rules.)

## The composition scale (A4 / A5 — how components nest + wire)

A4 carries more than "does this one component nest" — it grades the **tier ladder**: the same skill
that designs a single component grades **how components compose up to the module**. The single
component is the leaf; A4/A5 walk **up** from it. `references/composition-patterns.md` is the recipe
library (anatomy · seam · state · adaptation, per pattern), mechanized by `bin/composition-check.py`.

**The three tiers** (A4's first decision — `composition-check.py`'s tier-consistency gate):

| Tier | What it is | Owned by |
|---|---|---|
| **Primitive** | an atomic control — composes no other `x-*` (button · input · select / menu · spinner) | a single **contract card** (the families above + the REALIZE geometry law) — the leaf |
| **Component** | a composition of primitives + a **seam** (named slots · a slot-presence grid · an overflow mechanism) | A4 — the **component** patterns (toolbar+overflow, card, modal) |
| **Module** | a whole embedded **workflow** — components in regions, with cross-component state | A4 — the **module** patterns (settings nav+content, master-detail, wizard); the *app shell* hands UP to layout-decomposer |

**The seam is a gate.** A "component" whose children are hardcoded — no slots, no slot-presence
adaptation, no overflow story — is **boxed but inert**: it renders once and breaks the moment content
varies. The **slot-presence → grid-columns** mapping (an *absent* slot leaves *no* phantom column) is
the one deterministic joint, so it's routed to code like the geometry law. A capacity-constrained axis
carrying many actions **must** declare an overflow mechanism (priority-ordered collapse into a menu,
the *same* actions projected, one source of truth — never two hand-kept lists).

**Cross-component state folds into REALIZE.** The wire mechanics — value flows *up*, control flows
*down*, cross-piece coordination (a modal's `open`, the settings nav↔content selection, the toolbar's
overflowed set) lives at the **lowest common parent**, never duplicated — are the cross-component
notes on **B3 (semantics/state)** and **B4 (interaction/reflow)**. State authored twice (a modal that
owns its own `open` *and* a parent that owns one) is the cross-component defect.

**A5 / the up-handoff.** Spacing *between* pieces is the parent composition's `gap` / region grid — a
self-owned outer margin is the most common composition-wide drift (the same no-outer-margin rule the
single component obeys). The **module is the largest thing this skill owns**; the *page* it lives in —
the fixed app shell, the header/nav/canvas/footer region grid, which archetype it is — hands **UP to
[layout-decomposer](../layout-decomposer/SKILL.md)**. A5 checks only *"does this module cohere as one
workflow and fit the slot the shell hands it"*; a module that fights its frame is an A5 finding **and**
a hand-up. (Down the other way: anything *inside* one element — its parts, padding, ARIA — is the
single-component REALIZE concern; cite the leaf's contract, don't re-derive it.)

## §SelfAudit

- **Geometry is arithmetic, not taste.** The paddings, the squareness, the pill radius, and the
  composed insets are *computed* from `(height − glyph)/2` and the ramp — run `geometry-check.py`,
  don't eyeball them. A glyph-only button that isn't square, or a symmetric padding that ignores
  icon ≠ caret, is a gate failure, not a preference.
- **The native-parity budget is non-negotiable.** Every native affordance you drop by refusing
  `<input>/<button>/<select>/<textarea>` (autofill, the mobile picker, forced-colors, the focus
  ring, label association, IME) is a line item you must rebuild and prove. The skill *prices* the
  constraint; it never pretends it's free.
- **Gates before reviews, always.** A mis-layered, off-ramp, or form-naive component can't earn
  composition or fidelity scores. Stop each axis at its first failed gate.
- **Two scores, never one.** Report Compose and Realize separately and name the quadrant cell.
  Averaging *designed-right-built-wrong* with *built-right-designed-wrong* hides which you have —
  and they need opposite fixes (platform/geometry work vs API surgery).
- **Components don't set their own outer margin.** Spacing is the parent's job (a layout primitive's
  `gap`). A self-owned margin is the single most common library-wide drift — flag it every time, at
  the single-component scale **and** between composed pieces (A5).
- **Composition without a seam is a pile.** A "component" whose children are hardcoded — no slots, no
  slot-presence adaptation, no overflow — is **boxed but inert** (it renders once, breaks when content
  varies). The seam (A4) is a gate, not a nicety — run `composition-check.py`. And **don't re-derive
  the leaf**: a primitive's pixels / FACE / keyboard are the single-component REALIZE concern; the
  *app shell* hands UP to layout-decomposer — duplicating either neighbour's scale is a finding.
- **Contract, not code.** This skill locks the contract card (single component), the composition card
  (how they nest + wire), the geometry spec, and the grade — it does not emit the element. Hand the
  locked artifacts to a code author (e.g. the `ui-build-components` peer); speak the host's signals +
  `UIElement`/`UIFormElement` + `@scope`-CSS idiom.

## Verify Target

A **component** is **done** when: it sits at the right layer with named, `::part`/slot/`:state()`-exposed
anatomy; its geometry passes `geometry-check.py` (on the ramp, derived paddings, glyph-only square,
composed insets); it's an autonomous element with role via `ElementInternals` and — if it bears a
value — is form-associated with a `setValidity` story; the APG keyboard + focus contract and
`@media (forced-colors: active)` are present; SSR/theming/icon strategy are declared; and both axes
score ≥4 with zero gate failures, landing in the **SHIPPABLE** quadrant. **NOT done** when: the API
is clean but the pixels are off the ramp, it submits nothing in a form, or it vanishes in forced
colors (*designed right, built wrong*); or it's exact and accessible but prop-exploded,
outer-margined, or mis-layered (*built right, designed wrong*); or anatomy is named that can't be
embodied; or one blended score is reported.

A **composition** (how components nest + wire) is **done** when: every piece sits at the right tier
with a clean boundary; the containment tree is named (module → regions → components → slots →
primitives); each component has a real **seam** (named slots / a slot-presence grid / an overflow that
keeps every action reachable); cross-component state flows one way with a single source of truth at the
lowest common parent; it adapts (reflow / overflow / slot-presence / empty-loading-error); it owns only
its insides (no outer margin); the leaf contracts are cited (not re-derived) and the app shell is handed
UP to layout-decomposer; `composition-check.py` passes; and both axes score ≥4 with zero gate failures.
**NOT done** when: the pieces are cleanly boxed but the overflow never collapses, the slots are static,
or state is authored twice (*boxed but inert* — built right, designed wrong at A4); or everything works
but a god-component swallows five concerns, a "component" is really a module, or boundaries leak; or a
tier is named the piece can't embody.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Compose × Realize), the leveled walk (A1–A5 × B1–B5) with gates, the defect quadrant, and the DESIGN / DECOMPOSE / GRADE workflows |
| `references/geometry-system.md` | **any geometry / sizing / spacing question** — the `(height − glyph)/2` law, the XS–2XL ramp (free + derived), the box model and eight permutations, radius, badges/tags, composed container padding, and the CSS-token idiom; mechanized by `bin/geometry-check.py` |
| `references/platform-baseline.md` | **the Realize axis / any element, FACE, SSR, or modern-CSS question** — autonomous elements, ElementInternals/FACE, APG + the native-parity budget, DSD/SSR, theming, icons, and the June-2026 Baseline/feature-detect table (anchor positioning, Popover API, view transitions) |
| `references/api-policy.md` | **the Compose axis / API or governance question** — the layering model + primitive-vs-composition rule, slots-vs-props, boolean-prop explosion, compound + controlled/uncontrolled, naming/versioning/deprecation, the definition-of-done, and the contract-card shape |
| `references/attributes-as-api.md` | **A3 for a custom element** — the four-channel surface (typed attributes + reflection · declared-vs-manual properties · semantic events · the FACE value channel) and the lazy-upgrade / `upgradeProperty` hazard the contract linter checks |
| `references/family-controls.md` | **a form control** — button · select/combobox · checkbox · switch · radio · textarea-like: anatomy, states, role, keyboard, FACE contract, and the geometry they share |
| `references/family-overlays.md` | **a top-layer surface** — modal card · menu · popover · drawer · tooltip · toast: the focus-behavior spine, Popover API + anchor positioning, and composed-padding cards |
| `references/composition-patterns.md` | **the A4/A5 composition scale / any nest · seam · slot · overflow / tier question** — the primitive → component → module tier ladder's recipe library (toolbar+overflow, card, modal; settings nav, master-detail, wizard), each with anatomy · seam · state · adaptation, plus the leaf-DOWN / app-shell-UP boundaries; mechanized by `bin/composition-check.py` |
| `bin/geometry-check.py` | **mechanizes B1** — holds the ramp + the `(height − glyph)/2` law; `ramp` prints it, `layout <SIZE> <slots>` lays out a permutation, `validate <file>` checks a declared geometry, `selftest` proves the law against the source table |
| `bin/component-contract-check.py` | **mechanizes A1/A2/B2/B3/B4** (the single-component contract card) — lints a `*.contract.json` card (hyphenated tag, layer, parts, FACE, APG-keyboard minimum, forced-colors; warns on boolean-prop explosion + self-owned margin); `selftest` over good/bad fixtures |
| `bin/composition-check.py` | **mechanizes A4/A5** (the multi-component composition card) — lints a `*.composition.json` card: tier-consistency (no tier-skips, no god-components), the seam gate, overflow-declared on a constrained axis, no self-margin; `slot-grid` emits the slot-presence → grid-template-columns mapping; `selftest` over good/bad fixtures |
