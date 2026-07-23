"""Logical chain operators for combining conditions in SQL queries."""

from enum import StrEnum


class ChainEnum(StrEnum):
    """Enumeration of logical chain operators used to combine multiple conditions."""

    AND = 'AND'
    OR = 'OR'
