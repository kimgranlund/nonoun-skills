#!/usr/bin/env python3
"""model-smells.py — the type-decomposer model-smell linter. Self-contained (stdlib only).

Static scan of a type definition for the shapes that let illegal states slip through — the
MODEL-axis (A3/A4) smells the instance check can't see until you write the counterexample.
Advisory signals, not proof: each one points at a place the state space is wider than the domain.

Reads three dialects, dispatched by file extension (a dir scan picks up all three):
  .json / .schema.json   JSON Schema      (walked as a schema tree)
  .ts / .tsx             TypeScript       (regex + brace-matching over type/interface blocks)
  .py / .pyi             Python            (ast over TypedDict / @dataclass class bodies)

The same five finding KINDS and message style are used for every dialect — the smells
(boolean-blindness / optional-soup / primitive-obsession / open-record / stringly-typed-enum) are
language-agnostic.

Smells:
  BOOLEAN_BLINDNESS   >= 2 boolean-ish fields on one object/type — a real boolean, an enum:[true,
                      false] / a `true|false` union, or a const/`bool` all count — usually a
                      mutually-exclusive state that should be a oneOf / discriminated union / enum
                      (2 booleans = 4 states, often 1-2 of them illegal)
  OPTIONAL_SOUP       many properties, <=1 required, no oneOf/anyOf/discriminant grouping — most
                      field combinations are representable, including the illegal ones
  PRIMITIVE_OBSESSION a field named like a constrained type (email/url/id/uuid/date/...) typed as a
                      bare primitive (string/number/str/int/float) with no format/pattern/enum,
                      brand, or literal union — an Email is not a String
  OPEN_RECORD         an object/type with fields but no closure (no additionalProperties:false; a
                      TS index signature `[k:string]:...`) — admits illegal extra fields
  STRINGLY_TYPED_ENUM a string/str field whose description or adjacent comment enumerates fixed
                      values but carries no enum / string-literal union / Literal[...]

  python3 bin/model-smells.py selftest
  python3 bin/model-smells.py <schema.json | types.ts | types.py | dir>

Python 3.8+.
"""
import ast
import json
import os
import re
import sys

# property-name hints that a bare string is really a constrained type
CONSTRAINED = re.compile(
    r"(?:^|_)(email|e_mail|url|uri|href|id|uuid|guid|slug|date|datetime|time|timestamp|"
    r"phone|tel|zip|postal|country|currency|color|colour|ip|cidr|mac|sha|hash|version|semver)s?$",
    re.I)
ENUM_HINT = re.compile(r"\b(one of|either|must be one|values?:|e\.g\.)\b|(\w+\s*\|\s*\w+)", re.I)


def _constrained_name(name):
    """True if a field NAME denotes a constrained type. Handles snake_case (`user_id`) AND camelCase
    (`userId`, `homeUrl`, `createdDate`) — the camelCase norm in TS/Python — by snake-normalizing
    first, so `userId`->`user_id` matches while a plain lowercase `grid`/`valid`/`android` does not."""
    snake = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", str(name)).lower()
    return bool(CONSTRAINED.search(str(name)) or CONSTRAINED.search(snake))


def _types(schema):
    t = schema.get("type")
    if t is None:
        return set()
    return set(t) if isinstance(t, list) else {t}


def _is_bare_string(schema):
    return _types(schema) == {"string"} and not any(
        k in schema for k in ("format", "pattern", "enum", "const"))


def _is_boolish(schema):
    """A field that is a boolean in disguise: a real boolean, OR an enum/const over the two
    boolean values (e.g. enum:[true,false]) — same 2-state shape, same blindness when paired."""
    if not isinstance(schema, dict):
        return False
    if "boolean" in _types(schema):
        return True
    enum = schema.get("enum")
    if isinstance(enum, list) and enum and set(map(type, enum)) == {bool}:
        return True
    if isinstance(schema.get("const"), bool):
        return True
    return False


