# Roadmap — config-decomposer

Ships its core in 0.1.0 (the two axes, the validity harness, the safety linter, the config-spec +
plan-verdict cards, the plan-and-drift centerpiece). Everything below is additive.

## `bin/config-lint.py`

- [ ] **Structured-aware passes** — parse YAML/JSON/HCL into a tree (where a stdlib or vendored parser
      allows) so the secret/grant checks are position-accurate, not regex-approximate, cutting the
      residual false-positive surface on multi-line and heredoc values.
- [ ] **Residual secret false-negatives (partially closed).** The text-level scan now catches the
      common secret shapes (inline single-line JSON, trailing-comma keys, YAML list items), the
      multi-line wildcard-array grant, **URL-embedded credentials**, and an **expanded key set** — but
      a regex floor will always miss some shapes. Status of the known gaps:
      - [x] **Connection-string / URL-embedded secrets** — `postgres://user:realpassword@host/db`,
        `redis://:realpassword@host`, a `DATABASE_URL`/`*_URL`/`dsn` with creds in the authority. Done
        in 0.2.1 as **URL_EMBEDDED_SECRET** (literal password in `scheme://user:PASS@host` userinfo;
        `${VAR}`/`${{…}}`/`<PASSWORD>`/`***`/`REDACTED`/no-password guarded).
      - [x] **Unusual key names** — `pwd`, `pat`, `bearer`, `dsn` (whole-key), plus `access_key_id`,
        `secret_key`, `private_key`, `client_secret` folded into the broad alternation. Done in 0.2.1.
      - [ ] **Base64 / encoded blobs** (a k8s `Secret` `data:` field, an inlined PEM/cert) — high
        entropy, not a literal string the `LOOKSREAL` test models.
      - [ ] **Heredoc / block-scalar** multi-line literal values.
      Until those close, `config-lint` is documented as a cheap **first pass**, not a complete floor
      (see `secrets-and-safety.md`); the deeper pass is a policy engine wired as the harness `policy`
      phase.
- [ ] **More smells**: world-writable file modes, `latest`-equivalent floating refs (a branch
      `?ref=main`, a `@v4` action tag), disabled TLS verification, default/empty admin passwords.
      - [x] **k8s pod-security** — `privileged: true` / `hostPath` / `runAsUser: 0` /
        `allowPrivilegeEscalation: true`. Done in 0.2.1 as **K8S_UNSAFE** (line-anchored, gated on a
        k8s-looking doc; `runAsUser: 1000` / `allowPrivilegeEscalation: false` / non-k8s prose guarded).
- [ ] **Allowlist / baseline file** — a committed `.config-lint-ignore` for reviewed exceptions, so a
      known-intended `0.0.0.0/0` (a public ALB) doesn't re-fire every run.
- [ ] Emit a machine-readable report (JSON) so GRADE can fold safety findings into the report card's
      `safety_findings[]`.

## `bin/config-harness.py`

- [ ] **Plan-diff parsing** — read the `terraform plan -json` / `kubectl diff` output and surface the
      create/update/**destroy**/replace counts directly, flagging a destroy/replace on a stateful
      resource as a candidate *surprise destroy* — turning the manual diff-read into a gated signal.
- [ ] **Idempotency check** — a `plan; apply; plan` loop (where safe) that gates on the second plan
      being empty, mechanizing the A4 idempotency review.
- [ ] Per-phase **timeout** + output capture to the report card; a `--json` report mode.
- [ ] A small **manifest registry** of starter manifests per ecosystem (terraform, kubernetes/helm,
      docker, github-actions, ansible) the skill can drop in.

## Method & corpus

- [ ] A **routing-eval corpus** (the maturity step the repo ROADMAP tracks) — especially the
      boundaries with `code-decomposer` (application code vs config), `/verify` (live behavior vs
      plan), `arch-system` (topology vs config), and `/simplify` (quality), which are the likely
      mis-routes.
- [ ] A worked **end-to-end transcript** (a Terraform module SPECIFY → author → DECOMPOSE → GRADE with
      a planted surprise-destroy), with the config-spec card, the validity report, and the fix checked
      in and dogfooded.
- [ ] A **format-family deepening** for the highest-risk targets (k8s RBAC + securityContext;
      Terraform state/import + immutable-attribute recreates) if the single `validity-axis.md` manifest
      table proves too thin.

## Plugin

- [ ] As `ops-skills` grows, candidate siblings from the same INTENT/VALIDITY lineage: a
      `pipeline-decomposer` (CI/CD: intent × run) and a `policy-decomposer` (OPA/Rego/admission:
      rule-intent × evaluation), both with deterministic example-set gates.
