from __future__ import annotations

from collections.abc import Callable
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
    ) -> DB:
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
        return DB(adapter, dialect_cls(version=adapter.version(), options=options or {}))

    @staticmethod
    def connect_sqlite(
        name: str,
        socket_info: dict[str, Any] | None = None,
        startup_queries: list[str] | None = None,
        options: dict[str, Any] | None = None,
        debug_callback: Callable[[str, float, str | None], None] | None = None,
    ) -> DB:
        """Connect to a SQLite database.

        Args:
            name: Database file path or ":memory:".
            socket_info: Unix socket info (not used by SQLite).
            startup_queries: Queries to run after connecting.
            options: Connection options (e.g. read_only, busy_timeout, journal_mode).
            debug_callback: Callback for debug logging.

        Returns:
            DB instance.
        """
        from pydba.adapters.sqlite import SQLiteAdapter
        from pydba.dialects.sqlite import SQLiteDialect
        return DB._connect(
            SQLiteAdapter, SQLiteDialect, name,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )

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
        """Connect to a PostgreSQL database.

        Args:
            name: Database name.
            host: Server hostname.
            port: Server port.
            user: Username.
            password: Password.
            socket_info: Unix socket info.
            startup_queries: Queries to run after connecting.
            options: Connection options (e.g. sslmode, search_path).
            debug_callback: Callback for debug logging.

        Returns:
            DB instance.
        """
        from pydba.adapters.postgres import PsycopgAdapter
        from pydba.dialects.postgres import PostgresqlDialect
        return DB._connect(
            PsycopgAdapter, PostgresqlDialect, name,
            host=host, port=port, user=user, password=password,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )

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
        """Connect to a MySQL database.

        Args:
            name: Database name.
            host: Server hostname.
            port: Server port.
            user: Username.
            password: Password.
            socket_info: Unix socket info.
            startup_queries: Queries to run after connecting.
            options: Connection options (e.g. ssl_mode, connect_timeout, charset).
            debug_callback: Callback for debug logging.

        Returns:
            DB instance.
        """
        from pydba.adapters.mysql import MySQLAdapter
        from pydba.dialects.mysql import MySQLDialect
        return DB._connect(
            MySQLAdapter, MySQLDialect, name,
            host=host, port=port, user=user, password=password,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )