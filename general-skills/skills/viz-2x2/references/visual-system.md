---
date: 2026-05-07
coverage: foundational
peers:
  - template.md
  - ../SKILL.md
primary_sources:
  - SKILL.md §Step 4: Design the charts
  - SKILL.md §Step 6: Build the artifact
---

# Visual system specification

This document explains the design system behind every 2×2 matrix artifact. Read this when you need to modify the visual design, create a new variant, or reason about why a particular design decision was made.

The template (`references/template.md`) is the *how* — this document is the *why*.

---

## 1. Design tokens

The artifact uses CSS custom properties for all visual values. No hardcoded colors or sizes exist outside the `:root` block.

### Neutral scale

| Token | Light | Dark | Purpose |
|---|---|---|---|
| `--bg0` | `#ffffff` | `#141413` | Page background |
| `--bg1` | `#f6f5f1` | `#1e1e1c` | Card backgrounds, takeaway box |
| `--bg2` | `#eceae4` | `#2a2a28` | Code inline, secondary surfaces |
| `--t1` | `#1a1a1a` | `#e8e6de` | Primary text (headings, body) |
| `--t2` | `#5c5c59` | `#b4b2a9` | Secondary text (descriptions) |
| `--t3` | `#9c9a92` | `#888780` | Tertiary text (labels, metadata) |
| `--t4` | `#c2c0b6` | `#5c5c59` | Borders, gridlines, subtle elements |
| `--brd` | `rgba(0,0,0,0.10)` | `rgba(255,255,255,0.08)` | Card borders |
| `--brd2` | `rgba(0,0,0,0.05)` | `rgba(255,255,255,0.04)` | Subtle dividers |

**Rationale**: The neutral palette is derived from newsprint / editorial design. Warm gray (not cool blue-gray) feels human and readable. The light-to-dark mapping preserves relative contrast, not identical values — `--bg1` in dark mode is not the inverse of `--bg1` in light mode; it's a darker surface that maintains the same hierarchical relationship to `--bg0`.

### Semantic colors (quadrants)

| Color | Background (tag) | Foreground (text) | Heading | Accent | Meaning |
|---|---|---|---|---|---|
| **Gray** | `#D3D1C7` / `#444441` | `#444441` / `#D3D1C7` | `#5F5E5A` / `#B4B2A9` | `#888780` | Unremarkable, default, baseline |
| **Teal** | `#9FE1CB` / `#085041` | `#085041` / `#9FE1CB` | `#0F6E56` / `#5DCAA5` | `#1D9E75` | Recommended, sweet spot, healthy |
| **Coral** | `#F5C4B3` / `#712B13` | `#712B13` / `#F5C4B3` | `#D85A30` / `#F0997B` | `#F0997B` | Anti-pattern, warning, lossy |
| **Purple** | `#CECBF6` / `#3C3489` | `#3C3489` / `#CECBF6` | `#534AB7` / `#AFA9EC` | `#7F77DD` | Over-engineered, costly, theoretical |

**Rationale**: These four colors are perceptually distinct for all common color vision deficiencies. Teal-coral is a classic "good-bad" pair (present in traffic lights, medical dashboards). Purple signals "expensive/rare" (historical association with imperial dye). Gray is the absence of signal — the control condition.

### Chart colors

| Token | Light | Dark | Purpose |
|---|---|---|---|
| `--sig-color` | `#BA7517` | `#EF9F27` | Primary metric (solid line) |
| `--sig-fill` | `rgba(186,117,23,0.08)` | `rgba(239,159,39,0.10)` | Primary area fill |
| `--int-color` | `#185FA5` | `#85B7EB` | Secondary metric (dashed line) |
| `--int-fill` | `rgba(24,95,165,0.08)` | `rgba(133,183,235,0.10)` | Secondary area fill |

**Rationale**: Orange-blue is the most robust color pair for data visualization. It survives all major CVD types (protanopia, deuteranopia, tritanopia). The fill opacity is intentionally low (8-10%) so overlapping areas don't obscure the grid.

### Axis highlight

| Token | Light | Dark | Purpose |
|---|---|---|---|
| `--axis-bg` | `#085041` | `#04342C` | "Better" axis endpoint background |
| `--axis-fg` | `#9FE1CB` | `#5DCAA5` | "Better" axis endpoint text |

