# Changelog — config-decomposer

Versioned independently of the `ops-skills` plugin; the gate (`bin/check-skills.py`) must pass for
any release.

## 0.2.1 — beta

Deepened the `bin/config-lint.py` safety floor from 5 smells to 7, with every new detection locked by
must-FLAG **and** must-NOT-flag selftest fixtures (all existing smells + their false-positive guards
intact). `references/secrets-and-safety.md` updated; the matching ROADMAP items marked done.

- **URL_EMBEDDED_SECRET (new).** A literal password in a connection-string / URL userinfo —
  `scheme://user:PASSWORD@host…` (postgres/mysql/redis/mongodb/amqp/https/…), including a
  `DATABASE_URL`/`*_URL`/`dsn` value carrying creds. Detects `://[^/\s:@]*:[^/\s@]+@` where the
  password segment is a literal. Guarded against `${VAR}` / `${{ … }}` / `{{ … }}` / `<PASSWORD>` /
  `***` / `REDACTED` and a no-password authority (`postgres://app@db`). Must-FLAG fixtures:
  `DATABASE_URL: "postgres://app:hunter2supersecret@db.internal:5432/app"`, `redis://:s3cr3tpass@cache:6379`.
- **PLAINTEXT_SECRET — expanded key set.** The secret-key detection now also catches `pwd`, `pat`,
  `bearer`, `dsn` (matched **only as a whole key**, so `path`/`pattern`/`compatibility`/`keyboard`/
  `gateway` don't false-positive), and `access_key_id` / `secret_key` / `private_key` / `client_secret`
  folded into the broad alternation — reusing the **same** literal-vs-reference guard, so a `${VAR}` /
  `secretKeyRef` value still isn't flagged. Must-FLAG: `client_secret: "abc123def456ghi"`, `pat: "ghp_…"`.
- **K8S_UNSAFE (new).** Pod-security privilege grants in a k8s-looking doc — `privileged: true`, a
  `hostPath:` volume, `runAsUser: 0`, `allowPrivilegeEscalation: true` — each reported as its own
  line-anchored sub-finding. Guarded: `runAsUser: 1000` and `allowPrivilegeEscalation: false` don't
  match, and a non-k8s doc that merely mentions "privileged" in prose/comment doesn't trip (the
  `is_k8s` gate + line anchoring).

## 0.2.0 — beta

Promoted to beta as part of the marketplace **v0.2.0** milestone (see the root CHANGELOG). This cycle the skill gained a checked-in, sibling-collision-tested routing-eval corpus, an adversarial-review hardening pass (fixes locked as selftest fixtures), and a worked `examples/walkthrough.md` (a red→green bin proof).

## 0.1.0 — draft

Initial release. Decompose / design / grade a configuration / infrastructure-as-code artifact on the
**INTENT × VALIDITY** crossing axes, scored separately with a gated rubric and the opposite-defect
quadrant.

- **The two-axis method** (`references/decomposition-method.md`): Intent (desired-state → contract →
  cases → drift & idempotency → fit) × Validity (parse → schema → plan → safety → observability),
  crossing at the config-measured-against-the-tool's-schema/state; gates before reviews; the
  *right-intent-won't-validate* vs *valid-but-wrong* quadrant; and the **plan-is-the-contract**
  doctrine (a missing tool is a SKIP, not a pass).
- **The VALIDITY harness** (`references/validity-axis.md` + `bin/config-harness.py`): a thin adapter
  modeled on code-decomposer's execution-harness — reads a per-tool command manifest, runs each
  present gate (parse/schema/plan/lint/policy), and normalizes verdicts to a report card; a missing
  tool is a SKIP flagged as `NO EVIDENCE`, never a pass. `selftest` proves the parse + normalize +
  run/skip logic with no external deps; `template` prints a starter manifest.
- **The plan-and-drift centerpiece** (`references/plan-and-drift.md`): the *plan-is-the-contract*
  principle, idempotency as a fixed point, the four failure shapes (surprise destroy, silent default,
  wrong scope, non-idempotent churn), the discipline of reading a plan diff against the desired state,
  and why a green parse proves nothing.
