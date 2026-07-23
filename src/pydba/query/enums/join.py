"""Join types for SQL JOIN clauses."""

from enum import StrEnum


class JoinEnum(StrEnum):
    """Enumeration of SQL join types used in FROM and JOIN clauses."""

    LEFT_JOIN = 'LEFT JOIN'
    LEFT_JOIN_LATERAL = 'LEFT JOIN LATERAL'
    INNER_JOIN = 'INNER JOIN'
    INNER_JOIN_LATERAL = 'INNER JOIN LATERAL'
    CROSS_JOIN = 'CROSS JOIN'
    CROSS_JOIN_LATERAL = 'CROSS JOIN LATERAL'
