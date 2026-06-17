#!/usr/bin/env python3
"""instance-check.py — the type-decomposer state-space gate. Self-contained (stdlib only).

A type's real meaning is the SET of values it admits, not its field names. "Make illegal states
unrepresentable" is a claim you cannot eyeball — you PROVE it by feeding the model both a LEGAL
instance set (every one must validate) and an ILLEGAL instance set (every one must be REJECTED).
An illegal instance that validates is the signature failure: an illegal state IS representable.

This carries a JSON-Schema SUBSET validator big enough to express the tools that make illegal
states unrepresentable — `oneOf` (tagged unions), `additionalProperties:false` (closed records),
`const`/`enum`, `required`, `not`, `allOf`/`anyOf`, `pattern`, an asserting `format` set
(email/uri/url/uuid/date/date-time), and local `$ref` into `#/$defs`/`#/definitions` — then runs
a spec of legal/illegal instances against it.

DEFAULT-DENY: this is a SUBSET, so any keyword it does not understand (`if/then/else`,
`patternProperties`, `dependentRequired`, `propertyNames`, `contains`, `prefixItems`, tuple-`items`,
a remote `$ref`, …) raises and surfaces as an UNSUPPORTED_SCHEMA finding — a LOUD failure — rather
than being silently ignored. A silent ignore would drop a real constraint and let an illegal
instance false-green; the gate's whole value is being a trustworthy rejecter.

Type-aware scalar equality (const/enum/uniqueItems): a JSON `bool` is a distinct value class from
int/float (`true != 1`), while `1 == 1.0`; a float with zero fractional part satisfies `integer`
(`5.0 ⊨ integer`); `format` is enforced (not the JSON-Schema default of non-asserting).

Spec file (JSON):
  { "schema": { ...json-schema-subset... },
    "legal":   [ ...instances that MUST validate... ],
    "illegal": [ ...instances that MUST be rejected... ] }

  python3 bin/instance-check.py selftest
  python3 bin/instance-check.py <spec.json>

Python 3.8+.
"""
import json
import re
import sys


def _typeof(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, int):
        return "integer"
    if isinstance(v, float):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    if isinstance(v, dict):
        return "object"
    return "unknown"


def _type_ok(v, t):
    a = _typeof(v)
    if t == "number":
        return a in ("integer", "number")
    if t == "integer":
        # JSON Schema: a number with zero fractional part IS an integer (5.0 ⊨ integer).
        # bool is never a number/integer.
        if isinstance(v, bool):
            return False
        if a == "integer":
            return True
        if a == "number":
            return v == int(v)
        return False
    return a == t


# JSON value classes for type-aware equality. bool is its OWN class, distinct from
# integer/number — JSON Schema treats true and 1 as different values, but 1 and 1.0 as equal.
def _value_class(v):
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if v is None:
        return "null"
    if isinstance(v, list):
        return "array"
    if isinstance(v, dict):
        return "object"
    return "unknown"


def _json_eq(a, b):
    """Type-aware JSON value equality used by const/enum/uniqueItems.

    bool is distinct from int/float (True != 1); numbers compare numerically so 1 == 1.0;
    containers compare structurally with the same rules applied element-wise.
    """
    ca, cb = _value_class(a), _value_class(b)
    if ca != cb:
        return False
    if ca == "number":
        return a == b  # 1 == 1.0 (neither is a bool here)
    if ca == "bool":
        return a is b
    if ca == "array":
        return len(a) == len(b) and all(_json_eq(x, y) for x, y in zip(a, b))
    if ca == "object":
        return a.keys() == b.keys() and all(_json_eq(a[k], b[k]) for k in a)
    return a == b


def _canon(v):
    """Hashable canonical key for uniqueItems: (value-class, normalized value) so 1 and 1.0
    collide and true is distinct from 1. Numbers normalize to float; containers recurse."""
    c = _value_class(v)
    if c == "number":
        return ("number", float(v))
    if c == "bool":
        return ("bool", v)
    if c == "array":
        return ("array", tuple(_canon(x) for x in v))
    if c == "object":
        return ("object", tuple(sorted((k, _canon(val)) for k, val in v.items())))
    return (c, v)


# Format checkers (asserting subset). JSON Schema makes `format` non-asserting by default;
# the type-decomposer docs sell format:email etc. as making the bad value unrepresentable, so
# the gate MUST enforce them. Unknown formats are treated as non-asserting (accept).
_FORMAT = {
    "email": re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
    "uri": re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*:.+$"),
    "url": re.compile(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://.+$"),
    "uuid": re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                       r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"),
    "date-time": re.compile(
        r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+\-]\d{2}:\d{2})$"),
    "date": re.compile(r"^\d{4}-\d{2}-\d{2}$"),
}

# Keywords this subset validator UNDERSTANDS. Anything else (a $ref, an if/then/else, a tuple
# items, patternProperties, …) must FAIL LOUD via default-deny — never be silently ignored, which
# would drop a real constraint and false-green an illegal instance.
_KNOWN = frozenset({
    "type", "const", "enum", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "multipleOf", "minLength", "maxLength", "pattern", "format", "minItems", "maxItems",
    "uniqueItems", "items", "properties", "required", "additionalProperties",
    "allOf", "anyOf", "oneOf", "not",
    # definition containers — hold subschemas reached via $ref; carry no constraint themselves
    "$defs", "definitions",
    # annotations — accepted, carry no constraint
    "title", "description", "default", "examples", "$comment", "$schema", "$id",
})


class SchemaError(Exception):
    """An unsupported/unresolvable schema keyword — a default-deny LOUD failure, not a validation
    miss. Raised so a spec using a keyword this subset can't enforce FAILS rather than false-greens."""


def _resolve_ref(ref, root, path):
    """Resolve a local JSON-pointer $ref into #/$defs or #/definitions. Remote/non-local refs are
    a loud SchemaError — silently passing them would drop the referenced constraint."""
    if not isinstance(ref, str) or not ref.startswith("#/"):
        raise SchemaError("%s: unsupported $ref %r (only local #/$defs and #/definitions)"
                          % (path, ref))
    target = root
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(target, dict) and token in target:
            target = target[token]
        else:
            raise SchemaError("%s: $ref %r does not resolve" % (path, ref))
    if not isinstance(target, (dict, bool)):
        raise SchemaError("%s: $ref %r points at a non-schema" % (path, ref))
    return target


