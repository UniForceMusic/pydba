from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from pydba._query_with_params import QueryWithParams
from pydba.query._ddl_mixins import IfExistsMixin
from pydba.query._query import Query

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC
    from pydba.database._abstract import DatabaseAbstract


class DropTableQuery(Query, IfExistsMixin):
    """Fluent DROP TABLE query builder."""

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(dialect, table, database=database, *args, **kwargs)

    def from_(self, table: Any) -> Self:
        self._table = table
        return self

    def to_query_with_params(self) -> QueryWithParams:
        if_exists = self._if_exists if hasattr(self, '_if_exists') else False
        return self._dialect.drop_table(
            if_exists=if_exists,
            table=self._table,
        )
