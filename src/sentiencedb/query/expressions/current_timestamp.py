from __future__ import annotations

from typing import Any

from sentiencedb.dialects._base import DialectABC
from sentiencedb.query.expressions._sql import SqlABC


class CurrentTimestamp(SqlABC):
    def sql(self, dialect: DialectABC) -> str:
        return "CURRENT_TIMESTAMP"

    def params(self, dialect: DialectABC) -> list[Any]:
        return []

    def raw_sql(self, dialect: DialectABC) -> str:
        return "CURRENT_TIMESTAMP"