**Rationale**: The axis highlight uses the teal family to signal "this direction is preferred" without attaching the full semantic weight of a quadrant color.

---

## 2. Typography

### Font families

| Role | Font | Weights | Purpose |
|---|---|---|---|
| Body | DM Sans | 400, 500, 600 | Humanist sans, warm, highly legible at small sizes |
| Mono | DM Mono | 400 | Data labels, metadata, axis values — not code blocks |

**Rationale**: DM Sans is designed for data-heavy interfaces ("Data Ministry"). Its large x-height and open apertures make it readable at 12px. DM Mono is its monospaced companion, ensuring visual consistency between proportional and fixed-width text.

### Type scale

| Element | Size | Weight | Line-height | Notes |
|---|---|---|---|---|
| H1 (title) | 28px | 600 | 1.2 | Letter-spacing -0.02em for tightness |
| H3 (quadrant name) | 14px | 600 | — | — |
| H4 (summary name) | 16px | 600 | — | — |
| Body (description) | 13px | 400 | 1.65 | — |
| Tagline | 10px | 500 | — | ALL CAPS, letter-spacing 0.01em |
| Axis label | 12px | 500 | — | ALL CAPS, letter-spacing 0.08em |
| Metadata | 12px | 400 | — | Mono family |
| Chart label | 9px | 400 | — | Mono family |
| Trait | 11px | 400 | 1.45 | Tertiary color |

**Responsive**: At ≤500px, H1 drops to 22px. At ≤600px, summary cards stack vertically (grid becomes single column).

---

## 3. Layout system

### Page container

```
max-width: 760px
padding: 48px 28px 64px
```

**Rationale**: 760px is the optimal reading width for mixed text + data visualization. Narrower and the charts feel cramped; wider and the text lines become too long for comfortable reading.

### Spacing scale

| Token | Value | Used for |
|---|---|---|
| Section gap | 40px | Between major sections (matrix → summaries → takeaway) |
| Card padding | 22px 24px | Summary card internal padding |
| Card gap | 28px | Between summary cards |
| Matrix cell padding | 18px 20px | Quadrant card internal padding |

---

## 4. SVG chart specification

### ViewBox and coordinate system

```
viewBox="0 0 210 110"
```

| Region | Coordinates | Purpose |
|---|---|---|
| Full SVG | 0,0 → 210,110 | Container |
| Drawing area | 28,8 → 204,94 | Data lines, areas, grid |
| Y-axis labels | 22,y | Left of drawing area, right-aligned |
| X-axis label | center, below | Centered beneath chart |

**Why 210×110?** The aspect ratio (1.91:1) is close to the golden ratio but slightly wider. This makes the chart feel expansive — suitable for showing trends over time. 110px height is enough for two curves with area fills without excessive vertical space.

### Coordinate mapping

```
y_pixel = 94 - (percentage / 100) * 82
```

| Percentage | y_pixel |
|---|---|
| 100 | 12 |
| 75 | 32.5 |
| 50 | 53 |
| 25 | 73.5 |
| 0 | 94 |

X coordinates are fixed at 6 evenly spaced points:
```
x = [28, 63, 99, 134, 169, 204]
```

### SVG element construction

**Area fill path** (metric A):
```svg
<path d="M28,{y1} L63,{y2} L99,{y3} L134,{y4} L169,{y5} L204,{y6} L204,94 L28,94Z" fill="var(--sig-fill)"/>
```

**Line polyline** (metric A):
```svg
<polyline points="28,{y1} 63,{y2} 99,{y3} 134,{y4} 169,{y5} 204,{y6}" fill="none" stroke="var(--sig-color)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
```

**Line polyline** (metric B, dashed):
```svg
<polyline ... stroke-dasharray="4 3"/>
```

### Grid elements

| Element | SVG |
|---|---|
| Border rect | `<rect x="28" y="8" width="176" height="86" fill="none" stroke="var(--brd2)" stroke-width="0.5" rx="2"/>` |
| 50% reference line | `<line x1="28" y1="51" x2="204" y2="51" stroke="var(--brd2)" stroke-width="0.5" stroke-dasharray="3 3"/>` |
| Y labels | `<text x="22" y="{15|54|96}" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">100|50|0</text>` |

---

## 5. Curve shape taxonomy

