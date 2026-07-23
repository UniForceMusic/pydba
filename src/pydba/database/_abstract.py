from __future__ import annotations

from typing import Any, Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pydba.adapters._base import AdapterABC
    from pydba.dialects._base import DialectABC
    from pydba._query_with_params import QueryWithParams
    from pydba.result._base import ResultABC
    from pydba.query.select import SelectQuery
    from pydba.query.insert import InsertQuery
    from pydba.query.update import UpdateQuery
    from pydba.query.delete import DeleteQuery


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

    def exec(self, query: str) -> Any:
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

    def begin_transaction(self, name: Optional[str] = None) -> None:
        if name:
            qwp = self._dialect.begin_savepoint(name)
            self._adapter.exec(qwp.query)
        else:
            self._adapter.begin_transaction()

    def commit_transaction(self, release_savepoints: bool = False, name: Optional[str] = None) -> None:
        if name:
            qwp = self._dialect.commit_savepoint(name)
            self._adapter.exec(qwp.query)
        else:
            self._adapter.commit_transaction()

    def rollback_transaction(self, release_savepoints: bool = False, name: Optional[str] = None) -> None:
        if name:
            qwp = self._dialect.rollback_savepoint(name)
            self._adapter.exec(qwp.query)
        else:
            self._adapter.rollback_transaction()

    @property
    def in_transaction(self) -> bool:
        return self._adapter.in_transaction

    def transaction(self, callback: Callable, release_savepoints: bool = False, name: Optional[str] = None) -> Any:
        """Execute a callback within a transaction."""
        self.begin_transaction(name=name)
        try:
            result = callback(self)
            self.commit_transaction(release_savepoints=release_savepoints, name=name)
            return result
        except Exception:
            self.rollback_transaction(release_savepoints=release_savepoints, name=name)
            raise

    def last_insert_id(self, name: Optional[str] = None) -> Optional[int | str]:
        return self._adapter.last_insert_id(name)

    # --- Query builder factories ---

    def select(self, table: Any) -> SelectQuery:
        from pydba.query.select import SelectQuery
        return SelectQuery(self._dialect, table, database=self)

    def select_table(self, table: Any, alias: Optional[str] = None) -> SelectQuery:
        from pydba.query.select import SelectQuery
        if alias:
            from pydba.query.expressions.alias import Alias
            table = Alias(table, alias)
        return SelectQuery(self._dialect, table, database=self)

    def select_sub_query(self, sub_query: Any, alias: str) -> SelectQuery:
        from pydba.query.select import SelectQuery
        from pydba.query.expressions.sub_query import SubQuery
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
