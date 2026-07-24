from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


def _row_to_object(row: dict[str, Any], cls: type, constructor_args: list[Any]) -> object | dict[str, Any]:
    if cls is dict or cls is None:
        return dict(row)
    obj = cls(*constructor_args)
    obj.__dict__.update(row)
    return obj  # type: ignore[no-any-return]


class ResultABC(ABC):
    """Abstract base class for query results."""
    
    @abstractmethod
    def columns(self) -> dict[str, str]:
        """Return column name -> type mapping."""
        ...
    
    @abstractmethod
    def scalar(self, column: str | None = None) -> Any:
        """Return a single scalar value."""
        ...
    
    @abstractmethod
    def fetch_object(self, cls: type = dict, constructor_args: list[Any] | None = None) -> object | dict[str, Any] | None:
        """Fetch next row as an object."""
        ...
    
    @abstractmethod
    def fetch_objects(self, cls: type = dict, constructor_args: list[Any] | None = None) -> list[object | dict[str, Any]]:
        """Fetch all rows as objects."""
        ...
    
    @abstractmethod
    def fetch_dict(self) -> dict[str, Any] | None:
        """Fetch next row as a dict."""
        ...

    @abstractmethod
    def fetch_dicts(self) -> list[dict[str, Any]]:
        """Fetch all rows as dicts."""
        ...


class ResultAbstract(ResultABC):
    """Abstract base implementation that derives scalar/fetch_object/fetch_objects
    from fetch_dict/fetch_dicts."""

    def scalar(self, column: str | None = None) -> Any:
        row = self.fetch_dict()
        if row is None:
            return None
        if column is not None:
            return row.get(column)
        # Return first value
        for val in row.values():
            return val
        return None

    def fetch_object(self, cls: type = dict, constructor_args: list[Any] | None = None) -> object | dict[str, Any] | None:
        row = self.fetch_dict()
        if row is None:
            return None
        return _row_to_object(row, cls, constructor_args or [])

    def fetch_objects(self, cls: type = dict, constructor_args: list[Any] | None = None) -> list[object | dict[str, Any]]:
        rows = self.fetch_dicts()
        return [_row_to_object(row, cls, constructor_args or []) for row in rows]

    # --- Concrete implementations for database-backed results ---
    # Subclasses must implement:
    #   def columns(self) -> dict[str, str]:
    #   def fetch_dict(self) -> Optional[dict]:
    #   def fetch_dicts(self) -> list[dict]:
