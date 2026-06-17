#!/usr/bin/env python3
"""schema-check.py — the extraction-decomposer VALIDITY gate. Self-contained (stdlib only).

A minimal JSON-Schema-SUBSET validator. This is the CHEAP, mechanizable axis: it proves an extraction
is well-formed JSON (B1), conforms to the declared schema's types/required/enum (B2), and satisfies
range/pattern/length constraints (B3). It says NOTHING about whether the values are TRUE — that is
the dangerous fidelity axis, and it routes to `groundedness-check.py` + an adversarial verifier. A
schema gate is necessary but cannot see hallucination; that inversion is the skill's reason to exist.

Supported keywords (a deliberate subset — enough to validate an extraction contract, no remote $ref,
no `$schema` fetch, no format registry):

  type        string | number | integer | boolean | object | array | null  (or a list of those)
  required    [names]  — every listed property must be present (B2; the field that tempts hallucination)
  properties  {name: subschema}  — validated when present
  items       subschema  — applied to every array element
  enum        [values]   — the value must be one of these
  minimum / maximum         — numeric bounds (inclusive)
  minLength / maxLength     — string length bounds
  pattern     a regex the string must search-match

UNKNOWN / UNSUPPORTED keywords are NOT silent no-ops. A schema-author typo (`requried`, `minimun`) or
an unsupported keyword (`additionalProperties`, `uniqueItems`) that this subset doesn't enforce is the
most dangerous schema bug: it produces a FALSE GREEN — the intended constraint is never checked, so a
violating doc passes. So every keyword a schema node carries that this validator does not implement is
surfaced as a `WARN: unknown/unsupported keyword 'X' — not enforced` finding, and the run exits
nonzero (a schema you can't fully enforce must not report a clean pass). Meta-keywords that legitimately
carry no validation here ($schema, $id, $comment, title, description, default, examples) are ignored.

  python3 bin/schema-check.py selftest
  python3 bin/schema-check.py <doc.json> <schema.json>   # nonzero exit on any violation OR unknown keyword

Python 3.8+.
"""
import json
import re
import sys

# JSON-Schema type name -> the Python check. `integer` excludes bool; `number` excludes bool too
# (in JSON, true is not 1). `null` is Python None.
_TYPE_CHECKS = {
    "string": lambda v: isinstance(v, str),
    "boolean": lambda v: isinstance(v, bool),
    "null": lambda v: v is None,
    "object": lambda v: isinstance(v, dict),
    "array": lambda v: isinstance(v, list),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
}


# keywords this validator IMPLEMENTS (carries enforcement for).
_SUPPORTED = frozenset({
    "type", "required", "properties", "items", "enum",
    "minimum", "maximum", "minLength", "maxLength", "pattern",
})
# meta / annotation keywords that legitimately carry no validation here — ignored, NOT warned.
_IGNORED = frozenset({
    "$schema", "$id", "$comment", "$defs", "definitions",
    "title", "description", "default", "examples",
})


def _type_ok(value, t):
    check = _TYPE_CHECKS.get(t)
    if check is None:
        return None   # unknown type name -> reported by validate as a schema error
    return check(value)


