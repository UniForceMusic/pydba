from __future__ import annotations

import pytest
from pydba.query.update import UpdateQuery
from pydba.dialects._sql_dialect import SQLDialect


def test_update_simple(sql_dialect: SQLDialect) -> None:
    q: UpdateQuery = UpdateQuery(sql_dialect, "users")
    q.updates({"name": "John"})
    qwp = q.to_query_with_params()
    assert "UPDATE" in qwp.query
    assert "SET" in qwp.query
    assert '"name"' in qwp.query


def test_update_with_where(sql_dialect: SQLDialect) -> None:
    q: UpdateQuery = UpdateQuery(sql_dialect, "users")
    q.updates({"name": "Jane"})
    q.where_equals("id", 1)
    qwp = q.to_query_with_params()
    assert "WHERE" in qwp.query
    assert "Jane" in qwp.params
    assert 1 in qwp.params
