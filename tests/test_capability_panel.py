import pytest
from selfbot.capabilities import CapabilityService
from selfbot.db import Database
from selfbot.domain_store import DomainStore
from selfbot.errors import NotFoundError, ValidationError
from selfbot.panel_security import PanelTokenSigner


def make_service():
    db = Database("sqlite+pysqlite:///:memory:")
    db.create_schema_for_tests()
    return db, CapabilityService(DomainStore(db))


def test_capabilities_are_durable_and_owner_scoped():
    db, service = make_service()
    assert service.is_enabled("owner-a", "ai") is False
    assert service.set_enabled("owner-a", "ai", True) is True
    assert service.is_enabled("owner-a", "ai") is True
    assert service.is_enabled("owner-b", "ai") is False
    assert service.snapshot("owner-a")["ai"] is True
    db.engine.dispose()


def test_capability_validation():
    db, service = make_service()
    with pytest.raises(NotFoundError):
        service.set_enabled("owner-a", "missing", True)
    with pytest.raises(ValidationError):
        service.require("owner-a", "ai")
    db.engine.dispose()


def test_panel_token_is_authenticated_and_compact():
    signer = PanelTokenSigner("test-secret")
    token = signer.issue("123456789")
    assert signer.verify(token) == "123456789"
    assert signer.verify(token[:-1] + ("A" if token[-1] != "A" else "B")) is None
    assert len(token) < 64
