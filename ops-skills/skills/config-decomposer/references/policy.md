# Policy — definition-of-done, the card, and the handoff

The reusable artifacts and boundaries: what "done" means, the shape of the config-spec card the skill
emits, the harness manifest, and how this hands off to the rest of the fleet without overlapping it.

## Definition-of-done (a config is shippable when…)

Gated items route to `bin/`; review items are 1–5 judgments. SHIPPABLE = the quadrant top-left.

1. **Right desired state (A1)** — produces the actual intended infrastructure, stated in one sentence.
2. **Sound contract (A2)** — the resources/keys and the dependency surface other configs read are
   explicit; required vs optional and the secret source are declared.
3. **Cases covered (A3)** — environments, defaults vs overrides, and the secret-handling path are
   enumerated; no dangerous silent default (≥4).
4. **Idempotent, intended diff (A4)** — re-apply is a no-op; the plan diff is exactly the intended
   change with no surprise destroy and nothing extra (≥4).
5. **Fits the project (A5)** — matches the modules, conventions, naming, and state layout; no
   duplication (≥4).
6. **Parses & schema-valid (B1/B2)** — `config-harness.py` parse + schema gates ran green; no unknown
   keys, no type errors, required keys present.
7. **Plan-clean ∧ intended (B3)** — the plan/dry-run gate ran green **and** the diff was read against
   A1 — no surprise destroy, no out-of-scope change, idempotent.
8. **Safe (B4)** — `config-lint.py` is clean (no plaintext secret / `:latest` / `0.0.0.0/0` / wildcard
   grant / missing limit) and grants are least-privilege, deps pinned (≥4).
9. **Observable (B5)** — the plan is reviewable; the change is scoped and reversible; state is
   inspectable (≥4).
10. **Both axes ≥4, zero gate fails, SHIPPABLE quadrant** — reported as two scores, gate failures
    first, with the config-spec card + plan verdict ready for handoff.

## The config-spec card

`*.config-spec.json` — emitted by SPECIFY, re-derived by DECOMPOSE:

```json
{
  "artifact": "web-asg.tf",
  "tool": ["terraform"],
  "desired_state": "3-node autoscaling group of web nodes behind an internet-facing ALB in us-east-1",
  "contract": {
    "creates":  ["aws_autoscaling_group.web", "aws_lb.web"],
    "outputs":  ["alb_dns_name", "web_sg_id"],
    "consumes": ["var.vpc_id", "data.aws_ami.web"],
    "required": ["vpc_id", "subnet_ids"],
    "secrets":  ["from aws_secretsmanager (never inline)"]
  },
  "cases": ["dev: 1 node, stage: 2, prod: 3", "ami unset -> defaults to latest -> PIN it",
            "subnet override per env"],
  "plan_verdict": "create 4, update 0, destroy 0 — matches desired state; idempotent (2nd plan empty)",
  "safety_findings": []
}
```

`plan_verdict` is the line that distinguishes a SHIPPABLE config from a *valid-but-wrong* one — it
records what the **plan** did, not what the text says. `safety_findings[]` carries the
`config-lint.py` output (empty = floor clean).

## The harness adapter manifest

The per-tool command map `config-harness.py` reads (`template` prints a starter). `gate` defaults:
parse/schema/plan gate; lint/policy advisory. Commit one manifest per config root; keep it in sync
with CI so the skill runs the **same** gates CI does (the same `terraform validate`/`plan`,
`kubeconform`, `hadolint`). Per-tool starter commands are tabulated in `validity-axis.md`.

A missing tool is a **SKIP, not a pass** — the harness flags a skipped gate as `NO EVIDENCE`, reports
the run as `INCOMPLETE`, and **exits non-zero (3)** so automation can't read a no-evidence run as
green. A SHIPPABLE verdict requires the gates to have actually **run**; a green parse with an unrun
plan is no evidence of the right outcome. Note the plan verdict is **tri-state**: a
`terraform plan -detailed-exitcode` exit 2 (or a `kubectl diff` exit 1) is `changes-present` — a
**pass with a diff to READ**, the intended outcome — not a fail; the `plan_verdict` line records what
that diff was (and that the 2nd plan was empty).

## Handoff — what this skill does NOT do

The fleet has clear seams; `config-decomposer` is the **authoring-time design + grade** stage for
config/IaC and feeds the others:

- **owns** — **config / IaC intent + validity grading**: the desired-state contract, the
  validate/plan ladder, the safety floor, the plan-is-the-contract read. The config-spec card + plan
  verdict are its deliverables.
- **→ a config author** (or plain editing): receives the locked config-spec card and writes/edits the
  HCL/YAML. This skill grades and locks the contract; it does not emit the final config.
- **→ `code-decomposer`**: for **application code** — a function, a module, a test. When the artifact
  is logic (a Lambda handler, a controller's reconcile loop), that's code-decomposer's SPEC ×
  EXECUTION, not this skill's INTENT × VALIDITY. A repo with both: grade the *config* here, the *code*
  there.
- **→ `/verify`**: runs the actual app/system to confirm **live behavior** end-to-end.
  `config-decomposer` proves the *config* validates and its *plan* is the intended change; `/verify`
  proves the running system behaves. Different altitude — a plan is a prediction, `/verify` is the
  observation.
- **← `arch-system` / `arch-pattern`**: hand *in* the infrastructure boundary/topology. This skill
  grades a config against its desired state; it does not design the system architecture.
- **not `/simplify`**: that's reuse/efficiency cleanup (quality). This skill is correctness
  (right + applies). A config can be SHIPPABLE here and still have a module to factor out for
  `/simplify`.

## Governance

- **Config-spec cards are checked in** next to the config as the contract of record; they version with
  the config and are the diff a reviewer reads first.
- **The manifest tracks CI** — if CI adds a gate (a new validator, a policy engine), add it to the
  manifest so the skill's verdict and CI's verdict can't diverge.
- **Plan in review, not blindly in CI** — a `plan` against prod state can require credentials and is
  read by a human; the safety lint is the cheap everywhere-gate, the read plan is the targeted proof.
