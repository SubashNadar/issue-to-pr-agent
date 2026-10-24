"""Runtime configuration, read from environment variables.

Secrets are required at startup. The process refuses to run without them,
rather than falling back to an insecure default.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping
import os


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    github_webhook_secret: str
    allowlist_path: str = "config/allowlist.json"
    audit_log_path: str = "data/audit.jsonl"
    trigger_label: str = "agent-fix"
    daily_reply_limit: int = 1

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> Settings:
        source = os.environ if env is None else env
        secret = source.get("GITHUB_WEBHOOK_SECRET", "").strip()
        if not secret:
            raise ConfigError("GITHUB_WEBHOOK_SECRET must be set")

        try:
            reply_limit = int(source.get("DAILY_REPLY_LIMIT", "1"))
        except ValueError as exc:
            raise ConfigError("DAILY_REPLY_LIMIT must be an integer") from exc
        if reply_limit < 0:
            raise ConfigError("DAILY_REPLY_LIMIT must be zero or more")

        return cls(
            github_webhook_secret=secret,
            allowlist_path=source.get("ALLOWLIST_PATH", "config/allowlist.json"),
            audit_log_path=source.get("AUDIT_LOG_PATH", "data/audit.jsonl"),
            trigger_label=source.get("TRIGGER_LABEL", "agent-fix"),
            daily_reply_limit=reply_limit,
        )
