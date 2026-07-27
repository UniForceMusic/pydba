from __future__ import annotations

from typing import TYPE_CHECKING, Self, cast

from sentiencedb.query._query import Query
from sentiencedb.query._simple_mixins import ReturningMixin
from sentiencedb.query._where_mixin import WhereMixin
from sentiencedb.result._base import ResultABC

if TYPE_CHECKING:
    from sentiencedb._query_with_params import QueryWithParams
    from sentiencedb.database._abstract import DatabaseAbstract
    from sentiencedb.dialects._base import DialectABC


class DeleteQuery(Query, WhereMixin, ReturningMixin):
    def __init__(self, dialect: DialectABC, table: str | list[str], database: DatabaseAbstract | None = None) -> None:
        super().__init__(dialect, table, database=database)

    def table(self, table: str | list[str]) -> Self:
        self._table = table
        return self

    def to_query_with_params(self) -> QueryWithParams:
        return self._dialect.delete(
            table=self._table,
            where=self.where,
            returning=self._returning_list,
        )
