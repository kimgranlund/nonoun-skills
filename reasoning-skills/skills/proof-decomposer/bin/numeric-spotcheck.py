#!/usr/bin/env python3
"""numeric-spotcheck.py — the proof-decomposer counterexample search. Self-contained (stdlib only).

A claim's persuasiveness is not its truth: a quantified statement ("for all n, ...") that *reads*
right can be false at one integer you didn't picture. This evaluates a parametric boolean claim over
a finite integer sample space and reports the FIRST counterexample, if one exists — the cheapest,
most decisive probe on the CLAIM axis (does the proof prove a true thing at all?). A surviving
counterexample is a disproof; "no counterexample in range" is corroboration, never a proof.

It does NOT call `eval`. The expression is parsed with the `ast` module and walked by a tiny
whitelisted evaluator over: integer/bool literals, the declared variables, + - * (unary -), `//`,
`%`, `**` (bounded result magnitude), comparisons (== != < <= > >=, chained), and `and`/`or`/`not`/
parentheses. Anything else — a name call, an attribute, a comprehension, `__import__` — is rejected
at parse time.

Two independent guards keep the "can't blow up / can't hang" guarantee. The sample-space cap bounds
the number of evaluations. The result-magnitude cap bounds the SIZE of any intermediate integer:
`**` is composable (`((n**64)**64)**64` stays under any per-exponent cap yet builds a ~500k-digit
integer), so capping the exponent alone is not enough — we predict each power's bit-size
(`base.bit_length() * exponent`) and reject it if it would exceed MAX_BITS *before* computing it. A
wall-clock budget across the search loop is the belt-and-suspenders backstop.

Claim (JSON):
  {"vars": ["n"], "expr": "n*(n+1) % 2 == 0", "range": [0, 100]}
  {"vars": ["a", "b"], "expr": "(a+b)**2 == a*a + 2*a*b + b*b", "range": [-20, 20]}

The sample space is the Cartesian product of `range`=[lo, hi] (inclusive) over every var. A guard
caps the product so a careless wide multi-var range can't hang.

  python3 bin/numeric-spotcheck.py selftest
  python3 bin/numeric-spotcheck.py <claim.json>

Python 3.8+.
"""
import ast
import itertools
import json
import sys
import time

MAX_POW = 64               # cap each exponent (a coarse first line of defence)
MAX_BITS = 100_000         # cap the bit-size of ANY power result — bounds magnitude, not just exponent
MAX_SAMPLES = 2_000_000    # cap the Cartesian product so a wide multi-var range can't hang
WALLCLOCK_BUDGET_S = 10.0  # belt-and-suspenders: a hard ceiling on the whole search loop


class UnsafeExpr(ValueError):
    """The expression uses a construct outside the whitelist."""


class SearchBudgetExceeded(ValueError):
    """The search loop blew its wall-clock budget — treat as an unsafe/oversized claim."""


_BINOPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
}
_CMP = {
    ast.Eq: lambda a, b: a == b,
    ast.NotEq: lambda a, b: a != b,
    ast.Lt: lambda a, b: a < b,
    ast.LtE: lambda a, b: a <= b,
    ast.Gt: lambda a, b: a > b,
    ast.GtE: lambda a, b: a >= b,
}


def compile_expr(expr):
    """Parse + validate the expression once; return the AST node. Raises UnsafeExpr on any disallowed node."""
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise UnsafeExpr("syntax error: %s" % e.msg)

    def validate(node):
        if isinstance(node, ast.Expression):
            return validate(node.body)
        if isinstance(node, ast.BoolOp):
            for v in node.values:
                validate(v)
            return
        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, (ast.USub, ast.UAdd, ast.Not)):
                raise UnsafeExpr("unary op %s not allowed" % type(node.op).__name__)
            return validate(node.operand)
        if isinstance(node, ast.BinOp):
            if type(node.op) not in _BINOPS and not isinstance(node.op, ast.Pow):
                raise UnsafeExpr("binary op %s not allowed" % type(node.op).__name__)
            validate(node.left)
            return validate(node.right)
        if isinstance(node, ast.Compare):
            for op in node.ops:
                if type(op) not in _CMP:
                    raise UnsafeExpr("comparator %s not allowed" % type(op).__name__)
            validate(node.left)
            for c in node.comparators:
                validate(c)
            return
        if isinstance(node, ast.Name):
            return
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, bool)):
                return
            raise UnsafeExpr("only int/bool literals allowed (got %r)" % (node.value,))
        raise UnsafeExpr("construct %s not allowed" % type(node).__name__)

    validate(tree)
    return tree


