#!/usr/bin/env python3
"""sql-lint.py — the query-decomposer SQL smell linter. Self-contained (stdlib only).

A query that returns rows is evidence of nothing if its grain is wrong or it's unsafe. This is the
mechanized static pre-filter for the smells that *correlate* with a wrong-grain or catastrophic
query (the "returns rows, wrong question/grain" quadrant and the B5 safety defects). It tokenizes
SQL with regex + simple bracket/quote stripping (best-effort, not a full parser) and flags:

  SELECT_STAR          SELECT * — hides the result columns, so you can't see the grain key
  MISSING_WHERE_DML    UPDATE/DELETE with no WHERE — rewrites the whole table (catastrophic)
  IMPLICIT_CROSS_JOIN  a FROM with multiple comma-separated tables and no join predicate (cartesian)
  LIMIT_NO_ORDER       LIMIT with no ORDER BY — a nondeterministic page
  GROUP_BY_INCOMPLETE  heuristic: more non-aggregated SELECT columns than GROUP BY keys (likely gap)
  JOIN_FANOUT          ≥2 joined tables with no GROUP BY/DISTINCT/aggregate — row grain may multiply
  OUTER_JOIN_DEMOTED   a WHERE predicate on a LEFT/RIGHT-JOIN'd table silently demotes it to INNER
  NON_SARGABLE         a WHERE/JOIN-ON predicate wraps a column in a function/arithmetic, or a
                       leading-wildcard LIKE — defeats an index on that column (A5/B4)

Findings are advisory signals for the SEMANTICS axis (A3/A4) and EXECUTION B5 — pair with the live
grain check (COUNT(*) vs COUNT(DISTINCT key)) and an EXPLAIN read for proof.

  python3 bin/sql-lint.py selftest
  python3 bin/sql-lint.py <file | dir>

Python 3.8+.
"""
import os
import re
import sys

# --- normalization: strip comments + string/identifier literals so keywords scan cleanly ----------
_LINE_COMMENT = re.compile(r"--[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_STRING_LIT = re.compile(r"'(?:''|[^'])*'")        # SQL single-quote string (doubled '' escape)
_DQUOTE_ID = re.compile(r'"(?:[^"])*"')            # double-quoted identifier
_BACKTICK_ID = re.compile(r"`(?:[^`])*`")          # MySQL/BigQuery identifier


def _blank_keep_newlines(m):
    """Replace a matched region with spaces of the SAME length, preserving newlines — so the
    normalized text stays positionally aligned with the original (line numbers don't drift)."""
    return re.sub(r"[^\n]", " ", m.group(0))


def _blank_literal(quote):
    """Blank a quoted literal/identifier to same-length filler: keep the quotes, space the inside,
    preserve newlines. Length-preserving so offsets map 1:1 onto the original text."""
    def repl(m):
        text = m.group(0)
        inner = re.sub(r"[^\n]", " ", text[1:-1])
        return quote + inner + quote
    return repl


def normalize(sql):
    """Lower-case-able copy with comments + string/identifier literals blanked. LENGTH-PRESERVING:
    every replacement keeps the original character count and newlines, so a position in the result
    maps onto the same position in `sql` (callers compute line numbers from the original offset)."""
    s = _BLOCK_COMMENT.sub(_blank_keep_newlines, sql)
    s = _LINE_COMMENT.sub(_blank_keep_newlines, s)
    s = _STRING_LIT.sub(_blank_literal("'"), s)
    s = _DQUOTE_ID.sub(_blank_literal('"'), s)
    s = _BACKTICK_ID.sub(_blank_literal("`"), s)
    return s


def _statements(sql):
    """Split on top-level semicolons (good enough after literals are blanked)."""
    return [s for s in normalize(sql).split(";") if s.strip()]


def _strip_parens(s):
    """Remove parenthesised groups (subqueries, function args) so clause scanning stays top-level."""
    out, depth = [], 0
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def _clause(stmt_top, start_kw, end_kws):
    """Return the top-level text of `start_kw ... (next end_kw | end)`, or '' if absent."""
    m = re.search(r"(?i)\b%s\b" % start_kw, stmt_top)
    if not m:
        return ""
    rest = stmt_top[m.end():]
    ends = [e.start() for e in re.finditer(r"(?i)\b(?:%s)\b" % "|".join(end_kws), rest)]
    return rest[:min(ends)] if ends else rest


_AGG = re.compile(r"(?i)\b(count|sum|avg|min|max|array_agg|string_agg|group_concat|stddev|variance)\s*\(")
_FROM_ENDS = ["where", "group by", "having", "order by", "limit", "window", "qualify", "union", "join",
              "left", "right", "inner", "outer", "cross", "full", "on"]
_SELECT_ENDS = ["from"]
# a real join predicate is `ident.ident = ident.ident` (column = column), NOT `col = 'literal'`,
# `1=1`, or `col >= 18`. Only such a predicate suppresses IMPLICIT_CROSS_JOIN.
_COL = r"[A-Za-z_][A-Za-z0-9_$]*(?:\.[A-Za-z_][A-Za-z0-9_$]*)+"   # requires a dotted qualifier
_COL_EQ_COL = re.compile(r"(?i)(?<![<>!])(?:%s)\s*=\s*(?:%s)(?!=)" % (_COL, _COL))
# a window function is a top-level `... OVER (...)`; such a SELECT item is not a "non-aggregated column"
_OVER = re.compile(r"(?i)\bover\s*\(")
# a pure literal/constant SELECT item: a number, a blanked string ('...' of spaces after normalize),
# or TRUE/FALSE/NULL. (normalize() leaves quoted strings as '<spaces>'.)
_LITERAL_ITEM = re.compile(r"(?i)^(?:[-+]?\d+(?:\.\d+)?|'\s*'|true|false|null)$")

