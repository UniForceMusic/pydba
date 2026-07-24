from __future__ import annotations

import pytest

from pydba.dialects._sql_dialect import SQLDialect
from pydba.dialects.postgres import PgSQLDialect
from pydba.dialects.sqlite import SQLiteDialect


@pytest.fixture
def sql_dialect() -> SQLDialect:
    """Return a base ANSI SQL dialect."""
    return SQLDialect()


@pytest.fixture
def sqlite_dialect() -> SQLiteDialect:
    """Return a SQLite dialect."""
    return SQLiteDialect()


@pytest.fixture
def pg_dialect() -> PgSQLDialect:
    """Return a PostgreSQL dialect."""
    return PgSQLDialect()
