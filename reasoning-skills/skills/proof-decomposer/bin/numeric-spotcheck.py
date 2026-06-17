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

Boolean claim (JSON) — the original shape:
  {"vars": ["n"], "expr": "n*(n+1) % 2 == 0", "range": [0, 100]}
  {"vars": ["a", "b"], "expr": "(a+b)**2 == a*a + 2*a*b + b*b", "range": [-20, 20]}

The sample space is the Cartesian product of `range`=[lo, hi] (inclusive) over every var. A guard
caps the product so a careless wide multi-var range can't hang.

Predicate claim (JSON or a natural-language sentence) — the number-theory shape: a single-var f(n)
asserted to satisfy a predicate over a bounded range. `f(n)` reuses the SAME safe evaluator (`^` is
normalised to `**`), so all of the guards above apply unchanged; only a bounded trial-division
primality test is added.
  {"f": "n^2 - n + 41", "predicate": "prime", "range": [0, 100]}
  {"f": "n^3 - n", "predicate": "divisible", "k": 6, "range": [0, 200]}
  {"f": "2*n", "predicate": "congruent", "m": 2, "r": 0, "range": [0, 100]}
  "n^2 - n + 41 is prime for all n >= 0"      # → COUNTEREXAMPLE at n=41, f(41)=1681≡0 (mod 41)=41²

  python3 bin/numeric-spotcheck.py selftest
  python3 bin/numeric-spotcheck.py <claim.json>
  python3 bin/numeric-spotcheck.py "<natural-language predicate claim>"

