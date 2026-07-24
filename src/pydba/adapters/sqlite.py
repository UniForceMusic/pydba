from __future__ import annotations

import sqlite3
import time
from typing import Any, Callable, Optional

from pydba._query_with_params import QueryWithParams
from pydba.adapters._base import AdapterAbstract
from pydba.dialects._base import DialectABC
from pydba.result._base import ResultABC
from pydba.result.sqlite import SQLite3Result


class SQLiteAdapter(AdapterAbstract):
    """SQLite adapter wrapping sqlite3.Connection."""

    def __init__(
        self,
        database_name: str = ":memory:",
        socket_info: Optional[dict[str, Any]] = None,
        startup_queries: Optional[list[str]] = None,
        options: Optional[dict[str, Any]] = None,
        debug_callback: Optional[Callable[[str, float, Optional[str]], None]] = None,
    ) -> None:
        super().__init__(
            driver_name="sqlite",
            database_name=database_name,
            socket_info=socket_info,
            startup_queries=startup_queries,
            options=options,
            debug_callback=debug_callback,
        )
        self._connection: Optional[sqlite3.Connection] = None
        self._connect()

    def _connect(self) -> None:
        db_name = self._database_name
        read_only = self._options.get("read_only", False)
        
        if read_only:
            # sqlite3 doesn't support read-only natively in Python's stdlib
            # We use URI mode
            uri = f"file:{db_name}?mode=ro"
            self._connection = sqlite3.connect(uri, uri=True)
        else:
            self._connection = sqlite3.connect(db_name)

        # Configure connection
        self._connection.row_factory = sqlite3.Row
        
        # Set PRAGMAs from options
        pragmas = {
            "busy_timeout": self._options.get("busy_timeout", 5000),
            "encoding": self._options.get("encoding", "UTF-8"),
            "journal_mode": self._options.get("journal_mode", "WAL"),
            "foreign_keys": self._options.get("foreign_keys", 1),
        }
        for key, value in pragmas.items():
            try:
                self._connection.execute(f"PRAGMA {key} = {value}")
            except sqlite3.Error:
                pass  # Ignore pragma failures

        # Handle encryption key if provided
        enc_key = self._options.get("encryption_key")
        if enc_key:
            self._connection.execute(f"PRAGMA key = '{enc_key}'")

        # Register REGEXP function
        self._connection.create_function("REGEXP", 2, _regexp_fn)

        # Execute startup queries
        self._exec_startup_queries()

    def version(self) -> str:
        if self._connection is None:
            return "0"
        try:
            cursor = self._connection.execute("SELECT sqlite_version()")
            row = cursor.fetchone()
            return str(row[0]) if row else "0"
        except sqlite3.Error:
            return "0"

    def exec(self, query: str) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
        start = time.time()
        error: Optional[str] = None
        try:
            self._connection.execute(query)
            self._connection.commit()
        except sqlite3.Error as e:
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
            return SQLite3Result(cursor)
        except sqlite3.Error as e:
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
                # Emulate by interpolating params into SQL
                sql_full = query_with_params.to_sql(dialect)
                cursor = self._connection.execute(sql_full)
            else:
                cursor = self._connection.execute(sql, params)
            return SQLite3Result(cursor)
        except sqlite3.Error as e:
            error = str(e)
            raise
        finally:
            duration = time.time() - start
            self._debug(query_with_params.to_sql(dialect), duration, error)

    def begin_transaction(self) -> None:
        if self._connection is None:
            raise RuntimeError("Connection is not established")
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
        return self._connection.in_transaction

    def last_insert_id(self, name: Optional[str] = None) -> Optional[int | str]:
        if self._connection is None:
            return None
        cursor = self._connection.execute("SELECT last_insert_rowid()")
        row = cursor.fetchone()
        return row[0] if row else None

    def close(self) -> None:
        if self._connection is not None:
            self._connection.close()
            self._connection = None


def _regexp_fn(pattern: str, value: str) -> int:
    """REGEXP function for SQLite."""
    import re
    try:
        return 1 if re.search(pattern, str(value)) else 0
    except re.error:
        return 0