def validate(v, schema, path="$", root=None):
    """Return a list of error strings; empty list == valid. JSON-Schema SUBSET validator.

    Default-deny: any keyword outside the supported subset raises SchemaError (a loud failure),
    so an unenforceable spec can never silently validate an illegal instance.
    """
    errs = []
    if root is None:
        root = schema
    if schema is True or schema == {}:
        return errs
    if schema is False:
        return ["%s: schema false — nothing is valid here" % path]
    if not isinstance(schema, dict):
        return errs

    if "$ref" in schema:
        # A $ref is the only keyword we follow rather than reject; siblings are ignored per JSON
        # Schema draft semantics, but flag any unknown sibling so nothing is silently dropped.
        for k in schema:
            if k != "$ref" and k not in _KNOWN:
                raise SchemaError("%s: unsupported keyword %r alongside $ref" % (path, k))
        return validate(v, _resolve_ref(schema["$ref"], root, path), path, root)

    unknown = [k for k in schema if k not in _KNOWN]
    if unknown:
        raise SchemaError("%s: unsupported keyword(s) %s — this validator covers a SUBSET; a green "
                          "here would be a false proof. Express the constraint with a supported "
                          "keyword or extend the tool." % (path, ", ".join(sorted(unknown))))

    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(v, t) for t in types):
            errs.append("%s: type is %s, expected %s" % (path, _typeof(v), "/".join(types)))
    if "const" in schema and not _json_eq(v, schema["const"]):
        errs.append("%s: %r != const %r" % (path, v, schema["const"]))
    if "enum" in schema and not any(_json_eq(v, e) for e in schema["enum"]):
        errs.append("%s: %r not in enum" % (path, v))

    kind = _typeof(v)
    if kind in ("integer", "number"):
        if "minimum" in schema and v < schema["minimum"]:
            errs.append("%s: %s < minimum %s" % (path, v, schema["minimum"]))
        if "maximum" in schema and v > schema["maximum"]:
            errs.append("%s: %s > maximum %s" % (path, v, schema["maximum"]))
        if "exclusiveMinimum" in schema and v <= schema["exclusiveMinimum"]:
            errs.append("%s: %s <= exclusiveMinimum %s" % (path, v, schema["exclusiveMinimum"]))
        if "exclusiveMaximum" in schema and v >= schema["exclusiveMaximum"]:
            errs.append("%s: %s >= exclusiveMaximum %s" % (path, v, schema["exclusiveMaximum"]))
        m = schema.get("multipleOf")
        if m:
            # Float % is brittle (0.3 % 0.1 != 0). Compare against the nearest multiple instead.
            q = round(v / m)
            if abs(q * m - v) > 1e-9 * max(1.0, abs(v)):
                errs.append("%s: %s not a multiple of %s" % (path, v, m))
    if kind == "string":
        if "minLength" in schema and len(v) < schema["minLength"]:
            errs.append("%s: shorter than minLength %s" % (path, schema["minLength"]))
        if "maxLength" in schema and len(v) > schema["maxLength"]:
            errs.append("%s: longer than maxLength %s" % (path, schema["maxLength"]))
        if "pattern" in schema:
            # ECMA `$` matches end-of-string; Python `$` also matches before a trailing \n. Use \Z.
            pat = re.sub(r"(?<!\\)\$$", r"\\Z", schema["pattern"])
            if not re.search(pat, v):
                errs.append("%s: does not match pattern %s" % (path, schema["pattern"]))
        fmt = schema.get("format")
        if fmt in _FORMAT and not _FORMAT[fmt].match(v):
            errs.append("%s: %r is not a valid %s" % (path, v, fmt))
    if kind == "array":
        if "minItems" in schema and len(v) < schema["minItems"]:
            errs.append("%s: fewer than minItems %s" % (path, schema["minItems"]))
        if "maxItems" in schema and len(v) > schema["maxItems"]:
            errs.append("%s: more than maxItems %s" % (path, schema["maxItems"]))
        if schema.get("uniqueItems"):
            seen = set()
            dup = False
            for x in v:
                key = _canon(x)
                if key in seen:
                    dup = True
                    break
                seen.add(key)
            if dup:
                errs.append("%s: items not unique" % path)
        if "items" in schema:
            if isinstance(schema["items"], list):
                raise SchemaError("%s: tuple-form `items` (array) is unsupported" % path)
            for i, item in enumerate(v):
                errs += validate(item, schema["items"], "%s[%d]" % (path, i), root)
    if kind == "object":
        props = schema.get("properties", {})
        for k in schema.get("required", []):
            if k not in v:
                errs.append("%s: missing required '%s'" % (path, k))
        ap = schema.get("additionalProperties", True)
        for k, val in v.items():
            if k in props:
                errs += validate(val, props[k], "%s.%s" % (path, k), root)
            elif ap is False:
                errs.append("%s: additional property '%s' not allowed (closed record)" % (path, k))
            elif isinstance(ap, dict):
                errs += validate(val, ap, "%s.%s" % (path, k), root)

    if "allOf" in schema:
        for sub in schema["allOf"]:
            errs += validate(v, sub, path, root)
    if "anyOf" in schema and not any(not validate(v, sub, path, root) for sub in schema["anyOf"]):
        errs.append("%s: matches none of anyOf" % path)
    if "oneOf" in schema:
        n = sum(1 for sub in schema["oneOf"] if not validate(v, sub, path, root))
        if n != 1:
            errs.append("%s: matches %d of oneOf (need exactly 1)" % (path, n))
    if "not" in schema and not validate(v, schema["not"], path, root):
        errs.append("%s: matches 'not' schema" % path)
    return errs


