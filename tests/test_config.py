from selfbot.config import load_settings
from selfbot.errors import ConfigurationError


def test_defaults(monkeypatch):
    for key in [
        "SELF_BOT_ENV",
        "LOG_LEVEL",
        "DATABASE_URL",
        "DATABASE_ECHO",
        "PC_WORKER_ENABLED",
        "PC_WORKER_URL",
        "PC_WORKER_TOKEN",
    ]:
        monkeypatch.delenv(key, raising=False)

    settings = load_settings()

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.database_url.startswith("sqlite://")
    assert settings.database_echo is False
    assert settings.pc_worker_enabled is False


def test_worker_requires_endpoint(monkeypatch):
    monkeypatch.setenv("PC_WORKER_ENABLED", "true")
    monkeypatch.delenv("PC_WORKER_URL", raising=False)
    monkeypatch.setenv("PC_WORKER_TOKEN", "secret")

    try:
        load_settings()
    except ConfigurationError as exc:
        assert exc.code == "configuration"
        assert "PC_WORKER_URL" in str(exc)
    else:
        raise AssertionError("expected ConfigurationError")


def test_invalid_boolean(monkeypatch):
    monkeypatch.setenv("PC_WORKER_ENABLED", "maybe")

    try:
        load_settings()
    except ConfigurationError as exc:
        assert "PC_WORKER_ENABLED" in str(exc)
    else:
        raise AssertionError("expected ConfigurationError")


def test_invalid_database_scheme(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql://example")

    try:
        load_settings()
    except ConfigurationError as exc:
        assert "SQLite or PostgreSQL" in str(exc)
    else:
        raise AssertionError("expected ConfigurationError")
