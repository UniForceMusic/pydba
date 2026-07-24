from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Optional, Self

from pydba.query.enums.chain import ChainEnum
from pydba.query._condition import Condition
from pydba.query.enums.condition import ConditionEnum


class ConditionGroupABC(ABC):
    """Abstract base class for groups of conditions (WHERE/Having groups)."""

    @property
    @abstractmethod
    def chain(self) -> ChainEnum:
        ...

    @property
    @abstractmethod
    def not_(self) -> bool:
        ...

    @property
    @abstractmethod
    def conditions(self) -> list[Condition | ConditionGroupABC]:
        ...


class _ConditionGroupMixin:
    """Mixin providing fluent condition methods for condition groups."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_conditions'):
            self._conditions: list[Condition | ConditionGroupABC] = []

    def _add(self, cond_enum: ConditionEnum, column: Any, value: Any, chain: ChainEnum = ChainEnum.AND) -> None:
        self._conditions.append(Condition(condition=cond_enum, identifier=column, value=value, chain=chain))

    # --- equals ---
    def where_equals(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.EQUALS, column, value)
        return self

    def or_where_equals(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.EQUALS, column, value, chain=ChainEnum.OR)
        return self

    def where_not_equals(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.NOT_EQUALS, column, value)
        return self

    def or_where_not_equals(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.NOT_EQUALS, column, value, chain=ChainEnum.OR)
        return self

    # --- is null ---
    def where_is_null(self, column: Any) -> Self:
        self._add(ConditionEnum.EQUALS, column, None)
        return self

    def or_where_is_null(self, column: Any) -> Self:
        self._add(ConditionEnum.EQUALS, column, None, chain=ChainEnum.OR)
        return self

    def where_is_not_null(self, column: Any) -> Self:
        self._add(ConditionEnum.NOT_EQUALS, column, None)
        return self

    def or_where_is_not_null(self, column: Any) -> Self:
        self._add(ConditionEnum.NOT_EQUALS, column, None, chain=ChainEnum.OR)
        return self

    # --- like ---
    def where_like(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.LIKE, column, value)
        return self

    def or_where_like(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.LIKE, column, value, chain=ChainEnum.OR)
        return self

    def where_not_like(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.NOT_LIKE, column, value)
        return self

    def or_where_not_like(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.NOT_LIKE, column, value, chain=ChainEnum.OR)
        return self

    # --- in ---
    def where_in(self, column: Any, values: list) -> Self:
        self._add(ConditionEnum.IN, column, values)
        return self

    def or_where_in(self, column: Any, values: list) -> Self:
        self._add(ConditionEnum.IN, column, values, chain=ChainEnum.OR)
        return self

    def where_not_in(self, column: Any, values: list) -> Self:
        self._add(ConditionEnum.NOT_IN, column, values)
        return self

    def or_where_not_in(self, column: Any, values: list) -> Self:
        self._add(ConditionEnum.NOT_IN, column, values, chain=ChainEnum.OR)
        return self

    # --- less/greater ---
    def where_less_than(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.LESS_THAN, column, value)
        return self

    def or_where_less_than(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.LESS_THAN, column, value, chain=ChainEnum.OR)
        return self

    def where_greater_than(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.GREATER_THAN, column, value)
        return self

    def or_where_greater_than(self, column: Any, value: Any) -> Self:
        self._add(ConditionEnum.GREATER_THAN, column, value, chain=ChainEnum.OR)
        return self

    # --- between ---
    def where_between(self, column: Any, min_val: Any, max_val: Any) -> Self:
        self._add(ConditionEnum.BETWEEN, column, [min_val, max_val])
        return self

    def or_where_between(self, column: Any, min_val: Any, max_val: Any) -> Self:
        self._add(ConditionEnum.BETWEEN, column, [min_val, max_val], chain=ChainEnum.OR)
        return self

    # --- group (nested) ---
    def where_group(self, callback: Callable) -> Self:
        group = WhereGroup()
        callback(group)
        self._conditions.append(group)
        return self

    def or_where_group(self, callback: Callable) -> Self:
        group = WhereGroup(chain=ChainEnum.OR)
        callback(group)
        self._conditions.append(group)
        return self


class WhereGroup(ConditionGroupABC, _ConditionGroupMixin):
    """A group of WHERE conditions that can be nested."""

    def __init__(self, chain: ChainEnum = ChainEnum.AND, not_: bool = False) -> None:
        self._chain = chain
        self._not = not_
        self._conditions: list[Condition | ConditionGroupABC] = []

    @property
    def chain(self) -> ChainEnum:
        return self._chain

    @property
    def not_(self) -> bool:
        return self._not

    @property
    def conditions(self) -> list[Condition | ConditionGroupABC]:
        return list(self._conditions)

    def add_condition(self, condition: Condition | ConditionGroupABC) -> None:
        self._conditions.append(condition)


class HavingGroup(ConditionGroupABC, _ConditionGroupMixin):
    """A group of HAVING conditions that can be nested."""

    def __init__(self, chain: ChainEnum = ChainEnum.AND, not_: bool = False) -> None:
        self._chain = chain
        self._not = not_
        self._conditions: list[Condition | ConditionGroupABC] = []

    @property
    def chain(self) -> ChainEnum:
        return self._chain

    @property
    def not_(self) -> bool:
        return self._not

    @property
    def conditions(self) -> list[Condition | ConditionGroupABC]:
        return list(self._conditions)

    def add_condition(self, condition: Condition | ConditionGroupABC) -> None:
        self._conditions.append(condition)
