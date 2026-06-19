# Changelog

Notable changes to the **nonoun-skills marketplace** — plugins, the gate, and cross-cutting work.
Each skill also keeps its own `CHANGELOG.md`; this file tracks the repo as a whole. Entries are
grouped by date; the first tagged release is **v0.2.0** (2026-06-17).

## 2026-06-19 — post-v0.3.0 cross-cutting work

- **Behavioral-eval method piloted + templated** — a new root [`behavioral-eval-method.md`](behavioral-eval-method.md):
  the method for measuring whether invoking a skill *improves the output* (with-skill vs a **suppressed**
  baseline, scored on a competence-matched, `bin/`-grounded metric), proven on two skills with contrasting
  results — component-decomposer (out-of-competence → the skill lifts correctness) and config-decomposer
  (in-competence → the skill adds verification/provenance/structure, not raw recall). Moves the ROADMAP's
  behavioral-eval item from "a project" to "piloted; automation still open". *(Byproduct: the config pilot
  surfaced a real `config-lint` false-negative — k8s `env`-list secrets — now on its ROADMAP.)*
- **A consistent `--json` report across 13 of ~19 lint bins** — extended the shared
  `{tool, ok, summary, findings:[…]}` schema (matching sql-lint) to the 3 new decomposers' bins + 4 more,
  so GRADE/CI can consume every consuming gate uniformly.
- **Decomposer coherence pass** — fixed stale `arch-system` references (→ `architecture-decomposer`,
  which graduated from it) in code-/query-/type-decomposer; reconciled skill statuses; closed the
  module↔shell and architecture↔code handoff seams.
- **component-decomposer 0.3.x** — absorbed the composition scale (the retired ui-decomposer draft) and a
  separate compact/dense geometry realm; see its CHANGELOG.

## 2026-06-18 — v0.3.0: the graduation (root library → marketplace)

The marketplace nearly tripled — **6 plugins / 14 skills → 11 plugins / 37 skills** — by graduating
the reusable, domain-agnostic skills from the root `~/.claude/skills` library into versioned, gated,
corpus-tested nonoun plugins. Each graduate was adapted to the contract (name==dir, ≤1024 description,
resolving links, fences rewritten to in-repo peers) and matured to the routing standard.

- **Five new plugins.** `general-skills` (research-survey · viz-2x2 · tool-stress), `knowledge-skills`
  (meta-expert-author · meta-theory-author · plan-knowledge · ops-knowledge), `manager-skills`
  (report-brief/-progress/-state/-strategic · resume-author), `skills-skills` (skills-studio ·
  skills-refactor · meta-app-scaffold), `plugins-skills` (plugin-decomposer).
- **design-skills → 0.5.0** (+6): `ref-polyfills` (reference) and the `ui-verify-*` family renamed to
  the **`*-verifier`** category (color/focus/i18n/perf/safety), each now backed by a card-based `bin/`
  mechanism gate (contrast ratio, CWV budgets, tabindex/focus, lang/dir/hardcoded-strings, the
  blast-radius×reversibility safety matrix).
- **code-skills → 0.5.0** (+1): `architecture-decomposer` — a net-new STRUCTURE × INTEGRITY decomposer
  with a Tarjan-SCC / layering / coupling `bin/` (graduated from the root `arch-system` knowledge).
- **plugin-decomposer** — a net-new BUNDLE × MANIFEST decomposer (a plugin manifest/structure linter).
- **Maturation.** All 22 graduated imports carry sibling-tested routing corpora + sharpened NOT-for
  fences (cross-fenced within families: the verifiers, the report-* family, expert↔theory,
  studio↔refactor); the gate's routing dogfood confirms the imports add zero new collisions.
- **Collision cleanup.** As each plugin was installed, its root twin was retired to
  `~/.claude/skills-retired/` (reversible) — **26 twins** total — so every request routes to exactly
  one (installed nonoun) skill. Gate green throughout: 37 skills, 26 bin selftests.

## 2026-06-17 — v0.2.x gate-deepening sweep (post-release)

A run of single-bin mechanism-gate deepenings across the decomposers, each **additive, fixture-locked,
and adversarially reviewed against novel inputs** (the review caught real bugs — a single-line-TS field
parser, a too-narrow k8s gate, a rate-limited agent's dropped constant — all fixed and locked). Per-skill
detail lives in each `CHANGELOG.md`; the cross-cutting threads:

- **A self-enforcing routing gate** — `check-skills.py` now dogfoods `routing-eval` over every skill's
  checked-in corpus and surfaces sibling-collision drift as advisory WARNs (the Phase-1 cleanup can't
  silently rot).
- **A consistent `--json` report mode** — `sql-lint`, `config-lint`, and `groundedness-check` emit one
  shared schema (`{tool, ok, summary, findings:[{kind, severity, location, message}]}`) so GRADE/CI can
  consume findings uniformly.
- **Gate deepenings** — regex AST-ReDoS; SQL join-fanout / outer-join-demotion / non-sargable /
  `EXPLAIN`-plan smells; config URL/base64/heredoc secrets, k8s privilege, world-writable, an allowlist;
  type TS/Python type-stubs + the full conditional/composition/structural keyword set; extraction
  locale numbers & dates, non-ASCII digits, `--spans` provenance, a configurable floor; proof
  modular/divisibility counterexamples; schema-check `additionalProperties`/`uniqueItems`/`const`/`$ref`.
- **A marketplace [ROADMAP.md](ROADMAP.md)** — the cross-cutting future work (live-harness execution,
  the behavioral-eval layer, worked transcripts, the by-design adversarial-verifier items) is now
  documented, with the deterministically-buildable bin backlog declared exhausted.

## 2026-06-17 — v0.2.0 (first tagged release)

The maturation milestone: every full-stack skill promoted **draft → beta**, and the marketplace's
first version tag. A four-phase program, each phase run **build → adversarial review → fix → gate**:

- **Routing corpora + sibling-collision analysis.** A checked-in routing-eval corpus per skill
  (positives across phrasing families + adversarial sibling-trigger negatives). The corpora surfaced
  that 8 of the 11 near-identically-phrased decomposers lexically grabbed each other's requests;
  each NOT-for fence was sharpened to name the colliding sibling's vocabulary — **12/13 skills now
  collision-clean**, recall held, the one residual a documented genuine ambiguity (not gamed).
- **Deepened mechanism gates.** `regex-check` ReDoS detection rebuilt on the real regex AST (stdlib
  `re._parser`) — verified against 14 novel patterns beyond its own fixtures. `groundedness-check`
  gained an opt-in wrong-span proximity signal, with role-confirmation honestly routed to
  adversarial verify rather than overclaimed as deterministic.
- **Worked walkthroughs.** All 11 decomposers ship an `examples/walkthrough.md` — a DECOMPOSE → fix
  → GRADE transcript, 10 of them with a checked-in red→green pair the bin actually verifies.
- **Promotion.** 13 skills → `status: beta`, `v0.2.0`; plugins bumped (design-/code-skills 0.4.0;
  data-/meta-/reasoning-/ops-skills 0.2.0); tagged **v0.2.0**. (`figma-plugins` is concurrently
  maintained — untouched.)

## 2026-06-16

### The decomposer expansion

The repo grew from **2 UI decomposers + 2 reference skills in one plugin** into a **6-plugin
marketplace of 14 skills, 11 of them decomposers** — as the two-axis technique (intent × mechanism,
scored separately, mechanism routed to a self-tested `bin/` gate) generalized from UI to code,
structured data, skill-routing, reasoning, and infrastructure.

#### Added — decomposers

- **component-decomposer** (`design-skills`) — COMPOSE × REALIZE for zero-dependency web components.
  Carries a deterministic geometry engine (`geometry-check.py`: every glyph centered in a square cell
  ⇒ edge padding = (height − glyph)/2, so an icon-only button is square) and a contract linter.
- **code-decomposer** (`code-skills`, new plugin) — SPEC × EXECUTION for a unit of code. An execution
  harness routes the mechanism axis to the real toolchain; a test-vacuity linter attacks the
  "green but wrong" quadrant (tests that can't fail for the right reason).
- **regex-decomposer** (`code-skills`) — LANGUAGE × MATCH; example-set runner + ReDoS-smell scan.
- **query-decomposer** (`code-skills`) — SEMANTICS × EXECUTION; SQL linter + EXPLAIN/dry-run harness;
  the crossing seam is the query against the schema, and grain is the contract.
- **type-decomposer** (`code-skills`) — MODEL × VALIDITY; "make illegal states unrepresentable",
  proven by a JSON-Schema-subset validator over **legal and illegal** instance sets.
- **extraction-decomposer** (`data-skills`, new plugin) — FIDELITY × VALIDITY; a groundedness check
  catches invented values a schema gate is blind to (gate validity, adversarially verify fidelity).
- **routing-decomposer** (`meta-skills`, new plugin) — INSTRUCTION × ROUTING; grades a skill's
  frontmatter description with a mechanized precision/recall routing eval + a description linter.
- **proof-decomposer** (`reasoning-skills`, new plugin) — ARGUMENT × VERIFICATION; a proof-structure
  DAG check (circular reasoning / dangling citations / goal-reachability) + a safe numeric
  counterexample search.
- **config-decomposer** (`ops-skills`, new plugin) — INTENT × VALIDITY; validate/plan harness + a
  safety linter (plaintext secrets, `:latest`, wide-open permissions); the plan is the contract.

#### Added — other

- **figma-plugins** (`code-skills`) — a domain build skill for Figma plugins (the sandbox↔iframe
  message bridge, the variables API, headless testing). Not a decomposer.
- **New plugins**: `code-skills`, `data-skills`, `meta-skills`, `reasoning-skills`, `ops-skills`.
- **Root docs**: `HOWTO.md` (how to author a decomposer) and this `CHANGELOG.md`; `README.md`
  rewritten around the decomposer spine.

#### Changed

- `design-skills` 0.2.0 → 0.3.0 (adds component-decomposer). `code-skills` → 0.3.0.
- `marketplace.json` now registers 6 plugins.
- The gate (`bin/check-skills.py`) is unchanged in contract but now validates 14 skills / 19 bin
  selftests; every new mechanism gate is stdlib-only and self-tested.

#### Fixed — adversarial hardening pass

A parallel adversarial review ran each new tool with hostile inputs and found real defects the
shallow one-fixture selftests missed — several where the tool certified the very thing it exists to
catch as safe. Each fix is **locked with the adversarial input as a regression fixture**:

- **regex** — ReDoS scan reported catastrophic patterns (`(.*a){10}`, `(a?){20}a{20}`, bounded
  `{m,n}` nesting) as "safety clean"; now flags the polynomial family. Dropped a false-positive on
  disjoint alternation. Static scan documented as a lossy pre-filter.
- **query** — `IMPLICIT_CROSS_JOIN` was defeated by any `=` in WHERE; now needs a real
  `ident.ident = ident.ident` predicate. GROUP_BY false-positives on window functions/constants fixed.
- **extraction** — groundedness was a raw substring test (invented "Fran" grounded in "Francisco");
  now token/word-boundary matching + a weak-grounding floor; `schema-check` warns on unknown keywords.
- **routing** — the token-overlap eval inverted its own doctrine (the NOT-for fence lowered the
  score); the fence now repels, and the eval is demoted from "the proof" to a legibility aid.
- **proof** — a numeric-spotcheck DoS via nested `**` (`((n**64)**64)**64`) bounded by predicted
  result size + a wall-clock budget; empty-`from` steps flagged UNJUSTIFIED. (Code-injection defense
  held.)
- **config** — secret linter missed trailing-comma / single-line-JSON / YAML-list secrets and
  multi-line wildcard IAM; all now flagged; tri-state plan verdict (terraform exit 2 = changes-present).
- **type** — validator conflated `bool` with `int` (`true` matched enum `[0,1,2]`) and silently
  ignored `$ref`/unknown keywords; now type-aware equality + default-deny (`UNSUPPORTED_SCHEMA`).
- **shared harnesses** — a skipped gate (tool absent) now reports **INCOMPLETE / exit 3**, never a
  PASS — consistent with the "a skip is no evidence" doctrine (`execution-harness`, `query-harness`,
  `config-harness`).

### Foundation (earlier the same day)

- `nonoun-skills` established as a dedicated home + marketplace for general-purpose skills.
- `design-skills` plugin (renamed from `ui-decomposers`); added the `color-science` and
  `typography-lettering` reference skills.
- The two original decomposers renamed to drop the `ui-` prefix (`layout-decomposer`,
  `mermaid-decomposer`).
