from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydba._query_with_params import QueryWithParams
from pydba.query._query import Query
from pydba.query._simple_mixins import LastInsertIdMixin, OnConflictMixin, ReturningMixin, ValuesMixin
from pydba.result._base import ResultABC

if TYPE_CHECKING:
    from pydba.database._abstract import DatabaseAbstract
    from pydba.dialects._base import DialectABC


class InsertQuery(Query, ValuesMixin, OnConflictMixin, ReturningMixin, LastInsertIdMixin):

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None) -> None:
        super().__init__(dialect, table, database=database)

    def to_query_with_params(self) -> QueryWithParams:
        return self._dialect.insert(
            table=self._table,
            values=self._values_list,
            on_conflict=self._on_conflict,
            returning=self._returning_list,
            last_insert_id=self._last_insert_id_col,
        )

    def execute(self, emulate_prepare: bool = False) -> ResultABC:
        return super().execute(emulate_prepare)  # type: ignore[return-value]
