from __future__ import annotations

from dataclasses import dataclass

from pydba.query.enums.order_by_dir import OrderByDirectionEnum


@dataclass
class OrderBy:
    """Represents an ORDER BY clause entry."""
    column: str
    direction: OrderByDirectionEnum = OrderByDirectionEnum.ASC
