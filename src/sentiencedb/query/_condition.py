from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sentiencedb.query.enums.chain import ChainEnum
from sentiencedb.query.enums.condition import ConditionEnum


@dataclass
class Condition:
    condition: ConditionEnum | str
    identifier: str | list[str] | None = None
    value: Any = None
    chain: ChainEnum = ChainEnum.AND
    cast: bool = False
