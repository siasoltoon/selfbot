from selfbot.capabilities import CapabilityService, PANEL_CAPABILITIES
from selfbot.db import Database
from selfbot.domain_store import DomainStore
from selfbot.panel import PanelService


EXPECTED_ROOTS = {
    "myoi_core": {
        "panel_diamond_transfer", "panel_personal_assistant", "panel_self_management",
        "panel_utility", "panel_calculator", "panel_ping", "panel_information",
        "panel_premium_clock", "panel_profile_photo", "panel_identity_clock",
        "panel_online_mode", "panel_action_mode",
    },
    "myoi_auto": {
        "panel_auto_cat", "panel_auto_meow", "panel_auto_transfer", "panel_auto_roulette",
        "panel_auto_fishing", "panel_auto_factory", "panel_auto_rescue",
        "panel_auto_robbery", "panel_auto_cook",
    },
    "security": {
        "panel_enemy", "panel_block", "panel_private_lock", "panel_absence",
        "panel_secretary", "panel_forced_join", "panel_mute", "panel_word_filter",
    },
    "content": {
        "panel_content", "panel_auto_reply", "panel_tag_members", "panel_group_management",
        "panel_chat_guard", "panel_auto_read", "panel_auto_reaction",
        "panel_first_comment", "panel_spam", "panel_sender", "panel_tabchi",
    },
    "tools": {
        "panel_translate", "panel_downloader", "panel_currency", "panel_delete",
        "panel_games", "panel_voice_search", "panel_tts", "panel_premium_emoji",
        "panel_stars_challenge", "panel_image_quality",
    },
}


def make_service():
    db = Database("sqlite+pysqlite:///:memory:")
    db.create_schema_for_tests()
    return db, CapabilityService(DomainStore(db))


def test_requested_panel_roots_are_complete_and_grouped():
    by_category = {}
    for item in PANEL_CAPABILITIES:
        if item.parent_id is None:
            by_category.setdefault(item.category_id, set()).add(item.capability_id)
    assert by_category == EXPECTED_ROOTS


def test_requested_panel_children_are_durable_and_owner_scoped():
    db, service = make_service()
    panel = PanelService(service)
    owner = "owner-a"
    assert service.is_enabled(owner, "panel_personal_assistant") is False
    assert service.set_enabled(owner, "panel_personal_assistant", True) is True
    assert service.is_enabled(owner, "panel_assistant_on") is False
    assert service.is_enabled("owner-b", "panel_assistant_on") is False

    service.set_enabled(owner, "panel_assistant_on", True)
    assert service.is_enabled(owner, "panel_assistant_on") is True
    service.set_enabled(owner, "panel_personal_assistant", False)
    assert service.is_enabled(owner, "panel_assistant_on") is False
    assert panel.children("panel_personal_assistant")

    db.engine.dispose()


def test_user_panel_does_not_remove_internal_capabilities():
    db, service = make_service()
    assert service.definition("ai").title == "هوش مصنوعی"
    assert service.definition("panel_translate").title == "🌐 ترجمه"
    db.engine.dispose()
