from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC


# Regex that matches string literals, comments, bracket expressions, and
# the two token types we care about: ? placeholders (group 1) and :named
# parameters (group 2).  Everything else (literals, comments, etc.) is
# matched by the first alternative and returned verbatim by re.sub.
#
# Ported from the PHP reference implementation in SentienceDatabase.
REGEX_PATTERN = re.compile(
    r"""(?x)
    (?:
        '(?:\\.|[^\\'])*'
        |"(?:\\.|[^\\"])*"
        |`(?:\\.|[^\\`])*`
        |\[(?:\\.|[^\[\]])*?\]
        |--[^\r\n]*
        |/\*[\s\S]*?\*/
        |\#.*
    )
    |
    (\?)
    |
    (?<!\:)(\:\w+)
    (?=
        (?:
            [^'"`\[\]]
            |'(?:\\.|[^\\'])*'
            |"(?:\\.|[^\\"])*"
            |`(?:\\.|[^\\`])*`
            |\[(?:\\.|[^\[\]])*?\]
        )*$
    )
    """,
    re.MULTILINE,
)


@dataclass
class QueryWithParams:
    """Represents a parameterized SQL query with its parameters."""

    query: str
    params: list[Any] = field(default_factory=list)

    def named_params_to_question_marks(self) -> QueryWithParams:
        """
        Convert :named parameters to ? positional parameters.

        The regex skips string literals, comments, and bracket expressions
        so that :word inside 'literal', "literal", `` `literal` ``, etc. is
        never mistaken for a named parameter.
        """
        def _replacer(match: re.Match[str]) -> str:
            # Group 2 captures :named parameters
            if match.group(2) is not None:
                return "?"
            # Everything else (literals, comments, ?, etc.) is returned unchanged
            return match.group(0)

        query = REGEX_PATTERN.sub(_replacer, self.query)
        return QueryWithParams(query=query, params=list(self.params))

    def to_sql(self, dialect: DialectABC) -> str:
        """
        Convert to a full SQL string by replacing ? placeholders
        with dialect-casted values.

        String literals, comments, and bracket expressions are left
        intact so that a literal '?' inside a string is never replaced.
        """
        param_idx: list[int] = [0]

        def _replacer(match: re.Match[str]) -> str:
            # Group 1 captures ? placeholders
            if match.group(1) is not None:
                idx = param_idx[0]
                if idx < len(self.params):
                    value = self.params[idx]
                    casted = dialect.cast_to_query(value)
                    param_idx[0] += 1
                    return casted
                # If we run out of params, return ? unchanged
                return "?"
            # Everything else (literals, comments, :named params, etc.)
            return match.group(0)

        return REGEX_PATTERN.sub(_replacer, self.query)