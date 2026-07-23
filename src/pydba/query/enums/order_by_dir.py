"""Sort direction for SQL ORDER BY clauses."""

from enum import StrEnum


class OrderByDirectionEnum(StrEnum):
    """Enumeration of sort directions used in ORDER BY clauses."""

    ASC = 'ASC'
    DESC = 'DESC'
