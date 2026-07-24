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
    """Fluent SELECT query builder."""

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None, *args: Any, **kwargs: Any) -> None:
        kwargs['database'] = database
        super().__init__(dialect, table, *args, **kwargs)

    def from_(self, table: Any) -> Self:
        self._table = table
        return self

    def to_query_with_params(self) -> QueryWithParams:
        # Collect state from mixins
        cols = self._columns_list if hasattr(self, '_columns_list') else None
        distinct = self._distinct if hasattr(self, '_distinct') else None
        joins = self.joins if hasattr(self, 'joins') else None
        where = self.where if hasattr(self, 'where') else None
        group_by = self._group_by_cols if hasattr(self, '_group_by_cols') else None
        having = self.having if hasattr(self, 'having') else None
        order_by = self._order_by_list if hasattr(self, '_order_by_list') else None
        limit_val = self._limit_val if hasattr(self, '_limit_val') else None
        offset_val = self._offset_val if hasattr(self, '_offset_val') else None
        unions = self._unions_list if hasattr(self, '_unions_list') else None

        return self._dialect.select(
            distinct=distinct,
            columns=cols,
            table=self._table,
            joins=joins,
            where=where,
            group_by=group_by,
            having=having,
            order_by=order_by,
            limit=limit_val,
            offset=offset_val,
            unions=unions,
        )

    def execute(self, emulate_prepare: bool = False) -> ResultABC:
        result = super().execute(emulate_prepare)
        assert isinstance(result, ResultABC), "Expected a single ResultABC, got a list"
        return result

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
