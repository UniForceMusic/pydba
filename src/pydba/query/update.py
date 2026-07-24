from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydba._query_with_params import QueryWithParams
from pydba.query._query import Query
from pydba.query._simple_mixins import ReturningMixin, UpdatesMixin
from pydba.query._where_mixin import WhereMixin
from pydba.result._base import ResultABC

if TYPE_CHECKING:
    from pydba.database._abstract import DatabaseAbstract
    from pydba.dialects._base import DialectABC


class UpdateQuery(Query, WhereMixin, UpdatesMixin, ReturningMixin):
    """Fluent UPDATE query builder."""

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None, *args: Any, **kwargs: Any) -> None:
        kwargs['database'] = database
        super().__init__(dialect, table, *args, **kwargs)

    def to_query_with_params(self) -> QueryWithParams:
        updates = self._updates_dict if hasattr(self, '_updates_dict') else {}
        where = self.where if hasattr(self, 'where') else None
        returning = self._returning_list if hasattr(self, '_returning_list') else None

        return self._dialect.update(
            table=self._table,
            updates=updates,
            where=where,
            returning=returning,
        )

    def execute(self, emulate_prepare: bool = False) -> ResultABC:
        result = super().execute(emulate_prepare)
        assert isinstance(result, ResultABC), "Expected a single ResultABC, got a list"
        return result
