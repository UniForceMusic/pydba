from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Self

from pydba._query_with_params import QueryWithParams
from pydba.query._ddl_mixins import AltersMixin
from pydba.query._query import Query
from pydba.result._base import ResultABC

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC
    from pydba.database._abstract import DatabaseAbstract


class AlterTableQuery(Query, AltersMixin):
    """Fluent ALTER TABLE query builder."""

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(dialect, table, database=database, *args, **kwargs)

    def to_query_with_params(self) -> list[QueryWithParams]:
        alters = self._alters if hasattr(self, '_alters') else []
        return self._dialect.alter_table(
            table=self._table,
            alters=alters,
        )

    def to_sql(self) -> list[str]:
        queries_with_params = self.to_query_with_params()
        return [qwp.to_sql(self._dialect) for qwp in queries_with_params]

    def execute(self, emulate_prepare: bool = False) -> list[ResultABC]:
        if self._database is None:
            raise RuntimeError("Query is not bound to a Database. Call db.connect() or use db.alter_table().")
        queries_with_params = self.to_query_with_params()
        return [self._database.query_with_params(qwp, emulate_prepare) for qwp in queries_with_params]

    def explain(self, emulate_prepare: bool = False) -> list[dict]:
        return []
