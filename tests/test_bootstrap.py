from selfbot.bootstrap import create_runtime


def test_create_runtime(monkeypatch, tmp_path):
    monkeypatch.setenv("SELF_BOT_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'runtime.db'}")
    monkeypatch.delenv("PC_WORKER_ENABLED", raising=False)

    runtime = create_runtime()

    assert runtime.settings.environment == "test"
    assert runtime.database.ping() is True