def walk(schema, path, findings):
    if not isinstance(schema, dict):
        return
    if "object" in _types(schema) or "properties" in schema:
        props = schema.get("properties", {}) or {}
        required = set(schema.get("required", []) or [])
        has_choice = any(k in schema for k in ("oneOf", "anyOf"))

        bools = [k for k, s in props.items() if _is_boolish(s)]
        if len(bools) >= 2:
            findings.append(("BOOLEAN_BLINDNESS", path,
                             "%d boolean fields (%s) — model the exclusive state as a oneOf/enum"
                             % (len(bools), ", ".join(sorted(bools)))))
        if len(props) >= 4 and len(required) <= 1 and not has_choice:
            findings.append(("OPTIONAL_SOUP", path,
                             "%d properties, %d required, no oneOf — most field combinations are "
                             "representable" % (len(props), len(required))))
        if props and schema.get("additionalProperties", True) is not False:
            findings.append(("OPEN_RECORD", path,
                             "object with properties but additionalProperties is not false — extra "
                             "fields are representable"))
        for k, s in props.items():
            if isinstance(s, dict):
                if _is_bare_string(s) and _constrained_name(k):
                    findings.append(("PRIMITIVE_OBSESSION", "%s.%s" % (path, k),
                                     "'%s' is a bare string — give it a format/pattern/enum" % k))
                if "string" in _types(s) and "enum" not in s and ENUM_HINT.search(str(s.get("description", ""))):
                    findings.append(("STRINGLY_TYPED_ENUM", "%s.%s" % (path, k),
                                     "'%s' description lists fixed values but has no enum" % k))
                walk(s, "%s.%s" % (path, k), findings)
    if "items" in schema:
        walk(schema["items"], path + "[]", findings)
    for comb in ("oneOf", "anyOf", "allOf"):
        for i, sub in enumerate(schema.get(comb, []) or []):
            walk(sub, "%s/%s[%d]" % (path, comb, i), findings)


def smells(schema):
    findings = []
    walk(schema, "$", findings)
    return findings


# --- TypeScript path (regex + brace-matching; no stdlib TS parser) ----------------------------
# Bare primitives a constrained-name field should NOT be (mirrors _is_bare_string for JSON Schema).
_TS_BARE_PRIM = re.compile(r"^(string|number)$")
# A string-literal union ('a' | 'b' | "c") — the GOOD form of a stringly-typed enum, must NOT flag.
_TS_LIT_UNION = re.compile(r"""['"][^'"]*['"]\s*\|""")
# A boolean-in-disguise union: true|false (any order, ignoring spaces).
_TS_BOOL_UNION = re.compile(r"^(?:true|false)(?:\s*\|\s*(?:true|false))+$")
# A branded primitive: `string & { __brand: ... }` / `number & { _tag: ... }` — nominal, not bare.
_TS_BRANDED = re.compile(r"^(?:string|number)\s*&\s*\{")
# Header of a `type Name = {` / `interface Name {` block (export/declare tolerated).
_TS_BLOCK = re.compile(
    r"(?:export\s+)?(?:declare\s+)?(type)\s+(\w+)\s*=\s*\{|"
    r"(?:export\s+)?(?:declare\s+)?(interface)\s+(\w+)\b[^{]*\{")
# An index signature => open record. `[key: string]: Foo` / `[k: number]: Bar`.
_TS_INDEX_SIG = re.compile(r"\[\s*\w+\s*:\s*(?:string|number|symbol)\s*\]\s*:")


