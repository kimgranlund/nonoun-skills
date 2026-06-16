# The two-axis decomposition method (for Mermaid diagrams)

A Mermaid diagram is correct on **two independent axes that traverse the same hierarchy in opposite directions** — the same outside-in / inside-out seam the UI decomposer applies to *space*, here applied to a *diagram*. Decompose (or create, or grade) any diagram by walking *both*.

```
            INTENT  (whole → atom · "what the diagram CLAIMS")
   ┌────────────────────────────────────────────────────────────┐
   │  A1 Relationship → A2 Type → A3 Skeleton → A4 Elements → A5 Labels
   │                              ⤫  cross at the TYPE's grammar  │
   │  B5 Portable/a11y ← B4 Legible ← B3 Strict ← B2 Syntax ← B1 Keyword
   └────────────────────────────────────────────────────────────┘
            RENDER  (atom → whole · "what actually DRAWS, here")
```

The axes **cross at the diagram type**: the type is simultaneously the *claim* (it expresses one relationship — top of Axis A) and the *grammar* (it fixes the exact keyword + syntax that must render — bottom of Axis B). Two failure shapes follow, and they are opposites:

- **Right but broken** — Axis A passes (correct type for the relationship, sound structure) but Axis B gate-fails (a missing `-beta`, a `securityLevel:strict` violation, a feature newer than the target's pin). The diagram *means* the right thing and *draws nothing* — a syntax error or a blank.
- **Renders but wrong** — Axis B passes (valid syntax, clean render) but Axis A fails (a `flowchart` faking a `sequenceDiagram`; a generic `graph` where the relationship is really set-overlap → should be `venn-beta`). The diagram *draws fine* and *communicates the wrong structure*.

Because they are opposites, **score and report the two axes separately. Never average them** — a single middling number hides which of the two defects you have, and they need different fixes (re-pick the type vs. fix the keyword/strict-safety).

> The two axes are the **walk**; `mermaid-rubric.md` (M1–M6) is the **scorecard** — they are one system. Each level below names the rubric dimension it scores. `advanced-mermaid-reference.md` is the **type catalog** the walk consults.

---

## Axis A — Intent (relationship → label · top-down)

Zoom in from "what am I even communicating?" down to a single label. **Each level is only meaningful once the level above it holds** — a wrong type makes the skeleton beneath it meaningless, so grade top-down and stop at the first gate that fails.

### A1 · Relationship `[gate]`  → rubric M1
The diagram expresses **one clear relationship**. Name it in a word: **flow · sequence · structure/containment · hierarchy · time/schedule · stage/process · overlap · causation · value-chain · comparison**.
- If the content is secretly *several* relationships mashed together, **no single type fits** — that is the gate failure: split it into multiple diagrams (or pick the dominant relationship and demote the rest to prose).
- *Cascade:* a muddled intent makes A2 (type) unmeasurable. Resolve the relationship first.

### A2 · Type-fit `[gate]`  → rubric M1
The chosen **diagram type matches the relationship** (consult the `advanced-mermaid-reference.md` §2 matrix).
- flow→`flowchart`/`sankey-beta` · sequence→`sequenceDiagram` · schema→`erDiagram` · time→`gantt`/`timeline` · journey→`journey` · board→`kanban` · overlap→`venn-beta` · causation→`ishikawa-beta` · strategy→`wardley-beta` · deployment→`architecture-beta` · event-sourcing→`eventmodeling`.
- *Cascade:* the wrong type forces the content into the wrong skeleton — A3–A5 grade a structure that shouldn't exist. **Re-pick the type before refining anything below.**

### A3 · Skeleton `[review]`  → rubric M4
The **top-level organization** fits the content: sections (`journey`/`gantt`), columns (`kanban`), swimlanes (`eventmodeling`), groups (`architecture-beta`), direction (`TD`/`LR`), sets (`venn-beta`). One organizing principle, applied consistently.

### A4 · Elements `[review]`  → rubric M4
The **nodes / tasks / entities / sets** are the right grain and count — enough to carry the meaning, few enough to read (≈ ≤15–20 nodes). Not one mega-node hiding structure; not 50 atoms no one can trace.

### A5 · Labels `[review]`  → rubric M4
Atomic **text** is short, consistent, and unambiguous. Parallel phrasing across siblings; no essay in a node; special characters quoted so they read as text, not syntax.

---

## Axis B — Render (keyword → whole · bottom-up)

Build out from the single token that names the diagram to the whole rendered picture. Each level presumes the one before it. **The first three are gates** — a diagram that won't draw cannot be judged on legibility (you can't read what doesn't render).

### B1 · Keyword `[gate]`  → rubric M2
The **first line is the exact diagram keyword, including any `-beta` suffix**. This is the #1 real failure.
- `-beta` required: `sankey-beta` · `architecture-beta` · `venn-beta` · `ishikawa-beta` · `wardley-beta` · `treeView-beta`. **No** suffix: `kanban` · `eventmodeling` · `journey` · `gantt` · `erDiagram` · `flowchart` · `sequenceDiagram`.
- ⚠️ The mermaid.ai docs show bare `sankey` — it is a **hard syntax error**; the OSS engine needs `sankey-beta` (issue #7613).

### B2 · Syntax `[gate]`  → rubric M2
**Every construct parses** in the target's pinned engine (default: `mermaid@11.15.0`).
- No feature newer than the pin; labels with `()`/`:`/`#`/`,`/`-` quoted; one statement per line; status tags / cardinality pairs / metadata blocks well-formed per the type's grammar.

### B3 · Strict-safety `[gate]`  → rubric M3
It renders under **`securityLevel:"strict"` with no host-side config**.
- **No** `click`/`call` interactivity, **no** HTML in labels (`<br/>`/`<b>`/`<a>` are encoded to literal text under strict), **no** non-built-in `architecture-beta` icons (iconify packs need a host `registerIconPacks()` a fence can't call), **no** reliance on JS-only config (`sankey`/`kanban` width/colors/`ticketBaseUrl`). Anything meaning-bearing that depends on these is broken in a strict host.

### B4 · Legibility `[review]`  → rubric M4
The **rendered whole** is scannable in a glance: bounded node/edge count, a sensible direction, chunking via `section`/`group`, no hairball of crossing edges. If it conveys less than the table it replaced, split or simplify.

### B5 · Portability + accessibility `[review]`  → rubric M5 + M6
The diagram **travels and is accessible**: all config in-fence (frontmatter `config:` / inline `style`, not host JS); deterministic layout (force-directed types like `architecture-beta` pinned via `randomize`/fcose knobs); `accTitle:`/`accDescr:` set; meaning never carried by color alone; no hard-coded theme that fights the host's light/dark.

---

## Scoring

- A `[gate]` failure on **A1 · A2** (intent) or **B1 · B2 · B3** (render) ⇒ **BLOCKED**: fix it before grading any `[review]`. A wrong type makes the structure meaningless; a diagram that won't render can't be read.
- `[review]` dimensions score **1–5**; a shippable diagram is **≥4 on every review with zero gate failures**.
- **Report the Intent axis and the Render axis separately**, gate failures first, each with the single corrective it implies. Then roll up to the `mermaid-rubric.md` M1–M6 scorecard if a formal grade is wanted.

---

## Workflows

### DECOMPOSE (read an existing diagram → what it is + grade)
1. **Name the relationship (A1)** the diagram is *trying* to show — in one word.
2. **Check type-fit (A2)** — does the keyword match that relationship? If not, that's the headline (renders-but-wrong); name the better type and stop refining the structure.
3. **Render-walk (B1→B3)** — exact keyword incl. `-beta`? parses on the pin? strict-safe? Any gate failure here is the headline (right-but-broken).
4. **Judge the reviews** — skeleton/elements/labels (A3–A5) and legibility/portability/a11y (B4–B5) only while the gates hold.
5. **Two-axis verdict** — separate Intent and Render scores, gate failures first, one fix each.

### CREATE (intent → a diagram that renders)  — *Intent down, then Render up*
1. **Relationship → Type (A1→A2)** — name the one relationship, pick the matching type from the `advanced-mermaid-reference.md` matrix. This decides everything.
2. **Pull the verbatim minimal example** for that type from the reference; start from it, never from memory (the `-beta` suffix and the exact grammar are easy to misremember).
3. **Render-safe by construction (B1→B3)** — keep the exact keyword; stay inside 11.15.0; assume strict (no clicks, no HTML labels, built-in icons only, in-fence config only).
4. **Fill the structure (A3→A5)** — skeleton, then elements at the right grain, then short consistent labels.
5. **Finish on the reviews (B4→B5)** — legible (bounded, chunked), portable + accessible (`accTitle`/`accDescr`, deterministic, in-fence config).
6. **Verify it renders** — paste into the target host (e.g. a corpus-reader bake, or `mermaid.live` pinned to v11 with strict) before committing. A diagram that doesn't render is worse than prose.

### GRADE (score a diagram against the rubric)
Run `mermaid-rubric.md` M1–M6 top-down, the two `[gate]` dimensions (M2 syntax/version, M3 renders-in-target) before the reviews, with evidence cited from the diagram source (not impressions). One Critical (a gate failure) plus its corrective beats a page of prose.

---

## Reading the cross (worked shape)

```
                          INTENT
        A1 relationship ─ A2 type ─ A3 skeleton ─ A4 elements ─ A5 labels
                                    │
   the TYPE  ───────────────────────┼──────────────  the same type is…
                                    │
        B1 keyword ─ B2 syntax ─ B3 strict ─ B4 legible ─ B5 portable
                          RENDER
```
A `sankey-beta` energy flow is, on Axis A, *relationship=flow → type=sankey → three-column CSV → the flows → short node labels*; on Axis B it is *the exact `sankey-beta` keyword → valid 3-column rows → renders under strict (its width/color config left at host defaults, since those don't travel) → readable widths → `accDescr` set*. Grade it on both: a perfectly-chosen Sankey written as bare `sankey` aces Axis A and renders **nothing** — a textbook *right-but-broken*.
