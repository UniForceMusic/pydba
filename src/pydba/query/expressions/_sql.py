from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from pydba.dialects._base import DialectABC


class SqlABC(ABC):
    """Abstract base class for all SQL expressions."""
    
    @abstractmethod
    def sql(self, dialect: DialectABC) -> str:
        """Return parameterized SQL with ? placeholders."""
        ...
    
    @abstractmethod
    def params(self, dialect: DialectABC) -> list[Any]:
        """Return list of parameter values."""
        ...
    
    @abstractmethod
    def raw_sql(self, dialect: DialectABC) -> str:
        """Return fully interpolated SQL string."""
        ...
