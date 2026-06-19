# Changelog — component-decomposer

All notable changes to this skill are recorded here. Versioned independently of the `design-skills`
plugin; the gate (`bin/check-skills.py`) must pass for any release.

## 0.3.1 — beta

**The compact / dense realm** — folded in from the upstream geometry spec
(`fable-tests/reactive-components/docs/geometry-sizing-spec.md` §5.1/§5.2). The compact controls (kbd,
slider, slider-multi, radio, switch, tag, badge, chip, checkbox) are now modeled as a **separate size
system**, not "a small button":

- `bin/geometry-check.py` gains the **two-band compact box ramp** (`COMPACT_RAMP` — the `ui-*` tight lane
  12·14·16·18·20, the `content-*` generous lane 18·20·22·24·26·28·32), a `compact-ramp` subcommand, and
  compact-card validation (box-on-ramp + rejects the comfortable `h/2` pad misused on a compact control).
  Selftest locks both bands + the validation. **The comfortable button ramp is untouched.**
- `references/geometry-system.md` replaces the old "badges & tags map onto the button ramp" claim with
  the compact realm (the two-band ramp, keep-the-compact-pad-not-`h/2`, density-on-rhythm), and records
  the ramp's **sublinear power-law** generating rule (`icon ≈ 2.49·h^0.58`, `font ≈ 2.65·√h`,
  `caret = font`) plus the frame/rhythm families (`caret = font`, `gap = font/2`).
- `references/family-controls.md`: checkbox/switch geometry now points at the compact ramp.

## 0.3.0 — beta

**Absorbed the composition scale** — merged the composition layer of the untracked v0.1 `ui-decomposer`
draft INTO this skill, then retired the draft. component-decomposer now grades a **single component AND
how components nest + wire (compose) up to the module**, on the *same* COMPOSE × REALIZE axis pair (no
second axis added). The decision: ONE skill covers a component and its composition; the draft is gone.

What folded in, by where it landed:

- **A4 Composition / A5 Coherence deepened** (`SKILL.md` + `references/decomposition-method.md`): A4 now
  carries the **tier ladder** (primitive → component → module), the **seam** (named slots · the
  slot-presence grid · the overflow mechanism) as a `[gate, code]` joint, and the **god-component**
  defect; A5 carries the no-self-margin rule between composed pieces and the **up-handoff** — the module
  is the largest scale this skill owns; the *app shell / page region grid* hands UP to layout-decomposer.
  The **wire/seam mechanics** (cross-component state at the lowest common parent; overflow reflow /
  slot-presence adaptation) fold into REALIZE's **B3 (semantics/state)** and **B4 (interaction)** as
  cross-component notes — *not* a new axis.
- **New `references/composition-patterns.md`** (from the draft): the tier-ladder recipe library —
  component patterns (toolbar+overflow, card, modal) and module patterns (settings nav+content,
  master-detail, wizard), each with anatomy · seam · state · adaptation, plus the leaf-DOWN /
  app-shell-UP boundaries (the useful content from the draft's `handoffs.md`, folded in here rather than
  copied as a stray doc).
- **New `bin/composition-check.py`** (from the draft, reframed to COMPOSE A4/A5 vocabulary): the
  **multi-component composition-card gate** — complements `component-contract-check.py` (the
  single-component contract card). Lints a `*.composition.json` card: tier-consistency · the seam gate ·
  overflow-declared · god-component fanout · no self-margin; `slot-grid` emits the deterministic
  slot-presence → grid-template-columns mapping. `selftest` green (6 fixtures + the slot-grid law).
- **`examples/walkthrough.md`** gains a second worked example — a toolbar+overflow on COMPOSE × REALIZE,
  where the A4 seam gate catches a fake overflow (the *built-right-designed-wrong* / boxed-but-inert
  composition defect), salvaged from the draft's walkthrough.
- **Description + corpus**: the frontmatter description now reads "a component AND how components nest +
  wire up to the module"; the corpus gains composition positives (nest, the toolbar↔overflow seam, a
  god-component, slot-presence) and sharpened layout-decomposer negatives (app shell / page region grid
  / archetype) so the module→shell boundary stays fenced and does not collide with layout-decomposer.
- `skill.json` `files[]` registers the two new files; three `bin/` selftests now run (geometry · contract
  · composition).

## 0.2.1 — beta

**Attributes as API** folded into the Compose A3 surface (spec: `spec/attributes-as-api.spec.md`).
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
