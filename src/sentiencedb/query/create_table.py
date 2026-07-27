from __future__ import annotations

from typing import Any, cast

from sentiencedb._query_with_params import QueryWithParams
from sentiencedb.database._abstract import DatabaseAbstract
from sentiencedb.dialects._base import DialectABC
from sentiencedb.query._ddl_mixins import ColumnsDefinitionMixin, ConstraintsMixin, IfNotExistsMixin, PrimaryKeysMixin
from sentiencedb.query._query import Query
from sentiencedb.result._base import ResultABC


class CreateTableQuery(Query, ColumnsDefinitionMixin, PrimaryKeysMixin, ConstraintsMixin, IfNotExistsMixin):
    def __init__(self, dialect: DialectABC, table: str | list[str], database: DatabaseAbstract, *args: Any, **kwargs: Any) -> None:
        kwargs['database'] = database
        super().__init__(dialect, table, *args, **kwargs)

    def to_query_with_params(self) -> QueryWithParams:
        return self._dialect.create_table(
            if_not_exists=self._if_not_exists,
            table=self._table,
            columns=self._columns,
            primary_keys=self._primary_keys if self._primary_keys else None,
            constraints=self._constraints if self._constraints else None,
        )

    def execute(self, emulate_prepare: bool = False) -> ResultABC:
        return cast(ResultABC, super().execute(emulate_prepare))
