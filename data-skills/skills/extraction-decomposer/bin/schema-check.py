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
  patternProperties  {regex: subschema}  — each matching property is validated (and counts as "known"
                                           for additionalProperties)
  additionalProperties  false | subschema  — `false` forbids any property not named in `properties`
                        and not matched by `patternProperties`; a subschema constrains every such extra
                        property (the most common false-green keyword: an extractor adds an off-contract
                        field and an unenforced schema waves it through)
  items       subschema  — applied to every array element
  minItems / maxItems       — array length bounds (inclusive)
  uniqueItems true  — every array element must be distinct under type-aware deep equality (bool ≠ int)
  enum        [values]   — the value must be one of these
  const       value      — the value must deep-equal this (type-aware: 1 ≠ true)
  minimum / maximum         — numeric bounds (inclusive)
  minLength / maxLength     — string length bounds
  pattern     a regex the string must search-match
  $ref        "#/$defs/Name" or "#/definitions/Name"  — a SAME-DOCUMENT local reference only; the named
              subschema (under the ROOT schema's `$defs`/`definitions`) is resolved and applied in place.
              No remote/`http(s)`/file fetch — that would break the clean-checkout-true contract.

UNKNOWN / UNSUPPORTED keywords are NOT silent no-ops. A schema-author typo (`requried`, `minimun`) or
an unsupported keyword (`propertyNames`, `if`/`then`) that this subset doesn't enforce is the
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
    "type", "required", "properties", "patternProperties", "additionalProperties",
    "items", "minItems", "maxItems", "uniqueItems", "enum", "const",
    "minimum", "maximum", "minLength", "maxLength", "pattern", "$ref",
})
# meta / annotation keywords that legitimately carry no validation here — ignored, NOT warned.
# `$defs`/`definitions` hold subschemas resolved via `$ref`; they carry no validation at their own node.
_IGNORED = frozenset({
    "$schema", "$id", "$comment", "$defs", "definitions",
    "title", "description", "default", "examples",
})


def _type_ok(value, t):
    check = _TYPE_CHECKS.get(t)
    if check is None:
        return None   # unknown type name -> reported by validate as a schema error
    return check(value)


