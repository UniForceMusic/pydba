from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from pydba.query.enums.type import TypeEnum

if TYPE_CHECKING:
    from pydba._query_with_params import QueryWithParams
    from pydba.query._on_conflict import OnConflict


def _parse_version(version: str) -> int:
    """Parse version string to integer for comparison.

    '15.2' -> 150200 (major*100^2 + minor*100 + patch)
    """
    parts = version.split(".")
    major = int(parts[0]) if len(parts) > 0 else 0
    minor = int(parts[1]) if len(parts) > 1 else 0
    patch = int(parts[2]) if len(parts) > 2 else 0
    return major * 10000 + minor * 100 + patch


class DialectABC(ABC):
    """Abstract base class for SQL dialects."""

    # --- DML: SELECT, INSERT, UPDATE, DELETE ---

    @abstractmethod
    def select(
        self,
        distinct: list[str] | None,
        columns: list[Any] | None,
        table: Any,
        joins: list[Any] | None,
        where: list[Any] | None,
        group_by: list[str] | None,
        having: list[Any] | None,
        order_by: list[Any] | None,
        limit: int | None,
        offset: int | None,
        unions: list[Any] | None,
    ) -> QueryWithParams:
        """Build a SELECT query."""
        ...

    @abstractmethod
    def insert(
        self,
        table: Any,
        values: list[dict[str, Any]],
        on_conflict: OnConflict | None,
        returning: list[str] | None,
        last_insert_id: str | None,
    ) -> QueryWithParams:
        """Build an INSERT query."""
        ...

    @abstractmethod
    def update(
        self,
        table: Any,
        updates: dict[str, Any],
        where: list[Any] | None,
        returning: list[str] | None,
    ) -> QueryWithParams:
        """Build an UPDATE query."""
        ...

    @abstractmethod
    def delete(
        self,
        table: Any,
        where: list[Any] | None,
        returning: list[str] | None,
    ) -> QueryWithParams:
        """Build a DELETE query."""
        ...

    # --- DDL: CREATE, ALTER, DROP TABLE ---

    @abstractmethod
    def create_table(
        self,
        if_not_exists: bool,
        table: Any,
        columns: list[dict[str, Any]],
        primary_keys: list[str] | None,
        constraints: list[dict[str, Any]] | None,
    ) -> QueryWithParams:
        """Build a CREATE TABLE query."""
        ...

    @abstractmethod
    def alter_table(
        self,
        table: Any,
        alters: list[dict[str, Any]],
    ) -> list[QueryWithParams]:
        """Build ALTER TABLE queries. Returns a list since some alters may require multiple statements."""
        ...

    @abstractmethod
    def drop_table(
        self,
        if_exists: bool,
        table: Any,
    ) -> QueryWithParams:
        """Build a DROP TABLE query."""
        ...

    # --- Transactions ---

    @abstractmethod
    def begin_transaction(self) -> QueryWithParams:
        ...

    @abstractmethod
    def commit_transaction(self) -> QueryWithParams:
        ...

    @abstractmethod
    def rollback_transaction(self) -> QueryWithParams:
        ...

    # --- Savepoints ---

    @abstractmethod
    def begin_savepoint(self, name: str) -> QueryWithParams:
        ...

    @abstractmethod
    def commit_savepoint(self, name: str) -> QueryWithParams:
        ...

    @abstractmethod
    def rollback_savepoint(self, name: str) -> QueryWithParams:
        ...

    # --- Type coercion ---

    @abstractmethod
    def escape_identifier(self, identifier: str | list[str]) -> str:
        ...

    @abstractmethod
    def escape_string(self, string: str) -> str:
        ...

    @abstractmethod
    def cast_to_query(self, value: Any) -> str:
        """Convert a Python value to a SQL-safe string representation."""
        ...

    @abstractmethod
    def cast_bool(self, value: bool) -> bool | int:
        ...

    @abstractmethod
    def cast_datetime(self, value: Any) -> str:
        ...

    @abstractmethod
    def parse_bool(self, value: Any) -> bool:
        ...

    @abstractmethod
    def parse_datetime(self, value: Any) -> Any:
        ...

    @abstractmethod
    def type(self, type_enum: TypeEnum, bits: int | None = None) -> str:
        """Return the SQL type name for a given TypeEnum."""
        ...

    # --- Capability flags ---

    # Capability attributes are set as instance attributes in SQLDialect.__init__:
    # bool, distinct_on, on_conflict, returning, lateral, savepoints,
    # generated_by_default_as_identity, escape_identifier_char,
    # escape_string_char, escape_ansi, datetime_format


class DialectAbstract(DialectABC):
    """Abstract base implementation for dialects with common version/option scaffolding."""

    def __init__(self, version: str = "0", options: dict[str, Any] | None = None) -> None:
        self._version_str = version
        self._version = self._parse_version(version)
        self._options = options or {}

    @staticmethod
    def _parse_version(version: str) -> int:
        """Parse version string to integer for comparison.

        '15.2' -> 150200 (major*100^2 + minor*100 + patch)
        """
        parts = version.split(".")
        major = int(parts[0]) if len(parts) > 0 else 0
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0
        return major * 10000 + minor * 100 + patch

    @property
    def version(self) -> str:
        """Return the raw version string."""
        return self._version_str

    @property
    def version_int(self) -> int:
        """Return the parsed version as a comparable integer."""
        return self._version

    @property
    def options(self) -> dict[str, Any]:
        """Return a shallow copy of the dialect options."""
        return dict(self._options)

    def option(self, key: str, default: Any = None) -> Any:
        """Return a specific option value, falling back to *default*."""
        return self._options.get(key, default)
