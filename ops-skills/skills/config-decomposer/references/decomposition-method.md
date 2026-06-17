# The two-axis method — INTENT × VALIDITY

A configuration / infrastructure-as-code artifact is **correct on two independent axes that walk the
same hierarchy in opposite directions** — the decomposer seam the layout-, mermaid-, component-, and
code-decomposers apply to space, diagrams, components, and code, here applied to a config (a CI
workflow, a Terraform module, a k8s manifest, a Dockerfile, an app config file).

- **Intent · whole → part** grades the **intent**: the desired state it should produce → its contract
  (the resources/keys other configs depend on) → the cases it handles → its drift/idempotency → its
  fit with the project. *"Is it the right config?"*
- **Validity · part → whole** grades the **mechanism**: it parses → its keys/types are schema-valid →
  it plans (validate/dry-run succeeds *and the diff is the intended one*) → it's safe → its plan is
  reviewable. *"Does it provably apply, here, to the right effect?"*

They **cross at the config measured against the tool's schema/state** — the same text is *both* the
claim (what infrastructure should exist) and the mechanism (what the tool's validator accepts and what
the plan diff will actually do). A config that won't validate is fiction; a config that validates but
produces the wrong plan is "valid but wrong" waiting to happen.

That crossing is the whole technique. A config can be:

- **right intent, won't validate/plan** — right desired state and contract, but a syntax error, an
  unknown key, a wrong type, or a `plan` that errors. The recoverable LLM failure: plausible config
  that the tool rejects.
- **valid config, wrong outcome / drifts** — parses, schema-validates, the field types are right —
  but it provisions the wrong thing, the plan diff is a *surprise destroy*, a silent default flips an
  environment, or re-applying it is not idempotent. The dangerous LLM trap: a green parse on the
  wrong infrastructure.

Opposite defects, opposite fixes — so you **score and report the two axes separately, never
averaged.** An averaged score hides which one you have, and they need opposite work (fix the syntax/
schema vs re-derive the desired state and read the plan).

## The leveled walk

| Axis | Direction | Levels (in order) | Asks |
|---|---|---|---|
| **A · Intent** | whole → part | **A1** Desired-state `[gate]` → **A2** Contract `[gate]` → **A3** Cases → **A4** Drift & idempotency → **A5** Fit | "Is it the *right config*?" |
| **B · Validity** | part → whole | **B1** Parses `[gate, code]` → **B2** Schema `[gate, code]` → **B3** Plan `[gate, code]` → **B4** Safety → **B5** Observability | "Does it *provably apply*, to the right effect?" |

`A1 · A2` and `B1 · B2 · B3` are **`[gate]`s** — a failure cascades and BLOCKS the reviews below it on
that axis. `A3–A5 · B4–B5` are **`[review]`s** (1–5). A shippable config is **≥4 on every review with
zero gate failures**, reported as two separate axis scores plus the quadrant cell. The VALIDITY gates
route to `bin/config-harness.py`; the B4 Safety floor routes to `bin/config-lint.py`.

### A · Intent (whole → part)

- **A1 Desired-state `[gate]`** — what should this config *declare or produce*, in one sentence?
  ("an autoscaling group of 3 web nodes behind an ALB in us-east-1.") Provisioning the wrong thing
  makes everything below moot. See `intent-axis.md`.
- **A2 Contract `[gate]`** — the resources/keys it creates and their meaning: the names, outputs, and
  shapes *other configs depend on* (a security-group id, an output variable, a service name, an env
  var another container reads). Wrong contract poisons every downstream config.
- **A3 Cases `[review]`** — environments (dev/stage/prod), defaults vs overrides, required vs
  optional keys, the secret-handling path. Configs hide their failures in the un-set default.
- **A4 Drift & idempotency `[review]`** — re-applying produces no change; the plan diff is *exactly*
  the intended change and nothing extra; no manual drift is silently reverted or clobbered. The
  centerpiece — see `plan-and-drift.md`.
- **A5 Fit `[review]`** — matches the project's modules, conventions, naming, and the existing
  state; doesn't duplicate a module or hard-code what a variable should carry.

### B · Validity (part → whole)

- **B1 Parses `[gate, code]`** — well-formed YAML/HCL/JSON/TOML; no tabs-in-YAML, no unterminated
  block. The cheapest gate. Routed to `bin/config-harness.py` (`parse`).
- **B2 Schema `[gate, code]`** — valid keys and types per the tool's schema; required keys present;
  no unknown attributes. `terraform validate` / `kubeconform` / a JSON-schema check. Routed to the
  harness (`schema`).
- **B3 Plan `[gate, code]`** — `validate`/dry-run/`plan` succeeds **AND the diff is the intended
  change** — not a surprise destroy, not an empty no-op when you expected a change. The decisive gate.
  Routed to the harness (`plan`). A green parse is *not* evidence here — see the doctrine.
