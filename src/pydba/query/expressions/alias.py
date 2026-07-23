from __future__ import annotations

from typing import Any, TYPE_CHECKING

from pydba.query.expressions._sql import SqlABC

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC


class Alias(SqlABC):
    """Represents an aliased identifier or expression: `expr AS alias`."""
    
    def __init__(self, identifier: str | list[str] | SqlABC, alias: str) -> None:
        self._identifier = identifier
        self._alias = alias
    
    def sql(self, dialect: DialectABC) -> str:
        from pydba.query.expressions.identifier import Identifier
        if isinstance(self._identifier, SqlABC):
            id_sql = self._identifier.sql(dialect)
        else:
            id_sql = dialect.escape_identifier(self._identifier)
        return f"{id_sql} AS {dialect.escape_identifier(self._alias)}"
    
    def params(self, dialect: DialectABC) -> list[Any]:
        from pydba.query.expressions.identifier import Identifier
        if isinstance(self._identifier, SqlABC):
            return self._identifier.params(dialect)
        return []
    
    def raw_sql(self, dialect: DialectABC) -> str:
        from pydba.query.expressions.identifier import Identifier
        if isinstance(self._identifier, SqlABC):
            id_sql = self._identifier.raw_sql(dialect)
        else:
            id_sql = dialect.escape_identifier(self._identifier)
        return f"{id_sql} AS {dialect.escape_identifier(self._alias)}"
