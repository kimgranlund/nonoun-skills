# SPEC — "Attributes as API" for `component-decomposer`

**Status:** draft · **Target skill:** `design-skills/skills/component-decomposer` · **Axis:** Compose
**A3 (API surface)** + the contract card + `bin/component-contract-check.py`.

## Intent

The Compose axis grades A3 (API surface) at the level of *slots-vs-props · variants-not-booleans ·
boolean-prop explosion · controlled/uncontrolled* (`references/api-policy.md`). That is correct but
**incomplete for a custom element**, whose API *is* its **attributes / properties / reflection /
events** surface — a platform-precise contract with failure modes the current A3 can't see. Fold the
**"attributes as API"** body of knowledge into the skill so A3 grades the real surface and the
contract card + linter check it mechanically.

This spec is **knowledge + technique transfer**, not a new axis. The two-axis method, the gates, and
the geometry foundation are unchanged.

## Motivation (the gap, with evidence)

A custom element's authored surface is four coupled channels, and the skill currently names only the
first loosely:

1. **Attributes** — the HTML surface; *typed* (`string|number|boolean|enum|json`), with a **reflection
   direction** (property→attribute or not) and a default. `enum` attributes have a closed value set.
2. **Properties** — the JS surface; some are **declared** (prop-system backed), some are
   **hand-written accessors** (`value` with sanitize/caret guards). The attribute↔property↔reflection
   relationship is the contract, and it has a real, repeatable bug.
3. **Events** — also API; must be the **semantic** set (`change`/`input`/`open`/`close`/`select`),
   never implementation names.
4. **Form value (FACE)** — for a value-bearing control, the value channel is the *primary* API:
   dirty-value semantics, `value` typically **non-reflecting**, a `setValidity` story.

**The load-bearing failure mode the current A3 misses** (rce ledger-12, reproduced + fixed): a
template `.prop=` binding commits on a cloned element **before** custom-element upgrade → the value
lands as a **shadowing own data property** the class accessor never sees → the component renders
empty/stale, but **only under dynamic subtree insertion** (static HTML upgrades children-first and
hides it). The fix is an explicit **`upgradeProperty(...names)`** for every *hand-written* accessor.
Declared props are handled by the prop system; manual accessors are the gap. A clean API review that
doesn't know this passes a component that is broken in the one case a test rarely covers.

## Scope

**In:**
- A new reference `references/attributes-as-api.md` — the four-channel model, the typed-attribute
  table, the reflection-direction rules, FACE value semantics, events-as-API, and the
  manual-accessor / lazy-upgrade hazard with its corrective.
- An **enriched contract card** (`*.contract.json`): a typed `attributes` table and a `properties`
  list carrying `manual`/`readonly`, plus an `events` list — **backward-compatible** (old flat
  `props`/`boolean_props` still parse; new fields are additive).
- New `bin/component-contract-check.py` checks (below).
- A3 rubric wiring in `references/decomposition-method.md` (+ the A3 line in `api-policy.md`).

**Out (non-goals):**
- No change to the geometry foundation, B-axis, gates, or the two-score reporting.
- Not framework-specific: rce is the evidence source, but the model is stated in platform terms
  (attributes/properties/reflection/`ElementInternals`), portable to any custom-element library.
- The skill stays **contract, not code** — it grades the descriptor; it does not emit `upgradeProperty`.

## Deliverables & acceptance criteria

**D1 — `references/attributes-as-api.md`** exists and states, each as a decision rule:
- the four channels and which is primary for a value-bearing control;
- the typed-attribute table (`type ∈ {string,number,boolean,enum,json}`; `enum ⇒ values`; default; reflect direction);
- attribute kebab-case ↔ property camelCase; events semantic-only (cross-links `api-policy.md` A5);
- **the manual-accessor / lazy-upgrade hazard**: symptom (empty only on dynamic insertion), cause
  (own-property shadow before upgrade), rule — *every hand-written property accessor must be listed
  `manual:true` and re-applied through the accessor at connect*.

**D2 — enriched contract card.** The card schema (documented in `api-policy.md` §"The contract card")
gains:
```jsonc
"attributes": { "size": { "type": "enum", "values": ["sm","md","lg"], "reflect": true },
                "value": { "type": "string", "reflect": false } },
"properties": [ { "name": "value", "manual": true }, { "name": "checked", "readonly": false } ],
"events":     ["change", "input"]
```
Old cards (flat `props`/`boolean_props`, no `attributes`) **still lint clean** (the new fields are optional).

**D3 — linter checks** (`component-contract-check.py`, with `selftest` fixtures, all green):
- **fail** when an attribute is `type:"enum"` with no `values` (closed set required);
- **warn** when a `properties[]` entry is `manual:true` but the component declares no upgrade story —
  the ledger-12 surface (a marker field, e.g. `"upgrades_manual_props": true`, satisfies it);
- **warn** when an `events[]` name is outside the semantic set (implementation-named event);
- **warn** when `value` is listed reflecting (`reflect:true`) on a form-associated control (dirty-value
  smell). All existing checks unchanged; `python3 bin/check-skills.py` stays green.

**D4 — A3 wiring.** `decomposition-method.md`'s A3 review references `attributes-as-api.md`; the A3
score cannot reach **5** while a `manual:true` property has no upgrade story (it is the
*designed-right/built-wrong* defect in API form). `api-policy.md` §A3 gains a one-paragraph pointer.

## Definition of done

`bin/check-skills.py` green; `component-contract-check.py selftest` green incl. the new fixtures
(enum-without-values fails; manual-without-upgrade warns; old flat card still clean); the four
deliverables present; SKILL.md's reference table lists `attributes-as-api.md`.

## Provenance (the rce source artifacts)

- `docs/component-api-contract.json` — the worked descriptor schema this generalizes (tag · tier ·
  extends · **attributes** · **properties** [`manual`/`readonly`] · **events** · slots · parts ·
  customStates · **face** · aria[role+labelSource] · keyboard · geometry · forcedColors).
- `docs/component-evaluation-rubric.md` — the A1–A5 / B1–B5 grade; the `ui-button` worked grade.
- rce **ledger-12** — the lazy-property / `upgradeProperty` bug + the probe that now catches it
  (the empirical basis for the D3 manual-accessor warning).