Python 3.8+.
"""
import ast
import itertools
import json
import re
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


# === MODULAR / DIVISIBILITY / PRIMALITY claims ==================================================
# A second claim shape: a single-variable integer function f(n) asserted to satisfy a NUMBER-THEORY
# predicate for all n in a range — "f(n) is prime", "k | f(n)", "f(n) ≡ r (mod m)". These read just
# as plausibly as an algebraic identity and die at exactly one n (the Euler polynomial n²−n+41 is
# prime for n=0..40 and composite at n=41). f(n) is evaluated by the SAME safe AST evaluator above
# (compile_expr + eval_node) — no eval(), and every existing guard (the `**` magnitude/exponent caps,
# the wall-clock backstop) is inherited unchanged. We add only a bounded trial-division primality
# test and a per-n predicate; the search walks the range and returns the SMALLEST counterexample.

MAX_TRIAL_DIV_N = 1 << 40  # cap |f(n)| for the trial-division primality test (~10^12) — keeps the
#                            # O(√N) factor search bounded; a larger value is reported, never tested.


def is_prime(n):
    """Bounded deterministic trial division. Returns True/False; raises UnsafeExpr if |n| is too large
    to test in bounded time (so a primality claim over a huge f(n) is rejected, never hung on)."""
    if not isinstance(n, int):
        raise UnsafeExpr("primality is defined only on integers (got %r)" % (n,))
    if abs(n) > MAX_TRIAL_DIV_N:
        raise UnsafeExpr("value %d exceeds the trial-division cap %d — primality claim too large to "
                         "spot-check safely" % (n, MAX_TRIAL_DIV_N))
    if n < 2:
        return False           # 0, 1, and negatives are not prime
    if n < 4:
        return True            # 2, 3
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def smallest_factor(n):
    """The smallest prime factor of |n| for n with |n|>=2 (used to witness a composite). Bounded by the
    same trial-division cap as is_prime."""
    n = abs(n)
    if n < 2:
        return None
    if n % 2 == 0:
        return 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return d
        d += 2
    return n                    # n is itself prime — its smallest factor is itself


# Predicate-claim parsing. A predicate claim is either a JSON object
#   {"f": "n^2 - n + 41", "predicate": "prime",            "range": [0, 100]}
#   {"f": "n^2 + 1",      "predicate": "divisible", "k": 2, "range": [0, 100]}
#   {"f": "n*n - n",      "predicate": "congruent", "m": 5, "r": 0, "range": [0, 100]}
# or a natural-language string we parse into that shape. `^` is normalised to `**` so textbook
# polynomials ("n^2 - n + 41") parse; the var defaults to "n".

_RANGE_FORALL = re.compile(r"for\s+all\s+\w+\s*(?:>=|≥)\s*(-?\d+)", re.I)
_RANGE_BOUNDED = re.compile(r"(-?\d+)\s*(?:<=|≤)\s*\w+\s*(?:<=|≤)\s*(-?\d+)")
_DIVISIBLE_BY = re.compile(r"divisible\s+by\s+(\d+)", re.I)
_K_DIVIDES = re.compile(r"(\d+)\s*\|\s*")                                # "6 | f(n)"
_MOD = re.compile(r"\(?\s*mod\s+(\d+)\s*\)?", re.I)
_CONGRUENT = re.compile(r"(?:≡|congruent\s+to)\s*(-?\d+)\s*\(?\s*mod\s+(\d+)\s*\)?", re.I)
_PRIME = re.compile(r"\bis\s+prime\b", re.I)


def _parse_range_from_text(text, default=(0, 100)):
    m = _RANGE_BOUNDED.search(text)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = _RANGE_FORALL.search(text)
    if m:
        return int(m.group(1)), int(m.group(1)) + 100  # "for all n >= lo" → sample lo..lo+100
    if re.search(r"for\s+all", text, re.I):
        return default
    return default


def _extract_f(text):
    """Pull the function expression out of a claim sentence: everything before the predicate clause."""
    # cut at the first predicate keyword (consume the copula `is` where it introduces the predicate)
    for kw in (r"\bis\s+prime\b", r"\bis\s+divisible\b", r"≡",
               r"\bis\s+congruent\b", r"\bcongruent\b", r"\|"):
        m = re.search(kw, text, re.I)
        if m:
            text = text[:m.start()]
            break
    # strip a trailing bare copula ("n is" → "n") left by the ≡/congruent forms, and any "for ..." tail
    text = re.split(r"\bfor\s+all\b|\bfor\s+\d", text, flags=re.I)[0]
    text = re.sub(r"\s+is\s*$", "", text, flags=re.I)
    return text.strip()


def parse_predicate_claim(doc):
    """Normalise a predicate claim (dict OR natural-language string) into a canonical dict:
       {"f": expr, "var": name, "predicate": "prime"|"divisible"|"congruent", k/m/r, "range":[lo,hi]}.
    Raises ValueError on a malformed claim. f's expression is validated by compile_expr (safe AST)."""
    if isinstance(doc, str):
        text = doc.strip()
        claim = {}
        # predicate + parameters
        if _PRIME.search(text):
            claim["predicate"] = "prime"
        else:
            cong = _CONGRUENT.search(text)
            if cong:
                claim["predicate"] = "congruent"
                claim["r"] = int(cong.group(1))
                claim["m"] = int(cong.group(2))
            else:
                div = _DIVISIBLE_BY.search(text)
                kdiv = _K_DIVIDES.search(text)
                if div:
                    claim["predicate"] = "divisible"
                    claim["k"] = int(div.group(1))
                    f_text = _extract_f(text)
                elif kdiv:
                    claim["predicate"] = "divisible"
                    claim["k"] = int(kdiv.group(1))
                    # "k | f(n)" — f is what follows the bar (before any "for ...")
                    rest = text[kdiv.end():]
                    f_text = re.split(r"\bfor\b", rest, flags=re.I)[0].strip()
                    claim["f"] = f_text
                else:
                    raise ValueError("could not parse a predicate (prime / divisible by k / ≡ r mod m) "
                                     "from claim text: %r" % text)
        claim.setdefault("f", _extract_f(text))
        lo, hi = _parse_range_from_text(text)
        claim["range"] = [lo, hi]
    elif isinstance(doc, dict):
        claim = dict(doc)
    else:
        raise ValueError("predicate claim must be a JSON object or a string")

    pred = claim.get("predicate")
    if pred not in ("prime", "divisible", "congruent"):
        raise ValueError("'predicate' must be one of prime|divisible|congruent (got %r)" % pred)
    f_expr = claim.get("f")
    if not isinstance(f_expr, str) or not f_expr.strip():
        raise ValueError("'f' must be a non-empty function expression")
    f_expr = f_expr.replace("^", "**")                # textbook caret → Python power (still guarded)
    var = claim.get("var", "n")
    rng = claim.get("range", [0, 100])
    if not (isinstance(rng, list) and len(rng) == 2 and all(isinstance(x, int) for x in rng)):
        raise ValueError("'range' must be [lo, hi] integers (inclusive)")
    lo, hi = rng
    if lo > hi:
        raise ValueError("'range' lo (%d) > hi (%d)" % (lo, hi))
    if hi - lo + 1 > MAX_SAMPLES:
        raise ValueError("sample space %d exceeds cap %d — narrow the range" % (hi - lo + 1, MAX_SAMPLES))
    if pred == "divisible":
        k = claim.get("k")
        if not isinstance(k, int) or k == 0:
            raise ValueError("'divisible' needs a nonzero integer 'k'")
    if pred == "congruent":
        m = claim.get("m")
        if not isinstance(m, int) or m <= 0:
            raise ValueError("'congruent' needs a positive integer modulus 'm'")
        if not isinstance(claim.get("r"), int):
            raise ValueError("'congruent' needs an integer residue 'r'")
    tree = compile_expr(f_expr)                        # safe AST validation (raises UnsafeExpr)
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id != var:
            raise ValueError("f references variable %r but the claim's var is %r" % (node.id, var))
    claim["f"] = f_expr
    claim["var"] = var
    claim["range"] = [lo, hi]
    claim["_tree"] = tree
    return claim


