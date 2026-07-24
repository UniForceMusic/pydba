from __future__ import annotations

from typing import Any

from pydba.database._abstract import DatabaseAbstract


class Database(DatabaseAbstract):
    """Concrete Database facade with static connect factory."""

    @staticmethod
    def connect(driver: str, name: str, **kwargs: Any) -> Database:
        """Create a Database instance by driver name.

        Args:
            driver: 'sqlite', 'postgresql', or 'mysql'
            name: database name/path
            **kwargs: additional connection options

        Returns:
            Database instance
        """
        driver = driver.lower()

        if driver == "sqlite":
            return Database._connect_sqlite(name, **kwargs)
        elif driver == "postgresql":
            return Database._connect_postgres(name, **kwargs)
        elif driver == "mysql":
            return Database._connect_mysql(name, **kwargs)
        else:
            raise ValueError(f"Unsupported driver: {driver}. Supported: sqlite, postgresql, mysql")

    @staticmethod
    def _connect_sqlite(name: str, **kwargs: Any) -> Database:
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

        return Database(adapter, dialect)

    @staticmethod
    def _connect_postgres(name: str, **kwargs: Any) -> Database:
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

        return Database(adapter, dialect)

    @staticmethod
    def _connect_mysql(name: str, **kwargs: Any) -> Database:
        from pydba.adapters.mysql import MySQLAdapter
        from pydba.dialects.mysql import MySQLDialect

        options = kwargs.pop("options", {})
        startup_queries = kwargs.pop("startup_queries", [])
        debug_callback = kwargs.pop("debug_callback", None)

        adapter = MySQLAdapter(
            database_name=name,
            options=options,
            startup_queries=startup_queries,
            debug_callback=debug_callback,
            **kwargs,
        )

        version = adapter.version()
        dialect = MySQLDialect(version=version, options=options)

        return Database(adapter, dialect)

    @staticmethod
    def drivers() -> list[str]:
        return ["sqlite", "postgresql", "mysql"]
