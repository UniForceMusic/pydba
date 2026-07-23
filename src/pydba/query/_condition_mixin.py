from __future__ import annotations

import re
from typing import Any, Callable, Optional
from pydba.query.enums.condition import ConditionEnum
from pydba.query.enums.chain import ChainEnum
from pydba.query._condition import Condition
from pydba.query._condition_group import ConditionGroupABC, WhereGroup


def _escape_like_chars(string: str, escape_backslash: bool = False) -> str:
    result = string.replace("%", "\\%").replace("_", "\\_")
    if escape_backslash:
        result = result.replace("\\", "\\\\")
    return result


class ConditionMixin:
    """Mixin providing protected condition-building helper methods."""

    def _equals(self, conditions: list, column: Any, value: Any, cast: bool = False, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.EQUALS, column, value, chain)

    def _not_equals(self, conditions: list, column: Any, value: Any, cast: bool = False, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.NOT_EQUALS, column, value, chain)

    def _is_null(self, conditions: list, column: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.EQUALS, column, None, chain)

    def _is_not_null(self, conditions: list, column: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.NOT_EQUALS, column, None, chain)

    def _like(self, conditions: list, column: Any, value: Any, case_insensitive: bool = False, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.LIKE, column, value, chain)

    def _not_like(self, conditions: list, column: Any, value: Any, case_insensitive: bool = False, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.NOT_LIKE, column, value, chain)

    def _starts_with(self, conditions: list, column: Any, value: Any, case_insensitive: bool = False, escape_backslash: bool = False, chain: ChainEnum = ChainEnum.AND) -> Condition:
        val = _escape_like_chars(str(value), escape_backslash)
        return self._add_condition(conditions, ConditionEnum.LIKE, column, f"{val}%", chain)

    def _ends_with(self, conditions: list, column: Any, value: Any, case_insensitive: bool = False, escape_backslash: bool = False, chain: ChainEnum = ChainEnum.AND) -> Condition:
        val = _escape_like_chars(str(value), escape_backslash)
        return self._add_condition(conditions, ConditionEnum.LIKE, column, f"%{val}", chain)

    def _contains(self, conditions: list, column: Any, value: Any, case_insensitive: bool = False, escape_backslash: bool = False, chain: ChainEnum = ChainEnum.AND) -> Condition:
        val = _escape_like_chars(str(value), escape_backslash)
        return self._add_condition(conditions, ConditionEnum.LIKE, column, f"%{val}%", chain)

    def _not_contains(self, conditions: list, column: Any, value: Any, case_insensitive: bool = False, escape_backslash: bool = False, chain: ChainEnum = ChainEnum.AND) -> Condition:
        val = _escape_like_chars(str(value), escape_backslash)
        return self._add_condition(conditions, ConditionEnum.NOT_LIKE, column, f"%{val}%", chain)

    def _glob(self, conditions: list, column: Any, value: Any, case_insensitive: bool = False, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.GLOB, column, value, chain)

    def _not_glob(self, conditions: list, column: Any, value: Any, case_insensitive: bool = False, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.NOT_GLOB, column, value, chain)

    def _in(self, conditions: list, column: Any, values: list, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.IN, column, values, chain)

    def _not_in(self, conditions: list, column: Any, values: list, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.NOT_IN, column, values, chain)

    def _less_than(self, conditions: list, column: Any, value: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.LESS_THAN, column, value, chain)

    def _less_than_or_equals(self, conditions: list, column: Any, value: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.LESS_THAN_OR_EQUALS, column, value, chain)

    def _greater_than(self, conditions: list, column: Any, value: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.GREATER_THAN, column, value, chain)

    def _greater_than_or_equals(self, conditions: list, column: Any, value: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.GREATER_THAN_OR_EQUALS, column, value, chain)

    def _between(self, conditions: list, column: Any, min_val: Any, max_val: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.BETWEEN, column, [min_val, max_val], chain)

    def _not_between(self, conditions: list, column: Any, min_val: Any, max_val: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.NOT_BETWEEN, column, [min_val, max_val], chain)

    def _empty(self, conditions: list, column: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        """Check if column is empty (empty string or null)."""
        return self._add_condition(conditions, ConditionEnum.EQUALS, column, "", chain)

    def _not_empty(self, conditions: list, column: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        """Check if column is not empty (not empty string and not null)."""
        return self._add_condition(conditions, ConditionEnum.NOT_EQUALS, column, "", chain)

    def _regex(self, conditions: list, column: Any, pattern: Any, flags: Any = None, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.REGEX, column, pattern, chain)

    def _not_regex(self, conditions: list, column: Any, pattern: Any, flags: Any = None, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.NOT_REGEX, column, pattern, chain)

    def _exists(self, conditions: list, select_query: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.EXISTS, None, select_query, chain)

    def _not_exists(self, conditions: list, select_query: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, ConditionEnum.NOT_EXISTS, None, select_query, chain)

    def _group(self, conditions: list, callback: Callable, not_: bool = False, group_class: type | None = None, chain: ChainEnum = ChainEnum.AND) -> ConditionGroupABC:
        if group_class is None:
            group_class = WhereGroup
        group = group_class(chain=chain, not_=not_)
        result = callback(group)
        if result is not None:
            group = result
        self._add_condition_group(conditions, group)
        return group

    def _operator(self, conditions: list, column: Any, operator: str, value: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        return self._add_condition(conditions, operator, column, value, chain)

    def _add_condition(self, conditions: list, condition: Any, identifier: Any, value: Any, chain: ChainEnum = ChainEnum.AND) -> Condition:
        cond = Condition(condition=condition, identifier=identifier, value=value, chain=chain)
        conditions.append(cond)
        return cond

    def _add_condition_group(self, conditions: list, group: Any) -> None:
        conditions.append(group)

    def _add_raw_condition(self, conditions: list, sql: str, values: list | None = None, chain: ChainEnum = ChainEnum.AND) -> Condition:
        from pydba.query.expressions.expression import Expression
        if values:
            cond = Condition(condition=ConditionEnum.RAW, identifier=None, value=Expression(sql, values), chain=chain)
        else:
            from pydba.query.expressions.raw import Raw
            cond = Condition(condition=ConditionEnum.RAW, identifier=None, value=Raw(sql), chain=chain)
        conditions.append(cond)
        return cond

    
