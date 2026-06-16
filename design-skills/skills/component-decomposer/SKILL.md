---
name: component-decomposer
description: >
  Decompose, design, and grade zero-dependency web components (Custom Elements, signals, FACE, no
  native form elements) on two crossing axes — COMPOSE (layer → anatomy → API → composition) and
  REALIZE (geometry → element → semantics → interaction → fidelity) — scored separately so a clean
  API can't hide a broken control. Backed by a gated rubric, a deterministic geometry engine (the
  (height-glyph)/2 padding law, the XS–2XL ramp, square icon-only buttons), a contract-card linter,
  and recipes for controls and overlays (modal cards, menus, custom selects, popovers). Carries the
  June-2026 platform baseline: FACE/ElementInternals, anchor positioning, the Popover API, view
  transitions, declarative-shadow-DOM SSR, and the native-parity budget. Use when designing a
  component library, fixing a component's geometry/parts/API, building a pattern with no native form
  element, or grading a component. NOT for code generation
  (ui-build-components), app-shell layout (layout-decomposer), or token math (ui-build-tokens).
---

# component-decomposer — design a component on two crossing axes

A building-block component is **correct on two independent axes that walk the same hierarchy in
opposite directions** — the same outside-in / inside-out seam the [layout-decomposer](../layout-decomposer/SKILL.md)
applies to space and the [mermaid-decomposer](../mermaid-decomposer/SKILL.md) applies to a diagram,
here applied to a zero-dependency web component:

- **Compose · whole → part** grades the **abstraction**: the layer → its anatomy (named parts) → its
  API surface → how it composes upward → its coherence with the library.
- **Realize · part → whole** grades the **embodiment**: its exact geometry → the custom element → its
  platform semantics (ARIA/FACE) → its interaction contract → its rendered fidelity.

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

**Modes:** **DESIGN** (Compose-down → Realize-up → reconcile at the contract → hand off to a code
peer) · **DECOMPOSE** (read a component → layer + anatomy + realization walk + grade) · **GRADE**
(score both axes against the rubric, gates before reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Compose** | whole → part | **A1** Layer → **A2** Anatomy → **A3** API → **A4** Composition → **A5** Coherence | "Is it the *right component*, shaped to compose?" |
| **B · Realize** | part → whole | **B1** Geometry → **B2** Element → **B3** Semantics → **B4** Interaction → **B5** Fidelity | "Does it *render exact and work*, here, with no native control?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on
that axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable component is **≥4 on every review
with zero gate failures**, reported as two separate axis scores plus the defect quadrant. Two gates
route to code: **B1 geometry** → `bin/geometry-check.py`; **A1/A2/B2/B3/B4 contract** →
`bin/component-contract-check.py`.

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
  `gap`). A self-owned margin is the single most common library-wide drift — flag it every time.
- **Contract, not code.** This skill locks the contract card, the geometry spec, and the grade — it
  does not emit the element. Hand the locked contract to a code author (e.g. the `ui-build-components`
  peer); speak the host's signals + `UIElement`/`UIFormElement` + `@scope`-CSS idiom.

## Verify Target

A component is **done** when: it sits at the right layer with named, `::part`/slot/`:state()`-exposed
anatomy; its geometry passes `geometry-check.py` (on the ramp, derived paddings, glyph-only square,
composed insets); it's an autonomous element with role via `ElementInternals` and — if it bears a
value — is form-associated with a `setValidity` story; the APG keyboard + focus contract and
`@media (forced-colors: active)` are present; SSR/theming/icon strategy are declared; and both axes
score ≥4 with zero gate failures, landing in the **SHIPPABLE** quadrant. **NOT done** when: the API
is clean but the pixels are off the ramp, it submits nothing in a form, or it vanishes in forced
colors (*designed right, built wrong*); or it's exact and accessible but prop-exploded,
outer-margined, or mis-layered (*built right, designed wrong*); or anatomy is named that can't be
embodied; or one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Compose × Realize), the leveled walk (A1–A5 × B1–B5) with gates, the defect quadrant, and the DESIGN / DECOMPOSE / GRADE workflows |
| `references/geometry-system.md` | **any geometry / sizing / spacing question** — the `(height − glyph)/2` law, the XS–2XL ramp (free + derived), the box model and eight permutations, radius, badges/tags, composed container padding, and the CSS-token idiom; mechanized by `bin/geometry-check.py` |
| `references/platform-baseline.md` | **the Realize axis / any element, FACE, SSR, or modern-CSS question** — autonomous elements, ElementInternals/FACE, APG + the native-parity budget, DSD/SSR, theming, icons, and the June-2026 Baseline/feature-detect table (anchor positioning, Popover API, view transitions) |
| `references/api-policy.md` | **the Compose axis / API or governance question** — the layering model + primitive-vs-composition rule, slots-vs-props, boolean-prop explosion, compound + controlled/uncontrolled, naming/versioning/deprecation, the definition-of-done, and the contract-card shape |
| `references/family-controls.md` | **a form control** — button · select/combobox · checkbox · switch · radio · textarea-like: anatomy, states, role, keyboard, FACE contract, and the geometry they share |
| `references/family-overlays.md` | **a top-layer surface** — modal card · menu · popover · drawer · tooltip · toast: the focus-behavior spine, Popover API + anchor positioning, and composed-padding cards |
| `bin/geometry-check.py` | **mechanizes B1** — holds the ramp + the `(height − glyph)/2` law; `ramp` prints it, `layout <SIZE> <slots>` lays out a permutation, `validate <file>` checks a declared geometry, `selftest` proves the law against the source table |
| `bin/component-contract-check.py` | **mechanizes A1/A2/B2/B3/B4** — lints a `*.contract.json` card (hyphenated tag, layer, parts, FACE, APG-keyboard minimum, forced-colors; warns on boolean-prop explosion + self-owned margin); `selftest` over good/bad fixtures |