def predicate_search(doc):
    """Search a single-var integer range for the SMALLEST n where the number-theory predicate fails.
    Returns (holds:bool, info:dict). f(n) is evaluated by the shared safe evaluator (all `**` guards
    inherited); the wall-clock backstop bounds the loop. For primality, the info reports the modular
    WITNESS — the smallest factor of f(n) — which for the Euler polynomial is the constant term."""
    claim = parse_predicate_claim(doc)
    var, tree = claim["var"], claim["_tree"]
    pred = claim["predicate"]
    lo, hi = claim["range"]
    checked = 0
    deadline = time.monotonic() + WALLCLOCK_BUDGET_S
    for n in range(lo, hi + 1):
        checked += 1
        if checked % 256 == 0 and time.monotonic() > deadline:
            raise SearchBudgetExceeded(
                "predicate search exceeded %.0fs after %d sample(s)" % (WALLCLOCK_BUDGET_S, checked))
        fn = eval_node(tree, {var: n})                 # safe eval — guards apply to any `**` inside f
        if pred == "prime":
            if not is_prime(fn):
                factor = smallest_factor(fn)
                info = {"counterexample": {var: n}, "f_value": fn, "checked": checked,
                        "predicate": "prime",
                        "reason": "f(%d) = %d is not prime" % (n, fn)}
                if factor is not None and fn not in (-1, 0, 1):
                    # the MODULAR witness: f(n) ≡ 0 (mod factor). For n²−n+41 at n=41, factor=41 (the
                    # constant term), so f(41) = 41·41 — divisible by 41 because 41 | the constant.
                    info["witness_factor"] = factor
                    info["mod_witness"] = "f(%d) = %d ≡ 0 (mod %d)  [%d | f(%d)]" % (
                        n, fn, factor, factor, n)
                    if fn != 0 and fn // factor == factor and factor * factor == fn:
                        info["mod_witness"] += "  = %d^2" % factor
                return False, info
        elif pred == "divisible":
            k = claim["k"]
            rem = fn % k
            if rem != 0:
                return False, {"counterexample": {var: n}, "f_value": fn, "checked": checked,
                               "predicate": "divisible", "k": k, "remainder": rem,
                               "reason": "f(%d) = %d ; %d mod %d = %d ≠ 0" % (n, fn, fn, k, rem)}
        else:  # congruent
            m, r = claim["m"], claim["r"]
            got = fn % m
            want = r % m
            if got != want:
                return False, {"counterexample": {var: n}, "f_value": fn, "checked": checked,
                               "predicate": "congruent", "m": m, "r": r, "residue": got,
                               "reason": "f(%d) = %d ≡ %d (mod %d), expected ≡ %d" % (n, fn, got, m, want)}
    return True, {"checked": checked, "range": [lo, hi], "var": var, "predicate": pred}


def _is_predicate_doc(doc):
    """A claim is a predicate claim if it's a string, or a dict carrying 'predicate'/'f'."""
    return isinstance(doc, str) or (isinstance(doc, dict) and ("predicate" in doc or "f" in doc))


