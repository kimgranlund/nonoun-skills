---
date: 2026-05-06
coverage: foundational
peers:
  - ../SKILL.md
primary_sources:
  - SKILL.md
---

# 2×2 Matrix HTML Template

This is the canonical HTML template for all 2×2 matrix artifacts. Copy the entire template, then replace the content slots marked with `{{SLOT_NAME}}` comments.

## Content slots to fill

| Slot | Location | Description |
|------|----------|-------------|
| `TITLE` | `<h1>`, `<title>`, og:title | Matrix name (e.g., "The typing matrix") |
| `SUBTITLE` | `.subtitle` | One-sentence description |
| `OG_DESC` | og:description, meta description | Link-preview description |
| `META_TAG_1/2/3` | `.meta span` | Attribution, category, year |
| `INTRO` | `.intro` | 3–4 sentence setup. Use `<strong>` for key terms, `<code>` for technical terms |
| `X_AXIS_LABEL` | `.x-label` | What the x-axis measures (e.g., "Structure") |
| `Y_AXIS_LABEL` | `.y-label` | What the y-axis measures (e.g., "Granularity") |
| `COL_LO/COL_HI` | `.col-h` | X-axis endpoint labels (e.g., "unstructured" / "structured") |
| `ROW_LO/ROW_HI` | `.row-label` | Y-axis endpoint labels (e.g., "coarse" / "fine") |
| `Q1–Q4` | `.q` cells | Quadrant name, tag, description, trait |
| `GRADIENT_LO/HI` | `.gradient-bar` | Spectrum endpoints (e.g., "lossy" / "compounding") |
| `GRADIENT_MID` | `.gradient-bar` | Arrow label (e.g., "→ interpretation cost decreases →") |
| `SECTION_TITLE` | `.section-title` | Summary section header |
| `S1–S4` | `.summary-card` | Mode label, name, description, reasoning |
| `CHART_LABEL` | `.chart-label` | X-axis of charts (e.g., "Pipeline stages →") |
| `METRIC_A/B` | `.chart-legend` | Chart legend labels (e.g., "Signal" / "Integrity") |
| `TAKEAWAY` | `.takeaway` | 3–4 paragraph actionable summary |
| `FOOTER_LEFT/RIGHT` | `.footer` | Attribution and category |

## Color reassignment

Default assignment (change if your matrix topology differs):

| Quadrant | Position | Default meaning | Color | CSS classes |
|----------|----------|-----------------|-------|-------------|
| Q1 | top-left | Baseline/default | Gray | `q1`, `s1` |
| Q2 | top-right | Sweet spot | Teal | `q2`, `s2` |
| Q3 | bottom-left | Anti-pattern | Coral | `q3`, `s3` |
| Q4 | bottom-right | Over-engineered | Purple | `q4`, `s4` |

To reassign: swap the color variable sets between quadrant classes. For example, if the sweet spot is bottom-right instead of top-right, give `q4`/`s4` the teal variables and `q2`/`s2` the purple variables.

## Chart data computation

Each chart has 6 data points mapping a percentage (0–100) to the SVG coordinate space:

```
y_pixel = 94 - (percentage / 100) * 82
x_pixels = [28, 63, 99, 134, 169, 204]  (6 evenly spaced points)
```

For the area fill path, append the bottom-right and bottom-left corners:
```
M{x1},{y1} L{x2},{y2} ... L{x6},{y6} L204,94 L28,94Z
```

For the line polyline, just the data points:
```
{x1},{y1} {x2},{y2} ... {x6},{y6}
```

### Common curve shapes (percentage values for 6 points)

**Exponential decay** (multiplicative degradation):
`100, 68, 45, 30, 20, 14` — for systems where each step multiplies the previous error

**Linear decline** (additive degradation):
`100, 82, 65, 50, 38, 28` — for systems that lose a constant amount per step

