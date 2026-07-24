from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pydba.database._abstract import DatabaseAbstract
    from pydba.dialects._base import DialectABC
    from pydba.query.delete import DeleteQuery
    from pydba.query.insert import InsertQuery
    from pydba.query.select import SelectQuery
    from pydba.query.update import UpdateQuery
    from pydba.result._base import ResultABC


class Table:
    """High-level table wrapper providing convenient CRUD operations."""

    def __init__(self, database: DatabaseAbstract, dialect: DialectABC, table: str) -> None:
        self._database = database
        self._dialect = dialect
        self._table = table

    def select(self, columns: list[Any] | None = None) -> SelectQuery:
        q = self._database.select(self._table)
        if columns:
            q.columns(columns)
        return q

    def insert(self, *values: dict[str, Any]) -> InsertQuery:
        q = self._database.insert(self._table)
        if values:
            q.values(*values)
        return q

    def select_or_insert(self, columns: list[Any], values: list[Any], **kwargs: Any) -> ResultABC:
        """Select matching rows or insert if none found."""
        q = self.select(columns).where_equals(**{columns[0]: values[0]})
        result = q.execute()
        row = result.fetch_dict()
        if row:
            return result
        return self.insert(dict(zip(columns, values))).execute()

    def insert_or_ignore(self, columns: list[Any], values: list[Any], **kwargs: Any) -> ResultABC:
        """Insert, ignoring if conflict."""
        q = self._database.insert(self._table)
        q.values(dict(zip(columns, values)))
        conflict = kwargs.get("conflict", columns[0])
        q.on_conflict_do_nothing(conflict)
        return self._database.query_with_params(q.to_query_with_params())

    def insert_or_update(self, columns: list[Any], values: list[Any], **kwargs: Any) -> ResultABC:
        """Insert or update on conflict (upsert)."""
        q = self._database.insert(self._table)
        q.values(dict(zip(columns, values)))
        conflict = kwargs.get("conflict", columns[0])
        updates = kwargs.get("updates", dict(zip(columns, values)))
        q.on_conflict_do_update(conflict, updates)
        return self._database.query_with_params(q.to_query_with_params())

    def update(self, values: dict[str, Any]) -> UpdateQuery:
        q = self._database.update(self._table)
        q.updates(values)
        return q

    def delete(self) -> DeleteQuery:
        return self._database.delete(self._table)

    def create(self, callback: Callable[..., Any] | None = None) -> ResultABC:
        """Create the table."""
        q = self._database.create_table(self._table)
        if callback:
            callback(q)
        return q.execute()

    def create_if_not_exists(self, callback: Callable[..., Any] | None = None) -> ResultABC:
        """Create the table if it doesn't exist."""
        q = self._database.create_table(self._table)
        q.if_not_exists()
        if callback:
            callback(q)
        return q.execute()

    def truncate(self) -> None:
        """Truncate (delete all rows from) the table."""
        qwp = self._dialect.delete(table=self._table, where=None, returning=None)
        self._database.query_with_params(qwp)

    def drop(self) -> ResultABC:
        """Drop the table."""
        return self._database.drop_table(self._table).execute()

    def drop_if_exists(self) -> ResultABC:
        """Drop the table if it exists."""
        q = self._database.drop_table(self._table)
        q.if_exists()
        return q.execute()

    def columns(self) -> list[str]:
        """Return the list of column names for the table."""
        # SQLite: PRAGMA table_info
        adapter_driver = getattr(self._database.adapter, 'driver_name', lambda: '')()
        if adapter_driver == 'sqlite':
            result = self._database.query(f"PRAGMA table_info({self._table})")
            rows = result.fetch_dicts()
            return [row['name'] for row in rows]
        # PostgreSQL: INFORMATION_SCHEMA
        result = self._database.query(
            f"SELECT column_name FROM information_schema.columns WHERE table_name = '{self._table}'"
        )
        rows = result.fetch_dicts()
        return [row['column_name'] for row in rows]

    def is_empty(self) -> bool:
        """Check if the table is empty."""
        result = self._database.query(f"SELECT count(*) AS cnt FROM {self._table}")
        row = result.fetch_dict()
        return row is None or row.get('cnt', 0) == 0
