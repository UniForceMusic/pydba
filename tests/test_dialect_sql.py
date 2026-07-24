from __future__ import annotations

from pydba._query_with_params import QueryWithParams
from pydba.dialects._sql_dialect import SQLDialect
from pydba.query.enums.type import TypeEnum


def test_select_simple(sql_dialect: SQLDialect) -> None:
    qwp: QueryWithParams = sql_dialect.select(
        distinct=None,
        columns=["id", "name"],
        table="users",
        joins=None,
        where=None,
        group_by=None,
        having=None,
        order_by=None,
        limit=None,
        offset=None,
        unions=None,
    )
    assert qwp.query == 'SELECT "id", "name" FROM "users"'


def test_select_star(sql_dialect: SQLDialect) -> None:
    qwp: QueryWithParams = sql_dialect.select(
        distinct=None,
        columns=None,
        table="users",
        joins=None,
        where=None,
        group_by=None,
        having=None,
        order_by=None,
        limit=None,
        offset=None,
        unions=None,
    )
    assert qwp.query == "SELECT * FROM \"users\""


def test_select_distinct(sql_dialect: SQLDialect) -> None:
    qwp: QueryWithParams = sql_dialect.select(
        distinct=[],
        columns=["name"],
        table="users",
        joins=None,
        where=None,
        group_by=None,
        having=None,
        order_by=None,
        limit=None,
        offset=None,
        unions=None,
    )
    assert "DISTINCT" in qwp.query


def test_select_with_where(sql_dialect: SQLDialect) -> None:
    from pydba.query._condition import Condition
    from pydba.query.enums.condition import ConditionEnum

    where: list[Condition] = [
        Condition(condition=ConditionEnum.EQUALS, identifier="id", value=1),
    ]
    qwp: QueryWithParams = sql_dialect.select(
        distinct=None,
        columns=None,
        table="users",
        joins=None,
        where=where,
        group_by=None,
        having=None,
        order_by=None,
        limit=None,
        offset=None,
        unions=None,
    )
    assert "WHERE" in qwp.query
    assert "?" in qwp.query
    assert 1 in qwp.params


def test_select_with_limit_offset(sql_dialect: SQLDialect) -> None:
    qwp: QueryWithParams = sql_dialect.select(
        distinct=None,
        columns=None,
        table="users",
        joins=None,
        where=None,
        group_by=None,
        having=None,
        order_by=None,
        limit=10,
        offset=20,
        unions=None,
    )
    assert "LIMIT 10" in qwp.query
    assert "OFFSET 20" in qwp.query


def test_select_with_order_by(sql_dialect: SQLDialect) -> None:
    from pydba.query._order_by import OrderBy
    from pydba.query.enums.order_by_dir import OrderByDirectionEnum

    ob: list[OrderBy] = [OrderBy(column="name", direction=OrderByDirectionEnum.ASC)]
    qwp: QueryWithParams = sql_dialect.select(
        distinct=None,
        columns=None,
        table="users",
        joins=None,
        where=None,
        group_by=None,
        having=None,
        order_by=ob,
        limit=None,
        offset=None,
        unions=None,
    )
    assert 'ORDER BY "name" ASC' in qwp.query


def test_insert_simple(sql_dialect: SQLDialect) -> None:
    qwp: QueryWithParams = sql_dialect.insert(
        table="users",
        values=[{"name": "John", "age": 30}],
        on_conflict=None,
        returning=None,
        last_insert_id=None,
    )
    assert "INSERT INTO" in qwp.query
    assert '"name"' in qwp.query
    assert '"age"' in qwp.query


def test_insert_multiple_rows(sql_dialect: SQLDialect) -> None:
    qwp: QueryWithParams = sql_dialect.insert(
        table="users",
        values=[{"name": "John"}, {"name": "Jane"}],
        on_conflict=None,
        returning=None,
        last_insert_id=None,
    )
    assert qwp.query.count("VALUES") == 1
    assert qwp.query.count("(") >= 3  # Two row sets with parens


def test_update_simple(sql_dialect: SQLDialect) -> None:
    qwp: QueryWithParams = sql_dialect.update(
        table="users",
        updates={"name": "John"},
        where=None,
        returning=None,
    )
    assert "UPDATE" in qwp.query
    assert "SET" in qwp.query
    assert '"name"' in qwp.query


