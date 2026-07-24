from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Self

from pydba._query_with_params import QueryWithParams
from pydba.query._query import Query
from pydba.query._ddl_mixins import ColumnsDefinitionMixin, PrimaryKeysMixin, ConstraintsMixin, IfNotExistsMixin

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC
    from pydba.database._abstract import DatabaseAbstract


class CreateTableQuery(Query, ColumnsDefinitionMixin, PrimaryKeysMixin, ConstraintsMixin, IfNotExistsMixin):
    """Fluent CREATE TABLE query builder."""

    def __init__(self, dialect: DialectABC, table: Any, database: DatabaseAbstract | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(dialect, table, database=database, *args, **kwargs)

    def to_query_with_params(self) -> QueryWithParams:
        return self._dialect.create_table(
            if_not_exists=self._if_not_exists,
            table=self._table,
            columns=self._columns,
            primary_keys=self._primary_keys if self._primary_keys else None,
            constraints=self._constraints if self._constraints else None,
        )
