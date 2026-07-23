"""Set operators for combining result sets in SQL queries."""

from enum import StrEnum


class UnionEnum(StrEnum):
    """Enumeration of SQL set operators used to combine multiple SELECT statements."""

    UNION = 'UNION'
    UNION_ALL = 'UNION ALL'
