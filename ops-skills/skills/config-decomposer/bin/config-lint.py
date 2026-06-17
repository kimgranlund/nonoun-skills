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
  BASE64_SECRET        a committed k8s Secret with a literal base64 `data:` value — commit-time secret material
  HEREDOC_SECRET       a secret-ish key assigned a multi-line literal (YAML block scalar | / >, or a shell heredoc)
  WORLD_WRITABLE       a world-writable file mode (0777/0666/777/666/0o777) or chmod 777/666/o+w/a+w
  UNPINNED_VERSION     `:latest` or a missing image/version pin — the deploy is not reproducible
  OPEN_NETWORK         0.0.0.0/0 or ::/0 — ingress/egress open to the entire internet
  WILDCARD_GRANT       "*" in an IAM action/resource/principal position — over-broad permission
  NO_RESOURCE_LIMITS   a k8s container with requests/limits absent — no cap on what it can consume
  K8S_UNSAFE           a k8s privilege grant — privileged:true / hostPath / runAsUser:0 / allowPrivilegeEscalation:true

  python3 bin/config-lint.py selftest
  python3 bin/config-lint.py <file | dir>
  python3 bin/config-lint.py --ignore <allowlist> <file | dir>
  python3 bin/config-lint.py --show-suppressed <file | dir>
  python3 bin/config-lint.py --json <file | dir>          # machine-readable report (composes with --ignore)

Nonzero exit on any finding. Python 3.8+.

MACHINE-READABLE REPORT (--json; additive reporting flag, parse-anywhere, composes with --ignore) -----
`--json` prints ONE report object to stdout and NOTHING else there — the shared schema every lint bin
emits, so GRADE/CI can fold structured safety findings into the report card's `safety_findings[]`:
  {"tool": "config-lint", "ok": <bool>, "summary": "<one line>",
   "findings": [{"kind", "severity": fail|warn, "location": "line:N", "message"}, ...]}
`ok` is true iff no un-suppressed finding (the exact condition that gives exit 0 in human mode). A
security smell (plaintext/URL/base64/heredoc secret, open-net, wildcard grant, k8s-unsafe,
world-writable) maps to severity `fail`; an advisory smell (unpinned version, no-resource-limits) and a
stale-allowlist WARN map to `warn`. A finding SUPPRESSED by the allowlist is NOT in `findings` (exactly
as in human mode) but its count is reported in `summary`. The exit code is UNCHANGED by --json (it is a
reporting flag, not a behavior change). Without --json, output + exit are byte-identical to before.

ALLOWLIST / BASELINE (opt-in; default behavior is byte-identical to no allowlist) -------------------
A reviewed, accepted finding can be suppressed without disabling the smell globally. Pass an explicit
allowlist with `--ignore <file>`, or drop a `.config-lint-ignore` file in the scanned directory (or
the CWD) — it is auto-discovered like a `.gitignore`. A suppressed finding is NOT printed and does NOT
count toward the exit code; the count of what was dropped is always surfaced to stderr (no silent
caps). `--show-suppressed` additionally prints each suppressed finding (prefixed `SUPPRESSED`).

Allowlist format (line-based; blank lines and `#` comments ignored). Each entry is one of:
  KIND                          suppress ALL findings of that kind  (e.g. `NO_RESOURCE_LIMITS`)
  KIND:path/to/file.yaml        suppress that kind in that file
  KIND:path/to/file.yaml:LINE   suppress that kind at that exact line in that file
