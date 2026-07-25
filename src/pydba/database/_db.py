from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pydba.database._database import Database


class DB(Database):
    @staticmethod
    def connect_sqlite(
        name: str,
        socket_info: dict[str, Any] | None = None,
        startup_queries: list[str] | None = None,
        options: dict[str, Any] | None = None,
        debug_callback: Callable[[str, float, str | None], None] | None = None,
    ) -> DB:
        from pydba.adapters.sqlite import SQLiteAdapter
        from pydba.dialects.sqlite import SQLiteDialect

        adapter = SQLiteAdapter(
            database_name=name,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )
        return DB(adapter, SQLiteDialect(version=adapter.version(), options=options or {}))

    @staticmethod
    def connect_postgresql(
        name: str,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "",
        socket_info: dict[str, Any] | None = None,
        startup_queries: list[str] | None = None,
        options: dict[str, Any] | None = None,
        debug_callback: Callable[[str, float, str | None], None] | None = None,
    ) -> DB:
        from pydba.adapters.postgres import PsycopgAdapter
        from pydba.dialects.postgres import PostgresqlDialect

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
        return DB(adapter, PostgresqlDialect(version=adapter.version(), options=options or {}))

    @staticmethod
    def connect_mysql(
        name: str,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        socket_info: dict[str, Any] | None = None,
        startup_queries: list[str] | None = None,
        options: dict[str, Any] | None = None,
        debug_callback: Callable[[str, float, str | None], None] | None = None,
    ) -> DB:
        from pydba.adapters.mysql import MySQLAdapter
        from pydba.dialects.mysql import MySQLDialect

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
        return DB(adapter, MySQLDialect(version=adapter.version(), options=options or {}))