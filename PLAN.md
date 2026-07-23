# Python Database Abstraction Layer (pydba) — Implementation Plan

## Overview

This plan describes a Python database abstraction layer inspired by the PHP package `sentience/database`. The Python version will support **PostgreSQL** and **SQLite** only (for now).

The four required pillars are:
1. **Dialects** — Database-specific SQL generation (ansi SQL standard, PostgreSQL, SQLite)
2. **Adapters** — Low-level database connection wrappers (psycopg for Postgres, sqlite3 for SQLite)
3. **Query Building** — Fluent builders for SELECT, INSERT, UPDATE, DELETE
4. **Result** — Uniform result set abstraction (fetch assoc, object, scalar, columns)

---

## Package Structure

```
pydba/
├── pyproject.toml          # modern Python packaging (PEP 621)
├── README.md
├── src/
│   └── pydba/
│       ├── __init__.py
│       │
│       ├── exceptions.py
│       │   ├── DatabaseError
│       │   ├── AdapterError
│       │   ├── DriverError
│       │   ├── QueryError
│       │   └── QueryWithParamsError
│       │
│       ├── _query_with_params.py      # QueryWithParams dataclass
│       │
│       ├── _helpers.py                # escape helpers (escape_ansi, escape_backslash)
│       │
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── _base.py               # AdapterABC (abstract base class)
│       │   ├── postgres.py            # PsycopgAdapter
│       │   └── sqlite.py              # SQLiteAdapter
│       │
│       ├── dialects/
│       │   ├── __init__.py
│       │   ├── _base.py               # DialectABC (abstract base class)
│       │   ├── _sql_dialect.py        # SQLDialect (ANSI base, ~1200+ lines)
│       │   ├── postgres.py            # PgSQLDialect
│       │   └── sqlite.py             # SQLiteDialect
│       │
│       ├── query/
│       │   ├── __init__.py
│       │   ├── _query.py              # Query (abstract base with static factory methods)
│       │   ├── select.py              # SelectQuery
│       │   ├── insert.py              # InsertQuery
│       │   ├── update.py              # UpdateQuery
│       │   ├── delete.py              # DeleteQuery
│       │   ├── _join.py               # Join object
│       │   ├── _condition.py          # Condition dataclass
│       │   ├── _where_group.py        # WhereGroup (implements ConditionGroup)
│       │   ├── _having_group.py        # HavingGroup (implements ConditionGroup)
│       │   ├── _on_conflict.py        # OnConflict dataclass
│       │   ├── _order_by.py           # OrderBy dataclass
│       │   ├── _union.py              # Union dataclass
│       │   │
│       │   ├── expressions/
│       │   │   ├── __init__.py
│       │   │   ├── _sql.py            # SqlABC (abstract base class)
│       │   │   ├── raw.py             # Raw expression
│       │   │   ├── identifier.py      # Identifier expression
│       │   │   ├── alias.py           # Alias expression
│       │   │   ├── expression.py      # Expression (sql + params)
│       │   │   ├── sub_query.py       # SubQuery
│       │   │   └── current_timestamp.py
│       │   │
│       │   └── enums/
│       │       ├── __init__.py
│       │       ├── condition.py       # ConditionEnum
│       │       ├── chain.py           # ChainEnum (AND / OR)
│       │       ├── join.py            # JoinEnum
│       │       ├── order_by_dir.py    # OrderByDirectionEnum
│       │       ├── union.py           # UnionEnum
│       │       ├── type.py            # TypeEnum (BOOL, INT, FLOAT, STRING, DATETIME)
│       │       └── referential_action.py
│       │
│       └── result/
│           ├── __init__.py
│           ├── _base.py               # ResultABC
│           ├── _result.py             # Result (in-memory)
│           ├── postgres.py            # PsycopgResult (or just use _abstract)
│           └── sqlite.py              # SQLite3Result
│
└── tests/
    ├── __init__.py
    ├── test_query_with_params.py
    ├── test_dialect_sql.py
    ├── test_dialect_postgres.py
    ├── test_dialect_sqlite.py
    ├── test_select_query.py
    ├── test_insert_query.py
    ├── test_update_query.py
    ├── test_delete_query.py
    ├── test_conditions.py
    ├── test_joins.py
    ├── test_expressions.py
    ├── test_result_abstract.py
    └── conftest.py
```

---

## Phase 1: Foundation (Enums, ABCs, Core Types)

### 1.1 Set up the project skeleton
- Create `pyproject.toml` with modern Python packaging (PEP 621)
- Use Python 3.11+ (type hints, `StrEnum`, `dataclass`)
- Dependencies: `psycopg[binary]` for Postgres adapter; no other deps for SQLite
- Dev dependencies: `pytest`, `mypy`, `ruff`

### 1.2 Exceptions (`exceptions.py`)
Five exception classes, all inheriting from `Exception`:
- `DatabaseError(Exception)` — base error
- `AdapterError(DatabaseError)` — adapter-level errors
- `DriverError(DatabaseError)` — driver/connection errors
- `QueryError(DatabaseError)` — query building errors
- `QueryWithParamsError(DatabaseError)` — parameterized query errors

### 1.3 QueryWithParams (`_query_with_params.py`)
```python
@dataclass
class QueryWithParams:
    query: str
    params: list[Any] = field(default_factory=list)

    def to_sql(self, dialect: "DialectABC") -> str: ...
    def named_params_to_question_marks(self) -> Self: ...
```
- Converts `:named` params to `?` positional params
- `to_sql()` interpolates `?` placeholders with dialect-casted values
- Must use a regex that respects string literals (not replacing params inside quoted strings)

