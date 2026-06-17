#!/usr/bin/env python3
"""config-lint.py — the config-decomposer safety-smell detector. Self-contained (stdlib only).

The dangerous config defects that a `parse`/`validate` pass is silent about — a plaintext secret, an
unpinned `:latest` image, a `0.0.0.0/0` wide-open ingress, a wildcard `"*"` IAM grant, a k8s
container with no resource limits — are *mechanizable*. This routes the B4 Safety review's hard floor
to code: a single text-level regex pass over YAML / JSON / HCL / Dockerfile / TOML (configs are
treated as text so one detector spans every format). Findings are gate-grade — a literal secret or a
wildcard grant is a FAIL, not a style nit.

It is deliberately a STATIC smell detector, not a policy engine (that's the harness's `policy` phase —
`checkov`/`conftest`). Its job is the cheap, always-available floor that needs no tool install.

Smell kinds:
  PLAINTEXT_SECRET     a secret-ish key (password/secret/token/api_key/pwd/pat/dsn/...) set to a literal string
  URL_EMBEDDED_SECRET  a literal password in a connection-string / URL userinfo (scheme://user:PASS@host)
  UNPINNED_VERSION     `:latest` or a missing image/version pin — the deploy is not reproducible
  OPEN_NETWORK         0.0.0.0/0 or ::/0 — ingress/egress open to the entire internet
  WILDCARD_GRANT       "*" in an IAM action/resource/principal position — over-broad permission
  NO_RESOURCE_LIMITS   a k8s container with requests/limits absent — no cap on what it can consume
  K8S_UNSAFE           a k8s privilege grant — privileged:true / hostPath / runAsUser:0 / allowPrivilegeEscalation:true

  python3 bin/config-lint.py selftest
  python3 bin/config-lint.py <file | dir>

Nonzero exit on any finding. Python 3.8+.
"""
import os
import re
import sys

CONFIG_EXTS = (".yaml", ".yml", ".json", ".tf", ".tfvars", ".hcl", ".toml", ".env")
CONFIG_NAMES = ("dockerfile",)   # extensionless config filenames (matched case-insensitively)

# A value that is a reference/interpolation, not a literal — these are SAFE on the secret check.
_REF = re.compile(r"""^\s*['"]?\s*(\$\{?[\w.\[\]-]+\}?         # ${VAR} / $VAR / ${var.x} / ${{ secrets.X }}
                      | \$\(.+\)                               # $(cmd)
                      | \{\{.+\}\}                             # {{ .Values.x }} / templated
                      | !(?:Ref|Sub|ImportValue|GetAtt)\b      # CloudFormation intrinsics
                      | (?:var|local|data|module|secret|env)\. # terraform/env references
                      | \{?\s*(?:secretKeyRef|configMapKeyRef|valueFrom)\b  # k8s value-from-a-ref shapes
                      | <[A-Z_]+>                              # <PLACEHOLDER>
                      | ['"]?(?:changeme|placeholder|example|redacted|xxx+|\*+)['"]?\s*$
                      )""", re.IGNORECASE | re.VERBOSE)

# secret-ish key on the left of a `:` / `=` assignment.
# The key may appear anywhere on the line, not only at the indent: a YAML list item (`  - password: x`),
# a single-line / inline JSON object (`{ "password": "x", ... }`), or a trailing-comma key in
# pretty-printed JSON all put the key after some `[{[,\s-]*` lead-in, not flush against the margin.
_SECRET_KEY = re.compile(
    r"""(?im)(?:^|[{\[,\s-])\s*['"]?([A-Za-z0-9_.\-]*?(?:password|passwd|secret|token|api[_-]?key|
        access[_-]?key(?:[_-]?id)?|secret[_-]?key|private[_-]?key|client[_-]?secret|auth|credential)
        [A-Za-z0-9_.\-]*)['"]?\s*[:=]\s*
        (                                       # the value — capture ONE field, not the rest of the line:
          '[^']*' | "[^"]*"                     #   a quoted string (so inline JSON can hold more keys after)
          | [^\s,}\]]+(?:\ [^\s,}\]#]+)*        #   or a bare value up to the next field/closer/comment
        )""", re.VERBOSE)

