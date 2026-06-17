#!/usr/bin/env python3
"""test-vacuity-check.py — the code-decomposer test-integrity linter. Self-contained (stdlib only).

A green test suite is evidence of nothing if the tests can't fail for the right reason. This is the
mechanized attack on the "green but wrong" quadrant (EXECUTION passes, SPEC fails): it flags tests
that pass vacuously. Python is parsed with the `ast` module (precise); JS/TS uses regex + brace
matching (best-effort). Findings are advisory signals for the EXECUTION axis's B3 review — pair with
a real mutation run for proof.

Vacuity kinds:
  NO_ASSERT   a test with no assertion at all — it can only fail by throwing
  TAUTOLOGY   assert True · assertEqual(x, x) · expect(2).toBe(2) — always passes, touches no code
  MOCK_ONLY   asserts only that a mock was called, never a real result
  FOCUSED     .only( — silently disables every sibling test in the file
  SKIPPED     skip / xit / @skip — counted as "passing" while running nothing

  python3 bin/test-vacuity-check.py selftest
  python3 bin/test-vacuity-check.py <file | dir>     [--unit NAME]

Python 3.8+.
"""
import ast
import os
import re
import sys

PY_ASSERT_METHODS = {  # unittest-style real assertions (presence = the test asserts something)
    "assertEqual", "assertNotEqual", "assertTrue", "assertFalse", "assertIs", "assertIsNot",
    "assertIsNone", "assertIsNotNone", "assertIn", "assertNotIn", "assertRaises", "assertRaisesRegex",
    "assertAlmostEqual", "assertGreater", "assertLess", "assertGreaterEqual", "assertLessEqual",
    "assertListEqual", "assertDictEqual", "assertSetEqual", "assertRegex", "assertCountEqual",
}
PY_MOCK_ASSERTS = {
    "assert_called", "assert_called_once", "assert_called_with", "assert_called_once_with",
    "assert_not_called", "assert_any_call", "assert_has_calls",
}


def _const(node):
    return isinstance(node, ast.Constant)


def _same(a, b):
    return ast.dump(a) == ast.dump(b)


def _py_decorator_skips(fn):
    for d in fn.decorator_list:
        s = ast.dump(d)
        if "skip" in s.lower():
            return True
    return False


def _analyze_py_test(fn, unit):
    """Yield (kind, line, detail) findings for one Python test function."""
    name = fn.name
    real, mock, finds = 0, 0, []
    if _py_decorator_skips(fn):
        finds.append(("SKIPPED", fn.lineno, "%s is skipped" % name))
    refs_unit = unit is None or unit in ast.dump(fn)
    for n in ast.walk(fn):
        if isinstance(n, ast.Assert):
            real += 1
            t = n.test
            if _const(t) and bool(getattr(t, "value", False)):
                finds.append(("TAUTOLOGY", n.lineno, "assert <truthy constant>"))
            elif isinstance(t, ast.Compare) and len(t.comparators) == 1:
                if _same(t.left, t.comparators[0]):
                    finds.append(("TAUTOLOGY", n.lineno, "assert x == x (same expression)"))
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            m = n.func.attr
            if m in PY_ASSERT_METHODS:
                real += 1
                args = list(n.args)
                if m in ("assertTrue", "assertFalse") and args and _const(args[0]):
                    finds.append(("TAUTOLOGY", n.lineno, "%s(<constant>)" % m))
                if m in ("assertEqual", "assertIs", "assertNotEqual") and len(args) >= 2 and _same(args[0], args[1]):
                    finds.append(("TAUTOLOGY", n.lineno, "%s(x, x)" % m))
            elif m in ("raises", "warns"):   # `with pytest.raises(...)` / assertRaises ctx — a real assertion
                real += 1
            elif m in PY_MOCK_ASSERTS:
                mock += 1
    if real == 0 and mock == 0:
        finds.append(("NO_ASSERT", fn.lineno, "%s asserts nothing" % name))
    elif real == 0 and mock > 0:
        finds.append(("MOCK_ONLY", fn.lineno, "%s asserts only that a mock was called" % name))
    if not refs_unit and (real or mock):
        finds.append(("NO_ASSERT", fn.lineno, "%s never references unit %r" % (name, unit)))
    return finds


