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

The `plan` subcommand reads a Postgres EXPLAIN (FORMAT JSON) document (structured JSON — robust, no
live DB needed) and flags EXECUTION-axis (B3/B4) plan smells the static SQL read cannot see:

  SEQ_SCAN             a Seq Scan with a Filter (or a large Plan Rows) — an index may be missing
  NESTED_LOOP_NO_INDEX a Nested Loop whose inner child is a Seq Scan — O(n*m) join, likely no index
  HIGH_COST_SORT       a Sort / Hash Aggregate over many rows (or a high Total Cost) — spill risk
  ROW_ESTIMATE_BLOWUP  (ANALYZE only) Actual Rows vs Plan Rows differ by >100x — stale-stats smell

  python3 bin/sql-lint.py selftest
  python3 bin/sql-lint.py <file | dir>            # lint .sql source
  python3 bin/sql-lint.py plan <explain.json>     # lint a Postgres EXPLAIN (FORMAT JSON) plan
  python3 bin/sql-lint.py [--json] <file | dir>   # machine-readable report (also: plan --json)

Exit convention (shared by both modes): any non-advisory smell ⇒ exit 1; otherwise exit 0. In the
SQL-source mode every smell is advisory-by-doctrine but still returns exit 1 so CI/automation keys on
it. The `plan` mode mirrors that: any plan smell ⇒ exit 1 (advisory findings are still printed).

`--json` (additive reporting flag; parse-anywhere in argv) prints ONE machine-readable report object to
stdout and NOTHING else there — the shared schema every lint bin emits, so GRADE/CI can fold structured
findings into the report card:
  {"tool": "sql-lint", "ok": <bool>, "summary": "<one line>",
   "findings": [{"kind", "severity": fail|advisory, "location": "line:N", "message"}, ...]}
`ok` is true iff no blocking finding (the exact condition that gives exit 0 in human mode). In the
SQL-source mode every finding is `fail` (advisory-by-doctrine but exit-1-blocking); in `plan` mode a
blocking smell is `fail` and an advisory one (SEQ_SCAN / HIGH_COST_SORT) is `advisory`. The exit code is
UNCHANGED by --json (it is a reporting flag, not a behavior change). Without --json, output + exit are
byte-identical to before.