### 1.4 Enums (query/enums/)
Seven enums mirroring the PHP versions:

| Enum | File | Values |
|---|---|---|
| `ConditionEnum(StrEnum)` | `condition.py` | `EQUALS='='`, `NOT_EQUALS='<>'`, `LESS_THAN='<'`, `LESS_THAN_OR_EQUALS='<='`, `GREATER_THAN='>'`, `GREATER_THAN_OR_EQUALS='>='`, `BETWEEN='BETWEEN'`, `NOT_BETWEEN='NOT BETWEEN'`, `LIKE='LIKE'`, `NOT_LIKE='NOT LIKE'`, `GLOB='GLOB'`, `NOT_GLOB='NOT GLOB'`, `IN='IN'`, `NOT_IN='NOT IN'`, `REGEX='REGEX'`, `NOT_REGEX='NOT REGEX'`, `EXISTS='EXISTS'`, `NOT_EXISTS='NOT EXISTS'`, `RAW='RAW'` |
| `ChainEnum(StrEnum)` | `chain.py` | `AND='AND'`, `OR='OR'` |
| `JoinEnum(StrEnum)` | `join.py` | `LEFT_JOIN`, `LEFT_JOIN_LATERAL`, `INNER_JOIN`, `INNER_JOIN_LATERAL`, `CROSS_JOIN`, `CROSS_JOIN_LATERAL` |
| `OrderByDirectionEnum(StrEnum)` | `order_by_dir.py` | `ASC='ASC'`, `DESC='DESC'` |
| `UnionEnum(StrEnum)` | `union.py` | `UNION='UNION'`, `UNION_ALL='UNION ALL'` |
| `TypeEnum(Enum)` | `type.py` | Pure enum: `BOOL`, `INT`, `FLOAT`, `STRING`, `DATETIME` |
| `ReferentialActionEnum(StrEnum)` | `referential_action.py` | `ON_UPDATE_NO_ACTION`, `ON_UPDATE_SET_NULL`, `ON_UPDATE_CASCADE`, `ON_DELETE_NO_ACTION`, `ON_DELETE_SET_NULL`, `ON_DELETE_CASCADE` |

### 1.5 Expression types (query/expressions/)
An abstract base class `Sql` with three abstract methods:
- `sql(dialect: DialectABC) -> str` — parameterized SQL with `?` placeholders
- `params(dialect: DialectABC) -> list` — list of parameter values
- `raw_sql(dialect: DialectABC) -> str` — fully interpolated SQL string

Concrete implementations:
- **`Raw`**: wraps a plain SQL string, no params
- **`Identifier`**: delegates to `dialect.escape_identifier()`, no params
- **`Alias`**: holds `identifier` and `alias`; renders as `identifier AS alias`
- **`Expression`**: holds `sql` string and `params` list
- **`SubQuery`**: wraps a `SelectQuery` with an `alias`
- **`CurrentTimestamp`**: renders `CURRENT_TIMESTAMP`, no params

### 1.6 Query objects (query/)
- **`Condition`**: dataclass with `condition: ConditionEnum|str`, `identifier`, `value`, `chain: ChainEnum`
- **`ConditionGroupABC`**: abstract base class for grouped conditions (in `query/_condition_group.py`). Subclasses: `WhereGroup` (uses WhereMixin, stores in `where`), `HavingGroup` (uses HavingMixin, stores in `having`)
- **`Join`**: dataclass with `join: JoinEnum`, `table`, and uses `WhereMixin` for ON conditions. Methods: `on()`, `or_on()`
- **`OrderBy`**: dataclass with `column`, `direction: OrderByDirectionEnum`
- **`Union`**: dataclass with `union: UnionEnum`, `select_query: SelectQuery`
- **`OnConflict`**: dataclass with `conflict: str|list[str]`, `updates: Optional[dict]` (None = do nothing, empty dict = update all, populated dict = specific updates)

### 1.7 Abstract Base Classes (no `interfaces/` directory — ABCs live alongside their implementations)

**Why ABCs instead of protocols:** Python's `abc.ABC` provides runtime type checking via `isinstance()` and enforces method implementation at instantiation time, which is closer to PHP's interface contract than structural subtyping (`Protocol`).

**DialectABC** (`dialects/_base.py`):
- Uses `abc.ABC` and `@abstractmethod`
- 12+ abstract methods:
  - `select(distinct, columns, table, joins, where, group_by, having, order_by, limit, offset, unions) -> QueryWithParams`
  - `insert(table, values, on_conflict, returning, last_insert_id) -> QueryWithParams`
  - `update(table, updates, where, returning) -> QueryWithParams`
  - `delete(table, where, returning) -> QueryWithParams`
  - `create_table(if_not_exists, table, columns, primary_keys, constraints) -> QueryWithParams`
  - `alter_table(table, alters) -> list[QueryWithParams]`
  - `drop_table(if_exists, table) -> QueryWithParams`
  - Transaction methods: `begin_transaction`, `commit_transaction`, `rollback_transaction`
  - Savepoint methods: `begin_savepoint`, `commit_savepoint`, `rollback_savepoint`
  - Type coercion: `escape_identifier`, `escape_string`, `cast_to_query`, `cast_bool`, `cast_datetime`, `parse_bool`, `parse_datetime`, `type(type_enum, bits)`
  - Capability flags (as `@property`): `bool`, `distinct_on`, `generated_by_default_as_identity`, `lateral`, `on_conflict`, `returning`, `savepoints`

