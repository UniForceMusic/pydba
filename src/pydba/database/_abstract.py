from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pydba._query_with_params import QueryWithParams
    from pydba.adapters._base import AdapterABC
    from pydba.dialects._base import DialectABC
    from pydba.query.alter_table import AlterTableQuery
    from pydba.query.create_table import CreateTableQuery
    from pydba.query.delete import DeleteQuery
    from pydba.query.drop_table import DropTableQuery
    from pydba.query.insert import InsertQuery
    from pydba.query.select import SelectQuery
    from pydba.query.update import UpdateQuery
    from pydba.result._base import ResultABC


class DatabaseAbstract:
    """Abstract base class for the top-level database facade."""

    def __init__(self, adapter: AdapterABC, dialect: DialectABC) -> None:
        self._adapter = adapter
        self._dialect = dialect

    @property
    def adapter(self) -> AdapterABC:
        return self._adapter

    @property
    def dialect(self) -> DialectABC:
        return self._dialect

    def exec(self, query: str) -> None:
        return self._adapter.exec(query)

    def query(self, query: str) -> ResultABC:
        return self._adapter.query(query)

    def prepared(self, query: str, params: list[Any], emulate: bool = False) -> ResultABC:
        from pydba._query_with_params import QueryWithParams
        qwp = QueryWithParams(query=query, params=params)
        return self._adapter.query_with_params(self._dialect, qwp, emulate)

    def query_with_params(self, qwp: QueryWithParams, emulate: bool = False) -> ResultABC:
        return self._adapter.query_with_params(self._dialect, qwp, emulate)

    # --- Transaction handling ---

    def begin_transaction(self, name: str | None = None) -> None:
        if name:
            qwp = self._dialect.begin_savepoint(name)
            self._adapter.exec(qwp.query)
        else:
            self._adapter.begin_transaction()

    def commit_transaction(self, release_savepoints: bool = False, name: str | None = None) -> None:
        if name:
            qwp = self._dialect.commit_savepoint(name)
            self._adapter.exec(qwp.query)
        else:
            self._adapter.commit_transaction()

    def rollback_transaction(self, release_savepoints: bool = False, name: str | None = None) -> None:
        if name:
            qwp = self._dialect.rollback_savepoint(name)
            self._adapter.exec(qwp.query)
        else:
            self._adapter.rollback_transaction()

    @property
    def in_transaction(self) -> bool:
        return self._adapter.in_transaction

    def transaction(self, callback: Callable[..., Any], release_savepoints: bool = False, name: str | None = None) -> Any:
        """Execute a callback within a transaction."""
        self.begin_transaction(name=name)
        try:
            result = callback(self)
            self.commit_transaction(release_savepoints=release_savepoints, name=name)
            return result
        except Exception:
            self.rollback_transaction(release_savepoints=release_savepoints, name=name)
            raise

    def last_insert_id(self, name: str | None = None) -> int | str | None:
        return self._adapter.last_insert_id(name)

    # --- Query builder factories ---

    def select(self, table: Any) -> SelectQuery:
        from pydba.query.select import SelectQuery
        return SelectQuery(self._dialect, table, database=self)

    def select_table(self, table: Any, alias: str | None = None) -> SelectQuery:
        from pydba.query.select import SelectQuery
        if alias:
            from pydba.query.expressions.alias import Alias
            table = Alias(table, alias)
        return SelectQuery(self._dialect, table, database=self)

    def select_sub_query(self, sub_query: Any, alias: str) -> SelectQuery:
        from pydba.query.expressions.sub_query import SubQuery
        from pydba.query.select import SelectQuery
        sq = SubQuery(sub_query, alias)
        return SelectQuery(self._dialect, sq, database=self)

    def insert(self, table: Any) -> InsertQuery:
        from pydba.query.insert import InsertQuery
        return InsertQuery(self._dialect, table, database=self)

    def update(self, table: Any) -> UpdateQuery:
        from pydba.query.update import UpdateQuery
        return UpdateQuery(self._dialect, table, database=self)

    def delete(self, table: Any) -> DeleteQuery:
        from pydba.query.delete import DeleteQuery
        return DeleteQuery(self._dialect, table, database=self)

    def create_table(self, table: Any) -> CreateTableQuery:
        from pydba.query.create_table import CreateTableQuery
        return CreateTableQuery(self._dialect, table, database=self)

    def alter_table(self, table: Any) -> AlterTableQuery:
        from pydba.query.alter_table import AlterTableQuery
        return AlterTableQuery(self._dialect, table, database=self)

    def drop_table(self, table: Any) -> DropTableQuery:
        from pydba.query.drop_table import DropTableQuery
        return DropTableQuery(self._dialect, table, database=self)
