from selfbot.capabilities import CapabilityService
from selfbot.domain_store import DomainStore
from selfbot.db import Database
from selfbot.panel import PanelService


def test_panel_has_hierarchical_categories_and_children():
    db = Database("sqlite+pysqlite:///:memory:")
    db.create_schema_for_tests()
    service = CapabilityService(DomainStore(db))
    panel = PanelService(service)

    category_ids = {item.category_id for item in panel.categories()}
    assert {"myoi_core", "myoi_auto", "security", "content", "tools"} <= category_ids
    assert panel.children("ai")
    assert {item.capability_id for item in panel.children("ai")} >= {"ai_chat", "ai_summarize", "ai_translate", "ai_context"}
    db.engine.dispose()


def test_parent_disable_cascades_to_real_children():
    db = Database("sqlite+pysqlite:///:memory:")
    db.create_schema_for_tests()
    service = CapabilityService(DomainStore(db))

    service.set_enabled("owner", "ai", True)
    service.set_enabled("owner", "ai_chat", True)
    assert service.is_enabled("owner", "ai_chat")

    service.set_enabled("owner", "ai", False)
    assert not service.is_enabled("owner", "ai")
    assert not service.is_enabled("owner", "ai_chat")
    db.engine.dispose()


def test_core_security_and_tasks_remain_enabled():
    db = Database("sqlite+pysqlite:///:memory:")
    db.create_schema_for_tests()
    service = CapabilityService(DomainStore(db))

    assert service.is_enabled("owner", "security")
    assert service.is_enabled("owner", "tasks")
    db.engine.dispose()
