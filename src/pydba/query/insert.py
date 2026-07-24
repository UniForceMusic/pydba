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
    """Fluent INSERT query builder."""

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None, *args: Any, **kwargs: Any) -> None:
        kwargs['database'] = database
        super().__init__(dialect, table, *args, **kwargs)

    def to_query_with_params(self) -> QueryWithParams:
        values = self._values_list if hasattr(self, '_values_list') else []
        on_conflict = self._on_conflict if hasattr(self, '_on_conflict') else None
        returning = self._returning_list if hasattr(self, '_returning_list') else None
        last_insert_id = self._last_insert_id_col if hasattr(self, '_last_insert_id_col') else None

        return self._dialect.insert(
            table=self._table,
            values=values,
            on_conflict=on_conflict,
            returning=returning,
            last_insert_id=last_insert_id,
        )

    def execute(self, emulate_prepare: bool = False) -> ResultABC:
        result = super().execute(emulate_prepare)
        assert isinstance(result, ResultABC), "Expected a single ResultABC, got a list"
        return result