# The short / unusual secret keys (`pwd`, `pat`, `bearer`, `dsn`) match ONLY as a WHOLE key — never as a
# substring — or `pat` would fire on `path`/`pattern`, `dsn` on words, etc. The key boundary is a line
# start / `{`/`[`/`,`/whitespace/`-` on the left and the assignment `:`/`=` (with optional quote) on the
# right, with no intervening key-name chars. (`passwd` already matches above; kept here for symmetry is
# unneeded — these are the keys the broad alternation deliberately does NOT cover.)
_SECRET_KEY_WHOLE = re.compile(
    r"""(?im)(?:^|[{\[,\s-])\s*['"]?(pwd|pat|bearer|dsn)['"]?\s*[:=]\s*
        (
          '[^']*' | "[^"]*"
          | [^\s,}\]]+(?:\ [^\s,}\]#]+)*
        )""", re.VERBOSE)

_UNPINNED = re.compile(r"""(?im)(?:^|[\s"'=:])(?:image|FROM)\b[^\n#]*?[\w./-]+:latest\b""")
_FROM_NO_TAG = re.compile(r"""(?im)^\s*FROM\s+(?!.*(?::[\w.-]+|@sha256:))[\w./-]+\s*(?:AS\s+\w+)?\s*$""")
_OPEN_NET = re.compile(r"""(?:0\.0\.0\.0/0|(?<![\w:])::/0)""")
# a wildcard in an action/resource/principal position (IAM-shaped): key … : … "*"
_WILDCARD_GRANT = re.compile(
    r"""(?im)["']?(?:Action|Resource|Principal|actions|resources|permissions|scopes?)["']?\s*[:=]\s*["']\*["']""")
_WILDCARD_GRANT_LIST = re.compile(
    r"""(?im)["']?(?:Action|Resource|Principal|actions|resources|permissions|scopes?)["']?\s*[:=]\s*\[\s*["']\*["']""")
# the canonical MULTI-LINE wildcard: the key opens an array on one line and a bare `"*"` element sits on a
# later line — `"Action": [` \n `"*"` \n `]`. Same-line regexes miss it; this spans the gap up to the `"*"`.
_WILDCARD_GRANT_MULTILINE = re.compile(
    r"""(?is)["']?(?:Action|Resource|Principal|actions|resources|permissions|scopes?)["']?\s*[:=]\s*\[
        [^\]\*]*                                 # only whitespace/commas between the `[` and the bare `*`
        ["']\*["']""", re.VERBOSE)

_SECRET_VALUE_LOOKSREAL = re.compile(r"""^['"]?[^\s'"#]{4,}['"]?$""")

# A credential embedded in a connection-string / URL userinfo: `scheme://user:PASSWORD@host…`. The
# password is the segment between the FIRST `:` after `://` and the `@`. We require BOTH a user and a
# password (`user:pass@`) — a bare `scheme://host` or `scheme://user@host` has no embedded secret.
# Group 1 = the literal password segment, tested against the placeholder/reference guard below.
_URL_USERINFO = re.compile(
    r"""(?ix)
        [a-z][a-z0-9+.\-]*://         # scheme:// (postgres/mysql/redis/mongodb/amqp/https/…)
        [^/\s:@]*                     # userinfo username (may be empty — `redis://:pass@host`)
        :([^/\s@]+)                   # `:` then the password segment (group 1) — no `/`/`@`/space
        @                             # `@` ends the userinfo
    """)
# A URL password segment that is a reference/placeholder, not a literal — SAFE (same spirit as _REF).
_URL_PW_REF = re.compile(
    r"""(?ix)^(?:
          \$\{?[\w.\[\]-]*\}?            # ${VAR} / $VAR / ${PASSWORD}
        | \$\{\{.+\}\}                   # ${{ secrets.X }}
        | \{\{.*\}\}                     # {{ .Values.x }}
        | <[^>]*>                        # <PASSWORD> / <CHANGEME>
        | \*+                            # *** (masked)
        | redacted
        )$""")