# --- selftest fixtures -------------------------------------------------------------------------
TRUE_CLAIM = {"vars": ["n"], "expr": "n*(n+1) % 2 == 0", "range": [0, 100]}
TRUE_BINOMIAL = {"vars": ["a", "b"], "expr": "(a+b)**2 == a*a + 2*a*b + b*b", "range": [-15, 15]}
FALSE_CLAIM = {"vars": ["n"], "expr": "n*n >= n+1", "range": [0, 100]}            # fails at n in {0,1}
# A false ALGEBRAIC IDENTITY the tool genuinely falsifies — the cube of a sum is NOT the sum of cubes;
# the cross terms 3*a*a*b + 3*a*b*b are missing, so it fails wherever a,b are both nonzero. (Primality
# / divisibility / congruence claims live in the predicate shape below — the famous n²−n+41 prime
# story is now a real fixture, EULER_PRIME, not just motivation.)
FALSE_IDENTITY = {"vars": ["a", "b"], "expr": "(a+b)**3 == a*a*a + b*b*b", "range": [-8, 8]}
# B1 DoS fixture: `**` is composable, so this chains to exponent 64*64*64=262144 — under MAX_POW per
# operator, but the result is ~500k digits. Must be REJECTED (raise UnsafeExpr), not hang.
POW_BOMB = {"vars": ["n"], "expr": "(((n**64)**64)**64) >= 0", "range": [2, 200]}

