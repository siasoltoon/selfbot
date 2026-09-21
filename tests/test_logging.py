import json
import logging

from selfbot.logging import JsonFormatter, configure_logging, log_context


def test_context_redacts_sensitive_values():
    context = log_context(token="secret", user_id=42)

    assert context["token"] == "[REDACTED]"
    assert context["user_id"] == 42


def test_json_formatter_contains_structured_fields():
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.context = {"api_key": "secret", "operation": "ping"}

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["message"] == "hello"
    assert payload["context"]["api_key"] == "[REDACTED]"
    assert payload["context"]["operation"] == "ping"


def test_configure_logging_is_idempotent():
    root = logging.getLogger()
    before = len([h for h in root.handlers if getattr(h, "_selfbot_json", False)])

    configure_logging("INFO")
    configure_logging("INFO")

    after = len([h for h in root.handlers if getattr(h, "_selfbot_json", False)])
    assert after == max(1, before)
