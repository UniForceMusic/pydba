"""Data type identifiers for SQL column definitions."""

from enum import Enum


class TypeEnum(Enum):
    """Enumeration of supported SQL data types."""

    BOOL = 1
    INT = 2
    FLOAT = 3
    STRING = 4
    DATETIME = 5
