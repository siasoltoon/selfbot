"""Structured application logging with secret-safe fields."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Mapping

SENSITIVE_KEYS = frozenset({
    "token",
    "password",
    "secret",
    "api_key",
    "api_hash",
    "session",
    "authorization",
})


def _redact(value: Any, key: str | None = None) -> Any:
    if key and key.lower() in SENSITIVE_KEYS:
        return "[REDACTED]"
    if isinstance(value, Mapping):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(v) for v in value]
    return value


class JsonFormatter(logging.Formatter):
    """Emit one structured JSON object per log record."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        context = getattr(record, "context", None)
        if context:
            payload["context"] = _redact(context)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(_redact(payload), ensure_ascii=False, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Configure the process root logger once with a JSON stream handler."""

    normalized = level.upper()
    if normalized not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        raise ValueError("invalid log level")

    root = logging.getLogger()
    root.setLevel(normalized)

    for handler in root.handlers:
        if getattr(handler, "_selfbot_json", False):
            handler.setLevel(normalized)
            return

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(normalized)
    handler.setFormatter(JsonFormatter())
    handler._selfbot_json = True
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_context(**values: Any) -> dict[str, Any]:
    """Return a redaction-ready context mapping for structured logging."""

    return _redact(values)