Python 3.8+.
"""
import json
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


# --- EXPLAIN (FORMAT JSON) plan-smell parser ---------------------------------------------------
# The `plan` subcommand reads a Postgres `EXPLAIN (FORMAT JSON)` document — a top-level list whose
# first element is `{"Plan": {...}}`. Each Plan node carries a "Node Type" and (when present)
# "Relation Name", "Plan Rows", "Total Cost", "Filter"/"Index Cond", and a nested "Plans": [...].
# `EXPLAIN (ANALYZE, FORMAT JSON)` additionally carries "Actual Rows". We walk the tree top-down and
# flag the EXECUTION-axis (B3/B4) smells a static SQL read cannot see — routing the dangerous plan
# judgement to a deterministic parse of structured output, never to an LLM's read of the plan.
#
# Thresholds (deliberately coarse — these are advisory pre-filters, not a cost model):
_PLAN_ROWS_SEQ_SCAN = 10000      # a Seq Scan over this many estimated rows is worth a look even w/o a Filter
_PLAN_ROWS_HIGH_SORT = 100000    # a Sort / Hash Aggregate over this many rows risks an external (disk) spill
_PLAN_COST_HIGH_SORT = 1000000.0  # ...or a Total Cost this high
_ROW_BLOWUP_FACTOR = 100         # Actual vs estimated rows differing by this factor ⇒ stale-stats smell


def _plan_roots(doc):
    """Yield each top-level Plan node from a parsed EXPLAIN (FORMAT JSON) document. The canonical shape
    is a list `[{"Plan": {...}}]`; tolerate a bare `{"Plan": {...}}` or a bare Plan node too."""
    roots = []
    items = doc if isinstance(doc, list) else [doc]
    for item in items:
        if isinstance(item, dict) and isinstance(item.get("Plan"), dict):
            roots.append(item["Plan"])
        elif isinstance(item, dict) and "Node Type" in item:   # already a bare Plan node
            roots.append(item)
    return roots


def _children(node):
    """The nested child Plan nodes of a Plan node (the "Plans" list), or []."""
    kids = node.get("Plans")
    return kids if isinstance(kids, list) else []


def _node_label(node):
    """A short `Node Type on relation` label for a finding."""
    nt = node.get("Node Type", "?")
    rel = node.get("Relation Name")
    return "%s on %s" % (nt, rel) if rel else nt


def _walk_plan(node, finds):
    """Recursively walk a Plan node, appending (kind, label, why) findings. Each finding's third slot
    carries an `advisory` bool via a 4-tuple internally; the caller flattens to (kind, label, why)."""
    nt = node.get("Node Type", "")
    rel = node.get("Relation Name")
    plan_rows = node.get("Plan Rows")
    total_cost = node.get("Total Cost")
    has_filter = bool(node.get("Filter"))
    children = _children(node)

    # SEQ_SCAN — a Seq Scan WITH a Filter (an index may be missing for that predicate), or a Seq Scan
    # whose estimated Plan Rows is large. A small unfiltered Seq Scan is often optimal, so it does NOT
    # flag — only a filtered scan or a wide one. Advisory.
    if nt == "Seq Scan":
        if has_filter:
            finds.append(("SEQ_SCAN", _node_label(node),
                          "Seq Scan with a Filter (%s) — an index on the filtered column may be missing"
                          % _short(node.get("Filter")), True))
        elif isinstance(plan_rows, (int, float)) and plan_rows >= _PLAN_ROWS_SEQ_SCAN:
            finds.append(("SEQ_SCAN", _node_label(node),
                          "Seq Scan over ~%s estimated rows — a wide scan; confirm an index isn't expected"
                          % _num(plan_rows), True))

    # NESTED_LOOP_NO_INDEX — a Nested Loop whose INNER child (the second Plan, re-driven per outer row)
    # is a Seq Scan ⇒ O(n*m): the join probably lacks an index on the inner relation's join key. This
    # is the dominant B3 plan defect. Non-advisory (the one the exit code should react to).
    if nt == "Nested Loop" and len(children) >= 2:
        inner = children[1]                          # Postgres lists [outer, inner]
        if isinstance(inner, dict) and inner.get("Node Type") == "Seq Scan":
            finds.append(("NESTED_LOOP_NO_INDEX", _node_label(node),
                          "Nested Loop drives a Seq Scan on '%s' per outer row (O(n*m)) — the join "
                          "likely lacks an index on the inner relation's key"
                          % (inner.get("Relation Name") or "?"), False))

    # HIGH_COST_SORT — a Sort or Hash Aggregate over many rows (or with a high Total Cost) risks an
    # in-memory blow-up / external (on-disk) spill. Advisory.
    if nt in ("Sort", "Hash Aggregate"):
        big_rows = isinstance(plan_rows, (int, float)) and plan_rows >= _PLAN_ROWS_HIGH_SORT
        big_cost = isinstance(total_cost, (int, float)) and total_cost >= _PLAN_COST_HIGH_SORT
        if big_rows or big_cost:
            why = []
            if big_rows:
                why.append("~%s rows" % _num(plan_rows))
            if big_cost:
                why.append("cost %s" % _num(total_cost))
            finds.append(("HIGH_COST_SORT", _node_label(node),
                          "%s over %s — a large in-memory sort/agg; spill (work_mem) risk"
                          % (nt, " / ".join(why)), True))

    # ROW_ESTIMATE_BLOWUP — only when ANALYZE output is present (Actual Rows exists). A node whose
    # actual rows diverge from the planner's estimate by >100x is a stale-stats / bad-estimate smell
    # that misleads every join order above it. Non-advisory.
    actual = node.get("Actual Rows")
    if isinstance(actual, (int, float)) and isinstance(plan_rows, (int, float)):
        hi, lo = max(actual, plan_rows), min(actual, plan_rows)
        if lo >= 0 and (lo == 0 and hi >= _ROW_BLOWUP_FACTOR
                        or lo > 0 and hi / lo > _ROW_BLOWUP_FACTOR):
            finds.append(("ROW_ESTIMATE_BLOWUP", _node_label(node),
                          "Actual Rows %s vs Plan Rows %s differ by >%dx — stale stats / bad estimate; "
                          "ANALYZE the relation" % (_num(actual), _num(plan_rows), _ROW_BLOWUP_FACTOR),
                          False))

    for child in children:
        if isinstance(child, dict):
            _walk_plan(child, finds)


def _short(text, n=60):
    """Trim a Filter/Index-Cond string to a single short line for a finding."""
    s = " ".join(str(text).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def _num(x):
    """Render a Plan Rows / Cost number compactly (integers without a trailing .0)."""
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    return "{:,}".format(x) if isinstance(x, int) else str(x)


def analyze_plan(doc):
    """Yield (kind, label, why, advisory) findings for a parsed EXPLAIN (FORMAT JSON) `doc`. `doc` is
    the already-json.loads'd document (a list `[{"Plan": {...}}]` or a tolerated bare variant)."""
    finds = []
    for root in _plan_roots(doc):
        _walk_plan(root, finds)
    return finds


