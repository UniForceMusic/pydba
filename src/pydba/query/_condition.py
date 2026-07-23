from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydba.query.enums.condition import ConditionEnum
from pydba.query.enums.chain import ChainEnum


@dataclass
class Condition:
    """Represents a single WHERE/HAVING condition."""
    condition: ConditionEnum | str
    identifier: Any = None
    value: Any = None
    chain: ChainEnum = ChainEnum.AND
