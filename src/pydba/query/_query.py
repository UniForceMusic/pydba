from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional, TYPE_CHECKING

from pydba._query_with_params import QueryWithParams
from pydba.query.expressions.raw import Raw
from pydba.query.expressions.identifier import Identifier
from pydba.query.expressions.alias import Alias
from pydba.query.expressions.expression import Expression
from pydba.query.expressions.sub_query import SubQuery
from pydba.query.expressions.current_timestamp import CurrentTimestamp
from pydba.result._base import ResultABC

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC
    from pydba.database._abstract import DatabaseAbstract


class Query(ABC):
    """Abstract base class for all query types (SELECT, INSERT, UPDATE, DELETE)."""

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._dialect = dialect
        self._table = table
        self._database = database

    @property
    def dialect(self) -> DialectABC:
        return self._dialect

    @abstractmethod
    def to_query_with_params(self) -> QueryWithParams:
        """Convert the query to a QueryWithParams for execution."""
        ...

    def to_sql(self) -> str:
        """Return the full SQL string for this query."""
        qwp = self.to_query_with_params()
        return qwp.to_sql(self._dialect)

    def execute(self, emulate_prepare: bool = False) -> ResultABC:
        """Execute the query. Requires a database reference to be set."""
        if self._database is None:
            raise RuntimeError("Query is not bound to a Database. Call db.connect() or use db.select/insert/update/delete.")
        qwp = self.to_query_with_params()
        return self._database.query_with_params(qwp, emulate_prepare)

    def explain(self, emulate_prepare: bool = False) -> list[dict]:
        """Return EXPLAIN output for this query."""
        if self._database is None:
            raise RuntimeError("Query is not bound to a Database. Call db.connect() or use db.select/insert/update/delete.")
        qwp = self.to_query_with_params()
        import copy
        explain_qwp = QueryWithParams(
            query=f"EXPLAIN {qwp.query}",
            params=list(qwp.params),
        )
        result = self._database.query_with_params(explain_qwp, emulate_prepare)
        return result.fetch_dicts()

    # --- Module-level factory functions ---


def raw(sql: str) -> Raw:
    return Raw(sql)


def identifier(identifier: str | list[str]) -> Identifier:
    return Identifier(identifier)


def alias(identifier: str | list[str] | Any, alias: str) -> Alias:
    return Alias(identifier, alias)


def expression(sql: str, params: Optional[list] = None) -> Expression:
    return Expression(sql, params)


def sub_query(query: Any, alias: str) -> SubQuery:
    return SubQuery(query, alias)


def current_timestamp() -> CurrentTimestamp:
    return CurrentTimestamp()


def now() -> datetime:
    return datetime.now()