def _ts_match_brace(text, open_idx):
    """Return the index just past the `}` that closes the `{` at open_idx (brace-matched, with
    string/comment awareness kept simple — types rarely embed stray braces in strings)."""
    depth = 0
    i = open_idx
    n = len(text)
    while i < n:
        c = text[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return n


def _ts_blocks(text):
    """Yield (kind, name, body) for each top-level type/interface object block."""
    for m in _TS_BLOCK.finditer(text):
        kind = m.group(1) or m.group(3)
        name = m.group(2) or m.group(4)
        open_idx = text.index("{", m.start())
        end = _ts_match_brace(text, open_idx)
        body = text[open_idx + 1:end - 1]
        yield kind, name, body


def _ts_fields(body):
    """Parse a block body into (name, optional, type_str, trailing_comment) tuples.

    Brace-matches nested object types so a field's `{...}` value stays on one logical field, and
    keeps the rest-of-line `//` comment with the field it annotates."""
    fields = []
    i = 0
    n = len(body)
    while i < n:
        # find a field-name token at this scan position
        m = re.match(r"\s*(\w+)\s*(\??)\s*:\s*", body[i:])
        if not m:
            # advance to next newline to skip a non-field line (index sig, comment, blank)
            nl = body.find("\n", i)
            i = n if nl < 0 else nl + 1
            continue
        name = m.group(1)
        optional = m.group(2) == "?"
        j = i + m.end()
        # consume the type, brace-matching nested object types, stopping at a top-level ; , or newline
        depth = 0
        k = j
        while k < n:
            c = body[k]
            if c in "{[(<":
                depth += 1
            elif c in "}])>":
                depth -= 1
            elif depth == 0 and (c == ";" or c == "," or c == "\n"):
                break
            k += 1
        type_str = body[j:k].strip()
        # trailing // comment on the same line (after the terminator)
        line_end = body.find("\n", k)
        if line_end < 0:
            line_end = n
        tail = body[k:line_end]
        cm = re.search(r"//(.*)$", tail)
        comment = cm.group(1).strip() if cm else ""
        fields.append((name, optional, type_str, comment))
        # advance past THIS field's terminator at k (a `;`/`,`/newline), NOT to the next newline —
        # otherwise a single-line `{ a: T; b: U }` loses every field after the first.
        i = k + 1
    return fields


def _ts_is_boolish(type_str):
    t = type_str.strip()
    return t == "boolean" or bool(_TS_BOOL_UNION.match(t.replace(" ", "")))


def ts_smells(text):
    """Detect the model smells over TypeScript type/interface object definitions."""
    findings = []
    for kind, name, body in _ts_blocks(text):
        fields = _ts_fields(body)
        path = name
        # a discriminated union member uses a literal-typed tag (`tag: 'a'`) — but a single object
        # block isn't itself a union; the "not a discriminated union" guard for OPTIONAL_SOUP keys
        # off whether any field is a string-literal tag named like a discriminant.
        has_discriminant = any(
            fname in ("tag", "type", "kind", "_tag", "_type", "variant") and (
                _TS_LIT_UNION.search(ftype + " |") or re.match(r"""^['"][^'"]*['"]$""", ftype))
            for fname, _, ftype, _ in fields)
        open_record = bool(_TS_INDEX_SIG.search(body))

        bools = [f[0] for f in fields if _ts_is_boolish(f[2])]
        if len(bools) >= 2:
            findings.append(("BOOLEAN_BLINDNESS", path,
                             "%d boolean fields (%s) — model the exclusive state as a discriminated "
                             "union/enum" % (len(bools), ", ".join(sorted(bools)))))
        if len(fields) >= 4 and not has_discriminant:
            required = [f for f in fields if not f[1]]
            if len(required) <= 1:
                findings.append(("OPTIONAL_SOUP", path,
                                 "%d fields, %d required, no discriminated union — most field "
                                 "combinations are representable" % (len(fields), len(required))))
        if open_record:
            findings.append(("OPEN_RECORD", path,
                             "type with an index signature [k: string]: ... — extra fields are "
                             "representable"))
        for fname, _opt, ftype, comment in fields:
            t = ftype.strip()
            is_lit_union = bool(_TS_LIT_UNION.search(t + " |"))
            is_branded = bool(_TS_BRANDED.match(t))
            if _constrained_name(fname) and _TS_BARE_PRIM.match(t) and not is_branded and not is_lit_union:
                findings.append(("PRIMITIVE_OBSESSION", "%s.%s" % (path, fname),
                                 "'%s' is a bare %s — brand it or give it a literal-union/format"
                                 % (fname, t)))
            if t == "string" and not is_lit_union and ENUM_HINT.search(comment):
                findings.append(("STRINGLY_TYPED_ENUM", "%s.%s" % (path, fname),
                                 "'%s' comment lists fixed values but the type is bare string "
                                 "(use a string-literal union)" % fname))
    return findings


# --- Python path (stdlib `ast` — precise, not regex) ------------------------------------------
_PY_BARE_PRIM = {"str", "int", "float"}


def _py_ann_str(node):
    """Best-effort source text for an annotation node (ast.unparse on 3.9+, else a small fallback)."""
    if node is None:
        return ""
    try:
        return ast.unparse(node)  # 3.9+
    except AttributeError:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Constant):
            return repr(node.value)
        if isinstance(node, ast.Subscript):
            return _py_ann_str(node.value) + "[...]"
        if isinstance(node, ast.Attribute):
            return _py_ann_str(node.value) + "." + node.attr
        return ""