# JOIN_FANOUT — any explicit JOIN keyword (LEFT/RIGHT/INNER/OUTER/CROSS/FULL JOIN or bare JOIN).
_JOIN_KW = re.compile(r"(?i)\bjoin\b")
# OUTER_JOIN_DEMOTED — a LEFT/RIGHT [OUTER] JOIN clause: capture the joined table and its optional
# alias. Groups: 1=table, 2=alias (None if omitted; `AS` keyword optional, never `ON`/`USING`).
_OUTER_JOIN = re.compile(
    r"(?i)\b(?:left|right)\s+(?:outer\s+)?join\s+"
    r"([A-Za-z_][A-Za-z0-9_$]*(?:\.[A-Za-z_][A-Za-z0-9_$]*)*)"          # 1: table (maybe schema-qualified)
    r"(?:\s+(?:as\s+)?(?!on\b|using\b|where\b|left\b|right\b|inner\b|join\b|on\b)"
    r"([A-Za-z_][A-Za-z0-9_$]*))?"                                       # 2: optional alias
)

# NON_SARGABLE — a predicate that wraps a likely-indexed COLUMN in a function or arithmetic (or a
# leading-wildcard LIKE) defeats an index on the raw column. Detect on WHERE/JOIN-ON predicates only.
_BARE_COL = r"[A-Za-z_][A-Za-z0-9_$]*(?:\.[A-Za-z_][A-Za-z0-9_$]*)*"     # ident, optionally qualified
_CMP = r"(?:<=|>=|<>|!=|=|<|>)"                                          # plain comparison operators
# 1: a FUNCTION wrapping a column on a comparison side — `FN(col ...) <cmp>` or `<cmp> FN(col ...)`.
#    The first arg must be a bare column (not a literal/another call); a leading `(` arg-list rules out
#    nested calls like `LOWER(TRIM(x))` matching `x` directly, but the OUTER fn still flags the column.
_FN_OF_COL = (r"([A-Za-z_][A-Za-z0-9_$]*)\s*\(\s*"                       # 1: function name
              r"(%s)" % _BARE_COL +                                     # 2: the wrapped column (first arg)
              r"(?:\s*,[^()]*)?\s*\)")                                  # optional further args, no nested ()
_NON_SARG_FN_LEFT = re.compile(r"(?i)%s\s*%s" % (_FN_OF_COL, _CMP))     # FN(col...) <cmp>
_NON_SARG_FN_RIGHT = re.compile(r"(?i)%s\s*%s" % (_CMP, _FN_OF_COL))    # <cmp> FN(col...)
# 2: ARITHMETIC on a column on a comparison side — `col <+-*/> <number>` then a comparison, or the
#    mirror. Require a numeric operand so a join `a.x = b.y` (no arithmetic) never matches.
_ARITH = r"[-+*/]"
_NON_SARG_ARITH_LEFT = re.compile(
    r"(?i)(%s)\s*%s\s*[-+]?\d+(?:\.\d+)?\s*%s" % (_BARE_COL, _ARITH, _CMP))    # col*1.2 > ...
_NON_SARG_ARITH_RIGHT = re.compile(
    r"(?i)%s\s*[-+]?\d+(?:\.\d+)?\s*%s\s*(%s)" % (_CMP, _ARITH, _BARE_COL))    # ... < col+0   (mirror)
# 3: a LEADING-wildcard LIKE — `col LIKE '%...'`. After normalize() a string literal is '<spaces>', so
#    the leading wildcard survives as the first inner char being '%' only if the ORIGINAL started '%'.
#    normalize blanks the inside to spaces, so we test the ORIGINAL literal, not the normalized one.
_LIKE_COL = re.compile(r"(?i)(%s)\s+(?:not\s+)?like\s+'" % _BARE_COL)
# function names that are NOT a column transform when they wrap something — pure aggregates belong to
# HAVING/SELECT, not a WHERE column-index smell; we additionally scope by clause, but guard the name too.
_SARG_FN_SKIP = {"now", "current_date", "current_timestamp", "current_time"}


def analyze_sql(sql):
    """Yield (kind, line, detail) findings for a SQL string (possibly multiple statements)."""
    finds = []
    norm = normalize(sql)
    # work statement-by-statement but keep line numbers against the ORIGINAL text
    offset = 0
    raw_stmts = norm.split(";")
    for raw in raw_stmts:
        if not raw.strip():
            offset += len(raw) + 1
            continue
        line = sql.count("\n", 0, offset + (len(raw) - len(raw.lstrip()))) + 1
        # normalize() is LENGTH-PRESERVING, so this original slice aligns 1:1 with `raw` (offsets map),
        # letting the leading-`%` LIKE check read the un-blanked literal that `raw` blanked to spaces.
        orig = sql[offset:offset + len(raw)]
        finds += _analyze_one(raw, line, orig)
        offset += len(raw) + 1
    return finds


