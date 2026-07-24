from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydba.query.enums.chain import ChainEnum
from pydba.query.enums.condition import ConditionEnum


@dataclass
class Condition:
    """Represents a single WHERE/HAVING condition."""
    condition: ConditionEnum | str
    identifier: Any = None
    value: Any = None
    chain: ChainEnum = ChainEnum.AND