# --- predicate-claim fixtures (modular / divisibility / primality) -------------------------------
# The classic Euler polynomial: prime for n=0..40, COMPOSITE at n=41 where f(41)=1681=41². The modular
# insight: the constant term 41 divides f(41), so 41 | f(41) — the witness factor is 41. (NL string.)
EULER_PRIME = "n^2 - n + 41 is prime for all n >= 0"
# The SAME family, but a BOUNDED range that stops before the failure — TRUE in range, must NOT false-
# positive. (n²+n+41 is prime for n=0..39; we pin the range to the true window.)
EULER_BOUNDED = "n^2 + n + 41 is prime for 0 <= n <= 39"
# TRUE divisibility: n³ − n = (n−1)n(n+1), a product of 3 consecutive ints, always divisible by 6.
DIV_TRUE = {"f": "n^3 - n", "predicate": "divisible", "k": 6, "range": [0, 200]}
# FALSE divisibility: n²+1 is NOT always even — at n=2, f(2)=5, 5 mod 2 = 1. Smallest counterexample
# is n=2 (n=0→1 odd too, but we pin lo=2 to assert the reported value cleanly per the brief). Use NL
# form to also exercise the parser. lo is 1 so the first failure in-range is n=2 (f(1)=2 is even).
DIV_FALSE = "n^2 + 1 is divisible by 2 for all n >= 1"
# TRUE congruence: n² ≡ 0 or 1 (mod 4)… use the clean one: 2n ≡ 0 (mod 2) for all n.
CONG_TRUE = {"f": "2*n", "predicate": "congruent", "m": 2, "r": 0, "range": [0, 100]}
# FALSE congruence: n ≡ 0 (mod 3) is false at n=1 (1 mod 3 = 1).
CONG_FALSE = {"f": "n", "predicate": "congruent", "m": 3, "r": 0, "range": [0, 50]}
# A primality claim over a value that would exceed the trial-division cap must be REJECTED, not hung.
PRIME_BOMB = {"f": "n**8", "predicate": "prime", "range": [100000, 100001]}  # 1e5^8 ≫ cap


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

    # --- MODULAR / DIVISIBILITY / PRIMALITY ----------------------------------------------------
    # the trial-division primality test itself, against known values
    for p in (2, 3, 5, 7, 41, 1009):
        if not is_prime(p):
            errs.append("is_prime(%d) should be True" % p)
    for c in (0, 1, 4, 9, 41 * 41, 1009 * 1013):
        if is_prime(c):
            errs.append("is_prime(%d) should be False" % c)

    # the Euler polynomial: a REAL counterexample at n=41, with the mod-41 modular witness
    holds, info = predicate_search(EULER_PRIME)
    if holds or "counterexample" not in info:
        errs.append("EULER_PRIME should yield a counterexample, got %s" % info)
    else:
        if info["counterexample"].get("n") != 41:
            errs.append("EULER_PRIME counterexample should be n=41, got %s" % info["counterexample"])
        if info.get("f_value") != 1681:
            errs.append("EULER_PRIME f(41) should be 1681, got %s" % info.get("f_value"))
        if info.get("witness_factor") != 41:
            errs.append("EULER_PRIME mod witness factor should be 41, got %s" % info.get("witness_factor"))

    # the bounded Euler claim is TRUE in its pinned window — must NOT false-positive
    holds, info = predicate_search(EULER_BOUNDED)
    if not holds:
        errs.append("EULER_BOUNDED should hold in 0..39, got counterexample %s"
                    % info.get("counterexample"))

    # TRUE divisibility (n³−n divisible by 6) — no counterexample
    holds, info = predicate_search(DIV_TRUE)
    if not holds:
        errs.append("DIV_TRUE (n^3-n div by 6) should hold, got %s" % info.get("counterexample"))

    # FALSE divisibility (n²+1 divisible by 2) — counterexample at n=2 with remainder 1
    holds, info = predicate_search(DIV_FALSE)
    if holds or "counterexample" not in info:
        errs.append("DIV_FALSE should yield a counterexample, got %s" % info)
    else:
        if info["counterexample"].get("n") != 2:
            errs.append("DIV_FALSE counterexample should be n=2, got %s" % info["counterexample"])
        if info.get("remainder") != 1 or info.get("f_value") != 5:
            errs.append("DIV_FALSE should report f(2)=5, 5 mod 2 = 1, got %s" % info)

    # TRUE congruence (2n ≡ 0 mod 2) — no counterexample
    holds, info = predicate_search(CONG_TRUE)
    if not holds:
        errs.append("CONG_TRUE (2n ≡ 0 mod 2) should hold, got %s" % info.get("counterexample"))

    # FALSE congruence (n ≡ 0 mod 3) — counterexample at n=1
    holds, info = predicate_search(CONG_FALSE)
    if holds or info.get("counterexample", {}).get("n") != 1:
        errs.append("CONG_FALSE should yield a counterexample at n=1, got %s" % info)

    # DoS: a primality claim over a value past the trial-division cap must be REJECTED, never hung
    try:
        predicate_search(PRIME_BOMB)
        errs.append("PRIME_BOMB should be REJECTED (trial-division cap), but search returned")
    except UnsafeExpr:
        pass

    # the safe evaluator still guards f(n): a `**` bomb inside a predicate claim is rejected at parse
    try:
        parse_predicate_claim({"f": "(((n**64)**64)**64)", "predicate": "prime", "range": [2, 3]})
        # parse alone may pass (the bomb fires at eval); the search must reject it
        predicate_search({"f": "(((n**64)**64)**64)", "predicate": "prime", "range": [2, 3]})
        errs.append("predicate `**` bomb should be REJECTED by the magnitude guard")
    except UnsafeExpr:
        pass

    # predicate parsing rejects malformed claims
    for bad in ({"f": "n", "predicate": "bogus", "range": [0, 1]},
                {"f": "", "predicate": "prime", "range": [0, 1]},
                {"f": "n+m", "predicate": "prime", "range": [0, 1]},       # foreign var m
                {"f": "n", "predicate": "divisible", "k": 0, "range": [0, 1]},   # k=0
                {"f": "n", "predicate": "congruent", "m": 0, "r": 0, "range": [0, 1]},  # m=0
                "this is not a predicate claim at all"):
        try:
            parse_predicate_claim(bad)
            errs.append("parse_predicate_claim accepted malformed: %s" % (bad,))
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
    # The argument is either a path to a JSON claim, or — for the predicate shapes — a literal
    # natural-language string ("n^2 - n + 41 is prime for all n >= 0"). Try to read it as a file
    # holding JSON; if that fails to be valid JSON, fall back to treating argv[0] as the claim text.
    raw = argv[0]
    doc = None
    try:
        with open(raw, encoding="utf-8") as fh:
            text = fh.read()
        try:
            doc = json.loads(text)
        except json.JSONDecodeError:
            doc = text.strip()          # a file holding a plain claim sentence
    except OSError:
        doc = raw                       # not a file — treat the argument itself as the claim text
    try:
        if _is_predicate_doc(doc):
            holds, info = predicate_search(doc)
        else:
            holds, info = search(doc)
    except (ValueError, UnsafeExpr) as e:
        sys.stderr.write("numeric-spotcheck: invalid claim — %s\n" % e)
        return 2
    if holds:
        print("numeric-spotcheck: no counterexample in %s over %d sample(s) — corroborated, NOT proven"
              % (info["range"], info["checked"]))
        return 0
    ce = info.get("counterexample", {})
    detail = info.get("reason") or ("evaluates to %r, not True" % info.get("value"))
    witness = info.get("mod_witness")
    sys.stderr.write("numeric-spotcheck: COUNTEREXAMPLE at %s — the claim is FALSE (%s; checked %d)\n"
                     % (ce, detail, info.get("checked", 0)))
    if witness:
        sys.stderr.write("  modular witness: %s\n" % witness)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
