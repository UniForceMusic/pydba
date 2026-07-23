from __future__ import annotations

import pytest
from pydba.query._join import Join
from pydba.query.enums.join import JoinEnum
from pydba.query.enums.chain import ChainEnum
from pydba.query._condition import Condition
from pydba.query.enums.condition import ConditionEnum


def test_join_creation() -> None:
    j = Join(join=JoinEnum.LEFT_JOIN, table="posts")
    assert j.join == JoinEnum.LEFT_JOIN
    assert j.table == "posts"
    assert j.conditions == []


def test_join_on_condition() -> None:
    j = Join(join=JoinEnum.INNER_JOIN, table="posts")
    c = Condition(condition=ConditionEnum.EQUALS, identifier="users.id", value="posts.user_id")
    j.on(c)
    assert len(j.conditions) == 1
    assert j.conditions[0].chain == ChainEnum.AND


def test_join_or_on_condition() -> None:
    j = Join(join=JoinEnum.LEFT_JOIN, table="posts")
    c = Condition(condition=ConditionEnum.EQUALS, identifier="a", value="b")
    j.or_on(c)
    assert j.conditions[0].chain == ChainEnum.OR


def test_multiple_join_conditions() -> None:
    j = Join(join=JoinEnum.LEFT_JOIN, table="posts")
    j.on(Condition(condition=ConditionEnum.EQUALS, identifier="users.id", value="posts.user_id"))
    j.on(Condition(condition=ConditionEnum.EQUALS, identifier="users.deleted", value=0))
    assert len(j.conditions) == 2


def test_all_join_types() -> None:
    for join_type in JoinEnum:
        j = Join(join=join_type, table="t")
        assert j.join == join_type
