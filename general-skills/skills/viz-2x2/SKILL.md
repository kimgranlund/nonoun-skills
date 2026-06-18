---
name: viz-2x2
description: Create shareable 2×2 matrix diagrams that illustrate strategic trade-offs across two independent axes. Use this skill whenever the user asks to make a 2×2, comparison matrix, quadrant diagram, trade-off framework, strategic positioning map, or any visual that places four archetypes on two axes. Also trigger when the user describes four scenarios or modes and wants to visualize the relationships between them — even if they don't say "2×2" explicitly. Trigger on phrases like "make a matrix", "show the trade-offs", "quadrant diagram", "four modes of X", "compare these four approaches", or when the user provides four things that differ along two dimensions. This skill produces a polished, self-contained HTML artifact with a matrix diagram, summary cards with inline SVG charts, and a takeaway section — all shareable and responsive with light/dark mode.
---

# 2×2 Matrix Artifact Skill

Create polished, shareable 2×2 matrix artifacts that illustrate strategic trade-offs. The output is a self-contained HTML artifact — deployable as a Claude Chat artifact or saved as a file — with a consistent design system optimized for both human reading and sharing.

## Invocation

This is an **artifact-generation** skill. The user describes four scenarios or modes differing along two dimensions. Decompose: (1) validate axis independence, (2) name the quadrants, (3) write summaries with charts, (4) build the HTML artifact.

### Step 1 — Ingestion

Classify the ask surface:
- "Make a 2×2" / "quadrant diagram" → full artifact; derive axes from four items
- "Show trade-offs" → identify the two independent dimensions
- "Four modes of X" → validate that axes are genuinely independent (correlation test)
- "Compare four approaches" → each approach maps to one quadrant

### Step 2 — Decomposition

| Sub-task | Validation |
|---|---|
| Axis independence | Can you name a real example in each quadrant? If not, axes are correlated. |
| Quadrant naming | Memorable 1–2 word names; tag lines ≤5 words; traits explain compounding |
| Summary cards | Mode label, description (why people end up here), reasoning (mechanism) |
| Charts | Two metrics over 6 points; only winning quadrant improves or stays flat |
| Takeaway | 3–4 actionable imperatives, each bolded; migration path if applicable |

### Step 3 — Execution routing

Read `references/template.md` for the full HTML template. Colors are consistent across all matrices: gray (default), teal (sweet spot), coral (anti-pattern), purple (over-engineered). The artifact is self-contained: one HTML file, no external dependencies except Google Fonts.

## First principles

**Two independent axes, not a gradient.** The matrix only works when the axes are genuinely independent — movement along one axis doesn't force movement along the other. If the four quadrants collapse into a single spectrum, it's not a matrix; it's a ranking. Test: can you name a real example in each quadrant? If not, the axes are correlated and the matrix is misleading.

**Each quadrant is an archetype, not a judgment.** Even the "worst" quadrant has scenarios where it's the right choice. The skill produces analysis, not propaganda. Every quadrant gets a fair description of when it applies, not just a label of "bad" or "good."

**The argument lives in the charts.** The matrix shows *what exists*. The charts show *what happens over time or at scale*. The charts are where you make the case for why one quadrant compounds and others degrade. Without charts, it's a taxonomy. With charts, it's a strategic argument.

**Constraint is guidance.** A strict visual template eliminates design decisions so the user can focus on thinking. Same fonts, same colors, same layout, same chart format. Consistency across artifacts creates a recognizable visual language.

## When NOT to use this skill

Don't use this for simple comparison tables (use a markdown table), rankings or tier lists (use a ranked list), decision trees (use a flowchart), or when the user has more or fewer than four archetypes that don't decompose into two axes.

## Workflow

### Step 1: Find the axes

The user usually provides four archetypes (scenarios, modes, strategies). Your job is to find the two independent dimensions that separate them. This is the hardest intellectual step.

**Method:** Take the four archetypes and ask — what distinguishes archetype A from archetype B, but not from archetype C? That distinction is an axis. Repeat for the other pair to find the second axis.

**Validation check:** Place all four archetypes on the resulting 2×2. Does each quadrant contain exactly one archetype? Do the axes feel genuinely independent (not correlated)? Can you name a real-world example in each quadrant?

