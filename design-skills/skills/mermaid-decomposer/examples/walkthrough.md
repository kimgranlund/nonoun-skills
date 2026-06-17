# Worked example — "right but broken" on INTENT × RENDER

A complete DECOMPOSE → fix → GRADE for one Sankey diagram, showing the **M2 keyword gate** catching
a bare beta keyword and the red→green proof. The two example docs in this folder are checked in and
the render-check actually verifies them. (Both live in `examples/` only — never `references/` — so
the bad block can't trip the gate's dogfood over `references/`.)

## The artifact

An energy-flow diagram: Coal + Gas → Electricity → Homes + Industry, weighted. The author reached for
Sankey (correct — it's a weighted flow) and wrote the block opening with a bare keyword:

```text
sankey

Coal,Electricity,30
Gas,Electricity,20
...
```

Markdown preview renders nothing useful, and the author shrugs — "it's the right diagram type."

## DECOMPOSE

**A · Intent** (relationship → type → skeleton → labels)
- **Relationship** — a *weighted flow* between nodes (sources → sink → sinks). ✓
- **Type** `[M1]` — Sankey is the natural fit for weighted flow. ✓
- Skeleton / labels — three CSV edges, sensible node names. ✓

**B · Render** (keyword → syntax → strict → legibility)
- **Keyword** `[M2 gate, code]` — run the render-check on the doc (`examples/sankey.red.md`):

```
$ python3 bin/mermaid-render-check.py examples/sankey.red.md
mermaid-render-check: FAIL — 1 block(s) (static keyword gate only ...)
  examples/sankey.red.md:4 [static] `sankey` needs the `-beta` suffix — write `sankey-beta` (bare `sankey` is a syntax error in 11.x)
```

**M2 gate fails.** In mermaid 11.x the keyword is `sankey-beta`; the bare `sankey` is a hard syntax
error — nothing renders. The diagram is the *right type* (M1 is fine) but it is *broken* on the way
out. A failed `[gate]` blocks the rest of the RENDER axis (syntax/strict/legibility): no point
grading legibility on a block the engine refuses to parse.

## Fix

Add the `-beta` suffix — one token (`examples/sankey.green.md`: `sankey-beta`):

```
$ python3 bin/mermaid-render-check.py examples/sankey.green.md
mermaid-render-check: OK — 1 block(s) pass (static keyword gate only ...)
```

Nothing else changed — same nodes, same weights, same skeleton. The defect was never the design; it
was a missing suffix on an otherwise correct diagram. (Where `mmdc` is on PATH the same command also
renders the block under `securityLevel:strict` — the full M3 test.)

## GRADE — two scores, never averaged

- **Intent: 5/5** — right relationship (weighted flow), right type (Sankey), clean skeleton + labels.
- **Render: M2 gate-fail → (after fix) 5/5** — keyword now exact; syntax/strict/legibility all clear
  on a block the engine accepts.

**Quadrant:** the red doc sat in **"right diagram, broken output"** (Intent passed — it IS a Sankey —
but Render's keyword gate failed) — *designed right, rendered wrong*. The fix is one suffix, not a
re-think of the diagram. After it: **SHIPPABLE**.

The lesson: a correct diagram type is invisible to the engine if the keyword is off by a `-beta` —
and you can't eyeball "will it render"; you feed the fence to the gate and watch it mint the verdict
from the source text, never from inference.
