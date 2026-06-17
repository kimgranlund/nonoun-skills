# Changelog — component-decomposer

All notable changes to this skill are recorded here. Versioned independently of the `design-skills`
plugin; the gate (`bin/check-skills.py`) must pass for any release.

## 0.2.1 — beta

**Attributes as API** folded into the Compose A3 surface (from `docs/specs/attributes-as-api.spec.md`).
A custom element's public API is its typed **attributes** (+ reflection), declared-vs-manual
**properties**, semantic **events**, and the **form-value** channel — not just a prop list.

- New `references/attributes-as-api.md`: the four-channel model, the typed-attribute table, the
  reflection rules, events-as-API, and the **manual-accessor / lazy-upgrade hazard** (a `.prop=`
  binding committing before upgrade as a shadowing own property → empty/stale only under dynamic
  insertion; corrective: `upgradeProperty`).
- The contract card gains an additive, backward-compatible `attributes` / `properties` / `events` /
  `upgrades_manual_props` block (old flat `props` cards still lint clean).
- `bin/component-contract-check.py` (new checks, selftested): **FAIL** on an enum attribute with no
  `values`; **WARN** on a `manual:true` property with no upgrade story, an implementation-named event,
  or a form control reflecting its `value`.
- A3 wiring: A3 cannot score 5 while a `manual:true` property has no upgrade story (the
  *designed-right, built-wrong* defect in API form).

## 0.2.0 — beta

Promoted to beta as part of the marketplace **v0.2.0** milestone (see the root CHANGELOG). This cycle the skill gained a checked-in, sibling-collision-tested routing-eval corpus, an adversarial-review hardening pass (fixes locked as selftest fixtures), and a worked `examples/walkthrough.md` (a red→green bin proof).

## 0.1.0 — draft

Initial release. Decompose / design / grade zero-dependency web components on the **COMPOSE ×
REALIZE** crossing axes, scored separately with a gated rubric and the opposite-defect quadrant.

- **The two-axis method** (`references/decomposition-method.md`): Compose (layer → anatomy → API →
  composition → coherence) × Realize (geometry → element → semantics → interaction → fidelity),
  crossing at the component contract; gates before reviews; the *designed-right-built-wrong* vs
  *built-right-designed-wrong* quadrant.
- **The geometry foundation** (`references/geometry-system.md` + `bin/geometry-check.py`): the
  `(height − glyph)/2` padding law, the XS–2XL ramp (free: height/icon/caret/font/spacer; derived:
  paddings, pill radius, composed insets), the box model + eight permutations, square icon-only
  buttons, badges/tags as a smaller scale, composed container padding. The engine's `selftest`
  proves the law against the hand-authored source table.
- **The contract linter** (`bin/component-contract-check.py`): lints a `*.contract.json` card —
  hyphenated tag, layer, parts, FACE for controls, APG-keyboard minimum, forced-colors; warns on
  boolean-prop explosion and self-owned outer margin.
- **Platform baseline** (`references/platform-baseline.md`): autonomous elements,
  ElementInternals/FACE, the native-parity budget, DSD/SSR, theming, icons, and the June-2026
  Baseline/feature-detect table (anchor positioning, Popover API, view transitions).
- **API & library policy** (`references/api-policy.md`): layering + primitive-vs-composition rule,
  slots-vs-props, boolean-prop explosion, compound + controlled/uncontrolled, naming/versioning/
  deprecation, the 10-point definition-of-done.
- **Family recipes**: `family-controls.md` (button · select · checkbox · switch · radio ·
  textarea-like) and `family-overlays.md` (modal card · menu · popover · drawer · tooltip · toast).
- Authored against the signals + `UIElement`/`UIFormElement` + `@scope`-CSS idiom of the reference
  libraries (`fable-tests/reactive-components`, `adia/gen-ui-kit`).
