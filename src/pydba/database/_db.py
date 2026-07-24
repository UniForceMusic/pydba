from __future__ import annotations

from typing import Any

from pydba.database._database import Database


class DB(Database):
    """User-friendly facade for Database.

    Usage::

        from pydba.database import DB

        db = DB.connect_sqlite(":memory:")
        result = db.select("users").execute()
    """

    @staticmethod
    def _connect(adapter_cls: type, dialect_cls: type, name: str, **kwargs: Any) -> DB:
        options = kwargs.pop("options", {})
        startup_queries = kwargs.pop("startup_queries", [])
        debug_callback = kwargs.pop("debug_callback", None)
        adapter = adapter_cls(
            database_name=name,
            options=options,
            startup_queries=startup_queries,
            debug_callback=debug_callback,
            **kwargs,
        )
        return DB(adapter, dialect_cls(version=adapter.version(), options=options))

    @staticmethod
    def connect_sqlite(name: str, **kwargs: Any) -> DB:
        from pydba.adapters.sqlite import SQLiteAdapter
        from pydba.dialects.sqlite import SQLiteDialect
        return DB._connect(SQLiteAdapter, SQLiteDialect, name, **kwargs)

    @staticmethod
    def connect_postgresql(name: str, **kwargs: Any) -> DB:
        from pydba.adapters.postgres import PsycopgAdapter
        from pydba.dialects.postgres import PgSQLDialect
        return DB._connect(PsycopgAdapter, PgSQLDialect, name, **kwargs)

    @staticmethod
    def connect_mysql(name: str, **kwargs: Any) -> DB:
        from pydba.adapters.mysql import MySQLAdapter
        from pydba.dialects.mysql import MySQLDialect
        return DB._connect(MySQLAdapter, MySQLDialect, name, **kwargs)
