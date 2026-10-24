"""Decide what to do with an inbound email.

Order of checks matters:
1. Unauthenticated senders are dropped with no reply. Replying to a forged
   address would turn this system into a spam source.
2. Automated senders (bounces, no-reply, bulk mail) are dropped with no reply.
3. Allow-listed senders create an issue.
4. Anyone else gets the "not permitted" reply, at most once per day.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from threading import Lock

from .allowlist import AllowList
from .email_auth import parse_authentication_results, sender_authenticated

AUTOMATED_LOCAL_PARTS = frozenset({"no-reply", "noreply", "do-not-reply", "mailer-daemon", "postmaster"})
AUTOMATED_PRECEDENCE = frozenset({"bulk", "list", "junk"})


class IntakeAction(str, Enum):
    CREATE_ISSUE = "create_issue"
    REPLY_NOT_PERMITTED = "reply_not_permitted"
    DROP = "drop"


@dataclass(frozen=True)
class IntakeDecision:
    action: IntakeAction
    reason: str


class ReplyLimiter:
    """Allows at most `limit` replies per sender per day.

    In memory for this phase. A restart resets the counts, which is acceptable
    for now and will be replaced by persistent storage later.
    """

    def __init__(self, limit: int) -> None:
        self._limit = limit
        self._counts: dict[tuple[str, date], int] = {}
        self._lock = Lock()

    def allow(self, sender: str, today: date) -> bool:
        key = (sender.strip().casefold(), today)
        with self._lock:
            # Drop counts from earlier days so memory does not grow forever.
            self._counts = {k: v for k, v in self._counts.items() if k[1] == today}
            used = self._counts.get(key, 0)
            if used >= self._limit:
                return False
            self._counts[key] = used + 1
            return True


def _lower_headers(headers: dict[str, str]) -> dict[str, str]:
    return {k.strip().lower(): v for k, v in headers.items()}


def is_automated(sender: str, headers: dict[str, str]) -> bool:
    local_part = sender.rsplit("@", 1)[0].strip().casefold()
    if local_part in AUTOMATED_LOCAL_PARTS:
        return True

    lowered = _lower_headers(headers)
    if lowered.get("auto-submitted", "no").strip().casefold() != "no":
        return True
    return lowered.get("precedence", "").strip().casefold() in AUTOMATED_PRECEDENCE


def decide_email(
    sender: str,
    headers: dict[str, str],
    allowlist: AllowList,
    limiter: ReplyLimiter,
    today: date,
) -> IntakeDecision:
    auth_header = _lower_headers(headers).get("authentication-results")
    if not sender_authenticated(parse_authentication_results(auth_header), sender):
        return IntakeDecision(IntakeAction.DROP, "dropped:sender_not_authenticated")

    if is_automated(sender, headers):
        return IntakeDecision(IntakeAction.DROP, "dropped:automated_sender")

    if allowlist.email_allowed(sender):
        return IntakeDecision(IntakeAction.CREATE_ISSUE, "create:allow_listed")

    if limiter.allow(sender, today):
        return IntakeDecision(IntakeAction.REPLY_NOT_PERMITTED, "reply:not_allow_listed")

    return IntakeDecision(IntakeAction.DROP, "dropped:reply_limit_reached")