def lint_plan_file(path):
    """Read + parse an EXPLAIN (FORMAT JSON) file and return (findings, error). A malformed/empty file
    or a structurally-wrong document yields an empty findings list and a human-readable error string —
    never a crash. `error` is None on success."""
    try:
        raw = open(path, encoding="utf-8").read()
    except OSError as e:
        return [], "unreadable (%s)" % e
    return _lint_plan_text(raw)


def _lint_plan_text(raw):
    """Parse EXPLAIN-JSON `raw` text → (findings, error). Shared by the file path and the selftest."""
    if not raw.strip():
        return [], "empty input — expected an EXPLAIN (FORMAT JSON) document"
    try:
        doc = json.loads(raw)
    except (ValueError, TypeError) as e:
        return [], "not valid JSON (%s)" % e
    roots = _plan_roots(doc)
    if not roots:
        return [], ("no Plan node found — expected EXPLAIN (FORMAT JSON) output "
                    "(a list like [{\"Plan\": {...}}])")
    return analyze_plan(doc), None


def _run_plan(path):
    """The `plan` subcommand: lint one EXPLAIN (FORMAT JSON) file. Prints findings; returns the process
    exit code (1 if any NON-advisory plan smell, else 0 — advisory-only is exit 0 with warnings)."""
    finds, err = lint_plan_file(path)
    if err is not None:
        sys.stderr.write("sql-lint plan: %s: %s\n" % (path, err))
        return 2
    if not finds:
        print("sql-lint plan: OK — no plan smells in %s" % path)
        return 0
    blocking = 0
    for kind, label, why, advisory in finds:
        tag = "advisory" if advisory else "SMELL"
        if not advisory:
            blocking += 1
        print("  %-20s [%s]  %s — %s" % (kind, tag, label, why))
    print("sql-lint plan: %d finding(s) in %s (%d blocking, %d advisory) — confirm against the live "
          "plan / schema" % (len(finds), path, blocking, len(finds) - blocking))
    return 1 if blocking else 0


# --- machine-readable report (--json) ----------------------------------------------------------
# ONE shared schema across every lint bin: {tool, ok, summary, findings:[{kind, severity, location,
# message}]}. `ok` is true iff no blocking finding (the same condition that gives exit 0 in human mode).
# Printed via json.dumps(indent=2); nothing else goes to stdout under --json.
def _report_json(tool, ok, summary, findings):
    """Emit the shared report object to stdout (and nothing else). `findings` is a list of dicts already
    in {kind, severity, location, message} shape. Returns the dict so callers/selftests can reuse it."""
    report = {"tool": tool, "ok": ok, "summary": summary, "findings": findings}
    print(json.dumps(report, indent=2))
    return report


def build_sql_report(findings):
    """Build the JSON report for the SQL-SOURCE mode. `findings` is analyze_sql()'s (kind, line, detail)
    list. Every SQL-source smell is advisory-by-doctrine but exit-1-blocking, so each maps to severity
    `fail` and `ok` is true iff there are none — mirroring the human mode's exit (any smell ⇒ exit 1)."""
    out = []
    for kind, line, detail in findings:
        out.append({"kind": kind, "severity": "fail", "location": "line:%d" % line, "message": detail})
    ok = not out
    if ok:
        summary = "no SQL smells"
    else:
        summary = "%d SQL smell(s) — verify grain with COUNT(*) vs COUNT(DISTINCT key)" % len(out)
    return {"tool": "sql-lint", "ok": ok, "summary": summary, "findings": out}