def _py_is_optional(ann):
    """True if the annotation is Optional[...] or `X | None`."""
    a = ann.replace(" ", "")
    return a.startswith("Optional[") or a.startswith("typing.Optional[") or \
        "|None" in a or "None|" in a


def _py_is_literal(ann):
    a = ann.replace(" ", "")
    return a.startswith("Literal[") or a.startswith("typing.Literal[") or "Literal[" in a


def _py_base_names(cls):
    out = []
    for b in cls.bases:
        if isinstance(b, ast.Name):
            out.append(b.id)
        elif isinstance(b, ast.Attribute):
            out.append(b.attr)
        elif isinstance(b, ast.Subscript):  # e.g. Generic[T]
            v = b.value
            out.append(v.id if isinstance(v, ast.Name) else getattr(v, "attr", ""))
    return out


def _py_is_dataclass(cls):
    for d in cls.decorator_list:
        target = d.func if isinstance(d, ast.Call) else d
        if isinstance(target, ast.Name) and target.id == "dataclass":
            return True
        if isinstance(target, ast.Attribute) and target.attr == "dataclass":
            return True
    return False


def _py_is_typeddict(cls):
    return "TypedDict" in _py_base_names(cls)


def _py_total_false(cls):
    """A TypedDict declared `total=False` — every field is then optional."""
    for kw in cls.keywords:
        if kw.arg == "total" and isinstance(kw.value, ast.Constant) and kw.value.value is False:
            return True
    return False


def _py_line_comments(src):
    """Map line number -> trailing `# ...` comment text (1-based, matches ast lineno)."""
    out = {}
    for n, line in enumerate(src.splitlines(), 1):
        # strip string-literal hashes crudely; annotations rarely carry # inside strings
        m = re.search(r"#(.*)$", line)
        if m:
            out[n] = m.group(1).strip()
    return out


