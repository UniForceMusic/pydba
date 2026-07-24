from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from pydba._query_with_params import QueryWithParams
from pydba.query._ddl_mixins import IfExistsMixin
from pydba.query._query import Query
from pydba.result._base import ResultABC

if TYPE_CHECKING:
    from pydba.database._abstract import DatabaseAbstract
    from pydba.dialects._base import DialectABC


class DropTableQuery(Query, IfExistsMixin):
    """Fluent DROP TABLE query builder."""

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None, *args: Any, **kwargs: Any) -> None:
        kwargs['database'] = database
        super().__init__(dialect, table, *args, **kwargs)

    def from_(self, table: Any) -> Self:
        self._table = table
        return self

    def to_query_with_params(self) -> QueryWithParams:
        if_exists = self._if_exists if hasattr(self, '_if_exists') else False
        return self._dialect.drop_table(
            if_exists=if_exists,
            table=self._table,
        )

    def execute(self, emulate_prepare: bool = False) -> ResultABC:
        result = super().execute(emulate_prepare)
        assert isinstance(result, ResultABC), "Expected a single ResultABC, got a list"
        return result
