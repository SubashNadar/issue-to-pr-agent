"""Who may start work, per channel.

Trust is an explicit list. Nothing is inferred from repository visibility,
email display names, or who can see an issue.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _norm_email(value: str) -> str:
    return value.strip().casefold()


def _norm_login(value: str) -> str:
    # GitHub logins are case-insensitive.
    return value.strip().casefold()


@dataclass(frozen=True)
class AllowList:
    emails: frozenset[str] = frozenset()
    github_authors: frozenset[str] = frozenset()
    github_maintainers: frozenset[str] = frozenset()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AllowList:
        return cls(
            emails=frozenset(_norm_email(e) for e in data.get("email", [])),
            github_authors=frozenset(_norm_login(u) for u in data.get("github_authors", [])),
            github_maintainers=frozenset(_norm_login(u) for u in data.get("github_maintainers", [])),
        )

    @classmethod
    def load(cls, path: str | Path) -> AllowList:
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))

    def email_allowed(self, address: str) -> bool:
        return _norm_email(address) in self.emails

    def github_author_allowed(self, login: str) -> bool:
        return _norm_login(login) in self.github_authors

    def github_maintainer(self, login: str) -> bool:
        return _norm_login(login) in self.github_maintainers
