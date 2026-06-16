# Roadmap — ui-mermaid-decomposer

## Now (0.1.0)
The two-axis method + the advanced-Mermaid reference + the M1–M6 rubric, usable for CREATE / DECOMPOSE / GRADE against `mermaid@11.15.0` under `securityLevel:"strict"`. Plus `bin/mermaid-render-check.py` — the **mechanized M2/M3 gate**: a stdlib static keyword gate (catches a bare `sankey`/`architecture`/… missing its `-beta`, no engine needed) + an `mmdc` render layer (verdict from exit status) that lights up when the mermaid CLI is on PATH. Selftested.

## Next
- **A routing-eval corpus** (`evals/routing-corpus.json`) — trigger + adversarial phrases scored before the
  description is locked (the skills-studio D5 gate), so routing accuracy is measured, not assumed. Adversarials
  route to ui-layout-decomposer (UI structure, not diagrams) and brand-forge (visual taste).
- **Bundle `mmdc` into CI** — the render layer only fires where the mermaid CLI is installed; wire it into whatever
  ships this skill so the full M3 render gate runs on every change, not just the static keyword gate.
- **A worked CREATE + GRADE example per family** — one real diagram taken end-to-end on both axes, as a calibration
  reference for the rubric (the analog of ui-layout-decomposer's per-archetype worked decompositions).
- **Version-drift note** — when the target host bumps its mermaid pin, what changes (new types graduate out of
  `-beta`, new keywords appear); a short procedure for re-validating the keyword/version matrix.

## Someday
- **Promote `treeView`/`venn`/`ishikawa`/`wardley`/`sankey`/`architecture` out of `-beta`** in the reference once
  the upstream engine drops the suffix — a single-source keyword matrix the `bin/` check reads.
- **Cross-link the seam:** ui-layout-decomposer (UI structure) hands a flow/state that wants a diagram here;
  brand-forge takes the visual/color taste. One review, three homes.
- **A second host profile** beyond the corpus-reader — e.g. GitHub-flavored Markdown's mermaid (a different pin +
  different security posture), so the "reader-compatibility contract" generalizes to a named set of targets.