# k8s privilege-grant smells (only scanned in a k8s-looking doc). Each is a distinct sub-finding.
_K8S_PRIVILEGED = re.compile(r"""(?im)^\s*privileged\s*:\s*true\b""")
_K8S_HOSTPATH = re.compile(r"""(?im)^\s*hostPath\s*:""")
_K8S_RUNASROOT = re.compile(r"""(?im)^\s*runAsUser\s*:\s*0\b""")
_K8S_PRIVESC = re.compile(r"""(?im)^\s*allowPrivilegeEscalation\s*:\s*true\b""")


def _strip_value(value):
    """Normalize a captured secret value: drop a trailing comment and a single trailing `,`/`]`/`}`.

    A non-last key in pretty-printed JSON ends in `,`; an inline value can be followed by the array/
    object closer (`]`/`}`). Strip exactly one such trailer (and re-trim) so the literal test sees the
    bare value, not `"hunter2supersecret",` or `"hunter2", "api_key": ...`.
    """
    v = value.split("#", 1)[0].strip()           # drop trailing comment
    # if this is an inline JSON value, cut at the closing quote of the FIRST quoted token so a
    # single-line `{ "password": "hunter2", "api_key": "..." }` doesn't swallow the rest of the line
    if v[:1] in ("'", '"'):
        q = v[0]
        end = v.find(q, 1)
        if end != -1:
            v = v[:end + 1]
    else:
        # bare value: stop at the first separator that ends an inline field
        v = re.split(r"[,\]}]", v, 1)[0].strip()
    # strip one trailing structural char left on a quoted value (`"x",` / `"x"]` / `"x"}`)
    while v and v[-1] in ",]}":
        v = v[:-1].strip()
    return v


def _looks_like_literal_secret(value):
    """True if a secret-key's value is a real literal, not a reference/placeholder/empty."""
    v = _strip_value(value)
    if not v or v in ("''", '""', "null", "~", "{}", "[]"):
        return False
    if _REF.match(v):
        return False
    return bool(_SECRET_VALUE_LOOKSREAL.match(v))


def _url_pw_is_literal(pw):
    """True if a URL userinfo password segment is a real literal, not a placeholder/reference.

    The whole authority can also be an env-only interpolation that the userinfo regex split on a `:`
    inside `${...}` — `_URL_PW_REF` catches those because the captured segment still starts with the
    interpolation/placeholder syntax.
    """
    pw = pw.strip()
    if not pw:
        return False
    if _URL_PW_REF.match(pw):
        return False
    return True


