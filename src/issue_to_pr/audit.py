"""Append-only audit log, one JSON object per line.

Entries record what was decided and why. They never contain message bodies,
issue text, or secrets. Callers pass only the identifiers they need.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any


class AuditLog:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._lock = Lock()

    def record(self, channel: str, outcome: str, reason: str, **details: Any) -> None:
        entry = {
            "ts": datetime.now(UTC).isoformat(),
            "channel": channel,
            "outcome": outcome,
            "reason": reason,
            **details,
        }
        line = json.dumps(entry, sort_keys=True, default=str)
        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
