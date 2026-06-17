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
  PLAINTEXT_SECRET   a secret-ish key (password/secret/token/api_key/...) set to a literal string
  UNPINNED_VERSION   `:latest` or a missing image/version pin — the deploy is not reproducible
  OPEN_NETWORK       0.0.0.0/0 or ::/0 — ingress/egress open to the entire internet
  WILDCARD_GRANT     "*" in an IAM action/resource/principal position — over-broad permission
  NO_RESOURCE_LIMITS a k8s container with requests/limits absent — no cap on what it can consume

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
                      | <[A-Z_]+>                              # <PLACEHOLDER>
                      | ['"]?(?:changeme|placeholder|example|redacted|xxx+|\*+)['"]?\s*$
                      )""", re.IGNORECASE | re.VERBOSE)

# secret-ish key on the left of a `:` / `=` assignment
_SECRET_KEY = re.compile(
    r"""(?im)^\s*['"]?([A-Za-z0-9_.\-]*?(?:password|passwd|secret|token|api[_-]?key|
        access[_-]?key|secret[_-]?key|private[_-]?key|client[_-]?secret|auth|credential)
        [A-Za-z0-9_.\-]*)['"]?\s*[:=]\s*(.+?)\s*$""", re.VERBOSE)

_UNPINNED = re.compile(r"""(?im)(?:^|[\s"'=:])(?:image|FROM)\b[^\n#]*?[\w./-]+:latest\b""")
_FROM_NO_TAG = re.compile(r"""(?im)^\s*FROM\s+(?!.*(?::[\w.-]+|@sha256:))[\w./-]+\s*(?:AS\s+\w+)?\s*$""")
_OPEN_NET = re.compile(r"""(?:0\.0\.0\.0/0|(?<![\w:])::/0)""")
# a wildcard in an action/resource/principal position (IAM-shaped): key … : … "*"
_WILDCARD_GRANT = re.compile(
    r"""(?im)["']?(?:Action|Resource|Principal|actions|resources|permissions|scopes?)["']?\s*[:=]\s*["']\*["']""")
_WILDCARD_GRANT_LIST = re.compile(
    r"""(?im)["']?(?:Action|Resource|Principal|actions|resources|permissions|scopes?)["']?\s*[:=]\s*\[\s*["']\*["']""")

_SECRET_VALUE_LOOKSREAL = re.compile(r"""^['"]?[^\s'"#]{4,}['"]?$""")


def _looks_like_literal_secret(value):
    """True if a secret-key's value is a real literal, not a reference/placeholder/empty."""
    v = value.split("#", 1)[0].strip()           # drop trailing comment
    if not v or v in ("''", '""', "null", "~", "{}", "[]"):
        return False
    if _REF.match(v):
        return False
    return bool(_SECRET_VALUE_LOOKSREAL.match(v))


def lint_text(text, path=""):
    """Return a list of (kind, line, detail) findings for one config blob."""
    finds = []
    lines = text.splitlines()
    is_k8s = bool(re.search(r"(?m)^\s*apiVersion:\s*\S", text)) and "kind:" in text

    for i, line in enumerate(lines, 1):
        stripped = line.split("#", 1)[0]
        if not stripped.strip():
            continue
        m = _SECRET_KEY.match(line)
        if m and _looks_like_literal_secret(m.group(2)):
            finds.append(("PLAINTEXT_SECRET", i, "%s set to a literal value — use a secret ref/var" % m.group(1)))
        if _OPEN_NET.search(stripped):
            finds.append(("OPEN_NETWORK", i, "0.0.0.0/0 or ::/0 — open to the entire internet"))
        if _WILDCARD_GRANT.search(line) or _WILDCARD_GRANT_LIST.search(line):
            finds.append(("WILDCARD_GRANT", i, "wildcard \"*\" grant — over-broad permission (least-privilege)"))

    for m in _UNPINNED.finditer(text):
        finds.append(("UNPINNED_VERSION", text.count("\n", 0, m.start()) + 1, "uses :latest — not reproducible, pin a version/digest"))
    for m in _FROM_NO_TAG.finditer(text):
        finds.append(("UNPINNED_VERSION", text.count("\n", 0, m.start()) + 1, "Dockerfile FROM has no tag/digest — pin it"))

    # k8s: a container declared with no resources block at all (heuristic, advisory-shaped but gated as a smell)
    if is_k8s and re.search(r"(?m)^\s*containers:\s*$", text) and "resources:" not in text:
        line = next((i for i, ln in enumerate(lines, 1) if re.match(r"\s*containers:\s*$", ln)), 0)
        finds.append(("NO_RESOURCE_LIMITS", line, "k8s container(s) declare no resources.requests/limits"))

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
SAFE_SECRET_REF = 'db:\n  password: ${DB_PASSWORD}\n  token: "{{ .Values.token }}"\n  secret: ""\n  apiKey: <CHANGEME>\n'
BAD_LATEST = "FROM node:latest\nimage: nginx:latest\n"
BAD_FROM_NOTAG = "FROM ubuntu\nRUN apt-get update\n"
BAD_OPEN_NET = 'ingress:\n  - cidr_blocks: ["0.0.0.0/0"]\n  - ipv6: "::/0"\n'
BAD_WILDCARD = '{"Statement": [{"Effect": "Allow", "Action": "*", "Resource": "*"}]}\n'
BAD_WILDCARD_LIST = 'permissions:\n  actions: ["*"]\n'
BAD_K8S_NOLIMITS = "apiVersion: v1\nkind: Pod\nspec:\n  containers:\n    - name: app\n      image: app:1.0\n"


def selftest():
    errs = []

    def kinds(text):
        return {k for k, _, _ in lint_text(text)}

    if lint_text(CLEAN):
        errs.append("CLEAN config produced findings: %s" % lint_text(CLEAN))
    for text, want in (
        (BAD_SECRET, "PLAINTEXT_SECRET"),
        (BAD_LATEST, "UNPINNED_VERSION"),
        (BAD_FROM_NOTAG, "UNPINNED_VERSION"),
        (BAD_OPEN_NET, "OPEN_NETWORK"),
        (BAD_WILDCARD, "WILDCARD_GRANT"),
        (BAD_WILDCARD_LIST, "WILDCARD_GRANT"),
        (BAD_K8S_NOLIMITS, "NO_RESOURCE_LIMITS"),
    ):
        if want not in kinds(text):
            errs.append("missed %s (got %s)" % (want, sorted(kinds(text))))
    # a referenced/placeholder secret must NOT be flagged (the false-positive guard)
    if "PLAINTEXT_SECRET" in kinds(SAFE_SECRET_REF):
        errs.append("false positive: flagged a secret reference/placeholder as plaintext")
    # both wildcard action and resource on one JSON line are caught (count >= 1)
    if "WILDCARD_GRANT" not in kinds(BAD_WILDCARD):
        errs.append("JSON wildcard grant not caught")
    return errs


def _iter_files(path):
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            if "/.git" in dp or "__pycache__" in dp:
                continue
            for fn in sorted(fns):
                low = fn.lower()
                if low.endswith(CONFIG_EXTS) or any(low == n or low.startswith(n + ".") for n in CONFIG_NAMES):
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
        print("config-lint: OK — 5 safety smells caught + reference/placeholder false-positive guard verified")
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
