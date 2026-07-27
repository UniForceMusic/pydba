from __future__ import annotations

from typing import Any

from sentiencedb.dialects._base import DialectABC
from sentiencedb.query.expressions._sql import SqlABC


class Identifier(SqlABC):
    def __init__(self, identifier: str | list[str]) -> None:
        self._identifier = identifier

    def sql(self, dialect: DialectABC) -> str:
        return dialect.escape_identifier(self._identifier)

    def params(self, dialect: DialectABC) -> list[Any]:
        return []

    def raw_sql(self, dialect: DialectABC) -> str:
        return dialect.escape_identifier(self._identifier)
