from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pydba._query_with_params import QueryWithParams
    from pydba.dialects._base import DialectABC
    from pydba.result._base import ResultABC


class AdapterABC(ABC):
    """Abstract base class for database adapters."""
    
    @abstractmethod
    def version(self) -> str:
        """Return the database server version string."""
        ...
    
    @abstractmethod
    def exec(self, query: str) -> None:
        """Execute a query that returns no result set (e.g., INSERT, UPDATE, DELETE, DDL)."""
        ...
    
    @abstractmethod
    def query(self, query: str) -> ResultABC:
        """Execute a query and return a result set."""
        ...
    
    @abstractmethod
    def query_with_params(
        self,
        dialect: DialectABC,
        query_with_params: QueryWithParams,
        emulate_prepare: bool = False,
    ) -> ResultABC:
        """Execute a parameterized query and return a result set."""
        ...
    
    @abstractmethod
    def begin_transaction(self) -> None:
        ...
    
    @abstractmethod
    def commit_transaction(self) -> None:
        ...
    
    @abstractmethod
    def rollback_transaction(self) -> None:
        ...
    
    @abstractmethod
    def begin_savepoint(self, name: str) -> None:
        ...
    
    @abstractmethod
    def commit_savepoint(self, name: str) -> None:
        ...
    
    @abstractmethod
    def rollback_savepoint(self, name: str) -> None:
        ...
    
    @property
    @abstractmethod
    def in_transaction(self) -> bool:
        ...
    
    @abstractmethod
    def last_insert_id(self, name: str | None = None) -> int | str | None:
        ...


class AdapterAbstract(AdapterABC):
    """Abstract base implementation for adapters with common scaffolding."""
    
    def __init__(
        self,
        driver_name: str,
        database_name: str,
        socket_info: dict[str, Any] | None = None,
        startup_queries: list[str] | None = None,
        options: dict[str, Any] | None = None,
        debug_callback: Callable[[str, float, str | None], None] | None = None,
    ) -> None:
        self._driver_name = driver_name
        self._database_name = database_name
        self._socket_info = socket_info or {}
        self._startup_queries = startup_queries or []
        self._options = options or {}
        self._debug_callback = debug_callback
        self._in_transaction = False
    
    def _exec_startup_queries(self) -> None:
        """Execute any startup queries after connection is established."""
        for query in self._startup_queries:
            self.exec(query)
    
    def _debug(self, sql: str, duration: float, error: str | None = None) -> None:
        """Invoke debug callback if set."""
        if self._debug_callback is not None:
            self._debug_callback(sql, duration, error)
    
    @property
    def driver_name(self) -> str:
        return self._driver_name
    
    @property
    def database_name(self) -> str:
        return self._database_name
