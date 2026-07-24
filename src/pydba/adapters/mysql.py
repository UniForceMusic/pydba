from __future__ import annotations

import time
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pydba._query_with_params import QueryWithParams
from pydba.adapters._base import AdapterAbstract
from pydba.dialects._base import DialectABC
from pydba.result._base import ResultABC
from pydba.result.mysql import MySQLResult

if TYPE_CHECKING:
    pass


class MySQLAdapter(AdapterAbstract):
    """MySQL adapter wrapping mysql.connector.Connection."""

    def __init__(
        self,
        database_name: str,
        socket_info: dict[str, Any] | None = None,
        startup_queries: list[str] | None = None,
        options: dict[str, Any] | None = None,
        debug_callback: Callable[[str, float, str | None], None] | None = None,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
    ) -> None:
        super().__init__(
            driver_name="mysql",
            database_name=database_name,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._connection: Any = None
        self._connect()

    def _connect(self) -> None:
        import mysql.connector

        kwargs: dict[str, Any] = {
            "host": self._host,
            "port": self._port,
            "database": self._database_name,
            "user": self._user,
            "password": self._password,
        }

        # SSL options
        ssl_mode = self._options.get("ssl_mode")
        if ssl_mode:
            kwargs["ssl_mode"] = ssl_mode

        # Connection timeout
        connect_timeout = self._options.get("connect_timeout")
        if connect_timeout:
            kwargs["connect_timeout"] = connect_timeout

        # Charset
        charset = self._options.get("charset", "utf8mb4")
        kwargs["charset"] = charset

        self._connection = mysql.connector.connect(**kwargs)

        # Execute startup queries
        self._exec_startup_queries()

    def version(self) -> str:
        if self._connection is None:
            return "0"
        try:
            cursor = self._connection.execute("SELECT VERSION()")
            row = cursor.fetchone()
            if row:
                return str(row[0])
            return "0"
        except Exception:  # noqa: BLE001
            return "0"

    def exec(self, query: str) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        start = time.time()
        error: str | None = None
        try:
            cursor = self._connection.cursor()
            cursor.execute(query)
            self._connection.commit()
        except Exception as e:
            error = str(e)
            raise
        finally:
            duration = time.time() - start
            self._debug(query, duration, error)

    def query(self, query: str) -> ResultABC:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        start = time.time()
        error: str | None = None
        try:
            cursor = self._connection.cursor()
            cursor.execute(query)
            return MySQLResult(cursor)
        except Exception as e:
            error = str(e)
            raise
        finally:
            duration = time.time() - start
            self._debug(query, duration, error)

    def query_with_params(
        self,
        dialect: DialectABC,
        query_with_params: QueryWithParams,
        emulate_prepare: bool = False,
    ) -> ResultABC:
        if self._connection is None:
            raise RuntimeError("Connection is not established")

        sql = query_with_params.query
        params = query_with_params.params

        start = time.time()
        error: str | None = None
        try:
            if emulate_prepare:
                # Emulate by interpolating params into SQL
                sql_full = query_with_params.to_sql(dialect)
                cursor = self._connection.cursor()
                cursor.execute(sql_full)
            else:
                # Convert ? placeholders to %s for mysql.connector
                sql_mysql = sql.replace("?", "%s")
                cursor = self._connection.cursor()
                cursor.execute(sql_mysql, params)
            return MySQLResult(cursor)
        except Exception as e:
            error = str(e)
            raise
        finally:
            duration = time.time() - start
            self._debug(query_with_params.to_sql(dialect), duration, error)

    def begin_transaction(self) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        self._connection.start_transaction()
        self._in_transaction = True

    def commit_transaction(self) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        self._connection.commit()
        self._in_transaction = False

    def rollback_transaction(self) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        self._connection.rollback()
        self._in_transaction = False

    def begin_savepoint(self, name: str) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        cursor = self._connection.cursor()
        cursor.execute(f"SAVEPOINT {name}")

    def commit_savepoint(self, name: str) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        cursor = self._connection.cursor()
        cursor.execute(f"RELEASE SAVEPOINT {name}")

    def rollback_savepoint(self, name: str) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        cursor = self._connection.cursor()
        cursor.execute(f"ROLLBACK TO SAVEPOINT {name}")

    @property
    def in_transaction(self) -> bool:
        if self._connection is None:
            return False
        return self._in_transaction

    def last_insert_id(self, name: str | None = None) -> int | str | None:
        if self._connection is None:
            return None
        cursor = self._connection.cursor()
        cursor.execute("SELECT LAST_INSERT_ID()")
        row = cursor.fetchone()
        return row[0] if row else None

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
