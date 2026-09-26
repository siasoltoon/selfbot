"""Professional Telegram panel domain model.

This module contains navigation metadata only; Telegram rendering remains in the
adapter so the core panel design stays deployment- and transport-agnostic.
"""
from __future__ import annotations

from dataclasses import dataclass

from .capabilities import CapabilityDefinition, CapabilityService


@dataclass(frozen=True, slots=True)
class PanelCategory:
    category_id: str
    title: str
    description: str
    capability_ids: tuple[str, ...]


PANEL_CATEGORIES: tuple[PanelCategory, ...] = (
    PanelCategory("myoi_core", "🐱 بازی میویی", "قابلیت‌های اصلی حساب و بازی میویی", (
        "panel_diamond_transfer", "panel_personal_assistant", "panel_self_management",
        "panel_utility", "panel_calculator", "panel_ping", "panel_information",
        "panel_premium_clock", "panel_profile_photo", "panel_identity_clock",
        "panel_online_mode", "panel_action_mode",
    )),
    PanelCategory("myoi_auto", "🤖 خودکارهای میویی", "اتوماسیون پیشی، میو، انتقال، رولت، ماهی‌گیری، کارخانه، نجات، سرقت و آشپز", (
        "panel_auto_cat", "panel_auto_meow", "panel_auto_transfer", "panel_auto_roulette",
        "panel_auto_fishing", "panel_auto_factory", "panel_auto_rescue",
        "panel_auto_robbery", "panel_auto_cook",
    )),
    PanelCategory("security", "🛡 دشمن و امنیت", "کنترل دشمن، بلاک، قفل پیوی، عدم حضور، منشی، عضویت اجباری، سکوت و فیلتر", (
        "panel_enemy", "panel_block", "panel_private_lock", "panel_absence",
        "panel_secretary", "panel_forced_join", "panel_mute", "panel_word_filter",
    )),
    PanelCategory("content", "💬 محتوا و تعامل", "محتوا، پاسخ خودکار، تگ، مدیریت گروه، نگهبان، سین، ری‌اکشن، کامنت، اسپم، سندر و تبچی", (
        "panel_content", "panel_auto_reply", "panel_tag_members", "panel_group_management",
        "panel_chat_guard", "panel_auto_read", "panel_auto_reaction",
        "panel_first_comment", "panel_spam", "panel_sender", "panel_tabchi",
    )),
    PanelCategory("tools", "🧰 ابزارها", "ترجمه، دانلود، ارز، حذف پیام، بازی، ویس، TTS، ایموجی، استارزی و کیفیت عکس", (
        "panel_translate", "panel_downloader", "panel_currency", "panel_delete",
        "panel_games", "panel_voice_search", "panel_tts", "panel_premium_emoji",
        "panel_stars_challenge", "panel_image_quality",
    )),
    PanelCategory("system", "👤 حساب و سیستم", "حساب متصل، وضعیت سرویس و کنترل‌های عمومی", ()),
)


class PanelService:
    """Builds the hierarchical panel state from the durable capability registry."""

    def __init__(self, capabilities: CapabilityService) -> None:
        self.capabilities = capabilities

    @staticmethod
    def categories() -> tuple[PanelCategory, ...]:
        return PANEL_CATEGORIES

    def category(self, category_id: str) -> PanelCategory:
        value = str(category_id).strip().lower()
        for item in PANEL_CATEGORIES:
            if item.category_id == value:
                return item
        raise KeyError(f"unknown panel category: {category_id}")

    def roots(self, category_id: str) -> tuple[CapabilityDefinition, ...]:
        category = self.category(category_id)
        ids = set(category.capability_ids)
        return tuple(
            item for item in self.capabilities.definitions()
            if item.capability_id in ids
        )

    def children(self, capability_id: str) -> tuple[CapabilityDefinition, ...]:
        return self.capabilities.children(capability_id)

    def category_stats(self, owner_id: str, category_id: str) -> tuple[int, int]:
        roots = self.roots(category_id)
        snapshot = self.capabilities.snapshot(owner_id)
        enabled = sum(1 for item in roots if snapshot[item.capability_id])
        return enabled, len(roots)

    def summary(self, owner_id: str) -> tuple[int, int]:
        snapshot = self.capabilities.snapshot(owner_id)
        toggleable = [
            item for item in self.capabilities.definitions() if item.toggleable
        ]
        return sum(snapshot[item.capability_id] for item in toggleable), len(toggleable)