def _analyze_one(stmt, line, orig=None):
    if orig is None:
        orig = stmt
    finds = []
    low = stmt.lower()
    top = _strip_parens(stmt)            # top-level clauses only (subqueries excluded from clause scans)
    low_top = top.lower()

    # SELECT_STAR — only at the top level of a SELECT (ignore COUNT(*), subquery stars handled by paren-strip)
    if re.search(r"(?i)\bselect\b", top) and re.search(r"(?i)\bselect\s+(?:distinct\s+)?\*", top):
        finds.append(("SELECT_STAR", line, "SELECT * hides the result columns / grain key"))

    # MISSING_WHERE_DML — UPDATE/DELETE with no top-level WHERE. Matches both a bare statement and a
    # CTE-led one (`WITH cte AS (...) DELETE FROM t`): look for a top-level (paren-stripped) UPDATE/
    # DELETE verb, so a DELETE nested inside a CTE subquery (which IS parenthesized) doesn't count here
    # and the governing top-level statement's missing WHERE is still caught.
    m = re.search(r"(?i)\b(update|delete)\b", top)
    if m and not re.search(r"(?i)\bwhere\b", top):
        finds.append(("MISSING_WHERE_DML", line,
                      "%s with no WHERE — rewrites the whole table" % m.group(1).upper()))

    # IMPLICIT_CROSS_JOIN — a FROM with >1 comma-separated table and no join predicate.
    # A join predicate is a top-level `ident.ident = ident.ident` (column=column) in the WHERE — NOT
    # merely the presence of `=`: `WHERE a.status='x'`, `WHERE 1=1`, `WHERE a.age>=18` are all filters,
    # not joins, and must NOT suppress the cartesian flag.
    from_clause = _clause(top, "from", _FROM_ENDS)
    if from_clause:
        tables = [t for t in from_clause.split(",") if t.strip()]
        has_join_kw = bool(re.search(r"(?i)\bjoin\b", top))
        where_clause = _clause(top, "where", ["group by", "having", "order by", "limit"])
        has_join_predicate = bool(_COL_EQ_COL.search(where_clause))
        if len(tables) > 1 and not has_join_kw and not has_join_predicate:
            finds.append(("IMPLICIT_CROSS_JOIN", line,
                          "FROM lists %d tables with no join predicate — cartesian product" % len(tables)))

    # LIMIT_NO_ORDER — top-level LIMIT with no top-level ORDER BY
    if re.search(r"(?i)\blimit\b", low_top) and not re.search(r"(?i)\border\s+by\b", low_top):
        finds.append(("LIMIT_NO_ORDER", line, "LIMIT with no ORDER BY — nondeterministic page"))

    # GROUP_BY_INCOMPLETE — heuristic: a GROUP BY exists, but the SELECT lists non-aggregated columns
    # beyond the group keys. Use the full statement (parens INTACT) so aggregate calls like SUM(x) are
    # still detectable; _split_top_commas respects paren depth so subquery/function commas don't split.
    gb = _clause(stmt, "group by", ["having", "order by", "limit", "qualify", "window"])
    if gb.strip():
        sel = _clause(stmt, "select", _SELECT_ENDS)
        sel = re.sub(r"(?i)^\s*distinct\b", "", sel)
        sel_items = [c for c in _split_top_commas(sel) if c.strip()]
        non_agg = [c for c in sel_items if not _is_aggregated_item(c)]
        gb_keys = [k for k in _split_top_commas(gb) if k.strip()]
        if non_agg and len(non_agg) > len(gb_keys):
            finds.append(("GROUP_BY_INCOMPLETE", line,
                          "%d non-aggregated SELECT columns but %d GROUP BY keys — likely incomplete GROUP BY"
                          % (len(non_agg), len(gb_keys))))

    # JOIN_FANOUT — ≥2 joined tables (explicit JOINs + comma-FROM tables beyond the first) and NO
    # GROUP BY, NO SELECT DISTINCT, NO aggregate in SELECT ⇒ a 1:N × 1:N fan-out can silently multiply
    # rows (returns rows, wrong grain). Conservative: any collapsing construct suppresses the flag.
    # Count on the top-level statement (parens stripped) so JOINs/commas inside subqueries don't count.
    if re.search(r"(?i)\bselect\b", top):
        join_count = len(_JOIN_KW.findall(top))
        comma_tables = 0
        if from_clause:                                  # from_clause computed above (top-level FROM)
            comma_tables = max(0, len([t for t in from_clause.split(",") if t.strip()]) - 1)
        joined = join_count + comma_tables
        sel_fan = _clause(stmt, "select", _SELECT_ENDS)  # full statement so SUM(...) is detectable
        has_distinct = bool(re.search(r"(?i)^\s*distinct\b", sel_fan.strip()))
        has_group_by = bool(gb.strip())                  # gb computed above (top-level GROUP BY)
        has_agg = bool(_AGG.search(sel_fan))
        if joined >= 2 and not has_group_by and not has_distinct and not has_agg:
            finds.append(("JOIN_FANOUT", line,
                          "%d joins with no GROUP BY/DISTINCT/aggregate — row grain may multiply; "
                          "verify with COUNT(*) vs COUNT(DISTINCT <key>)" % joined))

    # OUTER_JOIN_DEMOTED — a LEFT/RIGHT [OUTER] JOIN whose table/alias appears in WHERE under a plain
    # comparison (=,<,>,<=,>=,<>,!=,LIKE,IN) — but NOT `IS [NOT] NULL` — silently demotes the outer
    # join to an INNER join (the NULL-extended rows get filtered out). `WHERE o.id IS NULL` is the
    # legitimate anti-join and must NOT flag; a predicate on the LEFT (driving) table must NOT flag.
    where_for_outer = _clause(top, "where", ["group by", "having", "order by", "limit", "qualify", "window"])
    if where_for_outer.strip():
        for tbl, alias in _OUTER_JOIN.findall(top):
            ref = alias or tbl                           # the name the WHERE would reference
            if _outer_demoting_predicate(where_for_outer, ref):
                finds.append(("OUTER_JOIN_DEMOTED", line,
                              "WHERE predicate on the outer-joined '%s' demotes the LEFT JOIN to "
                              "INNER — move it to the ON clause or use IS NULL" % ref))

    # NON_SARGABLE — a WHERE or JOIN-ON predicate that wraps a likely-indexed COLUMN in a function or
    # arithmetic (or uses a leading-wildcard LIKE) defeats an index on the raw column. Scoped to
    # WHERE/JOIN-ON predicate regions ONLY — NOT HAVING (its aggregates are not a column-index smell)
    # and NOT bare SELECT items. Each region carries the offset into `stmt` so the leading-`%` LIKE
    # check can read the un-blanked literal from `orig` (length-preserving normalize ⇒ offsets align).
    seen = set()                                         # de-dupe identical (col, kind) within a stmt
    for region, base in _sargable_regions(stmt, top):
        for col, why in _non_sargable_hits(region, orig, base):
            key = (col.lower(), why)
            if key in seen:
                continue
            seen.add(key)
            finds.append(("NON_SARGABLE", line,
                          "predicate wraps column '%s' in %s — defeats an index on it; move the "
                          "transform to the literal side or store a computed column" % (col, why)))
    return finds


