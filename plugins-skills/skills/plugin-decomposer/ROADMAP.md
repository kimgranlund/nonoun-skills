# Roadmap — plugin-decomposer

Ships its core in 0.1.0 (the two axes, the manifest checker, the plugin-anatomy contract, the
quadrant). Everything below is additive.

## `bin/plugin-check.py`

- [ ] **On-disk path resolution** (optional `--root DIR`): given the plugin dir, assert each declared
      component/source path *exists* (closing the gap between B4 "legal shape" and "actually there") —
      the analogue of the repo gate's `files[]`-exist check, but for plugin components.
- [ ] **Component discovery**: walk the plugin dir for convention-discovered components
      (`skills/*/skill.json`, `commands/*.md`, `agents/*.md`, `hooks/`, MCP config) and compute the
      kitchen-sink kind-count from what's *on disk*, not only what's *declared* — catching a bundle
      that smuggles in components the manifest doesn't list.
- [ ] **`--json` report mode** so GRADE can fold the manifest verdict into the report card (matching
      the round-3 `--json` convention across the lint bins).
- [ ] **Richer name/version diagnostics**: distinguish the specific kebab violation (leading hyphen vs
      underscore vs caps) and the specific semver violation, each as its own fixture.
- [ ] **Marketplace cross-checks**: warn when the marketplace `description` and the `plugin.json`
      `description` drift, or when a `category`/`tags` entry is missing (advisory, not a gate).

## Method & corpus

- [ ] A **routing-eval corpus** (`plugin-decomposer.corpus.json`) — the maturity step the repo ROADMAP
      tracks. The sharp sibling collisions to lock: `skills-studio` / `skills-skills` (authoring a
      SKILL, not a plugin), `code-decomposer` (a unit of code), `core-mcp-best-practices` (an MCP
      perimeter), and the global `plugins-factory` peer (lifecycle authoring vs. this skill's
      decompose/grade focus).
- [ ] A worked **end-to-end transcript** (a `db-toolkit` DESIGN → DECOMPOSE → GRADE) with the one-job
      statement, the component map, the manifest report card, and a kitchen-sink split checked in and
      dogfooded.
- [ ] An **adversarial one-job probe template** (the fresh-context skeptic prompt: "what two jobs is
      this really doing? which component would a user disable?") as a reusable reference, shared in
      shape with `deep-research`'s verify step and the `plugins-factory:plugin-critique` council.
- [ ] A **standing-context cost** deepening for A5 — a heuristic for estimating the always-on token
      weight a bundle adds (skill descriptions + command names + agent definitions + MCP tool schemas
      carried every session) if the single quadrant table proves too thin.

## Plugin

- [ ] As `plugins-skills` grows, candidate siblings from the same authoring lineage: a
      `marketplace-decomposer` (the catalog itself: are the plugins well-partitioned, do the
      descriptions route, is there sibling overlap?) and a `hook-decomposer` (a plugin hook's blast
      radius / safety, paired with a deterministic permission-scope checker).
- [ ] Seam-tighten with the global `plugins-factory` family — this skill is the nonoun-native
      decompose/grade peer; keep the `NOT for …` fence and the corpus negatives in sync as that family
      evolves.