Eight canonical curve shapes, each encoding a different degradation/compounding mechanism. These are the **semantic vocabulary** of the charts.

| Shape | Percentages | Mechanism | When to use |
|---|---|---|---|
| **Exponential decay** | `100, 68, 45, 30, 20, 14` | Multiplicative error accumulation | Systems where each step compounds previous errors (e.g., untyped data pipelines) |
| **Linear decline** | `100, 82, 65, 50, 38, 28` | Additive loss per step | Systems that lose a fixed amount of quality per unit of scale |
| **Cliff collapse** | `90, 80, 60, 30, 12, 5` | Works-until-it-doesn't | Monoliths exceeding a hard limit (context window, memory) |
| **Plateau after drop** | `100, 70, 58, 52, 49, 47` | One-time loss then stability | Extraction pipelines that lose signal on first transform, then hold |
| **Recovery** | `100, 90, 88, 91, 94, 96` | Verification ratchet | Typed systems where early errors are caught and the system improves |
| **Near-flat** | `85, 82, 80, 78, 76, 75` | Graceful degradation | Well-designed systems with slow, predictable decline |
| **Improving** | `80, 82, 85, 88, 90, 92` | Compounding returns | Structured systems where organization pays dividends |
| **Steady low** | `50, 35, 22, 14, 9, 5` | Bad from the start | Fundamentally broken approaches that never worked well |

### The winning quadrant rule

**Only one quadrant may have a curve that stays flat or improves.** This is the visual argument. If multiple quadrants improve, the matrix loses its prescriptive force. If none improve, the matrix is pessimistic and the reader has no clear path forward.

### Choosing between two metrics

| Primary (solid) | Secondary (dashed) | Story |
|---|---|---|
| Efficiency | Findability | Fast but hard to locate vs. slow but discoverable |
| Signal retention | Data integrity | How much signal survives vs. how correct the output is |
| Throughput | Reliability | More output vs. fewer failures |
| Cost | Quality | Cheap and bad vs. expensive and good |

---

## 6. Responsive behavior

| Breakpoint | Change |
|---|---|
| ≤760px | Page padding reduces, content still readable |
| ≤600px | Summary cards stack vertically (1fr → 1fr single column) |
| ≤500px | H1 drops from 28px to 22px; matrix cell padding reduces |

**No JavaScript**: All responsive behavior is CSS `@media` queries. The artifact is a single static HTML file.

---

## 7. Accessibility

| Feature | Implementation |
|---|---|
| Color independence | All data is encoded in position (charts) and text (labels), not color alone |
| CVD safety | Teal-coral separates for protanopia; orange-blue chart pair separates for all CVD types |
| Contrast | All text meets WCAG AA (4.5:1) against its background in both light and dark modes |
| Motion | No animations; `prefers-reduced-motion` has no effect because nothing moves |
| Semantic HTML | `<h1>`, `<h3>`, `<h4>` used; no div-soup for headings |

---

## 8. Meta tags and sharing

| Tag | Purpose | Example |
|---|---|---|
| `og:title` | Link preview title | "The typing matrix — How structure affects LLM output quality" |
| `og:description` | Link preview body | "Four approaches to type discipline in AI-assisted coding…" |
| `meta description` | Search snippet | Same as og:description |
| `<title>` | Browser tab | "The typing matrix" |

**Filename convention**: `the_typing_matrix.html` (snake_case, no spaces, descriptive).

---

## 9. Modification guidelines

### Safe changes (won't break the system)

- Swapping quadrant colors (e.g., sweet spot on bottom-right instead of top-right)
- Changing the chart x-axis label
- Adjusting the number of data points (if you change the SVG path generation accordingly)
- Adding a fourth meta tag

### Risky changes (test thoroughly)

- Changing the viewBox dimensions — all coordinate math must be recalculated
- Adding a third curve — the two-metric system is core to the visual argument
- Changing fonts — DM Sans/DM Mono are paired; substituting one breaks the visual rhythm
- Removing the 50% reference line — readers use it as a visual anchor

### Forbidden changes (breaks the contract)

- Putting charts inside matrix quadrants (they belong in summary cards)
- Using non-semantic colors without updating the quadrant meaning table
- Hardcoding colors instead of using CSS custom properties (breaks dark mode)
