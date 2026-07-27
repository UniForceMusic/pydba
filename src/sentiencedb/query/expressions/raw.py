from __future__ import annotations

from typing import Any

from sentiencedb.dialects._base import DialectABC
from sentiencedb.query.expressions._sql import SqlABC


class Raw(SqlABC):
    def __init__(self, sql: str) -> None:
        self._sql = sql

    def sql(self, dialect: DialectABC) -> str:
        return self._sql

    def params(self, dialect: DialectABC) -> list[Any]:
        return []

    def raw_sql(self, dialect: DialectABC) -> str:
        return self._sql