**AdapterABC** (`adapters/_base.py`):
- Uses `abc.ABC` and `@abstractmethod`
- 11+ abstract methods:
  - `version() -> str`
  - `exec(query: str) -> None`
  - `query(query: str) -> ResultABC`
  - `query_with_params(dialect, query_with_params, emulate_prepare) -> ResultABC`
  - `begin_transaction`, `commit_transaction`, `rollback_transaction`
  - `begin_savepoint`, `commit_savepoint`, `rollback_savepoint`
  - `in_transaction() -> bool`
  - `last_insert_id(name: Optional[str]) -> Optional[int|str]`

**ResultABC** (`result/_base.py`):
- Uses `abc.ABC` and `@abstractmethod`
- 6 abstract methods:
  - `columns() -> dict[str, str]` — column name → type
  - `scalar(column: Optional[str] = None) -> Any`
  - `fetch_object(cls=dict, constructor_args=[]) -> Optional[object|dict]`
  - `fetch_objects(cls=dict, constructor_args=[]) -> list`
  - `fetch_assoc() -> Optional[dict]`
  - `fetch_assocs() -> list[dict]`

**QueryABC** (`query/_query.py`):
- Already the abstract `Query` base class
- Abstract method: `to_query_with_params() -> QueryWithParams`
- Concrete: `to_sql()`, `execute()`, `explain()` built on top
- Static factory methods: `raw()`, `identifier()`, `alias()`, `expression()`, `sub_query()`, `current_timestamp()`, `now()`

**DatabaseABC** — Not needed as a separate ABC. `DatabaseAbstract` (in `database/_abstract.py`) serves as the abstract base with a concrete `Database` subclass.

**SqlABC** — Abstract base in `query/expressions/_sql.py` with `sql()`, `params()`, `raw_sql()` abstract methods.

**ConditionGroupABC** — Abstract base in `query/_condition_group.py` with `chain()`, `not_()`, `conditions()` abstract methods.

---

## Phase 2: Dialects

### 2.1 DialectAbstract (`dialects/_base.py`)
- Abstract class extending `DialectABC`
- Stores `version` (parsed to integer for comparison), `options` dict
- Version parsing: `"15.2"` → `150200` (major*100^2 + minor*100 + patch)

### 2.2 SQLDialect (`dialects/_sql_dialect.py`) — **THE CORE (~1200+ lines)**
This is the biggest single file. It implements the full ANSI SQL standard.

**Constants as class attributes (overridable in subclasses):**
```python
BOOL = False
DISTINCT_ON = False
ON_CONFLICT = False
RETURNING = False
LATERAL = False
SAVEPOINTS = True
GENERATED_BY_DEFAULT_AS_IDENTITY = True
ESCAPE_IDENTIFIER = '"'
ESCAPE_STRING = "'"
ESCAPE_ANSI = True
DATETIME_FORMAT = "Y-m-d H:i:s"
```

**Public methods implementing DialectABC:**
- `select()`, `insert()`, `update()`, `delete()` — each returns `QueryWithParams`
- `create_table()`, `alter_table()` (returns list of QueryWithParams), `drop_table()`
- Transaction/savepoint methods
- Type methods: `type()`, `escape_identifier()`, `escape_string()`, `cast_to_query()`, `cast_bool()`, `cast_datetime()`, `parse_bool()`, `parse_datetime()`
- Capability property methods

**Protected `build_*` helper methods (overridable by subclasses):**
- `_build_distinct()`, `_build_table()`, `_build_joins()`, `_build_where()`, `_build_group_by()`, `_build_having()`, `_build_order_by()`, `_build_limit()`, `_build_offset()`, `_build_unions()`
- Condition builders: `_build_condition()`, `_build_condition_equals()`, `_build_condition_between()`, `_build_condition_like()`, `_build_condition_glob()`, `_build_condition_in()`, `_build_condition_regex()`, `_build_condition_exists()`, `_build_condition_raw()`, `_build_condition_group()`
- `_build_on_conflict()`, `_build_returning()`, `_build_question_marks()`, `_build_sql()`
- DDL: `_build_column()`, `_build_unique_constraint()`, `_build_foreign_key_constraint()`
- ALTER: `_build_alter_table_add_column()`, `_build_alter_table_alter_column()`, `_build_alter_table_rename_column()`, `_build_alter_table_drop_column()`, `_build_alter_table_add_primary_keys()`, `_build_alter_table_add_unique_constraint()`, `_build_alter_table_add_foreign_key_constraint()`, `_build_alter_table_drop_constraint()`

### 2.3 PgSQLDialect (`dialects/postgres.py`)
Extends `SQLDialect`. Overrides:

| Feature | PostgreSQL behavior |
|---|---|
| `BOOL = True` | Native `BOOLEAN` type; `cast_bool()` returns bool directly |
| `DISTINCT_ON = True` | Supports `DISTINCT ON (...)` syntax |
| `DATETIME_FORMAT = "Y-m-d H:i:s.u"` | Microsecond precision |
| `build_condition_like()` | Uses `ILIKE`/`NOT ILIKE` for case-insensitive matching |
| `build_condition_regex()` | Version ≥ 15: `regexp_like()`; else or if option `use_tilde_regex` set: `~`/`!~` operators |
| `_build_column()` | Optional `SERIAL`/`BIGSERIAL` when option `use_serials` set |
| `type()` | `FLOAT` → `REAL`(≤32) or `DOUBLE PRECISION`(>32); `DATETIME` → `TIMESTAMP` |
| `parse_datetime()` | Fix timezone offsets missing minutes |
| Version-gated features | `distinct_on` >= 7.2, `generated_by_default_as_identity` >= 17.0, `lateral` >= 9.3, `on_conflict` >= 9.5, `returning` >= 8.2 |

