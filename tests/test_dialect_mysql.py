from __future__ import annotations

import pytest

from pydba._query_with_params import QueryWithParams
from pydba.dialects.mysql import MySQLDialect
from pydba.exceptions import QueryError
from pydba.query._condition import Condition
from pydba.query._on_conflict import OnConflict
from pydba.query.enums.condition import ConditionEnum
from pydba.query.enums.type import TypeEnum


def test_mysql_select(mysql_dialect: MySQLDialect) -> None:
    qwp: QueryWithParams = mysql_dialect.select(
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
    assert qwp.query == "SELECT `id`, `name` FROM `users`"


def test_mysql_placeholder(mysql_dialect: MySQLDialect) -> None:
    """Verify MySQL uses ? placeholders, not %s."""
    qwp: QueryWithParams = mysql_dialect.insert(
        table="users",
        values=[{"id": 1, "name": "Alice"}],
        on_conflict=None,
        returning=None,
        last_insert_id=None,
    )
    assert "?" in qwp.query
    assert "%s" not in qwp.query
    assert qwp.params == [1, "Alice"]


def test_mysql_on_duplicate_key_update(mysql_dialect: MySQLDialect) -> None:
    """Verify ON DUPLICATE KEY UPDATE with VALUES(col)."""
    updates = {"name": "VALUES"}
    qwp: QueryWithParams = mysql_dialect.insert(
        table="users",
        values=[{"id": 1, "name": "John"}],
        on_conflict=OnConflict(conflict="id", updates=updates),
        returning=None,
        last_insert_id=None,
    )
    assert "ON DUPLICATE KEY UPDATE" in qwp.query
    assert "VALUES(`name`)" in qwp.query


def test_mysql_on_duplicate_key_update_all(mysql_dialect: MySQLDialect) -> None:
    """Empty updates dict = update all columns from VALUES."""
    qwp: QueryWithParams = mysql_dialect.insert(
        table="users",
        values=[{"id": 1, "name": "John", "email": "john@example.com"}],
        on_conflict=OnConflict(conflict="id", updates={}),
        returning=None,
        last_insert_id=None,
    )
    assert "ON DUPLICATE KEY UPDATE" in qwp.query
    assert "VALUES(`id`)" in qwp.query
    assert "VALUES(`name`)" in qwp.query
    assert "VALUES(`email`)" in qwp.query


def test_mysql_on_duplicate_key_update_specific(mysql_dialect: MySQLDialect) -> None:
    """Specific column updates with literal values."""
    updates = {"name": "UpdatedName", "count": 42}
    qwp: QueryWithParams = mysql_dialect.insert(
        table="users",
        values=[{"id": 1, "name": "John", "count": 0}],
        on_conflict=OnConflict(conflict="id", updates=updates),
        returning=None,
        last_insert_id=None,
    )
    assert "ON DUPLICATE KEY UPDATE" in qwp.query
    assert "`name` = ?" in qwp.query
    assert "`count` = ?" in qwp.query
    assert qwp.params == [1, "John", 0, "UpdatedName", 42]


def test_mysql_on_duplicate_key_update_do_nothing_raises(
    mysql_dialect: MySQLDialect,
) -> None:
    """None updates should raise QueryError — MySQL has no DO NOTHING."""
    with pytest.raises(QueryError, match="DO NOTHING"):
        mysql_dialect.insert(
            table="users",
            values=[{"id": 1, "name": "John"}],
            on_conflict=OnConflict(conflict="id", updates=None),
            returning=None,
            last_insert_id=None,
        )


def test_mysql_no_returning(mysql_dialect: MySQLDialect) -> None:
    """RETURNING clause should raise QueryError."""
    with pytest.raises(QueryError, match="RETURNING"):
        mysql_dialect.insert(
            table="users",
            values=[{"name": "John"}],
            on_conflict=None,
            returning=["id"],
            last_insert_id=None,
        )


def test_mysql_type_mapping(mysql_dialect: MySQLDialect) -> None:
    assert mysql_dialect.type(TypeEnum.BOOL) == "TINYINT(1)"
    assert mysql_dialect.type(TypeEnum.INT) == "INT"
    assert mysql_dialect.type(TypeEnum.FLOAT) == "FLOAT"
    assert mysql_dialect.type(TypeEnum.FLOAT, 64) == "DOUBLE"
    assert mysql_dialect.type(TypeEnum.STRING) == "VARCHAR(255)"
    assert mysql_dialect.type(TypeEnum.STRING, 64) == "VARCHAR(64)"
    assert mysql_dialect.type(TypeEnum.DATETIME) == "DATETIME"


def test_mysql_bool_casting(mysql_dialect: MySQLDialect) -> None:
    assert mysql_dialect.cast_bool(True) == 1
    assert mysql_dialect.cast_bool(False) == 0
    assert mysql_dialect.parse_bool(True) is True
    assert mysql_dialect.parse_bool(False) is False
    assert mysql_dialect.parse_bool(1) is True
    assert mysql_dialect.parse_bool(0) is False
    assert mysql_dialect.parse_bool("true") is True
    assert mysql_dialect.parse_bool("false") is False
    assert mysql_dialect.parse_bool("1") is True
    assert mysql_dialect.parse_bool("yes") is True
    assert mysql_dialect.parse_bool("on") is True


def test_mysql_auto_increment_column(mysql_dialect: MySQLDialect) -> None:
    col: dict[str, object] = {
        "name": "id",
        "type": TypeEnum.INT,
        "auto_increment": True,
    }
    col_def: str = mysql_dialect._build_column(col)
    assert "AUTO_INCREMENT" in col_def
    assert "PRIMARY KEY" in col_def


def test_mysql_regex_condition(mysql_dialect: MySQLDialect) -> None:
    cond = Condition(
        condition=ConditionEnum.REGEX,
        identifier="email",
        value="^[a-z]+@example\\.com$",
    )
    parts: list[str] = []
    params: list[object] = []
    mysql_dialect._build_condition(parts, params, cond)
    result = "".join(parts)
    assert "REGEXP" in result
    assert "`email`" in result


def test_mysql_not_regex_condition(mysql_dialect: MySQLDialect) -> None:
    cond = Condition(
        condition=ConditionEnum.NOT_REGEX,
        identifier="email",
        value="^spam@",
    )
    parts: list[str] = []
    params: list[object] = []
    mysql_dialect._build_condition(parts, params, cond)
    result = "".join(parts)
    assert "NOT REGEXP" in result


def test_mysql_no_distinct_on(mysql_dialect: MySQLDialect) -> None:
    assert not mysql_dialect.distinct_on


def test_mysql_escape_identifier(mysql_dialect: MySQLDialect) -> None:
    assert mysql_dialect.escape_identifier("users") == "`users`"
    assert mysql_dialect.escape_identifier("order") == "`order`"
    assert mysql_dialect.escape_identifier("select") == "`select`"


def test_mysql_escape_string(mysql_dialect: MySQLDialect) -> None:
    assert mysql_dialect.escape_string("it's") == "it''s"
    assert mysql_dialect.escape_string("back\\slash") == "back\\\\slash"
    assert mysql_dialect.escape_string("normal") == "normal"


def test_mysql_transaction_syntax(mysql_dialect: MySQLDialect) -> None:
    assert mysql_dialect.begin_transaction().query == "START TRANSACTION"
    assert mysql_dialect.commit_transaction().query == "COMMIT"
    assert mysql_dialect.rollback_transaction().query == "ROLLBACK"


def test_mysql_create_table(mysql_dialect: MySQLDialect) -> None:
    qwp: QueryWithParams = mysql_dialect.create_table(
        if_not_exists=True,
        table="users",
        columns=[
            {"name": "id", "type": TypeEnum.INT, "auto_increment": True},
            {"name": "name", "type": TypeEnum.STRING, "bits": 100, "not_null": True},
            {"name": "email", "type": TypeEnum.STRING, "bits": 255},
        ],
    )
    query = qwp.query
    assert "CREATE TABLE IF NOT EXISTS" in query
    assert "`users`" in query
    assert "`id`" in query
    assert "AUTO_INCREMENT" in query
    assert "PRIMARY KEY" in query
    assert "`name`" in query
    assert "VARCHAR(100)" in query
    assert "NOT NULL" in query
    assert "`email`" in query
    assert "VARCHAR(255)" in query


def test_mysql_alter_add_column(mysql_dialect: MySQLDialect) -> None:
    qwp: QueryWithParams = mysql_dialect._build_alter(
        "users",
        {
            "type": "add_column",
            "column": {"name": "age", "type": TypeEnum.INT, "not_null": True},
        },
    )
    assert qwp.query == "ALTER TABLE `users` ADD COLUMN `age` INT NOT NULL"


def test_mysql_alter_rename_column(mysql_dialect: MySQLDialect) -> None:
    qwp: QueryWithParams = mysql_dialect._build_alter(
        "users",
        {"type": "rename_column", "old_name": "name", "new_name": "username"},
    )
    assert qwp.query == "ALTER TABLE `users` RENAME COLUMN `name` TO `username`"


def test_mysql_alter_drop_primary_key(mysql_dialect: MySQLDialect) -> None:
    qwp: QueryWithParams = mysql_dialect._build_alter(
        "users",
        {"type": "drop_constraint", "constraint_type": "primary_key"},
    )
    assert qwp.query == "ALTER TABLE `users` DROP PRIMARY KEY"


def test_mysql_alter_drop_foreign_key(mysql_dialect: MySQLDialect) -> None:
    qwp: QueryWithParams = mysql_dialect._build_alter(
        "orders",
        {
            "type": "drop_constraint",
            "constraint_type": "foreign_key",
            "name": "fk_user_id",
        },
    )
    assert qwp.query == "ALTER TABLE `orders` DROP FOREIGN KEY `fk_user_id`"


def test_mysql_insert_with_params(mysql_dialect: MySQLDialect) -> None:
    """Verify INSERT generates ? placeholders and correct params."""
    qwp: QueryWithParams = mysql_dialect.insert(
        table="users",
        values=[
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
        ],
        on_conflict=None,
        returning=None,
        last_insert_id=None,
    )
    assert qwp.query == (
        "INSERT INTO `users` (`name`, `age`) VALUES (?, ?), (?, ?)"
    )
    assert qwp.params == ["Alice", 30, "Bob", 25]


def test_mysql_update_with_params(mysql_dialect: MySQLDialect) -> None:
    """Verify UPDATE generates ? placeholders."""
    from pydba.query._condition import Condition
    from pydba.query.enums.condition import ConditionEnum

    where = [
        Condition(condition=ConditionEnum.EQUALS, identifier="id", value=42),
    ]
    qwp: QueryWithParams = mysql_dialect.update(
        table="users",
        updates={"name": "UpdatedName", "age": 35},
        where=where,
        returning=None,
    )
    assert "UPDATE `users` SET `name` = ?, `age` = ?" in qwp.query
    assert "WHERE `id` = ?" in qwp.query
    assert qwp.params == ["UpdatedName", 35, 42]


def test_mysql_delete_with_params(mysql_dialect: MySQLDialect) -> None:
    """Verify DELETE generates ? placeholders."""
    from pydba.query._condition import Condition
    from pydba.query.enums.condition import ConditionEnum

    where = [
        Condition(condition=ConditionEnum.EQUALS, identifier="id", value=99),
    ]
    qwp: QueryWithParams = mysql_dialect.delete(
        table="users",
        where=where,
        returning=None,
    )
    assert "DELETE FROM `users`" in qwp.query
    assert "WHERE `id` = ?" in qwp.query
    assert qwp.params == [99]


def test_mysql_drop_table(mysql_dialect: MySQLDialect) -> None:
    qwp: QueryWithParams = mysql_dialect.drop_table(
        if_exists=True,
        table="users",
    )
    assert qwp.query == "DROP TABLE IF EXISTS `users`"

    qwp2: QueryWithParams = mysql_dialect.drop_table(
        if_exists=False,
        table="users",
    )
    assert qwp2.query == "DROP TABLE `users`"


def test_mysql_version_gating(mysql_dialect: MySQLDialect) -> None:
    assert mysql_dialect.distinct_on is False
    assert mysql_dialect.lateral is False  # 8.0.0 < 8.0.14
    assert mysql_dialect.on_conflict is False
    assert mysql_dialect.returning is False
    assert mysql_dialect.savepoints is True

    # 8.0.14+ enables lateral
    mysql_8014 = MySQLDialect(version="8.0.14")
    assert mysql_8014.lateral is True

    mysql_8020 = MySQLDialect(version="8.0.20")
    assert mysql_8020.lateral is True