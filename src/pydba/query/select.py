from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from pydba._query_with_params import QueryWithParams
from pydba.query._having_mixin import HavingMixin
from pydba.query._joins_mixin import JoinsMixin
from pydba.query._query import Query
from pydba.query._simple_mixins import (
    ColumnsMixin,
    DistinctMixin,
    GroupByMixin,
    LimitMixin,
    OffsetMixin,
    OrderByMixin,
    UnionMixin,
)
from pydba.query._where_mixin import WhereMixin
from pydba.result._base import ResultABC

if TYPE_CHECKING:
    from pydba.database._abstract import DatabaseAbstract
    from pydba.dialects._base import DialectABC


class SelectQuery(
    Query, WhereMixin, HavingMixin, JoinsMixin,
    ColumnsMixin, DistinctMixin, GroupByMixin,
    OrderByMixin, LimitMixin, OffsetMixin, UnionMixin,
):

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None) -> None:
        super().__init__(dialect, table, database=database)

    def from_(self, table: Any) -> Self:
        self._table = table
        return self

    def to_query_with_params(self) -> QueryWithParams:
        return self._dialect.select(
            distinct=self._distinct,
            columns=self._columns_list,
            table=self._table,
            joins=self.joins,
            where=self.where,
            group_by=self._group_by_cols,
            having=self.having,
            order_by=self._order_by_list,
            limit=self._limit_val,
            offset=self._offset_val,
            unions=self._unions_list,
        )

    def execute(self, emulate_prepare: bool = False) -> ResultABC:
        return super().execute(emulate_prepare)  # type: ignore[return-value]

    def count(self, emulate_prepare: bool = False) -> int:
        """Wrap the query in SELECT count(*) FROM (...) and return count."""
        inner_qwp = self.to_query_with_params()
        inner_sql = inner_qwp.query
        count_sql = f"SELECT count(*) FROM ({inner_sql}) AS _count"
        count_qwp = QueryWithParams(query=count_sql, params=list(inner_qwp.params))
        if self._database is None:
            raise RuntimeError("count() requires a Database to execute the query")
        result = self._database.query_with_params(count_qwp, emulate_prepare)
        row = result.fetch_dict()
        if row:
            for val in row.values():
                return int(val)
        return 0
