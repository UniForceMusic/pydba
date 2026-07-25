from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pydba.query.enums.union import UnionEnum

if TYPE_CHECKING:
    from pydba.query.select import SelectQuery

@dataclass
class Union:
    union: UnionEnum
    select_query: SelectQuery