def _strip_alias(item):
    """Drop a trailing `AS alias` (bare, double-quoted, or backtick-quoted — quoted forms are blanked
    to '<spaces>' by normalize) so we test the expression, not its label."""
    s = item.strip()
    s = re.sub(r"""(?i)\s+as\s+(?:"\s*"|`\s*`|[A-Za-z_][A-Za-z0-9_$]*)\s*$""", "", s)
    return s.strip()


def _is_aggregated_item(item):
    """A SELECT item that does NOT count as a 'non-aggregated column' for the GROUP BY check:
    an aggregate call (SUM/COUNT/...), a window function (top-level `OVER (...)`), or a pure
    literal/constant ('summary', 42, TRUE). Such items are legal in a grouped SELECT regardless of
    the GROUP BY, so they must not inflate the non-aggregated count."""
    if _AGG.search(item):
        return True
    if _OVER.search(item):                       # a window function: RANK() OVER (...), etc.
        return True
    if _LITERAL_ITEM.match(_strip_alias(item)):  # a bare literal/constant select item
        return True
    return False


def _outer_demoting_predicate(where_clause, ref):
    """True iff `where_clause` contains a plain predicate on a column of `ref` (an outer-joined table
    or its alias) that is NOT an `IS [NOT] NULL` test — such a predicate filters out the NULL-extended
    rows and silently demotes the LEFT/RIGHT JOIN to INNER. `ref.col IS NULL` is the legitimate
    anti-join and is excluded; a column on a *different* table is excluded (the `\bref\.` anchor)."""
    col = r"\b%s\.[A-Za-z_][A-Za-z0-9_$]*\b" % re.escape(ref)
    # the whole expression of interest must be `ref.col <op> ...`; if the operator is IS [NOT] NULL it
    # is an anti-join, not a demotion. Match `ref.col` then look at what immediately follows.
    for m in re.finditer(r"(?i)%s\s*" % col, where_clause):
        tail = where_clause[m.end():].lstrip().lower()
        if tail.startswith("is "):                       # `IS NULL` / `IS NOT NULL` — anti-join, OK
            continue
        # a plain comparison / membership / pattern predicate demotes the join
        if re.match(r"(?i)(?:<=|>=|<>|!=|=|<|>|like\b|in\b|between\b)", tail):
            return True
    return False


# clause keywords that END a WHERE region (the next top-level clause), and an ON region (the next
# JOIN/structural keyword). Used to bound the predicate text NON_SARGABLE scans.
_WHERE_REGION_ENDS = r"(?i)\b(?:group\s+by|having|order\s+by|limit|qualify|window|union|except|intersect)\b"
_ON_REGION_ENDS = (r"(?i)\b(?:where|group\s+by|having|order\s+by|limit|qualify|window|union|"
                   r"join|left|right|inner|outer|cross|full)\b")


