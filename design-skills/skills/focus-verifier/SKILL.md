---
name: focus-verifier
description: Derive and verify focus-ring recipes, hit-target minimums, focus order, and keyboard affordances that satisfy WCAG 2.2 SC 2.5.8 (target size), SC 2.4.11/2.4.13 (focus appearance), and keyboard-only operability. Use when the user needs to check focus order / tab sequence, keyboard navigation and traps, focus management on route change, focus-ring tokens that clear 3:1 under every surface, or hit-area expansions for small interactive elements. NOT for general text/background contrast, palette, or color-blind safety (color-verifier) — this owns only focus-ring contrast; NOT for RTL/bidi, dir/lang on text surfaces, locale Intl formatting, or text-expansion (i18n-verifier); NOT for loading skeleton/spinner, CLS, or perceived-latency budgets (perf-verifier); NOT for destructive-action undo/type-to-confirm or audit-trail UX (safety-verifier); NOT for color-space theory or palette math (color-science); NOT for building a tab-list or menu component (component-decomposer).
---

# focus-verifier

Reasoning skill that owns the **how** of interactive affordances in ui-dev. Focus rings, hit targets, and keyboard affordances are jointly constrained by color (ring contrast), spacing (hit-area expansion), radius (ring offset), and motion (focus transition). Upstream composition skills produce their primitives; this skill resolves the cross-cutting interactive rules — and proves them against WCAG 2.2.


## Invocation

This is a **constraint** decomposition skill. The user needs focus-ring tokens or hit-target sizing. Decompose: (1) read surface color context, (2) derive minimum sizes from WCAG 2.2, (3) compute focus-ring recipes, (4) verify under every surface.

### Step 1 — Ingestion

Classify the ask surface:
- "Focus ring tokens" → derive ring width, offset, and color per surface background
- "Hit-target sizing" → identify minimum 24×24dp targets; flag undersized controls
- "Keyboard affordances" → map shortcut schemes, skip links, focus traps
- "Focus management across routes" → specify focus reset on navigation change

### Step 2 — Decomposition

| Sub-ask | Standard | Verification |
|---|---|---|
| Target size minimum | WCAG 2.2 SC 2.5.8 | 24×24 CSS px min (coarse fine at ≥44×44) |
| Focus ring appearance | WCAG 2.2 SC 2.4.11/2.4.13 | 2px thickness, 2px offset, 3:1 adjacent contrast |
| Focus ring against tinted surface | Dual-color ring pattern | box-shadow: surface-bg then ring-color |
| Keyboard-only op-erability | APG | Every interactive reachable via Tab; no keyboard traps |
| Focus movement on route change | Best practice | Focus moves to h1 or dialog on transition |

### Step 3 — Execution routing

Focus-ring recipes must clear contrast against *every adjacent color* (WCAG SC 1.4.11), not just the background. Small interactive elements (<24×24) require explicit hit-area expansion. All outputs are consumed by `ui-compose-interaction` (state definitions) and `ui-build-theme` (provider overrides).


## When to use

- A surface role needs a focus-ring recipe that clears contrast against every adjacent surface (including dark/light scheme, prefers-contrast).
- An interactive element is visually smaller than the 24×24 CSS px WCAG 2.2 minimum and needs hit-area expansion.
- A keyboard-only user flow needs explicit affordances (skip links, roving tabindex, visible focus on non-default elements).
- User wants to verify an existing UI against WCAG 2.2 SC 2.4.11, 2.4.13, and 2.5.8.

## When NOT to use

- Focus styling for purely presentational containers (no interactivity) — they should not carry focus.
- Pointer-only interactions (drag, hover-reveal) without keyboard equivalents — route to UX work first; affordances cannot rescue a keyboard-inaccessible design.
- Native form controls with default UA styling that already pass — verify first, don't rewrite.

## Rate-limiting factor

**WCAG 2.2 floors are load-bearing, not aesthetic.** The irreducible constraints: SC 2.5.8 mandates ≥24×24 CSS px interactive targets (with documented exceptions); SC 2.4.11 mandates focus indicators with specific contrast and coverage; SC 2.4.13 mandates focus appearance of minimum 2 CSS px thickness and 3:1 contrast against adjacent colors. Designs inside the corridor are accessible; outside, they fail audit regardless of aesthetic.

## First principles