def _is_py_test(fn):
    return isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and fn.name.startswith("test")


def analyze_python(src, unit=None):
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [("PARSE", getattr(e, "lineno", 0) or 0, "could not parse: %s" % e.msg)]
    finds = []
    for node in ast.walk(tree):
        if _is_py_test(node):
            finds += _analyze_py_test(node, unit)
    return finds


# --- JS/TS (best-effort: regex + brace matching) ----------------------------------------------
_JS_FOCUS = re.compile(r"\b(?:it|test|describe)\.only\s*\(")
_JS_SKIP = re.compile(r"\b(?:xit|xdescribe|xtest)\b|\b(?:it|test|describe)\.skip\s*\(")
_JS_TAUT_BOOL = re.compile(r"expect\(\s*(?:true|false)\s*\)\s*\.\s*toBe(?:Truthy|Falsy)?\s*\(")
_JS_TAUT_SAME = re.compile(r"expect\(\s*([^()]+?)\s*\)\s*\.\s*toBe\w*\(\s*([^()]+?)\s*\)")
_JS_TEST_OPEN = re.compile(r"\b(it|test)\s*\(")
_JS_HAS_ASSERT = re.compile(r"\bexpect\s*\(|\bassert\b|\.should\b|\.toBe|\.toEqual")
_JS_MOCK_ASSERT = re.compile(r"\.(toHaveBeenCalled\w*|toBeCalled\w*)\s*\(")


def _line_of(src, idx):
    return src.count("\n", 0, idx) + 1


def _js_block_body(src, open_paren):
    """From the '(' of a test(...) call, return the callback body between its outer braces."""
    brace = src.find("{", open_paren)
    if brace < 0:
        return ""
    depth, i = 0, brace
    while i < len(src):
        c = src[i]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return src[brace + 1:i]
        i += 1
    return src[brace + 1:]


def analyze_js(src, unit=None):
    finds = []
    for m in _JS_FOCUS.finditer(src):
        finds.append(("FOCUSED", _line_of(src, m.start()), ".only disables sibling tests"))
    for m in _JS_SKIP.finditer(src):
        finds.append(("SKIPPED", _line_of(src, m.start()), "test is skipped"))
    for m in _JS_TAUT_BOOL.finditer(src):
        finds.append(("TAUTOLOGY", _line_of(src, m.start()), "expect(<bool literal>).toBe*"))
    for m in _JS_TAUT_SAME.finditer(src):
        a, b = m.group(1).strip(), m.group(2).strip()
        if a == b:
            finds.append(("TAUTOLOGY", _line_of(src, m.start()), "expect(x).toBe(x) (same expr/literal)"))
    for m in _JS_TEST_OPEN.finditer(src):
        body = _js_block_body(src, m.end() - 1)
        if not body.strip():
            continue
        if not _JS_HAS_ASSERT.search(body):
            finds.append(("NO_ASSERT", _line_of(src, m.start()), "test body has no assertion"))
        elif _JS_MOCK_ASSERT.search(body) and not re.search(r"\.(toBe|toEqual|toMatch|toContain|toThrow)\w*\s*\(", body):
            finds.append(("MOCK_ONLY", _line_of(src, m.start()), "asserts only that a mock was called"))
        elif unit and unit not in body:
            finds.append(("NO_ASSERT", _line_of(src, m.start()), "test never references unit %r" % unit))
    return finds


def analyze(path, src, unit=None):
    if path.endswith(".py"):
        return analyze_python(src, unit)
    if path.endswith((".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")):
        return analyze_js(src, unit)
    return []


