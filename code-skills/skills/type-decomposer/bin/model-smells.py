#!/usr/bin/env python3
"""model-smells.py — the type-decomposer model-smell linter. Self-contained (stdlib only).

Static scan of a JSON Schema for the shapes that let illegal states slip through — the MODEL-axis
(A3/A4) smells the instance check can't see until you write the counterexample. Advisory signals,
not proof: each one points at a place the state space is wider than the domain.

Smells:
  BOOLEAN_BLINDNESS   >= 2 boolean-ish fields on one object — a real boolean, an enum:[true,false],
                      or a const-boolean all count — usually a mutually-exclusive state that should
                      be a oneOf / enum (2 booleans = 4 states, often 1-2 of them illegal)
  OPTIONAL_SOUP       many properties, <=1 required, no oneOf/anyOf grouping — most field
                      combinations are representable, including the illegal ones
  PRIMITIVE_OBSESSION a string named like a constrained type (email/url/id/uuid/date/...) with no
                      format / pattern / enum — an Email is not a String
  OPEN_RECORD         an object with properties but no additionalProperties:false — admits
                      illegal extra fields (the record is probably closed)
  STRINGLY_TYPED_ENUM a string whose description enumerates fixed values but carries no enum

  python3 bin/model-smells.py selftest
  python3 bin/model-smells.py <schema.json | dir>

Python 3.8+.
"""
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
                if _is_bare_string(s) and CONSTRAINED.search(k):
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
    return errs


def _iter(path):
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            for fn in sorted(fns):
                if fn.endswith(".json"):
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
        print("model-smells: OK — 5 smell detectors verified over dirty/clean fixtures")
        return 0
    total = 0
    for fp in _iter(argv[0]):
        try:
            schema = json.load(open(fp, encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as ex:
            print("  ⚠ %s: unreadable (%s)" % (fp, ex))
            continue
        for kind, path, detail in smells(schema):
            total += 1
            print("  %s  %-20s %s  %s" % (os.path.relpath(fp), kind, path, detail))
    if total:
        print("model-smells: %d smell(s) — widen-able state space; confirm with an illegal-instance set" % total)
        return 1
    print("model-smells: OK — no model smells")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
