from selfbot.config import ConfigurationError, load_settings


def test_defaults(monkeypatch):
    monkeypatch.delenv("SELF_BOT_ENV", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("PC_WORKER_ENABLED", raising=False)
    monkeypatch.delenv("PC_WORKER_URL", raising=False)
    monkeypatch.delenv("PC_WORKER_TOKEN", raising=False)

    settings = load_settings()

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.database_url.startswith("sqlite://")
    assert settings.pc_worker_enabled is False


def test_worker_requires_endpoint(monkeypatch):
    monkeypatch.setenv("PC_WORKER_ENABLED", "true")
    monkeypatch.delenv("PC_WORKER_URL", raising=False)
    monkeypatch.setenv("PC_WORKER_TOKEN", "secret")

    try:
        load_settings()
    except ConfigurationError as exc:
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
