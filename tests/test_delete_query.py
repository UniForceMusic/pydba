from __future__ import annotations

import pytest
from pydba.query.delete import DeleteQuery
from pydba.dialects._sql_dialect import SQLDialect


def test_delete_simple(sql_dialect: SQLDialect) -> None:
    q = DeleteQuery(sql_dialect, "users")
    qwp = q.to_query_with_params()
    assert qwp.query == 'DELETE FROM "users"'


def test_delete_with_where(sql_dialect: SQLDialect) -> None:
    q = DeleteQuery(sql_dialect, "users")
    q.where_equals("id", 5)
    qwp = q.to_query_with_params()
    assert "WHERE" in qwp.query
    assert qwp.params == [5]
