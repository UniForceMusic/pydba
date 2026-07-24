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

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None) -> None:
        super().__init__(dialect, table, database=database)

    def to_query_with_params(self) -> QueryWithParams:
        return self._dialect.update(
            table=self._table,
            updates=self._updates_dict,
            where=self.where,
            returning=self._returning_list,
        )

    def execute(self, emulate_prepare: bool = False) -> ResultABC:
        return super().execute(emulate_prepare)  # type: ignore[return-value]
