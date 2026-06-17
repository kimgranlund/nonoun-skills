# The VALIDITY axis — does it provably apply, to the right effect?

The Validity axis (B1–B5) grades *mechanism*, bottom-up: from "does this even parse" to "is the plan
reviewable and reversible." It is the **mechanizable** axis — route it to the tool's own
validate/plan via `bin/config-harness.py` and **trust the plan, not the read-through**. An LLM cannot
reliably tell by reading whether HCL validates, whether a k8s manifest matches the API schema, or —
the decisive one — what a `plan` will actually *do* to current state. Running it is the only evidence.

## The ladder

| Level | Gate | The tool that proves it | The signal |
|---|---|---|---|
| **B1 Parses** | `[gate]` | the parser / linter (`yamllint`, `terraform fmt`, `hcl`, `jq`) | well-formed YAML/HCL/JSON/TOML — no tabs, no unterminated block |
| **B2 Schema** | `[gate]` | `terraform validate` · `kubeconform` · a JSON-schema check | valid keys & types per the tool's schema; required keys present; no unknown attrs |
| **B3 Plan** | `[gate]` | `terraform plan` · `kubectl diff --dry-run` · app `--check` | dry-run succeeds **and the diff is the intended change** (see `plan-and-drift.md`) |
| **B4 Safety** | review | `config-lint.py` + `checkov`/`conftest` | no plaintext secret, least-privilege, pinned versions, no wide-open net |
| **B5 Observability** | review | the plan output + the state backend | the diff is reviewable, scoped, reversible; the state is inspectable |

The gates cascade: don't grade safety (B4) for a config that won't parse (B1). A red gate stops the
axis — fix it before reviewing. **And a green B1/B2 is not a pass for B3** — syntax and schema say
nothing about what the plan will do (see the doctrine in `decomposition-method.md`).

## The live-gate protocol (the harness manifest)

`bin/config-harness.py` is a thin adapter, not a bundled validator. You declare the project's
commands once; it runs each phase whose tool is on PATH and normalizes the verdicts. A missing tool is
a **SKIP** (evidence incomplete), never a pass — like code-decomposer's execution harness, the static
logic is self-tested with no deps, the live run fires where the tools exist.

```json
{
  "tool": "terraform",
  "gates": {
    "parse":  { "cmd": "terraform fmt -check" },
    "schema": { "cmd": "terraform validate" },
    "plan":   { "cmd": "terraform plan -detailed-exitcode" },
    "lint":   { "cmd": "tflint", "gate": false },
    "policy": { "cmd": "checkov -d .", "gate": false }
  }
}
```

`gate` defaults: parse / schema / plan gate; lint / policy are advisory. Run it:

```sh
python3 bin/config-harness.py template          # print a starter manifest
python3 bin/config-harness.py manifest.json     # run present gates; report card; nonzero on gate fail
```

Read the card honestly: a **skipped** gate means you have *no evidence* for that level, not a pass. A
SHIPPABLE verdict requires the gates to have actually **run**, not merely "not failed." The harness
makes both halves of that explicit in its verdicts and exit code:

- A skipped **gate** with no fails is `INCOMPLETE`, and the harness **exits non-zero (3)** — so a
  no-evidence run can never be read by automation as a green PASS.
- The `plan` verdict is **tri-state**, because the recommended flag makes the success case non-zero:
  `terraform plan -detailed-exitcode` exits **2** when changes are present, and `kubectl diff` exits
  **1** when a diff exists. The harness scores those as `changes-present` — a **pass with a diff to
  READ** (the doctrine's intended outcome), **not** a gate fail. A fail is reserved for a true error
  (terraform exit 1 or >2; kubectl diff exit >1). So a `changes-present` plan is your cue to read the
  diff against the desired state, not a red gate.

### Starter manifests by tool

| Tool / format | parse | schema | plan |
|---|---|---|---|
| **Terraform** | `terraform fmt -check` | `terraform validate` | `terraform plan -detailed-exitcode` |
| **Kubernetes** | `yamllint .` | `kubeconform -strict manifests/` | `kubectl diff -f manifests/` |
| **Helm** | `helm lint .` | `helm template . \| kubeconform -strict` | `helm diff upgrade rel . ` |
| **Dockerfile** | `hadolint Dockerfile` | `hadolint Dockerfile` | `docker build --check .` |
| **GitHub Actions** | `yamllint .github` | `actionlint` | — (no dry-run; lint is the floor) |
| **Ansible** | `ansible-lint` | `ansible-playbook --syntax-check` | `ansible-playbook --check --diff` |
| **App config (JSON/TOML)** | `jq . config.json` | schema check (`ajv`, app `--validate`) | app `--check` / `--dry-run` |

`plan` is the decisive gate. Where a format has no dry-run (GitHub Actions, many app configs), say so
explicitly — B3 then rests on the lint floor + the adversarial intent read, and you report B3 as
**partial evidence**, not a clean pass.

## Reading each tool's signal

- **Parse / fmt** — the cheapest, highest-value gate: catches the YAML tab, the unbalanced HCL brace,
  the trailing comma in strict JSON. Run it first, always.
- **Schema validator** — confirms keys and types match the tool's contract (B2). An "unknown
  attribute" or "missing required key" is often the contract mismatch the read-through missed. Treat a
  *skipped* validator (no schema available) as un-checked surface, not a pass.
- **Plan / dry-run** — the decisive gate. Green-that-it-ran is necessary, not sufficient: the
  question is whether the **diff is the intended change**. Pair every plan with a *diff read against
  the desired state* — a green plan that destroys the database is the *valid-but-wrong* quadrant.
- **Lint / policy** — advisory by default, but a finding in a real-bug category (an open CIDR, a
  missing limit) is signal, not noise. The `config-lint.py` safety floor is always available; a
  policy engine (`checkov`/`conftest`) is the deeper pass.

## B4 Safety & B5 Observability (reviews)

- **B4** — beyond "validates": no plaintext secret, least-privilege grants, pinned versions/digests,
  no `0.0.0.0/0`, resource limits present. The mechanizable subset routes to `bin/config-lint.py`
  (gate-grade findings); the judgment subset (is this grant *minimal*?) stays a review. Full taxonomy
  in `secrets-and-safety.md`.
- **B5** — when it's applied, can you tell what changed and undo it? Is the plan diff small and
  reviewable (not a 400-line churn from a formatting change), is the change **scoped** (this module,
  not the whole account), is it **reversible** (a destroy of stateful data is not), and is the state
  **inspectable** after?

The output of this axis is the **VALIDITY report card** — which gates ran, their verdicts, the plan
verdict (intended-diff or surprise), and the safety findings — handed alongside the config-spec card
to a config author and to `/verify`.
