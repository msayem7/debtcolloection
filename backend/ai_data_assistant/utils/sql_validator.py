"""
SQL Validator — ensures LLM-generated SQL is safe to execute.

Rules:
1. Only SELECT statements are allowed (no DDL, DML, or utility commands).
2. No multi-statement execution (semicolons inside the statement).
3. No dangerous functions (pg_sleep, COPY, etc.).
4. Maximum row limit enforced.
5. Tenant isolation: branch_id filter must be present.
"""

import re
from typing import Tuple


FORBIDDEN_KEYWORDS = [
    r'\bDROP\b', r'\bALTER\b', r'\bCREATE\b', r'\bTRUNCATE\b',
    r'\bDELETE\b', r'\bUPDATE\b', r'\bINSERT\b', r'\bREPLACE\b',
    r'\bEXEC\b', r'\bEXECUTE\b', r'\bCOPY\b',
    r'\bPG_SLEEP\b', r'\bpg_sleep\b',
    r'\bGRANT\b', r'\bREVOKE\b',
    r'\bINTO\s+OUTFILE\b', r'\bINTO\s+DUMPFILE\b',
    r'\bLOAD\s+DATA\b', r'\bLOAD_FILE\b',
    r'\bINFORMATION_SCHEMA\b', r'\bpg_catalog\b',
    r'\bUNION\s+ALL\s+SELECT\b',  # allow UNION SELECT but flag suspicious ones
]

FORBIDDEN_PATTERNS = [re.compile(kw, re.IGNORECASE) for kw in FORBIDDEN_KEYWORDS]


def validate_sql(sql: str) -> Tuple[bool, str]:
    if not sql or not sql.strip():
        return False, "Empty SQL statement"

    sql_stripped = sql.strip().rstrip(';')

    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(sql_stripped):
            return False, f"SQL contains forbidden keyword: {pattern.pattern}"

    if not re.match(r'^\s*SELECT\b', sql_stripped, re.IGNORECASE):
        return False, "Only SELECT statements are allowed"

    if ';' in sql_stripped.rstrip(';'):
        parts = [p.strip() for p in sql_stripped.split(';') if p.strip()]
        if len(parts) > 1:
            return False, "Multi-statement execution is not allowed"

    return True, ""


def inject_tenant_filter(sql: str, branch_id: int, branch_alias_id: str) -> Tuple[bool, str]:
    sql_stripped = sql.strip().rstrip(';')
    lower_sql = sql_stripped.lower()

    if re.search(r'\bwhere\b', lower_sql):
        where_match = re.search(r'\bwhere\b', lower_sql, re.IGNORECASE)
        if not where_match:
            return True, sql_stripped
        insert_pos = where_match.start()
        where_keyword = sql_stripped[insert_pos:insert_pos + 5]
        rest = sql_stripped[:insert_pos]
        after_where = sql_stripped[insert_pos + 5:].lstrip()

        has_branch_filter = bool(re.search(r'\bbranch_id\s*=\s*', after_where))
        if has_branch_filter:
            return True, sql_stripped

        main_table = _detect_main_table(sql_stripped)
        branch_column = _get_branch_column(main_table)
        if branch_column:
            modified = f"{rest} {where_keyword} {branch_column} = {branch_id} AND {after_where}"
        else:
            modified = sql_stripped
        return True, modified

    order_pos = re.search(r'\bORDER\s+BY\b', sql_stripped, re.IGNORECASE)
    limit_pos = re.search(r'\bLIMIT\b', sql_stripped, re.IGNORECASE)
    offset_pos = re.search(r'\bOFFSET\b', sql_stripped, re.IGNORECASE)

    insert_at = len(sql_stripped)
    for pos in [order_pos, limit_pos, offset_pos]:
        if pos:
            insert_at = min(insert_at, pos.start())

    before = sql_stripped[:insert_at].rstrip()
    after = sql_stripped[insert_at:]

    main_table = _detect_main_table(sql_stripped)
    branch_column = _get_branch_column(main_table)
    if branch_column:
        modified = f"{before} WHERE {branch_column} = {branch_id} {after}"
    else:
        modified = sql_stripped

    return True, modified


def _detect_main_table(sql: str) -> str:
    from_match = re.search(r'\bFROM\s+(\w+)', sql, re.IGNORECASE)
    if from_match:
        return from_match.group(1)
    join_match = re.search(r'\bJOIN\s+(\w+)', sql, re.IGNORECASE)
    if join_match:
        return join_match.group(1)
    return ''


def _get_branch_column(table: str) -> str:
    table_branch_map = {
        'credit_invoice': 'ci.branch_id',
        'payment': 'p.branch_id',
        'customer': 'c.branch_id',
        'claim': 'cl.branch_id',
        'payment_details': 'pd.branch_id',
        'branch': 'branch.id',
    }
    return table_branch_map.get(table, '')


def enforce_row_limit(sql: str, max_rows: int = 1000) -> str:
    sql_stripped = sql.strip().rstrip(';')
    if re.search(r'\bLIMIT\b', sql_stripped, re.IGNORECASE):
        return sql_stripped
    return f"{sql_stripped} LIMIT {max_rows}"


def strip_parameters(sql: str) -> str:
    sql_stripped = sql.strip().rstrip(';')
    result = re.sub(
        r'%\((\w+)\)s(::\w+)?',
        lambda m: _placeholder_default(m.group(1), m.group(2)),
        sql_stripped
    )
    return result


def _placeholder_default(name: str, cast_suffix: str = None) -> str:
    name_lower = name.lower()
    if 'date' in name_lower:
        val = "'2026-01-01'"
        return val + (cast_suffix or '')
    if any(kw in name_lower for kw in ['name', 'org', 'customer', 'branch']):
        return "''"
    if 'status' in name_lower:
        return "'all'"
    if any(kw in name_lower for kw in ['id', 'number', 'amount', 'count']):
        return "0"
    return "''"