If the user already named their axes, validate that they're independent. If they're correlated, surface this and propose alternatives.

### Step 2: Name the quadrants

Each quadrant gets three things:
1. **A memorable name** — one or two words that someone can reference in conversation ("the monolith", "pipeline mode", "junk drawer")
2. **A tag line** — ≤5 words in a pill badge that captures the failure mode or defining trait
3. **A trait** — one sentence at the bottom of the quadrant card, separated by a border, that names the compounding or degradation behavior

### Step 3: Write the summaries

Each quadrant gets a summary card with:
- **Mode label** — the axis coordinates (e.g., "Coarse + Unstructured", "Typed → Typed")
- **Name** — the quadrant name from step 2
- **Description** — 3–5 sentences explaining the archetype. What it is, why people end up here, what happens at the extremes. Write as if explaining to a smart peer who hasn't encountered the framework before.
- **Reasoning** — 2–3 sentences in italic that explain the *mechanism* behind the chart curve. This is causal, not descriptive. Why does the curve have this shape?

### Step 4: Design the charts

Each summary card includes a small inline SVG area chart (viewBox 210×110) showing two metrics over a scaling axis (time, pipeline stages, base size, etc.).

**Chart design rules:**
- Two curves per chart: one solid (primary metric), one dashed (secondary metric)
- Area fills beneath each line at ~8-10% opacity
- Y-axis: 0–100 (three labels: 0, 50, 100)
- X-axis: 6 data points, evenly spaced
- The x-axis label describes what's increasing (e.g., "Pipeline stages →", "Knowledge base size →")
- Chart viewBox is `0 0 210 110`, drawing area from x=28 to x=204, y=8 to y=94

**Curve shape guidelines:**
- The "winning" quadrant should be the only one where at least one curve stays flat or improves. This is the visual punchline.
- Degradation curves: use exponential decay for multiplicative problems, linear decline for additive problems
- Collapse curves: high starting value that falls off a cliff (monolith exceeding context window)
- Compounding curves: slight dip then recovery (typed pipeline where verification catches errors)

**Choosing metrics:** Pick two metrics that together tell the strategic story. They should be somewhat independent — if both curves always move together, one is redundant. Good pairs: efficiency + findability, signal retention + data integrity, cost + quality, throughput + reliability.

### Step 5: Write the framing

The artifact has four prose sections surrounding the matrix:
1. **Title** — "The [noun] matrix" (keep it simple)
2. **Subtitle** — one sentence explaining what the framework is for
3. **Intro paragraph** — 3–4 sentences that set up the key insight. Name the common mistake people make (usually: conflating the two axes). Establish the evaluative question the matrix answers.
4. **Takeaway section** — a boxed section at the bottom with a practical "migration path" or "design heuristic." This tells the reader what to *do* with the framework. 3–4 short paragraphs, each starting with a bolded imperative.

### Step 6: Build the artifact

Read `references/template.md` for the full HTML template and design tokens. The template is a complete, working HTML file — fill in the content slots and adjust colors, axis labels, and chart data.

**Color assignments (consistent across all matrices):**
- Q1 (top-left, usually the "default/baseline" quadrant): **Gray** — the unremarkable starting point
- Q2 (top-right, usually the "sweet spot"): **Teal** — the recommended target
- Q3 (bottom-left, usually the "worst" quadrant): **Coral** — the anti-pattern
- Q4 (bottom-right, usually the "over-engineered" quadrant): **Purple** — the technically correct but impractical option

These aren't fixed meanings — they're defaults. If the matrix has a different topology (e.g., the sweet spot is bottom-right), reassign colors to match: teal always goes to the recommended quadrant.

**Axis styling:**
- The "better" end of each axis gets the dark teal background (`--axis-bg`/`--axis-fg`)
- The "worse" or "default" end gets the neutral light background (`--bg1`/`--t3`)

**Two output modes** — pick the one that matches the user's environment:

| Mode | Context | What to do |
|---|---|---|
| **Artifact** | Claude Chat (claude.ai), Claude Design, or any artifact-enabled interface | Wrap the HTML in `<artifact>` tags with a unique identifier. See `references/claude-artifacts.md` for the exact format. |
| **File** | Local disk, GitHub, email attachment, or any file-based sharing | Save as `.html`. The file is self-contained and opens in any browser. |

