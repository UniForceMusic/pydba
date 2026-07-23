from __future__ import annotations

from typing import Any, TYPE_CHECKING

from pydba.query.expressions._sql import SqlABC

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC


class Identifier(SqlABC):
    """Represents a SQL identifier (column/table name), properly escaped."""
    
    def __init__(self, identifier: str | list[str]) -> None:
        self._identifier = identifier
    
    def sql(self, dialect: DialectABC) -> str:
        return dialect.escape_identifier(self._identifier)
    
    def params(self, dialect: DialectABC) -> list[Any]:
        return []
    
    def raw_sql(self, dialect: DialectABC) -> str:
        return dialect.escape_identifier(self._identifier)
