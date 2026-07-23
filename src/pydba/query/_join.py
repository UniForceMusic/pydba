from __future__ import annotations

from typing import Any, Optional
from dataclasses import dataclass, field

from pydba.query.enums.join import JoinEnum
from pydba.query.enums.chain import ChainEnum
from pydba.query._condition import Condition


@dataclass
class Join:
    """Represents a JOIN clause with optional ON conditions."""
    join: JoinEnum
    table: Any
    conditions: list[Condition | Any] = field(default_factory=list)

    def on(self, *conditions: Condition | Any) -> Join:
        """Add AND conditions to the JOIN."""
        for c in conditions:
            if hasattr(c, 'chain'):
                c.chain = ChainEnum.AND
            self.conditions.append(c)
        return self

    def or_on(self, *conditions: Condition | Any) -> Join:
        """Add OR conditions to the JOIN."""
        for c in conditions:
            if hasattr(c, 'chain'):
                c.chain = ChainEnum.OR
            self.conditions.append(c)
        return self