def build_plan_report(findings):
    """Build the JSON report for the `plan` mode. `findings` is analyze_plan()'s (kind, label, why,
    advisory) list: a blocking smell → severity `fail`, an advisory one (SEQ_SCAN/HIGH_COST_SORT) →
    `advisory`. `ok` is true iff no BLOCKING smell — the exact exit-0 condition of `_run_plan`."""
    out, blocking = [], 0
    for kind, label, why, advisory in findings:
        if not advisory:
            blocking += 1
        out.append({"kind": kind, "severity": "advisory" if advisory else "fail",
                    "location": label, "message": why})
    ok = blocking == 0
    if not out:
        summary = "no plan smells"
    else:
        summary = ("%d plan finding(s) (%d blocking, %d advisory) — confirm against the live plan/schema"
                   % (len(out), blocking, len(out) - blocking))
    return {"tool": "sql-lint", "ok": ok, "summary": summary, "findings": out}


def _run_sql_json(path):
    """`--json` SQL-source mode: lint .sql files under `path`, emit ONE report object, exit as human mode
    (1 if any smell, else 0). Unreadable files are skipped (mirroring the human mode's per-file warn)."""
    files = []
    if os.path.isdir(path):
        for dp, _, fns in os.walk(path):
            files += [os.path.join(dp, fn) for fn in sorted(fns) if _is_sql_file(fn)]
    else:
        files = [path]
    findings = []
    for fp in files:
        try:
            src = open(fp, encoding="utf-8").read()
        except OSError:
            continue
        findings += analyze_sql(src)
    rep = build_sql_report(findings)
    _report_json(rep["tool"], rep["ok"], rep["summary"], rep["findings"])
    return 0 if rep["ok"] else 1


def _run_plan_json(path):
    """`--json` plan mode: lint one EXPLAIN (FORMAT JSON) file, emit ONE report object, exit as human
    mode (2 on a malformed/empty/no-Plan document, 1 on any blocking smell, else 0)."""
    finds, err = lint_plan_file(path)
    if err is not None:
        sys.stderr.write("sql-lint plan: %s: %s\n" % (path, err))
        return 2
    rep = build_plan_report(finds)
    _report_json(rep["tool"], rep["ok"], rep["summary"], rep["findings"])
    return 0 if rep["ok"] else 1


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


# --- plan-smell fixtures (EXPLAIN (FORMAT JSON)) -----------------------------------------------
# P1 (flag) — a Nested Loop whose inner child is a Seq Scan WITH a Filter ⇒ NESTED_LOOP_NO_INDEX
# (blocking) + SEQ_SCAN (advisory). The shape `EXPLAIN (FORMAT JSON)` emits: a list of one node.
PLAN_FLAG = """
[
  {
    "Plan": {
      "Node Type": "Nested Loop",
      "Total Cost": 24000.50,
      "Plan Rows": 5000,
      "Plans": [
        {
          "Node Type": "Seq Scan",
          "Relation Name": "orders",
          "Total Cost": 1800.00,
          "Plan Rows": 5000
        },
        {
          "Node Type": "Seq Scan",
          "Relation Name": "line_items",
          "Total Cost": 950.00,
          "Plan Rows": 200,
          "Filter": "(line_items.order_id = orders.id)"
        }
      ]
    }
  }
]
"""

# P2 (clean) — an Index Scan / Index Only Scan plan with no Seq Scan, no Nested-Loop-over-Seq-Scan,
# no large sort ⇒ NO findings.
PLAN_CLEAN = """
[
  {
    "Plan": {
      "Node Type": "Index Scan",
      "Relation Name": "orders",
      "Index Name": "orders_customer_id_idx",
      "Total Cost": 8.30,
      "Plan Rows": 12,
      "Index Cond": "(customer_id = 42)",
      "Plans": [
        {
          "Node Type": "Index Only Scan",
          "Relation Name": "customers",
          "Index Name": "customers_pkey",
          "Total Cost": 0.42,
          "Plan Rows": 1,
          "Index Cond": "(id = 42)"
        }
      ]
    }
  }
]
"""

# P3 (flag) — a Sort over many rows + (ANALYZE) a row-estimate blowup ⇒ HIGH_COST_SORT (advisory) +
# ROW_ESTIMATE_BLOWUP (blocking). Exercises the ANALYZE-only Actual Rows path.
PLAN_ANALYZE = """
[
  {
    "Plan": {
      "Node Type": "Sort",
      "Total Cost": 50000.00,
      "Plan Rows": 250000,
      "Actual Rows": 250000,
      "Plans": [
        {
          "Node Type": "Hash Join",
          "Plan Rows": 80,
          "Actual Rows": 90000,
          "Total Cost": 41000.00
        }
      ]
    }
  }
]
"""

