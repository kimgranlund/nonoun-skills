# Secrets & safety — the mechanizable smells (B4)

The B4 Safety review has a hard floor whose findings are **gate-grade, not a matter of taste**: a
plaintext secret (a secret-ish key, a credential in a connection-string URL, a committed k8s `Secret`
base64 `data:` value, or a secret assigned a multi-line block-scalar/heredoc literal), an unpinned
`:latest` image, a `0.0.0.0/0` ingress, a wildcard `"*"` IAM grant, a k8s container with no resource
cap, a k8s privilege grant (`privileged: true` / `hostPath` / `runAsUser: 0` /
`allowPrivilegeEscalation: true`), a world-writable file mode (`0777`/`0666`/`chmod 777`/`o+w`).
`bin/config-lint.py` is the always-available static pass that catches them. It is a **cheap,
high-signal FIRST pass — not a complete floor**: a text-level regex over five formats will have a
residual false-negative surface (an entropy-only secret with no secret-ish key, an indentation the
heuristic doesn't model). So treat a clean run as *"none of the common shapes tripped,"* not *"provably
secret-free"* — when the stakes are high, still read the diff, and wire the deeper policy engine
(`checkov`/`conftest`) as the harness `policy` phase. The judgment part of B4 (is this grant *minimal*?
is this exposure *intended*? is this privilege *justified*?) stays a review; the smells below are what
the linter mechanizes.

## The smell taxonomy (what `config-lint.py` flags)

Static, cheap, deterministic — one text-level regex pass spanning YAML / JSON / HCL / Dockerfile /
TOML (configs treated as text so one detector covers every format):

| Kind | Smell | Why it's a defect |
|---|---|---|
| **PLAINTEXT_SECRET** | a secret-ish key (`password`/`passwd`/`pwd`/`secret`/`token`/`api_key`/`access_key(_id)`/`secret_key`/`private_key`/`client_secret`/`pat`/`bearer`/`dsn`/…) set to a *literal* string | the secret is now in source control, logs, and state — it must come from a manager/ref, never a literal |
| **URL_EMBEDDED_SECRET** | a *literal* password in a connection-string / URL userinfo — `scheme://user:PASSWORD@host…` (postgres/mysql/redis/mongodb/amqp/https/…), incl. a `DATABASE_URL`/`*_URL`/`dsn` carrying creds | the secret hides in the *value's* userinfo, not behind a secret key — same exposure, harder to spot; inject it from a secret store |
| **BASE64_SECRET** | a committed k8s `Secret` (`kind: Secret`) whose `data:` block carries a *literal* base64 value (`password: cGFzc3dvcmQ=`) — k8s `data:` is base64 by spec, not encryption | committing the manifest commits the secret material — inject it via a secret store / sealed-secrets / external-secrets, don't check the rendered `Secret` into source control |
| **HEREDOC_SECRET** | a secret-ish key assigned a *multi-line literal* — a YAML block scalar (`private_key: |` / `token: >`) or a shell heredoc (`KEY=$(cat <<EOF`) | a multi-line secret is still a committed plaintext secret — the block-scalar / heredoc shape just spreads it across lines so a single-line regex (and a careless reviewer) misses it |
| **UNPINNED_VERSION** | `:latest`, or a Dockerfile `FROM` / image with no tag or digest | the deploy is **not reproducible** — "latest" drifts under you; the build is unrepeatable |
| **OPEN_NETWORK** | `0.0.0.0/0` or `::/0` in an ingress/egress/CIDR position | exposed to the **entire internet** — the default-deny posture is broken |
| **WILDCARD_GRANT** | `"*"` in an `Action` / `Resource` / `Principal` / `permissions` position | over-broad permission — violates least-privilege; one compromised credential is total |
| **NO_RESOURCE_LIMITS** | a k8s pod whose spec declares `containers:` but has **no `resources:` block anywhere in the document** (coarse, document-level) | no cap on CPU/memory — a noisy neighbour can starve the node |
| **K8S_UNSAFE** | in a k8s-looking doc: `privileged: true`, a `hostPath:` volume, `runAsUser: 0` (root), or `allowPrivilegeEscalation: true` | each is a pod-security privilege grant — a container break-out / host-takeover risk that needs an explicit justification, not a default |
| **WORLD_WRITABLE** | a world-writable file mode — an octal `mode:` of `0777`/`0666`/`777`/`666` (incl. `0o` prefix), or a `chmod 777`/`666`/`o+w`/`a+w`/`+w` | anyone on the host can modify the file — config tampering / privilege escalation; tighten to `0644`/`0600`/`0755` |

Run it: `python3 bin/config-lint.py <file|dir>` — nonzero exit on any finding. It is deliberately a
*smell detector*, not a policy engine: it is the floor that needs **no tool install**. The deeper pass
is a policy engine (`checkov`, `conftest`/OPA, `tfsec`, `kube-score`) wired as the harness `policy`
phase.

### The reference / placeholder guard (why it isn't noisy)

The plaintext-secret check fires only on a **literal** value. It explicitly does *not* flag a value
that is a reference or a placeholder — `${DB_PASSWORD}`, `$(cmd)`, `{{ .Values.token }}`,
`!Ref DbSecret`, `var.secret`, the k8s `valueFrom: { secretKeyRef: … }` / `configMapKeyRef` shapes,
`<CHANGEME>`, `changeme`, `""`. Those are the *correct* shape (the secret is sourced elsewhere), so
flagging them would be the false positive that trains people to ignore the linter. The smell is
specifically *a real secret pasted in as a literal*. The check also matches a secret key **anywhere
on the line** — an inline single-line JSON object, a trailing-comma key in pretty-printed JSON, a YAML
list item (`- password: …`) — not only one flush against the indent. The wildcard-grant check spans
the **multi-line** array shape too (`"Action": [` … `"*"` … `]`).

The key set is broad — `password`/`passwd`/`secret`/`token`/`api_key`/`access_key(_id)`/`secret_key`/
`private_key`/`client_secret`/`auth`/`credential` match as a *substring* of a longer key (`db_password`,
`oauth_client_secret`), while the short / ambiguous names `pwd`/`pat`/`bearer`/`dsn` match **only as a
whole key** — so `pat` does *not* fire on `path`/`pattern`/`compatibility`, nor `keyboard`/`gateway` on
anything. **URL_EMBEDDED_SECRET** reuses the same literal-vs-reference guard on the password segment of
a `scheme://user:PASSWORD@host` authority: a `://[^/\s:@]*:[^/\s@]+@` shape whose password is a literal
is flagged; one that is `${VAR}` / `${{ … }}` / `{{ … }}` / `<PASSWORD>` / `***` / `REDACTED`, or a URL
with no password at all (`postgres://app@db`), is not. **K8S_UNSAFE** is line-anchored and gated on a
k8s-looking doc, so `allowPrivilegeEscalation: false`, `runAsUser: 1000`, and the bare word
"privileged" in a non-k8s comment/prose do **not** trip it.

**BASE64_SECRET** is scoped **strictly** to a `kind: Secret` doc's `data:` block. A value is flagged
only when it's a literal base64 token (`^[A-Za-z0-9+/]{8,}={0,2}$`), so a `${SECRET}` / `<PLACEHOLDER>`
value is not. `stringData:` (which holds *plaintext*, by k8s convention) is **excluded** — that case is
PLAINTEXT_SECRET's job, so a `stringData:` literal is reported once as PLAINTEXT_SECRET, never
double-flagged as BASE64. And the check never fires outside a `kind: Secret` doc, so a base64-looking
string that is *not* secret material — a ConfigMap `data:` value, an `image: …@sha256:…` digest, a
checksum — does not trip it. Where BASE64_SECRET fires on a line, it **supersedes** a same-line
PLAINTEXT_SECRET (the base64 finding is the precise diagnosis — "literal value" is the wrong wording for
an encoded blob). **HEREDOC_SECRET** reuses the literal-vs-reference guard on the block-scalar body: a
secret key whose block scalar (`|` / `>`) holds a single `${VAR}` / placeholder line is **not** flagged,
and a block scalar on a NON-secret key (`description: |`) never matches (the key alternation is the
secret set). **WORLD_WRITABLE** flags only the world-writable octal modes (`0777`/`0666`/`777`/`666`,
incl. an `0o` prefix) and a `chmod` that grants `other`/`all` write (`777`/`666`/`o+w`/`a+w`/bare `+w`);
a restrictive mode (other-digit `0`/`4`/`5` — `0644`/`0600`/`0755`/`0700`/`0750`) and an owner/group-only
`chmod u+w`/`g+w` do **not** trip it.

## Allowlist / baseline — suppressing a *reviewed* exception (opt-in)

Some findings are intended: a public ALB *is* `0.0.0.0/0`, a demo image *is* pinned to a tag the team
accepts. Re-failing on those every run trains people to ignore the linter. The allowlist suppresses a
**specific, reviewed** finding *without* disabling the smell globally. It is **opt-in and default-off**:
with no `--ignore` flag and no discovered `.config-lint-ignore`, the linter behaves exactly as it does
without the feature — every smell still fires.

Provide it two ways:
- `python3 bin/config-lint.py --ignore <file> <target>` — an explicit allowlist (wins over discovery).
- drop a `.config-lint-ignore` in the scanned directory (or the CWD) — it is **auto-discovered** like a
  `.gitignore`, so a committed baseline travels with the repo.

**Format** — line-based; blank lines and `#` comments are ignored. Each entry is one of:

| Entry | Suppresses |
|---|---|
| `KIND` | **all** findings of that kind (e.g. `NO_RESOURCE_LIMITS`) |
| `KIND:path/to/file.yaml` | that kind **in that file** |
| `KIND:path/to/file.yaml:LINE` | that kind **at that exact line** in that file |

Matching is **deliberately precise** — a too-broad entry would silently hide a *real* finding, which is
the failure mode an allowlist must avoid:
- the **KIND** must match the finding's kind **exactly** (case-sensitive — `OPEN_NETWORK`, not
  `open_network`);