def py_smells(src):
    """Detect the model smells over Python TypedDict / @dataclass class bodies (ast)."""
    findings = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return _py_regex_fallback(src)
    comments = _py_line_comments(src)

    for cls in ast.walk(tree):
        if not isinstance(cls, ast.ClassDef):
            continue
        is_td = _py_is_typeddict(cls)
        is_dc = _py_is_dataclass(cls)
        if not (is_td or is_dc):
            continue
        total_false = is_td and _py_total_false(cls)
        path = cls.name

        fields = []  # (name, ann_str, has_default, lineno)
        for stmt in cls.body:
            if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                fields.append((stmt.target.id, _py_ann_str(stmt.annotation),
                               stmt.value is not None, stmt.lineno))

        has_discriminant = any(
            fname in ("tag", "type", "kind", "variant") and _py_is_literal(ann)
            for fname, ann, _, _ in fields)

        bools = [f[0] for f in fields if f[1].strip() in ("bool", "builtins.bool")]
        if len(bools) >= 2:
            findings.append(("BOOLEAN_BLINDNESS", path,
                             "%d bool fields (%s) — model the exclusive state as a tagged union/enum"
                             % (len(bools), ", ".join(sorted(bools)))))
        if len(fields) >= 4 and not has_discriminant:
            optional = [f for f in fields
                        if total_false or _py_is_optional(f[1]) or f[2]]
            required = [f for f in fields if f not in optional]
            if len(required) <= 1:
                findings.append(("OPTIONAL_SOUP", path,
                                 "%d fields, %d required, no tagged union — most field combinations "
                                 "are representable" % (len(fields), len(required))))
        for fname, ann, _default, lineno in fields:
            base = ann.strip()
            if _constrained_name(fname) and base in _PY_BARE_PRIM:
                findings.append(("PRIMITIVE_OBSESSION", "%s.%s" % (path, fname),
                                 "'%s' is a bare %s — wrap it in a NewType/branded type" % (fname, base)))
            if base in ("str", "builtins.str") and not _py_is_literal(ann):
                cm = comments.get(lineno, "")
                if ENUM_HINT.search(cm):
                    findings.append(("STRINGLY_TYPED_ENUM", "%s.%s" % (path, fname),
                                     "'%s' comment lists fixed values but the type is bare str "
                                     "(use Literal[...]/Enum)" % fname))
    return findings


def _py_regex_fallback(src):
    """Fragment fallback when `ast.parse` fails (not a full module): scan `name: ann` lines for the
    primitive-obsession smell only (the one smell that needs no class/structure context)."""
    findings = []
    for n, line in enumerate(src.splitlines(), 1):
        m = re.match(r"\s*(\w+)\s*:\s*(str|int|float)\b", line)
        if m and _constrained_name(m.group(1)):
            findings.append(("PRIMITIVE_OBSESSION", "?.%s" % m.group(1),
                             "'%s' is a bare %s (parsed as a fragment) — wrap it in a NewType"
                             % (m.group(1), m.group(2))))
    return findings


# --- selftest fixtures ------------------------------------------------------------------------
DIRTY = {
    "type": "object",
    "properties": {
        "is_active": {"type": "boolean"},
        "is_deleted": {"enum": [True, False]},    # boolean in disguise; + is_active => BOOLEAN_BLINDNESS
        "email": {"type": "string"},             # PRIMITIVE_OBSESSION
        "status": {"type": "string", "description": "one of open, closed, pending"},  # STRINGLY_TYPED_ENUM
        "note": {"type": "string"},
        "nickname": {"type": "string"},
    },  # 6 props, 0 required, no oneOf => OPTIONAL_SOUP; no additionalProperties:false => OPEN_RECORD
}
CLEAN = {
    "type": "object",
    "additionalProperties": False,
    "required": ["state"],
    "properties": {
        "state": {"oneOf": [
            {"type": "object", "additionalProperties": False, "required": ["tag"],
             "properties": {"tag": {"const": "active"}}},
            {"type": "object", "additionalProperties": False, "required": ["tag", "deleted_at"],
             "properties": {"tag": {"const": "deleted"}, "deleted_at": {"type": "string", "format": "date-time"}}},
        ]},
        "email": {"type": "string", "format": "email"},
    },
}


# A boolean-blind object where BOTH fields are booleans in disguise (enum:[true,false]) — the
# state shape is identical to two real booleans (4 states), so it must still trip the smell.
DISGUISED_BOOLS = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "is_active": {"enum": [True, False]},
        "is_deleted": {"const": True},
    },
}