def eval_node(node, env):
    """Evaluate a pre-validated node against an integer environment."""
    if isinstance(node, ast.Expression):
        return eval_node(node.body, env)
    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            return all(eval_node(v, env) for v in node.values)
        return any(eval_node(v, env) for v in node.values)
    if isinstance(node, ast.UnaryOp):
        v = eval_node(node.operand, env)
        if isinstance(node.op, ast.USub):
            return -v
        if isinstance(node.op, ast.UAdd):
            return +v
        return not v
    if isinstance(node, ast.BinOp):
        a, b = eval_node(node.left, env), eval_node(node.right, env)
        if isinstance(node.op, ast.Pow):
            if not isinstance(b, int) or b < 0 or b > MAX_POW:
                raise UnsafeExpr("exponent must be an int in [0, %d]" % MAX_POW)
            # Bound the RESULT MAGNITUDE, not just the exponent: `**` is composable, so a chain of
            # small exponents (((n**64)**64)**64) stays under MAX_POW yet builds a huge integer.
            # Predict the result's bit-size before computing it; |a**b| has ~ a.bit_length()*b bits.
            if isinstance(a, int) and a not in (-1, 0, 1) and b > 0:
                if a.bit_length() * b > MAX_BITS:
                    raise UnsafeExpr("power result would exceed %d bits (base %d ** exp %d) — "
                                     "claim too large to spot-check safely" % (MAX_BITS, a, b))
            return a ** b
        return _BINOPS[type(node.op)](a, b)
    if isinstance(node, ast.Compare):
        left = eval_node(node.left, env)
        for op, comp in zip(node.ops, node.comparators):
            right = eval_node(comp, env)
            if not _CMP[type(op)](left, right):
                return False
            left = right          # chained comparison semantics (a < b < c)
        return True
    if isinstance(node, ast.Name):
        if node.id not in env:
            raise UnsafeExpr("unknown variable %r" % node.id)
        return env[node.id]
    if isinstance(node, ast.Constant):
        return node.value
    raise UnsafeExpr("unexpected node at eval %s" % type(node).__name__)


def parse_claim(doc):
    """Validate the claim JSON. Returns (vars:list, tree, lo:int, hi:int). Raises ValueError."""
    if not isinstance(doc, dict):
        raise ValueError("claim must be a JSON object")
    variables = doc.get("vars")
    if not isinstance(variables, list) or not variables or not all(isinstance(v, str) for v in variables):
        raise ValueError("'vars' must be a non-empty list of strings")
    expr = doc.get("expr")
    if not isinstance(expr, str) or not expr.strip():
        raise ValueError("'expr' must be a non-empty string")
    rng = doc.get("range")
    if not (isinstance(rng, list) and len(rng) == 2 and all(isinstance(x, int) for x in rng)):
        raise ValueError("'range' must be [lo, hi] integers (inclusive)")
    lo, hi = rng
    if lo > hi:
        raise ValueError("'range' lo (%d) > hi (%d)" % (lo, hi))
    span = hi - lo + 1
    if span ** len(variables) > MAX_SAMPLES:
        raise ValueError("sample space %d^%d exceeds cap %d — narrow the range or var count"
                         % (span, len(variables), MAX_SAMPLES))
    tree = compile_expr(expr)        # raises UnsafeExpr (a ValueError) on disallowed constructs
    # every Name in the tree must be a declared var
    declared = set(variables)
    for n in ast.walk(tree):
        if isinstance(n, ast.Name) and n.id not in declared:
            raise ValueError("expr references undeclared variable %r (declare it in 'vars')" % n.id)
    return variables, tree, lo, hi


def search(doc):
    """Evaluate the claim over the sample space. Returns (holds:bool, info:dict)."""
    variables, tree, lo, hi = parse_claim(doc)
    domain = range(lo, hi + 1)
    checked = 0
    deadline = time.monotonic() + WALLCLOCK_BUDGET_S
    for combo in itertools.product(domain, repeat=len(variables)):
        env = dict(zip(variables, combo))
        checked += 1
        # belt-and-suspenders: even past the per-power magnitude cap, a pathological mix of large
        # ops shouldn't let the loop run unbounded. Check the clock periodically (cheap).
        if checked % 256 == 0 and time.monotonic() > deadline:
            raise SearchBudgetExceeded(
                "search exceeded %.0fs wall-clock budget after %d sample(s) — narrow the range or "
                "simplify the claim" % (WALLCLOCK_BUDGET_S, checked))
        try:
            val = eval_node(tree, env)
        except ZeroDivisionError:
            return False, {"counterexample": env, "reason": "division/modulo by zero", "checked": checked}
        if val is not True:          # a claim must be exactly True; anything else is a counterexample
            return False, {"counterexample": env, "value": val, "checked": checked}
    return True, {"checked": checked, "range": [lo, hi], "vars": variables}