1. **Hit target ≥ visual target.** A 16×16 icon-button must expand hit area to 24×24 via padding or pseudo-element. Small visual + large hit is correct.
2. **Focus ring is a solo indicator, not decoration.** 2px minimum thickness. 3:1 contrast against the adjacent background AND against the element itself. Outline (not box-shadow alone) guarantees paint order.
3. **Focus ring offset depends on radius.** Tight radius → ring hugs shape. Loose radius → ring offsets outward with matching radius. Square-cornered ring on round button reads as broken.
4. **Keyboard affordances are declared, not implicit.** Skip links, visible focus on non-button interactive elements, and roving tabindex are explicit markup, not emergent behavior.
5. **Focus ring color survives both schemes and prefers-contrast.** The ring token must clear 3:1 against EVERY surface it lands on — which usually means two ring colors in one recipe (inner + outer) or a high-contrast default.
6. **Spacing between hit targets matters.** WCAG 2.2 SC 2.5.8 permits smaller-than-24 if targets are separated by ≥24px spacing. Dense toolbars exploit this; careless dense toolbars fail.

## Procedure

### Step 1 — Enumerate interactive roles

From UISchema, list every role that accepts interaction: button, icon-button, link, checkbox, radio, switch, tab, accordion-trigger, menu-item, chip (if interactive), avatar (if interactive), disclosure-trigger, etc.

Flag any role declared `interactive: false` but visually affording interaction — that's a UX bug, not a focus-ring bug.

### Step 2 — Compute hit target per role

Apply target-size rules (see `targets/minimums.json`):

- **Default**: visual size ≥ 24×24 CSS px → pass.
- **Visual < 24×24**: expand hit area via padding or inset pseudo-element to ≥ 24×24; record `hitAreaExpansion` in token.
- **Exception: inline text links**: exempt from 24px rule per WCAG 2.2 SC 2.5.8 inline exception.
- **Exception: spacing exception**: targets < 24px allowed if center-to-center spacing between interactive targets is ≥ 24px.
- **Platform exceptions**: Apple HIG = 44pt hit target; Material Design = 48dp. Prefer the stricter rule if targeting those platforms.

### Step 3 — Design focus-ring recipe

Focus ring has three canonical recipes (see `focus-ring/recipes.json`):

- **Outer ring** (default): 2px solid outline, offset equal to half the element's radius, color = brand accent or high-contrast neutral. Contrast ≥ 3:1 against adjacent surface.
- **Inner-outer double ring**: 2px inner (element color) + 2px outer (accent). Used when element surface and page surface are both likely ring colors (e.g., a button on a colored banner).
- **Inset ring**: 2px solid inset for elements that cannot paint outside their bounds (full-width list items, iframes). Offset inward.

Never: box-shadow alone (paint order issues), dotted lines below 2px (antialiasing noise), color-only focus (fails SC 2.4.11).

### Step 4 — Resolve ring offset per radius

Ring offset follows a table (see `offsets/per-surface.json`):

| Element radius | Ring offset | Ring radius                     |
|----------------|-------------|--------------------------------|
| radius-none    | 2px         | 0                              |
| radius-sm (4)  | 2px         | element-radius + offset = 6    |
| radius-md (8)  | 2px         | element-radius + offset = 10   |
| radius-lg (12) | 3px         | element-radius + offset = 15   |
| radius-xl (16) | 4px         | element-radius + offset = 20   |
| radius-pill    | 2px         | pill (always fits)             |
| radius-circle  | 2px         | circle                         |

Offset grows slightly with radius to maintain optical separation.

### Step 5 — Color the ring

Focus-ring color must clear 3:1 against every surface it lands on (see `focus-ring/recipes.json::coloring`):

- **Default**: `var(--color-accent-600)` (light scheme) / `var(--color-accent-400)` (dark scheme).
- **On tinted surface**: ring color swaps to high-contrast neutral (`--color-neutral-1000` on light tint, `--color-neutral-0` on dark tint).
- **prefers-contrast escalation**: ring thickness → 3px; color switches to `CanvasText` system color.
- **Forced colors mode** (Windows HC): rely on `outline: 2px solid CanvasText` — all custom ring colors ignored.

### Step 6 — Wire focus-ring motion

Focus-ring transitions (see `ui-compose-motion`):

- Role: `--motion-focus-ring`.
- Duration: `duration-fast` (100ms).
- Easing: `move`.
- Property: `outline-offset` and `outline-color` only — never `outline-width` (width changes cause layout jitter).
- Under `prefers-reduced-motion`: remove offset transition; keep color transition at 80ms (feedback).

### Step 7 — Keyboard affordances

For each interactive role, declare (see `keyboard/affordances.json`):