# --- TypeScript fixtures ----------------------------------------------------------------------
# Dirty: a boolean-blind, optional-soup, primitive-obsessed, stringly-typed, open record.
TS_DIRTY = """
export interface RequestState {
  isLoading?: boolean;
  isError?: boolean;                // 2 boolean fields => BOOLEAN_BLINDNESS
  email?: string;                   // PRIMITIVE_OBSESSION (constrained name, bare string)
  status?: string;                  // one of open, closed, pending  -> STRINGLY_TYPED_ENUM
  note?: string;
  nickname?: string;                // 6 fields, 0 required => OPTIONAL_SOUP
  [key: string]: unknown;           // index signature => OPEN_RECORD
}
"""

# Clean: a discriminated union built from per-variant object types — branded primitive, a
# string-literal union enum, a literal `tag` discriminant. Must trip NOTHING.
TS_CLEAN = """
export type Email = string & { readonly __brand: 'Email' };

export type Loading = {
  tag: 'loading';
};

export type Ready = {
  tag: 'ready';
  data: string;
  contact: Email;                   // branded, not a bare string -> no PRIMITIVE_OBSESSION
  status: 'open' | 'closed' | 'pending';   // string-literal union -> no STRINGLY_TYPED_ENUM
};

export interface Failed {
  tag: 'failed';
  retriable: boolean;               // single boolean -> no BOOLEAN_BLINDNESS
  code: 'net' | 'auth' | 'unknown';
}
"""

# --- Python fixtures --------------------------------------------------------------------------
# Dirty: a @dataclass with boolean-blindness, optional-soup, primitive-obsession, stringly-typed.
PY_DIRTY = '''
from dataclasses import dataclass
from typing import Optional


@dataclass
class RequestState:
    email: str                           # the one required field; bare str => PRIMITIVE_OBSESSION
    is_loading: bool = False
    is_error: bool = False               # 2 bool fields => BOOLEAN_BLINDNESS
    status: str = "open"  # one of open, closed, pending  -> STRINGLY_TYPED_ENUM
    note: Optional[str] = None
    nickname: Optional[str] = None       # 6 fields, 1 required => OPTIONAL_SOUP
'''

# Clean: a tagged union via Literal-discriminated TypedDicts; Literal-typed enum field; a NewType
# brand for the constrained-name field. Must trip NOTHING.
PY_CLEAN = '''
from typing import Literal, NewType, TypedDict

Email = NewType("Email", str)


class Loading(TypedDict):
    tag: Literal["loading"]


class Ready(TypedDict):
    tag: Literal["ready"]
    data: str
    contact: Email                       # NewType brand -> no PRIMITIVE_OBSESSION
    status: Literal["open", "closed", "pending"]   # Literal -> no STRINGLY_TYPED_ENUM


class Failed(TypedDict):
    tag: Literal["failed"]
    retriable: bool                      # single bool -> no BOOLEAN_BLINDNESS
    code: Literal["net", "auth", "unknown"]
'''


