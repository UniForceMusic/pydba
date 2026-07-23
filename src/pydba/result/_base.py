from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


def _row_to_object(row: dict, cls: type, constructor_args: list) -> object | dict:
    if cls is dict or cls is None:
        return dict(row)
    obj = cls(*constructor_args)
    obj.__dict__.update(row)
    return obj


class ResultABC(ABC):
    """Abstract base class for query results."""
    
    @abstractmethod
    def columns(self) -> dict[str, str]:
        """Return column name -> type mapping."""
        ...
    
    @abstractmethod
    def scalar(self, column: Optional[str] = None) -> Any:
        """Return a single scalar value."""
        ...
    
    @abstractmethod
    def fetch_object(self, cls: type = dict, constructor_args: Optional[list] = None) -> Optional[object | dict]:
        """Fetch next row as an object."""
        ...
    
    @abstractmethod
    def fetch_objects(self, cls: type = dict, constructor_args: Optional[list] = None) -> list:
        """Fetch all rows as objects."""
        ...
    
    @abstractmethod
    def fetch_dict(self) -> Optional[dict]:
        """Fetch next row as a dict."""
        ...

    @abstractmethod
    def fetch_dicts(self) -> list[dict]:
        """Fetch all rows as dicts."""
        ...


class ResultAbstract(ResultABC):
    """Abstract base implementation that derives scalar/fetch_object/fetch_objects
    from fetch_dict/fetch_dicts."""

    def scalar(self, column: Optional[str] = None) -> Any:
        row = self.fetch_dict()
        if row is None:
            return None
        if column is not None:
            return row.get(column)
        # Return first value
        for val in row.values():
            return val
        return None

    def fetch_object(self, cls: type = dict, constructor_args: Optional[list] = None) -> Optional[object | dict]:
        row = self.fetch_dict()
        if row is None:
            return None
        return _row_to_object(row, cls, constructor_args or [])

    def fetch_objects(self, cls: type = dict, constructor_args: Optional[list] = None) -> list:
        rows = self.fetch_dicts()
        return [_row_to_object(row, cls, constructor_args or []) for row in rows]

    # --- Concrete implementations for database-backed results ---
    # Subclasses must implement:
    #   def columns(self) -> dict[str, str]:
    #   def fetch_dict(self) -> Optional[dict]:
    #   def fetch_dicts(self) -> list[dict]:
