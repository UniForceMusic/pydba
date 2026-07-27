from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sentiencedb.query.expressions._sql import SqlABC

if TYPE_CHECKING:
    from sentiencedb.dialects._base import DialectABC

class CurrentTimestamp(SqlABC):
    
    def sql(self, dialect: DialectABC) -> str:
        return "CURRENT_TIMESTAMP"
    
    def params(self, dialect: DialectABC) -> list[Any]:
        return []
    
    def raw_sql(self, dialect: DialectABC) -> str:
        return "CURRENT_TIMESTAMP"
