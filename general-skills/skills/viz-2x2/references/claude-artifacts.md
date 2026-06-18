---
date: 2026-05-12
coverage: foundational
peers:
  - template.md
  - visual-system.md
primary_sources:
  - Anthropic Claude artifact documentation
  - Claude Design theme system (opinionated base themes)
---

# Claude artifacts deployment guide

How to deploy 2×2 matrix artifacts in Claude Chat (claude.ai) and Claude Design environments. The core HTML is identical — only the packaging and theme integration differ.

---

## 1. Claude Chat (claude.ai) — Artifact mode

### The artifact tag format

Claude Chat renders HTML inside sandboxed iframes using the `<artifact>` tag. Wrap the complete HTML document:

```xml
<artifact type="text/html" identifier="the-typing-matrix" title="The Typing Matrix">
<!DOCTYPE html>
<html lang="en">
<head>...</head>
<body>...</body>
</html>
</artifact>
```

| Attribute | Required? | Value |
|---|---|---|
| `type` | Yes | Always `"text/html"` for matrix artifacts |
| `identifier` | Yes | Snake-case unique ID, e.g. `"the-typing-matrix"` |
| `title` | Yes | Human-readable title for the artifact header |

### Sandbox constraints

Artifacts run in a strict CSP sandbox:

| What works | What is blocked |
|---|---|
| Inline CSS in `<style>` | External stylesheets (`<link rel="stylesheet" href="...">`) |
| Inline SVG | External images (`<img src="...">`) |
| `data:` URIs | `fetch()`, `XMLHttpRequest` |
| Google Fonts via `link` | Some older browsers / strict CSP configs |

**Critical**: Google Fonts may not load reliably. The template already declares `system-ui, -apple-system` before `DM Sans` in the font stack, but in artifact mode the Google Fonts `<link>` should be treated as **progressive enhancement**, not a hard dependency.

### Font strategy for artifacts

The template's font stack (from `template.md`):

```css
--sans: 'DM Sans', system-ui, -apple-system, sans-serif;
--mono: 'DM Mono', ui-monospace, monospace;
```

In artifact mode, **do not remove** the Google Fonts `<link>`. If the font loads, the artifact looks polished. If it fails, the system fallback is visually acceptable. The design system works with system fonts — the metrics and spacing are font-agnostic.

### Container width

The artifact iframe has no fixed width — it expands to fill the chat column (typically ~680–760px depending on viewport). The template's `max-width: 760px` works well. Do not change this for artifact mode.

### Dark mode

The artifact viewer passes `prefers-color-scheme` based on the user's OS setting. The template's `@media(prefers-color-scheme:dark)` block handles this automatically. No changes needed.

---

## 2. Claude Design — Theme integration

Claude Design has **opinionated base themes** with specific color palettes and typographic scales. When the user is in Claude Design, the matrix should complement — not clash with — the base theme.

### Theme detection

There is no reliable CSS-only way to detect "Claude Design" vs "Claude Chat" vs "generic browser." The skill handles this by providing a **theme override layer** in the design tokens.

### Design theme color palette

Claude Design base themes (as of 2025) use:

| Token | Light | Dark | Usage |
|---|---|---|---|
| Background | `#fafafa` | `#0f0f0f` | Page surface |
| Surface | `#ffffff` | `#1a1a1a` | Cards, panels |
| Text primary | `#171717` | `#e5e5e5` | Headings, body |
| Text secondary | `#737373` | `#a3a3a3` | Descriptions |
| Border | `#e5e5e5` | `#262626` | Dividers |
| Accent | `#2563eb` | `#3b82f6` | Primary action, links |
| Success | `#16a34a` | `#22c55e` | Positive states |
| Warning | `#d97706` | `#f59e0b` | Caution |
| Danger | `#dc2626` | `#ef4444` | Errors |

### Adapting the matrix to Claude Design themes

Option A: **Embed within the theme** (recommended for Claude Design)
- Replace the neutral scale (`--bg0` through `--t4`) with CSS custom properties that inherit from the Design theme
- Keep the semantic quadrant colors (gray, teal, coral, purple) but desaturate them to match the Design aesthetic
- Use the Design accent color for the "sweet spot" axis highlight instead of teal

