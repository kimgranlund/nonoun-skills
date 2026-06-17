# Changelog

Notable changes to the **nonoun-skills marketplace** — plugins, the gate, and cross-cutting work.
Each skill also keeps its own `CHANGELOG.md`; this file tracks the repo as a whole. The marketplace
has no version tags yet, so entries are grouped by date.

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