- **B4 Safety `[review]`** — no plaintext secret, least-privilege grants, pinned versions, no
  `0.0.0.0/0`, resource limits present. The mechanizable floor routes to `bin/config-lint.py`; see
  `secrets-and-safety.md`.
- **B5 Observability `[review]`** — the plan is reviewable; the change is scoped and reversible; the
  state is inspectable. Can you tell what changed and roll it back?

## The opposite-defect quadrant

```
                 B · VALIDITY passes        B · VALIDITY fails
A · INTENT   ┌────────────────────────┬────────────────────────┐
  passes     │      SHIPPABLE         │  right intent, won't    │
             │                        │  validate/plan — right  │
             │                        │  desired state, but a   │
             │                        │  syntax/type error or   │
             │                        │  a plan that errors     │
             ├────────────────────────┼────────────────────────┤
A · INTENT   │ valid config, wrong    │       REBUILD           │
  fails      │ outcome / drifts —     │                         │
             │ parses & validates but │                         │
             │ provisions the wrong   │                         │
             │ thing, surprise-       │                         │
             │ destroys, or isn't     │                         │
             │ idempotent             │                         │
             └────────────────────────┴────────────────────────┘
```

The quadrant **names the fix**: top-right needs syntax/schema/plan work the tool reports plainly;
bottom-left needs *intent* work the validator **cannot see** — re-derive the desired state and read
the plan diff against it.

## The doctrine — the PLAN is the contract

This is why the skill earns its place (and why it's outsized for an LLM author):

- **A config's real behavior is its diff against current state, not its text.** The same HCL produces
  a create on an empty state and a *destroy-and-replace* on a populated one. You cannot grade B3 by
  reading — route VALIDITY to the tool's own `validate`/`plan` via `bin/config-harness.py` and
  **trust the plan, not the read-through**.
- **A missing tool is a SKIP, not a pass.** If `terraform`/`kubeconform`/the validator isn't on PATH,
  that gate produced *no evidence*. A SHIPPABLE verdict requires the gates to have actually **run** —
  a green parse with an unreviewed (or unrun) plan is no evidence of the right outcome.
- **The dangerous defect ("valid config, wrong outcome / drifts") is partly on the INTENT side and
  hidden inside B3 ("is the diff the *intended* one?").** Route it two ways: **read the plan diff
  against the stated desired state** (a create where you expected a no-op, a destroy where you
  expected an update — every line is a claim to verify), and **the safety lint** for the mechanizable
  smells (`bin/config-lint.py`: plaintext secrets, `:latest`, `0.0.0.0/0`, wildcard grants).
- **Safety smells are mechanizable — gate them.** A plaintext secret, an unpinned image, a wide-open
  CIDR, or a wildcard IAM grant is a deterministic FAIL, not a matter of taste. The lint is the cheap
  always-available floor; a policy engine (`checkov`/`conftest`, the harness `policy` phase) is the
  deeper pass.

## Modes

- **SPECIFY** (before writing) — walk Intent-down (desired-state → contract → cases), declare the
  validity plan (which validate/plan command will prove it, which safety floor applies), emit a
  **config-spec card**.
- **DECOMPOSE** (existing config) — recover the desired state (A1/A2), run the validity ladder (B1–B3
  via `config-harness.py`) + the safety lint (`config-lint.py`), read the plan diff against the
  desired state, score the reviews; emit the config-spec card + a gap list (e.g. *"validates, but the
  plan destroys the database — surprise destroy"*).
- **GRADE** — score both axes, gates first (run the harness + the lint, read the plan), place in the
  quadrant, name one corrective per failure.

## Walk order (do not skip)

1. **A1 Desired-state / A2 Contract** — name what it should produce and the surface others depend on.
   Wrong ⇒ stop, re-spec.
2. **B1/B2/B3 Validity** — run `config-harness.py`. Red gate ⇒ fix before reviewing (you can't grade
   drift for a config that won't validate). A skipped gate (tool absent) ⇒ *no evidence*, not a pass.
3. **B3 plan-read** — read the diff against the desired state (`plan-and-drift.md`). A surprise
   destroy / silent default / non-idempotent re-apply ⇒ the config is *valid but wrong*; the
   corrective is the config, not the score.
4. **B4 safety lint** — run `config-lint.py`; a plaintext secret / `:latest` / `0.0.0.0/0` / wildcard
   grant is a gate-grade finding.
5. **Reviews** — A3–A5 then B4(judgment)–B5, 1–5 each. Below 4 ⇒ name the single corrective.
6. **Report** — two axis scores, the quadrant cell, gate failures first; hand the verified
   config-spec card + the plan verdict to a config author and to `/verify`.
