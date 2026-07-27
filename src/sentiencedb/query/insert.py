from __future__ import annotations

from typing import cast

from sentiencedb._query_with_params import QueryWithParams
from sentiencedb.database._abstract import DatabaseAbstract
from sentiencedb.dialects._base import DialectABC
from sentiencedb.query._query import Query
from sentiencedb.query._simple_mixins import LastInsertIdMixin, OnConflictMixin, ReturningMixin, ValuesMixin
from sentiencedb.result._base import ResultABC


class InsertQuery(Query, ValuesMixin, OnConflictMixin, ReturningMixin, LastInsertIdMixin):
    def __init__(self, dialect: DialectABC, table: str | list[str], database: DatabaseAbstract) -> None:
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
        return cast(ResultABC, super().execute(emulate_prepare))