def _sargable_regions(stmt, top):
    """Yield (text, base_offset) for each predicate region NON_SARGABLE should scan: the WHERE clause
    and every JOIN ... ON clause — WITH parens intact (so `FN(col)` survives) and with the offset into
    `stmt` (so a hit's position maps back onto `orig` for the leading-`%` LIKE check). HAVING and bare
    SELECT items are deliberately excluded — a HAVING aggregate is not a column-index smell."""
    regions = []
    # the WHERE clause (parens intact). Find the top-level WHERE, then bound it by the next clause kw.
    wm = re.search(r"(?i)\bwhere\b", top)                # use `top` to find a TOP-LEVEL where
    if wm:
        # re-locate the same WHERE in `stmt` (parens intact). The first WHERE in `top` corresponds to
        # the first top-level WHERE in `stmt`; subquery WHEREs are inside parens, so we walk depth.
        start = _top_level_kw_offset(stmt, "where")
        if start is not None:
            rest = stmt[start:]
            end = _first_kw(rest, _WHERE_REGION_ENDS)
            regions.append((rest[:end], start))
    # every JOIN ... ON predicate (top-level). Scan `stmt` at depth 0 for `on`, bound by the next kw.
    for start in _top_level_kw_offsets(stmt, "on"):
        rest = stmt[start:]
        end = _first_kw(rest, _ON_REGION_ENDS)
        regions.append((rest[:end], start))
    return regions


def _first_kw(s, kw_re):
    """Offset of the first top-level (depth-0) regex match of `kw_re` in `s`, or len(s)."""
    depth = 0
    for m in re.finditer(kw_re, s):
        # only accept a match that sits at paren-depth 0
        if s[:m.start()].count("(") - s[:m.start()].count(")") == 0:
            return m.start()
    return len(s)


def _top_level_kw_offset(s, kw):
    """Offset just AFTER the first depth-0 occurrence of word `kw`, or None."""
    offs = _top_level_kw_offsets(s, kw)
    return offs[0] if offs else None


def _top_level_kw_offsets(s, kw):
    """All offsets just AFTER each depth-0 occurrence of the whole-word `kw` (case-insensitive)."""
    out = []
    for m in re.finditer(r"(?i)\b%s\b" % kw, s):
        if s[:m.start()].count("(") - s[:m.start()].count(")") == 0:
            out.append(m.end())
    return out


def _non_sargable_hits(region, orig, base):
    """Yield (column, reason) for each non-sargable predicate in `region` (a WHERE/ON predicate text,
    parens intact). `base` is region's offset into `stmt`; `orig` is the original (un-blanked) text of
    the whole statement, length-aligned with `stmt` — used to read the leading-`%` of a LIKE literal.

    Three smells: (1) a function wrapping a column on a comparison side; (2) arithmetic on a column on a
    comparison side; (3) a leading-wildcard LIKE. FP guards: a fn/arith on the LITERAL side only does
    NOT match (the column stays bare); `NOW()`/`CURRENT_*` on the literal side is skipped; an anchored
    `LIKE 'x%'` does NOT match (only a LEADING `%` does); a bare `col = 'lit'` does NOT match."""
    hits = []
    # (1) FN(col) on either comparison side
    for rx in (_NON_SARG_FN_LEFT, _NON_SARG_FN_RIGHT):
        for m in rx.finditer(region):
            fn, col = m.group(1), m.group(2)
            if fn.lower() in _SARG_FN_SKIP:              # NOW()/CURRENT_* — not a column transform
                continue
            if _LITERAL_ITEM.match(col):                 # FN(42) / FN('x') — literal arg, column is bare
                continue
            hits.append((col, "function %s()" % fn.upper()))
    # (2) arithmetic on a column on either comparison side
    for rx in (_NON_SARG_ARITH_LEFT, _NON_SARG_ARITH_RIGHT):
        for m in rx.finditer(region):
            col = m.group(1)
            if _LITERAL_ITEM.match(col):                 # a numeric op on a literal — not a column
                continue
            hits.append((col, "arithmetic"))
    # (3) a LEADING-wildcard LIKE — read the un-blanked literal from `orig` at the literal's offset
    for m in _LIKE_COL.finditer(region):
        col = m.group(1)
        lit_at = base + m.end()                          # position of the opening quote's NEXT char
        if lit_at < len(orig) and orig[lit_at] == "%":   # leading wildcard ⇒ non-sargable
            hits.append((col, "a leading-wildcard LIKE"))
    return hits


def _split_top_commas(s):
    """Split on commas not inside parentheses."""
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
            cur.append(ch)
        elif ch == ")":
            depth = max(0, depth - 1)
            cur.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur))
    return out


def _is_sql_file(fn):
    return fn.endswith(".sql")


# --- selftest fixtures -------------------------------------------------------------------------
SQL_CLEAN = """
SELECT c.id, SUM(o.amount) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'paid'
GROUP BY c.id
ORDER BY revenue DESC
LIMIT 10;
"""

SQL_STAR = "SELECT * FROM orders WHERE status = 'paid';"
SQL_DML = "DELETE FROM sessions;"
SQL_DML_OK = "DELETE FROM sessions WHERE expires_at < now();"
SQL_CROSS = "SELECT a.id, b.id FROM users a, roles b;"
SQL_CROSS_OK = "SELECT a.id, b.id FROM users a, roles b WHERE a.role_id = b.id;"
SQL_LIMIT = "SELECT id FROM events LIMIT 50;"
SQL_GROUP = "SELECT region, city, SUM(amount) FROM sales GROUP BY region;"
# a COUNT(*) and a string literal with a keyword must not trip SELECT_STAR / clause scans:
SQL_TRICKY = "SELECT COUNT(*) AS n FROM logs WHERE message = 'limit reached' GROUP BY day ORDER BY day;"

