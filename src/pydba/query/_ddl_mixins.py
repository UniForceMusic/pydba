from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

from pydba.query.enums.referential_action import ReferentialActionEnum
from pydba.query.enums.type import TypeEnum

if TYPE_CHECKING:
    pass


class IfNotExistsMixin:
    """Mixin providing if_not_exists() fluent API for DDL statements."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_if_not_exists'):
            self._if_not_exists: bool = False

    def if_not_exists(self) -> Self:
        self._if_not_exists = True
        return self


class IfExistsMixin:
    """Mixin providing if_exists() fluent API for DDL statements."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_if_exists'):
            self._if_exists: bool = False

    def if_exists(self) -> Self:
        self._if_exists = True
        return self


class PrimaryKeysMixin:
    """Mixin providing primary_keys() fluent API for DDL statements."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_primary_keys'):
            self._primary_keys: list[str] = []

    def primary_keys(self, columns: str | list[str]) -> Self:
        if isinstance(columns, str):
            columns = [columns]
        self._primary_keys = columns
        return self


class ConstraintsMixin:
    """Mixin providing constraint fluent API for DDL statements."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_constraints'):
            self._constraints: list = []

    def unique_constraint(self, columns: list, name: str | None = None) -> Self:
        self._constraints.append({
            "type": "unique",
            "columns": columns,
            "name": name,
        })
        return self

    def foreign_key_constraint(
        self,
        column: str,
        ref_table: str,
        ref_column: str,
        name: str | None = None,
        referential_actions: list | None = None,
    ) -> Self:
        on_delete: str | None = None
        on_update: str | None = None
        if referential_actions:
            for action in referential_actions:
                parts = str(action).split(' ', 2)
                if len(parts) == 3 and parts[0] == 'ON':
                    if parts[1] == 'DELETE':
                        on_delete = parts[2]
                    elif parts[1] == 'UPDATE':
                        on_update = parts[2]

        self._constraints.append({
            "type": "foreign_key",
            "columns": [column],
            "ref_table": ref_table,
            "ref_columns": [ref_column],
            "name": name,
            "on_delete": on_delete,
            "on_update": on_update,
        })
        return self

    def constraint(self, sql: str) -> Self:
        self._constraints.append(sql)
        return self


