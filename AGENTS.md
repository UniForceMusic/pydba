# pydba — Agent Instructions

A Python database abstraction layer (PostgreSQL + SQLite), ported from PHP `sentience/database`.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Commands

| Command | Purpose |
|---------|---------|
| `python3 -m pytest` | Run all 134 tests (unit + SQLite in-memory integration) |
| `python3 -m pytest tests/test_integration_sqlite.py` | Integration tests only |
| `python3 -m pytest tests/test_dialect_sql.py -k "test_select"` | Single test or pattern |
| `python3 -m mypy src/pydba` | Typecheck (strict mode). 133 errors currently. |
| `python3 -m ruff check src/pydba/ tests/` | Lint. 292 errors, 278 auto-fixable with `--fix`. |
| `python3 main.py` | Run the example script (SQLite in-memory CRUD) |

No Makefile, CI workflows, or pre-commit hooks exist.

## Architecture

Four pillars under `src/pydba/`:

- **`dialects/`** — SQL generation (`SQLDialect` base, `PgSQLDialect`, `SQLiteDialect`). `SQLDialect` is the largest file (~713 lines).
- **`adapters/`** — Connection wrappers (`SQLiteAdapter`, `PsycopgAdapter`).
- **`query/`** — Fluent query builders (`SelectQuery`, `InsertQuery`, `UpdateQuery`, `DeleteQuery`, `CreateTableQuery`, `AlterTableQuery`, `DropTableQuery`). Mixins: `WhereMixin`, `HavingMixin`, `JoinsMixin`, etc.
- **`result/`** — Result set abstraction (`Result`, `SQLite3Result`, `PsycopgResult`). Methods: `fetch_dict()`, `fetch_dicts()`, `scalar()`, `fetch_object()`, `fetch_objects()`, `columns()`.

User-facing facade: `from pydba.database import DB`

```python
db = DB.connect_sqlite(":memory:")
db = DB.connect_postgresql("mydb", host="localhost", user="postgres")
result = db.select("users").where_equals("name", "Alice").execute()
row = result.fetch_dict()
```

## Import gotchas

- `PsycopgAdapter` is NOT exported from `pydba.adapters` — import directly: `from pydba.adapters.postgres import PsycopgAdapter`
- `PsycopgResult` is NOT exported from `pydba.result` — import directly: `from pydba.result.postgres import PsycopgResult`
- `raw()` is a module-level function: `from pydba.query._query import raw` (not `Query.raw()`)
- `Snapshot` a result: `from pydba.result._result import snapshot_result`

## Key conventions

- **ABCs over Protocols** — nominal subtyping (`abc.ABC`) used everywhere.
- **Mixins over traits** — multiple inheritance with `WhereMixin`, `HavingMixin`, etc.
- **Fluent API returns `Self`** — all query builder methods return `Self` for chaining.
- **`to_query_with_params()`** — central method that returns `QueryWithParams(query, params)`. Each query class implements this.
- **`execute(emulate_prepare=False)`** — runs via the bound database, returns `ResultABC`.
- **`emulate_prepare`** — parameter for `query_with_params()` and `execute()` (used for drivers without native prepared statements).
- **`from __future__ import annotations`** — used in every file.
- **`if TYPE_CHECKING`** — used for lazy imports in type stubs.

## Dialect quirks

- `SQLDialect` properties like `bool`, `distinct_on`, `on_conflict`, `returning` are instance attributes (not abstract properties), set in `__init__`.
- `PgSQLDialect.datetime_format = "%Y-%m-%d %H:%M:%S.%f"` (microseconds).
- `SQLiteDialect` raises `QueryError` for ALTER COLUMN, DROP COLUMN, named constraints, and named ON CONFLICT.
- Version parsing: `"15.2"` → `150200` (major\*100^2 + minor\*100 + patch).

## Testing

- **134 tests, all passing** with `pytest`.
- **Unit tests** (no database): `test_dialect_*.py`, `test_*_query.py`, `test_conditions.py`, `test_joins.py`, `test_expressions.py`, `test_query_with_params.py`, `test_result_abstract.py`.
- **Integration tests**: `test_integration_sqlite.py` uses SQLite `:memory:` — no external services needed. No PostgreSQL integration tests exist yet.
- **Fixtures**: `conftest.py` provides `sql_dialect`, `sqlite_dialect`, `pg_dialect`.
- **DDL has no parameters** — use `adapter.exec(qwp.query)` not `adapter.query_with_params()`.
- **DML uses parameters** — use `adapter.query_with_params(dialect, qwp)`.

## Reference

- `PLAN.md` — 801-line implementation plan with architecture decisions, detailed method lists, and testing strategy.
- `SentienceDatabase/` — PHP reference implementation (not part of the Python package).
- `docker-compose.yml` — provides MySQL and PostgreSQL services (for future integration tests; not needed for current tests).