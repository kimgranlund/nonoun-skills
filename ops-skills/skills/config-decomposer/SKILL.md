---
name: config-decomposer
description: >
  Decompose, design, and grade a configuration / infrastructure-as-code artifact (YAML/HCL/JSON/TOML
  — CI configs, Terraform, k8s manifests, Dockerfiles, app config) on two crossing axes — INTENT
  (desired-state → contract → cases → drift → fit) and VALIDITY (parse → schema → plan → safety →
  observability) — scored separately so a config that validates can't hide one that provisions the
  wrong thing. Doctrine: the PLAN is the contract — a config's behavior is its diff against current
  state, not its text. VALIDITY routes to the tool's own validate/plan; a missing tool is a SKIP, not
  a pass. Mechanizable safety smells — plaintext secrets, :latest, 0.0.0.0/0, wildcard grants,
  missing limits — route to a static linter. Use when authoring a config, grading an IaC artifact, or
  catching a surprise-destroy / valid-but-wrong drift. NOT for application code (code-decomposer), a
  correct JSON Schema / type / data model (type-decomposer), a deductive argument / proof
  (proof-decomposer), /verify, arch-system, /simplify.
---

# config-decomposer — grade a config on two crossing axes

A configuration / infrastructure-as-code artifact is **correct on two independent axes that walk the
same hierarchy in opposite directions** — the decomposer seam the layout-, mermaid-, component-, and
code-decomposers apply to space, diagrams, components, and code, here applied to a config (a CI
workflow, a Terraform module, a k8s manifest, a Dockerfile, an app config):

- **Intent · whole → part** grades the **intent**: the desired state it should produce → its contract
  (the resources/keys other configs depend on) → the cases it handles → its drift/idempotency → its
  fit with the project. *"Is it the right config?"*
- **Validity · part → whole** grades the **mechanism**: it parses → its keys/types are schema-valid →
  it plans (validate/dry-run succeeds *and the diff is the intended one*) → it's safe → its plan is
  reviewable. *"Does it provably apply, here, to the right effect?"*