- **The safety linter** (`references/secrets-and-safety.md` + `bin/config-lint.py`): a static
  smell detector across YAML/JSON/HCL/Dockerfile/TOML (treated as text, one detector per format) —
  plaintext secrets, `:latest`/unpinned, `0.0.0.0/0`/`::/0`, wildcard `"*"` grants, missing k8s
  resource limits — with a reference/placeholder false-positive guard. `selftest` over good/bad
  fixtures.
- **The INTENT axis** (`references/intent-axis.md`): desired-state framing, the config contract (the
  dependency surface other configs read), case enumeration, drift & idempotency, fit, and recovering
  intent from an existing config — where the *valid-but-wrong* defect lives.
- **Policy** (`references/policy.md`): the 10-point definition-of-done, the config-spec card
  `{desired_state, contract, plan_verdict, safety_findings[]}`, the harness adapter manifest, and the
  handoff seams to `code-decomposer`, `/verify`, `arch-system`, and `/simplify`.

First skill in the new `ops-skills` plugin.

### Defect fixes (pre-release hardening)

- **config-lint — secret detection (B1):** the `PLAINTEXT_SECRET` check matched a secret-ish key only
  when it was flush against the indent and the value ran to end-of-line, so it missed the three most
  common shapes — a trailing-comma key in pretty-printed JSON (`"password": "…",`), an inline
  single-line JSON object (`{ "password": "…", "api_key": "…" }`), and a YAML list item
  (`- password: …`). Now the key matches **anywhere on the line** and the value capture stops at the
  field boundary (so multiple keys per line are each scored, and a trailing `,`/`]`/`}` is stripped).
  All three shapes added as must-FLAG fixtures; the reference/placeholder false-positive guards
  (`${VAR}`, `${{ secrets.X }}`, `var.`, `secretKeyRef`, `<CHANGEME>`, empty) verified intact.
- **config-lint — multi-line wildcard grant (B2):** added a multi-line scan that flags the canonical
  IAM shape `"Action": [` / `"*"` / `]` (key opens the array on one line, the bare `"*"` element on a
  later line) — the same-line regexes missed it. Must-FLAG fixture added; a scoped multi-line action
  list (real verbs, no bare `"*"`) verified as NOT flagged.
- **config-lint — `*.Dockerfile` scan (M3):** the directory walk now matches `*.dockerfile`
  (e.g. `api.Dockerfile`), not only `Dockerfile`/`Dockerfile.*`. `api.Dockerfile` added as a
  must-scan fixture.
- **config-harness — tri-state plan verdict (M1):** a successful `terraform plan -detailed-exitcode`
  (exit 2 = changes present) and `kubectl diff` (exit 1 = a diff) — the very flags the template and
  references recommend — were mislabeled as a gate FAIL. The `plan` verdict is now tri-state:
  exit 2 (terraform) / exit 1 (kubectl diff) is `changes-present` (a pass-with-a-diff-to-READ), and
  `fail` is reserved for a true error.
- **config-harness — INCOMPLETE on a skipped gate (M2):** the harness exited 0 (printing PASS) when a
  decisive GATE was SKIPPED (validator absent) despite a NO-EVIDENCE warning. A skipped gate with no
  fails is now `INCOMPLETE` and the harness **exits 3**, so automation can't read no-evidence as
  success.
- **Minors:** the k8s `NO_RESOURCE_LIMITS` check (whole-document substring; a sidecar's limits mask a
  peer's missing one) is now documented as a coarse document-level heuristic; `--cwd` with no value no
  longer raises `IndexError`; `secretKeyRef`/`configMapKeyRef`/`valueFrom` added to the secret-ref
  guard (honoring the doc claim); and the "deterministic FAIL / don't eyeball" language was softened —
  `config-lint` is a cheap **first pass**, not a complete floor (residual secret false-negatives —
  connection strings, base64, unusual key names — noted in ROADMAP).