def lint_text(text, path=""):
    """Return a list of (kind, line, detail) findings for one config blob."""
    finds = []
    lines = text.splitlines()
    is_k8s = bool(re.search(r"(?m)^\s*apiVersion:\s*\S", text)) and "kind:" in text

    for i, line in enumerate(lines, 1):
        stripped = line.split("#", 1)[0]
        if not stripped.strip():
            continue
        for m in _SECRET_KEY.finditer(line):
            if _looks_like_literal_secret(m.group(2)):
                finds.append(("PLAINTEXT_SECRET", i, "%s set to a literal value — use a secret ref/var" % m.group(1)))
        for m in _SECRET_KEY_WHOLE.finditer(line):
            if _looks_like_literal_secret(m.group(2)):
                finds.append(("PLAINTEXT_SECRET", i, "%s set to a literal value — use a secret ref/var" % m.group(1)))
        for m in _URL_USERINFO.finditer(line):
            if _url_pw_is_literal(m.group(1)):
                finds.append(("URL_EMBEDDED_SECRET", i,
                              "credentials embedded in a connection string — the password is in the "
                              "URL userinfo; inject it from a secret store"))
        if _OPEN_NET.search(stripped):
            finds.append(("OPEN_NETWORK", i, "0.0.0.0/0 or ::/0 — open to the entire internet"))
        if _WILDCARD_GRANT.search(line) or _WILDCARD_GRANT_LIST.search(line):
            finds.append(("WILDCARD_GRANT", i, "wildcard \"*\" grant — over-broad permission (least-privilege)"))

    for m in _WILDCARD_GRANT_MULTILINE.finditer(text):
        # report the line of the bare "*" element, not the opening key
        line = text.count("\n", 0, m.end()) + 1
        finds.append(("WILDCARD_GRANT", line, "wildcard \"*\" grant — over-broad permission (least-privilege)"))

    for m in _UNPINNED.finditer(text):
        finds.append(("UNPINNED_VERSION", text.count("\n", 0, m.start()) + 1, "uses :latest — not reproducible, pin a version/digest"))
    for m in _FROM_NO_TAG.finditer(text):
        finds.append(("UNPINNED_VERSION", text.count("\n", 0, m.start()) + 1, "Dockerfile FROM has no tag/digest — pin it"))

    # k8s: a pod whose spec has containers but NO `resources:` block anywhere in the document.
    # This is a coarse, document-level heuristic, not a per-container check: a sidecar that *does* set
    # `resources:` masks a sibling app container that doesn't (the substring is present), so the absence
    # of all caps is what fires here. The per-container audit (every container, requests AND limits) is
    # the B4 review beyond this floor — see references/secrets-and-safety.md.
    if is_k8s and re.search(r"(?m)^\s*containers:\s*$", text) and "resources:" not in text:
        line = next((i for i, ln in enumerate(lines, 1) if re.match(r"\s*containers:\s*$", ln)), 0)
        finds.append(("NO_RESOURCE_LIMITS", line, "k8s container(s) declare no resources.requests/limits anywhere (coarse check)"))

    # k8s pod-security privilege grants. Only fire in a k8s-looking doc — so the bare word "privileged"
    # in a non-k8s comment/prose, or a `runAsUser: 0` in some unrelated config, doesn't trip. Each is a
    # distinct sub-finding reported at its own line. The checks are line-anchored (a real YAML key), so
    # `allowPrivilegeEscalation: false` / `runAsUser: 1000` don't match. Gated on is_k8s OR a
    # `securityContext:` block, so Helm/kustomize pod-spec fragments (no apiVersion/kind) are still
    # scanned — `securityContext` is a k8s-specific key, a low-false-positive signal.
    if is_k8s or re.search(r"(?im)^\s*securityContext\s*:", text):
        for rx, detail in (
            (_K8S_PRIVILEGED, "privileged: true — the container runs with full host privileges"),
            (_K8S_HOSTPATH, "hostPath volume — mounts a host filesystem path into the pod"),
            (_K8S_RUNASROOT, "runAsUser: 0 — the container runs as root"),
            (_K8S_PRIVESC, "allowPrivilegeEscalation: true — the process can gain more privileges than its parent"),
        ):
            for m in rx.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                finds.append(("K8S_UNSAFE", line, detail))

    # de-dup identical (kind,line)
    seen, out = set(), []
    for f in finds:
        key = (f[0], f[1])
        if key not in seen:
            seen.add(key)
            out.append(f)
    return sorted(out, key=lambda f: (f[1], f[0]))


# --- selftest fixtures -------------------------------------------------------------------------
CLEAN = """\
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
        - name: web
          image: registry.example.com/web:1.4.2
          resources:
            limits: { cpu: "500m", memory: "256Mi" }
          env:
            - name: DB_PASSWORD
              valueFrom: { secretKeyRef: { name: db, key: password } }
"""
BAD_SECRET = 'database:\n  password: "hunter2supersecret"\n  api_key: AKIAIOSFODNN7EXAMPLE\n'
# --- B1 adversarial shapes: the headline secret smell in the three most common shapes the
#     indent-anchored / end-of-line-anchored regex used to miss ----------------------------------
BAD_SECRET_TRAILING_COMMA = '{\n  "region": "us-east-1",\n  "password": "hunter2supersecret",\n  "port": 5432\n}\n'
BAD_SECRET_SINGLE_LINE = '{ "password": "hunter2", "api_key": "AKIAIOSFODNN7EXAMPLE" }\n'
BAD_SECRET_YAML_LIST = 'credentials:\n  - name: bob\n  - password: anotherrealsecret\n'
SAFE_SECRET_REF = 'db:\n  password: ${DB_PASSWORD}\n  token: "{{ .Values.token }}"\n  secret: ""\n  apiKey: <CHANGEME>\n'
# the false-positive guards that must STAY clean even with the broadened key match
SAFE_SECRET_REF_MORE = ('env:\n  token: ${{ secrets.GH_TOKEN }}\n  password: secretKeyRef\n'
                        '  api_key: var.api_key\n  client_secret: ${CLIENT_SECRET}\n')