def is_valid(v, schema):
    return not validate(v, schema)


def check_spec(spec):
    """Return (findings, stats). A finding is a tuple (kind, detail)."""
    schema = spec.get("schema")
    if not isinstance(schema, dict):
        return [("SPEC", "spec has no 'schema' object")], {}
    findings = []
    legal, illegal = spec.get("legal", []), spec.get("illegal", [])
    try:
        for i, inst in enumerate(legal):
            errs = validate(inst, schema)
            if errs:
                findings.append(("LEGAL_REJECTED",
                                 "legal[%d] should validate but doesn't — model too tight: %s"
                                 % (i, errs[0])))
        for i, inst in enumerate(illegal):
            if is_valid(inst, schema):
                findings.append(("ILLEGAL_REPRESENTABLE",
                                 "illegal[%d] validates — an illegal state IS representable: %r"
                                 % (i, inst)))
    except SchemaError as ex:
        # Default-deny: the schema uses a keyword this subset can't enforce. A green would be a
        # FALSE proof, so this is a hard finding, not a silent pass.
        findings.append(("UNSUPPORTED_SCHEMA",
                         "%s — cannot prove unrepresentability; express it with a supported "
                         "keyword or extend instance-check.py" % ex))
    return findings, {"legal": len(legal), "illegal": len(illegal)}


# --- selftest fixtures ------------------------------------------------------------------------
# A TIGHT model: a payment is a tagged union (oneOf) of closed records. Illegal combinations
# (card with no number, cash carrying a card field, an unknown method, extra fields) are
# unrepresentable.
TIGHT = {
    "schema": {
        "type": "object",
        "oneOf": [
            {"type": "object", "additionalProperties": False,
             "required": ["method", "card_number"],
             "properties": {"method": {"const": "card"}, "card_number": {"type": "string", "minLength": 12}}},
            {"type": "object", "additionalProperties": False,
             "required": ["method"],
             "properties": {"method": {"const": "cash"}}},
        ],
    },
    "legal": [
        {"method": "card", "card_number": "4111111111111"},
        {"method": "cash"},
    ],
    "illegal": [
        {"method": "card"},                                   # card without a number
        {"method": "cash", "card_number": "4111111111111"},   # cash carrying card data
        {"method": "wire"},                                   # unknown method
        {"method": "card", "card_number": "4111111111111", "x": 1},  # extra field
        {},                                                   # no method
    ],
}
# A LOOSE model: "just an object" — admits every illegal state. The tool must catch this.
LOOSE = {
    "schema": {"type": "object"},
    "legal": [{"method": "card", "card_number": "4111111111111"}],
    "illegal": [{"method": "wire"}, {}],
}
# An OVER-TIGHT model: rejects a legal state (a legal 13-char number fails a wrong minLength 20).
OVERTIGHT = {
    "schema": {"type": "object", "properties": {"card_number": {"type": "string", "minLength": 20}}},
    "legal": [{"card_number": "4111111111111"}],
    "illegal": [],
}
# B1 (bool/int leak): an integer enum must REJECT a boolean. Python's True == 1 used to let
# `true` validate against {"enum":[0,1,2]} — an illegal state silently representable.
BOOL_IN_INT_ENUM = {
    "schema": {"type": "object", "additionalProperties": False, "required": ["level"],
               "properties": {"level": {"enum": [0, 1, 2]}}},
    "legal": [{"level": 0}, {"level": 2}],
    "illegal": [{"level": True}, {"level": False}, {"level": 3}],
}
# B2 (default-deny): a spec whose schema leans on $ref must be ENFORCED, not silently ignored.
# Here the $ref resolves locally, so {"kind":"zzz"} is correctly rejected (the enum holds).
REF_SPEC = {
    "schema": {"type": "object", "additionalProperties": False, "required": ["kind"],
               "$defs": {"tag": {"enum": ["a", "b"]}},
               "properties": {"kind": {"$ref": "#/$defs/tag"}}},
    "legal": [{"kind": "a"}, {"kind": "b"}],
    "illegal": [{"kind": "zzz"}],  # was silently ACCEPTED when $ref was ignored
}
# B2 (default-deny LOUD): an UNSUPPORTED keyword must surface as UNSUPPORTED_SCHEMA, never as a
# silent green. `patternProperties` is not in the subset.
UNSUPPORTED_SPEC = {
    "schema": {"type": "object", "patternProperties": {"^x": {"type": "string"}}},
    "legal": [{"x1": "ok"}],
    "illegal": [{"x1": 5}],
}
# M1 (5.0 ⊨ integer): a float with zero fractional part is a legal integer instance.
FLOAT_INTEGER = {
    "schema": {"type": "object", "additionalProperties": False, "required": ["qty"],
               "properties": {"qty": {"type": "integer", "minimum": 0}}},
    "legal": [{"qty": 5.0}, {"qty": 5}, {"qty": 0}],
    "illegal": [{"qty": 5.5}, {"qty": True}],  # bool is not an integer
}
# M2 (format enforced): format:email must REJECT a non-email — the doc-promised collapse.
FORMAT_EMAIL = {
    "schema": {"type": "object", "additionalProperties": False, "required": ["email"],
               "properties": {"email": {"type": "string", "format": "email"}}},
    "legal": [{"email": "a@b.co"}],
    "illegal": [{"email": "not-an-email"}],
}


