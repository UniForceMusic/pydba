# pydba — Agent Instructions

A Python database abstraction layer (PostgreSQL + SQLite + MySQL), ported from PHP `sentience/database`.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Commands

| Command | Purpose |
|---------|---------|
| `python3 -m pytest` | Run all 206 tests (unit + SQLite/PostgreSQL/MySQL integration) |
| `python3 -m pytest tests/test_integration_sqlite.py` | SQLite integration tests |
| `python3 -m pytest tests/test_integration_postgres.py` | PostgreSQL integration tests (skips when PG not reachable on localhost:5432; run `docker compose up -d postgres`) |
| `python3 -m pytest tests/test_integration_mysql.py` | MySQL integration tests (skips when MySQL not reachable on localhost:3306; run `docker start sentience-v3-mysql-1` or any `mysql` container with `MYSQL_ALLOW_EMPTY_PASSWORD=yes` on port 3306 — the suite auto-creates the `pydba` database) |
| `python3 -m pytest tests/test_dialect_sql.py -k "test_select"` | Single test or pattern |
| `python3 -m mypy src/pydba` | Typecheck (strict mode). Clean — no issues. |
| `python3 -m ruff check src/pydba/ tests/` | Lint. Clean — no issues. |
| `python3 main.py` | Run the example script (SQLite + PostgreSQL + MySQL CRUD + giant select) |

No Makefile, CI workflows, or pre-commit hooks exist.

## Architecture

Four pillars under `src/pydba/`:

- **`dialects/`** — SQL generation (`SQLDialect` base, `PostgresqlDialect`, `SQLiteDialect`). `SQLDialect` is the largest file (~713 lines).
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
- `PostgresqlDialect.datetime_format = "%Y-%m-%d %H:%M:%S.%f"` (microseconds).
- `SQLiteDialect` raises `QueryError` for ALTER COLUMN, DROP COLUMN, named constraints, and named ON CONFLICT.
- Version parsing: `"15.2"` → `150200` (major\*100^2 + minor\*100 + patch).

## Testing

- **206 tests, all passing** with `pytest` (134 unit/SQLite + 14 PostgreSQL integration + 10 MySQL integration + the rest unit).
- **Unit tests** (no database): `test_dialect_*.py`, `test_*_query.py`, `test_conditions.py`, `test_joins.py`, `test_expressions.py`, `test_query_with_params.py`, `test_result_abstract.py`.
- **Integration tests**: `test_integration_sqlite.py` uses SQLite `:memory:` — no external services needed. `test_integration_postgres.py` requires a PostgreSQL service on `localhost:5432` (skipped via `pytestmark` when unreachable; run `docker compose up -d postgres`). `test_integration_mysql.py` requires a MySQL service on `localhost:3306` with `MYSQL_ALLOW_EMPTY_PASSWORD=yes` (skipped via a session-scoped fixture when unreachable; the suite auto-creates the `pydba` database and drops all user tables between tests).
- **Fixtures**: `conftest.py` provides `sql_dialect`, `sqlite_dialect`, `pg_dialect`, `mysql_dialect`. The postgres integration module defines its own `pg_adapter` / `pg_dialect` / `pg_db` yield fixtures. The mysql integration module defines `mysql_adapter` / `mysql_dialect` (the latter overrides the conftest one within that module) plus a session-scoped `_pydba_database` bootstrap fixture.
- **DDL has no parameters** — use `adapter.exec(qwp.query)` not `adapter.query_with_params()`.
- **DML uses parameters** — use `adapter.query_with_params(dialect, qwp)`.
- **PostgreSQL adapter placeholder conversion** — `PsycopgAdapter.query_with_params` converts `?` placeholders to `%s` for psycopg (the dialect emits `?`; psycopg expects `%s`). The MySQL adapter does the same for `mysql.connector`.
- **MySQL implicit transactions** — `mysql.connector` defaults to `autocommit=False`, so any statement (even `SELECT` via `adapter.query()`) opens an implicit transaction. Call `adapter.commit_transaction()` before `adapter.begin_transaction()` to clear pending state, otherwise `start_transaction()` raises `ProgrammingError("Transaction already in progress")`. `adapter.exec()` commits after each statement; `adapter.query()` / `adapter.query_with_params()` do not.
- **Qualified column references** — pass columns/conditions as two-element lists (e.g. `["users", "id"]`) or wrap in `identifier(["users","id"])`. A dotted string like `"users.id"` is treated as a single identifier and escaped as `` `users.id` `` (non-existent column). Use `raw("...")` (a `SqlABC`) for raw JOIN clauses and aggregate expressions — `JoinsMixin.join()` ignores bare strings.
- **Schema-qualified INSERT** — the base `SQLDialect.insert()` does not split a `list[str]` table argument (it stringifies the list). Wrap the table in `identifier(["schema","table"])` (an `Identifier` expression) instead.

## Reference

- `PLAN.md` — 801-line implementation plan with architecture decisions, detailed method lists, and testing strategy.
- `SentienceDatabase/` — PHP reference implementation (not part of the Python package).
- `docker-compose.yml` — provides MySQL and PostgreSQL services (used by `test_integration_postgres.py`).