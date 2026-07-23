from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC


@dataclass
class QueryWithParams:
    """Represents a parameterized SQL query with its parameters."""
    
    query: str
    params: list[Any] = field(default_factory=list)

    def named_params_to_question_marks(self) -> QueryWithParams:
        """
        Convert :named parameters to ? positional parameters.
        The regex is careful to skip string literals.
        """
        # Pattern to match string literals or named params
        # Strategy: split on single-quoted strings, only replace outside them
        parts = re.split(r"('(?:[^']|'')*')", self.query)
        new_parts = []
        
        for idx, part in enumerate(parts):
            if idx % 2 == 0:
                # Outside string literal - replace :name with ?
                new_parts.append(re.sub(r":([a-zA-Z_][a-zA-Z0-9_]*)", "?", part))
            else:
                new_parts.append(part)
                
        return QueryWithParams(query="".join(new_parts), params=list(self.params))

    def to_sql(self, dialect: DialectABC) -> str:
        """
        Convert to a full SQL string by replacing ? placeholders
        with dialect-casted values.
        """
        import re
        parts = re.split(r"('(?:[^']|'')*')", self.query)
        new_parts = []
        param_idx = 0

        for idx, part in enumerate(parts):
            if idx % 2 == 0:
                # Outside string - replace ? with values
                while "?" in part and param_idx < len(self.params):
                    value = self.params[param_idx]
                    casted = dialect.cast_to_query(value)
                    part = part.replace("?", casted, 1)
                    param_idx += 1
                new_parts.append(part)
            else:
                new_parts.append(part)

        return "".join(new_parts)
