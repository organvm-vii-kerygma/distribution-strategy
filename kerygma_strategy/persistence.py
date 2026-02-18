"""JSON file persistence with atomic writes.

Provides a JsonStore class for safely reading/writing JSON data
to disk with atomic os.replace to prevent corruption.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


class JsonStore:
    """Persistent JSON key-value store with atomic writes."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path
        self._data: dict[str, Any] = {}
        if path and path.exists():
            self._load()

    def _load(self) -> None:
        if not self._path or not self._path.exists():
            return
        try:
            self._data = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, TypeError):
            self._data = {}

    def save(self) -> None:
        """Write data to disk atomically."""
        if not self._path:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self._data, indent=2, default=str), encoding="utf-8")
        os.replace(str(tmp), str(self._path))

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def keys(self) -> list[str]:
        return list(self._data.keys())

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    @classmethod
    def from_dict(cls, data: dict[str, Any], path: Path | None = None) -> JsonStore:
        store = cls(path=None)
        store._data = dict(data)
        store._path = path
        return store

    @property
    def is_persistent(self) -> bool:
        return self._path is not None
