from __future__ import annotations

from pydba._query_with_params import REGEX_PATTERN, QueryWithParams
from pydba.dialects._sql_dialect import SQLDialect


def test_query_with_params_creation() -> None:
    qwp: QueryWithParams = QueryWithParams(query="SELECT * FROM t WHERE col = ?", params=[1])
    assert qwp.query == "SELECT * FROM t WHERE col = ?"
    assert qwp.params == [1]


def test_named_params_to_question_marks() -> None:
    qwp: QueryWithParams = QueryWithParams(query="SELECT * FROM t WHERE col = :val", params=[1])
    result: QueryWithParams = qwp.named_params_to_question_marks()
    assert result.query == "SELECT * FROM t WHERE col = ?"
    assert result.params == [1]


def test_named_params_skips_single_quoted_strings() -> None:
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t WHERE col = :val AND name = ':not_a_param'",
        params=[1],
    )
    result: QueryWithParams = qwp.named_params_to_question_marks()
    assert result.query == "SELECT * FROM t WHERE col = ? AND name = ':not_a_param'"


def test_named_params_skips_double_quoted_strings() -> None:
    qwp: QueryWithParams = QueryWithParams(
        query='SELECT * FROM t WHERE col = :val AND name = ":not_a_param"',
        params=[1],
    )
    result: QueryWithParams = qwp.named_params_to_question_marks()
    assert result.query == 'SELECT * FROM t WHERE col = ? AND name = ":not_a_param"'


def test_named_params_skips_backtick_quoted_strings() -> None:
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t WHERE col = :val AND name = `:not_a_param`",
        params=[1],
    )
    result: QueryWithParams = qwp.named_params_to_question_marks()
    assert result.query == "SELECT * FROM t WHERE col = ? AND name = `:not_a_param`"


def test_named_params_multiple() -> None:
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t WHERE col1 = :val1 AND col2 = :val2",
        params=[1, 2],
    )
    result: QueryWithParams = qwp.named_params_to_question_marks()
    assert result.query == "SELECT * FROM t WHERE col1 = ? AND col2 = ?"


def test_named_params_skips_line_comments() -> None:
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t -- :not_a_param\nWHERE col = :val",
        params=[1],
    )
    result: QueryWithParams = qwp.named_params_to_question_marks()
    assert result.query == "SELECT * FROM t -- :not_a_param\nWHERE col = ?"


def test_named_params_skips_block_comments() -> None:
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t /* :not_a_param */ WHERE col = :val",
        params=[1],
    )
    result: QueryWithParams = qwp.named_params_to_question_marks()
    assert result.query == "SELECT * FROM t /* :not_a_param */ WHERE col = ?"


def test_named_params_skips_hash_comments() -> None:
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t # :not_a_param\nWHERE col = :val",
        params=[1],
    )
    result: QueryWithParams = qwp.named_params_to_question_marks()
    assert result.query == "SELECT * FROM t # :not_a_param\nWHERE col = ?"


def test_named_params_skips_postgres_cast() -> None:
    """::cast syntax should not match as :named parameter."""
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t WHERE col = :val AND col2::text = 'hello'",
        params=[1],
    )
    result: QueryWithParams = qwp.named_params_to_question_marks()
    assert result.query == "SELECT * FROM t WHERE col = ? AND col2::text = 'hello'"


def test_named_params_skips_question_marks() -> None:
    """? should remain as-is in named_params_to_question_marks."""
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t WHERE col = :val AND col2 = ?",
        params=[1, 2],
    )
    result: QueryWithParams = qwp.named_params_to_question_marks()
    assert result.query == "SELECT * FROM t WHERE col = ? AND col2 = ?"


def test_to_sql_with_dialect() -> None:
    dialect: SQLDialect = SQLDialect()
    qwp: QueryWithParams = QueryWithParams(query="SELECT * FROM t WHERE col = ? AND col2 = ?", params=[1, "hello"])
    sql: str = qwp.to_sql(dialect)
    assert "1" in sql
    assert "'hello'" in sql


def test_to_sql_interpolates_values() -> None:
    dialect: SQLDialect = SQLDialect()
    qwp: QueryWithParams = QueryWithParams(query="SELECT * FROM t WHERE col = ?", params=[None])
    sql: str = qwp.to_sql(dialect)
    assert "NULL" in sql


def test_to_sql_respects_single_quoted_string_literals() -> None:
    dialect: SQLDialect = SQLDialect()
    qwp: QueryWithParams = QueryWithParams(query="SELECT '?', ?", params=[42])
    sql: str = qwp.to_sql(dialect)
    assert "'?'" in sql
    assert "42" in sql


def test_to_sql_respects_double_quoted_string_literals() -> None:
    dialect: SQLDialect = SQLDialect()
    qwp: QueryWithParams = QueryWithParams(query='SELECT "?", ?', params=[42])
    sql: str = qwp.to_sql(dialect)
    assert '"?"' in sql
    assert "42" in sql


def test_to_sql_respects_backtick_quoted_string_literals() -> None:
    dialect: SQLDialect = SQLDialect()
    qwp: QueryWithParams = QueryWithParams(query="SELECT `?`, ?", params=[42])
    sql: str = qwp.to_sql(dialect)
    assert "`?`" in sql
    assert "42" in sql


def test_to_sql_respects_line_comments() -> None:
    dialect: SQLDialect = SQLDialect()
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t -- comment\nWHERE col = ?",
        params=[42],
    )
    sql: str = qwp.to_sql(dialect)
    assert "42" in sql


def test_to_sql_respects_block_comments() -> None:
    dialect: SQLDialect = SQLDialect()
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t /* comment */ WHERE col = ?",
        params=[42],
    )
    sql: str = qwp.to_sql(dialect)
    assert "42" in sql


def test_to_sql_respects_named_params() -> None:
    """Named params should remain as-is in to_sql (they are not ? placeholders)."""
    dialect: SQLDialect = SQLDialect()
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t WHERE col = :val AND col2 = ?",
        params=[42],
    )
    sql: str = qwp.to_sql(dialect)
    assert ":val" in sql
    assert "42" in sql


def test_regex_pattern_module_level() -> None:
    """REGEX_PATTERN is a compiled regex accessible at module level."""
    import re
    assert isinstance(REGEX_PATTERN, re.Pattern)
