from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydba.query import SelectQuery
from pydba.query.expressions.alias import Alias
from pydba.query.expressions.current_timestamp import CurrentTimestamp
from pydba.query.expressions.expression import Expression
from pydba.query.expressions.identifier import Identifier
from pydba.query.expressions.raw import Raw
from pydba.query.expressions.sub_query import SubQuery


def escape_ansi(string: str, chars: str) -> str:
    return string.translate(str.maketrans(chars, chars * 2))


def escape_backslash(string: str, chars: str) -> str:
    return string.translate(str.maketrans(chars, "\\" + chars))


def raw(sql: str) -> Raw:
    return Raw(sql)


def identifier(identifier: str | list[str]) -> Identifier:
    return Identifier(identifier)


def alias(identifier: str | list[str] | Any, alias: str) -> Alias:
    return Alias(identifier, alias)


def expression(sql: str, params: list[Any] | None = None) -> Expression:
    return Expression(sql, params)


def sub_query(query: SelectQuery, alias: str) -> SubQuery:
    return SubQuery(query, alias)


def current_timestamp() -> CurrentTimestamp:
    return CurrentTimestamp()


def now() -> datetime:
    return datetime.now(UTC)
