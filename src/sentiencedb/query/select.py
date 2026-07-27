from __future__ import annotations

from typing import Self, cast

from sentiencedb._query_with_params import QueryWithParams
from sentiencedb.database._abstract import DatabaseAbstract
from sentiencedb.dialects._base import DialectABC
from sentiencedb.query._having_mixin import HavingMixin
from sentiencedb.query._joins_mixin import JoinsMixin
from sentiencedb.query._query import Query
from sentiencedb.query._simple_mixins import (
    ColumnsMixin,
    DistinctMixin,
    GroupByMixin,
    LimitMixin,
    OffsetMixin,
    OrderByMixin,
    UnionMixin,
)
from sentiencedb.query._where_mixin import WhereMixin
from sentiencedb.result._base import ResultABC


class SelectQuery(
    Query, WhereMixin, HavingMixin, JoinsMixin,
    ColumnsMixin, DistinctMixin, GroupByMixin,
    OrderByMixin, LimitMixin, OffsetMixin, UnionMixin,
):

    def __init__(self, dialect: DialectABC, table: str | list[str], database: DatabaseAbstract) -> None:
        super().__init__(dialect, table, database=database)

    def table(self, table: str | list[str]) -> Self:
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
        return cast(ResultABC, super().execute(emulate_prepare))

    def count(self, emulate_prepare: bool = False) -> int:
        inner_qwp = self.to_query_with_params()
        inner_sql = inner_qwp.query
        count_sql = f"SELECT count(*) FROM ({inner_sql}) AS _count"
        count_qwp = QueryWithParams(query=count_sql, params=list(inner_qwp.params))
        result = self._database.query_with_params(count_qwp, emulate_prepare)
        row = result.fetch_dict()
        if row:
            for val in row.values():
                return int(val)
        return 0
