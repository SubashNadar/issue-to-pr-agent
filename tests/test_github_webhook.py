import hashlib
import hmac

from issue_to_pr.allowlist import AllowList
from issue_to_pr.github_webhook import decide_issue_event, verify_signature

SECRET = "test-secret"
ALLOWLIST = AllowList.from_dict(
    {
        "github_authors": ["Reporter-One"],
        "github_maintainers": ["Maintainer-One"],
    }
)


def sign(body: bytes, secret: str = SECRET) -> str:
    return "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def labelled_event(author="reporter-one", labeller="maintainer-one", label="agent-fix"):
    return {
        "action": "labeled",
        "label": {"name": label},
        "issue": {"number": 42, "user": {"login": author}},
        "repository": {"full_name": "owner/repo"},
        "sender": {"login": labeller},
    }


class TestSignature:
    def test_accepts_correct_signature(self):
        body = b'{"action":"opened"}'
        assert verify_signature(SECRET, body, sign(body))

    def test_rejects_wrong_secret(self):
        body = b"{}"
        assert not verify_signature(SECRET, body, sign(body, secret="other"))

    def test_rejects_tampered_body(self):
        assert not verify_signature(SECRET, b"{\"x\":2}", sign(b"{\"x\":1}"))

    def test_rejects_missing_or_malformed_header(self):
        assert not verify_signature(SECRET, b"{}", None)
        assert not verify_signature(SECRET, b"{}", "")
        assert not verify_signature(SECRET, b"{}", "md5=abc")


class TestDecision:
    def test_starts_for_allow_listed_author_and_maintainer_label(self):
        decision = decide_issue_event("issues", labelled_event(), ALLOWLIST, "agent-fix")
        assert decision.start
        assert decision.issue_number == 42
        assert decision.repo == "owner/repo"

    def test_ignores_other_labels(self):
        decision = decide_issue_event("issues", labelled_event(label="bug"), ALLOWLIST, "agent-fix")
        assert not decision.start
        assert decision.reason == "ignored:other_label"

    def test_ignores_non_issue_events(self):
        decision = decide_issue_event("pull_request", labelled_event(), ALLOWLIST, "agent-fix")
        assert not decision.start
        assert decision.reason == "ignored:not_issue_event"

    def test_ignores_actions_other_than_labelled(self):
        event = labelled_event()
        event["action"] = "opened"
        decision = decide_issue_event("issues", event, ALLOWLIST, "agent-fix")
        assert decision.reason == "ignored:not_labeled_action"

    def test_denies_label_added_by_non_maintainer(self):
        decision = decide_issue_event(
            "issues", labelled_event(labeller="random-user"), ALLOWLIST, "agent-fix"
        )
        assert not decision.start
        assert decision.reason == "denied:labeller_not_maintainer"

    def test_ignores_issue_from_author_not_allow_listed(self):
        decision = decide_issue_event(
            "issues", labelled_event(author="stranger"), ALLOWLIST, "agent-fix"
        )
        assert not decision.start
        assert decision.reason == "ignored:author_not_allowed"

    def test_login_matching_is_case_insensitive(self):
        decision = decide_issue_event(
            "issues",
            labelled_event(author="REPORTER-ONE", labeller="MAINTAINER-one"),
            ALLOWLIST,
            "agent-fix",
        )
        assert decision.start

    def test_handles_missing_fields_without_crashing(self):
        decision = decide_issue_event("issues", {"action": "labeled"}, ALLOWLIST, "agent-fix")
        assert not decision.start