BAD_LATEST = "FROM node:latest\nimage: nginx:latest\n"
BAD_FROM_NOTAG = "FROM ubuntu\nRUN apt-get update\n"
BAD_OPEN_NET = 'ingress:\n  - cidr_blocks: ["0.0.0.0/0"]\n  - ipv6: "::/0"\n'
BAD_WILDCARD = '{"Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}\n'
BAD_WILDCARD_LIST = 'permissions:\n  actions: ["*"]\n'
# --- B2 adversarial: the canonical MULTI-LINE wildcard grant (key opens an array, bare "*" on a later line)
BAD_WILDCARD_MULTILINE = ('{\n  "Statement": [{\n    "Effect": "Allow",\n    "Action": [\n'
                          '      "*"\n    ],\n    "Resource": "arn:aws:s3:::my-bucket/*"\n  }]\n}\n')
SAFE_WILDCARD_SCOPED = '{\n  "Action": [\n    "s3:GetObject",\n    "s3:PutObject"\n  ]\n}\n'
BAD_K8S_NOLIMITS = "apiVersion: v1\nkind: Pod\nspec:\n  containers:\n    - name: app\n      image: app:1.0\n"
# --- M3 adversarial: a `*.Dockerfile`-named file (api.Dockerfile) must be SCANNED by the dir walk
DOCKERFILE_NAMED = "FROM python:latest\nRUN pip install flask\n"

# --- NEW SMELL 1: URL_EMBEDDED_SECRET — a literal password in connection-string / URL userinfo ---
BAD_URL_SECRET = 'DATABASE_URL: "postgres://app:hunter2supersecret@db.internal:5432/app"\n'
BAD_URL_SECRET_REDIS = 'cache:\n  url: redis://:s3cr3tpass@cache:6379\n'
SAFE_URL_NO_PW = 'DATABASE_URL: "postgres://app@db/app"\n'           # no password segment
SAFE_URL_VAR = 'DATABASE_URL: "postgres://app:${DB_PASSWORD}@db/app"\n'  # var interpolation
SAFE_URL_PLACEHOLDER = 'DATABASE_URL: "postgres://app:<PASSWORD>@db/app"\n'  # placeholder
SAFE_URL_REDACTED = 'dsn_ref: postgres://app:***@db/app\n'           # masked / redacted

# --- NEW SMELL 2: expanded secret KEY set (whole-key short names + new alternation members) ---
BAD_KEY_CLIENT_SECRET = 'oidc:\n  client_secret: "abc123def456ghi"\n'
BAD_KEY_PAT = 'github:\n  pat: "ghp_realtokenvalue"\n'
BAD_KEY_PWD = 'db:\n  pwd: "realdatabasepw"\n'
BAD_KEY_ACCESS_KEY_ID = 'aws:\n  access_key_id: "AKIAIOSFODNN7EXAMPLE"\n'
SAFE_KEY_CLIENT_SECRET_REF = 'oidc:\n  client_secret: ${OIDC_SECRET}\n'
# whole-key guard: `keyboard:`/`gateway:` must NOT match (no `pat`/`pwd`/`dsn`/`bearer` whole-key, and
# the broad alternation members aren't substrings of these either)
SAFE_KEY_SUBSTRING = 'ui:\n  keyboard: "qwerty-layout"\n  gateway: "10.0.0.1"\n  path: "/var/run"\n'

# --- NEW SMELL 3: K8S_UNSAFE — pod-security privilege grants in a k8s-looking doc ---
BAD_K8S_PRIVILEGED = ('apiVersion: v1\nkind: Pod\nspec:\n  containers:\n    - name: app\n'
                      '      image: app:1.0\n      resources:\n        limits: { cpu: "1" }\n'
                      '      securityContext:\n        privileged: true\n')
BAD_K8S_RUNASROOT = ('apiVersion: v1\nkind: Pod\nspec:\n  securityContext:\n    runAsUser: 0\n'
                     '  containers:\n    - name: app\n      image: app:1.0\n      resources:\n'
                     '        limits: { cpu: "1" }\n')