# B1 — a real cartesian whose only WHERE predicate is a LITERAL filter must still FLAG (the `=` alone
# must not suppress it). Also exercises `WHERE 1=1` and `WHERE a.age>=18`, which used to defeat it.
SQL_CROSS_LITERAL = "SELECT a.id, b.id FROM users a, roles b WHERE a.status = 'x';"
SQL_CROSS_TRUE = "SELECT a.id, b.id FROM users a, roles b WHERE 1=1;"
SQL_CROSS_RANGE = "SELECT a.id, b.id FROM users a, roles b WHERE a.age >= 18;"
# and the genuine column=column join predicate must still NOT flag (alias of SQL_CROSS_OK's shape):
SQL_CROSS_JOINED = "SELECT a.id, b.id FROM users a, roles b WHERE a.x = b.y;"

# M2 — a window function and a constant SELECT item are legal in a grouped SELECT and must NOT
# inflate GROUP_BY_INCOMPLETE:
SQL_GROUP_WINDOW = "SELECT region, RANK() OVER (ORDER BY total DESC), SUM(total) FROM sales GROUP BY region;"
SQL_GROUP_CONST = "SELECT region, 'summary' AS kind, SUM(amt) FROM sales GROUP BY region;"

# minor m1 — a leading comment must not drift the reported line number (statement starts on line 3):
SQL_COMMENT_LINE = "-- a leading note\n-- another note\nDELETE FROM sessions;"
# minor m3 — a CTE-led DELETE with no WHERE must FLAG (re.match start-anchor used to miss it):
SQL_CTE_DELETE = "WITH stale AS (SELECT id FROM sessions WHERE expires_at < now()) DELETE FROM sessions;"

# J1 — JOIN_FANOUT: ≥2 joins of a parent to distinct tables, NO GROUP BY / DISTINCT / aggregate ⇒
# items × payments cross-multiply (the #1 grain killer). Must FLAG.
SQL_FANOUT = ("SELECT o.id, i.sku, p.amount FROM orders o "
              "JOIN items i ON i.order_id=o.id JOIN payments p ON p.order_id=o.id;")
# ...and the suppressors must NOT flag:
SQL_FANOUT_ONEJOIN = "SELECT o.id, i.sku FROM orders o JOIN items i ON i.order_id=o.id;"  # single join
SQL_FANOUT_GROUP = ("SELECT o.id, COUNT(*) FROM orders o "
                    "JOIN items i ON i.order_id=o.id JOIN payments p ON p.order_id=o.id GROUP BY o.id;")
SQL_FANOUT_DISTINCT = ("SELECT DISTINCT o.id FROM orders o "
                       "JOIN items i ON i.order_id=o.id JOIN payments p ON p.order_id=o.id;")
SQL_FANOUT_AGG = ("SELECT SUM(p.amount) FROM orders o "
                  "JOIN items i ON i.order_id=o.id JOIN payments p ON p.order_id=o.id;")  # aggregate rollup

# O1 — OUTER_JOIN_DEMOTED: a WHERE predicate on the LEFT-JOIN'd table demotes it to INNER. Must FLAG.
SQL_DEMOTE = ("SELECT u.id FROM users u "
              "LEFT JOIN orders o ON o.user_id=u.id WHERE o.status='paid';")
# ...and the safe forms must NOT flag:
SQL_DEMOTE_ISNULL = ("SELECT u.id FROM users u "
                     "LEFT JOIN orders o ON o.user_id=u.id WHERE o.id IS NULL;")          # anti-join
SQL_DEMOTE_LEFTCOL = ("SELECT u.id FROM users u "
                      "LEFT JOIN orders o ON o.user_id=u.id WHERE u.active='t';")          # predicate on LEFT table
SQL_DEMOTE_INNER = ("SELECT u.id FROM users u "
                    "INNER JOIN orders o ON o.user_id=u.id WHERE o.status='paid';")        # already INNER

# N1 — NON_SARGABLE: a WHERE/JOIN-ON predicate wrapping an indexed column in a function/arithmetic, or
# a leading-wildcard LIKE, defeats the index (A5/B4). Each must FLAG:
SQL_SARG_FN_DATE = "SELECT id FROM events WHERE DATE(created_at) = '2026-01-01';"           # function on col
SQL_SARG_FN_UPPER = "SELECT id FROM users WHERE UPPER(name) = 'X';"                         # function on col
SQL_SARG_ARITH = "SELECT id FROM items WHERE price * 1.2 > 100;"                            # arithmetic on col
SQL_SARG_LIKE_LEAD = "SELECT id FROM users WHERE name LIKE '%foo';"                         # leading-% LIKE
SQL_SARG_ON = "SELECT a.id FROM a JOIN b ON DATE(a.ts) = b.d;"                              # in a JOIN ON
# ...and the sargable / out-of-scope forms must NOT flag:
SQL_SARG_LIT_SIDE = "SELECT id FROM events WHERE created_at = DATE('2026-01-01');"          # fn on LITERAL side
SQL_SARG_NOW = "SELECT id FROM events WHERE ts >= NOW() - INTERVAL '7 days';"               # NOW() on literal side
SQL_SARG_LIKE_ANCHOR = "SELECT id FROM users WHERE name LIKE 'foo%';"                       # anchored LIKE (sargable)
SQL_SARG_BARE = "SELECT id FROM users WHERE status = 'active';"                             # bare col = literal
SQL_SARG_HAVING = ("SELECT region, COUNT(*) FROM sales "
                   "GROUP BY region HAVING COUNT(*) > 5;")                                  # HAVING aggregate, not WHERE
