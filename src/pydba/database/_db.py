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
    def connect_sqlite(name: str, **kwargs: Any) -> DB:
        """Connect to a SQLite database.

        Args:
            name: database name or path (e.g. ``":memory:"`` or ``"data.db"``)
            **kwargs: additional connection options

        Returns:
            DB instance connected to SQLite.
        """
        from pydba.adapters.sqlite import SQLiteAdapter
        from pydba.dialects.sqlite import SQLiteDialect

        options = kwargs.pop("options", {})
        startup_queries = kwargs.pop("startup_queries", [])
        debug_callback = kwargs.pop("debug_callback", None)

        adapter = SQLiteAdapter(
            database_name=name,
            options=options,
            startup_queries=startup_queries,
            debug_callback=debug_callback,
            **kwargs,
        )
        version = adapter.version()
        dialect = SQLiteDialect(version=version, options=options)
        return DB(adapter, dialect)

    @staticmethod
    def connect_postgresql(name: str, **kwargs: Any) -> DB:
        """Connect to a PostgreSQL database.

        Args:
            name: database name
            **kwargs: additional connection options

        Returns:
            DB instance connected to PostgreSQL.
        """
        from pydba.adapters.postgres import PsycopgAdapter
        from pydba.dialects.postgres import PgSQLDialect

        options = kwargs.pop("options", {})
        startup_queries = kwargs.pop("startup_queries", [])
        debug_callback = kwargs.pop("debug_callback", None)

        adapter = PsycopgAdapter(
            database_name=name,
            options=options,
            startup_queries=startup_queries,
            debug_callback=debug_callback,
            **kwargs,
        )
        version = adapter.version()
        dialect = PgSQLDialect(version=version, options=options)
        return DB(adapter, dialect)