BAD_K8S_HOSTPATH = ('apiVersion: v1\nkind: Pod\nspec:\n  containers:\n    - name: app\n'
                    '      image: app:1.0\n      resources:\n        limits: { cpu: "1" }\n'
                    '  volumes:\n    - name: hostvol\n      hostPath:\n        path: /var/run/docker.sock\n')
# a Helm/kustomize pod-spec FRAGMENT (no apiVersion/kind) — still scanned via the securityContext gate
BAD_K8S_FRAGMENT = ('containers:\n  - name: app\n    image: app:1.0\n'
                    '    securityContext:\n      privileged: true\n')
SAFE_K8S_HARDENED = ('apiVersion: v1\nkind: Pod\nspec:\n  containers:\n    - name: app\n'
                     '      image: app:1.0\n      resources:\n        limits: { cpu: "1" }\n'
                     '      securityContext:\n        runAsUser: 1000\n'
                     '        allowPrivilegeEscalation: false\n')
# a non-k8s doc that merely mentions "privileged"/"runAsUser" in prose/comment must NOT trip K8S_UNSAFE
SAFE_NONK8S_PROSE = '# this service runs privileged: true on the legacy box\nmode: standard\nrunAsUser: 0\n'


def selftest():
    errs = []

    def kinds(text):
        return {k for k, _, _ in lint_text(text)}

    if lint_text(CLEAN):
        errs.append("CLEAN config produced findings: %s" % lint_text(CLEAN))
    for text, want in (
        (BAD_SECRET, "PLAINTEXT_SECRET"),
        (BAD_SECRET_TRAILING_COMMA, "PLAINTEXT_SECRET"),   # B1: trailing-comma JSON key
        (BAD_SECRET_SINGLE_LINE, "PLAINTEXT_SECRET"),      # B1: inline single-line JSON object
        (BAD_SECRET_YAML_LIST, "PLAINTEXT_SECRET"),        # B1: YAML list item `- password: ...`
        (BAD_LATEST, "UNPINNED_VERSION"),
        (BAD_FROM_NOTAG, "UNPINNED_VERSION"),
        (BAD_OPEN_NET, "OPEN_NETWORK"),
        (BAD_WILDCARD, "WILDCARD_GRANT"),
        (BAD_WILDCARD_LIST, "WILDCARD_GRANT"),
        (BAD_WILDCARD_MULTILINE, "WILDCARD_GRANT"),        # B2: multi-line `"Action": [ \n "*" \n ]`
        (BAD_K8S_NOLIMITS, "NO_RESOURCE_LIMITS"),
        (BAD_URL_SECRET, "URL_EMBEDDED_SECRET"),           # NEW1: DATABASE_URL with literal password
        (BAD_URL_SECRET_REDIS, "URL_EMBEDDED_SECRET"),     # NEW1: redis://:pass@host
        (BAD_KEY_CLIENT_SECRET, "PLAINTEXT_SECRET"),       # NEW2: client_secret literal
        (BAD_KEY_PAT, "PLAINTEXT_SECRET"),                 # NEW2: pat (whole-key)
        (BAD_KEY_PWD, "PLAINTEXT_SECRET"),                 # NEW2: pwd (whole-key)
        (BAD_KEY_ACCESS_KEY_ID, "PLAINTEXT_SECRET"),       # NEW2: access_key_id
        (BAD_K8S_PRIVILEGED, "K8S_UNSAFE"),                # NEW3: privileged: true
        (BAD_K8S_RUNASROOT, "K8S_UNSAFE"),                 # NEW3: runAsUser: 0
        (BAD_K8S_HOSTPATH, "K8S_UNSAFE"),                  # NEW3: hostPath volume
        (BAD_K8S_FRAGMENT, "K8S_UNSAFE"),                  # NEW3: pod-spec fragment (no apiVersion/kind)
    ):
        if want not in kinds(text):
            errs.append("missed %s (got %s)" % (want, sorted(kinds(text))))
    # referenced/placeholder secrets must NOT be flagged (the false-positive guards, intact post-B1)
    for safe in (SAFE_SECRET_REF, SAFE_SECRET_REF_MORE, SAFE_KEY_CLIENT_SECRET_REF):
        if "PLAINTEXT_SECRET" in kinds(safe):
            errs.append("false positive: flagged a secret reference/placeholder as plaintext: %s" % kinds(safe))
    # the whole-key guard: a substring key (`keyboard`/`gateway`/`path`) must NOT be a PLAINTEXT_SECRET
    if "PLAINTEXT_SECRET" in kinds(SAFE_KEY_SUBSTRING):
        errs.append("false positive: a substring key (keyboard/gateway/path) flagged as a plaintext secret: %s"
                    % lint_text(SAFE_KEY_SUBSTRING))
    # NEW1 false-positive guards: a URL with no password / a var / a placeholder / a mask must NOT trip
    for safe in (SAFE_URL_NO_PW, SAFE_URL_VAR, SAFE_URL_PLACEHOLDER, SAFE_URL_REDACTED):
        if "URL_EMBEDDED_SECRET" in kinds(safe):
            errs.append("false positive: flagged a non-literal URL userinfo as an embedded secret: %s"
                        % lint_text(safe))
    # NEW3 false-positive guards: a hardened k8s doc (runAsUser:1000, allowPrivilegeEscalation:false)
    # and a non-k8s doc mentioning the words in prose must NOT trip K8S_UNSAFE
    for safe in (SAFE_K8S_HARDENED, SAFE_NONK8S_PROSE):
        if "K8S_UNSAFE" in kinds(safe):
            errs.append("false positive: flagged a hardened / non-k8s doc as K8S_UNSAFE: %s" % lint_text(safe))
    # a scoped multi-line action list (real verbs, no bare "*") must NOT trip the multi-line scan
    if "WILDCARD_GRANT" in kinds(SAFE_WILDCARD_SCOPED):
        errs.append("false positive: flagged a scoped (non-wildcard) action list as a wildcard grant")
    # both wildcard action and resource on one JSON line are caught (count >= 1)
    if "WILDCARD_GRANT" not in kinds(BAD_WILDCARD):
        errs.append("JSON wildcard grant not caught")
    # M3: a `*.Dockerfile`-named file (api.Dockerfile) is picked up by the directory walk
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        fp = os.path.join(d, "api.Dockerfile")
        with open(fp, "w", encoding="utf-8") as fh:
            fh.write(DOCKERFILE_NAMED)
        scanned = list(_iter_files(d))
        if fp not in scanned:
            errs.append("directory walk skipped api.Dockerfile (got %s)" % scanned)
        elif "UNPINNED_VERSION" not in {k for k, _, _ in lint_text(open(fp, encoding="utf-8").read())}:
            errs.append("api.Dockerfile content not linted for :latest")
    return errs


