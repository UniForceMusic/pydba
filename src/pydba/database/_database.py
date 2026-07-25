from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydba.database._abstract import DatabaseAbstract


class Database(DatabaseAbstract):
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
    def _connect(
        adapter_cls: type,
        dialect_cls: type,
        name: str,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        socket_info: dict[str, Any] | None = None,
        startup_queries: list[str] | None = None,
        options: dict[str, Any] | None = None,
        debug_callback: Callable[[str, float, str | None], None] | None = None,
    ) -> Database:
        kwargs: dict[str, Any] = {
            "database_name": name,
            "options": options or {},
            "startup_queries": startup_queries or [],
            "debug_callback": debug_callback,
        }
        if host is not None:
            kwargs["host"] = host
        if port is not None:
            kwargs["port"] = port
        if user is not None:
            kwargs["user"] = user
        if password is not None:
            kwargs["password"] = password
        if socket_info is not None:
            kwargs["socket_info"] = socket_info

        adapter = adapter_cls(**kwargs)
        return Database(adapter, dialect_cls(version=adapter.version(), options=options or {}))

    @staticmethod
    def _connect_sqlite(
        name: str,
        socket_info: dict[str, Any] | None = None,
        startup_queries: list[str] | None = None,
        options: dict[str, Any] | None = None,
        debug_callback: Callable[[str, float, str | None], None] | None = None,
    ) -> Database:
        from pydba.adapters.sqlite import SQLiteAdapter
        from pydba.dialects.sqlite import SQLiteDialect
        return Database._connect(
            SQLiteAdapter, SQLiteDialect, name,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )

    @staticmethod
    def _connect_postgres(
        name: str,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "",
        socket_info: dict[str, Any] | None = None,
        startup_queries: list[str] | None = None,
        options: dict[str, Any] | None = None,
        debug_callback: Callable[[str, float, str | None], None] | None = None,
    ) -> Database:
        from pydba.adapters.postgres import PsycopgAdapter
        from pydba.dialects.postgres import PostgresqlDialect
        return Database._connect(
            PsycopgAdapter, PostgresqlDialect, name,
            host=host, port=port, user=user, password=password,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )

    @staticmethod
    def _connect_mysql(
        name: str,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        socket_info: dict[str, Any] | None = None,
        startup_queries: list[str] | None = None,
        options: dict[str, Any] | None = None,
        debug_callback: Callable[[str, float, str | None], None] | None = None,
    ) -> Database:
        from pydba.adapters.mysql import MySQLAdapter
        from pydba.dialects.mysql import MySQLDialect
        return Database._connect(
            MySQLAdapter, MySQLDialect, name,
            host=host, port=port, user=user, password=password,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )

    @staticmethod
    def drivers() -> list[str]:
        return ["sqlite", "postgresql", "mysql"]