def selftest():
    errs = []
    kinds = {k for k, _, _ in smells(DIRTY)}
    for want in ("BOOLEAN_BLINDNESS", "OPTIONAL_SOUP", "OPEN_RECORD", "PRIMITIVE_OBSESSION", "STRINGLY_TYPED_ENUM"):
        if want not in kinds:
            errs.append("DIRTY missed %s (got %s)" % (want, sorted(kinds)))
    if smells(CLEAN):
        errs.append("CLEAN produced smells: %s" % smells(CLEAN))
    # boolean-in-disguise: two enum/const-boolean fields must still trip BOOLEAN_BLINDNESS
    if not any(k == "BOOLEAN_BLINDNESS" for k, _, _ in smells(DISGUISED_BOOLS)):
        errs.append("DISGUISED_BOOLS missed BOOLEAN_BLINDNESS (enum:[true,false] not seen as boolean)")

    # --- TypeScript ---
    ts_kinds = {k for k, _, _ in ts_smells(TS_DIRTY)}
    for want in ("BOOLEAN_BLINDNESS", "OPTIONAL_SOUP", "OPEN_RECORD", "PRIMITIVE_OBSESSION", "STRINGLY_TYPED_ENUM"):
        if want not in ts_kinds:
            errs.append("TS_DIRTY missed %s (got %s)" % (want, sorted(ts_kinds)))
    if ts_smells(TS_CLEAN):
        errs.append("TS_CLEAN produced smells: %s" % ts_smells(TS_CLEAN))

    # --- Python ---
    py_kinds = {k for k, _, _ in py_smells(PY_DIRTY)}
    for want in ("BOOLEAN_BLINDNESS", "OPTIONAL_SOUP", "PRIMITIVE_OBSESSION", "STRINGLY_TYPED_ENUM"):
        if want not in py_kinds:
            errs.append("PY_DIRTY missed %s (got %s)" % (want, sorted(py_kinds)))
    if py_smells(PY_CLEAN):
        errs.append("PY_CLEAN produced smells: %s" % py_smells(PY_CLEAN))

    # --- review lock-ins: single-line TS fields, camelCase constrained names, and the FP guards ---
    if "BOOLEAN_BLINDNESS" not in {k for k, _, _ in ts_smells("interface S { loading: boolean; error: boolean }")}:
        errs.append("single-line TS `;`-separated fields lost (BOOLEAN_BLINDNESS missed)")
    if "PRIMITIVE_OBSESSION" not in {k for k, _, _ in ts_smells("type U = { userId: string }")}:
        errs.append("camelCase TS field 'userId' not seen as a constrained name")
    if "PRIMITIVE_OBSESSION" not in {k for k, _, _ in py_smells(
            "from dataclasses import dataclass\n@dataclass\nclass U:\n    userId: str\n")}:
        errs.append("camelCase Python field 'userId' not seen as a constrained name")
    for fp in ("grid", "valid", "android"):
        if "PRIMITIVE_OBSESSION" in {k for k, _, _ in ts_smells("type G = { %s: string }" % fp)}:
            errs.append("false positive: lowercase '%s' (ends in 'id', not camelCase) flagged" % fp)
    return errs


_SCAN_EXTS = (".json", ".ts", ".tsx", ".py", ".pyi")


def _iter(path):
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            for fn in sorted(fns):
                if fn.endswith(_SCAN_EXTS):
                    yield os.path.join(dp, fn)
    else:
        yield path


def main(argv):
    if not argv or argv[0] == "selftest":
        e = selftest()
        if e:
            sys.stderr.write("model-smells: FAIL (%d)\n" % len(e))
            for x in e:
                sys.stderr.write("  - %s\n" % x)
            return 1
        print("model-smells: OK — 5 smell detectors verified over JSON-Schema, TypeScript, and "
              "Python dirty/clean fixtures")
        return 0
    total = 0
    for fp in _iter(argv[0]):
        ext = os.path.splitext(fp)[1].lower()
        try:
            text = open(fp, encoding="utf-8").read()
        except OSError as ex:
            print("  ⚠ %s: unreadable (%s)" % (fp, ex))
            continue
        if ext in (".ts", ".tsx"):
            found = ts_smells(text)
        elif ext in (".py", ".pyi"):
            found = py_smells(text)
        else:
            try:
                found = smells(json.loads(text))
            except json.JSONDecodeError as ex:
                print("  ⚠ %s: not valid JSON (%s)" % (fp, ex))
                continue
        for kind, path, detail in found:
            total += 1
            print("  %s  %-20s %s  %s" % (os.path.relpath(fp), kind, path, detail))
    if total:
        print("model-smells: %d smell(s) — widen-able state space; confirm with an illegal-instance set" % total)
        return 1
    print("model-smells: OK — no model smells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