def validate(value, schema, path="$", errors=None):
    """Validate `value` against `schema`. Appends "<path>: <message>" strings to `errors`.

    A `WARN: ... unknown/unsupported keyword 'X' — not enforced` line is appended for any keyword the
    validator does not implement (a typo or an unsupported constraint that would otherwise be a SILENT
    no-op → false green). Warnings count toward a nonzero exit, since a schema that can't be fully
    enforced must not report a clean pass."""
    if errors is None:
        errors = []
    if not isinstance(schema, dict):
        errors.append("%s: schema node is not an object" % path)
        return errors

    # --- unknown / unsupported keyword detection (defeats the author-typo false green) ---
    for kw in schema:
        if kw not in _SUPPORTED and kw not in _IGNORED:
            errors.append("%s: WARN unknown/unsupported keyword %r — not enforced "
                          "(typo, or a constraint this subset does not implement)" % (path, kw))

    # --- type ---
    if "type" in schema:
        types = schema["type"]
        types = types if isinstance(types, list) else [types]
        results = [_type_ok(value, t) for t in types]
        if any(r is None for r in results):
            errors.append("%s: schema declares unknown type %r" % (path, schema["type"]))
        elif not any(results):
            errors.append("%s: expected type %s, got %s"
                          % (path, "/".join(types), _json_type_name(value)))
            return errors  # a type miss makes the per-type constraints below meaningless

    # --- enum ---
    if "enum" in schema and value not in schema["enum"]:
        errors.append("%s: value %r not in enum %s" % (path, value, schema["enum"]))

    # --- string constraints ---
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append("%s: string length %d < minLength %d" % (path, len(value), schema["minLength"]))
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append("%s: string length %d > maxLength %d" % (path, len(value), schema["maxLength"]))
        if "pattern" in schema:
            try:
                if re.search(schema["pattern"], value) is None:
                    errors.append("%s: %r does not match pattern %r" % (path, value, schema["pattern"]))
            except re.error as e:
                errors.append("%s: invalid pattern %r (%s)" % (path, schema["pattern"], e))

    # --- numeric constraints (bool excluded — true is not a number here) ---
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append("%s: %s < minimum %s" % (path, value, schema["minimum"]))
        if "maximum" in schema and value > schema["maximum"]:
            errors.append("%s: %s > maximum %s" % (path, value, schema["maximum"]))

    # --- object: required + properties ---
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append("%s: missing required property %r" % (path, req))
        props = schema.get("properties", {})
        for name, sub in props.items():
            if name in value:
                validate(value[name], sub, "%s.%s" % (path, name), errors)

    # --- array: items applied elementwise ---
    if isinstance(value, list) and "items" in schema:
        for i, el in enumerate(value):
            validate(el, schema["items"], "%s[%d]" % (path, i), errors)

    return errors


def _json_type_name(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, str):
        return "string"
    if isinstance(v, int):
        return "integer"
    if isinstance(v, float):
        return "number"
    if isinstance(v, list):
        return "array"
    if isinstance(v, dict):
        return "object"
    return type(v).__name__


# --- selftest fixtures -------------------------------------------------------------------------
SCHEMA = {
    "type": "object",
    "required": ["vendor", "invoice_number", "total", "status"],
    "properties": {
        "vendor": {"type": "string", "minLength": 1},
        "invoice_number": {"type": "string", "pattern": r"^INV-\d{4}-\d{4}$"},
        "total": {"type": "number", "minimum": 0},
        "status": {"type": "string", "enum": ["paid", "unpaid", "void"]},
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["description", "amount"],
                "properties": {
                    "description": {"type": "string"},
                    "amount": {"type": "number", "minimum": 0},
                },
            },
        },
        "notes": {"type": ["string", "null"]},   # nullable: null is the right way to say "absent"
    },
}

GOOD = {
    "vendor": "Acme Robotics Inc.",
    "invoice_number": "INV-2026-0042",
    "total": 13020.0,
    "status": "unpaid",
    "line_items": [{"description": "Widgets", "amount": 12000}],
    "notes": None,
}