def _is_test_file(fn):
    base = os.path.basename(fn)
    return (base.endswith((".test.js", ".test.jsx", ".test.ts", ".test.tsx",
                           ".spec.js", ".spec.ts", ".spec.jsx", ".spec.tsx"))
            or (base.startswith("test_") and base.endswith(".py"))
            or base.endswith("_test.py"))


# --- selftest fixtures -------------------------------------------------------------------------
PY_BAD = '''
import unittest
class T(unittest.TestCase):
    def test_tautology(self):
        self.assertEqual(2, 2)
    def test_true(self):
        assert True
    def test_same(self):
        x = compute()
        assert x == x
    def test_noassert(self):
        compute()
    def test_mock_only(self):
        m = Mock(); m()
        m.assert_called_once()
    @unittest.skip("later")
    def test_skipped(self):
        self.assertEqual(real(), 5)
'''
PY_GOOD = '''
def test_real():
    assert add(2, 3) == 5
def test_raises():
    import pytest
    with pytest.raises(ValueError):
        parse("x")
'''
JS_BAD = '''
it.only("focused", () => { expect(add(1,2)).toBe(3); });
test("taut", () => { expect(true).toBe(true); });
it("literal", () => { expect(2).toBe(2); });
it("noassert", () => { const x = add(1,2); });
it("mockonly", () => { const m = jest.fn(); m(); expect(m).toHaveBeenCalled(); });
xit("skipped", () => { expect(add(1,2)).toBe(3); });
'''
JS_GOOD = '''
it("adds", () => { expect(add(2,3)).toEqual(5); });
test("throws", () => { expect(() => parse("x")).toThrow(); });
'''


def selftest():
    errs = []

    def kinds(fns):
        return {k for k, _, _ in fns}

    pb = kinds(analyze_python(PY_BAD))
    for want in ("TAUTOLOGY", "NO_ASSERT", "MOCK_ONLY", "SKIPPED"):
        if want not in pb:
            errs.append("python: missed %s (got %s)" % (want, sorted(pb)))
    pg = analyze_python(PY_GOOD)
    if pg:
        errs.append("python: false positive on good tests: %s" % pg)

    jb = kinds(analyze_js(JS_BAD))
    for want in ("FOCUSED", "TAUTOLOGY", "NO_ASSERT", "MOCK_ONLY", "SKIPPED"):
        if want not in jb:
            errs.append("js: missed %s (got %s)" % (want, sorted(jb)))
    jg = analyze_js(JS_GOOD)
    if jg:
        errs.append("js: false positive on good tests: %s" % jg)

    # --unit gating: a real assertion that never names the unit is flagged
    u = kinds(analyze_python("def test_x():\n    assert helper() == 1\n", unit="target"))
    if "NO_ASSERT" not in u:
        errs.append("python: --unit miss not flagged")
    return errs


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("test-vacuity-check: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("test-vacuity-check: OK — Python (ast) + JS/TS detectors verified over good/bad fixtures")
        return 0
    path = argv[0]
    unit = argv[argv.index("--unit") + 1] if "--unit" in argv else None
    files = []
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            files += [os.path.join(dp, fn) for fn in sorted(fns) if _is_test_file(fn)]
    else:
        files = [path]
    total = 0
    for fp in files:
        try:
            src = open(fp, encoding="utf-8").read()
        except OSError as e:
            print("  ⚠ %s: unreadable (%s)" % (fp, e))
            continue
        for kind, line, detail in analyze(fp, src, unit):
            total += 1
            print("  %s:%s  %-9s %s" % (os.path.relpath(fp), line, kind, detail))
    if total:
        print("test-vacuity-check: %d vacuity signal(s) across %d file(s) — verify with a mutation run"
              % (total, len(files)))
        return 1
    print("test-vacuity-check: OK — no vacuity signals in %d file(s)" % len(files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
