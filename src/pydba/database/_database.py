from __future__ import annotations

from typing import Any

from pydba.database._abstract import DatabaseAbstract


class Database(DatabaseAbstract):
    """Concrete Database facade with static connect factory."""

    @staticmethod
    def connect(driver: str, name: str, **kwargs: Any) -> Database:
        driver = driver.lower()
        if driver == "sqlite":
            return Database._connect_sqlite(name, **kwargs)
        if driver == "postgresql":
            return Database._connect_postgres(name, **kwargs)
        if driver == "mysql":
            return Database._connect_mysql(name, **kwargs)
        raise ValueError(f"Unsupported driver: {driver}. Supported: sqlite, postgresql, mysql")

    @staticmethod
    def _connect_sqlite(name: str, **kwargs: Any) -> Database:
        from pydba.adapters.sqlite import SQLiteAdapter
        from pydba.dialects.sqlite import SQLiteDialect
        return Database._connect(SQLiteAdapter, SQLiteDialect, name, **kwargs)

    @staticmethod
    def _connect_postgres(name: str, **kwargs: Any) -> Database:
        from pydba.adapters.postgres import PsycopgAdapter
        from pydba.dialects.postgres import PgSQLDialect
        return Database._connect(PsycopgAdapter, PgSQLDialect, name, **kwargs)

    @staticmethod
    def _connect_mysql(name: str, **kwargs: Any) -> Database:
        from pydba.adapters.mysql import MySQLAdapter
        from pydba.dialects.mysql import MySQLDialect
        return Database._connect(MySQLAdapter, MySQLDialect, name, **kwargs)

    @staticmethod
    def _connect(adapter_cls: type, dialect_cls: type, name: str, **kwargs: Any) -> Database:

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
        return Database(adapter, dialect_cls(version=adapter.version(), options=options))

    @staticmethod
    def drivers() -> list[str]:
        return ["sqlite", "postgresql", "mysql"]