### 2.4 SQLiteDialect (`dialects/sqlite.py`)
Extends `SQLDialect`. Overrides:

| Feature | SQLite behavior |
|---|---|
| `GENERATED_BY_DEFAULT_AS_IDENTITY = False` | Uses `INTEGER PRIMARY KEY AUTOINCREMENT` |
| `_build_condition_like()` | Case-insensitive: standard LIKE; case-sensitive: GLOB |
| `_build_condition_glob()` | Native GLOB support |
| `_build_condition_regex()` | `regexp_like()` by default; `REGEXP` operator with option `use_regexp` |
| `_build_on_conflict()` | Raises `QueryError` if named constraint used |
| `_build_column()` | Identity columns emit `name INTEGER PRIMARY KEY AUTOINCREMENT` |
| `_build_unique_constraint()` and `_build_foreign_key_constraint()` | Strip constraint name (SQLite doesn't support named table constraints) |
| ALTER TABLE | `_build_alter_table_alter_column()` always raises; `_build_alter_table_rename_column()` raises pre-3.25.0; all constraint-altering methods raise |
| `type()` | `BOOL` → `BOOLEAN`; `FLOAT` → `REAL` |
| Version-gated | `on_conflict` >= 3.24.0, `returning` >= 3.35.0 |

---

## Phase 3: Result Layer

### 3.1 ResultAbstract (`result/_base.py`)
Abstract class extending `ResultABC`. Implements `scalar()`, `fetch_object()`, `fetch_objects()` in terms of `fetch_assoc()`/`fetch_assocs()`.
- `scalar(column=None)`: calls `fetch_assoc()`, returns named column or first value
- `fetch_object(cls=dict, constructor_args=[])`: calls `fetch_assoc()`, hydrates object via `_assoc_to_object()`
- `fetch_objects(...)`: loops `fetch_assoc()` until exhaustion

### 3.2 Result (in-memory, `result/_result.py`)
- Constructor takes `columns: dict` and `rows: list[dict]`
- `fetch_assoc()` shifts first row off list; `fetch_assocs()` returns all remaining and clears list
- Static factory `from_result(result: ResultABC) -> Result` to snapshot any result

### 3.3 PsycopgResult (`result/postgres.py`)
- Wraps psycopg's cursor (or just use it directly for column metadata)
- `columns()`: iterate cursor.description for column names/types (OID → readable name)
- `fetch_assoc()`: `cursor.fetchone()` → dict (using cursor.description column names)
- `fetch_assocs()`: `cursor.fetchall()` → list of dicts

### 3.4 SQLite3Result (`result/sqlite.py`)
- Wraps `sqlite3.Cursor`
- `columns()`: use `cursor.description` for column names; map `type_code` to readable type names
- `fetch_assoc()`: `cursor.fetchone()` → `dict(zip(...))` using description
- `fetch_assocs()`: `cursor.fetchall()` → list of dicts (manual loop to handle SQLite's iteration behavior)

---

## Phase 4: Query Builders

### 4.1 Abstract Query (`query/_query.py`)
- Constructor: takes `database: DatabaseABC` and `dialect: DialectABC` and `table`
- `to_sql()` → calls `to_query_with_params().to_sql(dialect)`
- `execute(emulate_prepare=False)` → calls `database.query_with_params(query_with_params, emulate_prepare)`
- `explain(emulate_prepare=False)` → prepends `EXPLAIN`, returns `fetch_assocs()`

**Static factory methods** (the equivalent of PHP's `Query::raw()`, `Query::alias()`, etc.):
```python
@staticmethod
def raw(sql: str) -> Raw: ...

@staticmethod
def identifier(identifier: str | list[str]) -> Identifier: ...

@staticmethod
def alias(identifier: str | list[str] | Sql, alias: str) -> Alias: ...

@staticmethod
def expression(sql: str, params: list = None) -> Expression: ...

@staticmethod
def sub_query(query: "SelectQuery", alias: str) -> SubQuery: ...

@staticmethod
def current_timestamp() -> CurrentTimestamp: ...

@staticmethod
def now() -> datetime: ...
```

**Escape helpers** (module-level functions in `_helpers.py`):
- `escape_ansi(string, chars)` — `str.replace('"', '""')` style
- `escape_backslash(string, chars)` — `str.replace('\\', '\\\\')` style

### 4.2 ConditionsTrait (mixin pattern)
Since Python doesn't have PHP-style traits, use a **mixin class** or **composition**. Recommended approach: define a `ConditionMixin` class with protected helper methods, then use multiple inheritance.

```python
class ConditionMixin:
    """Adds protected condition-building methods. Used by WhereMixin and HavingMixin."""
    
    def _equals(self, conditions, column, value, cast, chain): ...
    def _not_equals(self, conditions, column, value, cast, chain): ...
    def _is_null(self, conditions, column, chain): ...
    def _is_not_null(self, conditions, column, chain): ...
    def _like(self, conditions, column, value, case_insensitive, chain): ...
    def _not_like(self, conditions, column, value, case_insensitive, chain): ...
    def _starts_with(self, conditions, column, value, case_insensitive, escape_backslash, chain): ...
    def _ends_with(self, conditions, column, value, case_insensitive, escape_backslash, chain): ...
    def _contains(self, conditions, column, value, case_insensitive, escape_backslash, chain): ...
    def _not_contains(self, conditions, column, value, case_insensitive, escape_backslash, chain): ...
    def _glob(self, conditions, column, value, case_insensitive, chain): ...
    def _not_glob(self, conditions, column, value, case_insensitive, chain): ...
    def _in(self, conditions, column, values, chain): ...
    def _not_in(self, conditions, column, values, chain): ...
    def _less_than(self, conditions, column, value, chain): ...
    def _less_than_or_equals(self, conditions, column, value, chain): ...
    def _greater_than(self, conditions, column, value, chain): ...
    def _greater_than_or_equals(self, conditions, column, value, chain): ...
    def _between(self, conditions, column, min_val, max_val, chain): ...
    def _not_between(self, conditions, column, min_val, max_val, chain): ...
    def _empty(self, conditions, column, chain): ...
    def _not_empty(self, conditions, column, chain): ...
    def _regex(self, conditions, column, pattern, flags, chain): ...
    def _not_regex(self, conditions, column, pattern, flags, chain): ...
    def _exists(self, conditions, select_query, chain): ...
    def _not_exists(self, conditions, select_query, chain): ...
    def _group(self, conditions, callback, not_, group_class, chain): ...
    def _operator(self, conditions, column, operator, value, chain): ...
    def _add_condition(self, conditions, condition, identifier, value, chain): ...
    def _add_condition_group(self, conditions, group): ...
    def _add_raw_condition(self, conditions, sql, values, chain): ...
    def _escape_like_chars(self, string, escape_backslash): ...
```

### 4.3 WhereMixin and HavingMixin
These provide the public fluent API for WHERE and HAVING conditions.

**WhereMixin**: ~40+ methods, each with `where_*` and `or_where_*` variants:
- `where_equals`, `or_where_equals`
- `where_not_equals`, `or_where_not_equals`
- `where_is_null`, `or_where_is_null`
- `where_is_not_null`, `or_where_is_not_null`
- `where_like`, `or_where_like`, `where_not_like`, `or_where_not_like`
- `where_starts_with`, `or_where_starts_with`
- `where_ends_with`, `or_where_ends_with`
- `where_contains`, `or_where_contains`, `where_not_contains`, `or_where_not_contains`
- `where_glob`, `or_where_glob`, `where_not_glob`, `or_where_not_glob`
- `where_in`, `or_where_in`, `where_not_in`, `or_where_not_in`
- `where_less_than`, `or_where_less_than`, `where_less_than_or_equals`, `or_where_less_than_or_equals`
- `where_greater_than`, `or_where_greater_than`, `where_greater_than_or_equals`, `or_where_greater_than_or_equals`
- `where_between`, `or_where_between`, `where_not_between`, `or_where_not_between`
- `where_empty`, `or_where_empty`, `where_not_empty`, `or_where_not_empty`
- `where_regex`, `or_where_regex`, `where_not_regex`, `or_where_not_regex`
- `where_exists`, `or_where_exists`, `where_not_exists`, `or_where_not_exists`
- `where_group(callback)`, `or_where_group(callback)`, `where_not_group`, `or_where_not_group`
- `where_operator`, `or_where_operator`
- `where(sql, values)`, `or_where(sql, values)`

**HavingMixin**: same ~40+ methods but with `having_*` / `or_having_*` prefixes.

The `_group` method uses **callback introspection** — it inspects the callback's parameter type hint to determine which `ConditionGroup` subclass to instantiate. In Python, use `typing.get_type_hints()` on the callback to detect if the user typed `WhereGroup` or `HavingGroup`. This allows the callback-passing pattern from the PHP API:

```python
query.where_group(lambda g: g.where_equals("col", 1).or_where_is_null("col2"))
```

### 4.4 JoinsMixin
- State: `joins: list[Join | Raw | Expression]`
- Methods: `left_join()`, `left_join_table()`, `left_join_sub_query()`, `left_join_lateral()`, `inner_join()`, `inner_join_lateral()`, `cross_join()`, `cross_join_lateral()`, `outer_apply()`, `cross_apply()` — each with table/sub_query variants
- `join(sql)` for raw joins

### 4.5 Other Simple Traits/Mixins
- **ColumnsMixin**: `columns(list)`
- **DistinctMixin**: `distinct(on=None)`
- **GroupByMixin**: `group_by(list)`
- **OrderByMixin**: `order_by_asc()`, `order_by_desc()`
- **LimitMixin**: `limit(int)`
- **OffsetMixin**: `offset(int)`
- **UnionMixin**: `union(SelectQuery)`, `union_all(SelectQuery)`
- **ValuesMixin**: `values(*dicts)` for INSERT
- **UpdatesMixin**: `updates(dict)` for UPDATE
- **ReturningMixin**: `returning(list)`
- **OnConflictMixin**: `on_conflict_do_nothing(conflict)`, `on_conflict_do_update(conflict, updates)`, `insert_ignore(conflict)`, `on_duplicate_key_update(conflict, updates)`
- **LastInsertIdMixin**: `last_insert_id(column)`

### 4.6 SelectQuery (`query/select.py`)
```python
class SelectQuery(Query, WhereMixin, ColumnsMixin, DistinctMixin, GroupByMixin,
                  HavingMixin, JoinsMixin, LimitMixin, OffsetMixin, OrderByMixin,
                  UnionMixin):
    def to_query_with_params(self) -> QueryWithParams:
        return self.dialect.select(
            self.distinct, self.columns, self.table, self.joins,
            self.where, self.group_by, self.having, self.order_by,
            self.limit, self.offset, self.unions
        )
    
    def from_(self, table) -> Self: ...
    def count(self, emulate_prepare=False) -> int:  # wraps in SELECT count(*) FROM (...)
```

### 4.7 InsertQuery (`query/insert.py`)
```python
class InsertQuery(Query, ValuesMixin, OnConflictMixin, ReturningMixin, LastInsertIdMixin):
    def to_query_with_params(self) -> QueryWithParams:
        return self.dialect.insert(
            self.table, self.values,
            None if self.emulate_on_conflict else self.on_conflict,
            None if self.emulate_returning else self.returning,
            self.last_insert_id
        )
    
    def execute(self, emulate_prepare=False):
        # If dialect supports ON CONFLICT natively, delegate to parent
        # If not, emulate: SELECT -> INSERT or UPDATE
        # If RETURNING is emulated, do extra SELECT after insert
    
    def emulate_on_conflict(self, last_insert_id, in_transaction=False) -> Self: ...
    def emulate_returning(self, last_insert_id) -> Self: ...
```

### 4.8 UpdateQuery (`query/update.py`)
```python
class UpdateQuery(Query, WhereMixin, UpdatesMixin, ReturningMixin):
    def to_query_with_params(self) -> QueryWithParams:
        return self.dialect.update(self.table, self.updates, self.where, self.returning)
```

### 4.9 DeleteQuery (`query/delete.py`)
```python
class DeleteQuery(Query, WhereMixin, ReturningMixin):
    def to_query_with_params(self) -> QueryWithParams:
        return self.dialect.delete(self.table, self.where, self.returning)
    
    def from_(self, table) -> Self: ...
```

---

## Phase 5: Adapters

### 5.1 AdapterAbstract (`adapters/_base.py`)
Common base extending `AdapterABC`:
- Constructor: `(driver_name, database_name, socket_info, startup_queries, options, debug_callback)`
- Tracks `_in_transaction` flag
- Implements common transaction/savepoint logic (delegates SQL generation to dialect)
- Debug callback support (timing + error recording)
- `_exec_startup_queries()` method

### 5.2 PsycopgAdapter (`adapters/postgres.py`)
- Wraps `psycopg.Connection`
- Connection: `psycopg.connect(host=..., port=..., dbname=..., user=..., password=...)`
- SSL options, search_path via options dict
- `exec()` → `connection.execute()` with autocommit management
- `query()` → returns `PsycopgResult`
- `query_with_params()` → prepared statement or emulated
- Transactions: `connection.begin()`, `connection.commit()`, `connection.rollback()`
- `in_transaction()` → `connection.info.transaction_status`
- `last_insert_id()` → `cursor.fetchone()` after INSERT if RETURNING not used

### 5.3 SQLiteAdapter (`adapters/sqlite.py`)
- Wraps `sqlite3.Connection`
- Connection: `sqlite3.connect(database=name, ...)`
- Options: read_only, encryption_key (via PRAGMA key), busy_timeout, encoding, journal_mode, foreign_keys
- Creates REGEXP function via `connection.create_function('REGEXP', 2, regexp_fn)`
- `exec()` → `connection.execute()`
- `query()` → returns `SQLite3Result`
- `query_with_params()` → `connection.execute(sql, params)` or emulated
- Transactions: `connection.execute('BEGIN TRANSACTION')` etc.
- `in_transaction()` → `connection.in_transaction` (Python 3.2+)
- `last_insert_id()` → `connection.lastrowid`

---

## Phase 6: Database Facade

### 6.1 DatabaseABC — abstract base for the top-level database object
No separate ABC file is needed since `DatabaseAbstract` (`database/_abstract.py`) serves as the sole abstract base. Key methods:
- `exec(query)`, `query(query)`, `prepared(query, params)`, `query_with_params(qwp, emulate)`
- `begin_transaction`, `commit_transaction`, `rollback_transaction`, `in_transaction`, `transaction(callback)`
- `last_insert_id()`
- Factory methods: `select(table)`, `insert(table)`, `update(table)`, `delete(table)`, `create_table(table)`, `alter_table(table)`, `drop_table(table)`, `table(table)`

### 6.2 DatabaseAbstract (`database/_abstract.py`)
```python
class DatabaseAbstract:
    def __init__(self, adapter: AdapterABC, dialect: DialectABC): ...
    
    def exec(self, query): ...
    def query(self, query): ...
    def prepared(self, query, params, emulate=False): ...
    def query_with_params(self, qwp, emulate=False): ...
    
    # Transaction handling with savepoint nesting
    def begin_transaction(self, name=None): ...
    def commit_transaction(self, release_savepoints=False, name=None): ...
    def rollback_transaction(self, release_savepoints=False, name=None): ...
    def in_transaction(self): ...
    def transaction(self, callback, release_savepoints=False, name=None): ...
    
    def last_insert_id(self, name=None): ...
    
    # Query builder factories
    def select(self, table) -> SelectQuery: ...
    def select_table(self, table, alias=None) -> SelectQuery: ...
    def select_sub_query(self, sub_query, alias) -> SelectQuery: ...
    def insert(self, table) -> InsertQuery: ...
    def update(self, table) -> UpdateQuery: ...
    def delete(self, table) -> DeleteQuery: ...
    def create_table(self, table) -> CreateTableQuery: ...
    def alter_table(self, table) -> AlterTableQuery: ...
    def drop_table(self, table) -> DropTableQuery: ...
    def table(self, table) -> Table: ...
```

### 6.3 Database (`database/__init__.py`)
```python
class Database(DatabaseAbstract):
    @staticmethod
    def connect(driver: str, name: str, **kwargs) -> Database: ...
    
    @staticmethod
    def drivers() -> list[str]: ...
```

The `connect()` method:
1. Selects adapter and dialect based on driver string (`"postgresql"` or `"sqlite"`)
2. Creates the adapter with connection parameters
3. Gets version from adapter
4. Creates dialect with version and options
5. Returns new `Database(adapter, dialect)`

### 6.4 Table (`table.py`)
High-level table wrapper (like PHP's `Table` class):
```python
class Table:
    def __init__(self, database, dialect, table): ...
    def select(self, columns=None) -> SelectQuery: ...
    def insert(self, *values) -> InsertQuery: ...
    def select_or_insert(self, columns, values, ...) -> Result: ...
    def insert_or_ignore(self, columns, values, ...) -> Result: ...
    def insert_or_update(self, columns, values, ...) -> Result: ...
    def update(self, values) -> UpdateQuery: ...
    def delete(self) -> DeleteQuery: ...
    def create(self, callback=None) -> CreateTableQuery: ...
    def create_if_not_exists(self, callback=None) -> CreateTableQuery: ...
    def alter(self, callback=None) -> AlterTableQuery: ...
    def truncate(self): ...
    def drop(self) -> DropTableQuery: ...
    def drop_if_exists(self) -> DropTableQuery: ...
    def columns(self) -> list[str]: ...
    def is_empty(self) -> bool: ...
    def copy_from(self, source, map_fn=None, ...) -> int: ...
    def copy_to(self, target, map_fn=None, ...) -> int: ...
```

---

## Phase 7: SQLDialect `_build_*` Method Details

The SQLDialect is the biggest component. Here's what each `_build_*` method must handle:

### `_build_distinct(query, distinct)`
- If `distinct` is None: nothing
- If `distinct` is empty list: add `DISTINCT`
- If `distinct` has columns: `DISTINCT ON (col1, col2)` (PostgreSQL only; SQLDialect raises)

### `_build_table(query, params, table)`
- `str`: quoted identifier
- `list[str]`: `"schema"."table"` (escaped list)
- `Alias`: `table AS alias`
- `Sql`: `raw_sql` output
- `SubQuery`: `(SELECT ...) AS alias`

### `_build_joins(query, params, joins)`
Iterates `joins`, each is `Join`, `Raw`, or `Expression`:
- For `Join`: `LEFT JOIN table ON condition1 AND condition2 ...`

### `_build_where` and `_build_having(query, params, conditions)`
If conditions non-empty: add ` WHERE ` or ` HAVING `, then chain each condition with AND/OR.
Each condition delegates to `_build_condition`.

### `_build_condition` (the big dispatch):
- `ConditionEnum.EQUALS`: `column = ?` (or `IS NULL` if value is None)
- `ConditionEnum.NOT_EQUALS`: `column <> ?` (or `IS NOT NULL`)
- `ConditionEnum.LIKE`: `column LIKE ?` (or `ILIKE` for case-insensitive)
- `ConditionEnum.IN`: `column IN (?, ?, ?)` (or `1=0` for empty list)
- `ConditionEnum.BETWEEN`: `column BETWEEN ? AND ?`
- `ConditionEnum.REGEX`: delegates to dialect-specific regex (see below)
- `ConditionEnum.EXISTS`: `EXISTS (SELECT ...)`
- `ConditionEnum.RAW`: raw SQL embedded
- `ConditionGroup`: wrap in `(conditions)` with optional `NOT`
- Operator conditions: `column OPERATOR ?`

### `_build_condition_regex(query, params, column, pattern, flags)`
- SQLDialect (base): raises `QueryError` — no standard regex
- PgSQLDialect: `column ~ pattern` or `regexp_like(column, pattern, flags)`
- SQLiteDialect: `regexp_like(column, pattern, flags)` or `column REGEXP pattern`

### `_build_limit` and `_build_offset`
- SQLDialect: `LIMIT n OFFSET n` (ANSI)
- PgSQLDialect: same (PostgreSQL supports LIMIT/OFFSET)

### `_build_order_by(query, order_by)`
- Each `OrderBy`: `column ASC` or `column DESC`

### `_build_group_by(query, group_by)`
- Comma-separated, each escaped via `escape_identifier()`

### `_build_unions(query, params, unions)`
- Each `Union`: ` UNION (SELECT ...)` or ` UNION ALL (SELECT ...)`

### `_build_on_conflict(query, params, on_conflict, values, last_insert_id)`
- SQLDialect (no native): no-op — returns empty string
- PgSQLDialect: `ON CONFLICT (col) DO NOTHING` or `ON CONFLICT (col) DO UPDATE SET col = EXCLUDED.col`

### `_build_returning(query, returning)`
- SQLDialect (no native): no-op
- PgSQLDialect: `RETURNING col1, col2`

### `_build_column(column: Column) -> str`
- `name type NOT NULL DEFAULT value` or `name INTEGER PRIMARY KEY AUTOINCREMENT`

### `_build_question_marks(params, value) -> str`
- If `value` is a `SelectQuery`: `(SELECT ...)` with params merged
- If `value` is a `Sql` object: delegates to `sql()`/`raw_sql()`
- If `value` is `None`: adds `?` with `None` to params, returns `?`
- Otherwise: adds `?` with value to params, returns `?`

### `_build_sql(params, sql: Sql) -> str`
- Renders Sql object inline, merging params

### `_build_select_query(params, select_query: SelectQuery) -> str`
- Wraps the sub-query: `(SELECT ...)` with all its params

---

## Phase 8: Type Casting and Value Handling

### `cast_to_query(value) -> str`
Converts Python values to SQL-safe string representations:
- `None` → `NULL`
- `bool` → `TRUE` / `FALSE` (or `1` / `0` if not native bools)
- `int` → `str(value)`
- `float` → `str(value)`
- `str` → `'escaped'`
- `datetime` → `'2024-01-15 10:30:00'` (dialect-specific format)
- `SelectQuery` → `(SELECT ...)` (inline, with params)
- `Sql` → `raw_sql()` output

### `cast_to_query` for prepared statements
For `query_with_params`, the adapter needs to bind Python types to driver-native types:
- `psycopg`: uses `cursor.execute(sql, params)` — psycopg handles type conversion natively
- `sqlite3`: uses `cursor.execute(sql, params)` — sqlite3 handles type conversion natively

### `escape_identifier(identifier) -> str`
- `str`: wrap in dialect-specific quotes (`"column"` for ANSI/PostgreSQL, `` `column` `` not needed for these two)
- `list[str]`: `"schema"."table"."column"` (each element quoted and dot-joined)

### `escape_string(string) -> str`
- Escape single quotes by doubling: `'O''Brien'`
- Handle backslash escapes for PostgreSQL (C-style escapes)

---

## Phase 9: Testing Strategy

### 9.1 Unit Tests (no database needed)
- **test_query_with_params.py**: Test `namedParamsToQuestionMarks` and `toSql()` with various parameter patterns
- **test_dialect_sql.py**: Test `SQLDialect` directly — generate SQL for SELECT, INSERT, UPDATE, DELETE, CREATE TABLE, etc. and assert exact SQL output
- **test_dialect_postgres.py**: Test `PgSQLDialect` overrides — DISTINCT ON, ILIKE, ON CONFLICT, RETURNING, regex variations
- **test_dialect_sqlite.py**: Test `SQLiteDialect` overrides — GLOB, regexp_like, AUTOINCREMENT, LIMITATIONS
- **test_select_query.py**: Build SelectQuery objects, call `to_sql()`, verify SQL output
- **test_insert_query.py**: Insert with values, on conflict, returning
- **test_update_query.py**: Update with values, where, returning
- **test_delete_query.py**: Delete with where, returning
- **test_conditions.py**: Test every condition type produces correct SQL
- **test_joins.py**: Test all join types and ON conditions
- **test_expressions.py**: Test Raw, Identifier, Expression, Alias, SubQuery
- **test_result_abstract.py**: Test ResultAbstract with mock fetchAssoc/fetchAssocs

### 9.2 Integration Tests (require actual databases)
- SQLite in-memory database
- PostgreSQL test container or local instance
- Test actual query execution, result fetching, transactions

---

## Implementation Order (Recommended)

| Step | Files | Dependencies |
|------|-------|--------------|
| 1 | `exceptions.py`, enums, `_helpers.py` | None |
| 2 | `QueryWithParams`, `SqlABC`, expressions | Step 1 |
| 3 | `DialectABC`, `DialectAbstract` | Steps 1-2 |
| 4 | `SQLDialect` (core — largest file) | Step 3 |
| 5 | `PgSQLDialect`, `SQLiteDialect` | Step 4 |
| 6 | `ResultABC`, `ResultAbstract`, concrete results | Steps 1-2 |
| 7 | `AdapterABC`, `AdapterAbstract`, concrete adapters | Steps 4-6 |
| 8 | Query objects (`Condition`, `Join`, `WhereGroup`, etc.) | Steps 1-2 |
| 9 | Mixins (`WhereMixin`, `HavingMixin`, `JoinsMixin`, etc.) | Steps 2, 8 |
| 10 | `Query` base + `SelectQuery`, `InsertQuery`, `UpdateQuery`, `DeleteQuery` | Steps 4-5, 9 |
| 11 | `DatabaseAbstract`, `Database`, `Table` | Steps 6-7, 10 |
| 12 | Tests | All of the above |

---

## Key Architectural Decisions

1. **ABCs over Protocols**: Python offers two abstraction mechanisms — `abc.ABC` (nominal subtyping) and `typing.Protocol` (structural subtyping). We use `abc.ABC` everywhere because:
   - It enforces method implementation at instantiation time (like PHP interfaces)
   - It supports `isinstance()` checks at runtime
   - It's more explicit about the contract
   - Protocols in Python are best reserved for duck-typing scenarios (e.g., accepting any object with a `.read()` method)

2. **Mixins over Traits**: Python doesn't have PHP traits, but multiple inheritance with mixin classes achieves the same composability. Use `super()` calls in mixins where needed.

3. **Query callback pattern**: PHP uses `fn (Join $join): Join => $join->on(...)`. In Python, use `lambda j: j.on(...)`, but type-hint introspection is needed to detect the callback's expected parameter type (WhereGroup vs HavingGroup vs Join). Use `typing.get_type_hints()` and inspect annotations.

4. **No dedicated Database class required**: As specified, skip creating a full `Database` class. Instead, the adapter and dialect can be wired together directly in user code. But providing a `Database` facade as a convenience is recommended.

5. **Emulated ON CONFLICT and RETURNING**: PostgreSQL has native support for both. SQLite ≥ 3.24 has native ON CONFLICT, ≥ 3.35 has native RETURNING. Only emulate when the dialect reports the feature is unavailable.

6. **Callable debug callback**: Like the PHP version, accept an optional `debug: Callable[[str, float, Optional[str]], None]` to log queries with timing and errors.

7. **Fluent API returns `Self`**: All query builder methods return `Self` for method chaining.

8. **Condition group introspection**: The `_group()` method needs to inspect the callback to determine which group class to instantiate. In PHP this uses `ReflectionFunction`. In Python, use `inspect.signature(callback)` to get parameter type hints. The callback is expected to accept a `ConditionGroupABC` subclass (either `WhereGroup` or `HavingGroup`).

9. **Named to positional param conversion**: Unlike PHP's intricate `preg_replace_callback` pattern, Python can use a simpler regex approach since `re.sub` with a callback handles the complexities. The key regex must skip string literals (single-quoted, double-quoted, backtick-quoted) and comments (`--`, `/* */`, `#`).