def selftest():
    errs = []

    # 1. a conforming doc validates clean.
    e = validate(GOOD, SCHEMA)
    if e:
        errs.append("GOOD doc produced errors: %s" % e)

    # 2. each violation class is caught, and ONLY where expected.
    def viol(mut, needle, label):
        bad = json.loads(json.dumps(GOOD))
        mut(bad)
        es = validate(bad, SCHEMA)
        if not any(needle in x for x in es):
            errs.append("%s not caught (got %s)" % (label, es))

    viol(lambda d: d.update(total="lots"), "expected type", "type violation (string for number)")
    viol(lambda d: d.pop("status"), "missing required", "required-field omission")
    viol(lambda d: d.update(status="pending"), "not in enum", "enum violation")
    viol(lambda d: d.update(invoice_number="INV-42"), "does not match pattern", "pattern violation")
    viol(lambda d: d.update(total=-5), "< minimum", "minimum violation")
    viol(lambda d: d.update(vendor=""), "minLength", "minLength violation")
    viol(lambda d: d["line_items"].append({"description": "x"}), "missing required", "nested required (items)")
    viol(lambda d: d["line_items"].append({"description": "x", "amount": -1}), "< minimum", "nested minimum (items)")

    # 3. the nullable field accepts both null AND a string (type list), rejects a number.
    if validate(dict(GOOD, notes="see attachment"), SCHEMA):
        errs.append("nullable field rejected a string")
    if not validate(dict(GOOD, notes=5), SCHEMA):
        errs.append("nullable field accepted a number (type list should reject)")

    # 4. integer vs boolean: true must NOT validate as integer/number.
    if not validate(True, {"type": "integer"}):
        errs.append("boolean wrongly accepted as integer")
    if not validate(True, {"type": "number"}):
        errs.append("boolean wrongly accepted as number")
    if validate(True, {"type": "boolean"}):
        errs.append("boolean rejected as boolean")

    # 5. M2 — a typo'd / unsupported keyword must NOT be a silent no-op (it produces a false green).
    #     `requried` (typo of required), `minimun` (typo of minimum), and `additionalProperties`
    #     (unsupported) are all unenforced; the run must WARN on each and NOT report clean.
    typo_schema = {"type": "object", "requried": ["a"],
                   "properties": {"a": {"type": "number", "minimun": 0}},
                   "additionalProperties": False}
    es = validate({"a": -999}, typo_schema)
    for kw in ("requried", "minimun", "additionalProperties"):
        if not any("WARN" in x and ("%r" % kw) in x for x in es):
            errs.append("unknown keyword %r not WARNed (got %s) — typo defeats validation silently"
                        % (kw, es))
    if not es:
        errs.append("typo'd schema reported clean — false green (the M2 bug)")

    # 5b. a schema using ONLY supported + ignored keywords produces NO spurious unknown-keyword WARN.
    annotated = {"$schema": "x", "title": "t", "description": "d",
                 "type": "object", "properties": {"a": {"type": "number", "minimum": 0}}}
    es = validate({"a": 1}, annotated)
    if any("WARN" in x for x in es):
        errs.append("supported/ignored-only schema produced a spurious WARN: %s" % es)
    return errs


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("schema-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("schema-check: OK — conforming doc validates; type/required/enum/pattern/range/"
              "nullable/nested violations each caught; unknown/unsupported keywords WARNed")
        return 0
    if len(argv) < 2:
        sys.stderr.write("usage: schema-check.py <doc.json> <schema.json>\n")
        return 2
    try:
        doc = json.load(open(argv[0], encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write("schema-check: FAIL — doc is not well-formed JSON (B1): %s\n" % e)
        return 1
    try:
        schema = json.load(open(argv[1], encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write("cannot read schema: %s\n" % e)
        return 2
    errors = validate(doc, schema)
    warns = [e for e in errors if "WARN" in e]
    viols = [e for e in errors if "WARN" not in e]
    for e in viols:
        print("  %s" % e)
    for w in warns:
        print("  %s" % w)
    if errors:
        if viols and warns:
            sys.stderr.write("schema-check: FAIL — %d schema violation(s) and %d unenforced "
                             "keyword(s)\n" % (len(viols), len(warns)))
        elif viols:
            sys.stderr.write("schema-check: FAIL — %d schema violation(s)\n" % len(viols))
        else:
            sys.stderr.write("schema-check: FAIL — %d unknown/unsupported keyword(s) not enforced — "
                             "the schema cannot be fully checked (typo? unsupported constraint?); fix "
                             "or remove them before trusting a pass\n" % len(warns))
        return 1
    print("schema-check: OK — document conforms to the schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