# P4 (clean) — a small UNFILTERED Seq Scan must NOT flag (a small table scan is often optimal).
PLAN_SMALL_SEQ = """
[{ "Plan": { "Node Type": "Seq Scan", "Relation Name": "currencies", "Plan Rows": 42, "Total Cost": 1.42 } }]
"""

PLAN_MALFORMED = "{ this is not valid json "
PLAN_EMPTY = "   \n  "
PLAN_NO_PLAN = '{"foo": "bar"}'


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

    # --- plan-smell selftest (EXPLAIN FORMAT JSON) ---------------------------------------------
    def plan_kinds(raw):
        finds, err = _lint_plan_text(raw)
        if err is not None:
            return None
        return {k for k, _, _, _ in finds}

    def plan_blocking(raw):
        finds, err = _lint_plan_text(raw)
        if err is not None:
            return None
        return {k for k, _, _, adv in finds if not adv}

    # P1 — the flag fixture: a Seq Scan + Filter under a Nested Loop flags both detectors
    pk = plan_kinds(PLAN_FLAG)
    if pk is None or "NESTED_LOOP_NO_INDEX" not in pk:
        errs.append("missed NESTED_LOOP_NO_INDEX on a Nested Loop driving an inner Seq Scan")
    if pk is None or "SEQ_SCAN" not in pk:
        errs.append("missed SEQ_SCAN on a Seq Scan with a Filter under a Nested Loop")
    # ...and NESTED_LOOP_NO_INDEX is the blocking (non-advisory) one
    pb = plan_blocking(PLAN_FLAG)
    if pb is None or "NESTED_LOOP_NO_INDEX" not in pb:
        errs.append("NESTED_LOOP_NO_INDEX should be a blocking (non-advisory) plan smell")
    if pb and "SEQ_SCAN" in pb:
        errs.append("SEQ_SCAN should be advisory, not blocking")

    # P2 — the clean fixture: an Index Scan / Index Only Scan plan yields NO findings
    ck = plan_kinds(PLAN_CLEAN)
    if ck is None:
        errs.append("clean Index Scan plan failed to parse")
    elif ck:
        errs.append("false positive plan smell on a clean Index Scan / Index Only Scan plan: %s" % ck)

    # P3 — ANALYZE path: a large Sort + a >100x row-estimate blowup
    ak = plan_kinds(PLAN_ANALYZE)
    if ak is None or "HIGH_COST_SORT" not in ak:
        errs.append("missed HIGH_COST_SORT on a large Sort node")
    if ak is None or "ROW_ESTIMATE_BLOWUP" not in ak:
        errs.append("missed ROW_ESTIMATE_BLOWUP on a >100x Actual-vs-Plan-Rows divergence")

    # P4 — a small UNFILTERED Seq Scan must NOT flag (FP guard)
    sk = plan_kinds(PLAN_SMALL_SEQ)
    if sk is None:
        errs.append("small Seq Scan plan failed to parse")
    elif "SEQ_SCAN" in sk:
        errs.append("false positive SEQ_SCAN on a small unfiltered Seq Scan (42 rows, no filter)")

    # malformed / empty / no-Plan inputs ⇒ a clean error, never a crash or a finding
    for raw, label in ((PLAN_MALFORMED, "malformed JSON"), (PLAN_EMPTY, "empty input"),
                       (PLAN_NO_PLAN, "a doc with no Plan node")):
        finds, err = _lint_plan_text(raw)
        if err is None:
            errs.append("expected a clean error (not a crash/finding) on %s" % label)
        if finds:
            errs.append("expected no findings on %s, got %s" % (label, finds))

    # --- --json report selftest (the shared schema) -------------------------------------------
    import io
    import contextlib

    def _capture_report(report_obj):
        """Round-trip a report dict through _report_json's stdout path and json.loads it back, asserting
        nothing but the JSON object lands on stdout."""
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _report_json(report_obj["tool"], report_obj["ok"], report_obj["summary"],
                         report_obj["findings"])
        return json.loads(buf.getvalue())

    def _assert_report(rep, tool, want_ok, want_nonempty, label):
        if not isinstance(rep, dict):
            errs.append("--json %s: report is not a dict" % label); return
        if rep.get("tool") != tool:
            errs.append("--json %s: tool=%r, want %r" % (label, rep.get("tool"), tool))
        if rep.get("ok") is not want_ok:
            errs.append("--json %s: ok=%r, want %r" % (label, rep.get("ok"), want_ok))
        if not isinstance(rep.get("summary"), str) or not rep["summary"]:
            errs.append("--json %s: summary missing/empty" % label)
        f = rep.get("findings")
        if not isinstance(f, list):
            errs.append("--json %s: findings not a list" % label); return
        if want_nonempty and not f:
            errs.append("--json %s: findings should be non-empty" % label)
        if not want_nonempty and f:
            errs.append("--json %s: findings should be [] on clean input, got %s" % (label, f))
        for fd in f:
            if not isinstance(fd, dict) or any(k not in fd for k in ("kind", "severity", "location", "message")):
                errs.append("--json %s: a finding is missing a required key: %r" % (label, fd))
            elif fd["severity"] not in ("fail", "warn", "advisory"):
                errs.append("--json %s: bad severity %r" % (label, fd["severity"]))

    # SQL-source dirty fixture (SQL_STAR ⇒ SELECT_STAR) parses, tool right, ok false, findings non-empty
    dirty_sql_rep = _capture_report(build_sql_report(analyze_sql(SQL_STAR)))
    _assert_report(dirty_sql_rep, "sql-lint", False, True, "sql-source dirty")
    if not any(fd["kind"] == "SELECT_STAR" for fd in dirty_sql_rep["findings"]):
        errs.append("--json sql-source dirty: SELECT_STAR finding missing from report")
    if not all(fd["severity"] == "fail" for fd in dirty_sql_rep["findings"]):
        errs.append("--json sql-source: every SQL-source finding should be severity 'fail'")
    # SQL-source clean fixture ⇒ ok true, findings []
    _assert_report(_capture_report(build_sql_report(analyze_sql(SQL_CLEAN))), "sql-lint", True, False,
                   "sql-source clean")

    # plan dirty fixture (PLAN_FLAG ⇒ blocking NESTED_LOOP_NO_INDEX + advisory SEQ_SCAN): ok false,
    # both severities present
    pfinds, _ = _lint_plan_text(PLAN_FLAG)
    dirty_plan_rep = _capture_report(build_plan_report(pfinds))
    _assert_report(dirty_plan_rep, "sql-lint", False, True, "plan dirty")
    sevs = {fd["kind"]: fd["severity"] for fd in dirty_plan_rep["findings"]}
    if sevs.get("NESTED_LOOP_NO_INDEX") != "fail":
        errs.append("--json plan: NESTED_LOOP_NO_INDEX should map to severity 'fail', got %r"
                    % sevs.get("NESTED_LOOP_NO_INDEX"))
    if sevs.get("SEQ_SCAN") != "advisory":
        errs.append("--json plan: SEQ_SCAN should map to severity 'advisory', got %r" % sevs.get("SEQ_SCAN"))
    # plan clean fixture ⇒ ok true, findings []
    cfinds, _ = _lint_plan_text(PLAN_CLEAN)
    _assert_report(_capture_report(build_plan_report(cfinds)), "sql-lint", True, False, "plan clean")
    # an advisory-only plan (small filtered scan would be advisory) keeps ok TRUE: a plan whose only
    # smell is advisory does not block, so ok stays true even with a non-empty findings list.
    adv_only = build_plan_report([("SEQ_SCAN", "Seq Scan on t", "wide scan", True)])
    if not adv_only["ok"]:
        errs.append("--json plan: an advisory-only report should keep ok=true (advisory doesn't block)")

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
              "OUTER_JOIN_DEMOTED / NON_SARGABLE detectors verified; plan smells "
              "SEQ_SCAN / NESTED_LOOP_NO_INDEX / HIGH_COST_SORT / ROW_ESTIMATE_BLOWUP verified")
        return 0
    # --json is a parse-anywhere reporting flag — strip it out, remember it, leave everything else.
    as_json = "--json" in argv
    if as_json:
        argv = [a for a in argv if a != "--json"]
        if not argv:
            sys.stderr.write("usage: sql-lint.py [--json] <file|dir>  |  plan [--json] <explain.json>\n")
            return 2
    if argv[0] == "plan":
        if len(argv) < 2:
            sys.stderr.write("usage: sql-lint.py plan <explain.json>\n")
            return 2
        return _run_plan_json(argv[1]) if as_json else _run_plan(argv[1])
    if as_json:
        return _run_sql_json(argv[0])
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