SQL_SARG_FN_IN_STRING = "SELECT id FROM t WHERE note = 'DATE(created_at) = today';"         # fn inside a string literal


def selftest():
    errs = []

    def kinds(sql):
        return {k for k, _, _ in analyze_sql(sql)}

    # clean query: no findings
    c = analyze_sql(SQL_CLEAN)
    if c:
        errs.append("false positive on clean query: %s" % c)
    # each smell is caught
    if "SELECT_STAR" not in kinds(SQL_STAR):
        errs.append("missed SELECT_STAR")
    if "MISSING_WHERE_DML" not in kinds(SQL_DML):
        errs.append("missed MISSING_WHERE_DML")
    if "IMPLICIT_CROSS_JOIN" not in kinds(SQL_CROSS):
        errs.append("missed IMPLICIT_CROSS_JOIN")
    if "LIMIT_NO_ORDER" not in kinds(SQL_LIMIT):
        errs.append("missed LIMIT_NO_ORDER")
    if "GROUP_BY_INCOMPLETE" not in kinds(SQL_GROUP):
        errs.append("missed GROUP_BY_INCOMPLETE")
    # no false positives on the safe variants
    if "MISSING_WHERE_DML" in kinds(SQL_DML_OK):
        errs.append("false positive MISSING_WHERE_DML on guarded DELETE")
    if "IMPLICIT_CROSS_JOIN" in kinds(SQL_CROSS_OK):
        errs.append("false positive IMPLICIT_CROSS_JOIN on a WHERE-joined query")
    # tricky: COUNT(*) is not SELECT_STAR; 'limit reached' literal is not a LIMIT; ORDER BY present
    tk = kinds(SQL_TRICKY)
    if "SELECT_STAR" in tk:
        errs.append("false positive SELECT_STAR on COUNT(*)")
    if "LIMIT_NO_ORDER" in tk:
        errs.append("false positive LIMIT_NO_ORDER (literal 'limit reached' / ORDER BY present)")

    # B1 — a `=` that is a literal/range/constant filter must NOT suppress the cartesian flag
    if "IMPLICIT_CROSS_JOIN" not in kinds(SQL_CROSS_LITERAL):
        errs.append("missed IMPLICIT_CROSS_JOIN with a literal WHERE filter (col='x')")
    if "IMPLICIT_CROSS_JOIN" not in kinds(SQL_CROSS_TRUE):
        errs.append("missed IMPLICIT_CROSS_JOIN with WHERE 1=1")
    if "IMPLICIT_CROSS_JOIN" not in kinds(SQL_CROSS_RANGE):
        errs.append("missed IMPLICIT_CROSS_JOIN with a range predicate (a.age>=18)")
    # ...but a genuine column=column join predicate still must NOT flag
    if "IMPLICIT_CROSS_JOIN" in kinds(SQL_CROSS_JOINED):
        errs.append("false positive IMPLICIT_CROSS_JOIN on a column=column join (a.x=b.y)")

    # M2 — window functions and constant SELECT items must NOT inflate GROUP_BY_INCOMPLETE
    if "GROUP_BY_INCOMPLETE" in kinds(SQL_GROUP_WINDOW):
        errs.append("false positive GROUP_BY_INCOMPLETE on a window function (RANK() OVER ...)")
    if "GROUP_BY_INCOMPLETE" in kinds(SQL_GROUP_CONST):
        errs.append("false positive GROUP_BY_INCOMPLETE on a constant SELECT item ('summary' AS kind)")

    # minor m1 — line number does not drift past leading comments (DELETE is on line 3)
    cl = [ln for k, ln, _ in analyze_sql(SQL_COMMENT_LINE) if k == "MISSING_WHERE_DML"]
    if cl != [3]:
        errs.append("line number drifted past leading comments: got %s, want [3]" % cl)
    # minor m3 — a CTE-led DELETE with no WHERE is caught
    if "MISSING_WHERE_DML" not in kinds(SQL_CTE_DELETE):
        errs.append("missed MISSING_WHERE_DML on a CTE-led DELETE (WITH ... DELETE)")

    # J1 — JOIN_FANOUT: ≥2 joins with no GROUP BY/DISTINCT/aggregate must FLAG...
    if "JOIN_FANOUT" not in kinds(SQL_FANOUT):
        errs.append("missed JOIN_FANOUT on a 2-join query with no GROUP BY/DISTINCT/aggregate")
    # ...and every suppressor must NOT flag
    if "JOIN_FANOUT" in kinds(SQL_FANOUT_ONEJOIN):
        errs.append("false positive JOIN_FANOUT on a single-join query")
    if "JOIN_FANOUT" in kinds(SQL_FANOUT_GROUP):
        errs.append("false positive JOIN_FANOUT on a ≥2-join query WITH GROUP BY")
    if "JOIN_FANOUT" in kinds(SQL_FANOUT_DISTINCT):
        errs.append("false positive JOIN_FANOUT on a ≥2-join query WITH SELECT DISTINCT")
    if "JOIN_FANOUT" in kinds(SQL_FANOUT_AGG):
        errs.append("false positive JOIN_FANOUT on a ≥2-join aggregate rollup (SUM(...))")

    # O1 — OUTER_JOIN_DEMOTED: a plain WHERE predicate on the LEFT-JOIN'd table must FLAG...
    if "OUTER_JOIN_DEMOTED" not in kinds(SQL_DEMOTE):
        errs.append("missed OUTER_JOIN_DEMOTED on a WHERE predicate against the LEFT-JOIN'd table")
    # ...and the legitimate / unaffected forms must NOT flag
    if "OUTER_JOIN_DEMOTED" in kinds(SQL_DEMOTE_ISNULL):
        errs.append("false positive OUTER_JOIN_DEMOTED on an IS NULL anti-join")
    if "OUTER_JOIN_DEMOTED" in kinds(SQL_DEMOTE_LEFTCOL):
        errs.append("false positive OUTER_JOIN_DEMOTED on a predicate against the LEFT (driving) table")
    if "OUTER_JOIN_DEMOTED" in kinds(SQL_DEMOTE_INNER):
        errs.append("false positive OUTER_JOIN_DEMOTED on an INNER JOIN with the same WHERE")

    # N1 — NON_SARGABLE: a function/arithmetic wrapping a column, or a leading-% LIKE, must FLAG...
    if "NON_SARGABLE" not in kinds(SQL_SARG_FN_DATE):
        errs.append("missed NON_SARGABLE on a function-wrapped column (DATE(created_at)=...)")
    if "NON_SARGABLE" not in kinds(SQL_SARG_FN_UPPER):
        errs.append("missed NON_SARGABLE on a function-wrapped column (UPPER(name)=...)")
    if "NON_SARGABLE" not in kinds(SQL_SARG_ARITH):
        errs.append("missed NON_SARGABLE on arithmetic over a column (price*1.2>...)")
    if "NON_SARGABLE" not in kinds(SQL_SARG_LIKE_LEAD):
        errs.append("missed NON_SARGABLE on a leading-wildcard LIKE (name LIKE '%foo')")
    if "NON_SARGABLE" not in kinds(SQL_SARG_ON):
        errs.append("missed NON_SARGABLE on a function-wrapped column in a JOIN ON (DATE(a.ts)=...)")
    # ...and the sargable / out-of-scope forms must NOT flag
    if "NON_SARGABLE" in kinds(SQL_SARG_LIT_SIDE):
        errs.append("false positive NON_SARGABLE on a function on the LITERAL side (created_at=DATE(...))")
    if "NON_SARGABLE" in kinds(SQL_SARG_NOW):
        errs.append("false positive NON_SARGABLE on NOW()-INTERVAL on the literal side")
    if "NON_SARGABLE" in kinds(SQL_SARG_LIKE_ANCHOR):
        errs.append("false positive NON_SARGABLE on an anchored LIKE 'foo%' (sargable)")
    if "NON_SARGABLE" in kinds(SQL_SARG_BARE):
        errs.append("false positive NON_SARGABLE on a bare column = literal (status='active')")
    if "NON_SARGABLE" in kinds(SQL_SARG_HAVING):
        errs.append("false positive NON_SARGABLE on a HAVING aggregate (COUNT(*)>5 is not a WHERE smell)")
    if "NON_SARGABLE" in kinds(SQL_SARG_FN_IN_STRING):
        errs.append("false positive NON_SARGABLE on a function name inside a string literal")
    return errs