## Artifact layout (agent wireframe)

The HTML artifact has a strict visual hierarchy. Use this ASCII wireframe when reasoning about DOM structure or layout changes:

```
┌─────────────────────────────────────────────────────────────────┐
│ TITLE: "The [Noun] Matrix"                                      │
│ Subtitle: one sentence                                          │
├─────────────────────────────────────────────────────────────────┤
│ Intro paragraph (3-4 sentences)                                 │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┬─────────────────┐                          │
│  │     AXIS_Y      │     AXIS_Y      │  ← axis labels span top │
│  │     (Better)    │     (Worse)     │                          │
│  ├─────────────────┼─────────────────┤                          │
│  │  Q1 (Gray)      │  Q2 (Teal)      │                          │
│  │  ┌───┐          │  ┌───┐          │  ← name + tagline       │
│  │  │   │          │  │   │          │                          │
│  │  └───┘          │  └───┘          │                          │
│  │  TRAIT          │  TRAIT          │  ← compounding/degrade  │
│  ├─────────────────┼─────────────────┤                          │
│  │  Q3 (Coral)     │  Q4 (Purple)    │                          │
│  │  ┌───┐          │  ┌───┐          │                          │
│  │  │   │          │  │   │          │                          │
│  │  └───┘          │  └───┘          │                          │
│  │  TRAIT          │  TRAIT          │                          │
│  └─────────────────┴─────────────────┘                          │
│  [Gradient bar: worst → best]                                   │
├─────────────────────────────────────────────────────────────────┤
│ SUMMARY CARDS (stacked vertically, each is a full-width block)  │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Q1 Card: Mode label, Name, Description, Reasoning           │ │
│ │     ┌──────────────────┐                                    │ │
│ │     │  SVG AREA CHART  │  (210×110, 2 curves, 6 points)   │ │
│ │     └──────────────────┘                                    │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Q2 Card: ...                                                │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Q3 Card: ...                                                │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ Q4 Card: ...                                                │ │
│ └─────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ TAKEAWAY SECTION (boxed)                                        │
│ • **Imperative 1** ...                                        │
│ • **Imperative 2** ...                                        │
│ • **Imperative 3** ...                                        │
└─────────────────────────────────────────────────────────────────┘
```

**Key structural invariants** (the wireframe encodes these):

| Element | Where it lives | What goes inside it |
|---|---|---|
| **Matrix grid** | Center of page, above summary cards | Four quadrant **cards** (name + tagline + trait only). No charts here. |
| **Summary cards** | Full-width stacked blocks below matrix | Mode label, full description, italic reasoning, **inline SVG chart**. |
| **SVG chart** | Inside each summary card | Two curves (solid primary, dashed secondary), 6 data points, area fill. |
| **Takeaway** | Bottom boxed section | Bolded imperatives, migration path. Never inside a quadrant. |

**Common layout confusion**: The SVG charts are **not** inside the matrix quadrants. The matrix shows topology (what lives in each quadrant). The summary cards explain the mechanics (why each quadrant behaves the way it does, plus the chart evidence). The takeaway tells the reader what to do about it.

### Step 7: Save and present

For **artifact mode**, present the wrapped `<artifact>` block directly in the chat. No file save needed — the artifact renderer handles display, download, and export.

For **file mode**, save as a descriptive filename (snake_case, no spaces) in the current working directory. The file is a complete, self-contained HTML document that works offline and shares via any channel. Keep the post-presentation commentary brief — the artifact speaks for itself.

## Quality checklist

Before presenting the artifact, verify:
- [ ] Axes are genuinely independent (not correlated)
- [ ] Each quadrant has a name, tagline, and trait
- [ ] Summary descriptions explain *why* people end up in each quadrant
- [ ] Reasoning statements explain the *mechanism* behind the chart curves
- [ ] Charts have the correct shape (only the winning quadrant improves or stays flat)
- [ ] Takeaway section has actionable imperatives, not just observations
- [ ] Light and dark mode both render correctly (all colors use CSS variables)
- [ ] OG meta tags populated for link previews
- [ ] Gradient bar at bottom of matrix labels the spectrum from worst to best