**Cliff collapse** (works-until-it-doesn't):
`90, 80, 60, 30, 12, 5` — starts good, then catastrophically fails at scale

**Plateau after drop** (extraction/one-sided typing):
`100, 70, 58, 52, 49, 47` — sharp initial loss that stabilizes

**Recovery curve** (verification ratchet):
`100, 90, 88, 91, 94, 96` — dip then improvement as the system learns

**Near-flat** (well-designed, scales gracefully):
`85, 82, 80, 78, 76, 75` — slow graceful decline

**Improving** (structure compounds):
`80, 82, 85, 88, 90, 92` — gets better as the system grows

**Steady low** (bad from the start):
`50, 35, 22, 14, 9, 5` — starts mediocre, ends terrible

## Full HTML template

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta property="og:title" content="{{TITLE}} — {{SUBTITLE_SHORT}}">
<meta property="og:description" content="{{OG_DESC}}">
<meta name="description" content="{{OG_DESC}}">
<title>{{TITLE}}</title>
<!-- Google Fonts: loaded as progressive enhancement. System fonts declared first in --sans/--mono.
     In artifact mode (Claude Chat), the link may be blocked by CSP — design still works. -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,400;0,500;0,600;1,400&family=DM+Mono:wght@400&display=swap" rel="stylesheet">
<style>
/* === DESIGN TOKENS ===
   All visual values are CSS custom properties. Override the :root block below
   to adapt to parent themes (e.g., Claude Design). See references/claude-artifacts.md
   for a pre-built Claude Design override. */
:root{
  --bg0:#ffffff;--bg1:#f6f5f1;--bg2:#eceae4;
  --t1:#1a1a1a;--t2:#5c5c59;--t3:#9c9a92;--t4:#c2c0b6;
  --brd:rgba(0,0,0,0.10);--brd2:rgba(0,0,0,0.05);
  --sans:'DM Sans',system-ui,-apple-system,sans-serif;
  --mono:'DM Mono',ui-monospace,monospace;
  --gray-tag-bg:#D3D1C7;--gray-tag-fg:#444441;--gray-h:#5F5E5A;--gray-accent:#888780;
  --purple-tag-bg:#CECBF6;--purple-tag-fg:#3C3489;--purple-h:#534AB7;--purple-accent:#7F77DD;
  --coral-tag-bg:#F5C4B3;--coral-tag-fg:#712B13;--coral-h:#D85A30;--coral-accent:#F0997B;
  --teal-tag-bg:#9FE1CB;--teal-tag-fg:#085041;--teal-h:#0F6E56;--teal-accent:#1D9E75;
  --sig-color:#BA7517;--sig-fill:rgba(186,117,23,0.08);
  --int-color:#185FA5;--int-fill:rgba(24,95,165,0.08);
  --axis-bg:#085041;--axis-fg:#9FE1CB;
}
@media(prefers-color-scheme:dark){:root{
  --bg0:#141413;--bg1:#1e1e1c;--bg2:#2a2a28;
  --t1:#e8e6de;--t2:#b4b2a9;--t3:#888780;--t4:#5c5c59;
  --brd:rgba(255,255,255,0.08);--brd2:rgba(255,255,255,0.04);
  --gray-tag-bg:#444441;--gray-tag-fg:#D3D1C7;--gray-h:#B4B2A9;--gray-accent:#888780;
  --purple-tag-bg:#3C3489;--purple-tag-fg:#CECBF6;--purple-h:#AFA9EC;--purple-accent:#7F77DD;
  --coral-tag-bg:#712B13;--coral-tag-fg:#F5C4B3;--coral-h:#F0997B;--coral-accent:#D85A30;
  --teal-tag-bg:#085041;--teal-tag-fg:#9FE1CB;--teal-h:#5DCAA5;--teal-accent:#1D9E75;
  --sig-color:#EF9F27;--sig-fill:rgba(239,159,39,0.10);
  --int-color:#85B7EB;--int-fill:rgba(133,183,235,0.10);
  --axis-bg:#04342C;--axis-fg:#5DCAA5;
}}
*{box-sizing:border-box;margin:0;padding:0}
html{font-size:16px}
body{background:var(--bg0);color:var(--t1);font-family:var(--sans);padding:0;-webkit-font-smoothing:antialiased}
.page{max-width:760px;margin:0 auto;padding:48px 28px 64px}
@media(max-width:600px){.page{padding:32px 16px 48px}}

.header{margin-bottom:40px;padding-bottom:28px;border-bottom:1px solid var(--brd)}
.header h1{font-size:28px;font-weight:600;line-height:1.2;letter-spacing:-0.02em;margin-bottom:8px}
@media(max-width:500px){.header h1{font-size:22px}}
.header .subtitle{font-size:15px;color:var(--t2);line-height:1.5;max-width:580px}
.header .meta{display:flex;flex-wrap:wrap;gap:16px;margin-top:14px;font-size:12px;color:var(--t3);font-family:var(--mono)}
.header .meta span{display:flex;align-items:center;gap:5px}
.dot-sep{width:3px;height:3px;border-radius:50%;background:var(--t4);display:inline-block}

.intro{font-size:14px;line-height:1.7;color:var(--t2);margin-bottom:36px;max-width:620px}
.intro strong{color:var(--t1);font-weight:500}
.intro code{font-family:var(--mono);font-size:13px;background:var(--bg1);padding:1px 5px;border-radius:4px;color:var(--t1)}

.matrix-section{margin-bottom:8px}
.matrix-wrap{position:relative;padding-left:52px}
.y-label{position:absolute;left:2px;top:50%;transform:translateY(-50%) rotate(-90deg);font-size:12px;font-weight:500;color:var(--t3);letter-spacing:.08em;text-transform:uppercase;font-family:var(--mono);white-space:nowrap}
.x-label{text-align:center;padding:0 0 6px;font-size:12px;font-weight:500;color:var(--t3);letter-spacing:.08em;text-transform:uppercase;font-family:var(--mono)}
.matrix{display:grid;grid-template-columns:28px 1fr 1fr;grid-template-rows:auto 1fr 1fr;gap:0}
.col-h{font-size:12px;font-weight:500;padding:7px 0;text-align:center;font-family:var(--mono);letter-spacing:.02em}
.col-h.lo{background:var(--bg1);color:var(--t3);border-radius:6px 6px 0 0}
.col-h.hi{background:var(--axis-bg);color:var(--axis-fg);border-radius:6px 6px 0 0}
.row-label{font-size:12px;font-weight:500;writing-mode:vertical-lr;transform:rotate(180deg);display:flex;align-items:center;justify-content:center;width:28px;font-family:var(--mono);letter-spacing:.02em}
.row-label.lo{background:var(--bg1);color:var(--t3)}
.row-label.hi{background:var(--axis-bg);color:var(--axis-fg)}
.q{padding:18px 20px;border:0.5px solid var(--brd)}
.q h3{font-size:14px;font-weight:600;margin:0 0 4px;letter-spacing:-0.01em}
.q .tag{font-size:10px;font-weight:500;display:inline-block;padding:2px 8px;border-radius:10px;margin-bottom:10px;letter-spacing:.01em;font-family:var(--mono)}
.q p{font-size:12.5px;line-height:1.55;color:var(--t2);margin:0 0 5px}
.q p:last-child{margin:0}
.q .trait{font-size:11px;line-height:1.45;color:var(--t3);margin:6px 0 0;padding-top:8px;border-top:0.5px solid var(--brd2)}
.q1{background:var(--bg1);border-radius:8px 0 0 0}
.q1 h3{color:var(--gray-h)}.q1 .tag{background:var(--gray-tag-bg);color:var(--gray-tag-fg)}
.q2{border-radius:0 8px 0 0}
.q2 h3{color:var(--teal-h)}.q2 .tag{background:var(--teal-tag-bg);color:var(--teal-tag-fg)}
.q3{border-radius:0 0 0 8px}
.q3 h3{color:var(--coral-h)}.q3 .tag{background:var(--coral-tag-bg);color:var(--coral-tag-fg)}
.q4{border-radius:0 0 8px 0}
.q4 h3{color:var(--purple-h)}.q4 .tag{background:var(--purple-tag-bg);color:var(--purple-tag-fg)}
.gradient-bar{display:flex;justify-content:space-between;padding:10px 32px 0;font-size:11px;color:var(--t4);font-family:var(--mono)}

.section-divider{height:1px;background:var(--brd);margin:40px 0 36px}
.section-title{font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.1em;color:var(--t3);margin-bottom:24px;font-family:var(--mono)}

.summaries{display:flex;flex-direction:column;gap:28px}
.summary-card{display:grid;grid-template-columns:1fr 210px;gap:24px;padding:22px 24px;border:0.5px solid var(--brd);border-radius:12px;background:var(--bg0)}
@media(max-width:600px){.summary-card{grid-template-columns:1fr;gap:16px}}
.summary-card .mode-label{font-size:10px;font-weight:500;letter-spacing:.08em;text-transform:uppercase;margin-bottom:2px;font-family:var(--mono)}
.summary-card h4{font-size:16px;font-weight:600;margin:0 0 8px;letter-spacing:-0.01em}
.summary-card .desc{font-size:13px;line-height:1.65;color:var(--t2)}
.summary-card .reasoning{font-size:12px;line-height:1.55;color:var(--t3);margin-top:10px;padding-top:10px;border-top:0.5px solid var(--brd2);font-style:italic}
.chart-wrap{display:flex;flex-direction:column;justify-content:center}
.chart-legend{display:flex;gap:14px;margin-bottom:8px;font-size:10px;color:var(--t3);font-family:var(--mono)}
.chart-legend span{display:flex;align-items:center;gap:4px}
.chart-legend .dot{width:7px;height:7px;border-radius:50%;display:inline-block}
.dot-sig{background:var(--sig-color)}.dot-int{background:var(--int-color)}
.chart-label{font-size:9px;color:var(--t4);text-align:center;margin-top:4px;font-family:var(--mono);letter-spacing:.04em}
.s1 .mode-label{color:var(--gray-accent)}.s1{border-left:3px solid var(--gray-accent)}
.s2 .mode-label{color:var(--teal-accent)}.s2{border-left:3px solid var(--teal-accent)}
.s3 .mode-label{color:var(--coral-accent)}.s3{border-left:3px solid var(--coral-accent)}
.s4 .mode-label{color:var(--purple-accent)}.s4{border-left:3px solid var(--purple-accent)}

.takeaway{margin-top:40px;padding:24px;background:var(--bg1);border-radius:12px;border:0.5px solid var(--brd)}
.takeaway h3{font-size:14px;font-weight:600;margin-bottom:10px;letter-spacing:-0.01em}
.takeaway p{font-size:13px;line-height:1.65;color:var(--t2)}
.takeaway p+p{margin-top:8px}
.takeaway strong{color:var(--t1);font-weight:500}
.takeaway code{font-family:var(--mono);font-size:12px;background:var(--bg2);padding:1px 5px;border-radius:4px;color:var(--t1)}

.footer{margin-top:40px;padding-top:20px;border-top:1px solid var(--brd);display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--t4);font-family:var(--mono)}
</style>
</head>
<body>
<div class="page">

  <!-- HEADER -->
  <div class="header">
    <h1>{{TITLE}}</h1>
    <div class="subtitle">{{SUBTITLE}}</div>
    <div class="meta">
      <span>{{META_TAG_1}}</span>
      <span class="dot-sep"></span>
      <span>{{META_TAG_2}}</span>
      <span class="dot-sep"></span>
      <span>{{META_TAG_3}}</span>
    </div>
  </div>

  <!-- INTRO -->
  <div class="intro">
    {{INTRO_HTML — use <strong> for key terms, <code> for technical terms}}
  </div>

  <!-- MATRIX -->
  <div class="matrix-section">
    <div class="x-label">{{X_AXIS_LABEL}}</div>
    <div class="matrix-wrap">
      <div class="y-label">{{Y_AXIS_LABEL}}</div>
      <div class="matrix">
        <div style="grid-column:1;grid-row:1"></div>
        <div style="grid-column:2/4;grid-row:1;display:grid;grid-template-columns:1fr 1fr">
          <div class="col-h lo">{{COL_LO}}</div>
          <div class="col-h hi">{{COL_HI}}</div>
        </div>
        <div style="grid-column:1;grid-row:2;display:flex"><div class="row-label lo">{{ROW_LO}}</div></div>
        <div style="grid-column:1;grid-row:3;display:flex"><div class="row-label hi">{{ROW_HI}}</div></div>

        <!-- Q1: top-left (ROW_LO + COL_LO) — Gray -->
        <div class="q q1" style="grid-column:2;grid-row:2">
          <h3>{{Q1_NAME}}</h3>
          <span class="tag">{{Q1_TAG}}</span>
          <p>{{Q1_DESC_P1}}</p>
          <p>{{Q1_DESC_P2}}</p>
          <div class="trait">{{Q1_TRAIT}}</div>
        </div>

        <!-- Q2: top-right (ROW_LO + COL_HI) — Teal -->
        <div class="q q2" style="grid-column:3;grid-row:2">
          <h3>{{Q2_NAME}}</h3>
          <span class="tag">{{Q2_TAG}}</span>
          <p>{{Q2_DESC_P1}}</p>
          <div class="trait">{{Q2_TRAIT}}</div>
        </div>

        <!-- Q3: bottom-left (ROW_HI + COL_LO) — Coral -->
        <div class="q q3" style="grid-column:2;grid-row:3">
          <h3>{{Q3_NAME}}</h3>
          <span class="tag">{{Q3_TAG}}</span>
          <p>{{Q3_DESC_P1}}</p>
          <p>{{Q3_DESC_P2}}</p>
          <div class="trait">{{Q3_TRAIT}}</div>
        </div>

        <!-- Q4: bottom-right (ROW_HI + COL_HI) — Purple -->
        <div class="q q4" style="grid-column:3;grid-row:3">
          <h3>{{Q4_NAME}}</h3>
          <span class="tag">{{Q4_TAG}}</span>
          <p>{{Q4_DESC_P1}}</p>
          <div class="trait">{{Q4_TRAIT}}</div>
        </div>
      </div>
    </div>
    <div class="gradient-bar">
      <span>{{GRADIENT_LO}}</span>
      <span>{{GRADIENT_MID}}</span>
      <span>{{GRADIENT_HI}}</span>
    </div>
  </div>

  <!-- SUMMARIES -->
  <div class="section-divider"></div>
  <div class="section-title">{{SECTION_TITLE}}</div>

  <div class="summaries">

    <!-- Summary 1 — Gray -->
    <div class="summary-card s1">
      <div>
        <div class="mode-label">{{S1_MODE_LABEL}}</div>
        <h4>{{S1_NAME}}</h4>
        <div class="desc">{{S1_DESC}}</div>
        <div class="reasoning">{{S1_REASONING}}</div>
      </div>
      <div class="chart-wrap">
        <div class="chart-legend"><span><span class="dot dot-sig"></span>{{METRIC_A}}</span><span><span class="dot dot-int"></span>{{METRIC_B}}</span></div>
        <svg viewBox="0 0 210 110" width="100%">
          <rect x="28" y="8" width="176" height="86" fill="none" stroke="var(--brd2)" stroke-width="0.5" rx="2"/>
          <line x1="28" y1="51" x2="204" y2="51" stroke="var(--brd2)" stroke-width="0.5" stroke-dasharray="3 3"/>
          <text x="22" y="15" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">100</text>
          <text x="22" y="54" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">50</text>
          <text x="22" y="96" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">0</text>
          <!-- Metric A area + line -->
          <path d="M28,{{A1}} L63,{{A2}} L99,{{A3}} L134,{{A4}} L169,{{A5}} L204,{{A6}} L204,94 L28,94Z" fill="var(--sig-fill)"/>
          <polyline points="28,{{A1}} 63,{{A2}} 99,{{A3}} 134,{{A4}} 169,{{A5}} 204,{{A6}}" fill="none" stroke="var(--sig-color)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <!-- Metric B area + line (dashed) -->
          <path d="M28,{{B1}} L63,{{B2}} L99,{{B3}} L134,{{B4}} L169,{{B5}} L204,{{B6}} L204,94 L28,94Z" fill="var(--int-fill)"/>
          <polyline points="28,{{B1}} 63,{{B2}} 99,{{B3}} 134,{{B4}} 169,{{B5}} 204,{{B6}}" fill="none" stroke="var(--int-color)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="4 3"/>
        </svg>
        <div class="chart-label">{{CHART_X_LABEL}}</div>
      </div>
    </div>

    <!-- Summary 2 — Teal -->
    <div class="summary-card s2">
      <div>
        <div class="mode-label">{{S2_MODE_LABEL}}</div>
        <h4>{{S2_NAME}}</h4>
        <div class="desc">{{S2_DESC}}</div>
        <div class="reasoning">{{S2_REASONING}}</div>
      </div>
      <div class="chart-wrap">
        <div class="chart-legend"><span><span class="dot dot-sig"></span>{{METRIC_A}}</span><span><span class="dot dot-int"></span>{{METRIC_B}}</span></div>
        <svg viewBox="0 0 210 110" width="100%">
          <rect x="28" y="8" width="176" height="86" fill="none" stroke="var(--brd2)" stroke-width="0.5" rx="2"/>
          <line x1="28" y1="51" x2="204" y2="51" stroke="var(--brd2)" stroke-width="0.5" stroke-dasharray="3 3"/>
          <text x="22" y="15" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">100</text>
          <text x="22" y="54" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">50</text>
          <text x="22" y="96" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">0</text>
          <path d="M28,{{A1}} L63,{{A2}} L99,{{A3}} L134,{{A4}} L169,{{A5}} L204,{{A6}} L204,94 L28,94Z" fill="var(--sig-fill)"/>
          <polyline points="28,{{A1}} 63,{{A2}} 99,{{A3}} 134,{{A4}} 169,{{A5}} 204,{{A6}}" fill="none" stroke="var(--sig-color)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M28,{{B1}} L63,{{B2}} L99,{{B3}} L134,{{B4}} L169,{{B5}} L204,{{B6}} L204,94 L28,94Z" fill="var(--int-fill)"/>
          <polyline points="28,{{B1}} 63,{{B2}} 99,{{B3}} 134,{{B4}} 169,{{B5}} 204,{{B6}}" fill="none" stroke="var(--int-color)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="4 3"/>
        </svg>
        <div class="chart-label">{{CHART_X_LABEL}}</div>
      </div>
    </div>

    <!-- Summary 3 — Coral -->
    <div class="summary-card s3">
      <div>
        <div class="mode-label">{{S3_MODE_LABEL}}</div>
        <h4>{{S3_NAME}}</h4>
        <div class="desc">{{S3_DESC}}</div>
        <div class="reasoning">{{S3_REASONING}}</div>
      </div>
      <div class="chart-wrap">
        <div class="chart-legend"><span><span class="dot dot-sig"></span>{{METRIC_A}}</span><span><span class="dot dot-int"></span>{{METRIC_B}}</span></div>
        <svg viewBox="0 0 210 110" width="100%">
          <rect x="28" y="8" width="176" height="86" fill="none" stroke="var(--brd2)" stroke-width="0.5" rx="2"/>
          <line x1="28" y1="51" x2="204" y2="51" stroke="var(--brd2)" stroke-width="0.5" stroke-dasharray="3 3"/>
          <text x="22" y="15" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">100</text>
          <text x="22" y="54" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">50</text>
          <text x="22" y="96" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">0</text>
          <path d="M28,{{A1}} L63,{{A2}} L99,{{A3}} L134,{{A4}} L169,{{A5}} L204,{{A6}} L204,94 L28,94Z" fill="var(--sig-fill)"/>
          <polyline points="28,{{A1}} 63,{{A2}} 99,{{A3}} 134,{{A4}} 169,{{A5}} 204,{{A6}}" fill="none" stroke="var(--sig-color)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M28,{{B1}} L63,{{B2}} L99,{{B3}} L134,{{B4}} L169,{{B5}} L204,{{B6}} L204,94 L28,94Z" fill="var(--int-fill)"/>
          <polyline points="28,{{B1}} 63,{{B2}} 99,{{B3}} 134,{{B4}} 169,{{B5}} 204,{{B6}}" fill="none" stroke="var(--int-color)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="4 3"/>
        </svg>
        <div class="chart-label">{{CHART_X_LABEL}}</div>
      </div>
    </div>

    <!-- Summary 4 — Purple -->
    <div class="summary-card s4">
      <div>
        <div class="mode-label">{{S4_MODE_LABEL}}</div>
        <h4>{{S4_NAME}}</h4>
        <div class="desc">{{S4_DESC}}</div>
        <div class="reasoning">{{S4_REASONING}}</div>
      </div>
      <div class="chart-wrap">
        <div class="chart-legend"><span><span class="dot dot-sig"></span>{{METRIC_A}}</span><span><span class="dot dot-int"></span>{{METRIC_B}}</span></div>
        <svg viewBox="0 0 210 110" width="100%">
          <rect x="28" y="8" width="176" height="86" fill="none" stroke="var(--brd2)" stroke-width="0.5" rx="2"/>
          <line x1="28" y1="51" x2="204" y2="51" stroke="var(--brd2)" stroke-width="0.5" stroke-dasharray="3 3"/>
          <text x="22" y="15" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">100</text>
          <text x="22" y="54" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">50</text>
          <text x="22" y="96" text-anchor="end" fill="var(--t4)" font-size="8" font-family="var(--mono)">0</text>
          <path d="M28,{{A1}} L63,{{A2}} L99,{{A3}} L134,{{A4}} L169,{{A5}} L204,{{A6}} L204,94 L28,94Z" fill="var(--sig-fill)"/>
          <polyline points="28,{{A1}} 63,{{A2}} 99,{{A3}} 134,{{A4}} 169,{{A5}} 204,{{A6}}" fill="none" stroke="var(--sig-color)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M28,{{B1}} L63,{{B2}} L99,{{B3}} L134,{{B4}} L169,{{B5}} L204,{{B6}} L204,94 L28,94Z" fill="var(--int-fill)"/>
          <polyline points="28,{{B1}} 63,{{B2}} 99,{{B3}} 134,{{B4}} 169,{{B5}} 204,{{B6}}" fill="none" stroke="var(--int-color)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="4 3"/>
        </svg>
        <div class="chart-label">{{CHART_X_LABEL}}</div>
      </div>
    </div>

  </div>

  <!-- TAKEAWAY -->
  <div class="takeaway">
    <h3>{{TAKEAWAY_TITLE}}</h3>
    <p><strong>{{TAKEAWAY_1_BOLD}}</strong> {{TAKEAWAY_1_REST}}</p>
    <p><strong>{{TAKEAWAY_2_BOLD}}</strong> {{TAKEAWAY_2_REST}}</p>
    <p><strong>{{TAKEAWAY_3_BOLD}}</strong> {{TAKEAWAY_3_REST}}</p>
    <p>{{TAKEAWAY_CONCLUSION}}</p>
  </div>

  <!-- FOOTER -->
  <div class="footer">
    <span>{{FOOTER_LEFT}}</span>
    <span>{{FOOTER_RIGHT}}</span>
  </div>

</div>
</body>
</html>
```