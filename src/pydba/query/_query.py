from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from pydba._query_with_params import QueryWithParams
from pydba.query.expressions.alias import Alias
from pydba.query.expressions.current_timestamp import CurrentTimestamp
from pydba.query.expressions.expression import Expression
from pydba.query.expressions.identifier import Identifier
from pydba.query.expressions.raw import Raw
from pydba.query.expressions.sub_query import SubQuery
from pydba.result._base import ResultABC

if TYPE_CHECKING:
    from pydba.database._abstract import DatabaseAbstract
    from pydba.dialects._base import DialectABC


class Query(ABC):

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None) -> None:
        super().__init__()
        self._dialect = dialect
        self._table = table
        self._database = database

    @property
    def dialect(self) -> DialectABC:
        return self._dialect

    @abstractmethod
    def to_query_with_params(self) -> QueryWithParams | list[QueryWithParams]:
        ...

    def to_sql(self) -> str | list[str]:
        """Return the full SQL string for this query."""
        qwp = self.to_query_with_params()
        if isinstance(qwp, list):
            return [q.to_sql(self._dialect) for q in qwp]
        return qwp.to_sql(self._dialect)

    def execute(self, emulate_prepare: bool = False) -> ResultABC | list[ResultABC]:
        if self._database is None:
            raise RuntimeError("Query is not bound to a Database. Call db.connect() or use db.select/insert/update/delete.")
        qwp = self.to_query_with_params()
        if isinstance(qwp, list):
            return [self._database.query_with_params(q, emulate_prepare) for q in qwp]
        return self._database.query_with_params(qwp, emulate_prepare)

    def explain(self, emulate_prepare: bool = False) -> list[dict[str, Any]]:
        if self._database is None:
            raise RuntimeError("Query is not bound to a Database. Call db.connect() or use db.select/insert/update/delete.")
        qwp = self.to_query_with_params()
        if isinstance(qwp, list):
            results: list[dict[str, Any]] = []
            for q in qwp:
                explain_qwp = QueryWithParams(
                    query=f"EXPLAIN {q.query}",
                    params=list(q.params),
                )
                result = self._database.query_with_params(explain_qwp, emulate_prepare)
                results.extend(result.fetch_dicts())
            return results
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


def expression(sql: str, params: list[Any] | None = None) -> Expression:
    return Expression(sql, params)


def sub_query(query: Any, alias: str) -> SubQuery:
    return SubQuery(query, alias)


def current_timestamp() -> CurrentTimestamp:
    return CurrentTimestamp()


def now() -> datetime:
    return datetime.now(UTC)
