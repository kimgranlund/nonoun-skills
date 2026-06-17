#!/usr/bin/env python3
"""instance-check.py — the type-decomposer state-space gate. Self-contained (stdlib only).

A type's real meaning is the SET of values it admits, not its field names. "Make illegal states
unrepresentable" is a claim you cannot eyeball — you PROVE it by feeding the model both a LEGAL
instance set (every one must validate) and an ILLEGAL instance set (every one must be REJECTED).
An illegal instance that validates is the signature failure: an illegal state IS representable.

This carries a JSON-Schema SUBSET validator big enough to express the tools that make illegal
states unrepresentable — `oneOf` (tagged unions), `additionalProperties:false` (closed records),
`const`/`enum`, `required`, `not`, `allOf`/`anyOf` — then runs a spec of legal/illegal instances
against it.

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
    return a == t


def validate(v, schema, path="$"):
    """Return a list of error strings; empty list == valid. JSON-Schema subset."""
    errs = []
    if schema is True or schema == {}:
        return errs
    if schema is False:
        return ["%s: schema false — nothing is valid here" % path]
    if not isinstance(schema, dict):
        return errs

    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(v, t) for t in types):
            errs.append("%s: type is %s, expected %s" % (path, _typeof(v), "/".join(types)))
    if "const" in schema and v != schema["const"]:
        errs.append("%s: %r != const %r" % (path, v, schema["const"]))
    if "enum" in schema and v not in schema["enum"]:
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
        if "multipleOf" in schema and schema["multipleOf"] and v % schema["multipleOf"] != 0:
            errs.append("%s: %s not a multiple of %s" % (path, v, schema["multipleOf"]))
    if kind == "string":
        if "minLength" in schema and len(v) < schema["minLength"]:
            errs.append("%s: shorter than minLength %s" % (path, schema["minLength"]))
        if "maxLength" in schema and len(v) > schema["maxLength"]:
            errs.append("%s: longer than maxLength %s" % (path, schema["maxLength"]))
        if "pattern" in schema and not re.search(schema["pattern"], v):
            errs.append("%s: does not match pattern %s" % (path, schema["pattern"]))
    if kind == "array":
        if "minItems" in schema and len(v) < schema["minItems"]:
            errs.append("%s: fewer than minItems %s" % (path, schema["minItems"]))
        if "maxItems" in schema and len(v) > schema["maxItems"]:
            errs.append("%s: more than maxItems %s" % (path, schema["maxItems"]))
        if schema.get("uniqueItems") and len({json.dumps(x, sort_keys=True) for x in v}) != len(v):
            errs.append("%s: items not unique" % path)
        if "items" in schema:
            for i, item in enumerate(v):
                errs += validate(item, schema["items"], "%s[%d]" % (path, i))
    if kind == "object":
        props = schema.get("properties", {})
        for k in schema.get("required", []):
            if k not in v:
                errs.append("%s: missing required '%s'" % (path, k))
        ap = schema.get("additionalProperties", True)
        for k, val in v.items():
            if k in props:
                errs += validate(val, props[k], "%s.%s" % (path, k))
            elif ap is False:
                errs.append("%s: additional property '%s' not allowed (closed record)" % (path, k))
            elif isinstance(ap, dict):
                errs += validate(val, ap, "%s.%s" % (path, k))

    if "allOf" in schema:
        for sub in schema["allOf"]:
            errs += validate(v, sub, path)
    if "anyOf" in schema and not any(not validate(v, sub, path) for sub in schema["anyOf"]):
        errs.append("%s: matches none of anyOf" % path)
    if "oneOf" in schema:
        n = sum(1 for sub in schema["oneOf"] if not validate(v, sub, path))
        if n != 1:
            errs.append("%s: matches %d of oneOf (need exactly 1)" % (path, n))
    if "not" in schema and not validate(v, schema["not"], path):
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
    # validator spot-checks
    if validate(True, {"type": "integer"}) == []:
        errs.append("bool wrongly accepted as integer")
    if validate(5, {"type": "number"}):
        errs.append("int wrongly rejected as number")
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
