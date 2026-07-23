from __future__ import annotations

from typing import Any, Optional

from pydba._query_with_params import QueryWithParams
from pydba.dialects._sql_dialect import SQLDialect
from pydba.query.enums.type import TypeEnum
from pydba.query._on_conflict import OnConflict
from pydba.query.expressions._sql import SqlABC
from pydba.exceptions import QueryError


class PgSQLDialect(SQLDialect):
    """PostgreSQL dialect implementation extending ANSI SQL dialect."""

    def __init__(self, version: str = "16", options: dict[str, Any] | None = None) -> None:
        super().__init__(version=version, options=options)
        self.bool = True
        self.distinct_on = True
        self.on_conflict = True
        self.returning = True
        self.lateral = True
        self.datetime_format = "%Y-%m-%d %H:%M:%S.%f"
        # Set version-gated capabilities
        self._version_gate()

    def _version_gate(self) -> None:
        """Set capability flags based on version."""
        v = self._version
        self.distinct_on = v >= 70200  # 7.2
        self.lateral = v >= 90300  # 9.3
        self.on_conflict = v >= 90500  # 9.5
        self.generated_by_default_as_identity = v >= 100000  # 10.0
        self.returning = v >= 80200  # 8.2

    def _build_on_conflict(
        self,
        query: list[str],
        params: list[Any],
        on_conflict: Optional[OnConflict],
        values: list[dict[str, Any]],
        last_insert_id: Optional[str],
    ) -> str:
        if on_conflict is None:
            return ""
        
        conflict_cols = on_conflict.conflict
        if isinstance(conflict_cols, str):
            conflict_cols = [conflict_cols]
        
        query.append(f" ON CONFLICT ({', '.join(self.escape_identifier(c) for c in conflict_cols)})")
        
        if on_conflict.updates is None:
            query.append(" DO NOTHING")
        elif not on_conflict.updates:
            # Update all columns from values
            if values:
                all_cols = list(values[0].keys())
                query.append(" DO UPDATE SET ")
                sets = []
                for col in all_cols:
                    sets.append(f"{self.escape_identifier(col)} = EXCLUDED.{self.escape_identifier(col)}")
                query.append(", ".join(sets))
        else:
            # Specific column updates
            query.append(" DO UPDATE SET ")
            sets = []
            for col, val in on_conflict.updates.items():
                if isinstance(val, str) and val.upper() == "EXCLUDED":
                    sets.append(f"{self.escape_identifier(col)} = EXCLUDED.{self.escape_identifier(col)}")
                else:
                    sets.append(f"{self.escape_identifier(col)} = ")
                    # Temporarily build the value
                    val_q = []
                    val_p: list = []
                    self._build_question_marks(val_q, val_p, val)
                    query.append("".join(val_q))
                    params.extend(val_p)
            query.append(", ".join(sets))
        
        return ""

    def _build_returning(self, query: list[str], returning: Optional[list[str]]) -> None:
        if returning is not None and returning:
            query.append(" RETURNING " + ", ".join(self.escape_identifier(c) for c in returning))

    def _build_condition_like(self, query: list[str], params: list[Any], cond: Any) -> None:
        if isinstance(cond.identifier, SqlABC):
            query.append(cond.identifier.raw_sql(self))
        else:
            query.append(self.escape_identifier(str(cond.identifier)))
        is_not = cond.condition.value.startswith("NOT ")
        if self._version >= 80400:  # PostgreSQL 8.4+ supports ILIKE
            query.append(f" {'NOT ' if is_not else ''}ILIKE ")
        else:
            query.append(f" {'NOT ' if is_not else ''}LIKE ")
        self._build_question_marks(query, params, cond.value)

    def _build_condition_regex(self, query: list[str], params: list[Any], cond: Any) -> None:
        is_not = cond.condition.value.startswith("NOT ")
        neg = "!" if is_not else ""
        
        if isinstance(cond.identifier, SqlABC):
            query.append(cond.identifier.raw_sql(self))
        else:
            query.append(self.escape_identifier(str(cond.identifier)))
        
        use_tilde = self.option("use_tilde_regex", False)
        if not use_tilde and self._version >= 150000:
            # PostgreSQL 15+ has regexp_like function
            query.append(f" {neg}~ ")
            self._build_question_marks(query, params, cond.value)
        else:
            # Use ~ operator
            query.append(f" {neg}~ ")
            self._build_question_marks(query, params, cond.value)

    def cast_bool(self, value: bool) -> bool | int:
        return value

    def parse_bool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value != 0
        if isinstance(value, str):
            return value.lower() in ("true", "1", "t", "yes", "on")
        return bool(value)

    def parse_datetime(self, value: Any) -> Any:
        from datetime import datetime
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            # Try with timezone offset first
            import re
            # Fix timezone offsets that are missing minutes (e.g., +02 instead of +02:00)
            fixed = re.sub(r'([+-]\d{2})$', r'\1:00', value)
            try:
                return datetime.strptime(fixed, self.datetime_format)
            except ValueError:
                try:
                    return datetime.fromisoformat(fixed)
                except ValueError:
                    return value
        return value

    def escape_string(self, string: str) -> str:
        # PostgreSQL style: double single quotes and escape backslashes
        result = string.replace("'", "''")
        result = result.replace("\\", "\\\\")
        return result

    def type(self, type_enum: TypeEnum, bits: Optional[int] = None) -> str:
        mapping = {
            TypeEnum.BOOL: "BOOLEAN",
            TypeEnum.INT: "INTEGER",
            TypeEnum.FLOAT: "DOUBLE PRECISION" if (bits or 0) > 32 else "REAL",
            TypeEnum.STRING: f"VARCHAR({bits or 255})",
            TypeEnum.DATETIME: "TIMESTAMP",
        }
        return mapping.get(type_enum, "VARCHAR(255)")