Matching is deliberately precise so a too-broad entry can't silently hide real findings: the KIND
must match the finding's kind EXACTLY (case-sensitive), and the path (when given) must match the
finding's file as a path SUFFIX on path-segment boundaries — `app/db.yaml` matches `svc/app/db.yaml`
but not `myapp/db.yaml`; a bare filename `db.yaml` matches any `…/db.yaml`. The LINE (when given) must
equal the finding's line. An entry that matches NOTHING is reported as a `WARN: stale allowlist entry`
so the baseline doesn't rot; a malformed line is reported as a `WARN` and skipped (never a crash).
"""
import json
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

# --- BASE64_SECRET: a committed k8s Secret with literal base64 `data:` material ---------------------
# Scoped STRICTLY to a `kind: Secret` doc (so a base64-looking checksum / `@sha256:` digest in an
# arbitrary doc never trips). Within such a doc, a `data:` block (NOT `stringData:` — that's plaintext,
# already PLAINTEXT_SECRET's job) whose entries are `key: <base64>` is committed secret material: k8s
# `data:` values are base64 by spec. A value is LITERAL base64 when it is >=8 chars of [A-Za-z0-9+/]
# with optional `=` padding and nothing else — a `${VAR}` / `<PLACEHOLDER>` / templated value is not.
_K8S_SECRET_KIND = re.compile(r"""(?im)^\s*kind\s*:\s*["']?Secret["']?\s*$""")
# a `data:` block header (its own line, no inline value) — `stringData:` is explicitly excluded by the
# `(?<![A-Za-z])` lookbehind so `stringData:` cannot match the `data:` tail.
_K8S_DATA_HEADER = re.compile(r"""(?im)^(\s*)(?<![A-Za-z])data\s*:\s*$""")
_K8S_STRINGDATA_HEADER = re.compile(r"""(?im)^(\s*)stringData\s*:\s*$""")
# one `key: value` entry inside a `data:` block; group 1 = key, group 2 = the (possibly quoted) value.
_DATA_ENTRY = re.compile(r"""^(\s*)([A-Za-z0-9_.\-]+)\s*:\s*(.*?)\s*$""")
_BASE64_LITERAL = re.compile(r"""^['"]?[A-Za-z0-9+/]{8,}={0,2}['"]?$""")

# --- HEREDOC_SECRET: a secret-ish key assigned a multi-line literal (block scalar / heredoc) --------
# A YAML block scalar opens a secret key with `|` / `>` (and chomp/indent indicators `|-`, `>2`, `|+`):
#   password: |
#     -----BEGIN ...
# Group 1 = the secret key. Reuses the SAME secret-key alternation as _SECRET_KEY/_SECRET_KEY_WHOLE.
_SECRET_KEY_NAME = (r"""[A-Za-z0-9_.\-]*?(?:password|passwd|secret|token|api[_-]?key|"""
                    r"""access[_-]?key(?:[_-]?id)?|secret[_-]?key|private[_-]?key|client[_-]?secret|"""
                    r"""auth|credential)[A-Za-z0-9_.\-]*|pwd|pat|bearer|dsn""")
_SECRET_BLOCK_SCALAR = re.compile(
    r"""(?im)^(\s*)['"]?(""" + _SECRET_KEY_NAME + r""")['"]?\s*:\s*[|>][+\-0-9]*\s*$""")
# a shell heredoc feeding a secret key: `KEY=$(cat <<EOF` / `KEY="$(cat <<'EOF'`  (the body follows).
_SECRET_HEREDOC = re.compile(
    r"""(?im)^[^\n#]*\b(""" + _SECRET_KEY_NAME + r""")\b[^\n=]*=\s*.*<<[-~]?\s*['"]?\w+['"]?""")

# --- WORLD_WRITABLE: a world-writable file mode (octal mode field or a chmod command) ---------------
# A `mode:` (k8s file mode / ansible) of 0777/0666/777/666 (with optional `0`/`0o` prefix, optional
# quotes), or a `chmod` granting world write: `chmod 777`/`766`-style octals ending in 6/7 for the
# `other` digit, or symbolic `o+w` / `a+w`. Octal modes 0644/0600/0755/0750 (other digit 0/4/5) are SAFE.
_WORLD_WRITABLE_MODE = re.compile(
    r"""(?im)\bmode\s*[:=]\s*['"]?(?:0o?)?(777|666)['"]?\b""")
# chmod granting world write: a 0?(777|666) octal, or a symbolic clause whose target class is `o`/`a`
# (or has no class — bare `+w`, which defaults to all) AND adds `w`.
_WORLD_WRITABLE_CHMOD = re.compile(
    r"""(?imx)\bchmod\b[^\n]*?
        (?: \b0?(?:777|666)\b                       # octal world-writable
          | (?:[oa]|[ugo]*[oa][ugo]*)\+[rx]*w       # o+w / a+w / go+w / ao+rwx (class includes o or a)
          | (?<![ugoa])\+[rx]*w\b )                 # bare +w (no class = "a" by default)
    """)


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


def _find_base64_secrets(text, lines):
    """Find committed k8s Secret `data:` entries whose value is literal base64.

    Scoped strictly to a `kind: Secret` doc. Walks each `data:` block (NOT `stringData:`) and flags any
    `key: <base64-literal>` entry — a `${VAR}`/`<PLACEHOLDER>`/templated value is not base64 so it's
    skipped by `_BASE64_LITERAL`, and `stringData:` is excluded so plaintext isn't double-flagged.
    """
    finds = []
    if not _K8S_SECRET_KIND.search(text):
        return finds
    in_data = False
    data_indent = -1
    for i, raw in enumerate(lines, 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        dh = _K8S_DATA_HEADER.match(raw)
        sdh = _K8S_STRINGDATA_HEADER.match(raw)
        if sdh:                                  # a stringData: block — leave data-scanning mode
            in_data = False
            continue
        if dh:
            in_data = True
            data_indent = len(dh.group(1))
            continue
        if in_data:
            em = _DATA_ENTRY.match(raw)
            indent = len(em.group(1)) if em else 0
            # a sibling/dedent key at or above the data: indent closes the block
            if not em or indent <= data_indent:
                in_data = False
                continue
            value = em.group(3)
            if value and _BASE64_LITERAL.match(value):
                finds.append(("BASE64_SECRET", i,
                              "%s: a committed k8s Secret with literal base64 data — inject via a secret "
                              "store / sealed-secrets / external-secrets, don't commit the manifest"
                              % em.group(2)))
    return finds


def _block_scalar_body_is_literal(lines, start_idx, key_indent):
    """A YAML block scalar opened at lines[start_idx] (0-based) has a non-empty literal body that is NOT
    a single `${VAR}`/placeholder reference. Returns (is_literal, body_end_line_1based).
    """
    body = []
    j = start_idx + 1
    while j < len(lines):
        ln = lines[j]
        if ln.strip() == "":
            body.append("")
            j += 1
            continue
        indent = len(ln) - len(ln.lstrip())
        if indent <= key_indent:                 # dedent ends the block scalar
            break
        body.append(ln.strip())
        j += 1
    nonblank = [b for b in body if b]
    if not nonblank:
        return False, j
    # a body that is a single reference/placeholder line is NOT a literal secret
    if len(nonblank) == 1 and (_REF.match(nonblank[0]) or _URL_PW_REF.match(nonblank[0])):
        return False, j
    return True, j


def _find_heredoc_secrets(text, lines):
    """A secret-ish key assigned a multi-line literal — a YAML block scalar (`key: |` / `key: >`) or a
    shell heredoc (`KEY=$(cat <<EOF`). The block-scalar body is checked against the ref/placeholder
    guard so a `${VAR}` body isn't flagged; a block scalar on a NON-secret key never matches (the key
    alternation is the secret set)."""
    finds = []
    for m in _SECRET_BLOCK_SCALAR.finditer(text):
        start = text.count("\n", 0, m.start())   # 0-based line index of the `key: |` line
        key_indent = len(m.group(1))
        is_lit, _ = _block_scalar_body_is_literal(lines, start, key_indent)
        if is_lit:
            finds.append(("HEREDOC_SECRET", start + 1,
                          "%s assigned a multi-line literal (block scalar) — still a committed plaintext "
                          "secret; source it from a secret ref" % m.group(2)))
    for m in _SECRET_HEREDOC.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        finds.append(("HEREDOC_SECRET", line,
                      "%s assigned a multi-line literal (shell heredoc) — still a committed plaintext "
                      "secret; source it from a secret ref" % m.group(1)))
    return finds


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
        mw = _WORLD_WRITABLE_MODE.search(line)
        if mw:
            finds.append(("WORLD_WRITABLE", i,
                          "world-writable mode %s — anyone can modify; tighten to 0644/0600/0755" % mw.group(1)))
        elif _WORLD_WRITABLE_CHMOD.search(line):
            finds.append(("WORLD_WRITABLE", i,
                          "world-writable chmod (777/666/o+w/a+w) — anyone can modify; tighten to 0644/0600/0755"))

    for m in _WILDCARD_GRANT_MULTILINE.finditer(text):
        # report the line of the bare "*" element, not the opening key
        line = text.count("\n", 0, m.end()) + 1
        finds.append(("WILDCARD_GRANT", line, "wildcard \"*\" grant — over-broad permission (least-privilege)"))

    for m in _UNPINNED.finditer(text):
        finds.append(("UNPINNED_VERSION", text.count("\n", 0, m.start()) + 1, "uses :latest — not reproducible, pin a version/digest"))
    for m in _FROM_NO_TAG.finditer(text):
        finds.append(("UNPINNED_VERSION", text.count("\n", 0, m.start()) + 1, "Dockerfile FROM has no tag/digest — pin it"))

    # committed k8s Secret base64 `data:` material, and secret keys assigned a multi-line literal.
    finds.extend(_find_base64_secrets(text, lines))
    finds.extend(_find_heredoc_secrets(text, lines))

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

    # where a BASE64_SECRET fires on a line, drop a PLAINTEXT_SECRET on the SAME line: a k8s Secret
    # `data:` value is base64 by spec, so the precise diagnosis is BASE64_SECRET (committed Secret
    # material), not "a literal value" — BASE64 is the canonical finding for that line, not a duplicate.
    b64_lines = {ln for k, ln, _ in finds if k == "BASE64_SECRET"}
    if b64_lines:
        finds = [f for f in finds if not (f[0] == "PLAINTEXT_SECRET" and f[1] in b64_lines)]

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

# --- NEW SMELL 4: BASE64_SECRET — a committed k8s Secret with literal base64 `data:` material ---
BAD_BASE64_SECRET = ('apiVersion: v1\nkind: Secret\nmetadata:\n  name: db\ntype: Opaque\n'
                     'data:\n  password: cGFzc3dvcmQ=\n  username: YWRtaW4=\n')
# stringData: is plaintext (covered by PLAINTEXT_SECRET) — must NOT be double-flagged as BASE64
SAFE_BASE64_STRINGDATA = ('apiVersion: v1\nkind: Secret\nmetadata:\n  name: db\n'
                          'stringData:\n  password: hunter2supersecret\n')
# a Secret `data:` whose value is a ${VAR}/placeholder reference — NOT literal base64
SAFE_BASE64_REF = ('apiVersion: v1\nkind: Secret\nmetadata:\n  name: db\n'
                   'data:\n  password: ${SECRET}\n  token: <PLACEHOLDER>\n')
# a NON-Secret doc that merely contains a base64-looking string (a digest / checksum) — out of scope
SAFE_BASE64_NONSECRET = ('apiVersion: apps/v1\nkind: Deployment\nspec:\n  template:\n    spec:\n'
                         '      containers:\n        - name: web\n'
                         '          image: web@sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b\n'
                         '          resources:\n            limits: { cpu: "1" }\n')

# --- NEW SMELL 5: HEREDOC_SECRET — a secret key assigned a multi-line literal (block scalar / heredoc) ---
BAD_HEREDOC_BLOCK_SCALAR = ('tls:\n  private_key: |\n    -----BEGIN RSA PRIVATE KEY-----\n'
                            '    MIIEowIBAAKCAQEA1234567890abcdef\n    -----END RSA PRIVATE KEY-----\n')
BAD_HEREDOC_SHELL = 'export DB_PASSWORD=$(cat <<EOF\nrealsecretvalue\nEOF\n)\n'
# a block scalar on a NON-secret key — must NOT be flagged
SAFE_HEREDOC_NONSECRET = 'config:\n  description: |\n    some multi-line\n    descriptive text\n'
# a block-scalar body that is a single ${VAR} reference — must NOT be flagged
SAFE_HEREDOC_REF = 'tls:\n  private_key: |\n    ${TLS_PRIVATE_KEY}\n'

# --- NEW SMELL 6: WORLD_WRITABLE — an octal world-writable mode or a chmod 777/666/o+w/a+w ---
BAD_WW_MODE_0777 = 'files:\n  - path: /data/app.conf\n    mode: 0777\n'
BAD_WW_CHMOD_777 = 'RUN chmod -R 777 /data\n'
BAD_WW_MODE_QUOTED_0666 = 'volume:\n  mode: "0666"\n'
BAD_WW_CHMOD_OW = 'RUN chmod o+w /var/log/app.log\n'
# safe modes (other digit 0/4/5) and a restrictive chmod must NOT be flagged
SAFE_WW_MODE_0644 = 'files:\n  - path: /etc/app.conf\n    mode: 0644\n'
SAFE_WW_MODE_0600 = 'files:\n  - path: /etc/secret.conf\n    mode: 0600\n'
SAFE_WW_MODE_0755 = 'files:\n  - path: /usr/bin/app\n    mode: 0755\n'
SAFE_WW_CHMOD_750 = 'RUN chmod 750 /opt/app\n'


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
        (BAD_BASE64_SECRET, "BASE64_SECRET"),              # NEW4: committed k8s Secret literal base64 data:
        (BAD_HEREDOC_BLOCK_SCALAR, "HEREDOC_SECRET"),      # NEW5: private_key: | multi-line literal
        (BAD_HEREDOC_SHELL, "HEREDOC_SECRET"),             # NEW5: KEY=$(cat <<EOF ...)
        (BAD_WW_MODE_0777, "WORLD_WRITABLE"),              # NEW6: mode: 0777
        (BAD_WW_CHMOD_777, "WORLD_WRITABLE"),              # NEW6: chmod -R 777
        (BAD_WW_MODE_QUOTED_0666, "WORLD_WRITABLE"),       # NEW6: mode: "0666"
        (BAD_WW_CHMOD_OW, "WORLD_WRITABLE"),               # NEW6: chmod o+w
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
    # NEW4 false-positive guards: stringData (plaintext, not BASE64), a ${VAR}/placeholder data value,
    # and a non-Secret doc with a base64-looking digest must NOT trip BASE64_SECRET
    for safe in (SAFE_BASE64_STRINGDATA, SAFE_BASE64_REF, SAFE_BASE64_NONSECRET):
        if "BASE64_SECRET" in kinds(safe):
            errs.append("false positive: flagged a stringData/ref/non-Secret as BASE64_SECRET: %s" % lint_text(safe))
    # the stringData fixture is plaintext base64-free text — but it IS a literal secret key, so it should
    # still be PLAINTEXT_SECRET (proving BASE64 doesn't steal the finding, and plaintext still fires)
    if "PLAINTEXT_SECRET" not in kinds(SAFE_BASE64_STRINGDATA):
        errs.append("stringData literal password not caught as PLAINTEXT_SECRET (BASE64 must not mask it)")
    # NEW5 false-positive guards: a block scalar on a NON-secret key, and a block-scalar body that is a
    # single ${VAR} reference must NOT trip HEREDOC_SECRET
    for safe in (SAFE_HEREDOC_NONSECRET, SAFE_HEREDOC_REF):
        if "HEREDOC_SECRET" in kinds(safe):
            errs.append("false positive: flagged a non-secret / ${VAR} block scalar as HEREDOC_SECRET: %s" % lint_text(safe))
    # NEW6 false-positive guards: octal modes with other-digit 0/4/5 and a restrictive chmod 750 must NOT
    # trip WORLD_WRITABLE
    for safe in (SAFE_WW_MODE_0644, SAFE_WW_MODE_0600, SAFE_WW_MODE_0755, SAFE_WW_CHMOD_750):
        if "WORLD_WRITABLE" in kinds(safe):
            errs.append("false positive: flagged a non-world-writable mode/chmod as WORLD_WRITABLE: %s" % lint_text(safe))
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

    errs.extend(_selftest_allowlist())
    errs.extend(_selftest_json())
    return errs


def _selftest_json():
    """The --json report path: run a dirty + a clean fixture through the report builder + the stdout
    path, json.loads it back, and assert the shared schema. Also exercises allowlist suppression
    composing with --json (a suppressed finding is NOT in `findings`, its count rides in `summary`)."""
    import io
    import contextlib
    import tempfile
    errs = []

    def _capture(target, ignore_path=None):
        """Run main(['--json', ...]) over a real target, capturing stdout, and json.loads it."""
        argv = ["--json"]
        if ignore_path is not None:
            argv += ["--ignore", ignore_path]
        argv += [target]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            rc = main(argv)
        return rc, out.getvalue()

    def _assert_schema(rep, want_ok, want_nonempty, label):
        if not isinstance(rep, dict):
            errs.append("--json %s: report is not a dict" % label); return
        if rep.get("tool") != "config-lint":
            errs.append("--json %s: tool=%r, want 'config-lint'" % (label, rep.get("tool")))
        if rep.get("ok") is not want_ok:
            errs.append("--json %s: ok=%r, want %r" % (label, rep.get("ok"), want_ok))
        if not isinstance(rep.get("summary"), str) or not rep["summary"]:
            errs.append("--json %s: summary missing/empty" % label)
        f = rep.get("findings")
        if not isinstance(f, list):
            errs.append("--json %s: findings not a list" % label); return
        if want_nonempty and not f:
            errs.append("--json %s: findings should be non-empty" % label)
        if not want_nonempty and f:
            errs.append("--json %s: findings should be [] on clean input, got %s" % (label, f))
        for fd in f:
            if not isinstance(fd, dict) or any(k not in fd for k in ("kind", "severity", "location", "message")):
                errs.append("--json %s: a finding is missing a required key: %r" % (label, fd))
            elif fd["severity"] not in ("fail", "warn", "advisory"):
                errs.append("--json %s: bad severity %r" % (label, fd["severity"]))

    with tempfile.TemporaryDirectory() as d:
        # dirty: BAD_SECRET ⇒ a PLAINTEXT_SECRET (a security smell ⇒ severity fail), ok false, exit 1.
        dirty = os.path.join(d, "secrets.yaml")
        with open(dirty, "w", encoding="utf-8") as fh:
            fh.write(BAD_SECRET)
        rc, out = _capture(dirty)
        try:
            rep = json.loads(out)
        except ValueError as e:
            errs.append("--json dirty: stdout is not valid JSON (%s): %r" % (e, out)); rep = {}
        _assert_schema(rep, False, True, "dirty")
        if rc != 1:
            errs.append("--json dirty: exit code should match human mode (1), got %d" % rc)
        if rep and not any(fd["kind"] == "PLAINTEXT_SECRET" and fd["severity"] == "fail"
                           for fd in rep.get("findings", [])):
            errs.append("--json dirty: expected a PLAINTEXT_SECRET fail finding, got %s"
                        % rep.get("findings"))

        # clean: CLEAN ⇒ no findings, ok true, exit 0, findings [].
        clean = os.path.join(d, "clean.yaml")
        with open(clean, "w", encoding="utf-8") as fh:
            fh.write(CLEAN)
        rc, out = _capture(clean)
        try:
            rep = json.loads(out)
        except ValueError as e:
            errs.append("--json clean: stdout is not valid JSON (%s): %r" % (e, out)); rep = {}
        _assert_schema(rep, True, False, "clean")
        if rc != 0:
            errs.append("--json clean: exit code should match human mode (0), got %d" % rc)

        # advisory severity: a `:latest` image (UNPINNED_VERSION) maps to severity `warn`, not `fail`.
        latest = os.path.join(d, "Dockerfile")
        with open(latest, "w", encoding="utf-8") as fh:
            fh.write(BAD_LATEST)
        rc, out = _capture(latest)
        rep = json.loads(out)
        sev = {fd["kind"]: fd["severity"] for fd in rep["findings"]}
        if sev.get("UNPINNED_VERSION") != "warn":
            errs.append("--json advisory: UNPINNED_VERSION should map to severity 'warn', got %r"
                        % sev.get("UNPINNED_VERSION"))

        # composes with --ignore: an allowlist suppressing the only finding ⇒ ok true, findings [],
        # exit 0, and the suppressed COUNT appears in `summary` (not in `findings`).
        ig = os.path.join(d, "allow.txt")
        with open(ig, "w", encoding="utf-8") as fh:
            fh.write("PLAINTEXT_SECRET\n")
        rc, out = _capture(dirty, ignore_path=ig)
        rep = json.loads(out)
        _assert_schema(rep, True, False, "suppressed")
        if rc != 0:
            errs.append("--json suppressed: exit should be 0 when the only finding is suppressed, got %d" % rc)
        if "suppressed by allowlist" not in rep.get("summary", ""):
            errs.append("--json suppressed: the suppressed count must appear in summary, got %r"
                        % rep.get("summary"))
    return errs


# --- ALLOWLIST selftest: a two-finding config + an allowlist suppressing exactly one ---------------
# `infra.yaml`: two distinct findings on two distinct lines.
#   line 2: UNPINNED_VERSION (image: nginx:latest)
#   line 4: OPEN_NETWORK     (0.0.0.0/0)
ALLOW_TWO_FINDINGS = 'svc:\n  image: nginx:latest\nnet:\n  cidr: "0.0.0.0/0"\n'


def _run(target, ignore_path=None, show_suppressed=False):
    """Invoke main() over a real temp tree, capturing stdout/stderr + the exit code."""
    import io
    import contextlib
    argv = []
    if ignore_path is not None:
        argv += ["--ignore", ignore_path]
    if show_suppressed:
        argv += ["--show-suppressed"]
    argv += [target]
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = main(argv)
    return rc, out.getvalue(), err.getvalue()


def _selftest_allowlist():
    import tempfile
    errs = []

    # The config has 2 distinct findings; confirm lint_text agrees before we test suppression.
    base_kinds = {k for k, _, _ in lint_text(ALLOW_TWO_FINDINGS)}
    if base_kinds != {"UNPINNED_VERSION", "OPEN_NETWORK"}:
        errs.append("allowlist fixture setup wrong: expected 2 findings, got %s" % sorted(base_kinds))
        return errs

    with tempfile.TemporaryDirectory() as d:
        cfg = os.path.join(d, "infra.yaml")
        with open(cfg, "w", encoding="utf-8") as fh:
            fh.write(ALLOW_TWO_FINDINGS)

        # (d-regression) NO allowlist present ⇒ both findings reported, FAIL (rc=1), no suppression noise.
        rc, out, err = _run(cfg)
        if rc != 1:
            errs.append("allowlist regression: no-allowlist run should FAIL (rc=1), got rc=%d" % rc)
        if "UNPINNED_VERSION" not in out or "OPEN_NETWORK" not in out:
            errs.append("allowlist regression: no-allowlist run should report both findings; out=%r" % out)
        if "suppressed" in err or "allowlist" in err:
            errs.append("allowlist regression: no-allowlist run emitted allowlist noise: %r" % err)

        # (a) an allowlist suppressing exactly ONE kind ⇒ only the other is reported; exit reflects only
        #     the unsuppressed one (still FAIL); the suppressed count is surfaced to stderr.
        ig = os.path.join(d, "allow.txt")
        with open(ig, "w", encoding="utf-8") as fh:
            fh.write("# accepted: this is a public ALB, reviewed 2026-06\nOPEN_NETWORK\n")
        rc, out, err = _run(cfg, ignore_path=ig)
        if rc != 1:
            errs.append("allowlist (a): one finding remains ⇒ should FAIL (rc=1), got rc=%d" % rc)
        if "OPEN_NETWORK" in out:
            errs.append("allowlist (a): suppressed OPEN_NETWORK still printed: %r" % out)
        if "UNPINNED_VERSION" not in out:
            errs.append("allowlist (a): unsuppressed UNPINNED_VERSION missing from output: %r" % out)
        if "1 finding(s) suppressed by allowlist" not in err:
            errs.append("allowlist (a): suppressed-count summary missing from stderr: %r" % err)

        # suppress BOTH ⇒ clean OK (rc=0), the suppressed count noted on the OK line + stderr.
        ig2 = os.path.join(d, "allow_both.txt")
        with open(ig2, "w", encoding="utf-8") as fh:
            fh.write("OPEN_NETWORK\nUNPINNED_VERSION\n")
        rc, out, err = _run(cfg, ignore_path=ig2)
        if rc != 0:
            errs.append("allowlist: suppressing all findings ⇒ should be OK (rc=0), got rc=%d (out=%r err=%r)"
                        % (rc, out, err))
        if "2 finding(s) suppressed by allowlist" not in err:
            errs.append("allowlist: both-suppressed count missing from stderr: %r" % err)

        # (b) a `KIND:file:line` entry suppresses PRECISELY one (the OPEN_NETWORK at its exact line),
        #     while a `KIND` line would suppress all of that kind. Here only line 4 is targeted.
        ig3 = os.path.join(d, "allow_precise.txt")
        with open(ig3, "w", encoding="utf-8") as fh:
            fh.write("OPEN_NETWORK:infra.yaml:4\n")
        rc, out, err = _run(cfg, ignore_path=ig3)
        if "OPEN_NETWORK" in out:
            errs.append("allowlist (b): KIND:file:line did not suppress the targeted finding: %r" % out)
        if "1 finding(s) suppressed by allowlist" not in err:
            errs.append("allowlist (b): precise-entry suppressed count missing: %r" % err)
        # the SAME entry pointed at the WRONG line must NOT suppress (precision guard) — and is stale.
        ig4 = os.path.join(d, "allow_wrongline.txt")
        with open(ig4, "w", encoding="utf-8") as fh:
            fh.write("OPEN_NETWORK:infra.yaml:99\n")
        rc, out, err = _run(cfg, ignore_path=ig4)
        if "OPEN_NETWORK" not in out:
            errs.append("allowlist (b): wrong-line entry wrongly suppressed the finding: %r" % out)
        if "stale allowlist entry" not in err:
            errs.append("allowlist (b): wrong-line entry should be flagged stale: %r" % err)

        # the WRONG file path must NOT suppress (path precision guard).
        ig5 = os.path.join(d, "allow_wrongfile.txt")
        with open(ig5, "w", encoding="utf-8") as fh:
            fh.write("OPEN_NETWORK:other.yaml\n")
        rc, out, err = _run(cfg, ignore_path=ig5)
        if "OPEN_NETWORK" not in out:
            errs.append("allowlist: wrong-file path entry wrongly suppressed the finding: %r" % out)
        if "stale allowlist entry" not in err:
            errs.append("allowlist: wrong-file entry should be flagged stale: %r" % err)

        # (c) a STALE entry (a kind that doesn't occur here) ⇒ WARN, baseline doesn't rot.
        ig6 = os.path.join(d, "allow_stale.txt")
        with open(ig6, "w", encoding="utf-8") as fh:
            fh.write("OPEN_NETWORK\nWORLD_WRITABLE\n")   # WORLD_WRITABLE matches nothing here
        rc, out, err = _run(cfg, ignore_path=ig6)
        if "stale allowlist entry 'WORLD_WRITABLE'" not in err:
            errs.append("allowlist (c): stale entry WORLD_WRITABLE not warned: %r" % err)
        if "stale allowlist entry 'OPEN_NETWORK'" in err:
            errs.append("allowlist (c): a USED entry (OPEN_NETWORK) wrongly flagged stale: %r" % err)

        # a MALFORMED line ⇒ WARN + skip, never crash; the rest of the allowlist still applies.
        ig7 = os.path.join(d, "allow_malformed.txt")
        with open(ig7, "w", encoding="utf-8") as fh:
            fh.write("not a valid kind!!!\nOPEN_NETWORK\n")
        rc, out, err = _run(cfg, ignore_path=ig7)
        if "malformed allowlist line" not in err:
            errs.append("allowlist: malformed line not warned: %r" % err)
        if "OPEN_NETWORK" in out:
            errs.append("allowlist: a malformed line broke the valid entry below it: %r" % out)

        # --show-suppressed prints the dropped finding (prefixed SUPPRESSED) for transparency.
        rc, out, err = _run(cfg, ignore_path=ig, show_suppressed=True)
        if "SUPPRESSED" not in out or "OPEN_NETWORK" not in out:
            errs.append("allowlist: --show-suppressed did not print the dropped finding: %r" % out)

        # AUTO-DISCOVERY: a `.config-lint-ignore` dropped in the scanned dir is picked up without --ignore.
        disc = os.path.join(d, IGNORE_FILENAME)
        with open(disc, "w", encoding="utf-8") as fh:
            fh.write("OPEN_NETWORK\n")
        rc, out, err = _run(cfg)
        if "OPEN_NETWORK" in out:
            errs.append("allowlist: auto-discovered .config-lint-ignore not applied: %r" % out)
        if "1 finding(s) suppressed by allowlist" not in err:
            errs.append("allowlist: auto-discovery did not surface the suppressed count: %r" % err)
        os.remove(disc)

    # path-suffix matching unit checks (segment-boundary precision).
    if not _path_suffix_match("app/db.yaml", "svc/app/db.yaml"):
        errs.append("path-suffix: 'app/db.yaml' should match 'svc/app/db.yaml'")
    if _path_suffix_match("app/db.yaml", "myapp/db.yaml"):
        errs.append("path-suffix: 'app/db.yaml' must NOT match 'myapp/db.yaml' (segment boundary)")
    if not _path_suffix_match("db.yaml", "a/b/c/db.yaml"):
        errs.append("path-suffix: bare 'db.yaml' should match any '…/db.yaml'")
    if _path_suffix_match("svc/app/db.yaml", "app/db.yaml"):
        errs.append("path-suffix: an over-long entry must NOT match a shorter finding path")
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


# --- ALLOWLIST / BASELINE (opt-in; absent ⇒ behavior byte-identical to no allowlist) ----------------
IGNORE_FILENAME = ".config-lint-ignore"


def _path_suffix_match(entry_path, finding_path):
    """True if `entry_path` matches `finding_path` as a path SUFFIX on segment boundaries.

    `app/db.yaml` matches `svc/app/db.yaml` but NOT `myapp/db.yaml`; a bare `db.yaml` matches any
    `…/db.yaml`. Both sides are normalized to `/` separators so a Windows-style entry still matches.
    Comparison is exact when the entry has as many segments as the finding (a full-path entry).
    """
    def norm(p):
        return [seg for seg in p.replace("\\", "/").strip("/").split("/") if seg]
    e = norm(entry_path)
    f = norm(finding_path)
    if not e or len(e) > len(f):
        return False
    return f[len(f) - len(e):] == e


class _Entry:
    """One parsed allowlist entry. `matched` flips True the first time it suppresses a finding."""
    __slots__ = ("raw", "kind", "path", "line", "matched")

    def __init__(self, raw, kind, path, line):
        self.raw = raw
        self.kind = kind
        self.path = path        # None ⇒ match any file
        self.line = line        # None ⇒ match any line
        self.matched = False

    def matches(self, fkind, fline, fpath):
        if fkind != self.kind:                       # KIND must match EXACTLY (case-sensitive)
            return False
        if self.line is not None and fline != self.line:
            return False
        if self.path is not None and not _path_suffix_match(self.path, fpath or ""):
            return False
        return True


class Allowlist:
    """A parsed `.config-lint-ignore`. `parse_lines` builds it; `suppress(finding, path)` tells whether
    a finding is allowlisted (and marks the matching entry); `warnings()` returns the malformed-line and
    stale-entry WARNs. An empty allowlist (no entries) suppresses nothing — the no-allowlist path."""

    def __init__(self):
        self.entries = []
        self._malformed = []     # (lineno, raw) of lines that didn't parse

    @classmethod
    def parse_lines(cls, lines):
        al = cls()
        for n, raw in enumerate(lines, 1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            # split into at most KIND : PATH : LINE — the path may itself contain ':' only on the LINE
            # tail, so split from the RIGHT for the optional trailing numeric line.
            kind, path, lineno = None, None, None
            parts = line.split(":")
            kind = parts[0].strip()
            if not kind or not re.match(r"^[A-Z][A-Z0-9_]*$", kind):
                al._malformed.append((n, raw.rstrip("\n")))
                continue
            rest = parts[1:]
            if rest:
                # if the final segment is a bare integer, it's the LINE; the rest (rejoined) is the path
                if len(rest) >= 1 and re.match(r"^\d+$", rest[-1].strip()):
                    lineno = int(rest[-1].strip())
                    path = ":".join(rest[:-1]).strip() or None
                    if path is None:
                        # `KIND::LINE` or `KIND:LINE` with no path is malformed — a line needs a file
                        al._malformed.append((n, raw.rstrip("\n")))
                        continue
                else:
                    path = ":".join(rest).strip() or None
                    if path is None:
                        al._malformed.append((n, raw.rstrip("\n")))
                        continue
            al.entries.append(_Entry(raw.rstrip("\n"), kind, path, lineno))
        return al

    @classmethod
    def from_file(cls, fp):
        with open(fp, encoding="utf-8") as fh:
            return cls.parse_lines(fh.read().splitlines())

    def is_empty(self):
        return not self.entries and not self._malformed

    def suppress(self, finding, path):
        """True if `finding` (kind, line, detail) at `path` is allowlisted — marks the matching entry."""
        kind, line = finding[0], finding[1]
        hit = False
        for e in self.entries:
            if e.matches(kind, line, path):
                e.matched = True
                hit = True                            # mark ALL matching entries (don't short-circuit
                                                       # — a broad KIND entry and a precise one can co-cover)
        return hit

    def warnings(self):
        warns = []
        for n, raw in self._malformed:
            warns.append("WARN: malformed allowlist line %d: %r (skipped)" % (n, raw))
        for e in self.entries:
            if not e.matched:
                warns.append("WARN: stale allowlist entry %r (matched nothing)" % e.raw)
        return warns


def _discover_ignore_file(scan_path):
    """Auto-discover a `.config-lint-ignore`: prefer one in the scanned dir (or the file's dir), then
    fall back to the CWD. Returns a path or None. An explicit `--ignore` always wins over this."""
    candidates = []
    base = scan_path if os.path.isdir(scan_path) else os.path.dirname(os.path.abspath(scan_path))
    if base:
        candidates.append(os.path.join(base, IGNORE_FILENAME))
    candidates.append(os.path.join(os.getcwd(), IGNORE_FILENAME))
    seen = set()
    for c in candidates:
        rc = os.path.realpath(c)
        if rc in seen:
            continue
        seen.add(rc)
        if os.path.isfile(c):
            return c
    return None


# --- machine-readable report (--json) ----------------------------------------------------------
# ONE shared schema across every lint bin: {tool, ok, summary, findings:[{kind, severity, location,
# message}]}. severity = `fail` for the security smells, `warn` for the advisory smells + stale-allowlist
# WARNs. A finding suppressed by the allowlist is NOT in `findings` (as in human mode); its count rides
# in `summary`. `ok` is true iff no un-suppressed finding (the exact exit-0 condition of human mode).
_ADVISORY_KINDS = frozenset({"UNPINNED_VERSION", "NO_RESOURCE_LIMITS"})


def _severity_for(kind):
    """`warn` for the advisory (reproducibility / coarse) smells, `fail` for the security smells."""
    return "warn" if kind in _ADVISORY_KINDS else "fail"


def build_config_report(reported, suppressed, stale_warns):
    """Build the JSON report. `reported` is the list of (kind, line, detail) findings that were NOT
    suppressed (the ones human mode prints); `suppressed` is the count dropped by the allowlist;
    `stale_warns` is the list of stale/malformed allowlist WARN strings (each a `warn` finding with a
    null location). `ok` is true iff there is no un-suppressed finding — matching the human exit code."""
    out = []
    for kind, line, detail in reported:
        out.append({"kind": kind, "severity": _severity_for(kind),
                    "location": "line:%d" % line, "message": detail})
    for w in stale_warns:
        out.append({"kind": "STALE_ALLOWLIST", "severity": "warn", "location": None, "message": w})
    ok = not reported          # advisory allowlist WARNs do not block; only real findings do
    smell_n = len(reported)
    if smell_n:
        summary = "%d safety smell(s)" % smell_n
    else:
        summary = "no safety smells"
    if suppressed:
        summary += " (%d suppressed by allowlist)" % suppressed
    if stale_warns:
        summary += " (%d stale/malformed allowlist entr%s)" % (len(stale_warns),
                                                               "y" if len(stale_warns) == 1 else "ies")
    return {"tool": "config-lint", "ok": ok, "summary": summary, "findings": out}


def _run_json(target, allow):
    """`--json` mode: scan `target`, apply `allow` (an Allowlist or None), emit ONE report object to
    stdout, and return the human exit code (1 if any un-suppressed finding, else 0). Composes with the
    resolved allowlist exactly as the human path does — suppressed findings are dropped, not reported."""
    reported, suppressed = [], 0
    for fp in _iter_files(target):
        try:
            text = open(fp, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for kind, line, detail in lint_text(text, fp):
            if allow is not None and allow.suppress((kind, line, detail), fp):
                suppressed += 1
                continue
            reported.append((kind, line, detail))
    stale_warns = allow.warnings() if allow is not None else []
    rep = build_config_report(reported, suppressed, stale_warns)
    print(json.dumps(rep, indent=2))
    return 0 if rep["ok"] else 1


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("config-lint: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("config-lint: OK — 10 safety smells (plaintext + URL-embedded + base64 + heredoc secrets, "
              "unpinned, open-net, wildcard grant, no-limits, k8s-unsafe, world-writable) caught; "
              "reference/placeholder/whole-key/stringData/non-Secret/non-secret-key + non-k8s + "
              "safe-mode false-positive guards + api.Dockerfile scan + allowlist suppress/stale/"
              "no-allowlist-regression verified")
        return 0

    # parse the opt-in allowlist flags (additive — no flag + no discovered file ⇒ legacy behavior)
    ignore_path = None
    show_suppressed = False
    as_json = False
    rest = []
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--ignore":
            if i + 1 >= len(argv):
                sys.stderr.write("config-lint: --ignore needs a file argument\n")
                return 2
            ignore_path = argv[i + 1]
            i += 2
            continue
        if a.startswith("--ignore="):
            ignore_path = a[len("--ignore="):]
            i += 1
            continue
        if a == "--show-suppressed":
            show_suppressed = True
            i += 1
            continue
        if a == "--json":           # parse-anywhere reporting flag; composes with --ignore
            as_json = True
            i += 1
            continue
        rest.append(a)
        i += 1
    if not rest:
        sys.stderr.write("config-lint: no path to scan\n")
        return 2
    target = rest[0]

    # resolve the allowlist: explicit --ignore wins; otherwise auto-discover .config-lint-ignore.
    allow = None
    allow_source = None
    if ignore_path is not None:
        if not os.path.isfile(ignore_path):
            sys.stderr.write("config-lint: --ignore file not found: %s\n" % ignore_path)
            return 2
        allow = Allowlist.from_file(ignore_path)
        allow_source = ignore_path
    else:
        discovered = _discover_ignore_file(target)
        if discovered is not None:
            allow = Allowlist.from_file(discovered)
            allow_source = discovered

    # --json: emit the shared report object (composes with the resolved allowlist) and exit as human mode.
    if as_json:
        return _run_json(target, allow)

    total, n, suppressed = 0, 0, 0
    for fp in _iter_files(target):
        try:
            text = open(fp, encoding="utf-8", errors="replace").read()
        except OSError as e:
            print("  ⚠ %s: unreadable (%s)" % (fp, e))
            continue
        n += 1
        for kind, line, detail in lint_text(text, fp):
            if allow is not None and allow.suppress((kind, line, detail), fp):
                suppressed += 1
                if show_suppressed:
                    print("  SUPPRESSED %s:%s  %-18s %s" % (os.path.relpath(fp), line, kind, detail))
                continue
            total += 1
            print("  %s:%s  %-18s %s" % (os.path.relpath(fp), line, kind, detail))

    # transparency: surface what the allowlist dropped, and any stale/malformed entries (no silent caps)
    if allow is not None:
        if suppressed:
            sys.stderr.write("config-lint: %d finding(s) suppressed by allowlist (%s)\n"
                             % (suppressed, os.path.relpath(allow_source)))
        for w in allow.warnings():
            sys.stderr.write("config-lint: %s\n" % w)

    if total:
        sys.stderr.write("config-lint: FAIL — %d safety smell(s) across %d file(s)\n" % (total, n))
        return 1
    print("config-lint: OK — no safety smells in %d file(s)%s"
          % (n, (" (%d suppressed by allowlist)" % suppressed) if suppressed else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
