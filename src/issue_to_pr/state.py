"""In-process state: seen webhook deliveries and the triage job queue.

Both are in memory for this phase. A restart forgets them. That is acceptable
for development and is replaced by PostgreSQL before any real deployment.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from threading import Lock


class SeenDeliveries:
    """Remembers webhook delivery IDs so a redelivered event is handled once."""

    def __init__(self, max_size: int = 10_000) -> None:
        self._max_size = max_size
        self._seen: OrderedDict[str, None] = OrderedDict()
        self._lock = Lock()

    def first_time(self, key: str) -> bool:
        with self._lock:
            if key in self._seen:
                return False
            self._seen[key] = None
            while len(self._seen) > self._max_size:
                self._seen.popitem(last=False)
            return True


@dataclass(frozen=True)
class TriageJob:
    repo: str
    issue_number: int
    delivery_id: str


class JobQueue:
    def __init__(self) -> None:
        self._jobs: list[TriageJob] = []
        self._lock = Lock()

    def put(self, job: TriageJob) -> None:
        with self._lock:
            self._jobs.append(job)

    def snapshot(self) -> list[TriageJob]:
        with self._lock:
            return list(self._jobs)
