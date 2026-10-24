"""Sender verification for inbound email.

The From header is easy to forge. The receiving mail server records whether
SPF and DKIM passed in its Authentication-Results header. This module reads
that record and checks that the DKIM signing domain matches the sender.

Known limitation: a message forwarded by another server can fail SPF while
still being genuine. Such messages are dropped, not trusted, which is the
safe default.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_RESULT = re.compile(r"\b(spf|dkim)=(\w+)", re.IGNORECASE)
_DKIM_DOMAIN = re.compile(r"header\.d=([^\s;()]+)", re.IGNORECASE)


@dataclass(frozen=True)
class EmailAuthResult:
    spf: str | None = None
    dkim: str | None = None
    dkim_domains: tuple[str, ...] = field(default_factory=tuple)


def parse_authentication_results(header: str | None) -> EmailAuthResult:
    if not header:
        return EmailAuthResult()

    results: dict[str, str] = {}
    for match in _RESULT.finditer(header):
        # Keep the first result seen for each method.
        results.setdefault(match.group(1).lower(), match.group(2).lower())

    domains = tuple(m.group(1).strip("<>").lower() for m in _DKIM_DOMAIN.finditer(header))
    return EmailAuthResult(spf=results.get("spf"), dkim=results.get("dkim"), dkim_domains=domains)


def sender_authenticated(result: EmailAuthResult, from_address: str) -> bool:
    """True only when SPF and DKIM both pass, and a passing DKIM signature covers the sender's domain."""
    if result.spf != "pass" or result.dkim != "pass":
        return False
    if "@" not in from_address:
        return False

    sender_domain = from_address.rsplit("@", 1)[-1].strip().casefold()
    for signing_domain in result.dkim_domains:
        if sender_domain == signing_domain or sender_domain.endswith("." + signing_domain):
            return True
    return False
