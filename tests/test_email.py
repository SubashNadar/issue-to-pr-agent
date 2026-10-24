from datetime import date

from issue_to_pr.allowlist import AllowList
from issue_to_pr.email_auth import parse_authentication_results, sender_authenticated
from issue_to_pr.intake import IntakeAction, ReplyLimiter, decide_email, is_automated
from issue_to_pr.pipeline import NOT_PERMITTED_TEXT, handle_email
from issue_to_pr.audit import AuditLog

TODAY = date(2026, 10, 24)
GOOD_AUTH = (
    "mx.google.com; dkim=pass header.i=@reporter.example header.d=reporter.example; "
    "spf=pass (google.com: domain of a@reporter.example designates 203.0.113.5) "
    "smtp.mailfrom=a@reporter.example"
)
ALLOWLIST = AllowList.from_dict({"email": ["Reporter@Reporter.example"]})


def headers(auth=GOOD_AUTH, **extra):
    base = {"Authentication-Results": auth} if auth is not None else {}
    base.update(extra)
    return base


class TestAuthenticationResults:
    def test_passes_when_spf_and_aligned_dkim_pass(self):
        result = parse_authentication_results(GOOD_AUTH)
        assert sender_authenticated(result, "a@reporter.example")

    def test_subdomain_of_signing_domain_is_accepted(self):
        result = parse_authentication_results(GOOD_AUTH)
        assert sender_authenticated(result, "team@mail.reporter.example")

    def test_rejects_spf_fail(self):
        header = GOOD_AUTH.replace("spf=pass", "spf=fail")
        assert not sender_authenticated(parse_authentication_results(header), "a@reporter.example")

    def test_rejects_dkim_fail(self):
        header = GOOD_AUTH.replace("dkim=pass", "dkim=fail")
        assert not sender_authenticated(parse_authentication_results(header), "a@reporter.example")

    def test_rejects_dkim_signed_by_unrelated_domain(self):
        header = GOOD_AUTH.replace("header.d=reporter.example", "header.d=attacker.example")
        assert not sender_authenticated(parse_authentication_results(header), "a@reporter.example")

    def test_rejects_missing_header(self):
        assert not sender_authenticated(parse_authentication_results(None), "a@reporter.example")


class TestAutomatedDetection:
    def test_known_automated_local_parts(self):
        assert is_automated("no-reply@example.com", {})
        assert is_automated("mailer-daemon@example.com", {})

    def test_auto_submitted_header(self):
        assert is_automated("a@example.com", {"Auto-Submitted": "auto-replied"})

    def test_bulk_precedence(self):
        assert is_automated("a@example.com", {"Precedence": "bulk"})

    def test_normal_person_is_not_automated(self):
        assert not is_automated("a@example.com", {"Auto-Submitted": "no"})


class TestIntakeDecision:
    def test_unauthenticated_sender_is_dropped_without_reply(self):
        decision = decide_email(
            "reporter@example.com", headers(auth=None), ALLOWLIST, ReplyLimiter(1), TODAY
        )
        assert decision.action is IntakeAction.DROP
        assert decision.reason == "dropped:sender_not_authenticated"

    def test_allow_listed_authenticated_sender_creates_issue(self):
        decision = decide_email(
            "reporter@reporter.example", headers(), ALLOWLIST, ReplyLimiter(1), TODAY
        )
        assert decision.action is IntakeAction.CREATE_ISSUE

    def test_unknown_sender_gets_one_reply_per_day(self):
        limiter = ReplyLimiter(1)
        first = decide_email("a@reporter.example", headers(), ALLOWLIST, limiter, TODAY)
        second = decide_email("a@reporter.example", headers(), ALLOWLIST, limiter, TODAY)
        assert first.action is IntakeAction.REPLY_NOT_PERMITTED
        assert second.action is IntakeAction.DROP
        assert second.reason == "dropped:reply_limit_reached"

    def test_reply_limit_resets_on_a_new_day(self):
        limiter = ReplyLimiter(1)
        decide_email("a@reporter.example", headers(), ALLOWLIST, limiter, TODAY)
        tomorrow = decide_email("a@reporter.example", headers(), ALLOWLIST, limiter, date(2026, 10, 25))
        assert tomorrow.action is IntakeAction.REPLY_NOT_PERMITTED

    def test_automated_sender_gets_no_reply_even_if_authenticated(self):
        decision = decide_email(
            "no-reply@reporter.example", headers(), ALLOWLIST, ReplyLimiter(1), TODAY
        )
        assert decision.action is IntakeAction.DROP
        assert decision.reason == "dropped:automated_sender"

    def test_spoofed_allow_listed_address_is_not_trusted(self):
        # Allow-listed address, but the mail was not authenticated for that domain.
        spoofed = headers(auth="mx.google.com; dkim=none; spf=fail")
        decision = decide_email("reporter@reporter.example", spoofed, ALLOWLIST, ReplyLimiter(1), TODAY)
        assert decision.action is IntakeAction.DROP


class FakeIssues:
    def __init__(self):
        self.created = []

    def create_issue(self, sender, subject, body):
        self.created.append((sender, subject))
        return "https://example.invalid/issues/1"


class FakeReplies:
    def __init__(self):
        self.sent = []

    def send(self, to, subject, body):
        self.sent.append((to, subject, body))


class TestPipeline:
    def run(self, sender, issues, replies, audit, limiter=None):
        return handle_email(
            sender,
            "Login broken",
            "Steps...",
            headers(),
            allowlist=ALLOWLIST,
            limiter=limiter or ReplyLimiter(1),
            issues=issues,
            replies=replies,
            audit=audit,
            today=TODAY,
        )

    def test_allowed_sender_creates_issue_and_no_reply(self, tmp_path):
        issues, replies = FakeIssues(), FakeReplies()
        self.run("reporter@reporter.example", issues, replies, AuditLog(tmp_path / "a.jsonl"))
        assert len(issues.created) == 1
        assert replies.sent == []

    def test_unknown_sender_gets_exact_generic_message(self, tmp_path):
        issues, replies = FakeIssues(), FakeReplies()
        self.run("stranger@reporter.example", issues, replies, AuditLog(tmp_path / "a.jsonl"))
        assert issues.created == []
        assert replies.sent == [("stranger@reporter.example", "Re: Login broken", NOT_PERMITTED_TEXT)]

    def test_every_outcome_is_audited(self, tmp_path):
        import json

        log = tmp_path / "a.jsonl"
        issues, replies = FakeIssues(), FakeReplies()
        self.run("reporter@reporter.example", issues, replies, AuditLog(log))
        self.run("stranger@reporter.example", issues, replies, AuditLog(log))
        entries = [json.loads(line) for line in log.read_text().splitlines()]
        assert [e["outcome"] for e in entries] == ["created", "replied"]
        assert all("body" not in e for e in entries)
