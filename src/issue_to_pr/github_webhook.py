"""GitHub webhook verification and the decision to start work.

A webhook starts work only when all of these hold:
1. The request is signed with the shared secret.
2. It is an issue event, the action is "labeled", and the label is the trigger label.
3. The person who added the label is a listed maintainer.
4. The issue author is allow-listed.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Any

from .allowlist import AllowList


def verify_signature(secret: str, body: bytes, signature_header: str | None) -> bool:
    """Check GitHub's X-Hub-Signature-256 header against the raw request body."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


@dataclass(frozen=True)
class Decision:
    start: bool
    reason: str
    repo: str | None = None
    issue_number: int | None = None


def decide_issue_event(
    event: str,
    payload: dict[str, Any],
    allowlist: AllowList,
    trigger_label: str,
) -> Decision:
    """Decide whether an already-verified webhook should start triage."""
    repo = (payload.get("repository") or {}).get("full_name")
    issue = payload.get("issue") or {}
    number = issue.get("number")

    if event != "issues":
        return Decision(False, "ignored:not_issue_event", repo, number)
    if payload.get("action") != "labeled":
        return Decision(False, "ignored:not_labeled_action", repo, number)
    if (payload.get("label") or {}).get("name") != trigger_label:
        return Decision(False, "ignored:other_label", repo, number)

    labeller = (payload.get("sender") or {}).get("login", "")
    if not allowlist.github_maintainer(labeller):
        return Decision(False, "denied:labeller_not_maintainer", repo, number)

    author = (issue.get("user") or {}).get("login", "")
    if not allowlist.github_author_allowed(author):
        return Decision(False, "ignored:author_not_allowed", repo, number)

    return Decision(True, "start", repo, number)