def _iter_files(path):
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            if "/.git" in dp or "__pycache__" in dp:
                continue
            for fn in sorted(fns):
                low = fn.lower()
                if (low.endswith(CONFIG_EXTS)
                        or low.endswith(".dockerfile")                        # api.Dockerfile, build.dockerfile
                        or any(low == n or low.startswith(n + ".") for n in CONFIG_NAMES)):  # Dockerfile, Dockerfile.dev
                    yield os.path.join(dp, fn)
    else:
        yield path


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("config-lint: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("config-lint: OK — 7 safety smells (plaintext + URL-embedded secrets, unpinned, open-net, "
              "wildcard grant, no-limits, k8s-unsafe) caught; reference/placeholder/whole-key + "
              "non-k8s false-positive guards + api.Dockerfile scan verified")
        return 0
    total, n = 0, 0
    for fp in _iter_files(argv[0]):
        try:
            text = open(fp, encoding="utf-8", errors="replace").read()
        except OSError as e:
            print("  ⚠ %s: unreadable (%s)" % (fp, e))
            continue
        n += 1
        for kind, line, detail in lint_text(text, fp):
            total += 1
            print("  %s:%s  %-18s %s" % (os.path.relpath(fp), line, kind, detail))
    if total:
        sys.stderr.write("config-lint: FAIL — %d safety smell(s) across %d file(s)\n" % (total, n))
        return 1
    print("config-lint: OK — no safety smells in %d file(s)" % n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