def _deep_equal(a, b):
    """Type-aware JSON deep equality. Crucially, a bool is NOT equal to an int/float of the same
    numeric value (in JSON `true` is not `1`), mirroring the integer/number type checks — so
    `uniqueItems`/`const` treat `[1, true]` as distinct and `1` as != `true`. `1 == 1.0` stays true
    (both are JSON numbers). Recurses structurally over lists and dicts."""
    if isinstance(a, bool) or isinstance(b, bool):
        # at least one is a bool -> equal only if both are bools with the same value
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return a == b   # 1 == 1.0 across int/float (both JSON "number")
    if type(a) is not type(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(_deep_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(_deep_equal(a[k], b[k]) for k in a)
    return a == b


def _resolve_ref(ref, root, path, errors):
    """Resolve a SAME-DOCUMENT local `$ref` against `root`. Supports `#/$defs/Name`,
    `#/definitions/Name`, and the bare root pointer `#`. Returns the referenced subschema, or None
    after appending a schema error (a remote ref, a bad pointer, or a missing target). No network/file
    fetch — that would break the clean-checkout-true contract."""
    if not isinstance(ref, str):
        errors.append("%s: $ref must be a string, got %r" % (path, ref))
        return None
    if not ref.startswith("#"):
        errors.append("%s: $ref %r is not a same-document reference (only '#/$defs/Name' / "
                      "'#/definitions/Name' are supported — no remote fetch)" % (path, ref))
        return None
    pointer = ref[1:]            # drop the leading '#'
    if pointer in ("", "/"):
        return root              # '#' -> the whole root schema
    if not pointer.startswith("/"):
        errors.append("%s: malformed $ref %r (expected '#/<segment>/...')" % (path, ref))
        return None
    node = root
    for raw in pointer[1:].split("/"):
        # JSON-Pointer unescaping: ~1 -> '/', ~0 -> '~'
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict) and token in node:
            node = node[token]
        elif isinstance(node, list):
            try:
                node = node[int(token)]
            except (ValueError, IndexError):
                errors.append("%s: $ref %r does not resolve (no element %r)" % (path, ref, token))
                return None
        else:
            errors.append("%s: $ref %r does not resolve (no '%s' under the root schema)"
                          % (path, ref, token))
            return None
    if not isinstance(node, dict):
        errors.append("%s: $ref %r resolves to a non-object schema node" % (path, ref))
        return None
    return node


def validate(value, schema, path="$", errors=None, root=None):
    """Validate `value` against `schema`. Appends "<path>: <message>" strings to `errors`.

    A `WARN: ... unknown/unsupported keyword 'X' — not enforced` line is appended for any keyword the
    validator does not implement (a typo or an unsupported constraint that would otherwise be a SILENT
    no-op → false green). Warnings count toward a nonzero exit, since a schema that can't be fully
    enforced must not report a clean pass."""
    if errors is None:
        errors = []
    if root is None:
        root = schema   # the first schema node is the document root that $ref resolves against
    if not isinstance(schema, dict):
        errors.append("%s: schema node is not an object" % path)
        return errors

    # --- $ref: resolve a same-document reference and validate against the target in place ---
    # (JSON Schema treats a node with $ref as a reference; we resolve it and apply the referenced
    #  subschema. Sibling keywords alongside $ref are not composed in this subset.)
    if "$ref" in schema:
        target = _resolve_ref(schema["$ref"], root, path, errors)
        if target is not None:
            validate(value, target, path, errors, root)
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

    # --- enum (membership via type-aware deep equality, so 1 does not satisfy an enum of [true]) ---
    if "enum" in schema and not any(_deep_equal(value, opt) for opt in schema["enum"]):
        errors.append("%s: value %r not in enum %s" % (path, value, schema["enum"]))

    # --- const (the value must deep-equal the const; type-aware, so 1 != true) ---
    if "const" in schema and not _deep_equal(value, schema["const"]):
        errors.append("%s: value %r != const %r" % (path, value, schema["const"]))

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

    # --- object: required + properties + patternProperties + additionalProperties ---
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append("%s: missing required property %r" % (path, req))
        props = schema.get("properties", {})
        for name, sub in props.items():
            if name in value:
                validate(value[name], sub, "%s.%s" % (path, name), errors, root)
        # patternProperties: validate each property whose NAME matches the regex.
        pattern_props = schema.get("patternProperties", {})
        compiled = []
        for rx, sub in pattern_props.items():
            try:
                compiled.append((re.compile(rx), sub))
            except re.error as e:
                errors.append("%s: invalid patternProperties regex %r (%s)" % (path, rx, e))
        for name, val in value.items():
            for crx, sub in compiled:
                if crx.search(name):
                    validate(val, sub, "%s.%s" % (path, name), errors, root)
        # additionalProperties: a property neither named in `properties` nor matched by any
        # patternProperties regex. `false` forbids any such extra; a subschema constrains each.
        if "additionalProperties" in schema:
            ap = schema["additionalProperties"]
            for name, val in value.items():
                if name in props:
                    continue
                if any(crx.search(name) for crx, _ in compiled):
                    continue
                if ap is False:
                    errors.append("%s: additional property %r is not allowed "
                                  "(additionalProperties: false)" % (path, name))
                elif isinstance(ap, dict):
                    validate(val, ap, "%s.%s" % (path, name), errors, root)
                # ap is True (or any other truthy) -> extras are unconstrained; nothing to check.

    # --- array: items elementwise + length bounds + uniqueItems ---
    if isinstance(value, list):
        if "items" in schema:
            for i, el in enumerate(value):
                validate(el, schema["items"], "%s[%d]" % (path, i), errors, root)
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append("%s: array length %d < minItems %d" % (path, len(value), schema["minItems"]))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append("%s: array length %d > maxItems %d" % (path, len(value), schema["maxItems"]))
        if schema.get("uniqueItems") is True:
            for i in range(len(value)):
                for j in range(i + 1, len(value)):
                    if _deep_equal(value[i], value[j]):
                        errors.append("%s: array items must be unique — %r at [%d] duplicates [%d]"
                                      % (path, value[i], j, i))
                        break

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

    # 5. M2 — a typo'd / still-unsupported keyword must NOT be a silent no-op (it produces a false
    #     green). `requried` (typo of required), `minimun` (typo of minimum), and `propertyNames`
    #     (a real JSON-Schema keyword this subset still does not enforce) are all unenforced; the run
    #     must WARN on each and NOT report clean. (`additionalProperties` is now ENFORCED — it must
    #     no longer appear as an unknown-keyword WARN; covered by 5c below.)
    typo_schema = {"type": "object", "requried": ["a"],
                   "properties": {"a": {"type": "number", "minimun": 0}},
                   "propertyNames": {"pattern": "^x"}}
    es = validate({"a": -999}, typo_schema)
    for kw in ("requried", "minimun", "propertyNames"):
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

    # small assertion helpers for the new-keyword fixtures.
    def ok(value, schema, label):
        es = validate(value, schema)
        if es:
            errs.append("%s: legal instance rejected (got %s)" % (label, es))

    def reject(value, schema, needle, label):
        es = validate(value, schema)
        if not any(needle in x for x in es):
            errs.append("%s: illegal instance not rejected (got %s)" % (label, es))
        if any("WARN" in x for x in es):
            errs.append("%s: NOW-ENFORCED keyword still WARNed as unsupported (got %s)" % (label, es))

    # 5c. additionalProperties — false forbids extras; a subschema constrains every extra.
    ap_false = {"type": "object", "properties": {"a": {"type": "string"}},
                "additionalProperties": False}
    ok({"a": "x"}, ap_false, "additionalProperties:false (no extra)")
    reject({"a": "x", "b": 1}, ap_false, "not allowed", "additionalProperties:false (extra present)")
    ap_str = {"type": "object", "properties": {"a": {"type": "string"}},
              "additionalProperties": {"type": "string"}}
    ok({"a": "x", "extra": "ok"}, ap_str, "additionalProperties:{string} (string extra)")
    reject({"a": "x", "extra": 7}, ap_str, "expected type",
           "additionalProperties:{string} (number extra)")
    # patternProperties names a property as known, so additionalProperties:false lets it through.
    ap_pat = {"type": "object", "properties": {"a": {"type": "string"}},
              "patternProperties": {"^x_": {"type": "number"}}, "additionalProperties": False}
    ok({"a": "s", "x_count": 3}, ap_pat, "patternProperties match (known via pattern)")
    reject({"a": "s", "x_count": "no"}, ap_pat, "expected type",
           "patternProperties subschema (wrong type)")
    reject({"a": "s", "y_other": 1}, ap_pat, "not allowed",
           "additionalProperties:false past patternProperties")

    # 5d. uniqueItems — distinct ok; a dup rejected; bool != int (no phantom dup).
    uniq = {"type": "array", "uniqueItems": True}
    ok([1, 2, 3], uniq, "uniqueItems ([1,2,3] distinct)")
    reject([1, 2, 2], uniq, "must be unique", "uniqueItems ([1,2,2] dup)")
    ok([1, True], uniq, "uniqueItems ([1,true] — bool != int, not a dup)")
    reject([True, True], uniq, "must be unique", "uniqueItems ([true,true] dup)")
    ok([{"a": 1}, {"a": 2}], uniq, "uniqueItems (distinct objects)")
    reject([{"a": 1}, {"a": 1}], uniq, "must be unique", "uniqueItems (deep-equal objects)")

    # 5e. minItems / maxItems — boundary cases (inclusive bounds).
    bounds = {"type": "array", "minItems": 2, "maxItems": 3}
    ok([1, 2], bounds, "minItems boundary (==2)")
    ok([1, 2, 3], bounds, "maxItems boundary (==3)")
    reject([1], bounds, "< minItems", "minItems (1 < 2)")
    reject([1, 2, 3, 4], bounds, "> maxItems", "maxItems (4 > 3)")

    # 5f. const — exact match ok; near-miss rejected; 1 != true (type-aware).
    ok("EUR", {"const": "EUR"}, "const string match")
    reject("USD", {"const": "EUR"}, "!= const", "const string near-miss")
    ok(1, {"const": 1}, "const int match")
    reject(True, {"const": 1}, "!= const", "const (true is not 1)")
    reject(1, {"const": True}, "!= const", "const (1 is not true)")
    ok({"k": [1, 2]}, {"const": {"k": [1, 2]}}, "const deep-equal object")
    reject({"k": [1, 3]}, {"const": {"k": [1, 2]}}, "!= const", "const deep object near-miss")

    # 5g. $ref / $defs — an instance validated THROUGH a #/$defs/X reference (same-document only).
    ref_schema = {
        "type": "object",
        "properties": {"price": {"$ref": "#/$defs/Money"},
                       "ship":  {"$ref": "#/definitions/Money"}},
        "$defs": {"Money": {"type": "number", "minimum": 0}},
        "definitions": {"Money": {"type": "number", "minimum": 0}},
    }
    ok({"price": 10, "ship": 0}, ref_schema, "$ref through $defs + definitions")
    reject({"price": -1, "ship": 5}, ref_schema, "< minimum", "$ref enforces target constraint")
    reject({"price": "free", "ship": 5}, ref_schema, "expected type", "$ref enforces target type")
    # a $ref'd schema using ONLY supported keywords must not WARN.
    es = validate({"price": 10, "ship": 0}, ref_schema)
    if any("WARN" in x for x in es):
        errs.append("$ref/$defs schema produced a spurious WARN: %s" % es)
    # a remote / unresolvable $ref is a schema error, not a silent pass.
    es = validate({}, {"$ref": "https://example.com/x.json"})
    if not any("not a same-document reference" in x for x in es):
        errs.append("remote $ref not flagged (got %s) — would break clean-checkout-true" % es)
    es = validate({}, {"$ref": "#/$defs/Missing"})
    if not any("does not resolve" in x for x in es):
        errs.append("unresolvable local $ref not flagged (got %s)" % es)

    # 5h. the still-unsupported-WARN guarantee survives the new keywords: a genuinely unknown keyword
    #     (here `if`, a conditional this subset does not do) still WARNs and is not a silent no-op.
    es = validate(1, {"if": {"type": "string"}})
    if not any("WARN" in x and ("%r" % "if") in x for x in es):
        errs.append("still-unsupported keyword 'if' no longer WARNed — silent no-op regression")

    return errs


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("schema-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("schema-check: OK — conforming doc validates; type/required/enum/const/pattern/range/"
              "nullable/nested + additionalProperties/uniqueItems/min-maxItems/$ref violations each "
              "caught; still-unsupported keywords WARNed")
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
