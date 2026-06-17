# The two-axis method — COMPOSE × REALIZE

A component is **correct on two independent axes that walk the same hierarchy in opposite
directions** — the same outside-in / inside-out seam the layout-decomposer applies to space and
the mermaid-decomposer applies to a diagram, here applied to a building-block component.

- **Compose · whole → part** grades the **abstraction**: the layer it sits at → its anatomy (named
  parts) → its API surface → how it composes upward → its coherence with the rest of the library.
  *"Is it the right component, shaped to compose?"*
- **Realize · part → whole** grades the **embodiment**: its exact geometry → the custom element →
  its platform semantics (ARIA/FACE) → its interaction contract → its rendered fidelity.
  *"Does it render exact and actually work — no framework, no native form element?"*

They **cross at the component contract** — the contract is *both* the abstraction (a named part with
an API) *and* the embodiment (a real box with exact pixels, an `ElementInternals`-bearing element,
a keyboard map). That crossing is the whole technique. A component can be:

- **designed right, built wrong** — clean layer, clean anatomy, elegant API, but the geometry is off
  the ramp, it submits nothing in a form (no FACE), it traps no focus, or it vanishes in Windows
  High Contrast. *Good idea, bad build.*
- **built right, designed wrong** — pixel-exact, accessible, form-associated, renders perfectly —
  but a boolean-prop explosion, a baked-in outer margin, a wrong layer. Works in isolation, **rots
  the library**. *Good build, bad idea.*

Opposite defects, opposite fixes — so you **score and report the two axes separately, never
averaged**. An averaged "3/5" hides which of the two you have.

## The leveled walk

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Compose** | whole → part | **A1** Layer `[gate]` → **A2** Anatomy `[gate]` → **A3** API surface → **A4** Composition → **A5** Coherence | "Is it the *right component*, shaped to compose?" |
| **B · Realize** | part → whole | **B1** Geometry `[gate, code]` → **B2** Element `[gate]` → **B3** Semantics `[gate]` → **B4** Interaction → **B5** Fidelity | "Does it *render exact and work*, here, with no native control?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** — a failure cascades and BLOCKS the reviews below it
on that axis (you can't judge an API that's mis-layered, or fidelity for an element that never
attaches internals). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable component is **≥4 on
every review with zero gate failures**, reported as two separate axis scores plus the quadrant.

Two gates route to code, never inference:
- **B1 Geometry** → `bin/geometry-check.py` (the ramp + the `(height − glyph)/2` law). See
  `geometry-system.md`.
- **A1/A2/B2/B3/B4 contract** → `bin/component-contract-check.py` (layer, parts, FACE, role,
  APG-keyboard minimum, forced-colors). See `api-policy.md` and `platform-baseline.md`.

### A · Compose (whole → part)

- **A1 Layer `[gate]`** — is it placed at the right tier: **token** (a raw/aliased value), **primitive**
  (token-only API, no domain name — `box`, `stack`, `cluster`, `grid`), **component** (a named, skinned
  widget — `button`, `select`, `card`), or **pattern** (a reusable composition of components — a
  modal card, a form field)? A `Card` is not a primitive; a `Stack` is not a component. Mis-layering
  poisons every decision below. (Decision rule in `api-policy.md`.)
- **A2 Anatomy `[gate]`** — are the parts named, and is every styleable part exposed (a `::part`, a
  slot, or a `:state()`)? A button is `[ icon? · label? · caret? ]`; a select is `[ trigger · value ·
  listbox · option · indicator ]`. Anatomy you can't name you can't theme, compose, or test.
- **A3 API surface `[review]`** — props-vs-slots discipline (config the common + finite, slot the
  open-ended), orthogonal `variant` × `size` enums (not multiplied booleans), controlled/uncontrolled,
  event payload contracts. For a custom element the API *is* the **attributes-as-API** surface — typed
  attributes (+ reflection), declared-vs-manual properties, semantic events, the form-value channel
  (`attributes-as-api.md`). **A3 cannot score 5 while a `manual:true` property has no upgrade story**
  (the lazy-upgrade / `upgradeProperty` hazard — *designed-right, built-wrong* in API form).
- **A4 Composition `[review]`** — does it compose *up* without boolean-prop explosion, without owning
  its outer margin, without leaking compound-component state? Does its anatomy nest (a button is also
  the trigger of a select, the item of a menu)?
- **A5 Coherence `[review]`** — naming, the semantic-token contract, size/density attributes, the
  versioning/deprecation surface — does it look like it belongs to the same library as its siblings?

### B · Realize (part → whole)

- **B1 Geometry `[gate, code]`** — does every dimension sit on the ramp and obey the `(height −
  glyph)/2` law: correct height/icon/caret/font/spacer for its size, derived edge paddings,
  icon-only/caret-only **square**, composed container insets? Routed to `bin/geometry-check.py`.
- **B2 Element `[gate]`** — an **autonomous** custom element (never a customized built-in / `is=""` —
  Safari refuses them permanently), hyphenated tag, signals-reactive, lifecycle correct (light DOM by
  default; nothing leaked on disconnect).
- **B3 Semantics `[gate]`** — role/ARIA/`:state()` set via `ElementInternals`; any control is
  **form-associated** (`formAssociated`, `setFormValue` on first render *and* change, a `name`, a
  `setValidity` story). No native `<input>/<button>/<select>/<textarea>` anywhere.
- **B4 Interaction `[review]`** — the APG keyboard + focus contract (roving tabindex vs
  `aria-activedescendant`), and the **native-parity budget**: every native affordance you gave up
  (focus ring, label association, autofill, mobile picker, forced-colors, IME) rebuilt and proven.
  `@media (forced-colors: active)` present.
- **B5 Fidelity `[review]`** — SSR via declarative shadow DOM (adopt-don't-recreate) or light-DOM,
  theming surface (`::part` + custom properties), inline-SVG-in-shadow icons, and graceful
  degradation on the non-Baseline edge (anchor positioning, cross-doc view transitions).

## The opposite-defect quadrant

```
                 B · REALIZE passes        B · REALIZE fails
A · COMPOSE  ┌────────────────────────┬────────────────────────┐
   passes    │      SHIPPABLE         │  designed right,        │
             │  (≥4 every review,     │  built wrong — clean    │
             │   zero gate fails)     │  API, but off-ramp      │
             │                        │  pixels / no FACE /     │
             │                        │  dead in forced-colors  │
             ├────────────────────────┼────────────────────────┤
A · COMPOSE  │ built right, designed  │       REBUILD           │
   fails     │ wrong — accessible &   │                         │
             │ exact, but prop-       │                         │
             │ exploded / outer-      │                         │
             │ margined / mis-layered │                         │
             └────────────────────────┴────────────────────────┘
```

The quadrant **names the fix**: top-right needs platform/geometry work; bottom-left needs API
surgery. Report the cell, not an average.

## Modes

- **DESIGN** — new component. Walk **A-down** (layer → anatomy → API → composition), then **B-up**
  (geometry → element → semantics → interaction → resilience), reconcile at the contract, run both
  `bin/` checks, hand the locked contract card to a code author (e.g. the `ui-build-components`
  peer). Output: a `*.contract.json` card + a geometry spec + the two-axis grade.
- **DECOMPOSE** — read an existing component (code, or a screenshot + measurements). Name its layer
  and anatomy (A1–A2), walk its realization bottom-up (B1–B3), then score the reviews. Output: its
  contract card + a platform/geometry gap list.
- **GRADE** — score both axes against the rubric (`component-rubric.md` lives inline in this file
  via the leveled walk above). Gates first, in cascade order; stop an axis at its first failed gate;
  place the result in the quadrant; name one corrective per failure.

## Walk order (do not skip)

1. **A1 Layer** — name the tier. Wrong tier ⇒ stop, re-place.
2. **A2 Anatomy** — name the parts. Unnamed parts ⇒ name them before anything else.
3. **B1 Geometry** — run `geometry-check.py`. Off the ramp or non-square glyph-only ⇒ fix the
   numbers; they are not negotiable design taste, they are arithmetic.
4. **B2 Element / B3 Semantics** — autonomous element? form-associated control? role via internals?
   Run `component-contract-check.py`. Any gate fail ⇒ fix before reviewing.
5. **Reviews** — A3–A5 then B4–B5, 1–5 each. Below 4 ⇒ name the single corrective.
6. **Report** — two axis scores, the quadrant cell, gate failures first.
