"""Glue between decisions and side effects.

The decision functions are pure. This module calls the sinks that do the real
work (create an issue, send a reply) and records every outcome in the audit log.
Sinks are protocols, so tests and dry runs use fakes, and the real GitHub and
Gmail clients plug in later without changing this logic.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol

from .allowlist import AllowList
from .audit import AuditLog
from .intake import IntakeAction, IntakeDecision, ReplyLimiter, decide_email

NOT_PERMITTED_TEXT = "You are not permitted to raise issues through this channel."


class IssueSink(Protocol):
    def create_issue(self, sender: str, subject: str, body: str) -> str:
        """Create a repository issue and return its URL."""
        ...


class ReplySink(Protocol):
    def send(self, to: str, subject: str, body: str) -> None:
        """Send a reply to an email address."""
        ...


def handle_email(
    sender: str,
    subject: str,
    body: str,
    headers: dict[str, str],
    *,
    allowlist: AllowList,
    limiter: ReplyLimiter,
    issues: IssueSink,
    replies: ReplySink,
    audit: AuditLog,
    today: date,
) -> IntakeDecision:
    decision = decide_email(sender, headers, allowlist, limiter, today)

    if decision.action is IntakeAction.CREATE_ISSUE:
        issue_url = issues.create_issue(sender=sender, subject=subject, body=body)
        audit.record("email", "created", decision.reason, sender=sender, issue_url=issue_url)
    elif decision.action is IntakeAction.REPLY_NOT_PERMITTED:
        replies.send(to=sender, subject=f"Re: {subject}", body=NOT_PERMITTED_TEXT)
        audit.record("email", "replied", decision.reason, sender=sender)
    else:
        audit.record("email", "dropped", decision.reason, sender=sender)

    return decision
