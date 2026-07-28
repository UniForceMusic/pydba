from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sentiencedb.database._abc import DatabaseABC


class Database(DatabaseABC):
    @classmethod
    def connect_sqlite(
        cls,
        name: str,
        socket_info: dict[str, Any] | None = None,
        startup_queries: list[str] | None = None,
        options: dict[str, Any] | None = None,
        debug_callback: Callable[[str, float, str | None], None] | None = None,
    ) -> Database:
        from sentiencedb.adapters.sqlite import SQLiteAdapter
        from sentiencedb.dialects.sqlite import SQLiteDialect

        adapter = SQLiteAdapter(
            database_name=name,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )
        return cls(adapter, SQLiteDialect(version=adapter.version(), options=options or {}))

    @classmethod
    def connect_postgresql(
        cls,
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
        from sentiencedb.adapters.postgres import PsycopgAdapter
        from sentiencedb.dialects.postgres import PostgresqlDialect

        adapter = PsycopgAdapter(
            database_name=name,
            host=host,
            port=port,
            user=user,
            password=password,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )
        return cls(adapter, PostgresqlDialect(version=adapter.version(), options=options or {}))

    @classmethod
    def connect_mysql(
        cls,
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
        from sentiencedb.adapters.mysql import MySQLAdapter
        from sentiencedb.dialects.mysql import MySQLDialect

        adapter = MySQLAdapter(
            database_name=name,
            host=host,
            port=port,
            user=user,
            password=password,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )
        return cls(adapter, MySQLDialect(version=adapter.version(), options=options or {}))

    @classmethod
    def connect_mariadb(
        cls,
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
        from sentiencedb.adapters.mysql import MySQLAdapter
        from sentiencedb.dialects.mysql import MySQLDialect

        adapter = MySQLAdapter(
            database_name=name,
            host=host,
            port=port,
            user=user,
            password=password,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )
        return cls(adapter, MySQLDialect(version=adapter.version(), options=options or {}, is_mariadb=True))

    @classmethod
    def drivers(cls) -> list[str]:
        return ["sqlite", "postgresql", "mysql"]
