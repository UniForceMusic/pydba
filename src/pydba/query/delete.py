from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Self

from pydba._query_with_params import QueryWithParams
from pydba.query._query import Query
from pydba.query._where_mixin import WhereMixin
from pydba.query._simple_mixins import ReturningMixin

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC
    from pydba.database._abstract import DatabaseAbstract


class DeleteQuery(Query, WhereMixin, ReturningMixin):
    """Fluent DELETE query builder."""

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(dialect, table, database=database, *args, **kwargs)

    def from_(self, table: Any) -> Self:
        self._table = table
        return self

    def to_query_with_params(self) -> QueryWithParams:
        where = self.where if hasattr(self, 'where') else None
        returning = self._returning_list if hasattr(self, '_returning_list') else None

        return self._dialect.delete(
            table=self._table,
            where=where,
            returning=returning,
        )