def selftest():
    errs = []
    f, _ = check_spec(TIGHT)
    if f:
        errs.append("TIGHT model produced findings (should be clean): %s" % f)
    f, _ = check_spec(LOOSE)
    if not any(k == "ILLEGAL_REPRESENTABLE" for k, _ in f):
        errs.append("LOOSE model did not flag a representable illegal state: %s" % f)
    f, _ = check_spec(OVERTIGHT)
    if not any(k == "LEGAL_REJECTED" for k, _ in f):
        errs.append("OVER-TIGHT model did not flag a rejected legal state: %s" % f)

    # B1 — bool/int leak: an integer enum must reject true/false; the fixture must be CLEAN
    # (i.e. its illegal set, incl. {"level": true}, is correctly rejected).
    f, _ = check_spec(BOOL_IN_INT_ENUM)
    if f:
        errs.append("BOOL_IN_INT_ENUM not clean — bool leaked through int enum/const: %s" % f)
    # B2 — local $ref must be resolved and ENFORCED, not silently ignored.
    f, _ = check_spec(REF_SPEC)
    if f:
        errs.append("REF_SPEC not clean — local $ref not resolved/enforced: %s" % f)
    # B2 — an unsupported keyword must FAIL LOUD, never silently pass.
    f, _ = check_spec(UNSUPPORTED_SPEC)
    if not any(k == "UNSUPPORTED_SCHEMA" for k, _ in f):
        errs.append("UNSUPPORTED_SPEC did not fail loud on an unsupported keyword: %s" % f)
    # M1 — 5.0 is a legal integer; the fixture must be CLEAN.
    f, _ = check_spec(FLOAT_INTEGER)
    if f:
        errs.append("FLOAT_INTEGER not clean — 5.0 wrongly rejected against integer: %s" % f)
    # M2 — format:email must reject a non-email; the fixture must be CLEAN.
    f, _ = check_spec(FORMAT_EMAIL)
    if f:
        errs.append("FORMAT_EMAIL not clean — format:email not enforced: %s" % f)

    # validator spot-checks
    if validate(True, {"type": "integer"}) == []:
        errs.append("bool wrongly accepted as integer")
    if validate(5, {"type": "number"}):
        errs.append("int wrongly rejected as number")
    if validate(5.0, {"type": "integer"}):
        errs.append("5.0 wrongly rejected as integer")
    if validate(5.5, {"type": "integer"}) == []:
        errs.append("5.5 wrongly accepted as integer")
    # B1 scalar equality: true != 1, 1 != true, but 1 == 1.0
    if validate(True, {"const": 1}) == []:
        errs.append("true wrongly accepted as const 1")
    if validate(1, {"const": True}) == []:
        errs.append("1 wrongly accepted as const true")
    if validate(1.0, {"const": 1}):
        errs.append("1.0 wrongly rejected as const 1")
    if validate(True, {"enum": [0, 1, 2]}) == []:
        errs.append("true wrongly accepted in int enum")
    # B1 uniqueItems: 1 and 1.0 are duplicates; true and 1 are not.
    if validate([1, 1.0], {"type": "array", "uniqueItems": True}) == []:
        errs.append("uniqueItems missed 1 == 1.0 duplicate")
    if validate([1, True], {"type": "array", "uniqueItems": True}):
        errs.append("uniqueItems wrongly merged 1 and true")
    # M2 format
    if validate("not-an-email", {"type": "string", "format": "email"}) == []:
        errs.append("format:email accepted a non-email")
    if validate("a@b.co", {"type": "string", "format": "email"}):
        errs.append("format:email rejected a valid email")
    # minor: multipleOf float tolerance (0.3 is a multiple of 0.1)
    if validate(0.3, {"type": "number", "multipleOf": 0.1}):
        errs.append("multipleOf 0.1 false-positive on 0.3")
    if validate(0.35, {"type": "number", "multipleOf": 0.1}) == []:
        errs.append("multipleOf 0.1 missed 0.35")
    # minor: pattern trailing $ must not match before a trailing newline (ECMA vs Python)
    if validate("ab\n", {"type": "string", "pattern": "^ab$"}) == []:
        errs.append("pattern $ wrongly matched before trailing newline")
    # B2 default-deny: an unsupported keyword raises rather than silently validating
    try:
        validate({"x1": "ok"}, {"type": "object", "patternProperties": {"^x": {"type": "string"}}})
        errs.append("unsupported keyword did not raise (silent false-green)")
    except SchemaError:
        pass
    # additionalProperties / oneOf still hold
    if not validate({"a": 1}, {"type": "object", "additionalProperties": False}):
        errs.append("additionalProperties:false not enforced")
    if validate("card", {"oneOf": [{"const": "card"}, {"const": "cash"}]}):
        errs.append("oneOf exact-one not satisfied for a valid tag")
    return errs


def main(argv):
    if not argv or argv[0] == "selftest":
        e = selftest()
        if e:
            sys.stderr.write("instance-check: FAIL (%d)\n" % len(e))
            for x in e:
                sys.stderr.write("  - %s\n" % x)
            return 1
        print("instance-check: OK — validator + legal/illegal state-space proof verified over fixtures")
        return 0
    try:
        spec = json.load(open(argv[0], encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as ex:
        sys.stderr.write("cannot read spec: %s\n" % ex)
        return 2
    findings, stats = check_spec(spec)
    for kind, detail in findings:
        print("  %-22s %s" % (kind, detail))
    if findings:
        sys.stderr.write("instance-check: FAIL (%d finding(s); %d legal / %d illegal instances)\n"
                         % (len(findings), stats.get("legal", 0), stats.get("illegal", 0)))
        return 1
    print("instance-check: OK — %d legal validate, %d illegal rejected (illegal states unrepresentable)"
          % (stats.get("legal", 0), stats.get("illegal", 0)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
