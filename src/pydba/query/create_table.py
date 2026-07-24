from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydba._query_with_params import QueryWithParams
from pydba.query._ddl_mixins import ColumnsDefinitionMixin, ConstraintsMixin, IfNotExistsMixin, PrimaryKeysMixin
from pydba.query._query import Query
from pydba.result._base import ResultABC

if TYPE_CHECKING:
    from pydba.database._abstract import DatabaseAbstract
    from pydba.dialects._base import DialectABC


class CreateTableQuery(Query, ColumnsDefinitionMixin, PrimaryKeysMixin, ConstraintsMixin, IfNotExistsMixin):
    """Fluent CREATE TABLE query builder."""

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None, *args: Any, **kwargs: Any) -> None:
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
        result = super().execute(emulate_prepare)
        assert isinstance(result, ResultABC), "Expected a single ResultABC, got a list"
        return result
