from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from sentiencedb._query_with_params import QueryWithParams
from sentiencedb.query._ddl_mixins import IfExistsMixin
from sentiencedb.query._query import Query
from sentiencedb.result._base import ResultABC

if TYPE_CHECKING:
    from sentiencedb.database._abstract import DatabaseAbstract
    from sentiencedb.dialects._base import DialectABC


class DropTableQuery(Query, IfExistsMixin):
    def __init__(self, dialect: DialectABC, table: str | list[str], database: DatabaseAbstract | None = None, *args: Any, **kwargs: Any) -> None:
        kwargs['database'] = database
        super().__init__(dialect, table, *args, **kwargs)

    def table(self, table: str | list[str]) -> Self:
        self._table = table
        return self

    def to_query_with_params(self) -> QueryWithParams:
        if_exists = self._if_exists
        return self._dialect.drop_table(
            if_exists=if_exists,
            table=self._table,
        )

    def execute(self, emulate_prepare: bool = False) -> ResultABC:
        result = super().execute(emulate_prepare)
        assert isinstance(result, ResultABC), "Expected a single ResultABC, got a list"
        return result
