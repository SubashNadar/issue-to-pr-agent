"""HTTP entry point: the GitHub webhook receiver.

Responses are deliberate:
- 401 for a bad signature, so a forged request is clearly rejected.
- 400 for a request that is signed but malformed.
- 202 for everything else, including ignored events, so GitHub does not retry them.
"""

from __future__ import annotations

import json
import os
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .allowlist import AllowList
from .audit import AuditLog
from .config import Settings
from .github_webhook import decide_issue_event, verify_signature
from .state import JobQueue, SeenDeliveries, TriageJob


def create_app(
    settings: Settings,
    allowlist: AllowList,
    audit: AuditLog,
    seen: SeenDeliveries,
    queue: JobQueue,
) -> FastAPI:
    app = FastAPI(title="issue-to-pr-agent", version="0.1.0")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/webhooks/github", status_code=202)
    async def github_webhook(request: Request) -> Any:
        body = await request.body()
        delivery = request.headers.get("X-GitHub-Delivery", "")
        event = request.headers.get("X-GitHub-Event", "")

        if not verify_signature(settings.github_webhook_secret, body, request.headers.get("X-Hub-Signature-256")):
            audit.record("github", "rejected", "signature_invalid", delivery=delivery)
            return JSONResponse({"status": "rejected"}, status_code=401)

        if not delivery:
            return JSONResponse({"status": "rejected", "reason": "missing_delivery_id"}, status_code=400)

        if not seen.first_time(delivery):
            return {"status": "duplicate"}

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            audit.record("github", "rejected", "invalid_json", delivery=delivery)
            return JSONResponse({"status": "rejected", "reason": "invalid_json"}, status_code=400)

        decision = decide_issue_event(event, payload, allowlist, settings.trigger_label)
        if decision.start:
            outcome = "started"
        elif decision.reason.startswith("denied:"):
            # A denial means someone without rights tried to start work. Keep it distinct in the audit log.
            outcome = "denied"
        else:
            outcome = "ignored"
        audit.record(
            "github",
            outcome,
            decision.reason,
            delivery=delivery,
            repo=decision.repo,
            issue=decision.issue_number,
        )

        if decision.start and decision.repo and decision.issue_number is not None:
            queue.put(TriageJob(decision.repo, decision.issue_number, delivery))

        return {"status": outcome, "reason": decision.reason}

    return app


def create_app_from_env() -> FastAPI:
    """Factory for `uvicorn issue_to_pr.app:create_app_from_env --factory`."""
    settings = Settings.from_env()
    allowlist_path = settings.allowlist_path
    if not os.path.exists(allowlist_path):
        raise RuntimeError(f"allow-list not found at {allowlist_path}; copy config/allowlist.example.json")
    return create_app(
        settings=settings,
        allowlist=AllowList.load(allowlist_path),
        audit=AuditLog(settings.audit_log_path),
        seen=SeenDeliveries(),
        queue=JobQueue(),
    )
