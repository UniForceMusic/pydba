from __future__ import annotations

import pytest
from pydba.result._result import Result, snapshot_result


def test_result_creation():
    result = Result(columns={"id": "INTEGER", "name": "TEXT"})
    assert result.columns() == {"id": "INTEGER", "name": "TEXT"}
    assert result.fetch_dict() is None
    assert result.fetch_dicts() == []


def test_result_fetch_dict():
    result = Result(
        columns={"id": "INTEGER", "name": "TEXT"},
        rows=[{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}],
    )
    row = result.fetch_dict()
    assert row == {"id": 1, "name": "John"}
    row2 = result.fetch_dict()
    assert row2 == {"id": 2, "name": "Jane"}
    assert result.fetch_dict() is None


def test_result_fetch_dicts():
    result = Result(
        columns={"id": "INTEGER", "name": "TEXT"},
        rows=[{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}],
    )
    rows = result.fetch_dicts()
    assert len(rows) == 2
    assert rows[0]["name"] == "John"


def test_result_scalar():
    result = Result(
        columns={"cnt": "INTEGER"},
        rows=[{"cnt": 42}],
    )
    val = result.scalar()
    assert val == 42


def test_result_scalar_named():
    result = Result(
        columns={"cnt": "INTEGER"},
        rows=[{"cnt": 42}],
    )
    val = result.scalar("cnt")
    assert val == 42


def test_result_scalar_empty():
    result = Result(columns={"cnt": "INTEGER"})
    assert result.scalar() is None


def test_result_fetch_object():
    result = Result(
        columns={"id": "INTEGER", "name": "TEXT"},
        rows=[{"id": 1, "name": "John"}],
    )
    obj = result.fetch_object()
    assert obj == {"id": 1, "name": "John"}


def test_result_fetch_objects():
    result = Result(
        columns={"id": "INTEGER", "name": "TEXT"},
        rows=[{"id": 1, "name": "John"}, {"id": 2, "name": "Jane"}],
    )
    objs = result.fetch_objects()
    assert len(objs) == 2


def test_result_from_result():
    inner = Result(
        columns={"id": "INTEGER"},
        rows=[{"id": 1}, {"id": 2}],
    )
    snapshot = snapshot_result(inner)
    assert snapshot.columns() == {"id": "INTEGER"}
    rows = snapshot.fetch_dicts()
    assert len(rows) == 2
    # Original should be exhausted
    assert inner.fetch_dicts() == []
