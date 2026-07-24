from __future__ import annotations

from typing import Any

from pydba.result._base import ResultABC, ResultAbstract


def snapshot_result(result: ResultABC) -> Result:
    """Snapshot any ResultABC into an in-memory Result."""
    columns = result.columns()
    rows = result.fetch_dicts()
    return Result(columns=columns, rows=rows)


class Result(ResultAbstract):
    """In-memory result set using a list of dict rows."""
    
    def __init__(self, columns: dict[str, str], rows: list[dict[str, Any]] | None = None) -> None:
        self._columns = dict(columns)
        self._rows = list(rows) if rows else []
    
    def columns(self) -> dict[str, str]:
        return dict(self._columns)
    
    def fetch_dict(self) -> dict[str, Any] | None:
        if not self._rows:
            return None
        return self._rows.pop(0)

    def fetch_dicts(self) -> list[dict[str, Any]]:
        result = list(self._rows)
        self._rows.clear()
        return result
