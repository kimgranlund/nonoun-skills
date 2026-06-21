# Roadmap — goals-decomposer

Ships its core in 0.1.0 (the two axes, the measurability gate, the AIM canon, the charter card, the
cross-check seam). Everything below is additive.

## `bin/charter-check.py`

- [ ] **A formal JSON Schema for the charter card** (`schema/charter.schema.json`) + a drift-guard in the
      selftest (enums/required match the bin), mirroring `brand-decomposer`'s pattern. Validate an
      arbitrary charter against it with `type-decomposer`'s `instance-check.py`.
- [ ] **Sharper CONTRADICTION** — beyond the literal non-goal↔characteristic overlap, detect a small set
      of known co-maximize conflicts (a `minimize cost` characteristic + a `maximize redundancy` one with
      no ranking between them). Lock each with a must-FLAG / must-NOT-flag fixture pair.
- [ ] **KPI shape lint** — flag a threshold with a unit mismatch (metric "rate" / threshold "300ms"), and
      a window that names no condition. Advisory.
- [ ] **`--json` already ships**; add a `cross-check` subcommand that takes a charter + an
      `architecture-decomposer` contract card and mechanizes the **coverage** half of the seam (every
      ranked characteristic name appears in some contract node/rule) — the deterministic part of §3 of
      `references/policy.md`.

## The AIM axis (A)

- [ ] **A behavioral-eval pilot** (`behavioral-eval-method.md`): with-skill vs SUPPRESSED-baseline on a
      real PRD. Hypothesis: base-model competence is *inside* the domain (it writes goals fluently), so
      the metric is **verification/structure** — does the skill make the model demand a diagnosis, rank
      strictly, and Goodhart-probe rather than emit a confident wish list?
- [ ] **A worked DESIGN example** — author a charter from a one-paragraph request, to show the DESIGN mode
      end-to-end (diagnosis → ranked -ilities → falsifiable acceptance).

## Cross-plane (the orchestrator)

- [ ] **The CROSS-CHECK mode, mechanized** — once the `nonoun-plugins` two-plane orchestrator
      (`docs/designs/two-plane-orchestrator.md`) lands, wire `charter-check.py cross-check` as the
      coverage gate, and document the staleness contract (a charter change stales the architecture).
- [ ] Promote draft → beta once the JSON-Schema card + drift-guard land, the behavioral-eval pilot runs,
      and the cross-check coverage subcommand ships with fixtures.
