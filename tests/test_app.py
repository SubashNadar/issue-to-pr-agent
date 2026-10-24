import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from issue_to_pr.allowlist import AllowList
from issue_to_pr.app import create_app
from issue_to_pr.audit import AuditLog
from issue_to_pr.config import ConfigError, Settings
from issue_to_pr.state import JobQueue, SeenDeliveries

SECRET = "webhook-secret"
ALLOWLIST = AllowList.from_dict(
    {"github_authors": ["reporter"], "github_maintainers": ["maintainer"]}
)


@pytest.fixture
def harness(tmp_path):
    audit_path = tmp_path / "audit.jsonl"
    queue = JobQueue()
    settings = Settings(github_webhook_secret=SECRET, audit_log_path=str(audit_path))
    app = create_app(settings, ALLOWLIST, AuditLog(audit_path), SeenDeliveries(), queue)
    return TestClient(app), queue, audit_path


def post(client, payload, *, delivery="d-1", event="issues", secret=SECRET):
    body = json.dumps(payload).encode()
    signature = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return client.post(
        "/webhooks/github",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-GitHub-Event": event,
            "X-GitHub-Delivery": delivery,
            "X-Hub-Signature-256": signature,
        },
    )


def labelled(author="reporter", labeller="maintainer", label="agent-fix"):
    return {
        "action": "labeled",
        "label": {"name": label},
        "issue": {"number": 7, "user": {"login": author}},
        "repository": {"full_name": "owner/repo"},
        "sender": {"login": labeller},
    }


def test_health_check(harness):
    client, _, _ = harness
    assert client.get("/healthz").json() == {"status": "ok"}


def test_rejects_bad_signature_with_401_and_queues_nothing(harness):
    client, queue, _ = harness
    response = post(client, labelled(), secret="wrong")
    assert response.status_code == 401
    assert queue.snapshot() == []


def test_valid_trigger_queues_one_job(harness):
    client, queue, _ = harness
    response = post(client, labelled())
    assert response.status_code == 202
    assert response.json()["status"] == "started"
    assert [(j.repo, j.issue_number) for j in queue.snapshot()] == [("owner/repo", 7)]


def test_redelivered_event_is_handled_once(harness):
    client, queue, _ = harness
    post(client, labelled(), delivery="same")
    response = post(client, labelled(), delivery="same")
    assert response.json()["status"] == "duplicate"
    assert len(queue.snapshot()) == 1


def test_non_maintainer_label_is_denied_and_not_queued(harness):
    client, queue, _ = harness
    response = post(client, labelled(labeller="random"))
    assert response.json()["reason"] == "denied:labeller_not_maintainer"
    assert queue.snapshot() == []


def test_issue_from_stranger_is_ignored_with_202(harness):
    client, queue, _ = harness
    response = post(client, labelled(author="stranger"))
    assert response.status_code == 202
    assert response.json()["status"] == "ignored"
    assert queue.snapshot() == []


def test_missing_delivery_id_is_rejected(harness):
    client, _, _ = harness
    body = json.dumps(labelled()).encode()
    signature = "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    response = client.post(
        "/webhooks/github",
        content=body,
        headers={"X-GitHub-Event": "issues", "X-Hub-Signature-256": signature},
    )
    assert response.status_code == 400


def test_signed_but_invalid_json_is_rejected(harness):
    client, _, _ = harness
    body = b"not json"
    signature = "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    response = client.post(
        "/webhooks/github",
        content=body,
        headers={"X-GitHub-Event": "issues", "X-GitHub-Delivery": "d-x", "X-Hub-Signature-256": signature},
    )
    assert response.status_code == 400


def test_every_decision_is_audited_without_issue_text(harness):
    client, _, audit_path = harness
    post(client, labelled(), delivery="a")
    post(client, labelled(labeller="random"), delivery="b")
    post(client, labelled(), delivery="c", secret="wrong")
    lines = [json.loads(line) for line in audit_path.read_text().splitlines()]
    assert [entry["outcome"] for entry in lines] == ["started", "denied", "rejected"]
    assert all("title" not in entry and "body" not in entry for entry in lines)


class TestSettings:
    def test_requires_webhook_secret(self):
        with pytest.raises(ConfigError):
            Settings.from_env({})

    def test_reads_values_from_environment(self):
        settings = Settings.from_env({"GITHUB_WEBHOOK_SECRET": "s", "DAILY_REPLY_LIMIT": "3"})
        assert settings.github_webhook_secret == "s"
        assert settings.daily_reply_limit == 3
        assert settings.trigger_label == "agent-fix"

    def test_rejects_non_integer_reply_limit(self):
        with pytest.raises(ConfigError):
            Settings.from_env({"GITHUB_WEBHOOK_SECRET": "s", "DAILY_REPLY_LIMIT": "many"})
