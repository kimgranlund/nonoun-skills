# The INTENT axis — is it the right config?

The Intent axis (A1–A5) grades *intent*, top-down: from the desired state the config must produce to
the detail of how it fits the project. This is the axis the validator **cannot see** — `terraform
validate` is silent on "this provisions the wrong region," and `kubeconform` is silent on "this
exposes the admin service publicly." It is also the axis LLMs fail silently on (a config that
validates perfectly and provisions exactly the wrong thing), so the dangerous *valid-but-wrong*
defect lives here — read against the plan, not just the schema.

## A1 · Desired-state `[gate]`

Name what the config should *declare or produce*, in one sentence, in infrastructure terms, before
reading the keys. Then ask: does this config produce *that*, or an adjacent thing it's easy to drift
to?

- State the **observable end state**, not the syntax: "three web nodes in an autoscaling group behind
  an internet-facing ALB, in `us-east-1`, with the DB in a private subnet" — not "an
  `aws_autoscaling_group` block."
- Distinguish the **asked** desired state from the **assumed** one. An LLM happily emits a *plausible
  neighbour* — `t3.micro` when the workload needs `m5.large`, `replicas: 1` for a service that must
  be HA, the default VPC when an isolated one was required.
- **Gate:** if the config provisions the wrong thing, stop — every level below is polishing the wrong
  infrastructure. Re-spec the desired state, don't refine the keys.

## A2 · Contract `[gate]`

The contract is the crossing seam with VALIDITY — the resources and keys this config creates, and the
**surface other configs depend on**. Make it explicit:

- **Resources / keys** — what it creates or sets: the named resources, the outputs, the service
  names, the env vars, the ports.
- **The dependency surface** — the outputs and identifiers *other configs read*: a `security_group_id`
  output, a Terraform `remote_state` value, a k8s `Service` name another Deployment targets, an env
  var a sibling container expects. This is the API of the config; breaking it breaks consumers.
- **Required vs optional** — which keys/variables are mandatory, which have defaults, and what those
  defaults *resolve to in each environment*.
- **The secret-handling contract** — *where* secrets come from (a secret manager, a `valueFrom`, a
  CI secret), declared, not inlined.
- **Gate:** a wrong or missing contract poisons cases, the plan, and review. Lock it first; it's the
  artifact you hand to a config author and the thing a consumer config binds against.

## A3 · Cases `[review]`

Enumerate the real configuration space — LLMs over-index on the single happy environment:

- **Environments** — dev / stage / prod: the same config across them; what each override actually
  resolves to. A value correct in dev (`replicas: 1`, a permissive CORS) is a defect in prod.
- **Defaults & overrides** — every key left unset takes a default; is that default correct *here*?
  The silent default is where the wrong outcome hides (see `plan-and-drift.md`).
- **Required vs optional** — is a required variable actually enforced (a `validation` block, a schema
  `required`), or does it silently default to something dangerous?
- **Secret handling** — is every secret sourced from a manager/ref, never a literal, in *every*
  environment's path?

Score by coverage of the space, not count of keys.

## A4 · Drift & idempotency `[review]`

The centerpiece review — the property a config text cannot show you, only the plan can (full
treatment in `plan-and-drift.md`):

- **Idempotency** — applying the config a second time produces **no change**. A config whose re-apply
  is not a no-op (a timestamp, a random default, a list that reorders) churns the infrastructure.
- **The diff is exactly the intended change** — the plan creates/updates/destroys *precisely* what
  A1 asked for, **and nothing extra**. An unexpected line in the diff is an unintended change.
- **No surprise destroy** — a change to an immutable attribute (a name, an AZ, an engine version)
  silently becomes a *destroy-and-replace*; on a stateful resource (a database, a volume) that is
  data loss. The plan reveals it; the text hides it.
- **No clobbered drift** — the config doesn't silently revert a deliberate manual change, or fight a
  controller that owns the same field.

## A5 · Fit `[review]`

Coherence with the surrounding project — the difference between *valid* and *belongs*:

- Matches the project's **module structure**, naming, tagging, and conventions; uses the shared
  module/base instead of re-declaring a resource inline.
- Doesn't **duplicate** an existing resource or hard-code what an existing variable/secret already
  carries.
- Lands in the **right place** in the state/repo layout; its variable/output surface is no larger
  than consumers need.

## Recovering intent from an existing config (DECOMPOSE)

When grading a config you didn't write, A1/A2 are *recovered*, not given:

1. Read the resource/key names and the outputs → draft the one-sentence desired state.
2. Trace the outputs and shared keys → that's the contract surface (what would break if you renamed
   it?).
3. **Then run the plan** (`config-harness.py`) and read the diff *against* your drafted desired state.
   A mismatch — a resource you didn't expect, a destroy you didn't intend — is the *valid-but-wrong*
   defect surfacing. The plan is the arbiter, not your read of the text.

The output of this axis is the **config-spec card** — the recovered/declared desired state + the
contract surface + the case list — the artifact GRADE re-derives and SPECIFY emits, and the thing you
hand to a config author and read the plan diff against.
