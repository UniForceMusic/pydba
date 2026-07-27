from __future__ import annotations

from dataclasses import dataclass

from sentiencedb.query.enums.union import UnionEnum
from sentiencedb.query.select import SelectQuery


@dataclass
class Union:
    union: UnionEnum
    select_query: SelectQuery
