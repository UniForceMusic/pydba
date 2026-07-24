from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class OnConflict:
    """Represents an ON CONFLICT (UPSERT) clause.

    - conflict: str or list of str - the conflict target column(s)
    - updates: None = DO NOTHING, empty dict = UPDATE ALL, populated dict = specific column updates
    """
    conflict: str | list[str]
    updates: dict[str, Any] | None = None  # None = do nothing