def main(argv):
    if not argv or argv[0] == "selftest":
        errs = selftest()
        if errs:
            sys.stderr.write("sql-lint: FAIL (%d)\n" % len(errs))
            for e in errs:
                sys.stderr.write("  - %s\n" % e)
            return 1
        print("sql-lint: OK — clean query passes; SELECT_STAR / MISSING_WHERE_DML / "
              "IMPLICIT_CROSS_JOIN / LIMIT_NO_ORDER / GROUP_BY_INCOMPLETE / JOIN_FANOUT / "
              "OUTER_JOIN_DEMOTED / NON_SARGABLE detectors verified")
        return 0
    path = argv[0]
    files = []
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            files += [os.path.join(dp, fn) for fn in sorted(fns) if _is_sql_file(fn)]
    else:
        files = [path]
    total = 0
    for fp in files:
        try:
            src = open(fp, encoding="utf-8").read()
        except OSError as e:
            print("  ⚠ %s: unreadable (%s)" % (fp, e))
            continue
        for kind, line, detail in analyze_sql(src):
            total += 1
            print("  %s:%s  %-19s %s" % (os.path.relpath(fp), line, kind, detail))
    if total:
        print("sql-lint: %d smell(s) across %d file(s) — verify grain with COUNT(*) vs COUNT(DISTINCT key)"
              % (total, len(files)))
        return 1
    print("sql-lint: OK — no smells in %d file(s)" % len(files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