# --- selftest fixtures -------------------------------------------------------------------------
TRUE_CLAIM = {"vars": ["n"], "expr": "n*(n+1) % 2 == 0", "range": [0, 100]}
TRUE_BINOMIAL = {"vars": ["a", "b"], "expr": "(a+b)**2 == a*a + 2*a*b + b*b", "range": [-15, 15]}
FALSE_CLAIM = {"vars": ["n"], "expr": "n*n >= n+1", "range": [0, 100]}            # fails at n in {0,1}
# A false ALGEBRAIC IDENTITY the tool genuinely falsifies — the cube of a sum is NOT the sum of cubes;
# the cross terms 3*a*a*b + 3*a*b*b are missing, so it fails wherever a,b are both nonzero. (Note:
# this tool cannot express primality — see M2 in verification-axis.md; the famous n²−n+41 prime story
# is motivation only, and primality is OUT OF SCOPE here, routed to a proof assistant.)
FALSE_IDENTITY = {"vars": ["a", "b"], "expr": "(a+b)**3 == a*a*a + b*b*b", "range": [-8, 8]}
# B1 DoS fixture: `**` is composable, so this chains to exponent 64*64*64=262144 — under MAX_POW per
# operator, but the result is ~500k digits. Must be REJECTED (raise UnsafeExpr), not hang.
POW_BOMB = {"vars": ["n"], "expr": "(((n**64)**64)**64) >= 0", "range": [2, 200]}


def selftest():
    errs = []

    holds, info = search(TRUE_CLAIM)
    if not holds:
        errs.append("TRUE_CLAIM should hold, got counterexample %s" % info.get("counterexample"))
    holds, info = search(TRUE_BINOMIAL)
    if not holds:
        errs.append("TRUE_BINOMIAL should hold, got %s" % info)

    holds, info = search(FALSE_CLAIM)
    if holds or "counterexample" not in info:
        errs.append("FALSE_CLAIM should yield a counterexample, got %s" % info)
    elif info["counterexample"]["n"] not in (0, 1):
        errs.append("FALSE_CLAIM counterexample should be n in {0,1}, got %s" % info["counterexample"])

    # a false algebraic identity must be caught — (a+b)^3 != a^3 + b^3 wherever both are nonzero
    holds, info = search(FALSE_IDENTITY)
    if holds or "counterexample" not in info:
        errs.append("FALSE_IDENTITY should yield a counterexample, got %s" % info)

    # B1 DoS: the composed-power bomb must be REJECTED by the magnitude guard, never computed/hung
    try:
        holds, info = search(POW_BOMB)
        errs.append("POW_BOMB should be REJECTED (magnitude guard), but search returned %s / %s"
                    % (holds, info))
    except UnsafeExpr:
        pass  # correct: rejected before building the ~500k-digit integer

    # chained comparison semantics: 1 < n < 3 true only at n=2
    holds, info = search({"vars": ["n"], "expr": "1 < n < 3", "range": [2, 2]})
    if not holds:
        errs.append("chained comparison at n=2 should hold, got %s" % info)
    holds, _ = search({"vars": ["n"], "expr": "1 < n < 3", "range": [0, 5]})
    if holds:
        errs.append("chained comparison should fail somewhere in [0,5]")

    # the safe evaluator REJECTS code execution attempts at parse time
    for danger in ("__import__('os')", "x.foo", "abs(x)", "[i for i in range(3)]", "lambda: 1"):
        try:
            compile_expr(danger)
            errs.append("compile_expr accepted unsafe expr: %s" % danger)
        except UnsafeExpr:
            pass

    # parse_claim rejects malformed claims + undeclared vars + an oversized sample space
    for bad in ({}, {"vars": [], "expr": "1==1", "range": [0, 1]},
                {"vars": ["n"], "expr": "", "range": [0, 1]},
                {"vars": ["n"], "expr": "1==1", "range": [5, 1]},
                {"vars": ["n"], "expr": "n == m", "range": [0, 1]},                 # undeclared m
                {"vars": ["a", "b", "c", "d"], "expr": "a==a", "range": [-1000, 1000]}):  # too big
        try:
            parse_claim(bad)
            errs.append("parse_claim accepted malformed: %s" % bad)
        except ValueError:
            pass
    return errs


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("numeric-spotcheck: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("numeric-spotcheck: OK — safe evaluator + true/false claims + reject-unsafe verified")
        return 0
    try:
        doc = json.load(open(argv[0], encoding="utf-8"))
        holds, info = search(doc)
    except (OSError, json.JSONDecodeError) as e:
        sys.stderr.write("numeric-spotcheck: bad claim — %s\n" % e)
        return 2
    except (ValueError, UnsafeExpr) as e:
        sys.stderr.write("numeric-spotcheck: invalid claim — %s\n" % e)
        return 2
    if holds:
        print("numeric-spotcheck: no counterexample in %s over %d sample(s) — corroborated, NOT proven"
              % (info["range"], info["checked"]))
        return 0
    ce = info.get("counterexample", {})
    detail = info.get("reason") or ("evaluates to %r, not True" % info.get("value"))
    sys.stderr.write("numeric-spotcheck: COUNTEREXAMPLE at %s — the claim is FALSE (%s; checked %d)\n"
                     % (ce, detail, info.get("checked", 0)))
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