def test_update_with_where(sql_dialect: SQLDialect) -> None:
    from pydba.query._condition import Condition
    from pydba.query.enums.condition import ConditionEnum

    where: list[Condition] = [Condition(condition=ConditionEnum.EQUALS, identifier="id", value=1)]
    qwp: QueryWithParams = sql_dialect.update(
        table="users",
        updates={"name": "Jane"},
        where=where,
        returning=None,
    )
    assert "WHERE" in qwp.query


def test_delete_simple(sql_dialect: SQLDialect) -> None:
    qwp: QueryWithParams = sql_dialect.delete(
        table="users",
        where=None,
        returning=None,
    )
    assert qwp.query == 'DELETE FROM "users"'


def test_delete_with_where(sql_dialect: SQLDialect) -> None:
    from pydba.query._condition import Condition
    from pydba.query.enums.condition import ConditionEnum

    where: list[Condition] = [Condition(condition=ConditionEnum.EQUALS, identifier="id", value=5)]
    qwp: QueryWithParams = sql_dialect.delete(
        table="users",
        where=where,
        returning=None,
    )
    assert "WHERE" in qwp.query
    assert "?" in qwp.query


def test_create_table(sql_dialect: SQLDialect) -> None:
    qwp: QueryWithParams = sql_dialect.create_table(
        if_not_exists=False,
        table="users",
        columns=[
            {"name": "id", "type": TypeEnum.INT, "auto_increment": True, "not_null": True},
            {"name": "name", "type": TypeEnum.STRING, "not_null": True},
        ],
        primary_keys=["id"],
        constraints=None,
    )
    assert "CREATE TABLE" in qwp.query
    assert '"users"' in qwp.query
    assert '"id"' in qwp.query
    assert '"name"' in qwp.query
    assert "PRIMARY KEY" in qwp.query


def test_drop_table(sql_dialect: SQLDialect) -> None:
    qwp: QueryWithParams = sql_dialect.drop_table(if_exists=False, table="users")
    assert qwp.query == 'DROP TABLE "users"'


def test_drop_table_if_exists(sql_dialect: SQLDialect) -> None:
    qwp: QueryWithParams = sql_dialect.drop_table(if_exists=True, table="users")
    assert qwp.query == 'DROP TABLE IF EXISTS "users"'


def test_transaction_queries(sql_dialect: SQLDialect) -> None:
    assert sql_dialect.begin_transaction().query == "BEGIN TRANSACTION"
    assert sql_dialect.commit_transaction().query == "COMMIT TRANSACTION"
    assert sql_dialect.rollback_transaction().query == "ROLLBACK TRANSACTION"


def test_savepoint_queries(sql_dialect: SQLDialect) -> None:
    sp = sql_dialect.begin_savepoint("sp1")
    assert "SAVEPOINT" in sp.query
    assert '"sp1"' in sp.query

    rsp = sql_dialect.commit_savepoint("sp1")
    assert "RELEASE SAVEPOINT" in rsp.query

    rbsp = sql_dialect.rollback_savepoint("sp1")
    assert "ROLLBACK TO SAVEPOINT" in rbsp.query


def test_escape_identifier(sql_dialect: SQLDialect) -> None:
    assert sql_dialect.escape_identifier("col") == '"col"'


def test_escape_identifier_list(sql_dialect: SQLDialect) -> None:
    assert sql_dialect.escape_identifier(["schema", "table"]) == '"schema"."table"'


def test_type_mapping(sql_dialect: SQLDialect) -> None:
    assert "INTEGER" in sql_dialect.type(TypeEnum.INT)
    assert "VARCHAR" in sql_dialect.type(TypeEnum.STRING)
    assert sql_dialect.type(TypeEnum.STRING, 50) == "VARCHAR(50)"


def test_cast_to_query(sql_dialect: SQLDialect) -> None:
    assert sql_dialect.cast_to_query(None) == "NULL"
    assert sql_dialect.cast_to_query(True) == "TRUE"
    assert sql_dialect.cast_to_query(42) == "42"
    assert sql_dialect.cast_to_query("hello") == "'hello'"
    assert sql_dialect.cast_to_query(3.14) == "3.14"
