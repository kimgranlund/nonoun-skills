#!/usr/bin/env python3
"""instance-check.py — the type-decomposer state-space gate. Self-contained (stdlib only).

A type's real meaning is the SET of values it admits, not its field names. "Make illegal states
unrepresentable" is a claim you cannot eyeball — you PROVE it by feeding the model both a LEGAL
instance set (every one must validate) and an ILLEGAL instance set (every one must be REJECTED).
An illegal instance that validates is the signature failure: an illegal state IS representable.

This carries a JSON-Schema SUBSET validator big enough to express the tools that make illegal
states unrepresentable — `oneOf` (tagged unions), `additionalProperties:false` (closed records),
`const`/`enum`, `required`, `not`, `allOf`/`anyOf`, `if`/`then`/`else` (cross-field conditional
legality), `patternProperties` (name-keyed subschemas), `propertyNames` (every property NAME must
validate as a string), `dependentRequired` (presence-triggered required), `dependentSchemas`
(presence-triggered whole-instance subschema), the array `contains` with `minContains`/`maxContains`
(bounded existence), `pattern`, an asserting `format` set (email/uri/url/uuid/date/date-time), and
local `$ref` into `#/$defs`/`#/definitions` — then runs a spec of legal/illegal instances against it.

DEFAULT-DENY: this is a SUBSET, so any keyword it does not understand (`unevaluatedProperties`,
`unevaluatedItems`, `prefixItems`, tuple-`items`, a remote `$ref`, …) raises and surfaces as an
UNSUPPORTED_SCHEMA finding — a LOUD failure — rather than being silently ignored. A silent ignore
would drop a real constraint and let an illegal instance false-green; the gate's whole value is
being a trustworthy rejecter.

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

# Keywords this subset validator UNDERSTANDS. Anything else (a remote $ref, a tuple-form items,
# prefixItems, unevaluatedProperties/unevaluatedItems, …) must FAIL LOUD via default-deny — never
# be silently ignored, which would drop a real constraint and false-green an illegal instance.
_KNOWN = frozenset({
    "type", "const", "enum", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "multipleOf", "minLength", "maxLength", "pattern", "format", "minItems", "maxItems",
    "uniqueItems", "items", "contains", "minContains", "maxContains",
    "properties", "patternProperties", "propertyNames", "required",
    "dependentRequired", "dependentSchemas", "additionalProperties",
    "allOf", "anyOf", "oneOf", "not", "if", "then", "else",
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
        if "contains" in schema:
            # `contains` asserts a BOUNDED count of matching elements. The element subschema reuses
            # validate(), so type-aware equality / format / $ref / required all apply inside it.
            # Count the matches once, then refine with minContains/maxContains:
            #   minContains (default 1) ≤ matches ≤ maxContains (default ∞).
            # minContains:0 makes `contains` pass even with ZERO matches (it relaxes the existence
            # floor to "no constraint on the low end" — only maxContains then bites).
            n = sum(1 for item in v if not validate(item, schema["contains"], path, root))
            lo = schema.get("minContains", 1)
            hi = schema.get("maxContains")
            if n < lo:
                errs.append("%s: only %d element(s) match `contains` (minContains %s)"
                            % (path, n, lo))
            if hi is not None and n > hi:
                errs.append("%s: %d element(s) match `contains` (maxContains %s)" % (path, n, hi))
    if kind == "object":
        props = schema.get("properties", {})
        pat_props = schema.get("patternProperties", {})
        for k in schema.get("required", []):
            if k not in v:
                errs.append("%s: missing required '%s'" % (path, k))
        ap = schema.get("additionalProperties", True)
        # Pre-compile the patternProperties regexes once. JSON Schema uses re.search (the pattern is
        # NOT implicitly anchored), so `^x-` matches a leading `x-` and a bare `x-` matches anywhere
        # in the name — anchor explicitly in the pattern if a full-name match is intended.
        pat_compiled = [(re.compile(p), sub) for p, sub in pat_props.items()]
        for k, val in v.items():
            covered = False
            if k in props:
                errs += validate(val, props[k], "%s.%s" % (path, k), root)
                covered = True
            # Every property whose NAME matches a patternProperties regex must validate against that
            # subschema (independent of, and combinable with, `properties` — a key can be governed by
            # both). A property covered by neither is unconstrained unless additionalProperties bites.
            for rx, sub in pat_compiled:
                if rx.search(k):
                    errs += validate(val, sub, "%s.%s" % (path, k), root)
                    covered = True
            if covered:
                continue
            if ap is False:
                errs.append("%s: additional property '%s' not allowed (closed record)" % (path, k))
            elif isinstance(ap, dict):
                errs += validate(val, ap, "%s.%s" % (path, k), root)
        # propertyNames: every property NAME is validated — as a STRING instance — against the
        # subschema. The name string reuses validate(), so `pattern`/`format`/`minLength`/enum all
        # apply to the key. A key that fails the name schema is an illegal key (e.g. `Foo` or `a1`
        # under {"pattern":"^[a-z]+$"}).
        if "propertyNames" in schema:
            for k in v:
                errs += validate(k, schema["propertyNames"], "%s/(propertyName %r)" % (path, k), root)
        # dependentRequired: if the trigger property is present, every listed dependent must be too.
        for trigger, deps in schema.get("dependentRequired", {}).items():
            if trigger in v:
                for dep in deps:
                    if dep not in v:
                        errs.append("%s: '%s' present but dependent '%s' missing" % (path, trigger, dep))
        # dependentSchemas: if the trigger property is present, the WHOLE instance must additionally
        # validate against the dependent subschema (sibling to dependentRequired, but an arbitrary
        # schema, not just a required list). Recurses the whole instance through validate().
        for trigger, sub in schema.get("dependentSchemas", {}).items():
            if trigger in v:
                errs += validate(v, sub, path, root)

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
    if "if" in schema:
        # Conditional: if the instance validates against `if`, it must validate against `then`;
        # otherwise against `else`. Each branch is optional — `if` failing with no `else` is a
        # pass; `if` holding with no `then` is a pass. A bare `then`/`else` with no `if` is inert
        # (JSON Schema annotation-only), so this whole block is gated on `if` being present.
        if validate(v, schema["if"], path, root):
            # `if` did not hold → the `else` branch governs (if present).
            if "else" in schema:
                errs += validate(v, schema["else"], path, root)
        else:
            # `if` held → the `then` branch governs (if present).
            if "then" in schema:
                errs += validate(v, schema["then"], path, root)
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
# silent green. `prefixItems` is not in the subset (patternProperties, then propertyNames, were the
# witnesses here until each joined the supported set — prefixItems is still out).
UNSUPPORTED_SPEC = {
    "schema": {"type": "array", "prefixItems": [{"type": "string"}]},
    "legal": [["ok"]],
    "illegal": [[5]],
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
# C1 (oneOf tagged union, EXACTLY-one): a tagged union of two closed records. A valid A and a valid
# B each match exactly one branch (legal). An instance matching BOTH branches or NEITHER is rejected
# — the discriminated-union contract is exactly-one, not at-least-one.
ONEOF_UNION = {
    "schema": {
        "oneOf": [
            {"type": "object", "additionalProperties": False, "required": ["tag", "a"],
             "properties": {"tag": {"const": "a"}, "a": {"type": "integer"}}},
            {"type": "object", "additionalProperties": False, "required": ["tag", "b"],
             "properties": {"tag": {"const": "b"}, "b": {"type": "string"}}},
        ],
    },
    "legal": [{"tag": "a", "a": 1}, {"tag": "b", "b": "x"}],
    "illegal": [
        # Matches NEITHER branch (closed records reject the foreign field, so no branch holds).
        {"tag": "a", "a": 1, "b": "x"},
        # Matches NEITHER: unknown tag, no branch's const holds.
        {"tag": "c"},
        {},
    ],
}
# C1b (oneOf BOTH-match → rejected): two open, overlapping branches. An instance satisfying both is
# ambiguous and must be rejected (need exactly 1, not ≥1) — the headline oneOf-vs-anyOf distinction.
ONEOF_BOTH = {
    "schema": {
        "oneOf": [
            {"type": "object", "required": ["a"], "properties": {"a": {"type": "integer"}}},
            {"type": "object", "required": ["b"], "properties": {"b": {"type": "integer"}}},
        ],
    },
    "legal": [{"a": 1}, {"b": 2}],
    "illegal": [{"a": 1, "b": 2}],  # satisfies BOTH branches → ambiguous → rejected
}
# C2 (if/then/else): cross-field conditional legality. A card must carry a `number`; a non-card must
# carry an `account`. `if` selects the branch; the recursion means `required`/`const` apply inside.
IF_THEN_ELSE = {
    "schema": {
        "type": "object",
        "if": {"properties": {"kind": {"const": "card"}}, "required": ["kind"]},
        "then": {"required": ["number"]},
        "else": {"required": ["account"]},
    },
    "legal": [
        {"kind": "card", "number": "4111"},   # if holds → then satisfied
        {"kind": "bank", "account": "GB123"},  # if fails → else satisfied
    ],
    "illegal": [
        {"kind": "card"},                       # if holds → then requires number (missing)
        {"kind": "bank", "number": "4111"},     # if fails → else requires account (missing)
    ],
}
# C2b (if with no else): `if` failing with no `else` is a PASS; `if` holding still imposes `then`.
IF_NO_ELSE = {
    "schema": {
        "type": "object",
        "if": {"required": ["premium"], "properties": {"premium": {"const": True}}},
        "then": {"required": ["billing"]},
    },
    "legal": [
        {"premium": True, "billing": "x"},  # if holds → then satisfied
        {"premium": False},                 # if fails, no else → pass
        {},                                 # if fails (no premium), no else → pass
    ],
    "illegal": [{"premium": True}],         # if holds → then requires billing (missing)
}
# C3 (allOf): the instance must satisfy EVERY subschema; failing one is rejected.
ALLOF = {
    "schema": {
        "allOf": [
            {"type": "object", "required": ["a"], "properties": {"a": {"type": "integer", "minimum": 0}}},
            {"type": "object", "required": ["b"], "properties": {"b": {"type": "string", "minLength": 2}}},
        ],
    },
    "legal": [{"a": 1, "b": "xy"}],
    "illegal": [
        {"a": 1},               # fails the second half (b missing)
        {"a": -1, "b": "xy"},   # fails the first half (a < minimum)
        {"a": 1, "b": "x"},     # fails the second half (b too short)
    ],
}
# C4 (anyOf): satisfying AT LEAST ONE subschema passes; satisfying none is rejected.
ANYOF = {
    "schema": {
        "anyOf": [
            {"type": "object", "required": ["email"], "properties": {"email": {"type": "string", "format": "email"}}},
            {"type": "object", "required": ["phone"], "properties": {"phone": {"type": "string", "minLength": 7}}},
        ],
    },
    "legal": [{"email": "a@b.co"}, {"phone": "1234567"}, {"email": "a@b.co", "phone": "1234567"}],
    "illegal": [
        {},                                  # matches neither (both contacts missing)
        {"email": "nope", "phone": "12"},    # email invalid AND phone too short → neither holds
    ],
}
# C5 (not): an instance of the FORBIDDEN shape is rejected; another passes. The negated subschema
# recurses, so the forbidden `const` is type-aware.
NOT = {
    "schema": {"type": "object", "not": {"required": ["banned"], "properties": {"banned": {"const": True}}}},
    "legal": [{"ok": 1}, {"banned": False}],
    "illegal": [{"banned": True}],  # is the forbidden shape → rejected
}
# C6 (default-deny PRESERVED): a still-unknown keyword (`prefixItems`) must STILL raise
# UNSUPPORTED_SCHEMA — adding propertyNames/dependentSchemas/min-maxContains did NOT open the gate to
# everything. (`contains`, then `propertyNames`, USED to be the witness here; now that both are
# supported, `prefixItems` is.)
STILL_UNSUPPORTED = {
    "schema": {"type": "array", "prefixItems": [{"type": "integer"}]},
    "legal": [[1]],
    "illegal": [["x"]],
}
# D1 (patternProperties): every property whose NAME matches the regex must validate against the
# subschema. An `x-foo: "ok"` (string) passes; `x-foo: 5` (number) is rejected; a property NOT
# matching the pattern (`y`) is unaffected. Combines with `properties`/`required` as usual.
PATTERN_PROPERTIES = {
    "schema": {"type": "object", "patternProperties": {"^x-": {"type": "string"}}},
    "legal": [
        {"x-foo": "ok"},                  # matches ^x- and is a string → valid
        {"x-foo": "ok", "y": 5},          # `y` does not match the pattern → unconstrained
        {"y": 5},                         # nothing matches → vacuously valid
    ],
    "illegal": [
        {"x-foo": 5},                     # matches ^x- but is a number → rejected
        {"x-foo": "ok", "x-bar": 7},      # x-bar matches ^x- but is a number → rejected
    ],
}
# D1b (patternProperties + closed record): a key matched by patternProperties is "covered", so
# additionalProperties:false must NOT flag it. A key matched by NEITHER properties NOR a pattern is
# still an illegal extra field on a closed record.
PATTERN_PROPERTIES_CLOSED = {
    "schema": {"type": "object", "additionalProperties": False,
               "required": ["name"],
               "properties": {"name": {"type": "string"}},
               "patternProperties": {"^x-": {"type": "string"}}},
    "legal": [
        {"name": "a"},                    # only the declared property
        {"name": "a", "x-trace": "id1"},  # x-trace matched by patternProperties → allowed
    ],
    "illegal": [
        {"name": "a", "other": 1},        # `other` matches neither → closed-record violation
        {"name": "a", "x-trace": 9},      # matched by pattern but wrong type → rejected
    ],
}
# D2 (contains): the array must have AT LEAST ONE element validating against the subschema (the
# default minContains 1). [1,2,"x"] has integers → passes; ["a","b"] has none → rejected.
CONTAINS = {
    "schema": {"type": "array", "contains": {"type": "integer"}},
    "legal": [[1, 2, "x"], [5], ["a", 3]],
    "illegal": [["a", "b"], [], [1.5, "x"]],  # no integer element (1.5 is not an integer)
}
# D3 (dependentRequired): if the trigger property is present, every listed dependent must be too.
# {credit_card, billing_address} passes; {credit_card} alone is rejected; {} (no trigger) passes.
DEPENDENT_REQUIRED = {
    "schema": {"type": "object",
               "dependentRequired": {"credit_card": ["billing_address"]}},
    "legal": [
        {"credit_card": "4111", "billing_address": "1 Main St"},  # trigger + dependent present
        {},                                                       # no trigger → no obligation
        {"billing_address": "1 Main St"},                         # dependent without trigger → fine
    ],
    "illegal": [
        {"credit_card": "4111"},                                  # trigger present, dependent missing
    ],
}
# D4 (propertyNames): every property NAME must validate as a STRING instance against the subschema.
# Under {pattern:"^[a-z]+$"} a key `Foo` (uppercase) or `a1` (digit) is an illegal key; lowercase
# keys pass. The empty object is vacuously valid (no names to check).
PROPERTY_NAMES = {
    "schema": {"type": "object", "propertyNames": {"pattern": "^[a-z]+$"}},
    "legal": [
        {"a": 1, "b": 2},                 # all names lowercase letters → valid
        {},                               # no names → vacuously valid
    ],
    "illegal": [
        {"A": 1},                         # uppercase name → rejected
        {"a1": 1},                        # digit in name → rejected
        {"a": 1, "B": 2},                 # one bad name spoils it
    ],
}
# D5 (dependentSchemas): if the trigger property is present, the WHOLE instance must additionally
# validate against the dependent subschema. {cc} alone is rejected (the dependent schema requires
# `billing`); {cc, billing} passes; {} (no trigger) passes. Sibling to dependentRequired.
DEPENDENT_SCHEMAS = {
    "schema": {"type": "object",
               "dependentSchemas": {"credit_card": {"required": ["billing"]}}},
    "legal": [
        {"credit_card": "x", "billing": "y"},  # trigger present, dependent schema satisfied
        {},                                    # no trigger → dependent schema not applied
        {"billing": "y"},                      # dependent's required field present, no trigger → fine
    ],
    "illegal": [
        {"credit_card": "x"},                  # trigger present, dependent schema's required missing
    ],
}
# D6 (minContains/maxContains): refine `contains` with a bounded match count.
# minContains:2 needs ≥2 matching elements; [1,2,"a"] (2 ints) passes, [1,"a"] (1 int) is rejected.
MIN_CONTAINS = {
    "schema": {"type": "array", "contains": {"type": "integer"}, "minContains": 2},
    "legal": [[1, 2, "a"], [1, 2, 3]],
    "illegal": [[1, "a"], ["a", "b"], []],   # 1, 0, 0 matches respectively → all < 2
}
# maxContains:1 caps the match count; default minContains is still 1, so exactly-one int passes.
# [1,"a"] (1 int) passes; [1,2] (2 ints) exceeds maxContains; ["a","b"] (0 ints) misses the default
# floor of 1 — both ends bite.
MAX_CONTAINS = {
    "schema": {"type": "array", "contains": {"type": "integer"}, "maxContains": 1},
    "legal": [[1, "a"], [5]],                # exactly 1 match each
    "illegal": [[1, 2], ["a", "b"]],         # 2 matches (> max) and 0 matches (< default min 1)
}
# minContains:0 relaxes the existence floor — `contains` passes even with ZERO matches (only
# maxContains, if present, then bites). An array with no integer is now LEGAL.
MIN_CONTAINS_ZERO = {
    "schema": {"type": "array", "contains": {"type": "integer"}, "minContains": 0},
    "legal": [[], ["a", "b"], [1, 2, 3]],    # 0, 0, 3 matches → all ≥ 0 (no floor)
    "illegal": [],
}
# minContains:0 + maxContains:1 — zero floor, but at most one match. [] and [1] pass; [1,2] rejected.
MIN_ZERO_MAX_ONE = {
    "schema": {"type": "array", "contains": {"type": "integer"},
               "minContains": 0, "maxContains": 1},
    "legal": [[], ["a"], [1, "a"]],          # 0, 0, 1 matches
    "illegal": [[1, 2]],                     # 2 matches → exceeds maxContains 1
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

    # C1 — oneOf is EXACTLY-one: valid A and valid B pass; neither-match is rejected. CLEAN.
    f, _ = check_spec(ONEOF_UNION)
    if f:
        errs.append("ONEOF_UNION not clean — oneOf tagged union not exactly-one: %s" % f)
    # C1b — an instance matching BOTH branches must be rejected (oneOf ≠ anyOf). CLEAN.
    f, _ = check_spec(ONEOF_BOTH)
    if f:
        errs.append("ONEOF_BOTH not clean — oneOf accepted a both-branch (ambiguous) match: %s" % f)
    # C2 — if/then/else routes to the right branch; required applies inside. CLEAN.
    f, _ = check_spec(IF_THEN_ELSE)
    if f:
        errs.append("IF_THEN_ELSE not clean — conditional branch not enforced: %s" % f)
    # C2b — if failing with no else is a pass; if holding still imposes then. CLEAN.
    f, _ = check_spec(IF_NO_ELSE)
    if f:
        errs.append("IF_NO_ELSE not clean — bare if/then semantics wrong: %s" % f)
    # C3 — allOf requires EVERY subschema; failing one is rejected. CLEAN.
    f, _ = check_spec(ALLOF)
    if f:
        errs.append("ALLOF not clean — allOf did not require every subschema: %s" % f)
    # C4 — anyOf requires AT LEAST ONE; none is rejected. CLEAN.
    f, _ = check_spec(ANYOF)
    if f:
        errs.append("ANYOF not clean — anyOf did not require at least one subschema: %s" % f)
    # C5 — not rejects the forbidden shape, passes others. CLEAN.
    f, _ = check_spec(NOT)
    if f:
        errs.append("NOT not clean — 'not' did not reject the forbidden shape: %s" % f)
    # C6 — DEFAULT-DENY PRESERVED: a still-unknown keyword (`propertyNames`) must FAIL LOUD, not be
    # silently allowed — proof the three new keywords didn't open the gate to everything.
    f, _ = check_spec(STILL_UNSUPPORTED)
    if not any(k == "UNSUPPORTED_SCHEMA" for k, _ in f):
        errs.append("STILL_UNSUPPORTED did not fail loud — default-deny was opened too wide: %s" % f)

    # D1 — patternProperties: name-matched props validate against the subschema; non-matching props
    # are unaffected. CLEAN.
    f, _ = check_spec(PATTERN_PROPERTIES)
    if f:
        errs.append("PATTERN_PROPERTIES not clean — patternProperties not enforced by name: %s" % f)
    # D1b — a patternProperties-matched key is "covered", so additionalProperties:false must not flag
    # it; a key matched by neither is still a closed-record violation. CLEAN.
    f, _ = check_spec(PATTERN_PROPERTIES_CLOSED)
    if f:
        errs.append("PATTERN_PROPERTIES_CLOSED not clean — pattern key wrongly flagged / closed "
                    "record not enforced: %s" % f)
    # D2 — contains: at least one element must match the subschema; an array with none is rejected.
    # CLEAN.
    f, _ = check_spec(CONTAINS)
    if f:
        errs.append("CONTAINS not clean — `contains` at-least-one semantics wrong: %s" % f)
    # D3 — dependentRequired: trigger present → dependents required; no trigger → no obligation.
    # CLEAN.
    f, _ = check_spec(DEPENDENT_REQUIRED)
    if f:
        errs.append("DEPENDENT_REQUIRED not clean — presence-triggered required not enforced: %s" % f)
    # D4 — propertyNames: every property NAME must validate (as a string) against the subschema; a
    # name failing the pattern is an illegal key. CLEAN.
    f, _ = check_spec(PROPERTY_NAMES)
    if f:
        errs.append("PROPERTY_NAMES not clean — property-name subschema not enforced: %s" % f)
    # D5 — dependentSchemas: trigger present → the whole instance must validate against the dependent
    # subschema; no trigger → not applied. CLEAN.
    f, _ = check_spec(DEPENDENT_SCHEMAS)
    if f:
        errs.append("DEPENDENT_SCHEMAS not clean — presence-triggered subschema not enforced: %s" % f)
    # D6 — minContains: the match count must be ≥ minContains; too-few matches is rejected. CLEAN.
    f, _ = check_spec(MIN_CONTAINS)
    if f:
        errs.append("MIN_CONTAINS not clean — minContains lower bound not enforced: %s" % f)
    # D6 — maxContains: the match count must be ≤ maxContains; too-many matches is rejected. CLEAN.
    f, _ = check_spec(MAX_CONTAINS)
    if f:
        errs.append("MAX_CONTAINS not clean — maxContains upper bound not enforced: %s" % f)
    # D6 — minContains:0 relaxes the existence floor — zero matches now passes. CLEAN.
    f, _ = check_spec(MIN_CONTAINS_ZERO)
    if f:
        errs.append("MIN_CONTAINS_ZERO not clean — minContains:0 did not relax the floor: %s" % f)
    # D6 — minContains:0 + maxContains:1 — zero floor but at most one match. CLEAN.
    f, _ = check_spec(MIN_ZERO_MAX_ONE)
    if f:
        errs.append("MIN_ZERO_MAX_ONE not clean — combined min:0/max:1 bound wrong: %s" % f)

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
    # B2 default-deny: an unsupported keyword raises rather than silently validating. `prefixItems`
    # is still outside the subset (patternProperties, then propertyNames, used to be the witness here
    # — both are now supported, so prefixItems carries the test).
    try:
        validate(["ok"], {"type": "array", "prefixItems": [{"type": "string"}]})
        errs.append("unsupported keyword did not raise (silent false-green)")
    except SchemaError:
        pass
    # additionalProperties / oneOf still hold
    if not validate({"a": 1}, {"type": "object", "additionalProperties": False}):
        errs.append("additionalProperties:false not enforced")
    if validate("card", {"oneOf": [{"const": "card"}, {"const": "cash"}]}):
        errs.append("oneOf exact-one not satisfied for a valid tag")
    # oneOf rejects a both-branch match (overlapping schemas) — exactly-one, not at-least-one
    if validate(5, {"oneOf": [{"type": "integer"}, {"minimum": 0}]}) == []:
        errs.append("oneOf accepted a value matching two branches")
    # if/then/else recursion: required inside `then` must be enforced via the same validate()
    _cond = {"if": {"required": ["k"], "properties": {"k": {"const": "card"}}}, "then": {"required": ["n"]}}
    if validate({"k": "card"}, _cond) == []:
        errs.append("if/then did not enforce `then` required when `if` held")
    if validate({"k": "card", "n": 1}, _cond):
        errs.append("if/then wrongly rejected a satisfying instance")
    if validate({"k": "x"}, _cond):
        errs.append("if/then wrongly applied `then` when `if` failed (no else → should pass)")
    # if/else: `if` failing routes to `else`
    if validate({}, {"if": {"required": ["a"]}, "else": {"required": ["b"]}}) == []:
        errs.append("if/else did not enforce `else` when `if` failed")
    # bare then/else with no `if` is inert (annotation-only), must not constrain
    if validate({}, {"then": {"required": ["x"]}, "else": {"required": ["y"]}}):
        errs.append("bare then/else (no if) wrongly constrained the instance")
    # patternProperties: a name-matched property is validated against the subschema; a non-matching
    # name is unconstrained. Use re.search (pattern is not auto-anchored).
    if validate({"x-a": "ok"}, {"type": "object", "patternProperties": {"^x-": {"type": "string"}}}):
        errs.append("patternProperties rejected a matching string property")
    if validate({"x-a": 5}, {"type": "object", "patternProperties": {"^x-": {"type": "string"}}}) == []:
        errs.append("patternProperties accepted a wrong-typed matching property")
    if validate({"y": 5}, {"type": "object", "patternProperties": {"^x-": {"type": "string"}}}):
        errs.append("patternProperties wrongly constrained a non-matching property")
    # patternProperties-matched key is "covered" → additionalProperties:false must not flag it
    if validate({"x-a": "ok"}, {"type": "object", "additionalProperties": False,
                                 "patternProperties": {"^x-": {"type": "string"}}}):
        errs.append("patternProperties key wrongly flagged by additionalProperties:false")
    if validate({"z": 1}, {"type": "object", "additionalProperties": False,
                           "patternProperties": {"^x-": {"type": "string"}}}) == []:
        errs.append("closed record wrongly accepted a key matched by neither")
    # contains: at least one element must match; an array with none is rejected
    if validate([1, 2, "x"], {"type": "array", "contains": {"type": "integer"}}):
        errs.append("contains rejected an array with a matching element")
    if validate(["a", "b"], {"type": "array", "contains": {"type": "integer"}}) == []:
        errs.append("contains accepted an array with no matching element")
    # dependentRequired: trigger present → dependents required; absent trigger → no obligation
    _dep = {"type": "object", "dependentRequired": {"credit_card": ["billing_address"]}}
    if validate({"credit_card": "x", "billing_address": "y"}, _dep):
        errs.append("dependentRequired rejected a satisfied dependency")
    if validate({"credit_card": "x"}, _dep) == []:
        errs.append("dependentRequired accepted a present trigger with a missing dependent")
    if validate({}, _dep):
        errs.append("dependentRequired wrongly required a dependent with no trigger present")
    # propertyNames: each key is validated as a STRING instance through the subschema; pattern applies
    _pn = {"type": "object", "propertyNames": {"pattern": "^[a-z]+$"}}
    if validate({"a": 1, "b": 2}, _pn):
        errs.append("propertyNames rejected an object whose names all match")
    if validate({"A": 1}, _pn) == []:
        errs.append("propertyNames accepted an object with a non-matching name")
    if validate({"a1": 1}, _pn) == []:
        errs.append("propertyNames accepted a name with a digit against ^[a-z]+$")
    if validate({}, _pn):
        errs.append("propertyNames wrongly rejected the empty object (no names → vacuous)")
    # propertyNames runs the name through the SAME validator, so format/minLength on the name apply
    if validate({"X": 1}, {"type": "object", "propertyNames": {"minLength": 2}}) == []:
        errs.append("propertyNames did not enforce minLength on the key string")
    # dependentSchemas: trigger present → whole instance must also satisfy the dependent subschema
    _ds = {"type": "object", "dependentSchemas": {"cc": {"required": ["billing"]}}}
    if validate({"cc": "x", "billing": "y"}, _ds):
        errs.append("dependentSchemas rejected a satisfied dependent subschema")
    if validate({"cc": "x"}, _ds) == []:
        errs.append("dependentSchemas accepted a trigger whose dependent subschema is unsatisfied")
    if validate({}, _ds):
        errs.append("dependentSchemas wrongly applied the subschema with no trigger present")
    # minContains/maxContains: refine the contains match count (default minContains 1)
    _ci = {"type": "array", "contains": {"type": "integer"}}
    if validate([1, 2, "a"], dict(_ci, minContains=2)):
        errs.append("minContains:2 rejected an array with 2 matching elements")
    if validate([1, "a"], dict(_ci, minContains=2)) == []:
        errs.append("minContains:2 accepted an array with only 1 matching element")
    if validate([1, 2], dict(_ci, maxContains=1)) == []:
        errs.append("maxContains:1 accepted an array with 2 matching elements")
    if validate([], dict(_ci, minContains=0)):
        errs.append("minContains:0 rejected an array with no matching element (floor not relaxed)")
    if validate(["a", "b"], dict(_ci, minContains=0)):
        errs.append("minContains:0 rejected a no-match array (floor not relaxed)")
    # default-deny still fires for a genuinely unknown keyword (gate not opened to everything).
    # `contains`, then `propertyNames`, USED to be witnesses here; now both ship, so `prefixItems` is.
    try:
        validate([1], {"type": "array", "prefixItems": [{"type": "integer"}]})
        errs.append("unknown keyword `prefixItems` did not raise after adding the 3 new keywords")
    except SchemaError:
        pass
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
