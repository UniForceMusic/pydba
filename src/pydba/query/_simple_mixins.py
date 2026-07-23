from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional, Self
from pydba.query.enums.order_by_dir import OrderByDirectionEnum
from pydba.query._order_by import OrderBy
from pydba.query._union import Union
from pydba.query._on_conflict import OnConflict

if TYPE_CHECKING:
    from pydba.query.select import SelectQuery


class ColumnsMixin:
    """Mixin providing columns() fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_columns_list'):
            self._columns_list: Optional[list] = None

    def columns(self, cols: list) -> Self:
        self._columns_list = cols
        return self


class DistinctMixin:
    """Mixin providing distinct() fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_distinct'):
            self._distinct: Optional[list] = None

    def distinct(self, on: Optional[list] = None) -> Self:
        self._distinct = on if on is not None else []
        return self


class GroupByMixin:
    """Mixin providing group_by() fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_group_by_cols'):
            self._group_by_cols: Optional[list] = None

    def group_by(self, columns: list) -> Self:
        self._group_by_cols = columns
        return self


class OrderByMixin:
    """Mixin providing order_by_asc/desc fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_order_by_list'):
            self._order_by_list: Optional[list] = None

    def order_by_asc(self, column: str) -> Self:
        if self._order_by_list is None:
            self._order_by_list = []
        self._order_by_list.append(OrderBy(column=column, direction=OrderByDirectionEnum.ASC))
        return self

    def order_by_desc(self, column: str) -> Self:
        if self._order_by_list is None:
            self._order_by_list = []
        self._order_by_list.append(OrderBy(column=column, direction=OrderByDirectionEnum.DESC))
        return self


class LimitMixin:
    """Mixin providing limit() fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_limit_val'):
            self._limit_val: Optional[int] = None

    def limit(self, limit: int) -> Self:
        self._limit_val = limit
        return self


class OffsetMixin:
    """Mixin providing offset() fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_offset_val'):
            self._offset_val: Optional[int] = None

    def offset(self, offset: int) -> Self:
        self._offset_val = offset
        return self


class UnionMixin:
    """Mixin providing union/union_all fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_unions_list'):
            self._unions_list: Optional[list] = None

    def union(self, select_query: SelectQuery) -> Self:
        from pydba.query.enums.union import UnionEnum
        if self._unions_list is None:
            self._unions_list = []
        self._unions_list.append(Union(union=UnionEnum.UNION, select_query=select_query))
        return self

    def union_all(self, select_query: SelectQuery) -> Self:
        from pydba.query.enums.union import UnionEnum
        if self._unions_list is None:
            self._unions_list = []
        self._unions_list.append(Union(union=UnionEnum.UNION_ALL, select_query=select_query))
        return self


class ValuesMixin:
    """Mixin providing values() fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_values_list'):
            self._values_list: list[dict] = []

    def values(self, *dicts: dict) -> Self:
        self._values_list.extend(dicts)
        return self


class UpdatesMixin:
    """Mixin providing updates() fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_updates_dict'):
            self._updates_dict: dict = {}

    def updates(self, updates: dict) -> Self:
        self._updates_dict.update(updates)
        return self


class ReturningMixin:
    """Mixin providing returning() fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_returning_list'):
            self._returning_list: Optional[list] = None

    def returning(self, columns: list) -> Self:
        self._returning_list = columns
        return self


class OnConflictMixin:
    """Mixin providing on_conflict_do_nothing/on_conflict_do_update fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_on_conflict'):
            self._on_conflict: Optional[OnConflict] = None

    def on_conflict_do_nothing(self, conflict: str | list[str]) -> Self:
        self._on_conflict = OnConflict(conflict=conflict, updates=None)
        return self

    def on_conflict_do_update(self, conflict: str | list[str], updates: dict) -> Self:
        self._on_conflict = OnConflict(conflict=conflict, updates=updates)
        return self


class LastInsertIdMixin:
    """Mixin providing last_insert_id() fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_last_insert_id_col'):
            self._last_insert_id_col: Optional[str] = None

    def last_insert_id(self, column: str) -> Self:
        self._last_insert_id_col = column
        return self