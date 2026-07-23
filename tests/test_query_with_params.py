from __future__ import annotations

from pydba._query_with_params import QueryWithParams
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


def test_named_params_skips_string_literals() -> None:
    qwp: QueryWithParams = QueryWithParams(
        query="SELECT * FROM t WHERE col = :val AND name = ':not_a_param'",
        params=[1],
    )
    result: QueryWithParams = qwp.named_params_to_question_marks()
    assert result.query == "SELECT * FROM t WHERE col = ? AND name = ':not_a_param'"


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


def test_to_sql_respects_string_literals() -> None:
    dialect: SQLDialect = SQLDialect()
    qwp: QueryWithParams = QueryWithParams(query="SELECT '?', ?", params=[42])
    sql: str = qwp.to_sql(dialect)
    assert "'?'" in sql
    assert "42" in sql
