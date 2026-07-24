from __future__ import annotations

import time
from typing import Any, Callable, Optional

from pydba._query_with_params import QueryWithParams
from pydba.adapters._base import AdapterAbstract
from pydba.dialects._base import DialectABC
from pydba.result._base import ResultABC
from pydba.result.postgres import PsycopgResult


class PsycopgAdapter(AdapterAbstract):
    """PostgreSQL adapter wrapping psycopg.Connection."""

    def __init__(
        self,
        database_name: str,
        socket_info: Optional[dict[str, Any]] = None,
        startup_queries: Optional[list[str]] = None,
        options: Optional[dict[str, Any]] = None,
        debug_callback: Optional[Callable[[str, float, Optional[str]], None]] = None,
        host: str = "localhost",
        port: int = 5432,
        user: str = "postgres",
        password: str = "",
    ) -> None:
        super().__init__(
            driver_name="postgresql",
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
        import psycopg

        kwargs: dict[str, Any] = {
            "host": self._host,
            "port": self._port,
            "dbname": self._database_name,
            "user": self._user,
            "password": self._password,
        }

        # SSL options
        ssl_mode = self._options.get("sslmode")
        if ssl_mode:
            kwargs["sslmode"] = ssl_mode

        # Search path
        search_path = self._options.get("search_path")
        if search_path:
            kwargs["options"] = f"-c search_path={search_path}"

        self._connection = psycopg.connect(**kwargs)

        # Execute startup queries
        self._exec_startup_queries()

    def version(self) -> str:
        if self._connection is None:
            return "0"
        try:
            cursor = self._connection.execute("SELECT version()")
            row = cursor.fetchone()
            if row:
                # Parse "PostgreSQL 15.2 on ..." format
                version_str = str(row[0])
                # Extract version number
                import re
                match = re.search(r'(\d+\.\d+(?:\.\d+)?)', version_str)
                if match:
                    return match.group(1)
            return "0"
        except Exception:
            return "0"

    def exec(self, query: str) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        start = time.time()
        error: Optional[str] = None
        try:
            self._connection.execute(query)
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
        error: Optional[str] = None
        try:
            cursor = self._connection.execute(query)
            return PsycopgResult(cursor)
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
        error: Optional[str] = None
        try:
            if emulate_prepare:
                sql_full = query_with_params.to_sql(dialect)
                cursor = self._connection.execute(sql_full)
            else:
                cursor = self._connection.execute(sql, params)
            return PsycopgResult(cursor)
        except Exception as e:
            error = str(e)
            raise
        finally:
            duration = time.time() - start
            self._debug(query_with_params.to_sql(dialect), duration, error)

    def begin_transaction(self) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        # psycopg starts a transaction automatically when the first statement is executed
        # However, after a commit, we need to explicitly begin
        self._connection.execute("BEGIN TRANSACTION")
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
        self._connection.execute(f"SAVEPOINT {name}")

    def commit_savepoint(self, name: str) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        self._connection.execute(f"RELEASE SAVEPOINT {name}")

    def rollback_savepoint(self, name: str) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        self._connection.execute(f"ROLLBACK TO SAVEPOINT {name}")

    @property
    def in_transaction(self) -> bool:
        if self._connection is None:
            return False
        return self._connection.info.transaction_status is not None

    def last_insert_id(self, name: Optional[str] = None) -> Optional[int | str]:
        if self._connection is None:
            return None
        if name:
            cursor = self._connection.execute(f"SELECT currval('{name}')")
        else:
            cursor = self._connection.execute("SELECT lastval()")
        row = cursor.fetchone()
        return row[0] if row else None

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None
