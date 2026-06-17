# Roadmap — nonoun-skills (marketplace level)

Each skill keeps its own `*/skills/<skill>/ROADMAP.md` for skill-specific work. This file tracks the
**cross-cutting and marketplace-level** future work — the items that span skills, or that aren't a
single skill's bin deepening.

**Status.** As of the **v0.2.x** line the *deterministically-buildable bin backlog is exhaustively
hardened*: every decomposer's mechanism gate has been deepened, adversarially reviewed against novel
inputs, and fixture-locked (see each skill's `CHANGELOG.md`). What remains below is, **by design**,
either infra-gated, a project, content, or deliberately the adversarial verifier's job — *not* a
deterministic gate we've left unbuilt.

## Not buildable in-repo — needs live infrastructure

These gates already exist as **harnesses** that route to a real tool and report **INCOMPLETE / exit 3**
when the tool is absent (never a false PASS — automation keys on the exit code). "Finishing" them means
wiring a live tool, which the **clean-checkout-true** contract deliberately keeps out of the repo:

- [ ] **Live harness execution** — `query-harness` (a real `EXPLAIN` / dry-run against a database),
  `config-harness` (`terraform plan` / `kubectl diff` against a real backend), and `code-decomposer`'s
  execution harness against a real toolchain plus `mutmut` / `stryker` / `cosmic-ray` **mutation
  scores**. The *parsing* side that needs no live tool is already done — e.g. query-decomposer's
  `EXPLAIN (FORMAT JSON)` plan-smell parser (0.2.3). (Each skill's ROADMAP tracks its own harness side.)

## A project, not an item

- [ ] **Behavioral-eval layer.** Every skill is graded today on **routing** (the checked-in
  `routing-eval` corpora, dogfooded by the gate) and on **gate correctness** (the `bin/` selftests with
  good *and* bad fixtures). What's unmeasured is **output quality** — does invoking the skill produce a
  better artifact than not? Closing this needs a held-out task set per skill, a *with-skill vs baseline*
  run, and a judge: a real eval harness, scoped as its own effort, not a drive-by deepening.

## Content — writable, not a gate

- [ ] **Fuller worked end-to-end transcripts** — a complete SPECIFY → build → DECOMPOSE → GRADE
  transcript with checked-in artifacts, beyond the `examples/walkthrough.md` each decomposer already
  ships (several skills' ROADMAPs track this individually).
- [ ] **A shared adversarial-cross-check template** — the fresh-context skeptic prompt, factored into a
  reusable reference shared across `extraction-` / `code-` / `proof-decomposer` (each names it today).

## Deferred by design — the adversarial verifier's job

Documented *in the skills* as intentionally out of the gate's reach: a deterministic checker cannot do
them honestly, so they route to a fresh-context **adversarial verify** rather than overclaim.

- [ ] **Wrong-span / fuzzy / derivable grounding** (extraction) — a faithful value copied into the
  *wrong field* still grounds (token matching is containment, not alignment); near-verbatim spans (OCR
  noise, hyphenation); arithmetic-derived values (a `total` that is the *sum* of grounded line items).
  The opt-in `WEAK_CONTEXT` proximity cue *approximates* role; true confirmation is the verifier's.
- [ ] **Uninhabited-type detection** (type) — an `allOf` / `oneOf` whose branches can never be jointly
  satisfied (a type with no legal inhabitant).

## Small cross-cutting finish-up

- [ ] **Extend `--json` to the remaining lint bins.** The shared machine-readable report schema
  (`{tool, ok, summary, findings:[{kind, severity, location, message}]}`) shipped for `sql-lint` /
  `config-lint` / `groundedness-check` (0.2.4). The same flag could cover `model-smells`, `regex-check`,
  `proof-structure-check`, and `description-lint` so GRADE/CI can consume every gate uniformly.

---

For per-skill roadmaps, see each `*/skills/<skill>/ROADMAP.md`. Marketplace history is in
[CHANGELOG.md](CHANGELOG.md); the authoring recipe is in [HOWTO.md](HOWTO.md).
