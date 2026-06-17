# Secrets & safety — the mechanizable smells (B4)

The B4 Safety review has a hard floor whose findings are **gate-grade, not a matter of taste**: a
plaintext secret (a secret-ish key *or* a credential in a connection-string URL), an unpinned `:latest`
image, a `0.0.0.0/0` ingress, a wildcard `"*"` IAM grant, a k8s container with no resource cap, a k8s
privilege grant (`privileged: true` / `hostPath` / `runAsUser: 0` / `allowPrivilegeEscalation: true`).
`bin/config-lint.py` is the always-available static pass that catches them. It is a **cheap,
high-signal FIRST pass — not a complete floor**: a text-level regex over five formats will have a
residual false-negative surface (a base64 blob, a heredoc/block-scalar literal, an indentation the
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
| **UNPINNED_VERSION** | `:latest`, or a Dockerfile `FROM` / image with no tag or digest | the deploy is **not reproducible** — "latest" drifts under you; the build is unrepeatable |
| **OPEN_NETWORK** | `0.0.0.0/0` or `::/0` in an ingress/egress/CIDR position | exposed to the **entire internet** — the default-deny posture is broken |
| **WILDCARD_GRANT** | `"*"` in an `Action` / `Resource` / `Principal` / `permissions` position | over-broad permission — violates least-privilege; one compromised credential is total |
| **NO_RESOURCE_LIMITS** | a k8s pod whose spec declares `containers:` but has **no `resources:` block anywhere in the document** (coarse, document-level) | no cap on CPU/memory — a noisy neighbour can starve the node |
| **K8S_UNSAFE** | in a k8s-looking doc: `privileged: true`, a `hostPath:` volume, `runAsUser: 0` (root), or `allowPrivilegeEscalation: true` | each is a pod-security privilege grant — a container break-out / host-takeover risk that needs an explicit justification, not a default |

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
- *floor* = `config-lint.py` is clean — no PLAINTEXT_SECRET / URL_EMBEDDED_SECRET / UNPINNED_VERSION /
  OPEN_NETWORK / WILDCARD_GRANT / NO_RESOURCE_LIMITS / K8S_UNSAFE (and any policy-engine pass you wired
  is green);
- *judgment* = grants are minimal, principals/networks narrowed, dependencies pinned to digests, and
  the change's blast radius is scoped and reversible.

A config with a clean parse/validate/plan but a literal secret or a wildcard grant is **not**
B4-passing — the floor failures are gate-grade, and the corrective is the config (move the secret to a
ref, scope the grant), not the score.
