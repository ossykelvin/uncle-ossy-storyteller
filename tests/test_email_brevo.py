"""Brevo email module tests (mocked — no real network/sends)."""
import core.email_brevo as eb


class _Resp:
    def __init__(self, status, body=None, text=""):
        self.status_code = status
        self._body = body or {}
        self.text = text

    def json(self):
        return self._body


def _enable(monkeypatch):
    monkeypatch.setattr(eb, "brevo_enabled", lambda: True)
    monkeypatch.setattr(eb, "BREVO_API_KEY", "test-key")
    monkeypatch.setattr(eb, "BREVO_SENDER_EMAIL", "noreply@example.com")
    monkeypatch.setattr(eb, "BREVO_SENDER_NAME", "Tester")


def test_send_email_success_returns_message_id(monkeypatch):
    _enable(monkeypatch)
    captured = {}

    def fake_post(url, json, headers, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["headers"] = headers
        return _Resp(201, {"messageId": "<abc@mailin.fr>"})

    monkeypatch.setattr(eb.requests, "post", fake_post)
    ok, msg = eb.send_email("u@example.com", "Hi", "<p>x</p>", to_name="U")
    assert ok is True and msg == "<abc@mailin.fr>"
    assert captured["json"]["to"] == [{"email": "u@example.com", "name": "U"}]
    assert captured["json"]["sender"]["email"] == "noreply@example.com"
    assert captured["headers"]["api-key"] == "test-key"


def test_send_email_error_status_returns_false(monkeypatch):
    _enable(monkeypatch)
    monkeypatch.setattr(eb.requests, "post", lambda *a, **k: _Resp(400, text="bad sender"))
    ok, msg = eb.send_email("u@example.com", "Hi", "<p>x</p>")
    assert ok is False and "400" in msg


def test_send_email_noop_when_not_configured(monkeypatch):
    monkeypatch.setattr(eb, "brevo_enabled", lambda: False)
    ok, msg = eb.send_email("u@example.com", "Hi", "<p>x</p>")
    assert ok is False and "not configured" in msg.lower()


def test_notify_signup_never_raises(monkeypatch):
    _enable(monkeypatch)

    def boom(*a, **k):
        raise RuntimeError("network down")

    monkeypatch.setattr(eb.requests, "post", boom)
    results = eb.notify_signup("u@example.com")  # must not raise
    assert set(results.keys()) == {"welcome", "admin"}
    assert results["welcome"][0] is False
