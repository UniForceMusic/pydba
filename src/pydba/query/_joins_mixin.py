from __future__ import annotations

from typing import Any, Self

from pydba.query._join import Join
from pydba.query.enums.join import JoinEnum


class JoinsMixin:
    """Mixin providing JOIN fluent API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'joins'):
            self.joins: list[Any] = []

    def left_join(self, table: Any, alias: str | None = None) -> Join:
        return self._add_join(JoinEnum.LEFT_JOIN, table, alias)

    def left_join_table(self, table: Any, alias: str | None = None) -> Join:
        return self._add_join(JoinEnum.LEFT_JOIN, table, alias)

    def left_join_sub_query(self, query: Any, alias: str) -> Join:
        from pydba.query.expressions.sub_query import SubQuery
        sq = SubQuery(query, alias)
        return self._add_join(JoinEnum.LEFT_JOIN, sq)

    def left_join_lateral(self, query: Any, alias: str) -> Join:
        from pydba.query.expressions.sub_query import SubQuery
        sq = SubQuery(query, alias)
        return self._add_join(JoinEnum.LEFT_JOIN_LATERAL, sq)

    def inner_join(self, table: Any, alias: str | None = None) -> Join:
        return self._add_join(JoinEnum.INNER_JOIN, table, alias)

    def inner_join_lateral(self, query: Any, alias: str) -> Join:
        from pydba.query.expressions.sub_query import SubQuery
        sq = SubQuery(query, alias)
        return self._add_join(JoinEnum.INNER_JOIN_LATERAL, sq)

    def cross_join(self, table: Any, alias: str | None = None) -> Join:
        return self._add_join(JoinEnum.CROSS_JOIN, table, alias)

    def cross_join_lateral(self, query: Any, alias: str) -> Join:
        from pydba.query.expressions.sub_query import SubQuery
        sq = SubQuery(query, alias)
        return self._add_join(JoinEnum.CROSS_JOIN_LATERAL, sq)

    def join(self, sql: Any) -> Self:
        """Add a raw join expression."""
        self.joins.append(sql)
        return self

    def _add_join(self, join_type: JoinEnum, table: Any, alias: str | None = None) -> Join:
        if alias:
            from pydba.query.expressions.alias import Alias
            table = Alias(table, alias)
        j = Join(join=join_type, table=table)
        self.joins.append(j)
        return j