- the **path** (when given) matches the finding's file as a **path SUFFIX on segment boundaries** —
  `app/db.yaml` matches `svc/app/db.yaml` but **not** `myapp/db.yaml`; a bare `db.yaml` matches any
  `…/db.yaml`. (A non-boundary substring like `fra.yaml` does **not** match `infra.yaml`.)
- the **LINE** (when given) must equal the finding's line.

**No silent caps — what was dropped is always surfaced.** Whenever the allowlist suppresses anything, a
one-line `config-lint: N finding(s) suppressed by allowlist (<file>)` summary is written to **stderr**,
so a silently over-broad allowlist is visible. `--show-suppressed` additionally prints each dropped
finding (prefixed `SUPPRESSED`). A suppressed finding is **not** counted toward the exit code, so a
config whose *only* remaining findings are all allowlisted exits `0` (with the suppressed count noted).

**Anti-rot guards** (so the baseline can't silently decay):
- an entry that matches **nothing** — a stale exception left after the config was fixed — emits
  `WARN: stale allowlist entry 'X' (matched nothing)`. Treat a new stale warning as a prompt to delete
  the line.
- a **malformed** line emits a `WARN` and is **skipped** (it never crashes the run); the rest of the
  allowlist still applies.

The allowlist is for an exception you have **read and accepted**, not a way to silence the linter
wholesale — it is the baseline equivalent of the reference/placeholder guard above: a finding is dropped
only when a human has explicitly listed it, and the drop is always counted in the open.

## Least-privilege (the B4 judgment, beyond the linter)

The linter catches the wildcard `"*"`; minimality needs a read:

- **Scope the action.** `s3:*` on `arn:aws:s3:::*` is a wildcard the linter catches; `s3:GetObject` on
  one bucket prefix is the minimal grant. Between them is a spectrum the linter can't judge — does
  this role need `Put`/`Delete`, or only `Get`? Grant the verbs actually used, on the resources
  actually named.
- **Principal narrowing.** A trust policy with `"Principal": "*"` is open; bind it to the specific
  role/account that must assume it.
- **Network reach.** Beyond `0.0.0.0/0`: is the security group / NetworkPolicy scoped to the source
  that needs it, or to a wide range? Default-deny, then allow the minimum.
- **Capabilities & privilege.** The linter now catches the headline pod-security grants directly as
  **K8S_UNSAFE** — `privileged: true`, a `hostPath:` volume, `runAsUser: 0`, `allowPrivilegeEscalation:
  true`. Beyond those, `hostNetwork`/`hostPID`/`hostIPC`, added Linux capabilities (`SYS_ADMIN`,
  `NET_ADMIN`), and a missing `readOnlyRootFilesystem` are each a privilege grant that needs a
  justification, not a default — the B4 judgment beyond the floor.

## Pinning & reproducibility

- **Images** — pin a tag *and* a digest (`image: web@sha256:…`) for true reproducibility; a bare tag
  still drifts when the registry re-pushes. `:latest` is the worst case; no tag at all (a Dockerfile
  `FROM ubuntu`) is the same defect.
- **Modules / providers / actions** — pin a Terraform module `?ref=v1.2.3` (not a branch), a provider
  version constraint, a GitHub Action to a commit SHA (`uses: actions/checkout@<sha>`, not `@v4`). An
  unpinned dependency is a supply-chain and a reproducibility hole.

## Resource limits & blast radius

- **Limits present** — every k8s container declares `resources.requests` and `limits`; an unbounded
  container is a node-level DoS waiting to happen. The linter check is **coarse and document-level**:
  it fires only when there is *no* `resources:` block anywhere in the manifest, so a sidecar that sets
  limits **masks** a sibling app container that doesn't. The per-container audit (every container has
  both requests *and* limits) and right-sizing the numbers are the B4 review beyond this floor.
- **Blast radius (ties to B5)** — the change is **scoped** (this module/namespace, not the whole
  account), **reversible** (a destroy of stateful data is not), and **protected** where it must be
  (`deletion_protection`, `prevent_destroy`, a `PodDisruptionBudget`).

## How this scores

B4 is **floor ∧ judgment**:
- *floor* = `config-lint.py` is clean — no PLAINTEXT_SECRET / URL_EMBEDDED_SECRET / BASE64_SECRET /
  HEREDOC_SECRET / UNPINNED_VERSION / OPEN_NETWORK / WILDCARD_GRANT / NO_RESOURCE_LIMITS / K8S_UNSAFE /
  WORLD_WRITABLE (and any policy-engine pass you wired is green);
- *judgment* = grants are minimal, principals/networks narrowed, dependencies pinned to digests, and
  the change's blast radius is scoped and reversible.

A config with a clean parse/validate/plan but a literal secret or a wildcard grant is **not**
B4-passing — the floor failures are gate-grade, and the corrective is the config (move the secret to a
ref, scope the grant), not the score.