Option B: **Stand out from the theme** (recommended for emphasis)
- Keep the full newsprint palette — the warm gray / editorial contrast against Design's cooler neutrals creates intentional visual hierarchy
- The matrix becomes a "figure" that breaks out of the "ground" of the Design UI

### Implementation: Theme override layer

Add a `:root` override block at the top of the `<style>` section, after the base `:root` but before any component styles:

```css
/* Base design tokens (from template) */
:root { ... }

/* Claude Design theme override — uncomment when deploying in Claude Design */
/*
:root {
  --bg0: #fafafa; --bg1: #ffffff; --bg2: #f5f5f5;
  --t1: #171717; --t2: #737373; --t3: #a3a3a3; --t4: #d4d4d4;
  --brd: rgba(0,0,0,0.08); --brd2: rgba(0,0,0,0.04);
  --teal-h: #2563eb; --teal-accent: #3b82f6;
  --teal-tag-bg: #eff6ff; --teal-tag-fg: #1e40af;
  --axis-bg: #1e3a8a; --axis-fg: #bfdbfe;
}
@media(prefers-color-scheme:dark) {
  :root {
    --bg0: #0f0f0f; --bg1: #1a1a1a; --bg2: #262626;
    --t1: #e5e5e5; --t2: #a3a3a3; --t3: #737373; --t4: #525252;
    --brd: rgba(255,255,255,0.08); --brd2: rgba(255,255,255,0.04);
    --teal-h: #60a5fa; --teal-accent: #3b82f6;
    --teal-tag-bg: #172554; --teal-tag-fg: #bfdbfe;
    --axis-bg: #172554; --axis-fg: #60a5fa;
  }
}
*/
```

**When to enable**: Ask the user "Do you want this matrix to match the Claude Design theme or use the editorial palette?" If they say "match the theme," uncomment the override block. If they say "editorial" or don't specify, keep the default newsprint palette.

---

## 3. Cross-environment checklist

| Concern | Claude Chat artifact | Claude Design | File (offline) |
|---|---|---|---|
| Packaging | `<artifact>` tags | `<artifact>` tags or inline component | `.html` file |
| External fonts | Google Fonts link (graceful fallback) | Same | Same |
| Theme override | Not needed | Optional override block | Not needed |
| Container width | `max-width: 760px` (fits chat column) | `max-width: 760px` or `100%` if in a panel | `max-width: 760px` |
| Dark mode | `prefers-color-scheme` | `prefers-color-scheme` | `prefers-color-scheme` |
| Interactivity | Static only (no JS) | Static only | Static only |
| Export | Artifact viewer handles download | Artifact viewer handles download | File is already saved |

---

## 4. Common issues and fixes

### Issue: "The artifact is blank / no styling"

**Cause**: The `<artifact>` tag was not closed properly, or the HTML is not a complete document.

**Fix**: Ensure the `<artifact>` wraps the entire HTML from `<!DOCTYPE html>` to `</html>`. Do not emit the HTML as plain text outside the artifact tag.

### Issue: "Fonts look wrong / too generic"

**Cause**: Google Fonts failed to load in the sandbox; system fonts are rendering.

**Fix**: This is expected behavior. The design system works with system fonts. If the user complains, explain that the artifact uses system fonts for maximum compatibility, and the layout/spacing remains consistent.

### Issue: "Colors clash with Claude Design"

**Cause**: The editorial palette (warm gray, teal, coral, purple) contrasts with Design's cooler neutrals.

**Fix**: Enable the theme override layer (Option A above) to harmonize the palette. Or leave it — the contrast may be intentional, making the matrix a focal point.

### Issue: "Matrix is too wide / horizontal scroll"

**Cause**: The chat column is narrower than 760px on small viewports.

**Fix**: The template already has `@media(max-width:600px)` breakpoints. If scrolling persists, check that `padding: 48px 28px` isn't causing overflow — the artifact iframe should handle its own horizontal overflow.

---

## 5. File mode vs artifact mode — quick decision

```
Is the user in Claude Chat, Claude Design, or an artifact-enabled interface?
└── YES → Artifact mode. Wrap in <artifact> tags. No file save.
└── NO  → File mode. Save as .html. User opens in browser.
```

When in doubt, ask: "Should I present this as a chat artifact or save it as a file?"
