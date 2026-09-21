import pytest
from selfbot.config import Settings
@pytest.fixture
def test_settings():
    return Settings(environment="test",log_level="INFO",database_url="sqlite:///:memory:",database_echo=False,telegram_api_id=None,telegram_api_hash=None,telegram_session=None,pc_worker_enabled=False,pc_worker_url=None,pc_worker_token=None)
