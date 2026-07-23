from __future__ import annotations

from typing import Any, TYPE_CHECKING

from pydba.query.expressions._sql import SqlABC

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC


class CurrentTimestamp(SqlABC):
    """Represents the SQL CURRENT_TIMESTAMP value."""
    
    def sql(self, dialect: DialectABC) -> str:
        return "CURRENT_TIMESTAMP"
    
    def params(self, dialect: DialectABC) -> list[Any]:
        return []
    
    def raw_sql(self, dialect: DialectABC) -> str:
        return "CURRENT_TIMESTAMP"
