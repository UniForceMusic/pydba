from __future__ import annotations

from dataclasses import dataclass

from sentiencedb.query.enums.order_by_dir import OrderByDirectionEnum


@dataclass
class OrderBy:
    column: str
    direction: OrderByDirectionEnum = OrderByDirectionEnum.ASC
