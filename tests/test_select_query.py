from __future__ import annotations

import pytest
from pydba.query.select import SelectQuery
from pydba.query._query import raw
from pydba.dialects._sql_dialect import SQLDialect


def test_select_query_creation(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.columns(["id", "name"])
    qwp = q.to_query_with_params()
    assert qwp.query == 'SELECT "id", "name" FROM "users"'


def test_select_with_where(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.columns(["id", "name"])
    q.where_equals("id", 1)
    qwp = q.to_query_with_params()
    assert "WHERE" in qwp.query
    assert qwp.params == [1]


def test_select_with_multiple_conditions(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.where_equals("name", "John")
    q.or_where_equals("name", "Jane")
    qwp = q.to_query_with_params()
    assert "OR" in qwp.query or "AND" in qwp.query


def test_select_with_limit(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.limit(10)
    qwp = q.to_query_with_params()
    assert "LIMIT 10" in qwp.query


def test_select_with_offset(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.limit(10)
    q.offset(20)
    qwp = q.to_query_with_params()
    assert "LIMIT 10" in qwp.query
    assert "OFFSET 20" in qwp.query


def test_select_with_order_by(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.order_by_asc("name")
    qwp = q.to_query_with_params()
    assert "ORDER BY" in qwp.query
    assert "ASC" in qwp.query


def test_select_with_order_by_desc(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.order_by_desc("name")
    qwp = q.to_query_with_params()
    assert "DESC" in qwp.query


def test_select_where_between(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.where_between("age", 18, 65)
    qwp = q.to_query_with_params()
    assert "BETWEEN" in qwp.query


def test_select_where_in(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.where_in("id", [1, 2, 3])
    qwp = q.to_query_with_params()
    assert "IN" in qwp.query


def test_select_where_like(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.where_like("name", "%john%")
    qwp = q.to_query_with_params()
    assert "LIKE" in qwp.query


def test_select_where_is_null(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.where_is_null("deleted_at")
    qwp = q.to_query_with_params()
    assert "IS NULL" in qwp.query


def test_select_to_sql(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.columns(["id"])
    q.where_equals("id", 1)
    sql = q.to_sql()
    assert '"id"' in sql
    assert '"users"' in sql


def test_select_where_group(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    q.where_group(lambda g: g.where_equals("name", "John").or_where_equals("name", "Jane"))
    qwp = q.to_query_with_params()
    assert "(" in qwp.query
    assert ")" in qwp.query


def test_select_join(sql_dialect):
    q = SelectQuery(sql_dialect, "users")
    j = q.left_join("posts")
    j.on(raw("users.id = posts.user_id"))
    qwp = q.to_query_with_params()
    assert "LEFT JOIN" in qwp.query