- **Tab order**: included in default tab flow or managed via roving tabindex (e.g., toolbars, menus, grids).
- **Activation key**: Space, Enter, both, or custom.
- **Escape behavior**: dismisses layer (dialog, popover, menu) when open.
- **Arrow-key navigation**: for composite widgets (menu, listbox, tabs, radiogroup).
- **Skip link**: page-level requirement — first focusable element is a visible "Skip to content" link.

Defaults per role map to WAI-ARIA Authoring Practices.

### Step 8 — Emit

Each interactive-role token:

```ts
{
  name: "--interactive-button",
  role: "button",
  visualSizePx: { minW: 32, minH: 32 },
  hitAreaPx:   { minW: 32, minH: 32, expansion: null },
  focusRing: {
    recipe: "outer",
    widthPx: 2,
    offsetPx: 2,
    colorLight: "var(--color-accent-600)",
    colorDark:  "var(--color-accent-400)",
    radius: "element-radius + 2"
  },
  keyboard: {
    tabbable: true,
    activationKeys: ["Enter", "Space"],
    escapeBehavior: null
  },
  motion: "--motion-focus-ring",
  a11y: { wcag248Pass: true, wcag2411Pass: true, wcag2413Pass: true }
}
```

### Step 9 — Verification

- Visual size OR hit-area expansion ≥ 24×24 (with exceptions documented).
- Focus-ring thickness ≥ 2px.
- Focus-ring contrast ≥ 3:1 against every surface it lands on (light + dark + prefers-contrast).
- Focus-ring color survives forced-colors mode.
- Keyboard affordance declared per role.
- Motion respects prefers-reduced-motion.

## Invariants

1. **Hit area ≥ 24×24 CSS px** (or inline-text exception or spacing exception documented).
2. **Focus ring ≥ 2px thick.**
3. **Focus ring ≥ 3:1 contrast against every surface it lands on, in every scheme.**
4. **Ring offset scales with element radius** per offset table.
5. **Every interactive role declares tab order + activation keys.**
6. **Focus-ring motion runs under prefers-reduced-motion** (at capped duration; this is feedback).
7. **Forced-colors mode falls back to system colors** (no custom ring color relied upon).


- **INV-FOC-001** — Every proof cites specific schema paths or CSS rules it evaluates (enforcement: convention)
- **INV-FOC-002** — Remediation suggestions are scoped to the schema/artifact that can fix them (enforcement: convention)

## Typed Interface

**Domain:** `ui-design`

**Consumes:** Relevant schemas and artifacts.

**Produces:** `FocusAndHitTargetsProof` — constraint-satisfaction proof or violation report.

**Invariants:** Evaluations cite schema paths or CSS rules; remediation suggestions scoped to fixable artifact.

**Downstream:** `ui-audit-quality`.

## Anti-patterns this skill refuses

- `outline: none` without replacement focus indicator — strips SC 2.4.11 compliance.
- Focus indicated by background-color change alone — fails on tinted backgrounds.
- Hit areas smaller than 24×24 without inline/spacing exception documented.
- Box-shadow focus rings that get clipped by parent `overflow: hidden`.
- Custom tab order via positive tabindex values — breaks keyboard expectations.
- Hover-only affordances for interactive elements — keyboard users cannot trigger.
- Ring color that passes contrast in light but fails in dark scheme (or vice versa).
- Identical ring treatment for button-on-surface and button-on-accent (one will fail contrast).
- Relying on `:focus` rather than `:focus-visible` for pointer users — creates ring flash on click.
- Animating `outline-width` — causes layout jitter.

## Handoff

- `color-verifier` provides accent and neutral ramps used for ring color; provides contrast-verification primitives.
- `ui-compose-spacing` provides the hit-area padding expansions.
- `ui-compose-radius` provides element radius, which determines ring radius/offset.
- `ui-compose-motion` provides the `--motion-focus-ring` role.
- `ui-build-tokens` consumes emitted interactive-role tokens.
- `ui-audit-quality` re-runs target-size, focus-contrast, and keyboard-affordance checks independently.

## Bundled reference files

- `targets/minimums.json` — WCAG 2.2 SC 2.5.8 rules, inline and spacing exceptions, platform minimums (Apple 44pt, Material 48dp).
- `focus-ring/recipes.json` — three canonical recipes (outer, inner-outer, inset), color strategies, prefers-contrast and forced-colors handling.
- `offsets/per-surface.json` — ring-offset and ring-radius per element radius.
- `keyboard/affordances.json` — per-role tab order, activation keys, escape behavior, arrow-key navigation (per WAI-ARIA APG).