They **cross at the config measured against the tool's schema/state** — the same text is *both* the
claim (what infrastructure should exist) and the mechanism (what the validator accepts and what the
plan diff will actually do). That crossing is the whole technique: a config can be **right intent,
won't validate/plan** (right desired state and contract, but a syntax/type error or a `plan` that
errors) or **valid config, wrong outcome / drifts** (parses, validates, field types right — but it
provisions the wrong thing, the plan diff is a *surprise destroy*, a silent default flips an
environment, or re-applying it isn't idempotent). Opposite defects, opposite fixes — so you **score
and report the two axes separately**, never averaged.

The reason this is outsized for an LLM author: VALIDITY is exactly where models emit confidently-wrong
config *and* it is mechanizable — so the gate converts the worst failure into a caught error. And the
**valid config, wrong outcome** quadrant — the one a green parse hides — gets a dedicated attack: read
the **plan diff** against the stated desired state, plus a static safety linter for the mechanizable
smells (secrets, `:latest`, `0.0.0.0/0`, wildcard grants).

## Quick Start

**You bring:** a config (a spec, a Terraform/YAML file, a Dockerfile) and the question — "design
this", "is this right?", "what will this actually do?", "is it safe to apply?". **You get:** a
config-spec card (desired state + contract), a validity report card with the plan verdict, and a
two-axis grade with the defect quadrant named.

> *"Is this `web-asg.tf` ready to apply?"* →
> 1. **Intent — desired-state → contract:** the desired state is "3 web nodes in an ASG behind an
>    internet-facing ALB in us-east-1" `[gate]`; the contract is its outputs `alb_dns_name`,
>    `web_sg_id` that other configs read `[gate]`. Cases: dev/stage/prod node counts, the unset `ami`.
> 2. **Validity — plan it, don't read it:** `bin/config-harness.py` runs parse + validate + **plan**
>    `[gate]`. Green that it *ran*? Now prove the diff is *intended*: read it against the desired state
>    — create 4 / destroy 0, or a **surprise destroy** of the DB? Idempotent (2nd plan empty)?
> 3. **Safety floor:** `bin/config-lint.py` — a plaintext secret, a `:latest` image, a `0.0.0.0/0`
>    ingress, a wildcard `"*"` grant is a gate-grade finding.
> 4. **Review + report:** cases/drift/fit (A3–A5), safety/observability (B4/B5), then the two axis
>    scores + the quadrant cell — gate failures first — handed to a config author and `/verify`.

**Modes:** **SPECIFY** (Intent-down → declare the validity plan → emit a config-spec card) ·
**DECOMPOSE** (read a config → recover the desired state → run validate/plan + safety lint → grade) ·
**GRADE** (score both axes, gates before reviews).

## The two axes (the method)

Load `references/decomposition-method.md` for the full method. The skeleton:

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Intent** | whole → part | **A1** Desired-state → **A2** Contract → **A3** Cases → **A4** Drift & idempotency → **A5** Fit | "Is it the *right config*?" |
| **B · Validity** | part → whole | **B1** Parses → **B2** Schema → **B3** Plan → **B4** Safety → **B5** Observability | "Does it *provably apply*, to the right effect?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** (a failure cascades and BLOCKS the reviews below it on
that axis). `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable config is **≥4 on every review with
zero gate failures**, reported as two separate axis scores plus the defect quadrant. Two gates route
to code: **B1/B2/B3 validity** → `bin/config-harness.py`; the **B4 safety floor** → `bin/config-lint.py`.

## The doctrine — the PLAN is the contract

The non-obvious core, and the reason it earns a skill:

- **A config's real behavior is its diff against current state, not its text** — the same HCL creates
  on an empty state and *destroy-and-replaces* on a populated one. Route B1/B2/B3 to the tool's own
  `validate`/`plan` via `bin/config-harness.py` and **trust the plan, not the read-through**. It
  catches *right-intent-won't-validate* outright.
- **A missing tool is a SKIP, not a pass**, and a green parse with an unreviewed plan is **no
  evidence**. The harness flags a skipped gate as `NO EVIDENCE` so it can't be mistaken for green.
- **"Valid config, wrong outcome / drifts" is NOT a parse-time error** — it's on the INTENT side and
  hidden inside B3 ("is the diff the *intended* one?"). Route it two ways: **read the plan diff**
  against the stated desired state (a surprise destroy, a silent default, a non-idempotent churn —
  every line is a claim to verify, see `plan-and-drift.md`), and the **safety lint** for the
  mechanizable smells (`config-lint.py`).
- **Safety smells are mechanizable — gate them.** A plaintext secret, a `:latest` image, a
  `0.0.0.0/0`, or a wildcard IAM grant that `config-lint.py` raises is a gate-grade FAIL, not taste.
  The linter is the cheap first pass (it catches the common shapes — inline/trailing-comma/list
  secrets, multi-line wildcard arrays); a clean run is not proof of safety, so a high-stakes config
  also gets the deeper policy engine wired as the harness `policy` phase.

## The tools & formats (pick by what the config targets)

Each format tells you **which validator proves VALIDITY** and **where the INTENT defect hides** — it
focuses the method, doesn't change it. Full per-tool manifest table in `references/validity-axis.md`.

| Format | Decisive validity gate / intent risk |
|---|---|
| Terraform / OpenTofu | `terraform validate` + **`plan`**; surprise-destroy on immutable attrs; silent defaults |
| Kubernetes / Helm | `kubeconform` + `kubectl diff`; missing limits, over-broad RBAC, wrong namespace |
| Dockerfile | `hadolint` + `docker build --check`; unpinned `FROM`, root user, leaked build secret |
| CI (GitHub Actions / GitLab) | `actionlint`/`yamllint` (no dry-run → lint is the floor); over-scoped token, unpinned action |
| App config (JSON/TOML/YAML) | schema check + app `--check`; wrong env default, inline secret |

## §SelfAudit

- **Validity is the gate the LLM fails silently.** Run the validator + plan (`config-harness.py`); do
  not certify "it validates / the plan is fine" from reading. An unrun gate is *no evidence*, not a
  pass; a tool absent is a SKIP, not a green light.
- **A green parse is evidence of nothing until the plan is read.** B3 is *plan-succeeds ∧
  intended-diff*. Read the diff against the desired state — a surprise destroy of a stateful resource,
  a silent dangerous default, or a non-idempotent churn is the *valid-but-wrong* quadrant regardless
  of a clean validate.
- **The dangerous defect is invisible to the validator — read the plan against intent.** "Valid
  config, wrong outcome" needs a skeptic reading the diff line-by-line against A1, not the validator's
  green check.
- **Safety smells are arithmetic, not taste — but the linter is a first pass, not a complete floor.**
  A plaintext secret, an unpinned image, a `0.0.0.0/0`, a wildcard grant, a missing limit — run
  `config-lint.py` first; a finding it *does* raise is gate-grade, not a preference. But a *clean* run
  is "none of the common shapes tripped," not "provably safe" — a text-level scan has a residual
  false-negative surface (a secret in a connection string, a base64 blob, an unusual key). On high
  stakes, still read, and wire the policy engine (`checkov`/`conftest`) as the harness `policy` phase.
- **Gates before reviews, always.** Don't grade drift for a config that won't parse, or fit for one
  whose desired state is wrong. Stop each axis at its first failed gate.
- **Two scores, never one.** *Right-intent-won't-validate* and *valid-but-wrong* need opposite fixes
  (fix the syntax/schema vs re-derive the desired state and read the plan). Report both axes and name
  the quadrant cell; never average.
- **Contract, not config.** This skill locks the desired-state contract, the plan verdict, and the
  grade — it does not write the config, grade application code (`code-decomposer`), run the system
  (`/verify`), or clean up quality (`/simplify`). Hand off; don't overlap.

## Verify Target

A config is **done** when: it produces the right desired state with an explicit contract (A1/A2);
cases/drift/fit ≥4; the harness parse + schema + **plan** gates ran **green**; the plan diff was read
against the desired state and is **exactly the intended change** — no surprise destroy, no silent
dangerous default, idempotent (a 2nd plan is a no-op); the safety floor is clean
(`config-lint.py`: no plaintext secret / `:latest` / `0.0.0.0/0` / wildcard grant / missing limit) and
grants are least-privilege; observability ≥4; and both axes score ≥4 with zero gate failures, landing
in the **SHIPPABLE** quadrant — with the config-spec card + plan verdict ready for a config author and
`/verify`. **NOT done** when: it validates but provisions the wrong thing, surprise-destroys a
stateful resource, flips an environment via a silent default, or isn't idempotent (*valid config,
wrong outcome*); or the desired state and contract are right but it won't parse/validate/plan
(*right intent, won't validate/plan*); or a gate was skipped (tool absent) and reported as a pass; or
one blended score is reported.

## References

| File | Load when |
|---|---|
| `references/decomposition-method.md` | **always, first** — the two-axis method (Intent × Validity), the leveled walk with gates, the quadrant, the plan-is-the-contract doctrine, and the SPECIFY / DECOMPOSE / GRADE workflows |
| `references/intent-axis.md` | **the Intent axis** — desired-state framing, the config contract (the dependency surface other configs read), case enumeration, drift, fit, and recovering intent from an existing config — where the **valid-but-wrong** defect lives |
| `references/validity-axis.md` | **the Validity axis** — the parse → schema → plan ladder, the **live-gate protocol** (the harness manifest + per-tool starter commands), and how to read each tool's signal; mechanized by `bin/config-harness.py` |
| `references/plan-and-drift.md` | **THE centerpiece — any "what will this actually do?" question** — the plan-is-the-contract principle, idempotency, the four failure shapes (surprise destroy, silent default, wrong scope, non-idempotent churn), reading a plan diff, and why a green parse proves nothing |
| `references/secrets-and-safety.md` | **the B4 safety review** — the mechanizable smell taxonomy (plaintext + URL-embedded + base64 + heredoc secrets, `:latest`/unpinned, `0.0.0.0/0`, wildcard grants, missing limits, k8s privilege grants, world-writable modes), the reference/placeholder guard, and least-privilege; mechanized by `bin/config-lint.py` |
| `references/policy.md` | **definition-of-done / handoff** — the 10-point DoD, the config-spec card `{desired_state, contract, plan_verdict, safety_findings[]}`, the harness adapter manifest, and the seams to `code-decomposer`, `/verify`, `arch-system`, `/simplify` |
| `bin/config-harness.py` | **mechanizes B1–B3** — reads a per-tool command manifest, runs each present gate (parse/schema/plan/lint/policy), normalizes verdicts to a report card (a missing tool is a SKIP, not a pass). `template` · `<manifest.json>` · `selftest` |
| `bin/config-lint.py` | **mechanizes the B4 floor** — a static smell detector across YAML/JSON/HCL/Dockerfile/TOML: plaintext + URL-embedded + base64 (k8s Secret `data:`) + heredoc/block-scalar secrets · `:latest`/unpinned · `0.0.0.0/0` · wildcard grants · missing k8s limits · k8s privilege grants (privileged/hostPath/runAsUser:0) · world-writable modes (0777/chmod 777); `<file\|dir>` · `selftest` |
