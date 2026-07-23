from __future__ import annotations

from typing import Any, TYPE_CHECKING

from pydba.query.expressions._sql import SqlABC

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC


class Expression(SqlABC):
    """Represents a SQL expression with parameters."""
    
    def __init__(self, sql: str, params: list[Any] | None = None) -> None:
        self._sql = sql
        self._params = params or []
    
    def sql(self, dialect: DialectABC) -> str:
        return self._sql
    
    def params(self, dialect: DialectABC) -> list[Any]:
        return list(self._params)
    
    def raw_sql(self, dialect: DialectABC) -> str:
        from pydba._query_with_params import QueryWithParams
        qwp = QueryWithParams(query=self._sql, params=list(self._params))
        return qwp.to_sql(dialect)