class ColumnsDefinitionMixin:
    """Mixin providing fluent column definition API for CREATE TABLE statements."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_columns'):
            self._columns: list = []
        if not hasattr(self, '_primary_keys'):
            self._primary_keys: list[str] = []

    def column(
        self,
        name: str,
        type_: TypeEnum | str,
        not_null: bool = False,
        default: Any = None,
        generated_by_default_as_identity: bool = False,
    ) -> Self:
        self._columns.append({
            "name": name,
            "type": type_,
            "not_null": not_null,
            "default": default,
            "auto_increment": generated_by_default_as_identity,
        })
        return self

    def auto_increment(self, name: str, bits: int = 64, add_primary_key: bool = True) -> Self:
        return self.identity(name, bits, add_primary_key)

    def identity(self, name: str, bits: int = 64, add_primary_key: bool = True) -> Self:
        if add_primary_key and name not in self._primary_keys:
            self._primary_keys.append(name)
        return self.int(name, bits, True, None, True)

    def bool(self, name: str, not_null: bool = False, default: bool | None = None) -> Self:
        return self.column(name, TypeEnum.BOOL, not_null, default)

    def int(
        self,
        name: str,
        bits: int = 64,
        not_null: bool = False,
        default: int | None = None,
        generated_by_default_as_identity: bool = False,
    ) -> Self:
        return self.column(name, TypeEnum.INT, not_null, default, generated_by_default_as_identity)

    def float(
        self,
        name: str,
        bits: int = 64,
        not_null: bool = False,
        default: float | None = None,
    ) -> Self:
        return self.column(name, TypeEnum.FLOAT, not_null, default)

    def string(
        self,
        name: str,
        size: int = 255,
        not_null: bool = False,
        default: str | None = None,
    ) -> Self:
        return self.column(name, TypeEnum.STRING, not_null, default)

    def text(self, name: str, not_null: bool = False, default: str | None = None) -> Self:
        return self.string(name, 0, not_null, default)

    def date_time(
        self,
        name: str,
        size: int = 6,
        not_null: bool = False,
        default: Any = None,
    ) -> Self:
        return self.column(name, TypeEnum.DATETIME, not_null, default)


class AltersMixin:
    """Mixin providing fluent ALTER TABLE operation API."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if not hasattr(self, '_alters'):
            self._alters: list = []

    def add_column(
        self,
        name: str,
        type_: TypeEnum | str,
        not_null: bool = False,
        default: Any = None,
        generated_by_default_as_identity: bool = False,
    ) -> Self:
        self._alters.append({
            "type": "add_column",
            "column": {
                "name": name,
                "type": type_,
                "not_null": not_null,
                "default": default,
                "auto_increment": generated_by_default_as_identity,
            },
        })
        return self

    def alter_column(self, column: str, sql: str) -> Self:
        self._alters.append({
            "type": "alter_column",
            "column": column,
            "sql": sql,
        })
        return self

    def rename_column(self, old: str, new: str) -> Self:
        self._alters.append({
            "type": "rename_column",
            "old_name": old,
            "new_name": new,
        })
        return self

    def drop_column(self, column: str) -> Self:
        self._alters.append({
            "type": "drop_column",
            "column": column,
        })
        return self

    def add_primary_keys(self, columns: str | list[str]) -> Self:
        if isinstance(columns, str):
            columns = [columns]
        self._alters.append({
            "type": "add_primary_key",
            "columns": columns,
        })
        return self

    def add_unique_constraint(self, columns: list, name: str | None = None) -> Self:
        self._alters.append({
            "type": "add_unique",
            "columns": columns,
            "name": name,
        })
        return self

    def add_foreign_key_constraint(
        self,
        column: str,
        ref_table: str,
        ref_column: str,
        name: str | None = None,
        referential_actions: list | None = None,
    ) -> Self:
        on_delete: str | None = None
        on_update: str | None = None
        if referential_actions:
            for action in referential_actions:
                parts = str(action).split(' ', 2)
                if len(parts) == 3 and parts[0] == 'ON':
                    if parts[1] == 'DELETE':
                        on_delete = parts[2]
                    elif parts[1] == 'UPDATE':
                        on_update = parts[2]

        self._alters.append({
            "type": "add_foreign_key",
            "columns": [column],
            "ref_table": ref_table,
            "ref_columns": [ref_column],
            "name": name,
            "on_delete": on_delete,
            "on_update": on_update,
        })
        return self

    def drop_constraint(self, constraint: str) -> Self:
        self._alters.append({
            "type": "drop_constraint",
            "name": constraint,
        })
        return self

    def alter(self, sql: str) -> Self:
        self._alters.append(sql)
        return self

    # --- Type convenience methods for add_column ---

    def add_auto_increment(self, name: str, bits: int = 64, add_primary_key: bool = True) -> Self:
        return self.add_identity(name, bits, add_primary_key)

    def add_identity(self, name: str, bits: int = 64, add_primary_key: bool = True) -> Self:
        if add_primary_key:
            self.add_primary_keys(name)
        return self.add_int(name, bits, True, None, True)

    def add_bool(self, name: str, not_null: bool = False, default: bool | None = None) -> Self:
        return self.add_column(name, TypeEnum.BOOL, not_null, default)

    def add_int(
        self,
        name: str,
        bits: int = 64,
        not_null: bool = False,
        default: int | None = None,
        generated_by_default_as_identity: bool = False,
    ) -> Self:
        return self.add_column(name, TypeEnum.INT, not_null, default, generated_by_default_as_identity)

    def add_float(
        self,
        name: str,
        bits: int = 64,
        not_null: bool = False,
        default: float | None = None,
    ) -> Self:
        return self.add_column(name, TypeEnum.FLOAT, not_null, default)

    def add_string(
        self,
        name: str,
        size: int = 255,
        not_null: bool = False,
        default: str | None = None,
    ) -> Self:
        return self.add_column(name, TypeEnum.STRING, not_null, default)

    def add_text(self, name: str, not_null: bool = False, default: str | None = None) -> Self:
        return self.add_string(name, 0, not_null, default)

    def add_date_time(
        self,
        name: str,
        size: int = 6,
        not_null: bool = False,
        default: Any = None,
    ) -> Self:
        return self.add_column(name, TypeEnum.DATETIME, not_null, default)