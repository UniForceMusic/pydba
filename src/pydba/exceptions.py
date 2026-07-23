"""Custom exception hierarchy for pydba."""

from __future__ import annotations


class DatabaseError(Exception):
    """Base error for all pydba exceptions."""


class AdapterError(DatabaseError):
    """Raised when an adapter-level error occurs."""


class DriverError(DatabaseError):
    """Raised when a driver or connection error occurs."""


class QueryError(DatabaseError):
    """Raised when a query building error occurs."""


class QueryWithParamsError(DatabaseError):
    """Raised when a parameterized query error occurs."""
