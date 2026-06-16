# Roadmap — component-decomposer

Tracks what's next, in rough priority order. The skill ships its core (the two axes, the geometry
foundation + engine, the contract linter, the controls/overlays families) in 0.1.0; everything below
is additive.

## Reference corpus

- [ ] **`family-disclosure.md`** — tabs · accordion · disclosure · command palette. The
      roving-tabindex vs `aria-activedescendant` axis in depth (the highlight-mechanism spine).
- [ ] **`family-primitives.md`** — box · stack · cluster · grid · card/panel. The no-outer-margin
      law and `gap`-based spacing as the *only* spacing mechanism; how primitives carry the geometry
      ramp (the composed-padding rules already live in `geometry-system.md`).
- [ ] **`field-and-form.md`** — the form *pattern* layer: field (label + control + hint + error),
      fieldset, form-level validity orchestration across FACE controls. Boundary with the
      `ui-compose-forms` peer.

## Geometry engine (`bin/geometry-check.py`)

- [ ] Emit the ramp as **CSS custom properties** (`--c-height`, derived `calc()` paddings) and as a
      **DTCG token** export, so the same source produces docs *and* shippable tokens.
- [ ] **Density** axis (compact / comfortable / spacious) as a multiplier on the free values, with
      the law preserved (re-derive paddings after scaling).
- [ ] **Optical centering** check for stroke-based icons (e.g. carets) where the visual center
      differs from the bounding box — currently treated as a centered glyph.
- [ ] Validate **focus-ring inset / outline offset** against the geometry (ring must not collide
      with neighbours at the tightest size).

## Contract linter (`bin/component-contract-check.py`)

- [ ] Per-role **state completeness** check (a `combobox` card without an `open`/`invalid` state, a
      control without `disabled`).
- [ ] **Compound-component** wiring check (a `*-option` declares its parent `*-select`; orphaned
      parts flagged).
- [ ] **Token-contract** check (a card referencing a non-semantic / primitive token directly).

## Method & routing

- [ ] A **routing-eval corpus** of trigger + adversarial phrases (the maturity step the repo's
      ROADMAP tracks for every skill) — especially the boundary with `ui-build-components` (code),
      `layout-decomposer` (shells), `ui-compose-forms` (form systems), and `ui-audit-coherence`
      (post-hoc drift).
- [ ] A worked **end-to-end DESIGN transcript** (button → select → modal card) as a reference
      example, with its contract cards checked in and dogfooded.
- [ ] **CREATE-from-screenshot** flow: measure a mockup → snap to the nearest ramp size → emit the
      contract card + geometry spec.
